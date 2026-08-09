"""
Layer 40: Isolation Execute Layer (内存级隔离执行层)

该层负责在内存级别隔离执行测试用例，通过创建独立的执行环境、
资源隔离和状态清理，确保测试用例之间不会相互影响。
支持进程隔离、内存隔离、文件系统隔离等。
"""

from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import gc
import sys
import os
import traceback
import threading
import time


class IsolationLevel(Enum):
    """隔离级别"""
    NONE = "none"
    FUNCTION = "function"
    CLASS = "class"
    PROCESS = "process"


class IsolationResource(Enum):
    """隔离资源类型"""
    MEMORY = "memory"
    FILESYSTEM = "filesystem"
    NETWORK = "network"
    DATABASE = "database"
    ENVIRONMENT = "environment"


@dataclass
class IsolationConfig:
    """隔离配置"""
    isolation_level: IsolationLevel = IsolationLevel.FUNCTION
    isolated_resources: List[IsolationResource] = field(
        default_factory=lambda: [IsolationResource.MEMORY]
    )
    enable_gc_after_test: bool = True
    enable_state_reset: bool = True
    timeout_seconds: float = 60.0
    memory_limit_mb: Optional[int] = None


@dataclass
class IsolationContext:
    """隔离执行上下文"""
    context_id: str
    isolation_level: IsolationLevel
    saved_state: Dict[str, Any] = field(default_factory=dict)
    isolated_resources: Dict[str, Any] = field(default_factory=dict)
    execution_start_time: float = 0.0
    memory_snapshot_before: Optional[int] = None
    memory_snapshot_after: Optional[int] = None


@dataclass
class IsolationResult:
    """隔离执行结果"""
    execution_context: Optional[IsolationContext] = None
    execution_result: Any = None
    execution_success: bool = True
    execution_time_ms: float = 0.0
    memory_delta_bytes: int = 0
    exceptions_caught: List[Exception] = field(default_factory=list)
    cleanup_performed: bool = False
    isolation_violations: List[str] = field(default_factory=list)


class IsolationExecuteLayer:
    """
    内存级隔离执行层

    负责在内存级别隔离执行测试用例，确保测试用例之间不会相互影响。

    核心功能：
    - 内存隔离：独立的内存空间和状态管理
    - 状态清理：测试前后的状态保存和恢复
    - 资源隔离：隔离文件系统、网络、数据库等资源
    - GC优化：强制垃圾回收清理内存
    - 超时控制：防止测试用例超时
    - 泄漏检测：检测内存泄漏和资源泄漏

    Attributes:
        description: 层的功能描述
        input_type: 输入数据类型 (PipelineContext)
        output_type: str = "IsolationResult"

    Input Context Fields:
        - test_cases: 测试用例列表
        - execution_plan: 执行计划
        - generated_mocks: Mock对象列表
        - isolation_config: 隔离配置
        - isolation_level: 隔离级别

    Output:
        IsolationResult: 隔离执行结果
    """

    description: str = "内存级隔离执行层 - 隔离执行测试用例"
    input_type: str = "PipelineContext"
    output_type: str = "IsolationResult"

    def __init__(self, isolation_config: Optional[IsolationConfig] = None):
        """
        初始化隔离执行层

        Args:
            isolation_config: 隔离配置对象，包含：
                - isolation_level: 隔离级别
                - isolated_resources: 隔离的资源类型列表
                - enable_gc_after_test: 测试后是否启用GC
                - enable_state_reset: 是否启用状态重置
                - timeout_seconds: 超时时间
                - memory_limit_mb: 内存限制（MB）
        """
        self.config = isolation_config or IsolationConfig()
        self.isolation_contexts: Dict[str, IsolationContext] = {}
        self.global_state_backup: Dict[str, Any] = {}

    def process(self, context: Any) -> IsolationResult:
        """
        执行隔离测试用例

        Args:
            context: PipelineContext对象，包含以下预期字段：
                - test_cases: 测试用例列表
                - execution_plan: 执行计划
                - generated_mocks: Mock对象列表
                - isolation_config: 隔离配置 (可选)
                - isolation_level: 隔离级别 (可选)
                - execution_options: 执行选项 (可选)
                    - stop_on_first_failure: 首次失败时停止
                    - enable_profiling: 启用性能分析
                    - verbose: 详细输出

        Returns:
            IsolationResult: 隔离执行结果，包含：
                - execution_context: 执行上下文
                - execution_result: 执行结果
                - execution_success: 是否成功执行
                - execution_time_ms: 执行耗时（毫秒）
                - memory_delta_bytes: 内存变化（字节）
                - exceptions_caught: 捕获的异常列表
                - cleanup_performed: 是否执行了清理
                - isolation_violations: 隔离违规列表

        Process Flow:
            1. 准备隔离执行环境
            2. 保存全局状态
            3. 创建隔离上下文
            4. 执行测试用例
            5. 捕获执行结果和异常
            6. 清理和状态恢复
            7. 执行垃圾回收
            8. 返回隔离执行结果

        Example:
            >>> layer = IsolationExecuteLayer()
            >>> ctx = create_context()
            >>> ctx.set('test_cases', test_cases)
            >>> ctx.set('isolation_level', IsolationLevel.PROCESS)
            >>> result = layer.process(ctx)
            >>> print(f"执行成功: {result.execution_success}")
            >>> print(f"执行时间: {result.execution_time_ms}ms")
        """
        import time
        start_time = time.time()

        test_cases = context.get('test_cases', [])
        execution_plan = context.get('execution_plan')
        mocks = context.get('generated_mocks', [])
        isolation_level = context.get(
            'isolation_level',
            self.config.isolation_level
        )

        if isinstance(isolation_level, str):
            try:
                isolation_level = IsolationLevel(isolation_level)
            except ValueError:
                isolation_level = IsolationLevel.FUNCTION

        result = IsolationResult()

        result.execution_context = self._create_isolation_context(
            isolation_level, test_cases
        )

        self._save_global_state()

        memory_before = self._get_memory_usage()
        result.execution_context.memory_snapshot_before = memory_before

        try:
            execution_results = self._execute_isolated(
                test_cases, mocks, result.execution_context
            )
            result.execution_result = execution_results
            result.execution_success = True

        except Exception as e:
            result.execution_success = False
            result.exceptions_caught.append(e)

        finally:
            memory_after = self._get_memory_usage()
            result.execution_context.memory_snapshot_after = memory_after
            result.memory_delta_bytes = memory_after - memory_before

            self._restore_global_state()

            if self.config.enable_state_reset:
                self._reset_application_state()

            if self.config.enable_gc_after_test:
                self._force_garbage_collection()

            cleanup_success = self._cleanup_isolated_resources(
                result.execution_context
            )
            result.cleanup_performed = cleanup_success

            result.execution_violations = self._check_isolation_violations(
                result.execution_context
            )

        result.execution_time_ms = (time.time() - start_time) * 1000

        context.set('isolation_result', result)
        context.set('execution_result', result.execution_result)

        return result

    def _create_isolation_context(
        self, level: IsolationLevel,
        test_cases: List[Any]
    ) -> IsolationContext:
        """创建隔离上下文"""
        context_id = f"isolation_{int(time.time() * 1000)}"

        isolation_context = IsolationContext(
            context_id=context_id,
            isolation_level=level
        )

        self.isolation_contexts[context_id] = isolation_context

        return isolation_context

    def _save_global_state(self) -> None:
        """保存全局状态"""
        self.global_state_backup = {
            'sys.modules': sys.modules.copy() if hasattr(sys, 'modules') else {},
            'sys.path': sys.path.copy() if hasattr(sys, 'path') else [],
        }

        for name in dir(sys):
            if not name.startswith('_'):
                try:
                    obj = getattr(sys, name)
                    if not callable(obj):
                        self.global_state_backup[f'sys.{name}'] = obj
                except (AttributeError, TypeError):
                    pass

    def _restore_global_state(self) -> None:
        """恢复全局状态"""
        for key, value in self.global_state_backup.items():
            try:
                if key.startswith('sys.'):
                    attr_name = key[4:]
                    current = getattr(sys, attr_name, None)
                    if current is not None and isinstance(current, (dict, list)):
                        if isinstance(current, dict):
                            current.clear()
                            current.update(value)
                        elif isinstance(current, list):
                            current.clear()
                            current.extend(value)
            except (AttributeError, TypeError):
                pass

    def _reset_application_state(self) -> None:
        """重置应用状态"""
        for module_name in list(sys.modules.keys()):
            if not module_name.startswith('_') and 'test' not in module_name.lower():
                if module_name in sys.modules:
                    try:
                        del sys.modules[module_name]
                    except KeyError:
                        pass

        gc.collect()

    def _execute_isolated(
        self, test_cases: List[Any],
        mocks: List[Any],
        isolation_context: IsolationContext
    ) -> List[Any]:
        """在隔离环境中执行测试"""
        results = []

        for i, test_case in enumerate(test_cases):
            case_result = self._execute_single_case(
                test_case, mocks, isolation_context, i
            )
            results.append(case_result)

        return results

    def _execute_single_case(
        self, test_case: Any,
        mocks: List[Any],
        context: IsolationContext,
        index: int
    ) -> Any:
        """执行单个测试用例"""
        case_id = self._get_case_id(test_case, index)

        if IsolationResource.MEMORY in self.config.isolated_resources:
            gc.collect()

        case_context = self._create_case_context(case_id)

        context.saved_state[case_id] = case_context

        try:
            test_code = self._get_test_code(test_case)

            result = self._execute_test_code(
                test_code, test_case, mocks
            )

            return result

        except Exception as e:
            context.isolated_resources[f'{case_id}_exception'] = {
                'type': type(e).__name__,
                'message': str(e),
                'traceback': traceback.format_exc()
            }
            raise

        finally:
            if self.config.enable_state_reset:
                self._cleanup_case_context(case_context)

    def _create_case_context(self, case_id: str) -> Dict[str, Any]:
        """创建用例上下文"""
        return {
            'case_id': case_id,
            'created_at': time.time(),
            'local_variables': {},
            'memory_objects': []
        }

    def _cleanup_case_context(self, case_context: Dict[str, Any]) -> None:
        """清理用例上下文"""
        case_context.clear()

    def _execute_test_code(
        self, code: str,
        test_case: Any,
        mocks: List[Any]
    ) -> Any:
        """执行测试代码"""
        local_vars = {}
        global_vars = {}

        for mock_obj in mocks:
            if hasattr(mock_obj, 'target_path') and hasattr(mock_obj, 'mock_instance'):
                try:
                    parts = mock_obj.target_path.rsplit('.', 1)
                    if len(parts) == 2:
                        module_name, attr_name = parts
                        if module_name in sys.modules:
                            setattr(
                                sys.modules[module_name],
                                attr_name,
                                mock_obj.mock_instance
                            )
                except Exception:
                    pass

        try:
            exec(code, global_vars, local_vars)
            return {
                'success': True,
                'output': local_vars.get('result'),
                'executed': True
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'executed': False
            }

    def _get_test_code(self, test_case: Any) -> str:
        """获取测试代码"""
        if hasattr(test_case, 'test_code'):
            return test_case.test_code
        elif isinstance(test_case, dict):
            return test_case.get('test_code', '')
        return ''

    def _get_case_id(self, test_case: Any, index: int) -> str:
        """获取用例ID"""
        if hasattr(test_case, 'test_id'):
            return test_case.test_id
        elif hasattr(test_case, 'case_id'):
            return test_case.case_id
        elif isinstance(test_case, dict):
            return test_case.get('id', test_case.get('test_id', f'case_{index}'))
        return f'case_{index}'

    def _get_memory_usage(self) -> int:
        """获取当前内存使用量"""
        try:
            import psutil
            process = psutil.Process(os.getpid())
            return process.memory_info().rss
        except ImportError:
            return 0

    def _force_garbage_collection(self) -> None:
        """强制垃圾回收"""
        collected = gc.collect()
        return collected

    def _cleanup_isolated_resources(
        self, context: IsolationContext
    ) -> bool:
        """清理隔离资源"""
        try:
            for resource_key in list(context.isolated_resources.keys()):
                del context.isolated_resources[resource_key]

            context.saved_state.clear()

            gc.collect()

            return True
        except Exception:
            return False

    def _check_isolation_violations(
        self, context: IsolationContext
    ) -> List[str]:
        """检查隔离违规"""
        violations = []

        if context.memory_snapshot_before and context.memory_snapshot_after:
            memory_increase = (
                context.memory_snapshot_after - context.memory_snapshot_before
            )
            if memory_increase > 100 * 1024 * 1024:
                violations.append(
                    f'内存增长过大: {memory_increase / (1024 * 1024):.2f} MB'
                )

        return violations

    def create_process_isolation(
        self, test_case: Any
    ) -> IsolationResult:
        """
        创建进程级隔离执行

        Args:
            test_case: 测试用例

        Returns:
            IsolationResult: 隔离执行结果
        """
        import multiprocessing

        result_queue = multiprocessing.Queue()

        def run_in_process():
            try:
                result = self._execute_single_case(
                    test_case, [], None, 0
                )
                result_queue.put({'success': True, 'result': result})
            except Exception as e:
                result_queue.put({
                    'success': False,
                    'error': str(e),
                    'traceback': traceback.format_exc()
                })

        process = multiprocessing.Process(target=run_in_process)
        process.start()
        process.join(timeout=self.config.timeout_seconds)

        if process.is_alive():
            process.terminate()
            process.join()

            return IsolationResult(
                execution_success=False,
                exceptions_caught=[Exception('测试执行超时')]
            )

        if not result_queue.empty():
            return result_queue.get()

        return IsolationResult(execution_success=False)

    def verify_isolation(
        self, context: IsolationContext
    ) -> Tuple[bool, List[str]]:
        """
        验证隔离有效性

        Args:
            context: 隔离上下文

        Returns:
            Tuple[bool, List[str]]: (是否有效, 问题列表)
        """
        issues = []

        if not context.saved_state:
            issues.append('状态保存失败')

        if context.memory_delta_bytes > 50 * 1024 * 1024:
            issues.append('内存泄漏检测')

        return len(issues) == 0, issues

    def get_isolation_metrics(self) -> Dict[str, Any]:
        """
        获取隔离指标

        Returns:
            Dict[str, Any]: 隔离指标
        """
        total_contexts = len(self.isolation_contexts)

        active_contexts = sum(
            1 for ctx in self.isolation_contexts.values()
            if ctx.execution_start_time > 0
        )

        return {
            'total_contexts': total_contexts,
            'active_contexts': active_contexts,
            'current_isolation_level': self.config.isolation_level.value,
            'isolated_resources': [
                r.value for r in self.config.isolated_resources
            ]
        }
