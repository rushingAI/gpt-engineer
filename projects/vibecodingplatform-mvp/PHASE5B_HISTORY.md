# Phase 5B: 多应用历史管理

## 功能概述

在 Phase 5A 的基础上，实现多应用历史记录管理，用户可以保存、浏览、切换和删除最近生成的 10 个应用。

## 实现功能

### ✅ 1. 历史记录保存
- 每次生成/改进应用时自动添加到历史记录
- 最多保存 10 个应用（超出时自动删除最旧的）
- 历史记录存储在 localStorage

### ✅ 2. 历史记录侧边栏
- 点击右上角"📚 历史记录 (N)"按钮打开侧边栏
- 侧边栏显示在左侧，宽度 320px
- 按时间倒序显示（最新的在最上面）

### ✅ 3. 应用切换
- 点击历史记录卡片恢复对应的应用
- 自动切换 Sandpack 预览
- 更新当前应用状态

### ✅ 4. 删除记录
- 每个历史记录卡片右上角有 🗑️ 删除按钮
- 点击后弹出确认对话框
- 删除后更新 localStorage 和UI

### ✅ 5. 应用命名
- **自动提取**：从 prompt 自动提取应用名称（前20字符）
- **手动编辑**：双击应用名称进入编辑模式
- **Enter 保存**：按 Enter 或失焦保存新名称

## 数据结构

### 历史记录数组
```javascript
[
  {
    id: '1733900400000',           // 唯一ID（时间戳）
    name: '财务追踪器',             // 应用名称
    prompt: '创建一个个人财务...',  // 完整 prompt
    files: { '/index.html': '...' }, // Sandpack 文件
    timestamp: '2025-12-11T10:30:00.000Z' // ISO时间戳
  },
  // ... 最多 10 个
]
```

### localStorage 键
- `vibecodingplatform_current_app` - 当前应用
- `vibecodingplatform_history` - 历史记录数组（最多10个）

## 核心函数

### extractAppName(prompt)
从 prompt 提取应用名称：
```javascript
const extractAppName = (prompt) => {
  const cleanPrompt = prompt
    .replace(/^(创建|生成|做|制作)(一个)?/g, '')
    .trim()
  return cleanPrompt.substring(0, 20) + 
    (cleanPrompt.length > 20 ? '...' : '')
}
```

**示例**：
- 输入：`创建一个财务追踪应用，支持添加收支记录`
- 输出：`财务追踪应用，支持添加收支...`

### addToHistory(appData)
添加到历史记录（最多10个）：
```javascript
const addToHistory = (appData) => {
  const savedHistory = localStorage.getItem(HISTORY_KEY)
  let historyList = savedHistory ? JSON.parse(savedHistory) : []
  
  // 添加到开头（最新的在前）
  historyList.unshift(appData)
  
  // 只保留最近10个
  if (historyList.length > MAX_HISTORY) {
    historyList = historyList.slice(0, MAX_HISTORY)
  }
  
  localStorage.setItem(HISTORY_KEY, JSON.stringify(historyList))
  setHistory(historyList)
}
```

### loadFromHistory(item)
从历史记录恢复应用：
```javascript
const loadFromHistory = (item) => {
  setFiles(item.files)
  setPrompt(item.prompt)
  setSavedApp({ timestamp: item.timestamp })
  
  // 更新当前应用
  localStorage.setItem(STORAGE_KEY, JSON.stringify(item))
  
  setShowHistory(false)
  console.log('✓ 已从历史记录恢复应用:', item.name)
}
```

### deleteHistoryItem(id, e)
删除单个历史记录：
```javascript
const deleteHistoryItem = (id, e) => {
  e.stopPropagation() // 防止触发 loadFromHistory
  if (confirm('确定要删除这个历史记录吗？')) {
    const newHistory = history.filter(item => item.id !== id)
    localStorage.setItem(HISTORY_KEY, JSON.stringify(newHistory))
    setHistory(newHistory)
    console.log('✓ 已删除历史记录')
  }
}
```

### renameHistoryItem(id, newName)
重命名应用：
```javascript
const renameHistoryItem = (id, newName) => {
  const newHistory = history.map(item => 
    item.id === id ? { ...item, name: newName } : item
  )
  localStorage.setItem(HISTORY_KEY, JSON.stringify(newHistory))
  setHistory(newHistory)
  setEditingNameId(null)
  console.log('✓ 已重命名应用')
}
```

## UI 设计

### 历史记录按钮
- 位置：右上角 Header
- 样式：紫色按钮，显示数量 `📚 历史记录 (N)`
- 激活时背景色变为蓝色

### 侧边栏布局
```
┌─────────────────────────────┐
│ 📚 历史记录          [✕]   │  ← Header
├─────────────────────────────┤
│                             │
│  ┌─────────────────────┐   │
│  │ 财务追踪器      [🗑️] │   │  ← 历史记录卡片
│  │ 12/11 10:30        │   │
│  └─────────────────────┘   │
│                             │
│  ┌─────────────────────┐   │
│  │ 待办事项列表    [🗑️] │   │
│  │ 12/11 09:15        │   │
│  └─────────────────────┘   │
│                             │
│  ...                        │
│                             │
└─────────────────────────────┘
```

### 卡片样式
- 白色背景 + 浅灰边框
- Hover 时显示阴影
- 点击恢复应用
- 双击名称进入编辑模式
- 右上角删除按钮

## 测试步骤

### 测试 1：保存多个应用
1. 生成第一个应用：`创建一个计数器`
2. 点击"🗑️ 清除应用"
3. 生成第二个应用：`创建一个待办事项`
4. 点击"🗑️ 清除应用"
5. 生成第三个应用：`创建一个财务追踪器`
6. 点击右上角"📚 历史记录 (3)"
7. ✅ 应该看到 3 个历史记录，最新的在最上面

### 测试 2：切换应用
1. 在历史记录侧边栏中点击第二个应用（待办事项）
2. ✅ 侧边栏自动关闭
3. ✅ Sandpack 预览显示待办事项应用
4. ✅ Prompt 输入框显示对应的 prompt

### 测试 3：重命名应用
1. 打开历史记录侧边栏
2. 双击第一个应用的名称
3. 输入新名称：`我的计数器 v1`
4. 按 Enter 保存
5. ✅ 名称应该更新
6. 刷新浏览器页面
7. ✅ 新名称应该保持

### 测试 4：删除应用
1. 打开历史记录侧边栏
2. 点击某个应用右上角的 🗑️ 按钮
3. 确认删除
4. ✅ 该应用应该从列表中消失
5. ✅ 历史记录计数减 1

### 测试 5：超过 10 个应用
1. 连续生成 12 个不同的应用
2. 打开历史记录侧边栏
3. ✅ 应该只显示最新的 10 个
4. ✅ 最旧的 2 个应该被自动删除

### 测试 6：localStorage 验证
打开 Console，执行：
```javascript
// 查看历史记录
const history = JSON.parse(localStorage.getItem('vibecodingplatform_history'))
console.log('历史记录数量:', history.length)
console.log('应用名称:', history.map(h => h.name))

// 查看总大小
const currentApp = localStorage.getItem('vibecodingplatform_current_app')
const historyData = localStorage.getItem('vibecodingplatform_history')
const totalSize = (currentApp.length + historyData.length) / 1024
console.log('总大小:', totalSize.toFixed(2), 'KB')
```

## 交互细节

### 侧边栏
- **打开**：点击右上角"📚 历史记录 (N)"按钮
- **关闭**：点击侧边栏右上角 [✕] 或点击历史记录卡片（自动关闭）
- **背景色**：浅灰色 (#f8fafc)
- **宽度**：320px
- **滚动**：内容超出时可滚动

### 历史记录卡片
- **点击**：恢复应用
- **双击名称**：进入编辑模式
- **Hover**：显示阴影效果
- **删除按钮**：点击后弹出确认，阻止卡片点击事件

### 应用命名
- **编辑模式**：输入框自动 focus
- **保存**：Enter 键或失焦（blur）
- **取消**：不支持（失焦即保存）

## 性能考虑

### 容量限制
- **单个应用**：~10-50KB（HTML代码）
- **10 个应用**：~100-500KB
- **localStorage 限制**：5-10MB
- **结论**：完全够用，不会超出限制

### 加载性能
- 页面加载时一次性读取历史记录
- 使用 `useEffect` 避免重复加载
- 历史记录更新时立即保存

## 已知限制

1. **最多 10 个应用**：超出时自动删除最旧的
2. **仅限当前浏览器**：不同浏览器/设备无法同步
3. **无搜索功能**：应用较多时需手动查找
4. **无分类功能**：所有应用在同一列表中

这些限制将在 Phase 5C（Supabase 集成）或后续阶段中解决。

## 后续优化方向

### Phase 5C 或更高阶段
- **搜索功能**：根据应用名称/prompt 搜索
- **分类/标签**：给应用打标签（工具、游戏、展示等）
- **缩略图**：显示应用预览截图
- **导出/导入**：导出为 JSON，分享给他人
- **云端同步**：使用 Supabase 实现跨设备同步

## 文件变更

### `client/src/App.jsx`
**新增 State**：
- `history` - 历史记录数组
- `showHistory` - 侧边栏显示状态
- `editingNameId` - 正在编辑的应用ID
- `editingName` - 编辑中的名称

**新增常量**：
- `HISTORY_KEY` - localStorage 键名
- `MAX_HISTORY` - 最大保存数量（10）

**新增函数**：
- `extractAppName()` - 提取应用名称
- `addToHistory()` - 添加到历史
- `loadFromHistory()` - 加载历史应用
- `deleteHistoryItem()` - 删除历史
- `renameHistoryItem()` - 重命名

**更新函数**：
- `handleGenerate()` - 添加到历史记录
- `handleImprove()` - 更新历史记录
- `useEffect()` - 加载历史记录

**UI 更新**：
- 新增历史记录侧边栏
- 新增历史记录按钮
- 调整布局为 flex 容器

## 总结

Phase 5B 实现了完整的多应用历史管理功能，用户可以方便地在多个应用之间切换，大大提升了工作效率。结合 Phase 5A 的自动保存功能，平台的用户体验已经达到了一个新的高度。

下一步（Phase 5C）将引入 Supabase 云端存储，实现跨设备同步和应用分享功能。

