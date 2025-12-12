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

### 第六阶段：多页应用与对话式交互 (Multi-Page & Chat UI) 🚧 进行中
**目标**: 升级为多页应用架构，采用对话式交互，参考 Lovable 的 UI/UX 设计。

#### 6A：多页应用架构 ✅ 已完成
**目标**: 拆分为首页和项目页，优化用户流程。

- [x] **路由系统**:
    - 安装 `react-router-dom`。
    - 配置路由：首页 (`/`) + 项目页 (`/project/:id`)。
    - 实现页面跳转逻辑。
- [x] **首页（Landing Page）**:
    - 简洁的大输入框 + 生成按钮。
    - 示例提示词（可点击快速填充）。
    - 历史项目入口。
- [x] **项目页（Project Page）**:
    - 左右分割布局（40% 对话区 + 60% 预览区）。
    - 顶部导航栏（返回、项目名称、Sandbox/Code 切换、保存状态）。
    - 基础布局完成。

#### 6B：对话式交互 ✅ 已完成
**目标**: 用户通过持续对话来生成和优化应用。

- [x] **对话区（Chat Panel）**:
    - 左侧 40% 宽度，固定布局。
    - 消息列表（用户消息 + AI 消息）。
    - 底部输入框（固定位置）。
    - 历史记录按钮（对话区顶部）。
- [x] **消息显示**:
    - 用户消息：右对齐，渐变背景。
    - AI 消息：左对齐，浅灰背景。
    - 时间戳显示（相对时间：刚刚/N秒前/N分钟前）。
    - 加载动画（三点跳动效果）。
- [x] **智能优化判断**:
    - 分析用户消息关键词（"修改"、"添加"等）。
    - 小改动：调用 `/improve` 端点（使用 `improve_fn`）。
    - 大改动：调用 `/generate` 端点（重新生成）。
    - 自动构建上下文 prompt。

#### 6C：预览/代码切换 ✅ 已完成
**目标**: 右侧统一预览区，支持 Sandbox 和 Code 视图切换。

- [x] **标签切换**:
    - [👁️ Sandbox] [</> Code] 按钮（位于 header 右侧）。
    - 默认显示 Sandbox 预览。
    - 点击 Code 按钮切换到代码编辑器。
- [x] **Sandbox 预览**:
    - 自适应容器高度（`height: calc(100vh - 130px)`）。
    - iframe 填满容器（100% 宽高）。
    - 充分利用屏幕空间（适合游戏、复杂应用）。
- [x] **Code 编辑器**:
    - 复用 Sandpack 的代码编辑功能。
    - 60% 编辑器 + 40% 预览（并排显示）。
    - 语法高亮和行号。

#### 6D：数据结构升级 ✅ 已完成
**目标**: 支持对话历史存储和管理。

- [x] **新增 messages 字段**:
    - 每个应用包含对话历史数组。
    - 消息格式：`{ role, content, timestamp, filesCount }`。
    - 保存到 localStorage（兼容旧数据）。
- [x] **对话历史管理**:
    - 页面加载时恢复对话历史。
    - 新消息自动添加到数组。
    - 自动滚动到最新消息。
- [x] **数据迁移准备**:
    - 数据结构设计考虑 Supabase 迁移。
    - 使用可选字段（向后兼容）。

#### 6E：Lovable 风格 UI 升级 🚧 进行中
**目标**: 采用 shadcn/ui + Lovable 设计系统，提升视觉体验。

**设计规范**:
- 配色：
  - 背景：#F8F8F9（浅灰）
  - 品牌色：#FFB454（橙色）、#FF6A4A（珊瑚红）
  - 文字：#1A1A1A（深灰）
- 视觉语言：
  - 柔和阴影（shadow-sm, shadow-lg）
  - 大圆角（rounded-xl, rounded-2xl）
  - 平滑过渡（transition-all duration-200）
  - 平衡间距（p-4 到 p-6）
- 布局：
  - 左侧边栏：280px 固定宽度
  - 右侧主区域：flex-1 自适应

**实施步骤**:

- [x] **安装依赖**:
    - `lucide-react` - 图标库
    - `class-variance-authority` - 样式变体
    - `clsx` + `tailwind-merge` - 类名工具
    - `tailwindcss-animate` - 动画插件
- [x] **配置 Tailwind**:
    - 创建 `tailwind.config.js`
    - 添加 CSS 变量和主题色
    - 配置 Lovable 品牌色
- [ ] **配置 path alias**:
    - 更新 `vite.config.js` 添加 `@/` 别名
    - 更新 `jsconfig.json` 或 `tsconfig.json`
- [ ] **创建工具函数**:
    - `lib/utils.js` - cn() 函数（合并 Tailwind 类名）
- [ ] **安装 shadcn/ui 组件**:
    - Button（按钮）
    - Input（输入框）
    - Textarea（文本域）
    - Card（卡片）
    - Tabs（标签页）
    - Separator（分隔线）
    - ScrollArea（滚动区域）
- [ ] **重写 LandingPage**:
    - 使用 shadcn Button 和 Textarea
    - Lovable 风格的大标题和副标题
    - 示例卡片使用 Card 组件
    - 橙色品牌色 CTA 按钮
- [ ] **重写 ProjectPage**:
    - 280px 固定左侧边栏
    - 顶部导航栏使用 shadcn Button
    - Lovable 风格的工具栏
- [ ] **重写 ChatPanel**:
    - 使用 Card 组件包裹消息
    - Lovable 风格消息气泡（柔和圆角）
    - ScrollArea 替代原生滚动
- [ ] **重写 PreviewPanel**:
    - 使用 shadcn Tabs 组件
    - 白色画布 + 柔和阴影
    - Lovable 风格的预览窗口
- [ ] **统一应用主题**:
    - 所有组件使用 Lovable 配色
    - 统一圆角、间距、阴影
    - 添加平滑过渡效果
- [ ] **测试和优化**:
    - 端到端测试新 UI
    - 响应式适配
    - 性能优化
    - 细节打磨

**已完成工作（Commit 7c9cfa0）**:
- ✅ 21 个文件创建（pages, components, utils, styles）
- ✅ 多页应用架构（React Router）
- ✅ 对话式交互（持续对话优化）
- ✅ 智能优化判断（improve vs generate）
- ✅ Sandbox/Code 切换（header 中的按钮）
- ✅ 对话历史存储（localStorage + messages 字段）
- ✅ Bug 修复（宽度溢出、API 参数、错误处理）

**待完成工作（Phase 6E）**:
- 📋 shadcn/ui 集成（10个组件）
- 📋 Lovable 风格重写（4个主要页面/组件）
- 📋 配色方案应用（#F8F8F9, #FFB454, #FF6A4A）
- 📋 视觉细节打磨（阴影、圆角、过渡）

**预计时间**: 3-4 小时

#### 实施步骤（预计 10-12 小时）

**第1步：路由基础**（30分钟）
- 安装 `react-router-dom`
- 配置路由和基本页面框架
- 测试页面跳转

**第2步：首页实现**（1小时）
- 设计 Landing Page 样式
- 实现输入框 + 生成按钮
- 集成现有生成逻辑 + 跳转

**第3步：项目页布局**（1小时）
- 左右分割布局（40/60）
- 顶部导航栏
- 响应式适配

**第4步：对话区实现**（2小时）
- ChatPanel 组件
- MessageList + MessageItem
- ChatInput 组件
- 消息样式和动画

**第5步：预览区重构**（1小时）
- Sandbox/Code 标签切换
- 复用现有 Sandpack
- 自适应高度

**第6步：智能优化逻辑**（1小时）
- promptAnalyzer 工具函数
- 集成 improve_fn
- 测试小改动/大改动

**第7步：数据持久化**（1小时）
- 升级数据结构（添加 messages）
- 保存对话历史
- 兼容旧数据

**第8步：历史记录调整**（30分钟）
- 移动历史记录按钮到对话区
- 项目列表显示优化

**第9步：测试优化**（2小时）
- 端到端测试
- Bug 修复
- 性能优化

**第10步：文档更新**（1小时）
- 更新 README
- 编写使用指南
- 更新 PLAN

#### 技术细节

**组件结构**:
```
client/src/
├── main.jsx                    # 添加路由配置
├── App.jsx                     # 根组件（仅路由）
├── pages/
│   ├── LandingPage.jsx        # 首页
│   └── ProjectPage.jsx        # 项目页
├── components/
│   ├── ChatPanel.jsx          # 对话区
│   ├── MessageList.jsx        # 消息列表
│   ├── MessageItem.jsx        # 单条消息
│   ├── ChatInput.jsx          # 输入框
│   ├── PreviewPanel.jsx       # 预览/代码区
│   └── TabBar.jsx             # 标签切换
└── utils/
    ├── promptAnalyzer.js      # 智能判断工具
    └── api.js                 # API 调用封装
```

**数据结构**:
```javascript
{
  id: '1733900400000',
  name: '应用名称',
  files: { '/index.html': '...' },
  prompt: '初始 prompt',
  messages: [  // 新增
    { role: 'user', content: '创建应用', timestamp: '...' },
    { role: 'assistant', content: '✅ 已生成', timestamp: '...' }
  ],
  timestamp: '2025-12-11T...'
}
```

**智能判断逻辑**:
- 关键词：修改/改/换 → `improve_fn`
- 关键词：添加/增加/新增 → `gen_code`
- 默认：`improve_fn`（更快）

#### 与后续阶段的关系

**Phase 7（流式生成）时**:
- 在消息列表中添加打字机效果
- 后端改为 WebSocket/SSE
- **布局和交互不变**

**Phase 5C（Supabase）时**:
- 替换 localStorage 为 Supabase API
- 对话历史自动云端同步
- **前端逻辑几乎不变**

### 第七阶段：流式生成与视觉迭代 (Streaming & Vision) 📅 规划中
- [ ] **流式生成 (Streaming)**:
    - 改造后端为 WebSocket 或 SSE。
    - 前端实现打字机效果，代码实时上屏。
- [ ] **视觉迭代 (Vision)**:
    - 支持截图上传，让 AI "看着" 修改代码。

### 第八阶段：中国化与本地化 (Localization) 📅 规划中
- [ ] **模型多样化**: 集成 DeepSeek-Coder 或 Qwen 等国产模型。
- [ ] **网络优化**: 替换 npm 源为淘宝镜像，优化国内访问速度。
- [ ] **多语言支持**: 中英文切换。
