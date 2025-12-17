#!/usr/bin/env python3
"""快速验证颜色匹配修复"""

from style_selector import select_style_deterministic

print("🔍 验证颜色匹配修复")
print("=" * 60)

# 最关键的测试用例
prompt = "创建一个紫色梦幻风格的 portfolio"
style, source, metadata = select_style_deterministic(prompt, "auto")

print(f"📝 测试: {prompt}")
print(f"✨ 结果: {style}")
print(f"📊 来源: {source}")
print(f"📦 元数据: {metadata}")
print()

if style == "aurora" and source == "keyword_match":
    print("✅ 修复成功！紫色梦幻正确匹配到 aurora 风格")
    print("🎉 你现在可以在前端重新测试了")
else:
    print("❌ 修复未生效")
    print(f"   预期: aurora (keyword_match)")
    print(f"   实际: {style} ({source})")

