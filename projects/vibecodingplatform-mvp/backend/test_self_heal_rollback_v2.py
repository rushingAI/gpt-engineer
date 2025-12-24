#!/usr/bin/env python3
"""
测试 self_heal_loop 的回滚功能 - v2 (修复版)
使用正确的文件类型 (.tsx) 和模式 (obj.field.method()) 来触发 missing_null_check
"""

import sys
import os
import json
from typing import Dict, Any, List

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
            if self.call_count == 1:
                # 第1轮：修复2个，保留1个 error
                content = """src/components/generated/TestComponent.tsx
```
export function TestComponent() {
  const state = getState();
  if (state && state.data) {
    // 修复了2个，但保留1个 error
    const items = state.items.map(x => x);  // error: state.items.map()
    return <div>{items.length}</div>;
  }
  return null;
}

function getState() { return null; }
```

vibe.meta.json
```
{"dependencies": {}, "quality_gates": {}}
```"""
            else:
                # 第2轮：引入3个新 error (regression: 1 → 3)
                content = """src/components/generated/TestComponent.tsx
```
export function TestComponent() {
  const state = getState();
  const items = state.data.map(x => x);  // error 1
  
  const users = getUsers();
  const names = users.list.map(u => u.name);  // error 2
  
  const config = getConfig();
  const count = config.settings.length;  // error 3
  
  return <div>{items.length + names.length + count}</div>;
}

function getState() { return null; }
function getUsers() { return null; }
function getConfig() { return null; }
```"""
        
        elif self.scenario == "soft_regression":
            if self.call_count == 1:
                # 第1轮：修复部分，保留1个 error
                content = """src/components/generated/ProcessComponent.tsx
```
export function ProcessComponent({ input }: any) {
  if (!input) return null;
  
  const config = getConfig();
  const theme = config.data.length;  // error: config.data.length
  return <div>{theme}</div>;
}

function getConfig() { return null; }
```"""
            else:
                # 第2轮：error 不变，但引入大量 warning (soft regression)
                content = """src/lib/generated/processLogic.ts
```
export function process1() { return { a: 1, common: 'x' }; }
export function process2() { return { b: 2, common: 'x' }; }
export function process3() { return { c: 3, common: 'x' }; }
export function process4() { return { d: 4, common: 'x' }; }
export function process5() { return { e: 5, common: 'x' }; }
export function process6() { return { f: 6, common: 'x' }; }
export function process7() { return { g: 7, common: 'x' }; }
export function process8() { return { h: 8, common: 'x' }; }
export function process9() { return { i: 9, common: 'x' }; }
export function process10() { return { j: 10, common: 'x' }; }
export function process11() { return { k: 11, common: 'x' }; }
export function process12() { return { l: 12, common: 'x' }; }
export function process13() { return { m: 13 }; }
```

src/components/generated/ProcessComponent.tsx
```
export function ProcessComponent({ input }: any) {
  if (!input) return null;
  
  const config = getConfig();
  const theme = config.data.length;  // 保留1个 error
  return <div>{theme}</div>;
}

function getConfig() { return null; }
```"""
        
        elif self.scenario == "continuous_regression":
            if self.call_count == 1:
                # 第1轮：修复部分，保留1个 error
                content = """src/components/generated/TestComponent.tsx
```
export function TestComponent() {
  const data = getData();
  if (data && data.value) {
    console.log(data.value);  // 这个修复了
  }
  
  const items = getItems();
  const total = items.data.length;  // error: items.data.length
  return <div>{total}</div>;
}

function getData() { return null; }
function getItems() { return null; }
```"""
            else:
                # 第2轮：引入3个 error (regression: 1 → 3)
                content = """src/components/generated/TestComponent.tsx
```
export function TestComponent() {
  const state = getState();
  const items = state.data.map(x => x);  // error 1
  
  const users = getUsers();
  const names = users.list.length;  // error 2
  
  const config = getConfig();
  const count = config.settings.push(1);  // error 3
  
  return <div>{items.length + names + count}</div>;
}

function getState() { return null; }
function getUsers() { return null; }
function getConfig() { return null; }
```"""
        
        else:  # success
            content = """src/components/generated/TestComponent.tsx
```
export function TestComponent() {
  const value = getValue();
  if (value) {
    return <div>{value}</div>;
  }
  return null;
}

function getValue() { return 'test'; }
```"""
        
        return [MockMessage(content)]


def create_mock_gate_result(error_count: int, warning_count: int = 0) -> Dict[str, GateResult]:
    """创建模拟的 gate_results"""
    issues = []
    
    for i in range(error_count):
        issues.append({
            'rule_id': 'missing_null_check',
            'severity': 'error',
            'file': f'src/components/generated/test_{i}.tsx',
            'line': 10 + i,
            'message': f'缺少空值检查 #{i}',
            'priority': 2
        })
    
    for i in range(warning_count):
        issues.append({
            'rule_id': 'data_contract_violation',
            'severity': 'warning',
            'file': f'src/lib/generated/test_{i}.ts',
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
    
    initial_files = {
        'vibe.meta.json': '{"dependencies": {}, "quality_gates": {}}',
        'src/components/generated/TestComponent.tsx': '''export function TestComponent() {
  const state = getState();
  const items = state.data.map(x => x);  // error 1
  
  const users = getUsers();
  const names = users.list.length;  // error 2
  
  const config = getConfig();
  const count = config.settings.push(1);  // error 3
  
  return <div>{items.length + names + count}</div>;
}

function getState() { return null; }
function getUsers() { return null; }
function getConfig() { return null; }
'''
    }
    
    initial_gate_results = create_mock_gate_result(error_count=3, warning_count=2)
    
    print("\n初始状态: 3 errors, 2 warnings")
    print("预期: 第1轮改进(3→1) → 第2轮 regression(1→3) → 触发回滚")
    
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
    
    if 'vibe.meta.json' in final_files:
        meta = json.loads(final_files['vibe.meta.json'])
        history = meta.get('quality_gates', {}).get('healing_history', [])
        
        print(f"\n治愈历史:")
        for record in history:
            print(f"  迭代 {record['iteration']}: "
                  f"{record['error_count']} errors, "
                  f"{record['total_count']} total, "
                  f"regression={record['regression']} ({record['regression_type']})")
        
        if len(history) >= 2 and history[1]['regression']:
            print("\n✅ 回滚功能已触发！")
        else:
            print("\n⚠️ 警告: 未检测到 regression")


def test_soft_regression():
    """测试场景2: Soft Regression - warning 爆炸"""
    print("\n" + "="*80)
    print("测试场景 2: Soft Regression (warning 爆炸)")
    print("="*80)
    
    mock_ai = MockAI("soft_regression")
    
    initial_files = {
        'vibe.meta.json': '{"dependencies": {}, "quality_gates": {}}',
        'src/components/generated/ProcessComponent.tsx': '''export function ProcessComponent({ input }: any) {
  const data = getData();
  const value = data.field.length;  // error 1
  
  const items = getItems();
  const count = items.data.map(x => x);  // error 2
  
  return <div>{value + count.length}</div>;
}

function getData() { return null; }
function getItems() { return null; }
'''
    }
    
    initial_gate_results = create_mock_gate_result(error_count=2, warning_count=5)
    
    print("\n初始状态: 2 errors, 5 warnings")
    print("预期: 第1轮修复(2→1) → 第2轮 warning 爆炸 → 触发软回滚")
    
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
        
        if len(history) >= 2 and history[1].get('regression'):
            print("\n✅ Soft Regression 检测已触发！")


def test_continuous_regression():
    """测试场景3: 连续 Regression - 输出 best_snapshot"""
    print("\n" + "="*80)
    print("测试场景 3: 连续 Regression (输出 best_snapshot)")
    print("="*80)
    
    mock_ai = MockAI("continuous_regression")
    
    initial_files = {
        'vibe.meta.json': '{"dependencies": {}, "quality_gates": {}}',
        'src/components/generated/TestComponent.tsx': '''export function TestComponent() {
  const data = getData();
  const value = data.field.length;  // error 1
  
  const items = getItems();
  const count = items.data.push(1);  // error 2
  
  return <div>{value + count}</div>;
}

function getData() { return null; }
function getItems() { return null; }
'''
    }
    
    initial_gate_results = create_mock_gate_result(error_count=2, warning_count=3)
    
    print("\n初始状态: 2 errors, 3 warnings")
    print("预期: 第1轮改进(2→1) → 第2轮 regression(1→3) → 输出 best_snapshot")
    
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


def main():
    """运行所有测试"""
    print("="*80)
    print("自愈循环回滚功能测试 v2 (修复版)")
    print("="*80)
    print("\n使用正确的文件类型 (.tsx) 和模式 (obj.field.method())")
    print("来触发 missing_null_check 规则\n")
    
    try:
        test_hard_regression()
        test_soft_regression()
        test_continuous_regression()
        
        print("\n" + "="*80)
        print("✅ 所有测试完成！")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

