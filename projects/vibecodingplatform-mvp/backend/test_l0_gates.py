"""
L0 交互/样式门禁回归测试
验证 Gate1-Gate6 在 Sudoku 等结构性应用中的正确性
"""
import sys
import json
from pathlib import Path

# 添加 backend 目录到路径
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from l0_gates import run_l0_gates


def test_gate1_structural_no_shadcn_input():
    """Gate1: 结构性应用禁止使用 shadcn Input"""
    print("\n=== Gate1 测试：结构性应用禁止 shadcn Input ===")
    
    # 模拟 Sudoku 应用使用了 shadcn Input（应该失败）
    files = {
        'src/pages/Index.tsx': '''
import React from 'react';
import { SudokuGrid } from '@/components/generated/sudoku/SudokuGrid';
export default function Index() {
  return <SudokuGrid />;
}
''',
        'src/components/generated/sudoku/SudokuGrid.tsx': '''
import React from 'react';
import { Input } from '@/components/ui/input';  // ❌ 违规
export const SudokuGrid = () => {
  return <Input value="test" />;  // ❌ 违规
};
'''
    }
    
    context = {
        'prompt_text': '创建一个数独游戏',  # 关键词触发
        'app_type': 'game',
        'interaction_spec': None,
        'generated_file_paths': list(files.keys())
    }
    
    result = run_l0_gates(files, context, {'enabled': True})
    result_dict = result.to_dict()
    
    # 应该失败
    assert not result_dict['pass'], "Gate1: 使用 shadcn Input 应该失败"
    assert any(f['gate'] == 'G1_STRUCTURAL_NO_SHADCN_INPUT' for f in result_dict['fails']), "应该触发 G1"
    print("✓ Gate1 正确检测到 shadcn Input 违规")
    
    # 测试正确的用法（原生 input）
    files_correct = {
        'src/pages/Index.tsx': files['src/pages/Index.tsx'],
        'src/components/generated/sudoku/SudokuGrid.tsx': '''
import React from 'react';
import styles from './SudokuGrid.module.css';
export const SudokuGrid = () => {
  return <input className={styles.cell} />;  // ✅ 使用原生 input
};
''',
        'src/components/generated/sudoku/SudokuGrid.module.css': '''
.cell {
  width: 48px;
  height: 48px;
}
'''
    }
    
    result_correct = run_l0_gates(files_correct, context, {'enabled': True})
    # Gate1 不应该失败（但可能有其他 gate 问题，这里只关注 Gate1）
    has_g1_fail = any(f['gate'] == 'G1_STRUCTURAL_NO_SHADCN_INPUT' for f in result_correct.to_dict()['fails'])
    assert not has_g1_fail, "Gate1: 使用原生 input 不应该触发 G1"
    print("✓ Gate1 正确通过原生 input")


def test_gate2_css_modules_colocated():
    """Gate2: CSS Modules 必须与组件同名同目录，且必须被 import"""
    print("\n=== Gate2 测试：CSS Modules 同名同目录 + import ===")
    
    # 孤儿 CSS Module（没有对应组件）
    files_orphan = {
        'src/components/generated/sudoku/SudokuGrid.module.css': '.cell { width: 48px; }'
    }
    
    context = {
        'prompt_text': '数独游戏',
        'app_type': 'game',
        'interaction_spec': None,
        'generated_file_paths': list(files_orphan.keys())
    }
    
    result = run_l0_gates(files_orphan, context, {'enabled': True})
    assert any(f['gate'] == 'G2_CSS_MODULE_ORPHAN' for f in result.to_dict()['fails']), "应该检测到孤儿 CSS Module"
    print("✓ Gate2 正确检测到孤儿 CSS Module")
    
    # 组件没有 import CSS Module
    files_no_import = {
        'src/components/generated/sudoku/SudokuGrid.tsx': '''
import React from 'react';
export const SudokuGrid = () => <div>Grid</div>;
''',
        'src/components/generated/sudoku/SudokuGrid.module.css': '.cell { width: 48px; }'
    }
    
    result = run_l0_gates(files_no_import, context, {'enabled': True})
    assert any(f['gate'] == 'G2_CSS_MODULE_NOT_IMPORTED' for f in result.to_dict()['fails']), "应该检测到 CSS Module 未导入"
    print("✓ Gate2 正确检测到 CSS Module 未导入")
    
    # 正确的用法
    files_correct = {
        'src/components/generated/sudoku/SudokuGrid.tsx': '''
import React from 'react';
import styles from './SudokuGrid.module.css';  // ✅ 导入了
export const SudokuGrid = () => <div className={styles.cell}>Grid</div>;
''',
        'src/components/generated/sudoku/SudokuGrid.module.css': '.cell { width: 48px; }'
    }
    
    result = run_l0_gates(files_correct, context, {'enabled': True})
    has_g2_fail = any(f['gate'].startswith('G2_') for f in result.to_dict()['fails'])
    assert not has_g2_fail, "正确的 CSS Modules 不应该触发 G2"
    print("✓ Gate2 正确通过")


def test_gate3_forbidden_css():
    """Gate3: 禁止危险 CSS（:global, @import, url(http)）"""
    print("\n=== Gate3 测试：禁止危险 CSS ===")
    
    # 使用 :global
    files_global = {
        'src/components/generated/sudoku/SudokuGrid.tsx': '''
import React from 'react';
import styles from './SudokuGrid.module.css';
export const SudokuGrid = () => <div className={styles.cell}>Grid</div>;
''',
        'src/components/generated/sudoku/SudokuGrid.module.css': '''
.cell { width: 48px; }
:global(.body) { margin: 0; }  /* ❌ 违规 */
'''
    }
    
    context = {
        'prompt_text': '数独',
        'app_type': 'game',
        'interaction_spec': None,
        'generated_file_paths': list(files_global.keys())
    }
    
    result = run_l0_gates(files_global, context, {'enabled': True})
    assert any(f['gate'] == 'G3_FORBIDDEN_CSS' for f in result.to_dict()['fails']), "应该检测到 :global"
    print("✓ Gate3 正确检测到 :global")
    
    # 使用 @import
    files_import = {
        'src/components/generated/sudoku/SudokuGrid.tsx': files_global['src/components/generated/sudoku/SudokuGrid.tsx'],
        'src/components/generated/sudoku/SudokuGrid.module.css': '''
@import url('./other.css');  /* ❌ 违规 */
.cell { width: 48px; }
'''
    }
    
    result = run_l0_gates(files_import, context, {'enabled': True})
    assert any(f['gate'] == 'G3_FORBIDDEN_CSS' for f in result.to_dict()['fails']), "应该检测到 @import"
    print("✓ Gate3 正确检测到 @import")


def test_gate4_controlled_input():
    """Gate4: 受控输入必须闭环（value= 必须配 onChange 或 readOnly）"""
    print("\n=== Gate4 测试：受控输入闭环 ===")
    
    # value 但没有 onChange/readOnly
    files_no_handler = {
        'src/components/generated/sudoku/SudokuCell.tsx': '''
import React from 'react';
export const SudokuCell = ({ value }) => {
  return <input value={value} />;  /* ❌ 缺少 onChange */
};
'''
    }
    
    context = {
        'prompt_text': '数独',
        'app_type': 'game',
        'interaction_spec': None,
        'generated_file_paths': list(files_no_handler.keys())
    }
    
    result = run_l0_gates(files_no_handler, context, {'enabled': True})
    assert any(f['gate'] == 'G4_CONTROLLED_INPUT_NO_HANDLER' for f in result.to_dict()['fails']), "应该检测到缺少 onChange"
    print("✓ Gate4 正确检测到缺少 onChange")
    
    # 正确的用法（有 onChange）
    files_correct = {
        'src/components/generated/sudoku/SudokuCell.tsx': '''
import React from 'react';
export const SudokuCell = ({ value, onChange }) => {
  return <input value={value} onChange={onChange} />;  /* ✅ 有 onChange */
};
'''
    }
    
    result = run_l0_gates(files_correct, context, {'enabled': True})
    has_g4_fail = any(f['gate'] == 'G4_CONTROLLED_INPUT_NO_HANDLER' for f in result.to_dict()['fails'])
    assert not has_g4_fail, "有 onChange 不应该触发 G4"
    print("✓ Gate4 正确通过")


def test_gate5_readonly_logic():
    """Gate5: 防"填了就锁死"的 readOnly 逻辑"""
    print("\n=== Gate5 测试：readOnly 逻辑 ===")
    
    # 结构性应用：readOnly 基于当前 value（应该 Fail）
    files_structural = {
        'src/components/generated/sudoku/SudokuCell.tsx': '''
import React from 'react';
export const SudokuCell = ({ value, onChange }) => {
  return <input value={value} onChange={onChange} readOnly={value !== null} />;  /* ❌ 基于当前 value */
};
'''
    }
    
    context_structural = {
        'prompt_text': '创建数独游戏',
        'app_type': 'game',
        'interaction_spec': None,
        'generated_file_paths': list(files_structural.keys())
    }
    
    result = run_l0_gates(files_structural, context_structural, {'enabled': True, 'gate5_structural_fail': True})
    assert any(f['gate'] == 'G5_READONLY_WRONG_CONDITION' for f in result.to_dict()['fails']), "结构性应用应该 Fail"
    print("✓ Gate5 正确检测到结构性应用的错误 readOnly")
    
    # 普通应用：相同逻辑应该是 Warning（使用不含结构性关键词的路径）
    files_normal = {
        'src/components/generated/form/FormField.tsx': '''
import React from 'react';
export const FormField = ({ value, onChange }) => {
  return <input value={value} onChange={onChange} readOnly={value !== null} />;  /* ⚠️  基于当前 value */
};
'''
    }
    
    context_normal = {
        'prompt_text': '创建一个表单',
        'app_type': 'form',
        'interaction_spec': None,
        'generated_file_paths': list(files_normal.keys())
    }
    
    result = run_l0_gates(files_normal, context_normal, {'enabled': True, 'gate5_structural_fail': True})
    has_g5_fail = any(f['gate'] == 'G5_READONLY_WRONG_CONDITION' for f in result.to_dict()['fails'])
    has_g5_warn = any(w['gate'] == 'G5_READONLY_WRONG_CONDITION' for w in result.to_dict()['warnings'])
    assert not has_g5_fail, "普通应用不应该 Fail"
    assert has_g5_warn, "普通应用应该 Warning"
    print("✓ Gate5 正确区分结构性应用和普通应用")


def test_gate6_orphan_files():
    """Gate6: 新增文件必须被引用（防孤儿）"""
    print("\n=== Gate6 测试：孤儿文件检测 ===")
    
    # 孤儿组件（没有被引用） - 结构性应用
    files_orphan_structural = {
        'src/pages/Index.tsx': '''
import React from 'react';
export default function Index() {
  return <div>Sudoku</div>;
}
''',
        'src/components/generated/sudoku/SudokuGrid.tsx': '''
import React from 'react';
export const SudokuGrid = () => <div>Grid</div>;  /* ❌ 未被引用 */
'''
    }
    
    context_structural = {
        'prompt_text': '数独游戏',
        'app_type': 'game',
        'interaction_spec': None,
        'generated_file_paths': list(files_orphan_structural.keys())
    }
    
    result = run_l0_gates(files_orphan_structural, context_structural, {'enabled': True, 'gate6_orphan_severity_mode': 'error_structural'})
    assert any(f['gate'] == 'G6_ORPHAN_FILES' for f in result.to_dict()['fails']), "结构性应用的孤儿文件应该是 Error"
    print("✓ Gate6 正确检测到结构性应用的孤儿文件（Error）")
    
    # 普通应用的孤儿文件（应该是 Warning） - 使用不含结构性关键词的路径
    files_orphan_normal = {
        'src/pages/Index.tsx': '''
import React from 'react';
export default function Index() {
  return <div>Form</div>;
}
''',
        'src/components/generated/form/FormField.tsx': '''
import React from 'react';
export const FormField = () => <input />;  /* ❌ 未被引用 */
'''
    }
    
    context_normal = {
        'prompt_text': '一个表单',
        'app_type': 'form',
        'interaction_spec': None,
        'generated_file_paths': list(files_orphan_normal.keys())
    }
    
    result = run_l0_gates(files_orphan_normal, context_normal, {'enabled': True, 'gate6_orphan_severity_mode': 'error_structural'})
    has_g6_fail = any(f['gate'] == 'G6_ORPHAN_FILES' for f in result.to_dict()['fails'])
    has_g6_warn = any(w['gate'] == 'G6_ORPHAN_FILES' for w in result.to_dict()['warnings'])
    assert not has_g6_fail, "普通应用的孤儿文件不应该 Fail"
    assert has_g6_warn, "普通应用的孤儿文件应该 Warning"
    print("✓ Gate6 正确区分结构性应用和普通应用的孤儿文件")
    
    # 正确引用的组件
    files_correct = {
        'src/pages/Index.tsx': '''
import React from 'react';
import { SudokuGrid } from '@/components/generated/sudoku/SudokuGrid';  // ✅ 引用了
export default function Index() {
  return <SudokuGrid />;
}
''',
        'src/components/generated/sudoku/SudokuGrid.tsx': '''
import React from 'react';
export const SudokuGrid = () => <div>Grid</div>;
'''
    }
    
    result = run_l0_gates(files_correct, context_structural, {'enabled': True, 'gate6_orphan_severity_mode': 'error_structural'})
    has_g6_issue = any(
        f['gate'] == 'G6_ORPHAN_FILES' 
        for f in result.to_dict()['fails'] + result.to_dict()['warnings']
    )
    assert not has_g6_issue, "正确引用的组件不应该触发 G6"
    print("✓ Gate6 正确通过")


def test_gate7_import_export_consistency():
    """
    Gate7: import/export 一致性检查（命名导出 vs 默认导出）
    """
    print("\n=== Gate7 测试：import/export 一致性 ===")
    
    # 场景1：命名导入 vs 默认导出（应该失败）
    files_named_import_default_export = {
        'src/pages/Index.tsx': '''
import { SudokuGrid } from '@/components/generated/sudoku/SudokuGrid';
export default function Index() {
  return <SudokuGrid />;
}
''',
        'src/components/generated/sudoku/SudokuGrid.tsx': '''
const SudokuGrid = () => <div>Grid</div>;
export default SudokuGrid;
'''
    }
    result = run_l0_gates(files_named_import_default_export, {'prompt_text': 'sudoku', 'app_slug': 'sudoku'})
    assert not result.pass_status, "应该检测到 import/export 不匹配"
    assert any(f['gate'] == 'G7_IMPORT_EXPORT_MISMATCH' for f in result.fails), "应该有 G7 错误"
    print(f"✓ Gate7 正确检测到命名导入 vs 默认导出不匹配")
    
    # 场景2：默认导入 vs 命名导出（应该失败）
    files_default_import_named_export = {
        'src/pages/Index.tsx': '''
import SudokuGrid from '@/components/generated/sudoku/SudokuGrid';
export default function Index() {
  return <SudokuGrid />;
}
''',
        'src/components/generated/sudoku/SudokuGrid.tsx': '''
export const SudokuGrid = () => <div>Grid</div>;
'''
    }
    result = run_l0_gates(files_default_import_named_export, {'prompt_text': 'sudoku', 'app_slug': 'sudoku'})
    assert not result.pass_status, "应该检测到 import/export 不匹配"
    assert any(f['gate'] == 'G7_IMPORT_EXPORT_MISMATCH' for f in result.fails), "应该有 G7 错误"
    print(f"✓ Gate7 正确检测到默认导入 vs 命名导出不匹配")
    
    # 场景3：命名导入 + 命名导出（应该通过）
    files_named_both = {
        'src/pages/Index.tsx': '''
import { SudokuGrid } from '@/components/generated/sudoku/SudokuGrid';
export default function Index() {
  return <SudokuGrid />;
}
''',
        'src/components/generated/sudoku/SudokuGrid.tsx': '''
export const SudokuGrid = () => <div>Grid</div>;
'''
    }
    result = run_l0_gates(files_named_both, {'prompt_text': 'sudoku', 'app_slug': 'sudoku'})
    assert result.pass_status or not any(f['gate'] == 'G7_IMPORT_EXPORT_MISMATCH' for f in result.fails), "命名导入+命名导出应该通过"
    print(f"✓ Gate7 正确通过命名导入 + 命名导出")
    
    # 场景4：默认导入 + 默认导出（应该通过）
    files_default_both = {
        'src/pages/Index.tsx': '''
import SudokuGrid from '@/components/generated/sudoku/SudokuGrid';
export default function Index() {
  return <SudokuGrid />;
}
''',
        'src/components/generated/sudoku/SudokuGrid.tsx': '''
const SudokuGrid = () => <div>Grid</div>;
export default SudokuGrid;
'''
    }
    result = run_l0_gates(files_default_both, {'prompt_text': 'sudoku', 'app_slug': 'sudoku'})
    assert result.pass_status or not any(f['gate'] == 'G7_IMPORT_EXPORT_MISMATCH' for f in result.fails), "默认导入+默认导出应该通过"
    print(f"✓ Gate7 正确通过默认导入 + 默认导出")


def test_sudoku_classic_style_regression():
    """
    Sudoku 经典纸质风格回归测试
    确保生成"经典纸质数独"时，L0 门禁能正确工作
    """
    print("\n=== Sudoku 经典纸质风格回归测试 ===")
    
    # 模拟正确的实现（原生 input + CSS Modules）
    files_correct = {
        'src/pages/Index.tsx': '''
import React, { useState } from 'react';
import { SudokuGrid } from '@/components/generated/sudoku/SudokuGrid';

export default function Index() {
  const [board, setBoard] = useState(/* ... */);
  return <SudokuGrid board={board} onCellChange={setBoard} />;
}
''',
        'src/components/generated/sudoku/SudokuGrid.tsx': '''
import React from 'react';
import { SudokuCell } from './SudokuCell';
import styles from './SudokuGrid.module.css';

export const SudokuGrid = ({ board, onCellChange }) => {
  return (
    <div className={styles.grid}>
      {board.map((row, i) => row.map((cell, j) => (
        <SudokuCell key={`${i}-${j}`} value={cell} onChange={...} />
      )))}
    </div>
  );
};
''',
        'src/components/generated/sudoku/SudokuGrid.module.css': '''
.grid {
  display: grid;
  grid-template-columns: repeat(9, 48px);
  border: 3px solid black;
}
''',
        'src/components/generated/sudoku/SudokuCell.tsx': '''
import React from 'react';
import styles from './SudokuCell.module.css';

export const SudokuCell = ({ value, isOriginal, onChange }) => {
  return (
    <input
      className={styles.cell}
      value={value || ''}
      onChange={onChange}
      readOnly={isOriginal}
      maxLength={1}
    />
  );
};
''',
        'src/components/generated/sudoku/SudokuCell.module.css': '''
.cell {
  width: 48px;
  height: 48px;
  border: 1px solid #999;
  text-align: center;
  font-size: 20px;
}

.cell:nth-child(3n) {
  border-right: 3px solid black;
}
'''
    }
    
    context = {
        'prompt_text': '请把当前 Sudoku 游戏的 UI 样式改为"经典纸质数独"风格',
        'app_type': 'game',
        'interaction_spec': {
            'state': [{'name': 'board', 'type': 'number[][]'}],
            'events': [{'name': 'cellChange', 'trigger': 'input'}],
            'constraints': ['original cells are readonly'],
            'acceptance': ['can click cell', 'can input number', 'original cells locked']
        },
        'generated_file_paths': list(files_correct.keys())
    }
    
    config = {
        'enabled': True,
        'gate5_structural_fail': True,
        'gate6_orphan_severity_mode': 'error_structural'
    }
    
    result = run_l0_gates(files_correct, context, config)
    result_dict = result.to_dict()
    
    # 不应该有任何失败
    if not result_dict['pass']:
        print(f"❌ 回归测试失败！")
        print(f"   失败项：{json.dumps(result_dict['fails'], indent=2, ensure_ascii=False)}")
        assert False, "Sudoku 经典风格回归测试失败"
    
    print("✓ Sudoku 经典纸质风格回归测试通过！")
    print(f"   - Gate1: ✓ 没有使用 shadcn Input")
    print(f"   - Gate2: ✓ CSS Modules 正确共存")
    print(f"   - Gate3: ✓ 没有危险 CSS")
    print(f"   - Gate4: ✓ 受控输入闭环正确")
    print(f"   - Gate5: ✓ readOnly 基于 isOriginal")
    print(f"   - Gate6: ✓ 所有组件被正确引用")


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("L0 交互/样式门禁回归测试")
    print("="*60)
    
    try:
        test_gate1_structural_no_shadcn_input()
        test_gate2_css_modules_colocated()
        test_gate3_forbidden_css()
        test_gate4_controlled_input()
        test_gate5_readonly_logic()
        test_gate6_orphan_files()
        test_gate7_import_export_consistency()
        test_sudoku_classic_style_regression()
        
        print("\n" + "="*60)
        print("✅ 所有测试通过！L0 门禁工作正常")
        print("="*60 + "\n")
        return 0
    
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())

