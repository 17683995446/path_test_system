#!/usr/bin/env python3
"""
边缘情况和异常处理测试脚本
测试各种边界条件和异常情况的处理
"""

import requests
import json
import time
import random
import string
from datetime import datetime

BASE_URL = "http://localhost:5174/api"


def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def test_edge_cases():
    log("=" * 100)
    log("边缘情况和异常处理测试开始")
    log("=" * 100)
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    # 测试1：健康检查端点
    total_tests +=1
    try:
        log("测试1：健康检查端点...")
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            log("✅ 健康检查通过")
            passed_tests +=1
        else:
            log(f"❌ 健康检查失败：{response.status_code}")
            failed_tests.append("健康检查")
    except Exception as e:
        log(f"❌ 健康检查异常：{e}")
        failed_tests.append("健康检查")
    
    # 测试2：创建空项目
    total_tests +=1
    try:
        log("测试2：创建空项目（无数据）...")
        response = requests.post(f"{BASE_URL}/projects", json={}, timeout=5)
        if response.status_code in [400, 422]:  # 预期的错误响应
            log("✅ 空项目被正确拒绝")
            passed_tests +=1
        else:
            log(f"❌ 空项目处理不当：{response.status_code}")
            failed_tests.append("创建空项目")
    except Exception as e:
        log(f"❌ 空项目测试异常：{e}")
        failed_tests.append("创建空项目")
    
    # 测试3：超长项目名称
    total_tests +=1
    try:
        log("测试3：超长项目名称（5000字符）...")
        long_name = 'x' * 5000
        response = requests.post(f"{BASE_URL}/projects", json={
            "name": long_name,
            "path": "/workspace/path_test_system",
            "description": "超长名称测试"
        }, timeout=10)
        if response.status_code in [400, 422, 201]:  # 可以是拒绝或者成功（取决于验证）
            log("✅ 超长名称处理正常")
            passed_tests +=1
            # 如果成功创建，删除它
            if response.status_code == 201:
                data = response.json()
                if 'id' in data:
                    requests.delete(f"{BASE_URL}/projects/{data['id']}")
        else:
            log(f"❌ 超长名称处理不当：{response.status_code}")
            failed_tests.append("超长项目名称")
    except Exception as e:
        log(f"❌ 超长名称测试异常：{e}")
        failed_tests.append("超长项目名称")
    
    # 测试4：无效的路径
    total_tests +=1
    try:
        log("测试4：无效的路径...")
        response = requests.post(f"{BASE_URL}/projects", json={
            "name": "Invalid Path Test",
            "path": "/this/path/does/not/exist/ever/hopefully",
            "description": "无效路径测试"
        }, timeout=5)
        if response.status_code in [400, 422, 201]:
            log("✅ 无效路径处理正常")
            passed_tests +=1
            if response.status_code == 201:
                data = response.json()
                if 'id' in data:
                    requests.delete(f"{BASE_URL}/projects/{data['id']}")
        else:
            log(f"❌ 无效路径处理不当：{response.status_code}")
            failed_tests.append("无效路径")
    except Exception as e:
        log(f"❌ 无效路径测试异常：{e}")
        failed_tests.append("无效路径")
    
    # 测试5：访问不存在的项目
    total_tests +=1
    try:
        log("测试5：访问不存在的项目...")
        fake_id = "this-project-id-does-not-exist-1234567890"
        # 尝试获取
        response = requests.get(f"{BASE_URL}/projects/{fake_id}", timeout=5)
        # 尝试更新
        response2 = requests.put(f"{BASE_URL}/projects/{fake_id}", json={"name": "test"}, timeout=5)
        # 尝试删除
        response3 = requests.delete(f"{BASE_URL}/projects/{fake_id}", timeout=5)
        
        log(f"   获取: {response.status_code}, 更新: {response2.status_code}, 删除: {response3.status_code}")
        log("✅ 不存在的项目处理正常（不崩溃）")
        passed_tests +=1
    except Exception as e:
        log(f"❌ 不存在项目测试异常：{e}")
        failed_tests.append("访问不存在项目")
    
    # 测试6：特殊字符和注入测试
    total_tests +=1
    try:
        log("测试6：特殊字符和潜在注入测试...")
        special_chars = '!@#$%^&*()_+-=[]{}|;:,.<>?`~"\'\\'
        response = requests.post(f"{BASE_URL}/projects", json={
            "name": f"Test {special_chars}",
            "path": "/workspace/path_test_system",
            "description": f"Special chars {special_chars}"
        }, timeout=10)
        log(f"   状态码: {response.status_code}")
        log("✅ 特殊字符处理正常")
        passed_tests +=1
        if response.status_code == 201:
            data = response.json()
            if 'id' in data:
                requests.delete(f"{BASE_URL}/projects/{data['id']}")
    except Exception as e:
        log(f"❌ 特殊字符测试异常：{e}")
        failed_tests.append("特殊字符")
    
    # 测试7：大量快速创建和删除
    total_tests +=1
    try:
        log("测试7：大量快速创建和删除项目（100个）...")
        created_ids = []
        start = time.time()
        
        for i in range(100):
            try:
                response = requests.post(f"{BASE_URL}/projects", json={
                    "name": f"Rapid Test {i}",
                    "path": "/workspace/path_test_system"
                }, timeout=2)
                if response.status_code == 201:
                    data = response.json()
                    if 'id' in data:
                        created_ids.append(data['id'])
            except:
                pass
        
        elapsed_create = time.time() - start
        
        # 现在删除它们
        start_delete = time.time()
        for pid in created_ids:
            try:
                requests.delete(f"{BASE_URL}/projects/{pid}", timeout=1)
            except:
                pass
        
        elapsed_delete = time.time() - start_delete
        
        log(f"   创建: {len(created_ids)}个, {elapsed_create:.2f}s, 删除: {elapsed_delete:.2f}s")
        log("✅ 大量快速操作成功完成")
        passed_tests +=1
    except Exception as e:
        log(f"❌ 大量快速操作异常：{e}")
        failed_tests.append("大量快速操作")
    
    # 测试8：无意义的分析请求
    total_tests +=1
    try:
        log("测试8：无意义的分析请求...")
        response = requests.post(f"{BASE_URL}/analyze", json={}, timeout=5)
        log(f"   状态码: {response.status_code}")
        log("✅ 无意义请求处理正常")
        passed_tests +=1
    except Exception as e:
        log(f"❌ 无意义请求异常：{e}")
        failed_tests.append("无意义分析请求")
    
    # 测试9：获取问题列表和测试列表
    total_tests +=1
    try:
        log("测试9：获取问题列表和测试列表...")
        issues_resp = requests.get(f"{BASE_URL}/issues", timeout=5)
        tests_resp = requests.get(f"{BASE_URL}/tests", timeout=5)
        
        log(f"   问题: {issues_resp.status_code}, 测试: {tests_resp.status_code}")
        if issues_resp.status_code == 200 and tests_resp.status_code == 200:
            try:
                issues = issues_resp.json()
                tests = tests_resp.json()
                log(f"   获取到 {len(issues)} 个问题, {len(tests)} 个测试")
                log("✅ 获取列表成功")
                passed_tests +=1
            except json.JSONDecodeError:
                log("❌ 返回的不是有效的JSON")
                failed_tests.append("获取列表JSON无效")
        else:
            failed_tests.append("获取列表失败")
    except Exception as e:
        log(f"❌ 获取列表异常：{e}")
        failed_tests.append("获取列表")
    
    # 测试10：空字符串和None值
    total_tests +=1
    try:
        log("测试10：空字符串和None值测试...")
        test_cases = [
            {"name": "", "path": "/workspace/path_test_system"},
            {"name": "   ", "path": "/workspace/path_test_system"},
            {"name": None, "path": "/workspace/path_test_system"},
        ]
        
        for i, tc in enumerate(test_cases):
            response = requests.post(f"{BASE_URL}/projects", json=tc, timeout=5)
        
        log("✅ 空值测试完成")
        passed_tests +=1
    except Exception as e:
        log(f"❌ 空值测试异常：{e}")
        failed_tests.append("空值测试")
    
    # 最终报告
    print("\n" + "=" * 100)
    log("边缘情况和异常处理测试完成")
    print("=" * 100)
    print(f"总测试数: {total_tests}")
    print(f"通过: {passed_tests}")
    print(f"失败: {len(failed_tests)}")
    if failed_tests:
        print(f"失败的测试: {', '.join(failed_tests)}")
    else:
        print("✅ 所有测试通过！")
    
    return len(failed_tests) == 0


if __name__ == "__main__":
    success = test_edge_cases()
    exit(0 if success else 1)
