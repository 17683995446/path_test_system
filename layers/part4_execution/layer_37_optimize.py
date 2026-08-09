"""
Layer 37: Test Case Optimize Layer (测试用例优化层)

该层负责根据质量评估结果对测试用例进行优化，包括代码重构、
性能优化、冗余消除、断言增强等，提高测试用例的整体质量。
"""

from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum


class OptimizationStrategy(Enum):
    """优化策略"""
    CODE_REFACTOR = "code_refactor"
    ASSERTION_ENHANCE = "assertion_enhance"
    DUPLICATE_REMOVE = "duplicate_remove"
    PERFORMANCE = "performance"
    READABILITY = "readability"
    COVERAGE_BOOST = "coverage_boost"


class OptimizationPriority(Enum):
    """优化优先级"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class OptimizationAction:
    """优化操作"""
    action_id: str
    action_type: OptimizationStrategy
    target_case_id: str
    priority: OptimizationPriority
    description: str
    original_code: str
    optimized_code: str
    estimated_improvement: float
    auto_applicable: bool = True


@dataclass
class OptimizationResult:
    """优化结果"""
    optimized_cases: List[Any] = field(default_factory=list)
    optimization_actions: List[OptimizationAction] = field(default_factory=list)
    total_cases_optimized: int = 0
    total_improvement_score: float = 0.0
    strategies_applied: List[OptimizationStrategy] = field(default_factory=list)
    removed_duplicates: int = 0
    enhanced_assertions: int = 0
    performance_gains_ms: float = 0.0


@dataclass
class OptimizationPlan:
    """优化计划"""
    plan_id: str
    target_cases: List[str]
    strategies: List[OptimizationStrategy]
    priority_order: List[OptimizationPriority]
    estimated_time_ms: float
    constraints: Dict[str, Any] = field(default_factory=dict)


class TestCaseOptimizeLayer:
    """
    测试用例优化层

    负责对测试用例进行优化，提高其质量、可维护性和有效性。

    核心功能：
    - 代码重构：改善代码结构和可读性
    - 断言增强：丰富和优化断言逻辑
    - 冗余消除：移除重复的测试用例
    - 性能优化：提升测试执行效率
    - 可读性优化：改善代码格式和注释
    - 覆盖率提升：增加测试场景覆盖

    Attributes:
        description: 层的功能描述
        input_type: 输入数据类型 (PipelineContext)
        output_type: str = "OptimizationResult"

    Input Context Fields:
        - rendered_test_cases: 渲染后的测试用例列表
        - quality_evaluation_result: 质量评估结果
        - quality_issues: 质量问题列表
        - optimization_strategies: 优化策略列表（可选）
        - optimization_config: 优化配置（可选）

    Output:
        OptimizationResult: 优化结果
    """

    description: str = "测试用例优化层 - 优化测试用例质量"
    input_type: str = "PipelineContext"
    output_type: str = "OptimizationResult"

    def __init__(self, optimization_config: Optional[Dict[str, Any]] = None):
        """
        初始化测试用例优化层

        Args:
            optimization_config: 优化配置字典，包含：
                - max_optimizations_per_case: 每个用例最大优化次数
                - auto_apply: 是否自动应用优化
                - preserve_original: 是否保留原始代码
                - optimization_order: 优化顺序
        """
        self.config = optimization_config or {}
        self.max_optimizations = self.config.get('max_optimizations_per_case', 10)
        self.auto_apply = self.config.get('auto_apply', True)
        self.preserve_original = self.config.get('preserve_original', True)

    def process(self, context: Any) -> OptimizationResult:
        """
        执行测试用例优化

        Args:
            context: PipelineContext对象，包含以下预期字段：
                - rendered_test_cases: 渲染后的测试用例列表
                - quality_evaluation_result: 质量评估结果
                - quality_issues: 质量问题列表
                - optimization_strategies: 优化策略列表 (可选)
                - optimization_config: 优化配置 (可选)
                    - priority: 优化优先级
                    - max_cases: 最大优化用例数
                    - preserve_structure: 保留代码结构

        Returns:
            OptimizationResult: 优化结果，包含：
                - optimized_cases: 优化后的测试用例列表
                - optimization_actions: 执行的优化操作列表
                - total_cases_optimized: 优化的用例总数
                - total_improvement_score: 总改进分数
                - strategies_applied: 应用的优化策略
                - removed_duplicates: 移除的重复用例数
                - enhanced_assertions: 增强的断言数
                - performance_gains_ms: 性能提升（毫秒）

        Process Flow:
            1. 分析质量评估结果和质量问题
            2. 制定优化计划
            3. 应用代码重构优化
            4. 增强断言逻辑
            5. 消除冗余用例
            6. 应用性能优化
            7. 评估优化效果
            8. 返回优化结果

        Example:
            >>> layer = TestCaseOptimizeLayer()
            >>> ctx = create_context()
            >>> ctx.set('rendered_test_cases', cases)
            >>> ctx.set('quality_evaluation_result', quality_result)
            >>> result = layer.process(ctx)
            >>> print(f"优化了 {result.total_cases_optimized} 个用例")
        """
        rendered_cases = context.get('rendered_test_cases', [])
        quality_result = context.get('quality_evaluation_result')
        quality_issues = context.get('quality_issues', [])
        strategies = context.get(
            'optimization_strategies',
            [OptimizationStrategy.CODE_REFACTOR, OptimizationStrategy.ASSERTION_ENHANCE]
        )

        result = OptimizationResult()
        result.strategies_applied = list(strategies)

        issues_by_case = self._group_issues_by_case(quality_issues)

        for case in rendered_cases:
            case_id = self._get_case_id(case)
            case_issues = issues_by_case.get(case_id, [])

            optimized_case = case
            if case_issues or strategies:
                optimized_case = self._optimize_single_case(
                    case, case_issues, strategies
                )
                result.optimized_cases.append(optimized_case)
                result.total_cases_optimized += 1
            else:
                result.optimized_cases.append(case)

        duplicates = self._find_and_remove_duplicates(result.optimized_cases)
        result.removed_duplicates = len(duplicates)
        for dup in duplicates:
            result.optimized_cases.remove(dup)

        result.total_improvement_score = self._calculate_improvement_score(
            result.optimization_actions
        )

        result.enhanced_assertions = sum(
            1 for action in result.optimization_actions
            if action.action_type == OptimizationStrategy.ASSERTION_ENHANCE
        )

        result.performance_gains_ms = self._estimate_performance_gains(
            result.optimization_actions
        )

        context.set('optimized_test_cases', result.optimized_cases)
        context.set('optimization_result', result)

        return result

    def _group_issues_by_case(
        self, issues: List[Any]
    ) -> Dict[str, List[Any]]:
        """按用例分组质量问题"""
        grouped = {}

        for issue in issues:
            case_id = issue.get('case_id', 'unknown')
            if case_id not in grouped:
                grouped[case_id] = []
            grouped[case_id].append(issue)

        return grouped

    def _get_case_id(self, case: Any) -> str:
        """获取用例ID"""
        if hasattr(case, 'test_id'):
            return case.test_id
        elif hasattr(case, 'case_id'):
            return case.case_id
        elif isinstance(case, dict):
            return case.get('id', case.get('test_id', 'unknown'))
        return 'unknown'

    def _optimize_single_case(
        self, case: Any,
        issues: List[Any],
        strategies: List[OptimizationStrategy]
    ) -> Any:
        """优化单个测试用例"""
        optimizations_applied = 0

        for strategy in strategies:
            if optimizations_applied >= self.max_optimizations:
                break

            action = None

            if strategy == OptimizationStrategy.CODE_REFACTOR:
                action = self._apply_code_refactor(case, issues)
            elif strategy == OptimizationStrategy.ASSERTION_ENHANCE:
                action = self._apply_assertion_enhance(case, issues)
            elif strategy == OptimizationStrategy.READABILITY:
                action = self._apply_readability_improve(case, issues)
            elif strategy == OptimizationStrategy.PERFORMANCE:
                action = self._apply_performance_optimize(case, issues)

            if action:
                self._apply_optimization(case, action)
                optimizations_applied += 1

        return case

    def _apply_code_refactor(
        self, case: Any,
        issues: List[Any]
    ) -> Optional[OptimizationAction]:
        """应用代码重构优化"""
        code = self._get_case_code(case)

        refactored = code

        refactored = self._extract_magic_numbers(refactored)

        refactored = self._simplify_conditions(refactored)

        if refactored != code:
            return OptimizationAction(
                action_id=f"refactor_{self._get_case_id(case)}",
                action_type=OptimizationStrategy.CODE_REFACTOR,
                target_case_id=self._get_case_id(case),
                priority=OptimizationPriority.MEDIUM,
                description="代码重构优化",
                original_code=code,
                optimized_code=refactored,
                estimated_improvement=10.0,
                auto_applicable=True
            )

        return None

    def _apply_assertion_enhance(
        self, case: Any,
        issues: List[Any]
    ) -> Optional[OptimizationAction]:
        """应用断言增强优化"""
        code = self._get_case_code(case)

        if 'assert' not in code.lower():
            enhanced_code = code + '\n\n    # Enhanced assertions\n    assert result is not None, "Result should not be None"'
            return OptimizationAction(
                action_id=f"assert_{self._get_case_id(case)}",
                action_type=OptimizationStrategy.ASSERTION_ENHANCE,
                target_case_id=self._get_case_id(case),
                priority=OptimizationPriority.HIGH,
                description="添加断言验证",
                original_code=code,
                optimized_code=enhanced_code,
                estimated_improvement=15.0,
                auto_applicable=True
            )

        return None

    def _apply_readability_improve(
        self, case: Any,
        issues: List[Any]
    ) -> Optional[OptimizationAction]:
        """应用可读性优化"""
        code = self._get_case_code(case)

        improved_code = self._add_comments(code)

        improved_code = self._format_code(improved_code)

        if improved_code != code:
            return OptimizationAction(
                action_id=f"readability_{self._get_case_id(case)}",
                action_type=OptimizationStrategy.READABILITY,
                target_case_id=self._get_case_id(case),
                priority=OptimizationPriority.LOW,
                description="提高代码可读性",
                original_code=code,
                optimized_code=improved_code,
                estimated_improvement=5.0,
                auto_applicable=True
            )

        return None

    def _apply_performance_optimize(
        self, case: Any,
        issues: List[Any]
    ) -> Optional[OptimizationAction]:
        """应用性能优化"""
        code = self._get_case_code(case)

        optimized_code = self._remove_unnecessary_operations(code)

        if optimized_code != code:
            return OptimizationAction(
                action_id=f"perf_{self._get_case_id(case)}",
                action_type=OptimizationStrategy.PERFORMANCE,
                target_case_id=self._get_case_id(case),
                priority=OptimizationPriority.MEDIUM,
                description="性能优化",
                original_code=code,
                optimized_code=optimized_code,
                estimated_improvement=8.0,
                auto_applicable=True
            )

        return None

    def _extract_magic_numbers(self, code: str) -> str:
        """提取魔法数字"""
        import re

        magic_pattern = r'\b(\d{3,})\b'
        matches = re.finditer(magic_pattern, code)

        constants = []
        constant_map = {}
        counter = 1

        for match in matches:
            num = match.group(1)
            if num not in constant_map:
                constant_name = f"MAGIC_NUMBER_{counter}"
                constant_map[num] = constant_name
                constants.append(f"{constant_name} = {num}")
                counter += 1

        if constants:
            header = '\n'.join(constants) + '\n\n'
            return header + code

        return code

    def _simplify_conditions(self, code: str) -> str:
        """简化条件判断"""
        code = code.replace('if x == True:', 'if x:')
        code = code.replace('if x == False:', 'if not x:')
        code = code.replace('if x != None:', 'if x is not None:')

        return code

    def _add_comments(self, code: str) -> str:
        """添加注释"""
        lines = code.split('\n')
        commented_lines = []

        for i, line in enumerate(lines, 1):
            if line.strip() and not line.strip().startswith('#'):
                if i % 5 == 0:
                    commented_lines.append(f'    # Step {i // 5}')
            commented_lines.append(line)

        return '\n'.join(commented_lines)

    def _format_code(self, code: str) -> str:
        """格式化代码"""
        lines = [line.rstrip() for line in code.split('\n')]

        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()

        return '\n'.join(lines)

    def _remove_unnecessary_operations(self, code: str) -> str:
        """移除不必要的操作"""
        import re

        code = re.sub(r'time\.sleep\(\s*0\s*\)', '', code)

        code = re.sub(r'\n\s*\n\s*\n', '\n\n', code)

        return code

    def _apply_optimization(
        self, case: Any,
        action: OptimizationAction
    ) -> None:
        """应用优化到用例"""
        if hasattr(case, 'test_code'):
            case.test_code = action.optimized_code
        elif isinstance(case, dict):
            case['test_code'] = action.optimized_code

    def _get_case_code(self, case: Any) -> str:
        """获取用例代码"""
        if hasattr(case, 'test_code'):
            return case.test_code
        elif isinstance(case, dict):
            return case.get('test_code', '')
        return ''

    def _find_and_remove_duplicates(
        self, cases: List[Any]
    ) -> List[Any]:
        """查找并移除重复用例"""
        seen_codes = set()
        duplicates = []

        for case in cases:
            code = self._get_case_code(case)
            code_hash = hash(code.strip())

            if code_hash in seen_codes:
                duplicates.append(case)
            else:
                seen_codes.add(code_hash)

        return duplicates

    def _calculate_improvement_score(
        self, actions: List[OptimizationAction]
    ) -> float:
        """计算改进分数"""
        total_score = sum(action.estimated_improvement for action in actions)
        return round(total_score, 2)

    def _estimate_performance_gains(
        self, actions: List[OptimizationAction]
    ) -> float:
        """估算性能提升"""
        perf_actions = [
            a for a in actions
            if a.action_type == OptimizationStrategy.PERFORMANCE
        ]

        estimated_ms = len(perf_actions) * 5.0
        return round(estimated_ms, 2)

    def create_optimization_plan(
        self, cases: List[Any],
        quality_issues: List[Any],
        strategies: List[OptimizationStrategy]
    ) -> OptimizationPlan:
        """
        创建优化计划

        Args:
            cases: 测试用例列表
            quality_issues: 质量问题列表
            strategies: 优化策略列表

        Returns:
            OptimizationPlan: 优化计划对象
        """
        issues_by_case = self._group_issues_by_case(quality_issues)

        target_case_ids = list(issues_by_case.keys())

        priorities = self._determine_priorities(issues_by_case)

        estimated_time = len(target_case_ids) * 100.0

        return OptimizationPlan(
            plan_id=f"plan_{len(cases)}",
            target_cases=target_case_ids,
            strategies=strategies,
            priority_order=priorities,
            estimated_time_ms=estimated_time,
            constraints={'max_cases': len(cases)}
        )

    def _determine_priorities(
        self, issues_by_case: Dict[str, List[Any]]
    ) -> List[OptimizationPriority]:
        """确定优化优先级"""
        priorities = []

        for case_id, issues in issues_by_case.items():
            severities = [i.get('severity', 'minor') for i in issues]

            if 'critical' in severities:
                priorities.append(OptimizationPriority.HIGH)
            elif 'major' in severities:
                priorities.append(OptimizationPriority.MEDIUM)
            else:
                priorities.append(OptimizationPriority.LOW)

        return priorities

    def apply_optimization_batch(
        self, cases: List[Any],
        plan: OptimizationPlan
    ) -> OptimizationResult:
        """
        批量应用优化

        Args:
            cases: 测试用例列表
            plan: 优化计划

        Returns:
            OptimizationResult: 批量优化结果
        """
        context = {
            'rendered_test_cases': cases,
            'optimization_strategies': plan.strategies,
        }

        return self.process(type('Context', (), context)())

    def rollback_optimization(
        self, optimized_cases: List[Any],
        original_cases: List[Any]
    ) -> List[Any]:
        """
        回滚优化

        Args:
            optimized_cases: 优化后的用例
            original_cases: 原始用例

        Returns:
            List[Any]: 恢复后的用例列表
        """
        return list(original_cases)
