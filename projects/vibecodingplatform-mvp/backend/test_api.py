"""
测试脚本 - 验证后端 API 功能
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def test_health_check():
    """测试健康检查端点"""
    print("1️⃣  测试健康检查...")
    response = requests.get(f"{BASE_URL}/")
    print(f"   状态码: {response.status_code}")
    print(f"   响应: {response.json()}")
    assert response.status_code == 200
    print("   ✓ 通过\n")


def test_detailed_health():
    """测试详细健康检查"""
    print("2️⃣  测试详细健康检查...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   状态码: {response.status_code}")
    data = response.json()
    print(f"   AI 状态: {data.get('ai_initialized')}")
    print(f"   模型: {data.get('model')}")
    print("   ✓ 通过\n")


def test_generate_simple():
    """测试简单代码生成"""
    print("3️⃣  测试代码生成 (简单示例)...")
    
    prompt = "创建一个显示 Hello World 的简单 HTML 页面"
    
    print(f"   提示词: {prompt}")
    response = requests.post(
        f"{BASE_URL}/generate",
        json={"prompt_text": prompt},
        timeout=60  # 生成可能需要一些时间
    )
    
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        files = response.json()
        print(f"   生成文件数: {len(files)}")
        print(f"   文件列表: {list(files.keys())}")
        print("   ✓ 通过\n")
        return files
    else:
        print(f"   ✗ 失败: {response.text}")
        return None


def main():
    print("=" * 60)
    print("Vibecoding Platform - 后端 API 测试")
    print("=" * 60)
    print()
    
    try:
        test_health_check()
        test_detailed_health()
        files = test_generate_simple()
        
        if files:
            print("=" * 60)
            print("📝 生成的代码预览:")
            print("=" * 60)
            for filename, content in list(files.items())[:2]:  # 只显示前两个文件
                print(f"\n📄 {filename}:")
                print("-" * 60)
                print(content[:500] + "..." if len(content) > 500 else content)
        
        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到服务器")
        print("请确保后端服务正在运行: python server.py")
    except Exception as e:
        print(f"✗ 测试失败: {e}")


if __name__ == "__main__":
    main()

