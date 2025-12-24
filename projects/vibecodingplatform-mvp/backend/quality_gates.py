"""
质量门禁 - 检测生成代码的交互性问题
"""
import re
from typing import Dict, List, Tuple, Any
from policies import policy_manager


class GateResult:
    """门禁检查结果"""
    
    def __init__(self, level: str, passed: bool, issues: List[Dict[str, Any]] = None):
        self.level = level
        self.passed = passed
        self.issues = issues or []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level,
            "passed": self.passed,
            "issues_count": len(self.issues),
            "issues": self.issues
        }


class L0StaticGate:
    """
    L0 静态闸门 - AST/Regex 混合扫描
    检测 5 类高频交互性问题
    """
    
    def __init__(self):
        self.rules = policy_manager.get_static_gate_rules()
    
    def check(self, files: Dict[str, str]) -> GateResult:
        """
        检查文件中的静态问题
        
        Args:
            files: 文件字典 {filename: content}
            
        Returns:
            GateResult
        """
        issues = []
        
        # 只检查业务代码文件，排除 UI 库组件和配置文件
        excluded_patterns = [
            'src/components/ui/',      # UI 库组件
            'src/lib/utils',           # 工具函数
            'tailwind.config',         # 配置文件
            'vite.config',
            'tsconfig',
            'postcss.config',
            'package.json',
            'vibe.meta.json',
        ]
        
        react_files = {}
        for filename, content in files.items():
            if filename.endswith(('.tsx', '.jsx', '.ts', '.js')):
                # 检查是否应该排除
                should_exclude = any(pattern in filename for pattern in excluded_patterns)
                if not should_exclude:
                    react_files[filename] = content
        
        for filename, content in react_files.items():
            # 跳过规则 1-2（已由新的 Gate4/Gate5 检查）
            # issues.extend(self._check_controlled_input_missing_onchange(filename, content))
            # issues.extend(self._check_readonly_wrong_condition(filename, content))
            
            # 规则 3: onClick handler 内无状态更新（L0StaticGate 独有）
            issues.extend(self._check_onclick_no_state_update(filename, content))
            
            # 规则 4: 空 handler 或 TODO（L0StaticGate 独有）
            issues.extend(self._check_empty_handler(filename, content))
            
            # 跳过规则 5（较模糊，交给新门禁）
            # issues.extend(self._check_no_state_management(filename, content))
        
            # 规则 6: 导入边界违规（L0StaticGate 独有，重要）
            issues.extend(self._check_import_boundary_violation(filename, content))
            
            # 规则 7: Index.tsx 过大（L0StaticGate 独有，重要）
            if 'Index.tsx' in filename:
                issues.extend(self._check_index_too_large(filename, content))
        
             # 规则 8: 输入框文字对比度检查（防止文字与背景色冲突）
            issues.extend(self._check_input_text_contrast(filename, content))
             
             # 规则 9: 文本元素显式颜色检查（防止依赖全局继承）
            issues.extend(self._check_missing_text_color(filename, content))
             
             # 规则 10: 对比度问题检查（防止深色on深色/浅色on浅色）
            issues.extend(self._check_text_contrast_issues(filename, content))
            
            # 规则 11: API 使用错误检测（防止混淆不同库的 API）
            issues.extend(self._check_api_usage_errors(filename, content))
        
        # 规则 12: 导出一致性检查（新增，重要）
        issues.extend(self._check_export_consistency(files))
        
        # 规则 13: 导入导出匹配检查（防止 Index.tsx 导入不存在的导出）
        issues.extend(self._check_import_export_consistency(files))
        
        # 规则 14: 依赖一致性检查（确保依赖信息正确写入）
        issues.extend(self._check_dependency_consistency(files))
        
        # 规则 15: 重复定义检测（防止同一函数定义多次）
        issues.extend(self._check_duplicate_definitions(files))
        
        # 规则 16: 数据契约检测（防止返回数据缺少必需字段）
        issues.extend(self._check_data_contract(files))
        
        # 规则 17: 防御性编程检查（防止缺少空值检查）
        issues.extend(self._check_defensive_programming(files))
        
        # 跳过 CSS :global 和未引用文件检查（已由 Gate3/Gate6 检查）
        # css_files = {f: c for f, c in files.items() if f.endswith('.module.css')}
        # for filename, content in css_files.items():
        #     issues.extend(self._check_css_module_global_usage(filename, content))
        # issues.extend(self._check_unreferenced_generated_files(files))
        
        # 只有 ERROR 级别的 issue 才算失败，WARNING 不影响通过
        errors = [issue for issue in issues if issue.get('severity') == 'error']
        passed = len(errors) == 0
        
        return GateResult("L0_static", passed, issues)
    
    def _check_controlled_input_missing_onchange(self, filename: str, content: str) -> List[Dict[str, Any]]:
        """检查受控输入是否缺少 onChange"""
        issues = []
        
        # 更精确的检查：查找 <input 或 <Input 标签，检查是否有 value 但缺少 onChange
        # 使用更简单的方法：逐行检查，而不是复杂的正则
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # 跳过注释行
            if line_stripped.startswith('//') or line_stripped.startswith('/*'):
                continue
            
            # 检查是否有 <input 或 <Input 标签且有 value 属性
            if ('<input' in line_stripped.lower() or '<Input' in line_stripped) and 'value=' in line_stripped:
                # 检查是否有 onChange 或 readOnly（可能在同一行或附近几行）
                context_start = max(0, i - 2)
                context_end = min(len(lines), i + 3)
                context = '\n'.join(lines[context_start:context_end])
                
                has_onchange = 'onChange' in context or 'onInput' in context
                has_readonly = 'readOnly' in context or 'disabled' in context
                
                if not has_onchange and not has_readonly:
                    issues.append({
                        "rule_id": "controlled_input_missing_onchange",
                        "severity": "error",
                        "file": filename,
                        "line": i + 1,
                        "message": "受控输入 value= 缺少 onChange 且非 readOnly",
                        "snippet": line_stripped[:100]
                    })
        
        return issues
    
    def _check_readonly_wrong_condition(self, filename: str, content: str) -> List[Dict[str, Any]]:
        """检查 readOnly 锁定条件是否正确"""
        issues = []
        
        # 检测 readOnly={cell ...} 但缺少 original 关键词的情况
        pattern = r'readOnly\s*=\s*\{[^}]*\bcell\b(?!.*\boriginal\b)[^}]*\}'
        
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            line_no = content[:match.start()].count('\n') + 1
            issues.append({
                "rule_id": "readonly_wrong_condition",
                "severity": "warning",
                "file": filename,
                "line": line_no,
                "message": "readOnly 锁定条件可能错误：用当前 cell 而非 original",
                "snippet": match.group(0),
                "suggestion": "应使用 originalBoard 或类似的初始状态来锁定"
            })
        
        return issues
    
    def _check_onclick_no_state_update(self, filename: str, content: str) -> List[Dict[str, Any]]:
        """检查 onClick handler 内是否有状态更新"""
        issues = []
        
        # 简化检测：只检查明显的空 handler
        # 匹配 onClick={() => {}} 或 onClick={handleXXX} 这种调用函数的情况跳过
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'onClick' in line:
                # 检查是否是空 handler
                if 'onClick={}' in line.replace(' ', '') or 'onClick={()=>{}}' in line.replace(' ', ''):
                    issues.append({
                        "rule_id": "onclick_no_state_update",
                        "severity": "warning",
                        "file": filename,
                        "line": i + 1,
                        "message": "onClick handler 为空",
                        "snippet": line.strip()[:100]
                    })
        
        return issues
    
    def _check_empty_handler(self, filename: str, content: str) -> List[Dict[str, Any]]:
        """
        检查是否有未实现的事件处理器
        
        采用两阶段检测策略：
        1. 先用正则找出所有事件处理器
        2. 再用启发式规则判断是否已实现（包含函数调用、状态更新、赋值等）
        
        这样可以避免误报（如 todo 变量名被当作 TODO 注释）
        """
        issues = []
        
        # 阶段 1: 找出所有单行的事件处理器（不跨行的简单情况）
        # 匹配 on[Event]={...} 形式，捕获花括号内的内容
        handler_pattern = r'(on[A-Z]\w*)\s*=\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
        
        matches = re.finditer(handler_pattern, content)
        for match in matches:
            event_name = match.group(1)  # 如 onClick
            handler_body = match.group(2)  # 花括号内的内容
            
            # 阶段 2: 启发式判断是否已实现
            is_implemented = self._is_handler_implemented(handler_body)
            
            if not is_implemented:
                line_no = content[:match.start()].count('\n') + 1
                snippet = match.group(0)
                if len(snippet) > 60:
                    snippet = snippet[:57] + "..."
                
                    issues.append({
                        "rule_id": "empty_handler",
                        "severity": "error",
                        "priority": 2,
                        "file": filename,
                    "line": line_no,
                    "message": f"事件处理器 {event_name} 未实现或为空",
                    "snippet": snippet
                })
        
        return issues
    
    def _is_handler_implemented(self, handler_body: str) -> bool:
        """
        启发式判断事件处理器是否已实现
        
        判断标准（满足任一即认为已实现）：
        0. 函数引用传递：handleSubmit、onChange 等（常见的 React 模式）
        1. 包含函数调用：handle*()、set*()、*() 等
        2. 包含对象方法调用：obj.method()
        3. 包含赋值操作：= 
        4. 包含 return 语句
        5. 长度超过阈值（说明有实际代码）
        
        不算实现的情况：
        1. 空字符串或只有空白
        2. 只有注释
        3. 只有 console.log
        """
        # 去除注释和空白后的内容
        body_cleaned = re.sub(r'/\*.*?\*/', '', handler_body, flags=re.DOTALL)  # 移除多行注释
        body_cleaned = re.sub(r'//.*?$', '', body_cleaned, flags=re.MULTILINE)  # 移除单行注释
        body_cleaned = body_cleaned.strip()
        
        # 1. 完全空或只有空白
        if not body_cleaned:
            return False
        
        # 2. 只有空的箭头函数 () => {} 或 (e) => {}
        if re.match(r'^\([^)]*\)\s*=>\s*\{\s*\}$', body_cleaned):
            return False
        
        # 3. 只包含 console.log（占位符）
        if 'console.log' in body_cleaned and len(body_cleaned.replace('console.log', '').strip('();, ')) < 10:
            return False
        
        # 🆕 4. 检查是否是函数引用传递（常见的 React 模式）
        # 例如: handleSubmit, onChange, props.onSave
        if re.match(r'^[a-zA-Z_$][\w$]*(\.[a-zA-Z_$][\w$]*)*$', body_cleaned):
            # 单个标识符或属性访问（如 handleSubmit 或 props.onSave）
            # 认为这是传递函数引用，应该是已实现的
            return True
        
        # 5. 检查是否包含实际实现的标志
        implementation_indicators = [
            r'\w+\(',                    # 函数调用 foo()
            r'\.\w+\(',                  # 方法调用 obj.method()
            r'set[A-Z]\w*\(',           # setState 类调用
            r'handle\w*\(',             # handle* 函数调用
            r'\w+\s*=\s*\w+',           # 赋值操作（排除箭头函数的 =>）
            r'return\s+',               # return 语句
            r'throw\s+',                # throw 语句
            r'if\s*\(',                 # 条件语句
            r'for\s*\(',                # 循环语句
            r'while\s*\(',              # 循环语句
            r'switch\s*\(',             # switch 语句
        ]
        
        for indicator in implementation_indicators:
            if re.search(indicator, body_cleaned):
                return True
        
        # 6. 如果清理后的代码还有一定长度，认为可能有实现（保守策略）
        if len(body_cleaned) > 20:
            return True
        
        return False
    
    def _check_no_state_management(self, filename: str, content: str) -> List[Dict[str, Any]]:
        """检查是否缺少状态管理（如果声称可交互）"""
        issues = []
        
        # 检查是否有交互相关的关键词
        has_interactive_intent = any(keyword in content.lower() for keyword in [
            'interactive', 'click', 'input', 'form', 'button', 'game', 'todo'
        ])
        
        # 检查是否有状态管理
        has_state = 'useState' in content or 'useReducer' in content
        
        if has_interactive_intent and not has_state:
            issues.append({
                "rule_id": "no_state_management",
                "severity": "warning",
                "file": filename,
                "line": 1,
                "message": "文件看起来需要交互，但缺少状态管理（useState/useReducer）",
                "snippet": f"文件含有交互关键词但无状态管理"
            })
        
        return issues
    
    def _check_import_boundary_violation(self, filename: str, content: str) -> List[Dict[str, Any]]:
        """检查导入边界违规：../ 跨越到受保护目录或黑名单路径"""
        issues = []
        
        protected_patterns = ['components/ui', 'lib/utils', 'lib/cn']
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'import' in line and 'from' in line:
                # 提取 import 路径
                match = re.search(r'from\s+["\']([^"\']+)["\']', line)
                if match:
                    import_path = match.group(1)
                    
                    # 检查是否使用相对路径绕过（../../）
                    if '../' in import_path:
                        # 检查是否指向受保护目录
                        for pattern in protected_patterns:
                            if pattern in import_path:
                                issues.append({
                                    "rule_id": "import_boundary_violation",
                                    "severity": "error",
                                    "priority": 1,
                                    "file": filename,
                                    "line": i + 1,
                                    "message": f"导入边界违规：使用相对路径 ../ 访问受保护目录 {pattern}",
                                    "snippet": line.strip(),
                                    "suggestion": f"应使用 @/ 别名：@/{pattern}/..."
                                })
        
        return issues
    
    def _check_index_too_large(self, filename: str, content: str) -> List[Dict[str, Any]]:
        """检查 Index.tsx 是否过大，建议拆分"""
        issues = []
        
        # 获取阈值配置
        threshold = 300  # 默认 300 行
        for rule in self.rules:
            if rule.get('id') == 'index_tsx_too_large':
                threshold = rule.get('threshold_lines', 300)
                break
        
        lines = content.split('\n')
        line_count = len(lines)
        
        if line_count > threshold:
            issues.append({
                "rule_id": "index_tsx_too_large",
                "severity": "warning",
                "file": filename,
                "line": 1,
                "message": f"Index.tsx 有 {line_count} 行（超过 {threshold} 行阈值），建议拆分",
                "snippet": f"文件行数: {line_count}",
                "suggestion": "将复杂组件拆分到 src/components/generated/<appSlug>/*.tsx"
            })
        
        return issues
    
    def _check_input_text_contrast(self, filename: str, content: str) -> List[Dict[str, Any]]:
        """
        检查输入框是否有明确的文字颜色（防止与背景色冲突）
        常见问题：深色背景 + 深色文字，或浅色背景 + 浅色文字
        """
        issues = []
        
        # 检测 <input> 或 <Input> 标签
        import re
        
        # 匹配 input 标签（原生或 shadcn）
        # 支持多行和复杂属性
        input_pattern = r'<(input|Input)\s+([^/>]*(?:/>|>))'
        inputs = re.finditer(input_pattern, content, re.IGNORECASE | re.DOTALL)
        
        for match in inputs:
            tag_name = match.group(1)
            attributes = match.group(2)
            line_num = content[:match.start()].count('\n') + 1
            
            # 检查是否有明确的 text-* 颜色类
            has_text_color = bool(
                re.search(r'\btext-(white|black|gray-\d+|slate-\d+|zinc-\d+|neutral-\d+|stone-\d+)', attributes)
            )
            
            # 检查是否有 style 中的 color 属性
            has_style_color = bool(
                re.search(r'style=.*?\bcolor\s*:', attributes, re.IGNORECASE)
            )
            
            # 检查是否有 className 或 class（可能在样式文件中定义颜色）
            has_classname = bool(
                re.search(r'\b(className|class)=', attributes)
            )
            
            # 如果没有任何颜色相关的样式，发出警告
            if not has_text_color and not has_style_color:
                # 获取标签片段用于展示
                tag_snippet = match.group(0)[:100]
                if len(match.group(0)) > 100:
                    tag_snippet += '...'
                
                issues.append({
                    'rule_id': 'input_missing_text_color',
                    'severity': 'warning',  # warning 而非 error，因为颜色可能在外层容器
                    'priority': 3,
                    'file': filename,
                    'line': line_num,
                    'message': f'Input element may lack explicit text color styling (line {line_num}). Text may be invisible against background.',
                    'snippet': tag_snippet,
                    'suggestion': 'Add Tailwind classes: `text-gray-900` (light bg) or `text-white` (dark bg) and `placeholder:text-gray-400` or `placeholder:text-gray-500`'
                })
        
        return issues
    
    def _check_missing_text_color(self, filename: str, content: str) -> List[Dict[str, Any]]:
        """
        检查文本元素是否显式指定了颜色（防止依赖全局继承导致对比度不足）
        检查 h1-h6, p 等文本元素
        """
        issues = []
        
        # 检测标题元素 h1-h6
        heading_pattern = r'<(h[1-6])([^>]*)>(.*?)</\1>'
        headings = re.finditer(heading_pattern, content, re.IGNORECASE | re.DOTALL)
        
        for match in headings:
            tag = match.group(1)
            attributes = match.group(2)
            line_num = content[:match.start()].count('\n') + 1
            
            # 检查是否有显式的 text-* 颜色类
            has_text_color = bool(
                re.search(r'\btext-(white|black|gray-\d+|slate-\d+|zinc-\d+|neutral-\d+)', attributes)
            )
            
            # 检查是否有 style 中的 color 属性
            has_style_color = bool(
                re.search(r'style=.*?\bcolor\s*:', attributes, re.IGNORECASE)
            )
            
            if not has_text_color and not has_style_color:
                # 获取标签片段用于展示
                tag_snippet = match.group(0)[:100]
                if len(match.group(0)) > 100:
                    tag_snippet += '...'
                
                issues.append({
                    'rule_id': 'missing_explicit_text_color',
                    'severity': 'warning',  # 使用 warning 而非 error，避免过度严格
                    'priority': 3,
                    'file': filename,
                    'line': line_num,
                    'message': f'{tag.upper()} element missing explicit text color (line {line_num}). Text may be invisible against background.',
                    'snippet': tag_snippet,
                    'suggestion': 'Add text-white for dark backgrounds or text-gray-900 for light backgrounds to ensure readability'
                })
        
        return issues
    
    def _check_text_contrast_issues(self, filename: str, content: str) -> List[Dict[str, Any]]:
        """
        检测明显的对比度问题（如深色文字在深色背景上，浅色文字在浅色背景上）
        这个方法检测同一行中出现的危险颜色组合
        """
        issues = []
        
        # 定义危险的颜色组合
        dark_bg_patterns = [
            'bg-slate-900', 'bg-gray-900', 'bg-zinc-900', 'bg-neutral-900',
            'bg-black', 'bg-card'  # Cyberpunk/Minimal 中 bg-card 是深色
        ]
        dark_text_patterns = [
            'text-gray-900', 'text-slate-900', 'text-zinc-900', 
            'text-neutral-900', 'text-black'
        ]
        
        light_bg_patterns = [
            'bg-white', 'bg-gray-50', 'bg-gray-100', 'bg-slate-50', 
            'bg-slate-100', 'bg-background'  # 某些模板中 bg-background 是浅色
        ]
        light_text_patterns = [
            'text-white', 'text-gray-50', 'text-gray-100', 
            'text-slate-50', 'text-slate-100'
        ]
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            # 检查深色背景 + 深色文字
            has_dark_bg = any(bg in line for bg in dark_bg_patterns)
            has_dark_text = any(txt in line for txt in dark_text_patterns)
            
            if has_dark_bg and has_dark_text:
                # 找到具体的背景和文字类
                found_bg = next((bg for bg in dark_bg_patterns if bg in line), 'dark background')
                found_text = next((txt for txt in dark_text_patterns if txt in line), 'dark text')
                
                issues.append({
                    'rule_id': 'low_contrast_dark_on_dark',
                    'severity': 'error',
                    'priority': 3,
                    'file': filename,
                    'line': i + 1,
                    'message': f'低对比度：深色文字({found_text})在深色背景({found_bg})上，文字不可读',
                    'snippet': line.strip()[:120],
                    'suggestion': f'将 {found_text} 改为 text-white 或 text-gray-100'
                })
            
            # 检查浅色背景 + 浅色文字
            has_light_bg = any(bg in line for bg in light_bg_patterns)
            has_light_text = any(txt in line for txt in light_text_patterns)
            
            if has_light_bg and has_light_text:
                found_bg = next((bg for bg in light_bg_patterns if bg in line), 'light background')
                found_text = next((txt for txt in light_text_patterns if txt in line), 'light text')
                
                issues.append({
                    'rule_id': 'low_contrast_light_on_light',
                    'severity': 'error',
                    'priority': 3,
                    'file': filename,
                    'line': i + 1,
                    'message': f'低对比度：浅色文字({found_text})在浅色背景({found_bg})上，文字不可读',
                    'snippet': line.strip()[:120],
                    'suggestion': f'将 {found_text} 改为 text-gray-900 或 text-slate-900'
            })
        
        return issues
    
    def _check_css_module_global_usage(self, filename: str, content: str) -> List[Dict[str, Any]]:
        """检查 CSS Module 是否使用 :global() 污染全局"""
        issues = []
        
        if ':global' in content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if ':global' in line:
                    issues.append({
                        "rule_id": "css_module_global_usage",
                        "severity": "error",
                        "file": filename,
                        "line": i + 1,
                        "message": "CSS Module 使用了 :global() 污染全局样式",
                        "snippet": line.strip()[:100],
                        "suggestion": "移除 :global()，使用局部样式或通过设计系统的全局 token"
                    })
        
        return issues
    
    def _check_api_usage_errors(self, filename: str, content: str) -> List[Dict[str, Any]]:
        """
        检测常见的库 API 使用错误（防止混淆不同库的 API）
        
        常见问题：
        - date-fns vs moment.js API 混淆
        - recharts vs Chart.js API 混淆
        - axios vs fetch API 混淆
        """
        issues = []
        
        # 检测文件中导入的库
        imports = set()
        import_matches = re.finditer(r'from ["\']([^"\']+)["\']', content)
        for match in import_matches:
            imports.add(match.group(1))
        
        # 定义库 API 错误模式：{库名: [(错误正则, 错误说明, 正确用法)]}
        api_error_patterns = {
            'date-fns': [
                (
                    r'\.from\s*\(',
                    'date-fns 没有 .from() 方法（这是 moment.js 的 API）',
                    '使用 format(date, pattern), subDays(date, n), addDays(date, n)'
                ),
                (
                    r'\.format\s*\(',
                    'date-fns 没有 .format() 方法（这是 moment.js 的 API）',
                    '使用 format(date, pattern) 函数'
                ),
                (
                    r'\bmoment\s*\(',
                    'moment.js 未安装，应使用 date-fns',
                    '使用 parseISO(string) 或 new Date()'
                ),
            ],
            'recharts': [
                (
                    r'Chart\.(Line|Bar|Pie|Area)',
                    'recharts 不使用 Chart.Line() 语法（这是 Chart.js 的 API）',
                    '使用 JSX 组件: <LineChart>, <BarChart>, <PieChart>'
                ),
                (
                    r'new\s+Chart\s*\(',
                    'recharts 是声明式的，不使用 new Chart()（这是 Chart.js 的 API）',
                    '使用 JSX 组件: <LineChart data={...}>'
                ),
            ],
            'axios': [
                (
                    r'axios\.[a-z]+\([^)]*\)\.then\([^)]*\.json\(\)',
                    'axios 返回的数据已经是 JSON，不需要调用 .json()（这是 fetch 的 API）',
                    '直接使用 response.data'
                ),
                (
                    r'const\s+data\s*=\s*await\s+response\.json\(\)',
                    'axios 的响应已经是 JSON，不需要 .json()（这是 fetch 的 API）',
                    '使用 response.data 直接访问数据'
                ),
            ],
            'react-hook-form': [
                (
                    r'<Field\s+',
                    'react-hook-form 不使用 <Field> 组件（这是 Formik 的 API）',
                    '使用 <input {...register("fieldName")} />'
                ),
                (
                    r'<Formik\s+',
                    'Formik 未安装，应使用 react-hook-form',
                    '使用 useForm() hook'
                ),
            ],
        }
        
        # 对每个导入的库，检查是否有 API 使用错误
        for lib in imports:
            if lib in api_error_patterns:
                for pattern, error_msg, correct_usage in api_error_patterns[lib]:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        line_no = content[:match.start()].count('\n') + 1
                        snippet = match.group(0)
                        if len(snippet) > 50:
                            snippet = snippet[:47] + '...'
                        
                        issues.append({
                            'rule_id': 'api_usage_error',
                            'severity': 'error',
                            'priority': 2,
                            'file': filename,
                            'line': line_no,
                            'message': f'[{lib}] {error_msg}',
                            'snippet': snippet,
                            'suggestion': f'正确用法: {correct_usage}'
                        })
        
        return issues
    
    def _check_import_export_consistency(self, files: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        检查导入和导出的一致性（防止导入不存在的导出）
        
        常见问题：
        - Index.tsx 导入 computeOrderStats，但 dashboard-orders.ts 导出的是 getOrderStats
        - 组件导入 FILTER_OPTIONS，但逻辑文件忘记导出
        - 自愈修改了 generated 文件的导出，但没有同步修改导入
        """
        issues = []
        
        # 1. 解析所有文件的导出
        exports_map = {}  # {filepath: set(exported_names)}
        for filename, content in files.items():
            if filename.endswith(('.tsx', '.ts', '.jsx', '.js')):
                exports = self._extract_exports(content)
                if exports:
                    exports_map[filename] = exports
        
        # 2. 检查所有业务代码文件的导入（Index.tsx 和 generated 组件）
        files_to_check = []
        
        # 添加 Index.tsx
        if 'src/pages/Index.tsx' in files:
            files_to_check.append('src/pages/Index.tsx')
        
        # 添加所有 generated 目录下的组件
        for filename in files.keys():
            if '/generated/' in filename and filename.endswith(('.tsx', '.jsx', '.ts')):
                files_to_check.append(filename)
        
        # 检查每个文件的导入
        for file_path in files_to_check:
            file_content = files[file_path]
            imports = self._extract_named_imports_with_source(file_content)
        
        for imported_name, source_path in imports:
            # 只检查项目内部的导入（@/ 开头）
            if not source_path.startswith('@/'):
                continue
            
            # 解析相对路径到实际文件路径
            actual_path = self._resolve_import_path(source_path)
            
            if actual_path and actual_path in exports_map:
                exported_names = exports_map[actual_path]
                
                if imported_name not in exported_names:
                    # 尝试找到相似的导出名（可能是命名不一致）
                    similar = self._find_similar_export(imported_name, exported_names)
                    
                    if similar:
                        suggestion = f"'{actual_path}' 导出的是 '{similar}'，请在 {actual_path} 中将 '{similar}' 改名为 '{imported_name}'，或添加别名：export {{ {similar} as {imported_name} }}"
                    else:
                            suggestion = f"'{actual_path}' 没有导出 '{imported_name}'，请在 {actual_path} 中添加：export {{ {imported_name} }}"
                    
                    issues.append({
                        'rule_id': 'import_export_mismatch',
                        'severity': 'error',
                        'priority': 1,
                            'file': file_path,
                            'line': self._find_import_line(file_content, imported_name),
                        'message': f"导入的 '{imported_name}' 在 '{actual_path}' 中不存在",
                        'snippet': f'import {{ {imported_name} }} from "{source_path}"',
                            'suggestion': suggestion,
                            'gate': 'L0_static'
                    })
        
        return issues
    
    def _extract_exports(self, content: str) -> set:
        """提取文件中所有的导出名称"""
        exports = set()
        
        # export function/const/let/var name
        pattern1 = r'export\s+(?:function|const|let|var|async\s+function)\s+(\w+)'
        exports.update(re.findall(pattern1, content))
        
        # export { name1, name2 }
        pattern2 = r'export\s+\{([^}]+)\}'
        for match in re.finditer(pattern2, content):
            names_str = match.group(1)
            for name in names_str.split(','):
                name = name.strip()
                # 处理 as 重命名
                if ' as ' in name:
                    name = name.split(' as ')[1].strip()
                exports.add(name)
        
        # export type/interface
        pattern3 = r'export\s+(?:type|interface)\s+(\w+)'
        exports.update(re.findall(pattern3, content))
        
        return exports
    
    def _extract_named_imports_with_source(self, content: str) -> list:
        """提取导入的符号及其来源 [(imported_name, source_path), ...]"""
        imports = []
        
        # import { name1, name2 } from 'source'
        pattern = r'import\s+\{([^}]+)\}\s+from\s+["\']([^"\']+)["\']'
        for match in re.finditer(pattern, content):
            names_str = match.group(1)
            source = match.group(2)
            
            for name in names_str.split(','):
                name = name.strip()
                # 处理 type 导入（跳过类型导入，不检查）
                if name.startswith('type '):
                    continue
                # 处理 as 重命名（取原名）
                if ' as ' in name:
                    name = name.split(' as ')[0].strip()
                if name:  # 只添加非空名称
                    imports.append((name, source))
        
        return imports
    
    def _resolve_import_path(self, import_path: str) -> str:
        """解析 @/ 别名到实际文件路径"""
        if import_path.startswith('@/'):
            # @/lib/generated/dashboard-orders -> src/lib/generated/dashboard-orders
            base_path = 'src/' + import_path[2:]
            
            # 尝试添加可能的扩展名
            for ext in ['.ts', '.tsx', '.js', '.jsx']:
                if base_path + ext:
                    return base_path + ext
            
            return base_path + '.ts'  # 默认返回 .ts
        
        return None
    
    def _find_similar_export(self, imported_name: str, exported_names: set) -> str:
        """查找相似的导出名（可能只是命名差异）"""
        if not imported_name:  # 空名称（type 导入等）
            return None
        
        imported_lower = imported_name.lower()
        best_match = None
        best_score = 0
        
        for exported in exported_names:
            if len(exported) <= 1:  # 跳过单字符导出
                continue
                
            exported_lower = exported.lower()
            score = 0
            
            # 完全匹配（不应该到这里，但作为保险）
            if imported_lower == exported_lower:
                return exported
            
            # 检查是否一个是另一个的子串（更长的优先）
            if imported_lower in exported_lower:
                score = len(imported_name) * 2
            elif exported_lower in imported_lower:
                score = len(exported) * 2
            
            # 检查关键词匹配
            imported_words = set(re.findall(r'[A-Z][a-z]+|[a-z]+', imported_name))
            exported_words = set(re.findall(r'[A-Z][a-z]+|[a-z]+', exported))
            common_words = imported_words & exported_words
            
            if len(common_words) >= 2:  # 至少2个相同的词
                score += len(common_words) * 10
            
            # 更新最佳匹配
            if score > best_score:
                best_score = score
                best_match = exported
        
        # 只返回足够相似的匹配（score > 15）
        return best_match if best_score > 15 else None
    
    def _find_import_line(self, content: str, imported_name: str) -> int:
        """找到导入语句所在的行号"""
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if f'{imported_name}' in line and 'import' in line:
                return i
        return 1
    
    def _check_dependency_consistency(self, files: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        检查依赖一致性：确保使用的依赖都已声明在 vibe.meta.json 中
        
        这是一个关键的门禁，防止依赖注入失败导致运行时错误
        """
        issues = []
        
        # 1. 检查是否有 vibe.meta.json
        if 'vibe.meta.json' not in files:
            issues.append({
                'rule_id': 'missing_vibe_meta',
                'severity': 'error',
                'priority': 2,
                'file': 'vibe.meta.json',
                'line': 1,
                'message': 'vibe.meta.json 文件缺失，依赖信息无法传递给前端',
                'snippet': '',
                'suggestion': '确保生成流程中创建了 vibe.meta.json'
            })
            return issues
        
        # 2. 解析 vibe.meta.json
        try:
            import json
            vibe_meta = json.loads(files['vibe.meta.json'])
        except Exception as e:
            issues.append({
                'rule_id': 'invalid_vibe_meta',
                'severity': 'error',
                'priority': 2,
                'file': 'vibe.meta.json',
                'line': 1,
                'message': f'vibe.meta.json 格式错误: {str(e)}',
                'snippet': '',
                'suggestion': '检查 JSON 格式是否正确'
            })
            return issues
        
        # 3. 检查依赖字段是否存在
        if 'dependencies' not in vibe_meta:
            issues.append({
                'rule_id': 'missing_dependencies_field',
                'severity': 'warning',
                'file': 'vibe.meta.json',
                'line': 1,
                'message': 'vibe.meta.json 缺少 dependencies 字段',
                'snippet': '',
                'suggestion': '确保依赖检测和仲裁流程正常运行'
            })
            return issues
        
        dependencies = vibe_meta.get('dependencies', {})
        approved_deps = dependencies.get('approved', {})
        
        # 4. 检测代码中实际使用的第三方依赖
        from dependency_detector import (
            detect_imports_in_code, 
            PRESET_PACKAGES,
            NODEJS_BUILTIN_MODULES,
            DEV_DEPENDENCIES
        )
        
        # 配置文件列表（不检测这些文件中的导入）
        config_file_patterns = ['vite.config', 'tailwind.config', 'postcss.config', 'eslint.config']
        
        all_imports = set()
        for filename, content in files.items():
            # 跳过配置文件
            if any(pattern in filename for pattern in config_file_patterns):
                continue
                
            if filename.endswith(('.tsx', '.ts', '.jsx', '.js')):
                imports = detect_imports_in_code(content)
                all_imports.update(imports)
        
        # 三层过滤：预设 → Node.js 内置 → 开发依赖
        third_party_imports = all_imports - PRESET_PACKAGES - NODEJS_BUILTIN_MODULES - DEV_DEPENDENCIES
        
        # 5. 检查是否有使用但未批准的依赖
        unapproved_deps = third_party_imports - set(approved_deps.keys())
        
        if unapproved_deps:
            for pkg in sorted(unapproved_deps):
                issues.append({
                    'rule_id': 'unapproved_dependency_used',
                    'severity': 'error',
                    'priority': 2,
                    'file': 'vibe.meta.json',
                    'line': 1,
                    'message': f'代码中使用了未批准的依赖: {pkg}',
                    'snippet': f'import ... from "{pkg}"',
                    'suggestion': f'依赖 {pkg} 需要添加到白名单或从代码中移除'
                })
        
        # 6. 检查是否有批准但未使用的依赖（警告，不是错误）
        unused_deps = set(approved_deps.keys()) - third_party_imports
        
        if unused_deps:
            for pkg in sorted(unused_deps):
                issues.append({
                    'rule_id': 'approved_dependency_unused',
                    'severity': 'warning',
                    'file': 'vibe.meta.json',
                    'line': 1,
                    'message': f'批准的依赖未被使用: {pkg}',
                    'snippet': f'{pkg}@{approved_deps[pkg]}',
                    'suggestion': '这可能是正常的（如类型定义），或者是误检测'
                })
        
        return issues
    
    def _check_export_consistency(self, files: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        检查导出一致性问题
        
        规则：
        1. Index.tsx 必须使用默认导出: export default function Index()
        2. 其他组件应使用命名导出，且导出名应与文件名匹配
        3. 检测导入/导出不匹配的情况
        """
        issues = []
        
        for filename, content in files.items():
            if not filename.endswith(('.tsx', '.jsx', '.ts', '.js')):
                continue
            
            # 规则 1: Index.tsx 必须使用默认导出
            if 'Index.tsx' in filename or 'Index.jsx' in filename:
                has_default_export = bool(re.search(r'export\s+default\s+', content))
                has_named_export = bool(re.search(r'export\s+(const|function|class)\s+Index\b', content))
                
                if not has_default_export:
                    issues.append({
                        "rule_id": "index_missing_default_export",
                        "severity": "error",
                        "priority": 2,
                        "file": filename,
                        "line": 1,
                        "message": "Index.tsx 必须使用默认导出: export default function Index()",
                        "snippet": "缺少 export default",
                        "suggestion": "使用 'export default function Index()' 或 'export default Index'"
                    })
                
                if has_named_export and not has_default_export:
                    issues.append({
                        "rule_id": "index_wrong_export_type",
                        "severity": "error",
                        "priority": 2,
                        "file": filename,
                        "line": 1,
                        "message": "Index.tsx 使用了命名导出而不是默认导出",
                        "snippet": "export const Index 或 export function Index",
                        "suggestion": "改为 'export default function Index()'"
                    })
            
            # 规则 2: 检查组件文件的导出名是否与文件名匹配
            elif '/components/generated/' in filename and filename.endswith(('.tsx', '.jsx')):
                # 提取文件名（不含扩展名和路径）
                file_basename = filename.split('/')[-1].replace('.tsx', '').replace('.jsx', '')
                
                # 将 kebab-case 或 snake_case 转换为 PascalCase
                # 例如: neon-counter-card -> NeonCounterCard
                component_name_pascal = ''.join(
                    word.capitalize() for word in file_basename.replace('_', '-').split('-')
                )
                
                # 检查是否有匹配的命名导出（支持原文件名和 PascalCase 两种形式）
                has_matching_export = bool(re.search(
                    rf'export\s+(const|function|class)\s+({re.escape(component_name_pascal)}|{re.escape(file_basename)})\b',
                    content
                ))
                
                # 检查是否使用了默认导出（对于组件来说是不推荐的）
                has_default_export = bool(re.search(r'export\s+default\s+', content))
                
                if not has_matching_export and not has_default_export:
                    issues.append({
                        "rule_id": "component_missing_export",
                        "severity": "error",
                        "priority": 2,
                        "file": filename,
                        "line": 1,
                        "message": f"组件文件 {file_basename}.tsx 缺少对应的导出",
                        "snippet": f"未找到 export const {component_name_pascal} 或 export default",
                        "suggestion": f"添加 'export const {component_name_pascal} = ...' 或 'export default'"
                    })
                
                # 如果只有默认导出，警告应该使用命名导出
                if has_default_export and not has_matching_export:
                    issues.append({
                        "rule_id": "component_should_use_named_export",
                        "severity": "warning",
                        "file": filename,
                        "line": 1,
                        "message": f"组件 {file_basename} 使用了默认导出，建议使用命名导出",
                        "snippet": "export default ...",
                        "suggestion": f"改为 'export const {component_name_pascal} = ...' 以提高导入一致性"
                    })
        
        return issues
    
    def _check_unreferenced_generated_files(self, files: Dict[str, str]) -> List[Dict[str, Any]]:
        """检查未引用的 generated 文件"""
        issues = []
        
        # 找出所有 generated 目录中的组件文件
        generated_files = [f for f in files.keys() 
                          if '/generated/' in f and f.endswith(('.tsx', '.ts'))]
        
        # 收集所有文件的导入语句
        all_imports = []
        for filename, content in files.items():
            if filename.endswith(('.tsx', '.ts', '.jsx', '.js')):
                # 提取所有 import 语句
                import_matches = re.findall(r'from\s+["\']([^"\']+)["\']', content)
                all_imports.extend(import_matches)
        
        # 检查每个 generated 文件是否被引用
        for gen_file in generated_files:
            # 提取文件名（不含扩展名）
            file_base = gen_file.replace('.tsx', '').replace('.ts', '')
            
            # 检查是否有任何导入包含这个文件路径
            is_referenced = False
            for imp in all_imports:
                if file_base in imp or gen_file.split('/')[-1].replace('.tsx', '').replace('.ts', '') in imp:
                    is_referenced = True
                    break
            
            if not is_referenced:
                issues.append({
                    "rule_id": "unreferenced_generated_file",
                    "severity": "warning",
                    "file": gen_file,
                    "line": 1,
                    "message": f"生成的文件 {gen_file} 未被任何其他文件引用",
                    "snippet": "未被引用的文件",
                    "suggestion": "要么在 Index.tsx 或其他组件中导入它，要么删除它"
            })
        
        return issues
    
    def _check_duplicate_definitions(self, files: Dict[str, str]) -> List[Dict[str, Any]]:
        """检测同一文件中的重复函数/类定义"""
        issues = []
        
        for filename, content in files.items():
            if not filename.endswith(('.ts', '.tsx', '.js', '.jsx')):
                continue
            
            # 提取所有 export 定义
            export_pattern = r'export\s+(?:function|const|let|var|class)\s+(\w+)'
            exports = re.findall(export_pattern, content)
            
            # 检测重复
            seen = {}
            for name in exports:
                if name in seen:
                    seen[name] += 1
                else:
                    seen[name] = 1
            
            duplicates = {name: count for name, count in seen.items() if count > 1}
            
            for dup_name, count in duplicates.items():
                # 找到所有定义的行号
                lines = content.split('\n')
                locations = []
                for i, line in enumerate(lines, 1):
                    if f'export function {dup_name}' in line or f'export const {dup_name}' in line:
                        locations.append(i)
                
                issues.append({
                    'rule_id': 'duplicate_export_definition',
                    'severity': 'error',
                    'priority': 1,  # 最高优先级
                    'file': filename,
                    'line': locations[0] if locations else 1,
                    'message': f'函数/变量 {dup_name} 在同一文件中定义了 {count} 次（行号: {", ".join(map(str, locations))}）',
                    'snippet': f'export ... {dup_name}',
                    'suggestion': f'删除重复的 {dup_name} 定义，只保留最完整的版本'
                })
        
        return issues
    
    def _check_data_contract(self, files: Dict[str, str]) -> List[Dict[str, Any]]:
        """检测函数返回值是否满足组件期望"""
        issues = []
        
        # 针对常见模式：直接检查返回对象缺少字段
        for filename, content in files.items():
            if not filename.endswith(('.ts', '.tsx')):
                continue
            
            if '/lib/generated/' not in filename and '/pages/' not in filename:
                continue
            
            # 检查是否有多个return语句返回不同的字段
            return_blocks = re.findall(r'return\s*\{([^}]+)\}', content)
            
            if len(return_blocks) > 1:
                field_sets = []
                for block in return_blocks:
                    fields = {f.strip().split(':')[0].strip() for f in block.split(',') if f.strip()}
                    field_sets.append(fields)
                
                # 检查是否所有return都返回相同的字段
                if len(field_sets) >= 2:
                    first_fields = field_sets[0]
                    for i, fields in enumerate(field_sets[1:], 1):
                        missing = first_fields - fields
                        extra = fields - first_fields
                        
                        if missing or extra:
                            issues.append({
                                'rule_id': 'data_contract_violation',
                                'severity': 'error',
                                'priority': 2,
                                'file': filename,
                                'line': 1,
                                'message': f'函数返回的数据结构不一致：第1个return有{first_fields}，第{i+1}个return缺少{missing}，多出{extra}',
                                'snippet': 'return { ... }',
                                'suggestion': f'确保所有return语句返回相同的字段集合'
                            })
        
        return issues
    
    def _check_defensive_programming(self, files: Dict[str, str]) -> List[Dict[str, Any]]:
        """检测缺少空值检查的代码"""
        issues = []
        
        # 排除不应检查的目录（UI 库组件、工具函数等）
        excluded_patterns = [
            'src/components/ui/',
            'src/lib/utils',
            'node_modules/',
        ]
        
        dangerous_patterns = [
            (r'(\w+)\.(\w+)\.toLocaleString\(\)', 'toLocaleString()'),
            (r'(\w+)\.(\w+)\.map\(', 'map()'),
            (r'(\w+)\.(\w+)\.length', 'length'),
            (r'(\w+)\.(\w+)\.push\(', 'push()'),
        ]
        
        for filename, content in files.items():
            if not filename.endswith(('.tsx', '.jsx')):
                continue
            
            # 跳过排除的目录
            if any(pattern in filename for pattern in excluded_patterns):
                continue
            
            lines = content.split('\n')
            
            for pattern, method_name in dangerous_patterns:
                for line_num, line in enumerate(lines, 1):
                    matches = re.finditer(pattern, line)
                    
                    for match in matches:
                        obj = match.group(1)
                        field = match.group(2)
                        
                        # 检查是否有可选链或条件检查
                        has_optional_chain = '?.' in line[:match.start()]
                        has_conditional = f'{obj} &&' in line or f'{obj}?' in line
                        
                        if not has_optional_chain and not has_conditional:
                            issues.append({
                                'rule_id': 'missing_null_check',
                                'severity': 'error',
                                'priority': 3,
                                'file': filename,
                                'line': line_num,
                                'message': f'缺少空值检查：{obj}.{field}.{method_name} 可能在 {obj}.{field} 为 undefined 时崩溃',
                                'snippet': line.strip(),
                                'suggestion': f'使用可选链：{obj}?.{field}?.{method_name} 或添加条件：{obj} && {obj}.{field}'
                            })
        
        return issues


def run_quality_gates(files: Dict[str, str]) -> Dict[str, GateResult]:
    """
    运行所有启用的质量门禁
    
    Args:
        files: 文件字典
        
    Returns:
        门禁结果字典 {level_name: GateResult}
    """
    results = {}
    
    if not policy_manager.is_quality_gates_enabled():
        print("   ⚠️  质量门禁未启用")
        return results
    
    enabled_levels = policy_manager.get_enabled_gate_levels()
    print(f"   🚦 运行质量门禁: {', '.join(enabled_levels)}")
    
    for level_name in enabled_levels:
        if level_name == "L0_static":
            # 运行旧的 L0StaticGate（兼容性）
            old_gate = L0StaticGate()
            old_result = old_gate.check(files)
            
            # 运行新的 L0 交互/样式门禁（Gate1-8）
            from l0_gates import run_l0_gates
            context = {'prompt_text': '', 'app_slug': 'unknown'}  # 从文件推断
            new_l0_result = run_l0_gates(files, context)
            
            # 转换新格式到旧格式（标准化）
            new_issues_converted = []
            for fail in new_l0_result.fails:
                new_issues_converted.append({
                    'severity': 'error',
                    'file': fail.get('files', [''])[0] if fail.get('files') else '',
                    'line': fail.get('line', 1),
                    'message': f"[{fail.get('gate', 'UNKNOWN')}] {fail.get('message', '')}",
                    'suggestion': fail.get('suggestion', '')
                })
            for warn in new_l0_result.warnings:
                new_issues_converted.append({
                    'severity': 'warning',
                    'file': warn.get('files', [''])[0] if warn.get('files') else '',
                    'line': warn.get('line', 1),
                    'message': f"[{warn.get('gate', 'UNKNOWN')}] {warn.get('message', '')}",
                    'suggestion': warn.get('suggestion', '')
                })
            
            # 合并两个结果
            combined_issues = old_result.issues + new_issues_converted
            combined_passed = old_result.passed and new_l0_result.pass_status
            result = GateResult("L0_static", combined_passed, combined_issues)
            results[level_name] = result
            
            if result.passed:
                print(f"   ✓ {level_name}: 通过")
            else:
                errors = [i for i in combined_issues if i.get('severity') == 'error' or i.get('gate')]
                print(f"   ✗ {level_name}: 发现 {len(errors)} 个问题")
                for issue in errors[:3]:  # 只显示前 3 个
                    msg = issue.get('message', '')
                    file = issue.get('file') or (issue.get('files', [''])[0] if issue.get('files') else '')
                    line = issue.get('line', '?')
                    print(f"     - {msg[:80]} ({file}:{line})")
                if len(errors) > 3:
                    print(f"     - ... 还有 {len(errors) - 3} 个问题")
        
        # L1, L2, L3 门禁需要在 WebContainer 内运行，这里只做占位
        elif level_name == "L1_typecheck":
            print(f"   ⏭️  {level_name}: 需要在 WebContainer 内运行（暂未实现）")
            results[level_name] = GateResult(level_name, True, [])
        
        elif level_name == "L2_smoke_test":
            print(f"   ⏭️  {level_name}: 需要在 WebContainer 内运行（暂未实现）")
            results[level_name] = GateResult(level_name, True, [])
        
        elif level_name == "L3_lint":
            print(f"   ⏭️  {level_name}: 需要在 WebContainer 内运行（暂未实现）")
            results[level_name] = GateResult(level_name, True, [])
    
    return results


def format_gate_results_for_heal(
    results: Dict[str, GateResult], 
    max_issues: int = 8,
    group_by_file: bool = True
) -> str:
    """
    将门禁结果格式化为适合自愈循环的文本
    
    优化策略：
    1. 按优先级排序（priority 1 > 2 > 3）
    2. 智能分组（同文件的错误合并）
    3. 限制数量（最多显示 max_issues 个最重要的问题）
    
    Args:
        results: 门禁结果字典
        max_issues: 最多显示的问题数量
        group_by_file: 是否按文件分组
        
    Returns:
        格式化的错误报告
    """
    # 1. 收集所有错误
    all_issues = []
    for level_name, result in results.items():
        if not result.passed:
            for issue in result.issues:
                # 只处理 ERROR 级别（WARNING 不阻塞）
                if issue.get('severity') == 'error':
                    issue['gate'] = level_name
                    all_issues.append(issue)
    
    if not all_issues:
        return "No errors found."
    
    # 2. 按优先级排序
    def get_priority(issue):
        # 优先级：priority字段 > severity映射
        if 'priority' in issue:
            return issue['priority']
        # 兼容旧代码
        severity_map = {'critical': 1, 'error': 2, 'warning': 3}
        return severity_map.get(issue.get('severity', 'error'), 2)
    
    all_issues.sort(key=get_priority)
    
    # 3. 智能分组（同文件的错误合并）
    if group_by_file:
        grouped = {}
        for issue in all_issues:
            file_key = issue.get('file', 'unknown')
            if file_key not in grouped:
                grouped[file_key] = []
            grouped[file_key].append(issue)
        
        # 4. 生成报告（限制数量）
        report_lines = ["QUALITY GATE FAILURES (Prioritized & Grouped):\n"]
        issue_count = 0
        
        for filename, file_issues in grouped.items():
            if issue_count >= max_issues:
                break
            
            report_lines.append(f"\n📄 {filename}:")
            
            for issue in file_issues[:max_issues - issue_count]:
                priority_icon = {1: '🔴', 2: '🟠', 3: '🟡'}.get(get_priority(issue), '⚪')
                rule_id = issue.get('rule_id', 'unknown')
                
                report_lines.append(
                    f"  {priority_icon} [{rule_id}] Line {issue.get('line', '?')}: {issue['message']}"
                )
                
                if 'suggestion' in issue and issue['suggestion']:
                    # 建议最多显示100字符
                    suggestion = issue['suggestion'][:100]
                    report_lines.append(f"     💡 {suggestion}")
                
                issue_count += 1
                
                if issue_count >= max_issues:
                    break
        
        # 5. 添加汇总
        remaining = len(all_issues) - issue_count
        if remaining > 0:
            report_lines.append(f"\n... and {remaining} more issues (fix above first)")
        
        return "\n".join(report_lines)
    
    else:
        # 不分组，直接显示前N个
        report_lines = ["QUALITY GATE FAILURES (Top Priority):\n"]
        
        for i, issue in enumerate(all_issues[:max_issues]):
            priority_icon = {1: '🔴', 2: '🟠', 3: '🟡'}.get(get_priority(issue), '⚪')
            report_lines.append(
                f"{i+1}. {priority_icon} {issue.get('file', '?')}:{issue.get('line', '?')} - {issue['message']}"
            )
            if 'suggestion' in issue:
                report_lines.append(f"   💡 {issue['suggestion'][:100]}")
        
        remaining = len(all_issues) - max_issues
        if remaining > 0:
            report_lines.append(f"\n... and {remaining} more issues")
        
        return "\n".join(report_lines)

