# Build Report 功能测试指南

## 🔧 修复的 Bug

### Bug 1: server.py 的 NoneType 错误
**位置**: `backend/server.py` 第 1259 行  
**问题**: `report.get('telemetry', {})` 可能返回 `None`，导致链式调用 `.get()` 报错  
**修复**: 添加了安全检查，确保 telemetry 是 dict 类型再访问

---

## 📋 测试步骤

### 前置条件
✅ 后端服务运行中（Terminal 27，端口 8000）  
✅ 前端服务运行中（Terminal 25，Vite dev server）

### 测试 1: 基础生成流程（验收标准 1-3）

1. **打开浏览器**
   ```
   http://localhost:5173
   ```

2. **输入测试 prompt**
   ```
   创建一个简单的计数器应用，有加减按钮
   ```

3. **观察控制台输出**
   应该看到：
   ```
   🎯 Build Report initialized (runId: xxxxxxxx)
   ✅ 监控脚本已注入到 index.html (runId: xxxxxxxx)
   ✅ APP_READY 调用已注入到 src/main.tsx (runId: xxxxxxxx)
   📊 Telemetry loaded: xxxxxx
   🚦 L0 gates loaded: pass/fail
   ```

4. **等待生成完成**
   - install 阶段完成
   - dev server 启动
   - 首屏渲染

5. **检查报告保存**
   ```bash
   ls -la debug记录/ | grep build_report
   ```
   应该看到类似：
   ```
   build_report_20251223_143052_abc123_12345678.json
   ```

### 测试 2: 多次运行隔离（验收标准 2）

1. **连续生成 3 次**（使用相同 prompt）
   
2. **检查 debug记录 文件夹**
   ```bash
   ls -la debug记录/build_report_*.json
   ```
   应该有 3 个文件，runId 都不同

3. **验证 runId 隔离**
   ```bash
   # 查看最新的 3 个报告
   ls -t debug记录/build_report_*.json | head -3 | xargs -I {} sh -c 'echo "File: {}"; cat {} | jq ".runId"'
   ```
   每个 runId 应该都不同

### 测试 3: 错误场景（验收标准 3）

#### 测试 3.1: Install 失败

1. **修改 package.json 添加不存在的依赖**（临时测试）
   - 在前端修改生成逻辑，或
   - 手动在 vibe.meta.json 中添加错误依赖

2. **观察 report**
   ```bash
   cat debug记录/build_report_*.json | jq '.phases.install'
   ```
   应该显示：
   ```json
   {
     "status": "fail",
     "exitCode": 1,
     "logTail": "... npm ERR! ..."
   }
   ```

#### 测试 3.2: Dev 启动超时

1. **在 cyberpunkPreset.js 中引入语法错误**（临时测试）

2. **观察 report**
   ```bash
   cat debug记录/build_report_*.json | jq '.phases.dev'
   ```
   应该显示：
   ```json
   {
     "status": "timeout" 或 "fail",
     "logTail": "... error message ..."
   }
   ```

### 测试 4: 报告内容完整性（验收标准 4-5）

1. **查看最新报告的完整结构**
   ```bash
   cat $(ls -t debug记录/build_report_*.json | head -1) | jq '.'
   ```

2. **验证必需字段**
   ```bash
   # 检查 telemetry
   cat $(ls -t debug记录/build_report_*.json | head -1) | jq '.telemetry'
   
   # 检查 l0
   cat $(ls -t debug记录/build_report_*.json | head -1) | jq '.l0'
   
   # 检查 qualityGates
   cat $(ls -t debug记录/build_report_*.json | head -1) | jq '.qualityGates'
   
   # 检查 phases
   cat $(ls -t debug记录/build_report_*.json | head -1) | jq '.phases'
   
   # 检查 errors（验证降噪是否生效）
   cat $(ls -t debug记录/build_report_*.json | head -1) | jq '.errors'
   ```

3. **验证降噪效果**
   - `errors.console.total` 应该远小于实际日志行数
   - `errors.classified` 中各类别应该合理分布

---

## 🐛 已知潜在问题

### 问题 1: 首屏渲染检测
**现象**: `render.status` 可能显示 `timeout`  
**原因**: 
- React 入口未正确调用 `window.__APP_READY__()`
- 8 秒超时时间过短

**排查**:
```bash
# 检查注入的监控代码是否存在
cat $(ls -t debug记录/build_report_*.json | head -1) | jq '.phases.render'
```

**临时解决**: 增加 `RENDER_TIMEOUT_MS` 到 15000（15秒）

### 问题 2: Console errors 为空
**现象**: `errors.console.total === 0`  
**原因**: 
- 监控脚本未正确注入
- iframe 的 sandbox 属性阻止了 postMessage

**排查**:
```javascript
// 在浏览器控制台中检查
window.frames[0].__VIBE_RUN_ID__  // 应该显示当前 runId
window.frames[0].__APP_READY__    // 应该是一个函数
```

### 问题 3: Telemetry/L0 为 null
**现象**: report 中 telemetry/l0 字段为 null  
**原因**: 
- vibe.meta.json 未生成
- 读取 vibe.meta.json 失败

**排查**:
```bash
# 查看 WebContainer 控制台输出
# 应该有 "📊 Telemetry loaded" 日志
```

---

## 📊 成功标准

✅ **文件生成**: `debug记录/` 下有 `build_report_*.json` 文件  
✅ **文件名格式**: `build_report_{timestamp}_{promptHash6}_{runId8}.json`  
✅ **runId 隔离**: 多次运行的 runId 不同  
✅ **Phases 记录**: install/dev/render 三个阶段都有记录  
✅ **Telemetry 完整**: 包含 mode, prompt_hash, policy_version 等  
✅ **L0 结果**: 包含 status, issues 等  
✅ **错误分类**: 5 类错误统计正确（INSTALL/DEPENDENCY/BUILD/EXPORT/RUNTIME）  
✅ **降噪生效**: console.total 不会包含大量非错误日志

---

## 🔍 调试技巧

### 查看实时日志
```bash
# 后端日志
tail -f /Users/gaochang/.cursor/projects/Users-gaochang-gpt-engineer/terminals/27.txt

# 浏览器控制台
# F12 -> Console -> 搜索 "Build Report" 或 "📊"
```

### 快速查看最新报告
```bash
# 查看最新报告的摘要
cat $(ls -t debug记录/build_report_*.json | head -1) | jq '{
  runId: .runId,
  phases: .phases | map_values(.status),
  errors: .errors.classified,
  telemetry: {mode: .telemetry.mode, hash: .telemetry.prompt_hash[:8]}
}'
```

### 对比多次运行
```bash
# 对比最近 3 次运行的 runId 和 phases
for file in $(ls -t debug记录/build_report_*.json | head -3); do
  echo "=== $file ==="
  cat "$file" | jq '{runId: .runId[:8], phases: .phases | map_values(.status)}'
done
```

---

## 📝 测试检查清单

- [ ] 后端服务运行正常（端口 8000）
- [ ] 前端服务运行正常（端口 5173）
- [ ] 基础生成流程完成，生成 build_report
- [ ] 文件名格式正确（包含 timestamp, promptHash6, runId8）
- [ ] 多次运行 runId 不同
- [ ] install 阶段记录正确
- [ ] dev 阶段记录正确
- [ ] render 阶段记录正确（收到 APP_RENDERED）
- [ ] telemetry 字段完整
- [ ] l0 字段完整
- [ ] errors.classified 统计正确
- [ ] console errors 降噪生效（total 不虚高）

