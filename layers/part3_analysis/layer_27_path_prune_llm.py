"""
Layer 27: LLMPathPruneLayer - LLM辅助路径剪枝层【V3.1升级】

本层利用LLM的语义理解能力辅助进行路径剪枝决策，
识别语义相似、无效或不可行的路径，提高测试效率。
V3.1升级增强了LLM分析能力和批量处理效率。
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import defaultdict
import asyncio


class PruneReason(Enum):
    """剪枝原因枚举"""
    SEMANTICALLY_SIMILAR = auto()
    SYNTACTICALLY_EQUIVALENT = auto()
    INFEASIBLE = auto()
    UNREACHABLE = auto()
    REDUNDANT = auto()
    LOW_COVERAGE_VALUE = auto()
    INFINITE_LOOP = auto()
    LL_EFFORT_RATIO = auto()
    DUPLICATE_BEHAVIOR = auto()
    TESTED_EQUIVALENT = auto()


class PruneConfidence(Enum):
    """剪枝置信度枚举"""
    HIGH = auto()
    MEDIUM = auto()
    LOW = auto()


@dataclass
class PruneCandidate:
    """剪枝候选路径

    Attributes:
        path_id: 路径标识符
        prune_reason: 剪枝原因
        confidence: 置信度
        equivalent_paths: 等价路径列表
        analysis: LLM分析结果
        suggested_alternative: 建议的替代路径
        preservation_criteria: 保留条件
        business_impact: 业务影响评估
        test_coverage_impact: 测试覆盖影响
    """
    path_id: str
    prune_reason: PruneReason
    confidence: PruneConfidence
    equivalent_paths: List[str] = field(default_factory=list)
    analysis: Dict[str, Any] = field(default_factory=dict)
    suggested_alternative: Optional[str] = None
    preservation_criteria: List[str] = field(default_factory=list)
    business_impact: str = "low"
    test_coverage_impact: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "path_id": self.path_id,
            "prune_reason": self.prune_reason.name,
            "confidence": self.confidence.name,
            "equivalent_paths": self.equivalent_paths,
            "analysis": self.analysis,
            "suggested_alternative": self.suggested_alternative,
            "preservation_criteria": self.preservation_criteria,
            "business_impact": self.business_impact,
            "test_coverage_impact": self.test_coverage_impact
        }


@dataclass
class LLMAnalysis:
    """LLM分析结果

    Attributes:
        path_id: 路径标识符
        semantic_summary: 语义摘要
        behavioral_description: 行为描述
        edge_cases: 边界情况
        potential_issues: 潜在问题
        test_recommendations: 测试建议
        equivalence_class: 等价类
        confidence: 分析置信度
        processing_time: 处理时间
    """
    path_id: str
    semantic_summary: str = ""
    behavioral_description: str = ""
    edge_cases: List[str] = field(default_factory=list)
    potential_issues: List[str] = field(default_factory=list)
    test_recommendations: List[str] = field(default_factory=list)
    equivalence_class: str = ""
    confidence: float = 0.0
    processing_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "path_id": self.path_id,
            "semantic_summary": self.semantic_summary,
            "behavioral_description": self.behavioral_description,
            "edge_cases": self.edge_cases,
            "potential_issues": self.potential_issues,
            "test_recommendations": self.test_recommendations,
            "equivalence_class": self.equivalence_class,
            "confidence": self.confidence,
            "processing_time": self.processing_time
        }


@dataclass
class PruningResult:
    """剪枝结果

    Attributes:
        original_count: 原始路径数
        pruned_count: 剪枝路径数
        retained_count: 保留路径数
        prune_candidates: 剪枝候选列表
        retained_paths: 保留路径列表
        llm_analyses: LLM分析结果列表
        equivalence_groups: 等价路径组
        pruning_stats: 剪枝统计信息
        warnings: 警告信息
        metadata: 元信息
    """
    original_count: int = 0
    pruned_count: int = 0
    retained_count: int = 0
    prune_candidates: List[PruneCandidate] = field(default_factory=list)
    retained_paths: List[str] = field(default_factory=list)
    llm_analyses: List[LLMAnalysis] = field(default_factory=list)
    equivalence_groups: Dict[str, List[str]] = field(default_factory=dict)
    pruning_stats: Dict[str, Any] = field(default_factory=dict)
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
            "prune_candidates": [c.to_dict() for c in self.prune_candidates],
            "retained_paths": self.retained_paths,
            "llm_analyses": [a.to_dict() for a in self.llm_analyses],
            "equivalence_groups": self.equivalence_groups,
            "pruning_stats": self.pruning_stats,
            "warnings": self.warnings,
            "metadata": self.metadata
        }

    def get_pruning_rate(self) -> float:
        """获取剪枝率

        Returns:
            float: 剪枝率（0-100）
        """
        if self.original_count == 0:
            return 0.0
        return (self.pruned_count / self.original_count) * 100


class LLMPathPruneLayer:
    """LLM辅助路径剪枝层【V3.1升级】

    功能描述：
        - 利用LLM分析路径的语义特征
        - 识别语义等价和冗余路径
        - 判断路径的可行性和可达性
        - 评估路径的测试覆盖价值
        - 提供智能剪枝建议
        - 支持批量路径分析和并行处理
        - 生成剪枝报告和替代方案

    输入类型：
        - 枚举的路径列表（List[EnumeratedPath] 或 List[Path]）
        - LLM客户端（用于语义分析）
        - 业务上下文（BusinessRecognitionResult）
        - 剪枝配置

    输出类型：
        - PruningResult: 剪枝结果
        - List[PruneCandidate]: 剪枝候选列表
        - List[LLMAnalysis]: LLM分析结果
        - Dict[str, List[str]]: 等价路径组

    使用场景：
        - 大规模路径集的智能剪枝
        - 去除冗余和等价路径
        - 优化测试用例生成效率
        - 减少无效的测试工作
        - 提高路径分析的准确性

    V3.1升级点：
        - 增强LLM批量分析能力
        - 支持并行路径分析
        - 提供更精确的等价类识别
        - 增加语义相似度计算
        - 支持自定义剪枝规则
    """

    description: str = "LLM辅助路径剪枝层【V3.1升级】- 利用LLM进行智能路径剪枝"
    input_type: str = "List[Path]、LLM客户端和BusinessRecognitionResult"
    output_type: str = "PruningResult和List[PruneCandidate]"

    def __init__(self):
        """初始化LLM辅助路径剪枝层"""
        self.paths = []
        self.llm_client = None
        self.business_result = None
        self.prune_candidates = []
        self.llm_analyses = []
        self.equivalence_groups = {}
        self.pruning_result = None
        self.analysis_cache = {}
        self.config = self._default_config()

    def _default_config(self) -> Dict[str, Any]:
        """获取默认配置

        Returns:
            Dict[str, Any]: 默认配置字典
        """
        return {
            'similarity_threshold': 0.85,
            'batch_size': 10,
            'enable_parallel': True,
            'confidence_threshold': 0.7,
            'preserve_critical_paths': True,
            'min_test_value': 0.3,
            'max_pruning_ratio': 0.8,
            'enable_semantic_analysis': True,
            'llm_model': 'gpt-4'
        }

    def set_config(self, config: Dict[str, Any]) -> None:
        """设置配置

        Args:
            config: 配置字典
        """
        self.config.update(config)

    def set_llm_client(self, client) -> None:
        """设置LLM客户端

        Args:
            client: LLM客户端对象
        """
        self.llm_client = client

    def process(self, context) -> PruningResult:
        """处理路径，执行LLM辅助剪枝

        Args:
            context: PipelineContext对象，包含路径和配置信息

        Returns:
            PruningResult: 剪枝结果

        Raises:
            ValueError: 当输入数据不足时
        """
        if not context.has('enumerated_paths') and not context.has('paths'):
            if not context.has('execution_paths'):
                raise ValueError("LLMPathPruneLayer: 缺少路径数据")

        if context.has('enumerated_paths'):
            self.paths = context.get('enumerated_paths')
        elif context.has('paths'):
            self.paths = context.get('paths')
        elif context.has('execution_paths'):
            self.paths = context.get('execution_paths')

        if context.has('llm_client'):
            self.llm_client = context.get('llm_client')

        if context.has('business_recognition_result'):
            self.business_result = context.get('business_recognition_result')

        if context.has('pruning_config'):
            self.config.update(context.get('pruning_config'))

        self._analyze_paths_with_llm()

        self._identify_equivalence_classes()

        self._generate_prune_candidates()

        self._apply_pruning_decisions()

        self.pruning_result = self._create_pruning_result()

        context.set('prune_candidates', self.prune_candidates)
        context.set('llm_analyses', self.llm_analyses)
        context.set('equivalence_groups', self.equivalence_groups)
        context.set('pruning_result', self.pruning_result)
        context.set('path_pruning_complete', True)
        context.set('pruning_statistics', self._get_statistics())

        return self.pruning_result

    def _analyze_paths_with_llm(self) -> None:
        """使用LLM分析所有路径"""
        if not self.llm_client:
            self._analyze_without_llm()
            return

        if self.config.get('enable_parallel'):
            self._analyze_paths_parallel()
        else:
            self._analyze_paths_sequential()

    def _analyze_paths_parallel(self) -> None:
        """并行分析路径【V3.1增强】"""
        batch_size = self.config.get('batch_size', 10)
        batches = [self.paths[i:i + batch_size] for i in range(0, len(self.paths), batch_size)]

        for batch in batches:
            analyses = self._analyze_batch_with_llm(batch)
            self.llm_analyses.extend(analyses)

    def _analyze_batch_with_llm(self, paths: List) -> List[LLMAnalysis]:
        """批量使用LLM分析路径

        Args:
            paths: 路径批次

        Returns:
            List[LLMAnalysis]: 分析结果列表
        """
        analyses = []

        prompt = self._build_batch_analysis_prompt(paths)

        try:
            response = self.llm_client.analyze(prompt)

            for i, path in enumerate(paths):
                path_id = self._get_path_id(path)

                analysis = self._parse_llm_response(path_id, response, i)

                if analysis:
                    analyses.append(analysis)
                    self.analysis_cache[path_id] = analysis

        except Exception as e:
            for path in paths:
                path_id = self._get_path_id(path)
                fallback = self._create_fallback_analysis(path_id)
                analyses.append(fallback)
                self.analysis_cache[path_id] = fallback

        return analyses

    def _build_batch_analysis_prompt(self, paths: List) -> str:
        """构建批量分析提示

        Args:
            paths: 路径列表

        Returns:
            str: 提示文本
        """
        path_summaries = []
        for i, path in enumerate(paths):
            path_id = self._get_path_id(path)
            nodes = self._extract_path_nodes(path)
            path_summaries.append(f"Path {i+1} ({path_id}): {nodes}")

        prompt = f"""分析以下路径的语义特征：

{chr(10).join(path_summaries)}

对每个路径提供：
1. 语义摘要（20字内）
2. 行为描述（30字内）
3. 识别的边界情况
4. 潜在问题
5. 等价类标识（相似路径使用相同标识）
6. 测试建议

以JSON格式返回结果。"""

        return prompt

    def _parse_llm_response(self, path_id: str, response: str, index: int) -> Optional[LLMAnalysis]:
        """解析LLM响应

        Args:
            path_id: 路径标识符
            response: LLM响应文本
            index: 路径索引

        Returns:
            Optional[LLMAnalysis]: 分析结果
        """
        try:
            import json

            data = json.loads(response)

            if isinstance(data, list) and index < len(data):
                item = data[index]
            elif isinstance(data, dict):
                item = data
            else:
                return None

            analysis = LLMAnalysis(
                path_id=path_id,
                semantic_summary=item.get('semantic_summary', ''),
                behavioral_description=item.get('behavioral_description', ''),
                edge_cases=item.get('edge_cases', []),
                potential_issues=item.get('potential_issues', []),
                test_recommendations=item.get('test_recommendations', []),
                equivalence_class=item.get('equivalence_class', ''),
                confidence=item.get('confidence', 0.7),
                processing_time=0.0
            )

            return analysis

        except Exception:
            return self._create_fallback_analysis(path_id)

    def _create_fallback_analysis(self, path_id: str) -> LLMAnalysis:
        """创建备用分析（无LLM时使用）

        Args:
            path_id: 路径标识符

        Returns:
            LLMAnalysis: 备用分析结果
        """
        return LLMAnalysis(
            path_id=path_id,
            semantic_summary="路径分析",
            behavioral_description="执行相关代码路径",
            confidence=0.5
        )

    def _analyze_paths_sequential(self) -> None:
        """顺序分析路径"""
        for path in self.paths:
            path_id = self._get_path_id(path)

            if path_id in self.analysis_cache:
                self.llm_analyses.append(self.analysis_cache[path_id])
                continue

            if self.llm_client:
                analysis = self._analyze_single_path_with_llm(path)
            else:
                analysis = self._create_fallback_analysis(path_id)

            self.llm_analyses.append(analysis)
            self.analysis_cache[path_id] = analysis

    def _analyze_single_path_with_llm(self, path) -> LLMAnalysis:
        """使用LLM分析单个路径

        Args:
            path: 路径对象

        Returns:
            LLMAnalysis: 分析结果
        """
        path_id = self._get_path_id(path)
        prompt = self._build_single_analysis_prompt(path)

        try:
            response = self.llm_client.analyze(prompt)
            analysis = self._parse_llm_response(path_id, response, 0)
            if analysis:
                return analysis
        except Exception:
            pass

        return self._create_fallback_analysis(path_id)

    def _build_single_analysis_prompt(self, path) -> str:
        """构建单个路径分析提示

        Args:
            path: 路径对象

        Returns:
            str: 提示文本
        """
        path_id = self._get_path_id(path)
        nodes = self._extract_path_nodes(path)
        code = self._extract_path_code(path)

        prompt = f"""分析以下路径：

路径ID: {path_id}
节点序列: {nodes}
代码片段: {code[:200]}

提供：
1. 语义摘要
2. 行为描述
3. 边界情况
4. 潜在问题
5. 等价类
6. 测试建议

以JSON格式返回。"""

        return prompt

    def _analyze_without_llm(self) -> None:
        """无LLM时的简化分析"""
        for path in self.paths:
            path_id = self._get_path_id(path)
            analysis = self._create_fallback_analysis(path_id)
            self.llm_analyses.append(analysis)
            self.analysis_cache[path_id] = analysis

    def _identify_equivalence_classes(self) -> None:
        """识别等价类"""
        class_to_paths = defaultdict(list)

        for analysis in self.llm_analyses:
            if analysis.equivalence_class:
                class_to_paths[analysis.equivalence_class].append(analysis.path_id)
            else:
                signature = self._compute_path_signature(analysis.path_id)
                class_to_paths[signature].append(analysis.path_id)

        self.equivalence_groups = {k: v for k, v in class_to_paths.items() if len(v) > 1}

    def _compute_path_signature(self, path_id: str) -> str:
        """计算路径签名

        Args:
            path_id: 路径标识符

        Returns:
            str: 路径签名
        """
        if path_id in self.analysis_cache:
            analysis = self.analysis_cache[path_id]
            return f"class_{hash(analysis.semantic_summary) % 1000}"

        return f"class_{hash(path_id) % 1000}"

    def _generate_prune_candidates(self) -> None:
        """生成剪枝候选"""
        self.prune_candidates = []

        for eq_class, path_ids in self.equivalence_groups.items():
            if len(path_ids) > 1:
                candidates = self._select_paths_to_prune(path_ids)
                for path_id in candidates:
                    candidate = self._create_prune_candidate(path_id, eq_class)
                    self.prune_candidates.append(candidate)

        paths_without_equivalence = self._find_non_equivalent_paths()
        for path_id in paths_without_equivalence:
            analysis = self.analysis_cache.get(path_id)
            if analysis and analysis.confidence < self.config.get('confidence_threshold', 0.7):
                candidate = self._create_prune_candidate(path_id, 'low_confidence')
                self.prune_candidates.append(candidate)

    def _select_paths_to_prune(self, path_ids: List[str]) -> List[str]:
        """选择要剪枝的路径

        Args:
            path_ids: 路径标识符列表

        Returns:
            List[str]: 要剪枝的路径标识符
        """
        path_values = []

        for path_id in path_ids:
            value = self._estimate_path_value(path_id)
            path_values.append((path_id, value))

        path_values.sort(key=lambda x: x[1], reverse=True)

        keep_count = max(1, len(path_ids) // 3)

        prune_paths = [pv[0] for pv in path_values[keep_count:]]

        return prune_paths

    def _estimate_path_value(self, path_id: str) -> float:
        """估算路径价值

        Args:
            path_id: 路径标识符

        Returns:
            float: 价值评分
        """
        analysis = self.analysis_cache.get(path_id)
        if not analysis:
            return 0.5

        value = analysis.confidence

        if len(analysis.edge_cases) > 0:
            value += 0.2

        if len(analysis.potential_issues) > 0:
            value += 0.1

        return min(1.0, value)

    def _create_prune_candidate(self, path_id: str, eq_class: str) -> PruneCandidate:
        """创建剪枝候选

        Args:
            path_id: 路径标识符
            eq_class: 等价类

        Returns:
            PruneCandidate: 剪枝候选对象
        """
        analysis = self.analysis_cache.get(path_id)

        candidate = PruneCandidate(
            path_id=path_id,
            prune_reason=PruneReason.SEMANTICALLY_SIMILAR,
            confidence=PruneConfidence.HIGH if analysis and analysis.confidence > 0.8 else PruneConfidence.MEDIUM,
            equivalent_paths=self.equivalence_groups.get(eq_class, []),
            analysis=analysis.to_dict() if analysis else {}
        )

        equivalent = self.equivalence_groups.get(eq_class, [])
        if path_id in equivalent:
            candidate.suggested_alternative = next(
                (pid for pid in equivalent if pid != path_id), None
            )

        candidate.preservation_criteria = self._generate_preservation_criteria(candidate)

        candidate.test_coverage_impact = self._estimate_coverage_impact(path_id)

        return candidate

    def _generate_preservation_criteria(self, candidate: PruneCandidate) -> List[str]:
        """生成保留条件

        Args:
            candidate: 剪枝候选

        Returns:
            List[str]: 保留条件列表
        """
        criteria = []

        if candidate.test_coverage_impact > 0.3:
            criteria.append("高测试覆盖影响 - 谨慎剪枝")

        if candidate.confidence == PruneConfidence.LOW:
            criteria.append("低置信度 - 建议保留以验证")

        analysis = candidate.analysis
        if analysis.get('potential_issues'):
            criteria.append("包含潜在问题 - 需要测试")

        return criteria

    def _estimate_coverage_impact(self, path_id: str) -> float:
        """估算覆盖影响

        Args:
            path_id: 路径标识符

        Returns:
            float: 覆盖影响评分
        """
        for path in self.paths:
            if self._get_path_id(path) == path_id:
                if hasattr(path, 'coverage_potential'):
                    return 1.0 - path.coverage_potential
                if hasattr(path, 'test_value'):
                    return 1.0 - path.test_value

        return 0.3

    def _find_non_equivalent_paths(self) -> List[str]:
        """查找无等价类的路径

        Returns:
            List[str]: 路径标识符列表
        """
        all_path_ids = set(self._get_path_id(p) for p in self.paths)
        equivalent_path_ids = set()

        for path_ids in self.equivalence_groups.values():
            equivalent_path_ids.update(path_ids)

        return list(all_path_ids - equivalent_path_ids)

    def _apply_pruning_decisions(self) -> None:
        """应用剪枝决策"""
        prune_ids = set(c.path_id for c in self.prune_candidates)

        max_prune_ratio = self.config.get('max_pruning_ratio', 0.8)
        max_prune_count = int(len(self.paths) * max_prune_ratio)

        if len(prune_ids) > max_prune_count:
            candidates_by_confidence = sorted(
                self.prune_candidates,
                key=lambda c: c.confidence.value
            )
            prune_ids = set(c.path_id for c in candidates_by_confidence[:max_prune_count])

        self.pruned_path_ids = prune_ids
        self.retained_path_ids = set(self._get_path_id(p) for p in self.paths) - prune_ids

    def _create_pruning_result(self) -> PruningResult:
        """创建剪枝结果

        Returns:
            PruningResult: 剪枝结果
        """
        result = PruningResult(
            original_count=len(self.paths),
            pruned_count=len(self.pruned_path_ids),
            retained_count=len(self.retained_path_ids),
            prune_candidates=self.prune_candidates,
            retained_paths=list(self.retained_path_ids)
        )

        result.llm_analyses = self.llm_analyses
        result.equivalence_groups = self.equivalence_groups

        result.pruning_stats = self._compute_pruning_stats()

        if len(self.pruned_path_ids) > len(self.paths) * 0.5:
            result.warnings.append("剪枝率超过50%，可能影响测试覆盖")

        result.metadata = {
            'pruning_rate': result.get_pruning_rate(),
            'avg_confidence': sum(a.confidence for a in self.llm_analyses) / len(self.llm_analyses) if self.llm_analyses else 0,
            'equivalence_classes': len(self.equivalence_groups)
        }

        return result

    def _compute_pruning_stats(self) -> Dict[str, Any]:
        """计算剪枝统计

        Returns:
            Dict[str, Any]: 统计信息
        """
        stats = {
            'total_paths': len(self.paths),
            'pruned_paths': len(self.pruned_path_ids),
            'retained_paths': len(self.retained_path_ids),
            'equivalence_classes': len(self.equivalence_groups),
            'avg_path_value': sum(self._estimate_path_value(pid) for pid in self.retained_path_ids) / len(self.retained_path_ids) if self.retained_path_ids else 0
        }

        reason_counts = defaultdict(int)
        for candidate in self.prune_candidates:
            reason_counts[candidate.prune_reason.name] += 1
        stats['prune_reasons'] = dict(reason_counts)

        confidence_counts = defaultdict(int)
        for candidate in self.prune_candidates:
            confidence_counts[candidate.confidence.name] += 1
        stats['confidence_distribution'] = dict(confidence_counts)

        return stats

    def _get_path_id(self, path) -> str:
        """获取路径标识符

        Args:
            path: 路径对象

        Returns:
            str: 路径标识符
        """
        return getattr(path, 'path_id', '') or getattr(path, 'execution_id', str(id(path)))

    def _extract_path_nodes(self, path) -> str:
        """提取路径节点

        Args:
            path: 路径对象

        Returns:
            str: 节点序列字符串
        """
        if hasattr(path, 'nodes'):
            return ' -> '.join(str(n) for n in path.nodes[:10])

        return 'unknown'

    def _extract_path_code(self, path) -> str:
        """提取路径代码

        Args:
            path: 路径对象

        Returns:
            str: 代码字符串
        """
        if hasattr(path, 'source_code'):
            return path.source_code

        if hasattr(path, 'code'):
            return path.code

        return ''

    def _get_statistics(self) -> Dict[str, Any]:
        """获取统计信息

        Returns:
            Dict[str, Any]: 统计信息
        """
        if not self.pruning_result:
            return {}

        return {
            'original_count': self.pruning_result.original_count,
            'pruned_count': self.pruning_result.pruned_count,
            'retained_count': self.pruning_result.retained_count,
            'pruning_rate': self.pruning_result.get_pruning_rate(),
            'equivalence_classes': len(self.equivalence_groups),
            'pruning_stats': self.pruning_result.pruning_stats
        }

    def get_retained_paths(self) -> List[str]:
        """获取保留的路径列表

        Returns:
            List[str]: 保留路径标识符
        """
        return list(self.retained_path_ids)

    def get_pruned_by_reason(self, reason: PruneReason) -> List[PruneCandidate]:
        """按原因获取剪枝候选

        Args:
            reason: 剪枝原因

        Returns:
            List[PruneCandidate]: 剪枝候选列表
        """
        return [c for c in self.prune_candidates if c.prune_reason == reason]

    def get_high_confidence_prunes(self) -> List[PruneCandidate]:
        """获取高置信度剪枝

        Returns:
            List[PruneCandidate]: 高置信度剪枝候选
        """
        return [c for c in self.prune_candidates if c.confidence == PruneConfidence.HIGH]

    def export_pruning_report(self) -> Dict[str, Any]:
        """导出剪枝报告

        Returns:
            Dict[str, Any]: 剪枝报告
        """
        return {
            'summary': {
                'original': self.pruning_result.original_count,
                'pruned': self.pruning_result.pruned_count,
                'retained': self.pruning_result.retained_count,
                'pruning_rate': self.pruning_result.get_pruning_rate()
            },
            'equivalence_groups': self.equivalence_groups,
            'candidates': [c.to_dict() for c in self.prune_candidates],
            'statistics': self.pruning_result.pruning_stats,
            'warnings': self.pruning_result.warnings
        }

    def suggest_recovery_paths(self, pruned_count: int = 5) -> List[Dict[str, Any]]:
        """建议恢复路径（高价值被剪枝路径）

        Args:
            pruned_count: 建议恢复数量

        Returns:
            List[Dict[str, Any]]: 恢复建议
        """
        pruned_candidates = [c for c in self.prune_candidates
                          if c.business_impact == 'high' or c.test_coverage_impact > 0.5]

        suggestions = []
        for candidate in pruned_candidates[:pruned_count]:
            suggestions.append({
                'path_id': candidate.path_id,
                'reason': candidate.prune_reason.name,
                'coverage_impact': candidate.test_coverage_impact,
                'alternative': candidate.suggested_alternative
            })

        return suggestions
