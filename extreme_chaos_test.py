#!/usr/bin/env python3
"""
极度混乱并发测试 - 验证详细日志功能
包含最极端的并发场景
"""

import requests
import json
import time
import random
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://localhost:5174/api"

stop_event = threading.Event()
shared_data = {
    'project_ids': [],
    'created_count': 0,
    'deleted_count': 0,
    'lock': threading.Lock()
}


def log(msg: str):
    timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
    print(f"[{timestamp}] {msg}")


def chaos_worker(worker_id: int):
    """极度混乱的工作线程"""
    while not stop_event.is_set():
        try:
            # 更极端的随机操作
            action = random.choices(
                ["health", "get_all", "create", "create_bulk", "update", "delete", 
                 "update_delete_race", "concurrent_create_same", "get_nonexistent",
                 "update_nonexistent", "delete_nonexistent", "rapid_fire"],
                weights=[15, 10, 25, 5, 20, 15, 10, 5, 5, 5, 5, 10]
            )[0]

            if action == "health":
                response = requests.get(f"{BASE_URL}/health", timeout=5)
                log(f"Worker-{worker_id}: Health check - {response.status_code}")

            elif action == "get_all":
                response = requests.get(f"{BASE_URL}/projects", timeout=10)
                if response.status_code == 200:
                    try:
                        data = response.json()
                        log(f"Worker-{worker_id}: Got {len(data)} projects")
                    except:
                        log(f"Worker-{worker_id}: Failed to parse projects")

            elif action == "create":
                name = f"Chaos-{worker_id}-{int(time.time()*1000000)}"
                response = requests.post(f"{BASE_URL}/projects", json={
                    "name": name,
                    "path": "/workspace/path_test_system",
                    "description": f"Chaos test {worker_id}"
                }, timeout=10)
                
                if response.status_code == 201:
                    try:
                        data = response.json()
                        pid = data.get('id')
                        with shared_data['lock']:
                            shared_data['project_ids'].append(pid)
                            shared_data['created_count'] += 1
                        log(f"Worker-{worker_id}: Created {pid}")
                    except:
                        log(f"Worker-{worker_id}: Create failed to parse")
                else:
                    log(f"Worker-{worker_id}: Create failed {response.status_code}")

            elif action == "create_bulk":
                # 快速批量创建
                for i in range(5):
                    name = f"Bulk-{worker_id}-{i}-{int(time.time())}"
                    response = requests.post(f"{BASE_URL}/projects", json={
                        "name": name,
                        "path": "/workspace/path_test_system"
                    }, timeout=5)
                    if response.status_code == 201:
                        try:
                            data = response.json()
                            with shared_data['lock']:
                                shared_data['project_ids'].append(data.get('id'))
                                shared_data['created_count'] += 1
                        except:
                            pass
                log(f"Worker-{worker_id}: Bulk created 5 projects")

            elif action == "update":
                with shared_data['lock']:
                    if shared_data['project_ids']:
                        pid = random.choice(shared_data['project_ids'])
                    else:
                        pid = None
                
                if pid:
                    response = requests.put(f"{BASE_URL}/projects/{pid}", json={
                        "name": f"Updated-{worker_id}"
                    }, timeout=5)
                    log(f"Worker-{worker_id}: Update {pid} - {response.status_code}")

            elif action == "delete":
                with shared_data['lock']:
                    if shared_data['project_ids']:
                        pid = shared_data['project_ids'].pop(0)
                    else:
                        pid = None
                
                if pid:
                    response = requests.delete(f"{BASE_URL}/projects/{pid}", timeout=5)
                    if response.status_code in [200, 204, 404]:
                        with shared_data['lock']:
                            shared_data['deleted_count'] += 1
                    log(f"Worker-{worker_id}: Delete {pid} - {response.status_code}")

            elif action == "update_delete_race":
                # 竞争条件：同时更新和删除同一个项目
                name = f"Race-{worker_id}-{int(time.time())}"
                response = requests.post(f"{BASE_URL}/projects", json={
                    "name": name,
                    "path": "/workspace/path_test_system"
                }, timeout=5)
                
                if response.status_code == 201:
                    try:
                        pid = response.json().get('id')
                        
                        # 同时创建更新和删除线程
                        def update_it():
                            requests.put(f"{BASE_URL}/projects/{pid}", json={"name": "Updated"}, timeout=5)
                        
                        def delete_it():
                            requests.delete(f"{BASE_URL}/projects/{pid}", timeout=5)
                        
                        t1 = threading.Thread(target=update_it)
                        t2 = threading.Thread(target=delete_it)
                        t1.start()
                        t2.start()
                        t1.join()
                        t2.join()
                        log(f"Worker-{worker_id}: Race condition test on {pid}")
                    except:
                        pass

            elif action == "concurrent_create_same":
                # 多个线程同时创建同名项目
                name = f"SameName-{worker_id}"
                
                # 创建5个同名项目
                for i in range(5):
                    response = requests.post(f"{BASE_URL}/projects", json={
                        "name": name,
                        "path": "/workspace/path_test_system"
                    }, timeout=5)
                
                log(f"Worker-{worker_id}: Created 5 same-name projects")

            elif action == "get_nonexistent":
                fake_id = f"nonexistent-{worker_id}-{random.randint(1,10000)}"
                response = requests.get(f"{BASE_URL}/projects/{fake_id}", timeout=5)
                log(f"Worker-{worker_id}: Get nonexistent {fake_id} - {response.status_code}")

            elif action == "update_nonexistent":
                fake_id = f"nonexistent-{worker_id}-{random.randint(1,10000)}"
                response = requests.put(f"{BASE_URL}/projects/{fake_id}", json={"name": "test"}, timeout=5)
                log(f"Worker-{worker_id}: Update nonexistent - {response.status_code}")

            elif action == "delete_nonexistent":
                fake_id = f"nonexistent-{worker_id}-{random.randint(1,10000)}"
                response = requests.delete(f"{BASE_URL}/projects/{fake_id}", timeout=5)
                log(f"Worker-{worker_id}: Delete nonexistent - {response.status_code}")

            elif action == "rapid_fire":
                # 快速连续请求
                for i in range(20):
                    response = requests.get(f"{BASE_URL}/health", timeout=2)
                log(f"Worker-{worker_id}: Rapid fire 20 requests")

        except Exception as e:
            log(f"Worker-{worker_id}: Exception {type(e).__name__}: {e}")

        # 更短的延迟，增加混乱度
        time.sleep(random.uniform(0.001, 0.05))


def run_extreme_chaos_test(duration_minutes: int = 30, num_workers: int = 50):
    """运行极度混乱测试"""
    log("=" * 100)
    log("🚀 极度混乱并发测试开始")
    log("=" * 100)
    log(f"📅 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"⏱️  持续时间: {duration_minutes} 分钟")
    log(f"🔧 并发线程: {num_workers} 个")
    log(f"🎯 测试目标: 验证详细日志功能，发现潜在问题")
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(chaos_worker, i) for i in range(num_workers)]
        
        log(f"测试运行中...")
        time.sleep(duration_minutes * 60)
        
        log("时间到！正在停止...")
        stop_event.set()
        
        for f in futures:
            f.result()
    
    elapsed = time.time() - start_time
    
    print()
    log("=" * 100)
    log("🎉 测试完成")
    log("=" * 100)
    log(f"⏱️  持续时间: {elapsed:.2f}s ({elapsed/60:.2f}分钟)")
    log(f"✅ 创建项目数: {shared_data['created_count']}")
    log(f"🗑️  删除项目数: {shared_data['deleted_count']}")
    log(f"📊 当前项目ID数: {len(shared_data['project_ids'])}")
    log()
    log("📝 请检查上面的日志输出，验证：")
    log("   1. 所有操作是否都有日志记录")
    log("   2. 日志顺序是否正确")
    log("   3. 是否有任何异常或错误")
    log("   4. 文件锁是否正常工作")
    log("   5. 数据完整性是否保持")
    log()
    
    # 清理
    log("🧹 开始清理测试数据...")
    cleanup_count = 0
    for pid in shared_data['project_ids']:
        try:
            requests.delete(f"{BASE_URL}/projects/{pid}", timeout=2)
            cleanup_count += 1
        except:
            pass
    log(f"✅ 清理完成，删除了 {cleanup_count} 个项目")


if __name__ == "__main__":
    import sys
    duration = 30
    num_workers = 50
    
    if len(sys.argv) > 1:
        try:
            duration = int(sys.argv[1])
        except:
            pass
    if len(sys.argv) > 2:
        try:
            num_workers = int(sys.argv[2])
        except:
            pass
    
    run_extreme_chaos_test(duration_minutes=duration, num_workers=num_workers)
