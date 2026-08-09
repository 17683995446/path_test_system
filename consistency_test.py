#!/usr/bin/env python3
"""
极端并发数据一致性测试
测试在高并发读写下，文件锁是否能防止数据损坏
"""

import requests
import json
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

BASE_URL = "http://localhost:5174/api"

class ConsistencyTracker:
    def __init__(self):
        self.lock = threading.Lock()
        self.created_projects = []  # 我们创建的项目ID列表
        self.total_operations = 0
        self.success_operations = 0
        self.fail_operations = 0
        self.data_integrity_issues = []
    
    def record_operation(self, success: bool):
        with self.lock:
            self.total_operations += 1
            if success:
                self.success_operations += 1
            else:
                self.fail_operations += 1
    
    def add_created_project(self, project_id: str):
        with self.lock:
            self.created_projects.append(project_id)
    
    def add_integrity_issue(self, issue: str):
        with self.lock:
            self.data_integrity_issues.append(issue)

tracker = ConsistencyTracker()


def log(msg: str):
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {msg}")


def create_project(i: int):
    """创建项目"""
    try:
        name = f"ConsistencyTest_{i}_{random.randint(1000,9999)}"
        response = requests.post(f"{BASE_URL}/projects", json={
            "name": name,
            "path": "/workspace/path_test_system",
            "description": f"Test project {i}",
            "language": "Python"
        }, timeout=10)
        
        if response.status_code == 201:
            data = response.json()
            tracker.add_created_project(data.get("id"))
            tracker.record_operation(True)
            return True, data.get("id")
        else:
            tracker.record_operation(False)
            return False, None
    
    except Exception as e:
        tracker.record_operation(False)
        return False, None


def update_project(project_id: str):
    """随机更新项目"""
    try:
        updates = [
            {"name": f"Updated_{project_id}"},
            {"description": f"Updated at {datetime.now()}"},
            {"language": random.choice(["Python", "JavaScript", "TypeScript", "Go"])}
        ]
        payload = random.choice(updates)
        response = requests.put(f"{BASE_URL}/projects/{project_id}", json=payload, timeout=5)
        
        success = response.status_code in [200, 204]
        tracker.record_operation(success)
        return success
    
    except Exception as e:
        tracker.record_operation(False)
        return False


def get_projects():
    """获取项目并验证JSON有效性"""
    try:
        response = requests.get(f"{BASE_URL}/projects", timeout=10)
        
        if response.status_code == 200:
            try:
                # 验证返回的是有效的JSON并且有正确的格式
                data = response.json()
                if isinstance(data, list):
                    # 快速验证每个项目都有必要的字段
                    for item in data:
                        if not (isinstance(item, dict) and "id" in item and "name" in item and "path" in item):
                            tracker.add_integrity_issue(
                                f"Invalid project item format: {str(item)[:100]}"
                            )
                    tracker.record_operation(True)
                    return True, data
                else:
                    tracker.add_integrity_issue(f"Expected list, got {type(data)}")
                    tracker.record_operation(False)
                    return False, None
            except json.JSONDecodeError as e:
                tracker.add_integrity_issue(f"JSON decode error: {str(e)}")
                tracker.record_operation(False)
                return False, None
        else:
            tracker.record_operation(False)
            return False, None
    
    except Exception as e:
        tracker.record_operation(False)
        return False, None


def delete_project(project_id: str):
    """删除项目"""
    try:
        response = requests.delete(f"{BASE_URL}/projects/{project_id}", timeout=5)
        
        success = response.status_code in [200, 204] or response.status_code == 404  # 404也不算失败
        tracker.record_operation(success)
        return success
    
    except Exception as e:
        tracker.record_operation(False)
        return False


def verify_data_integrity():
    """直接检查磁盘上的数据文件是否完好"""
    try:
        projects_file = Path("/workspace/path_test_system/data/projects.json")
        if not projects_file.exists():
            return
        
        content = projects_file.read_text()
        try:
            data = json.loads(content)
            if not isinstance(data, list):
                tracker.add_integrity_issue("projects.json root should be a list")
                return
            
            # 验证每个项目的完整性
            for i, item in enumerate(data):
                if not isinstance(item, dict):
                    tracker.add_integrity_issue(f"projects.json[{i}] should be a dict")
                    continue
                
                required_fields = ["id", "name", "path", "status"]
                for field in required_fields:
                    if field not in item:
                        tracker.add_integrity_issue(f"projects.json[{i}] missing {field}")
        
        except json.JSONDecodeError as e:
            tracker.add_integrity_issue(f"projects.json parse error: {str(e)}")
            
    except Exception as e:
        tracker.add_integrity_issue(f"Failed to check data integrity: {str(e)}")


def consistency_test_worker(worker_id: int, iterations: int):
    """工作线程"""
    local_project_ids = []
    
    for i in range(iterations):
        # 随机选择操作
        op_type = random.choice([
            "create", "update", "get", "delete", "verify_integrity"
        ])
        
        if op_type == "create":
            success, project_id = create_project(worker_id * 1000 + i)
            if success and project_id:
                local_project_ids.append(project_id)
        
        elif op_type == "update":
            if local_project_ids:
                update_project(random.choice(local_project_ids))
        
        elif op_type == "get":
            get_projects()
        
        elif op_type == "delete":
            if local_project_ids:
                project_id = random.choice(local_project_ids)
                if delete_project(project_id):
                    try:
                        local_project_ids.remove(project_id)
                    except:
                        pass
        
        elif op_type == "verify_integrity":
            verify_data_integrity()
        
        # 随机短延迟，增加混乱度
        time.sleep(random.uniform(0.001, 0.05))


def run_consistency_test():
    """运行一致性测试"""
    print("=" * 100)
    print("极端数据一致性测试开始")
    print("=" * 100)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    num_workers = 30  # 更多的并发线程！
    iterations_per_worker = 50  # 更多的迭代！
    total_operations = num_workers * iterations_per_worker
    log(f"启动 {num_workers} 个并发工作线程，每个 {iterations_per_worker} 次迭代")
    log(f"总计 {total_operations} 次操作")
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(consistency_test_worker, i, iterations_per_worker) 
                  for i in range(num_workers)]
        
        # 定期打印进度
        while True:
            all_done = True
            for f in futures:
                if not f.done():
                    all_done = False
                    break
            
            if all_done:
                break
            
            with tracker.lock:
                current_stats = (
                    tracker.total_operations,
                    tracker.success_operations,
                    tracker.fail_operations
                )
            
            success_rate = current_stats[1]/current_stats[0]*100 if current_stats[0]>0 else 0
            log(f"进度: {current_stats[0]}/{total_operations}  "
                f"成功: {current_stats[1]}  "
                f"失败: {current_stats[2]}  "
                f"成功率: {success_rate:.1f}%  "
                f"完整性问题: {len(tracker.data_integrity_issues)}")
            
            time.sleep(2)
    
    elapsed = time.time() - start_time
    
    # 最终统计
    print("\n" + "=" * 100)
    print("测试完成！")
    print("=" * 100)
    print(f"总操作数: {tracker.total_operations}")
    print(f"成功: {tracker.success_operations}")
    print(f"失败: {tracker.fail_operations}")
    print(f"成功率: {tracker.success_operations/tracker.total_operations*100:.2f}%")
    print(f"吞吐量: {tracker.total_operations/elapsed:.1f} req/s")
    print(f"持续时间: {elapsed:.2f}s")
    
    if tracker.data_integrity_issues:
        print(f"\n发现 {len(tracker.data_integrity_issues)} 个数据完整性问题！")
        for i, issue in enumerate(tracker.data_integrity_issues[:10], 1):
            print(f"  {i}. {issue}")
        if len(tracker.data_integrity_issues) > 10:
            print(f"  ...还有 {len(tracker.data_integrity_issues) - 10} 个问题")
    else:
        print("\n✅ 没有发现任何数据完整性问题！")
    
    # 最后再次验证数据完整性
    print("\n最后验证数据文件...")
    verify_data_integrity()
    if not tracker.data_integrity_issues:
        print("✅ 最终数据一致性检查通过！")
    
    # 清理
    print("\n清理测试数据...")
    cleanup_count = 0
    for project_id in tracker.created_projects:
        try:
            requests.delete(f"{BASE_URL}/projects/{project_id}", timeout=2)
            cleanup_count += 1
        except:
            pass
    print(f"清理了 {cleanup_count} 个项目")


if __name__ == "__main__":
    run_consistency_test()
