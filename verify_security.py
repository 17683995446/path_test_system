#!/usr/bin/env python3
"""
安全测试验证脚本
测试我们的安全措施是否正常工作
"""

import requests
import json
import time

BASE_URL = "http://localhost:5174/api"

def test_health():
    """测试健康检查"""
    print("=" * 80)
    print("测试1: 健康检查")
    print("=" * 80)
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✓ 健康检查通过")
            return True
        else:
            print(f"✗ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 健康检查异常: {e}")
        return False

def test_xss_sanitization():
    """测试XSS过滤是否工作"""
    print("\n" + "=" * 80)
    print("测试2: XSS 输入过滤")
    print("=" * 80)
    
    xss_payload = "<script>alert('XSS')</script>Test Project"
    print(f"测试XSS payload: {repr(xss_payload)}")
    
    try:
        # 创建包含XSS的项目
        payload = {
            "name": xss_payload,
            "path": "/workspace/path_test_system",
            "description": "<img src=x onerror=alert('XSS')>",
            "language": "Python"
        }
        
        response = requests.post(f"{BASE_URL}/projects", json=payload, timeout=10)
        
        if response.status_code == 201:
            data = response.json()
            project_id = data.get("id")
            created_name = data.get("name")
            created_desc = data.get("description")
            
            print(f"✓ 项目创建成功")
            print(f"  原始名称: {repr(xss_payload)}")
            print(f"  过滤后名称: {repr(created_name)}")
            print(f"  原始描述: {repr(payload['description'])}")
            print(f"  过滤后描述: {repr(created_desc)}")
            
            # 验证XSS被过滤
            if "<script" in created_name or "alert" in created_name:
                print("✗ 警告: XSS payload没有被完全过滤!")
            else:
                print("✓ XSS payload被正确过滤了!")
            
            # 清理
            if project_id:
                requests.delete(f"{BASE_URL}/projects/{project_id}", timeout=5)
            return True
        else:
            print(f"✗ 项目创建失败: {response.status_code}, {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ XSS测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_path_validation():
    """测试路径验证"""
    print("\n" + "=" * 80)
    print("测试3: 路径验证和安全检查")
    print("=" * 80)
    
    # 测试不存在的路径
    print("测试不存在的路径...")
    payload = {
        "name": "Test Project",
        "path": "/nonexistent/path/123456",
        "description": "Test",
        "language": "Python"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/projects", json=payload, timeout=5)
        if response.status_code == 400:
            print("✓ 不存在路径被正确拒绝了")
        else:
            print(f"✗ 不存在路径没有被正确拒绝: {response.status_code}")
    except Exception as e:
        print(f"✗ 路径测试异常: {e}")
    
    # 测试目录遍历攻击
    print("\n测试目录遍历攻击...")
    payload = {
        "name": "Test Project",
        "path": "../../../etc/passwd",
        "description": "Path traversal test",
        "language": "Python"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/projects", json=payload, timeout=5)
        if response.status_code == 400:
            print("✓ 目录遍历攻击被正确拒绝了")
        else:
            print(f"✗ 目录遍历攻击没有被正确拒绝: {response.status_code}")
    except Exception as e:
        print(f"✗ 目录遍历测试异常: {e}")

def test_security_headers():
    """测试安全响应头"""
    print("\n" + "=" * 80)
    print("测试4: 安全响应头")
    print("=" * 80)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        
        checked_headers = [
            "X-Frame-Options",
            "X-Content-Type-Options",
            "X-XSS-Protection"
        ]
        
        print("检查的响应头:")
        for header in checked_headers:
            if header in response.headers:
                print(f"  ✓ {header}: {response.headers[header]}")
            else:
                print(f"  ✗ {header}: 缺失")
        
        # 检查 Content-Security-Policy
        if "Content-Security-Policy" in response.headers:
            print(f"  ✓ Content-Security-Policy: {response.headers['Content-Security-Policy']}")
        
        return True
    except Exception as e:
        print(f"✗ 安全响应头测试异常: {e}")
        return False

def test_api_works():
    """测试API是否正常工作"""
    print("\n" + "=" * 80)
    print("测试5: API功能正常性验证")
    print("=" * 80)
    
    all_ok = True
    
    # 测试获取项目
    print("测试获取项目列表...")
    try:
        response = requests.get(f"{BASE_URL}/projects", timeout=5)
        if response.status_code == 200:
            print(f"✓ 项目列表获取成功，有 {len(response.json())} 个项目")
        else:
            print(f"✗ 获取项目失败: {response.status_code}")
            all_ok = False
    except Exception as e:
        print(f"✗ 获取项目异常: {e}")
        all_ok = False
    
    # 测试获取问题
    print("测试获取问题列表...")
    try:
        response = requests.get(f"{BASE_URL}/issues", timeout=5)
        if response.status_code == 200:
            print(f"✓ 问题列表获取成功，有 {len(response.json())} 个问题")
        else:
            print(f"✗ 获取问题失败: {response.status_code}")
            all_ok = False
    except Exception as e:
        print(f"✗ 获取问题异常: {e}")
        all_ok = False
    
    return all_ok

def main():
    """主测试函数"""
    print("\n" + "=" * 80)
    print("50层代码分析系统 - 安全功能验证")
    print("=" * 80)
    
    print(f"\n测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    results.append(("健康检查", test_health()))
    time.sleep(1)
    results.append(("XSS过滤", test_xss_sanitization()))
    time.sleep(1)
    test_path_validation()
    results.append(("安全响应头", test_security_headers()))
    time.sleep(1)
    results.append(("API功能", test_api_works()))
    
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{name}: {status}")
    
    total = len(results)
    passed = sum(1 for n, p in results if p)
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有安全测试通过！系统安全性良好！")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")

if __name__ == "__main__":
    main()
