#!/bin/bash

echo "================================================================================"
echo "第七阶段：验证生成质量（需要后端服务运行）"
echo "================================================================================"
echo ""

# 检查服务是否运行
echo "🔍 1. 检查后端服务状态..."
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ❌ 后端服务未运行"
    echo ""
    echo "请先启动后端服务："
    echo "   cd /Users/gaochang/gpt-engineer/projects/vibecodingplatform-mvp/backend"
    echo "   ./run.sh"
    echo ""
    echo "服务启动后，重新运行此脚本："
    echo "   ./run_stage7_test.sh"
    exit 1
fi

SERVICE_INFO=$(curl -s http://localhost:8000/health | jq -r '{status, ai_initialized, model}')
echo "   ✅ 后端服务运行中"
echo "   服务信息: $SERVICE_INFO"
echo ""

# 测试案例 1: 紫色梦幻风格 → aurora
echo "🎨 2. 测试案例 1: 紫色梦幻风格 → aurora"
echo "   Prompt: '创建一个紫色梦幻风格的 portfolio'"
echo "   正在生成（预计 30-60 秒）..."
echo ""

RESPONSE1=$(curl -s -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_text": "创建一个紫色梦幻风格的 portfolio",
    "use_template": true,
    "style": "auto"
  }')

if echo "$RESPONSE1" | jq -e '."vibe.meta.json"' > /dev/null 2>&1; then
    META1=$(echo "$RESPONSE1" | jq -r '."vibe.meta.json"' | jq '.')
    STYLE1=$(echo "$META1" | jq -r '.style')
    SOURCE1=$(echo "$META1" | jq -r '.style_source')
    
    echo "   ✅ 生成成功"
    echo "   风格: $STYLE1"
    echo "   来源: $SOURCE1"
    echo "   元数据:"
    echo "$META1" | jq '{style, style_source, template_name, metadata}' | sed 's/^/      /'
    
    # 验证风格
    if [ "$STYLE1" = "aurora" ]; then
        echo "   ✅ 风格匹配正确 (aurora)"
    else
        echo "   ⚠️  风格不符合预期 (期望: aurora, 实际: $STYLE1)"
    fi
    
    # 保存结果
    echo "$RESPONSE1" > /tmp/test_aurora_project.json
    echo "   💾 已保存到: /tmp/test_aurora_project.json"
    
    # 文件统计
    FILE_COUNT1=$(echo "$RESPONSE1" | jq 'keys | length')
    echo "   📁 生成文件数: $FILE_COUNT1"
else
    echo "   ❌ 生成失败"
    echo "$RESPONSE1" | head -50
fi

echo ""
echo "─────────────────────────────────────────────────────────────────────────────"
echo ""

# 测试案例 2: 显式指定 glass 风格
echo "🎨 3. 测试案例 2: 显式指定 glass 风格"
echo "   Prompt: '创建一个简单的待办应用'"
echo "   Style: glass (显式指定)"
echo "   正在生成（预计 30-60 秒）..."
echo ""

RESPONSE2=$(curl -s -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_text": "创建一个简单的待办应用",
    "use_template": true,
    "style": "glass"
  }')

if echo "$RESPONSE2" | jq -e '."vibe.meta.json"' > /dev/null 2>&1; then
    META2=$(echo "$RESPONSE2" | jq -r '."vibe.meta.json"' | jq '.')
    STYLE2=$(echo "$META2" | jq -r '.style')
    SOURCE2=$(echo "$META2" | jq -r '.style_source')
    
    echo "   ✅ 生成成功"
    echo "   风格: $STYLE2"
    echo "   来源: $SOURCE2"
    echo "   元数据:"
    echo "$META2" | jq '{style, style_source, template_name}' | sed 's/^/      /'
    
    # 验证风格
    if [ "$STYLE2" = "glass" ] && [ "$SOURCE2" = "explicit" ]; then
        echo "   ✅ 显式指定正确生效 (glass, explicit)"
    else
        echo "   ⚠️  显式指定未生效 (期望: glass/explicit, 实际: $STYLE2/$SOURCE2)"
    fi
    
    # 保存结果
    echo "$RESPONSE2" > /tmp/test_glass_project.json
    echo "   💾 已保存到: /tmp/test_glass_project.json"
    
    # 文件统计
    FILE_COUNT2=$(echo "$RESPONSE2" | jq 'keys | length')
    echo "   📁 生成文件数: $FILE_COUNT2"
else
    echo "   ❌ 生成失败"
    echo "$RESPONSE2" | head -50
fi

echo ""
echo "================================================================================"
echo "📊 测试总结"
echo "================================================================================"
echo ""
echo "测试案例 1 (紫色梦幻 → aurora):"
if [ "$STYLE1" = "aurora" ]; then
    echo "   ✅ 通过"
else
    echo "   ❌ 失败 (实际: $STYLE1)"
fi
echo ""
echo "测试案例 2 (显式指定 glass):"
if [ "$STYLE2" = "glass" ] && [ "$SOURCE2" = "explicit" ]; then
    echo "   ✅ 通过"
else
    echo "   ❌ 失败 (实际: $STYLE2/$SOURCE2)"
fi
echo ""
echo "生成的项目已保存到:"
echo "   - /tmp/test_aurora_project.json"
echo "   - /tmp/test_glass_project.json"
echo ""
echo "你可以提取这些文件并在浏览器中查看实际效果"
echo ""
echo "================================================================================"
echo "✅ 第七阶段测试完成"
echo "================================================================================"

