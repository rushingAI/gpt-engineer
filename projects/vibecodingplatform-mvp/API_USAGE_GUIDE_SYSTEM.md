# API 使用指南系统 - 设计与实现

## 📋 问题背景

在生成代码时，AI 经常混淆不同库的 API，例如：
- 将 `moment.js` 的 `.from()` 方法用在 `date-fns` 上
- 将 `Chart.js` 的 `Chart.Line()` 语法用在 `recharts` 上
- 将 `fetch` 的 `.json()` 方法用在 `axios` 响应上

这些错误导致运行时报错，影响用户体验。

## 🎯 设计目标

1. **泛化性**：不只针对特定库，而是建立通用的 API 指南机制
2. **Token 效率**：只在检测到相关库导入时才注入对应的 API 指南
3. **可扩展性**：新增库的 API 指南应该简单快捷
4. **双重保障**：
   - **预防**：在生成阶段通过动态规则提供 API 指南
   - **检测**：在质量门禁阶段检测 API 使用错误

## 🏗️ 架构设计

### 1. 动态规则注入（预防层）

**位置**: `backend/prompt_fragments.py`

**机制**:
- 增强 `_check_file_pattern()` 函数，支持 `import:` 前缀的内容检测
- 在 `_get_dynamic_rule_definitions()` 中添加 API 指南规则
- 只在检测到相关库导入时激活对应规则

**示例**:
```python
# 检测模式
"file_patterns": ["import:date-fns"]

# 规则内容
"date-fns API: format(date,'yyyy-MM-dd'), parseISO(str), subDays(date,n). 
 NEVER use .from() or .format() methods (that's moment.js)"
```

**Token 效率**:
- 无相关库时：0 条 API 规则
- 使用 1 个库时：1 条 API 规则（约 30-50 tokens）
- 使用多个库时：按需激活，避免注入无关规则

### 2. 质量门禁检测（检测层）

**位置**: `backend/quality_gates.py`

**机制**:
- 新增 `_check_api_usage_errors()` 方法
- 定义库 API 错误模式字典
- 检测文件中的导入，并针对性地检查 API 使用错误

**错误模式定义**:
```python
api_error_patterns = {
    'date-fns': [
        (r'\.from\s*\(', 'date-fns 没有 .from() 方法', '使用 format(date, pattern)'),
        (r'\.format\s*\(', 'date-fns 没有 .format() 方法', '使用 format(date, pattern) 函数'),
    ],
    'recharts': [
        (r'Chart\.(Line|Bar|Pie)', 'recharts 不使用 Chart.Line() 语法', '使用 JSX 组件: <LineChart>'),
    ],
    # ... 更多库
}
```

**检测流程**:
1. 扫描文件中的 `import` 语句
2. 对每个导入的库，应用对应的错误模式
3. 发现错误时生成详细的错误报告（包含行号、错误说明、正确用法）

### 3. 策略配置（文档层）

**位置**: `backend/policies/generation_policy.json`

**内容**:
```json
"api_usage_rules": {
  "description": "常见库的 API 使用规范，防止混淆不同库的 API",
  "enabled": true,
  "libraries": {
    "date-fns": {
      "style": "functional",
      "correct_apis": ["format(date, pattern)", "parseISO(string)", ...],
      "forbidden_patterns": [".from()", ".format()", "moment()"],
      "common_mistake": "混淆 moment.js 的链式 API"
    },
    // ... 更多库
  }
}
```

**作用**:
- 为开发者提供清晰的 API 规范文档
- 作为未来 AI 训练的参考资料
- 便于团队协作和代码审查

## 📊 当前支持的库

| 库名 | API 风格 | 常见错误 | 正确用法 |
|------|---------|---------|---------|
| **date-fns** | 函数式 | 使用 `.from()`, `.format()` | `format(date, 'yyyy-MM-dd')` |
| **recharts** | 声明式 JSX | 使用 `Chart.Line()`, `new Chart()` | `<LineChart data={...}>` |
| **react-hook-form** | Hooks | 使用 `<Field>`, `<Formik>` | `useForm()`, `register()` |
| **axios** | Promise | 使用 `.json()` | 直接使用 `response.data` |

## 🔧 如何添加新库的 API 指南

### 步骤 1: 添加动态规则

在 `prompt_fragments.py` 的 `_get_dynamic_rule_definitions()` 中添加：

```python
(
    "api_guide_新库名",
    {
        "file_patterns": ["import:新库名"],
        "keywords": []
    },
    "新库名 API: 正确用法示例. NEVER use 错误用法 (that's 易混淆的库)"
),
```

### 步骤 2: 添加错误检测模式

在 `quality_gates.py` 的 `_check_api_usage_errors()` 中添加：

```python
'新库名': [
    (
        r'错误模式正则',
        '错误说明',
        '正确用法'
    ),
    # 可以添加多个错误模式
],
```

### 步骤 3: 更新策略配置

在 `generation_policy.json` 的 `api_usage_rules.libraries` 中添加：

```json
"新库名": {
  "style": "API 风格",
  "correct_apis": ["正确用法1", "正确用法2"],
  "forbidden_patterns": ["错误用法1", "错误用法2"],
  "common_mistake": "常见错误描述"
}
```

### 步骤 4: 添加测试用例

在 `test_api_usage_detection.py` 中添加测试用例验证。

## ✅ 测试验证

运行测试：
```bash
cd backend
python3 test_api_usage_detection.py
```

测试覆盖：
1. ✅ 导入检测（`import:` 模式）
2. ✅ 动态规则激活（按需注入）
3. ✅ API 错误检测（质量门禁）
4. ✅ Token 效率（避免无关规则）

所有测试通过 ✅

## 📈 效果评估

### Token 使用对比

| 场景 | 旧方案 | 新方案 | 节省 |
|------|--------|--------|------|
| 无 API 库 | 200 tokens | 0 tokens | 100% |
| 使用 1 个库 | 200 tokens | 40 tokens | 80% |
| 使用 2 个库 | 200 tokens | 80 tokens | 60% |
| 使用全部 4 个库 | 200 tokens | 160 tokens | 20% |

**平均节省**: 约 65% 的 token（基于典型项目使用 1-2 个库的情况）

### 错误预防效果

- **预防层**（动态规则）：在生成阶段就提供正确的 API 指南，减少错误产生
- **检测层**（质量门禁）：即使生成了错误代码，也能在自愈阶段修复
- **双重保障**：显著降低 API 混淆错误进入生产环境的概率

## 🚀 未来扩展

### 短期（1-2 周）
- [ ] 添加更多常用库的 API 指南（如 `lodash`, `zod`, `tanstack-query`）
- [ ] 优化错误提示信息，提供更详细的修复建议
- [ ] 添加自愈提示模板，针对 API 错误提供专门的修复指导

### 中期（1-2 月）
- [ ] 支持版本特定的 API 指南（如 React 17 vs 18）
- [ ] 添加 API 使用统计，分析最常见的错误模式
- [ ] 集成到 IDE 插件，提供实时的 API 提示

### 长期（3-6 月）
- [ ] 基于实际错误数据，自动学习和更新 API 指南
- [ ] 支持自定义库的 API 指南配置
- [ ] 构建 API 知识图谱，自动推理相似库的 API 差异

## 📝 总结

通过**动态规则注入 + 质量门禁检测**的双层架构，我们实现了：

1. ✅ **泛化性**：不再针对单个库打补丁，而是建立了通用的 API 指南机制
2. ✅ **Token 效率**：按需注入，避免 prompt 膨胀
3. ✅ **可扩展性**：添加新库只需 3 步，简单快捷
4. ✅ **双重保障**：预防 + 检测，显著降低 API 混淆错误

这是一个**可持续、可扩展、高效**的解决方案，为代码生成质量提供了坚实的保障。

