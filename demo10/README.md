[返回首页](../README.md) | [上一节：demo9](../demo9/README.md) | [下一节：demo11](../demo11/README.md)

# demo10：RAG Agent Demo

这一节把 Agent 从“只依赖上下文窗口”推进到“可以查询外部知识库”的形态，核心主题是 RAG。

## 本节目标

- 理解为什么 RAG 是“先检索，再生成”
- 学会把文档切分、向量化、入库和检索串成一条完整链路
- 理解外部知识库为什么能显著降低“凭空编造”的概率

## 入口文件

- [rag_demo.py](rag_demo.py)

## 关键模块

- [document_loader.py](document_loader.py)
- [embeddings.py](embeddings.py)
- [rag_store.py](rag_store.py)
- [config.py](config.py)
- [knowledge_base/agent_basics.md](knowledge_base/agent_basics.md)

## 运行前准备

先安装根依赖：

```bash
pip install -r requirements.txt
```

再准备一个启用了 `pgvector` 扩展的 PostgreSQL 数据库，并配置：

```powershell
$env:DEEPSEEK_API_KEY="你的 API Key"
$env:ZHIPU_API_KEY="你的智谱 API Key"
$env:PGVECTOR_HOST="你的 PostgreSQL 公网访问地址"
$env:PGVECTOR_PASSWORD="你的数据库密码"
```

## 运行方式

```bash
python demo10/rag_demo.py
```

## 本节新增能力

- 把 `knowledge_base` 里的 Markdown 文档加载进来
- 按 `CHUNK_SIZE` 和 `CHUNK_OVERLAP` 把长文档切成 chunks
- 使用智谱 `embedding-3` 把文本转成向量
- 把 chunk 内容和向量写入 PostgreSQL pgvector
- 用用户问题做相似度检索，取回 Top-K 相关资料
- 把检索结果整理进 prompt，再交给大模型生成答案

## 典型流程

1. `load_knowledge_base()` 读取知识库文档
2. `split_text()` 把文档切成适合检索的片段
3. `embed_texts()` 调用 embedding 模型生成向量
4. `rebuild_index()` 初始化 pgvector 表并写入索引
5. `retrieve()` 根据用户问题找回相关 chunks
6. `answer_with_rag()` 把资料和问题一起交给 LLM 回答

## 学习重点

和前面几节相比，这一节更强调：

- Agent 不一定只能依赖 prompt 和历史消息
- 外部知识库可以显著降低“凭空编造”的概率
- RAG 的关键链路不是某一个 prompt，而是“加载、切分、向量化、入库、检索、生成”
- 查询文本和文档文本必须使用同一个 embedding 模型，才能处在同一个向量空间

## 示例知识库

- [knowledge_base/agent_basics.md](knowledge_base/agent_basics.md)
- [knowledge_base/react.md](knowledge_base/react.md)
- [knowledge_base/workflow.md](knowledge_base/workflow.md)
- [knowledge_base/hitl.md](knowledge_base/hitl.md)

## 建议练习

- 新增一篇知识库文档，观察检索结果和回答是否变化
- 调整 chunk 大小、overlap、Top-K，比较召回质量变化
- 故意问一个知识库里没有的问题，观察系统是否会明确说明资料不足

## 与上一节相比多了什么

如果 `demo9` 教你的是“让 Agent 在关键动作前更安全”，那么 `demo10` 教你的就是“让 Agent 在回答问题前先查资料”。

[返回首页](../README.md) | [上一节：demo9](../demo9/README.md) | [下一节：demo11](../demo11/README.md)
