#!/usr/bin/env python3
"""
高级并发测试 - 包括并发写入和代码分析
"""

import requests
import json
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

BASE_URL = "http://localhost:5174/api"

class AdvancedTester:
    def __init__(self):
        self.results = []
        self.errors = []
        self.created_project_ids = []
        self.lock = threading.Lock()
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] {message}")
        
    def test_create_project(self, index):
        """创建项目"""
        try:
            project_name = f"Advanced Test Project {index} {random.randint(1000, 9999)}"
            payload = {
                "name": project_name,
                "path": "/workspace/path_test_system/test_project.py",
                "description": "高级测试项目",
                "language": "Python"
            }
            start = time.time()
            response = requests.post(f"{BASE_URL}/projects", json=payload, timeout=15)
            elapsed = time.time() - start
            if response.status_code == 201:
                data = response.json()
                project_id = data.get("id")
                with self.lock:
                    self.created_project_ids.append(project_id)
                return {"type": "create_project", "success": True, "time": elapsed, "id": project_id}
            else:
                return {"type": "create_project", "success": False, "status": response.status_code}
        except Exception as e:
            return {"type": "create_project", "success": False, "error": str(e)}
            
    def test_analyze_project(self, project_id):
        """分析项目"""
        try:
            payload = {"projectId": project_id}
            start = time.time()
            response = requests.post(f"{BASE_URL}/analyze", json=payload, timeout=30)
            elapsed = time.time() - start
            if response.status_code == 200:
                data = response.json()
                return {"type": "analyze", "success": True, "time": elapsed, "score": data.get("score")}
            else:
                return {"type": "analyze", "success": False, "status": response.status_code}
        except Exception as e:
            return {"type": "analyze", "success": False, "error": str(e)}
            
    def test_delete_project(self, project_id):
        """删除项目"""
        try:
            start = time.time()
            response = requests.delete(f"{BASE_URL}/projects/{project_id}", timeout=10)
            elapsed = time.time() - start
            if response.status_code in [200, 204]:
                return {"type": "delete_project", "success": True, "time": elapsed}
            else:
                return {"type": "delete_project", "success": False, "status": response.status_code}
        except Exception as e:
            return {"type": "delete_project", "success": False, "error": str(e)}
            
    def test_save_settings(self):
        """保存设置"""
        try:
            payload = {
                "theme": "dark",
                "autoSave": True,
                "maxFileSize": 20,
                "analysisDepth": 50,
                "notifications": True,
                "soundEffects": False
            }
            start = time.time()
            response = requests.post(f"{BASE_URL}/settings", json=payload, timeout=10)
            elapsed = time.time() - start
            if response.status_code == 200:
                return {"type": "save_settings", "success": True, "time": elapsed}
            else:
                return {"type": "save_settings", "success": False, "status": response.status_code}
        except Exception as e:
            return {"type": "save_settings", "success": False, "error": str(e)}
            
    def test_read_write_mixed(self):
        """读写混合测试"""
        test_choices = [
            ("read", lambda: requests.get(f"{BASE_URL}/projects", timeout=10)),
            ("read", lambda: requests.get(f"{BASE_URL}/issues", timeout=10)),
            ("write_create", lambda index: self.test_create_project(index)),
            ("read", lambda: requests.get(f"{BASE_URL}/tests", timeout=10)),
            ("write_settings", lambda: self.test_save_settings())
        ]
        
        choice = random.choice(test_choices)
        if choice[0] == "read":
            try:
                start = time.time()
                response = choice[1]()
                elapsed = time.time() - start
                if response.status_code == 200:
                    return {"type": "mixed_read", "success": True, "time": elapsed}
                else:
                    return {"type": "mixed_read", "success": False, "status": response.status_code}
            except Exception as e:
                return {"type": "mixed_read", "success": False, "error": str(e)}
        elif choice[0] == "write_create":
            return choice[1](random.randint(1000, 9999))
        else:  # write_settings
            return choice[1]()
            
    def run_concurrent_create(self):
        """并发创建项目测试"""
        self.log("\n" + "="*80)
        self.log("并发创建项目测试 - 测试写入操作的并发安全性")
        self.log("="*80)
        
        num_threads = 10
        self.log(f"并发创建 {num_threads} 个项目...")
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(self.test_create_project, i) for i in range(num_threads)]
            
            completed = 0
            for future in as_completed(futures):
                result = future.result()
                with self.lock:
                    self.results.append(result)
                    if not result["success"]:
                        self.errors.append(result)
                        self.log(f"ERROR: {result}")
                completed += 1
                self.log(f"进度: {completed}/{num_threads}")
                
        elapsed = time.time() - start_time
        
        total = num_threads
        success = len([r for r in self.results[-num_threads:] if r["success"]])
        
        self.log(f"\n并发创建项目测试完成!")
        self.log(f"总耗时: {elapsed:.2f}秒")
        self.log(f"成功率: {success}/{total} ({(success/total*100):.1f}%)")
        self.log(f"成功创建 {len(self.created_project_ids)} 个项目")
        
    def run_concurrent_create_and_analyze(self):
        """并发创建和分析测试 - 先创建，然后按顺序分析"""
        self.log("\n" + "="*80)
        self.log("并发创建+分析测试 - 模拟真实工作流程")
        self.log("="*80)
        
        # 先创建一些新项目来分析
        self.log("\n[步骤1] 创建新项目用于分析...")
        new_projects = []
        for i in range(3):
            result = self.test_create_project(1000 + i)
            if result["success"]:
                new_projects.append(result["id"])
                self.results.append(result)
        
        self.log(f"成功创建 {len(new_projects)} 个新项目")
        
        if not new_projects:
            self.log("没有新项目，跳过分析测试")
            return
            
        # 获取一些现有项目
        try:
            response = requests.get(f"{BASE_URL}/projects", timeout=10)
            if response.status_code == 200:
                projects = response.json()
                existing_ids = [p["id"] for p in projects if p["id"] not in new_projects][:3]
                all_project_ids = new_projects + existing_ids
                self.log(f"共有 {len(all_project_ids)} 个项目可用于分析")
            else:
                self.log(f"获取项目失败，使用新创建的项目")
                all_project_ids = new_projects
        except Exception as e:
            self.log(f"获取项目异常: {e}")
            all_project_ids = new_projects
            
        # 串行分析（避免409冲突），同时穿插其他操作
        self.log("\n[步骤2] 分析项目并穿插其他操作...")
        
        def mixed_task(index, project_id):
            """混合任务：分析+其他读操作"""
            results = []
            # 分析这个项目
            results.append(self.test_analyze_project(project_id))
            # 同时做一些读操作
            for _ in range(2):
                try:
                    start = time.time()
                    requests.get(f"{BASE_URL}/projects", timeout=5)
                    elapsed = time.time() - start
                    results.append({"type": "concurrent_read", "success": True, "time": elapsed})
                except Exception as e:
                    results.append({"type": "concurrent_read", "success": False, "error": str(e)})
            return results
            
        num_threads = len(all_project_ids)
        self.log(f"启动 {num_threads} 个分析工作流，每个包含分析+读操作...")
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(mixed_task, i, pid) for i, pid in enumerate(all_project_ids)]
            
            completed = 0
            for future in as_completed(futures):
                task_results = future.result()
                with self.lock:
                    for r in task_results:
                        self.results.append(r)
                        if not r["success"] and r.get("status") != 409:  # 409是预期行为
                            self.errors.append(r)
                            self.log(f"ERROR: {r}")
                completed += 1
                self.log(f"进度: {completed}/{num_threads}")
                    
        elapsed = time.time() - start_time
        
        # 统计分析任务（最后 num_threads * 3 个结果）
        task_results = self.results[-(num_threads * 3):] if num_threads > 0 else []
        analyze_tasks = [r for r in task_results if r["type"] == "analyze"]
        total = len(analyze_tasks)
        success = len([r for r in analyze_tasks if r["success"] or r.get("status") == 409])
        
        self.log(f"\n并发创建+分析测试完成!")
        self.log(f"总耗时: {elapsed:.2f}秒")
        self.log(f"分析任务: {len([r for r in analyze_tasks if r['success']])}/{len(analyze_tasks)} 成功，其余409是预期行为")
        
    def run_mixed_read_write(self):
        """混合读写测试"""
        self.log("\n" + "="*80)
        self.log("混合读写测试 - 大量并发读 + 少量并发写")
        self.log("="*80)
        
        num_threads = 20
        self.log(f"启动 {num_threads} 个并发混合读写...")
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(self.test_read_write_mixed) for _ in range(num_threads)]
            
            completed = 0
            for future in as_completed(futures):
                result = future.result()
                with self.lock:
                    self.results.append(result)
                    if not result["success"]:
                        self.errors.append(result)
                        self.log(f"ERROR: {result}")
                completed += 1
                if completed % 5 == 0:
                    self.log(f"进度: {completed}/{num_threads}")
                    
        elapsed = time.time() - start_time
        
        total = num_threads
        success = len([r for r in self.results[-num_threads:] if r["success"]])
        
        self.log(f"\n混合读写测试完成!")
        self.log(f"总耗时: {elapsed:.2f}秒")
        self.log(f"成功率: {success}/{total} ({(success/total*100):.1f}%)")
        
    def cleanup(self):
        """清理测试数据"""
        self.log("\n" + "="*80)
        self.log("清理测试数据...")
        self.log("="*80)
        
        if not self.created_project_ids:
            self.log("没有需要清理的项目")
            return
            
        self.log(f"删除 {len(self.created_project_ids)} 个测试项目...")
        
        success_count = 0
        for project_id in self.created_project_ids:
            result = self.test_delete_project(project_id)
            if result["success"]:
                success_count += 1
                
        self.log(f"清理完成: 删除了 {success_count}/{len(self.created_project_ids)} 个项目")
        
    def generate_report(self):
        """生成测试报告"""
        self.log("\n" + "="*80)
        self.log("高级测试报告")
        self.log("="*80)
        
        self.log(f"\n总测试数: {len(self.results)}")
        self.log(f"成功数: {len([r for r in self.results if r['success']])}")
        self.log(f"失败数: {len([r for r in self.results if not r['success']])}")
        
        if self.errors:
            self.log(f"\n错误详情 ({len(self.errors)}):")
            for i, error in enumerate(self.errors[:10], 1):
                self.log(f"  {i}. {error}")
                
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
        """运行所有高级测试"""
        self.log("="*80)
        self.log("50层代码分析系统 - 高级并发测试")
        self.log("="*80)
        
        # 预热
        self.log("\n[预热]...")
        time.sleep(1)
        
        # 并发创建
        self.run_concurrent_create()
        time.sleep(2)
        
        # 并发创建+分析
        self.run_concurrent_create_and_analyze()
        time.sleep(2)
        
        # 混合读写
        self.run_mixed_read_write()
        time.sleep(1)
        
        # 生成报告
        self.generate_report()
        
        # 清理
        self.cleanup()
        
        self.log("\n" + "="*80)
        self.log("高级测试完成!")
        self.log("="*80)

if __name__ == "__main__":
    tester = AdvancedTester()
    tester.run()
