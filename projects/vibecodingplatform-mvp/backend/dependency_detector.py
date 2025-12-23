"""
依赖检测器 - 自动检测代码中使用的第三方依赖
"""

import re
from typing import Dict, Set

# ⚠️ CRITICAL: 这个列表必须与 dependency_arbiter.py 中的 DEPENDENCY_WHITELIST 保持同步
# 建议：导入统一配置，避免重复定义
# 已知的第三方依赖包（不在预设中的）
KNOWN_PACKAGES = {
    # 图表库
    'react-chartjs-2': '^5.2.0',
    'chart.js': '^4.4.0',
    'recharts': '^2.10.0',
    'd3': '^7.8.5',
    
    # UI 组件库
    '@mui/material': '^5.15.0',
    '@mui/icons-material': '^5.15.0',
    
    # 网络请求
    'axios': '^1.6.0',
    
    # 工具库
    'date-fns': '^3.0.0',
    'lodash': '^4.17.21',
    '@faker-js/faker': '^8.3.0',
    
    # 表单与验证
    'react-hook-form': '^7.49.0',
    '@hookform/resolvers': '^3.3.0',
    'zod': '^3.22.0',
    
    # 状态管理
    '@tanstack/react-query': '^5.17.0',
    
    # 通知/Toast
    'react-hot-toast': '^2.4.1',
    'sonner': '^1.3.1',
    
    # Shadcn/UI 特定组件依赖
    'cmdk': '^0.2.0',
    'react-day-picker': '^8.10.0',
    'react-resizable-panels': '^1.0.0',
    'vaul': '^0.9.0',
    
    # Radix UI（shadcn/ui 的底层依赖）
    '@radix-ui/react-accordion': '^1.1.2',
    '@radix-ui/react-alert-dialog': '^1.0.5',
    '@radix-ui/react-aspect-ratio': '^1.0.3',
    '@radix-ui/react-avatar': '^1.0.4',
    '@radix-ui/react-checkbox': '^1.0.4',
    '@radix-ui/react-collapsible': '^1.0.3',
    '@radix-ui/react-context-menu': '^2.1.5',
    '@radix-ui/react-dialog': '^1.0.5',
    '@radix-ui/react-dropdown-menu': '^2.0.6',
    '@radix-ui/react-hover-card': '^1.0.7',
    '@radix-ui/react-label': '^2.0.2',
    '@radix-ui/react-menubar': '^1.0.4',
    '@radix-ui/react-navigation-menu': '^1.1.4',
    '@radix-ui/react-popover': '^1.0.7',
    '@radix-ui/react-progress': '^1.0.3',
    '@radix-ui/react-radio-group': '^1.1.3',
    '@radix-ui/react-scroll-area': '^1.0.5',
    '@radix-ui/react-select': '^2.0.0',
    '@radix-ui/react-separator': '^1.0.3',
    '@radix-ui/react-slider': '^1.1.2',
    '@radix-ui/react-switch': '^1.0.3',
    '@radix-ui/react-tabs': '^1.0.4',
    '@radix-ui/react-toast': '^1.1.5',
    '@radix-ui/react-tooltip': '^1.0.7',
    
    # 拖拽
    'react-dnd': '^16.0.1',
    'react-dnd-html5-backend': '^16.0.1',
    '@dnd-kit/core': '^6.1.0',
    '@dnd-kit/sortable': '^8.0.0',
}

# Node.js 内置模块（不需要安装）
NODEJS_BUILTIN_MODULES = {
    'assert', 'buffer', 'child_process', 'cluster', 'console', 'constants',
    'crypto', 'dgram', 'dns', 'domain', 'events', 'fs', 'http', 'http2',
    'https', 'inspector', 'module', 'net', 'os', 'path', 'perf_hooks',
    'process', 'punycode', 'querystring', 'readline', 'repl', 'stream',
    'string_decoder', 'timers', 'tls', 'trace_events', 'tty', 'url',
    'util', 'v8', 'vm', 'wasi', 'worker_threads', 'zlib'
}

# 开发依赖（构建时依赖，运行时不需要）
DEV_DEPENDENCIES = {
    'vite',
    '@vitejs/plugin-react',
    '@vitejs/plugin-react-swc',
    'typescript',
    'eslint',
    'eslint-plugin-react',
    'eslint-plugin-react-hooks',
    'eslint-plugin-react-refresh',
    'prettier',
    'autoprefixer',
    'postcss',
    'tailwindcss',
    'tailwindcss-animate',
    '@types/node',
    '@types/react',
    '@types/react-dom',
    'vite-plugin-pwa',
}

# 预设中已有的依赖（不需要添加）
# 这些依赖已经在 client/package.json 中预装，检测时直接跳过
PRESET_PACKAGES = {
    # React 核心
    'react',
    'react-dom',
    'react-router-dom',
    
    # UI 工具
    'framer-motion',
    'lucide-react',
    'class-variance-authority',
    'clsx',
    'tailwind-merge',
    
    # Radix UI（shadcn/ui 底层）- 已在模板中预装
    '@radix-ui/react-avatar',
    '@radix-ui/react-checkbox',
    '@radix-ui/react-context-menu',
    '@radix-ui/react-dialog',
    '@radix-ui/react-dropdown-menu',
    '@radix-ui/react-label',
    '@radix-ui/react-menubar',
    '@radix-ui/react-navigation-menu',
    '@radix-ui/react-popover',
    '@radix-ui/react-progress',
    '@radix-ui/react-radio-group',
    '@radix-ui/react-select',
    '@radix-ui/react-slot',
    '@radix-ui/react-switch',
    '@radix-ui/react-toast',
    '@radix-ui/react-tooltip',
    
    # Shadcn 特定依赖 - 已在模板中预装
    'cmdk',
    'react-day-picker',
    'react-resizable-panels',
    
    # 表单与验证 - 已在模板中预装
    'react-hook-form',
    '@hookform/resolvers',
    'zod',
    
    # 工具库 - 已在模板中预装
    'date-fns',
}


def detect_imports_in_code(code: str) -> Set[str]:
    """
    从代码中提取 import 语句中的包名
    
    支持的格式：
    - import X from 'package'
    - import { X } from 'package'
    - import * as X from 'package'
    - import 'package'
    """
    imports = set()
    
    # 匹配各种 import 格式
    patterns = [
        r"import\s+.*?\s+from\s+['\"]([^'\"]+)['\"]",  # import X from 'pkg'
        r"import\s+['\"]([^'\"]+)['\"]",                # import 'pkg'
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, code, re.MULTILINE)
        for match in matches:
            package = match.group(1)
            
            # 只关注非相对路径的 import（第三方包）
            if not package.startswith('.') and not package.startswith('/') and not package.startswith('@/'):
                # 提取包名（去掉子路径）
                # 例如: 'react-chartjs-2/auto' -> 'react-chartjs-2'
                # 例如: '@mui/material/Button' -> '@mui/material'
                if package.startswith('@'):
                    # scoped package
                    parts = package.split('/')
                    if len(parts) >= 2:
                        package_name = '/'.join(parts[:2])
                    else:
                        package_name = package
                else:
                    package_name = package.split('/')[0]
                
                imports.add(package_name)
    
    return imports


def detect_dependencies_in_files(files: Dict[str, str]) -> Dict[str, str]:
    """
    检测文件中使用的第三方依赖
    
    Args:
        files: 文件名到文件内容的映射
        
    Returns:
        需要添加的依赖字典 {package_name: version}
    """
    all_imports = set()
    
    # 配置文件列表（不检测这些文件中的导入）
    config_file_patterns = ['vite.config', 'tailwind.config', 'postcss.config', 'eslint.config']
    
    # 遍历所有 .tsx/.ts/.jsx/.js 文件
    for filename, content in files.items():
        # 跳过配置文件
        if any(pattern in filename for pattern in config_file_patterns):
            continue
            
        if filename.endswith(('.tsx', '.ts', '.jsx', '.js')):
            imports = detect_imports_in_code(content)
            all_imports.update(imports)
    
    # 过滤掉预设依赖、Node.js 内置模块和开发依赖
    third_party_imports = all_imports - PRESET_PACKAGES - NODEJS_BUILTIN_MODULES - DEV_DEPENDENCIES
    
    # 过滤出需要添加的依赖（在白名单中的）
    missing_deps = {}
    for package in third_party_imports:
        if package in KNOWN_PACKAGES:
            missing_deps[package] = KNOWN_PACKAGES[package]
            print(f"   🔍 检测到额外依赖: {package} {KNOWN_PACKAGES[package]}")
    
    if not missing_deps:
        print(f"   ✓ 没有检测到额外依赖")
    
    return missing_deps


def add_dependencies_to_package_json(package_json_str: str, new_deps: Dict[str, str]) -> str:
    """
    将新依赖添加到 package.json 中
    
    Args:
        package_json_str: package.json 的字符串内容
        new_deps: 要添加的依赖 {package_name: version}
        
    Returns:
        更新后的 package.json 字符串
    """
    import json
    
    try:
        pkg = json.loads(package_json_str)
        
        if 'dependencies' not in pkg:
            pkg['dependencies'] = {}
        
        # 添加新依赖
        for package, version in new_deps.items():
            if package not in pkg['dependencies']:
                pkg['dependencies'][package] = version
                print(f"   ➕ 添加依赖: {package}@{version}")
        
        return json.dumps(pkg, indent=2)
    except Exception as e:
        print(f"   ⚠️ 添加依赖失败: {e}")
        return package_json_str


if __name__ == '__main__':
    # 测试
    test_code = """
    import React from 'react';
    import { Line } from 'react-chartjs-2';
    import { Button } from '@/components/ui/button';
    import './styles.css';
    """
    
    imports = detect_imports_in_code(test_code)
    print("检测到的导入:", imports)
    
    test_files = {
        'src/App.tsx': test_code
    }
    deps = detect_dependencies_in_files(test_files)
    print("需要添加的依赖:", deps)

