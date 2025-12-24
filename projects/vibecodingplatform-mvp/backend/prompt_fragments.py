"""
Prompt 片段与触发器管理模块
提供可复用的规则片段、动态注入机制、以及上下文格式化工具
"""
import json
import hashlib
import re
from typing import Dict, List, Any, Optional, Literal
from policies import policy_manager


# 策略版本（与前后端对齐）
POLICY_VERSION = "1.0.0"


def build_base_rules(mode: Literal['generate', 'improve', 'heal'] = 'generate') -> str:
    """
    构建短硬可执行的 BaseRules（8-12 条 MUST/MUST NOT）
    
    Args:
        mode: 使用场景（generate/improve/heal）
        
    Returns:
        格式化的 BaseRules 字符串
    """
    rules = [
        "MUST output complete files as a map: filename -> full content",
        "MUST only write to allowed paths (src/pages/, src/components/generated/, src/lib/generated/)",
        "MUST keep application runnable (no syntax errors, complete imports)",
        "MUST use default export in src/pages/Index.tsx: `export default function Index()`",
        "MUST match filename to export in src/components/generated/: `CounterCard.tsx` exports `export const CounterCard` (PascalCase, exact match)",
        "MUST use lowercase shadcn imports: `from '@/components/ui/button'` NOT `from '@/components/ui/Button'`",
        "MUST specify explicit text color for ALL text: use text-white/text-gray-100 for Cyberpunk/Minimal/Brutalist, use text-gray-900/text-slate-900 for Glassmorphism/Modern/Playful",
        "MUST keep export names consistent: if Index.tsx imports 'computeOrderStats', export 'computeOrderStats', NOT 'getOrderStats'. Keep naming consistent across all files",
        "MUST NOT wrap <Routes> with <BrowserRouter> in App.tsx (already in main.tsx)",
        "MUST NOT edit locked paths (package.json, vite.config.ts, src/main.tsx, src/index.css, src/components/ui/*)",
        "MUST NOT add dependencies directly - report them in dependenciesRequested field if needed",
    ]
    
    # 根据模式添加特定规则
    if mode == 'heal':
        rules.extend([
            "MUST fix ONLY the issues listed in FailedGates section",
            "MUST maintain ALL existing functionality while fixing issues",
        ])
    elif mode == 'improve':
        rules.extend([
            "MUST modify ONLY files relevant to the improvement request",
            "MUST preserve all unmodified code exactly as is",
        ])
    
    # 格式化为编号清单
    formatted = "BASE RULES (MUST FOLLOW):\n"
    for i, rule in enumerate(rules, 1):
        formatted += f"{i}. {rule}\n"
    
    return formatted


def build_dynamic_rules(context: Dict[str, Any]) -> tuple[str, List[str]]:
    """
    根据上下文动态注入规则片段（基于触发器）
    
    Args:
        context: 上下文信息，包含:
            - gate_results: 门禁结果（优先级最高）
            - files: 文件内容字典（用于 FileScan）
            - prompt_text: 用户提示词（用于关键词检测）
            - interaction_spec: InteractionSpec（可选）
            
    Returns:
        (formatted_rules, activated_rule_ids)
    """
    gate_results = context.get('gate_results', {})
    files = context.get('files', {})
    prompt_text = context.get('prompt_text', '')
    
    activated_rules = []
    snippets = []
    
    # 定义动态规则三元组（RuleId, Triggers, Snippet）
    dynamic_rules = _get_dynamic_rule_definitions()
    
    for rule_id, triggers, snippet in dynamic_rules:
        should_activate = False
        
        # 触发器优先级：GateResults > FileScan > Keywords
        
        # 1) GateResults 触发（最可靠）
        if 'gate_codes' in triggers:
            for gate_code in triggers['gate_codes']:
                if _check_gate_failure(gate_results, gate_code):
                    should_activate = True
                    break
        
        # 2) FileScan 触发（次可靠）
        if not should_activate and 'file_patterns' in triggers:
            for pattern in triggers['file_patterns']:
                if _check_file_pattern(files, pattern):
                    should_activate = True
                    break
        
        # 3) Keywords 触发（兜底）
        if not should_activate and 'keywords' in triggers:
            for keyword in triggers['keywords']:
                if keyword.lower() in prompt_text.lower():
                    should_activate = True
                    break
        
        if should_activate:
            activated_rules.append(rule_id)
            snippets.append(snippet)
    
    # 格式化输出
    if not snippets:
        return "", []
    
    formatted = "DYNAMIC RULES (Context-Specific):\n"
    for i, snippet in enumerate(snippets, 1):
        formatted += f"DR{i}. {snippet}\n"
    
    return formatted, activated_rules


def _get_dynamic_rule_definitions() -> List[tuple[str, Dict[str, List[str]], str]]:
    """
    定义所有动态规则的三元组
    
    Returns:
        List of (rule_id, triggers, snippet)
    """
    return [
        # 导出规则（总是注入，因为这是高频错误）
        (
            "export_conventions",
            {
                "file_patterns": ["src/components/generated/", "src/pages/"],
                "keywords": []  # 空关键词意味着会通过文件扫描触发
            },
            "CRITICAL EXPORT RULES: Index.tsx uses DEFAULT export (`export default function Index()`). Components in src/components/generated/ use NAMED exports (`export const MyComponent = ...` or `export function MyComponent()`). Import accordingly: `import Index from './pages/Index'` vs `import { MyComponent } from './components/generated/...'`"
        ),
        
        # Sudoku Input 问题（高频）
        (
            "sudoku_native_input",
            {
                "gate_codes": ["G1_STRUCTURAL_NO_SHADCN_INPUT", "G1_SUDOKU_MUST_USE_INPUT"],
                "keywords": ["sudoku", "数独"]
            },
            "For Sudoku apps: Use native <input> elements, NOT shadcn Input component"
        ),
        
        # CSS Module 缺失
        (
            "css_module_create_missing",
            {
                "gate_codes": ["G2_CSS_MODULE_MISSING", "G2_CSS_MODULE_ORPHAN"],
            },
            "If you import a .module.css file, you MUST create that file in your output"
        ),
        
        # CSS Module 不应该用
        (
            "css_module_prefer_tailwind",
            {
                "gate_codes": ["G3_FORBIDDEN_CSS"],
            },
            "PREFER Tailwind classes over CSS Modules for styling unless custom complex styles are needed"
        ),
        
        # Index.tsx 过大
        (
            "index_too_large_split",
            {
                "gate_codes": ["index_tsx_too_large"],
            },
            "Extract components from Index.tsx to src/components/generated/<appSlug>/ when file exceeds 300 lines"
        ),
        
        # 路由相关（检测到 App.tsx 或路由关键词）
        (
            "router_setup",
            {
                "file_patterns": ["src/App.tsx"],
                "keywords": ["route", "routing", "navigation", "页面"]
            },
            "If generating App.tsx: Use <Routes> and <Route>, do NOT wrap with <BrowserRouter> (already in main.tsx)"
        ),
        
        # 导入边界违规
        (
            "import_boundary",
            {
                "gate_codes": ["import_boundary_violation"],
            },
            "NEVER bypass import boundaries with relative paths like ../../components/ui/"
        ),
        
        # 表单输入对比度（生成阶段提示）
        (
            "form_input_contrast",
            {
                "file_patterns": ["src/pages/", "src/components/generated/"],
                "keywords": ["form", "表单", "input", "输入", "wizard", "向导", "step", "步骤"]
            },
            "For forms/inputs: Ensure text color contrasts with background. Use Tailwind classes like `text-gray-900` or `text-white` on inputs. For dark backgrounds use `text-white placeholder:text-gray-400`, for light backgrounds use `text-gray-900 placeholder:text-gray-500`"
        ),
        
        # 🆕 API 指南：date-fns（检测到导入时触发）
        (
            "api_guide_date_fns",
            {
                "file_patterns": ["import:date-fns"],
                "keywords": []
            },
            "date-fns API: format(date,'yyyy-MM-dd'), parseISO(str), subDays(date,n), addDays(date,n). NEVER use .from() or .format() methods (that's moment.js)"
        ),
        
        # 🆕 API 指南：recharts
        (
            "api_guide_recharts",
            {
                "file_patterns": ["import:recharts"],
                "keywords": []
            },
            "recharts: Use JSX components <LineChart data={...}>, <BarChart>, <ResponsiveContainer>. NOT Chart.Line() or new Chart()"
        ),
        
        # 🆕 API 指南：react-hook-form
        (
            "api_guide_react_hook_form",
            {
                "file_patterns": ["import:react-hook-form"],
                "keywords": []
            },
            "react-hook-form: const {register,handleSubmit}=useForm(); <input {...register('name')}/>. NOT Formik's <Field>"
        ),
        
        # 🆕 API 指南：axios
        (
            "api_guide_axios",
            {
                "file_patterns": ["import:axios"],
                "keywords": []
            },
            "axios: Use response.data directly. NOT response.json() (that's fetch API)"
        ),
        
        # 🆕 API 指南：react-chartjs-2（高频易错）
        (
            "api_guide_react_chartjs",
            {
                "file_patterns": ["import:react-chartjs-2"],
                "keywords": []
            },
            """react-chartjs-2 + chart.js v4 CRITICAL SETUP:

STEP 1 - Import Chart.js components:
  import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';

STEP 2 - Register components BEFORE using (REQUIRED in v4):
  ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

STEP 3 - Import react-chartjs-2 component:
  import { Line } from 'react-chartjs-2';

STEP 4 - Use as JSX component:
  <Line data={{labels: [...], datasets: [{data: [...], label: '...', borderColor: '...'}]}} options={{...}} />

COMMON ERRORS:
  ❌ Forgot ChartJS.register() → "category is not a registered scale"
  ❌ Used Chart.Line() instead of <Line /> → "Chart.Line is not a constructor"
  ❌ Wrong data format → NaN in chart, blank screen

TIP: If this seems complex, consider using 'recharts' instead (simpler API, no registration needed)"""
        ),
        
        # 🆕 数据处理规则：使用内联数据，不要 fetch 外部文件（高频错误）
        (
            "data_handling_inline_only",
            {
                "file_patterns": ["src/pages/", "src/components/generated/"],
                "keywords": ["dashboard", "仪表板", "stats", "统计", "chart", "图表", "data", "数据"]
            },
            """DATA HANDLING CRITICAL RULES:

❌ NEVER fetch external JSON files: fetch('/data/stats.json'), fetch('./mock-data.json')
   → These files don't exist in WebContainer, will return 404 HTML, causing JSON parse errors

✅ ALWAYS use inline mock data or state:
   const mockData = [{ id: 1, name: 'Item 1', value: 100 }, ...];
   OR
   const [data, setData] = useState([...]);

✅ For data persistence, use localStorage:
   const savedData = localStorage.getItem('myData');
   const data = savedData ? JSON.parse(savedData) : defaultData;
   
✅ For API calls in production, use relative paths:
   fetch('/api/stats')  // OK - server endpoint
   axios.get('/api/users')  // OK - server endpoint

NEVER create separate .json data files. They won't be accessible in the preview environment."""
        ),
        
        # 🆕 导入导出一致性规则（自愈阶段触发）
        (
            "import_export_consistency",
            {
                "gate_codes": ["import_export_mismatch"],
            },
            "CRITICAL: Export names in src/lib/generated/ MUST match Index.tsx imports. If error shows 'computeOrderStats not exported', check what Index.tsx imports and export exactly that name. DO NOT rename exports without updating ALL imports."
        ),
        
        # 🆕 规则15: 重复定义修复
        (
            "duplicate_definition_fix",
            {
                "gate_codes": ["duplicate_export_definition"],
            },
            "CRITICAL: Same function/variable defined multiple times in ONE file. Keep ONLY the most complete version (check which has all required fields). DELETE all duplicate definitions."
        ),
        
        # 🆕 规则16: 数据契约修复
        (
            "data_contract_fix",
            {
                "gate_codes": ["data_contract_violation"],
            },
            "CRITICAL: Function returns incomplete data. ALL return statements must return the SAME fields. If first return has {totalRevenue, totalOrders, avgOrderValue}, all returns must include these exact fields."
        ),
        
        # 🆕 规则17: 空值安全修复
        (
            "null_safety_fix",
            {
                "gate_codes": ["missing_null_check"],
            },
            "Add null safety: Use optional chaining stats?.field?.method() instead of stats.field.method(). Or add conditional: stats && stats.field && stats.field.method()"
        ),
        
        # 深色主题文字颜色指导（主动触发）
        (
            "dark_theme_text_color",
            {
                "file_patterns": ["src/pages/", "src/components/generated/"],
                "keywords": []  # 总是检查文件模式
            },
            "CRITICAL for dark themes (Cyberpunk/Minimal/Brutalist): ALL text must use light colors. Use text-white or text-gray-100 for headings/primary text, text-gray-300 for body text, text-gray-400 for secondary/muted text. NEVER use text-gray-900, text-slate-900, or text-black on dark backgrounds (bg-card, bg-slate-900, bg-gray-900, etc.)"
        ),
        
        # 输入框对比度修复（自愈阶段触发）
        (
            "input_contrast_fix",
            {
                "gate_codes": ["input_missing_text_color"],
            },
            "Fix input text color: Add `text-gray-900` (for light bg) or `text-white` (for dark bg) to <input> or <Input> elements. Also add appropriate placeholder color like `placeholder:text-gray-400`"
        ),
        
        # 文字颜色修复（自愈阶段触发，门禁检测到缺失或对比度问题时）
        (
            "text_color_fix",
            {
                "gate_codes": ["missing_explicit_text_color", "low_contrast_dark_on_dark", "low_contrast_light_on_light"],
            },
            "Fix text color issues: For dark backgrounds (bg-card, bg-slate-900, bg-gray-900), use text-white or text-gray-100. For light backgrounds (bg-white, bg-gray-50), use text-gray-900 or text-slate-900. Replace any incorrect color classes that cause low contrast"
        ),
    ]


def _check_gate_failure(gate_results: Dict[str, Any], gate_code: str) -> bool:
    """检查是否有指定的门禁失败"""
    for gate_name, result in gate_results.items():
        if hasattr(result, 'issues'):
            for issue in result.issues:
                if issue.get('rule_id') == gate_code:
                    return True
    return False


def _check_file_pattern(files: Dict[str, str], pattern: str) -> bool:
    """
    检查是否有文件匹配模式
    
    支持两种模式：
    1. 文件名模式：如 "src/components/generated/"
    2. 内容模式（以 import: 开头）：如 "import:date-fns" - 检测文件内容中是否导入了该库
    """
    # 如果是内容模式（检测导入）
    if pattern.startswith("import:"):
        lib_name = pattern.replace("import:", "")
        for filename, content in files.items():
            if filename.endswith(('.tsx', '.ts', '.jsx', '.js')):
                # 检查是否导入了该库
                import_pattern = f'from ["\']({re.escape(lib_name)})["\']'
                if re.search(import_pattern, content):
                    return True
        return False
    
    # 原有的文件名匹配逻辑
    for filename in files.keys():
        if pattern in filename or filename.startswith(pattern.rstrip('/')):
            return True
    return False


def format_spec_payload(
    interaction_spec: Optional[Dict[str, Any]],
    gate_results: Optional[Dict[str, Any]] = None,
    prefer_summary: bool = True
) -> tuple[str, str]:
    """
    格式化 InteractionSpec 载荷
    
    Args:
        interaction_spec: InteractionSpec 字典
        gate_results: 门禁结果（用于判断是否需要全量 spec）
        prefer_summary: 是否优先使用摘要
        
    Returns:
        (formatted_spec, mode) - mode 为 'summary', 'compact', 或 'none'
    """
    if interaction_spec is None:
        return "", "none"
    
    # 判断是否需要全量 spec（当门禁失败涉及 spec 相关内容时）
    needs_full_spec = False
    if gate_results:
        for result in gate_results.values():
            if hasattr(result, 'issues'):
                for issue in result.issues:
                    # 如果门禁失败提到 spec 相关关键词，需要全量
                    if any(keyword in str(issue).lower() for keyword in ['spec', 'state', 'event', 'constraint']):
                        needs_full_spec = True
                        break
    
    if needs_full_spec or not prefer_summary:
        # 紧凑 JSON（无缩进）
        compact_json = json.dumps(interaction_spec, ensure_ascii=False, separators=(',', ':'))
        formatted = f"""
INTERACTION SPECIFICATION (MUST FOLLOW):
{compact_json}

CRITICAL: Implement ALL state/events/constraints/acceptance defined above.
"""
        return formatted, "compact"
    else:
        # 摘要模式
        state_count = len(interaction_spec.get('state', []))
        events_count = len(interaction_spec.get('events', []))
        constraints_count = len(interaction_spec.get('constraints', []))
        acceptance_count = len(interaction_spec.get('acceptance', []))
        
        # 提取关键条目（每类最多 2 个）
        key_state = interaction_spec.get('state', [])[:2]
        key_events = interaction_spec.get('events', [])[:2]
        key_constraints = interaction_spec.get('constraints', [])[:2]
        
        formatted = f"""
INTERACTION SPECIFICATION (Summary):
- State: {state_count} items (e.g., {', '.join(s.get('name', '') for s in key_state)})
- Events: {events_count} items (e.g., {', '.join(e.get('name', '') for e in key_events)})
- Constraints: {constraints_count} items
- Acceptance: {acceptance_count} test criteria

MUST implement all spec requirements. Full spec available if needed.
"""
        return formatted, "summary"


def format_file_manifest(files: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    生成文件清单（用于 /improve 阶段 A）
    
    Args:
        files: 文件字典
        
    Returns:
        文件清单列表
    """
    manifest = []
    
    # 文件类型推断
    def get_file_type(path: str) -> str:
        if 'pages/' in path:
            return 'page'
        elif 'components/' in path:
            return 'component'
        elif 'lib/' in path or 'utils/' in path:
            return 'lib'
        elif path.endswith('.css'):
            return 'css'
        elif 'test' in path.lower():
            return 'test'
        elif any(path.endswith(ext) for ext in ['.json', '.config.ts', '.config.js']):
            return 'config'
        return 'other'
    
    for filepath, content in files.items():
        manifest.append({
            'path': filepath,
            'type': get_file_type(filepath),
            'char_len': len(content),
            'is_entry': 'Index.tsx' in filepath or 'App.tsx' in filepath
        })
    
    # 按类型和入口优先级排序
    manifest.sort(key=lambda x: (not x['is_entry'], x['type'], x['path']))
    
    return manifest


def format_files_content(files: Dict[str, str], selected_paths: List[str]) -> str:
    """
    格式化选中文件的内容（用于 /improve 阶段 B）
    
    Args:
        files: 全部文件字典
        selected_paths: 选中的文件路径列表
        
    Returns:
        格式化的文件内容字符串
    """
    formatted_parts = []
    
    for path in selected_paths:
        if path in files:
            content = files[path]
            formatted_parts.append(f"{path}\n```\n{content}\n```")
    
    return "\n\n".join(formatted_parts)


def compute_prompt_hash(prompt: str) -> str:
    """
    计算 prompt 的哈希值（用于回放与定位漂移）
    
    Args:
        prompt: 提示词文本
        
    Returns:
        SHA256 哈希值（前 16 位）
    """
    return hashlib.sha256(prompt.encode('utf-8')).hexdigest()[:16]


def get_policy_version() -> str:
    """获取策略版本"""
    return POLICY_VERSION


def log_prompt_telemetry(
    prompt: str,
    mode: str,
    activated_fragments: List[str],
    spec_mode: str,
    context: Optional[Dict[str, Any]] = None
):
    """
    记录 prompt 遥测信息
    
    Args:
        prompt: 最终的 prompt 文本
        mode: 模式（generate/improve/heal）
        activated_fragments: 激活的动态片段 ID 列表
        spec_mode: Spec 模式（summary/compact/none）
        context: 额外的上下文信息
    """
    prompt_len = len(prompt)
    prompt_hash = compute_prompt_hash(prompt)
    estimated_tokens = prompt_len // 4  # 粗略估算
    
    print(f"   📊 Prompt 遥测:")
    print(f"     - 模式: {mode}")
    print(f"     - 策略版本: {POLICY_VERSION}")
    print(f"     - Prompt 哈希: {prompt_hash}")
    print(f"     - 长度: {prompt_len} 字符 (~{estimated_tokens} tokens)")
    print(f"     - Spec 模式: {spec_mode}")
    if activated_fragments:
        print(f"     - 激活的动态规则: {', '.join(activated_fragments)}")
    else:
        print(f"     - 激活的动态规则: 无")
    
    if context:
        if 'selected_files' in context:
            print(f"     - 选中文件数: {len(context['selected_files'])}")


def get_locked_paths() -> List[str]:
    """获取锁定路径列表（不可修改）"""
    return [
        'package.json',
        'vite.config.ts',
        'vite.config.js',
        'src/main.tsx',
        'src/index.css',
        'tailwind.config.js',
        'tsconfig.json',
        'postcss.config.js',
        'src/components/ui/*',
    ]


def get_allowed_paths() -> List[str]:
    """获取允许路径列表（可写入）"""
    return policy_manager.get_allowed_patterns()


def get_entrypoints_hint() -> List[str]:
    """获取入口文件提示"""
    return [
        'src/pages/Index.tsx',
        'src/App.tsx',
        'src/components/generated/<appSlug>/*',
    ]

