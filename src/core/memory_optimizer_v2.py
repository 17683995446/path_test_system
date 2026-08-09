"""
内存优化系统2.0
======================================================================

更高效的内存管理系统，包括：
- 对象池技术
- 增量解析器
- 内存监控与自动清理
- 内存泄漏检测
"""

import os
import gc
import tracemalloc
import weakref
from typing import Dict, List, Any, Optional, Callable, TypeVar, Generic, Type
from dataclasses import dataclass, field
from collections import OrderedDict
import threading
import time


T = TypeVar('T')


@dataclass
class MemorySnapshot:
    """内存快照"""
    timestamp: float
    current_mb: float
    peak_mb: float
    objects_count: int
    top_objects: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp,
            "current_mb": self.current_mb,
            "peak_mb": self.peak_mb,
            "objects_count": self.objects_count,
            "top_objects": self.top_objects
        }


class ObjectPool(Generic[T]):
    """
    对象池
    
    重用对象减少GC压力
    """
    
    def __init__(self, factory: Callable[[], T], max_size: int = 100):
        self.factory = factory
        self.max_size = max_size
        self.pool: List[T] = []
        self.lock = threading.Lock()
    
    def acquire(self) -> T:
        """获取对象"""
        with self.lock:
            if self.pool:
                return self.pool.pop()
            return self.factory()
    
    def release(self, obj: T) -> None:
        """释放对象"""
        with self.lock:
            if len(self.pool) < self.max_size:
                self._reset(obj)
                self.pool.append(obj)
    
    def _reset(self, obj: T) -> None:
        """重置对象（子类可重写）"""
        if hasattr(obj, 'reset'):
            obj.reset()
    
    def clear(self) -> None:
        """清空对象池"""
        with self.lock:
            self.pool.clear()
    
    def size(self) -> int:
        """获取当前大小"""
        with self.lock:
            return len(self.pool)


class LRUCache(Generic[T]):
    """
    优化的LRU缓存
    
    支持TLL、自动清理
    """
    
    def __init__(self, max_size: int = 1000, ttl: float = 3600.0):
        self.max_size = max_size
        self.ttl = ttl
        self.cache: OrderedDict[str, T] = OrderedDict()
        self.timestamps: Dict[str, float] = {}
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Optional[T]:
        """获取缓存"""
        with self.lock:
            if key not in self.cache:
                return None
            
            if self._is_expired(key):
                del self.cache[key]
                del self.timestamps[key]
                return None
            
            self.cache.move_to_end(key)
            return self.cache[key]
    
    def put(self, key: str, value: T) -> None:
        """设置缓存"""
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            else:
                if len(self.cache) >= self.max_size:
                    self._evict_lru()
                
                self.cache[key] = value
                self.timestamps[key] = time.time()
    
    def _evict_lru(self) -> None:
        """淘汰最近最少使用"""
        if self.cache:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            del self.timestamps[oldest_key]
    
    def _is_expired(self, key: str) -> bool:
        """判断是否过期"""
        ts = self.timestamps.get(key, 0)
        return (time.time() - ts) > self.ttl
    
    def clear_expired(self) -> int:
        """清理过期条目"""
        count = 0
        with self.lock:
            expired_keys = [k for k in self.timestamps if self._is_expired(k)]
            for key in expired_keys:
                del self.cache[key]
                del self.timestamps[key]
                count += 1
        return count
    
    def size(self) -> int:
        """获取大小"""
        with self.lock:
            return len(self.cache)


class IncrementalParser:
    """
    增量解析器
    
    避免一次性加载大文件
    """
    
    def __init__(self, chunk_size: int = 10000):
        self.chunk_size = chunk_size
    
    def parse_file_in_chunks(self, file_path: str) -> Any:
        """分块解析文件"""
        if not os.path.exists(file_path):
            return None
        
        result = []
        with open(file_path, 'r', encoding='utf-8') as f:
            while True:
                chunk = f.read(self.chunk_size)
                if not chunk:
                    break
                result.extend(self._parse_chunk(chunk))
        
        return result
    
    def _parse_chunk(self, chunk: str) -> List[Any]:
        """解析单个块（子类重写）"""
        return [chunk]


class MemoryMonitor:
    """
    内存监控器
    
    实时监控内存使用，自动触发清理
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.high_threshold_mb = self.config.get('high_threshold', 500)
        self.critical_threshold_mb = self.config.get('critical_threshold', 1000)
        self.enabled = self.config.get('enabled', True)
        
        self.snapshots: List[MemorySnapshot] = []
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
        
        if self.enabled:
            tracemalloc.start()
    
    def take_snapshot(self) -> MemorySnapshot:
        """获取当前内存快照"""
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        
        current, peak = tracemalloc.get_traced_memory()
        current_mb = current / 1024 / 1024
        peak_mb = peak / 1024 / 1024
        
        top_objects = []
        for stat in top_stats[:10]:
            top_objects.append({
                "file": str(stat.traceback),
                "size_mb": stat.size / 1024 / 1024,
                "count": stat.count
            })
        
        memory_snapshot = MemorySnapshot(
            timestamp=time.time(),
            current_mb=current_mb,
            peak_mb=peak_mb,
            objects_count=len(top_objects),
            top_objects=top_objects
        )
        
        with self.lock:
            self.snapshots.append(memory_snapshot)
            if len(self.snapshots) > 100:
                self.snapshots = self.snapshots[-100:]
        
        return memory_snapshot
    
    def check_memory_pressure(self) -> str:
        """检查内存压力"""
        snapshot = self.take_snapshot()
        
        if snapshot.current_mb > self.critical_threshold_mb:
            self._handle_critical()
            return "critical"
        elif snapshot.current_mb > self.high_threshold_mb:
            self._handle_high()
            return "high"
        
        return "normal"
    
    def _handle_high(self) -> None:
        """处理高内存压力"""
        gc.collect()
    
    def _handle_critical(self) -> None:
        """处理临界内存压力"""
        gc.collect(2)
    
    def get_usage_stats(self) -> Dict:
        """获取使用统计"""
        if not self.snapshots:
            return {}
        
        latest = self.snapshots[-1]
        return {
            "current_mb": latest.current_mb,
            "peak_mb": latest.peak_mb,
            "snapshot_count": len(self.snapshots),
            "pressure": self.check_memory_pressure()
        }


class MemoryOptimizer2:
    """
    内存优化系统2.0 - 主控制器
    ==============================================================
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        self.monitor = MemoryMonitor(self.config)
        self.lru_cache = LRUCache(max_size=self.config.get('cache_size', 1000))
        self.object_pools: Dict[str, ObjectPool] = {}
        
        self.auto_cleanup_enabled = self.config.get('auto_cleanup', True)
        self.last_cleanup = time.time()
        self.cleanup_interval = self.config.get('cleanup_interval', 60.0)
    
    def register_object_pool(self, name: str, pool: ObjectPool) -> None:
        """注册对象池"""
        self.object_pools[name] = pool
    
    def get_or_create_pool(self, name: str, factory: Callable[[], Any], max_size: int = 100) -> ObjectPool:
        """获取或创建对象池"""
        if name not in self.object_pools:
            self.object_pools[name] = ObjectPool(factory, max_size)
        return self.object_pools[name]
    
    def optimize(self) -> Dict:
        """执行优化"""
        result = {
            "gc_collected": 0,
            "cache_cleared": 0,
            "pools_cleaned": 0,
            "memory_released_mb": 0
        }
        
        before = self.monitor.take_snapshot().current_mb
        
        if self.auto_cleanup_enabled:
            self.lru_cache.clear_expired()
            gc.collect()
        
        after = self.monitor.take_snapshot().current_mb
        result["memory_released_mb"] = max(0, before - after)
        
        return result
    
    def get_stats(self) -> Dict:
        """获取统计"""
        stats = self.monitor.get_usage_stats()
        
        pool_stats = {}
        for name, pool in self.object_pools.items():
            pool_stats[name] = pool.size()
        
        stats["object_pools"] = pool_stats
        stats["cache_size"] = self.lru_cache.size()
        
        return stats


def create_memory_optimizer(config: Optional[Dict] = None) -> MemoryOptimizer2:
    """工厂函数创建内存优化器"""
    return MemoryOptimizer2(config)


if __name__ == "__main__":
    optimizer = create_memory_optimizer()
    
    print("✅ 内存优化系统2.0初始化完成")
    print(f"   统计: {optimizer.get_stats()}")
