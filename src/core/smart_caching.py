"""
智能缓存策略与可视化增强
======================================================================

智能缓存失效、实时仪表盘
"""

import time
import random
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from collections import OrderedDict
import threading


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    access_count: int = 0
    last_access: float = 0.0
    ttl: float = 3600.0
    created_at: float = 0.0


class SmartCache:
    """
    智能缓存
    
    支持多种淘汰策略：LRU、LFU、TTL
    """
    
    STRATEGY_LRU = "LRU"
    STRATEGY_LFU = "LFU"
    STRATEGY_TTL = "TTL"
    
    def __init__(
        self,
        max_size: int = 10000,
        default_ttl: float = 3600.0,
        strategy: str = "LRU"
    ):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.strategy = strategy
        
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: OrderedDict = OrderedDict()
        self.lock = threading.Lock()
        
        print("🧠 智能缓存初始化完成")
        print(f"   策略: {strategy}")
        print(f"   容量: {max_size}")
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        with self.lock:
            if key not in self.cache:
                return None
            
            entry = self.cache[key]
            
            if self._is_expired(entry):
                del self.cache[key]
                if key in self.access_order:
                    del self.access_order[key]
                return None
            
            # 更新访问统计
            entry.access_count += 1
            entry.last_access = time.time()
            
            if self.strategy == self.STRATEGY_LRU:
                if key in self.access_order:
                    self.access_order.move_to_end(key)
                else:
                    self.access_order[key] = None
            
            return entry.value
    
    def put(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """设置缓存"""
        with self.lock:
            if len(self.cache) >= self.max_size:
                self._evict()
            
            entry = CacheEntry(
                key=key,
                value=value,
                access_count=0,
                last_access=time.time(),
                ttl=ttl or self.default_ttl,
                created_at=time.time()
            )
            
            self.cache[key] = entry
            self.access_order[key] = None
    
    def _evict(self) -> None:
        """淘汰条目"""
        if not self.cache:
            return
        
        if self.strategy == self.STRATEGY_LRU:
            if self.access_order:
                oldest_key = next(iter(self.access_order))
                self._remove(oldest_key)
        elif self.strategy == self.STRATEGY_LFU:
            min_key = min(self.cache.keys(), key=lambda k: self.cache[k].access_count)
            self._remove(min_key)
        else:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k].created_at)
            self._remove(oldest_key)
    
    def _remove(self, key: str) -> None:
        """移除条目"""
        if key in self.cache:
            del self.cache[key]
        if key in self.access_order:
            del self.access_order[key]
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """判断过期"""
        return (time.time() - entry.created_at) > entry.ttl
    
    def clear(self) -> None:
        """清空"""
        with self.lock:
            self.cache.clear()
            self.access_order.clear()
    
    def size(self) -> int:
        """大小"""
        with self.lock:
            return len(self.cache)
    
    def get_stats(self) -> Dict:
        """获取统计"""
        with self.lock:
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "strategy": self.strategy
            }


class PerformanceDashboard:
    """性能仪表盘"""
    
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
        self.start_time = time.time()
        self.lock = threading.Lock()
    
    def record(self, name: str, value: float) -> None:
        """记录指标"""
        with self.lock:
            if name not in self.metrics:
                self.metrics[name] = []
            self.metrics[name].append(value)
            if len(self.metrics[name]) > 1000:
                self.metrics[name] = self.metrics[name][-1000:]
    
    def get_metric_stats(self, name: str) -> Optional[Dict]:
        """获取指标统计"""
        with self.lock:
            if name not in self.metrics or not self.metrics[name]:
                return None
            
            values = self.metrics[name]
            return {
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
                "count": len(values),
                "latest": values[-1]
            }
    
    def get_all_stats(self) -> Dict:
        """获取所有统计"""
        stats = {}
        for name in self.metrics:
            stat = self.get_metric_stats(name)
            if stat:
                stats[name] = stat
        return stats
    
    def print_dashboard(self) -> None:
        """打印仪表盘"""
        print("=" * 80)
        print("📊 性能仪表盘")
        print("=" * 80)
        
        uptime = time.time() - self.start_time
        print(f"\n运行时间: {uptime:.2f}秒")
        
        all_stats = self.get_all_stats()
        for name, stat in all_stats.items():
            print(f"\n{name}:")
            print(f"  平均值: {stat['avg']:.4f}")
            print(f"  最小值: {stat['min']:.4f}")
            print(f"  最大值: {stat['max']:.4f}")
            print(f"  最新值: {stat['latest']:.4f}")
            print(f"  样本数: {stat['count']}")


def create_smart_cache(
    max_size: int = 10000,
    strategy: str = "LRU"
) -> SmartCache:
    """创建智能缓存"""
    return SmartCache(max_size=max_size, strategy=strategy)


def create_dashboard() -> PerformanceDashboard:
    """创建仪表盘"""
    return PerformanceDashboard()


if __name__ == "__main__":
    cache = create_smart_cache()
    dashboard = create_dashboard()
    
    cache.put("test", "value")
    print("缓存测试:", cache.get("test"))
    
    dashboard.record("latency", 0.1)
    dashboard.print_dashboard()
