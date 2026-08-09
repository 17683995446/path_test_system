#!/usr/bin/env python3
"""
安全渗透测试 - 发现潜在的安全漏洞
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5174/api"

class SecurityPenetrationTest:
    def __init__(self):
        self.vulnerabilities = []
        self.findings = []

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    def test_xss_injection(self):
        """测试XSS注入"""
        self.log("\n" + "="*80)
        self.log("安全测试1：XSS注入测试")
        self.log("="*80)

        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg/onload=alert('XSS')>",
            "';alert('XSS');//"
        ]

        found_xss = []

        for payload in xss_payloads:
            try:
                # 尝试在项目名称中注入XSS
                payload_name = f"XSS Test {payload}"
                create_data = {
                    "name": payload_name,
                    "path": "/workspace/path_test_system",
                    "description": "XSS测试"
                }
                response = requests.post(f"{BASE_URL}/projects", json=create_data, timeout=10)

                if response.status_code == 201:
                    project_id = response.json().get("id")

                    # 获取项目列表，检查是否直接返回了恶意脚本
                    list_response = requests.get(f"{BASE_URL}/projects", timeout=10)
                    if list_response.status_code == 200:
                        projects = list_response.json()
                        for p in projects:
                            if payload in str(p.get("name", "")):
                                found_xss.append({
                                    "type": "XSS",
                                    "payload": payload,
                                    "location": "项目名称",
                                    "severity": "MEDIUM"
                                })
                                self.log(f"⚠ 发现XSS风险：{payload[:30]}...", "WARN")
                                break

                    # 清理
                    requests.delete(f"{BASE_URL}/projects/{project_id}", timeout=5)

            except Exception as e:
                self.log(f"✗ 测试异常：{e}", "ERROR")

        if not found_xss:
            self.log("✓ 未发现XSS漏洞（数据被适当转义或验证）", "PASS")
        else:
            self.log(f"✗ 发现 {len(found_xss)} 个XSS风险", "FAIL")

        return found_xss

    def test_path_traversal(self):
        """测试路径遍历"""
        self.log("\n" + "="*80)
        self.log("安全测试2：路径遍历测试")
        self.log("="*80)

        traversal_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "..%252f..%252f..%252fetc%252fpasswd",
            "/var/www/../../../etc/passwd"
        ]

        found_traversal = []

        for path in traversal_paths:
            try:
                # 尝试使用路径遍历读取文件
                payload = {"path": f"/workspace/{path}"}
                response = requests.post(f"{BASE_URL}/files/read", json=payload, timeout=10)

                # 检查是否返回了敏感文件内容
                if response.status_code == 200:
                    data = response.json()
                    content = data.get("content", "")
                    if "root:" in content or "[" in content:
                        found_traversal.append({
                            "type": "Path Traversal",
                            "payload": path,
                            "severity": "CRITICAL"
                        })
                        self.log(f"✗ 发现路径遍历漏洞！", "CRITICAL")
                    else:
                        self.log(f"✓ 路径遍历被阻止：{path[:30]}", "PASS")
                elif response.status_code == 403:
                    self.log(f"✓ 路径遍历被安全策略阻止：{path[:30]}", "PASS")
                else:
                    self.log(f"✓ 路径遍历失败：{path[:30]}", "PASS")

            except Exception as e:
                self.log(f"✗ 测试异常：{e}", "ERROR")

        if not found_traversal:
            self.log("✓ 未发现路径遍历漏洞", "PASS")
        else:
            self.log(f"✗ 发现 {len(found_traversal)} 个路径遍历风险", "FAIL")

        return found_traversal

    def test_sql_injection_patterns(self):
        """测试SQL注入模式（虽然当前使用JSON存储，但测试概念）"""
        self.log("\n" + "="*80)
        self.log("安全测试3：SQL注入模式测试")
        self.log("="*80)

        sql_patterns = [
            "' OR '1'='1",
            "' OR '1'='1' --",
            "' OR '1'='1' /*",
            "admin'--",
            "' UNION SELECT NULL--",
            "1' AND '1'='1"
        ]

        found_injection = []

        for pattern in sql_patterns:
            try:
                # 在项目名称中尝试SQL注入模式
                payload_name = f"SQL Test {pattern}"
                create_data = {
                    "name": payload_name,
                    "path": "/workspace/path_test_system",
                    "description": "SQL注入测试"
                }
                response = requests.post(f"{BASE_URL}/projects", json=create_data, timeout=10)

                if response.status_code == 201:
                    project_id = response.json().get("id")

                    # 验证数据是否被正确存储（不被解释为SQL）
                    list_response = requests.get(f"{BASE_URL}/projects", timeout=10)
                    if list_response.status_code == 200:
                        projects = list_response.json()
                        # 检查数据是否被原样存储
                        for p in projects:
                            if pattern in str(p.get("name", "")):
                                # 数据被原样存储是OK的，因为我们使用JSON存储
                                # 但如果是在SQL系统中，这就是注入点
                                found_injection.append({
                                    "type": "SQL Injection Pattern",
                                    "payload": pattern,
                                    "note": "数据被存储但未被解释为SQL",
                                    "severity": "LOW"
                                })
                                self.log(f"⚠ 发现SQL注入模式被存储：{pattern[:20]}...", "WARN")
                                break

                    # 清理
                    requests.delete(f"{BASE_URL}/projects/{project_id}", timeout=5)
                else:
                    self.log(f"✓ SQL注入模式被阻止：{pattern[:20]}", "PASS")

            except Exception as e:
                self.log(f"✗ 测试异常：{e}", "ERROR")

        if not found_injection:
            self.log("✓ 未发现SQL注入漏洞（使用JSON存储，无SQL风险）", "PASS")
        else:
            self.log(f"ℹ 发现 {len(found_injection)} 个SQL注入模式（低风险）", "INFO")

        return found_injection

    def test_rate_limiting(self):
        """测试速率限制"""
        self.log("\n" + "="*80)
        self.log("安全测试4：速率限制测试")
        self.log("="*80)

        # 快速发送100个请求
        self.log("发送100个快速连续请求...")

        success_count = 0
        fail_count = 0
        rate_limited = False

        for i in range(100):
            try:
                response = requests.get(f"{BASE_URL}/projects", timeout=2)
                if response.status_code == 200:
                    success_count += 1
                elif response.status_code == 429:
                    rate_limited = True
                    fail_count += 1
                else:
                    fail_count += 1

                if i % 20 == 0 and i > 0:
                    self.log(f"  进度: {i}/100")

            except Exception as e:
                fail_count += 1

        self.log(f"\n速率限制测试结果:")
        self.log(f"  成功请求: {success_count}/100")
        self.log(f"  失败请求: {fail_count}/100")

        if rate_limited:
            self.log("✓ 检测到速率限制机制", "PASS")
            return [{"type": "Rate Limiting", "status": "Active", "severity": "GOOD"}]
        else:
            if success_count == 100:
                self.log("ℹ 未检测到速率限制（可能不需要或使用其他机制）", "INFO")
            else:
                self.log("⚠ 存在失败但未触发速率限制", "WARN")
            return [{"type": "Rate Limiting", "status": "Not Detected", "severity": "INFO"}]

    def test_authentication_bypass(self):
        """测试认证绕过"""
        self.log("\n" + "="*80)
        self.log("安全测试5：认证测试")
        self.log("="*80)

        # 测试未授权访问受保护资源
        test_cases = []

        # 测试1: 不带认证信息访问需要认证的资源
        self.log("测试未授权访问...")
        try:
            response = requests.get(f"{BASE_URL}/projects", timeout=10)
            if response.status_code == 200:
                self.log("✓ 公开端点无需认证（符合预期）", "PASS")
                test_cases.append({"test": "公开端点", "passed": True})
            else:
                self.log(f"⚠ 公开端点返回：{response.status_code}", "WARN")
                test_cases.append({"test": "公开端点", "passed": False})
        except Exception as e:
            self.log(f"✗ 测试异常：{e}", "ERROR")

        # 测试2: 检查是否有敏感端点暴露
        sensitive_endpoints = [
            "/api/admin",
            "/api/config",
            "/api/debug",
            "/api/internal"
        ]

        self.log("检查敏感端点暴露...")
        for endpoint in sensitive_endpoints:
            try:
                response = requests.get(f"http://localhost:5174{endpoint}", timeout=5)
                if response.status_code == 404:
                    self.log(f"✓ 敏感端点不存在：{endpoint}", "PASS")
                    test_cases.append({"test": f"端点{endpoint}", "passed": True})
                elif response.status_code in [401, 403]:
                    self.log(f"✓ 敏感端点需要认证：{endpoint}", "PASS")
                    test_cases.append({"test": f"端点{endpoint}", "passed": True})
                else:
                    self.log(f"⚠ 发现敏感端点：{endpoint} (状态：{response.status_code})", "WARN")
                    test_cases.append({"test": f"端点{endpoint}", "passed": False})
            except Exception:
                self.log(f"✓ 端点不可访问：{endpoint}", "PASS")

        passed = sum(1 for t in test_cases if t["passed"])
        self.log(f"\n认证测试完成: {passed}/{len(test_cases)} 通过")

        return test_cases

    def test_data_persistence(self):
        """测试数据持久化安全性"""
        self.log("\n" + "="*80)
        self.log("安全测试6：数据持久化测试")
        self.log("="*80)

        # 创建包含敏感信息的数据
        sensitive_data = {
            "name": "敏感数据测试",
            "path": "/workspace/path_test_system",
            "description": "测试password=secret123, api_key=sk_test_xxx"
        }

        self.log("创建包含敏感信息的数据...")
        try:
            response = requests.post(f"{BASE_URL}/projects", json=sensitive_data, timeout=10)
            if response.status_code == 201:
                project_id = response.json().get("id")
                self.log("✓ 数据创建成功", "PASS")

                # 检查数据文件是否包含明文敏感信息
                import os
                projects_file = "/workspace/path_test_system/data/projects.json"

                if os.path.exists(projects_file):
                    with open(projects_file, 'r') as f:
                        content = f.read()

                    # 检查是否包含测试敏感词
                    sensitive_keywords = ["password", "api_key", "secret", "token"]
                    found_sensitive = []

                    for keyword in sensitive_keywords:
                        if keyword in content.lower():
                            # 检查是否是测试数据中的
                            if keyword in sensitive_data["description"].lower():
                                found_sensitive.append(keyword)

                    if found_sensitive:
                        self.log(f"ℹ 存储中包含敏感关键词（测试数据）: {', '.join(found_sensitive)}", "INFO")
                        self.log("  建议：真实环境中避免存储明文敏感信息", "INFO")
                    else:
                        self.log("✓ 未发现明文敏感信息泄露", "PASS")

                # 清理
                requests.delete(f"{BASE_URL}/projects/{project_id}", timeout=5)

            else:
                self.log(f"✗ 数据创建失败：{response.status_code}", "FAIL")

        except Exception as e:
            self.log(f"✗ 测试异常：{e}", "ERROR")

    def run_all_tests(self):
        """运行所有安全测试"""
        self.log("="*80)
        self.log("50层代码分析系统 - 安全渗透测试")
        self.log("="*80)

        all_results = []

        # 测试1: XSS
        xss_results = self.test_xss_injection()
        all_results.extend(xss_results)
        time.sleep(1)

        # 测试2: 路径遍历
        traversal_results = self.test_path_traversal()
        all_results.extend(traversal_results)
        time.sleep(1)

        # 测试3: SQL注入
        sql_results = self.test_sql_injection_patterns()
        all_results.extend(sql_results)
        time.sleep(1)

        # 测试4: 速率限制
        rate_results = self.test_rate_limiting()
        all_results.extend(rate_results)
        time.sleep(1)

        # 测试5: 认证
        auth_results = self.test_authentication_bypass()
        all_results.extend(auth_results)
        time.sleep(1)

        # 测试6: 数据持久化
        self.test_data_persistence()

        # 生成报告
        self.log("\n" + "="*80)
        self.log("安全测试最终报告")
        self.log("="*80)

        critical = sum(1 for r in all_results if isinstance(r, dict) and r.get("severity") == "CRITICAL")
        high = sum(1 for r in all_results if isinstance(r, dict) and r.get("severity") == "HIGH")
        medium = sum(1 for r in all_results if isinstance(r, dict) and r.get("severity") == "MEDIUM")
        low = sum(1 for r in all_results if isinstance(r, dict) and r.get("severity") == "LOW")

        self.log(f"\n风险评估:")
        self.log(f"  严重: {critical}")
        self.log(f"  高危: {high}")
        self.log(f"  中危: {medium}")
        self.log(f"  低危: {low}")

        if critical > 0:
            self.log("\n⚠ 发现严重安全漏洞，需要立即修复！", "CRITICAL")
        elif high > 0:
            self.log("\n⚠ 发现高危安全问题，建议尽快修复", "WARN")
        elif medium > 0:
            self.log("\nℹ 发现中危安全问题，建议关注", "INFO")
        else:
            self.log("\n✓ 安全测试通过，未发现严重漏洞", "PASS")

        self.log("\n" + "="*80)
        self.log("安全测试完成！")
        self.log("="*80)

if __name__ == "__main__":
    tester = SecurityPenetrationTest()
    tester.run_all_tests()
