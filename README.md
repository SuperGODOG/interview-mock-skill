# interview-mock-skill

针对 **Agent 开发岗面试**的练习全家桶：项目建档 → 路由出题 → 模拟拷打 → grilling 深挖 → 复盘 → 学习卡。跨平台、跨 agent（Codex / Claude / Gemini / Hermes），数据与代码分离，个人数据不上传。

> 核心承诺：**每题有记录、低分有 grilling、场场有复盘、复习有学习卡**。

---

## 一、这套 skill 解决什么问题

面试 Agent 开发岗时，**项目拷打（设计 / 细节 / 评估）是最重的一块**。常见痛点：

- 有项目但说不清技术细节（尤其是产品/管理视角的候选人）
- 练习时没有真实面试官，不知道会被追问哪些点
- 练完就忘，答得一般的题下次不会优先复习

这套方案把「建档 → 出题 → 点评 → 深挖 → 复盘 → 复习」全部固化进 skill，一次"开一场"跑完整条链。

## 二、四件套定位

| Skill | 角色 | 谁调用 | 频率 |
|---|---|---|---|
| [agent-project-grill](agent-project-grill/SKILL.md) | 编排壳（日常唯一入口） | 你 | 每次练习 |
| [interview-bank-pipeline](interview-bank-pipeline/SKILL.md) | 建档 / 生产端 | agent-project-grill 或你 | 新项目 / 项目大改 / 题库更新 |
| [project-mock-interview](project-mock-interview/SKILL.md) | 拷打引擎本体（主循环） | agent-project-grill | 每次练习 |
| [agent-review-audit](agent-review-audit/SKILL.md) | 可选代码体检 | 你（显式要求时） | 考前 / 挖坑 |

`grilling`（matt pocock 技能）作为深挖原语被编排调用：推荐随 mattpocock/skills 一并安装（仓库不内置）；缺失时 agent-project-grill 按阶段 2 内联规则兜底，流程不受影响。

## 三、核心工作流

### 两条路径

```
新项目：  interview-bank-pipeline 建档 ──► agent-project-grill 拷打
已建档：  agent-project-grill 直接拷打（pipeline 不参与）
```

`agent-project-grill` 阶段 0 会自动判断：项目 slug 的 `match.json` 是否已在 project-mock-interview 快照里。没有就先建档，有就直接开打。你只需要说：

- 新项目：`开一场 https://github.com/<owner>/<repo>`
- 已建档：`开一场 skillforge`

### 一次完整场次长这样

1. **环境与建档自检**：解析 `INTERVIEW_WORKSPACE`；检查项目是否建档；读上次复盘的学习卡/待复习清单
2. **模拟拷打**（project-mock-interview）：按项目路由表出题（薄弱优先 / 复习优先 / 深度递进），一次一题，四维点评（概念理解 / 原理深度 / 落地证据 / 结构完整度），默认 3 题/场
3. **grilling 深挖**：任一维 ≤2 或答不出的题，切到一问一答的追击模式，agent 会查代码库帮你补细节
4. **复盘 + 学习卡**：场次复盘（题目清单 + 得分表 + grilling 记录）写进 vault；低分题生成学习卡（`- [ ] Lxx ｜ 薄弱维度 ｜ 一句话记忆点 ｜ 下次复习`），下一场优先清

### 各阶段细节

#### agent-project-grill（编排壳）

- **阶段 0**：`INTERVIEW_WORKSPACE` 解析 → 建档检查 → 读复习源。未建档自动走 interview-bank-pipeline 建档并同步快照
- **阶段 1**：按 project-mock-interview 的拷问模式逐题问答，每题当场记录（题 id / 作答摘要 / 四维得分）
- **阶段 2**：低分题切 grilling，追问链与要点逐条记录，不留在聊天里
- **阶段 3**：写 `$INTERVIEW_WORKSPACE/obsidian_vault/40_项目档案/<slug>/面试复盘.md` + `学习卡.md`（纯 markdown，Obsidian 只是可选查看器）

#### interview-bank-pipeline（建档 / 生产端）

三个阶段：

1. **文档清洗分类**：面经源文档 → 切分条目 → subagent 分类 → `categories/` + `items.json`（240 题）
2. **Obsidian 知识图谱**：`concepts.yaml` → `obsidian_vault/`（MOC / 概念 / 索引 / 项目档案），断链自动校验
3. **GitHub 项目融合建档**：`repo_fuse fetch → match → subagent 画像/作答 → finalize`，产出 `match.json`（路由表）+ 项目画像 + 项目内作答（带 `文件:行号` 证据），并**同步快照**到 project-mock-interview 的 `references/项目/<slug>/`

脚本已内嵌在 `interview-bank-pipeline/scripts/`（pipeline.py / repo_fuse.py / verify_categories.py，另含两个一次性迁移工具 map_cards.py / distill_from_cards.py），通过 `INTERVIEW_WORKSPACE` 环境变量定位数据，不依赖 skill 目录外的任何文件。

## 四、project-mock-interview vs agent-review-audit（取舍）

两者**定位相同**：都是「题库路由匹配 → 出题 → 拷打/审查」引擎，日常二选一即可。差别在题库侧重和输出形态：

| 维度 | project-mock-interview | agent-review-audit |
|---|---|---|
| 题库 | 240 道通用大厂题（Agent 架构 / 记忆 / RAG / MCP / 评测 / 八股 / LeetCode） | 243 道 AI Agent & RAG 专项题卡 |
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

1. 把四个 skill 文件夹放进任一 agent 的 skills 目录
   - 本机统一入口：`~/.cc-switch/skills/`，Codex / Claude / Gemini / Hermes 用软链指向
   - 新设备：直接放入 `~/.codex/skills/`（Codex）或 `~/.claude/skills/`（Claude）
2. 设置数据工作区：`export INTERVIEW_WORKSPACE=<数据目录>`（写入 shell 配置长期生效）
   - 目录内放：`items.json` / `concepts.yaml` / `schema.json` / `obsidian_vault/`
   - 未设置时兼容回退 `~/桌面/面试文档裁切`（仅旧本机；跨平台必须显式设置）
3. 依赖：python3、PyYAML、git、jq（仅 project-mock-interview 路由提取用，macOS 用 `brew install jq`）

**macOS 迁移三步**：拷四个 skill 文件夹 → 设 `INTERVIEW_WORKSPACE` → 装依赖。已建档项目把 `project-mock-interview/references/` 一起带走即可（拷打只需要题库 + 项目快照，不需要 repos_cache）。

## 六、数据与隐私

- 仓库只放 skill 代码与语料快照；**不要上传**：`repos_cache/`（第三方仓库克隆）、原始面经文档、`obsidian_vault/30_手写笔记`（个人笔记）
- 个人数据全部落在 `$INTERVIEW_WORKSPACE`，与 skill 分离
- 题库/档案同步命令见 `project-mock-interview/references/README.md`

## 七、目录结构

```
interview-mock-skill/
├── README.md                     # 本文件
├── agent-project-grill/          # 编排壳：建档检查 → 拷打 → grilling → 复盘 → 学习卡
├── interview-bank-pipeline/      # 建档/生产端：清洗分类 + 图谱 + 项目融合（脚本内嵌）
├── project-mock-interview/       # 拷打引擎：240 题题库 + 项目档案快照 + 四维点评
├── agent-review-audit/           # 可选体检：243 道 Agent/RAG 题卡 + 三维打分
├── .github/                      # GitHub Pages 部署工作流
├── .pages/                       # 文档站源（mkdocs）
└── site-test/                    # 文档站构建产物
```
