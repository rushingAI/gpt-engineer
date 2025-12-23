"""
同步依赖白名单：从后端策略生成前端白名单代码
确保前后端保持一致
"""
import json
import sys
from pathlib import Path

def load_policy():
    """加载后端策略配置"""
    policy_file = Path(__file__).parent.parent / 'policies' / 'generation_policy.json'
    
    with open(policy_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_frontend_whitelist_code(policy):
    """生成前端白名单代码"""
    dep_policy = policy.get('dependency_policy', {})
    
    allowed_deps = dep_policy.get('allowed_dependencies', [])
    auto_approve_patterns = dep_policy.get('auto_approve_patterns', [])
    
    # 生成 JavaScript 代码
    code = f"""// 依赖白名单（与后端策略同步）
// 🤖 此部分由 backend/scripts/sync_dependency_whitelist.py 自动生成
// 请勿手动修改，运行 python backend/scripts/sync_dependency_whitelist.py 更新
const ALLOWED_DEPENDENCIES = [
"""
    
    for dep in allowed_deps:
        code += f"  '{dep}',\n"
    
    code += """];

// 自动批准的模式（类型定义等）
const AUTO_APPROVE_PATTERNS = [
"""
    
    for pattern in auto_approve_patterns:
        # 将字符串模式转换为正则表达式
        # @types/* -> /^@types\//
        if pattern == '@types/*':
            code += f"  /^@types\\//,  // 匹配所有以 @types/ 开头的包\n"
        else:
            # 转义特殊字符并转换为正则
            escaped = pattern.replace('/', '\\/')
            code += f"  /{escaped}/,\n"
    
    code += "];"
    
    return code

def find_frontend_file():
    """找到前端 webcontainer.js 文件"""
    frontend_file = Path(__file__).parent.parent.parent / 'client' / 'src' / 'utils' / 'webcontainer.js'
    
    if not frontend_file.exists():
        raise FileNotFoundError(f"前端文件不存在: {frontend_file}")
    
    return frontend_file

def update_frontend_file(frontend_file, new_code):
    """更新前端文件中的白名单部分"""
    content = frontend_file.read_text(encoding='utf-8')
    
    # 查找白名单定义的起始和结束位置
    start_marker = "// 依赖白名单（与后端策略同步）"
    end_marker = "AUTO_APPROVE_PATTERNS = ["
    
    start_idx = content.find(start_marker)
    if start_idx == -1:
        raise ValueError("找不到白名单起始标记")
    
    # 查找 AUTO_APPROVE_PATTERNS 数组的结束
    end_idx = content.find("];", content.find(end_marker, start_idx))
    if end_idx == -1:
        raise ValueError("找不到白名单结束标记")
    
    end_idx += 2  # 包含 '];'
    
    # 替换内容
    new_content = content[:start_idx] + new_code + "\n\n" + content[end_idx:]
    
    # 写回文件
    frontend_file.write_text(new_content, encoding='utf-8')

def main():
    """主函数"""
    print("=" * 80)
    print("同步依赖白名单：后端策略 → 前端实现")
    print("=" * 80)
    
    try:
        # 1. 加载后端策略
        print("\n📖 加载后端策略...")
        policy = load_policy()
        dep_policy = policy.get('dependency_policy', {})
        
        allowed_deps = dep_policy.get('allowed_dependencies', [])
        auto_approve = dep_policy.get('auto_approve_patterns', [])
        
        print(f"  ✅ 允许的依赖: {len(allowed_deps)} 个")
        print(f"  ✅ 自动批准模式: {len(auto_approve)} 个")
        
        # 2. 生成前端代码
        print("\n🔧 生成前端白名单代码...")
        new_code = generate_frontend_whitelist_code(policy)
        
        # 3. 查找前端文件
        print("\n📂 查找前端文件...")
        frontend_file = find_frontend_file()
        print(f"  ✅ 找到: {frontend_file}")
        
        # 4. 更新前端文件
        print("\n✏️  更新前端文件...")
        update_frontend_file(frontend_file, new_code)
        print("  ✅ 更新成功")
        
        # 5. 显示预览
        print("\n" + "=" * 80)
        print("前端白名单预览:")
        print("=" * 80)
        print(new_code)
        
        print("\n" + "=" * 80)
        print("✅ 同步完成！")
        print("=" * 80)
        print("\n请检查前端文件并提交更改:")
        print(f"  git diff {frontend_file}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 同步失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())

