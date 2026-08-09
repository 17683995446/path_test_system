#!/usr/bin/env python3
"""
极端并发与压力测试脚本
用于发现50层代码分析系统在高负载下的问题
"""

import requests
import json
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

BASE_URL = "http://localhost:5174/api"

class StressTester:
    def __init__(self):
        self.results = []
        self.errors = []
        self.lock = threading.Lock()
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] {message}")
        
    def test_health(self):
        """健康检查测试"""
        try:
            start = time.time()
            response = requests.get(f"{BASE_URL}/health", timeout=10)
            elapsed = time.time() - start
            if response.status_code == 200:
                return {"type": "health", "success": True, "time": elapsed}
            else:
                return {"type": "health", "success": False, "status": response.status_code}
        except Exception as e:
            return {"type": "health", "success": False, "error": str(e)}
            
    def test_get_projects(self):
        """获取项目列表测试"""
        try:
            start = time.time()
            response = requests.get(f"{BASE_URL}/projects", timeout=10)
            elapsed = time.time() - start
            if response.status_code == 200:
                data = response.json()
                return {"type": "get_projects", "success": True, "time": elapsed, "count": len(data)}
            else:
                return {"type": "get_projects", "success": False, "status": response.status_code}
        except Exception as e:
            return {"type": "get_projects", "success": False, "error": str(e)}
            
    def test_create_project(self):
        """创建项目测试"""
        try:
            project_name = f"Stress Test Project {random.randint(1000, 9999)}"
            payload = {
                "name": project_name,
                "path": "/workspace/path_test_system/test_project.py",
                "description": "压力测试项目",
                "language": "Python"
            }
            start = time.time()
            response = requests.post(f"{BASE_URL}/projects", json=payload, timeout=10)
            elapsed = time.time() - start
            if response.status_code == 201:
                data = response.json()
                return {"type": "create_project", "success": True, "time": elapsed, "id": data.get("id")}
            else:
                return {"type": "create_project", "success": False, "status": response.status_code}
        except Exception as e:
            return {"type": "create_project", "success": False, "error": str(e)}
            
    def test_get_issues(self):
        """获取问题列表测试"""
        try:
            start = time.time()
            response = requests.get(f"{BASE_URL}/issues", timeout=10)
            elapsed = time.time() - start
            if response.status_code == 200:
                data = response.json()
                return {"type": "get_issues", "success": True, "time": elapsed, "count": len(data)}
            else:
                return {"type": "get_issues", "success": False, "status": response.status_code}
        except Exception as e:
            return {"type": "get_issues", "success": False, "error": str(e)}
            
    def test_get_tests(self):
        """获取测试列表测试"""
        try:
            start = time.time()
            response = requests.get(f"{BASE_URL}/tests", timeout=10)
            elapsed = time.time() - start
            if response.status_code == 200:
                data = response.json()
                return {"type": "get_tests", "success": True, "time": elapsed, "count": len(data)}
            else:
                return {"type": "get_tests", "success": False, "status": response.status_code}
        except Exception as e:
            return {"type": "get_tests", "success": False, "error": str(e)}
            
    def test_get_settings(self):
        """获取设置测试"""
        try:
            start = time.time()
            response = requests.get(f"{BASE_URL}/settings", timeout=10)
            elapsed = time.time() - start
            if response.status_code == 200:
                return {"type": "get_settings", "success": True, "time": elapsed}
            else:
                return {"type": "get_settings", "success": False, "status": response.status_code}
        except Exception as e:
            return {"type": "get_settings", "success": False, "error": str(e)}
            
    def test_browse_files(self):
        """文件浏览器测试"""
        try:
            payload = {"path": "/workspace/path_test_system"}
            start = time.time()
            response = requests.post(f"{BASE_URL}/files/browse", json=payload, timeout=10)
            elapsed = time.time() - start
            if response.status_code == 200:
                data = response.json()
                return {"type": "browse_files", "success": True, "time": elapsed, "items": len(data.get("items", []))}
            else:
                return {"type": "browse_files", "success": False, "status": response.status_code}
        except Exception as e:
            return {"type": "browse_files", "success": False, "error": str(e)}
            
    def test_read_file(self):
        """读取文件测试"""
        try:
            payload = {"path": "/workspace/path_test_system/test_project.py"}
            start = time.time()
            response = requests.post(f"{BASE_URL}/files/read", json=payload, timeout=10)
            elapsed = time.time() - start
            if response.status_code == 200:
                data = response.json()
                return {"type": "read_file", "success": True, "time": elapsed, "size": len(data.get("content", ""))}
            else:
                return {"type": "read_file", "success": False, "status": response.status_code}
        except Exception as e:
            return {"type": "read_file", "success": False, "error": str(e)}
            
    def run_concurrent_test(self, test_func, num_threads, description):
        """运行并发测试"""
        self.log(f"\n{'='*60}")
        self.log(f"开始 {description}")
        self.log(f"并发数: {num_threads}")
        self.log(f"{'='*60}")
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(test_func) for _ in range(num_threads)]
            
            completed = 0
            for future in as_completed(futures):
                result = future.result()
                with self.lock:
                    self.results.append(result)
                    if not result["success"]:
                        self.errors.append(result)
                        self.log(f"ERROR: {result}")
                completed += 1
                if completed % 10 == 0:
                    self.log(f"进度: {completed}/{num_threads}")
                    
        elapsed = time.time() - start_time
        
        # 统计结果 - 修复：用更可靠的方法统计（从刚才添加的结果而不是全部results中过滤）
        # 由于刚才并发添加了num_threads个结果，取最后num_threads个进行统计
        recent_results = self.results[-num_threads:]
        total = len(recent_results)
        success = len([r for r in recent_results if r["success"]])
        avg_time = sum(r["time"] for r in recent_results if r["success"] and "time" in r) / success if success > 0 else 0
        
        self.log(f"\n{description} 完成!")
        self.log(f"总耗时: {elapsed:.2f}秒")
        self.log(f"成功率: {success}/{total} ({(success/total*100):.1f}%)")
        self.log(f"平均响应时间: {avg_time*1000:.2f}ms")
        
        return elapsed
        
    def run_extreme_concurrent_reads(self):
        """极端并发读取测试"""
        self.log("\n" + "="*80)
        self.log("极端并发读取测试 - 模拟大量用户同时读取数据")
        self.log("="*80)
        
        test_functions = [
            (self.test_get_projects, "获取项目"),
            (self.test_get_issues, "获取问题"),
            (self.test_get_tests, "获取测试"),
            (self.test_get_settings, "获取设置"),
            (self.test_health, "健康检查")
        ]
        
        for func, name in test_functions:
            self.run_concurrent_test(func, 20, f"{name}并发测试")
            time.sleep(1)
            
    def run_mixed_workload(self):
        """混合工作负载测试"""
        self.log("\n" + "="*80)
        self.log("混合工作负载测试 - 模拟真实世界的复杂场景")
        self.log("="*80)
        
        def mixed_request():
            """混合请求"""
            test_choices = [
                self.test_health,
                self.test_get_projects,
                self.test_get_issues,
                self.test_get_tests,
                self.test_browse_files,
                self.test_read_file
            ]
            chosen = random.choice(test_choices)
            return chosen()
            
        self.run_concurrent_test(mixed_request, 30, "混合工作负载测试")
        
    def run_sustained_load(self):
        """持续负载测试"""
        self.log("\n" + "="*80)
        self.log("持续负载测试 - 模拟长时间运行的负载")
        self.log("="*80)
        
        total_requests = 100
        interval = 0.1  # 每100ms发一个请求
        
        self.log(f"总请求数: {total_requests}")
        self.log(f"间隔: {interval*1000}ms")
        
        start_time = time.time()
        
        for i in range(total_requests):
            result = self.test_get_projects()
            with self.lock:
                self.results.append(result)
                if not result["success"]:
                    self.errors.append(result)
                    self.log(f"ERROR (请求 {i+1}): {result}")
            if i % 20 == 0:
                self.log(f"进度: {i+1}/{total_requests}")
            time.sleep(interval)
            
        elapsed = time.time() - start_time
        
        total = len([r for r in self.results if r["type"] == "get_projects"])
        success = len([r for r in self.results if r["type"] == "get_projects" and r["success"]])
        
        self.log(f"\n持续负载测试完成!")
        self.log(f"总耗时: {elapsed:.2f}秒")
        self.log(f"成功率: {success}/{total} ({(success/total*100):.1f}%)")
        
    def generate_report(self):
        """生成测试报告"""
        self.log("\n" + "="*80)
        self.log("测试报告")
        self.log("="*80)
        
        self.log(f"\n总测试数: {len(self.results)}")
        self.log(f"成功数: {len([r for r in self.results if r['success']])}")
        self.log(f"失败数: {len([r for r in self.results if not r['success']])}")
        
        if self.errors:
            self.log(f"\n错误详情 ({len(self.errors)}):")
            for i, error in enumerate(self.errors[:10], 1):
                self.log(f"  {i}. {error}")
            if len(self.errors) > 10:
                self.log(f"  ... 还有 {len(self.errors) - 10} 个错误")
                
        # 按类型统计
        from collections import defaultdict
        stats = defaultdict(lambda: {"count": 0, "success": 0, "total_time": 0})
        
        for result in self.results:
            t = result["type"]
            stats[t]["count"] += 1
            if result["success"]:
                stats[t]["success"] += 1
                if "time" in result:
                    stats[t]["total_time"] += result["time"]
                    
        self.log(f"\n按类型统计:")
        for t, s in stats.items():
            success_rate = (s["success"] / s["count"] * 100) if s["count"] > 0 else 0
            avg_time = (s["total_time"] / s["success"] * 1000) if s["success"] > 0 else 0
            self.log(f"  {t}: {s['success']}/{s['count']} ({success_rate:.1f}%), 平均 {avg_time:.2f}ms")
            
    def run(self):
        """运行所有测试"""
        self.log("="*80)
        self.log("50层代码分析系统 - 极端并发与压力测试")
        self.log("="*80)
        
        # 预热
        self.log("\n[1/4] 预热阶段...")
        self.test_health()
        self.test_get_projects()
        time.sleep(1)
        
        # 极端并发读取
        self.run_extreme_concurrent_reads()
        time.sleep(2)
        
        # 混合工作负载
        self.run_mixed_workload()
        time.sleep(2)
        
        # 持续负载
        self.run_sustained_load()
        
        # 生成报告
        self.generate_report()
        
        self.log("\n" + "="*80)
        self.log("压力测试完成!")
        self.log("="*80)

if __name__ == "__main__":
    tester = StressTester()
    tester.run()
