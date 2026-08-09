"""
Layer 29: PathPriorityLayer - 路径优先级排序层

本层负责对测试路径进行优先级排序，基于多维度因素
综合评估路径的测试价值，确定测试用例生成顺序。
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import defaultdict


class PriorityFactor(Enum):
    """优先级因素枚举"""
    COVERAGE_IMPACT = auto()
    RISK_LEVEL = auto()
    COMPLEXITY = auto()
    BUSINESS_VALUE = auto()
    EXECUTION_TIME = auto()
    DEPENDENCY_COUNT = auto()
    ERROR_FREQUENCY = auto()
    MAINTENANCE_FREQUENCY = auto()
    TEST_HISTORY = auto()
    CODE_CHANGE_FREQUENCY = auto()


class PriorityLevel(Enum):
    """优先级级别枚举"""
    CRITICAL = auto()
    HIGH = auto()
    MEDIUM = auto()
    LOW = auto()
    MINIMAL = auto()


@dataclass
class PathPriority:
    """路径优先级信息

    Attributes:
        path_id: 路径标识符
        priority_level: 优先级级别
        priority_score: 优先级评分
        factor_scores: 各因素评分
        ranking: 排名
        estimated_time: 预估测试时间
        coverage_gain: 预计覆盖率提升
        risk_assessment: 风险评估
        dependencies: 依赖关系
        execution_order: 执行顺序
        reasoning: 优先级推理
    """
    path_id: str
    priority_level: PriorityLevel
    priority_score: float = 0.0
    factor_scores: Dict[str, float] = field(default_factory=dict)
    ranking: int = 0
    estimated_time: float = 0.0
    coverage_gain: float = 0.0
    risk_assessment: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    execution_order: int = 0
    reasoning: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "path_id": self.path_id,
            "priority_level": self.priority_level.name,
            "priority_score": self.priority_score,
            "factor_scores": self.factor_scores,
            "ranking": self.ranking,
            "estimated_time": self.estimated_time,
            "coverage_gain": self.coverage_gain,
            "risk_assessment": self.risk_assessment,
            "dependencies": self.dependencies,
            "execution_order": self.execution_order,
            "reasoning": self.reasoning
        }


@dataclass
class PrioritizationResult:
    """优先级排序结果

    Attributes:
        total_paths: 总路径数
        prioritized_paths: 优先级排序后的路径列表
        priority_distribution: 优先级分布
        execution_plan: 执行计划
        batching_strategy: 批次策略
        statistics: 统计信息
        recommendations: 建议
        metadata: 元信息
    """
    total_paths: int = 0
    prioritized_paths: List[PathPriority] = field(default_factory=list)
    priority_distribution: Dict[str, int] = field(default_factory=dict)
    execution_plan: List[List[str]] = field(default_factory=list)
    batching_strategy: Dict[str, Any] = field(default_factory=dict)
    statistics: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "total_paths": self.total_paths,
            "prioritized_paths": [p.to_dict() for p in self.prioritized_paths],
            "priority_distribution": self.priority_distribution,
            "execution_plan": self.execution_plan,
            "batching_strategy": self.batching_strategy,
            "statistics": self.statistics,
            "recommendations": self.recommendations,
            "metadata": self.metadata
        }

    def get_critical_paths(self) -> List[PathPriority]:
        """获取关键路径

        Returns:
            List[PathPriority]: 关键路径列表
        """
        return [p for p in self.prioritized_paths
                if p.priority_level == PriorityLevel.CRITICAL]

    def get_high_priority_paths(self) -> List[PathPriority]:
        """获取高优先级路径

        Returns:
            List[PathPriority]: 高优先级路径列表
        """
        return [p for p in self.prioritized_paths
                if p.priority_level in [PriorityLevel.CRITICAL, PriorityLevel.HIGH]]


class PathPriorityLayer:
    """路径优先级排序层

    功能描述：
        - 综合评估路径的多个优先级因素
        - 计算路径的优先级评分
        - 确定优先级级别（CRITICAL/HIGH/MEDIUM/LOW/MINIMAL）
        - 生成优化的执行计划
        - 支持依赖感知的执行顺序
        - 提供优先级推理和解释
        - 支持批次执行策略

    输入类型：
        - 路径列表（List[Path] 或 List[ExecutionPath]）
        - 路径标注（List[PathAnnotation]）
        - 覆盖统计（coverage_statistics）
        - 业务识别结果（BusinessRecognitionResult）
        - 权重配置（可选）

    输出类型：
        - PrioritizationResult: 优先级排序结果
        - List[PathPriority]: 优先级信息列表
        - 执行计划

    使用场景：
        - 测试用例生成顺序优化
        - 回归测试优先级排序
        - 测试资源分配
        - 测试计划制定
        - 持续集成中的测试选择

    V3.1升级点：
        - 增强多因素综合评分算法
        - 支持自定义权重配置
        - 提供更精确的覆盖率增益估算
        - 增加执行时间预测
        - 支持智能批次划分
    """

    description: str = "路径优先级排序层 - 多维度评估路径优先级并生成执行计划"
    input_type: str = "List[Path]、PathAnnotation和覆盖统计"
    output_type: str = "PrioritizationResult和List[PathPriority]"

    def __init__(self):
        """初始化路径优先级排序层"""
        self.paths = []
        self.annotations = {}
        self.coverage_stats = {}
        self.business_result = None
        self.prioritized_paths = []
        self.prioritization_result = None
        self.weights = self._default_weights()

    def _default_weights(self) -> Dict[str, float]:
        """获取默认权重配置

        Returns:
            Dict[str, float]: 权重配置字典
        """
        return {
            'coverage_impact': 0.25,
            'risk_level': 0.20,
            'business_value': 0.20,
            'complexity': 0.10,
            'execution_time': 0.10,
            'dependency_count': 0.05,
            'error_frequency': 0.05,
            'code_change_frequency': 0.05
        }

    def set_weights(self, weights: Dict[str, float]) -> None:
        """设置权重配置

        Args:
            weights: 权重配置字典
        """
        self.weights.update(weights)

    def process(self, context) -> PrioritizationResult:
        """处理路径，确定优先级

        Args:
            context: PipelineContext对象，包含路径和标注信息

        Returns:
            PrioritizationResult: 优先级排序结果

        Raises:
            ValueError: 当输入数据不足时
        """
        if not context.has('paths') and not context.has('enumerated_paths'):
            if not context.has('execution_paths'):
                raise ValueError("PathPriorityLayer: 缺少路径数据")

        if context.has('paths'):
            self.paths = context.get('paths')
        elif context.has('enumerated_paths'):
            self.paths = context.get('enumerated_paths')
        elif context.has('execution_paths'):
            self.paths = context.get('execution_paths')

        if context.has('path_annotations'):
            self.annotations = context.get('path_annotations')

        if context.has('coverage_statistics'):
            self.coverage_stats = context.get('coverage_statistics')

        if context.has('business_recognition_result'):
            self.business_result = context.get('business_recognition_result')

        if context.has('priority_weights'):
            self.weights = context.get('priority_weights')

        self._calculate_all_priorities()

        self._assign_priority_levels()

        self._generate_execution_plan()

        self._create_batching_strategy()

        self.prioritization_result = self._create_prioritization_result()

        context.set('prioritized_paths', self.prioritized_paths)
        context.set('prioritization_result', self.prioritization_result)
        context.set('path_prioritization_complete', True)
        context.set('prioritization_statistics', self._get_statistics())

        return self.prioritization_result

    def _calculate_all_priorities(self) -> None:
        """计算所有路径的优先级"""
        self.prioritized_paths = []

        for path in self.paths:
            path_id = self._get_path_id(path)

            priority = PathPriority(
                path_id=path_id,
                priority_level=PriorityLevel.MEDIUM
            )

            priority.factor_scores = self._calculate_factor_scores(path)

            priority.priority_score = self._calculate_overall_score(priority.factor_scores)

            priority.estimated_time = self._estimate_execution_time(path)

            priority.coverage_gain = self._estimate_coverage_gain(path)

            priority.risk_assessment = self._assess_risk(path)

            priority.dependencies = self._extract_dependencies(path)

            priority.reasoning = self._generate_reasoning(priority)

            self.prioritized_paths.append(priority)

        self.prioritized_paths.sort(key=lambda p: p.priority_score, reverse=True)

        for i, priority in enumerate(self.prioritized_paths):
            priority.ranking = i + 1

    def _calculate_factor_scores(self, path) -> Dict[str, float]:
        """计算各因素评分

        Args:
            path: 路径对象

        Returns:
            Dict[str, float]: 各因素评分
        """
        scores = {}

        scores['coverage_impact'] = self._score_coverage_impact(path)

        scores['risk_level'] = self._score_risk_level(path)

        scores['business_value'] = self._score_business_value(path)

        scores['complexity'] = self._score_complexity(path)

        scores['execution_time'] = self._score_execution_time(path)

        scores['dependency_count'] = self._score_dependency_count(path)

        scores['error_frequency'] = self._score_error_frequency(path)

        scores['code_change_frequency'] = self._score_code_change_frequency(path)

        return scores

    def _score_coverage_impact(self, path) -> float:
        """评分覆盖影响

        Args:
            path: 路径对象

        Returns:
            float: 覆盖影响评分（0-1）
        """
        if hasattr(path, 'coverage_potential'):
            return path.coverage_potential

        if hasattr(path, 'test_value'):
            return path.test_value

        path_id = self._get_path_id(path)
        if path_id in self.annotations:
            annotation = self.annotations[path_id]
            return getattr(annotation, 'coverage_importance', 0.5)

        return 0.5

    def _score_risk_level(self, path) -> float:
        """评分风险等级

        Args:
            path: 路径对象

        Returns:
            float: 风险评分（0-1）
        """
        risk_keywords = ['payment', 'auth', 'security', 'transaction', 'critical',
                       'delete', 'remove', 'destroy']

        func_name = getattr(path, 'function_name', '').lower()

        for keyword in risk_keywords:
            if keyword in func_name:
                return 0.9

        path_id = self._get_path_id(path)
        if path_id in self.annotations:
            annotation = self.annotations[path_id]
            risk_level = getattr(annotation, 'risk_level', 'medium')

            risk_scores = {'high': 0.9, 'medium': 0.6, 'low': 0.3}
            return risk_scores.get(risk_level, 0.5)

        return 0.5

    def _score_business_value(self, path) -> float:
        """评分业务价值

        Args:
            path: 路径对象

        Returns:
            float: 业务价值评分（0-1）
        """
        if self.business_result:
            func_name = getattr(path, 'function_name', '')

            for scenario in self.business_result.scenarios:
                if func_name in scenario.matched_functions:
                    return scenario.confidence

        path_id = self._get_path_id(path)
        if path_id in self.annotations:
            annotation = self.annotations[path_id]
            category = getattr(annotation, 'category', None)

            if category:
                high_value_categories = ['BUSINESS_LOGIC', 'TRANSACTION', 'AUTHENTICATION']
                if hasattr(category, 'name') and category.name in high_value_categories:
                    return 0.8

        return 0.5

    def _score_complexity(self, path) -> float:
        """评分复杂度

        Args:
            path: 路径对象

        Returns:
            float: 复杂度评分（0-1），越复杂分数越高
        """
        complexity = 0.5

        if hasattr(path, 'complexity'):
            complexity = min(1.0, path.complexity / 20.0)

        if hasattr(path, 'length'):
            complexity += min(0.2, path.length / 100.0)

        if hasattr(path, 'segments'):
            complexity += min(0.2, len(path.segments) / 20.0)

        return min(1.0, complexity)

    def _score_execution_time(self, path) -> float:
        """评分执行时间

        Args:
            path: 路径对象

        Returns:
            float: 执行时间评分（0-1），时间越长分数越低
        """
        estimated_time = getattr(path, 'execution_time', None)

        if estimated_time is None:
            if hasattr(path, 'length'):
                estimated_time = path.length * 0.1
            else:
                estimated_time = 1.0

        if estimated_time <= 0.1:
            return 1.0
        elif estimated_time <= 1.0:
            return 0.7
        elif estimated_time <= 10.0:
            return 0.4
        else:
            return 0.2

    def _score_dependency_count(self, path) -> float:
        """评分依赖数量

        Args:
            path: 路径对象

        Returns:
            float: 依赖评分（0-1）
        """
        deps = getattr(path, 'dependencies', [])

        dep_count = len(deps) if deps else 0

        if dep_count == 0:
            return 0.5
        elif dep_count <= 3:
            return 0.8
        elif dep_count <= 10:
            return 0.6
        else:
            return 0.4

    def _score_error_frequency(self, path) -> float:
        """评分错误频率

        Args:
            path: 路径对象

        Returns:
            float: 错误频率评分（0-1）
        """
        if hasattr(path, 'metadata'):
            error_count = path.metadata.get('error_count', 0)
            if error_count > 10:
                return 0.9
            elif error_count > 5:
                return 0.7
            elif error_count > 0:
                return 0.5

        return 0.3

    def _score_code_change_frequency(self, path) -> float:
        """评分代码变更频率

        Args:
            path: 路径对象

        Returns:
            float: 变更频率评分（0-1）
        """
        if hasattr(path, 'metadata'):
            change_count = path.metadata.get('change_count', 0)
            if change_count > 10:
                return 0.9
            elif change_count > 5:
                return 0.7
            elif change_count > 0:
                return 0.5

        return 0.3

    def _calculate_overall_score(self, factor_scores: Dict[str, float]) -> float:
        """计算总体评分

        Args:
            factor_scores: 各因素评分

        Returns:
            float: 总体评分（0-1）
        """
        total_score = 0.0
        total_weight = 0.0

        for factor, weight in self.weights.items():
            if factor in factor_scores:
                score = factor_scores[factor]
                total_score += score * weight
                total_weight += weight

        if total_weight > 0:
            return total_score / total_weight

        return 0.5

    def _estimate_execution_time(self, path) -> float:
        """估算执行时间

        Args:
            path: 路径对象

        Returns:
            float: 预估时间（秒）
        """
        if hasattr(path, 'execution_time'):
            return path.execution_time

        time_estimate = 0.1

        if hasattr(path, 'length'):
            time_estimate = path.length * 0.01

        if hasattr(path, 'dependencies'):
            time_estimate += len(path.dependencies) * 0.05

        return time_estimate

    def _estimate_coverage_gain(self, path) -> float:
        """估算覆盖率增益

        Args:
            path: 路径对象

        Returns:
            float: 预计覆盖率提升
        """
        gain = 0.0

        if hasattr(path, 'coverage_potential'):
            gain = path.coverage_potential

        if hasattr(path, 'segments'):
            unique_coverage = len(set())
            gain = min(1.0, len(path.segments) / 10.0)

        return min(1.0, gain)

    def _assess_risk(self, path) -> Dict[str, Any]:
        """评估风险

        Args:
            path: 路径对象

        Returns:
            Dict[str, Any]: 风险评估结果
        """
        assessment = {
            'overall_risk': 'medium',
            'factors': [],
            'mitigation': []
        }

        func_name = getattr(path, 'function_name', '').lower()

        risk_keywords = {
            'payment': 'high',
            'auth': 'high',
            'security': 'high',
            'transaction': 'high',
            'delete': 'medium',
            'update': 'medium',
            'insert': 'medium'
        }

        for keyword, risk in risk_keywords.items():
            if keyword in func_name:
                assessment['overall_risk'] = risk
                assessment['factors'].append(f"高风险关键词: {keyword}")
                break

        if hasattr(path, 'complexity') and path.complexity > 15:
            assessment['factors'].append("高复杂度")
            if assessment['overall_risk'] == 'low':
                assessment['overall_risk'] = 'medium'

        return assessment

    def _extract_dependencies(self, path) -> List[str]:
        """提取依赖关系

        Args:
            path: 路径对象

        Returns:
            List[str]: 依赖列表
        """
        deps = []

        if hasattr(path, 'dependencies'):
            deps.extend(path.dependencies)

        if hasattr(path, 'variables'):
            deps.extend(path.variables[:5])

        return deps

    def _generate_reasoning(self, priority: PathPriority) -> str:
        """生成优先级推理

        Args:
            priority: 路径优先级对象

        Returns:
            str: 推理说明
        """
        reasons = []

        if priority.factor_scores.get('coverage_impact', 0) >= 0.7:
            reasons.append("高覆盖影响")

        if priority.factor_scores.get('risk_level', 0) >= 0.7:
            reasons.append("高风险")

        if priority.factor_scores.get('business_value', 0) >= 0.7:
            reasons.append("高业务价值")

        if priority.dependencies:
            reasons.append(f"依赖{len(priority.dependencies)}个其他路径")

        if not reasons:
            reasons.append("综合评分一般")

        return "; ".join(reasons)

    def _assign_priority_levels(self) -> None:
        """分配优先级级别"""
        if not self.prioritized_paths:
            return

        scores = [p.priority_score for p in self.prioritized_paths]
        max_score = max(scores)
        min_score = min(scores)

        score_range = max_score - min_score if max_score > min_score else 1.0

        for priority in self.prioritized_paths:
            normalized = (priority.priority_score - min_score) / score_range

            if normalized >= 0.9:
                priority.priority_level = PriorityLevel.CRITICAL
            elif normalized >= 0.7:
                priority.priority_level = PriorityLevel.HIGH
            elif normalized >= 0.4:
                priority.priority_level = PriorityLevel.MEDIUM
            elif normalized >= 0.2:
                priority.priority_level = PriorityLevel.LOW
            else:
                priority.priority_level = PriorityLevel.MINIMAL

    def _generate_execution_plan(self) -> None:
        """生成执行计划"""
        self.execution_plan = []

        current_order = 1

        for priority in self.prioritized_paths:
            priority.execution_order = current_order
            current_order += 1

        critical_paths = [p for p in self.prioritized_paths
                        if p.priority_level == PriorityLevel.CRITICAL]
        if critical_paths:
            self.execution_plan.append([p.path_id for p in critical_paths])

        high_paths = [p for p in self.prioritized_paths
                     if p.priority_level == PriorityLevel.HIGH]
        if high_paths:
            self.execution_plan.append([p.path_id for p in high_paths])

        medium_batch = [p for p in self.prioritized_paths
                       if p.priority_level == PriorityLevel.MEDIUM]
        if medium_batch:
            self.execution_plan.append([p.path_id for p in medium_batch])

        low_batch = [p for p in self.prioritized_paths
                    if p.priority_level in [PriorityLevel.LOW, PriorityLevel.MINIMAL]]
        if low_batch:
            self.execution_plan.append([p.path_id for p in low_batch])

    def _create_batching_strategy(self) -> None:
        """创建批次策略"""
        self.batching_strategy = {
            'batch_size': 10,
            'batches': [],
            'estimated_total_time': 0.0
        }

        batch_size = 10
        current_batch = []
        batch_time = 0.0

        for priority in self.prioritized_paths:
            current_batch.append(priority.path_id)
            batch_time += priority.estimated_time

            if len(current_batch) >= batch_size or batch_time >= 300:
                self.batching_strategy['batches'].append({
                    'paths': list(current_batch),
                    'estimated_time': batch_time
                })
                self.batching_strategy['estimated_total_time'] += batch_time
                current_batch = []
                batch_time = 0.0

        if current_batch:
            self.batching_strategy['batches'].append({
                'paths': list(current_batch),
                'estimated_time': batch_time
            })
            self.batching_strategy['estimated_total_time'] += batch_time

    def _create_prioritization_result(self) -> PrioritizationResult:
        """创建优先级排序结果

        Returns:
            PrioritizationResult: 优先级排序结果
        """
        result = PrioritizationResult(
            total_paths=len(self.paths),
            prioritized_paths=self.prioritized_paths,
            execution_plan=self.execution_plan,
            batching_strategy=self.batching_strategy
        )

        dist = defaultdict(int)
        for priority in self.prioritized_paths:
            dist[priority.priority_level.name] += 1
        result.priority_distribution = dict(dist)

        result.statistics = self._compute_statistics()

        result.recommendations = self._generate_recommendations()

        result.metadata = {
            'avg_priority_score': sum(p.priority_score for p in self.prioritized_paths) / len(self.prioritized_paths) if self.prioritized_paths else 0,
            'total_estimated_time': self.batching_strategy['estimated_total_time'],
            'critical_count': len(result.get_critical_paths()),
            'high_priority_count': len(result.get_high_priority_paths())
        }

        return result

    def _compute_statistics(self) -> Dict[str, Any]:
        """计算统计信息

        Returns:
            Dict[str, Any]: 统计信息
        """
        if not self.prioritized_paths:
            return {}

        stats = {
            'total_paths': len(self.prioritized_paths),
            'avg_priority_score': sum(p.priority_score for p in self.prioritized_paths) / len(self.prioritized_paths),
            'avg_estimated_time': sum(p.estimated_time for p in self.prioritized_paths) / len(self.prioritized_paths),
            'total_estimated_time': sum(p.estimated_time for p in self.prioritized_paths),
            'avg_coverage_gain': sum(p.coverage_gain for p in self.prioritized_paths) / len(self.prioritized_paths)
        }

        for level in PriorityLevel:
            count = sum(1 for p in self.prioritized_paths if p.priority_level == level)
            stats[f'{level.name.lower()}_count'] = count

        return stats

    def _generate_recommendations(self) -> List[str]:
        """生成建议

        Returns:
            List[str]: 建议列表
        """
        recommendations = []

        critical = self.prioritization_result.get_critical_paths()
        if critical:
            recommendations.append(f"建议优先执行{len(critical)}个关键路径")

        high = self.prioritization_result.get_high_priority_paths()
        if high:
            recommendations.append(f"建议优先覆盖{len(high)}个高优先级路径")

        total_time = self.batching_strategy['estimated_total_time']
        if total_time > 3600:
            recommendations.append(f"预计总执行时间{total_time/3600:.1f}小时，建议分批次执行")
        elif total_time > 600:
            recommendations.append(f"预计总执行时间{total_time/60:.1f}分钟，注意时间安排")

        return recommendations

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
        if not self.prioritization_result:
            return {}

        return {
            'total_paths': self.prioritization_result.total_paths,
            'priority_distribution': self.prioritization_result.priority_distribution,
            'statistics': self.prioritization_result.statistics,
            'recommendations': self.prioritization_result.recommendations
        }

    def get_paths_by_level(self, level: PriorityLevel) -> List[PathPriority]:
        """按级别获取路径

        Args:
            level: 优先级级别

        Returns:
            List[PathPriority]: 该级别的路径列表
        """
        return [p for p in self.prioritized_paths if p.priority_level == level]

    def get_top_n_paths(self, n: int) -> List[PathPriority]:
        """获取前N个路径

        Args:
            n: 数量

        Returns:
            List[PathPriority]: 前N个路径
        """
        return self.prioritized_paths[:n]

    def get_execution_order(self) -> List[str]:
        """获取执行顺序

        Returns:
            List[str]: 路径ID的执行顺序
        """
        return [p.path_id for p in sorted(self.prioritized_paths,
                                         key=lambda p: p.execution_order)]

    def export_execution_plan(self) -> Dict[str, Any]:
        """导出执行计划

        Returns:
            Dict[str, Any]: 执行计划
        """
        return {
            'execution_order': self.get_execution_order(),
            'execution_plan': self.execution_plan,
            'batching_strategy': self.batching_strategy,
            'priority_distribution': self.prioritization_result.priority_distribution,
            'statistics': self.prioritization_result.statistics
        }

    def suggest_test_sequence(self) -> List[str]:
        """建议测试序列

        Returns:
            List[str]: 建议的测试路径顺序
        """
        return self.get_execution_order()
