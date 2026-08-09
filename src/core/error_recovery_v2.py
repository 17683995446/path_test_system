"""
错误恢复系统2.0
======================================================================

更智能的错误恢复机制，包括：
- 自动重试（指数退避）
- 智能降级策略
- 故障隔离
- 错误自愈
"""

import time
import random
from typing import Dict, List, Any, Optional, Callable, Type
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import deque
import threading
from datetime import datetime


class ErrorSeverity(Enum):
    """错误严重级别"""
    FATAL = auto()  # 需要立即停止
    ERROR = auto()  # 需要处理但可继续
    WARNING = auto()  # 警告
    INFO = auto()  # 信息级


class ErrorRecoveryStrategy(Enum):
    """恢复策略"""
    RETRY = auto()  # 重试
    DEGRADE = auto()  # 降级
    SKIP = auto()  # 跳过
    TERMINATE = auto()  # 终止


@dataclass
class ErrorInfo:
    """错误信息"""
    error_id: str
    error_type: str
    severity: ErrorSeverity
    message: str
    timestamp: float = field(default_factory=time.time)
    layer_id: Optional[str] = None
    stack_trace: Optional[str] = None
    recoverable: bool = True
    retry_count: int = 0
    max_retries: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_id": self.error_id,
            "error_type": self.error_type,
            "severity": self.severity.name,
            "message": self.message,
            "timestamp": self.timestamp,
            "layer_id": self.layer_id,
            "stack_trace": self.stack_trace,
            "recoverable": self.recoverable,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries
        }


@dataclass
class RecoveryAction:
    """恢复操作"""
    action_type: ErrorRecoveryStrategy
    action_description: str
    action_timestamp: float = field(default_factory=time.time)
    success: bool = False
    result: Any = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.action_type.name,
            "description": self.action_description,
            "timestamp": self.action_timestamp,
            "success": self.success,
            "result": self.result
        }


class ErrorHistory:
    """错误历史记录"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.errors: deque[ErrorInfo] = deque(maxlen=max_size)
        self.recoveries: deque[RecoveryAction] = deque(maxlen=max_size)
        self.lock = threading.Lock()
    
    def add_error(self, error: ErrorInfo) -> None:
        """添加错误"""
        with self.lock:
            self.errors.append(error)
    
    def add_recovery(self, recovery: RecoveryAction) -> None:
        """添加恢复记录"""
        with self.lock:
            self.recoveries.append(recovery)
    
    def get_errors_by_layer(self, layer_id: str) -> List[ErrorInfo]:
        """获取某层的错误"""
        return [e for e in self.errors if e.layer_id == layer_id]
    
    def get_recent_errors(self, limit: int = 100) -> List[ErrorInfo]:
        """获取最近的错误"""
        return list(self.errors)[-limit:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self.lock:
            total_errors = len(self.errors)
            total_recoveries = len(self.recoveries)
            successful_recoveries = sum(1 for r in self.recoveries if r.success)
            error_by_severity = {}
            for error in self.errors:
                sev = error.severity.name
                error_by_severity[sev] = error_by_severity.get(sev, 0) + 1
            
            return {
                "total_errors": total_errors,
                "total_recoveries": total_recoveries,
                "successful_recoveries": successful_recoveries,
                "recovery_rate": (successful_recoveries / total_recoveries * 100) if total_recoveries > 0 else 0,
                "error_by_severity": error_by_severity
            }


class ErrorRecoverySystem2:
    """
    错误恢复系统2.0
    ==================================================================
    
    增强的错误恢复系统，支持更智能的恢复策略
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.history = ErrorHistory()
        self.max_retries = self.config.get("max_retries", 3)
        self.retry_delay_base = self.config.get("retry_delay", 1.0)
        self.fallback_enabled = self.config.get("fallback_enabled", True)
        self.degrade_functions: Dict[str, Callable] = {}
        self.auto_recovery = self.config.get("auto_recovery", True)
        
        self.error_counter: Dict[str, int] = {}
        self.lock = threading.Lock()
    
    def register_fallback(self, layer_id: str, fallback_func: Callable) -> None:
        """注册降级函数"""
        self.degrade_functions[layer_id] = fallback_func
    
    def decide_recovery_strategy(self, error: ErrorInfo) -> ErrorRecoveryStrategy:
        """
        智能决定恢复策略
        
        根据错误类型、频率、严重度决定最佳策略
        """
        if not error.recoverable:
            return ErrorRecoveryStrategy.TERMINATE
        
        if error.severity == ErrorSeverity.FATAL:
            return ErrorRecoveryStrategy.TERMINATE
        
        if error.retry_count < self.max_retries:
            return ErrorRecoveryStrategy.RETRY
        
        if self.fallback_enabled and error.layer_id in self.degrade_functions:
            return ErrorRecoveryStrategy.DEGRADE
        
        if error.severity in [ErrorSeverity.WARNING, ErrorSeverity.INFO]:
            return ErrorRecoveryStrategy.SKIP
        
        return ErrorRecoveryStrategy.DEGRADE
    
    def calculate_retry_delay(self, retry_count: int) -> float:
        """
        指数退避算法
        
        retry 0: 1s
        retry 1: 2s
        retry 2: 4s
        retry 3: 8s
        """
        delay = self.retry_delay_base * (2 ** retry_count)
        jitter = random.uniform(0, delay * 0.2)  # 20%抖动避免同步
        return delay + jitter
    
    def execute_with_recovery(
        self,
        primary_func: Callable,
        layer_id: str,
        fallback_func: Optional[Callable] = None,
        config: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        带恢复机制的执行
        
        Args:
            primary_func: 主函数
            layer_id: 层ID
            fallback_func: 降级函数
            config: 配置
        
        Returns:
            执行结果
        """
        local_config = config or self.config
        result: Dict[str, Any] = {
            "success": False,
            "output": None,
            "error": None,
            "recovered": False,
            "strategy_used": None,
            "retry_count": 0
        }
        
        for retry in range(self.max_retries):
            try:
                result["output"] = primary_func()
                result["success"] = True
                
                if retry > 0:
                    result["recovered"] = True
                    result["strategy_used"] = ErrorRecoveryStrategy.RETRY
                
                return result
            
            except Exception as e:
                error = ErrorInfo(
                    error_id=f"err_{int(time.time() * 1000000)}",
                    error_type=type(e).__name__,
                    severity=self._classify_error(e),
                    message=str(e),
                    layer_id=layer_id,
                    retry_count=retry,
                    max_retries=self.max_retries
                )
                
                self.history.add_error(error)
                
                strategy = self.decide_recovery_strategy(error)
                result["retry_count"] = retry + 1
                
                if strategy == ErrorRecoveryStrategy.RETRY:
                    if retry < self.max_retries - 1:
                        delay = self.calculate_retry_delay(retry)
                        time.sleep(delay)
                        result["strategy_used"] = strategy
                        continue
                
                elif strategy == ErrorRecoveryStrategy.DEGRADE:
                    if fallback_func:
                        try:
                            result["output"] = fallback_func()
                            result["success"] = True
                            result["recovered"] = True
                            result["strategy_used"] = strategy
                            recovery = RecoveryAction(
                                action_type=ErrorRecoveryStrategy.DEGRADE,
                                action_description=f"Fallback executed for {layer_id}",
                                success=True
                            )
                            self.history.add_recovery(recovery)
                            return result
                        except Exception as fallback_error:
                            pass
                
                elif strategy == ErrorRecoveryStrategy.SKIP:
                    result["output"] = None
                    result["success"] = True
                    result["strategy_used"] = strategy
                    return result
                
                result["error"] = error.to_dict()
                return result
        
        return result
    
    def _classify_error(self, error: Exception) -> ErrorSeverity:
        """分类错误"""
        error_name = type(error).__name__.lower()
        
        if "fatal" in error_name or "critical" in error_name:
            return ErrorSeverity.FATAL
        elif "warning" in error_name:
            return ErrorSeverity.WARNING
        elif "info" in error_name or "note" in error_name:
            return ErrorSeverity.INFO
        
        return ErrorSeverity.ERROR
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取系统统计"""
        return self.history.get_statistics()
    
    def self_heal(self) -> Dict[str, Any]:
        """
        自动自愈
        
        尝试自动修复已知问题
        """
        results = {
            "healed": 0,
            "attempts": 0,
            "details": []
        }
        
        for error in self.history.get_recent_errors(50):
            results["attempts"] += 1
            if self._can_self_heal(error):
                self._apply_heal(error)
                results["healed"] += 1
        
        return results
    
    def _can_self_heal(self, error: ErrorInfo) -> bool:
        """判断是否可自愈"""
        healable_errors = [
            "timeout", "connection", "network", 
            "memory", "resource"
        ]
        for err in healable_errors:
            if err in error.message.lower():
                return True
        return False
    
    def _apply_heal(self, error: ErrorInfo) -> bool:
        """应用自愈"""
        try:
            if "timeout" in error.message.lower():
                return True
            elif "memory" in error.message.lower():
                import gc
                gc.collect()
                return True
            return False
        except:
            return False


def create_error_recovery_system(config: Optional[Dict] = None) -> ErrorRecoverySystem2:
    """工厂函数创建错误恢复系统"""
    return ErrorRecoverySystem2(config)


if __name__ == "__main__":
    # 测试错误恢复系统
    system = create_error_recovery_system()
    
    print("✅ 错误恢复系统2.0初始化完成")
    print(f"   配置: {system.config}")
    print(f"   统计: {system.get_statistics()}")
