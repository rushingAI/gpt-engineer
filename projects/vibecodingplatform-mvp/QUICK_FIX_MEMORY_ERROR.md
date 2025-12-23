# 🚨 WebAssembly 内存错误 - 快速解决指南

## 错误信息
```
Uncaught (in promise) RangeError: WebAssembly.instantiate(): 
Out of memory: Cannot allocate Wasm memory for new instance
```

## 💡 快速解决方案（按优先级）

### ⚡ 立即尝试（30秒内）

1. **关闭其他浏览器标签页** 📑
   - 特别是 YouTube、Netflix 等视频网站
   - 大型网页应用（Gmail、Google Docs 等）

2. **点击"刷新页面重试"按钮** 🔄
   - 或按 `Ctrl+R` (Windows) / `Cmd+R` (Mac)

3. **点击"强制清理重试"按钮** 🧹
   - 在错误页面上会出现这个按钮
   - 会自动清理并重新加载

### 🔧 进阶方案（1-2分钟）

4. **完全重启浏览器** 🔄
   ```
   1. 完全关闭浏览器（所有窗口）
   2. 等待 5 秒
   3. 重新打开浏览器
   4. 只打开我们的应用页面
   ```

5. **使用无痕/隐私模式** 🕵️
   - Chrome: `Ctrl+Shift+N` (Windows) / `Cmd+Shift+N` (Mac)
   - Firefox: `Ctrl+Shift+P` (Windows) / `Cmd+Shift+P` (Mac)
   - 这会禁用扩展，释放更多内存

### 🛠️ 深度清理（5分钟）

6. **清理浏览器缓存** 🗑️
   ```
   Chrome/Edge:
   1. 按 Ctrl+Shift+Delete (Windows) 或 Cmd+Shift+Delete (Mac)
   2. 选择"时间范围" → "全部"
   3. 只勾选"缓存的图片和文件"
   4. 点击"清除数据"
   ```

7. **禁用浏览器扩展** 🔌
   ```
   Chrome:
   1. 打开 chrome://extensions/
   2. 暂时关闭所有扩展
   3. 重新加载我们的应用
   
   常见占内存的扩展：
   - 广告拦截器（AdBlock、uBlock）
   - 代理/VPN 扩展
   - 开发者工具扩展
   ```

## 🎯 推荐配置

### 浏览器版本
✅ Chrome 89+ （**推荐**）  
✅ Microsoft Edge 89+  
✅ Firefox 91+  
⚠️ Safari 15.2+ （部分支持）  
❌ 移动浏览器（不支持）

### 系统要求
- **内存**: 最少 8GB RAM（推荐 16GB）
- **操作系统**: Windows 10+, macOS 10.15+, Linux
- **可用内存**: 至少 2GB 空闲内存

## 🔍 检查内存使用情况

### 方法 1: Chrome 任务管理器
```
1. 按 Shift+Esc 打开 Chrome 任务管理器
2. 查看各个标签页的内存使用
3. 关闭占用内存最多的标签页
```

### 方法 2: 浏览器控制台
```javascript
// 在控制台（F12）中运行：
if (performance.memory) {
  const used = (performance.memory.usedJSHeapSize / 1024 / 1024).toFixed(0)
  const limit = (performance.memory.jsHeapSizeLimit / 1024 / 1024).toFixed(0)
  console.log(`内存使用: ${used}MB / ${limit}MB`)
}
```

## ❓ 常见问题

### Q1: 为什么会出现这个错误？
WebContainer 需要在浏览器中运行完整的 Node.js 环境，这需要大量内存（约 500MB-1GB）。如果浏览器已经占用太多内存，就无法为 WebContainer 分配空间。

### Q2: 我已经尝试了所有方法，还是不行怎么办？
- 检查系统可用内存（至少需要 2GB 空闲）
- 重启电脑释放所有内存
- 升级浏览器到最新版本
- 如果使用虚拟机，增加分配给虚拟机的内存

### Q3: 这是代码的 bug 吗？
不是。这是浏览器 WebAssembly 的内存限制导致的。我们已经优化了代码：
- ✅ 添加了自动重试机制
- ✅ 优化了 npm install 参数
- ✅ 限制了日志输出大小
- ✅ 添加了内存监控

### Q4: 生产环境也会有这个问题吗？
不会。生产环境会使用静态构建，不需要 WebContainer。

## 📞 仍需帮助？

如果以上方法都不能解决问题：

1. **记录以下信息**:
   - 浏览器版本和操作系统
   - 系统总内存和可用内存
   - 打开了哪些其他标签页
   - 完整的错误信息（控制台截图）

2. **联系技术支持** 或 **提交 GitHub Issue**

## 🎬 视频教程

查看详细的视频教程：[如何解决 WebAssembly 内存错误](链接待添加)

---

💡 **小贴士**: 为了获得最佳体验，建议：
- 使用最新版 Chrome 浏览器
- 确保系统有至少 8GB 内存
- 开发时只打开必要的标签页
- 定期重启浏览器

✨ **已应用的优化**: 代码已经更新，包含自动重试和内存优化。刷新页面即可使用最新版本。

