# Vibecoding 平台 MVP - 项目计划

本计划概述了将 `gpt-engineer` 命令行工具 (CLI) 转型为基于 Web 的 "Vibecoding" 平台（最小可行性产品 MVP）的步骤。

## 目标
创建一个 Web 界面，用户可以在其中输入自然语言提示词 (Prompt)，并在浏览器中即时看到生成的应用程序的运行预览，无需手动处理文件或在本地执行。

## 架构
- **后端**: Python (FastAPI)。封装 `gpt-engineer` 的核心逻辑，在内存中生成代码并以 JSON 格式返回。
- **前端**: React (Vite)。使用 `sandpack-react` 在浏览器中安全地执行和预览生成的代码。

## 路线图

### 第一阶段：后端服务 (`server.py`) ✅ 已完成
**目标**: 通过 REST API 暴露 `gpt-engineer` 的代码生成能力。

- [x] **依赖项**: 安装 `fastapi`, `uvicorn`。
- [x] **核心逻辑**:
    - 在 `projects/vibecodingplatform-mvp/backend` 中创建 `server.py`。
    - 从 `gpt-engineer` 初始化 `AI` 和 `PrepromptsHolder`。
    - 实现 `/generate` POST 端点。
    - 使用 `TemporaryDirectory` 绕过 `DiskMemory` 的磁盘持久化要求。
    - 直接以 JSON 格式返回 `FilesDict`。
- [x] **CORS**: 启用 CORS 以允许前端调用 API。
- [x] **代码改进**: 实现 `/improve` 端点，支持基于上下文的迭代修改。

### 第二阶段：前端客户端 (`client/`) ✅ 已完成
**目标**: 构建用于交互和预览的可视化界面。

- [x] **设置**: 在 `projects/vibecodingplatform-mvp/client` 中使用 Vite 初始化一个新的 React 项目。
- [x] **UI 组件**:
    - 用户提示词输入区域。
    - "生成" 按钮。
    - 加载状态指示器。
    - 迭代改进输入框。
- [x] **Sandpack 集成**:
    - 安装 `@codesandbox/sandpack-react`。
    - 配置 Sandpack 组件以接收动态文件字典。
    - 智能处理文件格式（自动补全 index.html）。
- [x] **API 集成**:
    - 从 `http://localhost:8000/generate` 获取数据。
    - 实现提示词增强（Prompt Engineering）以引导 Web 代码生成。

### 第三阶段：集成与测试 ✅ 已完成
- [x] **端到端测试**:
    - 启动后端: `uvicorn server:app --reload`
    - 启动前端: `npm run dev`
    - 测试流程: 输入 "贪吃蛇游戏" -> 等待 -> 验证游戏在预览中运行。
    - 测试流程: 输入 "修复 Game Over Bug" -> 验证代码更新。

### 第四阶段：现代化技术栈升级 (Modern Stack) ✅ 已完成
**目标**: 从生成简单的 HTML/JS 升级为生成现代化、美观的 Tailwind CSS 应用。

- [x] **采用 HTML + Tailwind CDN 方案**:
    - 前端 Sandpack 使用 `template="static"`（最稳定）。
    - 通过 CDN 引入 Tailwind CSS（`https://cdn.tailwindcss.com`）。
    - 避免了 Sandpack 不支持 Tailwind 编译的问题。
- [x] **Prompt 工程优化**:
    - 详细的设计要求：渐变背景、卡片阴影、圆角、Hover 效果等。
    - localStorage 使用规范：正确的初始化、保存、加载逻辑。
    - 明确禁止生成配置文件（package.json、tailwind.config.js 等）。
- [x] **智能文件处理**:
    - 自动过滤配置文件和入口文件。
    - 验证 Tailwind CDN 是否存在。
    - 智能重命名为 index.html。
- [x] **测试通过**:
    - ✅ 数据仪表盘（渐变背景 + 统计卡片）
    - ✅ 番茄钟计时器（倒计时 + 交互）
    - ✅ 待办事项（分类 + localStorage）
    - ✅ 个人财务追踪（复杂数据 + 持久化）

### 第五阶段：全栈与数据能力 (Fullstack & Data) 🚧 进行中

#### 5A：应用代码持久化 ✅ 已完成
**目标**: 解决刷新浏览器后应用消失的问题。

- [x] **自动保存**:
    - 生成/改进应用后自动保存到 localStorage。
    - 保存内容：files、prompt、timestamp。
- [x] **自动恢复**:
    - 页面加载时检查 localStorage。
    - 自动恢复上次生成的应用和 prompt。
- [x] **清除功能**:
    - 新增"清除应用"按钮（红色垃圾桶图标）。
    - 清除所有状态并回到初始界面。
- [x] **状态提示**:
    - 显示"💾 已保存 + 时间戳"。
    - 实时反馈保存状态。
- [x] **测试通过**:
    - ✅ 刷新后应用正确恢复
    - ✅ 清除功能正常工作
    - ✅ 改进后自动更新保存

#### 5B：多应用历史管理 ✅ 已完成
**目标**: 保存多个应用，支持历史记录和切换。

- [x] **历史记录列表**:
    - 保存最近 10 个生成的应用。
    - 侧边栏显示应用列表（名称、时间）。
    - 按时间倒序排列（最新的在最上面）。
- [x] **应用切换**:
    - 点击历史记录卡片恢复应用。
    - 支持删除单个历史记录（🗑️ 按钮）。
    - 自动更新当前应用状态。
- [x] **应用命名**:
    - 自动从 prompt 提取应用名称（前20字符）。
    - 支持双击名称进行手动编辑。
    - Enter 键或失焦保存新名称。
- [x] **UI 实现**:
    - 右上角"📚 历史记录 (N)"按钮。
    - 320px 宽度侧边栏，可滚动。
    - 卡片 Hover 效果和点击交互。

#### 5C：Supabase 云端存储 📅 规划中
**目标**: 跨设备同步，支持分享。

- [ ] **BaaS 集成 (Supabase)**:
    - 集成 Supabase JS 客户端。
    - 引导 AI 生成带有数据库 CRUD 逻辑的代码。
    - 实现"留言板"、"Todo List (带存储)"等持久化应用。

### 第六阶段：交互体验优化 (UX & Vibe)
- [ ] **流式生成 (Streaming)**:
    - 改造后端为 WebSocket 或 SSE。
    - 前端实现打字机效果，代码实时上屏。
- [ ] **视觉迭代 (Vision)**:
    - 支持截图上传，让 AI "看着" 修改代码。

### 第七阶段：中国化与本地化 (Localization)
- [ ] **模型多样化**: 集成 DeepSeek-Coder 或 Qwen 等国产模型。
- [ ] **网络优化**: 替换 npm 源为淘宝镜像，优化国内访问速度。
