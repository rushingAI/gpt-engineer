# 流式生成功能快速启动

## 快速开始

### 1. 启动后端服务器

```bash
cd /Users/gaochang/gpt-engineer/projects/vibecodingplatform-mvp/backend
python server.py
```

后端将在 `http://localhost:8000` 启动

### 2. 启动前端开发服务器

```bash
cd /Users/gaochang/gpt-engineer/projects/vibecodingplatform-mvp/client
npm run dev
```

前端将在 `http://localhost:5173` 启动

### 3. 访问应用

打开浏览器访问：http://localhost:5173

## 测试流式生成

### 简单测试

1. 点击"开始创建"按钮
2. 输入：`创建一个待办事项应用`
3. 观察对话框左侧的实时进度：
   - 正在分析需求...
   - 使用模板: react-ts-shadcn
   - 正在生成代码...
   - 已生成 package.json
   - 已生成 src/pages/Index.tsx
   - ...
   - 代码生成完成 (N 个文件)
   - 正在启动容器...
   - 挂载文件系统完成
   - 安装依赖中...
   - 启动开发服务器完成

### 测试改进功能

1. 在生成的应用基础上
2. 输入：`添加一个删除按钮`
3. 观察流式改进进度

## 功能特性

### 实时进度显示

- ✅ 所有步骤在对话框中实时显示
- ✅ 使用 lucide-react 图标：
  - `Loader2`（旋转）：进行中
  - `CheckCircle2`：完成
  - `Clock`：等待
  - `AlertTriangle`：失败
- ✅ 颜色编码：
  - 绿色 (#22c55e)：完成
  - 主题色：进行中
  - 红色 (#ef4444)：失败
  - 灰色：等待

### 两个阶段

1. **代码生成阶段**（后端 SSE）
   - 分析需求
   - 选择模板
   - 生成代码文件
   - 显示每个生成的文件名

2. **环境准备阶段**（前端 WebContainer）
   - 启动容器
   - 挂载文件系统
   - 安装依赖
   - 启动开发服务器

### 数据持久化

- ✅ 所有进度步骤保存到 localStorage
- ✅ 刷新页面后仍能看到历史进度
- ✅ 向后兼容旧数据格式

## API 端点

### 流式生成

```
POST http://localhost:8000/generate-stream
Content-Type: application/json

{
  "prompt_text": "创建一个待办事项应用",
  "use_template": true
}
```

返回 SSE 流：
```
data: {"type":"status","content":"正在分析需求..."}

data: {"type":"file","filename":"package.json"}

data: {"type":"complete","files":{...},"filesCount":8}
```

### 流式改进

```
POST http://localhost:8000/improve-stream
Content-Type: application/json

{
  "files": {...},
  "improvement_request": "添加删除按钮"
}
```

## 调试

### 查看 SSE 数据流

1. 打开浏览器开发工具
2. 切换到 Network 面板
3. 筛选 EventStream 类型
4. 查看 /generate-stream 请求
5. 点击查看 Response 数据

### 查看对话消息状态

在浏览器控制台输入：
```javascript
// 查看当前项目
const project = JSON.parse(localStorage.getItem('vibecodingplatform_current_app'))
console.log(project.messages)

// 查看最后一条消息的步骤
const lastMsg = project.messages[project.messages.length - 1]
console.log(lastMsg.steps)
```

### 后端日志

后端会在终端输出详细日志：
```
📝 收到生成请求: 创建一个待办事项应用...
   模式: 模板模式
   应用类型: web_app
   使用模板: react-ts-shadcn
   AI 生成了 8 个文件
✓ 模板模式生成完成，最终 15 个文件
```

## 常见问题

### Q: 看不到流式进度？

**A:** 检查：
1. 后端是否正常运行（http://localhost:8000）
2. 浏览器控制台是否有错误
3. Network 面板中 SSE 请求是否成功
4. 尝试刷新页面

### Q: 步骤卡住不动？

**A:** 可能原因：
1. WebContainer 启动失败（查看控制台错误）
2. npm install 时间较长（首次安装需要 10-20 秒）
3. 网络问题（检查网络连接）

### Q: 刷新后进度消失？

**A:** 进度应该保存在 localStorage 中。检查：
1. 浏览器是否禁用了 localStorage
2. 是否处于隐私模式
3. localStorage 是否已满

### Q: 图标显示不正确？

**A:** 确保：
1. `lucide-react` 已正确安装
2. 没有 import 错误
3. 图标名称拼写正确

## 技术栈

- **后端**: Python + FastAPI + SSE (Server-Sent Events)
- **前端**: React + Vite
- **图标**: lucide-react
- **预览**: WebContainers API
- **存储**: localStorage

## 下一步

测试完成后，可以：
1. 查看 `STREAMING_TEST.md` 进行全面测试
2. 根据测试结果优化性能
3. 添加更多错误处理
4. 实现更多 UI 增强

## 文件清单

### 新建文件：
- `backend/server.py` (新增 SSE 端点)
- `client/src/components/chat/StreamingMessage.jsx` (新建)
- `STREAMING_TEST.md` (新建)
- `QUICKSTART_STREAMING.md` (本文件)

### 修改文件：
- `client/src/utils/api.js` (新增流式 API)
- `client/src/components/chat/MessageList.jsx` (支持流式消息)
- `client/src/pages/ProjectPage.jsx` (集成流式逻辑)
- `client/src/components/preview/PreviewPanel.jsx` (传递回调)
- `client/src/components/preview/WebContainerPreview.jsx` (步骤回调)
- `client/src/utils/storage.js` (数据迁移)

## 支持

如有问题，请查看：
- `PLAN.md` - 项目总体规划
- `STREAMING_TEST.md` - 详细测试指南
- GitHub Issues

---

最后更新：2025-12-16

