# 项目上下文 - 用于下一次对话

## 📋 项目概述

**项目名称**: VibeCoding Platform MVP  
**目标**: 构建一个类似 Lovable 的 AI 代码生成平台，能够生成高质量的现代 Web 应用

**工作目录**: `/Users/gaochang/gpt-engineer/projects/vibecodingplatform-mvp/`

## 🎯 当前状态

### ✅ 已完成的工作

1. **Phase 6E: Lovable 风格 UI 升级**
   - 使用 Tailwind CSS + shadcn/ui 重构前端
   - 实现 Lovable 设计系统（橙色主题 #FFB454）
   - 所有页面组件已现代化

2. **Phase 7: 混合模板系统（Solution C）**
   - ✅ 创建 React + TypeScript + shadcn/ui 项目模板
   - ✅ 实现自定义 Preprompts 系统（landing_page, dashboard, modern_web_app）
   - ✅ 后端 Template Manager 和 Preprompt Manager
   - ✅ 前端支持多文件 React 项目预览
   - ✅ **刚刚修复**: 组件导入路径问题（大小写敏感）

### 🔧 最近的关键修复

**问题**: AI 生成的代码使用了错误的导入路径
- ❌ `import { Button } from '@/components/ui/Button'` (大写 - 错误)
- ✅ `import { Button } from '@/components/ui/button'` (小写 - 正确)

**解决方案**: 更新了所有 Preprompts 文件，明确指出组件文件名是小写的：
- `backend/preprompts_custom/modern_web_app`
- `backend/preprompts_custom/landing_page`
- `backend/preprompts_custom/dashboard`

**后端已重启**: 新的 Preprompts 已加载

## 🏗️ 技术架构

### 前端 (Vite + React)
- **路径**: `client/`
- **启动**: `cd client && npm run dev`
- **端口**: http://localhost:5173
- **关键依赖**:
  - React 18
  - Tailwind CSS 3.4.17
  - shadcn/ui (基于 Radix UI)
  - lucide-react (图标)
  - framer-motion (动画)
  - @codesandbox/sandpack-react (代码预览)
  - React Router

### 后端 (FastAPI + Python)
- **路径**: `backend/`
- **启动**: `./run.sh` (在项目根目录)
- **端口**: http://localhost:8000
- **核心模块**:
  - `server.py` - 主 API 服务器
  - `template_manager.py` - 项目模板管理
  - `preprompt_manager.py` - AI Prompt 增强
  - `templates/react-ts-shadcn/` - React 项目模板
  - `preprompts_custom/` - 自定义 AI 指令

### 代码生成流程

```
用户输入 Prompt
    ↓
Frontend: api.js → POST /generate
    ↓
Backend: server.py
    ↓
preprompt_manager.py (检测应用类型 + 加载对应 Preprompt)
    ↓
GPT Engineer (生成代码)
    ↓
template_manager.py (合并模板 + AI 代码)
    ↓
返回完整项目文件 (25 个文件)
    ↓
Frontend: PreviewPanel.jsx (Sandpack 预览)
```

## 🧪 待测试功能

### 当前需要测试
1. **Landing Page 生成** (刚修复，需要验证)
   - Prompt: `"create a landingpage"`
   - 预期: 看到完整的 Hero + Features + CTA + Footer
   - 检查: 组件导入路径是否正确

2. **Dashboard 生成**
   - Prompt: `"create a dashboard"`
   - 预期: 数据统计卡片 + 图表 + 侧边栏

3. **其他应用类型**
   - E-commerce
   - Portfolio
   - Blog

## 📁 关键文件清单

### 前端
```
client/
├── src/
│   ├── pages/
│   │   ├── LandingPage.jsx     # 主页（Lovable 风格）
│   │   └── ProjectPage.jsx     # 项目编辑页
│   ├── components/
│   │   ├── ui/                 # shadcn/ui 组件（小写文件名！）
│   │   │   ├── button.jsx
│   │   │   ├── card.jsx
│   │   │   ├── input.jsx
│   │   │   └── ...
│   │   ├── chat/              # 聊天面板
│   │   └── preview/           # Sandpack 预览
│   │       └── PreviewPanel.jsx  # 核心：检测项目类型，渲染 Sandpack
│   ├── utils/
│   │   └── api.js             # API 调用（生成应用的入口）
│   └── lib/
│       └── utils.js           # cn() 工具函数
└── vite.config.js             # 配置了 @/ 路径别名
```

### 后端
```
backend/
├── server.py                  # FastAPI 主服务
├── template_manager.py        # 模板加载和合并
├── preprompt_manager.py       # Prompt 增强
├── templates/
│   └── react-ts-shadcn/      # React 项目模板（25 个基础文件）
│       ├── package.json
│       ├── vite.config.ts
│       ├── tailwind.config.ts
│       └── src/
│           ├── components/ui/ # shadcn/ui 组件（小写！）
│           ├── pages/Index.tsx
│           └── ...
└── preprompts_custom/
    ├── modern_web_app         # 通用现代 Web 应用
    ├── landing_page          # Landing Page 专用
    └── dashboard             # Dashboard 专用
```

## 🐛 已知问题和注意事项

### 1. 组件导入路径（已修复，待验证）
- shadcn/ui 组件文件名是**小写**（button.tsx, card.tsx）
- 必须使用小写路径导入：`from '@/components/ui/button'`
- Preprompts 已更新，AI 现在应该知道这个规则

### 2. Sandpack 配置
- 使用 `theme="light"` 避免黑色背景
- React 项目使用 `react-ts` 模板
- 入口文件: `src/main.tsx`
- 活动文件: `src/pages/Index.tsx`

### 3. React Router 警告（可忽略）
- Console 会显示 Future Flag 警告
- 不影响功能，是 React Router v6 的正常提示

## 🚀 下一步测试步骤

### 步骤 1: 确认服务运行
```bash
# 前端
curl http://localhost:5173

# 后端
curl http://localhost:8000/health
```

### 步骤 2: 测试 Landing Page 生成
1. 打开 http://localhost:5173
2. 输入: `"create a landingpage"`
3. 点击"生成应用"
4. 等待生成（约 10-20 秒）
5. 查看 Sandpack 预览

### 步骤 3: 检查生成的代码
如果预览失败，检查：
1. **浏览器 Console**
   - 是否有模块导入错误？
   - 是否有组件未找到？
   - 路径是否正确？

2. **后端 Terminal** (`terminal 7` 或 `terminal 13`)
   - 生成了多少个文件？
   - 是否使用了正确的 Preprompt？
   - 是否合并了模板？

3. **Network 请求**
   - `/generate` 请求是否成功（200）？
   - Response 中的文件内容是否正确？

## 📊 对比参考

### Lovable 生成的代码 (高质量参考)
位置: `competitior-landingpage/landing-page-magic/`
- 完整的 TypeScript + React 项目
- 丰富的 shadcn/ui 组件
- 优雅的动画和交互
- 响应式设计

### 当前 MVP 生成的代码
位置: 前端 localStorage 或后端生成结果
- 应该接近 Lovable 的质量
- 使用相同的技术栈
- 遵循 Lovable 设计系统

## 🎨 Lovable 设计系统

### 颜色
```css
--lovable-orange: #FFB454   /* 主色 */
--lovable-coral: #FF6A4A    /* 辅助色 */
--lovable-gray: #F8F8F9     /* 背景色 */
--lovable-dark: #1A1A1A     /* 文字色 */
```

### 设计原则
- 大圆角 (`rounded-xl`, `rounded-2xl`)
- 柔和阴影 (`shadow-lg`, `shadow-xl`)
- 平滑过渡 (`transition-all duration-200`)
- 橙色渐变 (`from-lovable-orange to-lovable-coral`)
- 充足留白 (`py-20`, `px-4`)

## 💾 重要命令

### 启动服务
```bash
# 前端
cd client && npm run dev

# 后端（推荐）
./run.sh

# 后端（手动）
cd backend && uvicorn server:app --reload
```

### 查看日志
```bash
# 前端日志
浏览器 Console (F12)

# 后端日志
cat ~/.cursor/projects/Users-gaochang-gpt-engineer/terminals/7.txt
```

### Git 操作
```bash
git status
git add .
git commit -m "fix: 修复组件导入路径大小写问题"
git push origin main
```

## 🎯 测试目标

### 成功标准
1. ✅ Landing Page 能够正确生成和预览
2. ✅ 所有组件导入路径正确（小写）
3. ✅ Sandpack 中看到完整的页面内容
4. ✅ 动画和交互正常工作
5. ✅ 响应式布局正确
6. ✅ 代码质量接近 Lovable 水平

### 如果失败
1. 复制浏览器 Console 完整输出
2. 复制后端 Terminal 最后 30 行
3. 截图 Network 请求的 Response
4. 检查生成的代码中的导入路径
5. 在新对话中提供以上信息

## 📝 相关文档

- `PLAN.md` - 项目总体规划
- `PHASE7_TEMPLATE_SYSTEM.md` - 模板系统实现文档
- `LOVABLE_UPGRADE.md` - Phase 6E UI 升级文档
- `BUGFIX.md` - 历史 Bug 修复记录

---

**准备就绪！开始测试吧！** 🚀

如果遇到问题，提供以下信息：
1. Console 完整输出
2. 后端 Terminal 日志
3. Network Response 截图
4. 具体的错误信息
