# 自愈循环回滚功能测试指南

## 测试目的

验证 `self_heal_loop` 的回滚机制在以下场景下是否正常工作：
1. **Hard Regression**: error 数量增加
2. **Soft Regression**: warning 爆炸式增长
3. **Continuous Regression**: 连续两轮 regression，输出 best_snapshot

## 运行测试

### 方法 1: 直接运行

```bash
cd projects/vibecodingplatform-mvp/backend
python test_self_heal_rollback.py
```

### 方法 2: 使用 Python 模块方式

```bash
cd projects/vibecodingplatform-mvp
python -m backend.test_self_heal_rollback
```

## 测试场景说明

### 场景 1: Hard Regression (error 增加)

**初始状态**: 3 个 `missing_null_check` error  
**第1轮治愈**: MockAI 修复成功，减少到 1 个 error  
**第2轮治愈**: MockAI 故意引入更多 error，增加到 3 个  
**预期行为**:
- ✅ 检测到 `regression: true`, `regression_type: "hard"`
- ✅ 回滚到第1轮的状态 (1 error)
- ✅ `max_files_this_iteration` 收紧到 1

### 场景 2: Soft Regression (warning 爆炸)

**初始状态**: 2 error, 5 warning  
**第1轮治愈**: 修复所有 error，剩余 5 warning  
**第2轮治愈**: 引入大量 `data_contract_violation` warning (>15 个)  
**预期行为**:
- ✅ 检测到 `regression: true`, `regression_type: "soft"`
- ✅ 回滚到第1轮的状态 (0 error, 5 warning)

### 场景 3: Continuous Regression (连续回退)

**初始状态**: 2 error  
**第1轮治愈**: 引入 3 个 error (regression #1)  
**第2轮治愈**: 引入 4 个 error (regression #2)  
**预期行为**:
- ✅ 第1轮检测到 regression，回滚
- ✅ 第2轮再次检测到 regression
- ✅ `regression_count >= 2`，输出 best_snapshot (初始状态)
- ✅ 终止治愈循环

## 验证检查清单

运行测试后，检查输出中的以下关键点：

### ✅ 回滚触发检查
- [ ] 场景1: 第2轮显示 `regression=True (hard)`
- [ ] 场景2: 第2轮显示 `regression=True (soft)`
- [ ] 场景3: 连续两轮都显示 `regression=True`

### ✅ 状态恢复检查
- [ ] 场景1: 回滚后 error_count 恢复到第1轮的值
- [ ] 场景2: 回滚后 total_count 没有爆炸
- [ ] 场景3: 最终输出的是 best_snapshot (初始状态)

### ✅ 策略调整检查
- [ ] 回滚后打印 "max_files 收紧到 1"
- [ ] 连续 regression 后打印 "输出 best_snapshot"

## 输出示例

正常的输出应该类似：

```
================================================================================
测试场景 1: Hard Regression (error 增加)
================================================================================

初始状态: 3 errors, 2 warnings
预期: 第1轮治愈改进 → 第2轮引入 regression → 触发回滚

   🔧 迭代 1/3: 开始修复...
     📌 更新 best_snapshot: 1 errors, 3 total
   
   🔧 迭代 2/3: 开始修复...
     ⚠️  hard regression: 1 → 3 errors
     ↓ max_files 收紧到 1

结果:
  - 成功: False
  - 迭代次数: 3
  - AI 调用次数: 2

治愈历史:
  迭代 1: 1 errors, 3 total, regression=False (none)
  迭代 2: 3 errors, 5 total, regression=True (hard)

✅ 回滚功能已触发！
```

## 故障排查

### 如果 regression 未触发

1. 检查 `count_errors()` 函数是否正确统计 error
2. 检查 `run_quality_gates()` 是否正确解析 MockAI 返回的代码
3. 查看 `healing_history` 中的 `error_count` 是否正确

### 如果测试崩溃

1. 确保所有依赖模块都可以导入（`quality_gates`, `self_heal`）
2. 检查 Python 版本 (建议 3.8+)
3. 查看完整的 traceback 错误信息

## 修改测试场景

如果需要自定义测试场景，修改 `MockAI` 类中的逻辑：

```python
class MockAI:
    def next(self, messages, step_name: str = ""):
        if self.scenario == "my_custom_scenario":
            if self.call_count == 1:
                # 第1轮返回的代码
                content = """..."""
            else:
                # 第2轮返回的代码（引入 regression）
                content = """..."""
        ...
```

然后在 `main()` 中添加新的测试函数。

## 注意事项

1. 这个测试脚本使用 MockAI，不会真正调用 LLM API
2. 测试会调用真实的 `run_quality_gates()`，会执行实际的门禁检查
3. 测试完成后会在当前目录生成 `vibe.meta.json`（可以删除）
4. 测试不会修改任何生产代码，可以安全运行

