# Vibecoding Platform - Backend

FastAPI 后端服务，封装 gpt-engineer 的代码生成能力。

## 快速启动

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

在项目根目录创建 `.env` 文件：

```bash
OPENAI_API_KEY=your_api_key_here
# 或者使用 Anthropic
# ANTHROPIC_API_KEY=your_api_key_here
# MODEL_NAME=claude-3-5-sonnet-20241022
```

### 3. 启动服务

```bash
# 方式 1: 直接运行
python server.py

# 方式 2: 使用 uvicorn
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

服务将在 `http://localhost:8000` 启动。

## API 端点

### `GET /`
健康检查端点，返回服务状态。

### `POST /generate`
生成应用代码。

**请求体:**
```json
{
  "prompt_text": "创建一个贪吃蛇游戏"
}
```

**响应:**
```json
{
  "index.html": "<!DOCTYPE html>...",
  "style.css": "body { ... }",
  "script.js": "const game = ..."
}
```

### `GET /health`
详细健康检查，包含 AI 初始化状态和配置信息。

## API 文档

启动服务后访问:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 开发说明

### 目录结构
```
backend/
├── server.py          # FastAPI 应用主文件
├── requirements.txt   # Python 依赖
└── README.md         # 本文件
```

### 关键技术
- **FastAPI**: 现代 Python Web 框架
- **gpt-engineer**: 复用现有的 AI 代码生成逻辑
- **TemporaryDirectory**: 绕过磁盘持久化，直接在内存中处理

### 扩展点
- [ ] 添加流式响应 (WebSocket)
- [ ] 添加会话管理
- [ ] 添加代码改进端点
- [ ] 添加用户认证

