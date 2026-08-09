#!/usr/bin/env python3
"""
🚀 快速验证测试 - 2分钟版本
用于验证测试系统是否正常工作
"""

import requests
import json
import time
import random
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

BASE_URL = "http://localhost:5174/api"

class QuickTestMonitor:
    def __init__(self):
        self.lock = threading.Lock()
        self.total = 0
        self.success = 0
        self.failed = 0
        self.endpoints = defaultdict(lambda: {'t':0,'s':0,'f':0})
        self.errors = []
        self.warnings = []
    
    def log(self, msg, l="INFO"):
        ts = datetime.now().strftime('%H:%M:%S')
        print(f"[{ts}] [{l}] {msg}")
        if l == "ERROR": self.errors.append(msg)
        if l == "WARNING": self.warnings.append(msg)
    
    def record(self, ep, ok, sc=None):
        with self.lock:
            self.total +=1
            if ok: self.success +=1; self.endpoints[ep]['s'] +=1
            else: self.failed +=1; self.endpoints[ep]['f'] +=1
            self.endpoints[ep]['t'] +=1

monitor = QuickTestMonitor()
stop = threading.Event()
created = []
created_lock = threading.Lock()

def worker(worker_id):
    name = f"W{worker_id:02d}"
    monitor.log(f"🏃 {name} 启动")
    
    while not stop.is_set():
        try:
            op = random.choice(['health','get','create','update','delete','issues','browse','boundary'])
            
            if op == 'health':
                r = requests.get(f"{BASE_URL}/health", timeout=5)
                monitor.record('health', r.status_code ==200)
            
            elif op == 'get':
                r = requests.get(f"{BASE_URL}/projects", timeout=5)
                monitor.record('get_projects', r.status_code ==200)
            
            elif op == 'create':
                data = {"name":f"{name}-{random.randint(1,10000)}", "path":"/workspace/path_test_system"}
                r = requests.post(f"{BASE_URL}/projects", json=data, timeout=10)
                ok = r.status_code ==201
                monitor.record('create_project', ok)
                if ok:
                    try:
                        pid = r.json().get('id')
                        with created_lock:
                            created.append(pid)
                    except: pass
            
            elif op == 'update':
                with created_lock:
                    if not created: continue
                    pid = random.choice(created)
                r = requests.put(f"{BASE_URL}/projects/{pid}", json={"name":"Updated"}, timeout=10)
                monitor.record('update_project', r.status_code in [200,204,404])
            
            elif op == 'delete':
                with created_lock:
                    if not created: continue
                    pid = created.pop(0)
                r = requests.delete(f"{BASE_URL}/projects/{pid}", timeout=10)
                monitor.record('delete_project', r.status_code in [200,204,404])
            
            elif op == 'issues':
                r = requests.get(f"{BASE_URL}/issues", timeout=5)
                monitor.record('get_issues', r.status_code ==200)
            
            elif op == 'browse':
                r = requests.get(f"{BASE_URL}/files/browse", params={"path":"/workspace"}, timeout=5)
                monitor.record('browse', r.status_code ==200)
            
            elif op == 'boundary':
                r = requests.post(f"{BASE_URL}/projects", json={"name":"X"*300, "path":"/workspace"}, timeout=5)
                monitor.record('boundary', r.status_code in [201,400,404])
            
            time.sleep(random.uniform(0.01, 0.08))
            
        except Exception as e:
            monitor.log(f"⚠️ {name} 异常: {e}", "WARNING")

def print_status():
    rate = (monitor.success / monitor.total *100) if monitor.total>0 else 0
    monitor.log("="*70)
    monitor.log(f"📊 统计 - 总请求:{monitor.total}, 成功:{monitor.success}, 失败:{monitor.failed}, 成功率:{rate:.1f}%")
    monitor.log("="*70)

def run_quick_test():
    print("="*70)
    print("🚀 快速验证测试 - 2分钟")
    print("="*70)
    print(f"📅 开始: {datetime.now()}")
    
    # 启动线程
    workers = 15
    monitor.log(f"🔢 启动 {workers} 个工作线程")
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(worker, i) for i in range(workers)]
        
        # 运行2分钟
        start = time.time()
        next_print = start + 15
        
        while time.time() - start < 120:  # 2分钟
            time.sleep(0.1)
            
            if time.time() >= next_print:
                print_status()
                next_print += 15
        
        # 停止
        stop.set()
        monitor.log("⏳ 等待线程完成...")
        for f in futures: f.result()
    
    # 最终清理
    monitor.log("🧹 清理...")
    for pid in created[:]:
        try:
            requests.delete(f"{BASE_URL}/projects/{pid}", timeout=3)
        except: pass
    
    # 最终报告
    print_status()
    
    if monitor.errors:
        monitor.log(f"❌ 错误数: {len(monitor.errors)}", "ERROR")
    
    print("\n✅ 快速验证完成！")
    return monitor.success / monitor.total >= 0.9 if monitor.total>0 else False

if __name__ == "__main__":
    # 检查服务器
    try:
        print("🔍 检查服务器...")
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ 服务器响应: {r.status_code}")
    except Exception as e:
        print(f"❌ 服务器连接失败: {e}")
        print("请先启动服务器: python api_server_with_extreme_logging.py")
        import sys
        sys.exit(1)
    
    success = run_quick_test()
    print(f"\n🎯 结果: {'成功' if success else '需要关注'}")
