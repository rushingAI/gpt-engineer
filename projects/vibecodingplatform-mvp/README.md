# Vibecoding Platform MVP

将 `gpt-engineer` 命令行工具转型为基于 Web 的 Vibecoding 平台。

## 项目结构

```
vibecodingplatform-mvp/
├── backend/            # FastAPI 后端服务
│   ├── server.py       # 主服务器
│   ├── requirements.txt
│   ├── test_api.py     # API 测试
│   └── run.sh          # 启动脚本
├── client/             # React 前端应用
│   ├── src/
│   │   ├── App.jsx     # 主组件
│   │   └── App.css     # 样式
│   ├── package.json
│   └── run.sh          # 启动脚本
└── PLAN.md             # 项目计划
```

## 快速开始

### 前置要求

- Python 3.8+
- Node.js 16+
- OpenAI API Key 或 Anthropic API Key

### 1. 配置环境变量

在项目根目录（`gpt-engineer/`）创建 `.env` 文件：

```bash
OPENAI_API_KEY=your_api_key_here
# 或者使用 Anthropic
# ANTHROPIC_API_KEY=your_api_key_here
# MODEL_NAME=claude-3-5-sonnet-20241022
```

### 2. 启动后端服务

```bash
cd projects/vibecodingplatform-mvp/backend
pip install -r requirements.txt
./run.sh
```

后端将在 `http://localhost:8000` 启动。

### 3. 启动前端应用

在**新的终端**中：

```bash
cd projects/vibecodingplatform-mvp/client
npm install
./run.sh
```

前端将在 `http://localhost:5173` 启动。

### 4. 开始使用

1. 打开浏览器访问 `http://localhost:5173`
2. 在输入框中输入提示词，例如："创建一个待办事项列表应用"
3. 点击 "✨ 生成应用" 按钮
4. 等待 AI 生成代码
5. 在预览窗口中查看运行结果

## 功能特性

- ✅ **自然语言输入**: 用中文或英文描述你想要的应用
- ✅ **现代化技术栈**: 生成 React + Tailwind CSS 的专业级代码
- ✅ **实时代码生成**: AI 自动编写完整的应用代码
- ✅ **浏览器内预览**: 无需本地执行，直接在浏览器中运行
- ✅ **迭代改进**: 支持基于上下文的代码优化和 bug 修复
- ✅ **组件库支持**: 预装 lucide-react 图标库
- ✅ **错误提示**: 友好的错误信息和加载状态

## API 端点

### `POST /generate`
生成应用代码。

**请求:**
```json
{
  "prompt_text": "创建一个计时器应用"
}
```

**响应:**
```json
{
  "index.html": "<!DOCTYPE html>...",
  "style.css": "body { ... }",
  "script.js": "// ..."
}
```

完整 API 文档: http://localhost:8000/docs

## 示例提示词

### 简单应用
- 🔢 "创建一个计数器应用，有增加和减少按钮，使用渐变背景"
- ⏱️ "创建一个番茄钟计时器，25 分钟工作，5 分钟休息"
- 🧮 "创建一个计算器应用，支持基本的四则运算"

### 进阶应用
- ✅ "创建一个待办事项列表，支持添加、删除、标记完成，使用卡片布局"
- 📊 "创建一个数据仪表盘，显示 4 个统计卡片（用户数、收入、增长率、活跃度）"
- 🎨 "创建一个颜色选择器，支持 RGB、HEX 输入，实时预览"
- 🎮 "创建一个记忆卡片游戏，翻转动画效果"

## 故障排除

### 后端启动失败

1. 检查是否配置了 API key
2. 确认 Python 依赖已安装: `pip install -r backend/requirements.txt`
3. 检查端口 8000 是否被占用

### 前端无法连接后端

1. 确认后端服务正在运行
2. 检查浏览器控制台的 CORS 错误
3. 确认 `src/App.jsx` 中的 `API_URL` 设置正确

### 生成失败

1. 查看后端终端的错误日志
2. 确认 API key 有效且有足够的配额
3. 尝试简化提示词

## 技术栈

### 后端
- **FastAPI**: 现代 Python Web 框架
- **gpt-engineer**: AI 代码生成引擎
- **OpenAI/Anthropic**: 大语言模型

### 前端
- **React 18**: UI 框架
- **Vite**: 构建工具
- **Sandpack**: 浏览器内代码执行（React 模板）
- **Tailwind CSS**: 实用优先的 CSS 框架
- **lucide-react**: 现代化图标库

### 生成的应用
- **React 函数式组件**: 使用 Hooks 管理状态
- **Tailwind CSS**: 响应式、现代化设计
- **localStorage**: 客户端数据持久化

## 未来改进

- [ ] WebSocket 流式传输，实时显示生成过程
- [ ] 项目历史记录和版本管理
- [ ] 支持迭代改进生成的代码
- [ ] 用户认证和项目保存
- [ ] 支持更多编程语言和框架
- [ ] 代码导出和下载功能

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

继承自 gpt-engineer 项目的许可证。

