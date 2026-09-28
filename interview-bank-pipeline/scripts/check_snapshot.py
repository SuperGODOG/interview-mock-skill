#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_snapshot.py —— 检查项目面试快照版本新鲜度（Commit Hash & 树状态对账）

用法:
  python3 check_snapshot.py <target_path_or_url_or_slug> [--json] [--fail-on-stale]

状态码 (Exit code):
  0: FRESH (快照与当前代码版本一致)
  1: STALE / LEGACY_UNTRACKED / DIRTY (快照过时或存在未追踪改动)
  2: MISSING / CORRUPTED (快照完全不存在或损坏)
"""
import argparse
from datetime import datetime
import json
import os
import re
import subprocess
import sys


def run_cmd(cmd, cwd=None):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except Exception as e:
        return -1, "", str(e)


def resolve_slug_and_repo(target: str) -> tuple[str, str | None]:
    """解析目标，返回 (slug, local_repo_dir)"""
    target = target.strip()
    
    # 1. 如果是本地目录
    if os.path.isdir(target):
        repo_dir = os.path.abspath(target)
        code, url, _ = run_cmd(["git", "-C", repo_dir, "remote", "get-url", "origin"])
        if code == 0 and url:
            m = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$", url)
            if m:
                return f"{m.group(1)}__{m.group(2)}", repo_dir
        base = os.path.basename(repo_dir)
        return f"local__{base}", repo_dir

    # 2. 如果是 GitHub URL
    m = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$", target)
    if m:
        return f"{m.group(1)}__{m.group(2)}", None

    # 3. 假设直接输入的是 slug (owner__repo)
    return target, None


def get_repo_git_info(repo_dir: str) -> dict:
    """获取本地仓库的实时 Git 状态"""
    info = {"is_git": False}
    if not repo_dir or not os.path.isdir(os.path.join(repo_dir, ".git")):
        return info

    info["is_git"] = True
    _, head, _ = run_cmd(["git", "-C", repo_dir, "rev-parse", "HEAD"])
    _, branch, _ = run_cmd(["git", "-C", repo_dir, "rev-parse", "--abbrev-ref", "HEAD"])
    _, date, _ = run_cmd(["git", "-C", repo_dir, "log", "-1", "--format=%cd"])
    _, msg, _ = run_cmd(["git", "-C", repo_dir, "log", "-1", "--format=%s"])
    code, status, _ = run_cmd(["git", "-C", repo_dir, "status", "--porcelain"])

    info.update({
        "commit_hash": head,
        "commit_short": head[:7] if head else "",
        "branch": branch,
        "commit_date": date,
        "commit_message": msg,
        "is_dirty": bool(status.strip()) if code == 0 else False,
    })
    return info


def find_snapshot_dirs(slug: str) -> list[str]:
    """寻找可能存放该项目快照的目录"""
    candidates = []
    
    # 1. 优先检查环境变量与 standard project-mock-interview 目录
    pm_dir = os.environ.get("PROJECT_MOCK_SKILL_DIR")
    if pm_dir:
        candidates.append(os.path.join(pm_dir, "references", "项目", slug))
    
    # 相对路径回溯 (从当前 scripts 目录向上)
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    candidates.append(os.path.abspath(os.path.join(cur_dir, "..", "..", "project-mock-interview", "references", "项目", slug)))
    
    # 用户根目录常见软链
    candidates.append(os.path.expanduser(f"~/.gemini/skills/project-mock-interview/references/项目/{slug}"))
    candidates.append(os.path.expanduser(f"~/.cc-switch/skills/project-mock-interview/references/项目/{slug}"))
    
    # 2. Obsidian vault 档案区
    vault_root = os.environ.get("INTERVIEW_WORKSPACE") or os.path.expanduser("~/桌面/面试文档裁切")
    candidates.append(os.path.join(vault_root, "obsidian_vault", "40_项目档案", slug))

    # 去重
    seen = set()
    result = []
    for c in candidates:
        norm = os.path.normpath(c)
        if norm not in seen and os.path.isdir(norm):
            seen.add(norm)
            result.append(norm)
    return result


def extract_snapshot_metadata(snap_dir: str) -> dict:
    """提取快照中的版本元数据"""
    meta = {}
    
    # 1. 从 snapshot_meta.json 读
    meta_file = os.path.join(snap_dir, "snapshot_meta.json")
    if os.path.isfile(meta_file):
        try:
            with open(meta_file, encoding="utf-8") as f:
                meta = json.load(f)
                meta["source"] = "snapshot_meta.json"
                return meta
        except Exception:
            pass

    # 2. 从 match.json 的 meta 字段读
    match_file = os.path.join(snap_dir, "match.json")
    if os.path.isfile(match_file):
        try:
            with open(match_file, encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "meta" in data:
                    meta = dict(data["meta"])
                    meta["source"] = "match.json:meta"
                    return meta
        except Exception:
            pass

    # 3. 从 项目画像.md 的 frontmatter 读
    profile_file = os.path.join(snap_dir, "项目画像.md")
    if os.path.isfile(profile_file):
        try:
            with open(profile_file, encoding="utf-8") as f:
                content = f.read(2048)
                m = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
                if m:
                    fm = m.group(1)
                    c_match = re.search(r"^commit:\s*([a-f0-9]+)", fm, re.MULTILINE)
                    if c_match:
                        meta["commit_hash"] = c_match.group(1)
                        meta["commit_short"] = meta["commit_hash"][:7]
                        b_match = re.search(r"^branch:\s*(.+)", fm, re.MULTILINE)
                        if b_match:
                            meta["branch"] = b_match.group(1).strip()
                        meta["source"] = "项目画像.md:frontmatter"
                        return meta
        except Exception:
            pass

    return meta


def check_snapshot(target: str) -> dict:
    slug, repo_dir = resolve_slug_and_repo(target)
    snap_dirs = find_snapshot_dirs(slug)
    
    # 若无法根据目标直接推导 repo_dir，但 cache 存在
    if not repo_dir:
        root_ws = os.environ.get("INTERVIEW_WORKSPACE") or os.path.expanduser("~/桌面/面试文档裁切")
        cached_repo = os.path.join(root_ws, "repos_cache", slug)
        if os.path.isdir(cached_repo):
            repo_dir = cached_repo

    repo_git = get_repo_git_info(repo_dir) if repo_dir else {}

    result = {
        "slug": slug,
        "target": target,
        "repo_dir": repo_dir,
        "repo_git": repo_git,
        "snapshot_dirs": snap_dirs,
        "status": "UNKNOWN",
        "message": "",
        "diff_summary": None,
    }

    if not snap_dirs:
        result["status"] = "MISSING"
        result["message"] = f"未找到项目 [{slug}] 的快照档案。需要先运行 interview-bank-pipeline 建档。"
        return result

    primary_snap_dir = snap_dirs[0]
    result["active_snapshot_dir"] = primary_snap_dir
    files = [f for f in os.listdir(primary_snap_dir) if not f.startswith(".")]
    result["snapshot_files"] = files

    if "match.json" not in files:
        result["status"] = "CORRUPTED"
        result["message"] = f"快照目录存在但缺少核心路由文件 match.json。"
        return result

    snap_meta = extract_snapshot_metadata(primary_snap_dir)
    result["snapshot_meta"] = snap_meta

    if not snap_meta or not snap_meta.get("commit_hash"):
        result["status"] = "LEGACY_UNTRACKED"
        result["message"] = (
            f"快照存在（包含 {', '.join(files)}），但未记录 Git commit 版本（属于旧版流水线构建遗留物）。\n"
            "无法校验与当前代码的一致性，存在严重过期/幻觉风险，强烈建议重新建档刷新快照！"
        )
        return result

    snap_commit = snap_meta["commit_hash"]
    snap_short = snap_commit[:7]

    if not repo_git.get("is_git"):
        result["status"] = "UNVERIFIABLE_REPO"
        result["message"] = (
            f"快照记录版本为 {snap_short}，但当前目标非本地 Git 仓库或无法读取 Git 信息，无法对比新鲜度。"
        )
        return result

    head_commit = repo_git["commit_hash"]
    head_short = head_commit[:7]

    if snap_commit == head_commit:
        if repo_git.get("is_dirty"):
            result["status"] = "DIRTY_WORKTREE"
            result["message"] = (
                f"快照 commit ({snap_short}) 与 HEAD 完全匹配，但本地工作区存在未提交的修改 (Dirty)。"
            )
        else:
            result["status"] = "FRESH"
            result["message"] = (
                f"快照 100% 同步！当前 HEAD ({head_short}) 与快照一致，可安全用于面试与审查。"
            )
        return result

    # commit 不一致，计算差异
    result["status"] = "STALE"
    code_ahead, ahead_out, _ = run_cmd(
        ["git", "-C", repo_dir, "rev-list", "--count", f"{snap_commit}..{head_commit}"]
    )
    code_behind, behind_out, _ = run_cmd(
        ["git", "-C", repo_dir, "rev-list", "--count", f"{head_commit}..{snap_commit}"]
    )
    
    ahead = int(ahead_out) if code_ahead == 0 and ahead_out.isdigit() else "?"
    behind = int(behind_out) if code_behind == 0 and behind_out.isdigit() else "?"
    
    _, log_diff, _ = run_cmd(
        ["git", "-C", repo_dir, "log", "--oneline", "-n", "5", f"{snap_commit}..{head_commit}"]
    )

    result["diff_summary"] = {
        "snapshot_commit": snap_short,
        "head_commit": head_short,
        "ahead_commits": ahead,
        "behind_commits": behind,
        "recent_commits_ahead": log_diff.splitlines() if log_diff else []
    }

    result["message"] = (
        f"快照已严重过时！\n"
        f"  - 快照对应版本: {snap_short} ({snap_meta.get('commit_date', '未知日期')})\n"
        f"  - 本地当前最新: {head_short} ({repo_git.get('commit_date', '未知日期')})\n"
        f"  - 代码变动统计: 本地代码领先快照 {ahead} 个 commit (落后 {behind})\n"
        f"  - 最新提交说明: {repo_git.get('commit_message')}\n"
        f"⚠️  继续使用旧快照将导致模拟面试提问和点评基于旧代码（产生严重幻觉）。请刷新快照！"
    )
    return result


def main():
    parser = argparse.ArgumentParser(description="检查项目面试快照版本新鲜度")
    parser.add_argument("target", help="本地仓库路径、GitHub URL 或项目 slug")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    parser.add_argument("--fail-on-stale", action="store_true", help="若过时或未追踪则以非0退出")
    args = parser.parse_args()

    res = check_snapshot(args.target)

    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        status_icons = {
            "FRESH": "✅ [FRESH 100%同步]",
            "DIRTY_WORKTREE": "🟡 [DIRTY 工作区有未提交代码]",
            "STALE": "❌ [STALE 快照已过时]",
            "LEGACY_UNTRACKED": "⚠️ [LEGACY 旧版快照无版本信息]",
            "MISSING": "⚪ [MISSING 未建档]",
            "CORRUPTED": "💔 [CORRUPTED 快照文件损坏]",
            "UNVERIFIABLE_REPO": "❓ [UNVERIFIABLE 无法核对Git]",
        }
        icon = status_icons.get(res["status"], f"[{res['status']}]")
        print("\n" + "=" * 60)
        print(f"项目快照版本校验报告: {res['slug']}")
        print(f"状态判定: {icon}")
        print("=" * 60)
        print(res["message"])
        if res.get("active_snapshot_dir"):
            print(f"快照路径: {res['active_snapshot_dir']}")
        if res.get("diff_summary") and res["diff_summary"]["recent_commits_ahead"]:
            print("\n近期领先提交:")
            for line in res["diff_summary"]["recent_commits_ahead"]:
                print(f"  * {line}")
        print("=" * 60 + "\n")

    # 状态码映射
    if res["status"] == "FRESH":
        sys.exit(0)
    elif res["status"] in ("DIRTY_WORKTREE", "UNVERIFIABLE_REPO"):
        sys.exit(0 if not args.fail_on_stale else 1)
    elif res["status"] in ("STALE", "LEGACY_UNTRACKED"):
        sys.exit(1)
    else: # MISSING, CORRUPTED
        sys.exit(2)


if __name__ == "__main__":
    main()
