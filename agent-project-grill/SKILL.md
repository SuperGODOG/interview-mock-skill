---
name: agent-project-grill
description: Agent 项目面试拷打引擎。默认用 project-mock-interview 按项目题库出题、四维点评、复盘沉淀，对低分题用 grilling 深挖；未建档项目自动经 interview-bank-pipeline 建档并同步快照；全程过程落文档，回答一般的题自动生成学习卡供下次复习。当用户说"开一场 / 拷打我 / 针对我的 Agent 项目模拟面试 / 项目拷打练习"时使用。
---

# Agent 项目拷打（建档检查 → 出题 → 拷打 → 深挖 → 复盘）

整场上下文预算 ≤20K tokens。三个子 skill 的分工：interview-bank-pipeline 建档（生产端），project-mock-interview 出题点评（主循环），grilling 深挖（补课）。核心承诺：**每题有记录、低分有 grilling、场场有复盘、复习有学习卡**。

## 0. 环境与建档自检（开工前必做）

1. 解析工作区：`INTERVIEW_WORKSPACE`（未设置回退 `~/桌面/面试文档裁切`）；目录或脚本不可用（缺 repo_fuse.py 等）时，先按 interview-bank-pipeline 的「跨平台部署」初始化，再继续
2. 定位项目 slug（`owner__repo`），检查 project-mock-interview 的 `references/项目/<slug>/match.json` 是否存在
   - 存在（已建档）→ 直接进入阶段 1，interview-bank-pipeline 不参与
   - 不存在（新项目）→ 建档（按 interview-bank-pipeline 阶段三执行）：`repo_fuse.py fetch <url>` → `match <slug>` → 派 subagent 写画像/作答 → `finalize <slug>`（repo_fuse 会自动同步快照到 project-mock-interview `references/项目/<slug>/`；若脚本版本较旧没自动同步，按 `references/README.md` 手动同步）→ **校验** `references/项目/<slug>/match.json` 已存在，不存在则报错并重试 → 完成后回到本流程
3. 读复习源：`$INTERVIEW_WORKSPACE/obsidian_vault/40_项目档案/<slug>/学习卡.md` 与 `面试复盘.md` 的待复习清单，有则阶段 1 复习优先（先清未复习的学习卡）

## 1. 模拟拷打（project-mock-interview）

读取 project-mock-interview 的 SKILL.md，按其拷问模式执行：

- 出题策略：薄弱优先（有体检时用 weakness_tags）+ 复习优先（学习卡/待复习清单）；都没有则按深度递进
- 一次一题，用户答完做四维点评（概念理解 / 原理深度 / 落地证据 / 结构完整度），默认 3 题/场
- **每题当场记录**（供阶段 3 落档）：题 id、用户作答摘要、四维得分、点评要点
- 点评只引用作答档已有的证据锚点；证据不足就诚实说明，禁止编造

## 2. grilling 深挖

对四维任一 ≤2 或用户答不出的题，切到 grilling 深挖：

1. grilling 已随仓库/本地附带（`grilling/SKILL.md`，来自 mattpocock/skills）→ 读取其 SKILL.md，按原版追问节奏执行
2. 环境没有 grilling → 按内联规则执行：**一次只问一个问题**（同时问多个会让人懵）；每题给出推荐答案；能查代码库就先查代码库再问；逐条追问直到该薄弱点挖透

**逐问记录**：追问内容、用户回答、agent 给的要点，全部记入场次记录（阶段 3 落档），不留在聊天里丢失。

## 3. 复盘与学习卡（有文档可循）

每场结束写两处文档，都是纯 markdown，Obsidian 只是可选的查看方式，不依赖它：

1. **场次复盘**：`$INTERVIEW_WORKSPACE/obsidian_vault/40_项目档案/<slug>/面试复盘.md`，追加本场记录：
   - 场次信息（日期 / 项目 / 题数）
   - 题目清单 + 四维得分表
   - grilling 记录（追问链 + 要点）
2. **学习卡**：`$INTERVIEW_WORKSPACE/obsidian_vault/40_项目档案/<slug>/学习卡.md`，对任一维 ≤2 或触发过 grilling 的题追加一行：
   - 格式：`- [ ] Lxx ｜ 薄弱维度:xxx ｜ 一句话记忆点:xxx ｜ 下次复习`
   - 下一场阶段 0 优先复习；复习过关后勾掉 `[x]`，保留为已掌握记录

## 纪律

- 分层加载：只按需读题卡 / 题段 / 证据切片，禁止整读题库或全量代码
- 体检阶段只读路由输出，不读题卡全量
- 子 skill（project-mock-interview / grilling / interview-bank-pipeline）都按各自 SKILL.md 执行；建档是生产端，只在未建档或项目大改时跑
- grilling 已内置（来源 mattpocock/skills，MIT）；若被移除，按阶段 2 内联规则兜底，不影响流程
- 跨平台：所有数据路径以 `INTERVIEW_WORKSPACE` 为准，禁止写死用户目录
