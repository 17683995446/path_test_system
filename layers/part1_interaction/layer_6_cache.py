"""
Layer 6: LLM Cache Layer (LLM全局缓存管理层)

该层负责管理和优化LLM调用缓存，减少重复请求和成本。
"""

from typing import Any, Dict, Optional, Tuple
from datetime import datetime, timedelta
from .layer_1_entry import PipelineContext
import hashlib
import json


class CacheEntry:
    """缓存条目数据结构"""

    def __init__(
        self,
        key: str,
        value: Any,
        ttl: int = 3600,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.key = key
        self.value = value
        self.created_at = datetime.now()
        self.expires_at = datetime.now() + timedelta(seconds=ttl)
        self.access_count = 0
        self.last_accessed = datetime.now()
        self.metadata = metadata or {}

    def is_expired(self) -> bool:
        """检查是否过期"""
        return datetime.now() > self.expires_at

    def access(self) -> Any:
        """访问缓存并更新统计"""
        self.access_count += 1
        self.last_accessed = datetime.now()
        return self.value

    def refresh(self, ttl: Optional[int] = None) -> None:
        """刷新缓存TTL"""
        if ttl:
            self.expires_at = datetime.now() + timedelta(seconds=ttl)
        else:
            self.expires_at = datetime.now() + timedelta(
                seconds=(self.expires_at - self.created_at).total_seconds()
            )


class LLMCacheLayer:
    """
    LLM全局缓存管理层

    负责管理和优化LLM调用缓存，包括：
    - 语义缓存（基于请求哈希）
    - TTL管理和过期策略
    - LRU淘汰机制
    - 缓存统计和监控
    - 批量操作支持

    Attributes:
        description: 层的功能描述
        input_type: 输入数据类型
        output_type: 输出数据类型
    """

    description: str = "LLM全局缓存管理层 - 管理LLM调用缓存，减少重复请求"
    input_type: str = "PipelineContext"
    output_type: str = "PipelineContext"

    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        初始化缓存层

        Args:
            max_size: 最大缓存条目数
            default_ttl: 默认TTL（秒）
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_requests": 0
        }

    def process(self, context: PipelineContext) -> PipelineContext:
        """
        处理缓存管理

        Args:
            context: PipelineContext对象，包含：
                - request_id: 请求唯一标识符
                - user_input: 用户输入
                - metadata: 包含llm_request等信息
                - cache_config: 缓存配置

        Returns:
            PipelineContext: 更新后的上下文，包含缓存结果：
                - cache_hit: 是否命中缓存
                - cached_response: 缓存的响应（如果有）
                - cache_stats: 缓存统计信息
                - llm_response: LLM响应（可能来自缓存）

        Example:
            >>> layer = LLMCacheLayer()
            >>> ctx = layer.process(pipeline_context)
            >>> print(ctx.metadata["cache_hit"])  # True or False
        """
        cache_config = context.metadata.get("cache_config", {})
        llm_request = context.metadata.get("llm_request", {})

        if not cache_config.get("enabled", True):
            return self._process_without_cache(context)

        cache_key = self._generate_cache_key(llm_request, context)
        cached_response = self.get(cache_key)

        self._stats["total_requests"] += 1

        if cached_response is not None:
            self._stats["hits"] += 1
            context.metadata["cache_hit"] = True
            context.metadata["cached_response"] = cached_response
            context.metadata["llm_response"] = cached_response
            context.metadata["cache_key"] = cache_key
        else:
            self._stats["misses"] += 1
            context.metadata["cache_hit"] = False
            context.metadata["cache_key"] = cache_key
            self._store_response(context, cache_key, cache_config)

        context.metadata["cache_stats"] = self._get_stats()

        return context

    def _process_without_cache(self, context: PipelineContext) -> PipelineContext:
        """不使用缓存处理"""
        context.metadata["cache_hit"] = False
        context.metadata["cache_enabled"] = False
        return context

    def _generate_cache_key(
        self,
        llm_request: Dict[str, Any],
        context: PipelineContext
    ) -> str:
        """生成缓存键"""
        key_parts = [
            llm_request.get("intent", ""),
            llm_request.get("prompt", ""),
            llm_request.get("model", ""),
            str(sorted(context.metadata.get("parameters", {}).items()))
        ]

        key_string = "|".join(str(part) for part in key_parts)
        return hashlib.sha256(key_string.encode()).hexdigest()

    def _store_response(
        self,
        context: PipelineContext,
        cache_key: str,
        cache_config: Dict[str, Any]
    ) -> None:
        """存储LLM响应到缓存"""
        llm_response = context.metadata.get("llm_response")
        if llm_response is None:
            return

        ttl = cache_config.get("ttl", self._default_ttl)

        if len(self._cache) >= self._max_size:
            self._evict_lru()

        entry = CacheEntry(
            key=cache_key,
            value=llm_response,
            ttl=ttl,
            metadata={
                "intent": context.metadata.get("intent"),
                "model": llm_response.model if hasattr(llm_response, 'model') else None
            }
        )

        self._cache[cache_key] = entry

    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存条目

        Args:
            key: 缓存键

        Returns:
            缓存值，如果不存在或已过期返回None
        """
        entry = self._cache.get(key)

        if entry is None:
            return None

        if entry.is_expired():
            del self._cache[key]
            return None

        return entry.access()

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        设置缓存条目

        Args:
            key: 缓存键
            value: 缓存值
            ttl: TTL（秒），使用默认值如果为None
        """
        if len(self._cache) >= self._max_size and key not in self._cache:
            self._evict_lru()

        self._cache[key] = CacheEntry(
            key=key,
            value=value,
            ttl=ttl if ttl is not None else self._default_ttl
        )

    def _evict_lru(self) -> None:
        """LRU淘汰"""
        if not self._cache:
            return

        lru_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].last_accessed
        )

        del self._cache[lru_key]
        self._stats["evictions"] += 1

    def _get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total = self._stats["total_requests"]
        hit_rate = self._stats["hits"] / total if total > 0 else 0

        return {
            **self._stats,
            "hit_rate": hit_rate,
            "cache_size": len(self._cache),
            "max_size": self._max_size
        }

    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()

    def invalidate(self, key: str) -> bool:
        """
        使指定缓存失效

        Args:
            key: 缓存键

        Returns:
            是否成功删除
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def get_cache_size(self) -> int:
        """获取当前缓存大小"""
        return len(self._cache)
