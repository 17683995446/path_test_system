"""
Layer 31: ExplosionProtectionLayer - 路径爆炸防护层【V3.1升级】

本层负责防止路径数量指数级爆炸，通过智能限制、渐进式探索和
自适应策略，控制路径数量的增长在合理范围内。
V3.1升级增强了多层防护机制和动态调整能力。
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import deque


class ExplosionRisk(Enum):
    """爆炸风险等级枚举"""
    SAFE = auto()
    WARNING = auto()
    DANGER = auto()
    CRITICAL = auto()


class ProtectionStrategy(Enum):
    """防护策略枚举"""
    DEPTH_LIMIT = auto()
    WIDTH_LIMIT = auto()
    LOOP_LIMIT = auto()
    BRANCH_LIMIT = auto()
    SAMPLING = auto()
    CLUSTERING = auto()
    ADAPTIVE = auto()


@dataclass
class ProtectionConfig:
    """防护配置

    Attributes:
        max_paths: 最大路径数
        max_depth: 最大深度
        max_width: 最大宽度
        max_loop_iterations: 最大循环迭代
        explosion_threshold: 爆炸阈值
        enable_adaptive: 是否启用自适应
        enable_clustering: 是否启用聚类
        sampling_rate: 采样率
        warning_ratio: 警告比例
    """
    max_paths: int = 10000
    max_depth: int = 50
    max_width: int = 100
    max_loop_iterations: int = 5
    explosion_threshold: float = 0.8
    enable_adaptive: bool = True
    enable_clustering: bool = True
    sampling_rate: float = 0.5
    warning_ratio: float = 0.7


@dataclass
class PathGroup:
    """路径组信息

    Attributes:
        group_id: 组标识符
        representative_path: 代表路径
        member_count: 成员数量
        characteristics: 特征
        coverage_potential: 覆盖潜力
        test_value: 测试价值
    """
    group_id: str
    representative_path: str
    member_count: int = 1
    characteristics: Dict[str, Any] = field(default_factory=dict)
    coverage_potential: float = 0.5
    test_value: float = 0.5

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "group_id": self.group_id,
            "representative_path": self.representative_path,
            "member_count": self.member_count,
            "characteristics": self.characteristics,
            "coverage_potential": self.coverage_potential,
            "test_value": self.test_value
        }


@dataclass
class ExplosionRiskAssessment:
    """爆炸风险评估

    Attributes:
        current_risk: 当前风险等级
        path_count: 当前路径数
        growth_rate: 增长率
        projected_count: 预计路径数
        risk_factors: 风险因素
        mitigation_suggestions: 缓解建议
        confidence: 置信度
    """
    current_risk: ExplosionRisk
    path_count: int
    growth_rate: float = 0.0
    projected_count: int = 0
    risk_factors: List[str] = field(default_factory=list)
    mitigation_suggestions: List[str] = field(default_factory=list)
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "current_risk": self.current_risk.name,
            "path_count": self.path_count,
            "growth_rate": self.growth_rate,
            "projected_count": self.projected_count,
            "risk_factors": self.risk_factors,
            "mitigation_suggestions": self.mitigation_suggestions,
            "confidence": self.confidence
        }


@dataclass
class ProtectionResult:
    """防护结果

    Attributes:
        original_count: 原始路径数
        protected_count: 保护后路径数
        reduced_count: 减少路径数
        reduction_ratio: 减少比例
        risk_assessment: 风险评估
        applied_strategies: 应用的策略
        path_groups: 路径组
        retained_paths: 保留路径
        statistics: 统计信息
        warnings: 警告
        metadata: 元信息
    """
    original_count: int = 0
    protected_count: int = 0
    reduced_count: int = 0
    reduction_ratio: float = 0.0
    risk_assessment: Optional[ExplosionRiskAssessment] = None
    applied_strategies: List[str] = field(default_factory=list)
    path_groups: List[PathGroup] = field(default_factory=list)
    retained_paths: List[str] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "original_count": self.original_count,
            "protected_count": self.protected_count,
            "reduced_count": self.reduced_count,
            "reduction_ratio": self.reduction_ratio,
            "risk_assessment": self.risk_assessment.to_dict() if self.risk_assessment else None,
            "applied_strategies": self.applied_strategies,
            "path_groups": [g.to_dict() for g in self.path_groups],
            "retained_paths": self.retained_paths,
            "statistics": self.statistics,
            "warnings": self.warnings,
            "metadata": self.metadata
        }


class ExplosionProtectionLayer:
    """路径爆炸防护层【V3.1升级】

    功能描述：
        - 监控和控制路径数量的增长
        - 评估路径爆炸的风险等级
        - 应用多层防护策略
        - 支持自适应策略调整
        - 路径聚类和代表性选择
        - 生成防护报告和警告
        - 保障关键路径不被丢弃

    输入类型：
        - 路径列表（List[Path] 或 List[EnumeratedPath]）
        - 控制流图（ControlFlowGraph，可选）
        - 防护配置（ProtectionConfig，可选）
        - 上下文信息（可选）

    输出类型：
        - ProtectionResult: 防护结果
        - ExplosionRiskAssessment: 爆炸风险评估
        - List[PathGroup]: 路径组列表
        - 统计信息和警告

    使用场景：
        - 防止循环导致的路径爆炸
        - 控制复杂CFG的路径数量
        - 大规模测试的路径管理
        - 资源受限环境的路径优化
        - 持续集成中的路径控制

    V3.1升级点：
        - 增强多层防护机制
        - 支持动态风险评估
        - 增加路径聚类能力
        - 提供更智能的代表性选择
        - 支持增量式防护
    """

    description: str = "路径爆炸防护层【V3.1升级】- 防止路径数量指数级爆炸"
    input_type: str = "List[Path]、ControlFlowGraph和ProtectionConfig"
    output_type: str = "ProtectionResult和ExplosionRiskAssessment"

    def __init__(self):
        """初始化路径爆炸防护层"""
        self.paths = []
        self.cfg = None
        self.config = ProtectionConfig()
        self.risk_assessment = None
        self.path_groups = []
        self.protection_result = None
        self.path_history = []
        self.growth_threshold = 1.5

    def set_config(self, config: ProtectionConfig) -> None:
        """设置防护配置

        Args:
            config: 防护配置对象
        """
        self.config = config

    def process(self, context) -> ProtectionResult:
        """处理路径，执行爆炸防护

        Args:
            context: PipelineContext对象，包含路径和配置信息

        Returns:
            ProtectionResult: 防护结果

        Raises:
            ValueError: 当输入数据不足时
        """
        if not context.has('paths') and not context.has('enumerated_paths'):
            if not context.has('execution_paths'):
                raise ValueError("ExplosionProtectionLayer: 缺少路径数据")

        if context.has('paths'):
            self.paths = context.get('paths')
        elif context.has('enumerated_paths'):
            self.paths = context.get('enumerated_paths')
        elif context.has('execution_paths'):
            self.paths = context.get('execution_paths')

        if context.has('cfg_graphs'):
            self.cfg = context.get('cfg_graphs')
        elif context.has('cfg'):
            self.cfg = context.get('cfg')

        if context.has('protection_config'):
            self.config = context.get('protection_config')

        self._assess_explosion_risk()

        if self.config.enable_adaptive:
            self._adjust_config_adaptively()

        self._apply_protection_strategies()

        if self.config.enable_clustering:
            self._perform_path_clustering()

        self._select_representative_paths()

        self.protection_result = self._create_protection_result()

        context.set('explosion_risk_assessment', self.risk_assessment)
        context.set('path_groups', self.path_groups)
        context.set('protection_result', self.protection_result)
        context.set('explosion_protection_complete', True)
        context.set('protection_statistics', self._get_statistics())

        return self.protection_result

    def _assess_explosion_risk(self) -> ExplosionRiskAssessment:
        """评估爆炸风险"""
        path_count = len(self.paths)

        risk_factors = []

        if path_count > self.config.max_paths:
            risk_factors.append("路径数量超过限制")
            projected = path_count * 2
        else:
            projected = path_count

        growth_rate = self._calculate_growth_rate()

        if growth_rate > self.growth_threshold:
            risk_factors.append(f"增长率过高: {growth_rate:.2f}")

        loop_risk = self._assess_loop_risk()
        if loop_risk > 0:
            risk_factors.append(f"循环风险: {loop_risk:.2f}")
            projected = int(projected * (1 + loop_risk))

        branch_risk = self._assess_branch_risk()
        if branch_risk > 0:
            risk_factors.append(f"分支风险: {branch_risk:.2f}")
            projected = int(projected * (1 + branch_risk))

        max_risk = max(loop_risk, branch_risk)
        if max_risk < 0.3:
            current_risk = ExplosionRisk.SAFE
        elif max_risk < 0.5:
            current_risk = ExplosionRisk.WARNING
        elif max_risk < 0.7:
            current_risk = ExplosionRisk.DANGER
        else:
            current_risk = ExplosionRisk.CRITICAL

        projected_count = min(projected, self.config.max_paths * 10)

        self.risk_assessment = ExplosionRiskAssessment(
            current_risk=current_risk,
            path_count=path_count,
            growth_rate=growth_rate,
            projected_count=projected_count,
            risk_factors=risk_factors,
            mitigation_suggestions=self._generate_mitigation_suggestions(current_risk),
            confidence=self._calculate_assessment_confidence()
        )

        return self.risk_assessment

    def _calculate_growth_rate(self) -> float:
        """计算增长率

        Returns:
            float: 增长率
        """
        if len(self.path_history) < 2:
            return 1.0

        recent_counts = self.path_history[-5:]

        if len(recent_counts) < 2:
            return 1.0

        growth = recent_counts[-1] / recent_counts[0] if recent_counts[0] > 0 else 1.0

        return growth

    def _assess_loop_risk(self) -> float:
        """评估循环风险

        Returns:
            float: 循环风险评分
        """
        loop_risk = 0.0

        for path in self.paths[:100]:
            if hasattr(path, 'metadata'):
                if path.metadata.get('has_loop'):
                    loop_risk += 0.1

            if hasattr(path, 'loop_count'):
                if path.loop_count > self.config.max_loop_iterations:
                    loop_risk += 0.15

        if hasattr(self.cfg, 'loops') and self.cfg.loops:
            loop_risk += len(self.cfg.loops) * 0.05

        return min(1.0, loop_risk)

    def _assess_branch_risk(self) -> float:
        """评估分支风险

        Returns:
            float: 分支风险评分
        """
        branch_risk = 0.0

        for path in self.paths[:100]:
            if hasattr(path, 'branch_count'):
                if path.branch_count > 10:
                    branch_risk += 0.1

        if hasattr(self.cfg, 'nodes'):
            branch_nodes = sum(1 for node in self.cfg.nodes.values()
                            if hasattr(node, 'node_type') and node.node_type.value == 4)
            if branch_nodes > 20:
                branch_risk += 0.2

        return min(1.0, branch_risk)

    def _generate_mitigation_suggestions(self, risk: ExplosionRisk) -> List[str]:
        """生成缓解建议

        Args:
            risk: 风险等级

        Returns:
            List[str]: 缓解建议列表
        """
        suggestions = []

        if risk in [ExplosionRisk.DANGER, ExplosionRisk.CRITICAL]:
            suggestions.append("建议启用深度限制策略")
            suggestions.append("考虑启用路径聚类")
            suggestions.append("启用自适应调整")

        if risk == ExplosionRisk.CRITICAL:
            suggestions.append("严重警告：必须立即采取防护措施")
            suggestions.append("建议启用采样策略")

        if risk == ExplosionRisk.WARNING:
            suggestions.append("建议监控路径增长")
            suggestions.append("考虑启用宽度限制")

        if risk == ExplosionRisk.SAFE:
            suggestions.append("当前风险可控，继续监控")

        return suggestions

    def _calculate_assessment_confidence(self) -> float:
        """计算评估置信度

        Returns:
            float: 置信度
        """
        confidence = 0.7

        if hasattr(self.cfg, 'nodes'):
            confidence += 0.1

        if len(self.path_history) >= 3:
            confidence += 0.1

        return min(1.0, confidence)

    def _adjust_config_adaptively(self) -> None:
        """自适应调整配置【V3.1增强】"""
        if not self.risk_assessment:
            return

        risk = self.risk_assessment.current_risk

        if risk == ExplosionRisk.CRITICAL:
            self.config.max_paths = max(1000, int(self.config.max_paths * 0.5))
            self.config.max_depth = max(20, int(self.config.max_depth * 0.7))
            self.config.max_loop_iterations = max(2, int(self.config.max_loop_iterations * 0.5))
        elif risk == ExplosionRisk.DANGER:
            self.config.max_paths = max(3000, int(self.config.max_paths * 0.7))
            self.config.max_depth = max(30, int(self.config.max_depth * 0.8))
            self.config.max_loop_iterations = max(3, int(self.config.max_loop_iterations * 0.7))
        elif risk == ExplosionRisk.WARNING:
            self.config.max_paths = max(5000, int(self.config.max_paths * 0.9))
        else:
            pass

    def _apply_protection_strategies(self) -> None:
        """应用防护策略"""
        self.applied_strategies = []
        self.protected_paths = list(self.paths)

        if self.risk_assessment.current_risk in [ExplosionRisk.DANGER, ExplosionRisk.CRITICAL]:
            self._apply_depth_limit()
            self._apply_width_limit()
            self._apply_loop_limit()
            self._apply_sampling()

        elif self.risk_assessment.current_risk == ExplosionRisk.WARNING:
            self._apply_width_limit()
            if len(self.protected_paths) > self.config.max_paths:
                self._apply_sampling()

        else:
            if len(self.protected_paths) > self.config.max_paths:
                self._apply_width_limit()

    def _apply_depth_limit(self) -> None:
        """应用深度限制"""
        original_count = len(self.protected_paths)

        self.protected_paths = [
            path for path in self.protected_paths
            if self._check_depth_constraint(path)
        ]

        reduced = original_count - len(self.protected_paths)
        if reduced > 0:
            self.applied_strategies.append(f"DEPTH_LIMIT: 减少{reduced}条路径")

    def _check_depth_constraint(self, path) -> bool:
        """检查深度约束

        Args:
            path: 路径对象

        Returns:
            bool: 是否满足约束
        """
        if hasattr(path, 'length'):
            return path.length <= self.config.max_depth

        if hasattr(path, 'nodes'):
            return len(path.nodes) <= self.config.max_depth

        return True

    def _apply_width_limit(self) -> None:
        """应用宽度限制"""
        original_count = len(self.protected_paths)

        max_width = min(self.config.max_width, self.config.max_paths // 10)

        if len(self.protected_paths) > max_width:
            scored_paths = []
            for path in self.protected_paths:
                score = self._calculate_path_score(path)
                scored_paths.append((path, score))

            scored_paths.sort(key=lambda x: x[1], reverse=True)

            self.protected_paths = [p for p, _ in scored_paths[:max_width]]

        reduced = original_count - len(self.protected_paths)
        if reduced > 0:
            self.applied_strategies.append(f"WIDTH_LIMIT: 减少{reduced}条路径")

    def _apply_loop_limit(self) -> None:
        """应用循环限制"""
        original_count = len(self.protected_paths)

        self.protected_paths = [
            path for path in self.protected_paths
            if self._check_loop_constraint(path)
        ]

        reduced = original_count - len(self.protected_paths)
        if reduced > 0:
            self.applied_strategies.append(f"LOOP_LIMIT: 减少{reduced}条路径")

    def _check_loop_constraint(self, path) -> bool:
        """检查循环约束

        Args:
            path: 路径对象

        Returns:
            bool: 是否满足约束
        """
        if hasattr(path, 'loop_count'):
            return path.loop_count <= self.config.max_loop_iterations

        return True

    def _apply_sampling(self) -> None:
        """应用采样策略"""
        original_count = len(self.protected_paths)

        if len(self.protected_paths) > self.config.max_paths:
            sample_size = int(self.config.max_paths * self.config.sampling_rate)

            scored_paths = []
            for path in self.protected_paths:
                score = self._calculate_path_score(path)
                scored_paths.append((path, score))

            scored_paths.sort(key=lambda x: x[1], reverse=True)

            sampled = scored_paths[:sample_size]

            remaining_slots = self.config.max_paths - len(sampled)
            if remaining_slots > 0:
                for path, score in scored_paths[sample_size:sample_size + remaining_slots]:
                    sampled.append((path, score))

            self.protected_paths = [p for p, _ in sampled]

        reduced = original_count - len(self.protected_paths)
        if reduced > 0:
            self.applied_strategies.append(f"SAMPLING: 减少{reduced}条路径")

    def _calculate_path_score(self, path) -> float:
        """计算路径评分

        Args:
            path: 路径对象

        Returns:
            float: 路径评分
        """
        score = 0.5

        if hasattr(path, 'coverage_potential'):
            score = path.coverage_potential

        if hasattr(path, 'test_value'):
            score = max(score, path.test_value)

        if hasattr(path, 'complexity'):
            score += min(0.2, path.complexity / 100.0)

        if hasattr(path, 'branch_count'):
            score += min(0.1, path.branch_count / 50.0)

        return min(1.0, score)

    def _perform_path_clustering(self) -> None:
        """执行路径聚类【V3.1增强】"""
        self.path_groups = []

        if not self.protected_paths:
            return

        clusters = self._create_clusters()

        group_id = 0
        for cluster_paths in clusters.values():
            if not cluster_paths:
                continue

            representative = self._select_cluster_representative(cluster_paths)

            group = PathGroup(
                group_id=f"group_{group_id}",
                representative_path=self._get_path_id(representative),
                member_count=len(cluster_paths),
                characteristics=self._extract_cluster_characteristics(cluster_paths),
                coverage_potential=sum(self._calculate_path_score(p) for p in cluster_paths) / len(cluster_paths),
                test_value=sum(getattr(p, 'test_value', 0.5) for p in cluster_paths) / len(cluster_paths)
            )

            self.path_groups.append(group)
            group_id += 1

    def _create_clusters(self) -> Dict[str, List]:
        """创建聚类

        Returns:
            Dict[str, List]: 聚类结果
        """
        clusters = {}

        for path in self.protected_paths:
            cluster_key = self._determine_cluster_key(path)

            if cluster_key not in clusters:
                clusters[cluster_key] = []

            clusters[cluster_key].append(path)

        return clusters

    def _determine_cluster_key(self, path) -> str:
        """确定聚类键

        Args:
            path: 路径对象

        Returns:
            str: 聚类键
        """
        func_name = getattr(path, 'function_name', 'unknown')

        if hasattr(path, 'complexity'):
            if path.complexity < 5:
                complexity_level = 'low'
            elif path.complexity < 15:
                complexity_level = 'medium'
            else:
                complexity_level = 'high'
        else:
            complexity_level = 'unknown'

        return f"{func_name}_{complexity_level}"

    def _select_cluster_representative(self, cluster_paths: List) -> Any:
        """选择聚类代表

        Args:
            cluster_paths: 聚类路径列表

        Returns:
            代表路径对象
        """
        if not cluster_paths:
            return None

        return max(cluster_paths, key=lambda p: self._calculate_path_score(p))

    def _extract_cluster_characteristics(self, cluster_paths: List) -> Dict[str, Any]:
        """提取聚类特征

        Args:
            cluster_paths: 聚类路径列表

        Returns:
            Dict[str, Any]: 聚类特征
        """
        if not cluster_paths:
            return {}

        avg_length = sum(
            getattr(p, 'length', 0) or (len(p.nodes) if hasattr(p, 'nodes') else 0)
            for p in cluster_paths
        ) / len(cluster_paths)

        avg_complexity = sum(
            getattr(p, 'complexity', 0)
            for p in cluster_paths
        ) / len(cluster_paths)

        characteristics = {
            'size': len(cluster_paths),
            'avg_length': avg_length,
            'avg_complexity': avg_complexity
        }

        return characteristics

    def _select_representative_paths(self) -> None:
        """选择代表性路径"""
        self.retained_path_ids = []

        if self.path_groups:
            for group in self.path_groups:
                self.retained_path_ids.append(group.representative_path)

        else:
            for path in self.protected_paths[:self.config.max_paths]:
                self.retained_path_ids.append(self._get_path_id(path))

    def _create_protection_result(self) -> ProtectionResult:
        """创建防护结果

        Returns:
            ProtectionResult: 防护结果
        """
        result = ProtectionResult(
            original_count=len(self.paths),
            protected_count=len(self.retained_path_ids),
            reduced_count=len(self.paths) - len(self.retained_path_ids),
            risk_assessment=self.risk_assessment,
            applied_strategies=self.applied_strategies,
            path_groups=self.path_groups,
            retained_paths=self.retained_path_ids
        )

        result.reduction_ratio = result.reduced_count / len(self.paths) if self.paths else 0

        result.statistics = self._compute_statistics()

        if result.reduction_ratio > 0.8:
            result.warnings.append("路径减少超过80%，可能影响测试覆盖")

        if self.risk_assessment.current_risk == ExplosionRisk.CRITICAL:
            result.warnings.append("检测到严重路径爆炸风险，已采取紧急防护措施")

        result.metadata = {
            'config': {
                'max_paths': self.config.max_paths,
                'max_depth': self.config.max_depth,
                'max_width': self.config.max_width,
                'max_loop_iterations': self.config.max_loop_iterations
            },
            'risk_level': self.risk_assessment.current_risk.name,
            'cluster_count': len(self.path_groups),
            'protection_efficiency': self._calculate_protection_efficiency()
        }

        return result

    def _compute_statistics(self) -> Dict[str, Any]:
        """计算统计信息

        Returns:
            Dict[str, Any]: 统计信息
        """
        stats = {
            'original_count': len(self.paths),
            'protected_count': len(self.protected_paths),
            'retained_count': len(self.retained_path_ids),
            'reduction_ratio': self._calculate_reduction_ratio(),
            'applied_strategies': len(self.applied_strategies),
            'cluster_count': len(self.path_groups)
        }

        if self.path_groups:
            total_members = sum(g.member_count for g in self.path_groups)
            stats['avg_group_size'] = total_members / len(self.path_groups)

        stats['risk_assessment'] = {
            'risk_level': self.risk_assessment.current_risk.name,
            'growth_rate': self.risk_assessment.growth_rate,
            'projected_count': self.risk_assessment.projected_count
        }

        return stats

    def _calculate_reduction_ratio(self) -> float:
        """计算减少比例

        Returns:
            float: 减少比例
        """
        if len(self.paths) == 0:
            return 0.0

        return (len(self.paths) - len(self.retained_path_ids)) / len(self.paths)

    def _calculate_protection_efficiency(self) -> float:
        """计算防护效率

        Returns:
            float: 防护效率
        """
        if not self.path_groups:
            return 0.0

        coverage_score = sum(g.coverage_potential * g.member_count for g in self.path_groups)
        max_coverage = len(self.paths)

        efficiency = coverage_score / max_coverage if max_coverage > 0 else 0

        return min(1.0, efficiency)

    def _get_path_id(self, path) -> str:
        """获取路径标识符

        Args:
            path: 路径对象

        Returns:
            str: 路径标识符
        """
        return getattr(path, 'path_id', '') or getattr(path, 'execution_id', str(id(path)))

    def _get_statistics(self) -> Dict[str, Any]:
        """获取统计信息

        Returns:
            Dict[str, Any]: 统计信息
        """
        if not self.protection_result:
            return {}

        return {
            'original_count': self.protection_result.original_count,
            'protected_count': self.protection_result.protected_count,
            'retained_count': self.protection_result.retained_count,
            'reduction_ratio': self.protection_result.reduction_ratio,
            'risk_level': self.risk_assessment.current_risk.name if self.risk_assessment else 'unknown',
            'applied_strategies': self.protection_result.applied_strategies,
            'cluster_count': len(self.path_groups)
        }

    def get_protected_paths(self) -> List[str]:
        """获取保护的路径列表

        Returns:
            List[str]: 保护路径标识符
        """
        return self.retained_path_ids

    def get_path_groups(self) -> List[PathGroup]:
        """获取路径组列表

        Returns:
            List[PathGroup]: 路径组列表
        """
        return self.path_groups

    def get_risk_assessment(self) -> ExplosionRiskAssessment:
        """获取风险评估

        Returns:
            ExplosionRiskAssessment: 风险评估
        """
        return self.risk_assessment

    def export_protection_report(self) -> Dict[str, Any]:
        """导出防护报告

        Returns:
            Dict[str, Any]: 防护报告
        """
        return {
            'summary': {
                'original_paths': len(self.paths),
                'protected_paths': len(self.retained_path_ids),
                'reduction_ratio': self._calculate_reduction_ratio()
            },
            'risk_assessment': self.risk_assessment.to_dict() if self.risk_assessment else None,
            'applied_strategies': self.applied_strategies,
            'path_groups': [g.to_dict() for g in self.path_groups],
            'statistics': self.protection_result.statistics if self.protection_result else {},
            'warnings': self.protection_result.warnings if self.protection_result else []
        }

    def suggest_relaxation(self) -> List[str]:
        """建议放宽防护

        Returns:
            List[str]: 放宽建议
        """
        suggestions = []

        if self._calculate_reduction_ratio() > 0.7:
            suggestions.append("路径减少过多，建议增加max_paths限制")
            suggestions.append("考虑降低采样率以保留更多路径")

        if self.risk_assessment and self.risk_assessment.current_risk == ExplosionRisk.SAFE:
            suggestions.append("当前风险较低，可以逐步放宽限制")
            suggestions.append("建议渐进式增加max_paths和max_depth")

        return suggestions
