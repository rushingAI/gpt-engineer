# 🌐 Cyberpunk 设计系统升级指南

本文档说明如何将 Vibecoding 平台的生成效果升级到统一的 Cyberpunk 赛博朋克风格。

---

## 📋 目标

通过"预设文件（Preset Files）+ 写入拦截（Write Filtering）"的模式，确保：
1. 所有生成的应用拥有统一的 Cyberpunk 视觉风格（深色背景 + 霓虹青色 + 未来科技感）
2. AI 无法修改核心配置文件（package.json, vite.config.ts, tailwind.config.js 等）
3. AI 只能在允许的沙盒路径内生成业务代码（src/pages/**, src/features/**）
4. 无论生成什么应用，都自动继承高质量的视觉效果

---

## 🔧 核心修改

### 1. 前端：Cyberpunk 预设文件系统

**文件：** `client/src/utils/cyberpunkPreset.js`

**功能：**
- 定义所有 AI 不可修改的基建文件（package.json, tailwind.config.js, src/index.css 等）
- 提供统一的 Cyberpunk 设计 tokens（深色背景 #181c20、霓虹青色 #2dd4bf）
- 包含 `AppShell` 组件（全局背景 + 网格纹理 + 光晕效果）
- 提供通用炫酷样式类：
  - `.text-gradient` - 青色渐变文字
  - `.btn-brand` - 霓虹按钮（圆形 + 发光）
  - `.btn-brand-outline` - 轮廓按钮
  - `.glass-panel` - 玻璃拟态卡片
  - `.glow-primary` - 主色光晕效果

**关键导出：**
```javascript
export const BASE_PRESET_FILES = {
  'package.json': '...',
  'tailwind.config.js': '...',
  'src/index.css': '...',
  'src/components/app/AppShell.tsx': '...',
  // ... 其他基建文件
};

export const PROTECTED_PATHS = [
  /^package\.json$/,
  /^tailwind\.config\.(js|ts)$/,
  /^src\/index\.css$/,
  /^src\/components\/ui\//,
  // ... 更多保护路径
];
```

---

### 2. 前端：文件过滤与合并逻辑

**文件：** `client/src/utils/webcontainer.js`

**新增函数：**

#### `filterGeneratedFiles(files)`
- 过滤 AI 生成的文件，只保留允许的业务路径：
  - ✅ `src/pages/**`
  - ✅ `src/features/**`
  - ✅ `src/App.tsx`
  - ✅ `src/components/generated/**`（可选）
- 阻止 AI 写入保护路径，打印警告日志：`🚫 Blocked AI write to protected file: xxx`

#### `mergeWithPreset(aiFiles)`
- 合并 Cyberpunk 预设文件和 AI 业务文件
- 预设文件优先，保证基建不被覆盖
- 返回完整的文件树供 WebContainer 挂载

---

### 3. 前端：挂载流程集成

**文件：** `client/src/components/preview/WebContainerPreview.jsx`

**修改点：**
```javascript
// 原来：直接转换 AI 返回的文件
const fileSystemTree = convertToFileSystemTree(files)

// 现在：先合并预设，再转换
const finalFiles = mergeWithPreset(files) // 🎨 关键步骤
const fileSystemTree = convertToFileSystemTree(finalFiles)
```

**效果：**
- 每次挂载前自动注入 Cyberpunk 预设文件
- AI 生成的 `src/pages/Index.tsx` 等业务文件覆盖到预设之上
- 最终形成完整且风格统一的项目

---

### 4. 后端：Cyberpunk React Preprompt

**文件：** `backend/preprompts_custom/cyberpunk_react`

**功能：**
- 向 AI 明确说明它处于受限的 WebContainer 环境
- 列出禁止生成的文件（配置文件、基建文件）
- 强制要求使用 `<AppShell>` 组件包裹所有页面
- 提供详细的 Cyberpunk 设计系统使用指南和代码示例
- 包含三种设计模式示例：
  1. 全屏居中特性（倒计时、计数器）
  2. 仪表盘卡片布局
  3. 表单与玻璃拟态面板

**关键约束：**
```
❌ 禁止生成：
   - package.json
   - vite.config.ts
   - tailwind.config.js
   - src/index.css
   - src/components/ui/**

✅ 只能生成：
   - src/pages/**/*.tsx
   - src/features/**/*.tsx
   - src/App.tsx (仅路由)
```

---

### 5. 后端：Preprompt 管理器更新

**文件：** `backend/preprompt_manager.py`

**修改：**
```python
def build_system_prompt(self, app_type: str = "cyberpunk_react", use_cyberpunk: bool = True):
    """默认使用 Cyberpunk React 预设"""
    if use_cyberpunk:
        base_preprompt = self.load_preprompt("cyberpunk_react")
    else:
        base_preprompt = self.load_preprompt("modern_web_app")  # 兼容旧版
```

**效果：**
- 所有新生成的应用默认使用 `cyberpunk_react` preprompt
- AI 会自动遵循 Cyberpunk 设计约束
- 支持通过 `use_cyberpunk=False` 回退到旧版风格（向后兼容）

---

### 6. 后端：Server API 更新

**文件：** `backend/server.py`

**修改：**
- 将所有提到 "Lovable design system" 的地方改为 "Cyberpunk design system"
- 确保 `/generate` 和 `/improve` 端点的提示词都包含 Cyberpunk 约束

---

## 🎨 Cyberpunk 设计系统核心

### 颜色方案
```css
--background: 222 84% 5%;        /* 深色背景 #181c20 */
--foreground: 210 40% 98%;       /* 浅色文字 */
--primary: 174 72% 50%;          /* 霓虹青色 #2dd4bf */
--card: 220 18% 14%;             /* 卡片深色 */
--border: 220 15% 22%;           /* 边框 */
```

### 字体系统
- **Display（标题）**：Space Grotesk - 宽松的几何无衬线体
- **Mono（数字/代码）**：JetBrains Mono - 等宽字体，适合数字显示

### 通用样式类
| 类名 | 用途 | 效果 |
|------|------|------|
| `.text-gradient` | 标题、重要数字 | 青色渐变文字 |
| `.btn-brand` | 主要按钮 | 圆形 + 渐变 + 发光 |
| `.btn-brand-outline` | 次要按钮 | 轮廓 + 悬停发光 |
| `.glass-panel` | 内容卡片 | 玻璃拟态 + 渐变 |
| `.glow-primary` | 强调元素 | 多层发光阴影 |

### AppShell 组件
所有页面必须使用 `<AppShell>` 包裹：
```tsx
import { AppShell } from '@/components/app/AppShell';

export default function MyPage() {
  return (
    <AppShell>
      {/* 你的页面内容 */}
    </AppShell>
  );
}
```

**提供功能：**
- 深色全屏背景
- 网格纹理背景
- 左上角 + 右下角光晕效果
- 居中响应式容器
- 渐入动画

---

## ✅ 验证与测试流程

### 步骤 1：启动开发环境

**前端：**
```bash
cd projects/vibecodingplatform-mvp/client
npm install
npm run dev
```

**后端：**
```bash
cd projects/vibecodingplatform-mvp/backend
pip install -r requirements.txt
python server.py
```

---

### 步骤 2：测试生成应用

1. 打开浏览器访问前端页面（通常是 `http://localhost:5173`）
2. 在对话框输入测试提示词：
   - "做一个计数器"
   - "做一个番茄钟"
   - "做一个待办事项"
3. 点击"生成"按钮

---

### 步骤 3：观察控制台日志

**预期日志（前端 Console）：**
```
🎨 Merging files with Cyberpunk preset...
✅ File filtering complete: 2 allowed, 8 blocked
📦 Total files in merged tree: 15
📋 Preset files: package.json, tailwind.config.js, src/index.css, ...
📋 AI business files: src/pages/Index.tsx, src/App.tsx
```

**关键指标：**
- 如果看到 `🚫 Blocked AI write to protected file: xxx`，说明拦截生效 ✅
- 预设文件数量应该是 11-12 个
- AI 业务文件应该只有 1-3 个（主要是 `src/pages/Index.tsx`）

---

### 步骤 4：视觉验收

生成完成后，预览界面应该呈现：

#### 必须有的视觉元素：
- [ ] **深色背景**（接近黑色 #181c20）
- [ ] **网格纹理**（背景上的细微网格线）
- [ ] **光晕效果**（左上角青色、右下角紫色模糊光）
- [ ] **霓虹青色主题**（按钮、标题等使用 #2dd4bf）
- [ ] **渐变文字**（重要标题应该有青色渐变效果）
- [ ] **发光按钮**（按钮周围有光晕，悬停时增强）
- [ ] **玻璃拟态卡片**（如果有卡片，应该是半透明深色）

#### 测试交互：
- [ ] 悬停按钮时，按钮应该放大并增强光晕
- [ ] 点击按钮时，应该有缩小反馈
- [ ] 页面加载时应该有渐入动画（0.6s）

---

### 步骤 5：代码审查

打开生成的项目文件（可在 WebContainer 中查看）：

#### 检查 AI 是否遵守约束：
```bash
# 检查是否生成了禁止的文件（应该没有这些）
✅ package.json - 应该是预设版本（含 cyberpunk-app 名称）
✅ tailwind.config.js - 应该包含 Cyberpunk 颜色定义
✅ src/index.css - 应该包含 .text-gradient, .btn-brand 等类

# 检查 AI 生成的业务文件
✅ src/pages/Index.tsx - 应该导入并使用 <AppShell>
✅ src/App.tsx - 应该包含路由配置
```

#### 验证 AppShell 使用：
打开 `src/pages/Index.tsx`，应该看到：
```tsx
import { AppShell } from '@/components/app/AppShell';

export default function Index() {
  return (
    <AppShell>
      {/* 业务内容 */}
    </AppShell>
  );
}
```

#### 验证样式类使用：
AI 生成的代码应该使用预定义的类：
```tsx
<h1 className="text-gradient text-6xl font-bold">
  计数器
</h1>

<button className="btn-brand px-8 py-4">
  开始
</button>

<div className="glass-panel p-8">
  {/* 内容 */}
</div>
```

---

## 🐛 常见问题与解决

### 问题 1：生成的应用没有 Cyberpunk 风格

**排查：**
1. 检查控制台是否有 `🎨 Merging files with Cyberpunk preset...` 日志
2. 如果没有，说明前端的 `mergeWithPreset` 没有被调用

**解决：**
```bash
# 确认前端导入正确
grep "mergeWithPreset" client/src/components/preview/WebContainerPreview.jsx

# 应该看到：
# import { ..., mergeWithPreset } from '@/utils/webcontainer'
# const finalFiles = mergeWithPreset(files)
```

---

### 问题 2：AI 仍然生成了配置文件

**排查：**
1. 检查控制台是否有 `🚫 Blocked` 日志
2. 如果有，说明拦截生效但可能有遗漏的路径

**解决：**
```javascript
// 在 cyberpunkPreset.js 中添加更多保护路径
export const PROTECTED_PATHS = [
  /^package\.json$/,
  /^vite\.config\.(ts|js)$/,
  /^tailwind\.config\.(js|ts)$/,
  /^postcss\.config\.(js|cjs)$/,
  /^index\.html$/,
  /^src\/index\.css$/,
  /^src\/main\.tsx$/,
  /^src\/lib\/utils\.ts$/,
  /^src\/components\/app\//,
  /^src\/components\/ui\//,
  // 添加你发现的其他路径
];
```

---

### 问题 3：后端 preprompt 没有加载

**排查：**
```bash
# 检查文件是否存在
ls backend/preprompts_custom/cyberpunk_react

# 检查后端日志
python backend/server.py
# 启动时应该没有 "preprompt 不存在" 的警告
```

**解决：**
- 确保 `cyberpunk_react` 文件存在且没有扩展名
- 确保文件编码是 UTF-8
- 确保文件内容没有语法错误

---

### 问题 4：WebContainer 挂载失败

**排查：**
```javascript
// 检查浏览器控制台是否有 npm install 错误
```

**解决：**
```javascript
// 确保 package.json 中的依赖版本正确
// 在 cyberpunkPreset.js 中检查：
const PACKAGE_JSON = {
  dependencies: {
    "react": "^18.2.0",  // 确保版本兼容
    "react-dom": "^18.2.0",
    // ...
  }
};
```

---

## 📊 成功指标

完成升级后，应该达到以下效果：

### 视觉一致性
- [ ] 所有生成的应用都有深色背景 + 霓虹青色主题
- [ ] 所有应用都使用相同的字体（Space Grotesk + JetBrains Mono）
- [ ] 所有按钮都有发光效果
- [ ] 所有卡片都有玻璃拟态效果

### 技术约束
- [ ] AI 无法修改 `package.json`
- [ ] AI 无法修改 `tailwind.config.js`
- [ ] AI 无法修改 `src/index.css`
- [ ] AI 无法修改 `src/components/ui/` 下的组件

### 生成质量
- [ ] 生成的代码自动使用 `<AppShell>`
- [ ] 生成的代码自动使用 `.btn-brand` 等预定义类
- [ ] 生成的应用无需手动调整即可呈现高质量视觉效果

---

## 🚀 下一步优化建议

1. **主题切换**：添加浅色主题支持（通过环境变量切换）
2. **更多预设**：创建其他风格预设（如 Glassmorphism、Neo-brutalism）
3. **组件库扩展**：添加更多 Cyberpunk 风格的自定义组件
4. **性能监控**：记录生成时的拦截统计，优化规则
5. **A/B 测试**：对比 Cyberpunk 风格与原风格的用户满意度

---

## 📝 相关文件清单

### 前端
- `client/src/utils/cyberpunkPreset.js` - Cyberpunk 预设文件定义
- `client/src/utils/webcontainer.js` - 文件过滤和合并逻辑
- `client/src/components/preview/WebContainerPreview.jsx` - 挂载流程集成

### 后端
- `backend/preprompts_custom/cyberpunk_react` - AI 系统提示词
- `backend/preprompt_manager.py` - Preprompt 管理器
- `backend/server.py` - API 端点更新

---

## 🎉 总结

通过本次升级，Vibecoding 平台实现了：

✅ **设计规范固化**：将 Cyberpunk 风格硬编码在底层，无需每次生成时重复描述
✅ **AI 沙盒机制**：通过文件拦截确保 AI 只能操作业务代码，保护基建文件
✅ **视觉一致性**：所有生成的应用自动继承统一的高级感
✅ **开发体验提升**：用户无需关心样式细节，专注于功能描述

现在，无论用户输入什么需求（计数器、待办、仪表盘），生成的应用都会拥有：
- 🌑 深邃的深色背景
- 💎 霓虹青色的赛博朋克美学
- ✨ 炫酷的发光和动画效果
- 🎯 专业的玻璃拟态设计

**Vibecoding = 让每个 AI 生成的应用都拥有 Lovable 级别的视觉质量！** 🚀

