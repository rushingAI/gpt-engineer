"""
导入导出一致性测试 - 验证两层面的修复
"""

import sys
sys.path.insert(0, '.')

from dependency_detector import detect_dependencies_in_files, NODEJS_BUILTIN_MODULES, DEV_DEPENDENCIES
from quality_gates import L0StaticGate


def test_nodejs_builtin_filtering():
    """测试 1: Node.js 内置模块过滤"""
    print("🧪 测试 1: Node.js 内置模块过滤")
    
    code = '''
import path from 'path';
import { readFile } from 'fs';
import { URL } from 'url';
import crypto from 'crypto';
'''
    
    detected = detect_dependencies_in_files({'test.ts': code})
    
    if len(detected) == 0:
        print(f"  ✓ Node.js 内置模块被正确过滤")
        print(f"    path, fs, url, crypto 都未被检测为第三方依赖")
        return True
    else:
        print(f"  ✗ 仍检测到 {len(detected)} 个依赖: {list(detected.keys())}")
        return False


def test_dev_dependencies_filtering():
    """测试 2: 开发依赖过滤"""
    print("\n🧪 测试 2: 开发依赖过滤")
    
    code = '''
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import type { Config } from 'tailwindcss';
'''
    
    detected = detect_dependencies_in_files({'vite.config.ts': code})
    
    if len(detected) == 0:
        print(f"  ✓ 开发依赖被正确过滤")
        print(f"    vite, @vitejs/plugin-react 都未被检测")
        return True
    else:
        print(f"  ✗ 仍检测到 {len(detected)} 个依赖: {list(detected.keys())}")
        return False


def test_config_file_skipping():
    """测试 3: 配置文件跳过"""
    print("\n🧪 测试 3: 配置文件跳过")
    
    files = {
        'vite.config.ts': '''
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
''',
        'src/App.tsx': '''
import React from 'react';
import axios from 'axios';
'''
    }
    
    detected = detect_dependencies_in_files(files)
    
    # 应该只检测到 axios，vite.config.ts 中的导入应该被跳过
    if len(detected) == 1 and 'axios' in detected:
        print(f"  ✓ 配置文件被跳过")
        print(f"    只检测到 App.tsx 中的 axios")
        return True
    else:
        print(f"  ✗ 检测结果异常: {list(detected.keys())}")
        return False


def test_import_export_mismatch_detection():
    """测试 4: 导入导出不匹配检测"""
    print("\n🧪 测试 4: 导入导出不匹配检测")
    
    files = {
        'src/pages/Index.tsx': '''
import React from 'react';
import {
  computeOrderStats,
  generateMockOrders,
  type Order,
} from '@/lib/generated/dashboard-orders';

export default function Index() {
  const orders = generateMockOrders(100);
  const stats = computeOrderStats(orders);
  return <div>{stats.totalOrders}</div>;
}
''',
        'src/lib/generated/dashboard-orders.ts': '''
export type Order = {
  id: string;
  customer: string;
  total: number;
};

export function getOrders(): Order[] {
  return [];
}

export function getOrderStats(orders: Order[]) {
  return { totalOrders: orders.length };
}
'''
    }
    
    gate = L0StaticGate()
    result = gate.check(files)
    
    mismatch_errors = [
        issue for issue in result.issues 
        if issue.get('rule_id') == 'import_export_mismatch'
    ]
    
    if len(mismatch_errors) == 2:  # computeOrderStats 和 generateMockOrders
        print(f"  ✓ 检测到 2 个导入导出不匹配")
        for error in mismatch_errors:
            print(f"    - {error['message']}")
        return True
    else:
        print(f"  ✗ 检测到 {len(mismatch_errors)} 个错误（期望 2 个）")
        return False


def test_similar_export_suggestion():
    """测试 5: 相似导出建议"""
    print("\n🧪 测试 5: 相似导出建议")
    
    files = {
        'src/pages/Index.tsx': '''
import { computeOrderStats } from '@/lib/generated/stats';
''',
        'src/lib/generated/stats.ts': '''
export function getOrderStats() {
  return {};
}
'''
    }
    
    gate = L0StaticGate()
    result = gate.check(files)
    
    mismatch_errors = [
        issue for issue in result.issues 
        if issue.get('rule_id') == 'import_export_mismatch'
    ]
    
    if len(mismatch_errors) > 0:
        error = mismatch_errors[0]
        has_suggestion = 'getOrderStats' in error.get('suggestion', '')
        
        if has_suggestion:
            print(f"  ✓ 提供了相似导出建议")
            print(f"    建议: {error['suggestion'][:100]}...")
            return True
        else:
            print(f"  ✗ 未提供相似导出建议: {error['suggestion']}")
            return False
    else:
        print(f"  ✗ 未检测到不匹配（应该检测到）")
        return False


def test_correct_import_export():
    """测试 6: 正确的导入导出（不应报错）"""
    print("\n🧪 测试 6: 正确的导入导出")
    
    files = {
        'src/pages/Index.tsx': '''
import { getOrders, getOrderStats } from '@/lib/generated/orders';
''',
        'src/lib/generated/orders.ts': '''
export function getOrders() {
  return [];
}

export function getOrderStats() {
  return {};
}
'''
    }
    
    gate = L0StaticGate()
    result = gate.check(files)
    
    mismatch_errors = [
        issue for issue in result.issues 
        if issue.get('rule_id') == 'import_export_mismatch'
    ]
    
    if len(mismatch_errors) == 0:
        print(f"  ✓ 正确的导入导出不会报错")
        return True
    else:
        print(f"  ✗ 误报了 {len(mismatch_errors)} 个错误")
        return False


def main():
    """运行所有测试"""
    print("=" * 70)
    print("导入导出一致性测试")
    print("=" * 70)
    
    tests = [
        test_nodejs_builtin_filtering,
        test_dev_dependencies_filtering,
        test_config_file_skipping,
        test_import_export_mismatch_detection,
        test_similar_export_suggestion,
        test_correct_import_export,
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
        print("\n🎉 所有测试通过！两层面修复都工作正常。")
        print("\n💡 修复效果:")
        print(f"  ✓ 层面1: Node.js 内置模块 ({len(NODEJS_BUILTIN_MODULES)} 个) 和开发依赖 ({len(DEV_DEPENDENCIES)} 个) 正确过滤")
        print(f"  ✓ 层面2: 导入导出不匹配能正确检测并提供修复建议")
        return 0
    else:
        print(f"\n⚠️  有 {total_count - passed_count} 个测试失败，请检查。")
        return 1


if __name__ == '__main__':
    exit(main())

