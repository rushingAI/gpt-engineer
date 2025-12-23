"""
Preprompts 扫描门禁 - 检测单文件禁令漏网
确保所有 preprompts 都已更新到受控多文件结构
"""
import sys
import re
from pathlib import Path

# 检测的关键词模式（表示单文件限制）
SINGLE_FILE_PATTERNS = [
    r'single\s+file',
    r'Index\.tsx\s+only',
    r'do\s+not\s+create\s+new\s+files',
    r'NEVER\s+EVER\s+CREATE\s+SEPARATE\s+COMPONENT\s+FILES',
    r'DO\s+NOT\s+create\s+separate\s+component\s+files',
    r'write\s+ALL\s+.*\s+in\s+Index\.tsx',
    r'everything\s+in\s+Index\.tsx',
    r'one\s+file',
    r'ALL\s+IN\s+ONE\s+FILE',
]

def scan_preprompts(preprompts_dir: Path):
    """扫描所有 preprompt 文件，检测单文件限制"""
    issues = []
    
    # 遍历所有 preprompt 文件
    for preprompt_file in preprompts_dir.iterdir():
        if preprompt_file.is_file() and preprompt_file.name != 'README.md':
            content = preprompt_file.read_text(encoding='utf-8')
            
            # 检测每个模式
            for pattern in SINGLE_FILE_PATTERNS:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    # 计算行号
                    line_no = content[:match.start()].count('\n') + 1
                    issues.append({
                        'file': preprompt_file.name,
                        'line': line_no,
                        'pattern': pattern,
                        'snippet': match.group(0)
                    })
    
    return issues


def main():
    """主函数"""
    print("=" * 80)
    print("Preprompts 扫描门禁 - 检测单文件禁令")
    print("=" * 80)
    
    # 获取 preprompts_custom 目录
    backend_dir = Path(__file__).parent
    preprompts_dir = backend_dir / 'preprompts_custom'
    
    if not preprompts_dir.exists():
        print(f"❌ 错误：preprompts 目录不存在: {preprompts_dir}")
        return 1
    
    print(f"\n📂 扫描目录: {preprompts_dir}")
    
    # 扫描
    issues = scan_preprompts(preprompts_dir)
    
    # 报告
    print(f"\n{'='*80}")
    print("扫描结果:")
    print(f"{'='*80}\n")
    
    if not issues:
        print("✅ 未发现单文件限制关键词 - 所有 preprompts 已更新")
        return 0
    else:
        print(f"⚠️  发现 {len(issues)} 处单文件限制关键词:\n")
        
        # 按文件分组显示
        files_with_issues = {}
        for issue in issues:
            filename = issue['file']
            if filename not in files_with_issues:
                files_with_issues[filename] = []
            files_with_issues[filename].append(issue)
        
        for filename, file_issues in files_with_issues.items():
            print(f"📄 {filename}:")
            for issue in file_issues:
                print(f"   Line {issue['line']}: \"{issue['snippet']}\"")
                print(f"   匹配模式: {issue['pattern']}")
            print()
        
        print("❌ 扫描失败 - 请更新上述文件以支持受控多文件结构")
        print("\n建议:")
        print("  - 将 'DO NOT create separate files' 改为 '推荐在 generated/ 目录拆分组件'")
        print("  - 将 'Index.tsx only' 改为 'Index.tsx 编排，generated/ 存放领域组件'")
        print("  - 移除 'NEVER CREATE SEPARATE COMPONENT FILES' 等硬性禁令")
        
        return 1


if __name__ == '__main__':
    sys.exit(main())

