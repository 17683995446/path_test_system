"""
错误恢复机制 - 第一阶段核心优化
=================================

目标：实现容错、故障隔离、优雅降级
"""

from typing import Any, Callable, Optional, Dict, List
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
import time
import traceback


class ErrorSeverity(Enum):
    """错误严重级别"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ErrorInfo:
    """错误信息"""
    error_id: str
    error_type: str
    severity: ErrorSeverity
    message: str
    timestamp: float
    layer_id: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    stack_trace: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'error_id': self.error_id,
            'error_type': self.error_type,
            'severity': self.severity.value,
            'message': self.message,
            'timestamp': self.timestamp,
            'layer_id': self.layer_id,
            'context': self.context,
            'stack_trace': self.stack_trace
        }


@dataclass
class LayerExecutionResult:
    """层执行结果（带错误信息）"""
    layer_id: str
    success: bool
    output: Any = None
    error: Any = None
    warnings: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    retry_count: int = 0
    degraded: bool = False


class ErrorRecoverySystem:
    """
    错误恢复系统
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.errors: List[Any] = []
        self.error_counter = 0
        
        self.max_retries = self.config.get('max_retries', 3)
        self.retry_delay = self.config.get('retry_delay', 1.0)
        self.fallback_enabled = self.config.get('fallback_enabled', True)
        
        self.stats = {
            'total_errors': 0,
            'retries': 0,
            'skips': 0,
            'fallbacks': 0,
            'degrades': 0
        }
    
    def register_error(self, error: Exception, layer_id: str, context: Dict) -> Any:
        """注册错误"""
        self.error_counter += 1
        error_info = ErrorInfo(
            error_id=f"ERR-{self.error_counter:04d}",
            error_type=type(error).__name__,
            severity=self._classify_error(error),
            message=str(error),
            timestamp=time.time(),
            layer_id=layer_id,
            context=context,
            stack_trace=traceback.format_exc()
        )
        self.errors.append(error_info)
        self.stats['total_errors'] += 1
        return error_info
    
    def _classify_error(self, error: Exception) -> ErrorSeverity:
        """分类错误"""
        error_type = type(error).__name__
        
        if error_type in ['MemoryError', 'SystemError']:
            return ErrorSeverity.CRITICAL
        elif error_type in ['TimeoutError', 'RuntimeError']:
            return ErrorSeverity.HIGH
        elif error_type in ['ValueError', 'TypeError']:
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW
    
    def should_retry(self, error: Any) -> bool:
        """判断是否应该重试"""
        no_retry_types = ['ValueError', 'TypeError', 'SyntaxError']
        return error.error_type not in no_retry_types
    
    def execute_with_retry(self, func: Callable, layer_id: str, max_retries: Optional[int] = None) -> LayerExecutionResult:
        """带重试的执行"""
        max_retries = max_retries or self.max_retries
        result = LayerExecutionResult(layer_id=layer_id, success=False)
        
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                start_time = time.time()
                output = func()
                result.success = True
                result.output = output
                result.execution_time = time.time() - start_time
                result.retry_count = attempt
                return result
                
            except Exception as e:
                last_error = e
                if attempt < max_retries and self.should_retry(self.register_error(e, layer_id, {})):
                    self.stats['retries'] += 1
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    break
        
        result.error = self.register_error(last_error, layer_id, {}).to_dict()
        result.success = False
        return result
    
    def execute_with_fallback(self, primary_func: Callable, fallback_func: Optional[Callable], layer_id: str) -> LayerExecutionResult:
        """带降级的执行"""
        result = LayerExecutionResult(layer_id=layer_id, success=False)
        
        try:
            start_time = time.time()
            output = primary_func()
            result.success = True
            result.output = output
            result.execution_time = time.time() - start_time
            return result
        except Exception as e:
            result.error = self.register_error(e, layer_id, {}).to_dict()
            
            if self.fallback_enabled and fallback_func:
                try:
                    self.stats['fallbacks'] += 1
                    start_time = time.time()
                    output = fallback_func()
                    result.success = True
                    result.output = output
                    result.degraded = True
                    result.warnings.append(f"使用降级方案: {str(e)}")
                    result.execution_time = time.time() - start_time
                    return result
                except Exception as fallback_error:
                    result.error = self.register_error(fallback_error, layer_id, {}).to_dict()
                    result.success = False
                    return result
            
            return result
    
    def get_error_summary(self) -> Dict:
        """获取错误摘要"""
        return {
            'total_errors': self.stats['total_errors'],
            'retries': self.stats['retries'],
            'skips': self.stats['skips'],
            'fallbacks': self.stats['fallbacks'],
            'degrades': self.stats['degrades'],
            'recent_errors': [e.to_dict() if hasattr(e, 'to_dict') else e for e in self.errors[-10:]]
        }


class LayerIsolationWrapper:
    """层隔离包装器"""
    
    def __init__(self, error_recovery: ErrorRecoverySystem):
        self.error_recovery = error_recovery
        self.layer_results: Dict[str, LayerExecutionResult] = {}
    
    def wrap_layer(self, layer_id: str, layer_func: Callable, fallback_func: Optional[Callable] = None) -> LayerExecutionResult:
        """包装层执行"""
        result = self.error_recovery.execute_with_fallback(
            primary_func=lambda: layer_func(),
            fallback_func=fallback_func,
            layer_id=layer_id
        )
        
        self.layer_results[layer_id] = result
        return result
    
    def get_all_results(self) -> Dict[str, LayerExecutionResult]:
        return self.layer_results
    
    def get_failed_layers(self) -> List[str]:
        return [layer_id for layer_id, result in self.layer_results.items() if not result.success]


def demo_error_recovery():
    """演示错误恢复"""
    print("\n" + "="*80)
    print("🔄 错误恢复系统演示")
    print("="*80)
    
    error_sys = ErrorRecoverySystem({'max_retries': 2, 'retry_delay': 0.5})
    wrapper = LayerIsolationWrapper(error_sys)
    
    def layer_1_success():
        return {"status": "success", "data": "Layer 1 OK"}
    
    def layer_2_retry_then_success():
        if not hasattr(layer_2_retry_then_success, 'attempt'):
            layer_2_retry_then_success.attempt = 0
        layer_2_retry_then_success.attempt += 1
        
        if layer_2_retry_then_success.attempt < 2:
            raise RuntimeError("Temporary failure")
        return {"status": "success", "data": "Layer 2 OK"}
    
    def layer_3_fallback():
        raise ValueError("Primary failed")
    
    def layer_3_fallback_func():
        return {"status": "degraded", "data": "Fallback response"}
    
    def layer_4_fail():
        raise Exception("Permanent failure")
    
    print("\n执行层1 (成功):")
    result = wrapper.wrap_layer("layer_1", layer_1_success)
    print(f"  结果: {'✅ 成功' if result.success else '❌ 失败'}")
    
    print("\n执行层2 (重试后成功):")
    result = wrapper.wrap_layer("layer_2", layer_2_retry_then_success)
    print(f"  结果: {'✅ 成功' if result.success else '❌ 失败'}")
    print(f"  重试次数: {result.retry_count}")
    
    print("\n执行层3 (降级):")
    result = wrapper.wrap_layer("layer_3", layer_3_fallback, layer_3_fallback_func)
    print(f"  结果: {'✅ 成功' if result.success else '❌ 失败'}")
    print(f"  降级: {'是' if result.degraded else '否'}")
    
    print("\n执行层4 (最终失败):")
    result = wrapper.wrap_layer("layer_4", layer_4_fail)
    print(f"  结果: {'✅ 成功' if result.success else '❌ 失败'}")
    if result.error:
        print(f"  错误: {result.error.get('message') if isinstance(result.error, dict) else str(result.error)}")
    
    print("\n" + "="*80)
    print("📊 错误统计")
    print("="*80)
    summary = error_sys.get_error_summary()
    for key, value in summary.items():
        if key != 'recent_errors':
            print(f"  {key}: {value}")
    
    print("\n" + "="*80)
    print("✅ 错误恢复演示完成！")
    print("="*80)


if __name__ == "__main__":
    demo_error_recovery()
