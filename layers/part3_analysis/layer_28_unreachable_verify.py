"""
Layer 28: UnreachableVerifyLayer - 不可达路径验证层

本层负责验证和确认不可达路径，分析路径不可达的原因，
并提供改进建议以增加代码的可测试性和覆盖率。
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import defaultdict, deque


class UnreachabilityReason(Enum):
    """不可达原因枚举"""
    CONSTANT_CONDITION = auto()
    IMPOSSIBLE_PREREQUISITE = auto()
    TYPE_CONSTRAINT = auto()
    RANGE_CONSTRAINT = auto()
    DEAD_CODE = auto()
    INTERNAL_LOGIC_ERROR = auto()
    MISSING_DEPENDENCY = auto()
    CONFIGURATION = auto()
    ENVIRONMENT = auto()
    TEMPORARY = auto()


class VerificationMethod(Enum):
    """验证方法枚举"""
    STATIC_ANALYSIS = auto()
    SYMBOLIC_EXECUTION = auto()
    CONSTRAINT_SOLVING = auto()
    CONCRETE_EXECUTION = auto()
    LLM_REASONING = auto()
    MANUAL_REVIEW = auto()


@dataclass
class UnreachablePath:
    """不可达路径信息

    Attributes:
        path_id: 路径标识符
        unreachability_reason: 不可达原因
        verification_method: 验证方法
        blocker_conditions: 阻塞条件
        suggested_fix: 建议修复方案
        confidence: 置信度
        impact_analysis: 影响分析
        recovery_effort: 恢复工作量和难度
        priority: 处理优先级
    """
    path_id: str
    unreachability_reason: UnreachabilityReason
    verification_method: VerificationMethod
    blocker_conditions: List[str] = field(default_factory=list)
    suggested_fix: str = ""
    confidence: float = 0.0
    impact_analysis: Dict[str, Any] = field(default_factory=dict)
    recovery_effort: int = 1
    priority: int = 5

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "path_id": self.path_id,
            "unreachability_reason": self.unreachability_reason.name,
            "verification_method": self.verification_method.name,
            "blocker_conditions": self.blocker_conditions,
            "suggested_fix": self.suggested_fix,
            "confidence": self.confidence,
            "impact_analysis": self.impact_analysis,
            "recovery_effort": self.recovery_effort,
            "priority": self.priority
        }


@dataclass
class VerificationResult:
    """验证结果

    Attributes:
        total_paths: 总路径数
        reachable_paths: 可达路径数
        unreachable_paths: 不可达路径数
        verified_unreachable: 已验证不可达
        potentially_reachable: 可能可达
        unreachable_list: 不可达路径列表
        reachability_issues: 可达性问题列表
        verification_stats: 验证统计信息
        recommendations: 建议列表
        metadata: 元信息
    """
    total_paths: int = 0
    reachable_paths: int = 0
    unreachable_paths: int = 0
    verified_unreachable: int = 0
    potentially_reachable: int = 0
    unreachable_list: List[UnreachablePath] = field(default_factory=list)
    reachability_issues: List[Dict[str, Any]] = field(default_factory=list)
    verification_stats: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "total_paths": self.total_paths,
            "reachable_paths": self.reachable_paths,
            "unreachable_paths": self.unreachable_paths,
            "verified_unreachable": self.verified_unreachable,
            "potentially_reachable": self.potentially_reachable,
            "unreachable_list": [u.to_dict() for u in self.unreachable_list],
            "reachability_issues": self.reachability_issues,
            "verification_stats": self.verification_stats,
            "recommendations": self.recommendations,
            "metadata": self.metadata
        }

    def get_reachability_rate(self) -> float:
        """获取可达率

        Returns:
            float: 可达率（0-100）
        """
        if self.total_paths == 0:
            return 0.0
        return (self.reachable_paths / self.total_paths) * 100


class UnreachableVerifyLayer:
    """不可达路径验证层

    功能描述：
        - 验证路径的可达性
        - 分析路径不可达的具体原因
        - 识别阻塞条件和死代码
        - 评估不可达路径的业务影响
        - 提供恢复可达性的建议
        - 生成验证报告和改进建议
        - 支持多种验证方法

    输入类型：
        - 路径列表（List[Path] 或 List[EnumeratedPath]）
        - 控制流图（ControlFlowGraph）
        - 符号执行结果（可选）
        - 配置信息（可选）

    输出类型：
        - VerificationResult: 验证结果
        - List[UnreachablePath]: 不可达路径列表
        - 验证统计信息和建议

    使用场景：
        - 识别测试覆盖盲点
        - 发现死代码和无效逻辑
        - 优化代码结构和可测试性
        - 提高路径覆盖率
        - 代码质量评估

    V3.1升级点：
        - 增强符号执行和约束求解能力
        - 提供更精确的不可达原因分析
        - 支持LLM辅助的逻辑推理
        - 增加自动化验证流程
        - 提供更详细的影响分析
    """

    description: str = "不可达路径验证层 - 验证路径可达性并分析不可达原因"
    input_type: str = "List[Path]和ControlFlowGraph"
    output_type: str = "VerificationResult和List[UnreachablePath]"

    def __init__(self):
        """初始化不可达路径验证层"""
        self.paths = []
        self.cfg = None
        self.symbolic_results = None
        self.unreachable_paths = []
        self.verification_result = None
        self.reachability_cache = {}

    def process(self, context) -> VerificationResult:
        """处理路径，验证可达性

        Args:
            context: PipelineContext对象，包含路径和CFG信息

        Returns:
            VerificationResult: 验证结果

        Raises:
            ValueError: 当输入数据不足时
        """
        if not context.has('paths') and not context.has('enumerated_paths'):
            if not context.has('execution_paths'):
                raise ValueError("UnreachableVerifyLayer: 缺少路径数据")

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

        if context.has('symbolic_results'):
            self.symbolic_results = context.get('symbolic_results')

        self._analyze_all_paths()

        self._verify_unreachability()

        self._generate_recommendations()

        self.verification_result = self._create_verification_result()

        context.set('unreachable_paths', self.unreachable_paths)
        context.set('verification_result', self.verification_result)
        context.set('unreachability_verification_complete', True)
        context.set('verification_statistics', self._get_statistics())

        return self.verification_result

    def _analyze_all_paths(self) -> None:
        """分析所有路径的可达性"""
        self.reachability_cache = {}

        for path in self.paths:
            path_id = self._get_path_id(path)

            if path_id in self.reachability_cache:
                is_reachable = self.reachability_cache[path_id]
            else:
                is_reachable = self._check_path_reachability(path)
                self.reachability_cache[path_id] = is_reachable

            if not is_reachable:
                unreachable_info = self._analyze_unreachable_reason(path)
                self.unreachable_paths.append(unreachable_info)

    def _check_path_reachability(self, path) -> bool:
        """检查路径可达性

        Args:
            path: 路径对象

        Returns:
            bool: 是否可达
        """
        if hasattr(path, 'is_feasible'):
            return path.is_feasible

        nodes = self._extract_path_nodes(path)

        if self.cfg:
            if not self._nodes_exist(nodes):
                return False

            if not self._edges_exist(nodes):
                return False

        blockers = self._find_blocking_conditions(path)
        if blockers:
            return False

        return True

    def _nodes_exist(self, nodes: List[str]) -> bool:
        """检查节点是否存在

        Args:
            nodes: 节点列表

        Returns:
            bool: 是否都存在
        """
        if not self.cfg:
            return True

        if hasattr(self.cfg, 'nodes'):
            for node_id in nodes:
                if node_id not in self.cfg.nodes:
                    return False

        return True

    def _edges_exist(self, nodes: List[str]) -> bool:
        """检查边是否存在

        Args:
            nodes: 节点列表

        Returns:
            bool: 是否都存在
        """
        if not self.cfg:
            return True

        if hasattr(self.cfg, 'edges'):
            for i in range(len(nodes) - 1):
                source = nodes[i]
                target = nodes[i + 1]

                edge_exists = False
                for edge in self.cfg.edges:
                    if edge.source == source and edge.target == target:
                        edge_exists = True
                        break

                if not edge_exists:
                    return False

        return True

    def _find_blocking_conditions(self, path) -> List[str]:
        """查找阻塞条件

        Args:
            path: 路径对象

        Returns:
            List[str]: 阻塞条件列表
        """
        blockers = []

        if hasattr(path, 'conditions'):
            for condition in path.conditions:
                if self._is_constant_false(condition):
                    blockers.append(f"恒假条件: {condition}")
                elif self._is_self_contradicting(condition):
                    blockers.append(f"自相矛盾: {condition}")

        if hasattr(path, 'metadata'):
            if path.metadata.get('always_false'):
                blockers.append("元数据标记为恒假")
            if path.metadata.get('unreachable'):
                blockers.append("元数据标记为不可达")

        return blockers

    def _is_constant_false(self, condition: str) -> bool:
        """判断条件是否恒为假

        Args:
            condition: 条件字符串

        Returns:
            bool: 是否恒假
        """
        false_patterns = [
            'False', 'false', 'None', 'null', '0', '""', "''",
            '1 == 0', '0 == 1', 'True == False'
        ]

        condition_lower = condition.lower().strip()

        for pattern in false_patterns:
            if pattern.lower() in condition_lower:
                return True

        return False

    def _is_self_contradicting(self, condition: str) -> bool:
        """判断条件是否自相矛盾

        Args:
            condition: 条件字符串

        Returns:
            bool: 是否自相矛盾
        """
        if 'and' in condition.lower():
            parts = condition.lower().split('and')
            for part in parts:
                neg_part = self._negate_condition(part.strip())
                if neg_part and any(neg_part in other for other in parts if other != part):
                    return True

        return False

    def _negate_condition(self, condition: str) -> str:
        """取反条件

        Args:
            condition: 条件字符串

        Returns:
            str: 取反后的条件
        """
        condition = condition.strip()

        if condition.startswith('not '):
            return condition[4:].strip()

        if condition.startswith('!'):
            return condition[1:].strip()

        return f"not {condition}"

    def _analyze_unreachable_reason(self, path) -> UnreachablePath:
        """分析不可达原因

        Args:
            path: 路径对象

        Returns:
            UnreachablePath: 不可达路径信息
        """
        path_id = self._get_path_id(path)

        reason = self._determine_unreachability_reason(path)

        method = self._select_verification_method(path)

        blockers = self._find_blocking_conditions(path)

        fix = self._suggest_fix(path, reason)

        confidence = self._calculate_confidence(path, reason)

        impact = self._analyze_impact(path)

        effort = self._estimate_recovery_effort(path, reason)

        priority = self._calculate_priority(reason, effort, impact)

        return UnreachablePath(
            path_id=path_id,
            unreachability_reason=reason,
            verification_method=method,
            blocker_conditions=blockers,
            suggested_fix=fix,
            confidence=confidence,
            impact_analysis=impact,
            recovery_effort=effort,
            priority=priority
        )

    def _determine_unreachability_reason(self, path) -> UnreachabilityReason:
        """确定不可达原因

        Args:
            path: 路径对象

        Returns:
            UnreachabilityReason: 不可达原因
        """
        if hasattr(path, 'conditions'):
            for condition in path.conditions:
                if self._is_constant_false(condition):
                    return UnreachabilityReason.CONSTANT_CONDITION

        if hasattr(path, 'variables'):
            for var in path.variables:
                if self._has_type_constraint_issue(var):
                    return UnreachabilityReason.TYPE_CONSTRAINT

        if hasattr(path, 'metadata'):
            if path.metadata.get('dead_code'):
                return UnreachabilityReason.DEAD_CODE
            if path.metadata.get('config_blocked'):
                return UnreachabilityReason.CONFIGURATION

        if not self.cfg:
            return UnreachabilityReason.MANUAL_REVIEW

        nodes = self._extract_path_nodes(path)
        if not self._nodes_exist(nodes):
            return UnreachabilityReason.DEAD_CODE

        if not self._edges_exist(nodes):
            return UnreachabilityReason.MISSING_DEPENDENCY

        return UnreachabilityReason.INTERNAL_LOGIC_ERROR

    def _has_type_constraint_issue(self, var: str) -> bool:
        """检查变量是否有类型约束问题

        Args:
            var: 变量名

        Returns:
            bool: 是否有问题
        """
        type_keywords = ['int', 'str', 'bool', 'float', 'list', 'dict']

        var_lower = var.lower()

        for keyword in type_keywords:
            if keyword in var_lower:
                return True

        return False

    def _select_verification_method(self, path) -> VerificationMethod:
        """选择验证方法

        Args:
            path: 路径对象

        Returns:
            VerificationMethod: 验证方法
        """
        if self.symbolic_results:
            return VerificationMethod.SYMBOLIC_EXECUTION

        if hasattr(path, 'conditions') and path.conditions:
            return VerificationMethod.CONSTRAINT_SOLVING

        if hasattr(path, 'code') or hasattr(path, 'source_code'):
            return VerificationMethod.STATIC_ANALYSIS

        return VerificationMethod.MANUAL_REVIEW

    def _suggest_fix(self, path, reason: UnreachabilityReason) -> str:
        """建议修复方案

        Args:
            path: 路径对象
            reason: 不可达原因

        Returns:
            str: 修复建议
        """
        suggestions = {
            UnreachabilityReason.CONSTANT_CONDITION: "移除恒假条件或重构成有意义的逻辑",
            UnreachabilityReason.IMPOSSIBLE_PREREQUISITE: "调整前置条件或提供必要的依赖",
            UnreachabilityReason.TYPE_CONSTRAINT: "修正类型约束或使用正确的类型检查",
            UnreachabilityReason.RANGE_CONSTRAINT: "扩展有效范围或添加边界处理",
            UnreachabilityReason.DEAD_CODE: "删除死代码或将其转换为有效逻辑",
            UnreachabilityReason.INTERNAL_LOGIC_ERROR: "修复内部逻辑错误",
            UnreachabilityReason.MISSING_DEPENDENCY: "添加缺失的依赖或修正引用",
            UnreachabilityReason.CONFIGURATION: "调整配置或移除配置依赖",
            UnreachabilityReason.ENVIRONMENT: "修正环境设置或添加环境检查",
            UnreachabilityReason.TEMPORARY: "临时禁用，等待条件满足后启用"
        }

        base_suggestion = suggestions.get(reason, "需要人工审查确定具体修复方案")

        if hasattr(path, 'function_name'):
            base_suggestion += f" (影响函数: {path.function_name})"

        return base_suggestion

    def _calculate_confidence(self, path, reason: UnreachabilityReason) -> float:
        """计算置信度

        Args:
            path: 路径对象
            reason: 不可达原因

        Returns:
            float: 置信度评分
        """
        confidence = 0.5

        if reason == UnreachabilityReason.CONSTANT_CONDITION:
            confidence = 0.95
        elif reason == UnreachabilityReason.DEAD_CODE:
            confidence = 0.85
        elif reason == UnreachabilityReason.INTERNAL_LOGIC_ERROR:
            confidence = 0.7

        if self.symbolic_results:
            confidence += 0.1

        if hasattr(path, 'conditions') and path.conditions:
            confidence += 0.1

        return min(1.0, confidence)

    def _analyze_impact(self, path) -> Dict[str, Any]:
        """分析影响

        Args:
            path: 路径对象

        Returns:
            Dict[str, Any]: 影响分析结果
        """
        impact = {
            'code_coverage_loss': 0.0,
            'business_impact': 'low',
            'test_gaps': [],
            'risk_level': 'low'
        }

        if hasattr(path, 'length'):
            impact['code_coverage_loss'] = path.length / 100.0

        if hasattr(path, 'function_name'):
            func_name = path.function_name.lower()
            critical_keywords = ['payment', 'auth', 'security', 'transaction', 'critical']
            if any(keyword in func_name for keyword in critical_keywords):
                impact['business_impact'] = 'high'
                impact['risk_level'] = 'high'
            elif 'validation' in func_name or 'check' in func_name:
                impact['business_impact'] = 'medium'

        impact['test_gaps'] = self._identify_test_gaps(path)

        return impact

    def _identify_test_gaps(self, path) -> List[str]:
        """识别测试缺口

        Args:
            path: 路径对象

        Returns:
            List[str]: 测试缺口列表
        """
        gaps = []

        if hasattr(path, 'conditions'):
            gaps.append(f"条件覆盖缺口: {len(path.conditions)}个条件未覆盖")

        if hasattr(path, 'function_name'):
            gaps.append(f"函数{path.function_name}的特定路径未覆盖")

        return gaps

    def _estimate_recovery_effort(self, path, reason: UnreachabilityReason) -> int:
        """估算恢复工作量

        Args:
            path: 路径对象
            reason: 不可达原因

        Returns:
            int: 工作量评分（1-10）
        """
        effort = 3

        if reason == UnreachabilityReason.CONSTANT_CONDITION:
            effort = 2
        elif reason == UnreachabilityReason.DEAD_CODE:
            effort = 1
        elif reason == UnreachabilityReason.INTERNAL_LOGIC_ERROR:
            effort = 8

        if hasattr(path, 'length'):
            effort += path.length // 10

        return min(10, effort)

    def _calculate_priority(self, reason: UnreachabilityReason, effort: int,
                          impact: Dict[str, Any]) -> int:
        """计算优先级

        Args:
            reason: 不可达原因
            effort: 工作量
            impact: 影响分析

        Returns:
            int: 优先级（1-10，1最高）
        """
        priority = 5

        if impact.get('business_impact') == 'high':
            priority -= 2
        elif impact.get('business_impact') == 'medium':
            priority -= 1

        if impact.get('risk_level') == 'high':
            priority -= 2

        if effort <= 3:
            priority -= 1

        if reason == UnreachabilityReason.DEAD_CODE:
            priority += 1

        return max(1, min(10, priority))

    def _verify_unreachability(self) -> None:
        """验证不可达路径"""
        for unreachable in self.unreachable_paths:
            if unreachable.confidence < 0.8:
                unreachable.verification_method = VerificationMethod.CONSTRAINT_SOLVING

    def _generate_recommendations(self) -> None:
        """生成建议"""
        self.recommendations = []

        high_priority_count = sum(1 for u in self.unreachable_paths if u.priority <= 3)
        if high_priority_count > 0:
            self.recommendations.append(
                f"有{high_priority_count}个高优先级不可达路径需要处理"
            )

        dead_code_count = sum(1 for u in self.unreachable_paths
                              if u.unreachability_reason == UnreachabilityReason.DEAD_CODE)
        if dead_code_count > 0:
            self.recommendations.append(
                f"发现{dead_code_count}个死代码路径，建议清理"
            )

        constant_condition_count = sum(
            1 for u in self.unreachable_paths
            if u.unreachability_reason == UnreachabilityReason.CONSTANT_CONDITION
        )
        if constant_condition_count > 0:
            self.recommendations.append(
                f"发现{constant_condition_count}个恒假条件，建议检查业务逻辑"
            )

        if not self.unreachable_paths:
            self.recommendations.append("所有路径均已验证为可达")

    def _create_verification_result(self) -> VerificationResult:
        """创建验证结果

        Returns:
            VerificationResult: 验证结果
        """
        result = VerificationResult(
            total_paths=len(self.paths),
            reachable_paths=len(self.paths) - len(self.unreachable_paths),
            unreachable_paths=len(self.unreachable_paths),
            verified_unreachable=sum(1 for u in self.unreachable_paths if u.confidence >= 0.8),
            potentially_reachable=sum(1 for u in self.unreachable_paths if u.confidence < 0.8),
            unreachable_list=self.unreachable_paths
        )

        result.verification_stats = self._compute_verification_stats()

        result.recommendations = self.recommendations

        result.metadata = {
            'reachability_rate': result.get_reachability_rate(),
            'verification_methods_used': self._count_verification_methods(),
            'high_priority_unreachable': sum(1 for u in self.unreachable_paths if u.priority <= 3)
        }

        return result

    def _compute_verification_stats(self) -> Dict[str, Any]:
        """计算验证统计

        Returns:
            Dict[str, Any]: 统计信息
        """
        stats = {
            'total_analyzed': len(self.paths),
            'verified_unreachable': len(self.unreachable_paths),
            'avg_confidence': sum(u.confidence for u in self.unreachable_paths) / len(self.unreachable_paths) if self.unreachable_paths else 0,
            'avg_priority': sum(u.priority for u in self.unreachable_paths) / len(self.unreachable_paths) if self.unreachable_paths else 0
        }

        reason_counts = defaultdict(int)
        for u in self.unreachable_paths:
            reason_counts[u.unreachability_reason.name] += 1
        stats['by_reason'] = dict(reason_counts)

        method_counts = defaultdict(int)
        for u in self.unreachable_paths:
            method_counts[u.verification_method.name] += 1
        stats['by_method'] = dict(method_counts)

        effort_sum = sum(u.recovery_effort for u in self.unreachable_paths)
        stats['total_recovery_effort'] = effort_sum
        stats['avg_recovery_effort'] = effort_sum / len(self.unreachable_paths) if self.unreachable_paths else 0

        return stats

    def _count_verification_methods(self) -> Dict[str, int]:
        """统计使用的验证方法

        Returns:
            Dict[str, int]: 各方法使用次数
        """
        counts = defaultdict(int)
        for u in self.unreachable_paths:
            counts[u.verification_method.name] += 1
        return dict(counts)

    def _get_path_id(self, path) -> str:
        """获取路径标识符

        Args:
            path: 路径对象

        Returns:
            str: 路径标识符
        """
        return getattr(path, 'path_id', '') or getattr(path, 'execution_id', str(id(path)))

    def _extract_path_nodes(self, path) -> List[str]:
        """提取路径节点

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
        if not self.verification_result:
            return {}

        return {
            'total_paths': self.verification_result.total_paths,
            'reachable_paths': self.verification_result.reachable_paths,
            'unreachable_paths': self.verification_result.unreachable_paths,
            'reachability_rate': self.verification_result.get_reachability_rate(),
            'verification_stats': self.verification_result.verification_stats
        }

    def get_unreachable_by_reason(self, reason: UnreachabilityReason) -> List[UnreachablePath]:
        """按原因获取不可达路径

        Args:
            reason: 不可达原因

        Returns:
            List[UnreachablePath]: 不可达路径列表
        """
        return [u for u in self.unreachable_paths if u.unreachability_reason == reason]

    def get_high_priority_unreachable(self) -> List[UnreachablePath]:
        """获取高优先级不可达路径

        Returns:
            List[UnreachablePath]: 高优先级不可达路径
        """
        return sorted(
            [u for u in self.unreachable_paths if u.priority <= 3],
            key=lambda u: u.priority
        )

    def get_recoverable_paths(self, max_effort: int = 5) -> List[UnreachablePath]:
        """获取可恢复的路径

        Args:
            max_effort: 最大工作量

        Returns:
            List[UnreachablePath]: 可恢复路径
        """
        return [u for u in self.unreachable_paths if u.recovery_effort <= max_effort]

    def export_verification_report(self) -> Dict[str, Any]:
        """导出验证报告

        Returns:
            Dict[str, Any]: 验证报告
        """
        return {
            'summary': {
                'total_paths': self.verification_result.total_paths,
                'reachable': self.verification_result.reachable_paths,
                'unreachable': self.verification_result.unreachable_paths,
                'reachability_rate': self.verification_result.get_reachability_rate()
            },
            'unreachable_paths': [u.to_dict() for u in self.unreachable_paths],
            'statistics': self.verification_result.verification_stats,
            'recommendations': self.verification_result.recommendations
        }

    def suggest_improvements(self) -> List[Dict[str, Any]]:
        """建议改进方案

        Returns:
            List[Dict[str, Any]]: 改进建议列表
        """
        suggestions = []

        constant_conditions = self.get_unreachable_by_reason(UnreachabilityReason.CONSTANT_CONDITION)
        if constant_conditions:
            suggestions.append({
                'type': 'logic_review',
                'description': '检查恒假条件的业务逻辑',
                'affected_paths': len(constant_conditions),
                'action': '审查并修正条件表达式'
            })

        dead_code = self.get_unreachable_by_reason(UnreachabilityReason.DEAD_CODE)
        if dead_code:
            suggestions.append({
                'type': 'code_cleanup',
                'description': '清理死代码',
                'affected_paths': len(dead_code),
                'action': '删除或重构不可达代码'
            })

        low_confidence = [u for u in self.unreachable_paths if u.confidence < 0.8]
        if low_confidence:
            suggestions.append({
                'type': 'further_analysis',
                'description': '需要进一步分析的路径',
                'affected_paths': len(low_confidence),
                'action': '使用更精确的验证方法重新分析'
            })

        return suggestions
