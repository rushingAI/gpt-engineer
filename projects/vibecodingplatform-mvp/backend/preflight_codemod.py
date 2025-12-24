"""
Preflight Codemod - 在质量门禁前自动修复 import/export 问题
Runtime Safety 优先：只修复 value import（会导致 console error）
"""
import re
from typing import Dict, List, Tuple, Optional, Any
from difflib import SequenceMatcher
from datetime import datetime


class PreflightCodemod:
    """
    Preflight G7 Codemod - 自动修复 import/export 不匹配问题
    
    修复顺序：S0 → S1a → S1b → S2
    - S0: 改 import 形式（default ↔ named）
    - S1a: 在定义前加 export 关键字
    - S1b: 追加 export { X }
    - S2: 找相似未导出定义 + 真实定义验证
    """
    
    def __init__(self):
        self.applied_fixes = []
    
    def fix_all(self, files: Dict[str, str]) -> Tuple[Dict[str, str], List[Dict[str, Any]]]:
        """
        执行完整的 preflight 修复流程
        
        Returns:
            (fixed_files, applied_fixes)
        """
        self.applied_fixes = []
        
        # Step 1: import_reflow（归一化多行 import）
        files = reflow_imports(files)
        
        # Step 2: 提取所有 import 关系
        import_graph = self._build_import_graph(files)
        
        # Step 3: 依次应用 S0 → S1 → S2
        fixed_files = dict(files)
        
        for importer_path, imports in import_graph.items():
            for imp in imports:
                if imp['skip']:
                    continue
                
                target_path = self._resolve_import_path(importer_path, imp['from_path'], fixed_files)
                if not target_path or target_path not in fixed_files:
                    continue
                
                # S0: 修复 import 形式
                fixed_files, s0_fixes = self._apply_s0(
                    fixed_files, importer_path, target_path, imp
                )
                self.applied_fixes.extend(s0_fixes)
                
                # S1 & S2: 补缺失的 export
                for symbol in imp['missing_symbols']:
                    fixed_files, fix = self._apply_s1_s2(
                        fixed_files, target_path, symbol, imp['is_type']
                    )
                    if fix:
                        self.applied_fixes.append(fix)
        
        return fixed_files, self.applied_fixes
    
    def _build_import_graph(self, files: Dict[str, str]) -> Dict[str, List[Dict]]:
        """
        构建 import 关系图
        
        Returns:
            {importer_path: [{from_path, symbols, is_type, skip, missing_symbols}]}
        """
        graph = {}
        
        for filepath, content in files.items():
            if not filepath.endswith(('.ts', '.tsx', '.js', '.jsx')):
                continue
            
            imports = []
            
            # 匹配各种 import 形态
            patterns = [
                # import { A, B } from './path'
                (r"import\s*\{([^}]+)\}\s*from\s*['\"]([^'\"]+)['\"]", 'named'),
                # import A from './path'
                (r"import\s+(\w+)\s+from\s*['\"]([^'\"]+)['\"]", 'default'),
                # import A, { B, C } from './path'
                (r"import\s+(\w+)\s*,\s*\{([^}]+)\}\s*from\s*['\"]([^'\"]+)['\"]", 'mixed'),
            ]
            
            for pattern, import_type in patterns:
                for match in re.finditer(pattern, content):
                    # 跳过 type-only import
                    if 'import type' in content[max(0, match.start() - 20):match.start()]:
                        continue
                    
                    # 跳过 import * as
                    if import_type == 'named' and '*' in match.group(1):
                        continue
                    
                    if import_type == 'named':
                        symbols_str = match.group(1)
                        from_path = match.group(2)
                        symbols = [s.strip() for s in symbols_str.split(',') if s.strip() and not s.strip().startswith('type ')]
                        is_type = 'type' in symbols_str
                    elif import_type == 'default':
                        symbols = [match.group(1)]
                        from_path = match.group(2)
                        is_type = False
                    else:  # mixed
                        default_sym = match.group(1)
                        named_syms = [s.strip() for s in match.group(2).split(',') if s.strip()]
                        symbols = [default_sym] + named_syms
                        from_path = match.group(3)
                        is_type = False
                    
                    imports.append({
                        'from_path': from_path,
                        'symbols': symbols,
                        'is_type': is_type,
                        'import_type': import_type,
                        'skip': False,
                        'missing_symbols': []
                    })
            
            if imports:
                graph[filepath] = imports
        
        return graph
    
    def _resolve_import_path(self, importer: str, import_path: str, files: Dict[str, str]) -> Optional[str]:
        """
        解析相对导入路径为绝对路径
        """
        if not import_path.startswith('.'):
            return None
        
        # 简化：只处理 ./xxx 和 ../xxx
        importer_dir = '/'.join(importer.split('/')[:-1])
        
        # 去除前导 ./
        if import_path.startswith('./'):
            resolved = f"{importer_dir}/{import_path[2:]}"
        elif import_path.startswith('../'):
            # 简化处理：只上一级
            parent_dir = '/'.join(importer_dir.split('/')[:-1])
            resolved = f"{parent_dir}/{import_path[3:]}"
        else:
            resolved = f"{importer_dir}/{import_path}"
        
        # 尝试补全扩展名
        for ext in ['', '.ts', '.tsx', '.js', '.jsx']:
            candidate = resolved + ext
            if candidate in files:
                return candidate
            # 尝试 /index
            index_candidate = f"{resolved}/index{ext}"
            if index_candidate in files:
                return index_candidate
        
        return None
    
    def _apply_s0(
        self, 
        files: Dict[str, str], 
        importer_path: str, 
        target_path: str,
        imp: Dict
    ) -> Tuple[Dict[str, str], List[Dict]]:
        """
        S0: 修复 import 形式不匹配
        """
        fixes = []
        target_content = files[target_path]
        importer_content = files[importer_path]
        
        # 检测目标文件的导出形式
        has_default = bool(re.search(r'export\s+default\b', target_content))
        named_exports = set(re.findall(
            r'export\s+(?:const|function|class|type|interface)\s+(\w+)',
            target_content
        ))
        named_exports.update(re.findall(r'export\s*\{\s*([^}]+)\}', target_content))
        
        # TODO: S0 修复逻辑（比较复杂，暂时跳过，留给 S1/S2 处理缺失导出）
        
        return files, fixes
    
    def _apply_s1_s2(
        self,
        files: Dict[str, str],
        target_path: str,
        symbol: str,
        is_type: bool
    ) -> Tuple[Dict[str, str], Optional[Dict]]:
        """
        S1a/S1b/S2: 补缺失的 export
        """
        target_content = files[target_path]
        
        # S1: 尝试补 export
        fixed_content, action, success = self._fix_missing_export(target_content, symbol, is_type)
        if success:
            files[target_path] = fixed_content
            return files, {
                'type': 'g7_codemod',
                'file': target_path,
                'symbol': symbol,
                'action': action,
                'risk_level': action.split('_')[0],  # S1a / S1b
                'fix_category': 'runtime_fix',
                'timestamp': datetime.now().isoformat()
            }
        
        # S2: 尝试找相似未导出定义
        fixed_content, action, success = self._try_s2_similar_unexported(
            target_content, symbol, 'type' if is_type else 'value'
        )
        if success:
            files[target_path] = fixed_content
            return files, {
                'type': 'g7_codemod',
                'file': target_path,
                'symbol': symbol,
                'action': action,
                'risk_level': 'S2',
                'fix_category': 'runtime_fix',
                'timestamp': datetime.now().isoformat()
            }
        
        return files, None
    
    def _fix_missing_export(
        self, 
        target_content: str, 
        symbol: str, 
        is_type: bool
    ) -> Tuple[str, str, bool]:
        """
        S1a/S1b: 补 export（三条幂等性硬规则）
        
        Returns:
            (fixed_content, action_type, success)
        """
        # ===== 硬规则2：检查是否已有任何形式导出 =====
        existing_export_patterns = [
            rf'export\s+(?:const|function|type|interface|class)\s+{re.escape(symbol)}\b',
            rf'export\s+\{{\s*[^}}]*\b{re.escape(symbol)}\b',
            rf'export\s+type\s+\{{\s*[^}}]*\b{re.escape(symbol)}\b',
            rf'export\s+default\s+{re.escape(symbol)}\b',
        ]
        if any(re.search(p, target_content) for p in existing_export_patterns):
            return target_content, 'already_exported', False
        
        # ===== S1a：定位定义行 =====
        definition_patterns = [
            rf'^(\s*)(const\s+{re.escape(symbol)}\s*[=:])',
            rf'^(\s*)(function\s+{re.escape(symbol)}\s*\()',
            rf'^(\s*)(type\s+{re.escape(symbol)}\s*=)',
            rf'^(\s*)(interface\s+{re.escape(symbol)}\s*\{{)',
            rf'^(\s*)(class\s+{re.escape(symbol)}\b)',
        ]
        
        for pattern in definition_patterns:
            matches = list(re.finditer(pattern, target_content, re.MULTILINE))
            if len(matches) == 1:
                match = matches[0]
                indent = match.group(1)
                definition = match.group(2)
                
                # 硬规则3：顶层检查（缩进<4空格）
                if len(indent.replace('\t', '    ')) >= 4:
                    continue
                
                # 硬规则1：该行是否已含 export
                line_start = target_content.rfind('\n', 0, match.start()) + 1
                line = target_content[line_start:match.end()]
                if 'export' in line:
                    return target_content, 'already_exported', False
                
                # S1a 执行
                fixed = target_content[:match.start()] + indent + 'export ' + definition + target_content[match.end():]
                return fixed, 'S1a_add_keyword', True
        
        # ===== S1b：追加 export { X } =====
        # 硬规则3：检查符号是否为顶层定义
        toplevel_def_pattern = rf'^(?:const|let|var|function|type|interface|class)\s+{re.escape(symbol)}\b'
        if not re.search(toplevel_def_pattern, target_content, re.MULTILINE):
            return target_content, 'not_toplevel_definition', False
        
        # 追加导出
        if is_type:
            export_line = f"\nexport type {{ {symbol} }};\n"
        else:
            export_line = f"\nexport {{ {symbol} }};\n"
        
        return target_content.rstrip() + export_line, 'S1b_append_export', True
    
    def _try_s2_similar_unexported(
        self,
        target_content: str,
        missing_name: str,
        expected_kind: str,
        threshold: float = 0.9
    ) -> Tuple[str, str, bool]:
        """
        S2: 找相似的 *已定义但未导出* 符号
        硬护栏：必须是真实定义，禁止纯 alias
        
        Returns:
            (fixed_content, action_type, success)
        """
        # 提取所有顶层定义
        all_definitions = self._extract_toplevel_definitions(target_content)
        
        # 过滤掉已导出的
        unexported = [
            (name, kind) for name, kind in all_definitions
            if not self._is_already_exported(target_content, name)
        ]
        
        # 在未导出定义中找相似
        for def_name, def_kind in unexported:
            if def_kind != expected_kind:
                continue
            
            # 硬护栏：验证真实定义
            if not self._is_real_definition(target_content, def_name, expected_kind):
                continue
            
            ratio = SequenceMatcher(None, missing_name.lower(), def_name.lower()).ratio()
            if ratio >= threshold:
                if expected_kind == 'type':
                    export_line = f"\nexport type {{ {def_name} as {missing_name} }};\n"
                else:
                    export_line = f"\nexport {{ {def_name} as {missing_name} }};\n"
                
                return target_content.rstrip() + export_line, 'S2_export_similar_unexported', True
        
        return target_content, 'no_similar_found', False
    
    def _extract_toplevel_definitions(self, content: str) -> List[Tuple[str, str]]:
        """
        提取所有顶层定义
        
        Returns:
            [(name, kind)]，kind='value'|'type'
        """
        definitions = []
        
        # value 定义
        value_patterns = [
            r'^(?:export\s+)?const\s+(\w+)\s*[=:]',
            r'^(?:export\s+)?function\s+(\w+)\s*\(',
            r'^(?:export\s+)?class\s+(\w+)\b',
        ]
        for pattern in value_patterns:
            for match in re.finditer(pattern, content, re.MULTILINE):
                definitions.append((match.group(1), 'value'))
        
        # type 定义
        type_patterns = [
            r'^(?:export\s+)?type\s+(\w+)\s*=',
            r'^(?:export\s+)?interface\s+(\w+)\s*\{',
        ]
        for pattern in type_patterns:
            for match in re.finditer(pattern, content, re.MULTILINE):
                definitions.append((match.group(1), 'type'))
        
        return definitions
    
    def _is_already_exported(self, content: str, symbol: str) -> bool:
        """检查符号是否已导出"""
        patterns = [
            rf'export\s+(?:const|function|type|interface|class)\s+{re.escape(symbol)}\b',
            rf'export\s+\{{\s*[^}}]*\b{re.escape(symbol)}\b',
            rf'export\s+type\s+\{{\s*[^}}]*\b{re.escape(symbol)}\b',
        ]
        return any(re.search(p, content) for p in patterns)
    
    def _is_real_definition(self, content: str, symbol: str, expected_kind: str) -> bool:
        """验证 symbol 是目标文件内的真实定义（不是 re-export）"""
        if expected_kind == 'type':
            patterns = [
                rf'^(?:export\s+)?type\s+{re.escape(symbol)}\s*=',
                rf'^(?:export\s+)?interface\s+{re.escape(symbol)}\s*\{{',
            ]
        else:
            patterns = [
                rf'^(?:export\s+)?const\s+{re.escape(symbol)}\s*[=:]',
                rf'^(?:export\s+)?function\s+{re.escape(symbol)}\s*\(',
                rf'^(?:export\s+)?class\s+{re.escape(symbol)}\b',
            ]
        return any(re.search(p, content, re.MULTILINE) for p in patterns)


def reflow_imports(files: Dict[str, str]) -> Dict[str, str]:
    """
    只对 src/lib/generated/** 的 import 段落做单行化
    在 preflight codemod 前执行
    """
    result = {}
    for filename, content in files.items():
        if '/lib/generated/' not in filename:
            result[filename] = content
            continue
        
        # 匹配跨行 import { ... } from '...'
        pattern = r"import\s*\{\s*\n?([^}]+)\}\s*from\s*['\"]([^'\"]+)['\"];?"
        
        def to_single_line(match):
            names_raw = match.group(1)
            path = match.group(2)
            # 去除换行、多余空格、尾逗号
            names = [n.strip().rstrip(',') for n in names_raw.replace('\n', ',').split(',') if n.strip()]
            return f"import {{ {', '.join(names)} }} from '{path}';"
        
        result[filename] = re.sub(pattern, to_single_line, content, flags=re.DOTALL)
    
    return result


def apply_preflight_codemod(files: Dict[str, str]) -> Tuple[Dict[str, str], List[Dict[str, Any]]]:
    """
    应用 Preflight Codemod
    
    在门禁检测前调用
    """
    codemod = PreflightCodemod()
    return codemod.fix_all(files)

