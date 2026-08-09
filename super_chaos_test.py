#!/usr/bin/env python3
"""
🏆 超级混乱测试 - 极端边界 + 并发 + 异常注入
- 20分钟持续运行
- 15个并发线程
- 极端边界和异常情况
- 数据一致性验证
"""

import requests
import json
import time
import random
import threading
import sys
import string
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from pathlib import Path

BASE_URL = "http://localhost:5174/api"

class SuperChaosMonitor:
    def __init__(self, duration_minutes=20):
        self.lock = threading.Lock()
        self.start_time = time.time()
        self.end_time = self.start_time + duration_minutes * 60
        self.duration_minutes = duration_minutes
        
        self.total_requests = 0
        self.success_requests = 0
        self.failed_requests = 0
        self.errors = []
        self.warnings = []
        self.created_projects = []
        self.data_inconsistencies = 0
        
        self.endpoint_stats = defaultdict(lambda: {'total': 0, 'success': 0, 'failed': 0})
        self.critical_errors = []
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prefix = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "CRITICAL": "🚨"
        }
        print(f"[{timestamp}] [{prefix.get(level, '📄')}] {message}")
        if level == "ERROR":
            self.errors.append(message)
        elif level == "CRITICAL":
            self.critical_errors.append(message)
            self.errors.append(message)
        elif level == "WARNING":
            self.warnings.append(message)
        
    def record_request(self, endpoint, success):
        with self.lock:
            self.total_requests += 1
            self.endpoint_stats[endpoint]['total'] += 1
            if success:
                self.success_requests += 1
                self.endpoint_stats[endpoint]['success'] += 1
            else:
                self.failed_requests += 1
                self.endpoint_stats[endpoint]['failed'] += 1
                
    def print_status(self):
        with self.lock:
            elapsed = time.time() - self.start_time
            remaining = self.end_time - time.time()
            
            if self.total_requests > 0:
                success_rate = (self.success_requests / self.total_requests) * 100
            else:
                success_rate = 0
                
            print("\n" + "="*85)
            print(f"📊 超级混乱测试 - 已运行: {elapsed/60:.1f}分钟, 剩余: {remaining/60:.1f}分钟")
            print("="*85)
            print(f"📨 总请求: {self.total_requests:6} | ✅ 成功: {self.success_requests:6} | ❌ 失败: {self.failed_requests:6}")
            print(f"📈 成功率: {success_rate:5.1f}% | 🎯 活跃项目: {len(self.created_projects):4}")
            if self.critical_errors:
                print(f"🚨 严重错误: {len(self.critical_errors):4}")
            print("="*85)
            
    def get_final_report(self):
        with self.lock:
            elapsed = time.time() - self.start_time
            success_rate = (self.success_requests / self.total_requests * 100) if self.total_requests > 0 else 0
            
            report = []
            report.append("="*100)
            report.append("🏆 超级混乱测试 - 最终报告")
            report.append("="*100)
            report.append(f"📅 开始时间: {datetime.fromtimestamp(self.start_time)}")
            report.append(f"📅 结束时间: {datetime.now()}")
            report.append(f"⏱️ 持续时长: {elapsed/60:.2f}分钟")
            report.append("")
            
            report.append("="*100)
            report.append("📊 核心统计")
            report.append("="*100)
            report.append(f"📨 总请求数: {self.total_requests}")
            report.append(f"✅ 成功请求: {self.success_requests}")
            report.append(f"❌ 失败请求: {self.failed_requests}")
            report.append(f"📈 成功率: {success_rate:.2f}%")
            report.append(f"⚡ 平均吞吐: {self.total_requests/elapsed:.1f} req/s")
            report.append("")
            
            report.append("="*100)
            report.append("🔍 端点细分统计")
            report.append("="*100)
            for endpoint, stats in self.endpoint_stats.items():
                ep_success_rate = (stats['success']/stats['total']*100) if stats['total'] > 0 else 0
                report.append(f"  📍 {endpoint:15} {stats['total']:5}次, {stats['success']:5}成功, {ep_success_rate:6.1f}%")
            report.append("")
            
            if self.critical_errors:
                report.append("="*100)
                report.append("🚨 严重错误记录")
                report.append("="*100)
                for err in self.critical_errors[:15]:
                    report.append(f"  {err}")
                if len(self.critical_errors) > 15:
                    report.append(f"  ...还有 {len(self.critical_errors)-15} 个")
            else:
                report.append("="*100)
                report.append("✅ 无严重错误")
            
            if self.warnings:
                report.append("="*100)
                report.append("⚠️ 警告记录")
                report.append("="*100)
                for warn in self.warnings[:20]:
                    report.append(f"  {warn}")
                if len(self.warnings) > 20:
                    report.append(f"  ...还有 {len(self.warnings)-20} 个")
            
            report.append("="*100)
            if success_rate >= 95 and len(self.critical_errors) == 0:
                report.append("🎯 评级: 优秀！系统完美通过超级混乱测试！")
            elif success_rate >= 90:
                report.append("🎯 评级: 良好！系统稳定")
            elif success_rate >= 80:
                report.append("🎯 评级: 合格")
            else:
                report.append("🎯 评级: 需要关注")
            
            return "\n".join(report)

def generate_extreme_value():
    """生成极端值"""
    case = random.randint(0, 12)
    if case == 0:
        return ""
    elif case == 1:
        return " " * 50
    elif case == 2:
        return "x" * 500
    elif case == 3:
        return string.punctuation * 10
    elif case == 4:
        return string.ascii_letters * 20
    elif case == 5:
        return "1" + "0" * 100
    elif case == 6:
        return None
    elif case == 7:
        return "🚀🎉🎊" * 20
    elif case == 8:
        return "valid_normal_name"
    elif case == 9:
        return "<script>alert('xss')</script>"
    elif case == 10:
        return "' OR '1'='1' --"
    elif case == 11:
        return "name\nwith\nnewlines"
    else:
        return "test_" + str(random.randint(1, 1000000))

def super_chaos_worker(worker_id, monitor):
    """超级混乱工作线程"""
    thread_name = f"SCW{worker_id:02d}"
    local_projects = []
    
    while time.time() < monitor.end_time and not monitor.stop_event.is_set():
        try:
            operation = random.choices(
                [
                    'health', 
                    'create_project', 
                    'get_projects',
                    'update_project',
                    'delete_project',
                    'get_issues',
                    'get_settings',
                    'browse_files',
                    'read_file',
                    'create_test',
                    'analyze',
                    'extreme_operation',
                    'data_validation',
                ],
                weights=[5, 20, 25, 15, 10, 5, 5, 5, 5, 3, 3, 4, 5]
            )[0]
            
            success = False
            endpoint = operation
            
            if operation == 'health':
                try:
                    r = requests.get(f"{BASE_URL}/health", timeout=60)
                    success = r.status_code == 200
                except Exception:
                    pass
                    
            elif operation == 'create_project':
                try:
                    name = generate_extreme_value()
                    path = random.choice([
                        '/workspace/path_test_system',
                        '/workspace/path_test_system/data',
                        '/workspace'
                    ])
                    
                    data = {
                        'name': name,
                        'path': path,
                        'description': generate_extreme_value()
                    }
                    
                    r = requests.post(f"{BASE_URL}/projects", json=data, timeout=60)
                    
                    if r.status_code == 201:
                        try:
                            result_data = r.json()
                            if 'id' in result_data:
                                pid = result_data['id']
                                with monitor.lock:
                                    monitor.created_projects.append(pid)
                                local_projects.append(pid)
                                success = True
                        except Exception:
                            pass
                    else:
                        success = r.status_code in [400, 404, 403]
                except Exception:
                    pass
                    
            elif operation == 'get_projects':
                try:
                    r = requests.get(f"{BASE_URL}/projects", timeout=60)
                    success = r.status_code == 200
                except Exception:
                    pass
                    
            elif operation == 'update_project':
                if local_projects:
                    try:
                        pid = random.choice(local_projects)
                        r = requests.put(f"{BASE_URL}/projects/{pid}", json={
                            'name': generate_extreme_value(),
                            'description': generate_extreme_value()
                        }, timeout=60)
                        success = r.status_code in [200, 204, 404, 400]
                    except Exception:
                        pass
                        
            elif operation == 'delete_project':
                if local_projects:
                    try:
                        pid = local_projects.pop(0)
                        r = requests.delete(f"{BASE_URL}/projects/{pid}", timeout=60)
                        success = r.status_code in [200, 204, 404]
                        
                        if success:
                            with monitor.lock:
                                if pid in monitor.created_projects:
                                    monitor.created_projects.remove(pid)
                    except Exception:
                        pass
                        
            elif operation == 'get_issues':
                try:
                    r = requests.get(f"{BASE_URL}/issues", timeout=60)
                    success = r.status_code == 200
                except Exception:
                    pass
                    
            elif operation == 'get_settings':
                try:
                    r = requests.get(f"{BASE_URL}/settings", timeout=60)
                    success = r.status_code == 200
                except Exception:
                    pass
                    
            elif operation == 'browse_files':
                try:
                    paths = ['/workspace', '/workspace/path_test_system', '/']
                    path = random.choice(paths)
                    r = requests.get(f"{BASE_URL}/files/browse", params={'path': path}, timeout=60)
                    success = r.status_code in [200, 403, 404]
                except Exception:
                    pass
                    
            elif operation == 'read_file':
                try:
                    files = [
                        '/workspace/path_test_system/api_server.py',
                        '/workspace/path_test_system/requirements.txt'
                    ]
                    file = random.choice(files)
                    r = requests.get(f"{BASE_URL}/files/read", params={'path': file}, timeout=60)
                    success = r.status_code in [200, 404]
                except Exception:
                    pass
                    
            elif operation == 'create_test':
                try:
                    r = requests.post(f"{BASE_URL}/tests", json={
                        'name': f"Test_{thread_name}_{random.randint(1, 10000)}",
                        'file': '/workspace/path_test_system/test_project.py'
                    }, timeout=60)
                    success = r.status_code in [201, 400]
                except Exception:
                    pass
                    
            elif operation == 'analyze':
                if local_projects:
                    try:
                        pid = random.choice(local_projects)
                        r = requests.post(f"{BASE_URL}/analyze", json={'projectId': pid}, timeout=120)
                        success = r.status_code in [200, 400, 404]
                    except Exception:
                        pass
                        
            elif operation == 'extreme_operation':
                try:
                    choice = random.randint(0, 4)
                    if choice == 0:
                        for i in range(10):
                            requests.get(f"{BASE_URL}/health", timeout=2)
                            time.sleep(0.001)
                        success = True
                    elif choice == 1:
                        r = requests.post(f"{BASE_URL}/projects", json={}, timeout=60)
                        success = r.status_code in [400, 404]
                    elif choice == 2:
                        fake_id = "nonexistent_" + ''.join(random.choices(string.ascii_letters + string.digits, k=30))
                        r = requests.get(f"{BASE_URL}/projects/{fake_id}", timeout=60)
                        success = r.status_code == 404
                    elif choice == 3:
                        r = requests.post(f"{BASE_URL}/projects", json={
                            'name': generate_extreme_value(),
                            'path': generate_extreme_value()
                        }, timeout=60)
                        success = True
                except Exception:
                    pass
                    
            elif operation == 'data_validation':
                try:
                    # 数据一致性验证
                    r = requests.get(f"{BASE_URL}/projects", timeout=60)
                    if r.status_code == 200:
                        try:
                            data = r.json()
                            for p in data:
                                if not isinstance(p, dict):
                                    with monitor.lock:
                                        monitor.data_inconsistencies += 1
                                    monitor.log(f"数据格式异常: {type(p)}", "CRITICAL")
                            success = True
                        except Exception:
                            pass
                except Exception:
                    pass
                    
            # 记录请求
            monitor.record_request(endpoint, success)
            
            time.sleep(random.uniform(0.01, 0.15))
            
        except Exception as e:
            monitor.warnings.append(f"{thread_name} 异常: {str(e)}")
            
    # 清理
    for pid in local_projects:
        try:
            requests.delete(f"{BASE_URL}/projects/{pid}", timeout=30)
        except Exception:
            pass

def main():
    print("="*100)
    print("🏆 超级混乱测试 - 开始")
    print("="*100)
    print(f"📅 开始时间: {datetime.now()}")
    print(f"⏱️ 测试时长: 20分钟")
    print(f"👷 并发线程: 15个")
    print(f"🎯 目标: 极端边界、并发、异常注入、数据一致性")
    print("="*100)
    
    monitor = SuperChaosMonitor(duration_minutes=20)
    monitor.stop_event = threading.Event()
    
    print("\n🚀 启动工作线程...")
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = [executor.submit(super_chaos_worker, i, monitor) for i in range(15)]
        
        last_print = time.time()
        while time.time() < monitor.end_time:
            time.sleep(0.5)
            
            if time.time() - last_print >= 120:
                monitor.print_status()
                last_print = time.time()
        
        print("\n⏳ 等待工作线程完成...")
        monitor.stop_event.set()
        for f in futures:
            f.result()
    
    print("\n🧹 清理项目...")
    with monitor.lock:
        projects = list(monitor.created_projects)
    
    for pid in projects:
        try:
            requests.delete(f"{BASE_URL}/projects/{pid}", timeout=30)
        except Exception:
            pass
    
    final_report = monitor.get_final_report()
    print("\n" + final_report)
    
    report_file = f"/workspace/path_test_system/super_chaos_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(final_report)
    
    print(f"\n📄 报告保存至: {report_file}")
    
    return len(monitor.critical_errors) == 0

if __name__ == "__main__":
    try:
        result = main()
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ 测试中断")
        sys.exit(1)
