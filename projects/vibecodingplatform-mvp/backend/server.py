"""
Vibecoding Platform MVP - Backend Server

This FastAPI server wraps gpt-engineer's core functionality to expose
code generation capabilities via REST API.
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, List, Any
import json
import asyncio
import fnmatch

from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入 gpt-engineer 核心模块
from gpt_engineer.core.ai import AI
from gpt_engineer.core.default.steps import gen_code
from gpt_engineer.core.prompt import Prompt
from gpt_engineer.core.default.disk_memory import DiskMemory
from gpt_engineer.core.preprompts_holder import PrepromptsHolder
from gpt_engineer.core.default.paths import PREPROMPTS_PATH
from langchain_core.messages import HumanMessage

# 导入模板管理器和自定义 preprompts
from template_manager import template_manager
from preprompt_manager import custom_preprompts_manager
from dependency_detector import detect_dependencies_in_files
from dependency_arbiter import arbiter, print_arbitration_summary
from style_selector import select_style_deterministic, get_template_for_style
from policies import policy_manager
from spec_generator import (
    generate_interaction_spec_prompt,
    validate_and_repair_spec,
    create_spec_summary
)
from quality_gates import run_quality_gates
from self_heal import should_trigger_self_heal, self_heal_loop
from l0_gates import run_l0_gates
from prompt_fragments import (
    build_base_rules,
    build_dynamic_rules,
    format_spec_payload,
    format_file_manifest,
    format_files_content,
    get_policy_version,
    log_prompt_telemetry,
    compute_prompt_hash,
    get_locked_paths,
    get_allowed_paths,
    get_entrypoints_hint
)

app = FastAPI(
    title="Vibecoding Platform API",
    description="AI-powered code generation service",
    version="0.1.0"
)

# 配置 CORS - 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化 gpt-engineer 组件
# 检查 API key
if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
    print("警告: 未找到 OPENAI_API_KEY 或 ANTHROPIC_API_KEY 环境变量")

try:
    ai = AI(
        model_name=os.getenv("MODEL_NAME", "GPT-5.1-Codex-Max"),
        temperature=0.1
    )
    preprompts_holder = PrepromptsHolder(PREPROMPTS_PATH)
    print(f"✓ AI 初始化成功，使用模型: {ai.model_name}")
except Exception as e:
    print(f"✗ AI 初始化失败: {e}")
    ai = None
    preprompts_holder = None


@app.get("/")
def root():
    """健康检查端点"""
    return {
        "status": "running",
        "message": "Vibecoding Platform API",
        "ai_ready": ai is not None,
        "features": {
            "template_mode": True,
            "traditional_mode": True,
            "available_templates": len(template_manager.list_templates())
        }
    }


@app.get("/templates")
def list_templates():
    """列出所有可用的模板"""
    templates = template_manager.list_templates()
    return {
        "templates": templates,
        "count": len(templates)
    }


@app.post("/generate")
def generate_app(
    prompt_text: str = Body(..., embed=True),
    use_template: bool = Body(default=True, embed=True),
    template_name: str = Body(default=None, embed=True),
    style: str = Body(default="auto", embed=True)
) -> Dict[str, str]:
    """
    根据自然语言提示词生成应用代码
    
    支持两种模式：
    1. 传统模式（use_template=False）: 从零开始生成，生成单文件 HTML
    2. 模板模式（use_template=True）: 基于 React + TypeScript 模板生成现代化应用
    
    Args:
        prompt_text: 用户的自然语言描述
        use_template: 是否使用模板系统（默认 True）
        template_name: 模板名称（可选，会自动检测）
        style: 视觉风格（auto/cyberpunk/aurora/glass/neo_brutal/minimal/retro_futurism，默认 auto）
        
    Returns:
        Dict[str, str]: 文件名到文件内容的映射字典
        
    Example:
        POST /generate
        {
            "prompt_text": "创建一个现代化的 landing page",
            "use_template": true,
            "style": "auto"
        }
    """
    if ai is None:
        raise HTTPException(
            status_code=503,
            detail="AI 服务未就绪，请检查 API key 配置"
        )
    
    if not prompt_text or not prompt_text.strip():
        raise HTTPException(
            status_code=400,
            detail="prompt_text 不能为空"
        )
    
    try:
        prompt_text = prompt_text.strip()
        print(f"📝 收到生成请求: {prompt_text[:100]}...")
        print(f"   模式: {'模板模式' if use_template else '传统模式'}")
        
        if use_template:
            # 模板模式：生成现代化的 React 应用
            return generate_with_template(prompt_text, template_name, style)
        else:
            # 传统模式：使用原始的 gpt-engineer 流程
            return generate_traditional(prompt_text)
            
    except Exception as e:
        print(f"✗ 生成失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"代码生成失败: {str(e)}"
        )


def generate_traditional(prompt_text: str) -> Dict[str, str]:
    """传统生成模式：从零开始生成（通常是单文件 HTML）"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        memory = DiskMemory(tmp_dir)
        prompt = Prompt(prompt_text)
        
        # 使用原始的 gpt-engineer preprompts
        files_dict = gen_code(ai, prompt, memory, preprompts_holder)
        
        print(f"✓ 传统模式生成完成，共 {len(files_dict)} 个文件")
        return dict(files_dict)


def fix_component_imports(code: str) -> str:
    """
    修正常见的组件导入路径错误
    shadcn/ui 组件文件名是小写的，但 AI 经常会使用大写
    """
    import re
    
    # 定义需要修正的组件列表（大写 -> 小写）
    components_to_fix = [
        'Button', 'Card', 'Input', 'Textarea', 'Tabs', 'TabsList', 'TabsTrigger', 'TabsContent',
        'Separator', 'ScrollArea', 'Dialog', 'Select', 'Label', 'Checkbox', 'RadioGroup',
        'Switch', 'Slider', 'Progress', 'Avatar', 'Badge', 'Alert', 'Toast', 'Tooltip',
        'DropdownMenu', 'Popover', 'HoverCard', 'NavigationMenu', 'Command', 'Calendar',
        'Sheet', 'Accordion', 'AspectRatio', 'Collapsible', 'ContextMenu', 'Menubar',
        'CardHeader', 'CardContent', 'CardFooter', 'CardTitle', 'CardDescription'
    ]
    
    fixed_code = code
    
    # 修正每个组件的导入路径
    for component in components_to_fix:
        component_lower = component.lower()
        
        # 修正单独导入: from '@/components/ui/Button'
        pattern1 = rf"from ['\"]@/components/ui/{component}['\"]"
        replacement1 = f"from '@/components/ui/{component_lower}'"
        fixed_code = re.sub(pattern1, replacement1, fixed_code, flags=re.IGNORECASE)
        
        # 修正带文件扩展名的: from '@/components/ui/Button.tsx'
        pattern2 = rf"from ['\"]@/components/ui/{component}\.tsx['\"]"
        replacement2 = f"from '@/components/ui/{component_lower}'"
        fixed_code = re.sub(pattern2, replacement2, fixed_code, flags=re.IGNORECASE)
    
    return fixed_code


def fix_lucide_icons(code: str) -> str:
    """
    修正 lucide-react 图标导入错误
    AI 经常会创造不存在的图标名称，这里替换成真实的图标
    """
    import re
    
    # 检测无效的图标导入模式
    # 例如: import { FeatureIcon1, Icon1, FeatureIcon } from 'lucide-react'
    invalid_icon_patterns = [
        r'FeatureIcon\d*', r'Icon\d+', r'FeatureIcon', r'TestimonialIcon',
        r'HeroIcon', r'CardIcon', r'SectionIcon'
    ]
    
    # 真实的常用图标替换
    real_icons = ['Zap', 'Star', 'Heart', 'Sparkles', 'Rocket', 'Shield']
    
    # 查找 lucide-react 导入行
    lucide_import_pattern = r"import\s*\{([^}]+)\}\s*from\s*['\"]lucide-react['\"]"
    
    def replace_invalid_icons(match):
        imports = match.group(1)
        import_list = [i.strip() for i in imports.split(',')]
        
        fixed_imports = []
        icon_index = 0
        
        for imp in import_list:
            is_invalid = False
            for pattern in invalid_icon_patterns:
                if re.match(pattern, imp):
                    is_invalid = True
                    break
            
            if is_invalid:
                # 用真实图标替换
                if icon_index < len(real_icons):
                    fixed_imports.append(real_icons[icon_index])
                    icon_index += 1
            else:
                fixed_imports.append(imp)
        
        return f"import {{ {', '.join(fixed_imports)} }} from 'lucide-react'"
    
    fixed_code = re.sub(lucide_import_pattern, replace_invalid_icons, code)
    
    # 同时替换使用这些图标的地方
    for i, real_icon in enumerate(real_icons):
        for pattern in invalid_icon_patterns:
            # 替换变量使用: icon: FeatureIcon1 -> icon: Zap
            fixed_code = re.sub(
                rf'\bicon:\s*{pattern}\b',
                f'icon: {real_icons[i % len(real_icons)]}',
                fixed_code
            )
    
    return fixed_code


def generate_with_template(prompt_text: str, template_name: str = None, style: str = "auto") -> Dict[str, str]:
    """模板生成模式：基于 React + TypeScript 模板生成"""
    
    # 1. 选择风格（deterministic）
    selected_style, style_source, style_metadata = select_style_deterministic(prompt_text, style)
    print(f"   风格选择: {selected_style} (来源: {style_source})")
    if style_metadata:
        print(f"   风格元数据: {style_metadata}")
    
    # 2. 检测应用类型
    app_type = custom_preprompts_manager.detect_app_type(prompt_text)
    print(f"   应用类型: {app_type}")
    
    # 3. 选择模板（优先用户指定，否则根据风格选择）
    if template_name is None:
        template_name = get_template_for_style(selected_style)
    print(f"   使用模板: {template_name}")
    
    # 4. 加载模板
    template = template_manager.get_template(template_name)
    if template is None:
        raise Exception(f"模板不存在: {template_name}")
    
    # 5. 构建增强的系统提示词（基于风格和应用类型）
    system_prompt = custom_preprompts_manager.build_system_prompt(app_type, selected_style)
    
    # 5.5. Spec-first: 生成 InteractionSpec（如果启用）
    interaction_spec = None
    spec_status = "disabled"
    
    if policy_manager.is_spec_first_enabled():
        print("   🎯 Spec-first 模式已启用，正在生成 InteractionSpec...")
        
        # 生成 Spec 的 prompt
        spec_prompt = generate_interaction_spec_prompt(prompt_text, app_type)
        
        # 调用 AI 生成 Spec
        messages = ai.next(
            messages=[HumanMessage(content=spec_prompt)],
            step_name="generate_interaction_spec"
        )
        
        # 获取 AI 的响应（最后一条消息）
        spec_text = messages[-1].content
        
        # 验证并修复 Spec
        interaction_spec, spec_status = validate_and_repair_spec(ai, spec_text)
        
        if interaction_spec is None:
            print(f"   ✗ Spec 生成失败: {spec_status}")
            # 如果 Spec 生成失败，可以选择降级到非 Spec 模式，或者直接失败
            # 这里我们选择降级（警告但继续）
            print("   ⚠️  降级到非 Spec 模式继续生成")
        else:
            print(f"   ✓ InteractionSpec 生成成功 (状态: {spec_status})")
            print(f"     - State: {len(interaction_spec.get('state', []))} 个")
            print(f"     - Events: {len(interaction_spec.get('events', []))} 个")
            print(f"     - Constraints: {len(interaction_spec.get('constraints', []))} 个")
            print(f"     - Acceptance: {len(interaction_spec.get('acceptance', []))} 个")
    
    # 6. 构建用户提示词（使用新的模块化 prompt 片段）
    
    # 6.1 BaseRules（短硬可执行）
    base_rules = build_base_rules(mode='generate')
    
    # 6.2 DynamicRules（基于上下文触发）
    dynamic_context = {
        'gate_results': {},  # 生成阶段暂无门禁结果
        'files': {},
        'prompt_text': prompt_text,
        'interaction_spec': interaction_spec
    }
    dynamic_rules, activated_rule_ids = build_dynamic_rules(dynamic_context)
    
    # 6.3 Spec 载荷（优先摘要）
    spec_section, spec_mode = format_spec_payload(interaction_spec, prefer_summary=True)
    
    # 6.4 构建增强的 prompt
    enhanced_prompt = f"""{system_prompt}
{spec_section}

================================================================================
USER REQUEST:
================================================================================

{prompt_text}

================================================================================
{base_rules}

{dynamic_rules}

OUTPUT FORMAT:
You MUST output files in this EXACT format:

FILENAME
```
CODE
```

DO NOT use markdown headings (###), language tags, or descriptions!
Just: FILENAME then ``` CODE ```

ALLOWED FILE LOCATIONS:
- src/pages/Index.tsx (main entry, use default export)
- src/components/generated/<appSlug>/*.tsx (domain components)
- src/lib/generated/*.ts (pure logic, NO JSX)

YOU ARE WORKING WITH:
- Pre-configured React + TypeScript + Vite + Tailwind + shadcn/ui
- BrowserRouter already in src/main.tsx
- Global styles in src/index.css (do not modify)
- Import shadcn components from @/components/ui/ (lowercase paths)
- Import icons from lucide-react
"""
    
    # 7. 记录 prompt 遥测
    log_prompt_telemetry(
        prompt=enhanced_prompt,
        mode='generate',
        activated_fragments=activated_rule_ids,
        spec_mode=spec_mode,
        context={'policy_version': get_policy_version()}
    )
    
    # 8. 调用 AI 生成代码
    with tempfile.TemporaryDirectory() as tmp_dir:
        memory = DiskMemory(tmp_dir)
        prompt = Prompt(enhanced_prompt)
        
        # 使用原始的 preprompts_holder（用于文件格式等基础指导）
        generated_files = gen_code(ai, prompt, memory, preprompts_holder)
        
        print(f"   AI 生成了 {len(generated_files)} 个文件")
        
        # 9. 后处理：修正组件导入路径和图标导入
        fixed_generated_files = {}
        component_fixes = 0
        icon_fixes = 0
        
        for filename, content in generated_files.items():
            if filename.endswith(('.tsx', '.ts', '.jsx', '.js')):
                original_content = content
                
                # 修正组件导入路径
                fixed_content = fix_component_imports(content)
                if fixed_content != original_content:
                    component_fixes += 1
                    print(f"   ⚠️  修正了 {filename} 中的组件导入路径")
                
                # 修正图标导入
                original_after_component_fix = fixed_content
                fixed_content = fix_lucide_icons(fixed_content)
                if fixed_content != original_after_component_fix:
                    icon_fixes += 1
                    print(f"   ⚠️  修正了 {filename} 中的图标导入")
                
                fixed_generated_files[filename] = fixed_content
            else:
                fixed_generated_files[filename] = content
        
        if component_fixes > 0:
            print(f"   ✓ 自动修正了 {component_fixes} 个文件的组件导入路径")
        if icon_fixes > 0:
            print(f"   ✓ 自动修正了 {icon_fixes} 个文件的图标导入")
        
        # 10. 检测生成代码中的额外依赖并仲裁（不直接修改 package.json）
        requested_deps = detect_dependencies_in_files(fixed_generated_files)
        approved_deps = {}
        rejected_deps = {}
        dep_warnings = []
        
        if requested_deps:
            print(f"\n   🔍 检测到 {len(requested_deps)} 个额外依赖请求，提交仲裁...")
            approved_deps, rejected_deps, dep_warnings = arbiter.arbitrate(requested_deps)
            print_arbitration_summary(approved_deps, rejected_deps, dep_warnings)
        
        # 11. 合并模板和生成的文件
        template_files = template['files']
        
        # ⚠️ package.json 受保护，不再由 AI 直接修改
        # 批准的依赖将记录在 vibe.meta.json 中，由前端/WebContainer 动态注入
        
        final_files = template_manager.merge_files(template_files, fixed_generated_files)
        
        # 11.1. 提前创建 vibe.meta.json（至少包含依赖信息），以便门禁检查
        # 这样 _check_dependency_consistency 就能正常工作
        preliminary_vibe_meta = {
            "dependencies": arbiter.create_dependency_report(
                requested_deps if requested_deps else {},
                approved_deps if approved_deps else {},
                rejected_deps if rejected_deps else {}
            )
        }
        final_files['vibe.meta.json'] = json.dumps(preliminary_vibe_meta, indent=2, ensure_ascii=False)
        
        # 11.2. 运行 L0 交互/样式门禁（针对结构性应用）
        l0_config = policy_manager._policy.get('l0_style_gates', {})
        l0_context = {
            'prompt_text': prompt_text,
            'app_type': app_type,
            'interaction_spec': interaction_spec,
            'generated_file_paths': list(final_files.keys())
        }
        l0_result = run_l0_gates(final_files, l0_context, l0_config)
        
        # 打印 L0 门禁结果（便于调试）
        if not l0_result.to_dict()['pass']:
            print(f"\n   🚨 L0 交互/样式门禁失败:")
            for fail in l0_result.fails:
                print(f"     ✗ {fail['gate']}: {fail['message']}")
                print(f"       涉及文件: {', '.join(fail['files'][:3])}")
                if fail.get('suggestion'):
                    print(f"       建议: {fail['suggestion'][:100]}")
        if l0_result.warnings:
            print(f"\n   ⚠️  L0 交互/样式门禁警告 ({len(l0_result.warnings)} 个):")
            for warn in l0_result.warnings[:3]:
                print(f"     - {warn['gate']}: {warn['message']}")
        if l0_result.hints:
            for hint in l0_result.hints[:2]:
                print(f"   💡 {hint}")
        
        # 11.3. 运行质量门禁（最快失败优先）
        gate_results = run_quality_gates(final_files)
        
        # 11.3.5. 如果 L0 失败，将其映射到门禁结果（触发自愈）
        if not l0_result.to_dict()['pass']:
            # 创建一个伪 GateResult 对象用于自愈流程
            from quality_gates import GateResult
            l0_gate_issues = []
            for fail in l0_result.fails:
                l0_gate_issues.append({
                    'rule_id': fail['gate'],
                    'severity': 'error',
                    'file': fail['files'][0] if fail['files'] else 'unknown',
                    'line': 0,
                    'message': fail['message'],
                    'snippet': fail.get('snippet', ''),
                    'suggestion': fail.get('suggestion', '')
                })
            gate_results['L0_style_interaction'] = GateResult('L0_style_interaction', False, l0_gate_issues)
        
        # 11.4. 自愈循环（如果门禁失败）
        heal_iterations = 0
        heal_success = False
        heal_triggered = False
        
        if should_trigger_self_heal(gate_results):
            heal_triggered = True
            print(f"   🔧 触发自愈循环...")
            final_files, heal_success, heal_iterations = self_heal_loop(
                ai,
                final_files,
                gate_results,
                interaction_spec
            )
            
            if heal_success:
                print(f"   ✓ 自愈成功！")
                # 重新运行门禁以获取最终结果
                gate_results = run_quality_gates(final_files)
            else:
                print(f"   ✗ 自愈失败，返回最后一次迭代的结果")
        
        # 检查是否有门禁失败
        failed_gates = [name for name, result in gate_results.items() if not result.passed]
        if failed_gates:
            print(f"   ⚠️  质量门禁失败: {', '.join(failed_gates)}")
            # 注意：即使失败，也返回结果（用户可以看到警告并手动修复）
        
        # 11.5. 如果有 InteractionSpec，写入文件
        if interaction_spec is not None:
            spec_location = policy_manager.get_spec_location()
            final_files[spec_location] = json.dumps(interaction_spec, indent=2, ensure_ascii=False)
            print(f"   ✓ InteractionSpec 已写入: {spec_location}")
        
        # 12. 更新 vibe.meta.json（添加完整的元数据和 telemetry 信息）
        # 注意：vibe.meta.json 在第 11.1 步已经创建（包含 dependencies），现在添加其他字段
        vibe_meta = {
            "style": selected_style,
            "style_source": style_source,
            "template_name": template_name,
            "app_type": app_type,
            "metadata": style_metadata,
            "generated_at": __import__('datetime').datetime.now().isoformat(),
            # 依赖仲裁结果（已在 11.1 步写入，这里保持一致）
            "dependencies": arbiter.create_dependency_report(
                requested_deps if requested_deps else {},
                approved_deps if approved_deps else {},
                rejected_deps if rejected_deps else {}
            ),
            # Telemetry（策略版本与 prompt 哈希）
            "telemetry": {
                "policy_version": get_policy_version(),
                "prompt_hash": compute_prompt_hash(enhanced_prompt),
                "prompt_length": len(enhanced_prompt),
                "activated_dynamic_rules": activated_rule_ids,
                "spec_mode": spec_mode
            }
        }
        
        # 添加 Spec 摘要到 vibe.meta.json
        if interaction_spec is not None:
            vibe_meta["interaction_spec"] = {
                "enabled": True,
                "status": spec_status,
                "location": policy_manager.get_spec_location(),
                "summary": create_spec_summary(interaction_spec)
            }
        else:
            vibe_meta["interaction_spec"] = {
                "enabled": policy_manager.is_spec_first_enabled(),
                "status": spec_status
            }
        
        # 添加质量门禁结果到 vibe.meta.json
        if gate_results:
            vibe_meta["quality_gates"] = {
                "enabled": policy_manager.is_quality_gates_enabled(),
                "results": {name: result.to_dict() for name, result in gate_results.items()},
                "passed": all(result.passed for result in gate_results.values()),
                "failed_gates": [name for name, result in gate_results.items() if not result.passed]
            }
        else:
            vibe_meta["quality_gates"] = {
                "enabled": policy_manager.is_quality_gates_enabled(),
                "passed": True
            }
        
        # 添加自愈循环结果到 vibe.meta.json
        vibe_meta["self_heal"] = {
            "enabled": policy_manager.is_self_heal_enabled(),
            "triggered": heal_triggered,
            "success": heal_success if heal_triggered else None,
            "iterations": heal_iterations if heal_triggered else 0,
            "max_iterations": policy_manager.get_max_heal_iterations()
        }
        
        final_files['vibe.meta.json'] = json.dumps(vibe_meta, indent=2, ensure_ascii=False)
        
        print(f"✓ 模板模式生成完成，最终 {len(final_files)} 个文件（含 vibe.meta.json）")
        
        return final_files


def improve_stage_a_select_files(
    files: Dict[str, str],
    improvement_request: str,
    ai
) -> Dict[str, Any]:
    """
    改进阶段 A：选择需要修改的文件
    
    Returns:
        {
            "selected": [{"path": str, "reason": str, "edit_scope": str}],
            "not_selected_reasoning": str,
            "needs_dependency": [{"name": str, "why": str}]
        }
    """
    # 生成文件清单
    manifest = format_file_manifest(files)
    
    # 获取约束
    allowed_paths = get_allowed_paths()
    locked_paths = get_locked_paths()
    entrypoints_hint = get_entrypoints_hint()
    
    # 构建阶段 A prompt
    stage_a_prompt = f"""You are analyzing which files need modification for an improvement request.

IMPROVEMENT REQUEST:
{improvement_request}

FILE MANIFEST:
{json.dumps(manifest, indent=2, ensure_ascii=False)}

CONSTRAINTS:
- Allowed paths: {', '.join(allowed_paths)}
- Locked paths (DO NOT select): {', '.join(locked_paths)}
- Entry points hint: {', '.join(entrypoints_hint)}

OUTPUT STRICT JSON (NO OTHER TEXT):
{{
  "selected": [
    {{"path": "src/pages/Index.tsx", "reason": "needs UI change", "edit_scope": "modify existing component"}},
    ...
  ],
  "not_selected_reasoning": "why other files were not selected",
  "needs_dependency": [
    {{"name": "some-package", "why": "required for new feature"}},
    ...
  ]
}}

RULES:
1. Select ONLY files that need modification
2. DO NOT select locked files
3. Prefer entry points and related components
4. Keep selection minimal (usually 1-3 files)
5. Output ONLY valid JSON (no markdown, no説明)

Analyze and output JSON now:"""
    
    # 调用 AI
    with tempfile.TemporaryDirectory() as tmp_dir:
        memory = DiskMemory(tmp_dir)
        prompt = Prompt(stage_a_prompt)
        
        messages = ai.next(
            messages=[HumanMessage(content=stage_a_prompt)],
            step_name="improve_stage_a_select_files"
        )
        
        response_text = messages[-1].content
        
        # 解析 JSON 响应
        try:
            # 尝试提取 JSON（可能被包裹在 markdown 中）
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)
            
            selection = json.loads(response_text)
            
            # 过滤掉 locked 文件
            filtered_selected = []
            for item in selection.get('selected', []):
                file_path = item.get('path', '')
                is_locked = any(
                    fnmatch.fnmatch(file_path, pattern) for pattern in locked_paths
                )
                if not is_locked:
                    filtered_selected.append(item)
                else:
                    print(f"   ⚠️  过滤了 locked 文件: {file_path}")
            
            selection['selected'] = filtered_selected
            return selection
            
        except Exception as e:
            print(f"   ✗ 阶段 A JSON 解析失败: {e}")
            print(f"   响应内容: {response_text[:200]}")
            # 降级：选择入口文件
            return {
                "selected": [
                    {"path": "src/pages/Index.tsx", "reason": "fallback to entry point", "edit_scope": "modify"}
                ],
                "not_selected_reasoning": "JSON parse failed, using fallback",
                "needs_dependency": []
            }


def improve_stage_b_apply_changes(
    files: Dict[str, str],
    improvement_request: str,
    selected_files: List[Dict[str, Any]],
    ai,
    preprompts_holder
) -> Dict[str, str]:
    """
    改进阶段 B：对选中的文件执行改进
    
    Returns:
        改进后的文件字典
    """
    selected_paths = [item['path'] for item in selected_files]
    
    # 只传选中文件的内容
    selected_content = format_files_content(files, selected_paths)
    
    # 构建阶段 B prompt（使用 BaseRules）
    base_rules = build_base_rules(mode='improve')
    
    stage_b_prompt = f"""You are improving selected files in a React + TypeScript application.

IMPROVEMENT REQUEST:
{improvement_request}

SELECTED FILES FOR MODIFICATION:
{json.dumps(selected_files, indent=2, ensure_ascii=False)}

CURRENT CONTENT OF SELECTED FILES:
{selected_content}

{base_rules}

OUTPUT FORMAT:
filename.tsx
```
COMPLETE FILE CONTENT
```

YOU ARE WORKING WITH:
- React + TypeScript + Vite + Tailwind + shadcn/ui
- Import shadcn from @/components/ui/ (lowercase)
- Keep all configuration files unchanged

Output ALL modified files with COMPLETE content:"""
    
    # 记录 telemetry
    log_prompt_telemetry(
        prompt=stage_b_prompt,
        mode='improve',
        activated_fragments=[],
        spec_mode='none',
        context={
            'policy_version': get_policy_version(),
            'selected_files': selected_paths
        }
    )
    
    # 调用 AI
    with tempfile.TemporaryDirectory() as tmp_dir:
        memory = DiskMemory(tmp_dir)
        prompt = Prompt(stage_b_prompt)
        improved_files = gen_code(ai, prompt, memory, preprompts_holder)
    
    return improved_files


@app.post("/improve")
def improve_code(
    files: Dict[str, str] = Body(...),
    improvement_request: str = Body(...)
) -> Dict[str, str]:
    """
    改进已生成的代码（两阶段流程）
    
    Args:
        files: 当前的文件字典
        improvement_request: 改进要求
        
    Returns:
        Dict[str, str]: 改进后的文件字典
    """
    if ai is None:
        raise HTTPException(
            status_code=503,
            detail="AI 服务未就绪"
        )
    
    try:
        # 检测项目类型
        is_react_project = any(
            'package.json' in f or f.endswith('.tsx') or f.endswith('.jsx')
            for f in files.keys()
        )
        
        print(f"📝 收到改进请求: {improvement_request[:100]}...")
        print(f"   项目类型: {'React' if is_react_project else '静态 HTML'}")
        
        if not is_react_project:
            # 静态 HTML 项目：使用原始流程（无需两阶段）
            files_content = "\n\n".join([
                f"{filename}\n```\n{content}\n```"
                for filename, content in files.items()
            ])
            
            enhanced_prompt = f"""以下是当前的代码：

{files_content}

用户的改进要求：{improvement_request}

请提供改进后的完整代码。要求：
- 保持 HTML/CSS/JavaScript 的 Web 应用格式
- 只修改需要改进的部分
- 保持文件结构不变

输出格式：
FILENAME
```
CODE
```
"""
            
            with tempfile.TemporaryDirectory() as tmp_dir:
                memory = DiskMemory(tmp_dir)
                prompt = Prompt(enhanced_prompt)
                improved_files = gen_code(ai, prompt, memory, preprompts_holder)
            
            print(f"✓ 改进完成，共 {len(improved_files)} 个文件")
            return dict(improved_files)
        
        # React 项目：使用两阶段流程
        print(f"   🔍 阶段 A: 选择需要修改的文件...")
        selection = improve_stage_a_select_files(files, improvement_request, ai)
        
        selected_count = len(selection['selected'])
        print(f"   ✓ 阶段 A 完成: 选中 {selected_count} 个文件")
        for item in selection['selected']:
            print(f"     - {item['path']}: {item['reason']}")
        
        if selected_count == 0:
            print(f"   ⚠️  没有文件被选中，返回原始文件")
            return files
        
        print(f"   🔧 阶段 B: 执行改进...")
        improved_files = improve_stage_b_apply_changes(
            files,
            improvement_request,
            selection['selected'],
            ai,
            preprompts_holder
        )
        
        print(f"   AI 返回了 {len(improved_files)} 个文件")
        
        # 检测新增的依赖并仲裁
        requested_deps = detect_dependencies_in_files(improved_files)
        approved_deps = {}
        rejected_deps = {}
        
        if requested_deps:
            print(f"   🔍 检测到 {len(requested_deps)} 个新依赖，提交仲裁...")
            approved_deps, rejected_deps, dep_warnings = arbiter.arbitrate(requested_deps)
            print_arbitration_summary(approved_deps, rejected_deps, dep_warnings)
        
        # 合并文件
        result = dict(files)  # 复制原文件
        result.update(improved_files)  # 更新修改的文件
        
        # 更新 vibe.meta.json（合并依赖信息）
        if approved_deps or requested_deps:
            vibe_meta = {}
            if 'vibe.meta.json' in result:
                try:
                    vibe_meta = json.loads(result['vibe.meta.json'])
                except:
                    pass
            
            # 合并依赖信息
            existing_deps = vibe_meta.get('dependencies', {})
            updated_report = arbiter.create_dependency_report(
                requested_deps,
                approved_deps,
                rejected_deps
            )
            
            # 合并批准的依赖（保留旧的 + 新的）
            all_approved = existing_deps.get('approved', {}) if isinstance(existing_deps, dict) else {}
            all_approved.update(approved_deps)
            updated_report['approved'] = all_approved
            
            vibe_meta['dependencies'] = updated_report
            vibe_meta['last_improved_at'] = __import__('datetime').datetime.now().isoformat()
            
            result['vibe.meta.json'] = json.dumps(vibe_meta, indent=2, ensure_ascii=False)
            print(f"   ✓ 已更新 vibe.meta.json（累计批准依赖: {len(all_approved)}）")
        
        print(f"✓ 改进完成，最终 {len(result)} 个文件")
        return result
        
    except Exception as e:
        print(f"✗ 改进失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"代码改进失败: {str(e)}"
        )


@app.post("/generate-stream")
async def generate_app_stream(
    prompt_text: str = Body(..., embed=True),
    use_template: bool = Body(default=True, embed=True),
    template_name: str = Body(default=None, embed=True),
    style: str = Body(default="auto", embed=True)
):
    """
    流式生成应用代码 (SSE)
    
    返回 Server-Sent Events 流，实时推送生成进度
    """
    if ai is None:
        raise HTTPException(
            status_code=503,
            detail="AI 服务未就绪，请检查 API key 配置"
        )
    
    if not prompt_text or not prompt_text.strip():
        raise HTTPException(
            status_code=400,
            detail="prompt_text 不能为空"
        )
    
    async def event_generator():
        try:
            prompt_text_clean = prompt_text.strip()
            
            # 步骤 1: 发送分析状态
            yield f"data: {json.dumps({'type': 'status', 'content': '正在分析需求...'})}\n\n"
            await asyncio.sleep(0.1)
            
            # 步骤 2: 检测应用类型和模板
            if use_template:
                app_type = custom_preprompts_manager.detect_app_type(prompt_text_clean)
                detected_template = template_name or template_manager.detect_template_type(prompt_text_clean)
                
                yield f"data: {json.dumps({'type': 'status', 'content': f'使用模板: {detected_template}'})}\n\n"
                await asyncio.sleep(0.1)
                
                # 步骤 3: 生成代码
                yield f"data: {json.dumps({'type': 'status', 'content': '正在生成代码...'})}\n\n"
                
                # 调用生成函数
                files_dict = await asyncio.to_thread(
                    generate_with_template, 
                    prompt_text_clean, 
                    detected_template,
                    style
                )
                
                # 步骤 4: 发送文件生成事件
                for filename in files_dict.keys():
                    yield f"data: {json.dumps({'type': 'file', 'filename': filename})}\n\n"
                    await asyncio.sleep(0.05)  # 小延迟让前端有时间渲染
                
                # 步骤 5: 发送完成事件
                yield f"data: {json.dumps({'type': 'complete', 'files': files_dict, 'filesCount': len(files_dict)})}\n\n"
                
            else:
                # 传统模式
                yield f"data: {json.dumps({'type': 'status', 'content': '正在生成代码...'})}\n\n"
                
                files_dict = await asyncio.to_thread(
                    generate_traditional,
                    prompt_text_clean
                )
                
                for filename in files_dict.keys():
                    yield f"data: {json.dumps({'type': 'file', 'filename': filename})}\n\n"
                    await asyncio.sleep(0.05)
                
                yield f"data: {json.dumps({'type': 'complete', 'files': files_dict, 'filesCount': len(files_dict)})}\n\n"
            
        except Exception as e:
            print(f"✗ 流式生成失败: {e}")
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # 禁用 nginx 缓冲
        }
    )


@app.post("/improve-stream")
async def improve_code_stream(
    files: Dict[str, str] = Body(...),
    improvement_request: str = Body(...)
):
    """
    流式改进已生成的代码 (SSE)
    
    返回 Server-Sent Events 流，实时推送改进进度
    """
    if ai is None:
        raise HTTPException(
            status_code=503,
            detail="AI 服务未就绪"
        )
    
    async def event_generator():
        try:
            # 检测项目类型
            is_react_project = any(
                'package.json' in f or f.endswith('.tsx') or f.endswith('.jsx')
                for f in files.keys()
            )
            
            if not is_react_project:
                # 静态 HTML 项目：使用原始流程
                yield f"data: {json.dumps({'type': 'status', 'content': '正在分析改进需求...'})}\n\n"
                await asyncio.sleep(0.1)
                
                yield f"data: {json.dumps({'type': 'status', 'content': '正在优化代码...'})}\n\n"
                
                files_content = "\n\n".join([
                    f"{filename}\n```\n{content}\n```"
                    for filename, content in files.items()
                ])
                
                enhanced_prompt = f"""以下是当前的代码：

{files_content}

用户的改进要求：{improvement_request}

请提供改进后的完整代码。要求：
- 保持 HTML/CSS/JavaScript 的 Web 应用格式
- 只修改需要改进的部分
- 保持文件结构不变

输出格式：
FILENAME
```
CODE
```
"""
                
                with tempfile.TemporaryDirectory() as tmp_dir:
                    memory = DiskMemory(tmp_dir)
                    prompt = Prompt(enhanced_prompt)
                    improved_files = await asyncio.to_thread(
                        gen_code, ai, prompt, memory, preprompts_holder
                    )
                
                for filename in improved_files.keys():
                    yield f"data: {json.dumps({'type': 'file', 'filename': filename})}\n\n"
                    await asyncio.sleep(0.05)
                
                yield f"data: {json.dumps({'type': 'complete', 'files': dict(improved_files), 'filesCount': len(improved_files)})}\n\n"
                return
            
            # React 项目：使用两阶段流程
            # 步骤 1: 阶段 A - 选择文件
            yield f"data: {json.dumps({'type': 'status', 'content': '正在分析需要修改的文件...'})}\n\n"
            await asyncio.sleep(0.1)
            
            selection = await asyncio.to_thread(
                improve_stage_a_select_files,
                files,
                improvement_request,
                ai
            )
            
            selected_count = len(selection['selected'])
            
            if selected_count == 0:
                yield f"data: {json.dumps({'type': 'status', 'content': '没有文件需要修改'})}\n\n"
                yield f"data: {json.dumps({'type': 'complete', 'files': files, 'filesCount': len(files)})}\n\n"
                return
            
            # 步骤 2: 推送选中的文件
            yield f"data: {json.dumps({'type': 'status', 'content': f'选中了 {selected_count} 个文件进行修改'})}\n\n"
            await asyncio.sleep(0.1)
            
            for item in selection['selected']:
                yield f"data: {json.dumps({'type': 'selected_file', 'path': item['path'], 'reason': item['reason']})}\n\n"
                await asyncio.sleep(0.05)
            
            # 步骤 3: 阶段 B - 执行改进
            yield f"data: {json.dumps({'type': 'status', 'content': '正在优化代码...'})}\n\n"
            await asyncio.sleep(0.1)
            
            improved_files = await asyncio.to_thread(
                improve_stage_b_apply_changes,
                files,
                improvement_request,
                selection['selected'],
                ai,
                preprompts_holder
            )
            
            # 步骤 4: 检测和仲裁新依赖
            requested_deps = detect_dependencies_in_files(improved_files)
            approved_deps = {}
            rejected_deps = {}
            
            if requested_deps:
                yield f"data: {json.dumps({'type': 'status', 'content': f'检测到 {len(requested_deps)} 个新依赖，正在仲裁...'})}\n\n"
                approved_deps, rejected_deps, dep_warnings = arbiter.arbitrate(requested_deps)
                print_arbitration_summary(approved_deps, rejected_deps, dep_warnings)
            
            # 步骤 5: 合并文件
            result = dict(files)
            result.update(improved_files)
            
            # 更新 vibe.meta.json
            if approved_deps or requested_deps:
                vibe_meta = {}
                if 'vibe.meta.json' in result:
                    try:
                        vibe_meta = json.loads(result['vibe.meta.json'])
                    except:
                        pass
                
                existing_deps = vibe_meta.get('dependencies', {})
                updated_report = arbiter.create_dependency_report(
                    requested_deps,
                    approved_deps,
                    rejected_deps
                )
                
                # 合并批准的依赖
                all_approved = existing_deps.get('approved', {}) if isinstance(existing_deps, dict) else {}
                all_approved.update(approved_deps)
                updated_report['approved'] = all_approved
                
                vibe_meta['dependencies'] = updated_report
                vibe_meta['last_improved_at'] = __import__('datetime').datetime.now().isoformat()
                
                result['vibe.meta.json'] = json.dumps(vibe_meta, indent=2, ensure_ascii=False)
            
            # 步骤 7: 发送文件更新事件
            for filename in improved_files.keys():
                yield f"data: {json.dumps({'type': 'file', 'filename': filename})}\n\n"
                await asyncio.sleep(0.05)
            
            # 步骤 8: 发送完成事件
            yield f"data: {json.dumps({'type': 'complete', 'files': result, 'filesCount': len(result)})}\n\n"
            
        except Exception as e:
            print(f"✗ 流式改进失败: {e}")
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/health")
def health_check():
    """详细的健康检查"""
    return {
        "status": "healthy",
        "ai_initialized": ai is not None,
        "model": ai.model_name if ai else None,
        "preprompts_loaded": preprompts_holder is not None,
        "api_keys_configured": {
            "openai": bool(os.getenv("OPENAI_API_KEY")),
            "anthropic": bool(os.getenv("ANTHROPIC_API_KEY"))
        }
    }


if __name__ == "__main__":
    import uvicorn
    print("🚀 启动 Vibecoding Platform 后端服务...")
    print("📖 API 文档: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

