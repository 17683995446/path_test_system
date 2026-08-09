"""
增量计算引擎
======================================================================

只处理变更的内容，大幅提升处理速度
"""

import os
import time
import hashlib
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from pathlib import Path
import pickle


@dataclass
class FileFingerprint:
    """文件指纹"""
    file_path: str
    size: int
    mtime: float
    md5_hash: str
    last_processed: float
    
    def to_dict(self) -> Dict:
        return {
            "file_path": self.file_path,
            "size": self.size,
            "mtime": self.mtime,
            "md5_hash": self.md5_hash,
            "last_processed": self.last_processed
        }


def calculate_file_hash(file_path: str) -> str:
    """计算文件MD5哈希"""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except:
        return ""


class IncrementalCache:
    """增量缓存"""
    
    def __init__(self, cache_file: str = ".incremental_cache.pkl"):
        self.cache_file = cache_file
        self.fingerprints: Dict[str, FileFingerprint] = {}
        self.processed_results: Dict[str, Any] = {}
        
        self._load_cache()
    
    def _load_cache(self) -> None:
        """加载缓存"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "rb") as f:
                    data = pickle.load(f)
                    self.fingerprints = data.get("fingerprints", {})
                    self.processed_results = data.get("results", {})
            except:
                pass
    
    def _save_cache(self) -> None:
        """保存缓存"""
        try:
            with open(self.cache_file, "wb") as f:
                pickle.dump({
                    "fingerprints": self.fingerprints,
                    "results": self.processed_results
                }, f)
        except:
            pass
    
    def get_file_fingerprint(self, file_path: str) -> Optional[FileFingerprint]:
        """获取文件指纹"""
        if not os.path.exists(file_path):
            return None
        
        stat = os.stat(file_path)
        file_hash = calculate_file_hash(file_path)
        
        return FileFingerprint(
            file_path=file_path,
            size=stat.st_size,
            mtime=stat.st_mtime,
            md5_hash=file_hash,
            last_processed=time.time()
        )
    
    def is_file_changed(self, file_path: str) -> bool:
        """检查文件是否变更"""
        if file_path not in self.fingerprints:
            return True
        
        current_fingerprint = self.get_file_fingerprint(file_path)
        if not current_fingerprint:
            return True
        
        cached_fingerprint = self.fingerprints[file_path]
        
        return (
            current_fingerprint.size != cached_fingerprint.size
            or current_fingerprint.mtime != cached_fingerprint.mtime
            or current_fingerprint.md5_hash != cached_fingerprint.md5_hash
        )
    
    def update_file(self, file_path: str, result: Any) -> None:
        """更新文件"""
        fingerprint = self.get_file_fingerprint(file_path)
        if fingerprint:
            self.fingerprints[file_path] = fingerprint
            self.processed_results[file_path] = result
            self._save_cache()
    
    def get_cached_result(self, file_path: str) -> Optional[Any]:
        """获取缓存结果"""
        return self.processed_results.get(file_path)
    
    def get_changed_files(self, file_paths: List[str]) -> List[str]:
        """获取变更的文件列表"""
        return [fp for fp in file_paths if self.is_file_changed(fp)]
    
    def cleanup_old_entries(self, max_age_days: int = 30) -> int:
        """清理旧条目"""
        cutoff = time.time() - (max_age_days * 86400)
        removed = 0
        
        keys_to_remove = []
        for file_path, fingerprint in self.fingerprints.items():
            if fingerprint.last_processed < cutoff:
                keys_to_remove.append(file_path)
        
        for key in keys_to_remove:
            del self.fingerprints[key]
            if key in self.processed_results:
                del self.processed_results[key]
            removed += 1
        
        if removed > 0:
            self._save_cache()
        
        return removed


class IncrementalComputationEngine:
    """
    增量计算引擎
    ==============================================================
    """
    
    def __init__(self, cache_file: str = ".incremental_cache.pkl"):
        self.cache = IncrementalCache(cache_file)
        self.stats = {
            "total_files": 0,
            "changed_files": 0,
            "cached_files": 0,
            "processing_time": 0.0
        }
        
        print("🚀 增量计算引擎初始化完成")
    
    def process_files(
        self,
        file_paths: List[str],
        process_func: Callable
    ) -> Dict[str, Any]:
        """
        处理文件（仅变更文件）
        
        Args:
            file_paths: 文件列表
            process_func: 处理函数
        
        Returns:
            结果字典
        """
        start_time = time.time()
        results: Dict[str, Any] = {}
        
        self.stats["total_files"] = len(file_paths)
        
        changed_files = self.cache.get_changed_files(file_paths)
        cached_files = [fp for fp in file_paths if fp not in changed_files]
        
        self.stats["changed_files"] = len(changed_files)
        self.stats["cached_files"] = len(cached_files)
        
        # 获取缓存结果
        for file_path in cached_files:
            cached_result = self.cache.get_cached_result(file_path)
            if cached_result is not None:
                results[file_path] = cached_result
        
        # 处理变更文件
        for file_path in changed_files:
            try:
                result = process_func(file_path)
                results[file_path] = result
                self.cache.update_file(file_path, result)
            except Exception as e:
                results[file_path] = {"error": str(e)}
        
        self.stats["processing_time"] = time.time() - start_time
        
        return results
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return self.stats
    
    def get_cache_summary(self) -> Dict:
        """获取缓存摘要"""
        return {
            "cached_files": len(self.cache.fingerprints),
            "cache_file": self.cache.cache_file
        }


def create_incremental_engine(cache_file: str = ".incremental_cache.pkl") -> IncrementalComputationEngine:
    """创建增量计算引擎"""
    return IncrementalComputationEngine(cache_file)


if __name__ == "__main__":
    engine = create_incremental_engine()
    
    print("✅ 增量计算引擎初始化完成")
    print(f"   缓存摘要: {engine.get_cache_summary()}")
