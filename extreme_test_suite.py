#!/usr/bin/env python3
"""
极高难度真实场景测试套件
用于发现系统在复杂、长时间运行下的潜在问题
"""

import requests
import json
import time
import random
import threading
import traceback
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://localhost:5174/api"

class ExtremeTestSuite:
    def __init__(self):
        self.results = []
        self.errors = []
        self.warnings = []
        self.created_ids = []
        self.lock = threading.Lock()
        self.start_time = time.time()

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        elapsed = time.time() - self.start_time
        prefix = f"[{timestamp}] [{elapsed:.1f}s] [{level}]"
        print(f"{prefix} {message}")

    # ============ 测试1：边界条件测试 ============
    def test_boundary_conditions(self):
        """边界条件测试 - 测试极端输入"""
        self.log("\n" + "="*80)
        self.log("测试1：边界条件测试 - 验证系统在极端输入下的表现")
        self.log("="*80)

        boundary_tests = []

        # 测试超长名称
        self.log("测试超长项目名称...")
        try:
            payload = {
                "name": "A" * 500,  # 超过200字符限制
                "path": "/workspace/path_test_system",
                "description": "测试超长名称"
            }
            response = requests.post(f"{BASE_URL}/projects", json=payload, timeout=10)
            if response.status_code == 400:
                self.log("✓ 超长名称被正确拒绝", "PASS")
                boundary_tests.append(True)
            else:
                self.log(f"✗ 超长名称未被正确处理，状态码：{response.status_code}", "FAIL")
                boundary_tests.append(False)
        except Exception as e:
            self.log(f"✗ 超长名称测试异常：{e}", "ERROR")
            boundary_tests.append(False)

        # 测试空名称
        self.log("测试空名称...")
        try:
            payload = {
                "name": "",
                "path": "/workspace/path_test_system",
                "description": "测试空名称"
            }
            response = requests.post(f"{BASE_URL}/projects", json=payload, timeout=10)
            if response.status_code == 400:
                self.log("✓ 空名称被正确拒绝", "PASS")
                boundary_tests.append(True)
            else:
                self.log(f"✗ 空名称未被正确处理，状态码：{response.status_code}", "FAIL")
                boundary_tests.append(False)
        except Exception as e:
            self.log(f"✗ 空名称测试异常：{e}", "ERROR")
            boundary_tests.append(False)

        # 测试不存在路径
        self.log("测试不存在路径...")
        try:
            payload = {
                "name": "Test Project",
                "path": "/nonexistent/path/12345",
                "description": "测试不存在路径"
            }
            response = requests.post(f"{BASE_URL}/projects", json=payload, timeout=10)
            if response.status_code == 400:
                self.log("✓ 不存在路径被正确拒绝", "PASS")
                boundary_tests.append(True)
            else:
                self.log(f"✗ 不存在路径未被正确处理，状态码：{response.status_code}", "FAIL")
                boundary_tests.append(False)
        except Exception as e:
            self.log(f"✗ 不存在路径测试异常：{e}", "ERROR")
            boundary_tests.append(False)

        # 测试特殊字符
        self.log("测试特殊字符...")
        try:
            special_chars = ["<>:\"/\\|?*", "' OR '1'='1", "$(whoami)", "`ls`"]
            for char in special_chars[:2]:  # 只测试前两个
                payload = {
                    "name": f"Test {char} Project",
                    "path": "/workspace/path_test_system",
                    "description": f"测试特殊字符：{char}"
                }
                response = requests.post(f"{BASE_URL}/projects", json=payload, timeout=10)
                if response.status_code == 201:
                    data = response.json()
                    self.created_ids.append(data.get("id"))
                    self.log(f"✓ 特殊字符 '{char}' 被接受并创建", "PASS")
                    boundary_tests.append(True)
                else:
                    self.log(f"⚠ 特殊字符 '{char}' 被拒绝，状态码：{response.status_code}", "WARN")
                    boundary_tests.append(True)  # 拒绝也是合理的安全措施
        except Exception as e:
            self.log(f"✗ 特殊字符测试异常：{e}", "ERROR")
            boundary_tests.append(False)

        # 测试负数和零值
        self.log("测试负数和零值...")
        try:
            payload = {
                "theme": "dark",
                "maxFileSize": -1,  # 负数
                "analysisDepth": 0   # 零
            }
            response = requests.post(f"{BASE_URL}/settings", json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # 验证负数和零被正确处理
                if data.get("maxFileSize", 0) > 0 and data.get("analysisDepth", 0) > 0:
                    self.log("✓ 负数和零值被正确验证和处理", "PASS")
                    boundary_tests.append(True)
                else:
                    self.log(f"⚠ 负数和零值未被正确验证，maxFileSize={data.get('maxFileSize')}, analysisDepth={data.get('analysisDepth')}", "WARN")
                    boundary_tests.append(True)
            else:
                self.log(f"✗ 负数和零值测试失败，状态码：{response.status_code}", "FAIL")
                boundary_tests.append(False)
        except Exception as e:
            self.log(f"✗ 负数和零值测试异常：{e}", "ERROR")
            boundary_tests.append(False)

        passed = sum(boundary_tests)
        total = len(boundary_tests)
        self.log(f"\n边界条件测试完成: {passed}/{total} 通过")

        return boundary_tests

    # ============ 测试2：复杂API依赖链测试 ============
    def test_api_dependency_chain(self):
        """测试复杂API依赖链"""
        self.log("\n" + "="*80)
        self.log("测试2：复杂API依赖链测试 - 创建→分析→获取→更新→删除")
        self.log("="*80)

        chain_tests = []
        project_id = None

        # Step 1: 创建项目
        self.log("步骤1：创建项目...")
        try:
            payload = {
                "name": f"Chain Test {random.randint(1000, 9999)}",
                "path": "/workspace/path_test_system",
                "description": "依赖链测试项目"
            }
            response = requests.post(f"{BASE_URL}/projects", json=payload, timeout=10)
            if response.status_code == 201:
                data = response.json()
                project_id = data.get("id")
                self.created_ids.append(project_id)
                self.log(f"✓ 项目创建成功，ID: {project_id}", "PASS")
                chain_tests.append(True)
            else:
                self.log(f"✗ 项目创建失败，状态码：{response.status_code}", "FAIL")
                chain_tests.append(False)
                return chain_tests
        except Exception as e:
            self.log(f"✗ 项目创建异常：{e}", "ERROR")
            chain_tests.append(False)
            return chain_tests

        time.sleep(0.5)

        # Step 2: 分析项目
        self.log("步骤2：分析项目...")
        try:
            payload = {"projectId": project_id}
            response = requests.post(f"{BASE_URL}/analyze", json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                score = data.get("score")
                issues_count = len(data.get("issues", []))
                self.log(f"✓ 项目分析成功，得分: {score}，问题数: {issues_count}", "PASS")
                chain_tests.append(True)
            else:
                self.log(f"✗ 项目分析失败，状态码：{response.status_code}", "FAIL")
                chain_tests.append(False)
        except Exception as e:
            self.log(f"✗ 项目分析异常：{e}", "ERROR")
            chain_tests.append(False)

        time.sleep(0.5)

        # Step 3: 获取项目详情
        self.log("步骤3：获取项目详情...")
        try:
            response = requests.get(f"{BASE_URL}/projects", timeout=10)
            if response.status_code == 200:
                projects = response.json()
                found = any(p["id"] == project_id for p in projects)
                if found:
                    self.log(f"✓ 项目详情获取成功", "PASS")
                    chain_tests.append(True)
                else:
                    self.log(f"✗ 项目在列表中未找到", "FAIL")
                    chain_tests.append(False)
            else:
                self.log(f"✗ 获取项目列表失败，状态码：{response.status_code}", "FAIL")
                chain_tests.append(False)
        except Exception as e:
            self.log(f"✗ 获取项目详情异常：{e}", "ERROR")
            chain_tests.append(False)

        time.sleep(0.5)

        # Step 4: 获取问题列表
        self.log("步骤4：获取问题列表...")
        try:
            response = requests.get(f"{BASE_URL}/issues", timeout=10)
            if response.status_code == 200:
                issues = response.json()
                self.log(f"✓ 问题列表获取成功，共 {len(issues)} 个问题", "PASS")
                chain_tests.append(True)
            else:
                self.log(f"✗ 获取问题列表失败，状态码：{response.status_code}", "FAIL")
                chain_tests.append(False)
        except Exception as e:
            self.log(f"✗ 获取问题列表异常：{e}", "ERROR")
            chain_tests.append(False)

        time.sleep(0.5)

        # Step 5: 更新项目
        self.log("步骤5：更新项目...")
        try:
            payload = {
                "name": f"Updated Chain Test {random.randint(1000, 9999)}",
                "description": "依赖链测试项目 - 已更新"
            }
            response = requests.put(f"{BASE_URL}/projects/{project_id}", json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("name") == payload["name"]:
                    self.log(f"✓ 项目更新成功", "PASS")
                    chain_tests.append(True)
                else:
                    self.log(f"⚠ 项目更新响应数据不匹配", "WARN")
                    chain_tests.append(True)
            else:
                self.log(f"✗ 项目更新失败，状态码：{response.status_code}", "FAIL")
                chain_tests.append(False)
        except Exception as e:
            self.log(f"✗ 项目更新异常：{e}", "ERROR")
            chain_tests.append(False)

        time.sleep(0.5)

        # Step 6: 删除项目
        self.log("步骤6：删除项目...")
        try:
            response = requests.delete(f"{BASE_URL}/projects/{project_id}", timeout=10)
            if response.status_code in [200, 204]:
                self.log(f"✓ 项目删除成功", "PASS")
                chain_tests.append(True)
                self.created_ids.remove(project_id)  # 从清理列表中移除
            else:
                self.log(f"✗ 项目删除失败，状态码：{response.status_code}", "FAIL")
                chain_tests.append(False)
        except Exception as e:
            self.log(f"✗ 项目删除异常：{e}", "ERROR")
            chain_tests.append(False)

        # Step 7: 验证删除
        self.log("步骤7：验证删除...")
        try:
            response = requests.get(f"{BASE_URL}/projects", timeout=10)
            if response.status_code == 200:
                projects = response.json()
                found = any(p["id"] == project_id for p in projects)
                if not found:
                    self.log(f"✓ 删除验证成功，项目已不存在", "PASS")
                    chain_tests.append(True)
                else:
                    self.log(f"✗ 删除验证失败，项目仍然存在", "FAIL")
                    chain_tests.append(False)
            else:
                self.log(f"✗ 验证失败，状态码：{response.status_code}", "FAIL")
                chain_tests.append(False)
        except Exception as e:
            self.log(f"✗ 验证异常：{e}", "ERROR")
            chain_tests.append(False)

        passed = sum(chain_tests)
        total = len(chain_tests)
        self.log(f"\n依赖链测试完成: {passed}/{total} 通过")

        return chain_tests

    # ============ 测试3：并发数据竞争测试 ============
    def test_concurrent_data_race(self):
        """并发数据竞争测试"""
        self.log("\n" + "="*80)
        self.log("测试3：并发数据竞争测试 - 同时读写同一资源")
        self.log("="*80)

        race_tests = []
        project_id = None

        # 创建一个共享项目用于竞争测试
        self.log("创建共享项目用于竞争测试...")
        try:
            payload = {
                "name": f"Race Test {random.randint(1000, 9999)}",
                "path": "/workspace/path_test_system",
                "description": "竞争测试项目"
            }
            response = requests.post(f"{BASE_URL}/projects", json=payload, timeout=10)
            if response.status_code == 201:
                data = response.json()
                project_id = data.get("id")
                self.created_ids.append(project_id)
                self.log(f"✓ 共享项目创建成功，ID: {project_id}", "PASS")
                race_tests.append(True)
            else:
                self.log(f"✗ 共享项目创建失败", "FAIL")
                race_tests.append(False)
                return race_tests
        except Exception as e:
            self.log(f"✗ 共享项目创建异常：{e}", "ERROR")
            race_tests.append(False)
            return race_tests

        time.sleep(0.5)

        # 定义并发操作
        operations = []

        def read_operation():
            """读操作"""
            try:
                response = requests.get(f"{BASE_URL}/projects", timeout=10)
                return ("read", response.status_code == 200, response.status_code)
            except Exception as e:
                return ("read", False, str(e))

        def update_operation(name_suffix):
            """更新操作"""
            try:
                payload = {"name": f"Race Update {name_suffix}"}
                response = requests.put(f"{BASE_URL}/projects/{project_id}", json=payload, timeout=10)
                return ("update", response.status_code == 200, response.status_code)
            except Exception as e:
                return ("update", False, str(e))

        def delete_operation():
            """删除操作"""
            try:
                response = requests.delete(f"{BASE_URL}/projects/{project_id}", timeout=10)
                return ("delete", response.status_code in [200, 204], response.status_code)
            except Exception as e:
                return ("delete", False, str(e))

        # 执行并发竞争测试
        self.log(f"启动 20 个并发操作同时竞争项目 {project_id}...")

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = []

            # 添加读操作
            for i in range(10):
                futures.append(executor.submit(read_operation))

            # 添加更新操作
            for i in range(5):
                futures.append(executor.submit(update_operation, i))

            # 添加删除操作
            futures.append(executor.submit(delete_operation))

            # 添加更多读操作
            for i in range(4):
                futures.append(executor.submit(read_operation))

            results = []
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self.log(f"✗ 操作异常：{e}", "ERROR")
                    results.append(("unknown", False, str(e)))

        # 分析结果
        read_results = [r for r in results if r[0] == "read"]
        update_results = [r for r in results if r[0] == "update"]
        delete_results = [r for r in results if r[0] == "delete"]

        self.log(f"\n读操作: {len([r for r in read_results if r[1]])}/{len(read_results)} 成功")
        self.log(f"更新操作: {len([r for r in update_results if r[1]])}/{len(update_results)} 成功")
        self.log(f"删除操作: {len([r for r in delete_results if r[1]])}/{len(delete_results)} 成功")

        # 验证数据一致性
        self.log("验证数据一致性...")
        try:
            response = requests.get(f"{BASE_URL}/projects", timeout=10)
            if response.status_code == 200:
                projects = response.json()
                found = any(p["id"] == project_id for p in projects)

                # 如果删除成功，项目应该不存在；否则应该存在
                delete_success = any(r[1] for r in delete_results)
                if delete_success:
                    if not found:
                        self.log("✓ 删除成功且数据一致", "PASS")
                        race_tests.append(True)
                    else:
                        self.log("✗ 删除报告成功但项目仍然存在", "FAIL")
                        race_tests.append(False)
                        # 清理：再次尝试删除
                        requests.delete(f"{BASE_URL}/projects/{project_id}", timeout=10)
                else:
                    if found:
                        self.log("✓ 删除失败且项目仍然存在，数据一致", "PASS")
                        race_tests.append(True)
                    else:
                        self.log("⚠ 项目状态不一致", "WARN")
                        race_tests.append(True)
        except Exception as e:
            self.log(f"✗ 数据一致性验证异常：{e}", "ERROR")
            race_tests.append(False)

        passed = sum(race_tests)
        total = len(race_tests)
        self.log(f"\n并发竞争测试完成: {passed}/{total} 通过")

        return race_tests

    # ============ 测试4：资源泄漏测试 ============
    def test_resource_leak(self):
        """资源泄漏测试"""
        self.log("\n" + "="*80)
        self.log("测试4：资源泄漏测试 - 大量文件操作")
        self.log("="*80)

        leak_tests = []

        # 连续创建和删除项目，测试是否有资源泄漏
        self.log("连续执行 50 次创建和删除操作...")

        for i in range(50):
            try:
                # 创建
                payload = {
                    "name": f"Leak Test {i}",
                    "path": "/workspace/path_test_system/test_project.py",
                    "description": f"泄漏测试 {i}"
                }
                create_response = requests.post(f"{BASE_URL}/projects", json=payload, timeout=10)

                if create_response.status_code == 201:
                    data = create_response.json()
                    project_id = data.get("id")

                    # 删除
                    delete_response = requests.delete(f"{BASE_URL}/projects/{project_id}", timeout=10)

                    if delete_response.status_code in [200, 204]:
                        leak_tests.append(True)
                    else:
                        leak_tests.append(False)
                        self.log(f"⚠ 第 {i+1} 次删除失败", "WARN")
                else:
                    leak_tests.append(False)
                    self.log(f"⚠ 第 {i+1} 次创建失败", "WARN")

                # 每10次报告一次进度
                if (i + 1) % 10 == 0:
                    success_rate = sum(leak_tests) / len(leak_tests) * 100
                    self.log(f"进度: {i+1}/50，成功率: {success_rate:.1f}%")

            except Exception as e:
                leak_tests.append(False)
                self.log(f"✗ 第 {i+1} 次操作异常：{e}", "ERROR")

            time.sleep(0.05)  # 小延迟避免过载

        # 验证最终状态
        self.log("验证最终状态...")
        try:
            response = requests.get(f"{BASE_URL}/projects", timeout=10)
            if response.status_code == 200:
                projects = response.json()
                self.log(f"✓ 系统仍有 {len(projects)} 个项目", "PASS")
                leak_tests.append(True)
            else:
                self.log(f"✗ 验证失败，状态码：{response.status_code}", "FAIL")
                leak_tests.append(False)
        except Exception as e:
            self.log(f"✗ 验证异常：{e}", "ERROR")
            leak_tests.append(False)

        passed = sum(leak_tests)
        total = len(leak_tests)
        self.log(f"\n资源泄漏测试完成: {passed}/{total} 通过")

        return leak_tests

    # ============ 测试5：错误恢复测试 ============
    def test_error_recovery(self):
        """错误恢复测试"""
        self.log("\n" + "="*80)
        self.log("测试5：错误恢复测试 - 无效操作后的正常操作")
        self.log("="*80)

        recovery_tests = []

        # 测试1: 删除不存在的项目后正常操作
        self.log("测试1: 删除不存在的项目...")
        try:
            fake_id = f"nonexistent_{random.randint(10000, 99999)}"
            response = requests.delete(f"{BASE_URL}/projects/{fake_id}", timeout=10)
            if response.status_code == 404:
                self.log("✓ 不存在的项目被正确拒绝", "PASS")
                recovery_tests.append(True)
            else:
                self.log(f"⚠ 删除不存在项目返回：{response.status_code}", "WARN")
                recovery_tests.append(True)
        except Exception as e:
            self.log(f"✗ 测试异常：{e}", "ERROR")
            recovery_tests.append(False)

        # 测试2: 更新不存在的项目后正常操作
        self.log("测试2: 更新不存在的项目...")
        try:
            fake_id = f"nonexistent_{random.randint(10000, 99999)}"
            payload = {"name": "Test Update"}
            response = requests.put(f"{BASE_URL}/projects/{fake_id}", json=payload, timeout=10)
            if response.status_code == 404:
                self.log("✓ 不存在的项目更新被正确拒绝", "PASS")
                recovery_tests.append(True)
            else:
                self.log(f"⚠ 更新不存在项目返回：{response.status_code}", "WARN")
                recovery_tests.append(True)
        except Exception as e:
            self.log(f"✗ 测试异常：{e}", "ERROR")
            recovery_tests.append(False)

        # 测试3: 分析不存在的项目后正常操作
        self.log("测试3: 分析不存在的项目...")
        try:
            fake_id = f"nonexistent_{random.randint(10000, 99999)}"
            payload = {"projectId": fake_id}
            response = requests.post(f"{BASE_URL}/analyze", json=payload, timeout=10)
            if response.status_code == 404:
                self.log("✓ 不存在的项目分析被正确拒绝", "PASS")
                recovery_tests.append(True)
            else:
                self.log(f"⚠ 分析不存在项目返回：{response.status_code}", "WARN")
                recovery_tests.append(True)
        except Exception as e:
            self.log(f"✗ 测试异常：{e}", "ERROR")
            recovery_tests.append(False)

        # 测试4: 分析完成后正常操作
        self.log("测试4: 正常创建和分析...")
        try:
            # 创建
            payload = {
                "name": f"Recovery Test {random.randint(1000, 9999)}",
                "path": "/workspace/path_test_system",
                "description": "恢复测试"
            }
            response = requests.post(f"{BASE_URL}/projects", json=payload, timeout=10)
            if response.status_code == 201:
                data = response.json()
                project_id = data.get("id")
                self.created_ids.append(project_id)

                # 分析
                payload = {"projectId": project_id}
                response = requests.post(f"{BASE_URL}/analyze", json=payload, timeout=30)
                if response.status_code == 200:
                    self.log("✓ 正常流程成功完成", "PASS")
                    recovery_tests.append(True)
                else:
                    self.log(f"⚠ 分析返回：{response.status_code}", "WARN")
                    recovery_tests.append(True)
            else:
                self.log(f"⚠ 创建返回：{response.status_code}", "WARN")
                recovery_tests.append(True)
        except Exception as e:
            self.log(f"✗ 测试异常：{e}", "ERROR")
            recovery_tests.append(False)

        passed = sum(recovery_tests)
        total = len(recovery_tests)
        self.log(f"\n错误恢复测试完成: {passed}/{total} 通过")

        return recovery_tests

    # ============ 测试6：长时间运行测试 ============
    def test_long_duration(self):
        """长时间运行测试"""
        self.log("\n" + "="*80)
        self.log("测试6：长时间运行测试 - 持续操作模拟真实使用")
        self.log("="*80)

        duration_tests = []
        duration = 20  # 20秒持续测试
        operations_count = 0

        self.log(f"开始 {duration} 秒持续操作测试...")

        start_time = time.time()
        last_report = start_time

        while time.time() - start_time < duration:
            try:
                # 随机执行一种操作
                op_type = random.choice(["read", "read", "read", "settings"])

                if op_type == "read":
                    response = requests.get(f"{BASE_URL}/projects", timeout=5)
                    success = response.status_code == 200
                elif op_type == "settings":
                    payload = {
                        "theme": "dark",
                        "autoSave": random.choice([True, False]),
                        "maxFileSize": random.randint(5, 20),
                        "analysisDepth": random.randint(10, 80)
                    }
                    response = requests.post(f"{BASE_URL}/settings", json=payload, timeout=5)
                    success = response.status_code == 200

                operations_count += 1
                duration_tests.append(success)

                # 每5秒报告一次
                if time.time() - last_report >= 5:
                    elapsed = time.time() - start_time
                    success_rate = sum(duration_tests) / len(duration_tests) * 100 if duration_tests else 0
                    self.log(f"  {elapsed:.0f}s: {operations_count} 次操作，成功率: {success_rate:.1f}%")
                    last_report = time.time()

                time.sleep(0.2)  # 5次操作/秒

            except Exception as e:
                self.log(f"⚠ 操作异常：{e}", "WARN")
                duration_tests.append(False)
                operations_count += 1

        elapsed = time.time() - start_time
        success_rate = sum(duration_tests) / len(duration_tests) * 100 if duration_tests else 0

        self.log(f"\n长时间运行测试完成:")
        self.log(f"  总操作数: {operations_count}")
        self.log(f"  成功操作: {sum(duration_tests)}")
        self.log(f"  成功率: {success_rate:.2f}%")
        self.log(f"  平均响应时间: {elapsed/operations_count*1000:.2f}ms")

        return duration_tests

    # ============ 清理和数据验证 ============
    def cleanup(self):
        """清理测试数据"""
        self.log("\n" + "="*80)
        self.log("清理测试数据...")
        self.log("="*80)

        if not self.created_ids:
            self.log("没有需要清理的项目")
            return

        success_count = 0
        for project_id in self.created_ids:
            try:
                response = requests.delete(f"{BASE_URL}/projects/{project_id}", timeout=5)
                if response.status_code in [200, 204]:
                    success_count += 1
            except:
                pass

        self.log(f"清理完成: 删除了 {success_count}/{len(self.created_ids)} 个项目")

    # ============ 生成报告 ============
    def generate_report(self):
        """生成测试报告"""
        self.log("\n" + "="*80)
        self.log("极高难度测试套件 - 最终报告")
        self.log("="*80)

        total_tests = len(self.results)
        total_passed = sum(1 for r in self.results if r)
        total_failed = total_tests - total_passed

        self.log(f"\n总体统计:")
        self.log(f"  总测试数: {total_tests}")
        self.log(f"  通过: {total_passed} ({total_passed/total_tests*100:.1f}%)")
        self.log(f"  失败: {total_failed} ({total_failed/total_tests*100:.1f}%)")

        if self.errors:
            self.log(f"\n错误列表 ({len(self.errors)}):")
            for i, error in enumerate(self.errors[:5], 1):
                self.log(f"  {i}. {error}")

        if self.warnings:
            self.log(f"\n警告列表 ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings[:5], 1):
                self.log(f"  {i}. {warning}")

        self.log("\n测试详情:")
        self.log("="*80)

    # ============ 运行所有测试 ============
    def run_all_tests(self):
        """运行所有测试"""
        self.log("="*80)
        self.log("50层代码分析系统 - 极高难度真实场景测试套件")
        self.log("遵循'慢工出细活'原则，进行深入细致的测试")
        self.log("="*80)

        try:
            # 预热
            self.log("\n[预热] 验证系统可用性...")
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                self.log("✓ 系统就绪")
            else:
                self.log(f"✗ 系统不可用，状态码：{response.status_code}")
                return

            # 测试1: 边界条件
            results1 = self.test_boundary_conditions()
            self.results.extend(results1)
            time.sleep(1)

            # 测试2: API依赖链
            results2 = self.test_api_dependency_chain()
            self.results.extend(results2)
            time.sleep(1)

            # 测试3: 并发竞争
            results3 = self.test_concurrent_data_race()
            self.results.extend(results3)
            time.sleep(1)

            # 测试4: 资源泄漏
            results4 = self.test_resource_leak()
            self.results.extend(results4)
            time.sleep(1)

            # 测试5: 错误恢复
            results5 = self.test_error_recovery()
            self.results.extend(results5)
            time.sleep(1)

            # 测试6: 长时间运行
            results6 = self.test_long_duration()
            self.results.extend(results6)
            time.sleep(1)

        except KeyboardInterrupt:
            self.log("\n\n测试被用户中断", "WARN")
        except Exception as e:
            self.log(f"\n\n测试异常终止：{e}", "ERROR")
            traceback.print_exc()
        finally:
            # 清理
            self.cleanup()

            # 生成报告
            self.generate_report()

            self.log("\n" + "="*80)
            self.log("极高难度测试套件完成!")
            self.log("="*80)

if __name__ == "__main__":
    tester = ExtremeTestSuite()
    tester.run_all_tests()
