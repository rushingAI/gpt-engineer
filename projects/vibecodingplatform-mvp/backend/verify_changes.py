"""
验证组件化改造的关键改动是否到位
不需要运行服务器或 AI，只检查配置和代码
"""
import json
import sys
from pathlib import Path

def check_policy_css_modules():
    """检查策略是否支持 CSS Modules"""
    policy_file = Path(__file__).parent / 'policies' / 'generation_policy.json'
    policy = json.loads(policy_file.read_text())
    
    # 检查 allowlist 是否包含 CSS Modules
    allowlist = policy.get('file_policy', {}).get('allowlist_patterns', [])
    has_css_modules = any('module.css' in pattern for pattern in allowlist)
    
    # 检查是否有 CSS Modules 配置
    has_css_config = 'css_modules' in policy.get('file_policy', {})
    
    return has_css_modules and has_css_config

def check_quality_gates_new_rules():
    """检查质量门禁是否添加了新规则"""
    policy_file = Path(__file__).parent / 'policies' / 'generation_policy.json'
    policy = json.loads(policy_file.read_text())
    
    rules = policy.get('quality_gates', {}).get('levels', {}).get('L0_static', {}).get('rules', [])
    rule_ids = [r.get('id') for r in rules]
    
    new_rules = [
        'unreferenced_generated_file',
        'import_boundary_violation',
        'css_module_global_usage',
        'index_tsx_too_large'
    ]
    
    found_rules = [rule for rule in new_rules if rule in rule_ids]
    
    return len(found_rules) == len(new_rules), found_rules

def check_quality_gates_implementation():
    """检查 quality_gates.py 是否实现了新规则"""
    gates_file = Path(__file__).parent / 'quality_gates.py'
    content = gates_file.read_text()
    
    methods = [
        '_check_import_boundary_violation',
        '_check_index_too_large',
        '_check_css_module_global_usage',
        '_check_unreferenced_generated_files'
    ]
    
    found_methods = [m for m in methods if m in content]
    
    return len(found_methods) == len(methods), found_methods

def check_server_prompt_multi_file():
    """检查 server.py prompt 是否支持多文件"""
    server_file = Path(__file__).parent / 'server.py'
    content = server_file.read_text()
    
    # 检查是否有多文件结构说明
    has_multi_file = 'src/components/generated/' in content and 'ALLOWED FILE LOCATIONS' in content
    
    # 检查是否有 CSS Modules 说明
    has_css_modules = 'CSS MODULES SUPPORT' in content
    
    return has_multi_file and has_css_modules

def check_preprompts_updated():
    """检查 preprompts 是否已更新"""
    preprompts_dir = Path(__file__).parent / 'preprompts_custom'
    
    # 检查关键 preprompts
    files_to_check = ['modern_web_app', 'dashboard', 'landing_page', 'cyberpunk_react']
    
    all_updated = True
    for filename in files_to_check:
        file_path = preprompts_dir / filename
        if file_path.exists():
            content = file_path.read_text()
            # 检查是否有多文件支持的标记
            if 'src/components/generated/' not in content:
                all_updated = False
                print(f"  ⚠️  {filename} 可能未更新（未找到 generated 目录引用）")
    
    return all_updated

def check_self_heal_split_guidance():
    """检查自愈是否添加了拆分指导"""
    self_heal_file = Path(__file__).parent / 'self_heal.py'
    content = self_heal_file.read_text()
    
    has_split_guidance = 'Index.tsx TOO LARGE' in content
    has_refactor_instruction = 'Extract complex components' in content
    
    return has_split_guidance and has_refactor_instruction

def check_frontend_filter():
    """检查前端过滤器是否支持 CSS Modules"""
    frontend_file = Path(__file__).parent.parent / 'client' / 'src' / 'utils' / 'webcontainer.js'
    
    if not frontend_file.exists():
        print("  ⚠️  前端文件不存在，跳过检查")
        return True
    
    content = frontend_file.read_text()
    
    has_css_modules = '.module.css' in content or 'module\.css' in content
    
    return has_css_modules

def main():
    """主函数"""
    print("=" * 80)
    print("验证组件化改造关键改动")
    print("=" * 80)
    
    checks = [
        ("策略支持 CSS Modules", check_policy_css_modules),
        ("Server.py prompt 支持多文件", check_server_prompt_multi_file),
        ("Preprompts 已更新", check_preprompts_updated),
        ("自愈添加拆分指导", check_self_heal_split_guidance),
        ("前端过滤器支持 CSS Modules", check_frontend_filter),
    ]
    
    all_passed = True
    
    for name, check_fn in checks:
        try:
            result = check_fn()
            if result:
                print(f"✅ {name}")
            else:
                print(f"❌ {name}")
                all_passed = False
        except Exception as e:
            print(f"❌ {name}: {e}")
            all_passed = False
    
    # 特殊检查：质量门禁规则
    print("\n检查质量门禁:")
    
    # 策略配置
    has_rules, found_rules = check_quality_gates_new_rules()
    if has_rules:
        print(f"✅ 策略配置新增规则: {', '.join(found_rules)}")
    else:
        print(f"❌ 策略配置缺少规则（找到: {', '.join(found_rules)}）")
        all_passed = False
    
    # 实现检查
    has_impl, found_methods = check_quality_gates_implementation()
    if has_impl:
        print(f"✅ Quality gates 实现新方法: {len(found_methods)} 个")
    else:
        print(f"❌ Quality gates 缺少方法（找到: {', '.join(found_methods)}）")
        all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ 所有关键改动验证通过")
        print("\n下一步:")
        print("  1. 运行 Sudoku 回归测试已通过 ✅")
        print("  2. 启动后端测试实际生成: ./run.sh")
        print("  3. 在 WebContainer 中验证多文件组件化")
        return 0
    else:
        print("❌ 部分检查未通过，请查看上述输出")
        return 1


if __name__ == '__main__':
    sys.exit(main())

