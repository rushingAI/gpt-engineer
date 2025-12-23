"""
测试修复后的正则表达式
"""
import re

# 修复后的正则表达式
pattern = re.compile(r'^@types/')

# 测试用例
test_cases = [
    ('@types/node', True),
    ('@types/react', True),
    ('@types/lodash', True),
    ('axios', False),
    ('lodash', False),
    ('@tanstack/react-query', False),  # 注意：只匹配 @types/ 开头
]

print("=" * 80)
print("测试正则表达式: /^@types\//")
print("=" * 80)

all_passed = True

for package, expected in test_cases:
    result = bool(pattern.match(package))
    status = "✅" if result == expected else "❌"
    
    print(f"{status} '{package}' -> {result} (期望: {expected})")
    
    if result != expected:
        all_passed = False

print("\n" + "=" * 80)
if all_passed:
    print("✅ 所有测试通过！正则表达式工作正常")
else:
    print("❌ 部分测试失败")
print("=" * 80)

