"""
Sudoku 回归测试 - P0 验收标准
验证平台能否生成可玩的交互式数独游戏
"""
import json
import sys
from pathlib import Path

# 添加 backend 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from server import ai, generate_with_template
from policies import policy_manager


def test_sudoku_generation():
    """
    测试数独游戏生成
    
    验收标准（来自 policy 配置）:
    1. 点击空格可以选中
    2. 可以输入数字（键盘或数字面板）
    3. 非空初始格不可编辑（基于 original 状态）
    4. 冲突高亮或阻止非法输入
    """
    print("=" * 80)
    print("SUDOKU 回归测试 - P0 验收标准")
    print("=" * 80)
    
    # 获取 Sudoku 回归套件配置
    sudoku_suite = policy_manager.get_p0_regression_suite()
    
    if not sudoku_suite:
        print("✗ 错误：未找到 P0 回归测试套件（Sudoku）")
        return False
    
    print(f"\n测试套件: {sudoku_suite['name']}")
    print(f"描述: {sudoku_suite['description']}")
    print(f"Prompt: {sudoku_suite['prompt']}")
    print(f"\n验收标准:")
    for i, criterion in enumerate(sudoku_suite['acceptance_criteria'], 1):
        print(f"  {i}. {criterion}")
    
    # 生成数独游戏
    print(f"\n{'='*80}")
    print("开始生成数独游戏...")
    print(f"{'='*80}\n")
    
    try:
        files = generate_with_template(
            prompt_text=sudoku_suite['prompt'],
            template_name='react-ts-shadcn-cyberpunk',  # 使用默认模板
            style='auto'
        )
        
        print(f"\n{'='*80}")
        print(f"生成完成！共 {len(files)} 个文件")
        print(f"{'='*80}\n")
        
        # 检查关键文件
        print("检查关键文件:")
        key_files = [
            'src/pages/Index.tsx',
            'vibe.meta.json'
        ]
        
        missing_files = []
        for key_file in key_files:
            if key_file in files:
                print(f"  ✓ {key_file}")
            else:
                print(f"  ✗ {key_file} (缺失)")
                missing_files.append(key_file)
        
        if missing_files:
            print(f"\n✗ 错误：缺少关键文件: {', '.join(missing_files)}")
            return False
        
        # 检查 InteractionSpec
        print(f"\n{'='*80}")
        print("检查 InteractionSpec:")
        print(f"{'='*80}\n")
        
        spec_location = policy_manager.get_spec_location()
        if spec_location in files:
            print(f"  ✓ InteractionSpec 已生成: {spec_location}")
            spec = json.loads(files[spec_location])
            print(f"    - State: {len(spec.get('state', []))} 个")
            print(f"    - Events: {len(spec.get('events', []))} 个")
            print(f"    - Constraints: {len(spec.get('constraints', []))} 个")
            print(f"    - Acceptance: {len(spec.get('acceptance', []))} 个")
            
            # 验证 Spec 内容
            print(f"\n  验证 Spec 内容:")
            
            # 检查是否有选中状态
            has_selected_state = any(
                'select' in s.get('name', '').lower() or 'active' in s.get('name', '').lower()
                for s in spec.get('state', [])
            )
            print(f"    {'✓' if has_selected_state else '✗'} 有选中状态（selectedCell 或类似）")
            
            # 检查是否有 original 状态（锁定初始格）
            has_original_state = any(
                'original' in s.get('name', '').lower() or 'initial' in s.get('name', '').lower()
                for s in spec.get('state', [])
            )
            print(f"    {'✓' if has_original_state else '✗'} 有 original 状态（用于锁定初始格）")
            
            # 检查是否有点击事件
            has_click_event = any(
                'click' in e.get('trigger', '').lower()
                for e in spec.get('events', [])
            )
            print(f"    {'✓' if has_click_event else '✗'} 有点击事件")
            
            # 检查是否有输入事件
            has_input_event = any(
                'input' in e.get('trigger', '').lower() or 
                'key' in e.get('trigger', '').lower()
                for e in spec.get('events', [])
            )
            print(f"    {'✓' if has_input_event else '✗'} 有输入事件（键盘或数字面板）")
        else:
            print(f"  ⚠️  InteractionSpec 未生成（可能被策略禁用）")
        
        # 检查质量门禁结果
        print(f"\n{'='*80}")
        print("检查质量门禁结果:")
        print(f"{'='*80}\n")
        
        vibe_meta = json.loads(files['vibe.meta.json'])
        
        if 'quality_gates' in vibe_meta:
            gates = vibe_meta['quality_gates']
            print(f"  门禁启用: {gates.get('enabled', False)}")
            print(f"  门禁通过: {gates.get('passed', False)}")
            
            if not gates.get('passed', False):
                failed_gates = gates.get('failed_gates', [])
                print(f"  ✗ 失败的门禁: {', '.join(failed_gates)}")
                
                # 显示具体问题
                for gate_name, gate_result in gates.get('results', {}).items():
                    if not gate_result.get('passed', True):
                        print(f"\n  {gate_name} 失败:")
                        for issue in gate_result.get('issues', [])[:3]:
                            print(f"    - [{issue['severity'].upper()}] {issue['file']}:{issue['line']}: {issue['message']}")
            else:
                print(f"  ✓ 所有门禁通过")
        
        # 检查自愈循环结果
        if 'self_heal' in vibe_meta:
            heal = vibe_meta['self_heal']
            if heal.get('enabled', False):
                print(f"\n自愈循环:")
                print(f"  启用: {heal.get('enabled', False)}")
                print(f"  触发: {heal.get('triggered', False)}")
                if heal.get('triggered', False):
                    print(f"  成功: {heal.get('success', False)}")
                    print(f"  迭代次数: {heal.get('iterations', 0)}/{heal.get('max_iterations', 0)}")
        
        # 静态代码检查（手动验收标准）
        print(f"\n{'='*80}")
        print("静态代码检查 (Index.tsx):")
        print(f"{'='*80}\n")
        
        index_tsx = files.get('src/pages/Index.tsx', '')
        
        checks = [
            ("useState", "✓ 使用了 useState（有状态管理）"),
            ("onClick", "✓ 有 onClick 事件处理"),
            ("onChange" in index_tsx or "onKeyDown" in index_tsx, "✓ 有输入处理（onChange 或 onKeyDown）"),
            ("readOnly" in index_tsx or "disabled" in index_tsx, "✓ 有锁定逻辑（readOnly 或 disabled）"),
        ]
        
        for condition, message in checks:
            if isinstance(condition, str):
                has_feature = condition in index_tsx
            else:
                has_feature = condition
            
            if has_feature:
                print(f"  {message}")
            else:
                print(f"  ✗ {message.replace('✓', '缺少')}")
        
        # 最终判定
        print(f"\n{'='*80}")
        print("最终判定:")
        print(f"{'='*80}\n")
        
        all_passed = (
            not missing_files and
            (vibe_meta.get('quality_gates', {}).get('passed', False) or 
             not vibe_meta.get('quality_gates', {}).get('enabled', False))
        )
        
        if all_passed:
            print("  ✓ PASS - 数独游戏生成成功，通过所有基本检查")
            print("\n  建议:")
            print("    1. 在 WebContainer 中测试实际交互")
            print("    2. 验证所有验收标准")
            print("    3. 检查 UI 和 UX")
            return True
        else:
            print("  ✗ FAIL - 存在问题，需要修复")
            return False
    
    except Exception as e:
        print(f"\n✗ 生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_sudoku_generation()
    sys.exit(0 if success else 1)

