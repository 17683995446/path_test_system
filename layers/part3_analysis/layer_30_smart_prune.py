"""
Layer 30: SmartPruneLayer - 智能路径剪枝层【V3.1升级】

本层采用多种智能策略对路径进行剪枝，包括基于覆盖、基于风险、
基于相似度和基于代价的剪枝，提高测试效率。
V3.1升级增强了多策略融合和自适应剪枝能力。
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import defaultdict


class PruneStrategy(Enum):
    """剪枝策略枚举"""
    COVERAGE_BASED = auto()
    RISK_BASED = auto()
    SIMILARITY_BASED = auto()
    COST_BASED = auto()
    DOMINANCE_BASED = auto()
    ADAPTIVE = auto()


class PruneScope(Enum):
    """剪枝范围枚举"""
    AGGRESSIVE = auto()
    MODERATE = auto()
    CONSERVATIVE = auto()
    MINIMAL = auto()


@dataclass
class SmartPruneConfig:
    """智能剪枝配置

    Attributes:
        strategy: 剪枝策略
        scope: 剪枝范围
        max_prune_ratio: 最大剪枝比例
        min_coverage_threshold: 最小覆盖阈值
        similarity_threshold: 相似度阈值
        enable_adaptive: 是否启用自适应
        preserve_critical: 是否保留关键路径
        enable_logging: 是否启用日志
    """
    strategy: PruneStrategy = PruneStrategy.ADAPTIVE
    scope: PruneScope = PruneScope.MODERATE
    max_prune_ratio: float = 0.7
    min_coverage_threshold: float = 0.3
    similarity_threshold: float = 0.8
    enable_adaptive: bool = True
    preserve_critical: bool = True
    enable_logging: bool = True


@dataclass
class PruneCandidate:
    """智能剪枝候选

    Attributes:
        path_id: 路径标识符
        prune_strategy: 剪枝策略
        prune_score: 剪枝评分
        coverage_loss: 覆盖损失
        risk_impact: 风险影响
        alternatives: 替代路径
        justification: 剪枝理由
        preserved_conditions: 保留条件
    """
    path_id: str
    prune_strategy: PruneStrategy
    prune_score: float = 0.0
    coverage_loss: float = 0.0
    risk_impact: str = "low"
    alternatives: List[str] = field(default_factory=list)
    justification: str = ""
    preserved_conditions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "path_id": self.path_id,
            "prune_strategy": self.prune_strategy.name,
            "prune_score": self.prune_score,
            "coverage_loss": self.coverage_loss,
            "risk_impact": self.risk_impact,
            "alternatives": self.alternatives,
            "justification": self.justification,
            "preserved_conditions": self.preserved_conditions
        }


@dataclass
class SmartPruneResult:
    """智能剪枝结果

    Attributes:
        original_count: 原始路径数
        pruned_count: 剪枝路径数
        retained_count: 保留路径数
        prune_ratio: 剪枝比例
        strategy_used: 使用的策略
        candidates: 剪枝候选列表
        retained_paths: 保留路径列表
        coverage_metrics: 覆盖指标
        pruning_report: 剪枝报告
        warnings: 警告信息
        metadata: 元信息
    """
    original_count: int = 0
    pruned_count: int = 0
    retained_count: int = 0
    prune_ratio: float = 0.0
    strategy_used: str = ""
    candidates: List[PruneCandidate] = field(default_factory=list)
    retained_paths: List[str] = field(default_factory=list)
    coverage_metrics: Dict[str, Any] = field(default_factory=dict)
    pruning_report: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "original_count": self.original_count,
            "pruned_count": self.pruned_count,
            "retained_count": self.retained_count,
            "prune_ratio": self.prune_ratio,
            "strategy_used": self.strategy_used,
            "candidates": [c.to_dict() for c in self.candidates],
            "retained_paths": self.retained_paths,
            "coverage_metrics": self.coverage_metrics,
            "pruning_report": self.pruning_report,
            "warnings": self.warnings,
            "metadata": self.metadata
        }


class SmartPruneLayer:
    """智能路径剪枝层【V3.1升级】

    功能描述：
        - 采用多种智能剪枝策略
        - 支持自适应策略选择
        - 评估剪枝对覆盖的影响
        - 识别替代路径和保留条件
        - 生成详细的剪枝报告
        - 保障关键路径不被剪枝
        - 支持可配置的剪枝范围

    输入类型：
        - 路径列表（List[Path]）
        - 优先级信息（List[PathPriority]）
        - 覆盖统计（coverage_statistics）
        - 剪枝配置（SmartPruneConfig，可选）

    输出类型：
        - SmartPruneResult: 智能剪枝结果
        - List[PruneCandidate]: 剪枝候选列表
        - 剪枝报告和覆盖指标

    使用场景：
        - 大规模路径集的优化剪枝
        - 测试资源有限时的路径选择
        - 快速迭代开发中的轻量级测试
        - 持续集成中的测试优化
        - 回归测试选择

    V3.1升级点：
        - 增强多策略融合能力
        - 支持自适应策略调整
        - 提供更精确的覆盖损失评估
        - 增加风险影响分析
        - 支持渐进式剪枝
    """

    description: str = "智能路径剪枝层【V3.1升级】- 多策略智能路径剪枝优化"
    input_type: str = "List[Path]、List[PathPriority]和SmartPruneConfig"
    output_type: str = "SmartPruneResult和List[PruneCandidate]"

    def __init__(self):
        """初始化智能路径剪枝层"""
        self.paths = []
        self.priorities = []
        self.config = SmartPruneConfig()
        self.coverage_stats = {}
        self.candidates = []
        self.prune_result = None

    def set_config(self, config: SmartPruneConfig) -> None:
        """设置剪枝配置

        Args:
            config: 智能剪枝配置
        """
        self.config = config

    def process(self, context) -> SmartPruneResult:
        """处理路径，执行智能剪枝

        Args:
            context: PipelineContext对象，包含路径和配置信息

        Returns:
            SmartPruneResult: 智能剪枝结果

        Raises:
            ValueError: 当输入数据不足时
        """
        if not context.has('paths') and not context.has('enumerated_paths'):
            if not context.has('execution_paths'):
                raise ValueError("SmartPruneLayer: 缺少路径数据")

        if context.has('paths'):
            self.paths = context.get('paths')
        elif context.has('enumerated_paths'):
            self.paths = context.get('enumerated_paths')
        elif context.has('execution_paths'):
            self.paths = context.get('execution_paths')

        if context.has('prioritized_paths'):
            self.priorities = context.get('prioritized_paths')

        if context.has('coverage_statistics'):
            self.coverage_stats = context.get('coverage_statistics')

        if context.has('smart_prune_config'):
            self.config = context.get('smart_prune_config')

        if self.config.enable_adaptive:
            self._adjust_strategy_adaptively()

        self._generate_prune_candidates()

        self._apply_pruning_strategy()

        self._ensure_critical_paths_preserved()

        self.prune_result = self._create_prune_result()

        context.set('prune_candidates', self.candidates)
        context.set('smart_prune_result', self.prune_result)
        context.set('smart_pruning_complete', True)
        context.set('smart_pruning_statistics', self._get_statistics())

        return self.prune_result

    def _adjust_strategy_adaptively(self) -> None:
        """自适应调整策略【V3.1增强】"""
        if not self.paths:
            return

        path_count = len(self.paths)
        avg_complexity = self._calculate_avg_complexity()

        if path_count > 1000:
            self.config.strategy = PruneStrategy.AGGRESSIVE
            self.config.max_prune_ratio = 0.8
        elif path_count > 500:
            self.config.strategy = PruneStrategy.COST_BASED
            self.config.max_prune_ratio = 0.7
        elif avg_complexity > 15:
            self.config.strategy = PruneStrategy.RISK_BASED
            self.config.max_prune_ratio = 0.6
        else:
            self.config.strategy = PruneStrategy.COVERAGE_BASED
            self.config.max_prune_ratio = 0.5

        if self.config.scope == PruneScope.ADAPTIVE:
            if path_count > 500:
                self.config.scope = PruneScope.AGGRESSIVE
            elif path_count > 200:
                self.config.scope = PruneScope.MODERATE
            else:
                self.config.scope = PruneScope.CONSERVATIVE

    def _calculate_avg_complexity(self) -> float:
        """计算平均复杂度

        Returns:
            float: 平均复杂度
        """
        if not self.paths:
            return 0.0

        total_complexity = 0
        for path in self.paths:
            if hasattr(path, 'complexity'):
                total_complexity += path.complexity
            elif hasattr(path, 'length'):
                total_complexity += path.length

        return total_complexity / len(self.paths)

    def _generate_prune_candidates(self) -> None:
        """生成剪枝候选"""
        self.candidates = []

        if self.config.strategy == PruneStrategy.COVERAGE_BASED:
            self._generate_coverage_based_candidates()
        elif self.config.strategy == PruneStrategy.RISK_BASED:
            self._generate_risk_based_candidates()
        elif self.config.strategy == PruneStrategy.SIMILARITY_BASED:
            self._generate_similarity_based_candidates()
        elif self.config.strategy == PruneStrategy.COST_BASED:
            self._generate_cost_based_candidates()
        elif self.config.strategy == PruneStrategy.DOMINANCE_BASED:
            self._generate_dominance_based_candidates()
        else:
            self._generate_adaptive_candidates()

    def _generate_coverage_based_candidates(self) -> None:
        """基于覆盖生成剪枝候选"""
        coverage_scores = []

        for path in self.paths:
            path_id = self._get_path_id(path)
            score = self._calculate_coverage_score(path)

            coverage_scores.append((path_id, score))

        coverage_scores.sort(key=lambda x: x[1])

        max_prune = int(len(self.paths) * self.config.max_prune_ratio)

        for path_id, score in coverage_scores[:max_prune]:
            if score < self.config.min_coverage_threshold:
                candidate = self._create_coverage_based_candidate(path_id, score)
                self.candidates.append(candidate)

    def _calculate_coverage_score(self, path) -> float:
        """计算覆盖评分

        Args:
            path: 路径对象

        Returns:
            float: 覆盖评分
        """
        score = 0.3

        if hasattr(path, 'coverage_potential'):
            score = path.coverage_potential

        if hasattr(path, 'test_value'):
            score = max(score, path.test_value)

        if hasattr(path, 'segments'):
            score += min(0.2, len(path.segments) / 50.0)

        return min(1.0, score)

    def _create_coverage_based_candidate(self, path_id: str, score: float) -> PruneCandidate:
        """创建基于覆盖的剪枝候选

        Args:
            path_id: 路径标识符
            score: 覆盖评分

        Returns:
            PruneCandidate: 剪枝候选
        """
        alternatives = self._find_alternative_paths(path_id)

        return PruneCandidate(
            path_id=path_id,
            prune_strategy=PruneStrategy.COVERAGE_BASED,
            prune_score=1.0 - score,
            coverage_loss=score,
            risk_impact=self._assess_risk_impact(path_id),
            alternatives=alternatives,
            justification=f"低覆盖评分({score:.2f})，可被其他路径替代",
            preserved_conditions=self._get_preserved_conditions(path_id)
        )

    def _generate_risk_based_candidates(self) -> None:
        """基于风险生成剪枝候选"""
        risk_scores = []

        for path in self.paths:
            path_id = self._get_path_id(path)
            risk = self._calculate_risk_score(path)

            risk_scores.append((path_id, risk))

        risk_scores.sort(key=lambda x: x[1])

        max_prune = int(len(self.paths) * self.config.max_prune_ratio)

        low_risk_threshold = 0.3

        for path_id, risk in risk_scores[:max_prune]:
            if risk < low_risk_threshold:
                candidate = self._create_risk_based_candidate(path_id, risk)
                self.candidates.append(candidate)

    def _calculate_risk_score(self, path) -> float:
        """计算风险评分

        Args:
            path: 路径对象

        Returns:
            float: 风险评分
        """
        risk = 0.5

        func_name = getattr(path, 'function_name', '').lower()

        high_risk_keywords = ['payment', 'auth', 'security', 'transaction']
        for keyword in high_risk_keywords:
            if keyword in func_name:
                risk += 0.3

        if hasattr(path, 'risk_level'):
            risk_map = {'high': 0.8, 'medium': 0.5, 'low': 0.2}
            risk = risk_map.get(path.risk_level, 0.5)

        return min(1.0, risk)

    def _create_risk_based_candidate(self, path_id: str, risk: float) -> PruneCandidate:
        """创建基于风险的剪枝候选

        Args:
            path_id: 路径标识符
            risk: 风险评分

        Returns:
            PruneCandidate: 剪枝候选
        """
        alternatives = self._find_alternative_paths(path_id)

        return PruneCandidate(
            path_id=path_id,
            prune_strategy=PruneStrategy.RISK_BASED,
            prune_score=1.0 - risk,
            coverage_loss=self._estimate_coverage_loss(path_id),
            risk_impact="low",
            alternatives=alternatives,
            justification=f"低风险路径({risk:.2f})，剪枝影响小",
            preserved_conditions=self._get_preserved_conditions(path_id)
        )

    def _generate_similarity_based_candidates(self) -> None:
        """基于相似度生成剪枝候选【V3.1增强】"""
        path_groups = self._group_similar_paths()

        for group in path_groups:
            if len(group) > 1:
                candidates = self._select_prune_from_group(group)
                self.candidates.extend(candidates)

    def _group_similar_paths(self) -> List[List[str]]:
        """将相似路径分组

        Returns:
            List[List[str]]: 路径组列表
        """
        groups = []
        processed = set()

        for path in self.paths:
            path_id = self._get_path_id(path)
            if path_id in processed:
                continue

            group = [path_id]
            processed.add(path_id)

            for other_path in self.paths:
                other_id = self._get_path_id(other_path)
                if other_id in processed:
                    continue

                similarity = self._calculate_path_similarity(path, other_path)
                if similarity >= self.config.similarity_threshold:
                    group.append(other_id)
                    processed.add(other_id)

            if len(group) > 1:
                groups.append(group)

        return groups

    def _calculate_path_similarity(self, path1, path2) -> float:
        """计算路径相似度

        Args:
            path1: 路径1
            path2: 路径2

        Returns:
            float: 相似度评分（0-1）
        """
        nodes1 = set(self._get_path_nodes(path1))
        nodes2 = set(self._get_path_nodes(path2))

        if not nodes1 or not nodes2:
            return 0.0

        intersection = len(nodes1 & nodes2)
        union = len(nodes1 | nodes2)

        if union == 0:
            return 0.0

        return intersection / union

    def _select_prune_from_group(self, group: List[str]) -> List[PruneCandidate]:
        """从组中选择要剪枝的路径

        Args:
            group: 路径组

        Returns:
            List[PruneCandidate]: 剪枝候选列表
        """
        path_values = []
        for path_id in group:
            value = self._calculate_path_value(path_id)
            path_values.append((path_id, value))

        path_values.sort(key=lambda x: x[1], reverse=True)

        keep_count = max(1, len(group) // 3)
        prune_ids = [pv[0] for pv in path_values[keep_count:]]

        candidates = []
        for path_id in prune_ids:
            candidate = PruneCandidate(
                path_id=path_id,
                prune_strategy=PruneStrategy.SIMILARITY_BASED,
                prune_score=0.7,
                coverage_loss=0.1,
                risk_impact="low",
                alternatives=[pid for pid in group if pid != path_id],
                justification=f"与{len(group)-1}个路径相似，保留代表性路径即可",
                preserved_conditions=[]
            )
            candidates.append(candidate)

        return candidates

    def _generate_cost_based_candidates(self) -> None:
        """基于代价生成剪枝候选"""
        cost_scores = []

        for path in self.paths:
            path_id = self._get_path_id(path)
            cost = self._calculate_cost(path)

            cost_scores.append((path_id, cost))

        cost_scores.sort(key=lambda x: x[1], reverse=True)

        max_prune = int(len(self.paths) * self.config.max_prune_ratio)

        for path_id, cost in cost_scores[:max_prune]:
            candidate = self._create_cost_based_candidate(path_id, cost)
            self.candidates.append(candidate)

    def _calculate_cost(self, path) -> float:
        """计算代价

        Args:
            path: 路径对象

        Returns:
            float: 代价评分
        """
        cost = 0.0

        if hasattr(path, 'execution_time'):
            cost += path.execution_time * 0.5

        if hasattr(path, 'length'):
            cost += path.length * 0.01

        if hasattr(path, 'dependencies'):
            cost += len(path.dependencies) * 0.1

        coverage_score = self._calculate_coverage_score(path)
        value_score = 1.0 - coverage_score

        cost += value_score * 0.3

        return cost

    def _create_cost_based_candidate(self, path_id: str, cost: float) -> PruneCandidate:
        """创建基于代价的剪枝候选

        Args:
            path_id: 路径标识符
            cost: 代价评分

        Returns:
            PruneCandidate: 剪枝候选
        """
        alternatives = self._find_alternative_paths(path_id)

        return PruneCandidate(
            path_id=path_id,
            prune_strategy=PruneStrategy.COST_BASED,
            prune_score=min(1.0, cost),
            coverage_loss=self._estimate_coverage_loss(path_id),
            risk_impact=self._assess_risk_impact(path_id),
            alternatives=alternatives,
            justification=f"高代价路径({cost:.2f})，优化测试资源",
            preserved_conditions=self._get_preserved_conditions(path_id)
        )

    def _generate_dominance_based_candidates(self) -> None:
        """基于支配关系生成剪枝候选"""
        dominated_paths = self._find_dominated_paths()

        for dominated, dominator in dominated_paths.items():
            candidate = PruneCandidate(
                path_id=dominated,
                prune_strategy=PruneStrategy.DOMINANCE_BASED,
                prune_score=0.8,
                coverage_loss=0.05,
                risk_impact="low",
                alternatives=[dominator],
                justification=f"被路径{dominator}支配，覆盖可由其替代",
                preserved_conditions=[]
            )
            self.candidates.append(candidate)

    def _find_dominated_paths(self) -> Dict[str, str]:
        """查找被支配的路径

        Returns:
            Dict[str, str]: 被支配路径到支配路径的映射
        """
        dominated = {}

        for path in self.paths:
            path_id = self._get_path_id(path)
            path_nodes = set(self._get_path_nodes(path))

            for other_path in self.paths:
                other_id = self._get_path_id(other_path)
                if path_id == other_id:
                    continue

                other_nodes = set(self._get_path_nodes(other_path))

                if path_nodes.issubset(other_nodes) and len(path_nodes) < len(other_nodes):
                    dominated[path_id] = other_id
                    break

        return dominated

    def _generate_adaptive_candidates(self) -> None:
        """生成自适应剪枝候选【V3.1增强】"""
        coverage_candidates = []
        risk_candidates = []
        similarity_candidates = []

        self._generate_coverage_based_candidates()
        coverage_candidates = list(self.candidates)
        self.candidates.clear()

        self._generate_risk_based_candidates()
        risk_candidates = list(self.candidates)
        self.candidates.clear()

        self._generate_similarity_based_candidates()
        similarity_candidates = list(self.candidates)
        self.candidates.clear()

        combined_scores = defaultdict(lambda: {'score': 0.0, 'strategies': []})

        for candidate in coverage_candidates:
            combined_scores[candidate.path_id]['score'] += candidate.prune_score * 0.4
            combined_scores[candidate.path_id]['strategies'].append(PruneStrategy.COVERAGE_BASED)

        for candidate in risk_candidates:
            combined_scores[candidate.path_id]['score'] += candidate.prune_score * 0.3
            combined_scores[candidate.path_id]['strategies'].append(PruneStrategy.RISK_BASED)

        for candidate in similarity_candidates:
            combined_scores[candidate.path_id]['score'] += candidate.prune_score * 0.3
            combined_scores[candidate.path_id]['strategies'].append(PruneStrategy.SIMILARITY_BASED)

        max_prune = int(len(self.paths) * self.config.max_prune_ratio)

        sorted_candidates = sorted(combined_scores.items(),
                                key=lambda x: x[1]['score'],
                                reverse=True)

        for path_id, scores in sorted_candidates[:max_prune]:
            primary_strategy = scores['strategies'][0] if scores['strategies'] else PruneStrategy.ADAPTIVE

            candidate = PruneCandidate(
                path_id=path_id,
                prune_strategy=primary_strategy,
                prune_score=scores['score'],
                coverage_loss=0.2,
                risk_impact="low",
                alternatives=self._find_alternative_paths(path_id),
                justification=f"自适应策略评分: {scores['score']:.2f}",
                preserved_conditions=[]
            )
            self.candidates.append(candidate)

    def _find_alternative_paths(self, path_id: str) -> List[str]:
        """查找替代路径

        Args:
            path_id: 路径标识符

        Returns:
            List[str]: 替代路径列表
        """
        alternatives = []

        for path in self.paths:
            pid = self._get_path_id(path)
            if pid != path_id:
                alternatives.append(pid)
                if len(alternatives) >= 3:
                    break

        return alternatives

    def _calculate_path_value(self, path_id: str) -> float:
        """计算路径价值

        Args:
            path_id: 路径标识符

        Returns:
            float: 路径价值
        """
        for priority in self.priorities:
            if priority.path_id == path_id:
                return priority.priority_score

        for path in self.paths:
            if self._get_path_id(path) == path_id:
                coverage = self._calculate_coverage_score(path)
                risk = self._calculate_risk_score(path)
                return coverage * 0.6 + risk * 0.4

        return 0.5

    def _estimate_coverage_loss(self, path_id: str) -> float:
        """估算覆盖损失

        Args:
            path_id: 路径标识符

        Returns:
            float: 覆盖损失
        """
        for path in self.paths:
            if self._get_path_id(path) == path_id:
                return 1.0 - self._calculate_coverage_score(path)

        return 0.1

    def _assess_risk_impact(self, path_id: str) -> str:
        """评估风险影响

        Args:
            path_id: 路径标识符

        Returns:
            str: 风险影响等级
        """
        for priority in self.priorities:
            if priority.path_id == path_id:
                if priority.priority_level.name in ['CRITICAL', 'HIGH']:
                    return "high"
                elif priority.priority_level.name == 'MEDIUM':
                    return "medium"

        return "low"

    def _get_preserved_conditions(self, path_id: str) -> List[str]:
        """获取保留条件

        Args:
            path_id: 路径标识符

        Returns:
            List[str]: 保留条件列表
        """
        conditions = []

        for priority in self.priorities:
            if priority.path_id == path_id:
                if priority.preserved_conditions:
                    return priority.preserved_conditions

        coverage_loss = self._estimate_coverage_loss(path_id)
        if coverage_loss > 0.3:
            conditions.append("高覆盖损失风险")

        risk = self._assess_risk_impact(path_id)
        if risk == "high":
            conditions.append("高风险路径")

        return conditions

    def _apply_pruning_strategy(self) -> None:
        """应用剪枝策略"""
        self.pruned_path_ids = set()

        sorted_candidates = sorted(self.candidates,
                                  key=lambda c: c.prune_score,
                                  reverse=True)

        max_prune_count = int(len(self.paths) * self.config.max_prune_ratio)

        for candidate in sorted_candidates:
            if len(self.pruned_path_ids) >= max_prune_count:
                break

            if self.config.preserve_critical:
                if candidate.risk_impact == "high":
                    continue

            self.pruned_path_ids.add(candidate.path_id)

    def _ensure_critical_paths_preserved(self) -> None:
        """确保关键路径被保留"""
        if not self.config.preserve_critical:
            return

        for priority in self.priorities:
            if priority.priority_level.name == 'CRITICAL':
                if priority.path_id in self.pruned_path_ids:
                    self.pruned_path_ids.remove(priority.path_id)

                    for candidate in self.candidates:
                        if candidate.path_id == priority.path_id:
                            self.candidates.remove(candidate)
                            break

    def _create_prune_result(self) -> SmartPruneResult:
        """创建剪枝结果

        Returns:
            SmartPruneResult: 智能剪枝结果
        """
        result = SmartPruneResult(
            original_count=len(self.paths),
            pruned_count=len(self.pruned_path_ids),
            retained_count=len(self.paths) - len(self.pruned_path_ids),
            strategy_used=self.config.strategy.name
        )

        result.prune_ratio = len(self.pruned_path_ids) / len(self.paths) if self.paths else 0

        result.candidates = [c for c in self.candidates
                           if c.path_id in self.pruned_path_ids]

        result.retained_paths = [self._get_path_id(p) for p in self.paths
                                if self._get_path_id(p) not in self.pruned_path_ids]

        result.coverage_metrics = self._calculate_coverage_metrics()

        result.pruning_report = self._generate_pruning_report()

        if result.prune_ratio > 0.8:
            result.warnings.append("剪枝比例过高，可能影响测试覆盖")

        result.metadata = {
            'strategy': self.config.strategy.name,
            'scope': self.config.scope.name,
            'max_prune_ratio': self.config.max_prune_ratio,
            'coverage_threshold': self.config.min_coverage_threshold
        }

        return result

    def _calculate_coverage_metrics(self) -> Dict[str, Any]:
        """计算覆盖指标

        Returns:
            Dict[str, Any]: 覆盖指标
        """
        retained_paths = [p for p in self.paths
                        if self._get_path_id(p) not in self.pruned_path_ids]

        if not retained_paths:
            return {
                'retained_coverage': 0.0,
                'estimated_coverage_loss': 1.0
            }

        total_coverage = sum(self._calculate_coverage_score(p) for p in retained_paths)
        avg_coverage = total_coverage / len(retained_paths)

        pruned_coverage = 0.0
        for path in self.paths:
            if self._get_path_id(path) in self.pruned_path_ids:
                pruned_coverage += self._calculate_coverage_score(path)

        estimated_loss = pruned_coverage / len(self.paths) if self.paths else 0

        return {
            'retained_coverage': avg_coverage,
            'estimated_coverage_loss': estimated_loss,
            'retained_path_count': len(retained_paths),
            'pruned_path_count': len(self.pruned_path_ids)
        }

    def _generate_pruning_report(self) -> Dict[str, Any]:
        """生成剪枝报告

        Returns:
            Dict[str, Any]: 剪枝报告
        """
        report = {
            'summary': {
                'original_paths': len(self.paths),
                'pruned_paths': len(self.pruned_path_ids),
                'retained_paths': len(self.paths) - len(self.pruned_path_ids),
                'prune_ratio': self.prune_result.prune_ratio
            },
            'strategy': {
                'type': self.config.strategy.name,
                'scope': self.config.scope.name,
                'max_ratio': self.config.max_prune_ratio
            },
            'coverage': self.prune_result.coverage_metrics,
            'by_strategy': self._count_by_strategy(),
            'risk_impact': self._assess_overall_risk_impact()
        }

        return report

    def _count_by_strategy(self) -> Dict[str, int]:
        """按策略统计

        Returns:
            Dict[str, int]: 各策略剪枝数量
        """
        counts = defaultdict(int)
        for candidate in self.candidates:
            if candidate.path_id in self.pruned_path_ids:
                counts[candidate.prune_strategy.name] += 1
        return dict(counts)

    def _assess_overall_risk_impact(self) -> str:
        """评估整体风险影响

        Returns:
            str: 风险影响等级
        """
        high_impact = sum(1 for c in self.candidates
                        if c.path_id in self.pruned_path_ids and c.risk_impact == "high")

        if high_impact > 0:
            return "high"

        medium_impact = sum(1 for c in self.candidates
                          if c.path_id in self.pruned_path_ids and c.risk_impact == "medium")

        if medium_impact > len(self.pruned_path_ids) * 0.3:
            return "medium"

        return "low"

    def _get_path_id(self, path) -> str:
        """获取路径标识符

        Args:
            path: 路径对象

        Returns:
            str: 路径标识符
        """
        return getattr(path, 'path_id', '') or getattr(path, 'execution_id', str(id(path)))

    def _get_path_nodes(self, path) -> List[str]:
        """获取路径节点

        Args:
            path: 路径对象

        Returns:
            List[str]: 节点列表
        """
        if hasattr(path, 'nodes'):
            return path.nodes

        return []

    def _get_statistics(self) -> Dict[str, Any]:
        """获取统计信息

        Returns:
            Dict[str, Any]: 统计信息
        """
        if not self.prune_result:
            return {}

        return {
            'original_count': self.prune_result.original_count,
            'pruned_count': self.prune_result.pruned_count,
            'retained_count': self.prune_result.retained_count,
            'prune_ratio': self.prune_result.prune_ratio,
            'strategy_used': self.prune_result.strategy_used,
            'coverage_metrics': self.prune_result.coverage_metrics
        }

    def get_retained_paths(self) -> List[str]:
        """获取保留的路径列表

        Returns:
            List[str]: 保留路径标识符
        """
        return self.prune_result.retained_paths if self.prune_result else []

    def get_pruned_paths(self) -> List[str]:
        """获取剪枝的路径列表

        Returns:
            List[str]: 剪枝路径标识符
        """
        return list(self.pruned_path_ids) if hasattr(self, 'pruned_path_ids') else []

    def export_pruning_report(self) -> Dict[str, Any]:
        """导出剪枝报告

        Returns:
            Dict[str, Any]: 剪枝报告
        """
        return self.prune_result.pruning_report if self.prune_result else {}

    def suggest_adjustments(self) -> List[str]:
        """建议调整

        Returns:
            List[str]: 调整建议
        """
        suggestions = []

        if self.prune_result.prune_ratio > 0.7:
            suggestions.append("考虑降低剪枝比例以保留更多覆盖")

        if self.prune_result.coverage_metrics.get('estimated_coverage_loss', 0) > 0.3:
            suggestions.append("覆盖损失较高，建议增加高价值路径的保留")

        if self._assess_overall_risk_impact() == "high":
            suggestions.append("风险影响较高，确保关键业务路径未被剪枝")

        return suggestions
