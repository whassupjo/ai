# Enterprise-RAG-Knowledge-Agent

企业知识库智能问答系统，支持 PDF、Word、TXT、Markdown 文档上传、文本解析、文档切片、知识检索、角色权限过滤和基于通义千问 Qwen 的流式问答生成。

## 项目定位

这个项目对应企业内部“制度文档查询、流程咨询、知识沉淀”的真实场景。用户上传企业知识文档后，系统将文档切分为知识片段并建立本地索引；员工提问时，系统先召回相关片段，再把片段交给大模型生成答案。

页面已经改成 ChatGPT 风格：左侧为知识库上传和角色设置，右侧为聊天窗口，回答支持流式输出。

## 技术栈

- Python
- FastAPI
- 通义千问 Qwen API / DashScope OpenAI Compatible API
- PDF / Word / TXT / Markdown 文档解析
- 轻量本地检索
- Server-Sent Events 流式输出
- HTML + JavaScript 前端
- Docker

## 功能

- 上传 PDF、Word、TXT、Markdown 文档
- 自动识别 TXT 常见编码：UTF-8、GB18030、GBK
- 自动解析、清洗和切片
- 建立本地持久化知识索引
- 支持 guest / employee / admin 三级访问权限
- 基于 RAG 流程生成企业知识问答结果
- 返回召回来源，方便验证答案依据
- 支持 ChatGPT 风格流式输出
- 支持清空当前对话和清空知识库索引

## 目录结构

```text
Enterprise-RAG-Knowledge-Agent
├── backend
│   └── app
│       ├── api
│       │   ├── chat.py
│       │   └── documents.py
│       ├── core
│       │   └── config.py
│       ├── services
│       │   ├── chunker.py
│       │   ├── document_parser.py
│       │   ├── llm_client.py
│       │   ├── permissions.py
│       │   ├── rag_agent.py
│       │   └── vector_store.py
│       └── main.py
├── frontend
│   └── index.html
├── Dockerfile
├── requirements.txt
└── README.md
```

## 快速启动

```bash
pip install -r requirements.txt
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

启动后打开：

```text
http://127.0.0.1:8000/
```

## 千问 API 配置

项目会读取系统环境变量中的 `DASHSCOPE_API_KEY`。不要把真实 API Key 写进 GitHub。

`.env` 可配置：

```env
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
MODEL_NAME=qwen-plus
ENABLE_MOCK_LLM=false
VECTOR_STORE_PATH=./data/vector_store.json
```

如果暂时没有 API Key，可以改成：

```env
ENABLE_MOCK_LLM=true
```

注意：阿里云 RAM 里的 `AliyunServiceRoleForResourceMetaCenter` 是资源中心服务关联角色，不是千问 API Key。项目调用千问需要在阿里云百炼 / DashScope 控制台获取 `DASHSCOPE_API_KEY`。

## API 示例

上传文档：

```bash
curl -X POST http://localhost:8000/documents/upload \
  -F "file=@制度文档.txt" \
  -F "access_role=employee"
```

普通问答：

```bash
curl -X POST http://localhost:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"question":"报销流程是什么？","role":"employee","top_k":4}'
```

流式问答：

```bash
curl -N -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"question":"报销流程是什么？","role":"employee","top_k":4}'
```

清空知识库索引：

```bash
curl -X DELETE http://localhost:8000/documents/
```

## 可写进简历的项目描述

**企业知识库智能问答系统 | RAG / FastAPI / Qwen API**

基于 FastAPI 搭建企业知识库问答服务，实现 PDF、Word、TXT 等文档上传、解析、切片和知识检索。设计 RAG 检索增强链路，先召回相关知识片段，再结合通义千问 Qwen 大模型生成答案，降低模型直接回答造成的幻觉问题。实现 guest / employee / admin 三级权限过滤，使不同角色只能访问对应知识内容，并通过 Server-Sent Events 实现类 ChatGPT 的流式输出体验。


