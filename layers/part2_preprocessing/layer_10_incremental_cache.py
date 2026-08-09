"""
Layer 10: Incremental Cache Layer (增量缓存决策层)

该层负责增量缓存决策，判断哪些文件需要重新处理，哪些可以使用缓存。
通过文件哈希比对和时间戳分析，优化处理效率。
"""

from typing import Any, Dict, List, Optional, Set
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime


class CacheEntry:
    """缓存条目数据结构"""
    
    def __init__(self, file_path: str, file_hash: str, 
                 content_hash: str, processed_at: str,
                 metadata: Optional[Dict[str, Any]] = None):
        self.file_path = file_path
        self.file_hash = file_hash
        self.content_hash = content_hash
        self.processed_at = processed_at
        self.metadata = metadata or {}
        self.hit_count = 0
        self.last_accessed = processed_at
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "file_path": self.file_path,
            "file_hash": self.file_hash,
            "content_hash": self.content_hash,
            "processed_at": self.processed_at,
            "metadata": self.metadata,
            "hit_count": self.hit_count,
            "last_accessed": self.last_accessed
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CacheEntry':
        """从字典创建缓存条目"""
        entry = cls(
            file_path=data["file_path"],
            file_hash=data["file_hash"],
            content_hash=data["content_hash"],
            processed_at=data["processed_at"],
            metadata=data.get("metadata", {})
        )
        entry.hit_count = data.get("hit_count", 0)
        entry.last_accessed = data.get("last_accessed", data["processed_at"])
        return entry


class CacheDecision:
    """缓存决策结果"""
    
    def __init__(self):
        self.uncached_files: List[str] = []
        self.cached_files: List[str] = []
        self.invalidated_files: List[str] = []
        self.new_files: List[str] = []
        self.modified_files: List[str] = []
        self.cache_hit_rate = 0.0
        self.processing_time_saved_ms = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "uncached_files": self.uncached_files,
            "cached_files": self.cached_files,
            "invalidated_files": self.invalidated_files,
            "new_files": self.new_files,
            "modified_files": self.modified_files,
            "cache_hit_rate": self.cache_hit_rate,
            "processing_time_saved_ms": self.processing_time_saved_ms
        }


class IncrementalCacheLayer:
    """
    增量缓存决策层
    
    负责增量缓存管理，通过智能判断文件变更情况来决定：
    - 哪些文件需要重新处理（新增或修改）
    - 哪些文件可以使用缓存（未变更）
    - 哪些缓存需要失效（依赖文件变更）
    
    核心功能：
    - 文件哈希计算与比对
    - 缓存命中/未命中决策
    - 依赖追踪与级联失效
    - 缓存性能统计
    
    Attributes:
        description: 层的功能描述
        input_type: 输入数据类型 (PipelineContext)
        output_type: 输出数据类型 (CacheDecision)
    """
    
    description: str = "增量缓存决策层 - 智能判断文件变更并决策缓存使用"
    input_type: str = "PipelineContext"
    output_type: str = "CacheDecision"
    
    DEFAULT_CACHE_DIR: str = ".path_test_cache"
    DEFAULT_CACHE_TTL_DAYS: int = 7
    
    HASH_ALGORITHM: str = "sha256"
    
    def __init__(self, cache_dir: Optional[str] = None, 
                 cache_ttl_days: Optional[int] = None):
        """
        初始化增量缓存层
        
        Args:
            cache_dir: 缓存目录路径，默认使用项目根目录下的 .path_test_cache
            cache_ttl_days: 缓存有效期（天），默认7天
        """
        self.cache_dir = cache_dir or self.DEFAULT_CACHE_DIR
        self.cache_ttl_days = cache_ttl_days or self.DEFAULT_CACHE_TTL_DAYS
        self._cache: Dict[str, CacheEntry] = {}
        self._dependency_graph: Dict[str, Set[str]] = {}
        self._load_cache()
    
    def process(self, context: Any) -> CacheDecision:
        """
        执行增量缓存决策
        
        Args:
            context: PipelineContext对象，包含以下预期字段：
                - scanned_files: 扫描到的文件列表 (List[Dict])
                    - 每个Dict包含: file_path, content, checksum等
                - cache_options: 缓存选项 (dict, 可选)
                    - force_refresh: 是否强制刷新所有缓存 (默认False)
                    - ignore_patterns: 忽略的文件模式 (List[str])
                    - track_dependencies: 是否追踪依赖关系 (默认True)
                - previous_cache: 之前的缓存数据 (可选，用于跨会话)
        
        Returns:
            CacheDecision: 缓存决策结果，包含：
                - uncached_files: 需要完整处理的文件列表
                - cached_files: 可使用缓存的文件列表
                - invalidated_files: 缓存失效的文件列表
                - new_files: 新增文件列表
                - modified_files: 修改文件列表
                - cache_hit_rate: 缓存命中率
                - processing_time_saved_ms: 预估节省的处理时间（毫秒）
        
        Decision Logic:
            1. 计算当前文件的哈希值
            2. 与缓存中的哈希值比对
            3. 判断文件状态：新增/未修改/已修改/已删除
            4. 追踪依赖关系，确定级联失效
            5. 输出决策结果
        
        Example:
            >>> layer = IncrementalCacheLayer()
            >>> ctx = create_context()
            >>> ctx.set('scanned_files', [{'file_path': 'a.py', 'checksum': 'xxx'}])
            >>> decision = layer.process(ctx)
            >>> print(f"需要处理: {len(decision.uncached_files)} 个文件")
        """
        scanned_files = context.get('scanned_files', [])
        cache_options = context.get('cache_options', {})
        
        force_refresh = cache_options.get('force_refresh', False)
        ignore_patterns = cache_options.get('ignore_patterns', [])
        track_dependencies = cache_options.get('track_dependencies', True)
        
        decision = CacheDecision()
        
        all_files = set()
        current_hashes = {}
        
        for file_info in scanned_files:
            file_path = file_info.get('file_path', '')
            if not file_path or self._matches_pattern(file_path, ignore_patterns):
                continue
            
            all_files.add(file_path)
            
            if force_refresh:
                decision.uncached_files.append(file_path)
                continue
            
            content = file_info.get('content', '')
            current_hash = self._compute_hash(content or '')
            current_hashes[file_path] = current_hash
            
            cached_entry = self._cache.get(file_path)
            
            if cached_entry is None:
                decision.new_files.append(file_path)
                decision.uncached_files.append(file_path)
            elif cached_entry.content_hash != current_hash:
                decision.modified_files.append(file_path)
                decision.uncached_files.append(file_path)
                decision.invalidated_files.append(file_path)
            elif self._is_cache_expired(cached_entry):
                decision.modified_files.append(file_path)
                decision.uncached_files.append(file_path)
            else:
                decision.cached_files.append(file_path)
                cached_entry.hit_count += 1
                cached_entry.last_accessed = self._get_timestamp()
        
        if track_dependencies:
            self._update_dependency_graph(decision.modified_files)
            cascade_invalidations = self._get_cascade_invalidation(decision.modified_files)
            decision.invalidated_files.extend(cascade_invalidations)
            for invalidated in cascade_invalidations:
                if invalidated in decision.cached_files:
                    decision.cached_files.remove(invalidated)
                    if invalidated not in decision.uncached_files:
                        decision.uncached_files.append(invalidated)
        
        total_files = len(all_files)
        if total_files > 0:
            decision.cache_hit_rate = len(decision.cached_files) / total_files
        
        avg_processing_time_per_file_ms = 100.0
        decision.processing_time_saved_ms = len(decision.cached_files) * avg_processing_time_per_file_ms
        
        self._save_cache()
        
        context.set('cache_decision', decision)
        context.set('uncached_files', decision.uncached_files)
        context.set('cached_files', decision.cached_files)
        context.set('cache_hit_rate', decision.cache_hit_rate)
        
        return decision
    
    def _compute_hash(self, content: str) -> str:
        """计算内容的哈希值"""
        if self.HASH_ALGORITHM == "sha256":
            return hashlib.sha256(content.encode('utf-8')).hexdigest()
        elif self.HASH_ALGORITHM == "md5":
            return hashlib.md5(content.encode('utf-8')).hexdigest()
        else:
            return hashlib.blake2b(content.encode('utf-8')).hexdigest()
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        return datetime.now().isoformat()
    
    def _is_cache_expired(self, entry: CacheEntry) -> bool:
        """检查缓存是否已过期"""
        try:
            processed_time = datetime.fromisoformat(entry.processed_at)
            current_time = datetime.now()
            delta = current_time - processed_time
            return delta.days > self.cache_ttl_days
        except Exception:
            return True
    
    def _matches_pattern(self, file_path: str, patterns: List[str]) -> bool:
        """检查文件是否匹配忽略模式"""
        from fnmatch import fnmatch
        for pattern in patterns:
            if fnmatch(file_path, pattern) or fnmatch(os.path.basename(file_path), pattern):
                return True
        return False
    
    def _update_dependency_graph(self, modified_files: List[str]):
        """更新依赖图"""
        for file_path in modified_files:
            if file_path not in self._dependency_graph:
                self._dependency_graph[file_path] = set()
    
    def _get_cascade_invalidation(self, modified_files: List[str]) -> List[str]:
        """获取级联失效的文件列表"""
        invalidated = set()
        files_to_check = list(modified_files)
        
        while files_to_check:
            current_file = files_to_check.pop(0)
            for dependent, dependencies in self._dependency_graph.items():
                if current_file in dependencies and dependent not in invalidated:
                    invalidated.add(dependent)
                    files_to_check.append(dependent)
        
        return list(invalidated)
    
    def _load_cache(self):
        """从磁盘加载缓存"""
        cache_file = os.path.join(self.cache_dir, "incremental_cache.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    for file_path, entry_data in cache_data.items():
                        self._cache[file_path] = CacheEntry.from_dict(entry_data)
            except Exception:
                self._cache = {}
    
    def _save_cache(self):
        """保存缓存到磁盘"""
        os.makedirs(self.cache_dir, exist_ok=True)
        cache_file = os.path.join(self.cache_dir, "incremental_cache.json")
        try:
            cache_data = {file_path: entry.to_dict() for file_path, entry in self._cache.items()}
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
    
    def invalidate_cache(self, file_path: str):
        """手动使指定文件的缓存失效"""
        if file_path in self._cache:
            del self._cache[file_path]
    
    def clear_cache(self):
        """清空所有缓存"""
        self._cache.clear()
        self._dependency_graph.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_entries = len(self._cache)
        total_hits = sum(entry.hit_count for entry in self._cache.values())
        expired_entries = sum(1 for entry in self._cache.values() if self._is_cache_expired(entry))
        
        return {
            "total_entries": total_entries,
            "total_hits": total_hits,
            "expired_entries": expired_entries,
            "valid_entries": total_entries - expired_entries,
            "cache_dir": self.cache_dir,
            "ttl_days": self.cache_ttl_days
        }
    
    def register_dependency(self, dependent_file: str, dependency_file: str):
        """注册文件依赖关系"""
        if dependent_file not in self._dependency_graph:
            self._dependency_graph[dependent_file] = set()
        self._dependency_graph[dependent_file].add(dependency_file)
