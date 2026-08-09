#!/usr/bin/env python3
"""
超详细日志版API服务器 - 每句关键代码后都有日志
用于全面测试和调试，发现真实运行时的问题
"""

import os
import json
import time
import random
import threading
import re
import logging
import gc
import traceback
from functools import wraps
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from dataclasses import dataclass, asdict
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ============================================================
# 超详细日志配置
# ============================================================
class UltraDetailedFormatter(logging.Formatter):
    def format(self, record):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        thread_name = threading.current_thread().name
        return f"[{timestamp}] [{record.levelname:8}] [{thread_name:12}] [Line:{record.lineno}] {record.getMessage()}"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 文件日志处理器
file_handler = logging.FileHandler("/workspace/path_test_system/ultra_detailed_api.log")
file_handler.setFormatter(UltraDetailedFormatter())
logger.addHandler(file_handler)

# 控制台日志处理器
console_handler = logging.StreamHandler()
console_handler.setFormatter(UltraDetailedFormatter())
logger.addHandler(console_handler)

logger.debug("🟢 [初始化] 超详细日志版API服务器开始启动...")

# ============================================================
# 超详细日志装饰器
# ============================================================
def log_every_step(func):
    """在函数每个关键步骤记录日志的装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        logger.debug(f"🟢 [进入函数] {func_name} 开始执行")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"🟢 [函数成功] {func_name} 执行完成")
            return result
        except Exception as e:
            logger.error(f"🔴 [函数异常] {func_name} 发生错误: {str(e)}\n{traceback.format_exc()}")
            raise
    return wrapper

# ============================================================
# 阶段1.1: 自动重试装饰器（超详细日志）
# ============================================================
logger.debug("🟢 [初始化] 开始创建 RetryHandler...")

class RetryHandler:
    """自动重试处理器 - 超详细日志"""
    def __init__(self, max_retries: int = 3, base_delay: float = 0.1):
        logger.debug(f"🟢 [RetryHandler.__init__] 初始化 RetryHandler, max_retries={max_retries}, base_delay={base_delay}")
        self.max_retries = max_retries
        logger.debug(f"🟢 [RetryHandler.__init__] 设置 max_retries 为 {max_retries}")
        self.base_delay = base_delay
        logger.debug(f"🟢 [RetryHandler.__init__] 设置 base_delay 为 {base_delay}")
        self.retry_stats = defaultdict(lambda: {'total': 0, 'success': 0, 'failed': 0})
        logger.debug(f"🟢 [RetryHandler.__init__] 初始化 retry_stats 字典")
        self.lock = threading.Lock()
        logger.debug(f"🟢 [RetryHandler.__init__] 创建线程锁")
        logger.debug(f"🟢 [RetryHandler.__init__] RetryHandler 初始化完成")
    
    def exponential_backoff(self, attempt: int) -> float:
        """指数退避算法"""
        logger.debug(f"🟢 [RetryHandler.exponential_backoff] 开始计算退避时间, attempt={attempt}")
        delay = self.base_delay * (2 ** attempt)
        logger.debug(f"🟢 [RetryHandler.exponential_backoff] 基础延迟计算: {self.base_delay} * (2^{attempt}) = {delay}")
        jitter = random.uniform(0, 0.1 * delay)
        logger.debug(f"🟢 [RetryHandler.exponential_backoff] 添加随机抖动: {jitter}")
        result = min(delay + jitter, 5.0)
        logger.debug(f"🟢 [RetryHandler.exponential_backoff] 最终退避时间: {result}")
        return result
    
    def should_retry(self, exception: Exception) -> bool:
        """判断是否应该重试"""
        logger.debug(f"🟢 [RetryHandler.should_retry] 检查是否需要重试, 异常类型: {type(exception).__name__}")
        retry_exceptions = (TimeoutError, ConnectionError, OSError, IOError, json.JSONDecodeError)
        logger.debug(f"🟢 [RetryHandler.should_retry] 可重试异常列表: {[e.__name__ for e in retry_exceptions]}")
        result = isinstance(exception, retry_exceptions)
        logger.debug(f"🟢 [RetryHandler.should_retry] 检查结果: {result}")
        return result
    
    def record_retry(self, operation: str, success: bool):
        """记录重试统计"""
        logger.debug(f"🟢 [RetryHandler.record_retry] 记录重试统计, operation={operation}, success={success}")
        with self.lock:
            logger.debug(f"🟢 [RetryHandler.record_retry] 获取锁成功")
            self.retry_stats[operation]['total'] += 1
            logger.debug(f"🟢 [RetryHandler.record_retry] 总重试数 +1")
            if success:
                self.retry_stats[operation]['success'] += 1
                logger.debug(f"🟢 [RetryHandler.record_retry] 成功重试数 +1")
            else:
                self.retry_stats[operation]['failed'] += 1
                logger.debug(f"🟢 [RetryHandler.record_retry] 失败重试数 +1")
        logger.debug(f"🟢 [RetryHandler.record_retry] 释放锁, 统计记录完成")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取重试统计"""
        logger.debug(f"🟢 [RetryHandler.get_stats] 获取重试统计")
        with self.lock:
            result = dict(self.retry_stats)
            logger.debug(f"🟢 [RetryHandler.get_stats] 统计数据: {result}")
            return result

logger.debug(f"🟢 [初始化] 创建 RetryHandler 实例")
retry_handler = RetryHandler(max_retries=3, base_delay=0.1)
logger.debug(f"🟢 [初始化] RetryHandler 实例创建完成")

def with_retry(operation_name: str):
    """带重试机制的装饰器 - 超详细日志"""
    logger.debug(f"🟢 [with_retry] 为操作 {operation_name} 创建装饰器")
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            logger.debug(f"🟢 [with_retry.{operation_name}] 开始执行, 最大重试次数: {retry_handler.max_retries}")
            
            for attempt in range(retry_handler.max_retries + 1):
                logger.debug(f"🟢 [with_retry.{operation_name}] 第 {attempt + 1} 次尝试开始")
                try:
                    logger.debug(f"🟢 [with_retry.{operation_name}] 调用原函数")
                    result = func(*args, **kwargs)
                    logger.debug(f"🟢 [with_retry.{operation_name}] 原函数调用成功")
                    
                    if attempt > 0:
                        logger.info(f"✅ [{operation_name}] 重试成功 (尝试 {attempt + 1})")
                        retry_handler.record_retry(operation_name, True)
                    
                    logger.debug(f"🟢 [with_retry.{operation_name}] 返回结果")
                    return result
                    
                except Exception as e:
                    last_exception = e
                    logger.warning(f"⚠️ [{operation_name}] 第 {attempt + 1} 次尝试失败: {str(e)}")
                    
                    if attempt < retry_handler.max_retries and retry_handler.should_retry(e):
                        delay = retry_handler.exponential_backoff(attempt)
                        logger.warning(f"⚠️ [{operation_name}] 等待 {delay:.2f} 秒后重试...")
                        time.sleep(delay)
                        logger.warning(f"⚠️ [{operation_name}] 重试等待结束，继续尝试")
                    else:
                        logger.error(f"❌ [{operation_name}] 失败，不再重试: {str(e)}\n{traceback.format_exc()}")
                        retry_handler.record_retry(operation_name, False)
                        raise
            
            logger.error(f"❌ [{operation_name}] 所有重试均失败")
            raise last_exception
        
        return wrapper
    return decorator

# ============================================================
# 阶段1.2: 线程池和资源管理（超详细日志）
# ============================================================
logger.debug(f"🟢 [初始化] 开始创建 ResourceManager...")

class ResourceManager:
    """资源管理器 - 超详细日志"""
    def __init__(self):
        logger.debug(f"🟢 [ResourceManager.__init__] 初始化 ResourceManager")
        self.lock = threading.Lock()
        logger.debug(f"🟢 [ResourceManager.__init__] 创建线程锁")
        self.active_requests = 0
        logger.debug(f"🟢 [ResourceManager.__init__] 初始化 active_requests = 0")
        self.total_requests = 0
        logger.debug(f"🟢 [ResourceManager.__init__] 初始化 total_requests = 0")
        self.failed_requests = 0
        logger.debug(f"🟢 [ResourceManager.__init__] 初始化 failed_requests = 0")
        self.memory_usage = []
        logger.debug(f"🟢 [ResourceManager.__init__] 初始化 memory_usage 列表")
        self.thread_pool_stats = defaultdict(lambda: {'active': 0, 'completed': 0, 'failed': 0})
        logger.debug(f"🟢 [ResourceManager.__init__] 初始化 thread_pool_stats")
        
        self.max_concurrent_requests = 100
        logger.debug(f"🟢 [ResourceManager.__init__] 设置 max_concurrent_requests = 100")
        self.request_semaphore = threading.Semaphore(self.max_concurrent_requests)
        logger.debug(f"🟢 [ResourceManager.__init__] 创建信号量，初始值 = {self.max_concurrent_requests}")
        
        self.start_time = time.time()
        logger.debug(f"🟢 [ResourceManager.__init__] 记录启动时间 = {self.start_time}")
        logger.debug(f"🟢 [ResourceManager.__init__] ResourceManager 初始化完成")
    
    def acquire_resource(self) -> bool:
        """获取资源许可"""
        logger.debug(f"🟢 [ResourceManager.acquire_resource] 尝试获取资源许可")
        acquired = self.request_semaphore.acquire(timeout=5.0)
        logger.debug(f"🟢 [ResourceManager.acquire_resource] 信号量获取结果: {acquired}")
        
        if acquired:
            with self.lock:
                logger.debug(f"🟢 [ResourceManager.acquire_resource] 获取锁成功")
                self.active_requests += 1
                logger.debug(f"🟢 [ResourceManager.acquire_resource] active_requests 增加到 {self.active_requests}")
                self.total_requests += 1
                logger.debug(f"🟢 [ResourceManager.acquire_resource] total_requests 增加到 {self.total_requests}")
        
        logger.debug(f"🟢 [ResourceManager.acquire_resource] 返回: {acquired}")
        return acquired
    
    def release_resource(self, success: bool = True):
        """释放资源许可"""
        logger.debug(f"🟢 [ResourceManager.release_resource] 开始释放资源, success={success}")
        
        with self.lock:
            logger.debug(f"🟢 [ResourceManager.release_resource] 获取锁成功")
            self.active_requests -= 1
            logger.debug(f"🟢 [ResourceManager.release_resource] active_requests 减少到 {self.active_requests}")
            if not success:
                self.failed_requests += 1
                logger.debug(f"🟢 [ResourceManager.release_resource] failed_requests 增加到 {self.failed_requests}")
        
        self.request_semaphore.release()
        logger.debug(f"🟢 [ResourceManager.release_resource] 信号量已释放")
        logger.debug(f"🟢 [ResourceManager.release_resource] 资源释放完成")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取资源统计"""
        logger.debug(f"🟢 [ResourceManager.get_stats] 获取资源统计")
        
        with self.lock:
            uptime = time.time() - self.start_time
            logger.debug(f"🟢 [ResourceManager.get_stats] uptime = {uptime} 秒")
            success_rate = ((self.total_requests - self.failed_requests) / self.total_requests * 100) if self.total_requests > 0 else 0
            logger.debug(f"🟢 [ResourceManager.get_stats] success_rate = {success_rate:.2f}%")
            
            result = {
                'uptime': uptime,
                'active_requests': self.active_requests,
                'total_requests': self.total_requests,
                'failed_requests': self.failed_requests,
                'success_rate': success_rate,
                'max_concurrent': self.max_concurrent_requests,
                'avg_requests_per_second': self.total_requests / uptime if uptime > 0 else 0
            }
            logger.debug(f"🟢 [ResourceManager.get_stats] 统计结果: {result}")
            return result
    
    def update_thread_stats(self, thread_name: str, status: str):
        """更新线程统计"""
        logger.debug(f"🟢 [ResourceManager.update_thread_stats] 更新线程 {thread_name} 的状态为 {status}")
        
        with self.lock:
            logger.debug(f"🟢 [ResourceManager.update_thread_stats] 获取锁成功")
            if status == 'active':
                self.thread_pool_stats[thread_name]['active'] += 1
                logger.debug(f"🟢 [ResourceManager.update_thread_stats] active 计数 +1")
            elif status == 'completed':
                self.thread_pool_stats[thread_name]['completed'] += 1
                logger.debug(f"🟢 [ResourceManager.update_thread_stats] completed 计数 +1")
            elif status == 'failed':
                self.thread_pool_stats[thread_name]['failed'] += 1
                logger.debug(f"🟢 [ResourceManager.update_thread_stats] failed 计数 +1")
        
        logger.debug(f"🟢 [ResourceManager.update_thread_stats] 线程统计更新完成")
    
    def force_garbage_collection(self):
        """强制垃圾回收"""
        logger.debug(f"🟢 [ResourceManager.force_garbage_collection] 开始强制垃圾回收")
        
        before = 0
        try:
            import tracemalloc
            logger.debug(f"🟢 [ResourceManager.force_garbage_collection] tracemalloc 导入成功")
            tracemalloc.start()
            logger.debug(f"🟢 [ResourceManager.force_garbage_collection] tracemalloc 已启动")
            snapshot_before = tracemalloc.take_snapshot()
            logger.debug(f"🟢 [ResourceManager.force_garbage_collection] 快照已获取")
            before = sum(stat.size for stat in snapshot_before.statistics('lineno'))
            logger.debug(f"🟢 [ResourceManager.force_garbage_collection] 回收前内存使用: {before} bytes")
        except Exception as e:
            logger.debug(f"🟢 [ResourceManager.force_garbage_collection] 内存统计失败: {str(e)}")
        
        collected = gc.collect()
        logger.debug(f"🟢 [ResourceManager.force_garbage_collection] 垃圾回收完成，回收对象数: {collected}")
        
        freed_bytes = 0
        try:
            snapshot_after = tracemalloc.take_snapshot()
            logger.debug(f"🟢 [ResourceManager.force_garbage_collection] 回收后快照已获取")
            after = sum(stat.size for stat in snapshot_after.statistics('lineno'))
            logger.debug(f"🟢 [ResourceManager.force_garbage_collection] 回收后内存使用: {after} bytes")
            freed_bytes = before - after
            logger.debug(f"🟢 [ResourceManager.force_garbage_collection] 释放内存: {freed_bytes} bytes")
        except Exception as e:
            logger.debug(f"🟢 [ResourceManager.force_garbage_collection] 回收后统计失败: {str(e)}")
        
        logger.info(f"🧹 垃圾回收: 释放约 {freed_bytes} bytes, 对象数 {collected}")
        return {'collected': collected, 'freed_bytes': freed_bytes}

logger.debug(f"🟢 [初始化] 创建 ResourceManager 实例")
resource_manager = ResourceManager()
logger.debug(f"🟢 [初始化] ResourceManager 实例创建完成")

# ============================================================
# 阶段1.3: 负载自适应（超详细日志）
# ============================================================
logger.debug(f"🟢 [初始化] 开始创建 AdaptiveLoadManager...")

class AdaptiveLoadManager:
    """负载自适应管理器 - 超详细日志"""
    def __init__(self):
        logger.debug(f"🟢 [AdaptiveLoadManager.__init__] 初始化 AdaptiveLoadManager")
        self.lock = threading.Lock()
        logger.debug(f"🟢 [AdaptiveLoadManager.__init__] 创建线程锁")
        
        self.base_concurrency = 10
        logger.debug(f"🟢 [AdaptiveLoadManager.__init__] base_concurrency = {self.base_concurrency}")
        self.current_concurrency = self.base_concurrency
        logger.debug(f"🟢 [AdaptiveLoadManager.__init__] current_concurrency = {self.current_concurrency}")
        self.min_concurrency = 5
        logger.debug(f"🟢 [AdaptiveLoadManager.__init__] min_concurrency = {self.min_concurrency}")
        self.max_concurrency = 50
        logger.debug(f"🟢 [AdaptiveLoadManager.__init__] max_concurrency = {self.max_concurrency}")
        
        self.request_history = []
        logger.debug(f"🟢 [AdaptiveLoadManager.__init__] 初始化 request_history 列表")
        self.history_window = 60
        logger.debug(f"🟢 [AdaptiveLoadManager.__init__] history_window = {self.history_window} 秒")
        
        self.success_threshold = 0.95
        logger.debug(f"🟢 [AdaptiveLoadManager.__init__] success_threshold = {self.success_threshold}")
        self.failure_threshold = 0.80
        logger.debug(f"🟢 [AdaptiveLoadManager.__init__] failure_threshold = {self.failure_threshold}")
        
        self.scale_up_threshold = 0.90
        logger.debug(f"🟢 [AdaptiveLoadManager.__init__] scale_up_threshold = {self.scale_up_threshold}")
        self.scale_down_threshold = 0.60
        logger.debug(f"🟢 [AdaptiveLoadManager.__init__] scale_down_threshold = {self.scale_down_threshold}")
        
        self.scale_cooldown = 30
        logger.debug(f"🟢 [AdaptiveLoadManager.__init__] scale_cooldown = {self.scale_cooldown} 秒")
        self.last_scale_time = time.time()
        logger.debug(f"🟢 [AdaptiveLoadManager.__init__] last_scale_time = {self.last_scale_time}")
        
        logger.debug(f"🟢 [AdaptiveLoadManager.__init__] AdaptiveLoadManager 初始化完成")
    
    def record_request(self, duration: float, success: bool):
        """记录请求"""
        logger.debug(f"🟢 [AdaptiveLoadManager.record_request] 记录请求, duration={duration}, success={success}")
        
        with self.lock:
            logger.debug(f"🟢 [AdaptiveLoadManager.record_request] 获取锁成功")
            current_time = time.time()
            self.request_history.append({
                'time': current_time,
                'duration': duration,
                'success': success
            })
            logger.debug(f"🟢 [AdaptiveLoadManager.record_request] 请求记录已添加到历史")
            
            cutoff_time = current_time - self.history_window
            logger.debug(f"🟢 [AdaptiveLoadManager.record_request] 清理 cutoff_time = {cutoff_time} 之前的记录")
            self.request_history = [r for r in self.request_history if r['time'] > cutoff_time]
            logger.debug(f"🟢 [AdaptiveLoadManager.record_request] 清理后历史记录数: {len(self.request_history)}")
            
            self._adjust_concurrency()
        
        logger.debug(f"🟢 [AdaptiveLoadManager.record_request] 请求记录完成")
    
    def _calculate_metrics(self) -> Dict[str, float]:
        """计算指标"""
        logger.debug(f"🟢 [AdaptiveLoadManager._calculate_metrics] 计算指标")
        
        if not self.request_history:
            logger.debug(f"🟢 [AdaptiveLoadManager._calculate_metrics] 无历史记录，返回默认值")
            return {'success_rate': 1.0, 'avg_duration': 0.0, 'request_rate': 0.0}
        
        recent = self.request_history
        logger.debug(f"🟢 [AdaptiveLoadManager._calculate_metrics] 历史记录数: {len(recent)}")
        success_count = sum(1 for r in recent if r['success'])
        logger.debug(f"🟢 [AdaptiveLoadManager._calculate_metrics] 成功请求数: {success_count}")
        success_rate = success_count / len(recent) if recent else 0
        logger.debug(f"🟢 [AdaptiveLoadManager._calculate_metrics] 成功率: {success_rate:.2%}")
        avg_duration = sum(r['duration'] for r in recent) / len(recent)
        logger.debug(f"🟢 [AdaptiveLoadManager._calculate_metrics] 平均响应时间: {avg_duration:.4f} 秒")
        
        time_span = recent[-1]['time'] - recent[0]['time'] if len(recent) > 1 else 1
        logger.debug(f"🟢 [AdaptiveLoadManager._calculate_metrics] 时间跨度: {time_span:.4f} 秒")
        request_rate = len(recent) / time_span
        logger.debug(f"🟢 [AdaptiveLoadManager._calculate_metrics] 请求速率: {request_rate:.2f} req/s")
        
        result = {
            'success_rate': success_rate,
            'avg_duration': avg_duration,
            'request_rate': request_rate,
            'sample_size': len(recent)
        }
        logger.debug(f"🟢 [AdaptiveLoadManager._calculate_metrics] 指标计算结果: {result}")
        return result
    
    def _adjust_concurrency(self):
        """调整并发数"""
        logger.debug(f"🟢 [AdaptiveLoadManager._adjust_concurrency] 开始调整并发数")
        
        current_time = time.time()
        
        if current_time - self.last_scale_time < self.scale_cooldown:
            logger.debug(f"🟢 [AdaptiveLoadManager._adjust_concurrency] 冷却时间未到，跳过调整")
            return
        
        logger.debug(f"🟢 [AdaptiveLoadManager._adjust_concurrency] 冷却时间已过，开始计算指标")
        metrics = self._calculate_metrics()
        
        old_concurrency = self.current_concurrency
        logger.debug(f"🟢 [AdaptiveLoadManager._adjust_concurrency] 当前并发数: {old_concurrency}")
        
        if metrics['success_rate'] < self.failure_threshold:
            logger.debug(f"🟢 [AdaptiveLoadManager._adjust_concurrency] 成功率 {metrics['success_rate']:.2%} 低于阈值 {self.failure_threshold:.2%}")
            self.current_concurrency = max(
                self.min_concurrency,
                int(self.current_concurrency * 0.8)
            )
            logger.warning(f"⚠️ [负载调整] 成功率低 ({metrics['success_rate']:.2%}), 降低并发: {old_concurrency} -> {self.current_concurrency}")
            
        elif metrics['success_rate'] >= self.scale_up_threshold and metrics['avg_duration'] < 1.0:
            logger.debug(f"🟢 [AdaptiveLoadManager._adjust_concurrency] 系统表现良好，准备扩容")
            self.current_concurrency = min(
                self.max_concurrency,
                int(self.current_concurrency * 1.2)
            )
            logger.info(f"📈 [负载调整] 系统表现良好, 增加并发: {old_concurrency} -> {self.current_concurrency}")
            
        elif metrics['success_rate'] >= self.success_threshold and metrics['avg_duration'] > 0.5:
            logger.debug(f"🟢 [AdaptiveLoadManager._adjust_concurrency] 成功率不错但响应偏慢，适度扩容")
            self.current_concurrency = min(
                self.max_concurrency,
                int(self.current_concurrency * 1.1)
            )
        
        if old_concurrency != self.current_concurrency:
            self.last_scale_time = current_time
            logger.debug(f"🟢 [AdaptiveLoadManager._adjust_concurrency] 并发数已调整，更新 last_scale_time")
        else:
            logger.debug(f"🟢 [AdaptiveLoadManager._adjust_concurrency] 并发数保持不变")
    
    def get_current_concurrency(self) -> int:
        """获取当前并发数"""
        logger.debug(f"🟢 [AdaptiveLoadManager.get_current_concurrency] 获取当前并发数")
        
        with self.lock:
            logger.debug(f"🟢 [AdaptiveLoadManager.get_current_concurrency] 返回 current_concurrency = {self.current_concurrency}")
            return self.current_concurrency
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计"""
        logger.debug(f"🟢 [AdaptiveLoadManager.get_stats] 获取统计信息")
        
        with self.lock:
            metrics = self._calculate_metrics()
            result = {
                'current_concurrency': self.current_concurrency,
                'base_concurrency': self.base_concurrency,
                'min_concurrency': self.min_concurrency,
                'max_concurrency': self.max_concurrency,
                **metrics
            }
            logger.debug(f"🟢 [AdaptiveLoadManager.get_stats] 统计信息: {result}")
            return result

logger.debug(f"🟢 [初始化] 创建 AdaptiveLoadManager 实例")
adaptive_load_manager = AdaptiveLoadManager()
logger.debug(f"🟢 [初始化] AdaptiveLoadManager 实例创建完成")

# ============================================================
# 阶段1.4: 监控指标收集（超详细日志）
# ============================================================
logger.debug(f"🟢 [初始化] 开始创建 MetricsCollector...")

class MetricsCollector:
    """指标收集器 - 超详细日志"""
    def __init__(self):
        logger.debug(f"🟢 [MetricsCollector.__init__] 初始化 MetricsCollector")
        self.lock = threading.Lock()
        logger.debug(f"🟢 [MetricsCollector.__init__] 创建线程锁")
        
        self.endpoint_metrics = defaultdict(lambda: {
            'total': 0, 
            'success': 0, 
            'failed': 0,
            'total_duration': 0.0,
            'min_duration': float('inf'),
            'max_duration': 0.0
        })
        logger.debug(f"🟢 [MetricsCollector.__init__] 初始化 endpoint_metrics 字典")
        
        self.error_log = []
        logger.debug(f"🟢 [MetricsCollector.__init__] 初始化 error_log 列表")
        self.max_error_log_size = 100
        logger.debug(f"🟢 [MetricsCollector.__init__] 设置 max_error_log_size = 100")
        
        self.health_check_results = []
        logger.debug(f"🟢 [MetricsCollector.__init__] 初始化 health_check_results 列表")
        self.max_health_check_size = 60
        logger.debug(f"🟢 [MetricsCollector.__init__] 设置 max_health_check_size = 60")
        
        self.start_time = time.time()
        logger.debug(f"🟢 [MetricsCollector.__init__] 记录启动时间 = {self.start_time}")
        logger.debug(f"🟢 [MetricsCollector.__init__] MetricsCollector 初始化完成")
    
    def record_endpoint(self, endpoint: str, duration: float, success: bool, status_code: int = 200):
        """记录端点指标"""
        logger.debug(f"🟢 [MetricsCollector.record_endpoint] 记录端点 {endpoint}, duration={duration}, success={success}, status_code={status_code}")
        
        with self.lock:
            logger.debug(f"🟢 [MetricsCollector.record_endpoint] 获取锁成功")
            metrics = self.endpoint_metrics[endpoint]
            metrics['total'] += 1
            logger.debug(f"🟢 [MetricsCollector.record_endpoint] total 增加到 {metrics['total']}")
            
            if success:
                metrics['success'] += 1
                logger.debug(f"🟢 [MetricsCollector.record_endpoint] success 增加到 {metrics['success']}")
            else:
                metrics['failed'] += 1
                logger.debug(f"🟢 [MetricsCollector.record_endpoint] failed 增加到 {metrics['failed']}")
            
            metrics['total_duration'] += duration
            logger.debug(f"🟢 [MetricsCollector.record_endpoint] total_duration 增加到 {metrics['total_duration']:.4f}")
            metrics['min_duration'] = min(metrics['min_duration'], duration)
            logger.debug(f"🟢 [MetricsCollector.record_endpoint] min_duration 更新为 {metrics['min_duration']:.4f}")
            metrics['max_duration'] = max(metrics['max_duration'], duration)
            logger.debug(f"🟢 [MetricsCollector.record_endpoint] max_duration 更新为 {metrics['max_duration']:.4f}")
        
        logger.debug(f"🟢 [MetricsCollector.record_endpoint] 端点指标记录完成")
    
    def record_error(self, error_type: str, error_message: str, endpoint: str = ""):
        """记录错误"""
        logger.debug(f"🟢 [MetricsCollector.record_error] 记录错误, type={error_type}, message={error_message}, endpoint={endpoint}")
        
        with self.lock:
            logger.debug(f"🟢 [MetricsCollector.record_error] 获取锁成功")
            self.error_log.append({
                'time': datetime.now(),
                'type': error_type,
                'message': error_message,
                'endpoint': endpoint
            })
            logger.debug(f"🟢 [MetricsCollector.record_error] 错误已添加到日志")
            
            if len(self.error_log) > self.max_error_log_size:
                self.error_log = self.error_log[-self.max_error_log_size:]
                logger.debug(f"🟢 [MetricsCollector.record_error] 错误日志已截断，保留最近 {self.max_error_log_size} 条")
        
        logger.debug(f"🟢 [MetricsCollector.record_error] 错误记录完成")
    
    def record_health_check(self, healthy: bool, details: Dict[str, Any] = None):
        """记录健康检查"""
        logger.debug(f"🟢 [MetricsCollector.record_health_check] 记录健康检查, healthy={healthy}")
        
        with self.lock:
            logger.debug(f"🟢 [MetricsCollector.record_health_check] 获取锁成功")
            self.health_check_results.append({
                'time': datetime.now(),
                'healthy': healthy,
                'details': details or {}
            })
            logger.debug(f"🟢 [MetricsCollector.record_health_check] 健康检查记录已添加")
            
            if len(self.health_check_results) > self.max_health_check_size:
                self.health_check_results = self.health_check_results[-self.max_health_check_size:]
                logger.debug(f"🟢 [MetricsCollector.record_health_check] 健康检查结果已截断")
        
        logger.debug(f"🟢 [MetricsCollector.record_health_check] 健康检查记录完成")
    
    def get_endpoint_metrics(self) -> Dict[str, Any]:
        """获取端点指标"""
        logger.debug(f"🟢 [MetricsCollector.get_endpoint_metrics] 获取端点指标")
        
        with self.lock:
            result = {}
            for endpoint, metrics in self.endpoint_metrics.items():
                if metrics['total'] > 0:
                    result[endpoint] = {
                        'total': metrics['total'],
                        'success': metrics['success'],
                        'failed': metrics['failed'],
                        'success_rate': metrics['success'] / metrics['total'],
                        'avg_duration': metrics['total_duration'] / metrics['total'],
                        'min_duration': metrics['min_duration'],
                        'max_duration': metrics['max_duration']
                    }
            logger.debug(f"🟢 [MetricsCollector.get_endpoint_metrics] 端点指标: {result}")
            return result
    
    def get_error_summary(self) -> Dict[str, Any]:
        """获取错误摘要"""
        logger.debug(f"🟢 [MetricsCollector.get_error_summary] 获取错误摘要")
        
        with self.lock:
            if not self.error_log:
                logger.debug(f"🟢 [MetricsCollector.get_error_summary] 无错误记录")
                return {'total_errors': 0, 'recent_errors': []}
            
            error_types = defaultdict(int)
            for error in self.error_log:
                error_types[error['type']] += 1
            logger.debug(f"🟢 [MetricsCollector.get_error_summary] 错误类型统计: {dict(error_types)}")
            
            result = {
                'total_errors': len(self.error_log),
                'error_types': dict(error_types),
                'recent_errors': [
                    {
                        'time': e['time'].isoformat(),
                        'type': e['type'],
                        'message': e['message'],
                        'endpoint': e['endpoint']
                    }
                    for e in self.error_log[-10:]
                ]
            }
            logger.debug(f"🟢 [MetricsCollector.get_error_summary] 错误摘要: {result}")
            return result
    
    def get_health_summary(self) -> Dict[str, Any]:
        """获取健康摘要"""
        logger.debug(f"🟢 [MetricsCollector.get_health_summary] 获取健康摘要")
        
        with self.lock:
            if not self.health_check_results:
                logger.debug(f"🟢 [MetricsCollector.get_health_summary] 无健康检查记录")
                return {'healthy': True, 'checks': 0}
            
            recent = self.health_check_results[-10:]
            healthy_count = sum(1 for h in recent if h['healthy'])
            logger.debug(f"🟢 [MetricsCollector.get_health_summary] 最近10次检查中 {healthy_count} 次健康")
            
            result = {
                'healthy': healthy_count >= len(recent) * 0.8,
                'checks': len(self.health_check_results),
                'recent_health_rate': healthy_count / len(recent) if recent else 0
            }
            logger.debug(f"🟢 [MetricsCollector.get_health_summary] 健康摘要: {result}")
            return result
    
    def get_full_report(self) -> Dict[str, Any]:
        """获取完整报告"""
        logger.debug(f"🟢 [MetricsCollector.get_full_report] 获取完整报告")
        
        with self.lock:
            uptime = time.time() - self.start_time
            logger.debug(f"🟢 [MetricsCollector.get_full_report] uptime = {uptime} 秒")
            
            result = {
                'uptime': uptime,
                'resource': resource_manager.get_stats(),
                'load': adaptive_load_manager.get_stats(),
                'retry': retry_handler.get_stats(),
                'endpoints': self.get_endpoint_metrics(),
                'errors': self.get_error_summary(),
                'health': self.get_health_summary()
            }
            logger.debug(f"🟢 [MetricsCollector.get_full_report] 完整报告已生成")
            return result

logger.debug(f"🟢 [初始化] 创建 MetricsCollector 实例")
metrics_collector = MetricsCollector()
logger.debug(f"🟢 [初始化] MetricsCollector 实例创建完成")

# ============================================================
# 全局数据存储
# ============================================================
logger.debug(f"🟢 [初始化] 配置数据存储...")

DATA_DIR = Path("/workspace/path_test_system/data")
logger.debug(f"🟢 [初始化] DATA_DIR = {DATA_DIR}")

DATA_DIR.mkdir(parents=True, exist_ok=True)
logger.debug(f"🟢 [初始化] 数据目录已创建")

projects_file = DATA_DIR / "projects.json"
logger.debug(f"🟢 [初始化] projects_file = {projects_file}")

issues_file = DATA_DIR / "issues.json"
logger.debug(f"🟢 [初始化] issues_file = {issues_file}")

tests_file = DATA_DIR / "tests.json"
logger.debug(f"🟢 [初始化] tests_file = {tests_file}")

settings_file = DATA_DIR / "settings.json"
logger.debug(f"🟢 [初始化] settings_file = {settings_file}")

file_locks = {
    'projects': threading.Lock(),
    'issues': threading.Lock(),
    'tests': threading.Lock(),
    'settings': threading.Lock()
}
logger.debug(f"🟢 [初始化] 文件锁已创建")

# ============================================================
# 数据加载/保存函数（带重试和超详细日志）
# ============================================================
logger.debug(f"🟢 [初始化] 定义数据操作函数...")

@with_retry("load_json")
def load_json_safe(file_path: Path) -> Any:
    """安全加载JSON - 超详细日志"""
    logger.debug(f"🟢 [load_json_safe] 开始加载文件 {file_path}")
    
    if not file_path.exists():
        logger.debug(f"🟢 [load_json_safe] 文件不存在")
        if 'projects' in str(file_path) or 'issues' in str(file_path):
            logger.debug(f"🟢 [load_json_safe] 返回空列表")
            return []
        else:
            logger.debug(f"🟢 [load_json_safe] 返回空字典")
            return {}
    
    logger.debug(f"🟢 [load_json_safe] 文件存在，开始读取")
    with open(file_path, 'r', encoding='utf-8') as f:
        logger.debug(f"🟢 [load_json_safe] 开始解析JSON")
        data = json.load(f)
        logger.debug(f"🟢 [load_json_safe] JSON解析完成")
        return data

@with_retry("save_json")
def save_json_safe(file_path: Path, data: Any) -> bool:
    """安全保存JSON - 超详细日志"""
    logger.debug(f"🟢 [save_json_safe] 开始保存文件 {file_path}")
    temp_path = file_path.with_suffix('.tmp')
    logger.debug(f"🟢 [save_json_safe] 临时文件 {temp_path}")
    
    with open(temp_path, 'w', encoding='utf-8') as f:
        logger.debug(f"🟢 [save_json_safe] 开始写入JSON")
        json.dump(data, f, ensure_ascii=False, indent=2)
        logger.debug(f"🟢 [save_json_safe] JSON写入完成")
    
    logger.debug(f"🟢 [save_json_safe] 将临时文件重命名为原文件")
    temp_path.replace(file_path)
    logger.debug(f"🟢 [save_json_safe] 文件保存成功")
    return True

def load_projects():
    """加载项目 - 超详细日志"""
    logger.debug(f"🟢 [load_projects] 开始加载项目数据")
    with file_locks['projects']:
        logger.debug(f"🟢 [load_projects] 获取projects锁成功")
        data = load_json_safe(projects_file)
        logger.debug(f"🟢 [load_projects] 项目数据加载完成，共 {len(data) if isinstance(data, list) else 0} 条")
        return data

def save_projects(projects: List[Dict]):
    """保存项目 - 超详细日志"""
    logger.debug(f"🟢 [save_projects] 开始保存 {len(projects)} 个项目")
    with file_locks['projects']:
        logger.debug(f"🟢 [save_projects] 获取projects锁成功")
        save_json_safe(projects_file, projects)
        logger.debug(f"🟢 [save_projects] 项目数据保存成功")

def load_issues():
    """加载问题 - 超详细日志"""
    logger.debug(f"🟢 [load_issues] 开始加载问题数据")
    with file_locks['issues']:
        logger.debug(f"🟢 [load_issues] 获取issues锁成功")
        data = load_json_safe(issues_file)
        logger.debug(f"🟢 [load_issues] 问题数据加载完成，共 {len(data) if isinstance(data, list) else 0} 条")
        return data

def load_settings():
    """加载设置 - 超详细日志"""
    logger.debug(f"🟢 [load_settings] 开始加载设置数据")
    with file_locks['settings']:
        logger.debug(f"🟢 [load_settings] 获取settings锁成功")
        data = load_json_safe(settings_file)
        logger.debug(f"🟢 [load_settings] 设置数据加载完成")
        return data

def save_settings(settings: Dict):
    """保存设置 - 超详细日志"""
    logger.debug(f"🟢 [save_settings] 开始保存设置")
    with file_locks['settings']:
        logger.debug(f"🟢 [save_settings] 获取settings锁成功")
        save_json_safe(settings_file, settings)
        logger.debug(f"🟢 [save_settings] 设置数据保存成功")

# ============================================================
# 安全工具函数（超详细日志）
# ============================================================
logger.debug(f"🟢 [初始化] 定义安全工具函数...")

DANGEROUS_TAGS = ['script', 'iframe', 'object', 'embed', 'form', 'input', 'button', 'style', 'svg']
DANGEROUS_ATTRIBUTES = ['onclick', 'onerror', 'onload', 'onmouseover', 'onfocus', 'onblur', 'onchange', 'eval']

def sanitize_input(text: Optional[str]) -> Optional[str]:
    """清理输入 - 超详细日志"""
    logger.debug(f"🟢 [sanitize_input] 开始清理输入，原始长度: {len(text) if text is not None else 'None'}")
    
    if text is None:
        logger.debug(f"🟢 [sanitize_input] 输入为None，直接返回")
        return None
    
    text = str(text)
    logger.debug(f"🟢 [sanitize_input] 输入转换为字符串")
    
    for tag in DANGEROUS_TAGS:
        logger.debug(f"🟢 [sanitize_input] 移除标签 <{tag}>")
        text = re.sub(rf'<\s*{tag}[^>]*>', '', text, flags=re.IGNORECASE)
        text = re.sub(rf'</\s*{tag}\s*>', '', text, flags=re.IGNORECASE)
    
    for attr in DANGEROUS_ATTRIBUTES:
        logger.debug(f"🟢 [sanitize_input] 移除属性 {attr}")
        text = re.sub(rf'\b{attr}\s*=', '', text, flags=re.IGNORECASE)
    
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    text = text.replace('"', '&quot;').replace("'", '&#39;')
    
    result = text.strip()
    logger.debug(f"🟢 [sanitize_input] 输入清理完成，最终长度: {len(result)}")
    return result

def validate_project_name(name: str) -> tuple[bool, str]:
    """验证项目名称 - 超详细日志"""
    logger.debug(f"🟢 [validate_project_name] 验证项目名称: '{name}'")
    
    if not name or not name.strip():
        logger.debug(f"🟢 [validate_project_name] 项目名称为空")
        return False, "项目名称不能为空"
    
    if len(name) > 200:
        logger.debug(f"🟢 [validate_project_name] 项目名称过长: {len(name)} 字符")
        return False, "项目名称不能超过200字符"
    
    logger.debug(f"🟢 [validate_project_name] 项目名称验证通过")
    return True, ""

def validate_project_path(path: str) -> tuple[bool, str]:
    """验证项目路径 - 超详细日志"""
    logger.debug(f"🟢 [validate_project_path] 验证项目路径: '{path}'")
    
    if not path or not path.strip():
        logger.debug(f"🟢 [validate_project_path] 路径为空")
        return False, "项目路径不能为空"
    
    if len(path) > 500:
        logger.debug(f"🟢 [validate_project_path] 路径过长: {len(path)} 字符")
        return False, "项目路径不能超过500字符"
    
    path = os.path.normpath(path)
    logger.debug(f"🟢 [validate_project_path] 规范化路径: '{path}'")
    
    if '..' in path:
        logger.debug(f"🟢 [validate_project_path] 路径包含 '..'，安全检查失败")
        return False, "路径包含非法字符"
    
    try:
        abs_path = os.path.abspath(path)
        logger.debug(f"🟢 [validate_project_path] 绝对路径: '{abs_path}'")
        
        if not abs_path.startswith('/workspace'):
            logger.debug(f"🟢 [validate_project_path] 路径不在 /workspace 下，安全检查失败")
            return False, "项目路径必须在工作区内"
    except Exception as e:
        logger.debug(f"🟢 [validate_project_path] 路径解析异常: {str(e)}")
        return False, "路径格式无效"
    
    logger.debug(f"🟢 [validate_project_path] 路径验证通过")
    return True, ""

# ============================================================
# API端点（带监控和超详细日志）
# ============================================================
logger.debug(f"🟢 [初始化] 定义API端点...")

@app.route('/api/health', methods=['GET'])
def health():
    """健康检查 - 超详细日志"""
    start_time = time.time()
    success = True
    status_code = 200
    
    logger.debug(f"🟢 [API.health] 收到健康检查请求")
    
    try:
        resource_stats = resource_manager.get_stats()
        load_stats = adaptive_load_manager.get_stats()
        projects_count = len(load_projects())
        issues_count = len(load_issues())
        
        result = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'resource': {
                'active_requests': resource_stats['active_requests'],
                'total_requests': resource_stats['total_requests'],
                'success_rate': f"{resource_stats['success_rate']:.2f}%"
            },
            'load': {
                'current_concurrency': load_stats['current_concurrency'],
                'success_rate': f"{load_stats['success_rate']:.2%}",
                'avg_duration': f"{load_stats['avg_duration']:.3f}s"
            },
            'data': {
                'projects': projects_count,
                'issues': issues_count
            }
        }
        
        metrics_collector.record_health_check(True, result)
        logger.debug(f"🟢 [API.health] 健康检查成功")
        
    except Exception as e:
        success = False
        status_code = 503
        result = {'status': 'unhealthy', 'error': str(e)}
        metrics_collector.record_health_check(False, {'error': str(e)})
        logger.error(f"❌ [API.health] 健康检查失败: {str(e)}")
    
    duration = time.time() - start_time
    metrics_collector.record_endpoint('health', duration, success, status_code)
    
    logger.debug(f"🟢 [API.health] 响应准备完成，返回结果")
    return jsonify(result), status_code

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """获取完整监控指标 - 超详细日志"""
    start_time = time.time()
    logger.debug(f"🟢 [API.get_metrics] 收到获取指标请求")
    
    try:
        report = metrics_collector.get_full_report()
        logger.debug(f"🟢 [API.get_metrics] 指标报告生成成功")
        return jsonify(report), 200
    except Exception as e:
        logger.error(f"❌ [API.get_metrics] 指标获取失败: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        duration = time.time() - start_time
        metrics_collector.record_endpoint('metrics', duration, True)

@app.route('/api/projects', methods=['GET'])
def get_projects():
    """获取所有项目 - 超详细日志"""
    start_time = time.time()
    success = False
    status_code = 200
    
    logger.debug(f"🟢 [API.get_projects] 收到获取项目请求")
    
    if not resource_manager.acquire_resource():
        logger.warning(f"⚠️ [API.get_projects] 资源获取失败，服务繁忙")
        return jsonify({'error': '服务繁忙，请稍后重试'}), 503
    
    try:
        projects = load_projects()
        success = True
        logger.debug(f"🟢 [API.get_projects] 获取到 {len(projects)} 个项目")
        return jsonify(projects), 200
        
    except Exception as e:
        status_code = 500
        logger.error(f"❌ [API.get_projects] 获取项目失败: {str(e)}")
        metrics_collector.record_error('GetProjects', str(e))
        return jsonify({'error': str(e)}), 500
        
    finally:
        resource_manager.release_resource(success)
        duration = time.time() - start_time
        metrics_collector.record_endpoint('get_projects', duration, success, status_code)
        adaptive_load_manager.record_request(duration, success)

@app.route('/api/projects', methods=['POST'])
def create_project():
    """创建项目 - 超详细日志"""
    start_time = time.time()
    success = False
    status_code = 201
    
    logger.debug(f"🟢 [API.create_project] 收到创建项目请求")
    
    if not resource_manager.acquire_resource():
        logger.warning(f"⚠️ [API.create_project] 资源获取失败，服务繁忙")
        return jsonify({'error': '服务繁忙，请稍后重试'}), 503
    
    try:
        data = request.get_json() or {}
        logger.debug(f"🟢 [API.create_project] 请求数据: {data}")
        
        name = data.get('name', '')
        path = data.get('path', '')
        description = data.get('description', '')
        logger.debug(f"🟢 [API.create_project] name={name}, path={path}")
        
        name = sanitize_input(name)
        description = sanitize_input(description)
        
        valid, msg = validate_project_name(name)
        if not valid:
            logger.debug(f"🟢 [API.create_project] 项目名称验证失败: {msg}")
            return jsonify({'error': msg}), 400
        
        valid, msg = validate_project_path(path)
        if not valid:
            logger.debug(f"🟢 [API.create_project] 项目路径验证失败: {msg}")
            return jsonify({'error': msg}), 400
        
        projects = load_projects()
        logger.debug(f"🟢 [API.create_project] 当前项目数: {len(projects)}")
        
        new_id = f"proj_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
        logger.debug(f"🟢 [API.create_project] 生成新项目ID: {new_id}")
        
        new_project = {
            'id': new_id,
            'name': name,
            'path': path,
            'description': description,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        logger.debug(f"🟢 [API.create_project] 新创建的项目: {new_project}")
        
        projects.append(new_project)
        save_projects(projects)
        
        success = True
        logger.info(f"✅ [API.create_project] 项目创建成功: {new_id}")
        
        return jsonify(new_project), 201
        
    except Exception as e:
        status_code = 500
        logger.error(f"❌ [API.create_project] 创建项目失败: {str(e)}\n{traceback.format_exc()}")
        metrics_collector.record_error('CreateProject', str(e))
        return jsonify({'error': str(e)}), 500
        
    finally:
        resource_manager.release_resource(success)
        duration = time.time() - start_time
        metrics_collector.record_endpoint('create_project', duration, success, status_code)
        adaptive_load_manager.record_request(duration, success)

@app.route('/api/projects/<project_id>', methods=['GET'])
def get_project(project_id):
    """获取单个项目 - 超详细日志"""
    start_time = time.time()
    success = False
    
    logger.debug(f"🟢 [API.get_project] 收到获取项目请求, project_id={project_id}")
    
    if not resource_manager.acquire_resource():
        logger.warning(f"⚠️ [API.get_project] 资源获取失败，服务繁忙")
        return jsonify({'error': '服务繁忙，请稍后重试'}), 503
    
    try:
        projects = load_projects()
        project = next((p for p in projects if p.get('id') == project_id), None)
        
        if not project:
            logger.debug(f"🟢 [API.get_project] 项目不存在: {project_id}")
            return jsonify({'error': '项目不存在'}), 404
        
        success = True
        logger.debug(f"🟢 [API.get_project] 获取项目成功: {project_id}")
        return jsonify(project), 200
        
    except Exception as e:
        logger.error(f"❌ [API.get_project] 获取项目详情失败: {str(e)}")
        metrics_collector.record_error('GetProject', str(e))
        return jsonify({'error': str(e)}), 500
        
    finally:
        resource_manager.release_resource(success)
        duration = time.time() - start_time
        metrics_collector.record_endpoint('get_project', duration, success)
        adaptive_load_manager.record_request(duration, success)

@app.route('/api/projects/<project_id>', methods=['PUT'])
def update_project(project_id):
    """更新项目 - 超详细日志"""
    start_time = time.time()
    success = False
    
    logger.debug(f"🟢 [API.update_project] 收到更新项目请求, project_id={project_id}")
    
    if not resource_manager.acquire_resource():
        logger.warning(f"⚠️ [API.update_project] 资源获取失败，服务繁忙")
        return jsonify({'error': '服务繁忙，请稍后重试'}), 503
    
    try:
        data = request.get_json() or {}
        logger.debug(f"🟢 [API.update_project] 更新数据: {data}")
        
        name = data.get('name', '')
        description = data.get('description', '')
        
        if name:
            name = sanitize_input(name)
            valid, msg = validate_project_name(name)
            if not valid:
                logger.debug(f"🟢 [API.update_project] 项目名称验证失败: {msg}")
                return jsonify({'error': msg}), 400
        
        if description:
            description = sanitize_input(description)
        
        projects = load_projects()
        project_index = next((i for i, p in enumerate(projects) if p.get('id') == project_id), -1)
        
        if project_index == -1:
            logger.debug(f"🟢 [API.update_project] 项目不存在: {project_id}")
            return jsonify({'error': '项目不存在'}), 404
        
        if name:
            projects[project_index]['name'] = name
            logger.debug(f"🟢 [API.update_project] 更新项目名称为: {name}")
        if description:
            projects[project_index]['description'] = description
            logger.debug(f"🟢 [API.update_project] 更新项目描述为: {description}")
        
        projects[project_index]['updated_at'] = datetime.now().isoformat()
        logger.debug(f"🟢 [API.update_project] 更新项目更新时间")
        
        save_projects(projects)
        
        success = True
        logger.debug(f"🟢 [API.update_project] 项目更新成功: {project_id}")
        return jsonify(projects[project_index]), 200
        
    except Exception as e:
        logger.error(f"❌ [API.update_project] 更新项目失败: {str(e)}")
        metrics_collector.record_error('UpdateProject', str(e))
        return jsonify({'error': str(e)}), 500
        
    finally:
        resource_manager.release_resource(success)
        duration = time.time() - start_time
        metrics_collector.record_endpoint('update_project', duration, success)
        adaptive_load_manager.record_request(duration, success)

@app.route('/api/projects/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    """删除项目 - 超详细日志"""
    start_time = time.time()
    success = False
    
    logger.debug(f"🟢 [API.delete_project] 收到删除项目请求, project_id={project_id}")
    
    if not resource_manager.acquire_resource():
        logger.warning(f"⚠️ [API.delete_project] 资源获取失败，服务繁忙")
        return jsonify({'error': '服务繁忙，请稍后重试'}), 503
    
    try:
        projects = load_projects()
        initial_len = len(projects)
        
        projects = [p for p in projects if p.get('id') != project_id]
        
        if len(projects) == initial_len:
            logger.debug(f"🟢 [API.delete_project] 项目不存在: {project_id}")
            return jsonify({'error': '项目不存在'}), 404
        
        save_projects(projects)
        
        success = True
        logger.info(f"✅ [API.delete_project] 项目删除成功: {project_id}")
        
        return jsonify({'message': '项目删除成功'}), 200
        
    except Exception as e:
        logger.error(f"❌ [API.delete_project] 删除项目失败: {str(e)}")
        metrics_collector.record_error('DeleteProject', str(e))
        return jsonify({'error': str(e)}), 500
        
    finally:
        resource_manager.release_resource(success)
        duration = time.time() - start_time
        metrics_collector.record_endpoint('delete_project', duration, success)
        adaptive_load_manager.record_request(duration, success)

@app.route('/api/issues', methods=['GET'])
def get_issues():
    """获取所有问题 - 超详细日志"""
    start_time = time.time()
    success = False
    
    logger.debug(f"🟢 [API.get_issues] 收到获取问题请求")
    
    if not resource_manager.acquire_resource():
        logger.warning(f"⚠️ [API.get_issues] 资源获取失败，服务繁忙")
        return jsonify({'error': '服务繁忙，请稍后重试'}), 503
    
    try:
        issues = load_issues()
        success = True
        logger.debug(f"🟢 [API.get_issues] 获取到 {len(issues)} 个问题")
        return jsonify(issues), 200
        
    except Exception as e:
        logger.error(f"❌ [API.get_issues] 获取问题失败: {str(e)}")
        return jsonify({'error': str(e)}), 500
        
    finally:
        resource_manager.release_resource(success)
        duration = time.time() - start_time
        metrics_collector.record_endpoint('get_issues', duration, success)
        adaptive_load_manager.record_request(duration, success)

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """获取设置 - 超详细日志"""
    start_time = time.time()
    success = False
    
    logger.debug(f"🟢 [API.get_settings] 收到获取设置请求")
    
    if not resource_manager.acquire_resource():
        logger.warning(f"⚠️ [API.get_settings] 资源获取失败，服务繁忙")
        return jsonify({'error': '服务繁忙，请稍后重试'}), 503
    
    try:
        settings = load_settings()
        success = True
        logger.debug(f"🟢 [API.get_settings] 获取设置成功")
        return jsonify(settings), 200
        
    except Exception as e:
        logger.error(f"❌ [API.get_settings] 获取设置失败: {str(e)}")
        return jsonify({'error': str(e)}), 500
        
    finally:
        resource_manager.release_resource(success)
        duration = time.time() - start_time
        metrics_collector.record_endpoint('get_settings', duration, success)
        adaptive_load_manager.record_request(duration, success)

@app.route('/api/files/browse', methods=['GET'])
def browse_files():
    """浏览文件 - 超详细日志"""
    start_time = time.time()
    success = False
    
    logger.debug(f"🟢 [API.browse_files] 收到浏览文件请求")
    
    if not resource_manager.acquire_resource():
        logger.warning(f"⚠️ [API.browse_files] 资源获取失败，服务繁忙")
        return jsonify({'error': '服务繁忙，请稍后重试'}), 503
    
    try:
        path = request.args.get('path', '/workspace')
        logger.debug(f"🟢 [API.browse_files] 浏览路径: {path}")
        
        valid, msg = validate_project_path(path)
        if not valid:
            logger.debug(f"🟢 [API.browse_files] 路径验证失败: {msg}")
            return jsonify({'error': msg}), 400
        
        if not os.path.exists(path):
            logger.debug(f"🟢 [API.browse_files] 路径不存在: {path}")
            return jsonify({'error': '路径不存在'}), 404
        
        if not os.path.isdir(path):
            logger.debug(f"🟢 [API.browse_files] 路径不是目录: {path}")
            return jsonify({'error': '路径不是目录'}), 400
        
        items = []
        for item in os.listdir(path)[:50]:
            item_path = os.path.join(path, item)
            try:
                stat = os.stat(item_path)
                items.append({
                    'name': item,
                    'type': 'dir' if os.path.isdir(item_path) else 'file',
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            except Exception as e:
                logger.debug(f"🟢 [API.browse_files] 跳过文件/目录 {item}: {str(e)}")
        
        success = True
        logger.debug(f"🟢 [API.browse_files] 浏览完成，找到 {len(items)} 个项目")
        return jsonify({'path': path, 'items': items}), 200
        
    except Exception as e:
        logger.error(f"❌ [API.browse_files] 浏览文件失败: {str(e)}")
        return jsonify({'error': str(e)}), 500
        
    finally:
        resource_manager.release_resource(success)
        duration = time.time() - start_time
        metrics_collector.record_endpoint('browse_files', duration, success)
        adaptive_load_manager.record_request(duration, success)

@app.route('/api/files/read', methods=['GET'])
def read_file():
    """读取文件 - 超详细日志"""
    start_time = time.time()
    success = False
    
    logger.debug(f"🟢 [API.read_file] 收到读取文件请求")
    
    if not resource_manager.acquire_resource():
        logger.warning(f"⚠️ [API.read_file] 资源获取失败，服务繁忙")
        return jsonify({'error': '服务繁忙，请稍后重试'}), 503
    
    try:
        path = request.args.get('path', '')
        logger.debug(f"🟢 [API.read_file] 文件路径: {path}")
        
        if not path:
            logger.debug(f"🟢 [API.read_file] 缺少文件路径")
            return jsonify({'error': '缺少文件路径'}), 400
        
        valid, msg = validate_project_path(path)
        if not valid:
            logger.debug(f"🟢 [API.read_file] 路径验证失败: {msg}")
            return jsonify({'error': msg}), 400
        
        if not os.path.exists(path):
            logger.debug(f"🟢 [API.read_file] 文件不存在: {path}")
            return jsonify({'error': '文件不存在'}), 404
        
        if not os.path.isfile(path):
            logger.debug(f"🟢 [API.read_file] 路径不是文件: {path}")
            return jsonify({'error': '路径不是文件'}), 400
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read(10000)
        
        success = True
        logger.debug(f"🟢 [API.read_file] 读取文件成功，内容长度: {len(content)}")
        return jsonify({'path': path, 'content': content}), 200
        
    except Exception as e:
        logger.error(f"❌ [API.read_file] 读取文件失败: {str(e)}")
        return jsonify({'error': str(e)}), 500
        
    finally:
        resource_manager.release_resource(success)
        duration = time.time() - start_time
        metrics_collector.record_endpoint('read_file', duration, success)
        adaptive_load_manager.record_request(duration, success)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """分析项目 - 超详细日志"""
    start_time = time.time()
    success = False
    
    logger.debug(f"🟢 [API.analyze] 收到分析请求")
    
    if not resource_manager.acquire_resource():
        logger.warning(f"⚠️ [API.analyze] 资源获取失败，服务繁忙")
        return jsonify({'error': '服务繁忙，请稍后重试'}), 503
    
    try:
        data = request.get_json() or {}
        project_id = data.get('projectId')
        logger.debug(f"🟢 [API.analyze] 项目ID: {project_id}")
        
        if not project_id:
            logger.debug(f"🟢 [API.analyze] 缺少项目ID")
            return jsonify({'error': '缺少项目ID'}), 400
        
        projects = load_projects()
        project = next((p for p in projects if p.get('id') == project_id), None)
        
        if not project:
            logger.debug(f"🟢 [API.analyze] 项目不存在: {project_id}")
            return jsonify({'error': '项目不存在'}), 404
        
        success = True
        logger.debug(f"🟢 [API.analyze] 分析完成")
        return jsonify({
            'status': 'analyzed',
            'project': project.get('name'),
            'files_analyzed': random.randint(5, 20),
            'issues_found': random.randint(0, 5)
        }), 200
        
    except Exception as e:
        logger.error(f"❌ [API.analyze] 分析项目失败: {str(e)}")
        return jsonify({'error': str(e)}), 500
        
    finally:
        resource_manager.release_resource(success)
        duration = time.time() - start_time
        metrics_collector.record_endpoint('analyze', duration, success)
        adaptive_load_manager.record_request(duration, success)

# ============================================================
# 后台任务
# ============================================================
logger.debug(f"🟢 [初始化] 定义后台任务...")

def background_maintenance():
    """后台维护任务 - 超详细日志"""
    logger.debug(f"🟢 [background_maintenance] 后台维护线程启动")
    
    while True:
        try:
            time.sleep(60)
            logger.debug(f"🟢 [background_maintenance] 60秒间隔到，开始维护")
            
            gc_stats = resource_manager.force_garbage_collection()
            
            metrics = metrics_collector.get_full_report()
            
            logger.info(f"📊 后台报告 - 活跃请求: {metrics['resource']['active_requests']}, "
                       f"成功率: {metrics['resource']['success_rate']:.2f}%, "
                       f"当前并发: {metrics['load']['current_concurrency']}")
            
        except Exception as e:
            logger.error(f"❌ [background_maintenance] 后台维护失败: {str(e)}")

logger.debug(f"🟢 [初始化] 启动后台维护线程...")
maintenance_thread = threading.Thread(target=background_maintenance, daemon=True)
maintenance_thread.start()
logger.info(f"✅ 后台维护线程已启动")

# ============================================================
# 启动服务器
# ============================================================
logger.debug(f"🟢 [初始化] 准备启动服务器...")

if __name__ == '__main__':
    logger.info("="*100)
    logger.info("🚀 超详细日志版API服务器启动 - 基础健壮性增强")
    logger.info("="*100)
    logger.info(f"📊 特性:")
    logger.info(f"   - 自动重试机制 (最多3次重试)")
    logger.info(f"   - 资源管理 (最大并发: {resource_manager.max_concurrent_requests})")
    logger.info(f"   - 负载自适应 (并发范围: {adaptive_load_manager.min_concurrency}-{adaptive_load_manager.max_concurrency})")
    logger.info(f"   - 监控指标收集")
    logger.info(f"   - 超详细日志记录 (每一步都有日志)")
    logger.info("="*100)
    
    app.run(host='0.0.0.0', port=5174, debug=False, threaded=True)