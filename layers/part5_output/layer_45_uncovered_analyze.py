"""
Layer 45: Uncovered分析Layer - 未覆盖路径智能分析层【V3.1升级】

本层负责智能分析未被测试覆盖的代码路径，识别潜在风险，推荐优先测试的路径，
并分析未覆盖的原因（如：异常处理路径、边界条件、错误处理分支等）。
"""

from typing import Any, Optional, List, Dict, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import defaultdict


class UncoveredReason(Enum):
    """未覆盖原因枚举"""
    NORMAL_PATH_NOT_EXECUTED = auto()
    EXCEPTION_PATH_NOT_TESTED = auto()
    BOUNDARY_CONDITION_NOT_COVERED = auto()
    ERROR_HANDLING_NOT_TESTED = auto()
    DEAD_CODE = auto()
    DYNAMIC_BRANCH = auto()
    REFLECTION_BASED_CALL = auto()
    PLATFORM_SPECIFIC_CODE = auto()
    FEATURE_FLAG_DISABLED = auto()
    CONFIGURATION_DEPENDENT = auto()
    ASYNC_CODE_NOT_EXECUTED = auto()
    UNKNOWN = auto()


class RiskLevel(Enum):
    """风险等级枚举"""
    CRITICAL = auto()
    HIGH = auto()
    MEDIUM = auto()
    LOW = auto()
    INFO = auto()


class PathDifficulty(Enum):
    """路径难度枚举"""
    EASY = auto()
    MODERATE = auto()
    DIFFICULT = auto()
    VERY_DIFFICULT = auto()


@dataclass
class UncoveredItem:
    """未覆盖项数据模型

    Attributes:
        item_id: 唯一标识符
        item_type: 未覆盖项类型（line, branch, path, function）
        file_path: 文件路径
        line_number: 行号（行覆盖时）
        branch_id: 分支ID（分支覆盖时）
        path_id: 路径ID（路径覆盖时）
        function_name: 函数名称
        reason: 未覆盖原因
        risk_level: 风险等级
        difficulty: 路径难度
        test_suggestions: 测试建议列表
        required_inputs: 所需的测试输入
        dependencies: 依赖的外部条件
        related_issues: 相关的问题列表
        last_analyzed: 最后分析时间
    """
    item_id: str
    item_type: str
    file_path: str
    line_number: int = 0
    branch_id: str = ""
    path_id: str = ""
    function_name: str = ""
    reason: UncoveredReason = UncoveredReason.UNKNOWN
    risk_level: RiskLevel = RiskLevel.MEDIUM
    difficulty: PathDifficulty = PathDifficulty.MODERATE
    test_suggestions: List[str] = field(default_factory=list)
    required_inputs: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    related_issues: List[str] = field(default_factory=list)
    last_analyzed: float = 0.0

    def get_priority_score(self) -> float:
        """计算优先级评分

        Returns:
            float: 优先级评分（越高越需要优先测试）
        """
        risk_weights = {
            RiskLevel.CRITICAL: 100,
            RiskLevel.HIGH: 75,
            RiskLevel.MEDIUM: 50,
            RiskLevel.LOW: 25,
            RiskLevel.INFO: 10
        }

        difficulty_weights = {
            PathDifficulty.EASY: 40,
            PathDifficulty.MODERATE: 30,
            PathDifficulty.DIFFICULT: 20,
            PathDifficulty.VERY_DIFFICULT: 10
        }

        base_score = risk_weights.get(self.risk_level, 50)
        base_score += difficulty_weights.get(self.difficulty, 30)

        if self.reason == UncoveredReason.EXCEPTION_PATH_NOT_TESTED:
            base_score += 15
        elif self.reason == UncoveredReason.BOUNDARY_CONDITION_NOT_COVERED:
            base_score += 10

        return base_score

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "item_id": self.item_id,
            "item_type": self.item_type,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "branch_id": self.branch_id,
            "path_id": self.path_id,
            "function_name": self.function_name,
            "reason": self.reason.name,
            "risk_level": self.risk_level.name,
            "difficulty": self.difficulty.name,
            "priority_score": self.get_priority_score(),
            "test_suggestions": self.test_suggestions,
            "required_inputs": self.required_inputs,
            "dependencies": self.dependencies,
            "related_issues": self.related_issues
        }


@dataclass
class UncoveredGroup:
    """未覆盖项分组

    Attributes:
        group_id: 分组ID
        group_type: 分组类型
        items: 分组内的未覆盖项
        summary: 分组摘要
        recommendations: 分组建议
    """
    group_id: str
    group_type: str
    items: List[UncoveredItem] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)

    def add_item(self, item: UncoveredItem) -> None:
        """添加未覆盖项"""
        self.items.append(item)

    def get_total_priority(self) -> float:
        """获取分组总优先级"""
        return sum(item.get_priority_score() for item in self.items)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "group_id": self.group_id,
            "group_type": self.group_type,
            "item_count": len(self.items),
            "total_priority": self.get_total_priority(),
            "summary": self.summary,
            "recommendations": self.recommendations,
            "items": [item.to_dict() for item in self.items]
        }


@dataclass
class CoverageGapAnalysis:
    """覆盖率差距分析

    Attributes:
        uncovered_items: 未覆盖项列表
        uncovered_by_reason: 按原因分类的未覆盖项
        uncovered_by_file: 按文件分类的未覆盖项
        uncovered_by_function: 按函数分类的未覆盖项
        critical_gaps: 关键差距列表
        test_effort_estimate: 测试工作量估算
        recommendations: 改进建议
        metadata: 其他元信息
    """
    uncovered_items: List[UncoveredItem] = field(default_factory=list)
    uncovered_by_reason: Dict[UncoveredReason, List[UncoveredItem]] = field(default_factory=dict)
    uncovered_by_file: Dict[str, List[UncoveredItem]] = field(default_factory=dict)
    uncovered_by_function: Dict[str, List[UncoveredItem]] = field(default_factory=dict)
    critical_gaps: List[Dict[str, Any]] = field(default_factory=list)
    test_effort_estimate: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_uncovered_item(self, item: UncoveredItem) -> None:
        """添加未覆盖项"""
        self.uncovered_items.append(item)

        if item.reason not in self.uncovered_by_reason:
            self.uncovered_by_reason[item.reason] = []
        self.uncovered_by_reason[item.reason].append(item)

        if item.file_path not in self.uncovered_by_file:
            self.uncovered_by_file[item.file_path] = []
        self.uncovered_by_file[item.file_path].append(item)

        if item.function_name:
            if item.function_name not in self.uncovered_by_function:
                self.uncovered_by_function[item.function_name] = []
            self.uncovered_by_function[item.function_name].append(item)

    def get_sorted_by_priority(self) -> List[UncoveredItem]:
        """按优先级排序获取未覆盖项

        Returns:
            List[UncoveredItem]: 排序后的未覆盖项列表
        """
        return sorted(self.uncovered_items, key=lambda x: x.get_priority_score(), reverse=True)

    def get_critical_items(self, top_n: int = 20) -> List[UncoveredItem]:
        """获取最关键的未覆盖项

        Args:
            top_n: 返回数量

        Returns:
            List[UncoveredItem]: 关键未覆盖项列表
        """
        sorted_items = self.get_sorted_by_priority()
        return sorted_items[:top_n]

    def get_items_by_file(self, file_path: str) -> List[UncoveredItem]:
        """获取指定文件的未覆盖项

        Args:
            file_path: 文件路径

        Returns:
            List[UncoveredItem]: 该文件的未覆盖项列表
        """
        return self.uncovered_by_file.get(file_path, [])

    def get_items_by_reason(self, reason: UncoveredReason) -> List[UncoveredItem]:
        """获取指定原因的未覆盖项

        Args:
            reason: 未覆盖原因

        Returns:
            List[UncoveredItem]: 该原因的未覆盖项列表
        """
        return self.uncovered_by_reason.get(reason, [])

    def generate_summary(self) -> Dict[str, Any]:
        """生成分析摘要

        Returns:
            Dict[str, Any]: 分析摘要
        """
        return {
            "total_uncovered": len(self.uncovered_items),
            "by_reason": {
                reason.name: len(items)
                for reason, items in self.uncovered_by_reason.items()
            },
            "by_file": {
                file_path: len(items)
                for file_path, items in self.uncovered_by_file.items()
            },
            "critical_count": len(self.critical_gaps),
            "estimated_test_cases": self.test_effort_estimate.get("test_cases", 0)
        }

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "total_uncovered": len(self.uncovered_items),
            "uncovered_by_reason": {
                reason.name: len(items)
                for reason, items in self.uncovered_by_reason.items()
            },
            "uncovered_by_file": {
                file_path: len(items)
                for file_path, items in self.uncovered_by_file.items()
            },
            "critical_gaps": self.critical_gaps,
            "test_effort_estimate": self.test_effort_estimate,
            "recommendations": self.recommendations,
            "metadata": self.metadata
        }


class UncoveredPathAnalyzer:
    """未覆盖路径分析器

    功能描述：
        - 分析未覆盖代码的原因
        - 评估未覆盖项的风险等级
        - 推荐测试用例优先级
        - 估算测试工作量
        - 生成改进建议
    """

    def __init__(self):
        """初始化未覆盖路径分析器"""
        self.pattern_analyzers = self._init_pattern_analyzers()

    def _init_pattern_analyzers(self) -> Dict[str, Any]:
        """初始化模式分析器"""
        return {
            "exception_patterns": [
                r"try\s*:",
                r"except\s+\w+",
                r"raise\s+",
                r"finally\s*:"
            ],
            "boundary_patterns": [
                r"[<>]=?\s*\d+",
                r"==\s*\d+",
                r"!=\s*\d+",
                r"range\(",
                r"len\("
            ],
            "error_handling_patterns": [
                r"if\s+.*error",
                r"if\s+.*fail",
                r"if\s+.*invalid",
                r"if\s+.*null",
                r"if\s+.*None"
            ],
            "dynamic_patterns": [
                r"getattr\(",
                r"setattr\(",
                r"eval\(",
                r"exec\(",
                r"globals\(",
                r"locals\("
            ]
        }

    def analyze_uncovered_line(self, file_path: str, line_number: int,
                              source_context: str,
                              function_context: str) -> UncoveredItem:
        """分析未覆盖的行

        Args:
            file_path: 文件路径
            line_number: 行号
            source_context: 源代码上下文
            function_context: 函数上下文

        Returns:
            UncoveredItem: 未覆盖项
        """
        reason = self._determine_reason(source_context, function_context)
        risk_level = self._assess_risk(reason, source_context, function_context)
        difficulty = self._assess_difficulty(reason, source_context)

        item = UncoveredItem(
            item_id=f"line_{file_path}_{line_number}",
            item_type="line",
            file_path=file_path,
            line_number=line_number,
            reason=reason,
            risk_level=risk_level,
            difficulty=difficulty
        )

        item.test_suggestions = self._generate_test_suggestions(item, source_context, function_context)
        item.required_inputs = self._determine_required_inputs(item, source_context)

        return item

    def analyze_uncovered_branch(self, file_path: str, branch_id: str,
                                condition: str, line_number: int,
                                context: str) -> UncoveredItem:
        """分析未覆盖的分支

        Args:
            file_path: 文件路径
            branch_id: 分支ID
            condition: 分支条件
            line_number: 行号
            context: 上下文

        Returns:
            UncoveredItem: 未覆盖项
        """
        reason = self._determine_branch_reason(condition, context)
        risk_level = self._assess_branch_risk(condition, context)
        difficulty = self._assess_difficulty(reason, condition)

        item = UncoveredItem(
            item_id=f"branch_{file_path}_{branch_id}",
            item_type="branch",
            file_path=file_path,
            branch_id=branch_id,
            line_number=line_number,
            reason=reason,
            risk_level=risk_level,
            difficulty=difficulty
        )

        item.test_suggestions = self._generate_branch_suggestions(item, condition)
        item.required_inputs = self._extract_branch_inputs(condition)

        return item

    def _determine_reason(self, source_context: str, function_context: str) -> UncoveredReason:
        """判断未覆盖原因

        Args:
            source_context: 源代码上下文
            function_context: 函数上下文

        Returns:
            UncoveredReason: 未覆盖原因
        """
        import re

        for pattern in self.pattern_analyzers["exception_patterns"]:
            if re.search(pattern, source_context):
                return UncoveredReason.EXCEPTION_PATH_NOT_TESTED

        for pattern in self.pattern_analyzers["boundary_patterns"]:
            if re.search(pattern, source_context):
                return UncoveredReason.BOUNDARY_CONDITION_NOT_COVERED

        for pattern in self.pattern_analyzers["error_handling_patterns"]:
            if re.search(pattern, source_context, re.IGNORECASE):
                return UncoveredReason.ERROR_HANDLING_NOT_TESTED

        for pattern in self.pattern_analyzers["dynamic_patterns"]:
            if re.search(pattern, source_context):
                return UncoveredReason.DYNAMIC_BRANCH

        return UncoveredReason.NORMAL_PATH_NOT_EXECUTED

    def _assess_risk(self, reason: UncoveredReason, source_context: str,
                   function_context: str) -> RiskLevel:
        """评估风险等级

        Args:
            reason: 未覆盖原因
            source_context: 源代码上下文
            function_context: 函数上下文

        Returns:
            RiskLevel: 风险等级
        """
        risk_keywords = [
            "security", "auth", "payment", "transaction",
            "delete", "remove", "destroy", "critical",
            "validate", "verify", "check_permission"
        ]

        context_lower = (source_context + function_context).lower()
        risk_matches = sum(1 for keyword in risk_keywords if keyword in context_lower)

        if reason == UncoveredReason.EXCEPTION_PATH_NOT_TESTED:
            if risk_matches >= 2:
                return RiskLevel.CRITICAL
            elif risk_matches >= 1:
                return RiskLevel.HIGH
            else:
                return RiskLevel.MEDIUM
        elif reason == UncoveredReason.BOUNDARY_CONDITION_NOT_COVERED:
            if any(x in context_lower for x in ["zero", "null", "empty", "negative", "max"]):
                return RiskLevel.HIGH
            return RiskLevel.MEDIUM
        elif reason == UncoveredReason.ERROR_HANDLING_NOT_TESTED:
            return RiskLevel.HIGH
        else:
            return RiskLevel.MEDIUM

    def _assess_branch_risk(self, condition: str, context: str) -> RiskLevel:
        """评估分支风险

        Args:
            condition: 分支条件
            context: 上下文

        Returns:
            RiskLevel: 风险等级
        """
        critical_operators = ["==", "!=", ">=", "<="]
        for op in critical_operators:
            if op in condition:
                return RiskLevel.HIGH

        if "not" in condition.lower() or "is None" in condition.lower():
            return RiskLevel.MEDIUM

        return RiskLevel.LOW

    def _assess_difficulty(self, reason: UncoveredReason, context: str) -> PathDifficulty:
        """评估测试难度

        Args:
            reason: 未覆盖原因
            context: 上下文

        Returns:
            PathDifficulty: 难度等级
        """
        if reason == UncoveredReason.EXCEPTION_PATH_NOT_TESTED:
            return PathDifficulty.MODERATE
        elif reason == UncoveredReason.BOUNDARY_CONDITION_NOT_COVERED:
            return PathDifficulty.DIFFICULT
        elif reason == UncoveredReason.DYNAMIC_BRANCH:
            return PathDifficulty.VERY_DIFFICULT
        else:
            return PathDifficulty.EASY

    def _generate_test_suggestions(self, item: UncoveredItem,
                                  source_context: str,
                                  function_context: str) -> List[str]:
        """生成测试建议

        Args:
            item: 未覆盖项
            source_context: 源代码上下文
            function_context: 函数上下文

        Returns:
            List[str]: 测试建议列表
        """
        suggestions = []

        if item.reason == UncoveredReason.EXCEPTION_PATH_NOT_TESTED:
            suggestions.append(f"测试{item.function_name}的异常处理路径")
            suggestions.append("提供会导致异常抛出的输入参数")
            suggestions.append("模拟依赖服务的错误响应")
        elif item.reason == UncoveredReason.BOUNDARY_CONDITION_NOT_COVERED:
            suggestions.append(f"测试边界条件：最小值、最大值、零值")
            suggestions.append("提供临界值作为输入")
        elif item.reason == UncoveredReason.ERROR_HANDLING_NOT_TESTED:
            suggestions.append(f"测试错误处理分支")
            suggestions.append("提供无效输入触发错误处理逻辑")
        else:
            suggestions.append("检查测试用例是否覆盖了该代码路径")
            suggestions.append("审查测试用例的设计完整性")

        return suggestions

    def _generate_branch_suggestions(self, item: UncoveredItem,
                                    condition: str) -> List[str]:
        """生成分支测试建议

        Args:
            item: 未覆盖项
            condition: 分支条件

        Returns:
            List[str]: 测试建议列表
        """
        suggestions = []

        suggestions.append(f"测试条件 '{condition}' 为真的情况")
        suggestions.append(f"测试条件 '{condition}' 为假的情况")

        return suggestions

    def _determine_required_inputs(self, item: UncoveredItem,
                                   source_context: str) -> Dict[str, Any]:
        """确定所需测试输入

        Args:
            item: 未覆盖项
            source_context: 源代码上下文

        Returns:
            Dict[str, Any]: 所需输入字典
        """
        inputs: Dict[str, Any] = {}

        if item.reason == UncoveredReason.BOUNDARY_CONDITION_NOT_COVERED:
            inputs["boundary_values"] = ["最小值", "最大值", "零值", "临界值"]

        if item.reason == UncoveredReason.EXCEPTION_PATH_NOT_TESTED:
            inputs["exception_scenarios"] = ["空输入", "非法类型", "网络错误", "超时"]

        return inputs

    def _extract_branch_inputs(self, condition: str) -> Dict[str, Any]:
        """提取分支所需输入

        Args:
            condition: 分支条件

        Returns:
            Dict[str, Any]: 输入字典
        """
        inputs: Dict[str, Any] = {
            "true_condition": "满足条件的输入值",
            "false_condition": "不满足条件的输入值"
        }

        if ">=" in condition or ">" in condition:
            inputs["boundary_hint"] = "需要测试临界值"
        if "None" in condition or "null" in condition.lower():
            inputs["null_test"] = True

        return inputs

    def estimate_test_effort(self, items: List[UncoveredItem]) -> Dict[str, Any]:
        """估算测试工作量

        Args:
            items: 未覆盖项列表

        Returns:
            Dict[str, Any]: 工作量估算
        """
        effort_factors = {
            PathDifficulty.EASY: 1,
            PathDifficulty.MODERATE: 2,
            PathDifficulty.DIFFICULT: 4,
            PathDifficulty.VERY_DIFFICULT: 8
        }

        risk_multipliers = {
            RiskLevel.CRITICAL: 3,
            RiskLevel.HIGH: 2,
            RiskLevel.MEDIUM: 1.5,
            RiskLevel.LOW: 1,
            RiskLevel.INFO: 0.5
        }

        total_effort = 0
        estimated_test_cases = 0

        for item in items:
            base_effort = effort_factors.get(item.difficulty, 2)
            multiplier = risk_multipliers.get(item.risk_level, 1)
            item_effort = base_effort * multiplier
            total_effort += item_effort
            estimated_test_cases += 1

        return {
            "total_effort_hours": round(total_effort * 0.5, 1),
            "estimated_test_cases": estimated_test_cases,
            "critical_cases": sum(1 for i in items if i.risk_level == RiskLevel.CRITICAL),
            "high_priority_cases": sum(1 for i in items if i.risk_level == RiskLevel.HIGH)
        }


class UncoveredAnalyzeLayer:
    """Uncovered分析Layer - 未覆盖路径智能分析层【V3.1升级】

    功能描述：
        - 智能分析未被测试覆盖的代码路径
        - 识别未覆盖的原因和风险等级
        - 推荐优先测试的代码路径
        - 生成测试用例建议
        - 估算测试工作量
        - 按文件、函数、原因等多维度分类
        - 提供改进建议和优化策略

    输入类型：
        - PipelineContext: 包含覆盖率统计结果和源代码信息
        - 未覆盖的行号、路径、分支信息
        - 源代码上下文

    输出类型：
        - CoverageGapAnalysis: 覆盖率差距分析结果
        - 包含未覆盖项、分析和建议

    使用场景：
        - 测试覆盖率提升指导
        - 缺陷预防分析
        - 测试用例优先级排序
        - 回归测试优化
        - 测试策略制定

    V3.1升级点：
        - 增强的风险评估算法
        - 智能测试用例生成建议
        - 工作量自动估算
        - 多维度分析视图
        - 根因分析能力增强
        - 增量覆盖率分析
    """

    description: str = "Uncovered分析Layer - 智能分析未覆盖路径并推荐测试优先级"
    input_type: str = "PipelineContext - 包含覆盖率统计结果和源代码上下文"
    output_type: str = "CoverageGapAnalysis - 覆盖率差距分析结果"

    def __init__(self):
        """初始化未覆盖路径智能分析层"""
        self.analyzer = UncoveredPathAnalyzer()
        self.session_id = ""
        self.source_files: List[str] = []

    def process(self, context: Any) -> CoverageGapAnalysis:
        """处理覆盖率数据，分析未覆盖路径

        Args:
            context: PipelineContext对象，包含覆盖率分析结果

        Returns:
            CoverageGapAnalysis: 覆盖率差距分析结果

        Raises:
            ValueError: 当缺少必要的覆盖率数据时
        """
        self.session_id = context.get('session_id', 'default_session')
        self.source_files = context.get('source_files', [])

        analysis = CoverageGapAnalysis()

        if context.has('coverage_statistics_result'):
            coverage_result = context.get('coverage_statistics_result')
            self._process_coverage_result(coverage_result, analysis, context)

        if context.has('uncovered_lines'):
            uncovered_lines = context.get('uncovered_lines')
            self._process_uncovered_lines(uncovered_lines, analysis, context)

        if context.has('uncovered_branches'):
            uncovered_branches = context.get('uncovered_branches')
            self._process_uncovered_branches(uncovered_branches, analysis, context)

        if context.has('trace_collection_result'):
            trace_result = context.get('trace_collection_result')
            self._supplement_from_trace(trace_result, analysis)

        analysis.test_effort_estimate = self.analyzer.estimate_test_effort(
            analysis.uncovered_items
        )

        analysis.critical_gaps = self._identify_critical_gaps(analysis)

        analysis.recommendations = self._generate_recommendations(analysis)

        analysis.metadata = {
            "session_id": self.session_id,
            "source_files_count": len(self.source_files),
            "analysis_complete": True
        }

        context.set('coverage_gap_analysis', analysis)
        context.set('coverage_gap_analysis_complete', True)
        context.set('critical_uncovered_items', analysis.get_critical_items())

        return analysis

    def _process_coverage_result(self, coverage_result: Any,
                                analysis: CoverageGapAnalysis,
                                context: Any) -> None:
        """处理覆盖率统计结果

        Args:
            coverage_result: 覆盖率统计结果
            analysis: 差距分析对象
            context: 上下文对象
        """
        if hasattr(coverage_result, 'file_details'):
            for file_path, file_detail in coverage_result.file_details.items():
                uncovered_lines = getattr(file_detail, 'uncovered_lines', [])
                function_name = getattr(file_detail, 'function_name', '')

                for line_number in uncovered_lines:
                    source_context = self._get_source_context(file_path, line_number, context)
                    func_context = self._get_function_context(file_path, line_number, context)

                    item = self.analyzer.analyze_uncovered_line(
                        file_path, line_number, source_context, func_context
                    )
                    item.function_name = function_name
                    analysis.add_uncovered_item(item)

    def _process_uncovered_lines(self, uncovered_lines: Any,
                                analysis: CoverageGapAnalysis,
                                context: Any) -> None:
        """处理未覆盖的行信息

        Args:
            uncovered_lines: 未覆盖行数据
            analysis: 差距分析对象
            context: 上下文对象
        """
        if isinstance(uncovered_lines, dict):
            for file_path, lines in uncovered_lines.items():
                for line_number in lines:
                    source_context = self._get_source_context(file_path, line_number, context)
                    func_context = self._get_function_context(file_path, line_number, context)

                    item = self.analyzer.analyze_uncovered_line(
                        file_path, line_number, source_context, func_context
                    )
                    analysis.add_uncovered_item(item)

    def _process_uncovered_branches(self, uncovered_branches: Any,
                                   analysis: CoverageGapAnalysis,
                                   context: Any) -> None:
        """处理未覆盖的分支信息

        Args:
            uncovered_branches: 未覆盖分支数据
            analysis: 差距分析对象
            context: 上下文对象
        """
        if isinstance(uncovered_branches, dict):
            for file_path, branches in uncovered_branches.items():
                for branch_info in branches:
                    branch_id = branch_info.get('branch_id', '')
                    condition = branch_info.get('condition', '')
                    line_number = branch_info.get('line_number', 0)

                    item = self.analyzer.analyze_uncovered_branch(
                        file_path, branch_id, condition, line_number, ""
                    )
                    analysis.add_uncovered_item(item)

    def _supplement_from_trace(self, trace_result: Any,
                             analysis: CoverageGapAnalysis) -> None:
        """从轨迹结果补充分析

        Args:
            trace_result: 轨迹采集结果
            analysis: 差距分析对象
        """
        if hasattr(trace_result, 'function_traces'):
            function_traces = trace_result.function_traces
            for func_name, trace in function_traces.items():
                if trace.call_count == 0 and trace.covered_lines:
                    pass

    def _get_source_context(self, file_path: str, line_number: int,
                          context: Any) -> str:
        """获取源代码上下文

        Args:
            file_path: 文件路径
            line_number: 行号
            context: 上下文对象

        Returns:
            str: 源代码上下文
        """
        if context.has('source_code_cache'):
            cache = context.get('source_code_cache')
            if file_path in cache:
                lines = cache[file_path]
                start = max(0, line_number - 3)
                end = min(len(lines), line_number + 2)
                return '\n'.join(lines[start:end])

        return ""

    def _get_function_context(self, file_path: str, line_number: int,
                            context: Any) -> str:
        """获取函数上下文

        Args:
            file_path: 文件路径
            line_number: 行号
            context: 上下文对象

        Returns:
            str: 函数上下文
        """
        if context.has('function_semantics'):
            semantics = context.get('function_semantics')
            for func in semantics:
                if hasattr(func, 'file_path') and func.file_path == file_path:
                    return getattr(func, 'name', '')

        return ""

    def _identify_critical_gaps(self, analysis: CoverageGapAnalysis) -> List[Dict[str, Any]]:
        """识别关键差距

        Args:
            analysis: 差距分析对象

        Returns:
            List[Dict[str, Any]]: 关键差距列表
        """
        critical_gaps = []
        critical_items = analysis.get_critical_items(10)

        for item in critical_items:
            if item.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
                gap = {
                    "item_id": item.item_id,
                    "type": item.item_type,
                    "file": item.file_path,
                    "line": item.line_number or 0,
                    "risk_level": item.risk_level.name,
                    "reason": item.reason.name,
                    "priority_score": item.get_priority_score(),
                    "suggestion": item.test_suggestions[0] if item.test_suggestions else ""
                }
                critical_gaps.append(gap)

        return critical_gaps

    def _generate_recommendations(self, analysis: CoverageGapAnalysis) -> List[str]:
        """生成改进建议

        Args:
            analysis: 差距分析对象

        Returns:
            List[str]: 建议列表
        """
        recommendations = []

        exception_items = analysis.get_items_by_reason(UncoveredReason.EXCEPTION_PATH_NOT_TESTED)
        if exception_items:
            recommendations.append(
                f"发现{len(exception_items)}个未测试的异常处理路径，"
                f"建议为这些路径编写专门的异常测试用例"
            )

        boundary_items = analysis.get_items_by_reason(UncoveredReason.BOUNDARY_CONDITION_NOT_COVERED)
        if boundary_items:
            recommendations.append(
                f"发现{len(boundary_items)}个未覆盖的边界条件，"
                f"建议增加边界值测试用例"
            )

        high_priority = [i for i in analysis.uncovered_items
                        if i.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]]
        if high_priority:
            recommendations.append(
                f"有{len(high_priority)}个高风险未覆盖项，建议优先处理"
            )

        effort = analysis.test_effort_estimate
        if effort:
            recommendations.append(
                f"预计需要约{effort.get('total_effort_hours', 0)}小时，"
                f"编写约{effort.get('estimated_test_cases', 0)}个测试用例"
            )

        if analysis.critical_gaps:
            recommendations.append(
                f"识别出{len(analysis.critical_gaps)}个关键覆盖率差距，"
                f"建议制定专项测试计划"
            )

        return recommendations

    def get_prioritized_items(self, analysis: CoverageGapAnalysis,
                            top_n: int = 20) -> List[UncoveredItem]:
        """获取优先级排序的未覆盖项

        Args:
            analysis: 差距分析对象
            top_n: 返回数量

        Returns:
            List[UncoveredItem]: 优先级排序的未覆盖项
        """
        return analysis.get_sorted_by_priority()[:top_n]

    def get_items_by_category(self, analysis: CoverageGapAnalysis,
                            category: str) -> Dict[str, List[UncoveredItem]]:
        """按类别获取未覆盖项

        Args:
            analysis: 差距分析对象
            category: 分类类型（file, function, reason）

        Returns:
            Dict[str, List[UncoveredItem]]: 分类后的未覆盖项
        """
        if category == 'file':
            return analysis.uncovered_by_file
        elif category == 'function':
            return analysis.uncovered_by_function
        elif category == 'reason':
            return {r.name: items for r, items in analysis.uncovered_by_reason.items()}
        else:
            return {}

    def export_analysis_report(self, analysis: CoverageGapAnalysis,
                             format: str = "dict") -> Any:
        """导出分析报告

        Args:
            analysis: 差距分析对象
            format: 输出格式

        Returns:
            Any: 报告数据
        """
        if format == "dict":
            report = analysis.to_dict()
            report["prioritized_items"] = [
                item.to_dict() for item in analysis.get_sorted_by_priority()[:20]
            ]
            return report
        elif format == "summary":
            return {
                "total_uncovered": len(analysis.uncovered_items),
                "critical_gaps": len(analysis.critical_gaps),
                "estimated_hours": analysis.test_effort_estimate.get("total_effort_hours", 0),
                "recommendations": analysis.recommendations
            }
        else:
            return analysis.to_dict()
