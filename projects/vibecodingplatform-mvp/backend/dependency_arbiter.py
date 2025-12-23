"""
依赖仲裁器 - 控制 AI 依赖新增，避免直接修改 package.json

策略：
1. AI 只能声明 dependenciesRequested（检测到的依赖）
2. 平台仲裁器按白名单/安全策略批准
3. 批准后的依赖写入 vibe.meta.json，前端/WebContainer 动态注入
4. package.json 永远受保护，不被 AI 直接修改
"""

import json
from typing import Dict, Set, List, Tuple
from pathlib import Path

# 依赖白名单（经过人工审核的安全依赖及其版本）
DEPENDENCY_WHITELIST = {
    # 图表库
    'react-chartjs-2': '^5.2.0',
    'chart.js': '^4.4.0',
    'recharts': '^2.10.0',
    'd3': '^7.8.5',
    
    # UI 组件库（谨慎开放，避免与 shadcn/ui 冲突）
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

# 预设依赖（已在模板中，无需审批）
# 这些依赖已经在 client/package.json 中预装，AI 使用时直接跳过审批
PRESET_DEPENDENCIES = {
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
    
    # 图表库 - 已在模板中预装
    'recharts',
}

# 黑名单（禁止的依赖，安全/架构原因）
DEPENDENCY_BLACKLIST = {
    # 与现有技术栈冲突
    'vue': '与 React 技术栈冲突',
    'angular': '与 React 技术栈冲突',
    'svelte': '与 React 技术栈冲突',
    'jquery': '不推荐在现代 React 项目中使用',
    
    # 与 Tailwind 冲突
    'styled-components': '与 Tailwind CSS 冲突',
    'emotion': '与 Tailwind CSS 冲突',
    '@emotion/react': '与 Tailwind CSS 冲突',
    
    # 与 Vite 不兼容或有问题
    'webpack': 'Vite 项目不需要 webpack',
    'create-react-app': '不兼容 Vite',
    
    # 安全问题
    'lodash': '建议使用 lodash-es 或按需导入（已在白名单用特定版本）',
}


class DependencyArbiter:
    """依赖仲裁器"""
    
    def __init__(self, whitelist: Dict[str, str] = None, blacklist: Dict[str, str] = None):
        self.whitelist = whitelist or DEPENDENCY_WHITELIST
        self.blacklist = blacklist or DEPENDENCY_BLACKLIST
    
    def arbitrate(self, requested_deps: Dict[str, str]) -> Tuple[Dict[str, str], Dict[str, str], List[str]]:
        """
        仲裁依赖请求
        
        Args:
            requested_deps: AI 请求的依赖 {package_name: detected_version}
        
        Returns:
            (approved_deps, rejected_deps, warnings)
            - approved_deps: 批准的依赖 {package: version}
            - rejected_deps: 拒绝的依赖 {package: reason}
            - warnings: 警告信息列表
        """
        approved = {}
        rejected = {}
        warnings = []
        
        for package, detected_version in requested_deps.items():
            # 跳过预设依赖
            if package in PRESET_DEPENDENCIES:
                continue
            
            # 检查黑名单
            if package in self.blacklist:
                rejected[package] = self.blacklist[package]
                warnings.append(f"❌ 依赖 '{package}' 被黑名单拒绝: {self.blacklist[package]}")
                continue
            
            # 检查白名单
            if package in self.whitelist:
                # 使用白名单中的安全版本（而非 AI 检测的版本）
                approved[package] = self.whitelist[package]
                if detected_version != self.whitelist[package]:
                    warnings.append(
                        f"⚠️  依赖 '{package}' 版本已调整: "
                        f"{detected_version} → {self.whitelist[package]}（白名单版本）"
                    )
            else:
                # 不在白名单中，拒绝（需要人工审核后添加）
                rejected[package] = f"未在白名单中（需人工审核）"
                warnings.append(
                    f"❌ 依赖 '{package}' 未在白名单中，已拒绝。"
                    f"如需使用，请联系平台管理员审核并添加到白名单。"
                )
        
        return approved, rejected, warnings
    
    def create_dependency_report(
        self,
        requested: Dict[str, str],
        approved: Dict[str, str],
        rejected: Dict[str, str]
    ) -> Dict:
        """
        生成依赖仲裁报告（写入 vibe.meta.json）
        
        Returns:
            结构化的依赖报告
        """
        return {
            "requested": requested,
            "approved": approved,
            "rejected": rejected,
            "whitelist_count": len(self.whitelist),
            "blacklist_count": len(self.blacklist),
        }


def print_arbitration_summary(approved: Dict[str, str], rejected: Dict[str, str], warnings: List[str]):
    """打印仲裁摘要"""
    if approved:
        print(f"\n✅ 批准的依赖 ({len(approved)} 个):")
        for pkg, ver in approved.items():
            print(f"   ✓ {pkg}@{ver}")
    
    if rejected:
        print(f"\n❌ 拒绝的依赖 ({len(rejected)} 个):")
        for pkg, reason in rejected.items():
            print(f"   ✗ {pkg}: {reason}")
    
    if warnings:
        print(f"\n⚠️  警告信息:")
        for warning in warnings:
            print(f"   {warning}")


# 全局仲裁器实例
arbiter = DependencyArbiter()


if __name__ == '__main__':
    # 测试
    test_requested = {
        'react-chartjs-2': '^5.0.0',  # 白名单，但版本不同
        'chart.js': '^4.4.0',          # 白名单，版本一致
        'jquery': '^3.6.0',            # 黑名单
        'some-random-package': '^1.0.0',  # 未在白名单
    }
    
    approved, rejected, warnings = arbiter.arbitrate(test_requested)
    print_arbitration_summary(approved, rejected, warnings)
    
    report = arbiter.create_dependency_report(test_requested, approved, rejected)
    print(f"\n依赖报告:\n{json.dumps(report, indent=2, ensure_ascii=False)}")

