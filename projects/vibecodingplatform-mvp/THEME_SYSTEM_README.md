# 多主题系统实现文档

## 概述

已成功实现了多主题系统，支持：
- ✅ 12 套预设主题（teal/amber/violet/blue/pink/lime/cyan/red/emerald/orange/magenta/sky）
- ✅ 自动颜色意图识别（支持中英文颜色词 + hex 代码）
- ✅ 主题持久化（存储在 project.metadata）
- ✅ 旧项目自动补齐主题
- ✅ WebContainer 预览中自动应用主题
- ✅ 所有通用 CSS class 使用变量（.text-gradient/.btn-brand/.glow-primary/.surface-card 等）

## 新增文件

### 1. `client/src/utils/themes.js`
主题池，定义了 12 套预设主题，每个主题包含：
- 主题名称和描述
- CSS 变量配置（--brand1, --brand2, --glow, --bg, --card 等）

**主题列表：**
- `teal` - 青绿霓虹（默认，原有的赛博朋克风格）
- `amber` - 橙黄霓虹（温暖金黄色）
- `violet` - 紫色霓虹（电光紫）
- `blue` - 蓝色霓虹（电光蓝）
- `pink` - 粉色霓虹（热力粉）
- `lime` - 青柠霓虹（明亮绿）
- `cyan` - 青色霓虹（明亮青）
- `red` - 红色霓虹（热力红）
- `emerald` - 翡翠霓虹（翡翠绿）
- `orange` - 橙色霓虹（活力橙）
- `magenta` - 洋红霓虹（电光洋红）
- `sky` - 天空蓝霓虹（天空蓝）

### 2. `client/src/utils/theme.js`
主题应用工具，提供：
- `applyTheme(themeName, overrides)` - 应用主题到页面
- `ensureProjectTheme(project, userPromptText)` - 确保项目有主题（自动选择 + 保存）
- `getProjectTheme(project)` - 获取项目主题
- `getProjectThemeOverrides(project)` - 获取主题覆盖

### 3. `client/src/utils/colorIntent.js`
颜色意图提取，支持：
- 中文颜色词：橙/黄/紫/蓝/粉/绿/青/红等
- 英文颜色词：orange/amber/violet/blue/pink 等
- Hex 颜色代码：#FF9900 等
- 自动映射到最接近的主题

**示例：**
- "创建一个**橙色主题**的计数器" → 选择 `orange` 主题
- "我要一个**紫色**的待办列表" → 选择 `violet` 主题
- "用 **#FF9900** 作为主题色" → 自动映射到 `orange` 主题
- "普通的计数器应用"（无颜色词）→ 随机选择主题

## 修改的文件

### 1. `client/src/utils/storage.js`
新增：
- `saveProject(project)` - 别名函数，用于统一接口
- `ensureProjectMetadata(project)` - 确保 project.metadata 存在

### 2. `client/src/pages/LandingPage.jsx`
修改：
- 创建项目时初始化 `metadata: {}`
- 调用 `ensureProjectTheme(project, prompt)` 自动选择主题
- 主题信息会保存到 localStorage

### 3. `client/src/pages/ProjectPage.jsx`
修改：
- 加载项目时调用 `ensureProjectTheme()` 补齐旧项目主题
- 调用 `applyTheme()` 应用主题到当前页面
- 传递 `project` 对象给 PreviewPanel

### 4. `client/src/components/preview/PreviewPanel.jsx`
修改：
- 接收 `project` 参数并传递给 WebContainerPreview

### 5. `client/src/components/preview/WebContainerPreview.jsx`
修改：
- 接收 `project` 参数
- 获取项目主题信息
- 调用 `mergeWithPreset(files, themeName, themeOverrides)` 应用主题

### 6. `client/src/utils/webcontainer.js`
修改：
- `mergeWithPreset()` 新增 `themeName` 和 `themeOverrides` 参数
- 新增 `generateThemeVariablesCSS()` - 生成主题 CSS 变量
- 新增 `injectThemeVariables()` - 注入主题变量到 index.css

### 7. `client/src/utils/cyberpunkPreset.js`
修改 `INDEX_CSS`：
- 将所有写死的颜色值改为 CSS 变量引用
- `.text-gradient` 使用 `var(--brand1)` 和 `var(--brand2)`
- `.glow-primary` 使用 `var(--glow)`
- `.btn-brand` 使用 `var(--brand1)` 和 `var(--brand2)`
- `.btn-brand-outline` 使用 `var(--brand1)`
- 新增 `.surface-card` 别名

**修改前（写死颜色）：**
```css
.text-gradient {
  background: linear-gradient(135deg, hsl(174 72% 56%) 0%, hsl(174 72% 50%) 100%);
}
```

**修改后（使用变量）：**
```css
.text-gradient {
  background: linear-gradient(135deg, hsl(var(--brand1)) 0%, hsl(var(--brand2)) 100%);
}
```

## 数据结构

### Project 对象（更新后）
```javascript
{
  id: "1234567890",
  name: "计数器应用",
  files: { ... },
  prompt: "创建一个橙色主题的计数器",
  messages: [ ... ],
  metadata: {
    themeName: "orange",           // 新增：主题名称
    themeOverrides: {}             // 新增：主题覆盖（可选）
  },
  timestamp: "2023-12-15T10:00:00.000Z"
}
```

## 工作流程

### 创建新项目
1. 用户输入 prompt："创建一个橙色主题的计数器"
2. LandingPage.jsx 创建项目对象，初始化 `metadata: {}`
3. 调用 `ensureProjectTheme(project, prompt)`：
   - `extractColorIntent(prompt)` → 识别到 "橙色" → `{colorName: "orange"}`
   - `selectThemeByIntent()` → 选择 `orange` 主题
   - 写入 `project.metadata.themeName = "orange"`
   - 保存到 localStorage
4. 跳转到 ProjectPage，生成的应用使用橙色主题

### 打开已有项目
1. ProjectPage.jsx 从 localStorage 加载项目
2. 调用 `ensureProjectTheme(project)` - 如果是旧项目（没有 themeName），自动随机选择并保存
3. 调用 `applyTheme(themeName, overrides)` - 应用主题到当前页面
4. WebContainerPreview 启动时：
   - 调用 `mergeWithPreset(files, themeName, themeOverrides)`
   - 预设文件的 `src/index.css` 会被注入主题变量
   - 生成的应用显示正确的主题颜色

## 验证步骤

### 1. 测试随机主题（不指定颜色）
**操作：**
```
Prompt 1: "创建一个计数器应用"
Prompt 2: "创建一个待办列表"
Prompt 3: "创建一个数据仪表盘"
```

**预期结果：**
- 3 个项目应该有不同的主题色（不全是青绿色）
- 每个项目的主题应该保持一致（刷新页面后不变）

### 2. 测试颜色意图识别（橙色）
**操作：**
```
Prompt: "创建一个橙色主题的计数器"
```

**预期结果：**
- 应用应该显示橙黄色主题（不是青绿色）
- 渐变文字、按钮、光晕都是橙黄色系
- 刷新页面后主题保持不变

### 3. 测试颜色意图识别（紫色）
**操作：**
```
Prompt: "我要一个紫色的待办列表"
```

**预期结果：**
- 应用应该显示紫色主题
- 所有品牌色元素都是紫色系

### 4. 测试 Hex 颜色识别
**操作：**
```
Prompt: "创建一个 #FF9900 主题的应用"
```

**预期结果：**
- 应用应该映射到最接近的主题（可能是 orange 或 amber）
- 控制台应该输出色相计算日志

### 5. 测试旧项目自动补齐
**操作：**
1. 如果有旧项目（没有 metadata 字段），打开它
2. 查看控制台日志

**预期结果：**
- 控制台输出："🎨 项目缺少主题，开始自动选择..."
- 控制台输出："✅ 主题已设置并保存: xxx"
- 项目应该显示新选择的主题
- 刷新页面后主题保持不变

### 6. 测试多个项目切换
**操作：**
1. 创建项目 A（橙色主题）
2. 创建项目 B（紫色主题）
3. 切换回项目 A
4. 切换回项目 B

**预期结果：**
- 项目 A 始终显示橙色主题
- 项目 B 始终显示紫色主题
- 主题不会混淆

## 控制台日志示例

### 成功识别颜色意图
```
🎨 项目缺少主题，开始自动选择...
🎨 提取到中文颜色关键词: 橙色 -> orange
  ↳ 从 prompt 识别颜色意图: {colorName: "orange", hex: null}
  ↳ 选择匹配主题: orange
✅ 主题已设置并保存: orange
🎨 应用主题: 橙色霓虹 (orange)
✅ 主题已应用
```

### 随机选择主题
```
🎨 项目缺少主题，开始自动选择...
  ↳ 随机选择主题: violet
✅ 主题已设置并保存: violet
🎨 应用主题: 紫色霓虹 (violet)
✅ 主题已应用
```

### WebContainer 应用主题
```
🎨 Merging files with Cyberpunk preset (theme: orange)...
  ↳ Theme variables injected into index.css
📦 Total files in merged tree: 15
```

## 技术细节

### CSS 变量系统
所有主题都通过以下 CSS 变量控制：
- `--brand1` - 主色 1（渐变起点）
- `--brand2` - 主色 2（渐变终点）
- `--glow` - 光晕颜色
- `--bg` - 背景色
- `--card` - 卡片背景
- `--ring` - 聚焦环颜色
- `--border` - 边框颜色
- `--gradient-start` - 渐变起点（别名）
- `--gradient-end` - 渐变终点（别名）

### 主题优先级
1. 用户明确指定的颜色（prompt 中提到）
2. 项目已保存的主题（project.metadata.themeName）
3. 随机选择的主题

### 兼容性
- 旧项目（没有 metadata）会自动补齐并保存
- 默认主题是 `teal`（原有的青绿色）
- 所有 shadcn 组件继续正常工作（因为使用 HSL 格式）

## 扩展性

### 添加新主题
在 `client/src/utils/themes.js` 的 `THEMES` 对象中添加：

```javascript
newtheme: {
  name: 'newtheme',
  displayName: '新主题名称',
  description: '主题描述',
  colors: {
    '--brand1': '色相 饱和度% 亮度%',  // HSL 格式
    '--brand2': '色相 饱和度% 亮度%',
    '--glow': '色相 饱和度% 亮度%',
    '--bg': '222 84% 5%',              // 保持深色背景
    '--card': '220 18% 14%',           // 保持深色卡片
    '--ring': '色相 饱和度% 亮度%',
    '--border': '220 15% 22%',         // 保持深色边框
    '--primary': '色相 饱和度% 亮度%',
    '--accent': '色相 饱和度% 亮度%',
    '--gradient-start': '色相 饱和度% 亮度%',
    '--gradient-end': '色相 饱和度% 亮度%',
  }
}
```

### 添加新的颜色关键词
在 `client/src/utils/colorIntent.js` 的 `COLOR_KEYWORDS` 或 `ENGLISH_COLOR_KEYWORDS` 中添加映射。

## 故障排查

### 问题：主题没有应用
**检查：**
1. 控制台是否有 `🎨 应用主题` 日志？
2. `project.metadata.themeName` 是否存在？
3. 浏览器开发者工具 → Elements → `:root` 查看 CSS 变量是否正确

### 问题：颜色意图识别失败
**检查：**
1. 控制台是否有 `🎨 提取到...` 日志？
2. 检查 `colorIntent.js` 中的关键词映射表
3. 尝试使用更明确的颜色词（如"橙色主题"而不是"橙"）

### 问题：旧项目没有自动补齐
**检查：**
1. 确保 `ProjectPage.jsx` 中调用了 `ensureProjectTheme()`
2. 控制台是否有 `🎨 项目缺少主题` 日志？
3. 刷新页面后 localStorage 中是否有 `metadata` 字段

## 总结

✅ **已完成所有功能：**
- 12 套主题池
- 颜色意图提取（中英文 + hex）
- 主题持久化
- 旧项目自动补齐
- CSS 变量化（不写死颜色）
- WebContainer 预览支持

✅ **代码质量：**
- 无 linter 错误
- 完整的控制台日志
- 向后兼容（旧项目自动升级）
- 模块化设计（易于扩展）

