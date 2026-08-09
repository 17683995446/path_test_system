"""
并行处理架构
======================================================================

多进程、多线程、分布式处理支持
"""

import multiprocessing
import threading
import concurrent.futures
from typing import Dict, List, Any, Optional, Callable, TypeVar
from dataclasses import dataclass
from queue import Queue
from enum import Enum, auto
import time


T = TypeVar('T')
R = TypeVar('R')


class ParallelExecutionMode(Enum):
    """并行执行模式"""
    THREAD_POOL = auto()
    PROCESS_POOL = auto()
    THREAD = auto()
    PROCESS = auto()


@dataclass
class Task:
    """任务"""
    task_id: str
    func: Callable
    args: tuple = ()
    kwargs: dict = None
    priority: int = 0
    timeout: float = 300.0
    
    def __post_init__(self):
        if self.kwargs is None:
            self.kwargs = {}


@dataclass
class TaskResult:
    """任务结果"""
    task_id: str
    success: bool
    result: Any = None
    error: Optional[Exception] = None
    execution_time: float = 0.0
    start_time: float = 0.0
    end_time: float = 0.0


class ThreadPoolExecutor:
    """线程池执行器"""
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or multiprocessing.cpu_count()
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers
        )
    
    def submit(self, func: Callable, *args, **kwargs) -> concurrent.futures.Future:
        """提交任务"""
        return self.executor.submit(func, *args, **kwargs)
    
    def map(self, func: Callable, iterable, chunksize: int = 1):
        """映射任务"""
        return self.executor.map(func, iterable, chunksize=chunksize)
    
    def shutdown(self, wait: bool = True):
        """关闭池"""
        self.executor.shutdown(wait=wait)


class ProcessPoolExecutor:
    """进程池执行器"""
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or multiprocessing.cpu_count()
        self.executor = concurrent.futures.ProcessPoolExecutor(
            max_workers=self.max_workers
        )
    
    def submit(self, func: Callable, *args, **kwargs) -> concurrent.futures.Future:
        """提交任务"""
        return self.executor.submit(func, *args, **kwargs)
    
    def map(self, func: Callable, iterable, chunksize: int = 1):
        """映射任务"""
        return self.executor.map(func, iterable, chunksize=chunksize)
    
    def shutdown(self, wait: bool = True):
        """关闭池"""
        self.executor.shutdown(wait=wait)


class ParallelProcessor:
    """
    并行处理器
    
    统一的并行处理接口，支持多种模式
    """
    
    def __init__(
        self,
        mode: ParallelExecutionMode = ParallelExecutionMode.THREAD_POOL,
        max_workers: int = None
    ):
        self.mode = mode
        self.max_workers = max_workers or multiprocessing.cpu_count()
        
        if mode == ParallelExecutionMode.THREAD_POOL:
            self.executor = ThreadPoolExecutor(max_workers)
        elif mode == ParallelExecutionMode.PROCESS_POOL:
            self.executor = ProcessPoolExecutor(max_workers)
        else:
            self.executor = ThreadPoolExecutor(max_workers)
        
        self.task_queue: Queue[Task] = Queue()
        self.results: Dict[str, TaskResult] = {}
        self.running = False
    
    def execute_tasks(
        self,
        tasks: List[Task],
        timeout: float = 300.0
    ) -> Dict[str, TaskResult]:
        """
        批量执行任务
        
        Args:
            tasks: 任务列表
            timeout: 超时时间
        
        Returns:
            结果字典
        """
        futures: Dict[str, concurrent.futures.Future] = {}
        
        for task in tasks:
            futures[task.task_id] = self.executor.submit(
                self._execute_single_task,
                task
            )
        
        for task_id, future in futures.items():
            try:
                result = future.result(timeout=timeout)
                self.results[task_id] = result
            except Exception as e:
                self.results[task_id] = TaskResult(
                    task_id=task_id,
                    success=False,
                    error=e
                )
        
        return self.results
    
    def _execute_single_task(self, task: Task) -> TaskResult:
        """执行单个任务"""
        start_time = time.time()
        
        try:
            result = task.func(*task.args, **task.kwargs)
            end_time = time.time()
            
            return TaskResult(
                task_id=task.task_id,
                success=True,
                result=result,
                start_time=start_time,
                end_time=end_time,
                execution_time=end_time - start_time
            )
        except Exception as e:
            end_time = time.time()
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error=e,
                start_time=start_time,
                end_time=end_time,
                execution_time=end_time - start_time
            )
    
    def parallel_map(
        self,
        func: Callable,
        items: List[Any],
        chunksize: int = 1
    ) -> List[Any]:
        """
        并行映射
        
        Args:
            func: 函数
            items: 输入列表
            chunksize: 块大小
        
        Returns:
            结果列表
        """
        return list(self.executor.map(func, items, chunksize=chunksize))
    
    def shutdown(self):
        """关闭"""
        self.executor.shutdown()


class ParallelOptimizationEngine:
    """
    并行优化引擎
    
    整合并行处理能力的优化引擎
    """
    
    def __init__(
        self,
        config: Optional[Dict] = None
    ):
        self.config = config or {}
        self.thread_processor = ParallelProcessor(
            ParallelExecutionMode.THREAD_POOL
        )
        self.process_processor = ParallelProcessor(
            ParallelExecutionMode.PROCESS_POOL
        )
        
        print("🚀 并行处理架构初始化完成")
        print(f"   CPU核心数: {multiprocessing.cpu_count()}")
    
    def process_in_parallel(
        self,
        items: List[Any],
        processor_func: Callable,
        use_processes: bool = False
    ) -> List[Any]:
        """并行处理"""
        processor = self.process_processor if use_processes else self.thread_processor
        return processor.parallel_map(processor_func, items)
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            "thread_pool_workers": self.thread_processor.max_workers,
            "process_pool_workers": self.process_processor.max_workers
        }


def create_parallel_processor(
    mode: ParallelExecutionMode = ParallelExecutionMode.THREAD_POOL,
    max_workers: int = None
) -> ParallelProcessor:
    """创建并行处理器"""
    return ParallelProcessor(mode, max_workers)


if __name__ == "__main__":
    engine = ParallelOptimizationEngine()
    
    def square(x):
        return x * x
    
    numbers = list(range(10))
    result = engine.process_in_parallel(numbers, square)
    
    print("✅ 并行测试结果:", result)
