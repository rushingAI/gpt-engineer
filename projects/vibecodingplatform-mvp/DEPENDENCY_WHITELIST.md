# 依赖白名单管理

## 🎯 目标

防止 AI 随意添加不安全或不必要的依赖，通过白名单审批制确保依赖的安全性和可控性。

## 🔒 实现方式

### 策略配置

在 `backend/policies/generation_policy.json` 中定义白名单：

```json
"dependency_policy": {
  "enabled": true,
  "mode": "whitelist",
  "allowed_dependencies": [
    "axios",
    "lodash",
    "date-fns",
    // ... 更多批准的依赖
  ],
  "auto_approve_patterns": [
    "@types/*"  // 自动批准所有 TypeScript 类型定义
  ]
}
```

### 前端实现

在 `client/src/utils/webcontainer.js` 中：

1. **白名单检查**：`isDependencyAllowed()` 函数
2. **JSON 验证**：`validateAndParseJSON()` 函数（防止格式错误）
3. **安全合并**：`mergePackageJson()` 函数

## 📋 当前白名单

### 允许的依赖

```javascript
const ALLOWED_DEPENDENCIES = [
  // HTTP 客户端
  'axios',
  
  // 工具库
  'lodash',
  'date-fns',
  'uuid',
  'clsx',
  
  // 状态管理
  'zustand',
  
  // 表单
  'react-hook-form',
  'zod',
  
  // 可视化
  'recharts',
  
  // 已预装（但列出来保持一致性）
  'lucide-react',
  'framer-motion',
  'react-router-dom',
  
  // 数据获取
  'react-query',
  '@tanstack/react-query'
];
```

### 自动批准模式

```javascript
const AUTO_APPROVE_PATTERNS = [
  /^@types\//  // 所有 TypeScript 类型定义包
];
```

## 🔄 工作流程

### AI 请求添加新依赖

1. **AI 生成** `package.json` 包含新依赖：
   ```json
   {
     "dependencies": {
       "axios": "^1.6.0"
     }
   }
   ```

2. **前端合并时检查**：
   - ✅ `axios` 在白名单中 → 批准
   - 🚫 `some-random-pkg` 不在白名单 → 拒绝

3. **控制台输出**：
   ```
   ✅ 批准新依赖: axios
   🚫 拒绝依赖: some-random-pkg
   ```

### 处理失败情况

#### 场景 1：AI 生成的 package.json 格式错误

```javascript
// JSON 验证失败
❌ AI package.json 解析失败: Unterminated string in JSON...
⚠️  AI package.json 无效，忽略 AI 依赖
✅ 使用预设 package.json
```

#### 场景 2：合并后 JSON 格式错误

```javascript
// 序列化失败（理论上不应该发生，但有双重检查）
❌ package.json 序列化失败: ...
✅ 使用预设 package.json
```

## 🛠️ 如何添加新依赖到白名单

### 方法 1：修改策略文件（推荐）

1. 编辑 `backend/policies/generation_policy.json`
2. 添加到 `allowed_dependencies` 数组
3. **重要**：同时更新前端白名单（见下方）

### 方法 2：同时更新前后端（必须）

#### 后端（策略）
```json
// backend/policies/generation_policy.json
"allowed_dependencies": [
  "axios",
  "new-package"  // 新增
]
```

#### 前端（实现）
```javascript
// client/src/utils/webcontainer.js
const ALLOWED_DEPENDENCIES = [
  'axios',
  'new-package'  // 新增
];
```

### 方法 3：自动同步脚本（未来优化）

创建脚本自动从策略生成前端白名单：

```bash
cd backend
node scripts/sync-dependency-whitelist.js
```

## 📊 安全优势

### 防止的风险

1. **恶意包**：阻止 AI 添加已知有漏洞的包
2. **体积膨胀**：防止不必要的大型库（如整个 `moment.js`）
3. **版本冲突**：保持预设依赖的版本稳定
4. **供应链攻击**：限制攻击面

### 示例：被阻止的危险操作

```javascript
// AI 尝试添加
{
  "dependencies": {
    "some-crypto-miner": "1.0.0",  // 🚫 不在白名单
    "outdated-vulnerable-pkg": "^2.0.0"  // 🚫 不在白名单
  }
}

// 实际结果
🚫 拒绝依赖: some-crypto-miner, outdated-vulnerable-pkg
✅ package.json 合并成功并通过验证
```

## 🔍 调试

### 查看依赖审批日志

打开浏览器开发者工具 Console：

```
📦 Total files in merged tree: 26
  ↳ Merged package.json with AI dependencies
  ✅ 批准新依赖: axios, lodash
  🚫 拒绝依赖: malicious-package
  ✅ package.json 合并成功并通过验证
```

### 测试白名单

在浏览器 Console 中：

```javascript
// 测试依赖是否允许
import { isDependencyAllowed } from './utils/webcontainer.js';

console.log(isDependencyAllowed('axios'));  // true
console.log(isDependencyAllowed('malicious'));  // false
console.log(isDependencyAllowed('@types/node'));  // true (匹配模式)
```

## 🎯 最佳实践

### 1. 定期审查白名单

每月检查：
- 是否有新的必要依赖需要添加
- 是否有过时/不再使用的依赖需要移除
- 白名单中的包是否有安全更新

### 2. 保持前后端同步

**重要**：每次修改策略文件后，必须同时更新前端白名单！

### 3. 记录审批原因

在策略文件中添加注释：

```json
"allowed_dependencies": [
  "axios",  // HTTP 客户端，常用于 API 调用
  "date-fns",  // 日期处理，比 moment.js 更轻量
  "zod"  // 表单验证，与 react-hook-form 配合
]
```

## 🚀 未来优化

### 短期
- ✅ 实现依赖白名单
- ✅ 添加 JSON 验证
- ⏳ 创建自动同步脚本

### 中期
- 🔄 UI 展示被拒绝的依赖（让用户知道）
- 🔄 用户手动批准依赖（临时允许）
- 🔄 记录依赖审批历史

### 长期
- 🔄 依赖安全扫描（集成 npm audit）
- 🔄 自动版本更新建议
- 🔄 依赖分析报告（体积、使用频率）

## 📝 常见问题

### Q: AI 为什么不能添加 XXX 依赖？

A: 因为该依赖不在白名单中。检查是否需要添加到 `allowed_dependencies`。

### Q: 如何临时允许一个依赖？

A: 当前需要修改代码。未来会提供 UI 手动批准功能。

### Q: @types/* 包会自动批准吗？

A: 是的，所有 `@types/` 开头的包都会自动批准（类型定义通常是安全的）。

### Q: 前后端白名单不一致会怎样？

A: 后端策略仅用于文档/审计，实际执行在前端。保持一致很重要。

## 📚 相关文档

- [组件化改造总结](./COMPONENT_REFACTOR_SUMMARY.md)
- [策略配置](./backend/policies/generation_policy.json)
- [WebContainer 工具](./client/src/utils/webcontainer.js)

