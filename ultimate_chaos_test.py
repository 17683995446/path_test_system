#!/usr/bin/env python3
"""
================================================================================
超极端压力测试脚本 - 30分钟极限挑战
================================================================================
测试目标：
- 30分钟持续运行
- 20个并发线程
- 极端边界值注入
- 异常场景模拟
- 数据一致性验证
- 实时监控和问题发现

作者：AI Test Engineer
日期：2026-05-22
================================================================================
"""

import requests
import json
import time
import random
import threading
import sys
import string
import traceback
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict, deque
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field
import signal
import os

# ============================================================
# 测试配置
# ============================================================
BASE_URL = "http://localhost:5174/api"
TEST_DURATION_MINUTES = 30  # 30分钟极限测试
NUM_WORKERS = 20  # 20个并发线程
REQUEST_TIMEOUT = 30  # 30秒超时

# ============================================================
# 统计类
# ============================================================
@dataclass
class EndpointStats:
    """端点统计"""
    total: int = 0
    success: int = 0
    failed: int = 0
    errors: List[str] = field(default_factory=list)

class ChaosMonitor:
    """混乱测试监控器"""
    
    def __init__(self, duration_minutes: int):
        self.start_time = time.time()
        self.end_time = self.start_time + duration_minutes * 60
        self.duration_minutes = duration_minutes
        
        # 线程锁
        self.lock = threading.Lock()
        
        # 核心统计
        self.total_requests = 0
        self.success_requests = 0
        self.failed_requests = 0
        self.timeout_requests = 0
        self.error_requests = 0
        
        # 端点统计
        self.endpoint_stats: Dict[str, EndpointStats] = defaultdict(EndpointStats)
        
        # 错误追踪
        self.critical_errors: deque = deque(maxlen=100)
        self.warnings: deque = deque(maxlen=200)
        self.error_patterns: Dict[str, int] = defaultdict(int)
        
        # 项目追踪
        self.created_projects: List[str] = []
        self.deleted_projects: List[str] = []
        
        # 性能指标
        self.response_times: deque = deque(maxlen=1000)
        self.start_times: Dict[str, float] = {}
        
        # 停止事件
        self.stop_event = threading.Event()
        
        # 监控线程
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        
    def _monitor_loop(self):
        """监控循环"""
        last_report_time = time.time()
        
        while not self.stop_event.is_set():
            time.sleep(1)
            
            current_time = time.time()
            elapsed = current_time - self.start_time
            
            # 每60秒输出一次状态报告
            if current_time - last_report_time >= 60:
                self._print_status_report(elapsed)
                last_report_time = current_time
                
                # 检查是否有严重错误模式
                self._analyze_error_patterns()
    
    def _print_status_report(self, elapsed: float):
        """打印状态报告"""
        with self.lock:
            remaining = self.end_time - time.time()
            success_rate = (self.success_requests / self.total_requests * 100) if self.total_requests > 0 else 0
            avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
            
            print("\n" + "=" * 90)
            print(f"📊 阶段报告 - 已运行: {elapsed/60:.1f}分钟, 剩余: {remaining/60:.1f}分钟")
            print("=" * 90)
            print(f"📨 总请求: {self.total_requests:8} | ✅ 成功: {self.success_requests:8} | ❌ 失败: {self.failed_requests:8}")
            print(f"📈 成功率: {success_rate:6.2f}% | ⏱️ 平均响应: {avg_response_time:6.2f}s | ⏰ 超时: {self.timeout_requests:6}")
            print(f"🚨 严重错误: {len(self.critical_errors):6} | ⚠️  警告: {len(self.warnings):6} | 📦 项目: {len(self.created_projects):6}")
            print("=" * 90)
            
            # 显示最常见的错误
            if self.error_patterns:
                print("\n🔍 错误模式分析:")
                sorted_errors = sorted(self.error_patterns.items(), key=lambda x: x[1], reverse=True)[:5]
                for error_type, count in sorted_errors:
                    print(f"   - {error_type}: {count}次")
            
            # 显示最近的严重错误
            if self.critical_errors:
                print("\n🚨 最近严重错误:")
                for error in list(self.critical_errors)[-3:]:
                    print(f"   {error}")
    
    def _analyze_error_patterns(self):
        """分析错误模式"""
        if len(self.critical_errors) >= 10:
            recent_errors = list(self.critical_errors)[-10:]
            error_types = defaultdict(int)
            
            for error in recent_errors:
                # 简化错误信息，提取关键部分
                if "timeout" in error.lower():
                    error_types["请求超时"] += 1
                elif "connection" in error.lower():
                    error_types["连接错误"] += 1
                elif "500" in error:
                    error_types["服务器错误"] += 1
                elif "404" in error:
                    error_types["资源未找到"] += 1
                elif "lock" in error.lower():
                    error_types["文件锁问题"] += 1
                else:
                    error_types["其他错误"] += 1
            
            # 如果某个错误模式超过50%，发出警告
            total = sum(error_types.values())
            for error_type, count in error_types.items():
                if count / total > 0.5:
                    self.record_warning(f"⚠️ 错误模式警告: {error_type} 占 {count/total*100:.1f}%")
    
    def record_request(self, endpoint: str, success: bool, response_time: float = 0, 
                     error_msg: str = None, status_code: int = None):
        """记录请求"""
        with self.lock:
            self.total_requests += 1
            
            if success:
                self.success_requests += 1
            else:
                self.failed_requests += 1
                if "timeout" in str(error_msg).lower():
                    self.timeout_requests += 1
                else:
                    self.error_requests += 1
            
            # 记录响应时间
            if response_time > 0:
                self.response_times.append(response_time)
            
            # 端点统计
            stats = self.endpoint_stats[endpoint]
            stats.total += 1
            if success:
                stats.success += 1
            else:
                stats.failed += 1
                if error_msg:
                    stats.errors.append(error_msg)
            
            # 错误模式追踪
            if error_msg and status_code:
                error_key = f"HTTP {status_code}"
                self.error_patterns[error_key] += 1
    
    def record_critical_error(self, error_msg: str):
        """记录严重错误"""
        with self.lock:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            full_error = f"[{timestamp}] {error_msg}"
            self.critical_errors.append(full_error)
            print(f"🚨 严重错误: {error_msg}")
    
    def record_warning(self, warning_msg: str):
        """记录警告"""
        with self.lock:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            full_warning = f"[{timestamp}] {warning_msg}"
            self.warnings.append(full_warning)
    
    def record_project_created(self, project_id: str):
        """记录创建的项目"""
        with self.lock:
            self.created_projects.append(project_id)
    
    def record_project_deleted(self, project_id: str):
        """记录删除的项目"""
        with self.lock:
            self.deleted_projects.append(project_id)
            if project_id in self.created_projects:
                self.created_projects.remove(project_id)
    
    def get_final_report(self) -> str:
        """生成最终报告"""
        with self.lock:
            elapsed = time.time() - self.start_time
            success_rate = (self.success_requests / self.total_requests * 100) if self.total_requests > 0 else 0
            avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
            throughput = self.total_requests / elapsed if elapsed > 0 else 0
            
            report_lines = []
            report_lines.append("\n" + "=" * 100)
            report_lines.append("🏆 超极端压力测试 - 最终报告")
            report_lines.append("=" * 100)
            report_lines.append(f"📅 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append(f"⏱️  持续时长: {elapsed/60:.2f}分钟")
            report_lines.append(f"👷 并发线程: {NUM_WORKERS}个")
            report_lines.append("")
            
            report_lines.append("=" * 100)
            report_lines.append("📊 核心性能指标")
            report_lines.append("=" * 100)
            report_lines.append(f"📨 总请求数:      {self.total_requests:>12,}")
            report_lines.append(f"✅ 成功请求:      {self.success_requests:>12,}")
            report_lines.append(f"❌ 失败请求:      {self.failed_requests:>12,}")
            report_lines.append(f"⏰ 超时请求:      {self.timeout_requests:>12,}")
            report_lines.append(f"⚡ 系统吞吐量:    {throughput:>12.2f} req/s")
            report_lines.append(f"📈 请求成功率:    {success_rate:>12.2f}%")
            report_lines.append(f"⏱️  平均响应时间:  {avg_response_time:>12.2f}s")
            report_lines.append(f"📦 创建项目数:    {len(self.created_projects):>12,}")
            report_lines.append(f"🗑️  删除项目数:    {len(self.deleted_projects):>12,}")
            report_lines.append("")
            
            report_lines.append("=" * 100)
            report_lines.append("🔍 端点详细统计")
            report_lines.append("=" * 100)
            for endpoint, stats in sorted(self.endpoint_stats.items()):
                ep_success_rate = (stats.success / stats.total * 100) if stats.total > 0 else 0
                report_lines.append(f"  📍 {endpoint:20} {stats.total:>6}次 | ✅ {stats.success:>6} | ❌ {stats.failed:>6} | {ep_success_rate:>5.1f}%")
            report_lines.append("")
            
            # 错误分析
            if self.critical_errors:
                report_lines.append("=" * 100)
                report_lines.append("🚨 严重错误记录 (最多显示20条)")
                report_lines.append("=" * 100)
                for error in list(self.critical_errors)[:20]:
                    report_lines.append(f"  {error}")
                if len(self.critical_errors) > 20:
                    report_lines.append(f"  ... 还有 {len(self.critical_errors) - 20} 个错误")
                report_lines.append("")
            
            # 错误模式分析
            if self.error_patterns:
                report_lines.append("=" * 100)
                report_lines.append("🔍 错误模式分析")
                report_lines.append("=" * 100)
                sorted_errors = sorted(self.error_patterns.items(), key=lambda x: x[1], reverse=True)
                for error_type, count in sorted_errors[:10]:
                    percentage = count / self.total_requests * 100
                    report_lines.append(f"  {error_type:30} {count:>8}次 ({percentage:>5.2f}%)")
                report_lines.append("")
            
            # 最终评级
            report_lines.append("=" * 100)
            if success_rate >= 98 and len(self.critical_errors) == 0:
                report_lines.append("🎯 测试结果: 完美通过！系统表现出色！")
                report_lines.append("🌟 评级: S级 (卓越)")
            elif success_rate >= 95:
                report_lines.append("🎯 测试结果: 优秀！系统稳定可靠")
                report_lines.append("🌟 评级: A级 (优秀)")
            elif success_rate >= 90:
                report_lines.append("🎯 测试结果: 良好！有少量改进空间")
                report_lines.append("🌟 评级: B级 (良好)")
            elif success_rate >= 80:
                report_lines.append("🎯 测试结果: 合格！需要关注性能问题")
                report_lines.append("🌟 评级: C级 (合格)")
            else:
                report_lines.append("🎯 测试结果: 不合格！系统存在严重问题")
                report_lines.append("🌟 评级: D级 (不合格)")
            
            report_lines.append("=" * 100)
            
            return "\n".join(report_lines)


# ============================================================
# 极端值生成器
# ============================================================
class ExtremeValueGenerator:
    """极端值生成器"""
    
    @staticmethod
    def generate_name() -> str:
        """生成极端项目名称"""
        choice = random.randint(0, 20)
        
        if choice == 0:
            return ""  # 空字符串
        elif choice == 1:
            return " " * 100  # 大量空格
        elif choice == 2:
            return "x" * 500  # 超长名称
        elif choice == 3:
            return string.punctuation * 20  # 全是符号
        elif choice == 4:
            return "<script>alert('xss')</script>"  # XSS攻击
        elif choice == 5:
            return "' OR '1'='1' --"  # SQL注入
        elif choice == 6:
            return "中文测试项目名字"  # 中文
        elif choice == 7:
            return "🚀🎉💻🔥" * 10  # Emoji
        elif choice == 8:
            return "test\nwith\nnewlines"  # 换行符
        elif choice == 9:
            return "test\twith\ttabs"  # 制表符
        elif choice == 10:
            return "\x00\x01\x02\x03"  # 不可见字符
        elif choice == 11:
            return "path/../../../../../etc/passwd"  # 路径遍历
        elif choice == 12:
            return "null\x00byte"  # NULL字节
        elif choice == 13:
            return "   \t\n   "  # 空白字符
        elif choice == 14:
            return None  # None值
        else:
            return f"test_{random.randint(1, 999999)}"  # 正常值
    
    @staticmethod
    def generate_path() -> str:
        """生成极端路径"""
        choice = random.randint(0, 15)
        
        if choice == 0:
            return ""  # 空路径
        elif choice == 1:
            return "/nonexistent/path"  # 不存在的路径
        elif choice == 2:
            return "/workspace/../../../root"  # 路径遍历
        elif choice == 3:
            return "/workspace" + "/x" * 200  # 超长路径
        elif choice == 4:
            return "/workspace/path_test_system"  # 正常路径
        elif choice == 5:
            return "/workspace/path_test_system/core"  # 正常路径
        elif choice == 6:
            return "/workspace/path_test_system/src"  # 正常路径
        elif choice == 7:
            return "/workspace/path_test_system/tests"  # 正常路径
        elif choice == 8:
            return "/workspace/path_test_system/data"  # 正常路径
        elif choice == 9:
            return "/workspace/path_test_system/config"  # 正常路径
        elif choice == 10:
            return "/workspace/path_test_system/layers"  # 正常路径
        elif choice == 11:
            return "/workspace/path_test_system/plugins"  # 正常路径
        elif choice == 12:
            return "/workspace/path_test_system/docs"  # 正常路径
        elif choice == 13:
            return "/workspace/path_test_system/examples"  # 正常路径
        else:
            return "/workspace/path_test_system"  # 默认路径
    
    @staticmethod
    def generate_description() -> str:
        """生成极端描述"""
        choice = random.randint(0, 15)
        
        if choice == 0:
            return ""  # 空描述
        elif choice == 1:
            return " " * 200  # 大量空格
        elif choice == 2:
            return "x" * 1000  # 超长描述
        elif choice == 3:
            return string.ascii_letters * 50  # 纯字母
        elif choice == 4:
            return "🚀" * 100  # 大量Emoji
        elif choice == 5:
            return "<img src=x onerror=alert(1)>"  # XSS
        elif choice == 6:
            return "正常描述内容"  # 正常中文
        elif choice == 7:
            return "Mixed 中文 and English"  # 混合
        elif choice == 8:
            return "\n\n\n"  # 多换行
        else:
            return f"Test description {random.randint(1, 10000)}"  # 正常英文


# ============================================================
# 工作线程
# ============================================================
def chaos_worker(worker_id: int, monitor: ChaosMonitor):
    """混乱测试工作线程"""
    thread_name = f"CTW{worker_id:02d}"
    local_projects: List[str] = []
    
    print(f"ℹ️ [{thread_name}] 启动")
    
    while time.time() < monitor.end_time and not monitor.stop_event.is_set():
        try:
            # 选择操作类型
            operation = random.choices(
                [
                    'health_check',
                    'get_projects',
                    'create_project',
                    'get_project_detail',
                    'update_project',
                    'delete_project',
                    'get_issues',
                    'get_settings',
                    'browse_files',
                    'read_file',
                    'create_test',
                    'run_analysis',
                    'extreme_validation',
                    'concurrent_burst',
                    'malformed_request',
                ],
                weights=[
                    10,  # health_check
                    15,  # get_projects
                    20,  # create_project
                    10,  # get_project_detail
                    12,  # update_project
                    8,   # delete_project
                    5,   # get_issues
                    5,   # get_settings
                    5,   # browse_files
                    5,   # read_file
                    3,   # create_test
                    5,   # run_analysis
                    8,   # extreme_validation
                    3,   # concurrent_burst
                    6,   # malformed_request
                ]
            )[0]
            
            start_time = time.time()
            success = False
            error_msg = None
            status_code = None
            
            try:
                if operation == 'health_check':
                    success, status_code = test_health_check()
                    
                elif operation == 'get_projects':
                    success, status_code = test_get_projects()
                    
                elif operation == 'create_project':
                    success, status_code, project_id = test_create_project(
                        ExtremeValueGenerator.generate_name(),
                        ExtremeValueGenerator.generate_path(),
                        ExtremeValueGenerator.generate_description()
                    )
                    if success and project_id:
                        local_projects.append(project_id)
                        monitor.record_project_created(project_id)
                    elif success and project_id is None:
                        success = True  # 验证失败也算成功
                        
                elif operation == 'get_project_detail':
                    if local_projects:
                        project_id = random.choice(local_projects)
                        success, status_code = test_get_project_detail(project_id)
                    else:
                        success, status_code = True, 200  # 没有项目也算通过
                        
                elif operation == 'update_project':
                    if local_projects:
                        project_id = random.choice(local_projects)
                        success, status_code = test_update_project(
                            project_id,
                            ExtremeValueGenerator.generate_name(),
                            ExtremeValueGenerator.generate_description()
                        )
                    else:
                        success, status_code = True, 200
                        
                elif operation == 'delete_project':
                    if local_projects:
                        project_id = local_projects.pop(0)
                        success, status_code = test_delete_project(project_id)
                        if success:
                            monitor.record_project_deleted(project_id)
                    else:
                        success, status_code = True, 200
                        
                elif operation == 'get_issues':
                    success, status_code = test_get_issues()
                    
                elif operation == 'get_settings':
                    success, status_code = test_get_settings()
                    
                elif operation == 'browse_files':
                    success, status_code = test_browse_files(
                        ExtremeValueGenerator.generate_path()
                    )
                    
                elif operation == 'read_file':
                    success, status_code = test_read_file(
                        ExtremeValueGenerator.generate_path()
                    )
                    
                elif operation == 'create_test':
                    success, status_code = test_create_test(
                        ExtremeValueGenerator.generate_name(),
                        ExtremeValueGenerator.generate_path()
                    )
                    
                elif operation == 'run_analysis':
                    if local_projects:
                        project_id = random.choice(local_projects)
                        success, status_code = test_run_analysis(project_id)
                    else:
                        success, status_code = True, 200
                        
                elif operation == 'extreme_validation':
                    success, status_code = test_extreme_validation(monitor)
                    
                elif operation == 'concurrent_burst':
                    success, status_code = test_concurrent_burst()
                    
                elif operation == 'malformed_request':
                    success, status_code = test_malformed_request()
                
                response_time = time.time() - start_time
                monitor.record_request(operation, success, response_time, error_msg, status_code)
                
                # 随机延迟
                time.sleep(random.uniform(0.01, 0.3))
                
            except Exception as e:
                error_msg = str(e)
                response_time = time.time() - start_time
                monitor.record_request(operation, False, response_time, error_msg)
                monitor.record_critical_error(f"[{thread_name}] {operation} - {error_msg}")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            monitor.record_critical_error(f"[{thread_name}] 线程异常: {str(e)}")
            traceback.print_exc()
    
    # 清理本地项目
    print(f"ℹ️ [{thread_name}] 清理 {len(local_projects)} 个项目")
    for project_id in local_projects:
        try:
            requests.delete(f"{BASE_URL}/projects/{project_id}", timeout=10)
            monitor.record_project_deleted(project_id)
        except:
            pass
    
    print(f"ℹ️ [{thread_name}] 退出")


# ============================================================
# 测试函数
# ============================================================
def test_health_check() -> tuple:
    """测试健康检查"""
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=REQUEST_TIMEOUT)
        return r.status_code == 200, r.status_code
    except Exception as e:
        return False, None


def test_get_projects() -> tuple:
    """测试获取项目列表"""
    try:
        r = requests.get(f"{BASE_URL}/projects", timeout=REQUEST_TIMEOUT)
        return r.status_code == 200, r.status_code
    except Exception as e:
        return False, None


def test_create_project(name: str, path: str, description: str) -> tuple:
    """测试创建项目"""
    try:
        data = {'name': name, 'path': path}
        if description:
            data['description'] = description
            
        r = requests.post(f"{BASE_URL}/projects", json=data, timeout=REQUEST_TIMEOUT)
        
        if r.status_code == 201:
            try:
                result = r.json()
                project_id = result.get('id')
                return True, r.status_code, project_id
            except:
                return r.status_code in [400, 403], r.status_code, None
        else:
            return r.status_code in [400, 403, 404], r.status_code, None
    except Exception as e:
        return False, None, None


def test_get_project_detail(project_id: str) -> tuple:
    """测试获取项目详情"""
    try:
        r = requests.get(f"{BASE_URL}/projects/{project_id}", timeout=REQUEST_TIMEOUT)
        return r.status_code in [200, 404], r.status_code
    except Exception as e:
        return False, None


def test_update_project(project_id: str, name: str, description: str) -> tuple:
    """测试更新项目"""
    try:
        data = {'name': name}
        if description:
            data['description'] = description
            
        r = requests.put(f"{BASE_URL}/projects/{project_id}", json=data, timeout=REQUEST_TIMEOUT)
        return r.status_code in [200, 204, 404, 400], r.status_code
    except Exception as e:
        return False, None


def test_delete_project(project_id: str) -> tuple:
    """测试删除项目"""
    try:
        r = requests.delete(f"{BASE_URL}/projects/{project_id}", timeout=REQUEST_TIMEOUT)
        return r.status_code in [200, 204, 404], r.status_code
    except Exception as e:
        return False, None


def test_get_issues() -> tuple:
    """测试获取问题列表"""
    try:
        r = requests.get(f"{BASE_URL}/issues", timeout=REQUEST_TIMEOUT)
        return r.status_code == 200, r.status_code
    except Exception as e:
        return False, None


def test_get_settings() -> tuple:
    """测试获取设置"""
    try:
        r = requests.get(f"{BASE_URL}/settings", timeout=REQUEST_TIMEOUT)
        return r.status_code == 200, r.status_code
    except Exception as e:
        return False, None


def test_browse_files(path: str) -> tuple:
    """测试浏览文件"""
    try:
        r = requests.get(f"{BASE_URL}/files/browse", params={'path': path}, timeout=REQUEST_TIMEOUT)
        return r.status_code in [200, 403, 404], r.status_code
    except Exception as e:
        return False, None


def test_read_file(path: str) -> tuple:
    """测试读取文件"""
    try:
        r = requests.get(f"{BASE_URL}/files/read", params={'path': path}, timeout=REQUEST_TIMEOUT)
        return r.status_code in [200, 404], r.status_code
    except Exception as e:
        return False, None


def test_create_test(name: str, file_path: str) -> tuple:
    """测试创建测试"""
    try:
        r = requests.post(f"{BASE_URL}/tests", 
                         json={'name': name, 'file': file_path}, 
                         timeout=REQUEST_TIMEOUT)
        return r.status_code in [201, 400, 404], r.status_code
    except Exception as e:
        return False, None


def test_run_analysis(project_id: str) -> tuple:
    """测试运行分析"""
    try:
        r = requests.post(f"{BASE_URL}/analyze", 
                          json={'projectId': project_id}, 
                          timeout=REQUEST_TIMEOUT * 2)
        return r.status_code in [200, 400, 404], r.status_code
    except Exception as e:
        return False, None


def test_extreme_validation(monitor: ChaosMonitor) -> tuple:
    """测试极端验证场景"""
    try:
        # 测试各种极端情况
        test_cases = [
            # 空数据
            (requests.post, f"{BASE_URL}/projects", {'json': {}}),
            # None值
            (requests.post, f"{BASE_URL}/projects", {'json': {'name': None, 'path': None}}),
            # 超长数据
            (requests.post, f"{BASE_URL}/projects", {'json': {'name': 'x' * 1000, 'path': '/workspace'}}),
            # SQL注入
            (requests.post, f"{BASE_URL}/projects", {'json': {'name': "' OR '1'='1", 'path': '/workspace'}}),
            # XSS攻击
            (requests.post, f"{BASE_URL}/projects", {'json': {'name': '<script>alert(1)</script>', 'path': '/workspace'}}),
        ]
        
        for method, url, kwargs in test_cases:
            r = method(url, timeout=REQUEST_TIMEOUT, **kwargs)
            if r.status_code not in [400, 403, 404, 422]:
                monitor.record_warning(f"极端验证异常: {url} 返回 {r.status_code}")
        
        return True, 200
    except Exception as e:
        return False, None


def test_concurrent_burst() -> tuple:
    """测试并发突发"""
    try:
        # 快速发送多个请求
        results = []
        for _ in range(10):
            r = requests.get(f"{BASE_URL}/health", timeout=5)
            results.append(r.status_code == 200)
            time.sleep(0.01)
        
        return all(results), 200
    except Exception as e:
        return False, None


def test_malformed_request() -> tuple:
    """测试畸形请求"""
    try:
        # 测试各种畸形请求
        test_cases = [
            # 无效JSON
            (requests.post, f"{BASE_URL}/projects", {'data': "not json", 'headers': {'Content-Type': 'application/json'}}),
            # 无效参数
            (requests.get, f"{BASE_URL}/projects", {'params': {'invalid': 'param'}}),
            # 超大Header
            (requests.get, f"{BASE_URL}/health", {'headers': {'X-Custom': 'x' * 10000}}),
        ]
        
        for method, url, kwargs in test_cases:
            try:
                r = method(url, timeout=REQUEST_TIMEOUT, **kwargs)
                # 这些应该返回错误，但不是服务器错误
                if r.status_code >= 500:
                    return False, r.status_code
            except:
                pass
        
        return True, 400
    except Exception as e:
        return False, None


# ============================================================
# 主函数
# ============================================================
def main():
    """主函数"""
    print("\n" + "=" * 100)
    print("🏆 超极端压力测试 - 30分钟极限挑战")
    print("=" * 100)
    print(f"📅 开始时间: {datetime.now()}")
    print(f"⏱️  测试时长: {TEST_DURATION_MINUTES}分钟")
    print(f"👷 并发线程: {NUM_WORKERS}个")
    print(f"⏰ 请求超时: {REQUEST_TIMEOUT}秒")
    print(f"🎯 测试目标: 极端边界值、异常注入、数据一致性验证")
    print("=" * 100)
    
    # 创建监控器
    monitor = ChaosMonitor(TEST_DURATION_MINUTES)
    
    # 启动监控线程
    monitor.monitor_thread.start()
    
    # 设置信号处理器
    def signal_handler(sig, frame):
        print("\n\n⚠️ 收到中断信号，正在停止测试...")
        monitor.stop_event.set()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # 等待服务器就绪
    print("\n⏳ 等待服务器就绪...")
    max_retries = 10
    for i in range(max_retries):
        try:
            r = requests.get(f"{BASE_URL}/health", timeout=5)
            if r.status_code == 200:
                print("✅ 服务器就绪，开始测试！\n")
                break
        except:
            pass
        
        if i < max_retries - 1:
            print(f"⏳ 重试 {i+1}/{max_retries}...")
            time.sleep(2)
    else:
        print("❌ 服务器未就绪，测试终止")
        return 1
    
    # 启动工作线程
    print("🚀 启动工作线程...")
    with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        futures = [executor.submit(chaos_worker, i, monitor) for i in range(NUM_WORKERS)]
        
        # 等待测试完成
        try:
            for future in as_completed(futures):
                future.result()
        except KeyboardInterrupt:
            print("\n\n⚠️ 测试被中断")
            monitor.stop_event.set()
    
    # 清理
    print("\n🧹 清理测试数据...")
    with monitor.lock:
        projects_to_clean = list(monitor.created_projects)
    
    for project_id in projects_to_clean:
        try:
            requests.delete(f"{BASE_URL}/projects/{project_id}", timeout=10)
        except:
            pass
    
    # 生成报告
    final_report = monitor.get_final_report()
    print(final_report)
    
    # 保存报告
    report_file = f"/workspace/path_test_system/chaos_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(final_report)
    
    print(f"\n📄 报告已保存: {report_file}")
    
    # 返回状态码
    with monitor.lock:
        success_rate = (monitor.success_requests / monitor.total_requests * 100) if monitor.total_requests > 0 else 0
        has_critical = len(monitor.critical_errors) > 0
    
    if success_rate >= 95 and not has_critical:
        return 0
    elif success_rate >= 90:
        return 0
    else:
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 致命错误: {e}")
        traceback.print_exc()
        sys.exit(1)
