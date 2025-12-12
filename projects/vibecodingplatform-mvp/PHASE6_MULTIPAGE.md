# Phase 6: 多页应用与对话式交互

## 概述

Phase 6 将平台从单页应用升级为多页应用架构，采用对话式交互模式，参考 Lovable 的 UI/UX 设计。

## 主要功能

### ✅ 1. 多页应用架构
- **首页（Landing Page）**：简洁的输入框 + 生成按钮
- **项目页（Project Page）**：对话式交互 + 实时预览

### ✅ 2. 对话式交互
- **持续对话**：用户可以连续发送消息来优化应用
- **智能判断**：自动判断使用 improve_fn 还是 gen_code
- **对话历史**：每个项目保存完整的对话记录

### ✅ 3. 左右分割布局
- **左侧（40%）**：对话区
  - 消息列表（用户 + AI）
  - 输入框（固定底部）
  - 历史记录按钮
- **右侧（60%）**：预览/代码区
  - Sandbox/Code 标签切换
  - 自适应高度（填满容器）

### ✅ 4. 数据结构升级
- 新增 `messages` 字段存储对话历史
- 兼容旧数据（向后兼容）
- 为 Supabase 迁移预留接口

## 文件结构

```
client/src/
├── pages/
│   ├── LandingPage.jsx           # 首页
│   └── ProjectPage.jsx           # 项目页
├── components/
│   ├── chat/
│   │   ├── ChatPanel.jsx         # 对话区容器
│   │   ├── MessageList.jsx       # 消息列表
│   │   └── ChatInput.jsx         # 输入框
│   └── preview/
│       ├── PreviewPanel.jsx      # 预览/代码区容器
│       └── TabBar.jsx            # 标签切换
├── utils/
│   ├── storage.js                # localStorage 操作
│   ├── promptAnalyzer.js         # 智能优化判断
│   └── api.js                    # API 调用封装
├── styles/
│   ├── LandingPage.css
│   ├── ProjectPage.css
│   ├── ChatPanel.css
│   ├── MessageList.css
│   ├── ChatInput.css
│   ├── PreviewPanel.css
│   └── TabBar.css
└── App.jsx                       # 路由配置
```

## 数据结构

### 项目对象
```javascript
{
  id: '1733900400000',              // 项目ID（时间戳）
  name: '应用名称',                  // 自动提取的名称
  files: {                          // Sandpack 文件
    '/index.html': '...'
  },
  prompt: '初始 prompt',            // 第一条用户消息
  messages: [                       // 对话历史（新增）
    {
      role: 'user',
      content: '创建一个计数器',
      timestamp: '2025-12-11T10:30:00.000Z'
    },
    {
      role: 'assistant',
      content: '✅ 已生成应用\n📂 生成了 1 个文件',
      timestamp: '2025-12-11T10:30:05.000Z',
      filesCount: 1
    }
  ],
  timestamp: '2025-12-11T10:30:00.000Z'  // 创建时间
}
```

## 智能优化判断

### 判断逻辑

**使用 improve_fn（小改动）**：
- 关键词：修改、改、换、调整、优化、更新、变更、修复
- 示例：`"把背景改成蓝色"`
- 特点：快速、针对性强

**使用 gen_code（大改动）**：
- 关键词：添加、增加、新增、加上、实现、创建、生成
- 示例：`"添加一个统计面板"`
- 特点：重新生成，功能更完整

**默认**：使用 improve_fn

### 实现代码

```javascript
// utils/promptAnalyzer.js
export function shouldUseImprove(userMessage) {
  const improveKeywords = [
    '修改', '改', '换', '调整', '优化', '更新'
  ]
  const genKeywords = [
    '添加', '增加', '新增', '加上', '实现'
  ]
  
  const hasImprove = improveKeywords.some(kw => userMessage.includes(kw))
  const hasGen = genKeywords.some(kw => userMessage.includes(kw))
  
  if (hasImprove && !hasGen) return true
  if (hasGen) return false
  
  return true  // 默认 improve
}
```

## 用户流程

### 1. 进入首页
```
用户访问 / → 看到简洁的输入框
```

### 2. 创建应用
```
输入 "创建一个计数器"
  ↓
点击 "✨ 生成应用"
  ↓
调用 API 生成代码
  ↓
创建项目对象（包含 messages）
  ↓
保存到 localStorage + history
  ↓
跳转到 /project/:id
```

### 3. 项目页交互
```
左侧：对话区
  - 显示历史消息
  - 用户输入新消息："把背景改成蓝色"
  ↓
智能判断：检测到"改" → 使用 improve_fn
  ↓
调用 /improve 端点
  ↓
更新 files 和 messages
  ↓
右侧：预览区自动更新
```

### 4. 切换视图
```
点击 [👁️ Sandbox] → 显示应用预览
点击 [</> Code] → 显示代码编辑器
```

## API 调用

### 生成应用
```javascript
import { generateApp } from './utils/api'

const files = await generateApp('创建一个计数器')
// 返回: { '/index.html': '...' }
```

### 改进应用
```javascript
import { improveApp } from './utils/api'

const newFiles = await improveApp(
  '把背景改成蓝色',
  currentFiles
)
// 返回: { '/index.html': '...' }  // 更新后的文件
```

## Sandbox 自适应

### CSS 配置
```css
.preview-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 70px);  /* 减去 header 高度 */
}

.preview-content {
  flex: 1;
  overflow: hidden;
}

/* Sandpack iframe 填满容器 */
.preview-content iframe {
  width: 100%;
  height: 100% !important;
}
```

### 特点
- ✅ iframe 自动填满容器
- ✅ 响应式高度（适应不同屏幕）
- ✅ 适合游戏、复杂应用

## 响应式设计

### 桌面端（> 1024px）
```
┌─────────────────┬──────────────────┐
│  对话区 (40%)   │  预览区 (60%)     │
│                 │                  │
│  消息列表       │  Sandbox/Code    │
│                 │                  │
│  输入框         │                  │
└─────────────────┴──────────────────┘
```

### 移动端（< 1024px）
```
┌──────────────────────────────────┐
│  对话区 (50vh)                   │
│  消息列表 + 输入框               │
├──────────────────────────────────┤
│  预览区 (50vh)                   │
│  Sandbox/Code                    │
└──────────────────────────────────┘
```

## 测试场景

### 测试 1：基本流程
1. 访问首页
2. 输入 `"创建一个计数器"`
3. 点击生成
4. ✅ 跳转到项目页
5. ✅ 左侧显示对话历史
6. ✅ 右侧显示计数器应用

### 测试 2：持续对话
1. 在项目页输入 `"把背景改成蓝色渐变"`
2. ✅ 检测到"改" → 使用 improve_fn
3. ✅ 右侧预览更新为蓝色渐变
4. ✅ 对话历史添加新消息

### 测试 3：添加功能
1. 输入 `"添加一个重置按钮"`
2. ✅ 检测到"添加" → 使用 gen_code
3. ✅ 重新生成完整应用（包含重置按钮）
4. ✅ 保持之前的蓝色渐变背景

### 测试 4：视图切换
1. 点击 [</> Code] 标签
2. ✅ 显示代码编辑器
3. ✅ 可以查看 HTML 代码
4. 点击 [👁️ Sandbox]
5. ✅ 切换回预览模式

### 测试 5：刷新保持
1. 在项目页刷新浏览器
2. ✅ 项目数据从 localStorage 恢复
3. ✅ 对话历史完整保留
4. ✅ 预览正常显示

## 与其他阶段的关系

### Phase 5A/5B 的变化
- **之前**：单页应用，历史记录侧边栏
- **现在**：多页应用，对话式交互
- **兼容性**：数据结构向后兼容（新增 messages 字段）

### Phase 5C（Supabase）时的改动
```javascript
// 只需替换存储层
// 之前
localStorage.setItem(STORAGE_KEY, JSON.stringify(project))

// Phase 5C 时
await supabase.from('projects').insert(project)
```

### Phase 7（流式生成）时的改动
```javascript
// 在 MessageList 中添加打字机效果
function StreamingMessage({ content }) {
  return <TypeWriter text={content} speed={50} />
}
```

## 性能优化

### 1. 路由懒加载
```javascript
const LandingPage = lazy(() => import('./pages/LandingPage'))
const ProjectPage = lazy(() => import('./pages/ProjectPage'))
```

### 2. 消息列表虚拟化
对于超过 100 条消息的对话，使用虚拟滚动

### 3. Sandpack 优化
- 使用 `key` 强制重新挂载
- `autorun: true` 自动运行
- `autoReload: true` 自动重载

## 已知限制

1. **历史记录模态框**：暂时未实现，显示占位符
2. **导出功能**：未实现项目导出
3. **分享功能**：需要 Phase 5C（Supabase）
4. **多人协作**：需要 Phase 5C（Supabase）

## 总结

Phase 6 成功将平台升级为多页应用，实现了对话式交互，大大提升了用户体验：

✅ **多页应用架构**（首页 + 项目页）
✅ **对话式交互**（持续优化应用）
✅ **智能优化判断**（improve vs gen）
✅ **Sandbox/Code 切换**（灵活查看）
✅ **自适应预览**（填满容器）
✅ **对话历史存储**（localStorage）
✅ **响应式设计**（桌面 + 移动端）

**为后续阶段预留了良好的接口**，可以无缝集成流式生成和云端存储功能。

