# WebAssembly 内存不足问题解决方案

## 问题描述

在启动开发服务器时，浏览器控制台显示以下错误：

```
Uncaught (in promise) RangeError: WebAssembly.instantiate(): 
Out of memory: Cannot allocate Wasm memory for new instance
```

## 根本原因

这个错误通常发生在以下情况：

1. **浏览器内存不足** - 其他标签页或进程占用了太多内存
2. **WebContainer 实例未正确清理** - 多个实例同时存在导致内存泄漏
3. **npm install 过程消耗大量内存** - 依赖安装时的内存峰值过高
4. **WebAssembly 内存限制** - 浏览器对单个 WebAssembly 实例的内存分配有限制

## 已实施的解决方案

### 1. 增强的错误处理和重试机制

**文件：** `client/src/components/preview/WebContainerPreview.jsx`

- 添加了内存错误检测
- 实现了自动清理和重试逻辑
- 在首次启动失败时，会自动清理资源并重试一次

```javascript
// 如果是内存错误，尝试清理并重试一次
if (bootError.message && bootError.message.includes('memory')) {
  console.warn('⚠️ 检测到内存错误，尝试清理并重试...')
  await webContainerManager.teardown()
  
  // 强制垃圾回收（如果可用）
  if (window.gc) {
    window.gc()
  }
  
  // 等待一小段时间让内存释放
  await new Promise(resolve => setTimeout(resolve, 1000))
  
  // 重试一次
  container = await webContainerManager.getContainer()
}
```

### 2. 优化 npm install 过程

**文件：** `client/src/components/preview/WebContainerPreview.jsx`

- 使用 `--prefer-offline` 优先使用缓存
- 使用 `--no-audit` 跳过安全审计，减少内存占用
- 使用 `--progress=false` 禁用进度条，减少输出
- 限制输出日志大小，防止内存溢出

```javascript
const installProcess = await container.spawn('npm', [
  'install',
  '--prefer-offline',
  '--no-audit',
  '--progress=false'
])
```

### 3. 增强的内存监控

**文件：** `client/src/utils/webcontainer.js`

- 在启动前检查内存使用情况
- 提供更友好的错误信息
- 自动识别内存相关错误

```javascript
if (performance.memory) {
  const memoryInfo = performance.memory
  const usedPercent = (memoryInfo.usedJSHeapSize / memoryInfo.jsHeapSizeLimit) * 100
  console.log(`📊 内存使用情况: ${usedPercent.toFixed(1)}%`)
  
  if (usedPercent > 90) {
    console.warn('⚠️  内存使用率过高，可能影响 WebContainer 启动')
  }
}
```

### 4. 改进的用户界面

**文件：** `client/src/components/preview/WebContainerPreview.jsx`

- 针对内存错误显示详细的解决方案
- 提供"强制清理重试"按钮
- 显示技术说明帮助用户理解问题

## 用户解决方案

### 立即解决方法

1. **关闭其他浏览器标签页**
   - 特别是视频、大型网页应用等占用内存的页面
   
2. **刷新页面**
   - 点击浏览器刷新按钮
   - 或使用页面上的"刷新页面重试"按钮

3. **使用"强制清理重试"按钮**
   - 在错误提示页面点击此按钮
   - 会自动清理 WebContainer 实例后重新加载

### 长期解决方法

1. **重启浏览器**
   - 完全关闭浏览器（不只是关闭标签）
   - 重新打开浏览器

2. **使用推荐的浏览器**
   - Chrome 89+ （推荐）
   - Edge 89+
   - Firefox 91+
   - Safari 15.2+

3. **增加系统可用内存**
   - 关闭不必要的应用程序
   - 建议系统至少有 8GB 内存

4. **禁用浏览器扩展**
   - 某些扩展（特别是广告拦截器、代理等）可能占用大量内存
   - 尝试在无痕模式下运行

5. **清理浏览器缓存**
   - Chrome: 设置 > 隐私和安全 > 清除浏览数据
   - 选择"缓存的图片和文件"

## 技术说明

### WebContainer 内存需求

WebContainer 是一个在浏览器中运行的完整 Node.js 环境，它需要：

- **WebAssembly 内存**：用于运行 Node.js 运行时（~50-100MB）
- **文件系统内存**：用于虚拟文件系统（取决于项目大小）
- **npm 包内存**：安装依赖时的临时内存（可能达到 200-300MB）

总计可能需要 **500MB - 1GB** 的可用内存。

### 浏览器限制

不同浏览器对 WebAssembly 的内存限制不同：

- Chrome/Edge: 约 2GB（32位）或 4GB（64位）
- Firefox: 约 2GB
- Safari: 约 1GB

如果浏览器已经使用了大量内存，可能无法为 WebContainer 分配足够的空间。

## 监控和调试

### 查看内存使用情况

在浏览器控制台执行：

```javascript
// 查看当前内存使用
if (performance.memory) {
  console.log('已使用:', (performance.memory.usedJSHeapSize / 1024 / 1024).toFixed(0) + 'MB')
  console.log('总限制:', (performance.memory.jsHeapSizeLimit / 1024 / 1024).toFixed(0) + 'MB')
  console.log('使用率:', ((performance.memory.usedJSHeapSize / performance.memory.jsHeapSizeLimit) * 100).toFixed(1) + '%')
}
```

### 强制启用垃圾回收（仅开发模式）

Chrome 需要使用特殊标志启动才能暴露 `gc()` 函数：

```bash
# macOS/Linux
chrome --js-flags="--expose-gc"

# Windows
chrome.exe --js-flags="--expose-gc"
```

然后在控制台可以手动触发垃圾回收：

```javascript
if (window.gc) {
  window.gc()
  console.log('垃圾回收已执行')
}
```

## 预防措施

### 开发建议

1. **关闭开发工具的内存分析工具**
   - Performance 面板的录制会占用额外内存

2. **限制并发打开的项目数量**
   - 每个项目都会创建一个 WebContainer 实例

3. **定期重启浏览器**
   - 长时间运行的浏览器会积累内存碎片

### 生产环境

对于生产环境部署，建议：

1. 使用静态构建而不是 WebContainer
2. 提供预览链接而不是实时容器
3. 实现服务器端渲染

## 相关资源

- [WebContainer 官方文档](https://webcontainers.io/)
- [WebAssembly 内存管理](https://developer.mozilla.org/en-US/docs/WebAssembly/Understanding_the_text_format#memory)
- [Chrome 内存管理最佳实践](https://developer.chrome.com/docs/devtools/memory-problems/)

## 更新日志

- **2024-12-18**: 
  - 添加内存错误自动重试机制
  - 优化 npm install 参数
  - 增强错误提示界面
  - 添加内存使用监控

