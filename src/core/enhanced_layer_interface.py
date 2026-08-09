"""
增强层接口系统
======================================================================

统一的50层接口规范，实现类型安全、文档完善的层架构
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable, Type, Generic, TypeVar
from dataclasses import dataclass, field
from enum import Enum, auto
from datetime import datetime
import time


T = TypeVar('T')


class LayerStatus(Enum):
    """层执行状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"
    DEGRADED = "degraded"


class LayerCategory(Enum):
    """层分类枚举"""
    INTERACTION = "interaction"
    PREPROCESSING = "preprocessing"
    ANALYSIS = "analysis"
    EXECUTION = "execution"
    OUTPUT = "output"


@dataclass
class LayerExecutionStats:
    """层执行统计"""
    start_time: float = 0.0
    end_time: float = 0.0
    execution_time: float = 0.0
    memory_used_mb: float = 0.0
    cpu_used_percent: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    errors_recovered: int = 0
    warnings_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "execution_time": self.execution_time,
            "memory_used_mb": self.memory_used_mb,
            "cpu_used_percent": self.cpu_used_percent,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "errors_recovered": self.errors_recovered,
            "warnings_count": self.warnings_count
        }


@dataclass
class LayerOutput:
    """层输出数据"""
    data: Any
    format: str = "dict"
    size_bytes: int = 0
    cached: bool = False
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "data": self.data,
            "format": self.format,
            "size_bytes": self.size_bytes,
            "cached": self.cached,
            "warnings": self.warnings
        }


@dataclass
class LayerResult:
    """统一的层执行结果"""
    layer_id: str
    layer_name: str
    layer_category: LayerCategory
    status: LayerStatus
    output: Optional[LayerOutput] = None
    error: Optional[Dict[str, Any]] = None
    warnings: List[str] = field(default_factory=list)
    stats: LayerExecutionStats = field(default_factory=LayerExecutionStats)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    version: str = "2.0.0"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "layer_id": self.layer_id,
            "layer_name": self.layer_name,
            "layer_category": self.layer_category.value,
            "status": self.status.value,
            "output": self.output.to_dict() if self.output else None,
            "error": self.error,
            "warnings": self.warnings,
            "stats": self.stats.to_dict(),
            "timestamp": self.timestamp,
            "version": self.version
        }
    
    def is_success(self) -> bool:
        return self.status in [LayerStatus.COMPLETED, LayerStatus.DEGRADED]


class EnhancedBaseLayer(ABC):
    """
    增强的基础层接口
    ==========================================================================
    
    所有50层的统一基类，提供完整的类型安全、文档、性能监控功能
    """
    
    layer_id: str = "base_layer"
    layer_name: str = "Base Layer"
    layer_description: str = "Enhanced Base Layer"
    layer_category: LayerCategory = LayerCategory.ANALYSIS
    version: str = "2.0.0"
    is_optional: bool = False
    depends_on: List[str] = field(default_factory=list)
    timeout_seconds: int = 300
    max_retries: int = 3
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.stats = LayerExecutionStats()
        self.warnings: List[str] = []
        self.initialized = False
    
    def init(self) -> bool:
        """初始化层（调用run之前执行）"""
        if not self.initialized:
            self._on_init()
            self.initialized = True
        return True
    
    def _on_init(self) -> None:
        """初始化钩子（子类可重写）"""
        pass
    
    @abstractmethod
    def should_run(self, context: Dict[str, Any]) -> bool:
        """
        判断是否应该运行
        
        Args:
            context: 上下文数据
        
        Returns:
            是否应该运行
        """
        return True
    
    @abstractmethod
    def run(self, context: Dict[str, Any]) -> LayerOutput:
        """
        执行层的核心逻辑
        
        Args:
            context: 上下文数据
        
        Returns:
            层输出
        """
        pass
    
    def validate(self, context: Dict[str, Any]) -> bool:
        """验证前置条件（返回True表示验证通过）"""
        return True
    
    def cleanup(self, context: Dict[str, Any]) -> None:
        """清理资源"""
        pass
    
    def execute(self, context: Dict[str, Any]) -> LayerResult:
        """
        完整执行流程（包括初始化、执行、清理）
        
        Args:
            context: 上下文
        
        Returns:
            执行结果
        """
        result = LayerResult(
            layer_id=self.layer_id,
            layer_name=self.layer_name,
            layer_category=self.layer_category,
            status=LayerStatus.PENDING
        )
        
        start_time = time.time()
        self.stats.start_time = start_time
        
        try:
            if not self.should_run(context):
                result.status = LayerStatus.SKIPPED
                return result
            
            if not self.validate(context):
                result.status = LayerStatus.FAILED
                result.error = {"message": "Validation failed"}
                return result
            
            result.status = LayerStatus.RUNNING
            self.init()
            
            output = self.run(context)
            result.output = output
            result.status = LayerStatus.COMPLETED
            
        except Exception as e:
            result.status = LayerStatus.FAILED
            result.error = {
                "message": str(e),
                "type": type(e).__name__
            }
            self._on_error(e)
        finally:
            self.stats.end_time = time.time()
            self.stats.execution_time = self.stats.end_time - self.stats.start_time
            self.cleanup(context)
            result.stats = self.stats
            result.warnings = self.warnings
        
        return result
    
    def _on_error(self, error: Exception) -> None:
        """错误处理钩子（子类可重写）"""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """获取层信息"""
        return {
            "layer_id": self.layer_id,
            "layer_name": self.layer_name,
            "description": self.layer_description,
            "category": self.layer_category.value,
            "version": self.version,
            "is_optional": self.is_optional,
            "depends_on": self.depends_on,
            "timeout": self.timeout_seconds,
            "max_retries": self.max_retries
        }


def create_layer_info(layer: Type[EnhancedBaseLayer]) -> Dict[str, Any]:
    """创建层信息字典"""
    return {
        "layer_id": layer.layer_id,
        "layer_name": layer.layer_name,
        "description": layer.layer_description,
        "category": layer.layer_category.value,
        "version": layer.version,
        "is_optional": layer.is_optional,
        "depends_on": layer.depends_on
    }


# ========================================================
# 阶段1优化点1：层接口规范
# ========================================================
