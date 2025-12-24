#!/bin/bash
# 快速运行回滚功能测试

cd "$(dirname "$0")/backend"

echo "=================================="
echo "运行自愈循环回滚功能测试..."
echo "=================================="
echo ""

python3 test_self_heal_rollback.py

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "✅ 测试执行完成！"
    echo "请查看上述输出，验证回滚功能是否正常工作。"
else
    echo ""
    echo "❌ 测试执行失败，退出码: $exit_code"
    echo "请查看错误信息并修复。"
fi

exit $exit_code

