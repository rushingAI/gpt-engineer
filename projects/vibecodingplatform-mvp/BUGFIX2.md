# 第二次修复：Sandpack 文件格式问题

## 新问题

Sandpack 显示默认模板文件（index.js），而不是 AI 生成的文件。

## 根本原因

1. **文件名格式**：Sandpack 需要文件名以 `/` 开头（如 `/index.html`）
2. **模板选择**：`vanilla` 模板有默认文件，`static` 模板更适合纯 HTML
3. **文件过滤**：AI 可能生成了 Python 文件或其他非 Web 文件

## 修复内容

### 1. 文件名规范化
```javascript
const normalizedFilename = filename.startsWith('/') ? filename : `/${filename}`
```

### 2. 过滤非代码文件
```javascript
// 跳过 .txt, .md, README 等
if (filename.endsWith('.txt') || filename.endsWith('.md') || filename === 'README') {
  continue
}
```

### 3. 智能 index.html 处理
- 如果没有 `index.html`，查找其他 HTML 文件并重命名
- 如果只有 JS/CSS 文件，自动创建包装 HTML

### 4. 模板改为 `static`
```javascript
<Sandpack
  template="static"  // 更适合纯 HTML 应用
  // ...
/>
```

## 如何重新测试

1. **刷新浏览器**（Vite 应该已自动重载）
2. **清空之前的结果**：如果还显示旧内容，刷新页面
3. **重新生成**：输入 "创建一个计时器" 并点击生成

## 调试方法

打开浏览器开发者工具（F12），在 Console 标签中查看：
- "生成的文件:" - 显示后端返回的文件名
- "文件内容预览:" - 显示完整内容
- "转换后的文件:" - 显示传递给 Sandpack 的文件名

如果看到 Python 文件（.py），说明提示词增强没生效，需要检查。

