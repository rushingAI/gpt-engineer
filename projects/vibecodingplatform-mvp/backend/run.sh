#!/bin/bash
# 后端启动脚本

echo "🚀 启动 Vibecoding Platform 后端..."

# 检查是否安装了依赖
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 检测到缺少依赖，正在安装..."
    pip install -r requirements.txt
fi

# 检查环境变量
if [ -z "$OPENAI_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  警告: 未检测到 OPENAI_API_KEY 或 ANTHROPIC_API_KEY"
    echo "请在项目根目录创建 .env 文件并配置 API key"
fi

# 启动服务
echo "🌐 服务地址: http://localhost:8000"
echo "📚 API 文档: http://localhost:8000/docs"
echo ""

uvicorn server:app --reload --host 0.0.0.0 --port 8000

