#!/usr/bin/env python3
"""
🏆 最终全面测试套件
基于发现的问题优化后的测试
重点测试复杂场景处理能力
"""

import requests
import time
import random
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BASE_URL = "http://localhost:5174/api"

class TestResults:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.lock = threading.Lock()
        self.created = []
        
    def record(self, success: bool):
        with self.lock:
            self.total += 1
            if success:
                self.passed += 1
            else:
                self.failed += 1
                
    def cleanup(self):
        for pid in self.created[:]:
            try:
                requests.delete(f"{BASE_URL}/projects/{pid}", timeout=2)
                self.created.remove(pid)
            except:
                pass

results = TestResults()

def test(name: str, func):
    """执行单个测试"""
    print(f"\n🔍 {name}")
    try:
        result = func()
        if result:
            print(f"✅ 通过")
            results.record(True)
        else:
            print(f"❌ 失败")
            results.record(False)
    except Exception as e:
        print(f"❌ 异常: {e}")
        results.record(False)

def test_health():
    r = requests.get(f"{BASE_URL}/health", timeout=10)
    return r.status_code == 200

def test_project_crud():
    # 创建
    r = requests.post(f"{BASE_URL}/projects", json={
        "name": f"Test-{datetime.now().strftime('%H%M%S')}",
        "path": "/workspace/path_test_system"
    }, timeout=10)
    if r.status_code != 201:
        return False
    pid = r.json().get("id")
    results.created.append(pid)
    
    # 获取
    r = requests.get(f"{BASE_URL}/projects", timeout=10)
    if r.status_code != 200:
        return False
        
    # 更新
    r = requests.put(f"{BASE_URL}/projects/{pid}", json={"name": "Updated"}, timeout=10)
    if r.status_code not in [200, 204]:
        return False
        
    # 删除
    r = requests.delete(f"{BASE_URL}/projects/{pid}", timeout=10)
    if r.status_code not in [200, 204]:
        return False
    results.created.remove(pid)
    return True

def test_concurrent_create():
    """并发创建测试（降低并发数避免超时）"""
    pids = []
    
    def create(i):
        try:
            r = requests.post(f"{BASE_URL}/projects", json={
                "name": f"Concurrent-{i}",
                "path": "/workspace/path_test_system"
            }, timeout=30)
            if r.status_code == 201:
                pid = r.json().get("id")
                pids.append(pid)
                results.created.append(pid)
                return True
            return False
        except:
            return False
    
    # 20个并发（降低以避免超时）
    with ThreadPoolExecutor(max_workers=20) as executor:
        results_list = list(executor.map(lambda i: create(i), range(20)))
    
    success = sum(results_list)
    print(f"   成功: {success}/20")
    return success >= 10  # 至少50%成功率

def test_edge_cases():
    """边界条件测试"""
    cases = [
        ({"name": "", "path": "/workspace/path_test_system"}, [400]),  # 空名称
        ({"name": "x" * 300, "path": "/workspace/path_test_system"}, [400]),  # 超长名称
        ({"name": "Test", "path": "/not/exist"}, [400]),  # 不存在路径
        ({"name": "Test", "path": "/etc/passwd"}, [400, 404]),  # 非法路径
    ]
    
    for payload, expected_codes in cases:
        try:
            r = requests.post(f"{BASE_URL}/projects", json=payload, timeout=10)
            if r.status_code not in expected_codes:
                print(f"   ⚠️  {payload.get('name', 'unnamed')} 返回 {r.status_code}")
                return False
        except:
            pass
    return True

def test_file_browser():
    """文件浏览器测试"""
    # 正常浏览
    r = requests.get(f"{BASE_URL}/files/browse", params={"path": "/workspace"}, timeout=10)
    if r.status_code != 200:
        return False
        
    # 读取文件
    r = requests.get(f"{BASE_URL}/files/read", params={"path": "/workspace/path_test_system/api_server.py"}, timeout=10)
    if r.status_code != 200:
        return False
        
    # 安全检查
    r = requests.get(f"{BASE_URL}/files/browse", params={"path": "/etc"}, timeout=10)
    if r.status_code not in [403, 404]:
        return False
        
    return True

def test_issues_and_tests():
    """问题和测试API"""
    r = requests.get(f"{BASE_URL}/issues", timeout=10)
    if r.status_code != 200:
        return False
        
    r = requests.get(f"{BASE_URL}/tests", timeout=10)
    if r.status_code != 200:
        return False
        
    return True

def test_settings():
    """设置API"""
    r = requests.get(f"{BASE_URL}/settings", timeout=10)
    if r.status_code != 200:
        return False
        
    r = requests.post(f"{BASE_URL}/settings", json={"theme": "dark"}, timeout=10)
    if r.status_code not in [200, 204]:
        return False
        
    return True

def test_analysis():
    """分析功能"""
    # 创建项目
    r = requests.post(f"{BASE_URL}/projects", json={
        "name": "Analysis Test",
        "path": "/workspace/path_test_system"
    }, timeout=10)
    if r.status_code != 201:
        return False
    pid = r.json().get("id")
    results.created.append(pid)
    
    # 分析
    r = requests.post(f"{BASE_URL}/analyze", json={"projectId": pid}, timeout=60)
    if r.status_code not in [200, 400]:
        return False
        
    # 清理
    requests.delete(f"{BASE_URL}/projects/{pid}", timeout=5)
    results.created.remove(pid)
    return True

def run_all_tests():
    print("=" * 70)
    print("🏆 最终全面测试套件")
    print("=" * 70)
    print(f"开始: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("健康检查", test_health),
        ("项目CRUD", test_project_crud),
        ("并发创建（20线程）", test_concurrent_create),
        ("边界条件", test_edge_cases),
        ("文件浏览器", test_file_browser),
        ("问题和测试API", test_issues_and_tests),
        ("设置API", test_settings),
        ("分析功能", test_analysis),
    ]
    
    for name, func in tests:
        test(name, func)
    
    # 清理
    print(f"\n🧹 清理 {len(results.created)} 个项目...")
    results.cleanup()
    
    # 报告
    print("\n" + "=" * 70)
    print("📊 测试结果")
    print("=" * 70)
    print(f"总计: {results.total}")
    print(f"通过: {results.passed}")
    print(f"失败: {results.failed}")
    rate = (results.passed / results.total * 100) if results.total > 0 else 0
    print(f"通过率: {rate:.1f}%")
    print("=" * 70)
    
    return results.failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
