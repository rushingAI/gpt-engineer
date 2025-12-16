"""
依赖检测器 - 自动检测代码中使用的第三方依赖
"""

import re
from typing import Dict, Set

# 已知的第三方依赖包（不在预设中的）
KNOWN_PACKAGES = {
    'react-chartjs-2': '^5.2.0',
    'chart.js': '^4.4.0',
    'recharts': '^2.10.0',
    'd3': '^7.8.5',
    '@mui/material': '^5.15.0',
    '@mui/icons-material': '^5.15.0',
    'axios': '^1.6.0',
    'date-fns': '^3.0.0',
    'react-hook-form': '^7.49.0',
    'zod': '^3.22.0',
    '@tanstack/react-query': '^5.17.0',
    'react-hot-toast': '^2.4.1',
    'sonner': '^1.3.1',
    'vaul': '^0.9.0',
}

# 预设中已有的依赖（不需要添加）
PRESET_PACKAGES = {
    'react',
    'react-dom',
    'react-router-dom',
    'framer-motion',
    'lucide-react',
    'class-variance-authority',
    'clsx',
    'tailwind-merge',
    '@radix-ui/react-slot',
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
    
    # 遍历所有 .tsx/.ts/.jsx/.js 文件
    for filename, content in files.items():
        if filename.endswith(('.tsx', '.ts', '.jsx', '.js')):
            imports = detect_imports_in_code(content)
            all_imports.update(imports)
    
    # 过滤出需要添加的依赖（不在预设中的）
    missing_deps = {}
    for package in all_imports:
        if package not in PRESET_PACKAGES and package in KNOWN_PACKAGES:
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

