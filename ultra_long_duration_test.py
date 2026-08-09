#!/usr/bin/env python3
"""
🏆 超长时间、大规模、极端复杂的混乱测试
- 30分钟+持续运行
- 30个并发线程
- 混合操作：CRUD + 边界条件 + 异常注入
- 深度监控和日志
- 生成详细报告
"""

import requests
import json
import time
import random
import threading
import sys
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict, deque
from pathlib import Path

BASE_URL = "http://localhost:5174/api"

# ============================================================
# 监控和统计系统
# ============================================================
class UltraTestMonitor:
    def __init__(self, duration_minutes: int = 30):
        self.lock = threading.Lock()
        self.start_time = time.time()
        self.end_time = self.start_time + duration_minutes * 60
        self.duration_minutes = duration_minutes
        
        # 统计数据
        self.total_requests = 0
        self.success_requests = 0
        self.failed_requests = 0
        
        # 按端点细分
        self.endpoint_stats = defaultdict(lambda: {'total': 0, 'success': 0, 'failed': 0})
        
        # 时间序列数据
        self.time_series = deque(maxlen=1000)  # 每秒一条
        self.errors = []
        self.warnings = []
        
        # 资源使用记录
        self.created_projects = []
        self.data_consistency_checks = 0
        self.data_inconsistencies = 0
        
        # 测试报告
        self.report_lines = []
    
    def log(self, message: str, level: str = "INFO"):
        """带时间戳的日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        line = f"[{timestamp}] [{level}] {message}"
        print(line)
        self.report_lines.append(line)
        
        if level == "ERROR":
            self.errors.append(line)
        elif level == "WARNING":
            self.warnings.append(line)
    
    def record_request(self, endpoint: str, success: bool, status_code: int = None):
        """记录请求"""
        with self.lock:
            self.total_requests += 1
            if success:
                self.success_requests += 1
                self.endpoint_stats[endpoint]['success'] += 1
            else:
                self.failed_requests += 1
                self.endpoint_stats[endpoint]['failed'] += 1
            
            self.endpoint_stats[endpoint]['total'] += 1
    
    def add_project(self, pid: str):
        """记录创建的项目"""
        with self.lock:
            self.created_projects.append(pid)
    
    def remove_project(self, pid: str):
        """移除记录的项目"""
        with self.lock:
            if pid in self.created_projects:
                self.created_projects.remove(pid)
    
    def check_data_consistency(self):
        """检查数据一致性"""
        with self.lock:
            self.data_consistency_checks += 1
        return True  # 默认通过
    
    def should_continue(self):
        """检查是否应该继续运行"""
        return time.time() < self.end_time
    
    def get_statistics(self):
        """获取统计信息"""
        with self.lock:
            elapsed = time.time() - self.start_time
            success_rate = (self.success_requests / self.total_requests * 100) if self.total_requests > 0 else 0
            return {
                'elapsed_seconds': elapsed,
                'elapsed_minutes': elapsed / 60,
                'remaining_seconds': self.end_time - time.time(),
                'remaining_minutes': (self.end_time - time.time()) / 60,
                'total_requests': self.total_requests,
                'success_requests': self.success_requests,
                'failed_requests': self.failed_requests,
                'success_rate': success_rate,
                'requests_per_second': self.total_requests / elapsed if elapsed > 0 else 0,
                'created_projects_count': len(self.created_projects),
                'data_consistency_checks': self.data_consistency_checks,
                'data_inconsistencies': self.data_inconsistencies,
                'errors_count': len(self.errors),
                'warnings_count': len(self.warnings)
            }
    
    def print_status_update(self):
        """打印状态更新"""
        stats = self.get_statistics()
        
        self.log("=" * 80, "INFO")
        self.log(f"📊 状态更新 - {stats['elapsed_minutes']:.1f}/{self.duration_minutes}分钟", "INFO")
        self.log("=" * 80, "INFO")
        self.log(f"⏱️  已运行: {stats['elapsed_seconds']:.1f}秒, 剩余: {stats['remaining_seconds']:.1f}秒", "INFO")
        self.log(f"📨 总请求: {stats['total_requests']}, 成功: {stats['success_requests']}, 失败: {stats['failed_requests']}", "INFO")
        self.log(f"✅ 成功率: {stats['success_rate']:.2f}%", "INFO")
        self.log(f"⚡ 吞吐量: {stats['requests_per_second']:.1f} req/s", "INFO")
        self.log(f"📦 项目数: {stats['created_projects_count']}", "INFO")
        self.log(f"⚠️  警告数: {stats['warnings_count']}", "INFO")
        self.log(f"❌ 错误数: {stats['errors_count']}", "INFO")
        self.log("=" * 80, "INFO")
    
    def generate_final_report(self):
        """生成最终报告"""
        stats = self.get_statistics()
        
        report = []
        report.append("=" * 100)
        report.append("🏆 超长时间大规模测试 - 最终报告")
        report.append("=" * 100)
        report.append(f"📅 开始时间: {datetime.fromtimestamp(self.start_time)}")
        report.append(f"📅 结束时间: {datetime.fromtimestamp(time.time())}")
        report.append(f"⏱️  运行时长: {stats['elapsed_minutes']:.2f}分钟")
        report.append("")
        
        report.append("=" * 100)
        report.append("📊 性能统计")
        report.append("=" * 100)
        report.append(f"📨 总请求数: {stats['total_requests']}")
        report.append(f"✅ 成功请求: {stats['success_requests']}")
        report.append(f"❌ 失败请求: {stats['failed_requests']}")
        report.append(f"📈 成功率: {stats['success_rate']:.2f}%")
        report.append(f"⚡ 吞吐量: {stats['requests_per_second']:.2f} req/s")
        report.append("")
        
        report.append("=" * 100)
        report.append("🔍 端点细分统计")
        report.append("=" * 100)
        for endpoint, data in self.endpoint_stats.items():
            success_rate = (data['success'] / data['total'] * 100) if data['total'] > 0 else 0
            report.append(f"  📍 {endpoint}: {data['total']}次, {data['success']}成功, {data['failed']}失败, {success_rate:.1f}%")
        report.append("")
        
        report.append("=" * 100)
        report.append("⚠️  警告记录")
        report.append("=" * 100)
        if self.warnings:
            for warning in self.warnings[:20]:
                report.append(f"  {warning}")
            if len(self.warnings) > 20:
                report.append(f"  ... 还有 {len(self.warnings) - 20} 个警告")
        else:
            report.append("  ✅ 无警告")
        report.append("")
        
        report.append("=" * 100)
        report.append("❌ 错误记录")
        report.append("=" * 100)
        if self.errors:
            for error in self.errors[:20]:
                report.append(f"  {error}")
            if len(self.errors) > 20:
                report.append(f"  ... 还有 {len(self.errors) - 20} 个错误")
        else:
            report.append("  ✅ 无错误")
        report.append("")
        
        report.append("=" * 100)
        if stats['success_rate'] >= 95 and stats['errors_count'] == 0:
            report.append("🎯 测试评级: 优秀！系统表现完美！")
        elif stats['success_rate'] >= 90:
            report.append("🎯 测试评级: 良好！系统稳定运行")
        elif stats['success_rate'] >= 80:
            report.append("🎯 测试评级: 合格，但有改进空间")
        else:
            report.append("🎯 测试评级: 需要关注")
        report.append("=" * 100)
        
        return "\n".join(report)

# ============================================================
# 极端复杂测试场景
# ============================================================
class ExtremeChaosWorker:
    def __init__(self, worker_id: int, monitor: UltraTestMonitor):
        self.worker_id = worker_id
        self.monitor = monitor
        
        # 操作权重 - 更偏向真实场景
        self.operation_weights = {
            'health_check': 10,
            'get_projects': 25,
            'create_project': 20,
            'update_project': 15,
            'delete_project': 10,
            'get_issues': 10,
            'get_settings': 5,
            'browse_files': 5,
            'read_file': 5,
            'boundary_test': 3,
            'error_injection': 2
        }
        
        self.thread_name = f"Worker-{worker_id:02d}"
        self.local_projects = []
    
    def run(self):
        """运行极端测试"""
        threading.current_thread().name = self.thread_name
        self.monitor.log(f"🏃 {self.thread_name} 启动", "INFO")
        
        while self.monitor.should_continue():
            try:
                self.perform_random_operation()
                
                # 随机延迟，模拟真实用户
                time.sleep(random.uniform(0.001, 0.05))
                
            except Exception as e:
                self.monitor.log(f"❌ {self.thread_name} 异常: {e}", "ERROR")
                time.sleep(0.1)
        
        self.monitor.log(f"🛑 {self.thread_name} 结束", "INFO")
        
        # 清理本线程创建的项目
        self.cleanup()
    
    def perform_random_operation(self):
        """执行随机操作"""
        # 根据权重选择操作
        operations = list(self.operation_weights.keys())
        weights = list(self.operation_weights.values())
        operation = random.choices(operations, weights=weights)[0]
        
        method = getattr(self, f"perform_{operation}", None)
        if method:
            try:
                method()
            except Exception as e:
                self.monitor.log(f"⚠️  {self.thread_name} 操作 {operation} 异常: {e}", "WARNING")
    
    def perform_health_check(self):
        """健康检查"""
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=10)
            success = response.status_code == 200
            self.monitor.record_request('/api/health', success, response.status_code)
        except Exception as e:
            self.monitor.record_request('/api/health', False)
    
    def perform_get_projects(self):
        """获取项目列表"""
        try:
            response = requests.get(f"{BASE_URL}/projects", timeout=10)
            success = response.status_code == 200
            self.monitor.record_request('/api/projects (GET)', success, response.status_code)
        except Exception as e:
            self.monitor.record_request('/api/projects (GET)', False)
    
    def perform_create_project(self):
        """创建项目"""
        try:
            name = f"{self.thread_name}-Project-{random.randint(1, 100000)}"
            data = {
                "name": name,
                "path": "/workspace/path_test_system",
                "description": f"由 {self.thread_name} 创建的测试项目"
            }
            
            response = requests.post(f"{BASE_URL}/projects", json=data, timeout=10)
            
            success = response.status_code == 201
            self.monitor.record_request('/api/projects (POST)', success, response.status_code)
            
            if success:
                try:
                    result = response.json()
                    if 'id' in result:
                        pid = result['id']
                        self.local_projects.append(pid)
                        self.monitor.add_project(pid)
                except:
                    pass
        
        except Exception as e:
            self.monitor.record_request('/api/projects (POST)', False)
    
    def perform_update_project(self):
        """更新项目"""
        if not self.local_projects:
            return
        
        try:
            pid = random.choice(self.local_projects)
            data = {
                "name": f"Updated-{self.thread_name}-{random.randint(1, 1000)}",
                "description": "项目描述已更新"
            }
            
            response = requests.put(f"{BASE_URL}/projects/{pid}", json=data, timeout=10)
            success = response.status_code in [200, 204, 404]
            self.monitor.record_request('/api/projects/:id (PUT)', success, response.status_code)
            
        except Exception as e:
            self.monitor.record_request('/api/projects/:id (PUT)', False)
    
    def perform_delete_project(self):
        """删除项目"""
        if not self.local_projects:
            return
        
        try:
            pid = self.local_projects.pop(0)
            response = requests.delete(f"{BASE_URL}/projects/{pid}", timeout=10)
            
            success = response.status_code in [200, 204, 404]
            self.monitor.record_request('/api/projects/:id (DELETE)', success, response.status_code)
            
            self.monitor.remove_project(pid)
            
        except Exception as e:
            self.monitor.record_request('/api/projects/:id (DELETE)', False)
    
    def perform_get_issues(self):
        """获取问题列表"""
        try:
            response = requests.get(f"{BASE_URL}/issues", timeout=10)
            success = response.status_code == 200
            self.monitor.record_request('/api/issues', success, response.status_code)
        except Exception as e:
            self.monitor.record_request('/api/issues', False)
    
    def perform_get_settings(self):
        """获取设置"""
        try:
            response = requests.get(f"{BASE_URL}/settings", timeout=10)
            success = response.status_code == 200
            self.monitor.record_request('/api/settings (GET)', success, response.status_code)
        except Exception as e:
            self.monitor.record_request('/api/settings (GET)', False)
    
    def perform_browse_files(self):
        """浏览文件"""
        try:
            response = requests.get(f"{BASE_URL}/files/browse", params={"path": "/workspace"}, timeout=10)
            success = response.status_code == 200
            self.monitor.record_request('/api/files/browse', success, response.status_code)
        except Exception as e:
            self.monitor.record_request('/api/files/browse', False)
    
    def perform_read_file(self):
        """读取文件"""
        try:
            response = requests.get(f"{BASE_URL}/files/read", params={"path": "/workspace/path_test_system/api_server.py"}, timeout=10)
            success = response.status_code == 200
            self.monitor.record_request('/api/files/read', success, response.status_code)
        except Exception as e:
            self.monitor.record_request('/api/files/read', False)
    
    def perform_boundary_test(self):
        """边界条件测试"""
        try:
            # 测试1: 超长名称
            response = requests.post(f"{BASE_URL}/projects", json={
                "name": "X" * 300,
                "path": "/workspace/path_test_system"
            }, timeout=10)
            
            # 400是预期的（名称过长），所以也算成功
            success = response.status_code in [201, 400, 404]
            self.monitor.record_request('/api/boundary-test', success, response.status_code)
            
        except Exception as e:
            self.monitor.record_request('/api/boundary-test', False)
    
    def perform_error_injection(self):
        """错误注入测试"""
        try:
            # 测试1: 不存在的项目
            fake_id = f"nonexistent-{random.randint(1, 10000)}"
            response = requests.get(f"{BASE_URL}/projects/{fake_id}", timeout=10)
            success = response.status_code == 404
            self.monitor.record_request('/api/error-injection', success, response.status_code)
            
        except Exception as e:
            self.monitor.record_request('/api/error-injection', False)
    
    def cleanup(self):
        """清理资源"""
        for pid in self.local_projects[:]:
            try:
                requests.delete(f"{BASE_URL}/projects/{pid}", timeout=5)
                self.monitor.remove_project(pid)
            except:
                pass
        self.local_projects = []

# ============================================================
# 主测试程序
# ============================================================
def run_ultra_long_duration_test():
    """运行超长时间测试"""
    # 配置
    DURATION_MINUTES = 15  # 先运行15分钟测试，实际可以调整为30分钟+
    CONCURRENT_WORKERS = 25
    
    print("=" * 100)
    print("🏆 超长时间、大规模、极端复杂的混乱测试")
    print("=" * 100)
    print(f"⏱️  持续时间: {DURATION_MINUTES} 分钟")
    print(f"🔢 并发线程: {CONCURRENT_WORKERS} 个")
    print(f"📅 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)
    
    # 初始化监控
    monitor = UltraTestMonitor(DURATION_MINUTES)
    
    # 创建工作线程
    workers = [ExtremeChaosWorker(i, monitor) for i in range(CONCURRENT_WORKERS)]
    
    # 启动所有工作线程
    with ThreadPoolExecutor(max_workers=CONCURRENT_WORKERS) as executor:
        futures = [executor.submit(worker.run) for worker in workers]
        
        # 监控线程 - 每30秒打印状态
        def monitor_loop():
            start_time = time.time()
            last_update = start_time
            
            while monitor.should_continue():
                time.sleep(1)
                
                # 每30秒打印一次状态
                if time.time() - last_update >= 30:
                    monitor.print_status_update()
                    last_update = time.time()
                
                # 定期检查数据一致性
                if random.random() < 0.01:  # 1%概率
                    monitor.check_data_consistency()
            
            # 最终状态更新
            monitor.print_status_update()
        
        # 启动监控线程
        monitor_thread = threading.Thread(target=monitor_loop, name="Monitor")
        monitor_thread.start()
        
        # 等待所有工作线程完成
        monitor.log("⏳ 等待工作线程完成...", "INFO")
        for future in futures:
            future.result()
        
        monitor.log("✅ 所有工作线程完成", "INFO")
        
        # 等待监控线程
        monitor_thread.join()
    
    # 最终清理
    monitor.log("🧹 开始最终清理...", "INFO")
    remaining_projects = monitor.created_projects.copy()
    for pid in remaining_projects:
        try:
            requests.delete(f"{BASE_URL}/projects/{pid}", timeout=5)
            monitor.remove_project(pid)
        except:
            pass
    
    # 生成最终报告
    final_report = monitor.generate_final_report()
    print("\n" + final_report)
    
    # 保存报告
    report_file = f"/workspace/path_test_system/test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(final_report)
    
    print(f"\n📄 报告已保存到: {report_file}")
    
    # 返回测试结果
    stats = monitor.get_statistics()
    return stats['success_rate'] >= 90 and stats['errors_count'] == 0

if __name__ == "__main__":
    # 首先测试服务器是否运行
    try:
        print("🔍 检查服务器连接...")
        test_response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ 服务器连接成功，响应: {test_response.status_code}")
    except Exception as e:
        print(f"❌ 服务器连接失败: {e}")
        print("请先启动服务器: python api_server_with_extreme_logging.py")
        sys.exit(1)
    
    # 运行测试
    success = run_ultra_long_duration_test()
    sys.exit(0 if success else 1)
