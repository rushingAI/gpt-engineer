"""
Vibecoding Platform MVP - Backend Server

This FastAPI server wraps gpt-engineer's core functionality to expose
code generation capabilities via REST API.
"""

import os
import tempfile
from pathlib import Path
from typing import Dict

from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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
        "ai_ready": ai is not None
    }


@app.post("/generate")
def generate_app(prompt_text: str = Body(..., embed=True)) -> Dict[str, str]:
    """
    根据自然语言提示词生成应用代码
    
    Args:
        prompt_text: 用户的自然语言描述
        
    Returns:
        Dict[str, str]: 文件名到文件内容的映射字典
        
    Example:
        POST /generate
        {
            "prompt_text": "创建一个简单的待办事项列表应用"
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
        # 使用临时目录来满足 DiskMemory 的要求，但我们实际上不需要持久化
        with tempfile.TemporaryDirectory() as tmp_dir:
            memory = DiskMemory(tmp_dir)
            prompt = Prompt(prompt_text.strip())
            
            print(f"📝 收到生成请求: {prompt_text[:100]}...")
            
            # 核心调用！直接获取生成的文件字典
            files_dict = gen_code(ai, prompt, memory, preprompts_holder)
            
            print(f"✓ 生成完成，共 {len(files_dict)} 个文件")
            
            # FilesDict 可以直接转为普通字典
            return dict(files_dict)
            
    except Exception as e:
        print(f"✗ 生成失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"代码生成失败: {str(e)}"
        )


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
        # 构造改进提示词
        files_content = "\n\n".join([
            f"文件: {filename}\n```\n{content}\n```"
            for filename, content in files.items()
        ])
        
        enhanced_prompt = f"""以下是当前的代码：

{files_content}

用户的改进要求：{improvement_request}

请提供改进后的完整代码。要求：
- 保持 HTML/CSS/JavaScript 的 Web 应用格式
- 只修改需要改进的部分
- 保持文件结构不变
- 修复所有提到的 bug
"""
        
        print(f"📝 收到改进请求: {improvement_request[:100]}...")
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            memory = DiskMemory(tmp_dir)
            prompt = Prompt(enhanced_prompt)
            improved_files = gen_code(ai, prompt, memory, preprompts_holder)
            
        print(f"✓ 改进完成，共 {len(improved_files)} 个文件")
        return dict(improved_files)
        
    except Exception as e:
        print(f"✗ 改进失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"代码改进失败: {str(e)}"
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

