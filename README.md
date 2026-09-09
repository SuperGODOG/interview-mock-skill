# interview-mock-skill

针对 **Agent 开发岗面试**的练习全家桶：项目建档 → 备战包表达 → 路由出题 → 模拟拷打 → grilling 深挖 → 复盘 → 学习卡。跨平台、跨 agent（Codex / Claude / Gemini / Hermes），数据与代码分离，个人数据不上传。

> 核心承诺：**每题有记录、低分有 grilling、场场有复盘、复习有学习卡**。

---

## 一、这套 skill 解决什么问题

面试 Agent 开发岗时，**项目拷打（设计 / 细节 / 评估）是最重的一块**。常见痛点：

- 有项目但说不清技术细节（尤其是产品/管理视角的候选人）
- 练习时没有真实面试官，不知道会被追问哪些点
- 练完就忘，答得一般的题下次不会优先复习

这套方案把「建档 → 备战包 → 出题 → 点评 → 深挖 → 复盘 → 复习」全部固化进 skill，一次"开一场"跑完整条链。

## 二、六件套定位

| Skill | 角色 | 谁调用 | 频率 |
|---|---|---|---|
| [agent-project-grill](agent-project-grill/SKILL.md) | 编排壳（日常唯一入口） | 你 | 每次练习 |
| [interview-bank-pipeline](interview-bank-pipeline/SKILL.md) | 建档 / 生产端 | agent-project-grill 或你 | 新项目 / 项目大改 / 题库更新 |
| [interview-resume-pack](interview-resume-pack/SKILL.md) | 备战包 / 表达材料生产端 | agent-project-grill 软前置 + 用户直接触发 | 新项目 / 复盘修订建议≥3条 / 用户主动 |
| [project-mock-interview](project-mock-interview/SKILL.md) | 拷打引擎本体（主循环） | agent-project-grill | 每次练习 |
| [agent-review-audit](agent-review-audit/SKILL.md) | 可选代码体检 | 你（显式要求时） | 考前 / 挖坑 |
| [grilling](grilling/SKILL.md) | 深挖原语（内置，来源 mattpocock/skills，MIT） | agent-project-grill | 低分题深挖 |

`grilling`（来自 mattpocock/skills，MIT）作为深挖原语**已内置在仓库 `grilling/`**，agent-project-grill 阶段 2 直接读取其 SKILL.md 执行；即使该文件夹被移除，阶段 2 的内联规则仍可兜底。

## 三、核心工作流

### 两条路径

```
新项目：  建档 (pipeline) ──► 备战包 (软前置, 缺失提示不阻塞) ──► 拷打 (grill) ──► 复盘 ──► 学习卡
已建档：  备战包 (软前置, 缺失提示不阻塞) ───────────────────────► 拷打 (grill) ──► 复盘 ──► 学习卡
```

`agent-project-grill` 阶段 0 会自动完成环境与前置自检：
1. **建档自检**：判断项目 slug 的 `match.json` 是否已在 project-mock-interview 快照里。未建档自动走 `interview-bank-pipeline` 阶段三融合建档并自动同步快照，已建档直接推进。
2. **备战包软前置**：检查 `$WORKSPACE_ROOT/obsidian_vault/40_项目档案/<slug>/备战包/README.md` 存在且状态为「完整」（确认六类正文相对链接均存在）。若缺失，提示一次建议先由 `interview-resume-pack` 生成备战包（漏斗稿是表达地图，深钻点 L3 会成为本场优先出题源）；用户坚持直接开打则照常继续，不阻塞流程。

你只需要说：

- 新项目：`开一场 https://github.com/<owner>/<repo>`
- 生成备战包：`生成备战包` 或针对已建档项目要求生成表达材料
- 已建档开练：`开一场 skillforge`

### 一次完整场次长这样

1. **环境与建档自检**：解析 `INTERVIEW_WORKSPACE`；检查项目是否建档；执行备战包软前置自检（缺失提示但不阻塞）；读上次复盘的学习卡与待复习清单
2. **模拟拷打**（project-mock-interview）：出题策略采用「备战包优先（以完整备战包的深钻点 L3 问题与不会题清单为优先出题源）+ 薄弱优先 + 复习优先 + 深度递进」，一次一题，四维点评（概念理解 / 原理深度 / 落地证据 / 结构完整度），默认 3 题/场
3. **grilling 深挖**：任一维 ≤2 或答不出的题，切到一问一答的追击模式，agent 会查代码库帮你补细节
4. **复盘 + 学习卡 + 备战包反馈**：
   - 场次复盘（题目清单 + 得分表 + grilling 记录）写进 vault
   - 低分题生成学习卡（`- [ ] Lxx ｜ 薄弱维度 ｜ 一句话记忆点 ｜ 下次复习`），下一场优先清
   - 若本场暴露的薄弱点落在备战包覆盖范围内，在复盘文件末尾追加一行 `- [ ] 备战包修订建议：<哪份产物><哪个点><怎么改>` 回流建议；未勾选建议积累 ≥3 条时触发备战包重生成

### 各阶段细节

#### agent-project-grill（编排壳）

- **阶段 0**：`INTERVIEW_WORKSPACE` 解析 → 建档检查（未建档自动走 interview-bank-pipeline 建档并同步快照）→ **备战包软前置**（检查备战包 README 完整状态，缺失提示不阻塞）→ 读复习源
- **阶段 1**：按 project-mock-interview 的拷问模式出题（备战包优先：深钻点 L3 问题与不会题清单为优先检验源），逐题问答，每题当场记录（题 id / 作答摘要 / 四维得分）
- **阶段 2**：低分题切 grilling，追问链与要点逐条记录，不留在聊天里
- **阶段 3**：写 `$INTERVIEW_WORKSPACE/obsidian_vault/40_项目档案/<slug>/面试复盘.md` + `学习卡.md`；若存在备战包且有薄弱点命中，追加未勾选的「备战包修订建议」

#### interview-bank-pipeline（建档 / 生产端）

三个阶段：

1. **文档清洗分类**：面经源文档 → 切分条目 → subagent 分类 → `categories/` + `items.json`（318 题）
2. **Obsidian 知识图谱**：`concepts.yaml` → `obsidian_vault/`（MOC / 概念 / 索引 / 项目档案），断链自动校验
3. **GitHub 项目融合建档**：`repo_fuse fetch → match → subagent 画像/作答 → finalize`，产出 `match.json`（路由表）+ 项目画像 + 项目内作答（带 `文件:行号` 证据），并**同步快照**到 project-mock-interview 的 `references/项目/<slug>/`

脚本已内嵌在 `interview-bank-pipeline/scripts/`（pipeline.py / repo_fuse.py / verify_categories.py，另含两个一次性迁移工具 map_cards.py / distill_from_cards.py），通过 `INTERVIEW_WORKSPACE` 环境变量定位数据，不依赖 skill 目录外的任何文件。

#### interview-resume-pack（备战包 / 表达材料生产端）

从已建档项目档案生成"漏斗式表达"全套面试材料，是拷打的软前置。产出物保存在 `$INTERVIEW_WORKSPACE/obsidian_vault/40_项目档案/<slug>/备战包/`，包含**产出物七件（六类正文 + README 总览）**与**证据门机制**：

- **产出物七件**：
  1. `漏斗稿.md`：30s（痛点 + 两分法拆解 + 闭环拍点，严禁模块罗列）、3min（架构文字版 + 数据流 + 方案 + 拆法归因）、10min（2-3 个核心设计 × 三要素证据链 + 规范化代码锚点）三版。
  2. `深钻点-<名称>.md` × 2-3：证据链三要素（A 真实数字 / B 踩坑故事 / C 否决方案）至少占二的 2-3 个核心模块；每点严格五层硬结构（L1 为什么存在含否决方案 → L2 机制与参数怎么定 → L3 证据追问题清单 → L4 失效边界与反事实 → L5 规模外推与演进），附规范化代码锚点。
  3. `DHR卡.md`：核心场景的 Detection（信号/监控/日志）→ Handling（降级/兜底）→ Recovery（自愈/数据修复）与证据锚点。
  4. `不会题.md`：极限题防守模板库，四步防守协议（数字划界 → 拆关注点 → 功能性方案/专有名词降级 → 验证计划）与证据边界。
  5. `组合failure.md`：跨模块 worst-case 推演（A×B 故障组合传播链 → 最坏状态 → 检测点 → 断路设计与证据锚点）。
  6. `简历bullet.md`：自研/本人贡献已证实时为 3-5 条主 bullet（动词开头 + 机制一句话 + 数字结果 + 代码锚点）；第三方/学习谈资项目明示固定不适用声明。
  7. `README.md`：总览页（产物索引 + 完整性状态 + 深钻点拍板记录 + 完整不深钻排雷清单 + 出稿路径 + [待补]清单 + 已吸收修订建议）。
- **证据门机制（防编造红线，`scripts/evidence_gate.py`）**：
  - **锚点校验**：正文每个文件逐一执行 `python3 <本skill>/scripts/evidence_gate.py <产物文件> <repo-root>`，校验 `代码路径:行号` 真实存在，悬空即 FAIL；特例（无本人贡献 bullet / 全无实现不会题）由编排者走人工核验；README 校验相对链接均存在。
  - **数字红线**：正文中所有项目数字必须在档案或代码中有明确出处，找不到必须标 `[待补: 指标/口径]` 或删除，严禁凭空捏造。
  - **返修闭环**：任一校验 FAIL 必须由出稿者针对性返修，所有检查全 PASS 后 README 状态才写「完整」；成功吸收复盘建议并通过证据门后，自动将复盘中的修订建议标记为 `[x]`。

#### grilling（内置深挖原语）

`grilling` 是 matt pocock 的追问原语：**一次只问一个问题**（同时问多个会让人懵）、每题给出推荐答案、能查代码库就先查代码库再问，逐条追问直到该薄弱点挖透。

- 来源：[mattpocock/skills](https://github.com/mattpocock/skills)（MIT），本仓库已内置一份于 `grilling/`
- 用法：agent-project-grill 阶段 2 对低分题（四维任一 ≤2 或答不出）自动切到 grilling 深挖，追问链与要点全部记入复盘，不留在聊天里
- 兜底：该文件夹被移除时，阶段 2 的内联规则（一次一问 + 推荐答案 + 查代码库）等效执行，流程不受影响

## 四、project-mock-interview vs agent-review-audit（取舍）

两者**定位相同**：都是「题库路由匹配 → 出题 → 拷打/审查」引擎，日常二选一即可。差别在题库侧重和输出形态：

| 维度 | project-mock-interview | agent-review-audit |
|---|---|---|
| 题库 | 318 道通用大厂题（Agent 架构 / 记忆 / RAG / MCP / 评测 / 八股 / LeetCode） | 321 道 AI Agent & RAG 专项题卡 |
| 匹配方式 | 项目档案 match.json 路由（题目×概念×证据×深度） | route_project.py 按代码特征实时路由 |
| 点评 | 四维点评 + 答案要点（从作答档摘录，教学友好） | 三维打分（架构 / 生产就绪 / 健壮性，各 100 起扣） |
| 输出 | 逐题问答 + 四维得分表 + 追问 | JSON 审查报告 + 2-3 个交互追问 |
| 复盘 | 场次复盘 + 待复习清单 + 学习卡（长期复习闭环） | `.agent-audit/profile.json` 薄弱概念加权（下次命中更高权重） |
| 证据 | 引用作答档已有锚点，证据不足诚实说明 | slice_code.py 证据切片，禁止断言全局缺失 |
| 适合 | **日常模拟面试（审人）** | 考前体检 / 挖代码 gap（审代码） |

**怎么选**

- 默认用 `project-mock-interview`：它是完整的面试循环（出题→点评→答案要点→复盘→学习卡），对「产品视角、细节不熟」的人最友好——答不好它会当场教
- `agent-review-audit` 只在你想「先让面试官视角审一遍项目、看哪里有坑」时用；它输出的是体检报告，不是面试场
- 切换方式：改 `agent-project-grill` 阶段 1 指向即可（一行），或单独说"先审代码挖坑"

## 五、安装（跨平台，含 macOS 迁移）

**整包安装，勿单拆：本仓库是 1 主入口（agent-project-grill，兼公共语料枢纽）+ 5 依赖。六目录须同装在一个 skills 父目录，保持目录名；勿单独关闭组件。单件安装仅提供各 SKILL.md 声明的降级能力。**

1. 把仓库里的全部 6 个 skill 文件夹（agent-project-grill、interview-bank-pipeline、interview-resume-pack、project-mock-interview、agent-review-audit、grilling）放进任一 agent 的 skills 目录
   - 本机统一入口：`~/.cc-switch/skills/`，Codex / Claude / Gemini / Hermes 用软链指向
   - 新设备：直接放入 `~/.codex/skills/`（Codex）或 `~/.claude/skills/`（Claude）
2. 设置数据工作区：`export INTERVIEW_WORKSPACE=<数据目录>`（写入 shell 配置长期生效）
   - 生产/建档时初始化：从 `agent-project-grill/references/题库/` 复制缺少的 `items.json` / `concepts.yaml` / `schema.json` 到工作区；已有文件不覆盖。练习直接读取整包公共题库；个人记录保存在 `obsidian_vault/`
   - 未设置时兼容回退 `~/桌面/面试文档裁切`（仅旧本机；跨平台必须显式设置）
3. 依赖：python3、PyYAML、git、jq（仅 project-mock-interview 路由提取用，macOS 用 `brew install jq`）

**macOS 迁移三步**：拷全部 6 个 skill 文件夹（含内置 grilling） → 设 `INTERVIEW_WORKSPACE` → 装依赖。已建档项目同时携带 `agent-project-grill/references/题库/` 与 `project-mock-interview/references/项目/`（拷打只需要题库 + 项目快照，不需要 repos_cache）。注意：要**生成备战包**（interview-resume-pack）时还需要可解析的项目源码仓库根（本地 clone 或可 fetch 的 URL），仅带快照不够。

## 六、数据与隐私

- 仓库只放 skill 代码与语料快照；**不要上传**：`repos_cache/`（第三方仓库克隆）、原始面经文档、`obsidian_vault/30_手写笔记`（个人笔记）
- 个人数据全部落在 `$INTERVIEW_WORKSPACE`，与 skill 分离
- 题库/档案同步命令见 `project-mock-interview/references/README.md`

## 七、目录结构

```
interview-mock-skill/
├── README.md                     # 本文件
├── agent-project-grill/          # 编排壳：建档检查 → 备战包软前置 → 拷打 → grilling → 复盘 → 学习卡
│   └── references/题库/         # 公共题库唯一仓库副本：items.json / concepts.yaml / schema.json
├── interview-bank-pipeline/      # 建档/生产端：清洗分类 + 图谱 + 项目融合（脚本内嵌）
├── interview-resume-pack/        # 备战包生成：漏斗稿 + 深钻点 + 防守材料（scripts/evidence_gate.py）
├── project-mock-interview/       # 拷打引擎：读相邻主入口公共题库 + 自身项目档案快照 + 四维点评
├── agent-review-audit/           # 可选体检：321 道 Agent/RAG 题卡 + 三维打分
├── grilling/                     # 深挖原语（来自 mattpocock/skills，MIT）
├── .github/                      # GitHub Pages 部署工作流
├── .pages/                       # 文档站源（mkdocs）
└── site-test/                    # 文档站构建产物
```

## 八、评审记录（multi-agent skill review）

评审时间：2026-08-16（preview `a09eb3c`）。按 multi-agent-skill-review 三角色并行实测：harness 贴合度 / 模型适配度 / 数据链路。

| 评审官 | 评分 | 结论 |
|---|---|---|
| harness 贴合度官 | 8.5/10 | 六个 skill 均可加载；触发词覆盖建档/备战包/拷打/审代码/深挖各入口；grilling 已内置并被显式引用 |
| 模型适配度官 | 8/10 | 阶段 0 建档分支可照跑；四维 1/3/5 锚点与输出模板齐全；token 预算靠分层加载纪律实现，合规 |
| 数据链路官 | 8.5/10 | `finalize → sync_snapshot` 真实调用并实测通过；本地与仓库逐文件一致；学习卡/复盘有写入者与读取者 |

已修复（P1，commit `a09eb3c`）：

- `project-mock-interview/scripts/` 残留带写死路径的旧脚本副本 → 说明：旧副本已清理完毕，生产脚本统一位于 `interview-bank-pipeline/scripts/` 完整可用、正在工作且无改动计划
- `agent-review-audit/scripts/sync_corpus.py` 硬编码源路径 → 参数化（`--source` / `AGENT_REVIEW_CARDS_SOURCE`）
- 本地 `.cc-switch` 与仓库脚本不一致 → 补齐同步

遗留低危（不影响使用）：

- 三个 SKILL.md 的 `version` / `use_when` 为非标准 frontmatter 字段（校验提示，不影响加载）
- `map_cards.py` 正则 SyntaxWarning（一次性迁移工具）
- `~/桌面/面试文档裁切` 兼容回退字符串为有意保留（完整可用且正在工作，新设备用 `INTERVIEW_WORKSPACE`）

续审记录：

- 2026-09-08 interview-resume-pack 双轮审修(codex,五维度,14项发现全修复+证据门4边界bug修复)
