import time
"""
Layer 41: Concurrent Execute Layer (用例并发执行层)

该层负责并发执行测试用例，支持多线程、多进程执行模型。
提供智能的并发调度、资源管理和执行状态跟踪。
"""

from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, Future, as_completed
from threading import Lock, Semaphore
import time
import threading
import multiprocessing


class ConcurrencyModel(Enum):
    """并发模型"""
    THREAD = "thread"
    PROCESS = "process"
    ASYNCIO = "asyncio"
    HYBRID = "hybrid"


class ExecutionState(Enum):
    """执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class ExecutionMetrics:
    """执行指标"""
    total_cases: int = 0
    completed_cases: int = 0
    failed_cases: int = 0
    running_cases: int = 0
    pending_cases: int = 0
    total_duration_ms: float = 0.0
    avg_duration_ms: float = 0.0
    min_duration_ms: float = 0.0
    max_duration_ms: float = 0.0
    throughput: float = 0.0
    success_rate: float = 0.0


@dataclass
class WorkerMetrics:
    """工作线程指标"""
    worker_id: int
    cases_executed: int = 0
    total_time_ms: float = 0.0
    avg_time_per_case_ms: float = 0.0
    success_count: int = 0
    failure_count: int = 0


@dataclass
class ConcurrentExecutionResult:
    """并发执行结果"""
    execution_metrics: ExecutionMetrics = field(default_factory=ExecutionMetrics)
    worker_metrics: List[WorkerMetrics] = field(default_factory=list)
    execution_results: List[Any] = field(default_factory=list)
    total_duration_ms: float = 0.0
    parallel_degree: int = 1
    state: ExecutionState = ExecutionState.PENDING
    errors: List[Exception] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConcurrentExecuteLayer:
    """
    用例并发执行层

    负责并发执行测试用例，支持多种并发模型和执行策略。

    核心功能：
    - 多模型并发：支持线程池、进程池、异步执行
    - 智能调度：根据资源可用性动态调整并发度
    - 资源管理：限制并发数，防止资源耗尽
    - 执行跟踪：实时跟踪执行状态和进度
    - 结果聚合：收集和聚合执行结果
    - 错误处理：优雅处理并发执行中的错误

    Attributes:
        description: 层的功能描述
        input_type: 输入数据类型 (PipelineContext)
        output_type: str = "ConcurrentExecutionResult"

    Input Context Fields:
        - execution_plan: 执行计划
        - execution_batches: 执行批次
        - optimized_test_cases: 优化后的测试用例
        - isolation_result: 隔离执行结果
        - concurrency_model: 并发模型

    Output:
        ConcurrentExecutionResult: 并发执行结果
    """

    description: str = "用例并发执行层 - 并发执行测试用例"
    input_type: str = "PipelineContext"
    output_type: str = "ConcurrentExecutionResult"

    def __init__(self, concurrency_config: Optional[Dict[str, Any]] = None):
        """
        初始化并发执行层

        Args:
            concurrency_config: 并发配置字典，包含：
                - max_workers: 最大工作线程数
                - concurrency_model: 并发模型
                - timeout: 执行超时时间
                - enable_profiling: 启用性能分析
                - chunk_size: 批次大小
        """
        self.config = concurrency_config or {}
        self.max_workers = self.config.get('max_workers', 4)
        self.concurrency_model = ConcurrencyModel(
            self.config.get('concurrency_model', 'thread')
        )
        self.timeout = self.config.get('timeout', 300)
        self.enable_profiling = self.config.get('enable_profiling', False)
        self.chunk_size = self.config.get('chunk_size', 10)

        self.executor: Optional[Any] = None
        self.execution_lock = Lock()
        self.active_execution = False

    def process(self, context: Any) -> ConcurrentExecutionResult:
        """
        执行并发测试用例

        Args:
            context: PipelineContext对象，包含以下预期字段：
                - execution_plan: 执行计划
                - execution_batches: 执行批次列表
                - optimized_test_cases: 优化后的测试用例列表
                - isolation_result: 隔离执行结果
                - concurrency_model: 并发模型 (可选)
                - concurrency_options: 并发选项 (可选)
                    - max_workers: 最大工作线程数
                    - timeout: 超时时间
                    - stop_on_first_failure: 首次失败停止
                    - retry_failed: 重试失败的用例
                    - retry_count: 重试次数

        Returns:
            ConcurrentExecutionResult: 并发执行结果，包含：
                - execution_metrics: 执行指标
                - worker_metrics: 工作线程指标列表
                - execution_results: 执行结果列表
                - total_duration_ms: 总执行时长（毫秒）
                - parallel_degree: 并行度
                - state: 最终执行状态
                - errors: 错误列表
                - metadata: 附加元数据

        Process Flow:
            1. 准备执行环境和参数
            2. 选择合适的并发模型
            3. 创建执行器和工作线程
            4. 提交执行任务
            5. 监控执行进度
            6. 收集执行结果
            7. 计算执行指标
            8. 返回最终结果

        Example:
            >>> layer = ConcurrentExecuteLayer()
            >>> ctx = create_context()
            >>> ctx.set('execution_batches', batches)
            >>> ctx.set('optimized_test_cases', test_cases)
            >>> result = layer.process(ctx)
            >>> print(f"执行完成: {result.execution_metrics.completed_cases}/{result.execution_metrics.total_cases}")
        """
        import time
        start_time = time.time()

        execution_batches = context.get('execution_batches', [])
        test_cases = context.get('optimized_test_cases', [])
        isolation_result = context.get('isolation_result')
        concurrency_model = context.get('concurrency_model', self.concurrency_model)

        options = context.get('concurrency_options', {})
        max_workers = options.get('max_workers', self.max_workers)
        timeout = options.get('timeout', self.timeout)
        stop_on_first = options.get('stop_on_first_failure', False)
        retry_failed = options.get('retry_failed', False)

        result = ConcurrentExecutionResult()
        result.state = ExecutionState.RUNNING

        if concurrency_model == 'thread':
            self.concurrency_model = ConcurrencyModel.THREAD
        elif concurrency_model == 'process':
            self.concurrency_model = ConcurrencyModel.PROCESS
        elif concurrency_model == 'asyncio':
            self.concurrency_model = ConcurrencyModel.ASYNCIO

        test_cases_to_execute = self._prepare_test_cases(
            test_cases, execution_batches, isolation_result
        )

        result.execution_metrics.total_cases = len(test_cases_to_execute)

        self.executor = self._create_executor(
            self.concurrency_model, max_workers
        )

        try:
            execution_results = self._execute_concurrent(
                test_cases_to_execute,
                self.executor,
                timeout,
                stop_on_first
            )
            result.execution_results = execution_results

            self._process_execution_results(result, execution_results)

        except Exception as e:
            result.errors.append(e)
            result.state = ExecutionState.FAILED

        finally:
            self._shutdown_executor()
            self.active_execution = False

        result.total_duration_ms = (time.time() - start_time) * 1000
        result.execution_metrics.total_duration_ms = result.total_duration_ms

        result.execution_metrics.throughput = (
            result.execution_metrics.completed_cases /
            (result.total_duration_ms / 1000)
            if result.total_duration_ms > 0 else 0
        )

        result.execution_metrics.success_rate = (
            result.execution_metrics.completed_cases /
            result.execution_metrics.total_cases
            if result.execution_metrics.total_cases > 0 else 0
        )

        result.metadata = {
            'concurrency_model': self.concurrency_model.value,
            'max_workers_used': max_workers,
            'actual_workers': self._get_active_worker_count(),
            'profiling_enabled': self.enable_profiling
        }

        context.set('concurrent_execution_result', result)
        context.set('execution_metrics', result.execution_metrics)

        return result

    def _prepare_test_cases(
        self, test_cases: List[Any],
        batches: List[Any],
        isolation_result: Any
    ) -> List[Any]:
        """准备要执行的测试用例"""
        cases_to_execute = []

        if batches:
            for batch in batches:
                if hasattr(batch, 'test_case_ids'):
                    for case_id in batch.test_case_ids:
                        case = self._find_case_by_id(test_cases, case_id)
                        if case:
                            cases_to_execute.append(case)
        else:
            cases_to_execute = list(test_cases)

        return cases_to_execute

    def _find_case_by_id(
        self, test_cases: List[Any],
        case_id: str
    ) -> Optional[Any]:
        """根据ID查找测试用例"""
        for case in test_cases:
            if hasattr(case, 'test_id') and case.test_id == case_id:
                return case
            if hasattr(case, 'case_id') and case.case_id == case_id:
                return case
            if isinstance(case, dict):
                if case.get('id') == case_id or case.get('test_id') == case_id:
                    return case

        return None

    def _create_executor(
        self, model: ConcurrencyModel,
        max_workers: int
    ) -> Any:
        """创建执行器"""
        if model == ConcurrencyModel.THREAD:
            return ThreadPoolExecutor(max_workers=max_workers)
        elif model == ConcurrencyModel.PROCESS:
            return ProcessPoolExecutor(max_workers=max_workers)
        else:
            return ThreadPoolExecutor(max_workers=max_workers)

    def _shutdown_executor(self) -> None:
        """关闭执行器"""
        if self.executor:
            self.executor.shutdown(wait=True)
            self.executor = None

    def _execute_concurrent(
        self, test_cases: List[Any],
        executor: Any,
        timeout: float,
        stop_on_first: bool
    ) -> List[Any]:
        """并发执行测试用例"""
        futures: Dict[Future, Any] = {}
        results: List[Any] = []
        completed_count = 0

        for i, case in enumerate(test_cases):
            future = executor.submit(
                self._execute_single_case_with_timeout,
                case, i, timeout
            )
            futures[future] = case

        for future in as_completed(futures):
            case = futures[future]

            try:
                result = future.result(timeout=timeout)
                results.append(result)
                completed_count += 1

                if stop_on_first and not result.get('success', False):
                    for f in futures:
                        if not f.done():
                            f.cancel()
                    break

            except Exception as e:
                results.append({
                    'success': False,
                    'error': str(e),
                    'case_id': self._get_case_id(case),
                    'executed': False
                })

        return results

    def _execute_single_case_with_timeout(
        self, case: Any,
        index: int,
        timeout: float
    ) -> Any:
        """执行单个测试用例（带超时）"""
        import time
        case_start = time.time()

        try:
            test_code = self._get_test_code(case)
            case_id = self._get_case_id(case, index)

            result = {
                'case_id': case_id,
                'success': True,
                'executed': True,
                'duration_ms': 0
            }

            exec_globals = {}
            exec_locals = {}

            exec(test_code, exec_globals, exec_locals)

            result['duration_ms'] = (time.time() - case_start) * 1000

            return result

        except Exception as e:
            return {
                'case_id': self._get_case_id(case, index),
                'success': False,
                'error': str(e),
                'executed': True,
                'duration_ms': (time.time() - case_start) * 1000
            }

    def _get_test_code(self, case: Any) -> str:
        """获取测试代码"""
        if hasattr(case, 'test_code'):
            return case.test_code
        elif isinstance(case, dict):
            return case.get('test_code', '')
        return ''

    def _get_case_id(self, case: Any, index: int = 0) -> str:
        """获取用例ID"""
        if hasattr(case, 'test_id'):
            return case.test_id
        if hasattr(case, 'case_id'):
            return case.case_id
        if isinstance(case, dict):
            return case.get('id', case.get('test_id', f'case_{index}'))
        return f'case_{index}'

    def _process_execution_results(
        self, result: ConcurrentExecutionResult,
        execution_results: List[Any]
    ) -> None:
        """处理执行结果"""
        completed_cases = []
        failed_cases = []
        durations = []

        for exec_result in execution_results:
            if exec_result.get('success', False):
                completed_cases.append(exec_result)
                if 'duration_ms' in exec_result:
                    durations.append(exec_result['duration_ms'])
            else:
                failed_cases.append(exec_result)

        result.execution_metrics.completed_cases = len(completed_cases)
        result.execution_metrics.failed_cases = len(failed_cases)
        result.execution_metrics.running_cases = 0
        result.execution_metrics.pending_cases = 0

        if durations:
            result.execution_metrics.avg_duration_ms = sum(durations) / len(durations)
            result.execution_metrics.min_duration_ms = min(durations)
            result.execution_metrics.max_duration_ms = max(durations)

        result.state = (
            ExecutionState.COMPLETED
            if result.execution_metrics.failed_cases == 0
            else ExecutionState.FAILED
        )

    def _get_active_worker_count(self) -> int:
        """获取活跃工作线程数"""
        if isinstance(self.executor, ThreadPoolExecutor):
            return len(self.executor._threads) if hasattr(self.executor, '_threads') else 0
        elif isinstance(self.executor, ProcessPoolExecutor):
            return multiprocessing.cpu_count()
        return 1

    def execute_batch(
        self, batch: Any,
        max_workers: int
    ) -> List[Any]:
        """
        执行单个批次

        Args:
            batch: 执行批次
            max_workers: 最大工作线程数

        Returns:
            List[Any]: 批次执行结果
        """
        test_case_ids = []
        if hasattr(batch, 'test_case_ids'):
            test_case_ids = batch.test_case_ids
        elif isinstance(batch, dict):
            test_case_ids = batch.get('test_case_ids', [])

        test_cases = []
        for case_id in test_case_ids:
            case = self._find_case_by_id([], case_id)
            if case:
                test_cases.append(case)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self._execute_single_case_with_timeout, case, i, self.timeout)
                for i, case in enumerate(test_cases)
            ]

            results = []
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=self.timeout)
                    results.append(result)
                except Exception as e:
                    results.append({
                        'success': False,
                        'error': str(e)
                    })

            return results

    def get_execution_progress(self) -> Dict[str, Any]:
        """
        获取执行进度

        Returns:
            Dict[str, Any]: 执行进度信息
        """
        if not self.active_execution:
            return {'state': ExecutionState.PENDING}

        return {
            'state': ExecutionState.RUNNING,
            'active_workers': self._get_active_worker_count()
        }

    def cancel_execution(self) -> bool:
        """
        取消执行

        Returns:
            bool: 是否成功取消
        """
        if self.executor:
            self.executor.shutdown(wait=False)
            self.active_execution = False
            return True
        return False

    def retry_failed_cases(
        self, results: List[Any],
        test_cases: List[Any],
        max_workers: int
    ) -> List[Any]:
        """
        重试失败的用例

        Args:
            results: 之前的执行结果
            test_cases: 测试用例列表
            max_workers: 最大工作线程数

        Returns:
            List[Any]: 重试结果
        """
        failed_cases = []

        for result in results:
            if not result.get('success', False):
                case_id = result.get('case_id')
                case = self._find_case_by_id(test_cases, case_id)
                if case:
                    failed_cases.append(case)

        if not failed_cases:
            return []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self._execute_single_case_with_timeout, case, i, self.timeout)
                for i, case in enumerate(failed_cases)
            ]

            retry_results = []
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=self.timeout)
                    retry_results.append(result)
                except Exception as e:
                    retry_results.append({
                        'success': False,
                        'error': str(e),
                        'retry': True
                    })

            return retry_results

    def calculate_statistics(
        self, results: List[Any]
    ) -> ExecutionMetrics:
        """
        计算执行统计信息

        Args:
            results: 执行结果列表

        Returns:
            ExecutionMetrics: 执行指标
        """
        metrics = ExecutionMetrics()

        metrics.total_cases = len(results)

        completed = [r for r in results if r.get('success', False)]
        metrics.completed_cases = len(completed)

        metrics.failed_cases = metrics.total_cases - metrics.completed_cases

        durations = [
            r.get('duration_ms', 0)
            for r in completed
            if 'duration_ms' in r
        ]

        if durations:
            metrics.avg_duration_ms = sum(durations) / len(durations)
            metrics.min_duration_ms = min(durations)
            metrics.max_duration_ms = max(durations)

        metrics.success_rate = (
            metrics.completed_cases / metrics.total_cases
            if metrics.total_cases > 0 else 0
        )

        return metrics
