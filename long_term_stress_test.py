#!/usr/bin/env python3
"""
长期持续大规模压力测试脚本
- 长时间运行（可选时长）
- 更多并发线程
- 更多混合操作
- 详细监控和报告
- 数据一致性周期性检查
"""

import requests
import json
import time
import random
import threading
import os
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

BASE_URL = "http://localhost:5174/api"

# 全局统计和锁
stats = {
    'total_requests': 0,
    'success_requests': 0,
    'failed_requests': 0,
    'warnings': 0,
    'data_integrity_issues': 0,
    'start_time': None,
}
stats_lock = threading.Lock()
stop_event = threading.Event()
shared_project_ids = []
shared_lock = threading.Lock()


def log(msg: str):
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {msg}")


def update_stats(success: bool, warning: bool = False):
    with stats_lock:
        stats['total_requests'] += 1
        if success:
            stats['success_requests'] += 1
        else:
            stats['failed_requests'] += 1
        if warning:
            stats['warnings'] += 1


def check_data_integrity():
    """检查数据文件的完整性"""
    try:
        projects_file = Path("/workspace/path_test_system/data/projects.json")
        if not projects_file.exists():
            return True

        content = projects_file.read_text()
        data = json.loads(content)
        
        if not isinstance(data, list):
            return False
            
        for item in data:
            if not isinstance(item, dict):
                return False
            if not all(key in item for key in ['id', 'name', 'path', 'status']):
                return False
                
        return True
    except json.JSONDecodeError:
        return False
    except Exception:
        return False


def chaos_worker(worker_id: int):
    """单个工作线程执行的操作"""
    while not stop_event.is_set():
        try:
            action = random.choices(
                ["health", "get_projects", "create_project", "update_project", 
                 "delete_project", "analyze", "get_issues", "get_tests",
                 "browse_file", "read_file", "change_settings"],
                weights=[10, 15, 20, 15, 12, 8, 10, 5, 3, 2, 2]
            )[0]

            if action == "health":
                response = requests.get(f"{BASE_URL}/health", timeout=10)
                update_stats(response.status_code == 200)

            elif action == "get_projects":
                response = requests.get(f"{BASE_URL}/projects", timeout=10)
                update_stats(response.status_code == 200)

            elif action == "create_project":
                name = f"LT-Test-{worker_id}-{int(time.time()*1000000)}"
                response = requests.post(f"{BASE_URL}/projects", json={
                    "name": name,
                    "path": "/workspace/path_test_system",
                    "description": f"Long term test project by worker {worker_id}",
                    "language": random.choice(["Python", "JavaScript", "TypeScript", "Go", "Rust"])
                }, timeout=10)
                
                success = response.status_code == 201
                update_stats(success)
                
                if success:
                    try:
                        data = response.json()
                        if 'id' in data:
                            with shared_lock:
                                if len(shared_project_ids) < 100:  # 限制共享ID的数量
                                    shared_project_ids.append(data['id'])
                    except:
                        pass

            elif action == "update_project":
                project_id = None
                with shared_lock:
                    if shared_project_ids:
                        project_id = random.choice(shared_project_ids)
                
                if project_id:
                    updates = [
                        {"name": f"Updated-{random.randint(1,1000)}"},
                        {"description": f"Updated at {datetime.now()}"},
                        {"language": random.choice(["Python", "JS", "TS", "Go", "Rust"])}
                    ]
                    payload = random.choice(updates)
                    response = requests.put(f"{BASE_URL}/projects/{project_id}", json=payload, timeout=10)
                    update_stats(response.status_code in [200, 204])

            elif action == "delete_project":
                project_id = None
                with shared_lock:
                    if shared_project_ids:
                        project_id = shared_project_ids.pop(random.randint(0, len(shared_project_ids)-1))
                
                if project_id:
                    response = requests.delete(f"{BASE_URL}/projects/{project_id}", timeout=10)
                    update_stats(response.status_code in [200, 204, 404])

            elif action == "analyze":
                response = requests.post(f"{BASE_URL}/analyze", json={
                    "project_id": "1"  # 使用固定项目ID
                }, timeout=30)
                update_stats(response.status_code in [200, 202, 400])

            elif action == "get_issues":
                response = requests.get(f"{BASE_URL}/issues", timeout=10)
                update_stats(response.status_code == 200)

            elif action == "get_tests":
                response = requests.get(f"{BASE_URL}/tests", timeout=10)
                update_stats(response.status_code == 200)

            elif action == "browse_file":
                response = requests.get(f"{BASE_URL}/files/browse", params={
                    "path": "/workspace/path_test_system"
                }, timeout=10)
                update_stats(response.status_code in [200, 404, 403])

            elif action == "read_file":
                response = requests.get(f"{BASE_URL}/files/read", params={
                    "path": "/workspace/path_test_system/api_server.py"
                }, timeout=10)
                update_stats(response.status_code in [200, 404, 403])

            elif action == "change_settings":
                response = requests.post(f"{BASE_URL}/settings", json={
                    "theme": random.choice(["dark", "light"]),
                    "autoSave": random.choice([True, False])
                }, timeout=10)
                update_stats(response.status_code in [200, 204])

        except Exception as e:
            update_stats(False, warning=True)

        # 随机短延迟，增加混乱度
        time.sleep(random.uniform(0.005, 0.1))


def periodic_integrity_check():
    """周期性检查数据完整性"""
    last_check = time.time()
    check_interval = 60  # 每60秒检查一次
    
    while not stop_event.is_set():
        if time.time() - last_check >= check_interval:
            log("🔍 执行数据完整性检查...")
            if not check_data_integrity():
                with stats_lock:
                    stats['data_integrity_issues'] += 1
                log("⚠️  检测到数据完整性问题！")
            else:
                log("✅ 数据完整性检查通过")
            last_check = time.time()
        time.sleep(5)


def stats_reporter():
    """定期报告统计信息"""
    last_report = time.time()
    report_interval = 30  # 每30秒报告一次
    
    while not stop_event.is_set():
        if time.time() - last_report >= report_interval:
            with stats_lock:
                elapsed = time.time() - stats['start_time']
                success_rate = (stats['success_requests'] / stats['total_requests'] * 100) if stats['total_requests'] > 0 else 0
            
            log("=" * 80)
            log(f"📊 统计报告:")
            log(f"   运行时间: {elapsed:.1f}s")
            log(f"   总请求: {stats['total_requests']}")
            log(f"   成功: {stats['success_requests']}")
            log(f"   失败: {stats['failed_requests']}")
            log(f"   成功率: {success_rate:.2f}%")
            log(f"   警告: {stats['warnings']}")
            log(f"   数据完整性问题: {stats['data_integrity_issues']}")
            log("=" * 80)
            
            last_report = time.time()
        time.sleep(1)


def run_long_term_test(duration_minutes: int = 30, num_workers: int = 30):
    """
    运行长期测试
    
    参数:
        duration_minutes: 测试持续分钟数（默认30分钟）
        num_workers: 并发工作线程数（默认30个）
    """
    log("=" * 100)
    log("🚀 长期持续大规模压力测试开始")
    log("=" * 100)
    log(f"📅 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"⏱️  持续时间: {duration_minutes} 分钟")
    log(f"🔧 并发线程: {num_workers} 个")
    print()
    
    # 初始化统计
    with stats_lock:
        stats['start_time'] = time.time()
    
    # 启动监控线程
    integrity_thread = threading.Thread(target=periodic_integrity_check, daemon=True)
    integrity_thread.start()
    
    reporter_thread = threading.Thread(target=stats_reporter, daemon=True)
    reporter_thread.start()
    
    # 启动工作线程
    log(f"启动 {num_workers} 个工作线程...")
    
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(chaos_worker, i) for i in range(num_workers)]
        
        # 等待指定的持续时间
        log(f"测试运行中... 等待 {duration_minutes} 分钟")
        time.sleep(duration_minutes * 60)
        
        # 通知所有线程停止
        log("⏰ 时间到！正在停止所有工作线程...")
        stop_event.set()
        
        # 等待线程完成
        for f in futures:
            f.result()
    
    # 最终统计
    elapsed = time.time() - stats['start_time']
    success_rate = (stats['success_requests'] / stats['total_requests'] * 100) if stats['total_requests'] > 0 else 0
    throughput = stats['total_requests'] / elapsed if elapsed > 0 else 0
    
    print()
    log("=" * 100)
    log("🎉 长期持续大规模压力测试完成！")
    log("=" * 100)
    log(f"📅 结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"⏱️  总运行时间: {elapsed:.2f}s ({elapsed/60:.2f}分钟)")
    log("📊 最终统计:")
    log(f"   总请求数: {stats['total_requests']}")
    log(f"   成功请求: {stats['success_requests']}")
    log(f"   失败请求: {stats['failed_requests']}")
    log(f"   成功率: {success_rate:.2f}%")
    log(f"   吞吐量: {throughput:.1f} req/s")
    log(f"   警告数: {stats['warnings']}")
    log(f"   数据完整性问题: {stats['data_integrity_issues']}")
    
    if stats['data_integrity_issues'] == 0:
        log("✅ 数据完整性检查完美通过！")
    else:
        log("⚠️  发现数据完整性问题！")
    
    # 清理
    log("\n🔧 正在清理测试数据...")
    cleanup_count = 0
    with shared_lock:
        for project_id in shared_project_ids:
            try:
                requests.delete(f"{BASE_URL}/projects/{project_id}", timeout=2)
                cleanup_count += 1
            except:
                pass
    log(f"✅ 清理了 {cleanup_count} 个测试项目")
    
    return stats['data_integrity_issues'] == 0


if __name__ == "__main__":
    import sys
    duration = 30  # 默认30分钟
    num_workers = 30  # 默认30个线程
    if len(sys.argv) > 1:
        try:
            duration = int(sys.argv[1])
        except ValueError:
            pass
    if len(sys.argv) > 2:
        try:
            num_workers = int(sys.argv[2])
        except ValueError:
            pass
    
    success = run_long_term_test(duration_minutes=duration, num_workers=num_workers)
    exit(0 if success else 1)
