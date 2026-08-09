"""
Layer 23: CoverageMatchLayer - 覆盖规则预匹配层【V3.1升级】

本层负责将覆盖规则与代码结构进行预匹配，为后续的测试用例生成和路径分析提供覆盖指导。
V3.1升级增强了多维度覆盖规则匹配和智能覆盖缺口分析能力。
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import defaultdict


class CoverageCriteria(Enum):
    """覆盖标准枚举"""
    STATEMENT = auto()
    BRANCH = auto()
    CONDITION = auto()
    DECISION = auto()
    PATH = auto()
    MC_DC = auto()
    FUNCTION = auto()
    CALL = auto()
    LOOP = auto()
    LINE = auto()
    MULTIPLE_CONDITION = auto()


class MatchStatus(Enum):
    """匹配状态枚举"""
    MATCHED = auto()
    PARTIAL = auto()
    UNMATCHED = auto()
    NOT_APPLICABLE = auto()


class CoverageType(Enum):
    """覆盖类型枚举"""
    STATEMENT_COVERAGE = auto()
    BRANCH_COVERAGE = auto()
    PATH_COVERAGE = auto()
    CONDITION_COVERAGE = auto()
    FUNCTION_COVERAGE = auto()
    LINE_COVERAGE = auto()
    ENTRY_EXIT_COVERAGE = auto()


@dataclass
class CoverageRequirement:
    """覆盖需求

    Attributes:
        requirement_id: 需求标识符
        criteria: 覆盖标准
        target: 目标（节点ID、边ID、路径等）
        priority: 优先级
        complexity: 复杂度
        description: 描述
        test_hints: 测试提示
        constraints: 约束条件
        metadata: 其他元信息
    """
    requirement_id: str
    criteria: CoverageCriteria
    target: str
    priority: int = 5
    complexity: int = 1
    description: str = ""
    test_hints: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "requirement_id": self.requirement_id,
            "criteria": self.criteria.name,
            "target": self.target,
            "priority": self.priority,
            "complexity": self.complexity,
            "description": self.description,
            "test_hints": self.test_hints,
            "constraints": self.constraints,
            "metadata": self.metadata
        }


@dataclass
class CoverageMatch:
    """覆盖匹配结果

    Attributes:
        requirement: 覆盖需求
        match_status: 匹配状态
        matched_elements: 匹配的元素列表
        test_cases_needed: 需要的测试用例数
        coverage_points: 覆盖点列表
        prerequisites: 前置条件
        potential_test_values: 潜在的测试值
        risk_level: 风险等级
        match_confidence: 匹配置信度
        suggestions: 建议
    """
    requirement: CoverageRequirement
    match_status: MatchStatus
    matched_elements: List[str] = field(default_factory=list)
    test_cases_needed: int = 1
    coverage_points: List[Dict[str, Any]] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    potential_test_values: List[Any] = field(default_factory=list)
    risk_level: str = "low"
    match_confidence: float = 0.0
    suggestions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "requirement": self.requirement.to_dict(),
            "match_status": self.match_status.name,
            "matched_elements": self.matched_elements,
            "test_cases_needed": self.test_cases_needed,
            "coverage_points": self.coverage_points,
            "prerequisites": self.prerequisites,
            "potential_test_values": [str(v) for v in self.potential_test_values],
            "risk_level": self.risk_level,
            "match_confidence": self.match_confidence,
            "suggestions": self.suggestions
        }


@dataclass
class CoverageGap:
    """覆盖缺口

    Attributes:
        gap_id: 缺口标识符
        gap_type: 缺口类型
        uncovered_elements: 未覆盖的元素
        reason: 原因分析
        difficulty: 难度评估
        suggested_approach: 建议方法
        estimated_effort: 预计工作量
        priority: 优先级
        related_requirements: 相关需求
    """
    gap_id: str
    gap_type: str
    uncovered_elements: List[str] = field(default_factory=list)
    reason: str = ""
    difficulty: str = "medium"
    suggested_approach: str = ""
    estimated_effort: int = 1
    priority: int = 5
    related_requirements: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "gap_id": self.gap_id,
            "gap_type": self.gap_type,
            "uncovered_elements": self.uncovered_elements,
            "reason": self.reason,
            "difficulty": self.difficulty,
            "suggested_approach": self.suggested_approach,
            "estimated_effort": self.estimated_effort,
            "priority": self.priority,
            "related_requirements": self.related_requirements
        }


@dataclass
class CoveragePlan:
    """覆盖计划

    Attributes:
        plan_id: 计划标识符
        total_requirements: 总需求数
        matched_requirements: 已匹配需求数
        partial_requirements: 部分匹配需求数
        unmatched_requirements: 未匹配需求数
        coverage_matches: 匹配结果列表
        coverage_gaps: 覆盖缺口列表
        coverage_targets: 覆盖目标
        prioritized_tests: 优先级排序的测试
        metadata: 元信息
    """
    plan_id: str
    total_requirements: int = 0
    matched_requirements: int = 0
    partial_requirements: int = 0
    unmatched_requirements: int = 0
    coverage_matches: List[CoverageMatch] = field(default_factory=list)
    coverage_gaps: List[CoverageGap] = field(default_factory=list)
    coverage_targets: Dict[str, int] = field(default_factory=dict)
    prioritized_tests: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "plan_id": self.plan_id,
            "total_requirements": self.total_requirements,
            "matched_requirements": self.matched_requirements,
            "partial_requirements": self.partial_requirements,
            "unmatched_requirements": self.unmatched_requirements,
            "coverage_matches": [m.to_dict() for m in self.coverage_matches],
            "coverage_gaps": [g.to_dict() for g in self.coverage_gaps],
            "coverage_targets": self.coverage_targets,
            "prioritized_tests": self.prioritized_tests,
            "metadata": self.metadata
        }

    def get_coverage_percentage(self) -> float:
        """获取覆盖率

        Returns:
            float: 覆盖率（0-100）
        """
        if self.total_requirements == 0:
            return 0.0

        return (self.matched_requirements / self.total_requirements) * 100


class CoverageMatchLayer:
    """覆盖规则预匹配层【V3.1升级】

    功能描述：
        - 将覆盖规则与代码结构进行智能匹配
        - 生成基于覆盖标准的测试需求
        - 分析覆盖缺口和未覆盖区域
        - 评估覆盖实现的难度和风险
        - 提供测试用例生成指导
        - 支持多维度覆盖标准匹配
        - 提供覆盖优先级建议

    输入类型：
        - 控制流图（ControlFlowGraph）
        - 依赖图（DependencyGraph）
        - 函数切片列表
        - 预设的覆盖规则

    输出类型：
        - CoveragePlan: 覆盖计划
        - List[CoverageMatch]: 匹配结果列表
        - List[CoverageGap]: 覆盖缺口列表

    使用场景：
        - 为测试用例生成提供覆盖指导
        - 识别测试覆盖盲点
        - 评估测试充分性
        - 优化测试执行策略
        - 支持覆盖率驱动的测试设计

    V3.1升级点：
        - 增强多维度覆盖规则匹配算法
        - 提供智能的覆盖缺口分析
        - 支持条件组合和判定覆盖的智能匹配
        - 增加对复杂控制流的覆盖规则生成
        - 提供更精确的测试用例数量估算
    """

    description: str = "覆盖规则预匹配层【V3.1升级】- 匹配覆盖规则与代码结构"
    input_type: str = "ControlFlowGraph、DependencyGraph和函数切片"
    output_type: str = "CoveragePlan和List[CoverageMatch]"

    def __init__(self):
        """初始化覆盖匹配层"""
        self.cfg_graphs = {}
        self.dependency_graph = None
        self.function_slices = []
        self.function_semantics = []
        self.coverage_requirements = []
        self.coverage_matches = []
        self.coverage_gaps = []
        self.coverage_plan = None

    def set_coverage_criteria(self, criteria: List[CoverageCriteria]):
        """设置覆盖标准

        Args:
            criteria: 覆盖标准列表
        """
        self.coverage_criteria = criteria

    def process(self, context) -> Tuple[CoveragePlan, List[CoverageMatch]]:
        """处理CFG和依赖图，生成覆盖匹配计划

        Args:
            context: PipelineContext对象，包含CFG、依赖图和函数信息

        Returns:
            Tuple[CoveragePlan, List[CoverageMatch]]: (覆盖计划, 匹配结果列表)

        Raises:
            ValueError: 当输入数据不足时
        """
        if not context.has('cfg_graphs'):
            if not context.has('function_slices'):
                raise ValueError("CoverageMatchLayer: 缺少CFG或函数切片")

        if context.has('cfg_graphs'):
            self.cfg_graphs = context.get('cfg_graphs')

        if context.has('dependency_graph'):
            self.dependency_graph = context.get('dependency_graph')

        if context.has('function_slices'):
            self.function_slices = context.get('function_slices')

        if context.has('function_semantics'):
            self.function_semantics = context.get('function_semantics')

        self.coverage_requirements = self._generate_coverage_requirements()

        self.coverage_matches = self._match_requirements_with_structure()

        self.coverage_gaps = self._analyze_coverage_gaps()

        self.coverage_plan = self._create_coverage_plan()

        context.set('coverage_requirements', self.coverage_requirements)
        context.set('coverage_matches', self.coverage_matches)
        context.set('coverage_gaps', self.coverage_gaps)
        context.set('coverage_plan', self.coverage_plan)
        context.set('coverage_match_complete', True)
        context.set('coverage_statistics', self._get_statistics())

        return self.coverage_plan, self.coverage_matches

    def _generate_coverage_requirements(self) -> List[CoverageRequirement]:
        """生成覆盖需求

        Returns:
            List[CoverageRequirement]: 覆盖需求列表
        """
        requirements = []

        for func_name, cfg in self.cfg_graphs.items():
            requirements.extend(self._generate_for_cfg(cfg, func_name))

        for slice_item in self.function_slices:
            func_name = getattr(slice_item, 'qualified_name', '') or getattr(slice_item, 'name', '')
            requirements.extend(self._generate_for_function(slice_item, func_name))

        return requirements

    def _generate_for_cfg(self, cfg, func_name: str) -> List[CoverageRequirement]:
        """为CFG生成覆盖需求

        Args:
            cfg: 控制流图
            func_name: 函数名

        Returns:
            List[CoverageRequirement]: 覆盖需求列表
        """
        requirements = []

        for node_id, node in cfg.nodes.items():
            if node.node_type.value >= 3:
                req = CoverageRequirement(
                    requirement_id=f"{func_name}_stmt_{node_id}",
                    criteria=CoverageCriteria.STATEMENT,
                    target=node_id,
                    priority=3,
                    complexity=1,
                    description=f"语句覆盖: {node.label}",
                    test_hints=[f"执行到行{node.line_start}-{node.line_end}"]
                )
                requirements.append(req)

            if node.node_type.value == 4:
                for successor_id in node.successors:
                    edge = self._find_edge(cfg, node_id, successor_id)
                    if edge:
                        edge_type_name = edge.edge_type.name

                        req = CoverageRequirement(
                            requirement_id=f"{func_name}_branch_{node_id}_{successor_id}",
                            criteria=CoverageCriteria.BRANCH,
                            target=f"{node_id}->{successor_id}",
                            priority=4,
                            complexity=2,
                            description=f"分支覆盖: {edge_type_name}",
                            test_hints=[
                                f"执行条件{node.condition}",
                                f"选择{edge_type_name}分支"
                            ]
                        )
                        requirements.append(req)

        for loop in cfg.loops:
            req = CoverageRequirement(
                requirement_id=f"{func_name}_loop_{loop.get('header', 'unknown')}",
                criteria=CoverageCriteria.LOOP,
                target=loop.get('header', ''),
                priority=3,
                complexity=2,
                description=f"循环覆盖: 0次、1次、多次迭代",
                test_hints=[
                    "测试循环不执行（初始条件不满足）",
                    "测试循环执行一次",
                    "测试循环执行多次"
                ]
            )
            requirements.append(req)

        return requirements

    def _generate_for_function(self, func_slice, func_name: str) -> List[CoverageRequirement]:
        """为函数生成覆盖需求

        Args:
            func_slice: 函数切片
            func_name: 函数名

        Returns:
            List[CoverageRequirement]: 覆盖需求列表
        """
        requirements = []

        req = CoverageRequirement(
            requirement_id=f"{func_name}_function",
            criteria=CoverageCriteria.FUNCTION,
            target=func_name,
            priority=5,
            complexity=1,
            description=f"函数覆盖: {func_name}",
            test_hints=[
                "调用该函数至少一次",
                "验证函数执行完成"
            ]
        )
        requirements.append(req)

        parameters = getattr(func_slice, 'parameters', [])
        for i, param in enumerate(parameters):
            param_name = param.get('name', f'param_{i}')
            constraints = self._infer_param_constraints(param)

            if constraints:
                req = CoverageRequirement(
                    requirement_id=f"{func_name}_param_{param_name}",
                    criteria=CoverageCriteria.CONDITION,
                    target=f"{func_name}:{param_name}",
                    priority=3,
                    complexity=2,
                    description=f"参数条件覆盖: {param_name}",
                    test_hints=[f"测试约束: {c}" for c in constraints]
                )
                requirements.append(req)

        calls = getattr(func_slice, 'calls', [])
        for call in calls:
            target_func = call.get('name', '')
            if target_func:
                req = CoverageRequirement(
                    requirement_id=f"{func_name}_call_{target_func}",
                    criteria=CoverageCriteria.CALL,
                    target=f"{func_name}->{target_func}",
                    priority=4,
                    complexity=1,
                    description=f"调用覆盖: {target_func}",
                    test_hints=[f"确保{target_func}被调用"]
                )
                requirements.append(req)

        return requirements

    def _infer_param_constraints(self, param: Dict[str, Any]) -> List[str]:
        """推断参数约束

        Args:
            param: 参数信息

        Returns:
            List[str]: 约束列表
        """
        constraints = []
        param_name = param.get('name', '').lower()
        data_type = str(param.get('annotation', '')).lower()

        if 'id' in param_name:
            constraints.append("有效的标识符值")

        if 'name' in param_name:
            constraints.append("非空字符串")

        if 'count' in param_name or 'size' in param_name:
            constraints.append("非负整数")

        if 'rate' in param_name or 'price' in param_name:
            constraints.append("正数")

        if 'email' in param_name:
            constraints.append("有效的邮箱格式")

        if 'url' in param_name or 'uri' in param_name:
            constraints.append("有效的URL格式")

        if 'date' in param_name:
            constraints.append("有效的日期格式")

        if data_type == 'bool':
            constraints.append("True和False")

        if data_type in ('int', 'float'):
            constraints.append("正常值、边界值")

        return constraints

    def _find_edge(self, cfg, source: str, target: str):
        """查找边

        Args:
            cfg: 控制流图
            source: 源节点
            target: 目标节点

        Returns:
            找到的边
        """
        for edge in cfg.edges:
            if edge.source == source and edge.target == target:
                return edge
        return None

    def _match_requirements_with_structure(self) -> List[CoverageMatch]:
        """将需求与结构匹配

        Returns:
            List[CoverageMatch]: 匹配结果列表
        """
        matches = []

        for requirement in self.coverage_requirements:
            match = self._match_single_requirement(requirement)
            matches.append(match)

        return matches

    def _match_single_requirement(self, requirement: CoverageRequirement) -> CoverageMatch:
        """匹配单个需求

        Args:
            requirement: 覆盖需求

        Returns:
            CoverageMatch: 匹配结果
        """
        match = CoverageMatch(
            requirement=requirement,
            match_status=MatchStatus.UNMATCHED,
            matched_elements=[],
            test_cases_needed=1,
            risk_level="high",
            match_confidence=0.0
        )

        if requirement.criteria == CoverageCriteria.STATEMENT:
            match = self._match_statement_coverage(requirement)
        elif requirement.criteria == CoverageCriteria.BRANCH:
            match = self._match_branch_coverage(requirement)
        elif requirement.criteria == CoverageCriteria.FUNCTION:
            match = self._match_function_coverage(requirement)
        elif requirement.criteria == CoverageCriteria.CALL:
            match = self._match_call_coverage(requirement)
        elif requirement.criteria == CoverageCriteria.LOOP:
            match = self._match_loop_coverage(requirement)
        elif requirement.criteria == CoverageCriteria.CONDITION:
            match = self._match_condition_coverage(requirement)

        return match

    def _match_statement_coverage(self, requirement: CoverageRequirement) -> CoverageMatch:
        """匹配语句覆盖

        Args:
            requirement: 覆盖需求

        Returns:
            CoverageMatch: 匹配结果
        """
        match = CoverageMatch(
            requirement=requirement,
            match_status=MatchStatus.MATCHED,
            matched_elements=[requirement.target],
            test_cases_needed=1,
            risk_level="low",
            match_confidence=0.9,
            suggestions=["简单执行即可覆盖"]
        )

        for func_name, cfg in self.cfg_graphs.items():
            if requirement.target in cfg.nodes:
                node = cfg.nodes[requirement.target]
                if node.statements:
                    match.coverage_points = [{
                        'type': 'statement',
                        'location': f"line {node.line_start}-{node.line_end}",
                        'code': node.statements[0] if node.statements else ''
                    }]

        return match

    def _match_branch_coverage(self, requirement: CoverageRequirement) -> CoverageMatch:
        """匹配分支覆盖

        Args:
            requirement: 覆盖需求

        Returns:
            CoverageMatch: 匹配结果
        """
        match = CoverageMatch(
            requirement=requirement,
            match_status=MatchStatus.MATCHED,
            matched_elements=[requirement.target],
            test_cases_needed=2,
            risk_level="medium",
            match_confidence=0.8,
            suggestions=["需要True和False两个测试用例"]
        )

        target_parts = requirement.target.split('->')
        if len(target_parts) == 2:
            source_id, target_id = target_parts

            for func_name, cfg in self.cfg_graphs.items():
                if source_id in cfg.nodes:
                    source_node = cfg.nodes[source_id]
                    if source_node.condition:
                        match.potential_test_values = [
                            {'condition': source_node.condition, 'value': True},
                            {'condition': source_node.condition, 'value': False}
                        ]

                    other_successors = [sid for sid in source_node.successors if sid != target_id]
                    if other_successors:
                        match.prerequisites = [other_successors[0]]
                        match.match_status = MatchStatus.PARTIAL

        return match

    def _match_function_coverage(self, requirement: CoverageRequirement) -> CoverageMatch:
        """匹配函数覆盖

        Args:
            requirement: 覆盖需求

        Returns:
            CoverageMatch: 匹配结果
        """
        match = CoverageMatch(
            requirement=requirement,
            match_status=MatchStatus.MATCHED,
            matched_elements=[requirement.target],
            test_cases_needed=1,
            risk_level="low",
            match_confidence=1.0,
            suggestions=["直接调用函数即可"]
        )

        for slice_item in self.function_slices:
            func_name = getattr(slice_item, 'qualified_name', '') or getattr(slice_item, 'name', '')
            if func_name == requirement.target:
                params = getattr(slice_item, 'parameters', [])
                if params:
                    match.test_hints = [f"提供参数: {p.get('name', '')}" for p in params]

                if hasattr(slice_item, 'is_async') and getattr(slice_item, 'is_async', False):
                    match.suggestions.append("异步函数需要使用await")

                side_effects = getattr(slice_item, 'calls', [])
                if side_effects:
                    match.prerequisites = [c.get('name', '') for c in side_effects[:3]]

        return match

    def _match_call_coverage(self, requirement: CoverageRequirement) -> CoverageMatch:
        """匹配调用覆盖

        Args:
            requirement: 覆盖需求

        Returns:
            CoverageMatch: 匹配结果
        """
        match = CoverageMatch(
            requirement=requirement,
            match_status=MatchStatus.MATCHED,
            matched_elements=[requirement.target],
            test_cases_needed=1,
            risk_level="medium",
            match_confidence=0.85,
            suggestions=["需要确保被调用函数可访问"]
        )

        target_parts = requirement.target.split('->')
        if len(target_parts) == 2:
            caller, callee = target_parts

            if self.dependency_graph:
                deps = self.dependency_graph.get_dependencies(caller)
                if callee not in deps:
                    match.match_status = MatchStatus.PARTIAL
                    match.risk_level = "high"
                    match.suggestions.append("警告: 调用关系可能不可达")

        return match

    def _match_loop_coverage(self, requirement: CoverageRequirement) -> CoverageMatch:
        """匹配循环覆盖

        Args:
            requirement: 覆盖需求

        Returns:
            CoverageMatch: 匹配结果
        """
        match = CoverageMatch(
            requirement=requirement,
            match_status=MatchStatus.MATCHED,
            matched_elements=[requirement.target],
            test_cases_needed=3,
            risk_level="medium",
            match_confidence=0.75,
            suggestions=[
                "测试用例1: 循环不执行",
                "测试用例2: 循环执行一次",
                "测试用例3: 循环执行多次"
            ]
        )

        for func_name, cfg in self.cfg_graphs.items():
            if requirement.target in cfg.nodes:
                node = cfg.nodes[requirement.target]
                if node.condition:
                    match.potential_test_values = [
                        {'type': 'zero_iteration', 'condition': f"NOT {node.condition}"},
                        {'type': 'one_iteration', 'condition': f"{node.condition} 且 满足一次"},
                        {'type': 'multiple_iterations', 'condition': f"{node.condition} 持续满足"}
                    ]

        return match

    def _match_condition_coverage(self, requirement: CoverageRequirement) -> CoverageMatch:
        """匹配条件覆盖

        Args:
            requirement: 覆盖需求

        Returns:
            CoverageMatch: 匹配结果
        """
        match = CoverageMatch(
            requirement=requirement,
            match_status=MatchStatus.MATCHED,
            matched_elements=[requirement.target],
            test_cases_needed=2,
            risk_level="medium",
            match_confidence=0.7,
            suggestions=["需要测试参数的不同约束条件"]
        )

        target_parts = requirement.target.split(':')
        if len(target_parts) == 2:
            func_name, param_name = target_parts

            for slice_item in self.function_slices:
                slice_func_name = getattr(slice_item, 'qualified_name', '') or getattr(slice_item, 'name', '')
                if slice_func_name == func_name:
                    params = getattr(slice_item, 'parameters', [])
                    for param in params:
                        if param.get('name', '') == param_name:
                            constraints = self._infer_param_constraints(param)
                            match.test_hints = [f"测试约束: {c}" for c in constraints]

        return match

    def _analyze_coverage_gaps(self) -> List[CoverageGap]:
        """分析覆盖缺口

        Returns:
            List[CoverageGap]: 覆盖缺口列表
        """
        gaps = []

        gap_id_counter = 0

        for match in self.coverage_matches:
            if match.match_status == MatchStatus.UNMATCHED:
                gap_id_counter += 1
                gap = CoverageGap(
                    gap_id=f"gap_{gap_id_counter}",
                    gap_type=match.requirement.criteria.name,
                    uncovered_elements=[match.requirement.target],
                    reason=f"未能在代码结构中找到对应的{self._get_criteria_description(match.requirement.criteria)}目标",
                    difficulty="high" if match.risk_level == "high" else "medium",
                    suggested_approach=self._suggest_gap_approach(match),
                    estimated_effort=match.test_cases_needed * 2,
                    priority=10 - match.requirement.priority,
                    related_requirements=[match.requirement.requirement_id]
                )
                gaps.append(gap)

            elif match.match_status == MatchStatus.PARTIAL:
                gap_id_counter += 1
                gap = CoverageGap(
                    gap_id=f"gap_{gap_id_counter}",
                    gap_type=f"partial_{match.requirement.criteria.name}",
                    uncovered_elements=match.prerequisites,
                    reason="部分前置条件未满足",
                    difficulty="medium",
                    suggested_approach="需要先满足前置条件",
                    estimated_effort=1,
                    priority=8 - match.requirement.priority,
                    related_requirements=[match.requirement.requirement_id]
                )
                gaps.append(gap)

        return gaps

    def _get_criteria_description(self, criteria: CoverageCriteria) -> str:
        """获取覆盖标准描述

        Args:
            criteria: 覆盖标准

        Returns:
            str: 描述
        """
        descriptions = {
            CoverageCriteria.STATEMENT: "语句",
            CoverageCriteria.BRANCH: "分支",
            CoverageCriteria.CONDITION: "条件",
            CoverageCriteria.DECISION: "判定",
            CoverageCriteria.PATH: "路径",
            CoverageCriteria.MC_DC: "修正条件/判定覆盖",
            CoverageCriteria.FUNCTION: "函数",
            CoverageCriteria.CALL: "调用",
            CoverageCriteria.LOOP: "循环",
            CoverageCriteria.LINE: "行",
            CoverageCriteria.MULTIPLE_CONDITION: "多条件"
        }
        return descriptions.get(criteria, "未知")

    def _suggest_gap_approach(self, match: CoverageMatch) -> str:
        """建议缺口处理方法

        Args:
            match: 匹配结果

        Returns:
            str: 建议方法
        """
        criteria = match.requirement.criteria

        approaches = {
            CoverageCriteria.STATEMENT: "添加更多测试用例确保所有语句被执行",
            CoverageCriteria.BRANCH: "增加边界条件和异常情况的测试用例",
            CoverageCriteria.FUNCTION: "确保函数被正确调用，检查参数传递",
            CoverageCriteria.CALL: "检查函数间的调用关系，确保依赖可用",
            CoverageCriteria.LOOP: "设计测试覆盖循环的0次、1次、多次迭代",
            CoverageCriteria.CONDITION: "为参数设计不同约束条件的测试用例"
        }

        return approaches.get(criteria, "需要重新分析代码结构和测试需求")

    def _create_coverage_plan(self) -> CoveragePlan:
        """创建覆盖计划

        Returns:
            CoveragePlan: 覆盖计划
        """
        plan = CoveragePlan(
            plan_id="coverage_plan_1",
            total_requirements=len(self.coverage_requirements),
            matched_requirements=0,
            partial_requirements=0,
            unmatched_requirements=0,
            coverage_matches=self.coverage_matches,
            coverage_gaps=self.coverage_gaps
        )

        for match in self.coverage_matches:
            if match.match_status == MatchStatus.MATCHED:
                plan.matched_requirements += 1
            elif match.match_status == MatchStatus.PARTIAL:
                plan.partial_requirements += 1
            elif match.match_status == MatchStatus.UNMATCHED:
                plan.unmatched_requirements += 1

        coverage_targets = {
            'statement': sum(1 for m in self.coverage_matches if m.requirement.criteria == CoverageCriteria.STATEMENT),
            'branch': sum(1 for m in self.coverage_matches if m.requirement.criteria == CoverageCriteria.BRANCH),
            'function': sum(1 for m in self.coverage_matches if m.requirement.criteria == CoverageCriteria.FUNCTION),
            'call': sum(1 for m in self.coverage_matches if m.requirement.criteria == CoverageCriteria.CALL),
            'loop': sum(1 for m in self.coverage_matches if m.requirement.criteria == CoverageCriteria.LOOP),
            'condition': sum(1 for m in self.coverage_matches if m.requirement.criteria == CoverageCriteria.CONDITION)
        }

        plan.coverage_targets = coverage_targets

        plan.prioritized_tests = self._prioritize_tests()

        plan.metadata = {
            'coverage_percentage': plan.get_coverage_percentage(),
            'total_test_cases_needed': sum(m.test_cases_needed for m in self.coverage_matches),
            'high_risk_count': sum(1 for m in self.coverage_matches if m.risk_level == "high"),
            'medium_risk_count': sum(1 for m in self.coverage_matches if m.risk_level == "medium"),
            'low_risk_count': sum(1 for m in self.coverage_matches if m.risk_level == "low")
        }

        return plan

    def _prioritize_tests(self) -> List[Dict[str, Any]]:
        """优先级排序测试

        Returns:
            List[Dict[str, Any]]: 排序后的测试列表
        """
        prioritized = []

        for match in self.coverage_matches:
            test = {
                'requirement_id': match.requirement.requirement_id,
                'criteria': match.requirement.criteria.name,
                'priority': match.requirement.priority,
                'test_cases_needed': match.test_cases_needed,
                'risk_level': match.risk_level,
                'confidence': match.match_confidence,
                'hints': match.requirement.test_hints + match.suggestions
            }

            priority_score = (match.requirement.priority * 10 +
                            match.match_confidence * 5 -
                            match.test_cases_needed * 2)

            if match.risk_level == "high":
                priority_score += 20
            elif match.risk_level == "medium":
                priority_score += 10

            test['priority_score'] = priority_score
            prioritized.append(test)

        prioritized.sort(key=lambda x: x['priority_score'], reverse=True)

        return prioritized

    def _get_statistics(self) -> Dict[str, Any]:
        """获取统计信息

        Returns:
            Dict[str, Any]: 统计信息
        """
        if not self.coverage_plan:
            return {}

        return {
            'total_requirements': self.coverage_plan.total_requirements,
            'matched': self.coverage_plan.matched_requirements,
            'partial': self.coverage_plan.partial_requirements,
            'unmatched': self.coverage_plan.unmatched_requirements,
            'coverage_percentage': self.coverage_plan.get_coverage_percentage(),
            'total_test_cases': sum(m.test_cases_needed for m in self.coverage_matches),
            'gap_count': len(self.coverage_gaps),
            'by_criteria': self._count_by_criteria(),
            'risk_distribution': self._get_risk_distribution()
        }

    def _count_by_criteria(self) -> Dict[str, int]:
        """按覆盖标准统计

        Returns:
            Dict[str, int]: 各标准计数
        """
        counts = defaultdict(int)

        for match in self.coverage_matches:
            criteria_name = match.requirement.criteria.name
            counts[criteria_name] += 1

        return dict(counts)

    def _get_risk_distribution(self) -> Dict[str, int]:
        """获取风险分布

        Returns:
            Dict[str, int]: 风险分布
        """
        distribution = {'high': 0, 'medium': 0, 'low': 0}

        for match in self.coverage_matches:
            if match.risk_level in distribution:
                distribution[match.risk_level] += 1

        return distribution

    def get_matches_by_criteria(self, criteria: CoverageCriteria) -> List[CoverageMatch]:
        """获取指定标准的匹配

        Args:
            criteria: 覆盖标准

        Returns:
            List[CoverageMatch]: 匹配列表
        """
        return [m for m in self.coverage_matches if m.requirement.criteria == criteria]

    def get_matches_by_risk(self, risk_level: str) -> List[CoverageMatch]:
        """获取指定风险的匹配

        Args:
            risk_level: 风险等级

        Returns:
            List[CoverageMatch]: 匹配列表
        """
        return [m for m in self.coverage_matches if m.risk_level == risk_level]

    def suggest_next_tests(self, count: int = 5) -> List[Dict[str, Any]]:
        """建议下一步测试

        Args:
            count: 建议数量

        Returns:
            List[Dict[str, Any]]: 测试建议列表
        """
        suggestions = []

        high_risk_unmatched = [m for m in self.coverage_matches
                            if m.risk_level == "high" and m.match_status != MatchStatus.MATCHED]

        for match in high_risk_unmatched[:count]:
            suggestion = {
                'requirement_id': match.requirement.requirement_id,
                'reason': f"高风险未匹配: {match.requirement.description}",
                'approach': self._suggest_test_approach(match),
                'estimated_cases': match.test_cases_needed
            }
            suggestions.append(suggestion)

        unmatched_conditions = [m for m in self.coverage_matches
                              if m.match_status == MatchStatus.UNMATCHED and
                              m.requirement.criteria == CoverageCriteria.CONDITION]

        for match in unmatched_conditions[:max(0, count - len(suggestions))]:
            suggestion = {
                'requirement_id': match.requirement.requirement_id,
                'reason': f"条件未匹配: {match.requirement.description}",
                'approach': self._suggest_test_approach(match),
                'estimated_cases': match.test_cases_needed
            }
            suggestions.append(suggestion)

        return suggestions[:count]

    def _suggest_test_approach(self, match: CoverageMatch) -> str:
        """建议测试方法

        Args:
            match: 匹配结果

        Returns:
            str: 测试方法建议
        """
        criteria = match.requirement.criteria

        approaches = {
            CoverageCriteria.STATEMENT: "直接执行相关代码路径",
            CoverageCriteria.BRANCH: "设计True/False两个测试用例",
            CoverageCriteria.FUNCTION: "调用函数并验证返回值",
            CoverageCriteria.CALL: "确保被调用函数可用并正确调用",
            CoverageCriteria.LOOP: "设计0次、1次、多次迭代的测试用例",
            CoverageCriteria.CONDITION: "为参数设计满足不同约束的测试用例"
        }

        return approaches.get(criteria, "需要根据具体情况设计测试用例")

    def export_coverage_matrix(self) -> Dict[str, Any]:
        """导出覆盖矩阵

        Returns:
            Dict[str, Any]: 覆盖矩阵
        """
        matrix = {
            'functions': {},
            'criteria': {},
            'matrix': []
        }

        for match in self.coverage_matches:
            func_name = match.requirement.target.split('_')[0]
            criteria = match.requirement.criteria.name

            if func_name not in matrix['functions']:
                matrix['functions'][func_name] = {
                    'total': 0,
                    'covered': 0,
                    'by_criteria': {}
                }

            matrix['functions'][func_name]['total'] += 1

            if match.match_status == MatchStatus.MATCHED:
                matrix['functions'][func_name]['covered'] += 1

            if criteria not in matrix['functions'][func_name]['by_criteria']:
                matrix['functions'][func_name]['by_criteria'][criteria] = {
                    'total': 0,
                    'covered': 0
                }

            matrix['functions'][func_name]['by_criteria'][criteria]['total'] += 1

            if match.match_status == MatchStatus.MATCHED:
                matrix['functions'][func_name]['by_criteria'][criteria]['covered'] += 1

        matrix['criteria'] = self._count_by_criteria()

        return matrix
