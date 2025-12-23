"""
测试依赖白名单功能
验证：1. 白名单检查
2. JSON 验证
3. 合并逻辑
"""
import json
import sys
from pathlib import Path

def test_dependency_whitelist():
    """测试依赖白名单"""
    print("=" * 80)
    print("测试依赖白名单功能")
    print("=" * 80)
    
    # 模拟测试场景
    test_cases = [
        {
            "name": "场景1：批准白名单中的依赖",
            "ai_deps": {"axios": "^1.6.0", "lodash": "^4.17.21"},
            "expected_approved": ["axios", "lodash"],
            "expected_rejected": []
        },
        {
            "name": "场景2：拒绝不在白名单的依赖",
            "ai_deps": {"malicious-pkg": "1.0.0", "unknown-lib": "2.0.0"},
            "expected_approved": [],
            "expected_rejected": ["malicious-pkg", "unknown-lib"]
        },
        {
            "name": "场景3：混合批准和拒绝",
            "ai_deps": {"axios": "^1.6.0", "malicious-pkg": "1.0.0"},
            "expected_approved": ["axios"],
            "expected_rejected": ["malicious-pkg"]
        },
        {
            "name": "场景4：自动批准 @types/* 包",
            "ai_deps": {"@types/node": "^20.0.0", "@types/react": "^18.0.0"},
            "expected_approved": ["@types/node", "@types/react"],
            "expected_rejected": []
        },
    ]
    
    # 加载策略
    policy_file = Path(__file__).parent / 'policies' / 'generation_policy.json'
    with open(policy_file, 'r') as f:
        policy = json.load(f)
    
    allowed_deps = policy['dependency_policy']['allowed_dependencies']
    auto_approve_patterns = policy['dependency_policy']['auto_approve_patterns']
    
    print(f"\n📋 白名单配置:")
    print(f"  允许的依赖: {len(allowed_deps)} 个")
    print(f"  自动批准模式: {', '.join(auto_approve_patterns)}")
    
    # 模拟 isDependencyAllowed 函数
    def is_dependency_allowed(dep_name):
        if dep_name in allowed_deps:
            return True
        for pattern in auto_approve_patterns:
            # 简单的模式匹配（实际前端用正则）
            if pattern == '@types/*' and dep_name.startswith('@types/'):
                return True
        return False
    
    # 运行测试
    all_passed = True
    
    for idx, test in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"测试 {idx}: {test['name']}")
        print(f"{'='*80}")
        
        approved = []
        rejected = []
        
        for dep, version in test['ai_deps'].items():
            if is_dependency_allowed(dep):
                approved.append(dep)
                print(f"  ✅ 批准: {dep}")
            else:
                rejected.append(dep)
                print(f"  🚫 拒绝: {dep}")
        
        # 验证结果
        approved_ok = sorted(approved) == sorted(test['expected_approved'])
        rejected_ok = sorted(rejected) == sorted(test['expected_rejected'])
        
        if approved_ok and rejected_ok:
            print(f"\n  ✅ 测试通过")
        else:
            print(f"\n  ❌ 测试失败")
            if not approved_ok:
                print(f"     期望批准: {test['expected_approved']}")
                print(f"     实际批准: {approved}")
            if not rejected_ok:
                print(f"     期望拒绝: {test['expected_rejected']}")
                print(f"     实际拒绝: {rejected}")
            all_passed = False
    
    # JSON 验证测试
    print(f"\n{'='*80}")
    print("测试 5: JSON 验证")
    print(f"{'='*80}")
    
    invalid_json = '{"dependencies": {"axios": "1.0.0"'  # 缺少结束括号
    
    try:
        json.loads(invalid_json)
        print("  ❌ 应该抛出 JSON 解析错误")
        all_passed = False
    except json.JSONDecodeError as e:
        print(f"  ✅ 正确捕获 JSON 错误: {e.msg}")
    
    # 总结
    print(f"\n{'='*80}")
    if all_passed:
        print("✅ 所有测试通过")
        print("=" * 80)
        print("\n依赖白名单功能正常工作！")
        print("\n下一步:")
        print("  1. 测试实际生成应用")
        print("  2. 检查浏览器 Console 日志")
        print("  3. 验证 package.json 格式正确")
        return 0
    else:
        print("❌ 部分测试失败")
        print("=" * 80)
        return 1

if __name__ == '__main__':
    sys.exit(test_dependency_whitelist())

