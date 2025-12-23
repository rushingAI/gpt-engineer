"""
测试依赖门禁 - 验证配置文件中的依赖不会被误报
"""

import sys
sys.path.insert(0, '.')

from quality_gates import L0StaticGate
import json


def test_vite_config_dependencies():
    """测试 vite.config.ts 中的依赖不会被误报"""
    print("=" * 70)
    print("测试: vite.config.ts 中的依赖不应被检测")
    print("=" * 70)
    
    files = {
        'vibe.meta.json': json.dumps({
            "dependencies": {
                "requested": {},
                "approved": {},
                "rejected": {}
            }
        }, indent=2),
        
        'vite.config.ts': '''
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import { fileURLToPath } from 'url';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
''',
        
        'src/pages/Index.tsx': '''
import React from 'react';

export default function Index() {
  return <div>Hello</div>;
}
''',
    }
    
    gate = L0StaticGate()
    result = gate.check(files)
    
    dependency_errors = [
        issue for issue in result.issues
        if 'unapproved_dependency' in issue.get('rule_id', '')
    ]
    
    print(f"\n依赖相关错误数: {len(dependency_errors)}")
    
    if dependency_errors:
        print("\n❌ 发现依赖误报:")
        for error in dependency_errors:
            print(f"  - {error['message']}")
        return False
    else:
        print("\n✅ 没有依赖误报")
        print("  vite, @vitejs/plugin-react, path, url 都被正确过滤")
        return True


def test_runtime_dependencies():
    """测试运行时依赖会被正确检测"""
    print("\n" + "=" * 70)
    print("测试: 运行时依赖应该被检测")
    print("=" * 70)
    
    files = {
        'vibe.meta.json': json.dumps({
            "dependencies": {
                "requested": {},
                "approved": {},
                "rejected": {}
            }
        }, indent=2),
        
        'src/pages/Index.tsx': '''
import React from 'react';
import axios from 'axios';

export default function Index() {
  axios.get('/api/data');
  return <div>Hello</div>;
}
''',
    }
    
    gate = L0StaticGate()
    result = gate.check(files)
    
    dependency_errors = [
        issue for issue in result.issues
        if 'unapproved_dependency' in issue.get('rule_id', '') and 'axios' in issue.get('message', '')
    ]
    
    print(f"\n依赖相关错误数: {len(dependency_errors)}")
    
    if dependency_errors:
        print("\n✅ 正确检测到 axios 未批准")
        for error in dependency_errors:
            print(f"  - {error['message']}")
        return True
    else:
        print("\n❌ 应该检测到 axios 但没有检测到")
        return False


if __name__ == '__main__':
    test1 = test_vite_config_dependencies()
    test2 = test_runtime_dependencies()
    
    print("\n" + "=" * 70)
    print("测试结果")
    print("=" * 70)
    print(f"配置文件过滤: {'✅ 通过' if test1 else '❌ 失败'}")
    print(f"运行时依赖检测: {'✅ 通过' if test2 else '❌ 失败'}")
    
    exit(0 if (test1 and test2) else 1)

