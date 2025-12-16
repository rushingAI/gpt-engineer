# 自定义 Preprompts

这个目录包含针对 Vibecoding Platform 优化的自定义系统提示词。

## Preprompt 文件

### 核心 Preprompts
- `modern_web_app` - 现代 Web 应用通用指导
- `design_system` - Lovable 设计系统规范
- `code_quality` - 代码质量和最佳实践

### 应用类型特定 Preprompts
- `landing_page` - Landing Page 专用指导
- `dashboard` - Dashboard/SaaS 应用指导
- `component_library` - 组件库开发指导

## 设计原则

1. **明确技术栈** - 明确指定使用 React + TypeScript + shadcn/ui
2. **设计系统** - 强制使用 Lovable 的配色和视觉语言
3. **代码质量** - 强调组件化、类型安全、可维护性
4. **动画效果** - 鼓励使用 framer-motion 添加流畅动画
5. **最佳实践** - 遵循 React 和 TypeScript 最佳实践

## 与 gpt-engineer 原始 Preprompts 的区别

- 原始 preprompts 是通用的，适用于任何编程语言和项目类型
- 自定义 preprompts 专门针对现代 Web 应用，包含：
  - 具体的技术栈要求
  - 设计系统规范
  - UI/UX 最佳实践
  - 动画和交互指导
