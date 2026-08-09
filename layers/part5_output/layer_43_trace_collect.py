"""
Layer 43: TraceCollectLayer - 执行轨迹采集层

本层负责在测试执行过程中采集详细的执行轨迹信息，包括函数调用链、
变量状态变化、分支执行情况等，为后续的覆盖率分析和缺陷定位提供数据支撑。
"""

from typing import Any, Optional, List, Dict, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import defaultdict
import time
import threading
import json


class TraceEventType(Enum):
    """追踪事件类型枚举"""
    FUNCTION_CALL = auto()
    FUNCTION_RETURN = auto()
    BRANCH_TAKEN = auto()
    BRANCH_NOT_TAKEN = auto()
    VARIABLE_ASSIGN = auto()
    VARIABLE_READ = auto()
    LOOP_ITERATION = auto()
    EXCEPTION_RAISED = auto()
    EXCEPTION_CAUGHT = auto()
    ASSERTION_PASS = auto()
    ASSERTION_FAIL = auto()
    LINE_EXECUTE = auto()
    OBJECT_CREATE = auto()
    OBJECT_DESTROY = auto()


class TraceLevel(Enum):
    """追踪级别枚举"""
    MINIMAL = auto()
    STANDARD = auto()
    VERBOSE = auto()
    DEBUG = auto()


@dataclass
class TraceEvent:
    """追踪事件数据模型

    Attributes:
        event_id: 事件唯一标识符
        event_type: 事件类型
        timestamp: 事件发生的时间戳
        thread_id: 线程标识符
        process_id: 进程标识符
        function_name: 函数名称
        file_path: 文件路径
        line_number: 行号
        column_number: 列号
        call_stack: 调用栈信息
        variables: 变量状态快照
        metadata: 其他元信息
    """
    event_id: str
    event_type: TraceEventType
    timestamp: float
    thread_id: int
    process_id: int
    function_name: str = ""
    file_path: str = ""
    line_number: int = 0
    column_number: int = 0
    call_stack: List[str] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.name,
            "timestamp": self.timestamp,
            "thread_id": self.thread_id,
            "process_id": self.process_id,
            "function_name": self.function_name,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "column_number": self.column_number,
            "call_stack": self.call_stack,
            "variables": self.variables,
            "metadata": self.metadata
        }


@dataclass
class FunctionTrace:
    """函数追踪信息

    Attributes:
        function_name: 函数名称
        qualified_name: 完全限定名称
        entry_time: 进入时间
        exit_time: 退出时间
        duration: 执行时长（毫秒）
        call_count: 调用次数
        recursion_depth: 递归深度
        arguments: 参数快照
        return_value: 返回值
        exceptions: 抛出的异常列表
        called_functions: 调用的函数列表
        covered_lines: 覆盖的行号集合
        is_generator: 是否为生成器
        generator_yields: 生成器的yield次数
    """
    function_name: str
    qualified_name: str
    entry_time: float = 0.0
    exit_time: float = 0.0
    duration: float = 0.0
    call_count: int = 0
    recursion_depth: int = 0
    arguments: Dict[str, Any] = field(default_factory=dict)
    return_value: Any = None
    exceptions: List[str] = field(default_factory=list)
    called_functions: List[str] = field(default_factory=list)
    covered_lines: Set[int] = field(default_factory=set)
    is_generator: bool = False
    generator_yields: int = 0

    def add_covered_line(self, line_number: int) -> None:
        """添加覆盖的行号"""
        self.covered_lines.add(line_number)

    def add_called_function(self, func_name: str) -> None:
        """添加调用的函数"""
        if func_name not in self.called_functions:
            self.called_functions.append(func_name)

    def calculate_duration(self) -> float:
        """计算执行时长"""
        if self.exit_time > 0 and self.entry_time > 0:
            self.duration = (self.exit_time - self.entry_time) * 1000
        return self.duration

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "function_name": self.function_name,
            "qualified_name": self.qualified_name,
            "entry_time": self.entry_time,
            "exit_time": self.exit_time,
            "duration": self.duration,
            "call_count": self.call_count,
            "recursion_depth": self.recursion_depth,
            "arguments": self.arguments,
            "return_value": str(self.return_value) if self.return_value else None,
            "exceptions": self.exceptions,
            "called_functions": self.called_functions,
            "covered_lines": sorted(list(self.covered_lines)),
            "is_generator": self.is_generator,
            "generator_yields": self.generator_yields
        }


@dataclass
class BranchTrace:
    """分支追踪信息

    Attributes:
        branch_id: 分支标识符
        condition: 分支条件表达式
        file_path: 文件路径
        line_number: 行号
        true_count: 条件为真的执行次数
        false_count: 条件为假的执行次数
        total_count: 总执行次数
        is_covered: 是否被覆盖
        coverage_ratio: 覆盖率（0-1）
    """
    branch_id: str
    condition: str
    file_path: str
    line_number: int
    true_count: int = 0
    false_count: int = 0
    total_count: int = 0
    is_covered: bool = False
    coverage_ratio: float = 0.0

    def record_true(self) -> None:
        """记录条件为真"""
        self.true_count += 1
        self._update_stats()

    def record_false(self) -> None:
        """记录条件为假"""
        self.false_count += 1
        self._update_stats()

    def _update_stats(self) -> None:
        """更新统计数据"""
        self.total_count = self.true_count + self.false_count
        if self.total_count > 0:
            self.is_covered = True
            if self.true_count > 0 and self.false_count > 0:
                self.coverage_ratio = 1.0
            else:
                self.coverage_ratio = 0.5

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "branch_id": self.branch_id,
            "condition": self.condition,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "true_count": self.true_count,
            "false_count": self.false_count,
            "total_count": self.total_count,
            "is_covered": self.is_covered,
            "coverage_ratio": self.coverage_ratio
        }


@dataclass
class TraceCollectionResult:
    """轨迹采集结果

    Attributes:
        session_id: 会话标识符
        trace_events: 追踪事件列表
        function_traces: 函数追踪信息字典
        branch_traces: 分支追踪信息字典
        covered_files: 覆盖的文件集合
        covered_functions: 覆盖的函数集合
        covered_lines: 覆盖的行号字典（文件路径 -> 行号集合）
        execution_summary: 执行摘要信息
        statistics: 统计信息
        metadata: 其他元信息
    """
    session_id: str
    trace_events: List[TraceEvent] = field(default_factory=list)
    function_traces: Dict[str, FunctionTrace] = field(default_factory=dict)
    branch_traces: Dict[str, BranchTrace] = field(default_factory=dict)
    covered_files: Set[str] = field(default_factory=set)
    covered_functions: Set[str] = field(default_factory=set)
    covered_lines: Dict[str, Set[int]] = field(default_factory=dict)
    execution_summary: Dict[str, Any] = field(default_factory=dict)
    statistics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_trace_event(self, event: TraceEvent) -> None:
        """添加追踪事件"""
        self.trace_events.append(event)
        if event.file_path:
            self.covered_files.add(event.file_path)
        if event.function_name:
            self.covered_functions.add(event.function_name)
        if event.file_path and event.line_number > 0:
            if event.file_path not in self.covered_lines:
                self.covered_lines[event.file_path] = set()
            self.covered_lines[event.file_path].add(event.line_number)

    def get_function_trace(self, func_name: str) -> Optional[FunctionTrace]:
        """获取函数追踪信息"""
        return self.function_traces.get(func_name)

    def get_branch_trace(self, branch_id: str) -> Optional[BranchTrace]:
        """获取分支追踪信息"""
        return self.branch_traces.get(branch_id)

    def get_file_coverage(self, file_path: str) -> Optional[Set[int]]:
        """获取文件的行覆盖信息"""
        return self.covered_lines.get(file_path)

    def calculate_statistics(self) -> Dict[str, Any]:
        """计算统计信息"""
        self.statistics = {
            "total_events": len(self.trace_events),
            "unique_files": len(self.covered_files),
            "unique_functions": len(self.covered_functions),
            "total_lines_covered": sum(len(lines) for lines in self.covered_lines.values()),
            "total_branches": len(self.branch_traces),
            "covered_branches": sum(1 for b in self.branch_traces.values() if b.is_covered),
            "fully_covered_branches": sum(1 for b in self.branch_traces.values() if b.coverage_ratio >= 1.0),
            "total_function_traces": len(self.function_traces),
            "max_recursion_depth": max((t.recursion_depth for t in self.function_traces.values()), default=0),
            "total_exceptions": sum(len(t.exceptions) for t in self.function_traces.values())
        }
        return self.statistics

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "session_id": self.session_id,
            "trace_events": [e.to_dict() for e in self.trace_events],
            "function_traces": {k: v.to_dict() for k, v in self.function_traces.items()},
            "branch_traces": {k: v.to_dict() for k, v in self.branch_traces.items()},
            "covered_files": sorted(list(self.covered_files)),
            "covered_functions": sorted(list(self.covered_functions)),
            "covered_lines": {k: sorted(list(v)) for k, v in self.covered_lines.items()},
            "execution_summary": self.execution_summary,
            "statistics": self.statistics,
            "metadata": self.metadata
        }


class TraceCollector:
    """轨迹收集器核心类

    功能描述：
        - 提供运行时轨迹数据的采集能力
        - 支持函数调用、分支执行、变量变化的追踪
        - 维护调用栈信息和线程上下文
        - 支持轨迹数据的过滤和聚合
        - 提供轨迹事件的序列化和反序列化

    输入类型：
        - 测试执行上下文
        - 源代码信息
        - 配置参数

    输出类型：
        - TraceCollectionResult: 轨迹采集结果
    """

    def __init__(self, session_id: str, level: TraceLevel = TraceLevel.STANDARD):
        """初始化轨迹收集器

        Args:
            session_id: 会话标识符
            level: 追踪级别
        """
        self.session_id = session_id
        self.level = level
        self.events: List[TraceEvent] = []
        self.function_traces: Dict[str, FunctionTrace] = {}
        self.branch_traces: Dict[str, BranchTrace] = {}
        self.current_call_stack: List[str] = []
        self.current_function: Optional[str] = None
        self._event_counter = 0
        self._lock = threading.Lock()
        self.start_time = time.time()
        self._setup_event_filters()

    def _setup_event_filters(self) -> None:
        """设置事件过滤器"""
        self.event_filters: Dict[TraceEventType, bool] = {
            TraceEventType.FUNCTION_CALL: True,
            TraceEventType.FUNCTION_RETURN: True,
            TraceEventType.BRANCH_TAKEN: True,
            TraceEventType.BRANCH_NOT_TAKEN: True,
            TraceEventType.VARIABLE_ASSIGN: self.level in [TraceLevel.VERBOSE, TraceLevel.DEBUG],
            TraceEventType.VARIABLE_READ: self.level == TraceLevel.DEBUG,
            TraceEventType.LINE_EXECUTE: self.level in [TraceLevel.STANDARD, TraceLevel.VERBOSE, TraceLevel.DEBUG],
            TraceEventType.LOOP_ITERATION: self.level in [TraceLevel.VERBOSE, TraceLevel.DEBUG],
            TraceEventType.EXCEPTION_RAISED: True,
            TraceEventType.EXCEPTION_CAUGHT: True,
            TraceEventType.ASSERTION_PASS: True,
            TraceEventType.ASSERTION_FAIL: True,
            TraceEventType.OBJECT_CREATE: self.level in [TraceLevel.VERBOSE, TraceLevel.DEBUG],
            TraceEventType.OBJECT_DESTROY: self.level in [TraceLevel.VERBOSE, TraceLevel.DEBUG]
        }

    def _generate_event_id(self) -> str:
        """生成事件ID"""
        with self._lock:
            self._event_counter += 1
            return f"evt_{self.session_id}_{self._event_counter}"

    def record_function_entry(self, func_name: str, qualified_name: str,
                            file_path: str, line_number: int,
                            args: Dict[str, Any] = None) -> None:
        """记录函数进入事件

        Args:
            func_name: 函数名称
            qualified_name: 完全限定名称
            file_path: 文件路径
            line_number: 行号
            args: 函数参数
        """
        if not self.event_filters.get(TraceEventType.FUNCTION_CALL, True):
            return

        timestamp = time.time()
        thread_id = threading.get_ident()
        process_id = 0

        self.current_call_stack.append(qualified_name)
        self.current_function = qualified_name

        if qualified_name not in self.function_traces:
            self.function_traces[qualified_name] = FunctionTrace(
                function_name=func_name,
                qualified_name=qualified_name
            )

        trace = self.function_traces[qualified_name]
        trace.entry_time = timestamp
        trace.call_count += 1
        trace.recursion_depth = len([f for f in self.current_call_stack if f == qualified_name])
        if args:
            trace.arguments = args

        event = TraceEvent(
            event_id=self._generate_event_id(),
            event_type=TraceEventType.FUNCTION_CALL,
            timestamp=timestamp,
            thread_id=thread_id,
            process_id=process_id,
            function_name=qualified_name,
            file_path=file_path,
            line_number=line_number,
            call_stack=list(self.current_call_stack),
            metadata={"args": args} if args else {}
        )
        self._add_event(event)

    def record_function_exit(self, func_name: str, qualified_name: str,
                           return_value: Any = None, exception: str = None) -> None:
        """记录函数退出事件

        Args:
            func_name: 函数名称
            qualified_name: 完全限定名称
            return_value: 返回值
            exception: 异常信息
        """
        if not self.event_filters.get(TraceEventType.FUNCTION_RETURN, True):
            return

        timestamp = time.time()
        thread_id = threading.get_ident()

        if self.current_call_stack and self.current_call_stack[-1] == qualified_name:
            self.current_call_stack.pop()

        if qualified_name in self.function_traces:
            trace = self.function_traces[qualified_name]
            trace.exit_time = timestamp
            trace.calculate_duration()
            if return_value is not None:
                trace.return_value = return_value
            if exception:
                trace.exceptions.append(exception)

        if self.current_call_stack:
            self.current_function = self.current_call_stack[-1]
        else:
            self.current_function = None

        event = TraceEvent(
            event_id=self._generate_event_id(),
            event_type=TraceEventType.FUNCTION_RETURN,
            timestamp=timestamp,
            thread_id=thread_id,
            process_id=0,
            function_name=qualified_name,
            metadata={"return_value": str(return_value), "exception": exception}
        )
        self._add_event(event)

    def record_branch_execution(self, branch_id: str, condition: str,
                              file_path: str, line_number: int,
                              taken: bool, condition_value: bool) -> None:
        """记录分支执行事件

        Args:
            branch_id: 分支标识符
            condition: 分支条件
            file_path: 文件路径
            line_number: 行号
            taken: 是否被执行
            condition_value: 条件值
        """
        event_type = TraceEventType.BRANCH_TAKEN if taken else TraceEventType.BRANCH_NOT_TAKEN
        if not self.event_filters.get(event_type, True):
            return

        timestamp = time.time()
        thread_id = threading.get_ident()

        if branch_id not in self.branch_traces:
            self.branch_traces[branch_id] = BranchTrace(
                branch_id=branch_id,
                condition=condition,
                file_path=file_path,
                line_number=line_number
            )

        branch_trace = self.branch_traces[branch_id]
        if condition_value:
            branch_trace.record_true()
        else:
            branch_trace.record_false()

        event = TraceEvent(
            event_id=self._generate_event_id(),
            event_type=event_type,
            timestamp=timestamp,
            thread_id=thread_id,
            process_id=0,
            function_name=self.current_function or "",
            file_path=file_path,
            line_number=line_number,
            metadata={"branch_id": branch_id, "condition_value": condition_value}
        )
        self._add_event(event)

    def record_line_execution(self, file_path: str, line_number: int,
                            variables: Dict[str, Any] = None) -> None:
        """记录行执行事件

        Args:
            file_path: 文件路径
            line_number: 行号
            variables: 变量状态
        """
        if not self.event_filters.get(TraceEventType.LINE_EXECUTE, True):
            return

        timestamp = time.time()
        thread_id = threading.get_ident()

        if self.current_function and self.current_function in self.function_traces:
            self.function_traces[self.current_function].add_covered_line(line_number)

        event = TraceEvent(
            event_id=self._generate_event_id(),
            event_type=TraceEventType.LINE_EXECUTE,
            timestamp=timestamp,
            thread_id=thread_id,
            process_id=0,
            function_name=self.current_function or "",
            file_path=file_path,
            line_number=line_number,
            variables=variables or {},
            metadata={"variables_snapshot": variables} if variables else {}
        )
        self._add_event(event)

    def record_exception(self, exception_type: str, message: str,
                       file_path: str, line_number: int) -> None:
        """记录异常事件

        Args:
            exception_type: 异常类型
            message: 异常消息
            file_path: 文件路径
            line_number: 行号
        """
        timestamp = time.time()
        thread_id = threading.get_ident()

        event = TraceEvent(
            event_id=self._generate_event_id(),
            event_type=TraceEventType.EXCEPTION_RAISED,
            timestamp=timestamp,
            thread_id=thread_id,
            process_id=0,
            function_name=self.current_function or "",
            file_path=file_path,
            line_number=line_number,
            metadata={"exception_type": exception_type, "message": message}
        )
        self._add_event(event)

        if self.current_function and self.current_function in self.function_traces:
            self.function_traces[self.current_function].exceptions.append(
                f"{exception_type}: {message}"
            )

    def _add_event(self, event: TraceEvent) -> None:
        """添加事件到收集器"""
        with self._lock:
            self.events.append(event)

    def get_result(self) -> TraceCollectionResult:
        """获取轨迹采集结果

        Returns:
            TraceCollectionResult: 轨迹采集结果
        """
        result = TraceCollectionResult(
            session_id=self.session_id,
            trace_events=self.events.copy(),
            function_traces=self.function_traces.copy(),
            branch_traces=self.branch_traces.copy()
        )

        for event in self.events:
            result.add_trace_event(event)

        result.calculate_statistics()
        result.execution_summary = {
            "start_time": self.start_time,
            "end_time": time.time(),
            "duration": time.time() - self.start_time,
            "total_events": len(self.events),
            "trace_level": self.level.name
        }

        return result


class TraceCollectLayer:
    """执行轨迹采集层

    功能描述：
        - 在测试执行期间采集完整的执行轨迹
        - 追踪函数调用链和返回路径
        - 记录分支条件的执行情况
        - 捕获变量状态变化
        - 记录异常发生的位置和上下文
        - 生成详细的执行摘要报告

    输入类型：
        - PipelineContext: 包含测试执行上下文
        - 测试配置和源代码信息

    输出类型：
        - TraceCollectionResult: 轨迹采集结果
        - 包含事件流、函数追踪、分支追踪等完整信息

    使用场景：
        - 详细的代码执行分析
        - 性能瓶颈定位
        - 覆盖率增强分析
        - 缺陷调试和重现
        - 执行路径可视化

    V3.1升级点：
        - 支持异步执行轨迹追踪
        - 多线程环境的轨迹关联
        - 轨迹数据的压缩存储
        - 增量轨迹采集优化
        - 轨迹数据的实时流式输出
    """

    description: str = "执行轨迹采集层 - 采集测试执行期间的详细轨迹信息"
    input_type: str = "PipelineContext - 包含测试执行上下文和配置"
    output_type: str = "TraceCollectionResult - 轨迹采集结果"

    def __init__(self):
        """初始化执行轨迹采集层"""
        self.collector: Optional[TraceCollector] = None
        self.source_files: List[str] = []
        self.trace_level = TraceLevel.STANDARD

    def process(self, context: Any) -> TraceCollectionResult:
        """处理测试执行上下文，采集执行轨迹

        Args:
            context: PipelineContext对象，包含测试执行上下文

        Returns:
            TraceCollectionResult: 轨迹采集结果

        Raises:
            ValueError: 当缺少必要的上下文信息时
        """
        session_id = context.get('session_id', 'default_session')
        self.source_files = context.get('source_files', [])

        trace_config = context.get('trace_config', {})
        level_name = trace_config.get('level', 'STANDARD')
        try:
            self.trace_level = TraceLevel[level_name]
        except KeyError:
            self.trace_level = TraceLevel.STANDARD

        self.collector = TraceCollector(session_id, self.trace_level)

        if context.has('test_results'):
            test_results = context.get('test_results')
            self._process_test_results(test_results)

        if context.has('execution_paths'):
            execution_paths = context.get('execution_paths')
            self._process_execution_paths(execution_paths)

        if context.has('covered_lines'):
            covered_lines = context.get('covered_lines')
            self._process_covered_lines(covered_lines)

        result = self.collector.get_result()

        result.metadata = {
            "source_files_count": len(self.source_files),
            "trace_config": trace_config,
            "processing_complete": True
        }

        context.set('trace_collection_result', result)
        context.set('trace_collection_complete', True)
        context.set('trace_statistics', result.statistics)

        return result

    def _process_test_results(self, test_results: Any) -> None:
        """处理测试结果，提取轨迹信息

        Args:
            test_results: 测试结果数据
        """
        if isinstance(test_results, dict):
            for test_name, result in test_results.items():
                if isinstance(result, dict):
                    if 'duration' in result:
                        duration = result.get('duration', 0)
                        if duration > 0:
                            pass
                    if 'exception' in result:
                        exception = result.get('exception')
                        if exception:
                            self.collector.record_exception(
                                type(exception).__name__,
                                str(exception),
                                result.get('file_path', ''),
                                result.get('line_number', 0)
                            )

    def _process_execution_paths(self, execution_paths: Any) -> None:
        """处理执行路径，生成轨迹事件

        Args:
            execution_paths: 执行路径数据
        """
        if hasattr(execution_paths, '__iter__'):
            for path in execution_paths:
                path_id = getattr(path, 'path_id', str(path))
                nodes = getattr(path, 'nodes', [])

                for i, node in enumerate(nodes):
                    file_path = getattr(node, 'file_path', '')
                    line_number = getattr(node, 'line_number', 0)

                    if file_path and line_number > 0:
                        self.collector.record_line_execution(file_path, line_number)

                    if i < len(nodes) - 1:
                        next_node = nodes[i + 1]
                        branch_id = f"{path_id}_branch_{i}"
                        taken = True
                        condition_value = True
                        self.collector.record_branch_execution(
                            branch_id, f"path_{path_id}",
                            file_path, line_number,
                            taken, condition_value
                        )

    def _process_covered_lines(self, covered_lines: Any) -> None:
        """处理覆盖的行信息，补充轨迹数据

        Args:
            covered_lines: 覆盖的行数据
        """
        if isinstance(covered_lines, dict):
            for file_path, lines in covered_lines.items():
                for line_number in lines:
                    self.collector.record_line_execution(file_path, line_number)

    def create_collector(self, session_id: str, level: TraceLevel = TraceLevel.STANDARD) -> TraceCollector:
        """创建轨迹收集器

        Args:
            session_id: 会话标识符
            level: 追踪级别

        Returns:
            TraceCollector: 轨迹收集器实例
        """
        return TraceCollector(session_id, level)

    def set_trace_level(self, level: TraceLevel) -> None:
        """设置追踪级别

        Args:
            level: 追踪级别
        """
        self.trace_level = level
        if self.collector:
            self.collector.level = level
            self.collector._setup_event_filters()

    def get_coverage_summary(self) -> Dict[str, Any]:
        """获取覆盖率摘要

        Returns:
            Dict[str, Any]: 覆盖率摘要信息
        """
        if not self.collector:
            return {}

        result = self.collector.get_result()
        return {
            "files_covered": len(result.covered_files),
            "functions_covered": len(result.covered_functions),
            "total_lines_covered": result.statistics.get('total_lines_covered', 0),
            "branches_covered": result.statistics.get('covered_branches', 0),
            "total_branches": result.statistics.get('total_branches', 0)
        }

    def export_trace_json(self, file_path: str) -> None:
        """导出轨迹数据为JSON格式

        Args:
            file_path: 输出文件路径
        """
        if not self.collector:
            return

        result = self.collector.get_result()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)

    def get_hot_paths(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """获取热点执行路径

        Args:
            top_n: 返回前N个热点路径

        Returns:
            List[Dict[str, Any]]: 热点路径列表
        """
        if not self.collector:
            return []

        function_traces = self.collector.function_traces
        sorted_traces = sorted(
            function_traces.items(),
            key=lambda x: x[1].call_count * x[1].duration,
            reverse=True
        )

        hot_paths = []
        for func_name, trace in sorted_traces[:top_n]:
            hot_paths.append({
                "function": func_name,
                "call_count": trace.call_count,
                "total_duration": trace.duration,
                "avg_duration": trace.duration / trace.call_count if trace.call_count > 0 else 0,
                "covered_lines": len(trace.covered_lines)
            })

        return hot_paths
