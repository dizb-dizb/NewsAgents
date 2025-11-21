# 📰 Intelligent News Agent System  
### 基于 LangChain / LangGraph / LlamaIndex 的多智能体智能新闻系统  
**RAG + Task Routing + Multi-Agent + Memory + Continual Learning**

本项目是一个面向真实业务场景的 **智能新闻处理与问答系统**，通过 **多智能体（Multi-Agent）协作**、**RAG 检索增强**、**上下文工程（Context Engineering）** 和 **持续学习（Continual Training）** 实现对新闻的自动抓取、分类、事件抽取、摘要生成与智能问答。

本项目用于展示 Agent 工程能力，全方位覆盖企业级 JD 所需技能，包括：

- 🧠 **任务拆解与策略调度（Task Decomposition & Orchestration）**  
- 👥 **多智能体协作（Multi-Agent System）**  
- 🔧 **工具调用（Tool Calling）**  
- 🗂 **记忆管理（Memory & Long-term Storage）**  
- 📚 **RAG 与持续知识更新（Retrieval-Augmented Generation + Continual Training）**  
- 💡 **Context Engineering（提示工程 + 动态上下文）**  
- ⚙️ **LangChain / LangGraph 工作流构建**  
- 🧩 **LlamaIndex 用于索引、事件知识库、实体库**

---

## 🚀 功能特点（Features）

### 1. 多智能体（Multi-Agent）新闻处理系统

系统由多个专用智能体组成，协作完成不同任务：

| Agent 名称 | 功能 |
|-----------|------|
| **Task Router Agent** | 自动分析用户输入，完成任务拆解与路由 |
| **NewsCrawler Agent** | 通过工具自动抓取新闻数据 |
| **NewsClassifier Agent** | 新闻分类（如政治/经济/科技等） |
| **Summarizer Agent** | 生成长新闻摘要、要点、分段结构化信息 |
| **EventExtractor Agent** | 新闻事件抽取（主语/动作/客体/影响） |
| **NewsQA Agent** | 基于 RAG 的问答 |
| **Memory Manager Agent** | 管理短期/长期记忆，自动写入向量库 |

所有 Agents 均由 **Orchestrator（大脑）** 统一调度。

---

### 2. 基于 LangGraph 的 Agent 工作流

采用 LangChain 官方推荐的 **LangGraph**，构建可视化、可追踪、支持长程运行的智能体工作流，包括：

- 动态任务路由  
- 多 Agent 执行链  
- 工具自动调用  
- 状态持久化  
- Agent 间共享记忆  

---

### 3. 新闻 RAG 引擎（LlamaIndex + Hybrid Search）

新闻数据被解析为：

- 文本节点（Node）  
- 事件节点（Event Node）  
- 实体节点（Entity Node）  
- 时间线节点（Timeline Node）  

并通过 LlamaIndex 构建：

- SummaryIndex（摘要）  
- VectorStoreIndex（向量索引）  
- KeywordTableIndex（关键词索引）  
- TimeLineIndex（按时间排序检索）  

支持：

- **Hybrid Search（BM25 + 向量检索）**  
- **Reranker（如 bge-reranker）**  
- **事件级 Chunking（比普通分段更适合新闻）**

---

### 4. 持续学习（Continual Training）

系统具备自动学习能力，通过定时任务执行：

- 新闻抓取  
- 新闻内容入库  
- 事件抽取 + 合并旧事件  
- 摘要更新  
- 向量库扩展  
- timeline 自动演化  

构成“越用越聪明”的知识体系。

---

### 5. Context Engineering（上下文工程）

系统的 Prompt 采用：

- 动态模板加载（按新闻领域切换）  
- 多角色提示（Role Prompting）  
- 递归摘要（Recursive Summarization）  
- 上下文压缩 + 长短期记忆融合  

有效提升问答质量与模型稳定性。

---


