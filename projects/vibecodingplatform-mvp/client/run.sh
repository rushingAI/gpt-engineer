#!/bin/bash
# 前端启动脚本

echo "🎨 启动 Vibecoding Platform 前端..."

# 检查是否安装了依赖
if [ ! -d "node_modules" ]; then
    echo "📦 检测到缺少依赖，正在安装..."
    npm install
fi

echo "🌐 前端地址: http://localhost:5173"
echo "📡 请确保后端服务已启动在: http://localhost:8000"
echo ""

npm run dev

