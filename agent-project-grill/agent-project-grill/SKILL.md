---
name: agent-project-grill
description: Agent 项目面试拷打引擎。默认用 project-mock-interview 按项目题库出题、四维点评、复盘沉淀，对低分题用 grilling 深挖；可选先用 agent-review-audit 做代码体检挖薄弱点。当用户说"开一场 / 拷打我 / 针对我的 Agent 项目模拟面试 / 项目拷打练习"时使用。
---

# Agent 项目拷打（出题 → 拷打 → 深挖 → 复盘）

整场上下文预算 ≤20K tokens。主引擎是 project-mock-interview（与 agent-review-audit 定位重复，默认用前者）；agent-review-audit 仅在用户明确要求"先审代码挖坑"时作为前置体检。

## 1. 定位项目

用户给了路径就用；cwd 是项目就用 cwd；都没有就列可选项目让用户挑。

## 2. 可选代码体检（agent-review-audit）

仅当用户要求"先审查代码 / 挖坑"时运行：读取 agent-review-audit 的 SKILL.md，按其 SOP 运行 `scripts/route_project.py --path <项目路径>`，只读输出的 matched_concept / target_cards / weakness_tags，作为阶段 3 的薄弱优先输入。默认跳过。

## 3. 模拟拷打（project-mock-interview）

读取 project-mock-interview 的 SKILL.md，按其拷问模式执行：

- 出题策略：薄弱优先（有体检时用 weakness_tags）+ 复习优先（复盘文件待复习清单）；都没有则按深度递进
- 一次一题，用户答完做四维点评（概念理解 / 原理深度 / 落地证据 / 结构完整度），默认 3 题/场
- 点评只引用作答档已有的证据锚点；证据不足就诚实说明，禁止编造

## 4. grilling 深挖

对四维任一 ≤2 或用户答不出的题，切到 grilling 会话：一次一个问题、每题给推荐答案；能查代码库就查代码库补细节（用户是产品视角，细节由 agent 补，边问边教）。

## 5. 复盘

按 project-mock-interview 复盘规范写入 Obsidian vault 的 `40_项目档案/<slug>/面试复盘.md`：题目清单、四维得分、薄弱主题、待复习清单（低分题 id + 薄弱维度）。下一场开场先读它。

## 纪律

- 分层加载：只按需读题卡 / 题段 / 证据切片，禁止整读题库或全量代码
- 体检阶段只读路由输出，不读题卡全量
- 子 skill（project-mock-interview / grilling，可选 agent-review-audit）都已在本地，按其各自 SKILL.md 执行
