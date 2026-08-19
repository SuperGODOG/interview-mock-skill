---
name: interview-bank-pipeline
description: 面试题库文档清洗分类 + Obsidian 知识图谱 + GitHub 项目融合三合一流水线。当用户要求清洗/分类面试文档、把题库建成 Obsidian 图谱、或根据 GitHub 项目链接生成面试设计档案时使用。脚本已内嵌于本 skill 的 scripts/，数据工作区由 INTERVIEW_WORKSPACE 指定（未设置时回退 ~/桌面/面试文档裁切）。
version: 1.1.0
---

# 面试题库清洗与知识图谱流水线

三阶段流水线，判断活全部交给 subagent（隔离上下文），机械活全部脚本化。主会话只接触统计、校验结果与审计报告。

## 工作区（INTERVIEW_WORKSPACE）

- 所有数据（源文档/题库/图谱/缓存）都在**数据工作区**，不在 skill 目录里
- 解析顺序：环境变量 `INTERVIEW_WORKSPACE` → 未设置时回退 `~/桌面/面试文档裁切`（旧本机默认，仅为兼容）
- 跨平台/新设备：先设置 `INTERVIEW_WORKSPACE`（如 `export INTERVIEW_WORKSPACE=$HOME/.interview-workbench`），再按「跨平台部署」初始化数据
- 脚本已内嵌于本 skill 的 `scripts/`（pipeline.py / repo_fuse.py / verify_categories.py），通过环境变量定位工作区，可在任意目录执行

## 项目布局（$INTERVIEW_WORKSPACE/）

- `agent_review.md` 源文档（唯一输入）
- `concepts.yaml` 概念词典（图谱与融合的桥梁，唯一需人工维护的文件）
- `items.json` / `schema.json` / `batches/classified/` 中间态（checkpoint，可断点续跑）
- `categories/` 清洗产物（大类目录/小类文件）
- `obsidian_vault/` 知识图谱（00_MOC / 10_概念 / 20_索引 / 30_手写笔记 / 40_项目档案）
- `repos_cache/<owner>__<repo>/` 克隆缓存 + profile.json / match.json / sections/
- 旧工作区可能还有 pipeline.py / repo_fuse.py / verify_categories.py 的旧副本，可忽略；一律使用本 skill `scripts/` 下的版本

## 阶段一：文档清洗分类（源文档 → categories/）

1. 在 `$INTERVIEW_WORKSPACE` 下执行 `python3 <本skill>/scripts/pipeline.py split` — 切分条目（行号做稳定 ID，识别 标题/编号小类/括号子标签/HTML注释块），注释块内题目标记为自由分类
2. 派 subagent 分类批次（每批 ~48 条，最多 3 个并行）：
   - assigned=true 的条目保留机械分配的 major/minor，只补 depth(1-5) 和 subminor
   - assigned=false（注释块）按语义相似度归位，fuzzy=true + note 理由
   - 输出 JSON 到 batches/classified/，每批一个文件；用 `pipeline.py validate` 校验
3. `python3 <本skill>/scripts/pipeline.py merge` — 汇总生成 categories/<大类>/<小类>.md
4. ≥15 题的大文件派 subagent 递归细分：合并相近 H2 组、拆分超载组、删除"补充：源自「xxx」"组并入主题组、组内按逻辑深度排序（概念定义→原理机制→设计实现→落地与权衡→前沿延伸）；要求逐字保留题目
5. `python3 <本skill>/scripts/verify_categories.py` + `python3 <本skill>/scripts/pipeline.py audit` — 全绿才算完成

## 阶段二：Obsidian 知识图谱（categories/ → obsidian_vault/）

1. 编辑 `concepts.yaml`（概念名/aliases/keywords/summary/related；关键词注意 YAML 会把 "503" 解析成 int，必须加引号）
2. `python3 <本skill>/scripts/pipeline.py export` — 生成 00_MOC（总览+大类）、10_概念、20_索引（题级锚点 `### L6`）、99_dataview.md；内置断链校验
3. 保留区：30_手写笔记 与 40_项目档案 重跑时自动保留（内部实现：先移到 vault 外再 rmtree，注意 shutil.move 遇已存在目录会嵌套进去，移回前需 rmdir 空壳）
4. 概念笔记链接用 `[[20_索引/<大类>/<小类>.md#L6|L6 · 摘要]]` 锚点直达题目

## 阶段三：GitHub 项目融合（URL → 双落点档案）

1. `python3 <本skill>/scripts/repo_fuse.py fetch <url>` — 浅克隆 + 指纹（语言/框架/树）+ concepts.yaml 关键词匹配 → profile.json
2. `python3 <本skill>/scripts/repo_fuse.py match <slug>` — 命中概念 → 候选题目 → match.json
3. 派 subagent（3 个并行）：
   - 画像：自研项目写 30秒介绍+钩子+框架给的 vs 我设计的；第三方项目写"学习谈资档案"，必须排查概念误报
   - 作答（按大类分组）：每题 = 一句话回答 + 展开细节一/二/三，必须引用真实 文件:行号，未实现的部分诚实标注"对应物+一般方向"，无关题可弃（末尾弃题说明）
4. `python3 <本skill>/scripts/repo_fuse.py finalize <slug>` — 汇总 sections/ → obsidian_vault/40_项目档案/<slug>/（项目画像/匹配表/项目内作答）+ 仓库 docs/INTERVIEW_DESIGN_MAP.md
5. **同步快照到拷打引擎（联动，必做）**：把建档产物同步到 project-mock-interview 的 `references/项目/<slug>/`（match.json + 项目画像/面试题匹配表/项目内作答）。目标目录按当前 agent 解析：统一入口 `~/.cc-switch/skills/project-mock-interview`（Codex/Claude/Gemini/Hermes 均软链于此）。命令见 project-mock-interview 的 `references/README.md`；编排 skill（agent-project-grill）会在建档后自动执行
6. `python3 <本skill>/scripts/pipeline.py export` 刷新总览（项目档案区）
7. 推送（可选）：自己的仓库 push_files 到 master；第三方仓库先 fork → create_branch → push_files → 验证 get_file_contents

## 关键坑（都踩过）

- subagent 批量分类最多 3 个并发（delegate_task 限制），分波派发
- 每波 subagent 回来后立即 validate/verify，防坏 JSON 级联
- 机械关键词匹配必然有噪声（如"上下文"误命中"上下文切换"、"状态"误命中"状态码"），由作答 subagent 精选过滤——不要试图把词典调到零噪声
- 概念 related 引用必须精确匹配概念 name，否则产生断链（校验器会报）
- 大仓库（1809 文件实测）：树深度限 5、内容采样限 400 文件/4MB，克隆用 --depth 1
- 审计"未分类"要读 classified 结果，不能只看 items.json（depth/分类在 classified 里）
- 脚本里 `ROOT` 优先读 `INTERVIEW_WORKSPACE`：工作区换位置后必须重设环境变量，否则会落到脚本所在目录

## 跨平台部署（GitHub 分发后）

本 skill 自包含（scripts/ 已内嵌），新设备三步：

1. 设环境变量：`export INTERVIEW_WORKSPACE=<数据目录>`（写入 shell 配置或 agent 环境，长期生效）
2. 初始化数据：创建目录并放入 `agent_review.md`、`concepts.yaml`、`items.json`、`schema.json`、`categories/`、`obsidian_vault/`（题库与图谱可整体迁移；`repos_cache/` 可留空按需重建）
3. 装依赖：python3、PyYAML、git、jq（jq 仅 project-mock-interview 路由提取用）

不要上传 GitHub 的内容：`repos_cache/`（含第三方仓库克隆）、原始面经文档（如 `agent_review.md`）、含个人笔记的 `30_手写笔记`——仓库只放 skill 文件夹。Windows 建议用 Git Bash / WSL 运行 shell 步骤。

## 验证清单

- [ ] pipeline.py validate 全 OK（major/minor 与 schema 精确匹配、depth 1-5）
- [ ] verify_categories.py 全部 [OK]（题数 + 文本多重集一致）
- [ ] audit_report.md：题目总数 = 落盘数，无未分类
- [ ] export 链接校验 0 断链
- [ ] subagent 作答摘要包含每题证据文件列表（自报不可全信，抽查 2-3 处行号）
- [ ] GitHub 推送后用 get_file_contents 验证文件存在
- [ ] 建档后快照已同步到 project-mock-interview `references/项目/<slug>/`（联动步骤 5）
