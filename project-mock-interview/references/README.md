# 语料同步说明（project-mock-interview skill）

本目录是快照，源在数据工作区。工作区路径取 `INTERVIEW_WORKSPACE` 环境变量；未设置时回退 `~/桌面/面试文档裁切`（旧本机默认）。新设备请先设置：

```bash
export INTERVIEW_WORKSPACE=/path/to/your/interview-workspace
```

题库或项目档案更新后，在任意目录执行（自动遍历已有项目）：

```bash
WS="${INTERVIEW_WORKSPACE:-$HOME/桌面/面试文档裁切}"
S="$(cd "$(dirname "$0")/.." && pwd)"   # 本 skill 目录（软链已解析）

# 题库层
cp "$WS/items.json" "$WS/concepts.yaml" "$WS/schema.json" "$S/references/题库/"

# 项目层：遍历 vault 里已建档的项目，同步快照
for slug_dir in "$WS"/obsidian_vault/40_项目档案/*/; do
  [ -d "$slug_dir" ] || continue
  slug=$(basename "$slug_dir")
  mkdir -p "$S/references/项目/$slug"
  [ -f "$WS/repos_cache/$slug/match.json" ] && cp "$WS/repos_cache/$slug/match.json" "$S/references/项目/$slug/"
  cp "$slug_dir"/*.md "$S/references/项目/$slug/" 2>/dev/null || true
done
```

注意：`$HOME/桌面/面试文档裁切` 只是兼容回退，跨平台场景必须显式设置 `INTERVIEW_WORKSPACE`，否则中文桌面路径在其他系统不存在。

## 文件清单

- `题库/items.json` — 240 题（id/line/text/major/minor/depth/concepts），唯一题目原文来源
- `题库/concepts.yaml` — 33 概念词典（含 aliases/keywords/summary/related）
- `题库/schema.json` — 7 大类/14 小类骨架
- `项目/<slug>/match.json` — 路由表（候选题目 + hit_concepts + evidence + depth）
- `项目/<slug>/项目画像.md` — 技术档案（自研项目含钩子，第三方项目含谈资点+误报清单）
- `项目/<slug>/面试题匹配表.md` — 题目×概念×证据对照
- `项目/<slug>/项目内作答.md` — 逐题作答 + 文件:行号 证据锚点（点评依据）
- 复盘文件不在此目录（写在 `$INTERVIEW_WORKSPACE/obsidian_vault/40_项目档案/<slug>/面试复盘.md`）

## 约定

- 语料只增改不删题（大厂面试题合集，质量高）
- 新增项目：跑 interview-bank-pipeline 阶段三（repo_fuse fetch/match/finalize）后，用上面的命令同步快照；agent-project-grill 编排时会自动完成建档 + 同步
- **运行期状态不回流**：复习状态（待复习/已掌握）写在 vault 的 40_项目档案/<slug>/面试复盘.md，不写 items.json——同步命令会覆盖 skill 内快照，status 字段只是初始值
