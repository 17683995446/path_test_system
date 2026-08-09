"""
内存优化系统
============

高度模块化的内存管理和优化组件
- 流式处理：避免一次性加载整个文件
- 按需加载：AST树按需生成和释放
- 内存监控：实时监控内存使用
- 垃圾回收：智能触发垃圾回收

作者：PathTestSystem
版本：1.0.0
"""

import os
import sys
import gc
import time
import tracemalloc
from typing import Dict, Any, Optional, Iterator, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import threading


class MemoryPressure(Enum):
    """内存压力级别"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class MemorySnapshot:
    """内存快照"""
    timestamp: float
    current_mb: float
    peak_mb: float
    pressure: MemoryPressure
    object_counts: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp,
            'current_mb': self.current_mb,
            'peak_mb': self.peak_mb,
            'pressure': self.pressure.value,
            'object_counts': self.object_counts
        }


class MemoryMonitor:
    """
    内存监控器
    ==========
    
    实时监控内存使用情况，支持：
    - 内存压力检测
    - 内存峰值追踪
    - 内存泄漏检测
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.enabled = self.config.get('enabled', True)
        self.check_interval = self.config.get('check_interval', 1.0)
        self.high_threshold_mb = self.config.get('high_threshold_mb', 500)
        self.critical_threshold_mb = self.config.get('critical_threshold_mb', 1000)
        
        self.snapshots: List[MemorySnapshot] = []
        self.peak_memory = 0.0
        self.current_memory = 0.0
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        
        if self.enabled:
            self.start()
    
    def start(self):
        """启动内存监控"""
        if self.enabled and not self.monitoring:
            tracemalloc.start()
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
    
    def stop(self):
        """停止内存监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        tracemalloc.stop()
    
    def _monitor_loop(self):
        """监控循环"""
        while self.monitoring:
            try:
                snapshot = self._take_snapshot()
                with self._lock:
                    self.snapshots.append(snapshot)
                    if len(self.snapshots) > 1000:
                        self.snapshots = self.snapshots[-500:]
                
                if snapshot.current_mb > self.peak_memory:
                    self.peak_memory = snapshot.current_mb
                
                if snapshot.pressure in [MemoryPressure.HIGH, MemoryPressure.CRITICAL]:
                    self._trigger_cleanup()
                
                time.sleep(self.check_interval)
            except Exception:
                pass
    
    def _take_snapshot(self) -> MemorySnapshot:
        """获取内存快照"""
        current, peak = tracemalloc.get_traced_memory()
        current_mb = current / 1024 / 1024
        peak_mb = peak / 1024 / 1024
        self.current_memory = current_mb
        
        if current_mb >= self.critical_threshold_mb:
            pressure = MemoryPressure.CRITICAL
        elif current_mb >= self.high_threshold_mb:
            pressure = MemoryPressure.HIGH
        elif current_mb >= self.high_threshold_mb / 2:
            pressure = MemoryPressure.NORMAL
        else:
            pressure = MemoryPressure.LOW
        
        return MemorySnapshot(
            timestamp=time.time(),
            current_mb=current_mb,
            peak_mb=peak_mb,
            pressure=pressure
        )
    
    def _trigger_cleanup(self):
        """触发清理"""
        gc.collect()
    
    def get_current_snapshot(self) -> Optional[MemorySnapshot]:
        """获取当前快照"""
        if self.snapshots:
            with self._lock:
                return self.snapshots[-1]
        return None
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        if not self.snapshots:
            return {}
        
        with self._lock:
            snapshots = self.snapshots
        
        total_memory = sum(s.current_mb for s in snapshots)
        return {
            'peak_memory_mb': self.peak_memory,
            'current_memory_mb': self.current_memory,
            'average_memory_mb': total_memory / len(snapshots) if snapshots else 0,
            'snapshot_count': len(snapshots),
            'peak_pressure': max(s.pressure for s in snapshots).value
        }


class StreamingProcessor:
    """
    流式处理器
    ==========
    
    用于处理大型文件的流式处理，避免一次性加载：
    - 文件流式读取
    - 分块处理
    - 生成器模式
    """
    
    def __init__(self, chunk_size: int = 1000):
        self.chunk_size = chunk_size
    
    def stream_file_lines(self, file_path: str) -> Iterator[str]:
        """
        流式读取文件行
        
        Args:
            file_path: 文件路径
        
        Yields:
            文件的每一行
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    yield line
        except Exception:
            pass
    
    def stream_file_chunks(self, file_path: str) -> Iterator[List[str]]:
        """
        流式读取文件块
        
        Args:
            file_path: 文件路径
        
        Yields:
            文件块（每块chunk_size行）
        """
        chunk = []
        for line in self.stream_file_lines(file_path):
            chunk.append(line)
            if len(chunk) >= self.chunk_size:
                yield chunk
                chunk = []
        if chunk:
            yield chunk
    
    def stream_large_file(self, file_path: str, process_func: Callable[[str], Any]) -> List[Any]:
        """
        流式处理大文件
        
        Args:
            file_path: 文件路径
            process_func: 处理函数
        
        Returns:
            处理结果列表
        """
        results = []
        for chunk in self.stream_file_chunks(file_path):
            for line in chunk:
                result = process_func(line)
                if result is not None:
                    results.append(result)
        return results


class LazyASTLoader:
    """
    延迟AST加载器
    =============
    
    按需加载AST树，避免一次性解析所有文件：
    - LRU缓存
    - 自动过期
    - 内存感知
    """
    
    def __init__(self, max_cache_size: int = 100):
        self.max_cache_size = max_cache_size
        self.cache: Dict[str, Any] = {}
        self.cache_order: deque = deque()
        self.memory_monitor: Optional[MemoryMonitor] = None
    
    def set_memory_monitor(self, monitor: MemoryMonitor):
        """设置内存监控器"""
        self.memory_monitor = monitor
    
    def _check_memory_pressure(self):
        """检查内存压力"""
        if self.memory_monitor:
            snapshot = self.memory_monitor.get_current_snapshot()
            if snapshot and snapshot.pressure in [MemoryPressure.HIGH, MemoryPressure.CRITICAL]:
                self._evict_half()
    
    def _evict_half(self):
        """淘汰一半缓存"""
        evict_count = len(self.cache) // 2
        for _ in range(evict_count):
            if self.cache_order:
                oldest = self.cache_order.popleft()
                if oldest in self.cache:
                    del self.cache[oldest]
    
    def load_ast(self, file_path: str, parser_func: Callable[[str], Any]) -> Optional[Any]:
        """
        延迟加载AST
        
        Args:
            file_path: 文件路径
            parser_func: 解析函数
        
        Returns:
            AST对象或None
        """
        if file_path in self.cache:
            self.cache_order.remove(file_path)
            self.cache_order.append(file_path)
            return self.cache[file_path]
        
        self._check_memory_pressure()
        
        try:
            ast_tree = parser_func(file_path)
            if len(self.cache) >= self.max_cache_size:
                oldest = self.cache_order.popleft()
                del self.cache[oldest]
            
            self.cache[file_path] = ast_tree
            self.cache_order.append(file_path)
            return ast_tree
        except Exception:
            return None
    
    def invalidate(self, file_path: str):
        """使缓存失效"""
        if file_path in self.cache:
            del self.cache[file_path]
            if file_path in self.cache_order:
                self.cache_order.remove(file_path)
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.cache_order.clear()


class IncrementalFileProcessor:
    """
    增量文件处理器
    ==============
    
    支持增量处理，只处理变更的文件：
    - 文件指纹追踪
    - 变更检测
    - 跳过未变更文件
    """
    
    def __init__(self):
        self.file_fingerprints: Dict[str, str] = {}
    
    def compute_fingerprint(self, file_path: str) -> Optional[str]:
        """
        计算文件指纹
        
        Args:
            file_path: 文件路径
        
        Returns:
            文件指纹或None
        """
        try:
            stat = os.stat(file_path)
            mtime = stat.st_mtime
            size = stat.st_size
            fingerprint = f"{mtime}-{size}"
            return fingerprint
        except Exception:
            return None
    
    def has_changed(self, file_path: str) -> bool:
        """
        检查文件是否变更
        
        Args:
            file_path: 文件路径
        
        Returns:
            是否变更
        """
        current_fingerprint = self.compute_fingerprint(file_path)
        if current_fingerprint is None:
            return True
        
        old_fingerprint = self.file_fingerprints.get(file_path)
        if old_fingerprint is None:
            return True
        
        return current_fingerprint != old_fingerprint
    
    def mark_processed(self, file_path: str):
        """标记文件已处理"""
        fingerprint = self.compute_fingerprint(file_path)
        if fingerprint:
            self.file_fingerprints[file_path] = fingerprint
    
    def get_changed_files(self, file_paths: List[str]) -> List[str]:
        """
        获取变更的文件列表
        
        Args:
            file_paths: 所有文件路径
        
        Returns:
            变更的文件列表
        """
        return [f for f in file_paths if self.has_changed(f)]


class MemoryOptimizer:
    """
    内存优化器 - 主控制器
    ======================
    
    整合所有内存优化组件：
    - 内存监控
    - 流式处理
    - 延迟加载
    - 增量处理
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        self.monitor = MemoryMonitor({
            'enabled': self.config.get('enable_monitoring', True),
            'check_interval': self.config.get('check_interval', 1.0),
            'high_threshold_mb': self.config.get('high_threshold_mb', 500),
            'critical_threshold_mb': self.config.get('critical_threshold_mb', 1000)
        })
        
        self.stream_processor = StreamingProcessor(
            chunk_size=self.config.get('chunk_size', 1000)
        )
        
        self.lazy_loader = LazyASTLoader(
            max_cache_size=self.config.get('max_ast_cache_size', 100)
        )
        self.lazy_loader.set_memory_monitor(self.monitor)
        
        self.incremental_processor = IncrementalFileProcessor()
        
        self.gc_enabled = self.config.get('enable_gc', True)
        self.gc_threshold = self.config.get('gc_threshold', 1000)
        self.processed_count = 0
    
    def process_file_streaming(self, file_path: str, process_func: Callable[[str], Any]) -> List[Any]:
        """
        流式处理文件
        
        Args:
            file_path: 文件路径
            process_func: 处理函数
        
        Returns:
            处理结果
        """
        if self.monitor.get_current_snapshot():
            snapshot = self.monitor.get_current_snapshot()
            if snapshot.pressure == MemoryPressure.CRITICAL:
                gc.collect()
        
        results = self.stream_processor.stream_large_file(file_path, process_func)
        self.processed_count += 1
        
        if self.gc_enabled and self.processed_count % self.gc_threshold == 0:
            gc.collect()
        
        return results
    
    def process_files_incremental(self, file_paths: List[str], 
                                   process_func: Callable[[str], Any]) -> Dict[str, List[Any]]:
        """
        增量处理多个文件
        
        Args:
            file_paths: 文件列表
            process_func: 处理函数
        
        Returns:
            处理结果字典
        """
        changed_files = self.incremental_processor.get_changed_files(file_paths)
        
        results = {}
        for file_path in changed_files:
            try:
                results[file_path] = self.process_file_streaming(file_path, process_func)
                self.incremental_processor.mark_processed(file_path)
            except Exception:
                results[file_path] = []
        
        return results
    
    def load_ast_lazy(self, file_path: str, parser_func: Callable[[str], Any]) -> Optional[Any]:
        """
        延迟加载AST
        
        Args:
            file_path: 文件路径
            parser_func: 解析函数
        
        Returns:
            AST对象
        """
        return self.lazy_loader.load_ast(file_path, parser_func)
    
    def get_memory_status(self) -> Dict:
        """获取内存状态"""
        stats = self.monitor.get_statistics()
        return {
            'monitor_stats': stats,
            'lazy_loader_cache_size': len(self.lazy_loader.cache),
            'incremental_tracked_files': len(self.incremental_processor.file_fingerprints),
            'processed_count': self.processed_count
        }
    
    def force_cleanup(self):
        """强制清理"""
        gc.collect()
        self.lazy_loader.clear()
    
    def shutdown(self):
        """关闭优化器"""
        self.monitor.stop()
        self.force_cleanup()


def create_memory_optimizer(config: Optional[Dict] = None) -> MemoryOptimizer:
    """
    创建内存优化器工厂函数
    
    Args:
        config: 配置字典
    
    Returns:
        MemoryOptimizer实例
    """
    return MemoryOptimizer(config)


if __name__ == "__main__":
    optimizer = create_memory_optimizer({
        'enable_monitoring': True,
        'high_threshold_mb': 100,
        'critical_threshold_mb': 200,
        'chunk_size': 100,
        'max_ast_cache_size': 50
    })
    
    print("内存优化器初始化完成")
    print(f"当前内存状态: {optimizer.get_memory_status()}")
    
    optimizer.shutdown()
    print("内存优化器已关闭")
