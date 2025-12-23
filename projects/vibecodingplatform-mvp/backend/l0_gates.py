"""
L0 交互/样式门禁 - 专门针对结构性应用（数独/棋盘/网格）的样式和交互检查
防止 shadcn/ui Input 覆盖 CSS Modules 等问题
"""
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional


class L0GateResult:
    """L0 门禁结果"""
    
    def __init__(self):
        self.pass_status = True
        self.fails: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.hints: List[str] = []
    
    def add_fail(self, gate: str, files: List[str], message: str, snippet: str = None, suggestion: str = None):
        """添加失败项"""
        self.pass_status = False
        fail_item = {
            "gate": gate,
            "files": files,
            "message": message
        }
        if snippet:
            fail_item["snippet"] = snippet
        if suggestion:
            fail_item["suggestion"] = suggestion
        self.fails.append(fail_item)
    
    def add_warning(self, gate: str, files: List[str], message: str, snippet: str = None, suggestion: str = None):
        """添加警告项"""
        warning_item = {
            "gate": gate,
            "files": files,
            "message": message
        }
        if snippet:
            warning_item["snippet"] = snippet
        if suggestion:
            warning_item["suggestion"] = suggestion
        self.warnings.append(warning_item)
    
    def add_hint(self, hint: str):
        """添加提示"""
        if hint not in self.hints:
            self.hints.append(hint)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "pass": self.pass_status,
            "fails": self.fails,
            "warnings": self.warnings,
            "hints": self.hints
        }


class L0StyleInteractionGates:
    """L0 交互/样式门禁检查器"""
    
    # 结构性应用关键词（中英文）
    STRUCTURAL_KEYWORDS = [
        # 英文
        'sudoku', 'minesweeper', '2048', 'grid', 'board', 'pixel', 'canvas',
        'calendar', 'gantt', 'kanban', 'spreadsheet', 'datagrid', 'timeline',
        'flow', 'diagram', 'drag', 'chess', 'checkers', 'tic-tac-toe',
        # 中文
        '棋盘', '网格', '数独', '像素', '画布', '日历', '甘特', '看板', '拖拽', '表格',
        '扫雷', '象棋', '围棋', '五子棋', '井字棋'
    ]
    
    # 结构性应用文件名关键词
    STRUCTURAL_FILENAME_KEYWORDS = [
        'Sudoku', 'Grid', 'Board', 'Cell', 'Canvas', 'Kanban', 'Calendar',
        'Gantt', 'Spreadsheet', 'Minesweeper', 'Chess', 'Checkers', 'Pixel',
        'Drag', 'Drop', 'Timeline', 'Flow', 'Diagram'
    ]
    
    # 危险 CSS 模式
    FORBIDDEN_CSS_PATTERNS = [
        r':global\s*\(',  # :global() 污染全局
        r'@import',       # @import 引入外部文件
        r'url\s*\(\s*["\']?https?:',  # url(http...) 远程资源
    ]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化 L0 门禁
        
        Args:
            config: 配置字典（从 generation_policy.json 读取）
        """
        self.config = config or {}
        self.enabled = self.config.get('enabled', True)
        
        # 加载配置（如果有自定义配置则覆盖默认值）
        if 'structural_keywords' in self.config:
            self.STRUCTURAL_KEYWORDS.extend(self.config['structural_keywords'])
        if 'structural_filename_keywords' in self.config:
            self.STRUCTURAL_FILENAME_KEYWORDS.extend(self.config['structural_filename_keywords'])
        if 'forbidden_css_patterns' in self.config:
            self.FORBIDDEN_CSS_PATTERNS = self.config['forbidden_css_patterns']
        
        # Gate5/Gate6 的严重级别模式
        self.gate5_structural_fail = self.config.get('gate5_structural_fail', True)
        self.gate6_orphan_severity_mode = self.config.get('gate6_orphan_severity_mode', 'error_structural')
    
    def is_structural_app(self, context: Dict[str, Any]) -> bool:
        """
        判断是否为结构性应用
        
        使用多重信号：prompt + InteractionSpec + 文件名/路径
        
        Args:
            context: 上下文信息 {prompt_text, app_type, interaction_spec, generated_file_paths}
        
        Returns:
            是否为结构性应用
        """
        # 信号 1: prompt_text 包含关键词
        prompt_text = context.get('prompt_text', '').lower()
        if any(keyword.lower() in prompt_text for keyword in self.STRUCTURAL_KEYWORDS):
            return True
        
        # 信号 2: InteractionSpec 中的 state/events/constraints 包含关键词
        interaction_spec = context.get('interaction_spec')
        if interaction_spec:
            spec_text = json.dumps(interaction_spec, ensure_ascii=False).lower()
            if any(keyword.lower() in spec_text for keyword in self.STRUCTURAL_KEYWORDS):
                return True
        
        # 信号 3: 文件名/路径包含关键词
        file_paths = context.get('generated_file_paths', [])
        for file_path in file_paths:
            if any(keyword in file_path for keyword in self.STRUCTURAL_FILENAME_KEYWORDS):
                return True
        
        return False
    
    def check(self, files: Dict[str, str], context: Dict[str, Any]) -> L0GateResult:
        """
        运行 L0 交互/样式门禁检查
        
        Args:
            files: 文件字典 {filename: content}
            context: 上下文 {prompt_text, app_type, interaction_spec, generated_file_paths}
        
        Returns:
            L0GateResult
        """
        if not self.enabled:
            result = L0GateResult()
            result.add_hint("L0 交互/样式门禁未启用")
            return result
        
        result = L0GateResult()
        
        # 判断是否为结构性应用
        is_structural = self.is_structural_app(context)
        
        # 添加通用提示
        if is_structural:
            result.add_hint("检测到结构性应用（网格/棋盘/画布类），将应用更严格的交互/样式规则")
        result.add_hint("对于网格/棋盘 UI：使用原生 input/button 并将 CSS Modules 类施加在可见元素本体")
        result.add_hint("禁止编辑 src/index.css 或 src/components/ui/**")
        
        # 分离 TS/TSX 和 CSS 文件
        ts_files = {f: c for f, c in files.items() if f.endswith(('.tsx', '.ts', '.jsx', '.js'))}
        css_files = {f: c for f, c in files.items() if f.endswith('.module.css')}
        
        # Gate1: 结构性应用禁用 shadcn Input
        if is_structural:
            self._check_gate1_no_shadcn_input(ts_files, result)
        
        # Gate2: CSS Modules 同名同目录 + 必须 import
        self._check_gate2_css_modules_colocated(css_files, ts_files, result)
        
        # Gate3: 禁止危险 CSS
        self._check_gate3_forbidden_css(css_files, result)
        
        # Gate4: 受控输入闭环
        self._check_gate4_controlled_input(ts_files, result)
        
        # Gate5: 防"填了就锁死"的 readOnly 逻辑
        self._check_gate5_readonly_logic(ts_files, result, is_structural)
        
        # Gate6: 新增文件必须被引用
        self._check_gate6_orphan_files(files, context, result, is_structural)

        # Gate7: import/export 一致性（防止运行时报 “does not provide an export named ...”）
        self._check_gate7_import_export_consistency(files, result)

        # Gate8: 关键组件 props 必须接线（防止 map(undefined) 黑屏）
        self._check_gate8_required_props_wired(files, result)
        
        # Gate9: shadcn/ui 组件导入白名单检查（防止导入不存在的组件）
        self._check_gate9_shadcn_ui_whitelist(ts_files, result)
        
        return result
    
    def _check_gate1_no_shadcn_input(self, ts_files: Dict[str, str], result: L0GateResult):
        """
        Gate1: 结构性应用禁止使用 shadcn Input，且数独类应该使用 <input> 而不是 <div>
        """
        violating_files = []
        div_cell_files = []
        
        for filename, content in ts_files.items():
            # 检查是否导入了 @/components/ui/input
            if re.search(r"from\s+['\"]@/components/ui/input['\"]", content):
                violating_files.append(filename)
                continue
            
            # 检查是否使用了 <Input 标签
            if re.search(r'<Input\s', content):
                violating_files.append(filename)
            
            # 检查网格/表格类应用是否错误地使用了 <div> 作为单元格（应该用 <input>/<button>）
            # 特征：文件名包含 Cell，且有 <div...onClick...>{value...}</div> 模式（交互式格子）
            if 'Cell' in filename:
                # 查找可点击的 div 显示 value（应该用 input/button）
                if re.search(r'<div[^>]*onClick[^>]*>[\s\n]*\{[^}]*value[^}]*\}[\s\n]*</div>', content, re.IGNORECASE):
                    div_cell_files.append(filename)
        
        if violating_files:
            result.add_fail(
                gate="G1_STRUCTURAL_NO_SHADCN_INPUT",
                files=violating_files,
                message="结构性应用（网格/棋盘/画布）不得使用 shadcn Input 组件，必须使用原生 <input>/<button>",
                suggestion="将 <Input> 替换为原生 <input> 或 <button>，并将 CSS Modules 的 className 施加在原生元素本体上，而不是仅在 wrapper div。示例：<input className={styles.cell} ... /> 而不是 <div className={styles.cell}><Input /></div>"
            )
        
        if div_cell_files:
            result.add_fail(
                gate="G1_INTERACTIVE_CELL_MUST_USE_INPUT",
                files=div_cell_files,
                message="交互式单元格必须使用 <input>/<button> 元素，而不是可点击的 <div>（违反语义化和可访问性）",
                suggestion="将 <div onClick={...}>{value}</div> 替换为 <input className={styles.cell} value={value || ''} onChange={handleChange} /> 或 <button className={styles.cell} onClick={...}>{value}</button>。这样用户可以直接交互，且符合 HTML 语义和可访问性标准。"
            )
    
    def _check_gate2_css_modules_colocated(self, css_files: Dict[str, str], ts_files: Dict[str, str], result: L0GateResult):
        """
        Gate2: CSS Modules 必须与组件同名同目录，且必须被 import（双向检查）
        """
        # 正向检查：CSS Module 文件必须有对应的组件
        for css_filename in css_files.keys():
            # 只检查 src/components/generated/** 下的 CSS Modules
            if not css_filename.startswith('src/components/generated/'):
                continue
            
            # 提取组件名（去掉 .module.css）
            if not css_filename.endswith('.module.css'):
                continue
            
            # 获取目录和基础名
            css_path = Path(css_filename)
            css_dir = str(css_path.parent)
            base_name = css_path.stem.replace('.module', '')  # e.g., "SudokuGrid"
            
            # 查找同目录的 .tsx 文件
            expected_tsx = f"{css_dir}/{base_name}.tsx"
            expected_jsx = f"{css_dir}/{base_name}.jsx"
            
            component_file = None
            if expected_tsx in ts_files:
                component_file = expected_tsx
            elif expected_jsx in ts_files:
                component_file = expected_jsx
            
            if not component_file:
                result.add_fail(
                    gate="G2_CSS_MODULE_ORPHAN",
                    files=[css_filename],
                    message=f"CSS Module {css_filename} 没有对应的同目录同名组件文件（期望 {expected_tsx}）",
                    suggestion=f"创建 {expected_tsx} 或删除此 CSS Module 文件"
                )
                continue
            
            # 检查组件文件是否 import 了此 CSS Module
            component_content = ts_files[component_file]
            
            # 先检查是否有注释掉的导入
            commented_import_pattern = rf"//.*import\s+\w+\s+from\s+['\"]\./{base_name}\.module\.css['\"]"
            has_commented_import = re.search(commented_import_pattern, component_content)
            
            # 检查正常导入（必须从行首或空白开始，不能是注释）
            css_import_pattern = rf"^[ \t]*import\s+\w+\s+from\s+['\"]\./{base_name}\.module\.css['\"]"
            has_normal_import = re.search(css_import_pattern, component_content, re.MULTILINE)
            
            if not has_normal_import:
                if has_commented_import:
                    result.add_fail(
                        gate="G2_CSS_MODULE_COMMENTED_OUT",
                        files=[component_file],
                        message=f"❌ 严重错误：组件 {component_file} 的 CSS Module 导入被注释掉了！这会导致样式完全失效。",
                        snippet=f"发现: // import styles from './{base_name}.module.css'",
                        suggestion=f"⚠️ 取消注释！NEVER 删除或注释掉 CSS Modules 导入。CSS Modules 是必需的，不是可选的。恢复为：import styles from './{base_name}.module.css'"
                    )
                else:
                    result.add_fail(
                        gate="G2_CSS_MODULE_NOT_IMPORTED",
                        files=[component_file],
                        message=f"组件 {component_file} 没有导入对应的 CSS Module {css_filename}",
                        snippet=f"缺少: import styles from './{base_name}.module.css'",
                        suggestion=f"在 {component_file} 顶部添加: import styles from './{base_name}.module.css'"
                    )
        
        # 反向检查：组件 import 的 CSS Module 必须存在
        for component_file, component_content in ts_files.items():
            # 只检查 src/components/generated/** 下的组件
            if not component_file.startswith('src/components/generated/'):
                continue
            
            # 查找 CSS Module import 语句
            css_import_pattern = r"import\s+\w+\s+from\s+['\"]\./([\w-]+)\.module\.css['\"]"
            matches = re.finditer(css_import_pattern, component_content)
            
            for match in matches:
                imported_css_name = match.group(1)  # e.g., "SudokuControls"
                
                # 构建期望的 CSS Module 文件路径
                component_dir = str(Path(component_file).parent)
                expected_css = f"{component_dir}/{imported_css_name}.module.css"
                
                # 检查文件是否存在
                if expected_css not in css_files:
                    result.add_fail(
                        gate="G2_CSS_MODULE_MISSING",
                        files=[component_file],
                        message=f"组件 {component_file} 导入的 CSS Module 文件不存在: {expected_css}",
                        snippet=match.group(0),
                        suggestion=f"创建 {expected_css} 文件，或删除组件中的 import 语句"
                    )
    
    def _check_gate3_forbidden_css(self, css_files: Dict[str, str], result: L0GateResult):
        """
        Gate3: 禁止危险 CSS（:global、@import、url(http...)）+ 颜色对比度检查
        """
        for css_filename, content in css_files.items():
            # 只检查 generated 目录下的 CSS Modules
            if 'generated' not in css_filename:
                continue
            
            # 检查危险模式
            for pattern in self.FORBIDDEN_CSS_PATTERNS:
                matches = list(re.finditer(pattern, content, re.IGNORECASE))
                if matches:
                    for match in matches:
                        line_no = content[:match.start()].count('\n') + 1
                        result.add_fail(
                            gate="G3_FORBIDDEN_CSS",
                            files=[css_filename],
                            message=f"CSS Module 中禁止使用 {match.group(0)}（第 {line_no} 行）",
                            snippet=match.group(0),
                            suggestion="移除 :global()、@import 或远程 url()。使用局部类名和本地资源"
                        )
            
            # 检查颜色对比度（简单版本：检测相同颜色用于 color 和 background）
            self._check_color_contrast(css_filename, content, result)
    
    def _check_color_contrast(self, css_filename: str, content: str, result: L0GateResult):
        """
        检查 CSS 颜色对比度（防止白底白字等问题）
        """
        # 提取 CSS 规则块
        # 简单方法：查找 { ... } 块，分析其中的 color 和 background-color
        rule_blocks = re.finditer(r'\{([^}]+)\}', content, re.DOTALL)
        
        for block in rule_blocks:
            block_content = block.group(1)
            block_start = block.start()
            line_no = content[:block_start].count('\n') + 1
            
            # 提取颜色值（简化版，只检查明显的白色）
            # 注意：必须排除 background-color 中的 color 子串
            # 使用 (?<!-) 负向后瞻，确保 color 前面没有 -
            color_match = re.search(r'(?<![a-z-])color\s*:\s*([^;]+);', block_content, re.IGNORECASE)
            bg_match = re.search(r'background(-color)?\s*:\s*([^;]+);', block_content, re.IGNORECASE)
            
            # 只有同时明确指定了 color 和 background 才检查
            # 如果只有 background 没有 color，不检查（因为 color 可能是继承的）
            if color_match and bg_match:
                color_value = color_match.group(1).strip().lower()
                bg_value = bg_match.group(2).strip().lower()
                
                # 标准化颜色值
                def normalize_color(c):
                    c = c.replace(' ', '')
                    # 白色的各种表示
                    if c in ['#fff', '#ffffff', 'white', 'rgb(255,255,255)', 'rgba(255,255,255,1)']:
                        return 'white'
                    # 黑色的各种表示
                    if c in ['#000', '#000000', 'black', 'rgb(0,0,0)', 'rgba(0,0,0,1)']:
                        return 'black'
                    return c
                
                norm_color = normalize_color(color_value)
                norm_bg = normalize_color(bg_value)
                
                # 检查是否相同或对比度不足
                if norm_color == norm_bg:
                    result.add_fail(
                        gate="G3_COLOR_CONTRAST",
                        files=[css_filename],
                        message=f"文字颜色与背景颜色相同或对比度不足（第 {line_no} 行）：color={color_value}, background={bg_value}",
                        snippet=block_content[:80],
                        suggestion=f"如果背景是白色/浅色，文字必须用深色（如 color: #000 或 #1f2937）；如果背景是深色，文字必须用浅色"
                    )
                elif norm_color == 'white' and norm_bg == 'white':
                    result.add_fail(
                        gate="G3_WHITE_ON_WHITE",
                        files=[css_filename],
                        message=f"白底白字，文字不可见（第 {line_no} 行）",
                        snippet=f"color: {color_value}; background: {bg_value}",
                        suggestion="将 color 改为深色，例如：color: #000 (黑色) 或 color: #1f2937 (深灰)"
                    )
    
    def _check_gate4_controlled_input(self, ts_files: Dict[str, str], result: L0GateResult):
        """
        Gate4: 受控输入必须闭环（value= 必须配 onChange=，即使有动态 readOnly）
        """
        for filename, content in ts_files.items():
            # 使用 regex 查找 <input...> 或 <Input...> 标签（可能跨多行）
            input_pattern = r'<(input|Input)\s+([^>]*?)/?>'
            matches = re.finditer(input_pattern, content, re.IGNORECASE | re.DOTALL)
            
            for match in matches:
                tag_content = match.group(0)
                line_no = content[:match.start()].count('\n') + 1
                
                # 检查是否有 value= 属性
                if 'value=' not in tag_content:
                    continue
                
                # 检查是否有 onChange/onInput
                has_onchange = 'onChange' in tag_content or 'onInput' in tag_content
                
                # 检查 readOnly 是否为常量 true（不是动态值）
                readonly_match = re.search(r'readOnly\s*=\s*\{([^}]+)\}', tag_content)
                is_constant_readonly = False
                if readonly_match:
                    readonly_value = readonly_match.group(1).strip()
                    # 只有 readOnly={true} 才算常量只读
                    if readonly_value == 'true':
                        is_constant_readonly = True
                
                # 如果有 value 但没有 onChange，且不是常量只读，则失败
                if not has_onchange and not is_constant_readonly:
                    severity = 'error'
                    suggestion = "添加 onChange={(e) => handleChange(e.target.value)} 以支持用户输入"
                    
                    # 如果有动态 readOnly，给出更详细的建议
                    if readonly_match:
                        suggestion = f"虽然有 readOnly={{...}}，但它是动态值（{readonly_match.group(1)[:30]}...），当为 false 时需要 onChange。请添加 onChange 处理器"
                    
                    result.add_fail(
                        gate="G4_CONTROLLED_INPUT_NO_HANDLER",
                        files=[filename],
                        message=f"受控输入 value= 缺少 onChange 处理器（第 {line_no} 行）",
                        snippet=tag_content[:120].replace('\n', ' '),
                        suggestion=suggestion
                    )
    
    def _check_gate5_readonly_logic(self, ts_files: Dict[str, str], result: L0GateResult, is_structural: bool):
        """
        Gate5: 防"填了就锁死"的 readOnly 逻辑
        检查 readOnly 条件是否合理（应基于 original/locked 而非当前 value）
        """
        for filename, content in ts_files.items():
            # 匹配 readOnly={...} 但条件中有 value/cell 却没有 original/locked/given 等语义
            pattern = r'readOnly\s*=\s*\{[^}]*(value|cell)[^}]*\}'
            matches = re.finditer(pattern, content, re.IGNORECASE)
            
            for match in matches:
                readonly_expr = match.group(0)
                
                # 检查是否包含正确的语义变量
                has_correct_semantic = any(
                    keyword in readonly_expr.lower()
                    for keyword in ['original', 'locked', 'given', 'isoriginal', 'islocked', 'initial']
                )
                
                if not has_correct_semantic:
                    line_no = content[:match.start()].count('\n') + 1
                    
                    if is_structural:
                        # 结构性应用：Fail
                        result.add_fail(
                            gate="G5_READONLY_WRONG_CONDITION",
                            files=[filename],
                            message=f"readOnly 条件可能导致'填了就锁死'（第 {line_no} 行）：应基于 original/locked 而非当前 value",
                            snippet=readonly_expr,
                            suggestion="使用 originalBoard 或 initialState 来判断锁定，例如：readOnly={originalBoard[row][col] !== null}"
                        )
                    else:
                        # 普通应用：Warning
                        result.add_warning(
                            gate="G5_READONLY_WRONG_CONDITION",
                            files=[filename],
                            message=f"readOnly 条件疑似基于当前值而非初始值（第 {line_no} 行）",
                            snippet=readonly_expr,
                            suggestion="考虑使用 original/initial 状态来判断锁定"
                        )
    
    def _check_gate6_orphan_files(self, files: Dict[str, str], context: Dict[str, Any], result: L0GateResult, is_structural: bool):
        """
        Gate6: 新增文件必须被引用（防孤儿文件）
        """
        # 只检查本次生成的 src/components/generated/<appSlug>/**/*.tsx 文件
        generated_components = []
        for filepath in files.keys():
            if filepath.startswith('src/components/generated/') and filepath.endswith(('.tsx', '.jsx')):
                # 排除 Index.tsx（它是入口）
                if 'Index.tsx' not in filepath:
                    generated_components.append(filepath)
        
        if not generated_components:
            return  # 没有生成业务组件，跳过
        
        # 在所有文件中搜索对这些组件的引用
        orphan_files = []
        for component_file in generated_components:
            # 提取组件名（去掉路径和扩展名）
            component_name = Path(component_file).stem  # e.g., "SudokuGrid"
            
            # 在所有 TS/TSX 文件中搜索引用
            is_referenced = False
            for other_file, content in files.items():
                if other_file == component_file:
                    continue  # 跳过自己
                
                if not other_file.endswith(('.tsx', '.ts', '.jsx', '.js')):
                    continue
                
                # 检查是否被 import（按文件路径或组件名）
                # 例如：import { SudokuGrid } from '@/components/generated/sudoku/SudokuGrid'
                # 或者：import SudokuGrid from './SudokuGrid'
                if component_name in content:
                    # 进一步检查是否真的是 import 语句（简单 regex）
                    import_pattern = rf"import\s+.*{component_name}"
                    if re.search(import_pattern, content):
                        is_referenced = True
                        break
            
            if not is_referenced:
                orphan_files.append(component_file)
        
        if orphan_files:
            if is_structural:
                # 结构性应用：Error（触发自愈）
                result.add_fail(
                    gate="G6_ORPHAN_FILES",
                    files=orphan_files,
                    message=f"检测到 {len(orphan_files)} 个未被引用的组件文件（孤儿文件）",
                    suggestion=f"在 src/pages/Index.tsx 或其他页面中导入并使用这些组件：{', '.join([Path(f).stem for f in orphan_files])}"
                )
            else:
                # 普通应用：Warning
                result.add_warning(
                    gate="G6_ORPHAN_FILES",
                    files=orphan_files,
                    message=f"检测到 {len(orphan_files)} 个未被引用的组件文件",
                    suggestion=f"考虑在页面中接线这些组件，或删除它们：{', '.join([Path(f).stem for f in orphan_files])}"
                )

    def _check_gate7_import_export_consistency(self, files: Dict[str, str], result: L0GateResult):
        """
        Gate7: 检查 generated 组件之间的相对导入是否与目标文件导出一致
        - import { X } from './X' => 目标文件必须 export 命名导出 X
        - import X from './X' => 目标文件必须 export default
        """
        ts_files = {f: c for f, c in files.items() if f.endswith(('.tsx', '.ts', '.jsx', '.js'))}

        def resolve_relative_import(importer_file: str, import_path: str) -> Optional[str]:
            # 处理相对路径（./xxx）和别名路径（@/xxx）
            if import_path.startswith('.'):
                # 相对路径
                base_dir = Path(importer_file).parent
                raw = (base_dir / import_path).as_posix()
            elif import_path.startswith('@/'):
                # @/ 别名指向 src/
                raw = 'src/' + import_path[2:]
            else:
                # 外部包，跳过
                return None

            # 可能带扩展名，也可能不带；优先按 tsx/ts/jsx/js 依次匹配
            candidates = []
            if raw.endswith(('.tsx', '.ts', '.jsx', '.js')):
                candidates.append(raw)
            else:
                candidates.extend([raw + ext for ext in ['.tsx', '.ts', '.jsx', '.js']])
                # 也可能是目录 index
                candidates.extend([(raw + '/index' + ext) for ext in ['.tsx', '.ts', '.jsx', '.js']])

            for cand in candidates:
                if cand in ts_files:
                    return cand
            return None

        def has_named_export(target_content: str, name: str) -> bool:
            # 常见命名导出形式
            patterns = [
                rf'export\s+const\s+{re.escape(name)}\b',
                rf'export\s+function\s+{re.escape(name)}\b',
                rf'export\s+class\s+{re.escape(name)}\b',
                rf'export\s+\{{[^}}]*\b{re.escape(name)}\b[^}}]*\}}',
                rf'export\s+type\s+{re.escape(name)}\b',
                rf'export\s+interface\s+{re.escape(name)}\b',
            ]
            return any(re.search(p, target_content) for p in patterns)

        def has_default_export(target_content: str) -> bool:
            return bool(re.search(r'export\s+default\b', target_content))

        # 检查 pages 和 generated 业务组件的相对导入（避免误扫其他模板文件）
        for importer_file, importer_content in ts_files.items():
            if not (importer_file.startswith('src/components/generated/') or 
                    importer_file.startswith('src/pages/')):
                continue

            # named import: import { A, B as C } from './X'
            for m in re.finditer(r'import\s*\{\s*([^}]+?)\s*\}\s*from\s*[\'"]([^\'"]+)[\'"]', importer_content):
                spec = m.group(1)
                import_path = m.group(2)
                target_file = resolve_relative_import(importer_file, import_path)
                if not target_file:
                    continue
                target_content = ts_files[target_file]

                # split named specifiers
                names = []
                for part in spec.split(','):
                    part = part.strip()
                    if not part:
                        continue
                    # handle "A as B"
                    base = part.split(' as ')[0].strip()
                    if base:
                        names.append(base)

                missing = [n for n in names if not has_named_export(target_content, n)]
                if missing:
                    line_no = importer_content[:m.start()].count('\n') + 1
                    result.add_fail(
                        gate="G7_IMPORT_EXPORT_MISMATCH",
                        files=[importer_file, target_file],
                        message=f"相对导入的命名导出不存在（第 {line_no} 行）：{target_file} 未导出 {', '.join(missing)}",
                        snippet=m.group(0)[:120],
                        suggestion=f"要么在 {target_file} 中添加 `export const {missing[0]} = ...`（命名导出），要么把 {importer_file} 的导入改为 default import（并确保目标文件有 export default）。建议 generated 组件统一使用命名导出并用 `import {{ X }}` 导入。"
                    )

            # default import: import X from './X'
            for m in re.finditer(r'import\s+([A-Za-z_$][\w$]*)\s+from\s*[\'"]([^\'"]+)[\'"]', importer_content):
                # 跳过 "import type ..." 或同时含 { } 的情况（named import 已处理）
                if importer_content[m.start():m.start()+20].startswith('import type'):
                    continue
                if '{' in m.group(0):
                    continue
                local_name = m.group(1)
                import_path = m.group(2)
                target_file = resolve_relative_import(importer_file, import_path)
                if not target_file:
                    continue
                target_content = ts_files[target_file]

                if not has_default_export(target_content):
                    line_no = importer_content[:m.start()].count('\n') + 1
                    result.add_fail(
                        gate="G7_IMPORT_EXPORT_MISMATCH",
                        files=[importer_file, target_file],
                        message=f"相对导入 default export 不存在（第 {line_no} 行）：{target_file} 缺少 `export default`",
                        snippet=m.group(0)[:120],
                        suggestion=f"要么在 {target_file} 添加 `export default ...`，要么把 {importer_file} 的导入改为命名导入 `import {{ {local_name} }}` 并在目标文件导出同名符号。建议 generated 组件统一命名导出。"
                    )

    def _check_gate8_required_props_wired(self, files: Dict[str, str], result: L0GateResult):
        """
        Gate8: 检查 SudokuGrid 等关键组件的必需 props 是否在 Index.tsx 中接线
        目标：避免运行时出现 `Cannot read properties of undefined (reading 'map')`

        规则（先做 SudokuGrid 专项，后续可泛化）：
        - 解析 src/components/generated/**/SudokuGrid.tsx 中 interface SudokuGridProps 的必需字段（无 ?）
        - 检查 src/pages/Index.tsx 中 <SudokuGrid ...> 是否传入这些字段
        """
        index_file = 'src/pages/Index.tsx'
        if index_file not in files:
            return

        index = files[index_file]

        # 找 SudokuGrid 文件（可能在不同 appSlug 下）
        sudoku_grid_files = [p for p in files.keys() if p.endswith('/SudokuGrid.tsx') and p.startswith('src/components/generated/')]
        for grid_file in sudoku_grid_files:
            grid = files.get(grid_file, '')

            # 提取 interface SudokuGridProps {...}
            m = re.search(r'interface\s+SudokuGridProps\s*\{([\s\S]*?)\}', grid)
            if not m:
                continue
            body = m.group(1)

            required_props: List[str] = []
            for line in body.splitlines():
                line = line.strip()
                if not line or line.startswith('//'):
                    continue
                # 匹配 prop: Type;  或 prop?: Type;
                pm = re.match(r'([A-Za-z_$][\w$]*)\s*(\?)?\s*:\s*[^;]+;', line)
                if not pm:
                    continue
                name = pm.group(1)
                optional = pm.group(2) == '?'
                if not optional:
                    required_props.append(name)

            if not required_props:
                continue

            # 在 Index 里找 <SudokuGrid ...>
            jsx_match = re.search(r'<SudokuGrid\b([\s\S]*?)(/?>)', index)
            if not jsx_match:
                continue
            attrs_blob = jsx_match.group(1)

            # 提取传入的 prop 名（foo=）
            provided = set(re.findall(r'\b([A-Za-z_$][\w$]*)\s*=', attrs_blob))

            missing = [p for p in required_props if p not in provided]
            if missing:
                # 给一个更具体的提示：如果缺的是 sudokuBoard，但提供了 board，提示改名
                hint = ""
                if 'sudokuBoard' in missing and 'board' in provided:
                    hint = "检测到你传了 board=，但组件需要 sudokuBoard=。请统一命名（推荐统一用 board）。"
                if 'board' in missing and 'sudokuBoard' in provided:
                    hint = "检测到你传了 sudokuBoard=，但组件需要 board=。请统一命名（推荐统一用 board）。"

                result.add_fail(
                    gate="G8_REQUIRED_PROPS_NOT_WIRED",
                    files=[index_file, grid_file],
                    message=f"Index.tsx 未给 <SudokuGrid> 传入必需 props：{', '.join(missing)}（会导致运行时 undefined.map 崩溃）",
                    snippet=f"<SudokuGrid{attrs_blob[:120]}...>",
                    suggestion=("请让 Index.tsx 与 SudokuGridProps 完全一致：补齐缺失 props 或把组件的 props 命名改回与 Index 一致。"
                                + (f" {hint}" if hint else ""))
                )

    def _check_gate9_shadcn_ui_whitelist(self, ts_files: Dict[str, str], result: L0GateResult):
        """
        Gate9: 检查 shadcn/ui 组件导入是否在白名单中
        防止导入不存在的组件导致运行时错误
        """
        # 从 policies 读取允许的组件列表
        from policies import policy_manager
        allowed_components = policy_manager.get_allowed_shadcn_components()
        
        import logging
        logger = logging.getLogger(__name__)
        
        for filename, content in ts_files.items():
            # 移除所有注释后再检查
            cleaned_content = self._remove_comments(content)
            
            # 在清理后的内容中查找所有导入（支持多行导入）
            # 匹配 import ... from '@/components/ui/xxx'
            pattern = r"from\s+['\"]@/components/ui/([\w-]+)['\"]"
            matches = re.finditer(pattern, cleaned_content)
            
            for match in matches:
                component_name = match.group(1)
                # 计算行号（在清理后的内容中）
                line_no = cleaned_content[:match.start()].count('\n') + 1
                
                logger.debug(f"Gate9: 检测到 shadcn 导入 {component_name} 在 {filename}:{line_no}")
                
                if component_name not in allowed_components:
                    logger.warning(f"Gate9: 组件 {component_name} 不在白名单中！")
                    
                    # 获取匹配内容的上下文作为snippet
                    # 找到包含此导入的行范围
                    start_pos = max(0, match.start() - 50)
                    end_pos = min(len(cleaned_content), match.end() + 50)
                    snippet = cleaned_content[start_pos:end_pos].strip()[:100]
                    
                    result.add_fail(
                        gate="G9_SHADCN_COMPONENT_NOT_WHITELISTED",
                        files=[filename],
                        message=f"导入的 shadcn/ui 组件不存在: @/components/ui/{component_name}（第 {line_no} 行）",
                        snippet=snippet,
                        suggestion=f"可用组件：{', '.join(sorted(allowed_components)[:10])}... 请使用已存在的组件或请求添加新组件"
                    )
                else:
                    logger.debug(f"Gate9: 组件 {component_name} 在白名单中，通过检查")
    
    def _remove_comments(self, content: str) -> str:
        """
        移除 TypeScript/JavaScript 代码中的所有注释
        
        正确处理：
        1. 单行注释 // ...
        2. 多行注释 /* ... */
        3. 字符串中的注释语法（不移除）
        
        Args:
            content: 源代码字符串
            
        Returns:
            移除注释后的代码
        """
        result = []
        in_multiline_comment = False
        in_string = None  # None, '"', or "'"
        escaped = False
        i = 0
        
        while i < len(content):
            char = content[i]
            
            # 处理转义字符
            if escaped:
                result.append(char)
                escaped = False
                i += 1
                continue
            
            if char == '\\':
                result.append(char)
                escaped = True
                i += 1
                continue
            
            # 在字符串内部，不处理注释
            if in_string:
                result.append(char)
                if char == in_string:
                    in_string = None
                i += 1
                continue
            
            # 检测字符串开始
            if char in ('"', "'", '`'):
                in_string = char
                result.append(char)
                i += 1
                continue
            
            # 处理多行注释
            if in_multiline_comment:
                if char == '*' and i + 1 < len(content) and content[i + 1] == '/':
                    in_multiline_comment = False
                    i += 2  # 跳过 */
                    continue
                i += 1
                continue
            
            # 检测多行注释开始
            if char == '/' and i + 1 < len(content) and content[i + 1] == '*':
                in_multiline_comment = True
                i += 2  # 跳过 /*
                continue
            
            # 检测单行注释
            if char == '/' and i + 1 < len(content) and content[i + 1] == '/':
                # 跳过到行尾
                while i < len(content) and content[i] != '\n':
                    i += 1
                # 保留换行符
                if i < len(content):
                    result.append('\n')
                    i += 1
                continue
            
            # 普通字符
            result.append(char)
            i += 1
        
        return ''.join(result)


def run_l0_gates(files: Dict[str, str], context: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> L0GateResult:
    """
    运行 L0 交互/样式门禁
    
    Args:
        files: 文件字典 {filename: content}
        context: 上下文 {prompt_text, app_type, interaction_spec, generated_file_paths}
        config: 配置字典（可选，从 generation_policy.json 读取）
    
    Returns:
        L0GateResult
    """
    gates = L0StyleInteractionGates(config)
    return gates.check(files, context)

