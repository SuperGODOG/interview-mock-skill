#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""repo_fuse —— GitHub 项目 × 面试题库 融合工具（机械部分）

用法:
  python3 repo_fuse.py fetch <url>            # 克隆(浅) + 项目画像 + 概念匹配 -> repos_cache/<slug>/profile.json
  python3 repo_fuse.py match <slug>           # 命中概念 -> 题库候选题目 -> match.json
  python3 repo_fuse.py finalize <slug>        # 汇总 subagent 产出的 sections/ -> vault 档案 + 仓库 INTERVIEW_DESIGN_MAP.md

判断部分（项目画像润色/逐题作答）由主会话派 subagent 完成，
subagent 只读写 repos_cache/<slug>/sections/ 与 obsidian_vault/40_项目档案/<slug>/。
"""
import json
import os
import re
import shutil
import subprocess
import sys
import yaml

ROOT = os.environ.get("INTERVIEW_WORKSPACE") or (os.path.expanduser("~/桌面/面试文档裁切") if os.path.isdir(os.path.expanduser("~/桌面/面试文档裁切")) else os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "repos_cache")
VAULT = os.path.join(ROOT, "obsidian_vault")
ARCHIVE = os.path.join(VAULT, "40_项目档案")

if not os.path.isfile(os.path.join(ROOT, "concepts.yaml")):
    print(f"警告: 工作区 {ROOT} 中未找到 concepts.yaml。"
          "请设置 INTERVIEW_WORKSPACE 指向真实数据目录（如 export INTERVIEW_WORKSPACE=$HOME/.interview-workbench），"
          "或确认旧路径 ~/桌面/面试文档裁切 存在。", file=sys.stderr)

SKIP_DIRS = {".git", "node_modules", "venv", ".venv", "__pycache__", "dist", "build",
             "target", ".idea", ".vscode", "assets", "images", "docs", ".github"}
SKIP_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".lock", ".min.js",
             ".map", ".woff", ".woff2", ".ttf", ".pyc", ".pdf", ".zip"}
MANIFESTS = ("README", "readme", "package.json", "pyproject.toml", "requirements.txt",
             "go.mod", "Cargo.toml", "pom.xml", "build.gradle", "composer.json", "Gemfile")


def slug_of(url: str) -> str:
    m = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$", url.strip())
    if not m:
        raise SystemExit(f"无法解析 GitHub 链接: {url}")
    return f"{m.group(1)}__{m.group(2)}"


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


# ---------------- fetch ----------------

def fetch(url: str):
    slug = slug_of(url)
    rdir = os.path.join(CACHE, slug)
    if os.path.isdir(os.path.join(rdir, ".git")):
        run(["git", "-C", rdir, "pull", "--depth", "1", "--quiet"])
        print(f"已存在, 更新: {rdir}")
    else:
        os.makedirs(CACHE, exist_ok=True)
        r = run(["git", "clone", "--depth", "1", "--quiet", url, rdir])
        if r.returncode != 0:
            raise SystemExit(f"克隆失败: {r.stderr[-500:]}")
        print(f"克隆完成: {rdir}")

    # ---- 指纹: 语言/框架/树 ----
    ext_count, tree, manifests = {}, [], {}
    for d0, dirs, files in os.walk(rdir):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        rel = os.path.relpath(d0, rdir)
        depth = 0 if rel == "." else rel.count(os.sep) + 1
        for fn in files:
            p = os.path.join(d0, fn)
            rp = os.path.relpath(p, rdir)
            ext = os.path.splitext(fn)[1].lower()
            if ext in SKIP_EXTS or fn.endswith((".md", ".txt")) and fn not in ("README.md", "README.txt"):
                continue
            tree.append(rp)
            if ext:
                ext_count[ext] = ext_count.get(ext, 0) + 1
            if fn in MANIFESTS or fn.lower() in ("readme.md", "readme.txt"):
                try:
                    manifests[fn] = open(p, encoding="utf-8", errors="ignore").read(6000)
                except Exception:
                    pass
            if depth >= 5:
                dirs[:] = []

    readme = next((v for k, v in manifests.items() if "readme" in k.lower()), "")
    all_manifests = " ".join(manifests.values())

    # ---- 框架识别 ----
    known = {"langgraph": "LangGraph", "langchain": "LangChain", "autogen": "AutoGen",
             "crewai": "CrewAI", "fastapi": "FastAPI", "flask": "Flask", "django": "Django",
             "react": "React", "vue": "Vue", "next": "Next.js", "streamlit": "Streamlit",
             "gradio": "Gradio", "spring": "Spring", "pytorch": "PyTorch", "tensorflow": "TF",
             "transformers": "HuggingFace Transformers", "llamaindex": "LlamaIndex",
             "haystack": "Haystack", "redis": "Redis", "postgres": "PostgreSQL",
             "pgvector": "pgvector", "qdrant": "Qdrant", "milvus": "Milvus",
             "weaviate": "Weaviate", "chromadb": "ChromaDB", "sqlite": "SQLite",
             "opencv": "OpenCV", "whisper": "Whisper", "vllm": "vLLM", "dify": "Dify",
             "coze": "Coze", "mcp": "MCP", "docker": "Docker", "k8s": "K8s",
             "kubernetes": "K8s", "kafka": "Kafka", "rabbitmq": "RabbitMQ",
             "celery": "Celery", "pydantic": "Pydantic", "tortoise": "TortoiseORM"}
    blob = (readme + "\n" + all_manifests + "\n" + " ".join(tree)).lower()
    frameworks = sorted({v for k, v in known.items() if k in blob},
                        key=lambda v: -blob.count(v.lower()))
    top_ext = sorted(ext_count.items(), key=lambda kv: -kv[1])[:6]

    # ---- 概念匹配: README + manifests + 文件路径 + 抽样内容 ----
    with open(os.path.join(ROOT, "concepts.yaml"), encoding="utf-8") as f:
        concepts = yaml.safe_load(f)["concepts"]

    # 抽样内容: 树内文件采样(上限 400 个) + 各扩展名最大文件
    sampled = {}
    for rp in tree:
        if not os.path.splitext(rp)[1] or len(sampled) >= 400:
            continue
        try:
            sampled[rp] = open(os.path.join(rdir, rp), encoding="utf-8",
                               errors="ignore").read(3000)
        except Exception:
            pass
    big_files = {}
    for d0, dirs, files in os.walk(rdir):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in files:
            p = os.path.join(d0, fn)
            ext = os.path.splitext(fn)[1].lower()
            if ext in SKIP_EXTS:
                continue
            try:
                sz = os.path.getsize(p)
            except Exception:
                continue
            if sz > big_files.get(ext, (0, ""))[0] and sz < 300_000:
                big_files[ext] = (sz, p)
    for (sz, p) in big_files.values():
        rp = os.path.relpath(p, rdir)
        if rp not in sampled:
            try:
                sampled[rp] = open(p, encoding="utf-8", errors="ignore").read(3000)
            except Exception:
                pass

    path_blob = " ".join(tree).lower()
    concept_hits = {}
    for c in concepts:
        files_hit = []
        for rp in tree:
            rpl = rp.lower()
            if any(str(kw).lower() in rpl for kw in c["keywords"]):
                files_hit.append(rp)
        body = readme.lower() + "\n" + all_manifests.lower()
        for rp, txt in sampled.items():
            body += "\n" + txt.lower()
        if len(body) > 4_000_000:
            body = body[:4_000_000]
        if any(str(kw).lower() in body for kw in c["keywords"]):
            files_hit = files_hit or ["<内容命中>"]
            concept_hits[c["name"]] = files_hit[:8]

    profile = {
        "slug": slug, "url": url, "dir": rdir,
        "ext_count": top_ext, "frameworks": frameworks[:10],
        "file_count": len(tree), "readme_head": readme[:1500],
        "tree": tree[:300], "concept_hits": concept_hits,
    }
    with open(os.path.join(rdir, "profile.json"), "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=1)
    print(f"画像完成: {len(tree)} 文件 / 框架 {frameworks[:6]} / 命中概念 {len(concept_hits)}")
    for c, files in sorted(concept_hits.items(), key=lambda kv: -len(kv[1]))[:12]:
        print(f"  {c}: {len(files)} 个证据文件")


# ---------------- match ----------------

def load_bank():
    items = json.load(open(os.path.join(ROOT, "items.json"), encoding="utf-8"))
    classified = {}
    cdir = os.path.join(ROOT, "batches", "classified")
    for cf in os.listdir(cdir):
        if cf.endswith(".json"):
            for c in json.load(open(os.path.join(cdir, cf), encoding="utf-8"))["items"]:
                classified[c["id"]] = c
    with open(os.path.join(ROOT, "concepts.yaml"), encoding="utf-8") as f:
        concepts = yaml.safe_load(f)["concepts"]
    qs = []
    for it in items:
        if it["kind"] != "question":
            continue
        c = classified.get(it["id"])
        if c is None and not it.get("assigned"):
            continue
        major, minor = (c["major"], c["minor"]) if c else (it["major"], it["minor"])
        depth = int((c or {}).get("depth") or it.get("depth") or 99)
        tl = it["text"].lower()
        q_concepts = [cc["name"] for cc in concepts
                      if any(str(kw).lower() in tl for kw in cc["keywords"])]
        qs.append({"id": it["id"], "text": it["text"], "major": major,
                   "minor": minor, "depth": depth, "concepts": q_concepts})
    return qs


def match(slug: str):
    rdir = os.path.join(CACHE, slug)
    profile = json.load(open(os.path.join(rdir, "profile.json"), encoding="utf-8"))
    qs = load_bank()
    hits = profile.get("concept_hits", {})
    cands, per_concept = [], {}
    for q in qs:
        c_hit = [c for c in q["concepts"] if c in hits]
        if c_hit:
            cands.append({**q, "hit_concepts": c_hit})
            for c in c_hit:
                per_concept.setdefault(c, []).append(q["id"])
    # 每个概念最多 4 题(按深度分布取), 总候选上限 30
    chosen, seen = [], set()
    for c, ids in per_concept.items():
        for q in cands:
            if q["id"] in ids and q["id"] not in seen:
                seen.add(q["id"])
                chosen.append({**q, "evidence": hits[c][:5]})
                break
    chosen.sort(key=lambda q: (q["major"], q["minor"], q["depth"], q["line"] if "line" in q else 0))
    chosen = chosen[:30]
    with open(os.path.join(rdir, "match.json"), "w", encoding="utf-8") as f:
        json.dump({"candidates": chosen, "per_concept": per_concept}, f,
                  ensure_ascii=False, indent=1)
    print(f"命中概念 {len(hits)} 个 -> 候选题目 {len(chosen)} 道")
    for q in chosen:
        print(f"  {q['id']} [{q['major']}/{q['minor']} d{q['depth']}] {q['text'][:50]}"
              f" <- {','.join(q['hit_concepts'])}")


# ---------------- finalize ----------------

def finalize(slug: str):
    rdir = os.path.join(CACHE, slug)
    profile = json.load(open(os.path.join(rdir, "profile.json"), encoding="utf-8"))
    matchd = json.load(open(os.path.join(rdir, "match.json"), encoding="utf-8"))
    sec = os.path.join(rdir, "sections")
    out = os.path.join(ARCHIVE, slug)
    os.makedirs(out, exist_ok=True)

    # 画像: 机械部分 + subagent 润色(如有 sections/00_画像.md)
    intro = open(os.path.join(sec, "00_画像.md"), encoding="utf-8").read() \
        if os.path.exists(os.path.join(sec, "00_画像.md")) else ""
    lang = "、".join(f"{e[0].lstrip('.')}×{e[1]}" for e in profile["ext_count"])
    profile_md = f"""---
type: project
url: {profile['url']}
frameworks: {json.dumps(profile['frameworks'], ensure_ascii=False)}
concepts: {json.dumps(list(profile['concept_hits'].keys()), ensure_ascii=False)}
---
# 项目档案：{slug}

> 来源：{profile['url']} ｜ 文件 {profile['file_count']} 个 ｜ 语言 {lang}

## 技术栈
{('、'.join(profile['frameworks'])) if profile['frameworks'] else '_无主流框架识别结果_'}
""" + (f"""
## 画像（subagent 润色版）

{intro}
""" if intro else "") + f"""
## 命中概念与证据文件

""" + "\n".join(
        f"- **{c}**：{', '.join(files[:4])}" for c, files in profile["concept_hits"].items()
    ) + "\n"

    # 匹配表
    rows = []
    for q in matchd["candidates"]:
        rows.append(f"| {q['id']} | {q['text'][:45]} | {q['depth']}/5 | "
                    f"{'、'.join(q['hit_concepts'])} | {'、'.join(q.get('evidence', [])[:2])} |")
    match_md = f"""---
type: question_map
project: {slug}
---
# 面试题匹配表：{slug}

命中概念 {len(profile['concept_hits'])} 个，候选题目 {len(matchd['candidates'])} 道。
（完整作答见《项目内作答.md》；每题的证据锚点由 subagent 在作答时从代码中定位）

| 题号 | 题目 | 深度 | 命中概念 | 证据文件 |
|---|---|---|---|---|
""" + "\n".join(rows) + "\n"

    # 项目内作答: 合并 sections (按文件名排序, 00_画像 除外)
    ans_parts = []
    for fn in sorted(os.listdir(sec)):
        if fn.endswith(".md") and fn != "00_画像.md":
            ans_parts.append(open(os.path.join(sec, fn), encoding="utf-8").read())
    ans_md = (f"---\ntype: project_qa\nproject: {slug}\n---\n# 项目内作答：{slug}\n\n"
              + "\n\n---\n\n".join(ans_parts) + "\n" if ans_parts
              else "# 项目内作答\n\n_尚无作答草稿，先运行 fuse 流程生成。_\n")

    for name, content in (("项目画像.md", profile_md), ("面试题匹配表.md", match_md),
                          ("项目内作答.md", ans_md)):
        with open(os.path.join(out, name), "w", encoding="utf-8") as f:
            f.write(content)
    print(f"vault 档案已写入: {out}")

    # 仓库注入: docs/INTERVIEW_DESIGN_MAP.md
    top = []
    for q in matchd["candidates"]:
        if q["hit_concepts"][0] not in {t[0] for t in top}:
            top.append((q["hit_concepts"][0], q.get("evidence", [])[:3]))
    map_md = f"""# Interview Design Map — {slug}

> 由 repo_fuse 自动生成（面试题库 × 本仓库设计映射）。用于把本项目的设计决策与面试高频设计主题对齐。

## 项目技术画像

- 框架/技术栈：{('、'.join(profile['frameworks'])) if profile['frameworks'] else '未识别'}
- 文件规模：{profile['file_count']} 个源文件
- 与面试题库命中 {len(profile['concept_hits'])} 个设计主题

## 设计主题 ↔ 仓库实现映射

| 面试设计主题 | 仓库中的实现/证据 | 对应题库位置 |
|---|---|---|
""" + "\n".join(
        f"| {c} | {', '.join(files)} | 见题库「{c}」概念笔记 |" for c, files in top
    ) + f"""

## 建议的面试切入点

- 本仓库最能体现设计深度的模块（按命中概念与证据文件定位，建议对照《项目内作答》准备）
- 每个主题准备"框架给的 vs 我设计的"对照（如用 LangGraph 则强调图结构与状态设计的自有决策）

---
生成时间：由 repo_fuse 生成，随题库/仓库变化可重跑更新。
"""
    docdir = os.path.join(profile["dir"], "docs")
    os.makedirs(docdir, exist_ok=True)
    with open(os.path.join(docdir, "INTERVIEW_DESIGN_MAP.md"), "w", encoding="utf-8") as f:
        f.write(map_md)
    print(f"仓库注入完成: {os.path.join(docdir, 'INTERVIEW_DESIGN_MAP.md')}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "fetch"
    if cmd == "fetch":
        fetch(sys.argv[2])
    elif cmd == "match":
        match(sys.argv[2])
    elif cmd == "finalize":
        finalize(sys.argv[2])
    else:
        raise SystemExit(__doc__)
