"""
API 使用错误检测测试 - 验证动态规则和质量门禁能正确检测 API 混淆
"""

import sys
import json
sys.path.insert(0, '.')

from prompt_fragments import build_dynamic_rules, _check_file_pattern
from quality_gates import L0StaticGate


def test_file_pattern_import_detection():
    """测试文件模式检测是否支持导入检测"""
    print("🧪 测试 1: 导入检测")
    
    test_cases = [
        {
            'name': 'date-fns 导入检测',
            'files': {
                'src/App.tsx': 'import { format } from "date-fns";'
            },
            'pattern': 'import:date-fns',
            'should_match': True
        },
        {
            'name': 'recharts 导入检测',
            'files': {
                'src/Chart.tsx': 'import { LineChart } from "recharts";'
            },
            'pattern': 'import:recharts',
            'should_match': True
        },
        {
            'name': '未导入的库',
            'files': {
                'src/App.tsx': 'import React from "react";'
            },
            'pattern': 'import:date-fns',
            'should_match': False
        },
        {
            'name': '文件名模式（原有功能）',
            'files': {
                'src/components/generated/MyComponent.tsx': 'export const MyComponent = () => {}'
            },
            'pattern': 'src/components/generated/',
            'should_match': True
        }
    ]
    
    all_passed = True
    for test in test_cases:
        result = _check_file_pattern(test['files'], test['pattern'])
        if result == test['should_match']:
            print(f"  ✓ {test['name']}")
        else:
            print(f"  ✗ {test['name']}")
            print(f"    期望: {test['should_match']}, 实际: {result}")
            all_passed = False
    
    return all_passed


def test_dynamic_rules_activation():
    """测试动态规则是否在检测到导入时激活"""
    print("\n🧪 测试 2: 动态规则激活")
    
    test_cases = [
        {
            'name': 'date-fns 规则激活',
            'context': {
                'files': {
                    'src/App.tsx': 'import { format } from "date-fns";'
                },
                'prompt_text': '',
                'gate_results': {}
            },
            'expected_rules': ['api_guide_date_fns']
        },
        {
            'name': 'recharts 规则激活',
            'context': {
                'files': {
                    'src/Chart.tsx': 'import { LineChart } from "recharts";'
                },
                'prompt_text': '',
                'gate_results': {}
            },
            'expected_rules': ['api_guide_recharts']
        },
        {
            'name': '多个 API 规则同时激活',
            'context': {
                'files': {
                    'src/App.tsx': '''
import { format } from "date-fns";
import { LineChart } from "recharts";
import axios from "axios";
'''
                },
                'prompt_text': '',
                'gate_results': {}
            },
            'expected_rules': ['api_guide_date_fns', 'api_guide_recharts', 'api_guide_axios']
        },
        {
            'name': '无相关导入时不激活',
            'context': {
                'files': {
                    'src/App.tsx': 'import React from "react";'
                },
                'prompt_text': '',
                'gate_results': {}
            },
            'expected_rules': []
        }
    ]
    
    all_passed = True
    for test in test_cases:
        rules_text, activated_rules = build_dynamic_rules(test['context'])
        
        # 检查期望的规则是否都被激活
        all_expected_activated = all(rule in activated_rules for rule in test['expected_rules'])
        # 检查是否有多余的 API 规则被激活
        api_rules_activated = [r for r in activated_rules if r.startswith('api_guide_')]
        no_extra_api_rules = all(rule in test['expected_rules'] for rule in api_rules_activated)
        
        if all_expected_activated and no_extra_api_rules:
            print(f"  ✓ {test['name']}")
            if test['expected_rules']:
                print(f"    激活的 API 规则: {', '.join(api_rules_activated)}")
        else:
            print(f"  ✗ {test['name']}")
            print(f"    期望激活: {test['expected_rules']}")
            print(f"    实际激活: {api_rules_activated}")
            all_passed = False
    
    return all_passed


def test_api_error_detection():
    """测试质量门禁是否能检测 API 使用错误"""
    print("\n🧪 测试 3: API 错误检测")
    
    test_cases = [
        {
            'name': 'date-fns .from() 错误',
            'files': {
                'src/App.tsx': '''
import { format } from "date-fns";

const date = someDate.from(now);  // 错误！
'''
            },
            'should_detect_error': True,
            'error_rule': 'api_usage_error'
        },
        {
            'name': 'date-fns 正确使用',
            'files': {
                'src/App.tsx': '''
import { format, subDays } from "date-fns";

const formatted = format(new Date(), 'yyyy-MM-dd');
const pastDate = subDays(new Date(), 7);
'''
            },
            'should_detect_error': False
        },
        {
            'name': 'recharts Chart.Line() 错误',
            'files': {
                'src/Chart.tsx': '''
import { LineChart } from "recharts";

const chart = Chart.Line(data);  // 错误！
'''
            },
            'should_detect_error': True,
            'error_rule': 'api_usage_error'
        },
        {
            'name': 'recharts 正确使用',
            'files': {
                'src/Chart.tsx': '''
import { LineChart, Line } from "recharts";

const MyChart = () => (
  <LineChart data={data}>
    <Line dataKey="value" />
  </LineChart>
);
'''
            },
            'should_detect_error': False
        },
        {
            'name': 'axios .json() 错误',
            'files': {
                'src/Api.tsx': '''
import axios from "axios";

const data = await response.json();  // 错误！应该用 response.data
'''
            },
            'should_detect_error': True,
            'error_rule': 'api_usage_error'
        }
    ]
    
    gate = L0StaticGate()
    all_passed = True
    
    for test in test_cases:
        result = gate.check(test['files'])
        api_errors = [
            issue for issue in result.issues 
            if issue.get('rule_id') == 'api_usage_error'
        ]
        
        has_error = len(api_errors) > 0
        
        if has_error == test['should_detect_error']:
            print(f"  ✓ {test['name']}")
            if api_errors:
                print(f"    检测到: {api_errors[0]['message']}")
        else:
            print(f"  ✗ {test['name']}")
            print(f"    期望检测错误: {test['should_detect_error']}")
            print(f"    实际检测到: {has_error}")
            if api_errors:
                print(f"    错误: {api_errors[0]['message']}")
            all_passed = False
    
    return all_passed


def test_token_efficiency():
    """测试 token 效率 - 确保只在需要时注入规则"""
    print("\n🧪 测试 4: Token 效率")
    
    # 场景 1: 无 API 库导入
    context_no_api = {
        'files': {
            'src/App.tsx': '''
import React from "react";
import { Button } from "@/components/ui/button";

export default function App() {
  return <Button>Click me</Button>;
}
'''
        },
        'prompt_text': '',
        'gate_results': {}
    }
    
    rules_no_api, activated_no_api = build_dynamic_rules(context_no_api)
    api_rules_no_api = [r for r in activated_no_api if r.startswith('api_guide_')]
    
    # 场景 2: 使用 date-fns
    context_with_datefns = {
        'files': {
            'src/App.tsx': '''
import React from "react";
import { format } from "date-fns";

export default function App() {
  const date = format(new Date(), 'yyyy-MM-dd');
  return <div>{date}</div>;
}
'''
        },
        'prompt_text': '',
        'gate_results': {}
    }
    
    rules_with_datefns, activated_with_datefns = build_dynamic_rules(context_with_datefns)
    api_rules_with_datefns = [r for r in activated_with_datefns if r.startswith('api_guide_')]
    
    print(f"  无 API 库时激活的 API 规则: {len(api_rules_no_api)} 个")
    print(f"  使用 date-fns 时激活的 API 规则: {len(api_rules_with_datefns)} 个")
    print(f"  Token 节省: 只在需要时注入，避免 {4 - len(api_rules_with_datefns)} 条无关规则")
    
    # 验证：无 API 库时不应该激活任何 API 规则
    # 使用 date-fns 时只应该激活 date-fns 规则
    passed = (
        len(api_rules_no_api) == 0 and
        len(api_rules_with_datefns) == 1 and
        'api_guide_date_fns' in api_rules_with_datefns
    )
    
    if passed:
        print(f"  ✓ Token 效率优化成功")
    else:
        print(f"  ✗ Token 效率有问题")
    
    return passed


def main():
    """运行所有测试"""
    print("=" * 60)
    print("API 使用错误检测测试")
    print("=" * 60)
    
    tests = [
        test_file_pattern_import_detection,
        test_dynamic_rules_activation,
        test_api_error_detection,
        test_token_efficiency
    ]
    
    results = []
    for test in tests:
        try:
            passed = test()
            results.append((test.__name__, passed))
        except Exception as e:
            print(f"  ✗ 测试异常: {e}")
            import traceback
            traceback.print_exc()
            results.append((test.__name__, False))
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n总计: {passed_count}/{total_count} 通过")
    
    if passed_count == total_count:
        print("\n🎉 所有测试通过！API 使用错误检测系统工作正常。")
        return 0
    else:
        print(f"\n⚠️  有 {total_count - passed_count} 个测试失败，请检查。")
        return 1


if __name__ == '__main__':
    exit(main())

