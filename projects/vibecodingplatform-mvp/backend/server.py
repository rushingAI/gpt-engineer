"""
Vibecoding Platform MVP - Backend Server

This FastAPI server wraps gpt-engineer's core functionality to expose
code generation capabilities via REST API.
"""

import os
import tempfile
from pathlib import Path
from typing import Dict
import json
import asyncio

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

# 导入模板管理器和自定义 preprompts
from template_manager import template_manager
from preprompt_manager import custom_preprompts_manager
from dependency_detector import detect_dependencies_in_files, add_dependencies_to_package_json

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
        model_name=os.getenv("MODEL_NAME", "gpt-4o"),
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
    template_name: str = Body(default=None, embed=True)
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
        
    Returns:
        Dict[str, str]: 文件名到文件内容的映射字典
        
    Example:
        POST /generate
        {
            "prompt_text": "创建一个现代化的 landing page",
            "use_template": true
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
            return generate_with_template(prompt_text, template_name)
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


def generate_with_template(prompt_text: str, template_name: str = None) -> Dict[str, str]:
    """模板生成模式：基于 React + TypeScript 模板生成"""
    
    # 1. 检测应用类型和模板
    app_type = custom_preprompts_manager.detect_app_type(prompt_text)
    if template_name is None:
        template_name = template_manager.detect_template_type(prompt_text)
    
    print(f"   应用类型: {app_type}")
    print(f"   使用模板: {template_name}")
    
    # 2. 加载模板
    template = template_manager.get_template(template_name)
    if template is None:
        raise Exception(f"模板不存在: {template_name}")
    
    # 3. 构建增强的系统提示词
    system_prompt = custom_preprompts_manager.build_system_prompt(app_type)
    
    # 4. 构建用户提示词
    # 告诉 AI 它正在使用模板，只需要生成业务代码
    enhanced_prompt = f"""{system_prompt}

================================================================================
USER REQUEST:
================================================================================

{prompt_text}

IMPORTANT INSTRUCTIONS:
- You are working with a pre-configured React + TypeScript project with Cyberpunk design system
- DO NOT generate configuration files (package.json, vite.config.ts, etc.)
- DO NOT generate src/main.tsx - the entry point is already configured
- DO NOT generate src/index.css - global styles are already configured
- Focus ONLY on creating the page components and business logic
- Use the pre-installed shadcn/ui components from @/components/ui/
- Import icons from lucide-react
- Use framer-motion for animations
- Follow the Cyberpunk design system (deep dark bg, neon cyan primary)
- The main entry point is src/pages/Index.tsx - this is where you should create your UI

⚠️ CRITICAL - ROUTING SETUP:
- The BrowserRouter is ALREADY set up in src/main.tsx
- If you generate src/App.tsx, it should ONLY contain <Routes> and <Route>, NOT <BrowserRouter>
- Example correct App.tsx:
  import from 'react-router-dom' Routes and Route
  import Index from pages
  function App returns Routes with Route elements
  DO NOT wrap with BrowserRouter!
- NEVER wrap <Routes> with <BrowserRouter> in App.tsx!

⚠️ CRITICAL - COMPONENT IMPORT PATHS:
shadcn/ui component files are LOWERCASE! You MUST use:
  ✅ import {{ Button }} from '@/components/ui/button'
  ✅ import {{ Card }} from '@/components/ui/card'  
  ✅ import {{ Input }} from '@/components/ui/input'
  
  ❌ NOT from '@/components/ui/Button'
  ❌ NOT from '@/components/ui/Card'
  ❌ NOT from '@/components/ui/Input'

⚠️ CRITICAL - FILE OUTPUT FORMAT:
You MUST output files in this EXACT format:

FILENAME
```
CODE
```

Example:
src/pages/Index.tsx
```
import React from 'react';
export default function Index() {{
  return <div>Hello</div>;
}}
```

DO NOT use markdown headings (###) or add descriptions!
DO NOT use language tags like ```tsx or ```typescript!
Just: FILENAME then ``` CODE ```

Generate ALL necessary files including src/pages/Index.tsx and component files.
"""
    
    # 5. 调用 AI 生成代码
    with tempfile.TemporaryDirectory() as tmp_dir:
        memory = DiskMemory(tmp_dir)
        prompt = Prompt(enhanced_prompt)
        
        # 使用原始的 preprompts_holder（用于文件格式等基础指导）
        generated_files = gen_code(ai, prompt, memory, preprompts_holder)
        
        print(f"   AI 生成了 {len(generated_files)} 个文件")
        
        # 6. 后处理：修正组件导入路径和图标导入
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
        
        # 7. 检测生成代码中的额外依赖
        extra_deps = detect_dependencies_in_files(fixed_generated_files)
        
        # 8. 合并模板和生成的文件
        template_files = template['files']
        
        # 如果检测到额外依赖，更新 package.json
        if extra_deps and 'package.json' in template_files:
            print(f"   🔧 自动添加 {len(extra_deps)} 个额外依赖到 package.json")
            template_files['package.json'] = add_dependencies_to_package_json(
                template_files['package.json'],
                extra_deps
            )
        
        final_files = template_manager.merge_files(template_files, fixed_generated_files)
        
        print(f"✓ 模板模式生成完成，最终 {len(final_files)} 个文件")
        
        return final_files


@app.post("/improve")
def improve_code(
    files: Dict[str, str] = Body(...),
    improvement_request: str = Body(...)
) -> Dict[str, str]:
    """
    改进已生成的代码
    
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
        
        # 构造文件内容
        files_content = "\n\n".join([
            f"{filename}\n```\n{content}\n```"
            for filename, content in files.items()
        ])
        
        # 根据项目类型构造不同的 prompt
        if is_react_project:
            # React 项目改进
            enhanced_prompt = f"""You are improving a React + TypeScript application.

CURRENT CODE:
{files_content}

USER REQUEST:
{improvement_request}

IMPORTANT INSTRUCTIONS:
- This is a React + TypeScript project using Vite, Tailwind CSS, shadcn/ui with Cyberpunk design system
- Modify ONLY the files that need changes based on the user's request
- Keep all configuration files unchanged (package.json, vite.config.js, etc.)
- DO NOT modify src/main.tsx or src/index.css unless absolutely necessary
- Use @/components/ui/ imports for shadcn components
- Import icons from lucide-react
- Follow the Cyberpunk design system (deep dark bg, neon cyan primary)
- IMPORTANT: BrowserRouter is already set up in main.tsx - do NOT add another one in App.tsx

⚠️ CRITICAL - FILE OUTPUT FORMAT:
You MUST output files in this EXACT format:

FILENAME
```
CODE
```

DO NOT use markdown headings (###) or add descriptions!
DO NOT use language tags like ```tsx or ```typescript!
Just: FILENAME then ``` CODE ```

Output ALL modified files with their complete content.
"""
        else:
            # 静态 HTML 项目改进
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
            
        print(f"   AI 返回了 {len(improved_files)} 个文件")
        
        # 对于 React 项目，需要合并文件而不是完全替换
        if is_react_project:
            # 保留未修改的文件
            result = dict(files)  # 复制原文件
            result.update(improved_files)  # 更新修改的文件
            print(f"✓ 改进完成，最终 {len(result)} 个文件")
            return result
        else:
            print(f"✓ 改进完成，共 {len(improved_files)} 个文件")
            return dict(improved_files)
        
    except Exception as e:
        print(f"✗ 改进失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"代码改进失败: {str(e)}"
        )


@app.post("/generate-stream")
async def generate_app_stream(
    prompt_text: str = Body(..., embed=True),
    use_template: bool = Body(default=True, embed=True),
    template_name: str = Body(default=None, embed=True)
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
                    detected_template
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
            # 步骤 1: 发送分析状态
            yield f"data: {json.dumps({'type': 'status', 'content': '正在分析改进需求...'})}\n\n"
            await asyncio.sleep(0.1)
            
            # 检测项目类型
            is_react_project = any(
                'package.json' in f or f.endswith('.tsx') or f.endswith('.jsx')
                for f in files.keys()
            )
            
            # 步骤 2: 构造 prompt
            yield f"data: {json.dumps({'type': 'status', 'content': '正在优化代码...'})}\n\n"
            
            # 构造文件内容
            files_content = "\n\n".join([
                f"{filename}\n```\n{content}\n```"
                for filename, content in files.items()
            ])
            
            # 根据项目类型构造不同的 prompt
            if is_react_project:
                enhanced_prompt = f"""You are improving a React + TypeScript application.

CURRENT CODE:
{files_content}

USER REQUEST:
{improvement_request}

IMPORTANT INSTRUCTIONS:
- This is a React + TypeScript project using Vite, Tailwind CSS, shadcn/ui with Cyberpunk design system
- Modify ONLY the files that need changes based on the user's request
- Keep all configuration files unchanged (package.json, vite.config.js, etc.)
- DO NOT modify src/main.tsx or src/index.css unless absolutely necessary
- Use @/components/ui/ imports for shadcn components
- Import icons from lucide-react
- Follow the Cyberpunk design system (deep dark bg, neon cyan primary)
- IMPORTANT: BrowserRouter is already set up in main.tsx - do NOT add another one in App.tsx

⚠️ CRITICAL - FILE OUTPUT FORMAT:
You MUST output files in this EXACT format:

FILENAME
```
CODE
```

DO NOT use markdown headings (###) or add descriptions!
DO NOT use language tags like ```tsx or ```typescript!
Just: FILENAME then ``` CODE ```

Output ALL modified files with their complete content.
"""
            else:
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
            
            # 步骤 3: 调用 AI 改进
            with tempfile.TemporaryDirectory() as tmp_dir:
                memory = DiskMemory(tmp_dir)
                prompt = Prompt(enhanced_prompt)
                improved_files = await asyncio.to_thread(
                    gen_code, ai, prompt, memory, preprompts_holder
                )
            
            # 步骤 4: 合并文件
            if is_react_project:
                result = dict(files)
                result.update(improved_files)
                improved_files = result
            
            # 步骤 5: 发送文件更新事件
            for filename in improved_files.keys():
                yield f"data: {json.dumps({'type': 'file', 'filename': filename})}\n\n"
                await asyncio.sleep(0.05)
            
            # 步骤 6: 发送完成事件
            yield f"data: {json.dumps({'type': 'complete', 'files': dict(improved_files), 'filesCount': len(improved_files)})}\n\n"
            
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

