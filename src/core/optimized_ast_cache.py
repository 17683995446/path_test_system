"""
OptimizedASTCacheSystem - 优化的AST缓存系统
=========================================

多级缓存架构：
- L1: 内存LRU缓存（快速访问）
- L2: 磁盘持久化缓存（大容量存储）

核心特性：
1. 多级缓存（内存+磁盘）
2. LRU淘汰策略
3. 文件指纹检测
4. 自动失效机制
5. 并发安全
6. 跨会话复用

作者：PathTestSystem
版本：2.0.0
"""

import os
import ast
import json
import time
import hashlib
import pickle
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from collections import OrderedDict
from threading import Lock
import threading


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    fingerprint: str
    created_at: float
    last_accessed: float
    access_count: int
    size_bytes: int
    ttl: float = 3600.0  # 默认1小时
    level: int = 1  # 1=L1内存, 2=L2磁盘
    
    def is_expired(self, current_time: float) -> bool:
        """检查是否过期"""
        return (current_time - self.created_at) > self.ttl
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'key': self.key,
            'fingerprint': self.fingerprint,
            'created_at': self.created_at,
            'last_accessed': self.last_accessed,
            'access_count': self.access_count,
            'size_bytes': self.size_bytes,
            'ttl': self.ttl,
            'level': self.level
        }


@dataclass
class CacheStatistics:
    """缓存统计"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    writes: int = 0
    reads: int = 0
    total_size_bytes: int = 0
    l1_hits: int = 0
    l2_hits: int = 0
    
    def get_hit_rate(self) -> float:
        """获取命中率"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    def get_l1_hit_rate(self) -> float:
        """获取L1命中率"""
        l1_total = self.l1_hits + self.misses
        return self.l1_hits / l1_total if l1_total > 0 else 0.0
    
    def to_dict(self) -> Dict:
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': f"{self.get_hit_rate():.2%}",
            'l1_hit_rate': f"{self.get_l1_hit_rate():.2%}",
            'evictions': self.evictions,
            'writes': self.writes,
            'reads': self.reads,
            'total_size_mb': self.total_size_bytes / 1024 / 1024
        }


class LRUCache:
    """
    LRU缓存实现
    =============
    
    最近最少使用缓存
    """
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = Lock()
    
    def get(self, key: str) -> Optional[CacheEntry]:
        """获取缓存"""
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                self.cache.move_to_end(key)
                entry.last_accessed = time.time()
                entry.access_count += 1
                return entry
            return None
    
    def put(self, key: str, entry: CacheEntry):
        """放入缓存"""
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            else:
                if len(self.cache) >= self.max_size:
                    oldest_key = next(iter(self.cache))
                    del self.cache[oldest_key]
            
            self.cache[key] = entry
    
    def remove(self, key: str):
        """移除缓存"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
    
    def clear(self):
        """清空缓存"""
        with self.lock:
            self.cache.clear()
    
    def get_size(self) -> int:
        """获取缓存大小"""
        with self.lock:
            return len(self.cache)
    
    def get_all_entries(self) -> List[CacheEntry]:
        """获取所有条目"""
        with self.lock:
            return list(self.cache.values())


class DiskCache:
    """
    磁盘缓存
    =========
    
    基于文件系统的持久化缓存
    """
    
    def __init__(self, cache_dir: str = "/tmp/pathtest_ast_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.index_file = self.cache_dir / "cache_index.json"
        self.data_dir = self.cache_dir / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        self.index: Dict[str, CacheEntry] = {}
        self.lock = Lock()
        
        self._load_index()
    
    def _load_index(self):
        """加载索引"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for key, entry_data in data.items():
                    self.index[key] = CacheEntry(
                        key=entry_data['key'],
                        value=None,
                        fingerprint=entry_data['fingerprint'],
                        created_at=entry_data['created_at'],
                        last_accessed=entry_data['last_accessed'],
                        access_count=entry_data['access_count'],
                        size_bytes=entry_data['size_bytes'],
                        ttl=entry_data.get('ttl', 3600),
                        level=2
                    )
            except Exception:
                self.index = {}
    
    def _save_index(self):
        """保存索引"""
        try:
            data = {key: entry.to_dict() for key, entry in self.index.items()}
            
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass
    
    def get(self, key: str) -> Optional[CacheEntry]:
        """获取缓存"""
        with self.lock:
            if key not in self.index:
                return None
            
            entry = self.index[key]
            data_file = self.data_dir / f"{hashlib.md5(key.encode()).hexdigest()}.pkl"
            
            if not data_file.exists():
                del self.index[key]
                return None
            
            try:
                with open(data_file, 'rb') as f:
                    entry.value = pickle.load(f)
                
                entry.last_accessed = time.time()
                entry.access_count += 1
                
                return entry
            except Exception:
                del self.index[key]
                return None
    
    def put(self, key: str, entry: CacheEntry):
        """放入缓存"""
        with self.lock:
            data_file = self.data_dir / f"{hashlib.md5(key.encode()).hexdigest()}.pkl"
            
            try:
                with open(data_file, 'wb') as f:
                    pickle.dump(entry.value, f)
                
                entry.level = 2
                self.index[key] = entry
                
                self._save_index()
            except Exception:
                pass
    
    def remove(self, key: str):
        """移除缓存"""
        with self.lock:
            if key in self.index:
                data_file = self.data_dir / f"{hashlib.md5(key.encode()).hexdigest()}.pkl"
                
                if data_file.exists():
                    try:
                        data_file.unlink()
                    except Exception:
                        pass
                
                del self.index[key]
                self._save_index()
    
    def clear(self):
        """清空缓存"""
        with self.lock:
            for key in list(self.index.keys()):
                self.remove(key)
            self.index = {}
            self._save_index()
    
    def get_size(self) -> int:
        """获取缓存大小"""
        with self.lock:
            return len(self.index)


class FingerprintGenerator:
    """
    文件指纹生成器
    ==============
    
    用于检测文件变更
    """
    
    @staticmethod
    def generate_file_fingerprint(file_path: str) -> Optional[str]:
        """
        生成文件指纹
        
        Args:
            file_path: 文件路径
        
        Returns:
            文件指纹或None
        """
        try:
            stat = os.stat(file_path)
            
            fingerprint_data = {
                'path': file_path,
                'mtime': stat.st_mtime,
                'size': stat.st_size,
                'inode': stat.st_ino
            }
            
            fingerprint_str = json.dumps(fingerprint_data, sort_keys=True)
            return hashlib.sha256(fingerprint_str.encode()).hexdigest()
        except Exception:
            return None
    
    @staticmethod
    def generate_content_fingerprint(content: str) -> str:
        """
        生成内容指纹
        
        Args:
            content: 文件内容
        
        Returns:
            内容指纹
        """
        return hashlib.sha256(content.encode()).hexdigest()


class OptimizedASTCacheSystem:
    """
    优化的AST缓存系统 - 主控制器
    =================================
    
    多级缓存架构：
    - L1: 内存LRU缓存（快速访问）
    - L2: 磁盘持久化缓存（大容量存储）
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        self.l1_cache = LRUCache(
            max_size=self.config.get('l1_max_size', 1000)
        )
        
        self.l2_cache = DiskCache(
            cache_dir=self.config.get('l2_cache_dir', '/tmp/pathtest_ast_cache')
        )
        
        self.fingerprint_generator = FingerprintGenerator()
        self.statistics = CacheStatistics()
        
        self.default_ttl = self.config.get('default_ttl', 3600)
        self.auto_promote = self.config.get('auto_promote', True)
        self.fingerprint_check = self.config.get('fingerprint_check', True)
        
        self.lock = Lock()
    
    def get(self, key: str, file_path: Optional[str] = None) -> Optional[Any]:
        """
        获取缓存
        
        Args:
            key: 缓存键
            file_path: 文件路径（用于指纹检测）
        
        Returns:
            缓存值或None
        """
        with self.lock:
            entry = self.l1_cache.get(key)
            
            if entry:
                if self.fingerprint_check and file_path:
                    current_fingerprint = self.fingerprint_generator.generate_file_fingerprint(file_path)
                    if current_fingerprint and entry.fingerprint != current_fingerprint:
                        self.l1_cache.remove(key)
                        self.statistics.misses += 1
                        return None
                
                if entry.is_expired(time.time()):
                    self.l1_cache.remove(key)
                    self.statistics.misses += 1
                    return None
                
                self.statistics.hits += 1
                self.statistics.l1_hits += 1
                return entry.value
            
            entry = self.l2_cache.get(key)
            
            if entry:
                if self.fingerprint_check and file_path:
                    current_fingerprint = self.fingerprint_generator.generate_file_fingerprint(file_path)
                    if current_fingerprint and entry.fingerprint != current_fingerprint:
                        self.l2_cache.remove(key)
                        self.statistics.misses += 1
                        return None
                
                if entry.is_expired(time.time()):
                    self.l2_cache.remove(key)
                    self.statistics.misses += 1
                    return None
                
                if self.auto_promote:
                    entry.level = 1
                    self.l1_cache.put(key, entry)
                
                self.statistics.hits += 1
                self.statistics.l2_hits += 1
                return entry.value
            
            self.statistics.misses += 1
            return None
    
    def put(self, key: str, value: Any, file_path: Optional[str] = None,
           ttl: Optional[float] = None, level: int = 1):
        """
        放入缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            file_path: 文件路径（用于指纹生成）
            ttl: 过期时间（秒）
            level: 缓存级别（1=L1, 2=L2）
        """
        with self.lock:
            fingerprint = None
            if file_path:
                fingerprint = self.fingerprint_generator.generate_file_fingerprint(file_path)
            
            entry = CacheEntry(
                key=key,
                value=value,
                fingerprint=fingerprint or "",
                created_at=time.time(),
                last_accessed=time.time(),
                access_count=1,
                size_bytes=len(pickle.dumps(value)) if hasattr(pickle, 'dumps') else 0,
                ttl=ttl or self.default_ttl,
                level=level
            )
            
            if level == 1:
                self.l1_cache.put(key, entry)
            else:
                self.l2_cache.put(key, entry)
            
            self.statistics.writes += 1
    
    def remove(self, key: str):
        """移除缓存"""
        with self.lock:
            self.l1_cache.remove(key)
            self.l2_cache.remove(key)
    
    def clear(self, level: Optional[int] = None):
        """
        清空缓存
        
        Args:
            level: 缓存级别（None=全部）
        """
        with self.lock:
            if level is None or level == 1:
                self.l1_cache.clear()
            if level is None or level == 2:
                self.l2_cache.clear()
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        with self.lock:
            return {
                'l1_size': self.l1_cache.get_size(),
                'l2_size': self.l2_cache.get_size(),
                'statistics': self.statistics.to_dict()
            }
    
    def cleanup_expired(self):
        """清理过期缓存"""
        with self.lock:
            current_time = time.time()
            
            for entry in self.l1_cache.get_all_entries():
                if entry.is_expired(current_time):
                    self.l1_cache.remove(entry.key)
            
            for key in list(self.l2_cache.index.keys()):
                entry = self.l2_cache.index[key]
                if entry.is_expired(current_time):
                    self.l2_cache.remove(key)


def create_optimized_ast_cache(config: Optional[Dict] = None) -> OptimizedASTCacheSystem:
    """
    创建优化的AST缓存系统工厂函数
    
    Args:
        config: 配置字典
    
    Returns:
        OptimizedASTCacheSystem实例
    """
    return OptimizedASTCacheSystem(config)


if __name__ == "__main__":
    cache = create_optimized_ast_cache({
        'l1_max_size': 100,
        'default_ttl': 3600,
        'auto_promote': True,
        'fingerprint_check': True
    })
    
    print("=" * 80)
    print("Optimized AST Cache System Test")
    print("=" * 80)
    
    test_files = [
        '/workspace/path_test_system/src/core/engine_integrated.py',
        '/workspace/path_test_system/src/core/error_recovery.py'
    ]
    
    print("\nTest 1: Cache Write and Read")
    print("-" * 80)
    
    for file_path in test_files:
        if os.path.exists(file_path):
            print(f"\nProcessing: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            try:
                tree = ast.parse(content)
                key = f"ast_{file_path}"
                
                cache.put(key, tree, file_path=file_path)
                print(f"  ✓ Cached AST for {os.path.basename(file_path)}")
                
                cached_tree = cache.get(key, file_path=file_path)
                if cached_tree:
                    print(f"  ✓ Retrieved cached AST")
                else:
                    print(f"  ✗ Failed to retrieve cached AST")
            except Exception as e:
                print(f"  ✗ Error: {e}")
    
    print("\n\nTest 2: Cache Statistics")
    print("-" * 80)
    
    stats = cache.get_statistics()
    print(f"  L1 Cache Size: {stats['l1_size']}")
    print(f"  L2 Cache Size: {stats['l2_size']}")
    print(f"  Cache Hits: {stats['statistics']['hits']}")
    print(f"  Cache Misses: {stats['statistics']['misses']}")
    print(f"  Hit Rate: {stats['statistics']['hit_rate']}")
    print(f"  L1 Hit Rate: {stats['statistics']['l1_hit_rate']}")
    
    print("\n\nTest 3: Cache Read (Second Access)")
    print("-" * 80)
    
    for file_path in test_files:
        if os.path.exists(file_path):
            key = f"ast_{file_path}"
            cached_tree = cache.get(key, file_path=file_path)
            if cached_tree:
                print(f"  ✓ Retrieved from cache: {os.path.basename(file_path)}")
    
    print("\n\nFinal Statistics:")
    print("-" * 80)
    
    stats = cache.get_statistics()
    print(f"  L1 Cache Size: {stats['l1_size']}")
    print(f"  L2 Cache Size: {stats['l2_size']}")
    print(f"  Cache Hits: {stats['statistics']['hits']}")
    print(f"  Cache Misses: {stats['statistics']['misses']}")
    print(f"  Hit Rate: {stats['statistics']['hit_rate']}")
    print(f"  Writes: {stats['statistics']['writes']}")
    print(f"  Reads: {stats['statistics']['reads']}")
    
    print("\n" + "=" * 80)
    print("Test Complete")
    print("=" * 80)
