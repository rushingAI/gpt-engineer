"""
依赖注入完整性测试 - 确保依赖检测、仲裁、注入流程端到端正常工作
"""

import sys
import json
sys.path.insert(0, '.')

from dependency_detector import detect_imports_in_code, detect_dependencies_in_files, KNOWN_PACKAGES
from dependency_arbiter import arbiter, DEPENDENCY_WHITELIST
from quality_gates import L0StaticGate


def test_whitelist_sync():
    """测试白名单同步"""
    print("🧪 测试 1: 白名单同步")
    
    known_set = set(KNOWN_PACKAGES.keys())
    whitelist_set = set(DEPENDENCY_WHITELIST.keys())
    
    only_in_known = known_set - whitelist_set
    only_in_whitelist = whitelist_set - known_set
    
    if only_in_known or only_in_whitelist:
        print(f"  ✗ 白名单不同步:")
        if only_in_known:
            print(f"    - 只在 KNOWN_PACKAGES: {only_in_known}")
        if only_in_whitelist:
            print(f"    - 只在 WHITELIST: {only_in_whitelist}")
        return False
    
    # 检查版本一致
    for pkg in known_set & whitelist_set:
        if KNOWN_PACKAGES[pkg] != DEPENDENCY_WHITELIST[pkg]:
            print(f"  ✗ 版本不一致: {pkg}")
            print(f"    KNOWN: {KNOWN_PACKAGES[pkg]}")
            print(f"    WHITELIST: {DEPENDENCY_WHITELIST[pkg]}")
            return False
    
    print("  ✓ 白名单完全同步")
    return True


def test_dependency_detection():
    """测试依赖检测"""
    print("\n🧪 测试 2: 依赖检测")
    
    test_cases = [
        {
            'name': 'recharts 导入',
            'code': 'import { LineChart } from "recharts";',
            'expected': {'recharts'}
        },
        {
            'name': 'date-fns 导入',
            'code': 'import { format } from "date-fns";',
            'expected': {'date-fns'}
        },
        {
            'name': 'scoped package',
            'code': 'import { Button } from "@mui/material";',
            'expected': {'@mui/material'}
        },
        {
            'name': '相对路径（应忽略）',
            'code': 'import { Button } from "@/components/ui/button";',
            'expected': set()
        },
        {
            'name': '预设依赖（应忽略）',
            'code': 'import React from "react";',
            'expected': {'react'}  # 会检测到但不会添加到 missing_deps
        }
    ]
    
    all_passed = True
    for test in test_cases:
        imports = detect_imports_in_code(test['code'])
        if imports == test['expected']:
            print(f"  ✓ {test['name']}")
        else:
            print(f"  ✗ {test['name']}")
            print(f"    期望: {test['expected']}")
            print(f"    实际: {imports}")
            all_passed = False
    
    return all_passed


def test_arbitration():
    """测试依赖仲裁"""
    print("\n🧪 测试 3: 依赖仲裁")
    
    test_cases = [
        {
            'name': '白名单依赖（应批准）',
            'requested': {'recharts': '^2.10.0'},
            'should_approve': True
        },
        {
            'name': '黑名单依赖（应拒绝）',
            'requested': {'jquery': '^3.6.0'},
            'should_approve': False
        },
        {
            'name': '未知依赖（应拒绝）',
            'requested': {'unknown-package': '^1.0.0'},
            'should_approve': False
        },
        {
            'name': '预设依赖（应跳过）',
            'requested': {'react': '^18.0.0'},
            'should_approve': False  # 会被跳过，不在 approved 中
        }
    ]
    
    all_passed = True
    for test in test_cases:
        approved, rejected, warnings = arbiter.arbitrate(test['requested'])
        
        pkg_name = list(test['requested'].keys())[0]
        is_approved = pkg_name in approved
        
        if is_approved == test['should_approve']:
            print(f"  ✓ {test['name']}")
        else:
            print(f"  ✗ {test['name']}")
            print(f"    期望批准: {test['should_approve']}")
            print(f"    实际批准: {is_approved}")
            print(f"    approved: {approved}")
            print(f"    rejected: {rejected}")
            all_passed = False
    
    return all_passed


def test_end_to_end():
    """端到端测试：从代码到 vibe.meta.json"""
    print("\n🧪 测试 4: 端到端流程")
    
    # 模拟生成的代码
    files = {
        'src/components/Chart.tsx': '''
import React from 'react';
import { LineChart, Line } from 'recharts';
import { format } from 'date-fns';
import { Button } from '@/components/ui/button';

export const Chart = () => {
    return <LineChart />;
};
''',
        'src/pages/Index.tsx': '''
import React from 'react';
import { Chart } from '@/components/Chart';

export default function Index() {
    return <div><Chart /></div>;
}
'''
    }
    
    # 步骤 1: 检测依赖
    requested_deps = detect_dependencies_in_files(files)
    print(f"  1️⃣ 检测到依赖: {list(requested_deps.keys())}")
    
    if not requested_deps:
        print("  ✗ 应该检测到 recharts 和 date-fns")
        return False
    
    # 步骤 2: 仲裁
    approved_deps, rejected_deps, warnings = arbiter.arbitrate(requested_deps)
    print(f"  2️⃣ 批准依赖: {list(approved_deps.keys())}")
    
    if not approved_deps:
        print("  ✗ 应该批准依赖")
        return False
    
    # 步骤 3: 生成 vibe.meta.json
    vibe_meta = {
        "dependencies": arbiter.create_dependency_report(
            requested_deps,
            approved_deps,
            rejected_deps
        )
    }
    
    files['vibe.meta.json'] = json.dumps(vibe_meta, indent=2)
    print(f"  3️⃣ 生成 vibe.meta.json")
    
    # 步骤 4: 运行质量门禁验证
    gate = L0StaticGate()
    result = gate.check(files)
    
    # 检查是否有依赖相关的错误
    dep_errors = [
        issue for issue in result.issues 
        if issue.get('rule_id') in ['unapproved_dependency_used', 'missing_vibe_meta', 'missing_dependencies_field']
        and issue.get('severity') == 'error'
    ]
    
    if dep_errors:
        print(f"  ✗ 质量门禁检测到依赖问题:")
        for err in dep_errors:
            print(f"    - {err['message']}")
        return False
    
    print(f"  4️⃣ 质量门禁通过")
    print("  ✓ 端到端流程正常")
    return True


def test_missing_dependency_detection():
    """测试缺失依赖检测"""
    print("\n🧪 测试 5: 缺失依赖检测")
    
    # 模拟使用了依赖但未在 vibe.meta.json 中声明
    files = {
        'src/App.tsx': '''
import React from 'react';
import { LineChart } from 'recharts';

export const App = () => <LineChart />;
''',
        'vibe.meta.json': json.dumps({
            "dependencies": {
                "requested": {},
                "approved": {},  # 空的！
                "rejected": {}
            }
        })
    }
    
    gate = L0StaticGate()
    result = gate.check(files)
    
    # 应该检测到 unapproved_dependency_used 错误
    unapproved_errors = [
        issue for issue in result.issues 
        if issue.get('rule_id') == 'unapproved_dependency_used'
    ]
    
    if unapproved_errors:
        print(f"  ✓ 正确检测到未批准的依赖: {len(unapproved_errors)} 个")
        return True
    else:
        print(f"  ✗ 未检测到缺失依赖问题")
        return False


def main():
    """运行所有测试"""
    print("=" * 60)
    print("依赖注入完整性测试")
    print("=" * 60)
    
    tests = [
        test_whitelist_sync,
        test_dependency_detection,
        test_arbitration,
        test_end_to_end,
        test_missing_dependency_detection
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
        print("\n🎉 所有测试通过！依赖注入流程完整无误。")
        return 0
    else:
        print(f"\n⚠️  有 {total_count - passed_count} 个测试失败，请检查。")
        return 1


if __name__ == '__main__':
    exit(main())

