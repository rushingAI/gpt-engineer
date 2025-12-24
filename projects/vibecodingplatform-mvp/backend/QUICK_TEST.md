# 快速测试回滚功能

## 🎯 目的

测试 self_heal_loop 的回滚机制（best_snapshot 功能）

## ⚡ 最简单的方法

由于测试脚本需要导入项目依赖，最简单的方法是**在后端服务运行时**，使用 Python REPL 运行测试：

### 步骤 1: 确保后端正在运行

```bash
cd projects/vibecodingplatform-mvp/backend
./run.sh
```

### 步骤 2: 在另一个终端运行测试

```bash
cd projects/vibecodingplatform-mvp/backend
python3 test_self_heal_rollback.py
```

## 📊 预期输出

你应该看到 3 个测试场景的输出：

### 场景 1: Hard Regression
```
================================================================================
测试场景 1: Hard Regression (error 增加)
================================================================================

初始状态: 3 errors, 2 warnings
预期: 第1轮治愈改进 → 第2轮引入 regression → 触发回滚

   🔧 迭代 1/3: 开始修复...
     📌 更新 best_snapshot: X errors, Y total
   
   🔧 迭代 2/3: 开始修复...
     ⚠️  hard regression: X → Z errors
     ↓ max_files 收紧到 1

✅ 回滚功能已触发！
```

### 场景 2: Soft Regression  
类似输出，但会显示 "soft regression (warning爆炸)"

### 场景 3: Continuous Regression
连续两轮 regression，最终输出 best_snapshot

## ✅ 验证清单

运行完成后，检查输出中是否包含：

- [ ] **Hard Regression**: 看到 `regression=True (hard)`
- [ ] **Soft Regression**: 看到 `regression=True (soft)`
- [ ] **Continuous Regression**: 看到 "连续 regression" 和 "输出 best_snapshot"
- [ ] **回滚触发**: 看到 `⚠️ regression` 和 `↓ max_files 收紧到 1`

## 🐛 故障排查

### 错误: ModuleNotFoundError

确保后端依赖已安装：

```bash
cd projects/vibecodingplatform-mvp/backend
pip3 install -r requirements.txt
```

### 错误: 测试崩溃

查看完整的 traceback，可能是：
1. `run_quality_gates()` 无法解析代码
2. `count_errors()` 统计错误
3. MockAI 返回的代码格式问题

### 测试没有输出预期的 regression

检查 `healing_history` 中的 `error_count` 值是否正确递增/递减。

## 📝 阅读详细文档

完整的测试说明在: `TEST_ROLLBACK_README.md`

