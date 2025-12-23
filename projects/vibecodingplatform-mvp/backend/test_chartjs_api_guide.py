"""
测试 react-chartjs-2 API 指导的激活和效果
"""

import sys
sys.path.insert(0, '.')

from prompt_fragments import build_dynamic_rules


def test_chartjs_guide_activation():
    """测试当检测到 react-chartjs-2 导入时，API指导是否被激活"""
    print("=" * 70)
    print("测试：react-chartjs-2 API 指导激活机制")
    print("=" * 70)
    
    # 模拟使用 react-chartjs-2 的代码
    files = {
        'src/components/generated/dashboard/OrdersChart.tsx': '''
import React from 'react';
import { Line } from 'react-chartjs-2';

export const OrdersChart = ({ data }: any) => {
  return <Line data={data} />;
};
'''
    }
    
    # 构建动态规则
    context = {
        'prompt_text': "Create a dashboard with charts",
        'files': files,
        'gate_results': {}  # 空字典而不是None
    }
    dynamic_rules, activated_ids = build_dynamic_rules(context)
    
    # 检查是否激活了 react-chartjs-2 指导
    if 'api_guide_react_chartjs' in activated_ids:
        print("\n✅ 测试通过：成功检测到 react-chartjs-2 导入")
        print(f"✅ 激活的规则 ID: {activated_ids}")
        
        # 检查指导内容是否包含关键信息
        key_points = [
            'ChartJS.register',
            'CategoryScale',
            'chart.js',
            'import { Chart as ChartJS',
            'not a registered scale'
        ]
        
        missing_points = []
        for point in key_points:
            if point not in dynamic_rules:
                missing_points.append(point)
        
        if missing_points:
            print(f"\n⚠️  警告：指导内容缺少关键点：{missing_points}")
            return False
        else:
            print("\n✅ 指导内容包含所有关键点：")
            print("  - ChartJS.register() 注册机制")
            print("  - CategoryScale 等组件导入")
            print("  - chart.js 导入说明")
            print("  - 常见错误提示")
            
            print("\n📋 完整的指导内容：")
            print("-" * 70)
            print(dynamic_rules)
            print("-" * 70)
            return True
    else:
        print(f"\n❌ 测试失败：未激活 react-chartjs-2 指导")
        print(f"激活的规则: {activated_ids}")
        return False


def test_recharts_not_trigger_chartjs_guide():
    """测试使用 recharts 时不应该触发 react-chartjs-2 指导"""
    print("\n" + "=" * 70)
    print("测试：recharts 不应触发 react-chartjs-2 指导")
    print("=" * 70)
    
    files = {
        'src/components/Chart.tsx': '''
import React from 'react';
import { LineChart, Line } from 'recharts';

export const Chart = () => <LineChart><Line /></LineChart>;
'''
    }
    
    context = {
        'prompt_text': "Create a chart",
        'files': files,
        'gate_results': {}
    }
    dynamic_rules, activated_ids = build_dynamic_rules(context)
    
    # recharts 应该触发 api_guide_recharts，但不应触发 api_guide_react_chartjs
    if 'api_guide_react_chartjs' not in activated_ids:
        print("\n✅ 测试通过：recharts 不会误触发 react-chartjs-2 指导")
        
        if 'api_guide_recharts' in activated_ids:
            print("✅ 正确激活了 recharts 指导")
        
        return True
    else:
        print("\n❌ 测试失败：recharts 误触发了 react-chartjs-2 指导")
        return False


def test_no_chart_library():
    """测试没有使用图表库时不应触发任何图表指导"""
    print("\n" + "=" * 70)
    print("测试：无图表库时不应触发图表指导")
    print("=" * 70)
    
    files = {
        'src/components/Button.tsx': '''
import React from 'react';

export const Button = () => <button>Click</button>;
'''
    }
    
    context = {
        'prompt_text': "Create a button",
        'files': files,
        'gate_results': {}
    }
    dynamic_rules, activated_ids = build_dynamic_rules(context)
    
    chart_guides = [
        'api_guide_react_chartjs',
        'api_guide_recharts'
    ]
    
    triggered_chart_guides = [g for g in chart_guides if g in activated_ids]
    
    if not triggered_chart_guides:
        print("\n✅ 测试通过：没有误触发图表库指导")
        return True
    else:
        print(f"\n❌ 测试失败：误触发了图表指导：{triggered_chart_guides}")
        return False


def test_real_world_scenario():
    """测试真实场景：用户报告的问题代码"""
    print("\n" + "=" * 70)
    print("测试：真实场景 - 用户报告的 OrdersChart 代码")
    print("=" * 70)
    
    # 模拟用户报告的出错代码
    files = {
        'src/components/generated/dashboard/OrdersChart.tsx': '''
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

export const OrdersChart = ({ data }: any) => {
  return <Line data={data} />;
};
'''
    }
    
    context = {
        'prompt_text': "Dashboard with order trends",
        'files': files,
        'gate_results': {}
    }
    dynamic_rules, activated_ids = build_dynamic_rules(context)
    
    if 'api_guide_react_chartjs' in activated_ids:
        print("\n✅ 真实场景测试通过：能够检测到问题代码")
        print("✅ 会向AI注入修复指导，告诉它需要添加 ChartJS.register()")
        
        # 检查指导是否提到注册
        if 'ChartJS.register' in dynamic_rules:
            print("✅ 指导中包含了 ChartJS.register() 的说明")
            return True
        else:
            print("❌ 指导中缺少 ChartJS.register() 的说明")
            return False
    else:
        print("\n❌ 真实场景测试失败：未能检测到问题代码")
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("react-chartjs-2 API 指导 - 完整测试套件")
    print("=" * 70)
    
    tests = [
        ("API指导激活机制", test_chartjs_guide_activation),
        ("recharts不误触发", test_recharts_not_trigger_chartjs_guide),
        ("无图表库不触发", test_no_chart_library),
        ("真实场景验证", test_real_world_scenario),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ 测试异常: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    print("\n" + "=" * 70)
    print("测试结果汇总")
    print("=" * 70)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n总计: {passed_count}/{total_count} 通过")
    
    if passed_count == total_count:
        print("\n🎉 所有测试通过！")
        print("\n✨ react-chartjs-2 API 指导已正确配置")
        print("   当AI使用 react-chartjs-2 时，会自动收到：")
        print("   ✅ ChartJS.register() 的完整步骤")
        print("   ✅ 正确的导入方式")
        print("   ✅ 常见错误提示")
        print("   ✅ 推荐使用 recharts 的提示")
        return 0
    else:
        print(f"\n⚠️  有 {total_count - passed_count} 个测试失败")
        return 1


if __name__ == '__main__':
    exit(main())

