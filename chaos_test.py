#!/usr/bin/env python3
"""
极端混乱测试场景 - 模拟真实世界中的混乱情况
- 高并发
- 混合读写操作
- 随机错误注入
- 资源竞争
- 长时间运行
"""

import requests
import json
import time
import random
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import List, Dict, Any, Optional

BASE_URL = "http://localhost:5174/api"

# 全局状态跟踪
class ChaosTracker:
    def __init__(self):
        self.lock = threading.Lock()
        self.total_requests = 0
        self.successful = 0
        self.failed = 0
        self.errors = []
        self.created_entities = []
        self.warning_count = 0
    
    def record_request(self, success: bool, error: Optional[str] = None, entity_type: Optional[str] = None, entity_id: Optional[str] = None):
        with self.lock:
            self.total_requests += 1
            if success:
                self.successful += 1
                if entity_type and entity_id:
                    self.created_entities.append((entity_type, entity_id))
            else:
                self.failed += 1
                if error:
                    self.errors.append(error)
                    if len(self.errors) > 50:  # 只保留最近50个错误
                        self.errors.pop(0)
    
    def record_warning(self, msg: str):
        with self.lock:
            self.warning_count += 1
            if len(self.errors) < 100:
                self.errors.append(f"WARN: {msg}")

tracker = ChaosTracker()

def log(msg: str):
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {msg}")

# 1. 健康检查请求
def chaos_health_check():
    """健康检查，偶尔失败"""
    try:
        # 10%的概率不等待，模拟超时
        timeout = random.choice([0.1, 0.5, 1, 5, 10])
        response = requests.get(f"{BASE_URL}/health", timeout=timeout)
        success = response.status_code == 200
        tracker.record_request(success, None if success else f"Health: {response.status_code}")
        return success
    except Exception as e:
        tracker.record_request(False, f"Health exc: {str(e)}")
        return False

# 2. 获取项目列表
def chaos_get_projects():
    """随机获取项目列表"""
    try:
        timeout = random.choice([1, 3, 5])
        response = requests.get(f"{BASE_URL}/projects", timeout=timeout)
        success = response.status_code == 200
        tracker.record_request(success, None if success else f"GetProjects: {response.status_code}")
        if success:
            return response.json()
        return []
    except Exception as e:
        tracker.record_request(False, f"GetProjects exc: {str(e)}")
        return []

# 3. 创建项目 - 包含各种边缘情况
def chaos_create_project():
    """创建项目，包含各种混乱输入"""
    # 5%的概率发送空数据
    if random.random() < 0.05:
        try:
            response = requests.post(f"{BASE_URL}/projects", json={}, timeout=10)
            tracker.record_request(response.status_code == 201, f"Create empty: {response.status_code}")
            return None
        except Exception as e:
            tracker.record_request(False, f"Create empty exc: {str(e)}")
            return None
    
    # 10%的概率发送非常奇怪的数据
    if random.random() < 0.1:
        payloads = [
            {"name": "", "path": "/workspace"},
            {"name": "x" * 1000, "path": "/workspace"},
            {"name": "Test", "path": "/nonexistent/path"},
            {"name": "Test", "path": "/workspace/../../etc/passwd"},
            {"name": None, "path": None},
        ]
        payload = random.choice(payloads)
    else:
        # 正常数据
        project_name = f"Chaos_{datetime.now().strftime('%H%M%S_%f')}_{random.randint(1000, 9999)}"
        payload = {
            "name": project_name,
            "path": "/workspace/path_test_system",
            "description": "This is a chaos test project with some special chars: <script>alert(1)</script> & ' \"",
            "language": random.choice(["Python", "JavaScript", "TypeScript", "Go"]),
        }
    
    try:
        response = requests.post(f"{BASE_URL}/projects", json=payload, timeout=10)
        success = response.status_code == 201
        tracker.record_request(success, None if success else f"CreateProject: {response.status_code}")
        
        if success:
            data = response.json()
            project_id = data.get("id")
            if project_id:
                tracker.record_request(True, entity_type="project", entity_id=project_id)
                return project_id
        return None
    except Exception as e:
        tracker.record_request(False, f"CreateProject exc: {str(e)}")
        return None

# 4. 分析项目
def chaos_analyze_project(project_id: str):
    """分析项目"""
    try:
        payload = {"projectId": project_id}
        timeout = random.choice([5, 10, 30, 60])  # 随机超时时间
        response = requests.post(f"{BASE_URL}/analyze", json=payload, timeout=timeout)
        success = response.status_code == 200
        
        # 409也是预期的（项目已在分析中）
        if response.status_code == 409:
            tracker.record_warning(f"Project {project_id} already analyzing")
            tracker.record_request(True)  # 409不是失败
        else:
            tracker.record_request(success, None if success else f"Analyze: {response.status_code}")
        
        return success
    except Exception as e:
        tracker.record_request(False, f"Analyze exc: {str(e)}")
        return False

# 5. 更新项目
def chaos_update_project(project_id: str):
    """随机更新项目"""
    try:
        updates = [
            {"name": f"Updated_{random.randint(1000, 9999)}"},
            {"description": "Updated chaos description"},
            {"language": random.choice(["Python", "Go", "Rust"])},
            {"name": None, "description": None},
        ]
        
        payload = random.choice(updates)
        response = requests.put(f"{BASE_URL}/projects/{project_id}", json=payload, timeout=5)
        success = response.status_code in [200, 204]
        
        tracker.record_request(success, None if success else f"Update: {response.status_code}")
        return success
    except Exception as e:
        tracker.record_request(False, f"Update exc: {str(e)}")
        return False

# 6. 删除项目
def chaos_delete_project(project_id: str):
    """删除项目"""
    try:
        response = requests.delete(f"{BASE_URL}/projects/{project_id}", timeout=5)
        success = response.status_code in [200, 204]
        
        # 404也是预期的（项目可能已被删除）
        if response.status_code == 404:
            tracker.record_warning(f"Project {project_id} already deleted")
            tracker.record_request(True)
        else:
            tracker.record_request(success, None if success else f"Delete: {response.status_code}")
        
        return success
    except Exception as e:
        tracker.record_request(False, f"Delete exc: {str(e)}")
        return False

# 7. 获取问题
def chaos_get_issues():
    """获取问题列表"""
    try:
        response = requests.get(f"{BASE_URL}/issues", timeout=10)
        success = response.status_code == 200
        tracker.record_request(success, None if success else f"Issues: {response.status_code}")
        return success
    except Exception as e:
        tracker.record_request(False, f"Issues exc: {str(e)}")
        return False

# 8. 文件操作
def chaos_file_operation():
    """随机文件浏览或读取"""
    try:
        operation = random.choice(["browse", "read"])
        
        if operation == "browse":
            paths = [
                "/workspace/path_test_system",
                "/workspace/path_test_system/data",
                "/workspace",
                "/",
                "/nonexistent",
            ]
            path = random.choice(paths)
            response = requests.post(f"{BASE_URL}/files/browse", json={"path": path}, timeout=5)
            success = response.status_code == 200
            tracker.record_request(success, None if success else f"Browse: {response.status_code}")
        
        else:
            files = [
                "/workspace/path_test_system/api_server.py",
                "/workspace/path_test_system/test_project.py",
                "/workspace/path_test_system/nonexistent.py",
                "/etc/passwd",
            ]
            file_path = random.choice(files)
            response = requests.post(f"{BASE_URL}/files/read", json={"path": file_path}, timeout=10)
            success = response.status_code == 200
            tracker.record_request(success, None if success else f"Read: {response.status_code}")
        
        return success
    except Exception as e:
        tracker.record_request(False, f"File op exc: {str(e)}")
        return False

# 9. 设置操作
def chaos_settings_operation():
    """修改设置"""
    try:
        settings = {
            "theme": random.choice(["dark", "light", "random", None]),
            "autoSave": random.choice([True, False, "yes", 1, 0]),
            "maxFileSize": random.randint(-100, 1000),
            "analysisDepth": random.randint(-10, 200),
        }
        
        response = requests.post(f"{BASE_URL}/settings", json=settings, timeout=5)
        success = response.status_code == 200
        tracker.record_request(success, None if success else f"Settings: {response.status_code}")
        return success
    except Exception as e:
        tracker.record_request(False, f"Settings exc: {str(e)}")
        return False

# 共享项目ID池
shared_project_ids = []
project_ids_lock = threading.Lock()

def chaos_worker():
    """单个混乱工作线程"""
    worker_id = threading.current_thread().name
    
    # 每个线程的局部项目ID缓存
    local_projects = []
    
    for _ in range(100):  # 每个线程做100个操作
        # 随机选择操作
        action = random.choices(
            ["health", "get", "create", "analyze", "update", "delete", "issues", "file", "settings"],
            weights=[5, 20, 15, 10, 15, 8, 15, 7, 5]
        )[0]
        
        try:
            if action == "health":
                chaos_health_check()
            
            elif action == "get":
                chaos_get_projects()
            
            elif action == "create":
                project_id = chaos_create_project()
                if project_id:
                    local_projects.append(project_id)
                    # 也添加到共享池
                    with project_ids_lock:
                        shared_project_ids.append(project_id)
                        if len(shared_project_ids) > 100:  # 限制池大小
                            shared_project_ids.pop(0)
            
            elif action in ["analyze", "update", "delete"]:
                # 获取一个项目ID - 优先使用本地，然后共享
                target_id = None
                if local_projects:
                    target_id = random.choice(local_projects)
                else:
                    with project_ids_lock:
                        if shared_project_ids:
                            target_id = random.choice(shared_project_ids)
                
                if target_id:
                    if action == "analyze":
                        chaos_analyze_project(target_id)
                    elif action == "update":
                        chaos_update_project(target_id)
                    elif action == "delete":
                        chaos_delete_project(target_id)
                        # 从本地缓存移除
                        if target_id in local_projects:
                            local_projects.remove(target_id)
            
            elif action == "issues":
                chaos_get_issues()
            
            elif action == "file":
                chaos_file_operation()
            
            elif action == "settings":
                chaos_settings_operation()
        
        except Exception as e:
            tracker.record_request(False, f"Unexpected in {worker_id}: {str(e)}")
        
        # 随机短延迟 - 增加混乱度
        time.sleep(random.uniform(0.001, 0.1))

def print_progress():
    """定期打印进度"""
    while True:
        with tracker.lock:
            success_rate = (tracker.successful / tracker.total_requests * 100) if tracker.total_requests > 0 else 0
            log(f"Stats: {tracker.total_requests} requests, {tracker.successful} OK, {tracker.failed} FAIL "
                f"({success_rate:.1f}% success), {tracker.warning_count} warnings, {len(shared_project_ids)} shared IDs")
        
        time.sleep(2)

def run_chaos_test():
    """运行混乱测试"""
    print("=" * 100)
    print("极端混乱并发测试开始")
    print("=" * 100)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    num_threads = 20
    log(f"启动 {num_threads} 个并发工作线程...")
    
    # 启动进度打印线程
    progress_thread = threading.Thread(target=print_progress, daemon=True)
    progress_thread.start()
    
    # 先创建一些种子项目
    log("创建种子项目...")
    for _ in range(10):
        project_id = chaos_create_project()
        if project_id:
            shared_project_ids.append(project_id)
            time.sleep(0.1)
    
    log(f"种子项目数: {len(shared_project_ids)}")
    
    # 运行混乱测试
    start_time = time.time()
    duration = 60  # 运行60秒
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(chaos_worker) for _ in range(num_threads)]
        
        log(f"开始混乱测试，持续 {duration} 秒...")
        
        # 等待指定时间
        time.sleep(duration)
        
        log("\n时间到！等待线程完成...")
        # 取消所有线程（虽然不是真正取消，但让它们知道应该结束）
    
    elapsed = time.time() - start_time
    
    # 打印最终报告
    print("\n" + "=" * 100)
    print("极端混乱并发测试完成")
    print("=" * 100)
    
    with tracker.lock:
        total = tracker.total_requests
        success = tracker.successful
        failed = tracker.failed
        success_rate = (success / total * 100) if total > 0 else 0
        
        print(f"\n测试统计:")
        print(f"  总请求数: {total}")
        print(f"  成功: {success}")
        print(f"  失败: {failed}")
        print(f"  成功率: {success_rate:.2f}%")
        print(f"  警告数: {tracker.warning_count}")
        print(f"  持续时间: {elapsed:.2f}秒")
        print(f"  吞吐量: {total / elapsed:.1f} req/s")
        
        if tracker.errors:
            print(f"\n错误样本 (最近20个):")
            for i, err in enumerate(tracker.errors[-20:]):
                print(f"  {i+1}. {err}")
        
        if failed > 0:
            print(f"\n⚠️  发现 {failed} 个失败请求")
        else:
            print(f"\n🎉 0个失败！系统在混乱场景下表现良好！")
    
    # 清理
    print("\n清理测试数据...")
    cleanup_count = 0
    for entity_type, entity_id in tracker.created_entities:
        if entity_type == "project":
            try:
                requests.delete(f"{BASE_URL}/projects/{entity_id}", timeout=2)
                cleanup_count += 1
            except:
                pass
    print(f"  清理了 {cleanup_count} 个项目")

if __name__ == "__main__":
    run_chaos_test()
