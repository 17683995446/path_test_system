#!/usr/bin/env python3
"""
🏆 优化的10分钟超长测试 - 更稳定的压力测试
- 10个并发线程
- 10分钟持续运行
- 实时监控和报告
"""

import requests
import json
import time
import random
import threading
import sys
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

BASE_URL = "http://localhost:5174/api"

class TestMonitor:
    def __init__(self, duration_minutes=10, num_workers=10):
        self.lock = threading.Lock()
        self.start_time = time.time()
        self.end_time = self.start_time + duration_minutes * 60
        self.duration_minutes = duration_minutes
        self.num_workers = num_workers
        
        self.total_requests = 0
        self.success_requests = 0
        self.failed_requests = 0
        self.errors = []
        self.warnings = []
        self.created_projects = []
        
        self.endpoint_stats = defaultdict(lambda: {'total': 0, 'success': 0, 'failed': 0})
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def record_request(self, endpoint, success, status_code=None):
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
                
            print("\n" + "="*80)
            print(f"📊 状态更新 - 已运行: {elapsed/60:.1f}分钟, 剩余: {remaining/60:.1f}分钟")
            print("="*80)
            print(f"📨 总请求: {self.total_requests}")
            print(f"✅ 成功: {self.success_requests}")
            print(f"❌ 失败: {self.failed_requests}")
            print(f"📈 成功率: {success_rate:.1f}%")
            print(f"🎯 活跃项目: {len(self.created_projects)}")
            print("="*80)
            
    def get_final_report(self):
        with self.lock:
            elapsed = time.time() - self.start_time
            success_rate = (self.success_requests / self.total_requests * 100) if self.total_requests > 0 else 0
            
            report = []
            report.append("="*100)
            report.append("🏆 优化10分钟超长测试 - 最终报告")
            report.append("="*100)
            report.append(f"📅 开始时间: {datetime.fromtimestamp(self.start_time)}")
            report.append(f"📅 结束时间: {datetime.now()}")
            report.append(f"⏱️ 持续时长: {elapsed/60:.2f}分钟")
            report.append(f"👷 并发线程: {self.num_workers}")
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
                report.append(f"  📍 {endpoint}: {stats['total']}次, {stats['success']}成功, {ep_success_rate:.1f}%")
            report.append("")
            
            if self.errors:
                report.append("="*100)
                report.append("❌ 错误记录")
                report.append("="*100)
                for err in self.errors[:20]:
                    report.append(f"  {err}")
                if len(self.errors) > 20:
                    report.append(f"  ...还有 {len(self.errors)-20} 个错误")
            else:
                report.append("="*100)
                report.append("✅ 无错误记录")
            
            report.append("="*100)
            if success_rate >= 95 and len(self.errors) == 0:
                report.append("🎯 评级: 优秀！系统完美稳定！")
            elif success_rate >= 90:
                report.append("🎯 评级: 良好！系统稳定运行")
            elif success_rate >= 80:
                report.append("🎯 评级: 合格")
            else:
                report.append("🎯 评级: 需要关注")
            
            return "\n".join(report)

def worker_task(worker_id, monitor):
    """工作线程任务"""
    thread_name = f"W{worker_id:02d}"
    local_projects = []
    
    while time.time() < monitor.end_time and not monitor.stop_event.is_set():
        try:
            # 随机选择操作
            operation = random.choices(
                ['health', 'get_projects', 'create_project', 'update_project', 
                 'delete_project', 'get_issues', 'browse_files', 'read_file'],
                weights=[10, 25, 20, 15, 10, 10, 5, 5]
            )[0]
            
            success = False
            endpoint = operation
            
            if operation == 'health':
                try:
                    r = requests.get(f"{BASE_URL}/health", timeout=30)
                    success = r.status_code == 200
                except Exception:
                    pass
                    
            elif operation == 'get_projects':
                try:
                    r = requests.get(f"{BASE_URL}/projects", timeout=30)
                    success = r.status_code == 200
                except Exception:
                    pass
                    
            elif operation == 'create_project':
                try:
                    project_name = f"{thread_name}-{int(time.time()*1000)}-{random.randint(1, 10000)}"
                    r = requests.post(f"{BASE_URL}/projects", json={
                        'name': project_name,
                        'path': '/workspace/path_test_system',
                        'description': f'Test from {thread_name}'
                    }, timeout=30)
                    
                    if r.status_code == 201:
                        try:
                            data = r.json()
                            if 'id' in data:
                                with monitor.lock:
                                    monitor.created_projects.append(data['id'])
                                local_projects.append(data['id'])
                                success = True
                        except:
                            pass
                except Exception:
                    pass
                    
            elif operation == 'update_project':
                if local_projects:
                    try:
                        pid = random.choice(local_projects)
                        r = requests.put(f"{BASE_URL}/projects/{pid}", json={
                            'name': f'Updated-{thread_name}-{random.randint(1, 1000)}'
                        }, timeout=30)
                        success = r.status_code in [200, 204, 404]
                    except Exception:
                        pass
                        
            elif operation == 'delete_project':
                if local_projects:
                    try:
                        pid = local_projects.pop(0)
                        r = requests.delete(f"{BASE_URL}/projects/{pid}", timeout=30)
                        success = r.status_code in [200, 204, 404]
                        
                        if success:
                            with monitor.lock:
                                if pid in monitor.created_projects:
                                    monitor.created_projects.remove(pid)
                    except Exception:
                        pass
                        
            elif operation == 'get_issues':
                try:
                    r = requests.get(f"{BASE_URL}/issues", timeout=30)
                    success = r.status_code == 200
                except Exception:
                    pass
                    
            elif operation == 'browse_files':
                try:
                    r = requests.get(f"{BASE_URL}/files/browse", params={'path': '/workspace'}, timeout=30)
                    success = r.status_code == 200
                except Exception:
                    pass
                    
            elif operation == 'read_file':
                try:
                    r = requests.get(f"{BASE_URL}/files/read", params={'path': '/workspace/path_test_system/api_server.py'}, timeout=30)
                    success = r.status_code == 200
                except Exception:
                    pass
                    
            # 记录请求
            monitor.record_request(endpoint, success)
            
            # 随机延迟
            time.sleep(random.uniform(0.01, 0.1))
            
        except Exception as e:
            monitor.warnings.append(f"{thread_name} 异常: {e}")
            
    # 清理本地项目
    for pid in local_projects:
        try:
            requests.delete(f"{BASE_URL}/projects/{pid}", timeout=10)
        except:
            pass

def main():
    """主测试函数"""
    print("="*100)
    print("🏆 优化的10分钟超长测试 - 开始")
    print("="*100)
    print(f"📅 开始时间: {datetime.now()}")
    print(f"⏱️ 测试时长: 10分钟")
    print(f"👷 并发线程: 10个")
    print("="*100)
    
    # 初始化监控
    monitor = TestMonitor(duration_minutes=10, num_workers=10)
    monitor.stop_event = threading.Event()
    
    # 启动工作线程
    print("\n🚀 启动工作线程...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(worker_task, i, monitor) for i in range(10)]
        
        # 监控循环
        last_print_time = time.time()
        while time.time() < monitor.end_time:
            time.sleep(1)
            
            if time.time() - last_print_time >= 60:
                monitor.print_status()
                last_print_time = time.time()
        
        # 等待线程完成
        print("\n⏳ 等待工作线程完成...")
        monitor.stop_event.set()
        for f in futures:
            f.result()
    
    # 清理剩余项目
    print("\n🧹 清理剩余项目...")
    with monitor.lock:
        projects_to_clean = list(monitor.created_projects)
    
    for pid in projects_to_clean:
        try:
            requests.delete(f"{BASE_URL}/projects/{pid}", timeout=10)
        except:
            pass
    
    # 打印最终报告
    final_report = monitor.get_final_report()
    print("\n" + final_report)
    
    # 保存报告
    report_file = f"/workspace/path_test_system/test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(final_report)
    
    print(f"\n📄 报告已保存到: {report_file}")
    
    return monitor.failed_requests == 0

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ 测试被用户中断")
        sys.exit(130)
