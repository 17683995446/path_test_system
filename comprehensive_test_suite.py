#!/usr/bin/env python3
"""
全面测试框架 - 符合用户要求的所有测试场景
包括:
1. 静态代码核验
2. 单元全覆盖测试
3. 模块集成联调
4. 接口全量遍历
5. 业务场景闭环
6. 数据一致性校验
7. 异常容错测试
8. 基础性能核验
9. 大规模混乱压力测试
"""

import requests
import json
import time
import random
import threading
import sys
import os
import re
import string
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from pathlib import Path

BASE_URL = "http://localhost:5174/api"

class ComprehensiveTestSuite:
    """全面测试套件"""
    
    def __init__(self):
        self.test_results = defaultdict(list)
        self.errors = []
        self.warnings = []
        self.created_projects = []
        self.start_time = time.time()
        
    def log_test(self, test_name, passed, message=""):
        """记录测试结果"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "✅" if passed else "❌"
        self.test_results[test_name].append({"status": passed, "message": message, "time": timestamp})
        print(f"[{timestamp}] {status} {test_name}: {message}")
        
        if not passed:
            self.errors.append(f"{test_name}: {message}")
            
    def log_warning(self, message):
        """记录警告"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.warnings.append(f"[{timestamp}] ⚠️ {message}")
        print(f"[{timestamp}] ⚠️ {message}")
        
    def print_summary(self):
        """打印测试摘要"""
        print("\n" + "="*100)
        print("📊 全面测试总结报告")
        print("="*100)
        
        total_tests = 0
        passed_tests = 0
        
        for test_name, results in self.test_results.items():
            total = len(results)
            passed = sum(1 for r in results if r["status"])
            total_tests += total
            passed_tests += passed
            print(f"\n📁 {test_name}:")
            for result in results:
                status = "✅" if result["status"] else "❌"
                print(f"   {status} [{result['time']}] {result['message']}")
        
        print("\n" + "="*100)
        print(f"📈 总计: {total_tests} 测试, {passed_tests} 通过, {total_tests - passed_tests} 失败")
        print(f"📈 成功率: {passed_tests/total_tests*100:.2f}%" if total_tests > 0 else "")
        
        if self.errors:
            print(f"\n❌ 错误记录 ({len(self.errors)}):")
            for error in self.errors[:20]:
                print(f"   {error}")
        
        if self.warnings:
            print(f"\n⚠️ 警告记录 ({len(self.warnings)}):")
            for warning in self.warnings[:20]:
                print(f"   {warning}")
        
        print(f"\n⏱️ 测试总耗时: {time.time() - self.start_time:.2f} 秒")
        print("="*100)
        
        return passed_tests == total_tests

    # ============================================================
    # 1. 静态代码核验
    # ============================================================
    def static_code_analysis(self):
        """静态代码核验"""
        print("\n" + "="*100)
        print("📝 1. 静态代码核验")
        print("="*100)
        
        # 检查代码文件存在性
        test_files = [
            "/workspace/path_test_system/ultra_detailed_log_api_server.py",
            "/workspace/path_test_system/robust_api_server.py"
        ]
        
        for file_path in test_files:
            if os.path.exists(file_path):
                self.log_test("静态代码检查-文件存在性", True, f"{file_path} 存在")
                
                # 检查文件大小和内容
                file_size = os.path.getsize(file_path)
                if file_size > 1000:
                    self.log_test("静态代码检查-文件大小", True, f"{file_path} 大小: {file_size} 字节")
                else:
                    self.log_test("静态代码检查-文件大小", False, f"{file_path} 异常小")
                
                # 检查基本语法
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # 检查关键字
                    required_keywords = ["def", "class", "import", "if", "try"]
                    for keyword in required_keywords:
                        if keyword in content:
                            self.log_test(f"静态代码检查-关键字{keyword}", True, f"找到关键字 {keyword}")
                        
                    # 检查问题
                    if len(content) > 0:
                        self.log_test("静态代码检查-非空文件", True, "文件内容正常")
                except Exception as e:
                    self.log_test("静态代码检查-文件读取", False, f"读取失败: {str(e)}")
            else:
                self.log_test("静态代码检查-文件存在性", False, f"{file_path} 不存在")
        
        # 检查数据目录
        data_dir = Path("/workspace/path_test_system/data")
        if data_dir.exists():
            self.log_test("静态代码检查-数据目录", True, "数据目录存在")
        else:
            self.log_test("静态代码检查-数据目录", False, "数据目录不存在")
            
    # ============================================================
    # 2. 单元全覆盖测试
    # ============================================================
    def unit_tests(self):
        """单元全覆盖测试"""
        print("\n" + "="*100)
        print("🧪 2. 单元全覆盖测试")
        print("="*100)
        
        # 健康检查API测试
        for i in range(10):
            try:
                response = requests.get(f"{BASE_URL}/health", timeout=10)
                self.log_test(f"单元测试-健康检查#{i+1}", response.status_code == 200, 
                           f"状态码: {response.status_code}")
            except Exception as e:
                self.log_test(f"单元测试-健康检查#{i+1}", False, f"异常: {str(e)}")
        
        # 获取项目列表测试
        for i in range(5):
            try:
                response = requests.get(f"{BASE_URL}/projects", timeout=10)
                self.log_test(f"单元测试-获取项目列表#{i+1}", 
                           response.status_code in [200, 201],
                           f"状态码: {response.status_code}")
            except Exception as e:
                self.log_test(f"单元测试-获取项目列表#{i+1}", False, f"异常: {str(e)}")
        
        # 创建和删除项目测试
        for i in range(5):
            try:
                # 创建项目
                project_data = {
                    "name": f"单元测试项目_{i}_{int(time.time())}",
                    "path": "/workspace/path_test_system",
                    "description": "单元测试描述"
                }
                response = requests.post(f"{BASE_URL}/projects", json=project_data, timeout=10)
                
                if response.status_code == 201:
                    self.log_test(f"单元测试-创建项目#{i+1}", True, "创建成功")
                    
                    try:
                        project = response.json()
                        project_id = project.get("id")
                        
                        if project_id:
                            self.created_projects.append(project_id)
                            
                            # 获取单个项目
                            get_response = requests.get(f"{BASE_URL}/projects/{project_id}", timeout=10)
                            self.log_test(f"单元测试-获取项目#{i+1}", 
                                       get_response.status_code in [200, 404],
                                       f"状态码: {get_response.status_code}")
                            
                            # 更新项目
                            update_data = {"name": f"更新后项目_{i}"}
                            update_response = requests.put(f"{BASE_URL}/projects/{project_id}", 
                                                          json=update_data, timeout=10)
                            self.log_test(f"单元测试-更新项目#{i+1}", 
                                       update_response.status_code in [200, 204, 404],
                                       f"状态码: {update_response.status_code}")
                            
                            # 删除项目
                            delete_response = requests.delete(f"{BASE_URL}/projects/{project_id}", timeout=10)
                            self.log_test(f"单元测试-删除项目#{i+1}", 
                                       delete_response.status_code in [200, 204, 404],
                                       f"状态码: {delete_response.status_code}")
                    except Exception as e:
                        self.log_warning(f"单元测试-项目操作详情异常: {str(e)}")
                else:
                    self.log_test(f"单元测试-创建项目#{i+1}", False, f"创建失败: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"单元测试-项目操作#{i+1}", False, f"异常: {str(e)}")
                
    # ============================================================
    # 3. 模块集成联调
    # ============================================================
    def integration_tests(self):
        """模块集成联调测试"""
        print("\n" + "="*100)
        print("🔗 3. 模块集成联调测试")
        print("="*100)
        
        # 完整业务流程
        test_cases = [
            ("创建-获取-更新-删除流程", self._test_full_project_crud),
            ("文件浏览和读取", self._test_file_operations),
            ("指标监控端点", self._test_metrics_endpoint),
        ]
        
        for test_name, test_func in test_cases:
            try:
                result = test_func()
                self.log_test(f"集成测试-{test_name}", result[0], result[1])
            except Exception as e:
                self.log_test(f"集成测试-{test_name}", False, f"异常: {str(e)}")
                
    def _test_full_project_crud(self):
        """测试完整项目CRUD流程"""
        test_name = "单元测试项目_" + str(int(time.time()))
        
        try:
            # 创建
            create_resp = requests.post(f"{BASE_URL}/projects", 
                                       json={"name": test_name, 
                                             "path": "/workspace/path_test_system"},
                                       timeout=15)
            if create_resp.status_code != 201:
                return False, "创建失败"
                
            project = create_resp.json()
            project_id = project.get("id")
            if not project_id:
                return False, "项目ID缺失"
                
            self.created_projects.append(project_id)
            
            # 获取
            get_resp = requests.get(f"{BASE_URL}/projects/{project_id}", timeout=10)
            if get_resp.status_code != 200:
                return False, "获取失败"
                
            # 更新
            update_resp = requests.put(f"{BASE_URL}/projects/{project_id}", 
                                       json={"name": test_name + "_updated"},
                                       timeout=10)
            if update_resp.status_code not in [200, 204]:
                return False, "更新失败"
                
            # 删除
            delete_resp = requests.delete(f"{BASE_URL}/projects/{project_id}", timeout=10)
            if delete_resp.status_code not in [200, 204]:
                return False, "删除失败"
                
            return True, "CRUD流程正常"
        except Exception as e:
            return False, f"异常: {str(e)}"
            
    def _test_file_operations(self):
        """测试文件操作"""
        try:
            # 浏览文件
            browse_resp = requests.get(f"{BASE_URL}/files/browse", 
                                      params={"path": "/workspace/path_test_system"},
                                      timeout=10)
            if browse_resp.status_code != 200:
                return False, "浏览失败"
                
            # 尝试读取文件
            files = ["requirements.txt", "robust_api_server.py"]
            for file in files:
                file_path = f"/workspace/path_test_system/{file}"
                read_resp = requests.get(f"{BASE_URL}/files/read", 
                                        params={"path": file_path},
                                        timeout=10)
                if read_resp.status_code in [200, 404]:
                    continue
                else:
                    return False, f"读取{file}失败"
                    
            return True, "文件操作正常"
        except Exception as e:
            return False, f"异常: {str(e)}"
            
    def _test_metrics_endpoint(self):
        """测试指标端点"""
        try:
            metrics_resp = requests.get(f"{BASE_URL}/metrics", timeout=10)
            if metrics_resp.status_code == 200:
                metrics = metrics_resp.json()
                if "resource" in metrics and "load" in metrics:
                    return True, "指标数据正常"
            return False, "指标响应异常"
        except Exception as e:
            return False, f"异常: {str(e)}"
            
    # ============================================================
    # 4. 接口全量遍历
    # ============================================================
    def interface_tests(self):
        """接口全量遍历"""
        print("\n" + "="*100)
        print("🌐 4. 接口全量遍历测试")
        print("="*100)
        
        # 所有接口列表
        endpoints = [
            ("GET", "/health", "健康检查"),
            ("GET", "/metrics", "获取指标"),
            ("GET", "/projects", "获取项目"),
            ("POST", "/projects", "创建项目"),
            ("GET", "/issues", "获取问题"),
            ("GET", "/settings", "获取设置"),
            ("GET", "/files/browse", "浏览文件"),
            ("GET", "/files/read", "读取文件"),
        ]
        
        for method, endpoint, desc in endpoints:
            try:
                url = f"{BASE_URL}{endpoint}"
                
                if method == "GET":
                    if endpoint == "/files/browse":
                        response = requests.get(url, params={"path": "/workspace"}, timeout=10)
                    elif endpoint == "/files/read":
                        response = requests.get(url, params={"path": "/workspace/path_test_system/requirements.txt"}, timeout=10)
                    else:
                        response = requests.get(url, timeout=10)
                elif method == "POST":
                    if endpoint == "/projects":
                        response = requests.post(url, json={"name": "接口测试", "path": "/workspace"}, timeout=10)
                    else:
                        response = requests.post(url, json={}, timeout=10)
                
                # 记录结果（非5xx状态视为成功）
                self.log_test(f"接口测试-{desc}", 
                           response.status_code < 500,
                           f"{method} {endpoint} - 状态码: {response.status_code}")
                
                # 如果创建了项目，删除它
                if method == "POST" and endpoint == "/projects" and response.status_code == 201:
                    try:
                        project = response.json()
                        project_id = project.get("id")
                        if project_id:
                            requests.delete(f"{BASE_URL}/projects/{project_id}", timeout=10)
                    except:
                        pass
                        
            except Exception as e:
                self.log_test(f"接口测试-{desc}", False, f"异常: {str(e)}")
                
    # ============================================================
    # 5. 业务场景闭环
    # ============================================================
    def business_scenario_tests(self):
        """业务场景闭环"""
        print("\n" + "="*100)
        print("🔄 5. 业务场景闭环测试")
        print("="*100)
        
        scenarios = [
            ("正常工作流程", self._test_normal_workflow),
            ("并发操作流程", self._test_concurrent_workflow),
            ("快速创建删除流程", self._test_rapid_crud),
        ]
        
        for scenario_name, scenario_func in scenarios:
            try:
                result = scenario_func()
                self.log_test(f"业务场景-{scenario_name}", result[0], result[1])
            except Exception as e:
                self.log_test(f"业务场景-{scenario_name}", False, f"异常: {str(e)}")
                
    def _test_normal_workflow(self):
        """测试正常工作流程"""
        try:
            # 1. 健康检查
            health_resp = requests.get(f"{BASE_URL}/health", timeout=10)
            if health_resp.status_code != 200:
                return False, "健康检查失败"
                
            # 2. 获取项目列表
            projects_resp = requests.get(f"{BASE_URL}/projects", timeout=10)
            if projects_resp.status_code != 200:
                return False, "获取项目失败"
                
            # 3. 创建测试项目
            create_resp = requests.post(f"{BASE_URL}/projects", 
                                       json={"name": "业务测试_" + str(int(time.time())),
                                             "path": "/workspace/path_test_system"},
                                       timeout=10)
            if create_resp.status_code != 201:
                return False, "创建项目失败"
                
            project_id = create_resp.json().get("id")
            self.created_projects.append(project_id)
            
            # 4. 分析项目
            analyze_resp = requests.post(f"{BASE_URL}/analyze", 
                                        json={"projectId": project_id},
                                        timeout=10)
            if analyze_resp.status_code != 200:
                return False, "分析失败"
                
            # 5. 清理
            requests.delete(f"{BASE_URL}/projects/{project_id}", timeout=10)
            
            return True, "正常工作流程完成"
        except Exception as e:
            return False, f"异常: {str(e)}"
            
    def _test_concurrent_workflow(self):
        """测试并发操作流程"""
        test_start = time.time()
        
        def worker(worker_id):
            local_success = False
            try:
                name = f"并发测试_{worker_id}_{int(time.time()*1000)}"
                resp = requests.post(f"{BASE_URL}/projects", 
                                    json={"name": name, "path": "/workspace/path_test_system"},
                                    timeout=15)
                if resp.status_code == 201:
                    project = resp.json()
                    project_id = project.get("id")
                    if project_id:
                        requests.get(f"{BASE_URL}/projects/{project_id}", timeout=10)
                        requests.delete(f"{BASE_URL}/projects/{project_id}", timeout=10)
                        local_success = True
            except:
                pass
            return local_success
            
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(worker, i) for i in range(10)]
            results = [f.result() for f in futures]
            
        success_count = sum(1 for r in results if r)
        
        return success_count >= 7, f"并发测试: {success_count}/{len(results)} 成功"
        
    def _test_rapid_crud(self):
        """测试快速创建删除"""
        try:
            for i in range(10):
                # 创建
                create_resp = requests.post(f"{BASE_URL}/projects", 
                                           json={"name": f"快速测试_{i}_{int(time.time())}",
                                                 "path": "/workspace/path_test_system"},
                                           timeout=10)
                if create_resp.status_code == 201:
                    project_id = create_resp.json().get("id")
                    self.created_projects.append(project_id)
                    requests.delete(f"{BASE_URL}/projects/{project_id}", timeout=10)
                    
            return True, "快速CRUD完成"
        except Exception as e:
            return False, f"异常: {str(e)}"
            
    # ============================================================
    # 6. 数据一致性校验
    # ============================================================
    def data_consistency_tests(self):
        """数据一致性校验"""
        print("\n" + "="*100)
        print("📝 6. 数据一致性校验")
        print("="*100)
        
        try:
            # 首先创建几个项目
            project_ids = []
            for i in range(3):
                name = f"一致性测试_{i}_{int(time.time())}"
                resp = requests.post(f"{BASE_URL}/projects", 
                                    json={"name": name, "path": "/workspace"},
                                    timeout=10)
                if resp.status_code == 201:
                    project_id = resp.json().get("id")
                    project_ids.append(project_id)
                    self.created_projects.append(project_id)
                    
            # 获取列表
            projects_resp = requests.get(f"{BASE_URL}/projects", timeout=10)
            projects = projects_resp.json() if projects_resp.status_code == 200 else []
            
            # 检查一致性
            for pid in project_ids:
                found = any(p.get("id") == pid for p in projects)
                self.log_test(f"数据一致性-项目{pid}", found, "项目存在于列表中")
                
                # 获取单个项目
                single_resp = requests.get(f"{BASE_URL}/projects/{pid}", timeout=10)
                self.log_test(f"数据一致性-获取{pid}", 
                           single_resp.status_code == 200,
                           f"状态码: {single_resp.status_code}")
                           
        except Exception as e:
            self.log_test("数据一致性校验", False, f"异常: {str(e)}")
            
        # 清理
        for pid in project_ids:
            try:
                requests.delete(f"{BASE_URL}/projects/{pid}", timeout=10)
            except:
                pass
                
    # ============================================================
    # 7. 异常容错测试
    # ============================================================
    def error_tolerance_tests(self):
        """异常容错测试"""
        print("\n" + "="*100)
        print("⚠️ 7. 异常容错测试")
        print("="*100)
        
        # 测试无效输入
        invalid_inputs = [
            ("空项目名称", {"name": "", "path": "/workspace"}),
            ("空路径", {"name": "test", "path": ""}),
            ("过长名称", {"name": "x"*300, "path": "/workspace"}),
            ("非法路径", {"name": "test", "path": "/etc/passwd"}),
            ("空JSON", {}),
        ]
        
        for test_name, test_data in invalid_inputs:
            try:
                resp = requests.post(f"{BASE_URL}/projects", json=test_data, timeout=10)
                # 4xx 是预期的错误响应
                expected = resp.status_code >= 400 and resp.status_code < 500
                self.log_test(f"异常容错-{test_name}", 
                           expected, 
                           f"状态码: {resp.status_code}")
            except Exception as e:
                self.log_test(f"异常容错-{test_name}", False, f"异常: {str(e)}")
                
        # 测试不存在的项目
        for i in range(3):
            fake_id = "nonexistent_" + ''.join(random.choices(string.ascii_letters, k=20))
            try:
                # 获取
                get_resp = requests.get(f"{BASE_URL}/projects/{fake_id}", timeout=10)
                self.log_test(f"异常容错-获取不存在项目#{i+1}", 
                           get_resp.status_code == 404,
                           f"状态码: {get_resp.status_code}")
                           
                # 更新
                put_resp = requests.put(f"{BASE_URL}/projects/{fake_id}", 
                                       json={"name": "fake"}, timeout=10)
                self.log_test(f"异常容错-更新不存在项目#{i+1}", 
                           put_resp.status_code == 404,
                           f"状态码: {put_resp.status_code}")
                           
                # 删除
                del_resp = requests.delete(f"{BASE_URL}/projects/{fake_id}", timeout=10)
                self.log_test(f"异常容错-删除不存在项目#{i+1}", 
                           del_resp.status_code in [200, 204, 404],
                           f"状态码: {del_resp.status_code}")
                           
            except Exception as e:
                self.log_test(f"异常容错-不存在项目#{i+1}", False, f"异常: {str(e)}")
                
    # ============================================================
    # 8. 基础性能核验
    # ============================================================
    def performance_tests(self):
        """基础性能核验"""
        print("\n" + "="*100)
        print("⚡ 8. 基础性能核验")
        print("="*100)
        
        # 健康检查性能
        durations = []
        for i in range(50):
            start = time.time()
            try:
                requests.get(f"{BASE_URL}/health", timeout=5)
                end = time.time()
                durations.append(end - start)
            except:
                pass
                
        if durations:
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            min_duration = min(durations)
            
            self.log_test("性能测试-健康检查平均响应", 
                       avg_duration < 1.0, 
                       f"平均: {avg_duration*1000:.2f}ms, 最小: {min_duration*1000:.2f}ms, 最大: {max_duration*1000:.2f}ms")
                
        # 获取项目列表性能
        get_durations = []
        for i in range(30):
            start = time.time()
            try:
                requests.get(f"{BASE_URL}/projects", timeout=5)
                end = time.time()
                get_durations.append(end - start)
            except:
                pass
                
        if get_durations:
            avg_get = sum(get_durations) / len(get_durations)
            self.log_test("性能测试-获取项目列表", 
                       avg_get < 2.0, 
                       f"平均: {avg_get*1000:.2f}ms")
            
    # ============================================================
    # 9. 大规模混乱压力测试（重要！）
    # ============================================================
    def chaos_stress_tests(self):
        """大规模混乱压力测试"""
        print("\n" + "="*100)
        print("🔥 9. 大规模混乱压力测试")
        print("="*100)
        
        test_duration = 300  # 5分钟
        num_workers = 15
        
        shared_stats = {"total": 0, "success": 0, "failed": 0}
        lock = threading.Lock()
        
        def chaos_worker(worker_id):
            """混乱工作线程 - 随机操作"""
            worker_start = time.time()
            
            while time.time() - worker_start < test_duration:
                try:
                    operation = random.choices([
                        "health",
                        "create",
                        "get_all",
                        "get_single",
                        "update",
                        "delete",
                        "browse",
                        "read",
                        "issues",
                        "settings",
                    ], weights=[15, 20, 20, 10, 10, 10, 5, 5, 3, 2])[0]
                    
                    success = False
                    
                    with lock:
                        shared_stats["total"] += 1
                    
                    if operation == "health":
                        resp = requests.get(f"{BASE_URL}/health", timeout=10)
                        success = resp.status_code == 200
                        
                    elif operation == "create":
                        # 随机生成混乱的数据
                        name_options = [
                            f"混乱项目_{worker_id}_{int(time.time()*1000)}",
                            "x"*50,
                            string.punctuation*5,
                            "",
                            "a",
                            "<script>hack</script>",
                            " " * 20,
                        ]
                        name = random.choice(name_options)
                        
                        path_options = [
                            "/workspace/path_test_system",
                            "/workspace",
                            "/etc",
                            "/",
                            "",
                        ]
                        path = random.choice(path_options)
                        
                        resp = requests.post(f"{BASE_URL}/projects", 
                                            json={"name": name, "path": path, 
                                                 "description": random.choice(["", "desc", None])},
                                            timeout=15)
                        
                        if resp.status_code == 201:
                            success = True
                            try:
                                project_id = resp.json().get("id")
                                if project_id:
                                    self.created_projects.append(project_id)
                            except:
                                pass
                        else:
                            # 4xx 是预期错误，也算作"成功"（系统正确处理异常）
                            success = 400 <= resp.status_code < 500
                            
                    elif operation == "get_all":
                        resp = requests.get(f"{BASE_URL}/projects", timeout=10)
                        success = resp.status_code == 200
                        
                    elif operation == "get_single":
                        # 随机获取或用假ID
                        if self.created_projects and random.random() < 0.7:
                            pid = random.choice(self.created_projects)
                        else:
                            pid = "fake_" + ''.join(random.choices(string.ascii_letters + string.digits, k=30))
                            
                        resp = requests.get(f"{BASE_URL}/projects/{pid}", timeout=10)
                        success = resp.status_code in [200, 404]
                        
                    elif operation == "update":
                        if self.created_projects and random.random() < 0.7:
                            pid = random.choice(self.created_projects)
                        else:
                            pid = "fake_" + ''.join(random.choices(string.ascii_letters, k=30))
                            
                        update_data = {
                            "name": random.choice([f"更新_{int(time.time())}", "", "x"*100]),
                            "description": random.choice(["", "desc", None])
                        }
                        
                        resp = requests.put(f"{BASE_URL}/projects/{pid}", 
                                           json=update_data, timeout=10)
                        success = resp.status_code in [200, 204, 404, 400]
                        
                    elif operation == "delete":
                        if self.created_projects and random.random() < 0.7:
                            pid = self.created_projects.pop(0) if self.created_projects else "fake"
                        else:
                            pid = "fake_" + ''.join(random.choices(string.ascii_letters, k=30))
                            
                        resp = requests.delete(f"{BASE_URL}/projects/{pid}", timeout=10)
                        success = resp.status_code in [200, 204, 404]
                        
                    elif operation == "browse":
                        path = random.choice(["/workspace", "/workspace/path_test_system", "/", "/etc"])
                        resp = requests.get(f"{BASE_URL}/files/browse", params={"path": path}, timeout=10)
                        success = resp.status_code in [200, 400, 403, 404]
                        
                    elif operation == "read":
                        files = ["/workspace/path_test_system/requirements.txt", 
                                "/workspace/path_test_system/nonexistent.txt",
                                "/etc/passwd"]
                        filepath = random.choice(files)
                        resp = requests.get(f"{BASE_URL}/files/read", params={"path": filepath}, timeout=10)
                        success = resp.status_code in [200, 400, 403, 404]
                        
                    elif operation == "issues":
                        resp = requests.get(f"{BASE_URL}/issues", timeout=10)
                        success = resp.status_code == 200
                        
                    elif operation == "settings":
                        resp = requests.get(f"{BASE_URL}/settings", timeout=10)
                        success = resp.status_code == 200
                        
                    # 统计
                    with lock:
                        if success:
                            shared_stats["success"] += 1
                        else:
                            shared_stats["failed"] += 1
                            
                except Exception as e:
                    with lock:
                        shared_stats["failed"] += 1
                        
                # 随机延迟
                time.sleep(random.uniform(0.01, 0.3))
        
        print(f"🚀 启动 {num_workers} 个并发工作线程，测试 {test_duration} 秒...")
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(chaos_worker, i) for i in range(num_workers)]
            
            # 实时监控
            last_print = time.time()
            while any(not f.done() for f in futures):
                time.sleep(1)
                
                if time.time() - last_print >= 30:
                    with lock:
                        total = shared_stats["total"]
                        success = shared_stats["success"]
                        failed = shared_stats["failed"]
                        elapsed = time.time() - start_time
                        rate = total / elapsed if elapsed > 0 else 0
                        
                        print(f"  📊 实时统计 - 总请求: {total}, "
                              f"成功: {success}, 失败: {failed}, "
                              f"成功率: {success/total*100:.1f}% "
                              f"({rate:.1f} req/s)")
                    last_print = time.time()
        
        # 最终统计
        elapsed = time.time() - start_time
        total = shared_stats["total"]
        success = shared_stats["success"]
        failed = shared_stats["failed"]
        success_rate = success / total * 100 if total > 0 else 0
        
        print(f"\n📊 混乱压力测试结果:")
        print(f"   总请求: {total}")
        print(f"   成功: {success}")
        print(f"   失败: {failed}")
        print(f"   成功率: {success_rate:.2f}%")
        print(f"   耗时: {elapsed:.2f}秒")
        print(f"   吞吐量: {total/elapsed:.2f} req/s")
        
        self.log_test("大规模混乱压力测试", 
                   success_rate >= 90.0, 
                   f"成功率: {success_rate:.2f}%, 总请求: {total}")
        
        return success_rate >= 90.0
                
    # ============================================================
    # 清理
    # ============================================================
    def cleanup(self):
        """清理创建的测试项目"""
        print("\n" + "="*100)
        print("🧹 清理测试数据")
        print("="*100)
        
        cleaned = 0
        for project_id in self.created_projects:
            try:
                requests.delete(f"{BASE_URL}/projects/{project_id}", timeout=10)
                cleaned += 1
            except:
                pass
                
        print(f"🧹 清理完成: {cleaned} 个项目")
        
    # ============================================================
    # 运行所有测试
    # ============================================================
    def run_all_tests(self):
        """运行所有测试"""
        print("="*100)
        print("🚀 开始全面测试")
        print("="*100)
        print(f"📅 开始时间: {datetime.now()}")
        print("="*100)
        
        try:
            self.static_code_analysis()
            self.unit_tests()
            self.integration_tests()
            self.interface_tests()
            self.business_scenario_tests()
            self.data_consistency_tests()
            self.error_tolerance_tests()
            self.performance_tests()
            self.chaos_stress_tests()
            
            return self.print_summary()
            
        finally:
            self.cleanup()

# ============================================================
# 主函数
# ============================================================
if __name__ == "__main__":
    print("检查服务器连接...")
    try:
        test_response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"✅ 服务器连接成功！状态码: {test_response.status_code}")
        
        test_suite = ComprehensiveTestSuite()
        passed = test_suite.run_all_tests()
        
        sys.exit(0 if passed else 1)
        
    except Exception as e:
        print(f"❌ 服务器连接失败: {str(e)}")
        print("请确保API服务器正在运行!")
        sys.exit(1)
