#!/usr/bin/env python3
"""
测试 self_heal_loop 的回滚功能
模拟 regression 场景，验证 best_snapshot 回滚机制

用法:
    cd projects/vibecodingplatform-mvp/backend
    python test_self_heal_rollback.py
"""

import sys
import os
import json
from typing import Dict, Any, List

# 确保可以导入 backend 模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from quality_gates import GateResult
from self_heal import self_heal_loop


class MockAI:
    """模拟 AI，可控制地引入 regression"""
    
    def __init__(self, scenario: str):
        self.scenario = scenario
        self.call_count = 0
        
    def next(self, messages, step_name: str = ""):
        """模拟 AI 返回，根据场景返回不同的代码"""
        self.call_count += 1
        
        class MockMessage:
            def __init__(self, content):
                self.content = content
        
        if self.scenario == "hard_regression":
            # 场景1: Hard Regression - 第2轮引入更多 error
            if self.call_count == 1:
                # 第1轮：只修复部分 error，保留 1 个 error（强制进入第2轮）
                content = """src/lib/generated/test.tsx
```
export function test() {
  const value = getValue();
  if (value) {
    console.log(value);
  }
  
  // 故意保留一个 error，确保进入第2轮（使用两层嵌套触发 missing_null_check）
  const state = getState();
  const items = state.data.map(x => x);  // 缺少 null check: state.data.map()
  return items;
}

function getValue() {
  return 'test';
}

function getState() {
  return null;
}
```

vibe.meta.json
```
{"dependencies": {}, "quality_gates": {}}
```"""
            else:
                # 第2轮：引入新的 error（故意写错）
                content = """src/lib/generated/test.ts
```
export function test() {
  const value = getValue();
  console.log(value);
  
  // 故意引入新的 null check error
  const data = getUserData();
  const names = data.map(u => u.name);  // 缺少 null check
  
  const items = getItems();
  const total = items.reduce((a, b) => a + b, 0);  // 又一个 null check error
}

function getValue() {
  return 'test';
}

function getUserData() {
  return null;
}

function getItems() {
  return undefined;
}
```"""
        
        elif self.scenario == "soft_regression":
            # 场景2: Soft Regression - 第2轮引入大量 warning
            if self.call_count == 1:
                # 第1轮：只修复部分 error，保留 1 个
                content = """src/lib/generated/test.ts
```
export function processData(input: any) {
  if (!input) return null;
  
  // 故意保留一个 error，确保进入第2轮
  const config = getConfig();
  return { value: input, theme: config.theme };  // 缺少 null check
}

function getConfig() {
  return null;
}
```"""
            else:
                # 第2轮：引入大量 data_contract_violation warning (不一致的返回字段)
                content = """src/lib/generated/test.ts
```
export function processData(input: any) {
  if (input.type === 'a') return { a: 1, common: 'x' };
  if (input.type === 'b') return { b: 2, common: 'x' };
  if (input.type === 'c') return { c: 3, common: 'x' };
  if (input.type === 'd') return { d: 4, common: 'x' };
  if (input.type === 'e') return { e: 5, common: 'x' };
  if (input.type === 'f') return { f: 6, common: 'x' };
  if (input.type === 'g') return { g: 7, common: 'x' };
  if (input.type === 'h') return { h: 8, common: 'x' };
  if (input.type === 'i') return { i: 9, common: 'x' };
  if (input.type === 'j') return { j: 10, common: 'x' };
  if (input.type === 'k') return { k: 11, common: 'x' };
  if (input.type === 'l') return { l: 12, common: 'x' };
  return { default: 0 };
}
```"""
        
        elif self.scenario == "continuous_regression":
            # 场景3: 连续 Regression - 两轮都失败（改进但仍有问题）
            if self.call_count == 1:
                # 第1轮：修复部分问题，但仍保留 1 个 error（确保进入第2轮）
                content = """src/lib/generated/test.ts
```
export function test() {
  const data = getData();
  if (data) {
    const value = data.value;  // 修复了原来的 error
    console.log(value);
  }
  
  // 保留 1 个 error，确保进入第2轮
  const items = getItems();
  const total = items.length;  // error: items 可能为 null
  return total;
}

function getData() { return null; }
function getItems() { return null; }
```"""
            else:
                # 第2轮：引入 3 个新 error（regression！比第1轮的 1 个更多）
                content = """src/lib/generated/test.ts
```
export function test() {
  const data = getData();
  if (data) {
    const value = data.value;
    console.log(value);
  }
  
  // 故意引入 3 个新的 null check error（regression）
  const items = getItems();
  const total = items.length;  // error 1
  
  const users = getUsers();
  const names = users.map(u => u.name);  // error 2
  
  const config = getConfig();
  return config.theme;  // error 3
}

function getData() { return null; }
function getItems() { return null; }
function getUsers() { return null; }
function getConfig() { return null; }
```"""
        
        else:  # success
            content = """src/lib/generated/test.ts
```
export function test() {
  const value = getValue();
  if (value) {
    console.log(value);
  }
}

function getValue() {
  return 'test';
}
```"""
        
        return [MockMessage(content)]


def create_mock_gate_result(error_count: int, warning_count: int = 0) -> Dict[str, GateResult]:
    """创建模拟的 gate_results"""
    issues = []
    
    # 添加 error
    for i in range(error_count):
        issues.append({
            'rule_id': 'missing_null_check',
            'severity': 'error',
            'file': f'src/test_{i}.tsx',
            'line': 10 + i,
            'message': f'缺少空值检查 #{i}',
            'priority': 2
        })
    
    # 添加 warning
    for i in range(warning_count):
        issues.append({
            'rule_id': 'data_contract_violation',
            'severity': 'warning',
            'file': f'src/test_{i}.tsx',
            'line': 20 + i,
            'message': f'数据契约不一致 #{i}',
            'priority': 5
        })
    
    passed = error_count == 0
    return {
        'L0_static': GateResult('L0_static', passed, issues)
    }


def test_hard_regression():
    """测试场景1: Hard Regression - error 增加"""
    print("\n" + "="*80)
    print("测试场景 1: Hard Regression (error 增加)")
    print("="*80)
    
    mock_ai = MockAI("hard_regression")
    
    # 初始状态：3 个 error (缺少 null check)
    initial_files = {
        'vibe.meta.json': '{"dependencies": {}, "quality_gates": {}}',  # 添加必需文件
        'src/lib/generated/test.ts': '''export function test() {
  const data = getUsers();
  const names = data.map(u => u.name);  // error 1: data 可能为 null
  
  const items = getItems();
  const total = items.length;  // error 2: items 可能为 undefined
  
  const config = getConfig();
  return config.theme;  // error 3: config 可能为 null
}

function getUsers() { return null; }
function getItems() { return undefined; }
function getConfig() { return null; }
'''
    }
    
    initial_gate_results = create_mock_gate_result(error_count=3, warning_count=2)
    
    print("\n初始状态: 3 errors, 2 warnings")
    print("预期: 第1轮治愈改进 → 第2轮引入 regression → 触发回滚")
    
    # 执行自愈
    final_files, success, iterations = self_heal_loop(
        mock_ai,
        initial_files,
        initial_gate_results,
        interaction_spec=None
    )
    
    print(f"\n结果:")
    print(f"  - 成功: {success}")
    print(f"  - 迭代次数: {iterations}")
    print(f"  - AI 调用次数: {mock_ai.call_count}")
    
    # 读取 healing_history
    if 'vibe.meta.json' in final_files:
        meta = json.loads(final_files['vibe.meta.json'])
        history = meta.get('quality_gates', {}).get('healing_history', [])
        
        print(f"\n治愈历史:")
        for record in history:
            print(f"  迭代 {record['iteration']}: "
                  f"{record['error_count']} errors, "
                  f"{record['total_count']} total, "
                  f"regression={record['regression']} ({record['regression_type']})")
        
        # 验证回滚
        if len(history) >= 2:
            if history[1]['regression']:
                print("\n✅ 回滚功能已触发！")
            else:
                print("\n❌ 警告: 应该检测到 regression，但未触发")
    else:
        print("\n❌ 警告: 未找到 vibe.meta.json")


def test_soft_regression():
    """测试场景2: Soft Regression - warning 爆炸"""
    print("\n" + "="*80)
    print("测试场景 2: Soft Regression (warning 爆炸)")
    print("="*80)
    
    mock_ai = MockAI("soft_regression")
    
    initial_files = {
        'vibe.meta.json': '{"dependencies": {}, "quality_gates": {}}',  # 添加必需文件
        'src/lib/generated/test.ts': '''export function processData(input: any) {
  const data = getData();
  return data.value;  // error 1: data 可能为 null
}

function getData() { return null; }
'''
    }
    
    initial_gate_results = create_mock_gate_result(error_count=2, warning_count=5)
    
    print("\n初始状态: 2 errors, 5 warnings")
    print("预期: 第1轮修复 error → 第2轮 warning 爆炸 → 触发软回滚")
    
    final_files, success, iterations = self_heal_loop(
        mock_ai,
        initial_files,
        initial_gate_results,
        interaction_spec=None
    )
    
    print(f"\n结果:")
    print(f"  - 成功: {success}")
    print(f"  - 迭代次数: {iterations}")
    
    if 'vibe.meta.json' in final_files:
        meta = json.loads(final_files['vibe.meta.json'])
        history = meta.get('quality_gates', {}).get('healing_history', [])
        
        print(f"\n治愈历史:")
        for record in history:
            print(f"  迭代 {record['iteration']}: "
                  f"{record['error_count']} errors, "
                  f"{record['total_count']} total, "
                  f"regression={record['regression']} ({record['regression_type']})")
        
        if len(history) >= 2:
            if history[1].get('regression'):
                print("\n✅ Soft Regression 检测已触发！")


def test_continuous_regression():
    """测试场景3: 连续 Regression - 输出 best_snapshot"""
    print("\n" + "="*80)
    print("测试场景 3: 连续 Regression (输出 best_snapshot)")
    print("="*80)
    
    mock_ai = MockAI("continuous_regression")
    
    initial_files = {
        'vibe.meta.json': '{"dependencies": {}, "quality_gates": {}}',  # 添加必需文件
        'src/lib/generated/test.ts': '''export function test() {
  const data = getData();
  return data.value;  // error 1: data 可能为 null
  
  const items = getItems();
  return items.length;  // error 2: items 可能为 undefined
}

function getData() { return null; }
function getItems() { return undefined; }
'''
    }
    
    initial_gate_results = create_mock_gate_result(error_count=2, warning_count=3)
    
    print("\n初始状态: 2 errors, 3 warnings")
    print("预期: 第1轮 regression → 第2轮 regression → 输出 best_snapshot (初始状态)")
    
    final_files, success, iterations = self_heal_loop(
        mock_ai,
        initial_files,
        initial_gate_results,
        interaction_spec=None
    )
    
    print(f"\n结果:")
    print(f"  - 成功: {success}")
    print(f"  - 迭代次数: {iterations}")
    
    if 'vibe.meta.json' in final_files:
        meta = json.loads(final_files['vibe.meta.json'])
        history = meta.get('quality_gates', {}).get('healing_history', [])
        
        print(f"\n治愈历史:")
        for record in history:
            print(f"  迭代 {record['iteration']}: "
                  f"{record['error_count']} errors, "
                  f"{record['total_count']} total, "
                  f"regression={record['regression']} ({record['regression_type']})")
        
        regression_count = sum(1 for r in history if r.get('regression'))
        if regression_count >= 2:
            print(f"\n✅ 连续 regression 检测到 {regression_count} 次！")
            print("✅ 应该已输出 best_snapshot")


def main():
    """运行所有测试"""
    print("="*80)
    print("自愈循环回滚功能测试")
    print("="*80)
    print("\n这个脚本会模拟 3 种 regression 场景:")
    print("  1. Hard Regression: error 数量增加")
    print("  2. Soft Regression: warning 爆炸式增长")
    print("  3. Continuous Regression: 连续两轮 regression")
    
    try:
        # 测试1: Hard Regression
        test_hard_regression()
        
        # 测试2: Soft Regression
        test_soft_regression()
        
        # 测试3: Continuous Regression
        test_continuous_regression()
        
        print("\n" + "="*80)
        print("✅ 所有测试完成！")
        print("="*80)
        print("\n请检查上述输出，确认:")
        print("  1. regression 标志是否正确设置")
        print("  2. regression_type 是否准确 (hard/soft/none)")
        print("  3. 回滚逻辑是否触发")
        print("  4. best_snapshot 是否在连续 regression 时输出")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

