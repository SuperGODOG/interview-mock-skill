# interview-mock-skill

Agent 开发岗面试练习全家桶：**项目建档 → 路由出题 → 模拟拷打 → 深挖 → 复盘学习卡**。跨平台、跨 agent，数据与代码分离。

## 四个 skill

| Skill | 角色 | 说明 |
|---|---|---|
| [agent-project-grill](agent-project-grill/SKILL.md) | 编排壳（日常入口） | 一句"开一场"自动完成：建档检查 → 拷打 → grilling 深挖 → 复盘 → 学习卡 |
| [interview-bank-pipeline](interview-bank-pipeline/SKILL.md) | 建档 / 生产端 | 面经清洗分类、Obsidian 知识图谱、GitHub 项目融合建档；脚本内嵌 |
| [project-mock-interview](project-mock-interview/SKILL.md) | 拷打引擎本体 | 240 道题库 + 项目档案快照，路由出题、四维点评、复盘沉淀 |
| [agent-review-audit](agent-review-audit/SKILL.md) | 可选代码体检 | 243 道 Agent & RAG 题卡，三维打分、架构 Gap 分析 |

## 安装（跨平台）

1. 把四个 skill 文件夹放进任一 agent 的 skills 目录（本机统一入口 `~/.cc-switch/skills/`，Codex/Claude/Gemini/Hermes 用软链指向）
2. 设置数据工作区：`export INTERVIEW_WORKSPACE=<数据目录>`（包含 `items.json` / `concepts.yaml` / `schema.json` / `obsidian_vault/`；未设置时兼容回退 `~/桌面/面试文档裁切`）
3. 依赖：python3、PyYAML、git、jq（仅路由提取用）

## 用法

- 新项目：`开一场 https://github.com/<owner>/<repo>` —— 自动建档后进入拷打
- 已建档项目：`开一场 skillforge` —— 直接拷打
- 题库/档案同步：见 `project-mock-interview/references/README.md`
- 建档与数据迁移：见 `interview-bank-pipeline/SKILL.md` 的「跨平台部署」

## 数据位置

skill 文件夹只放代码与语料快照；`repos_cache/`、原始面经文档、手写笔记等个人数据不要上传，放在 `$INTERVIEW_WORKSPACE`。
