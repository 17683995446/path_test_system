"""
增量缓存系统 - 第二阶段核心优化
================================

目标：支持增量分析、断点续传、避免重复计算
"""

import os
import json
import hashlib
import time
from typing import Any, Dict, Optional, List, Callable
from dataclasses import dataclass, field
from pathlib import Path
import fcntl
from datetime import datetime


@dataclass
class FileFingerprint:
    """文件指纹"""
    file_path: str
    content_hash: str
    mtime: float
    size: int
    line_count: int
    
    def to_dict(self) -> Dict:
        return {
            'file_path': self.file_path,
            'content_hash': self.content_hash,
            'mtime': self.mtime,
            'size': self.size,
            'line_count': self.line_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FileFingerprint':
        return cls(**data)


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    created_at: float
    last_accessed: float
    access_count: int
    fingerprint: Optional[FileFingerprint] = None
    metadata: Dict = field(default_factory=dict)
    
    def is_valid(self, fingerprint: Optional[FileFingerprint] = None) -> bool:
        """检查缓存是否有效"""
        if fingerprint and self.fingerprint:
            return fingerprint.content_hash == self.fingerprint.content_hash
        return True


class IncrementalCacheSystem:
    """
    增量缓存系统
    =============
    
    核心特性：
    1. 文件指纹追踪
    2. 智能缓存策略
    3. 断点续传
    4. 增量更新
    """
    
    def __init__(self, cache_dir: str = "/tmp/pathtest_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 内存缓存
        self.memory_cache: Dict[str, CacheEntry] = {}
        
        # 持久化缓存索引
        self.index_file = self.cache_dir / "cache_index.json"
        self.fingerprint_file = self.cache_dir / "fingerprints.json"
        
        # 配置
        self.max_memory_entries = 1000
        self.default_ttl = 24 * 3600  # 24小时
        
        # 加载索引
        self._load_index()
    
    def _load_index(self):
        """加载索引"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    data = json.load(f)
                    # 只加载最近的条目到内存
                    for key, entry_data in list(data.items())[:self.max_memory_entries]:
                        self.memory_cache[key] = CacheEntry(**entry_data)
            except:
                pass
    
    def _save_index(self):
        """保存索引"""
        data = {
            key: {
                'key': entry.key,
                'created_at': entry.created_at,
                'last_accessed': entry.last_accessed,
                'access_count': entry.access_count,
                'metadata': entry.metadata
            }
            for key, entry in self.memory_cache.items()
        }
        
        with open(self.index_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def compute_fingerprint(self, file_path: str) -> Optional[FileFingerprint]:
        """计算文件指纹"""
        try:
            stat = os.stat(file_path)
            with open(file_path, 'rb') as f:
                content = f.read()
                content_hash = hashlib.sha256(content).hexdigest()
            
            # 计算行数
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                line_count = sum(1 for _ in f)
            
            return FileFingerprint(
                file_path=file_path,
                content_hash=content_hash,
                mtime=stat.st_mtime,
                size=stat.st_size,
                line_count=line_count
            )
        except Exception as e:
            return None
    
    def get(self, key: str, fingerprint: Optional[FileFingerprint] = None) -> Optional[Any]:
        """获取缓存"""
        if key not in self.memory_cache:
            return None
        
        entry = self.memory_cache[key]
        
        # 检查有效性
        if not entry.is_valid(fingerprint):
            del self.memory_cache[key]
            return None
        
        # 更新访问信息
        entry.last_accessed = time.time()
        entry.access_count += 1
        
        return entry.value
    
    def set(self, key: str, value: Any, fingerprint: Optional[FileFingerprint] = None):
        """设置缓存"""
        # LRU淘汰
        if len(self.memory_cache) >= self.max_memory_entries:
            self._evict_lru()
        
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=time.time(),
            last_accessed=time.time(),
            access_count=1,
            fingerprint=fingerprint
        )
        
        self.memory_cache[key] = entry
        self._save_index()
    
    def _evict_lru(self):
        """LRU淘汰"""
        if not self.memory_cache:
            return
        
        # 找到最久未使用的
        lru_key = min(
            self.memory_cache.keys(),
            key=lambda k: self.memory_cache[k].last_accessed
        )
        
        del self.memory_cache[lru_key]
    
    def invalidate(self, key: str):
        """使缓存失效"""
        if key in self.memory_cache:
            del self.memory_cache[key]
            self._save_index()
    
    def clear(self):
        """清空所有缓存"""
        self.memory_cache.clear()
        if self.index_file.exists():
            self.index_file.unlink()
    
    def get_stats(self) -> Dict:
        """获取缓存统计"""
        total_accesses = sum(e.access_count for e in self.memory_cache.values())
        return {
            'total_entries': len(self.memory_cache),
            'total_accesses': total_accesses,
            'max_entries': self.max_memory_entries,
            'cache_dir': str(self.cache_dir)
        }


class IncrementalProcessor:
    """
    增量处理器
    =============
    
    使用缓存系统实现增量处理
    """
    
    def __init__(self, cache_system: IncrementalCacheSystem):
        self.cache = cache_system
        self.processed_files: List[str] = []
        self.failed_files: List[str] = []
        self.skipped_files: List[str] = []
    
    def should_process_file(self, file_path: str) -> bool:
        """判断文件是否需要处理"""
        fingerprint = self.cache.compute_fingerprint(file_path)
        
        if not fingerprint:
            return True
        
        cache_key = f"file_analysis:{fingerprint.content_hash}"
        cached = self.cache.get(cache_key, fingerprint)
        
        if cached is not None:
            self.skipped_files.append(file_path)
            return False
        
        return True
    
    def process_with_cache(
        self,
        file_path: str,
        process_func: Callable,
        force: bool = False
    ) -> Any:
        """使用缓存处理文件"""
        fingerprint = self.cache.compute_fingerprint(file_path)
        
        if not fingerprint:
            raise ValueError(f"无法计算文件指纹: {file_path}")
        
        cache_key = f"file_analysis:{fingerprint.content_hash}"
        
        # 检查缓存
        if not force:
            cached = self.cache.get(cache_key, fingerprint)
            if cached is not None:
                self.skipped_files.append(file_path)
                return cached
        
        # 执行处理
        try:
            result = process_func(file_path)
            self.processed_files.append(file_path)
            
            # 保存缓存
            self.cache.set(cache_key, result, fingerprint)
            
            return result
        except Exception as e:
            self.failed_files.append(file_path)
            raise
    
    def get_progress_report(self) -> Dict:
        """获取进度报告"""
        total = len(self.processed_files) + len(self.skipped_files) + len(self.failed_files)
        return {
            'total_files': total,
            'processed': len(self.processed_files),
            'skipped': len(self.skipped_files),
            'failed': len(self.failed_files),
            'cache_hit_rate': len(self.skipped_files) / total if total > 0 else 0
        }


# ============ 演示 ============

def demo_incremental_cache():
    """演示增量缓存"""
    print("\n" + "="*80)
    print("🚀 增量缓存系统演示")
    print("="*80)
    
    # 1. 初始化
    cache = IncrementalCacheSystem("/tmp/pathtest_demo_cache")
    processor = IncrementalProcessor(cache)
    
    # 2. 示例处理函数
    def process_python_file(file_path: str) -> Dict:
        """模拟文件处理"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        return {
            'file': file_path,
            'lines': len(lines),
            'processed_at': datetime.now().isoformat()
        }
    
    # 3. 处理文件（第一次）
    print("\n第一次处理:")
    test_file = "/workspace/path_test_system/src/core/context.py"
    
    if os.path.exists(test_file):
        # 第一次处理
        result1 = processor.process_with_cache(test_file, process_python_file)
        print(f"  ✅ 首次处理: {result1['lines']} 行")
        print(f"  📊 进度: {processor.get_progress_report()}")
        
        # 第二次处理（应该使用缓存）
        result2 = processor.process_with_cache(test_file, process_python_file)
        print(f"\n第二次处理:")
        print(f"  ✅ 缓存命中（跳过）: {result2['lines']} 行")
        print(f"  📊 进度: {processor.get_progress_report()}")
    
    # 4. 缓存统计
    print("\n" + "="*80)
    print("📊 缓存统计")
    print("="*80)
    stats = cache.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "="*80)
    print("✅ 增量缓存演示完成！")
    print("="*80)


if __name__ == "__main__":
    demo_incremental_cache()
