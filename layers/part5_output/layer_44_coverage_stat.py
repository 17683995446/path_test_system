"""
Layer 44: Coverage统计Layer - 覆盖率统计分析层【V3.1升级】

本层负责对测试覆盖率数据进行全面的统计分析，包括行覆盖率、分支覆盖率、
函数覆盖率、路径覆盖率等多维度指标计算，并生成详细的覆盖率报告和趋势分析。
"""

from typing import Any, Optional, List, Dict, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import defaultdict
from datetime import datetime


class CoverageMetricType(Enum):
    """覆盖率指标类型枚举"""
    LINE = auto()
    BRANCH = auto()
    FUNCTION = auto()
    PATH = auto()
    STATEMENT = auto()
    CONDITION = auto()
    TOGGLE = auto()
    MC_DC = auto()
    COMPOSITE = auto()


class CoverageLevel(Enum):
    """覆盖率等级枚举"""
    CRITICAL = auto()
    HIGH = auto()
    MEDIUM = auto()
    LOW = auto()
    INSUFFICIENT = auto()


@dataclass
class CoverageMetric:
    """覆盖率指标数据模型

    Attributes:
        metric_type: 指标类型
        metric_name: 指标名称
        covered_count: 已覆盖数量
        total_count: 总数量
        coverage_rate: 覆盖率（0-100）
        weight: 权重系数
        weighted_score: 加权得分
        details: 详细信息
        timestamp: 统计时间戳
    """
    metric_type: CoverageMetricType
    metric_name: str
    covered_count: int = 0
    total_count: int = 0
    coverage_rate: float = 0.0
    weight: float = 1.0
    weighted_score: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=datetime.now().timestamp)

    def __post_init__(self) -> None:
        """初始化后计算覆盖率"""
        if self.total_count > 0:
            self.coverage_rate = (self.covered_count / self.total_count) * 100.0
        self.weighted_score = self.coverage_rate * self.weight

    def is_complete(self) -> bool:
        """检查是否完全覆盖"""
        return self.covered_count >= self.total_count and self.total_count > 0

    def get_level(self) -> CoverageLevel:
        """获取覆盖率等级

        Returns:
            CoverageLevel: 覆盖率等级
        """
        rate = self.coverage_rate
        if rate >= 90:
            return CoverageLevel.CRITICAL
        elif rate >= 75:
            return CoverageLevel.HIGH
        elif rate >= 50:
            return CoverageLevel.MEDIUM
        elif rate >= 25:
            return CoverageLevel.LOW
        else:
            return CoverageLevel.INSUFFICIENT

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "metric_type": self.metric_type.name,
            "metric_name": self.metric_name,
            "covered_count": self.covered_count,
            "total_count": self.total_count,
            "coverage_rate": round(self.coverage_rate, 2),
            "weight": self.weight,
            "weighted_score": round(self.weighted_score, 2),
            "level": self.get_level().name,
            "details": self.details,
            "timestamp": self.timestamp
        }


@dataclass
class FileCoverageDetail:
    """文件覆盖率详细信息

    Attributes:
        file_path: 文件路径
        relative_path: 相对路径
        language: 编程语言
        line_coverage: 行覆盖率
        branch_coverage: 分支覆盖率
        function_coverage: 函数覆盖率
        executable_lines: 可执行行数
        covered_lines: 已覆盖行数
        uncovered_lines: 未覆盖行号列表
        branch_count: 分支总数
        covered_branches: 已覆盖分支数
        uncovered_branches: 未覆盖分支ID列表
        function_count: 函数总数
        covered_functions: 已覆盖函数数
        uncovered_functions: 未覆盖函数列表
        complexity: 圈复杂度
        risk_score: 风险评分
        last_modified: 最后修改时间
    """
    file_path: str
    relative_path: str = ""
    language: str = "python"
    line_coverage: float = 0.0
    branch_coverage: float = 0.0
    function_coverage: float = 0.0
    executable_lines: int = 0
    covered_lines: Set[int] = field(default_factory=set)
    uncovered_lines: List[int] = field(default_factory=list)
    branch_count: int = 0
    covered_branches: int = 0
    uncovered_branches: List[str] = field(default_factory=list)
    function_count: int = 0
    covered_functions: int = 0
    uncovered_functions: List[str] = field(default_factory=list)
    complexity: int = 1
    risk_score: float = 0.0
    last_modified: Optional[float] = None

    def calculate_risk_score(self) -> float:
        """计算风险评分

        Returns:
            float: 风险评分（0-100）
        """
        uncovered_ratio = len(self.uncovered_lines) / self.executable_lines if self.executable_lines > 0 else 0
        uncovered_branch_ratio = len(self.uncovered_branches) / self.branch_count if self.branch_count > 0 else 0
        complexity_factor = min(self.complexity / 20, 1.0)

        self.risk_score = (
            uncovered_ratio * 40 +
            uncovered_branch_ratio * 30 +
            complexity_factor * 30
        )
        return self.risk_score

    def get_priority_score(self) -> float:
        """获取优先级评分（需要优先测试的优先级）

        Returns:
            float: 优先级评分（越高越需要优先测试）
        """
        coverage_gap = 100.0 - self.line_coverage
        complexity_factor = self.complexity / 10
        uncovered_count = len(self.uncovered_lines)

        return coverage_gap * 0.4 + complexity_factor * 30 + uncovered_count * 2

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "file_path": self.file_path,
            "relative_path": self.relative_path,
            "language": self.language,
            "line_coverage": round(self.line_coverage, 2),
            "branch_coverage": round(self.branch_coverage, 2),
            "function_coverage": round(self.function_coverage, 2),
            "executable_lines": self.executable_lines,
            "covered_lines": sorted(list(self.covered_lines)),
            "uncovered_lines": self.uncovered_lines,
            "branch_count": self.branch_count,
            "covered_branches": self.covered_branches,
            "uncovered_branches": self.uncovered_branches,
            "function_count": self.function_count,
            "covered_functions": self.covered_functions,
            "uncovered_functions": self.uncovered_functions,
            "complexity": self.complexity,
            "risk_score": round(self.risk_score, 2),
            "priority_score": round(self.get_priority_score(), 2)
        }


@dataclass
class CoverageTrend:
    """覆盖率趋势数据

    Attributes:
        timestamp: 时间戳
        overall_coverage: 整体覆盖率
        line_coverage: 行覆盖率
        branch_coverage: 分支覆盖率
        function_coverage: 函数覆盖率
        test_count: 测试数量
        execution_time: 执行时间
        commit_id: 提交ID
        branch_name: 分支名称
    """
    timestamp: float
    overall_coverage: float = 0.0
    line_coverage: float = 0.0
    branch_coverage: float = 0.0
    function_coverage: float = 0.0
    test_count: int = 0
    execution_time: float = 0.0
    commit_id: str = ""
    branch_name: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "timestamp": self.timestamp,
            "overall_coverage": round(self.overall_coverage, 2),
            "line_coverage": round(self.line_coverage, 2),
            "branch_coverage": round(self.branch_coverage, 2),
            "function_coverage": round(self.function_coverage, 2),
            "test_count": self.test_count,
            "execution_time": round(self.execution_time, 2),
            "commit_id": self.commit_id,
            "branch_name": self.branch_name
        }


@dataclass
class CoverageStatisticsResult:
    """覆盖率统计结果

    Attributes:
        session_id: 会话标识符
        overall_coverage: 整体覆盖率
        metrics: 各维度覆盖率指标
        file_details: 文件级覆盖率详情
        trends: 覆盖率趋势数据
        target_coverage: 目标覆盖率
        target_met: 是否达到目标
        gap_analysis: 差距分析
        recommendations: 改进建议
        statistics: 统计摘要
        metadata: 其他元信息
    """
    session_id: str
    overall_coverage: float = 0.0
    metrics: Dict[str, CoverageMetric] = field(default_factory=dict)
    file_details: Dict[str, FileCoverageDetail] = field(default_factory=dict)
    trends: List[CoverageTrend] = field(default_factory=list)
    target_coverage: float = 80.0
    target_met: bool = False
    gap_analysis: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_metric(self, metric: CoverageMetric) -> None:
        """添加覆盖率指标"""
        self.metrics[metric.metric_name] = metric

    def get_metric(self, metric_name: str) -> Optional[CoverageMetric]:
        """获取指定指标"""
        return self.metrics.get(metric_name)

    def get_file_detail(self, file_path: str) -> Optional[FileCoverageDetail]:
        """获取文件覆盖率详情"""
        return self.file_details.get(file_path)

    def add_trend(self, trend: CoverageTrend) -> None:
        """添加趋势数据点"""
        self.trends.append(trend)

    def calculate_overall_coverage(self) -> float:
        """计算整体覆盖率"""
        if not self.metrics:
            return 0.0

        total_weighted_score = sum(m.weighted_score for m in self.metrics.values())
        total_weight = sum(m.weight for m in self.metrics.values())

        if total_weight > 0:
            self.overall_coverage = total_weighted_score / total_weight
        else:
            self.overall_coverage = 0.0

        self.target_met = self.overall_coverage >= self.target_coverage
        return self.overall_coverage

    def get_high_priority_files(self, top_n: int = 10) -> List[FileCoverageDetail]:
        """获取高优先级文件（需要优先测试的文件）

        Args:
            top_n: 返回文件数量

        Returns:
            List[FileCoverageDetail]: 按优先级排序的文件列表
        """
        files = list(self.file_details.values())
        files.sort(key=lambda f: f.get_priority_score(), reverse=True)
        return files[:top_n]

    def get_critical_uncovered_items(self) -> Dict[str, List[Any]]:
        """获取关键未覆盖项

        Returns:
            Dict[str, List[Any]]: 按类型分类的未覆盖项
        """
        critical_items: Dict[str, List[Any]] = {
            "critical_lines": [],
            "critical_branches": [],
            "critical_functions": []
        }

        for file_detail in self.file_details.values():
            risk_score = file_detail.risk_score
            if risk_score > 50:
                for line in file_detail.uncovered_lines[:5]:
                    critical_items["critical_lines"].append({
                        "file": file_detail.file_path,
                        "line": line,
                        "risk_score": risk_score
                    })
                for branch in file_detail.uncovered_branches[:3]:
                    critical_items["critical_branches"].append({
                        "file": file_detail.file_path,
                        "branch": branch,
                        "risk_score": risk_score
                    })

        return critical_items

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "session_id": self.session_id,
            "overall_coverage": round(self.overall_coverage, 2),
            "target_coverage": self.target_coverage,
            "target_met": self.target_met,
            "metrics": {k: v.to_dict() for k, v in self.metrics.items()},
            "file_details": {k: v.to_dict() for k, v in self.file_details.items()},
            "trends": [t.to_dict() for t in self.trends],
            "gap_analysis": self.gap_analysis,
            "recommendations": self.recommendations,
            "statistics": self.statistics,
            "metadata": self.metadata
        }


class CoverageStatisticsCalculator:
    """覆盖率统计计算器

    功能描述：
        - 计算多维度覆盖率指标
        - 分析文件级和函数级覆盖率
        - 生成覆盖率趋势报告
        - 识别覆盖率盲点
        - 提供优先级建议
    """

    def __init__(self, target_coverage: float = 80.0):
        """初始化覆盖率统计计算器

        Args:
            target_coverage: 目标覆盖率
        """
        self.target_coverage = target_coverage
        self.weights = {
            CoverageMetricType.LINE: 0.4,
            CoverageMetricType.BRANCH: 0.25,
            CoverageMetricType.FUNCTION: 0.2,
            CoverageMetricType.PATH: 0.15
        }

    def calculate_line_coverage(self, covered_lines: Set[int],
                               total_lines: int) -> CoverageMetric:
        """计算行覆盖率

        Args:
            covered_lines: 已覆盖行号集合
            total_lines: 总行数

        Returns:
            CoverageMetric: 行覆盖率指标
        """
        covered_count = len(covered_lines)
        metric = CoverageMetric(
            metric_type=CoverageMetricType.LINE,
            metric_name="line_coverage",
            covered_count=covered_count,
            total_count=total_lines,
            weight=self.weights[CoverageMetricType.LINE],
            details={
                "covered_lines": sorted(list(covered_lines)),
                "uncovered_count": total_lines - covered_count
            }
        )
        return metric

    def calculate_branch_coverage(self, covered_branches: Set[str],
                                 total_branches: int) -> CoverageMetric:
        """计算分支覆盖率

        Args:
            covered_branches: 已覆盖分支ID集合
            total_branches: 总分支数

        Returns:
            CoverageMetric: 分支覆盖率指标
        """
        covered_count = len(covered_branches)
        metric = CoverageMetric(
            metric_type=CoverageMetricType.BRANCH,
            metric_name="branch_coverage",
            covered_count=covered_count,
            total_count=total_branches,
            weight=self.weights[CoverageMetricType.BRANCH],
            details={
                "covered_branches": sorted(list(covered_branches)),
                "uncovered_count": total_branches - covered_count
            }
        )
        return metric

    def calculate_function_coverage(self, covered_functions: Set[str],
                                   total_functions: int) -> CoverageMetric:
        """计算函数覆盖率

        Args:
            covered_functions: 已覆盖函数名集合
            total_functions: 总函数数

        Returns:
            CoverageMetric: 函数覆盖率指标
        """
        covered_count = len(covered_functions)
        metric = CoverageMetric(
            metric_type=CoverageMetricType.FUNCTION,
            metric_name="function_coverage",
            covered_count=covered_count,
            total_count=total_functions,
            weight=self.weights[CoverageMetricType.FUNCTION],
            details={
                "covered_functions": sorted(list(covered_functions)),
                "uncovered_count": total_functions - covered_count
            }
        )
        return metric

    def calculate_path_coverage(self, covered_paths: Set[str],
                               total_paths: int) -> CoverageMetric:
        """计算路径覆盖率

        Args:
            covered_paths: 已覆盖路径ID集合
            total_paths: 总路径数

        Returns:
            CoverageMetric: 路径覆盖率指标
        """
        covered_count = len(covered_paths)
        metric = CoverageMetric(
            metric_type=CoverageMetricType.PATH,
            metric_name="path_coverage",
            covered_count=covered_count,
            total_count=total_paths,
            weight=self.weights[CoverageMetricType.PATH],
            details={
                "covered_paths": sorted(list(covered_paths)),
                "uncovered_count": total_paths - covered_count
            }
        )
        return metric

    def analyze_file_coverage(self, file_path: str, covered_lines: Set[int],
                            total_lines: int, branch_count: int,
                            covered_branches: Set[str],
                            function_count: int,
                            covered_functions: Set[str],
                            complexity: int = 1) -> FileCoverageDetail:
        """分析文件级覆盖率

        Args:
            file_path: 文件路径
            covered_lines: 已覆盖行号集合
            total_lines: 总行数
            branch_count: 分支总数
            covered_branches: 已覆盖分支ID集合
            function_count: 函数总数
            covered_functions: 已覆盖函数名集合
            complexity: 圈复杂度

        Returns:
            FileCoverageDetail: 文件覆盖率详情
        """
        uncovered_lines = sorted(list(set(range(1, total_lines + 1)) - covered_lines))

        detail = FileCoverageDetail(
            file_path=file_path,
            line_coverage=(len(covered_lines) / total_lines * 100) if total_lines > 0 else 0.0,
            branch_coverage=(len(covered_branches) / branch_count * 100) if branch_count > 0 else 0.0,
            function_coverage=(len(covered_functions) / function_count * 100) if function_count > 0 else 0.0,
            executable_lines=total_lines,
            covered_lines=covered_lines,
            uncovered_lines=uncovered_lines,
            branch_count=branch_count,
            covered_branches=len(covered_branches),
            uncovered_branches=[],
            function_count=function_count,
            covered_functions=len(covered_functions),
            uncovered_functions=[],
            complexity=complexity
        )

        detail.uncovered_branches = [f"branch_{i}" for i in range(branch_count)
                                     if f"branch_{i}" not in covered_branches]

        detail.calculate_risk_score()
        return detail

    def calculate_trend_change(self, previous: CoverageTrend,
                              current: CoverageTrend) -> Dict[str, float]:
        """计算趋势变化

        Args:
            previous: 之前的趋势数据
            current: 当前的趋势数据

        Returns:
            Dict[str, float]: 变化量字典
        """
        return {
            "overall_change": current.overall_coverage - previous.overall_coverage,
            "line_change": current.line_coverage - previous.line_coverage,
            "branch_change": current.branch_coverage - previous.branch_coverage,
            "function_change": current.function_coverage - previous.function_coverage
        }


class CoverageStatLayer:
    """Coverage统计Layer - 覆盖率统计分析层【V3.1升级】

    功能描述：
        - 收集和计算多维度覆盖率指标
        - 分析文件级和函数级覆盖率详情
        - 跟踪覆盖率随时间的变化趋势
        - 识别低覆盖率区域和高风险代码
        - 生成覆盖率差距分析和改进建议
        - 支持多种编程语言的覆盖率统计

    输入类型：
        - PipelineContext: 包含覆盖率原始数据
        - 已执行的轨迹信息
        - 源代码结构信息

    输出类型：
        - CoverageStatisticsResult: 覆盖率统计结果
        - 包含指标、文件详情、趋势和建议

    使用场景：
        - 测试覆盖率评估和报告
        - 质量门禁检查
        - CI/CD集成
        - 测试优先级排序
        - 回归测试分析

    V3.1升级点：
        - 支持增量覆盖率统计
        - 多分支覆盖率对比分析
        - 智能风险评分算法
        - 自动生成改进建议
        - 支持自定义权重配置
        - 增强的覆盖率趋势可视化
    """

    description: str = "Coverage统计Layer - 统计分析测试覆盖率多维度指标"
    input_type: str = "PipelineContext - 包含覆盖率原始数据和轨迹信息"
    output_type: str = "CoverageStatisticsResult - 覆盖率统计结果"

    def __init__(self):
        """初始化覆盖率统计分析层"""
        self.calculator = CoverageStatisticsCalculator()
        self.session_id = ""
        self.source_files: List[str] = []
        self.target_coverage = 80.0

    def process(self, context: Any) -> CoverageStatisticsResult:
        """处理覆盖率数据，生成统计报告

        Args:
            context: PipelineContext对象，包含覆盖率相关数据

        Returns:
            CoverageStatisticsResult: 覆盖率统计结果

        Raises:
            ValueError: 当缺少必要的覆盖率数据时
        """
        self.session_id = context.get('session_id', 'default_session')
        self.source_files = context.get('source_files', [])
        self.target_coverage = context.get('target_coverage', 80.0)
        self.calculator.target_coverage = self.target_coverage

        result = CoverageStatisticsResult(
            session_id=self.session_id,
            target_coverage=self.target_coverage
        )

        if context.has('trace_collection_result'):
            trace_result = context.get('trace_collection_result')
            self._process_from_trace(trace_result, result)

        if context.has('covered_lines'):
            covered_lines = context.get('covered_lines')
            self._process_covered_lines(covered_lines, result)

        if context.has('executable_lines'):
            executable_lines = context.get('executable_lines')
            self._process_executable_lines(executable_lines, result)

        if context.has('coverage_metrics'):
            coverage_metrics = context.get('coverage_metrics')
            self._process_coverage_metrics(coverage_metrics, result)

        if context.has('file_complexity'):
            file_complexity = context.get('file_complexity')
            self._apply_complexity(file_complexity, result)

        if context.has('previous_coverage'):
            previous_coverage = context.get('previous_coverage')
            self._calculate_trends(previous_coverage, result)

        result.overall_coverage = result.calculate_overall_coverage()
        result.gap_analysis = self._analyze_gap(result)
        result.recommendations = self._generate_recommendations(result)
        result.statistics = self._calculate_summary_statistics(result)

        result.metadata = {
            "processing_time": datetime.now().timestamp(),
            "source_files_count": len(self.source_files),
            "files_analyzed": len(result.file_details),
            "version": "V3.1"
        }

        context.set('coverage_statistics_result', result)
        context.set('coverage_statistics_complete', True)
        context.set('overall_coverage', result.overall_coverage)

        return result

    def _process_from_trace(self, trace_result: Any, result: CoverageStatisticsResult) -> None:
        """从轨迹结果处理覆盖率数据

        Args:
            trace_result: 轨迹采集结果
            result: 覆盖率统计结果
        """
        if hasattr(trace_result, 'covered_lines'):
            covered_lines = trace_result.covered_lines
            self._process_covered_lines(covered_lines, result)

        if hasattr(trace_result, 'function_traces'):
            function_traces = trace_result.function_traces
            total_functions = len(function_traces)
            covered_functions = {
                name for name, trace in function_traces.items()
                if trace.call_count > 0
            }
            metric = self.calculator.calculate_function_coverage(
                set(covered_functions), total_functions
            )
            result.add_metric(metric)

    def _process_covered_lines(self, covered_lines: Any,
                              result: CoverageStatisticsResult) -> None:
        """处理覆盖的行信息

        Args:
            covered_lines: 覆盖的行数据
            result: 覆盖率统计结果
        """
        if isinstance(covered_lines, dict):
            for file_path, lines in covered_lines.items():
                if file_path not in result.file_details:
                    result.file_details[file_path] = FileCoverageDetail(
                        file_path=file_path,
                        covered_lines=set(lines) if isinstance(lines, (list, set)) else set()
                    )
                else:
                    result.file_details[file_path].covered_lines = set(lines)

    def _process_executable_lines(self, executable_lines: Any,
                                 result: CoverageStatisticsResult) -> None:
        """处理可执行行信息

        Args:
            executable_lines: 可执行行数据
            result: 覆盖率统计结果
        """
        if isinstance(executable_lines, dict):
            for file_path, total in executable_lines.items():
                if file_path in result.file_details:
                    result.file_details[file_path].executable_lines = total
                    covered = len(result.file_details[file_path].covered_lines)
                    rate = (covered / total * 100) if total > 0 else 0.0
                    result.file_details[file_path].line_coverage = rate

    def _process_coverage_metrics(self, coverage_metrics: Any,
                                 result: CoverageStatisticsResult) -> None:
        """处理覆盖率指标数据

        Args:
            coverage_metrics: 覆盖率指标数据
            result: 覆盖率统计结果
        """
        if isinstance(coverage_metrics, dict):
            for metric_name, metric_data in coverage_metrics.items():
                if isinstance(metric_data, dict):
                    covered = metric_data.get('covered', 0)
                    total = metric_data.get('total', 0)
                    metric_type_name = metric_data.get('type', 'LINE')

                    try:
                        metric_type = CoverageMetricType[metric_type_name]
                    except KeyError:
                        metric_type = CoverageMetricType.LINE

                    weight = self.calculator.weights.get(metric_type, 1.0)
                    metric = CoverageMetric(
                        metric_type=metric_type,
                        metric_name=metric_name,
                        covered_count=covered,
                        total_count=total,
                        weight=weight
                    )
                    result.add_metric(metric)

    def _apply_complexity(self, file_complexity: Any,
                        result: CoverageStatisticsResult) -> None:
        """应用复杂度数据

        Args:
            file_complexity: 文件复杂度数据
            result: 覆盖率统计结果
        """
        if isinstance(file_complexity, dict):
            for file_path, complexity in file_complexity.items():
                if file_path in result.file_details:
                    result.file_details[file_path].complexity = complexity
                    result.file_details[file_path].calculate_risk_score()

    def _calculate_trends(self, previous_coverage: Any,
                        result: CoverageStatisticsResult) -> None:
        """计算覆盖率趋势

        Args:
            previous_coverage: 之前的覆盖率数据
            result: 覆盖率统计结果
        """
        if hasattr(previous_coverage, 'trends'):
            result.trends.extend(previous_coverage.trends)

        current_trend = CoverageTrend(
            timestamp=datetime.now().timestamp(),
            overall_coverage=result.overall_coverage
        )

        if 'line_coverage' in result.metrics:
            current_trend.line_coverage = result.metrics['line_coverage'].coverage_rate
        if 'branch_coverage' in result.metrics:
            current_trend.branch_coverage = result.metrics['branch_coverage'].coverage_rate
        if 'function_coverage' in result.metrics:
            current_trend.function_coverage = result.metrics['function_coverage'].coverage_rate

        result.trends.append(current_trend)

        if len(result.trends) > 1:
            previous = result.trends[-2]
            changes = self.calculator.calculate_trend_change(previous, current_trend)
            result.metadata['trend_changes'] = changes

    def _analyze_gap(self, result: CoverageStatisticsResult) -> Dict[str, Any]:
        """分析覆盖率差距

        Args:
            result: 覆盖率统计结果

        Returns:
            Dict[str, Any]: 差距分析结果
        """
        gap = {
            "target": self.target_coverage,
            "current": result.overall_coverage,
            "gap": self.target_coverage - result.overall_coverage,
            "gap_percentage": 0.0
        }

        if self.target_coverage > 0:
            gap["gap_percentage"] = (
                (self.target_coverage - result.overall_coverage) / self.target_coverage * 100
            )

        low_coverage_files = []
        for file_detail in result.file_details.values():
            if file_detail.line_coverage < self.target_coverage:
                low_coverage_files.append({
                    "file": file_detail.file_path,
                    "coverage": file_detail.line_coverage,
                    "gap": self.target_coverage - file_detail.line_coverage,
                    "uncovered_count": len(file_detail.uncovered_lines)
                })

        gap["low_coverage_files"] = sorted(
            low_coverage_files,
            key=lambda x: x['gap'],
            reverse=True
        )[:20]

        return gap

    def _generate_recommendations(self, result: CoverageStatisticsResult) -> List[str]:
        """生成改进建议

        Args:
            result: 覆盖率统计结果

        Returns:
            List[str]: 改进建议列表
        """
        recommendations = []

        if result.overall_coverage < self.target_coverage:
            gap = self.target_coverage - result.overall_coverage
            recommendations.append(
                f"整体覆盖率({result.overall_coverage:.1f}%)未达到目标({self.target_coverage}%)，"
                f"差距{gap:.1f}%，建议优先测试高风险低覆盖文件"
            )

        critical_items = result.get_critical_uncovered_items()
        if critical_items["critical_lines"]:
            recommendations.append(
                f"发现{len(critical_items['critical_lines'])}个高风险未覆盖行，"
                f"建议优先为这些位置编写测试用例"
            )

        high_priority = result.get_high_priority_files(5)
        if high_priority:
            file_names = [f.file_path for f in high_priority]
            recommendations.append(
                f"建议优先测试以下文件：{', '.join(file_names[:3])}"
            )

        if 'branch_coverage' in result.metrics:
            branch_cov = result.metrics['branch_coverage'].coverage_rate
            if branch_cov < 60:
                recommendations.append(
                    f"分支覆盖率({branch_cov:.1f}%)偏低，建议增加条件分支测试用例"
                )

        if result.trends and len(result.trends) >= 2:
            recent_change = result.trends[-1].overall_coverage - result.trends[-2].overall_coverage
            if recent_change < 0:
                recommendations.append(
                    f"覆盖率较上次下降了{abs(recent_change):.1f}%，请检查新增代码的测试覆盖"
                )

        return recommendations

    def _calculate_summary_statistics(self, result: CoverageStatisticsResult) -> Dict[str, Any]:
        """计算汇总统计信息

        Args:
            result: 覆盖率统计结果

        Returns:
            Dict[str, Any]: 统计摘要
        """
        total_files = len(result.file_details)
        covered_files = sum(1 for f in result.file_details.values()
                          if f.line_coverage >= 100.0)
        partial_files = sum(1 for f in result.file_details.values()
                           if 0 < f.line_coverage < 100.0)
        uncovered_files = sum(1 for f in result.file_details.values()
                             if f.line_coverage == 0.0)

        total_lines = sum(f.executable_lines for f in result.file_details.values())
        total_covered_lines = sum(len(f.covered_lines) for f in result.file_details.values())
        total_uncovered_lines = sum(len(f.uncovered_lines) for f in result.file_details.values())

        return {
            "total_files": total_files,
            "fully_covered_files": covered_files,
            "partially_covered_files": partial_files,
            "uncovered_files": uncovered_files,
            "total_executable_lines": total_lines,
            "total_covered_lines": total_covered_lines,
            "total_uncovered_lines": total_uncovered_lines,
            "average_file_coverage": sum(f.line_coverage for f in result.file_details.values()) / total_files if total_files > 0 else 0,
            "high_risk_files": sum(1 for f in result.file_details.values() if f.risk_score > 50)
        }

    def set_target_coverage(self, target: float) -> None:
        """设置目标覆盖率

        Args:
            target: 目标覆盖率值（0-100）
        """
        self.target_coverage = max(0.0, min(100.0, target))
        self.calculator.target_coverage = self.target_coverage

    def set_metric_weights(self, weights: Dict[str, float]) -> None:
        """设置指标权重

        Args:
            weights: 权重字典
        """
        for metric_name, weight in weights.items():
            try:
                metric_type = CoverageMetricType[metric_name.upper()]
                self.calculator.weights[metric_type] = weight
            except KeyError:
                pass

    def export_report(self, result: CoverageStatisticsResult,
                     format: str = "dict") -> Any:
        """导出覆盖率报告

        Args:
            result: 覆盖率统计结果
            format: 输出格式

        Returns:
            Any: 报告数据
        """
        if format == "dict":
            return result.to_dict()
        elif format == "summary":
            return {
                "session_id": result.session_id,
                "overall_coverage": result.overall_coverage,
                "target_met": result.target_met,
                "file_count": len(result.file_details),
                "recommendations": result.recommendations
            }
        else:
            return result.to_dict()
