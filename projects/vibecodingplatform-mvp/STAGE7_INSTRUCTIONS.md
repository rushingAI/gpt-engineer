# 第七阶段测试说明

## 📋 测试目标

验证生成质量：实际调用 AI 生成项目，检查：
- 风格匹配是否正确
- 生成的文件是否完整
- vibe.meta.json 是否包含正确信息
- 模板文件是否正确应用

## 🚀 执行步骤

### 1. 启动后端服务

在一个终端中启动后端：

```bash
cd /Users/gaochang/gpt-engineer/projects/vibecodingplatform-mvp/backend
./run.sh
```

等待看到：
```
✓ AI 初始化成功，使用模型: gpt-4o
🚀 启动 Vibecoding Platform 后端服务...
```

### 2. 运行测试脚本

在**另一个终端**中运行测试：

```bash
cd /Users/gaochang/gpt-engineer/projects/vibecodingplatform-mvp/backend
./run_stage7_test.sh
```

### 3. 查看测试结果

测试将执行两个生成案例：

**案例 1：紫色梦幻风格 → aurora**
- Prompt: "创建一个紫色梦幻风格的 portfolio"
- 预期风格: aurora
- 预期来源: keyword_match
- 保存位置: `/tmp/test_aurora_project.json`

**案例 2：显式指定 glass**
- Prompt: "创建一个简单的待办应用"
- Style: glass (显式指定)
- 预期风格: glass
- 预期来源: explicit
- 保存位置: `/tmp/test_glass_project.json`

## ✅ 成功标准

- ✅ 案例 1 生成 aurora 风格
- ✅ 案例 2 生成 glass 风格且来源为 explicit
- ✅ 两个项目都包含 vibe.meta.json
- ✅ 生成的文件数量 > 20（包含所有必要文件）

## 🔍 可选：提取并查看生成的项目

如果想在浏览器中查看实际效果：

```bash
# 创建测试目录
mkdir -p /tmp/aurora_app
cd /tmp/aurora_app

# 提取文件
python3 << 'EOF'
import json
import os

with open('/tmp/test_aurora_project.json', 'r') as f:
    data = json.load(f)

for filename, content in data.items():
    os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
    with open(filename, 'w') as f:
        f.write(content)

print("✓ 文件提取完成")
EOF

# 安装依赖并运行
npm install
npm run dev
```

打开 http://localhost:5173 查看效果。

## 📊 预期输出示例

```
================================================================================
第七阶段：验证生成质量（需要后端服务运行）
================================================================================

🔍 1. 检查后端服务状态...
   ✅ 后端服务运行中
   服务信息: {"status":"healthy","ai_initialized":true,"model":"gpt-4o"}

🎨 2. 测试案例 1: 紫色梦幻风格 → aurora
   Prompt: '创建一个紫色梦幻风格的 portfolio'
   正在生成（预计 30-60 秒）...

   ✅ 生成成功
   风格: aurora
   来源: keyword_match
   元数据:
      {
        "style": "aurora",
        "style_source": "keyword_match",
        "template_name": "react-ts-shadcn-aurora",
        "metadata": {
          "detected_color": "紫, 紫色",
          "temperature": "cool",
          "matched_keyword": "梦幻"
        }
      }
   ✅ 风格匹配正确 (aurora)
   💾 已保存到: /tmp/test_aurora_project.json
   📁 生成文件数: 25

...

================================================================================
📊 测试总结
================================================================================

测试案例 1 (紫色梦幻 → aurora):
   ✅ 通过

测试案例 2 (显式指定 glass):
   ✅ 通过

================================================================================
✅ 第七阶段测试完成
================================================================================
```

## ⚠️ 注意事项

1. **API 消耗**：每次生成会消耗 API tokens（约 $0.02-0.05 per request）
2. **时间**：每个生成需要 30-60 秒
3. **服务要求**：确保后端服务正常运行且 AI 已初始化

## 🐛 常见问题

**Q: 服务启动失败怎么办？**
A: 检查 `.env` 文件是否配置了 `OPENAI_API_KEY` 或 `ANTHROPIC_API_KEY`

**Q: 生成失败怎么办？**
A: 查看后端日志：`tail -f /tmp/backend_server.log`（如果用脚本启动）

**Q: 风格匹配不正确怎么办？**
A: 重新运行测试，检查 style_selector.py 是否正确修复

