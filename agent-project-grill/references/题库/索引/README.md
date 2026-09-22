# 面试题库多维分类检索索引

> 本目录提供针对 `agent-project-grill/references/题库/items.json` 全量公共题目的多维静态检索索引。
> **设计原则**: 单一真理源（Canonical Source of Truth）、按需轻量检索、不重复冗余答案、ID 稳定对应。

## 索引分类总览

| 索引名称与链接 | 机器检索 JSON | 题数 | 分类范围与说明 |
|---|---|---|---|
| [业务线与项目实战面试题索引](./01_business_projects.md) | `01_business_projects.json` | **33** | 涵盖业务流程拆解、秒杀架构、大文件分片上传与断点续传、跨集群多节点部署及实际生产落地问题。 |
| [前端工程、渲染与页面交互题索引](./02_frontend.md) | `02_frontend.json` | **3** | 涵盖从浏览器 URL 到页面渲染完整链路、前端大文件分片与 Hash 计算、AI 生成代码前端端到端（E2E）与影响面回归测试。 |
| [后端基建 · 操作系统（OS）面试题索引](./02_backend_os.md) | `02_backend_os.json` | **11** | 涵盖 Linux 内核调度、进程/线程/协程原理、用户态上下文切换、IPC 进程间通信、系统调用与资源监控。 |
| [后端基建 · 计算机网络面试题索引](./02_backend_network.md) | `02_backend_network.json` | **12** | 涵盖 TCP/IP 协议栈、三次握手/四次挥手、HTTP/1.1 与 HTTP/2、SSE 流式、WebSocket、Nginx 反向代理与负载均衡。 |
| [后端基建 · 数据库与存储面试题索引](./02_backend_database.md) | `02_backend_database.json` | **65** | 涵盖 MySQL 与 PostgreSQL 引擎机制、B+ 树、聚簇与联合索引、事务隔离级别与 MVCC、锁机制、CAS/状态机、Redis 缓存与持久化。 |
| [后端基建 · 消息队列与异步流面试题索引](./02_backend_mq.md) | `02_backend_mq.json` | **9** | 涵盖 RabbitMQ 与 Kafka 核心架构、Quorum 队列、分区消费模型、消息积压治理、死信队列、ACK 与幂等消费。 |
| [Agent Harness 核心设计与评测沙箱面试题索引](./03_agent_harness.md) | `03_agent_harness.json` | **60** | 涵盖 Harness 测试基准、Loop Engineering 迭代循环、自动评测（LLM-as-a-Judge）、Grader 评分器、Trace 归因、Badcase 数据飞轮、代码沙箱隔离执行与环境部署。 |
| [Agent 架构设计、工作流与编排面试题索引](./04_agent_architecture.md) | `04_agent_architecture.json` | **146** | 涵盖 ReAct 循环、Plan-and-Execute 规划、Reflection 自反思、LangGraph 图编排、Multi-Agent 多智能体协同、MCP 协议、Tool Calling 与长短期记忆机制。 |
| [RAG 检索增强生成与知识库面试题索引](./05_rag_retrieval.md) | `05_rag_retrieval.json` | **41** | 涵盖文档解析、Semantic Chunking 分块、父子切分、向量表示（Embedding）、BM25 关键词检索、混合检索（RRF）、Rerank 精排策略与幻觉抑制。 |
| [Java 核心、JVM 与并发编程面试题索引](./06_backend_java.md) | `06_backend_java.json` | **21** | 涵盖 HashMap 底层与位运算寻址、ConcurrentHashMap、线程池核心参数、JMM 内存模型、volatile 内存屏障、GC 垃圾收集与类加载机制。 |
| [算法与手撕代码题索引](./07_algorithms.md) | `07_algorithms.json` | **31** | 涵盖 LeetCode 经典题、快速选择、反转单链表、多叉树路径查找、动态规划、LRU 缓存、二叉树遍历与高并发算法设计。 |
| [通用综合、行为面与反问面试题索引](./08_general_behavior.md) | `08_general_behavior.json` | **16** | 涵盖国企特别版、团队反问、业务反问、综合行为面、技术成长与职业规划沟通。 |
| **全库总计** | `index_manifest.json` | **445** | 覆盖全部公共提问题目 |

## 检索路由与降级策略

1. **分类精准路由**:
   - 业务与项目考察：优先读取 `01_business_projects.json`
   - 前端工程与渲染交互：优先读取 `02_frontend.json`
   - 后端计算机基础：按需选择 OS (`02_backend_os.json`)、网络 (`02_backend_network.json`)、数据库 (`02_backend_database.json`)、消息队列 (`02_backend_mq.json`)
   - Agent Harness 评测与沙箱：优先读取 `03_agent_harness.json`
2. **唯一内容回源**:
   - 索引文件仅保存稳定 `id`、`line`、`text`、`tag` 和 `depth`，不复制长文本答案。
   - 提取题目完整四步答题框架（core/steps）时，直接以 `id` 索引回查 `../items.json`。
3. **容灾降级**:
   - 若任何分类索引文件缺失，检索流程自动回退为遍历 `../items.json` 全量语料或使用 `concepts.yaml` 关键词匹配。
