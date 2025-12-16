# Vibecoding 平台 MVP - 项目计划

本计划概述了将 `gpt-engineer` 命令行工具 (CLI) 转型为基于 Web 的 "Vibecoding" 平台（最小可行性产品 MVP）的步骤。

## 最近更新 📅

**2025-12-16** - Phase 8 流式生成功能完成
- ✅ 实现后端 SSE 流式推送（/generate-stream、/improve-stream）
- ✅ 实现前端 SSE 客户端（实时接收进度）
- ✅ 创建 StreamingMessage 组件（步骤可视化）
- ✅ 对话框集成流式进度显示
- ✅ WebContainer 环境准备步骤回调
- ✅ 数据持久化支持（steps 字段 + 向后兼容）
- ✅ 遵循设计规范（lucide-react 图标系统）
- 📄 测试文档：`STREAMING_TEST.md`

**2025-12-12** - Phase 6F 质量提升计划
- 📊 完成 Vibecoding vs Lovable 对比分析
- 📝 识别五大核心差距（设计系统、字体、组件、动画、布局）
- 📋 制定三阶段优化方案（模板升级、Preprompt 强化、设计系统包）
- 🎯 目标：视觉质量提升 166%，接近 Lovable 水平
- 📄 详细文档：`OPTIMIZATION_PLAN.md`

**2025-12-11** - Phase 7 WebContainers 架构设计
- 🔄 从 Sandpack 迁移到 WebContainers
- ✅ 支持完整的 React + TypeScript + Tailwind 技术栈
- 📱 混合预览模式（桌面开发 + 移动分享）
- 📄 详细文档：`PHASE7A_CONTEXT.md`

**2025-12-10** - Phase 6 多页应用完成
- ✅ 多页应用架构（Landing + Project）
- ✅ 对话式交互（持续优化）
- ✅ Sandbox/Code 切换
- ✅ 对话历史存储

## 目标
创建一个 Web 界面，用户可以在其中输入自然语言提示词 (Prompt)，并在浏览器中即时看到生成的应用程序的运行预览，无需手动处理文件或在本地执行。

## 架构

### 当前架构 (Phase 1-6)
- **后端**: Python (FastAPI)。封装 `gpt-engineer` 的核心逻辑，在内存中生成代码并以 JSON 格式返回。
- **前端**: React (Vite)。使用 `sandpack-react` 在浏览器中安全地执行和预览生成的代码。
- **限制**: Sandpack 不支持 Tailwind CSS 构建流程,限制了现代前端技术栈的使用。

### 新架构 (Phase 7+) - 混合预览模式
- **后端**: 
  - FastAPI 服务器 (代码生成)
  - 构建服务 (npm run build)
  - 静态文件托管 (/previews/)
- **前端**:
  - **桌面端开发**: StackBlitz WebContainers (完整的 Node.js + Vite + Tailwind)
  - **移动端/分享**: 静态托管预览 (dist 构建产物)
  - **降级方案**: Sandpack (简单 HTML 应用)
- **优势**: 
  - ✅ 支持完整的现代前端技术栈 (React + TypeScript + Tailwind + shadcn/ui)
  - ✅ 桌面端获得完整开发体验 (HMR, 实时预览, 代码编辑)
  - ✅ 移动端通过静态链接完美访问 (100% 兼容性)
  - ✅ 分享链接永久可用,无需实时服务器

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

#### 6F：生成代码质量提升 (Code Quality Enhancement) 🚧 当前重点
**目标**: 通过对比 Lovable 输出，系统性提升 AI 生成代码的视觉质量和设计层次。

**背景分析（2025-12-12）**:
通过对比 Vibecoding 平台生成的 Landing Page 和 Lovable 生成的页面，发现五大核心差距：

1. **设计系统差距** ⭐⭐⭐⭐⭐ (影响最大)
   - ❌ 缺少完整的 CSS 变量系统（颜色、渐变、阴影、字体）
   - ❌ 使用硬编码颜色而非语义化设计令牌
   - ✅ Lovable 有完整的设计系统（20+ CSS 变量）

2. **字体系统差距** ⭐⭐⭐⭐⭐
   - ❌ 只使用系统默认字体
   - ❌ 没有标题/正文的字体层次
   - ✅ Lovable 使用 `Playfair Display` (标题) + `Inter` (正文)

3. **组件细节差距** ⭐⭐⭐⭐
   - ❌ 组件较简单，缺少视觉层次
   - ❌ 缺少 Badge、Stats、多层动画等细节
   - ✅ Lovable 组件丰富，hover 效果复杂

4. **动画质量差距** ⭐⭐⭐⭐
   - ❌ 只有基础动画（scale, opacity）
   - ❌ 动画时长较短，缺少自定义 keyframes
   - ✅ Lovable 有 float、pulse-glow 等自定义动画

5. **布局和间距差距** ⭐⭐⭐
   - ❌ 间距较小（py-20, p-6）
   - ❌ 视觉密度过高，缺少呼吸感
   - ✅ Lovable 间距更大（py-24, p-8），布局更舒适

**优化方案（已规划）**:
详细方案见 `OPTIMIZATION_PLAN.md`，包含：
- 阶段一：设计系统优化（CSS 变量、字体、颜色）
- 阶段二：组件升级（按钮变体、Hero 增强、Features 优化）
- 阶段三：内容和文案优化
- 阶段四：布局和间距优化
- 阶段五：微交互和细节打磨

**实施策略**:

**方案A: 升级模板系统** (推荐 ⭐⭐⭐⭐⭐)
```
目标: 将优化成果固化到模板中
位置: backend/templates/react-ts-shadcn/

实施步骤:
1. 升级模板的 index.css
   - 添加 Google Fonts 导入
   - 完整的 CSS 变量系统
   - 自定义 utility classes

2. 升级模板的 tailwind.config.js
   - 字体配置 (fontFamily)
   - 自定义动画 (keyframes, animation)
   - 扩展颜色系统

3. 升级 UI 组件
   - button.tsx: 添加 hero/heroOutline 变体
   - card.tsx: 增强 hover 效果
   - 其他组件: 统一视觉风格

4. 创建组件示例
   - templates/react-ts-shadcn/examples/
   - HeroSection.example.tsx
   - FeaturesSection.example.tsx
   - 供 AI 参考的高质量代码

优势:
✅ 一次修改，所有生成受益
✅ 确保一致性和质量
✅ 降低 AI 生成难度
✅ 可持续维护
```

**方案B: 强化 Preprompt** (补充 ⭐⭐⭐⭐)
```
目标: 通过更详细的 preprompt 引导 AI
位置: backend/preprompts_custom/landing_page

增强内容:
1. 设计系统规范
   - 必须使用 CSS 变量
   - 字体层次要求
   - 间距标准（py-24, p-8）

2. 组件细节要求
   - Hero 必须包含: Badge + Stats + 多层动画
   - Features 必须包含: 6个卡片 + group hover
   - 按钮使用 hero 变体

3. 视觉标准
   - 动画时长: 6-10s 无限循环
   - 圆角: rounded-2xl
   - 阴影: shadow-lg + hover 增强

4. 提供参考代码片段
   - 直接在 preprompt 中包含示例
```

**方案C: 创建设计系统包** (长期 ⭐⭐⭐)
```
目标: 独立的设计系统 npm 包
名称: @vibecoding/design-system

包含:
- 完整的 Tailwind 配置
- CSS 变量主题
- UI 组件库
- 动画效果库

优势:
✅ 可独立维护和版本控制
✅ 可在其他项目中复用
✅ 易于分享和协作

劣势:
⚠️ 增加复杂度
⚠️ 需要额外维护
```

**实施计划**:
```
Week 1: 方案A - 升级模板系统
  Day 1-2: 升级 index.css + tailwind.config.js
  Day 3-4: 升级所有 UI 组件
  Day 5: 创建组件示例和文档

Week 2: 方案B - 强化 Preprompt
  Day 1-2: 重写 landing_page preprompt
  Day 3: 重写 dashboard preprompt
  Day 4: 重写 modern_web_app preprompt
  Day 5: 测试和优化

Week 3: 验证和迭代
  Day 1-3: 生成 20+ 测试案例
  Day 4-5: 根据结果调整和优化
```

**预期提升**:
| 维度 | 当前 | 目标 | 提升 |
|-----|------|------|-----|
| 视觉高级感 | 3/10 | 8/10 | +166% |
| 动画流畅度 | 5/10 | 9/10 | +80% |
| 设计一致性 | 4/10 | 9/10 | +125% |
| 细节完成度 | 3/10 | 8/10 | +166% |
| 与 Lovable 差距 | 较大 | 接近 | -70% |

**成功指标**:
- ✅ 生成的页面包含完整的设计系统
- ✅ 自动使用双字体组合
- ✅ Hero 区域包含 Badge + Stats + 多层动画
- ✅ Features 至少 6 个卡片 + group hover
- ✅ 间距符合规范（py-24, p-8, rounded-2xl）
- ✅ 按钮使用 hero 变体并带发光效果
- ✅ 整体视觉质量接近 Lovable 水平

**相关文档**:
- 详细分析: `OPTIMIZATION_PLAN.md`
- 对比示例: `competitior-landingpage/mvp/` vs `landing-page-magic/`

**预计时间**: 2-3 周

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

### 第七阶段：混合预览架构 + 质量提升 (Hybrid Preview + Quality) 🚧 进行中
**目标**: 
1. 解决 Sandpack 的 Tailwind CSS 支持问题,采用混合预览方案（技术升级）
2. 系统性提升生成代码的视觉质量和设计层次（质量升级）

**双轨并进策略**:
- **技术轨** (7A-7C): WebContainers + 静态托管 → 解决技术栈限制
- **质量轨** (6F): 设计系统升级 → 提升生成质量

### 第七阶段A：混合预览架构 (Hybrid Preview Architecture) 🚧 当前重点
**目标**: 解决 Sandpack 的 Tailwind CSS 支持问题,采用混合预览方案。

**背景问题**:
- ❌ Sandpack 不支持 Tailwind CSS 构建流程(`@tailwind` directives)
- ❌ 无法运行 PostCSS/Vite 完整构建工具链
- ❌ 外部 CDN 支持受限,导致样式无法生效
- ⚠️ 限制了 React + TypeScript + shadcn/ui 技术栈的使用

**解决方案: 混合预览模式**

#### 7A: WebContainers 桌面端开发 🚧 当前重点
**目标**: 使用 StackBlitz WebContainers 在桌面浏览器中提供完整的开发环境。

**技术选型**:
- **WebContainers**: 浏览器内运行真实 Node.js 和 npm
- **完整支持**: Vite + Tailwind + PostCSS + 所有 npm 包
- **实时预览**: HMR 热重载,完整的开发体验

**架构设计**:
```
用户输入 Prompt (桌面 Chrome/Edge/Firefox)
    ↓
后端生成代码 (React + TypeScript + Tailwind)
    ↓
前端: WebContainer.boot()
    ↓
挂载文件系统 + npm install
    ↓
启动 Vite dev server (npm run dev)
    ↓
实时预览 (完整的样式、HMR、构建流程)
    ↓
用户可以编辑代码并即时看到效果
```

**实施步骤**:
- [ ] **安装依赖**:
    ```bash
    npm install @webcontainer/api
    ```
- [ ] **配置 HTTP 头部** (必需):
    ```javascript
    // vite.config.js
    server: {
      headers: {
        'Cross-Origin-Opener-Policy': 'same-origin',
        'Cross-Origin-Embedder-Policy': 'require-corp'
      }
    }
    ```
- [ ] **创建 WebContainerPreview 组件**:
    - 检测浏览器支持 (`SharedArrayBuffer`)
    - 启动 WebContainer
    - 挂载文件系统
    - 运行 npm install + npm run dev
    - 在 iframe 中显示预览
- [ ] **添加加载状态**:
    - "正在启动容器..." (2-5秒)
    - "安装依赖..." (5-10秒)
    - "启动开发服务器..." (2-3秒)
    - 总计: 10-18秒首次加载
- [ ] **资源管理**:
    - 限制同时活跃的容器数量(1个)
    - 切换应用时销毁旧容器
    - 内存优化和清理
- [ ] **错误处理**:
    - 检测浏览器兼容性
    - 捕获构建错误并显示
    - 提供降级方案

**浏览器兼容性**:
```javascript
// 支持的浏览器
✅ Chrome/Edge >= 89 (2021年3月)
✅ Firefox >= 91 (2021年8月)
✅ Safari >= 15.2 (2021年12月)

// 不支持
❌ 所有移动浏览器 (iOS Safari, Chrome Mobile)
❌ 旧版桌面浏览器
```

#### 7B: 静态托管分享链接 🚧 当前重点
**目标**: 为移动端和分享场景生成静态预览链接。

**架构设计**:
```
用户在桌面完成开发
    ↓
点击"生成分享链接"按钮
    ↓
后端/WebContainer 执行: npm run build
    ↓
获取 dist/ 构建产物 (HTML + CSS + JS)
    ↓
上传到静态文件托管
    ↓
返回公开 URL: https://preview.yoursite.com/abc123
    ↓
任何设备都能访问 (移动端、PC、分享)
```

**实施方案对比**:

| 方案 | 成本 | 速度 | 稳定性 | 推荐度 |
|------|------|------|--------|--------|
| 自建静态托管 | 服务器成本 | 快 | 中 | ⭐⭐⭐⭐⭐ (MVP) |
| 阿里云 OSS | ¥0.6/千预览 | 快(CDN) | 高 | ⭐⭐⭐⭐ (扩展) |
| Vercel API | 免费100次/月 | 慢(1-2分钟) | 最高 | ⭐⭐⭐ (备选) |

**实施步骤 - 方案1: 自建托管** (推荐用于 MVP):

- [ ] **后端 API 端点**:
    ```python
    # backend/server.py
    @app.post("/api/build-preview")
    async def build_preview(files: Dict[str, str]):
        # 1. 生成唯一 ID
        preview_id = str(uuid.uuid4())[:8]
        
        # 2. 创建临时目录并写入文件
        temp_dir = f"/tmp/builds/{preview_id}"
        for filename, content in files.items():
            write_file(f"{temp_dir}/{filename}", content)
        
        # 3. 执行构建
        subprocess.run(["npm", "install"], cwd=temp_dir)
        subprocess.run(["npm", "run", "build"], cwd=temp_dir)
        
        # 4. 移动 dist 到静态服务目录
        shutil.move(f"{temp_dir}/dist", f"/var/www/previews/{preview_id}")
        
        # 5. 返回预览 URL
        return {
            "preview_url": f"https://yourdomain.com/previews/{preview_id}",
            "preview_id": preview_id,
            "expires_at": datetime.now() + timedelta(days=7)
        }
    ```

- [ ] **Nginx 配置**:
    ```nginx
    # 托管静态预览
    location /previews/ {
        alias /var/www/previews/;
        try_files $uri $uri/ /index.html;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }
    ```

- [ ] **前端集成**:
    ```javascript
    // 添加"生成分享链接"按钮
    <Button onClick={handleGeneratePreview}>
      🔗 生成分享链接
    </Button>
    
    const handleGeneratePreview = async () => {
      setBuilding(true)
      const response = await fetch('/api/build-preview', {
        method: 'POST',
        body: JSON.stringify({ files: currentFiles })
      })
      const { preview_url } = await response.json()
      
      // 显示链接并复制到剪贴板
      navigator.clipboard.writeText(preview_url)
      toast.success('分享链接已复制!')
    }
    ```

- [ ] **构建队列** (可选优化):
    - 使用 Celery/RQ 异步处理构建
    - 避免阻塞用户操作
    - 支持进度查询

- [ ] **定期清理**:
    ```python
    # 定时任务: 每天凌晨3点清理7天前的预览
    @celery.beat_schedule(crontab(hour=3))
    def cleanup_old_previews():
        cutoff = datetime.now() - timedelta(days=7)
        for preview_id in os.listdir('/var/www/previews'):
            preview_path = f'/var/www/previews/{preview_id}'
            if os.path.getctime(preview_path) < cutoff.timestamp():
                shutil.rmtree(preview_path)
    ```

**优化建议**:
- 缓存 node_modules (加速构建)
- 使用构建缓存 (Vite build cache)
- 压缩输出文件 (gzip)
- 添加 CDN (如需全球访问)

#### 7C: 智能预览模式切换 📅 规划中
**目标**: 根据用户环境和项目类型自动选择最佳预览方式。

**切换逻辑**:
```javascript
function selectPreviewMode(files, userAgent) {
  // 1. 检测项目类型
  const isSimpleHTML = !files['package.json']
  const isReactApp = files['package.json']?.includes('react')
  
  // 2. 检测浏览器能力
  const supportsWebContainers = 
    typeof SharedArrayBuffer !== 'undefined' &&
    !isMobile(userAgent)
  
  // 3. 智能选择
  if (isSimpleHTML) {
    return 'sandpack'  // 简单 HTML 用 Sandpack
  }
  
  if (isReactApp && supportsWebContainers) {
    return 'webcontainer'  // 桌面端 React 用 WebContainer
  }
  
  if (isReactApp && !supportsWebContainers) {
    return 'build-preview'  // 移动端用静态预览
  }
  
  return 'sandpack'  // 默认降级
}
```

**用户流程**:
```
桌面用户 (Chrome)
    ↓
生成 React 应用
    ↓
WebContainer 实时预览 ✅
    ↓
点击"生成分享链接"
    ↓
获得静态 URL,分享给朋友

---

移动用户 (iPhone Safari)
    ↓
打开分享链接
    ↓
直接访问静态页面 ✅
    ↓
完美显示,无兼容性问题
```

**实施步骤**:
- [ ] 创建 `PreviewModeSelector` 组件
- [ ] 实现浏览器检测逻辑
- [ ] 添加降级提示 UI
- [ ] 测试各种场景

#### 技术债务和风险

**WebContainers 风险**:
- ⚠️ 首次加载较慢 (10-18秒)
- ⚠️ 内存消耗较大 (~200MB/实例)
- ⚠️ 浏览器兼容性限制 (约20-30%用户)
- ⚠️ 依赖第三方服务 (StackBlitz)

**缓解措施**:
- ✅ 混合模式 (桌面开发 + 移动分享)
- ✅ 详细的加载状态提示
- ✅ 资源管理和清理
- ✅ 降级方案 (Sandpack)

**静态托管风险**:
- ⚠️ 存储空间管理
- ⚠️ 构建时间 (30-60秒)
- ⚠️ 服务器资源消耗

**缓解措施**:
- ✅ 定期清理过期预览
- ✅ 异步构建队列
- ✅ 构建缓存优化

#### 预期收益

**功能完整性**:
- ✅ 支持完整的 React + TypeScript + Tailwind 技术栈
- ✅ 支持 shadcn/ui + framer-motion 等现代库
- ✅ 支持完整的构建流程和 HMR

**用户体验**:
- ✅ 桌面端: 接近 Lovable/Bolt.new 的体验
- ✅ 移动端: 完美的分享和预览体验
- ✅ 跨平台: 任何设备都能访问静态链接

**可扩展性**:
- ✅ 为后续功能打下基础 (代码编辑、协作等)
- ✅ 支持任何 npm 包和构建工具
- ✅ 易于集成新的预览方式

**里程碑**:
- **Phase 7A 完成**: WebContainers 桌面预览可用
- **Phase 7B 完成**: 静态分享链接可用
- **Phase 7C 完成**: 智能切换逻辑完善

**预计时间**: 2-3 周

### 第八阶段：流式生成与视觉迭代 (Streaming & Vision) ✅ 已完成 (Streaming)
- [x] **流式生成 (Streaming)**:
    - ✅ 后端 SSE 端点（/generate-stream、/improve-stream）
    - ✅ 前端 SSE 客户端（generateAppStreaming、improveAppStreaming）
    - ✅ StreamingMessage 组件（步骤可视化）
    - ✅ 对话框集成（实时进度显示）
    - ✅ WebContainer 步骤回调（环境准备进度）
    - ✅ 数据持久化支持（steps 字段）
    - ✅ 使用 lucide-react 图标系统
    - ✅ 支持 chunk 粒度推送（按文件推送，不使用打字机效果）
- [ ] **视觉迭代 (Vision)** 📅 规划中:
    - 支持截图上传，让 AI "看着" 修改代码。

### 第九阶段：中国化与本地化 (Localization) 📅 规划中
- [ ] **模型多样化**: 集成 DeepSeek-Coder 或 Qwen 等国产模型。
- [ ] **网络优化**: 替换 npm 源为淘宝镜像，优化国内访问速度。
- [ ] **多语言支持**: 中英文切换。

---

## 附录：相关文档 📚

### 核心规划文档
- **PLAN.md** (本文档) - 项目总体规划和路线图
- **OPTIMIZATION_PLAN.md** - Landing Page 质量优化详细方案
- **PHASE7A_CONTEXT.md** - WebContainers 架构设计和实施细节
- **PHASE7_TEMPLATE_SYSTEM.md** - 模板系统设计文档

### 功能文档
- **PHASE5A_PERSISTENCE.md** - 应用代码持久化实现
- **PHASE5B_HISTORY.md** - 多应用历史管理实现
- **PHASE6_MULTIPAGE.md** - 多页应用架构实现

### 问题修复
- **BUGFIX.md** - Bug 修复记录
- **BUGFIX2.md** - 更多 Bug 修复
- **FEATURE_IMPROVE.md** - 功能改进建议

### 技术升级
- **UPGRADE_REACT.md** - React 升级指南
- **LOVABLE_UPGRADE.md** - Lovable 风格 UI 升级

### 对比和参考
- **competitior-landingpage/** - 竞品分析
  - `mvp/` - Vibecoding 生成的 Landing Page 示例
  - `mvp-1/` - 早期版本
  - `landing-page-magic/` - Lovable 生成的高质量参考

### 快速导航

**当前重点** (Phase 7):
1. 🔧 WebContainers 集成 → 查看 `PHASE7A_CONTEXT.md`
2. 🎨 质量提升 → 查看 `OPTIMIZATION_PLAN.md`

**如何开始优化**:
1. 阅读 `OPTIMIZATION_PLAN.md` 了解详细对比和方案
2. 从阶段一开始（设计系统优化）
3. 预计 1 小时可见显著提升

**如何理解架构**:
1. 阅读本文档了解整体路线图
2. 阅读 `PHASE7A_CONTEXT.md` 了解 WebContainers
3. 查看 `backend/templates/` 了解模板系统

---

## 项目状态总览 📊

### 已完成 ✅
- Phase 1: 后端服务 (FastAPI + gpt-engineer)
- Phase 2: 前端客户端 (React + Sandpack)
- Phase 3: 集成与测试
- Phase 4: 现代化技术栈 (Tailwind CDN)
- Phase 5A: 应用代码持久化
- Phase 5B: 多应用历史管理
- Phase 6A-6D: 多页应用 + 对话式交互
- Phase 8: 流式生成 (SSE + 实时进度显示)

### 进行中 🚧
- **Phase 6F: 代码质量提升** (当前重点)
  - 已完成对比分析
  - 已制定优化方案
  - 待实施模板升级
- **Phase 7A: WebContainers 集成** (技术升级)
  - 架构设计完成
  - 待实施集成
- Phase 6E: Lovable 风格 UI (部分完成)

### 规划中 📅
- Phase 5C: Supabase 云端存储
- Phase 7B: 静态托管分享链接
- Phase 7C: 智能预览模式切换
- Phase 8: 流式生成与视觉迭代
- Phase 9: 中国化与本地化

### 关键指标

**代码生成能力**:
- ✅ 支持 HTML + Tailwind CDN
- 🚧 支持 React + TypeScript (WebContainers)
- ✅ 支持 shadcn/ui 组件
- 🚧 视觉质量：当前 3/10，目标 8/10

**用户体验**:
- ✅ 对话式交互
- ✅ 历史记录管理
- ✅ 自动保存/恢复
- 🚧 实时预览 (WebContainers)
- 📅 分享链接 (计划中)

**技术栈**:
- ✅ Python FastAPI 后端
- ✅ React + Vite 前端
- ✅ Sandpack 预览（简单应用）
- 🚧 WebContainers 预览（复杂应用）
- 📅 Supabase 存储 (计划中)

---

最后更新：2025-12-12
