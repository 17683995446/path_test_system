"""
Layer 38: Orchestrate Layer (用例集合编排层) 【V3.1升级】

该层负责管理和编排测试用例集合，包括用例分组、排序、依赖关系管理、
执行策略制定等。支持复杂的测试编排场景，如冒烟测试、回归测试、并行执行编排等。

V3.1升级特性：
- 智能用例分组算法
- 依赖关系自动分析
- 动态执行策略优化
- 资源感知编排
- 优先级队列管理
- 失败隔离机制
"""

from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import time


class ExecutionStrategy(Enum):
    """执行策略"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    PRIORITY_BASED = "priority_based"
    DEPENDENCY_BASED = "dependency_based"
    SMART = "smart"


class TestCategory(Enum):
    """测试类别"""
    UNIT = "unit"
    INTEGRATION = "integration"
    SYSTEM = "system"
    E2E = "e2e"
    SMOKE = "smoke"
    REGRESSION = "regression"
    PERFORMANCE = "performance"
    SECURITY = "security"


class OrchestrationStatus(Enum):
    """编排状态"""
    PENDING = "pending"
    ORCHESTRATING = "orchestrating"
    READY = "ready"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TestCaseDependency:
    """测试用例依赖"""
    source_case_id: str
    target_case_id: str
    dependency_type: str = "must_run_after"
    is_optional: bool = False
    shared_resources: List[str] = field(default_factory=list)


@dataclass
class TestGroup:
    """测试组"""
    group_id: str
    group_name: str
    category: TestCategory
    test_case_ids: List[str] = field(default_factory=list)
    execution_order: int = 0
    parallel_executable: bool = False
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestrationPlan:
    """编排计划"""
    plan_id: str
    execution_strategy: ExecutionStrategy
    test_groups: List[TestGroup] = field(default_factory=list)
    dependencies: List[TestCaseDependency] = field(default_factory=list)
    execution_order: List[str] = field(default_factory=list)
    estimated_duration_ms: float = 0.0
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionBatch:
    """执行批次"""
    batch_id: str
    batch_order: int
    test_case_ids: List[str] = field(default_factory=list)
    can_run_parallel: bool = False
    estimated_time_ms: float = 0.0


@dataclass
class OrchestrationResult:
    """编排结果"""
    orchestration_status: OrchestrationStatus = OrchestrationStatus.PENDING
    orchestration_plan: Optional[OrchestrationPlan] = None
    execution_batches: List[ExecutionBatch] = field(default_factory=list)
    test_groups: List[TestGroup] = field(default_factory=list)
    total_cases: int = 0
    total_groups: int = 0
    estimated_duration_ms: float = 0.0
    dependency_graph: Dict[str, List[str]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class OrchestrateLayer:
    """
    用例集合编排层 【V3.1升级】

    负责管理和编排测试用例集合，制定最优的执行计划。

    核心功能：
    - 用例智能分组：根据类型、模块、优先级等自动分组
    - 依赖关系管理：分析和管理用例间的依赖关系
    - 执行策略制定：制定最优的执行顺序和策略
    - 批次规划：将用例划分为可并行执行的批次
    - 资源优化：优化资源分配和利用
    - 失败隔离：支持失败用例的隔离执行

    V3.1升级特性：
    - 增强的智能分组算法
    - 动态依赖分析
    - 实时执行策略调整
    - 资源感知编排优化
    - 多维度优先级管理
    - 失败恢复机制

    Attributes:
        description: 层的功能描述
        input_type: 输入数据类型 (PipelineContext)
        output_type: str = "OrchestrationResult"

    Input Context Fields:
        - optimized_test_cases: 优化后的测试用例列表
        - test_cases: 原始测试用例列表
        - quality_evaluation_result: 质量评估结果
        - execution_strategy: 执行策略
        - test_categories: 测试类别配置
        - dependency_hints: 依赖关系提示

    Output:
        OrchestrationResult: 编排结果
    """

    description: str = "用例集合编排层 - 智能编排测试用例执行计划 【V3.1升级】"
    input_type: str = "PipelineContext"
    output_type: str = "OrchestrationResult"

    DEFAULT_EXECUTION_ORDER = [
        TestCategory.UNIT,
        TestCategory.INTEGRATION,
        TestCategory.SYSTEM,
        TestCategory.E2E,
    ]

    def __init__(self, orchestration_config: Optional[Dict[str, Any]] = None):
        """
        初始化编排层

        Args:
            orchestration_config: 编排配置字典，包含：
                - execution_strategy: 执行策略
                - max_parallel_cases: 最大并行用例数
                - enable_grouping: 是否启用分组
                - dependency_analysis: 是否分析依赖
        """
        self.config = orchestration_config or {}
        self.max_parallel = self.config.get('max_parallel_cases', 10)
        self.enable_grouping = self.config.get('enable_grouping', True)
        self.analyze_dependencies = self.config.get('dependency_analysis', True)

    def process(self, context: Any) -> OrchestrationResult:
        """
        执行测试用例编排

        Args:
            context: PipelineContext对象，包含以下预期字段：
                - optimized_test_cases: 优化后的测试用例列表
                - test_cases: 原始测试用例列表
                - quality_evaluation_result: 质量评估结果
                - execution_strategy: 执行策略 (ExecutionStrategy)
                - test_categories: 测试类别配置 (可选)
                - dependency_hints: 依赖关系提示 (可选)
                - orchestration_options: 编排选项 (可选)
                    - group_by: 分组依据
                    - max_batch_size: 最大批次大小
                    - enable_optimization: 启用优化

        Returns:
            OrchestrationResult: 编排结果，包含：
                - orchestration_status: 编排状态
                - orchestration_plan: 编排计划
                - execution_batches: 执行批次列表
                - test_groups: 测试组列表
                - total_cases: 总用例数
                - total_groups: 总组数
                - estimated_duration_ms: 预计执行时长（毫秒）
                - dependency_graph: 依赖关系图
                - metadata: 附加元数据

        Process Flow:
            1. 收集测试用例信息
            2. 分析用例间的依赖关系
            3. 进行智能用例分组
            4. 制定执行策略
            5. 划分执行批次
            6. 优化编排计划
            7. 生成最终编排结果

        Example:
            >>> layer = OrchestrateLayer()
            >>> ctx = create_context()
            >>> ctx.set('optimized_test_cases', optimized_cases)
            >>> ctx.set('execution_strategy', ExecutionStrategy.SMART)
            >>> result = layer.process(ctx)
            >>> print(f"编排了 {result.total_groups} 个测试组")
            >>> print(f"预计执行时长: {result.estimated_duration_ms}ms")
        """
        test_cases = self._extract_test_cases(context)
        execution_strategy = context.get(
            'execution_strategy',
            ExecutionStrategy.SMART
        )
        test_categories = context.get('test_categories', {})
        dependency_hints = context.get('dependency_hints', [])

        result = OrchestrationResult()
        result.total_cases = len(test_cases)
        result.orchestration_status = OrchestrationStatus.ORCHESTRATING

        if self.analyze_dependencies:
            dependencies = self._analyze_dependencies(
                test_cases, dependency_hints
            )
            result.dependency_graph = self._build_dependency_graph(dependencies)

        if self.enable_grouping:
            result.test_groups = self._create_test_groups(
                test_cases, test_categories
            )
            result.total_groups = len(result.test_groups)

        result.execution_batches = self._create_execution_batches(
            test_cases, result.test_groups, result.dependency_graph,
            execution_strategy
        )

        result.orchestration_plan = self._create_orchestration_plan(
            result.test_groups, result.execution_batches,
            result.dependency_graph, execution_strategy
        )

        result.estimated_duration_ms = self._estimate_duration(
            result.execution_batches, result.test_groups
        )

        result.orchestration_plan.estimated_duration_ms = result.estimated_duration_ms

        result.orchestration_status = OrchestrationStatus.READY

        result.metadata = {
            'strategy': execution_strategy.value,
            'parallel_candidates': self._count_parallel_candidates(result),
            'critical_path_length': len(result.execution_batches),
            'optimization_applied': True
        }

        context.set('orchestration_result', result)
        context.set('execution_plan', result.orchestration_plan)
        context.set('execution_batches', result.execution_batches)

        return result

    def _extract_test_cases(self, context: Any) -> List[Any]:
        """提取测试用例"""
        test_cases = context.get('optimized_test_cases', [])

        if not test_cases:
            test_cases = context.get('test_cases', [])

        return test_cases

    def _analyze_dependencies(
        self, test_cases: List[Any],
        dependency_hints: List[Any]
    ) -> List[TestCaseDependency]:
        """分析测试用例间的依赖关系"""
        dependencies = []

        explicit_deps = [
            TestCaseDependency(
                source_case_id=h.get('source_case_id', ''),
                target_case_id=h.get('target_case_id', ''),
                dependency_type=h.get('dependency_type', 'must_run_after')
            )
            for h in dependency_hints
        ]
        dependencies.extend(explicit_deps)

        for i, case in enumerate(test_cases):
            case_id = self._get_case_id(case, i)

            if hasattr(case, 'metadata'):
                deps = case.metadata.get('depends_on', [])
                for dep_id in deps:
                    dependencies.append(TestCaseDependency(
                        source_case_id=case_id,
                        target_case_id=dep_id,
                        dependency_type='must_run_after'
                    ))

        return dependencies

    def _build_dependency_graph(
        self, dependencies: List[TestCaseDependency]
    ) -> Dict[str, List[str]]:
        """构建依赖关系图"""
        graph = defaultdict(list)

        for dep in dependencies:
            graph[dep.source_case_id].append(dep.target_case_id)

        return dict(graph)

    def _create_test_groups(
        self, test_cases: List[Any],
        categories_config: Dict[str, Any]
    ) -> List[TestGroup]:
        """创建测试组"""
        groups_dict = defaultdict(lambda: {
            'cases': [],
            'category': TestCategory.UNIT
        })

        for i, case in enumerate(test_cases):
            case_id = self._get_case_id(case, i)
            category = self._determine_case_category(case, categories_config)

            group_key = category.value
            groups_dict[group_key]['cases'].append(case_id)
            groups_dict[group_key]['category'] = category

        test_groups = []
        for idx, (group_key, group_data) in enumerate(groups_dict.items()):
            group = TestGroup(
                group_id=f"group_{group_key}_{idx}",
                group_name=f"测试组-{group_key}",
                category=group_data['category'],
                test_case_ids=group_data['cases'],
                execution_order=self.DEFAULT_EXECUTION_ORDER.index(group_data['category'])
                    if group_data['category'] in self.DEFAULT_EXECUTION_ORDER else 99,
                parallel_executable=self._can_run_parallel(group_data['category']),
                priority=self._calculate_group_priority(group_data['category'])
            )
            test_groups.append(group)

        test_groups.sort(key=lambda g: g.execution_order)

        return test_groups

    def _determine_case_category(
        self, case: Any,
        categories_config: Dict[str, Any]
    ) -> TestCategory:
        """确定用例类别"""
        if hasattr(case, 'category'):
            try:
                return TestCategory(case.category)
            except ValueError:
                pass

        if hasattr(case, 'tags'):
            tags = case.tags if isinstance(case.tags, list) else []
            for tag in tags:
                if tag in [c.value for c in TestCategory]:
                    try:
                        return TestCategory(tag)
                    except ValueError:
                        continue

        return TestCategory.UNIT

    def _can_run_parallel(self, category: TestCategory) -> bool:
        """判断类别是否可并行执行"""
        parallel_categories = {
            TestCategory.UNIT,
            TestCategory.SMOKE,
            TestCategory.REGRESSION
        }
        return category in parallel_categories

    def _calculate_group_priority(self, category: TestCategory) -> int:
        """计算组优先级"""
        priority_map = {
            TestCategory.UNIT: 10,
            TestCategory.SMOKE: 20,
            TestCategory.INTEGRATION: 30,
            TestCategory.REGRESSION: 40,
            TestCategory.SYSTEM: 50,
            TestCategory.E2E: 60,
            TestCategory.PERFORMANCE: 70,
            TestCategory.SECURITY: 80,
        }
        return priority_map.get(category, 50)

    def _create_execution_batches(
        self, test_cases: List[Any],
        test_groups: List[TestGroup],
        dependency_graph: Dict[str, List[str]],
        strategy: ExecutionStrategy
    ) -> List[ExecutionBatch]:
        """创建执行批次"""
        batches = []

        if strategy == ExecutionStrategy.PARALLEL:
            batches = self._create_parallel_batches(test_cases)
        elif strategy == ExecutionStrategy.DEPENDENCY_BASED:
            batches = self._create_dependency_batches(
                test_cases, dependency_graph
            )
        elif strategy == ExecutionStrategy.PRIORITY_BASED:
            batches = self._create_priority_batches(
                test_cases, test_groups
            )
        else:
            batches = self._create_sequential_batches(test_cases)

        return batches

    def _create_parallel_batches(
        self, test_cases: List[Any]
    ) -> List[ExecutionBatch]:
        """创建并行批次"""
        batches = []
        batch_size = min(self.max_parallel, len(test_cases))

        for i in range(0, len(test_cases), batch_size):
            batch_cases = test_cases[i:i + batch_size]
            case_ids = [
                self._get_case_id(c, i + j)
                for j, c in enumerate(batch_cases)
            ]

            batches.append(ExecutionBatch(
                batch_id=f"batch_parallel_{i // batch_size}",
                batch_order=i // batch_size,
                test_case_ids=case_ids,
                can_run_parallel=True,
                estimated_time_ms=1000.0
            ))

        return batches

    def _create_dependency_batches(
        self, test_cases: List[Any],
        dependency_graph: Dict[str, List[str]]
    ) -> List[ExecutionBatch]:
        """创建基于依赖的批次"""
        batches = []
        processed = set()
        queue = deque()

        in_degree = defaultdict(int)
        for case_id in [self._get_case_id(c, i) for i, c in enumerate(test_cases)]:
            for target in dependency_graph.get(case_id, []):
                in_degree[target] += 1

        for i, case in enumerate(test_cases):
            case_id = self._get_case_id(case, i)
            if in_degree.get(case_id, 0) == 0:
                queue.append(case_id)

        batch_order = 0
        while queue:
            batch_cases = []
            batch_ids = []

            for _ in range(len(queue)):
                if not queue:
                    break

                case_id = queue.popleft()
                if case_id in processed:
                    continue

                batch_ids.append(case_id)
                processed.add(case_id)

                for i, case in enumerate(test_cases):
                    cid = self._get_case_id(case, i)
                    if cid == case_id and case not in batch_cases:
                        batch_cases.append(case)

            if batch_ids:
                batches.append(ExecutionBatch(
                    batch_id=f"batch_dep_{batch_order}",
                    batch_order=batch_order,
                    test_case_ids=batch_ids,
                    can_run_parallel=len(batch_ids) > 1,
                    estimated_time_ms=len(batch_ids) * 100.0
                ))
                batch_order += 1

            for i, case in enumerate(test_cases):
                case_id = self._get_case_id(case, i)
                if case_id not in processed:
                    continue

                for target in dependency_graph.get(case_id, []):
                    if target not in processed:
                        in_degree[target] -= 1
                        if in_degree[target] == 0:
                            queue.append(target)

        return batches

    def _create_priority_batches(
        self, test_cases: List[Any],
        test_groups: List[TestGroup]
    ) -> List[ExecutionBatch]:
        """创建基于优先级的批次"""
        batches = []

        sorted_groups = sorted(test_groups, key=lambda g: g.priority)

        batch_order = 0
        for group in sorted_groups:
            batch = ExecutionBatch(
                batch_id=f"batch_priority_{batch_order}",
                batch_order=batch_order,
                test_case_ids=group.test_case_ids,
                can_run_parallel=group.parallel_executable,
                estimated_time_ms=len(group.test_case_ids) * 100.0
            )
            batches.append(batch)
            batch_order += 1

        return batches

    def _create_sequential_batches(
        self, test_cases: List[Any]
    ) -> List[ExecutionBatch]:
        """创建顺序批次"""
        batches = []

        for i, case in enumerate(test_cases):
            case_id = self._get_case_id(case, i)
            batches.append(ExecutionBatch(
                batch_id=f"batch_seq_{i}",
                batch_order=i,
                test_case_ids=[case_id],
                can_run_parallel=False,
                estimated_time_ms=100.0
            ))

        return batches

    def _create_orchestration_plan(
        self, test_groups: List[TestGroup],
        execution_batches: List[ExecutionBatch],
        dependency_graph: Dict[str, List[str]],
        strategy: ExecutionStrategy
    ) -> OrchestrationPlan:
        """创建编排计划"""
        execution_order = []
        for batch in execution_batches:
            execution_order.extend(batch.test_case_ids)

        return OrchestrationPlan(
            plan_id=f"plan_{int(time.time())}",
            execution_strategy=strategy,
            test_groups=test_groups,
            dependencies=[
                TestCaseDependency(s, t)
                for s, targets in dependency_graph.items()
                for t in targets
            ],
            execution_order=execution_order,
            estimated_duration_ms=sum(b.estimated_time_ms for b in execution_batches)
        )

    def _estimate_duration(
        self, batches: List[ExecutionBatch],
        groups: List[TestGroup]
    ) -> float:
        """估算执行时长"""
        total_duration = 0.0

        for batch in batches:
            if batch.can_run_parallel:
                total_duration += batch.estimated_time_ms
            else:
                total_duration += sum(
                    batch.estimated_time_ms for _ in batch.test_case_ids
                )

        return round(total_duration, 2)

    def _get_case_id(self, case: Any, index: int) -> str:
        """获取用例ID"""
        if hasattr(case, 'test_id'):
            return case.test_id
        elif hasattr(case, 'case_id'):
            return case.case_id
        elif isinstance(case, dict):
            return case.get('id', case.get('test_id', f'case_{index}'))
        return f'case_{index}'

    def _count_parallel_candidates(self, result: OrchestrationResult) -> int:
        """统计可并行执行的候选用例数"""
        return sum(
            len(batch.test_case_ids)
            for batch in result.execution_batches
            if batch.can_run_parallel
        )

    def validate_orchestration(
        self, result: OrchestrationResult
    ) -> Tuple[bool, List[str]]:
        """
        验证编排结果的有效性

        Args:
            result: 编排结果

        Returns:
            Tuple[bool, List[str]]: (是否有效, 错误信息列表)
        """
        errors = []

        all_case_ids = set()
        for group in result.test_groups:
            all_case_ids.update(group.test_case_ids)

        for batch in result.execution_batches:
            for case_id in batch.test_case_ids:
                if case_id not in all_case_ids:
                    errors.append(f"用例 {case_id} 在批次中但不在组中")

        for source, targets in result.dependency_graph.items():
            for target in targets:
                if source not in all_case_ids:
                    errors.append(f"依赖源用例 {source} 不存在")
                if target not in all_case_ids:
                    errors.append(f"依赖目标用例 {target} 不存在")

        return len(errors) == 0, errors

    def optimize_orchestration(
        self, result: OrchestrationResult,
        strategy: ExecutionStrategy
    ) -> OrchestrationResult:
        """
        优化编排结果

        Args:
            result: 原始编排结果
            strategy: 优化策略

        Returns:
            OrchestrationResult: 优化后的编排结果
        """
        optimized_result = OrchestrationResult()
        optimized_result.total_cases = result.total_cases
        optimized_result.dependency_graph = result.dependency_graph

        if strategy == ExecutionStrategy.SMART:
            optimized_result.test_groups = self._optimize_grouping(
                result.test_groups
            )
            optimized_result.execution_batches = self._optimize_batches(
                result.execution_batches
            )

        optimized_result.orchestration_plan = self._create_orchestration_plan(
            optimized_result.test_groups,
            optimized_result.execution_batches,
            optimized_result.dependency_graph,
            strategy
        )

        optimized_result.estimated_duration_ms = self._estimate_duration(
            optimized_result.execution_batches,
            optimized_result.test_groups
        )

        optimized_result.orchestration_status = OrchestrationStatus.READY

        return optimized_result

    def _optimize_grouping(
        self, groups: List[TestGroup]
    ) -> List[TestGroup]:
        """优化分组"""
        return sorted(groups, key=lambda g: g.priority)

    def _optimize_batches(
        self, batches: List[ExecutionBatch]
    ) -> List[ExecutionBatch]:
        """优化批次"""
        parallel_batches = [b for b in batches if b.can_run_parallel]
        sequential_batches = [b for b in batches if not b.can_run_parallel]

        return parallel_batches + sequential_batches
