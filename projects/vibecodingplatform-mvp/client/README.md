# Vibecoding Platform - Frontend

React + Vite 前端应用，提供可视化的 AI 代码生成界面。

## 快速启动

### 1. 安装依赖

```bash
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

应用将在 `http://localhost:5173` 启动。

### 3. 构建生产版本

```bash
npm run build
```

## 功能特性

- 🎨 **现代化 UI**: 渐变背景 + 流畅动画
- 📝 **智能输入**: 支持 Enter 快捷键提交
- 🔄 **实时预览**: 使用 Sandpack 在浏览器中运行生成的代码
- ⚡ **即时反馈**: 加载状态 + 错误提示
- 📱 **响应式设计**: 支持移动端和桌面端

## 核心依赖

- **React 18**: UI 框架
- **Vite**: 构建工具
- **@codesandbox/sandpack-react**: 浏览器内代码执行引擎

## 项目结构

```
client/
├── src/
│   ├── App.jsx         # 主应用组件
│   ├── App.css         # 样式文件
│   ├── main.jsx        # 入口文件
│   └── index.css       # 全局样式
├── public/             # 静态资源
├── index.html          # HTML 模板
├── package.json        # 依赖配置
└── vite.config.js      # Vite 配置
```

## 使用说明

1. **输入提示词**: 在输入框中描述你想要的应用
2. **点击生成**: 点击 "✨ 生成应用" 按钮
3. **查看结果**: 在下方的预览窗口中看到运行的应用

### 示例提示词

- "创建一个简单的计时器"
- "创建一个待办事项列表"
- "创建一个贪吃蛇游戏"

## API 配置

默认后端地址: `http://localhost:8000`

如需修改，编辑 `src/App.jsx` 中的 `API_URL` 常量。

## 开发建议

- 使用浏览器开发者工具查看网络请求
- 检查控制台日志了解生成过程
- 修改 Sandpack 的 `template` 属性以支持不同类型的项目（vanilla, react, vue 等）
