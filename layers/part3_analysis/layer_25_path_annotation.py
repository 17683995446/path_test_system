"""
Layer 25: PathAnnotationLayer - 路径语义标注层

本层负责对执行路径进行语义标注，为每条路径添加有意义的标签和描述，
帮助理解路径的业务含义和测试价值。
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import defaultdict


class PathCategory(Enum):
    """路径类别枚举"""
    BUSINESS_LOGIC = auto()
    VALIDATION = auto()
    ERROR_HANDLING = auto()
    DATA_PROCESSING = auto()
    STATE_TRANSITION = auto()
    QUERY_OPERATION = auto()
    TRANSACTION = auto()
    AUTHENTICATION = auto()
    AUTHORIZATION = auto()
    NOTIFICATION = auto()
    AUDIT = auto()
    UTILITY = auto()
    UNKNOWN = auto()


class PathComplexity(Enum):
    """路径复杂度枚举"""
    TRIVIAL = auto()
    SIMPLE = auto()
    MODERATE = auto()
    COMPLEX = auto()
    VERY_COMPLEX = auto()


class AnnotationType(Enum):
    """标注类型枚举"""
    BUSINESS_RULE = auto()
    VALIDATION_RULE = auto()
    ERROR_CONDITION = auto()
    SECURITY_CHECK = auto()
    PERFORMANCE_HOTSPOT = auto()
    DATA_DEPENDENCY = auto()
    EXTERNAL_CALL = auto()
    STATE_CHANGE = auto()


@dataclass
class PathAnnotation:
    """路径标注信息

    Attributes:
        path_id: 路径标识符
        category: 路径类别
        complexity: 复杂度等级
        business_meaning: 业务含义描述
        semantic_tags: 语义标签列表
        annotations: 详细标注列表
        coverage_importance: 覆盖重要性评分
        test_focus: 测试关注点
        risk_level: 风险等级
        prerequisites: 前置条件
        expected_behavior: 预期行为描述
    """
    path_id: str
    category: PathCategory
    complexity: PathComplexity
    business_meaning: str = ""
    semantic_tags: List[str] = field(default_factory=list)
    annotations: List[Dict[str, Any]] = field(default_factory=list)
    coverage_importance: float = 0.5
    test_focus: List[str] = field(default_factory=list)
    risk_level: str = "medium"
    prerequisites: List[str] = field(default_factory=list)
    expected_behavior: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "path_id": self.path_id,
            "category": self.category.name,
            "complexity": self.complexity.name,
            "business_meaning": self.business_meaning,
            "semantic_tags": self.semantic_tags,
            "annotations": self.annotations,
            "coverage_importance": self.coverage_importance,
            "test_focus": self.test_focus,
            "risk_level": self.risk_level,
            "prerequisites": self.prerequisites,
            "expected_behavior": self.expected_behavior
        }

    def add_tag(self, tag: str) -> None:
        """添加语义标签

        Args:
            tag: 标签字符串
        """
        if tag not in self.semantic_tags:
            self.semantic_tags.append(tag)

    def add_annotation(self, annotation_type: AnnotationType, description: str,
                       importance: float = 0.5) -> None:
        """添加详细标注

        Args:
            annotation_type: 标注类型
            description: 描述信息
            importance: 重要性评分
        """
        self.annotations.append({
            "type": annotation_type.name,
            "description": description,
            "importance": importance
        })


@dataclass
class AnnotatedPath:
    """带标注的路径

    Attributes:
        path_id: 路径标识符
        original_path: 原始路径数据
        annotation: 路径标注
        enhanced_description: 增强的描述
        test_hints: 测试提示列表
        suggested_inputs: 建议的输入值
        related_paths: 相关路径列表
        confidence: 标注置信度
    """
    path_id: str
    original_path: Dict[str, Any]
    annotation: PathAnnotation
    enhanced_description: str = ""
    test_hints: List[str] = field(default_factory=list)
    suggested_inputs: Dict[str, Any] = field(default_factory=dict)
    related_paths: List[str] = field(default_factory=list)
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "path_id": self.path_id,
            "original_path": self.original_path,
            "annotation": self.annotation.to_dict(),
            "enhanced_description": self.enhanced_description,
            "test_hints": self.test_hints,
            "suggested_inputs": self.suggested_inputs,
            "related_paths": self.related_paths,
            "confidence": self.confidence
        }


@dataclass
class AnnotationResult:
    """标注结果汇总

    Attributes:
        total_paths: 总路径数
        annotated_paths: 已标注路径数
        category_distribution: 类别分布
        complexity_distribution: 复杂度分布
        high_priority_paths: 高优先级路径列表
        annotated_paths_list: 带标注的路径列表
        statistics: 统计信息
        metadata: 元信息
    """
    total_paths: int = 0
    annotated_paths: int = 0
    category_distribution: Dict[str, int] = field(default_factory=dict)
    complexity_distribution: Dict[str, int] = field(default_factory=dict)
    high_priority_paths: List[str] = field(default_factory=list)
    annotated_paths_list: List[AnnotatedPath] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "total_paths": self.total_paths,
            "annotated_paths": self.annotated_paths,
            "category_distribution": self.category_distribution,
            "complexity_distribution": self.complexity_distribution,
            "high_priority_paths": self.high_priority_paths,
            "annotated_paths": [p.to_dict() for p in self.annotated_paths_list],
            "statistics": self.statistics,
            "metadata": self.metadata
        }

    def get_annotation_rate(self) -> float:
        """获取标注率

        Returns:
            float: 标注率（0-100）
        """
        if self.total_paths == 0:
            return 0.0
        return (self.annotated_paths / self.total_paths) * 100


class PathAnnotationLayer:
    """路径语义标注层

    功能描述：
        - 对执行路径进行语义分析和标注
        - 识别路径的业务含义和类别
        - 评估路径的复杂度和测试价值
        - 生成有意义的路径描述和标签
        - 识别路径中的关键点和测试关注点
        - 支持业务规则的路径标注
        - 提供路径间的关系分析

    输入类型：
        - 执行路径列表（List[Path] 或 List[ExecutionPath]）
        - 业务识别结果（BusinessRecognitionResult）
        - 函数切片列表（用于语义理解）

    输出类型：
        - AnnotationResult: 标注结果汇总
        - List[AnnotatedPath]: 带标注的路径列表
        - Dict[str, PathAnnotation]: 路径标注字典

    使用场景：
        - 帮助理解复杂路径的业务含义
        - 指导测试用例的设计和优先级排序
        - 识别测试覆盖的关键路径
        - 支持路径可视化时的语义展示
        - 辅助回归测试的路径选择

    V3.1升级点：
        - 增强多维度语义分析能力
        - 提供更精确的业务规则识别
        - 支持跨路径的关系标注
        - 增加对复杂控制流的语义理解
        - 提供更智能的测试建议
    """

    description: str = "路径语义标注层 - 为路径添加业务语义和测试价值标注"
    input_type: str = "List[Path]、BusinessRecognitionResult和函数切片"
    output_type: str = "AnnotationResult和List[AnnotatedPath]"

    def __init__(self):
        """初始化路径语义标注层"""
        self.paths = []
        self.business_result = None
        self.function_slices = []
        self.semantic_patterns = self._init_semantic_patterns()
        self.category_keywords = self._init_category_keywords()
        self.annotated_paths = []
        self.annotation_result = None

    def _init_semantic_patterns(self) -> Dict[AnnotationType, Dict[str, Any]]:
        """初始化语义模式库

        Returns:
            Dict[AnnotationType, Dict[str, Any]]: 语义模式字典
        """
        return {
            AnnotationType.BUSINESS_RULE: {
                'keywords': ['rule', 'policy', 'business', 'calculate', 'apply', 'validate_business'],
                'weight': 1.0
            },
            AnnotationType.VALIDATION_RULE: {
                'keywords': ['validate', 'check', 'verify', 'assert', 'required', 'format'],
                'weight': 0.9
            },
            AnnotationType.ERROR_CONDITION: {
                'keywords': ['error', 'exception', 'raise', 'catch', 'fail', 'invalid', 'timeout'],
                'weight': 1.0
            },
            AnnotationType.SECURITY_CHECK: {
                'keywords': ['authenticate', 'authorize', 'permission', 'security', 'sanitize', 'escape'],
                'weight': 1.0
            },
            AnnotationType.PERFORMANCE_HOTSPOT: {
                'keywords': ['loop', 'batch', 'bulk', 'optimize', 'cache', 'index'],
                'weight': 0.8
            },
            AnnotationType.DATA_DEPENDENCY: {
                'keywords': ['join', 'foreign', 'reference', 'relation', 'dependency', 'coupling'],
                'weight': 0.7
            },
            AnnotationType.EXTERNAL_CALL: {
                'keywords': ['api', 'http', 'request', 'call', 'external', 'service', 'grpc'],
                'weight': 0.9
            },
            AnnotationType.STATE_CHANGE: {
                'keywords': ['state', 'status', 'transition', 'update', 'change', 'transition'],
                'weight': 0.8
            }
        }

    def _init_category_keywords(self) -> Dict[PathCategory, List[str]]:
        """初始化类别关键词

        Returns:
            Dict[PathCategory, List[str]]: 类别关键词字典
        """
        return {
            PathCategory.BUSINESS_LOGIC: ['calculate', 'process', 'handle', 'execute', 'apply', 'determine'],
            PathCategory.VALIDATION: ['validate', 'check', 'verify', 'ensure', 'test', 'compare'],
            PathCategory.ERROR_HANDLING: ['error', 'exception', 'catch', 'handle_error', 'retry', 'fallback'],
            PathCategory.DATA_PROCESSING: ['transform', 'convert', 'parse', 'format', 'encode', 'decode'],
            PathCategory.STATE_TRANSITION: ['state', 'transition', 'status', 'change_state', 'update'],
            PathCategory.QUERY_OPERATION: ['query', 'search', 'find', 'filter', 'select', 'fetch'],
            PathCategory.TRANSACTION: ['transaction', 'commit', 'rollback', 'atomic', 'lock'],
            PathCategory.AUTHENTICATION: ['login', 'authenticate', 'token', 'credential', 'verify_identity'],
            PathCategory.AUTHORIZATION: ['authorize', 'permission', 'access', 'role', 'check_access'],
            PathCategory.NOTIFICATION: ['notify', 'send', 'email', 'message', 'push', 'alert'],
            PathCategory.AUDIT: ['audit', 'log', 'history', 'track', 'record'],
            PathCategory.UTILITY: ['helper', 'util', 'common', 'shared', 'format', 'parse']
        }

    def process(self, context) -> AnnotationResult:
        """处理路径，生成语义标注

        Args:
            context: PipelineContext对象，包含路径和业务信息

        Returns:
            AnnotationResult: 标注结果汇总

        Raises:
            ValueError: 当输入数据不足时
        """
        if not context.has('execution_paths') and not context.has('paths'):
            if not context.has('function_slices'):
                raise ValueError("PathAnnotationLayer: 缺少路径或函数切片数据")

        if context.has('execution_paths'):
            self.paths = context.get('execution_paths')
        elif context.has('paths'):
            self.paths = context.get('paths')

        if context.has('business_recognition_result'):
            self.business_result = context.get('business_recognition_result')

        if context.has('function_slices'):
            self.function_slices = context.get('function_slices')

        self.annotated_paths = self._annotate_all_paths()

        self.annotation_result = self._create_annotation_result()

        context.set('path_annotations', {ap.path_id: ap.annotation for ap in self.annotated_paths})
        context.set('annotated_paths', self.annotated_paths)
        context.set('annotation_result', self.annotation_result)
        context.set('path_annotation_complete', True)
        context.set('annotation_statistics', self._get_statistics())

        return self.annotation_result

    def _annotate_all_paths(self) -> List[AnnotatedPath]:
        """为所有路径生成标注

        Returns:
            List[AnnotatedPath]: 带标注的路径列表
        """
        annotated = []

        for path in self.paths:
            path_id = getattr(path, 'path_id', '') or getattr(path, 'execution_id', f'path_{len(annotated)}')
            original_path = path.to_dict() if hasattr(path, 'to_dict') else {'path_id': path_id}

            annotation = self._annotate_single_path(path)

            enhanced_desc = self._generate_enhanced_description(path, annotation)

            test_hints = self._generate_test_hints(annotation)

            suggested_inputs = self._suggest_test_inputs(annotation)

            related = self._find_related_paths(path_id)

            annotated_path = AnnotatedPath(
                path_id=path_id,
                original_path=original_path,
                annotation=annotation,
                enhanced_description=enhanced_desc,
                test_hints=test_hints,
                suggested_inputs=suggested_inputs,
                related_paths=related,
                confidence=self._calculate_annotation_confidence(annotation)
            )

            annotated.append(annotated_path)

        return annotated

    def _annotate_single_path(self, path) -> PathAnnotation:
        """为单个路径生成标注

        Args:
            path: 路径对象

        Returns:
            PathAnnotation: 路径标注
        """
        path_id = getattr(path, 'path_id', '') or getattr(path, 'execution_id', 'unknown')

        source_code = self._extract_path_code(path)

        category = self._classify_path_category(source_code)

        complexity = self._assess_path_complexity(path)

        business_meaning = self._extract_business_meaning(path, category)

        semantic_tags = self._extract_semantic_tags(source_code)

        annotations = self._generate_detailed_annotations(source_code)

        coverage_importance = self._calculate_coverage_importance(
            category, complexity, annotations
        )

        test_focus = self._identify_test_focus(category, annotations)

        risk_level = self._assess_risk_level(category, annotations, complexity)

        prerequisites = self._extract_prerequisites(path)

        expected_behavior = self._describe_expected_behavior(path, category)

        annotation = PathAnnotation(
            path_id=path_id,
            category=category,
            complexity=complexity,
            business_meaning=business_meaning,
            semantic_tags=semantic_tags,
            annotations=annotations,
            coverage_importance=coverage_importance,
            test_focus=test_focus,
            risk_level=risk_level,
            prerequisites=prerequisites,
            expected_behavior=expected_behavior
        )

        return annotation

    def _extract_path_code(self, path) -> str:
        """提取路径代码

        Args:
            path: 路径对象

        Returns:
            str: 路径代码字符串
        """
        code_parts = []

        if hasattr(path, 'path_representation') and path.path_representation:
            code_parts.append(path.path_representation)

        if hasattr(path, 'nodes'):
            for node_id in path.nodes:
                if hasattr(path, 'get_node_code'):
                    node_code = path.get_node_code(node_id)
                    if node_code:
                        code_parts.append(node_code)

        if hasattr(path, 'source_code'):
            code_parts.append(path.source_code)

        if not code_parts and hasattr(path, 'code'):
            code_parts.append(path.code)

        return ' '.join(code_parts).lower()

    def _classify_path_category(self, source_code: str) -> PathCategory:
        """分类路径类别

        Args:
            source_code: 路径代码

        Returns:
            PathCategory: 路径类别
        """
        category_scores = defaultdict(float)

        for category, keywords in self.category_keywords.items():
            score = 0.0
            for keyword in keywords:
                if keyword in source_code:
                    score += 1.0

            if score > 0:
                category_scores[category] = score

        if not category_scores:
            return PathCategory.UNKNOWN

        best_category = max(category_scores.items(), key=lambda x: x[1])[0]
        return best_category

    def _assess_path_complexity(self, path) -> PathComplexity:
        """评估路径复杂度

        Args:
            path: 路径对象

        Returns:
            PathComplexity: 复杂度等级
        """
        complexity_score = 0

        if hasattr(path, 'nodes'):
            complexity_score += len(path.nodes) * 0.1

        if hasattr(path, 'segments'):
            complexity_score += len(path.segments) * 0.5

        if hasattr(path, 'conditions'):
            complexity_score += len(path.conditions) * 1.0

        if hasattr(path, 'complexity'):
            complexity_score += path.complexity * 0.5

        if hasattr(path, 'metadata'):
            if path.metadata.get('has_recursion'):
                complexity_score += 3.0
            if path.metadata.get('has_loop'):
                complexity_score += 1.0
            if path.metadata.get('has_exception'):
                complexity_score += 0.5

        if complexity_score < 2:
            return PathComplexity.TRIVIAL
        elif complexity_score < 5:
            return PathComplexity.SIMPLE
        elif complexity_score < 10:
            return PathComplexity.MODERATE
        elif complexity_score < 20:
            return PathComplexity.COMPLEX
        else:
            return PathComplexity.VERY_COMPLEX

    def _extract_business_meaning(self, path, category: PathCategory) -> str:
        """提取业务含义

        Args:
            path: 路径对象
            category: 路径类别

        Returns:
            str: 业务含义描述
        """
        function_name = getattr(path, 'function_name', '')

        business_meanings = {
            PathCategory.BUSINESS_LOGIC: f"执行业务逻辑: {function_name}",
            PathCategory.VALIDATION: f"执行验证检查: {function_name}",
            PathCategory.ERROR_HANDLING: f"处理错误和异常: {function_name}",
            PathCategory.DATA_PROCESSING: f"处理数据转换: {function_name}",
            PathCategory.STATE_TRANSITION: f"状态转换: {function_name}",
            PathCategory.QUERY_OPERATION: f"执行查询操作: {function_name}",
            PathCategory.TRANSACTION: f"管理事务: {function_name}",
            PathCategory.AUTHENTICATION: f"用户认证: {function_name}",
            PathCategory.AUTHORIZATION: f"权限检查: {function_name}",
            PathCategory.NOTIFICATION: f"发送通知: {function_name}",
            PathCategory.AUDIT: f"审计日志: {function_name}",
            PathCategory.UTILITY: f"工具函数: {function_name}",
            PathCategory.UNKNOWN: f"未知功能: {function_name}"
        }

        return business_meanings.get(category, f"功能: {function_name}")

    def _extract_semantic_tags(self, source_code: str) -> List[str]:
        """提取语义标签

        Args:
            source_code: 源代码

        Returns:
            List[str]: 语义标签列表
        """
        tags = set()

        tag_keywords = {
            'critical': ['critical', 'essential', 'must', 'required', 'mandatory'],
            'async': ['async', 'await', 'concurrent', 'parallel'],
            'database': ['db', 'database', 'sql', 'query', 'transaction'],
            'api': ['api', 'http', 'rest', 'endpoint', 'request'],
            'cache': ['cache', 'redis', 'memcached', 'ttl'],
            'security': ['auth', 'security', 'encrypt', 'decrypt', 'hash'],
            'logging': ['log', 'debug', 'trace', 'audit'],
            'config': ['config', 'setting', 'parameter', 'option']
        }

        for tag, keywords in tag_keywords.items():
            if any(keyword in source_code for keyword in keywords):
                tags.add(tag)

        return list(tags)

    def _generate_detailed_annotations(self, source_code: str) -> List[Dict[str, Any]]:
        """生成详细标注

        Args:
            source_code: 源代码

        Returns:
            List[Dict[str, Any]]: 标注列表
        """
        annotations = []

        for annotation_type, config in self.semantic_patterns.items():
            keywords = config['keywords']
            weight = config['weight']

            matched_keywords = [kw for kw in keywords if kw in source_code]

            if matched_keywords:
                annotations.append({
                    "type": annotation_type.name,
                    "description": f"发现{annotation_type.name}: {', '.join(matched_keywords)}",
                    "importance": weight,
                    "matched_keywords": matched_keywords
                })

        return annotations

    def _calculate_coverage_importance(self, category: PathCategory,
                                     complexity: PathComplexity,
                                     annotations: List[Dict[str, Any]]) -> float:
        """计算覆盖重要性

        Args:
            category: 路径类别
            complexity: 复杂度
            annotations: 标注列表

        Returns:
            float: 覆盖重要性评分（0-1）
        """
        importance = 0.5

        if category in [PathCategory.BUSINESS_LOGIC, PathCategory.ERROR_HANDLING,
                       PathCategory.AUTHENTICATION, PathCategory.AUTHORIZATION]:
            importance += 0.2

        if complexity in [PathComplexity.COMPLEX, PathComplexity.VERY_COMPLEX]:
            importance += 0.15

        high_importance_count = sum(1 for ann in annotations if ann.get('importance', 0) >= 0.9)
        importance += high_importance_count * 0.05

        return min(1.0, importance)

    def _identify_test_focus(self, category: PathCategory,
                           annotations: List[Dict[str, Any]]) -> List[str]:
        """识别测试关注点

        Args:
            category: 路径类别
            annotations: 标注列表

        Returns:
            List[str]: 测试关注点列表
        """
        focus_points = []

        focus_map = {
            PathCategory.BUSINESS_LOGIC: ["验证业务规则正确性", "检查业务约束"],
            PathCategory.VALIDATION: ["边界值测试", "异常输入测试"],
            PathCategory.ERROR_HANDLING: ["异常场景覆盖", "错误恢复测试"],
            PathCategory.DATA_PROCESSING: ["数据转换准确性", "格式兼容性"],
            PathCategory.TRANSACTION: ["事务一致性", "回滚机制"],
            PathCategory.AUTHENTICATION: ["认证流程", "会话管理"],
            PathCategory.AUTHORIZATION: ["权限边界", "越权测试"],
            PathCategory.QUERY_OPERATION: ["查询性能", "结果准确性"]
        }

        if category in focus_map:
            focus_points.extend(focus_map[category])

        for annotation in annotations:
            if annotation['type'] == 'SECURITY_CHECK':
                focus_points.append("安全相关测试")
            elif annotation['type'] == 'PERFORMANCE_HOTSPOT':
                focus_points.append("性能测试")
            elif annotation['type'] == 'EXTERNAL_CALL':
                focus_points.append("外部依赖测试")

        return list(set(focus_points))

    def _assess_risk_level(self, category: PathCategory,
                         annotations: List[Dict[str, Any]],
                         complexity: PathComplexity) -> str:
        """评估风险等级

        Args:
            category: 路径类别
            annotations: 标注列表
            complexity: 复杂度

        Returns:
            str: 风险等级
        """
        risk_score = 0

        high_risk_categories = [PathCategory.TRANSACTION, PathCategory.AUTHENTICATION,
                               PathCategory.AUTHORIZATION, PathCategory.PAYMENT]
        if category in high_risk_categories:
            risk_score += 2

        if complexity in [PathComplexity.COMPLEX, PathComplexity.VERY_COMPLEX]:
            risk_score += 1

        for annotation in annotations:
            if annotation['type'] in ['ERROR_CONDITION', 'SECURITY_CHECK', 'EXTERNAL_CALL']:
                risk_score += 1

        if risk_score >= 4:
            return "high"
        elif risk_score >= 2:
            return "medium"
        else:
            return "low"

    def _extract_prerequisites(self, path) -> List[str]:
        """提取前置条件

        Args:
            path: 路径对象

        Returns:
            List[str]: 前置条件列表
        """
        prerequisites = []

        if hasattr(path, 'dependencies'):
            for dep in path.dependencies:
                prerequisites.append(f"依赖: {dep}")

        if hasattr(path, 'variables'):
            for var in path.variables[:5]:
                prerequisites.append(f"变量: {var}")

        if hasattr(path, 'metadata'):
            if path.metadata.get('requires_auth'):
                prerequisites.append("需要用户认证")
            if path.metadata.get('requires_db'):
                prerequisites.append("需要数据库连接")
            if path.metadata.get('requires_cache'):
                prerequisites.append("需要缓存服务")

        return prerequisites

    def _describe_expected_behavior(self, path, category: PathCategory) -> str:
        """描述预期行为

        Args:
            path: 路径对象
            category: 路径类别

        Returns:
            str: 预期行为描述
        """
        function_name = getattr(path, 'function_name', 'unknown')

        behavior_map = {
            PathCategory.BUSINESS_LOGIC: f"应正确执行业务逻辑并返回预期结果",
            PathCategory.VALIDATION: f"应验证输入并正确处理合法/非法值",
            PathCategory.ERROR_HANDLING: f"应捕获并适当处理所有异常情况",
            PathCategory.DATA_PROCESSING: f"应准确转换数据格式",
            PathCategory.QUERY_OPERATION: f"应返回准确的查询结果",
            PathCategory.TRANSACTION: f"应保证事务的原子性和一致性",
            PathCategory.AUTHENTICATION: f"应正确验证用户凭证",
            PathCategory.AUTHORIZATION: f"应正确检查用户权限",
            PathCategory.NOTIFICATION: f"应成功发送通知消息",
            PathCategory.AUDIT: f"应记录所有相关操作",
            PathCategory.UTILITY: f"应提供一致的辅助功能",
            PathCategory.UNKNOWN: f"应完成指定功能"
        }

        return behavior_map.get(category, f"应正确执行{function_name}")

    def _generate_enhanced_description(self, path, annotation: PathAnnotation) -> str:
        """生成增强描述

        Args:
            path: 路径对象
            annotation: 路径标注

        Returns:
            str: 增强描述
        """
        parts = [annotation.business_meaning]

        if annotation.semantic_tags:
            parts.append(f"标签: {', '.join(annotation.semantic_tags)}")

        if annotation.test_focus:
            parts.append(f"测试重点: {', '.join(annotation.test_focus[:2])}")

        if annotation.risk_level == "high":
            parts.append("[高风险]")

        return " | ".join(parts)

    def _generate_test_hints(self, annotation: PathAnnotation) -> List[str]:
        """生成测试提示

        Args:
            annotation: 路径标注

        Returns:
            List[str]: 测试提示列表
        """
        hints = []

        if annotation.category == PathCategory.VALIDATION:
            hints.append("测试合法输入")
            hints.append("测试边界值")
            hints.append("测试非法输入")
        elif annotation.category == PathCategory.ERROR_HANDLING:
            hints.append("触发各种错误条件")
            hints.append("测试错误恢复机制")
        elif annotation.category == PathCategory.AUTHENTICATION:
            hints.append("测试有效凭证")
            hints.append("测试无效凭证")
            hints.append("测试会话过期")
        elif annotation.category == PathCategory.TRANSACTION:
            hints.append("测试正常提交")
            hints.append("测试回滚场景")

        for focus in annotation.test_focus[:2]:
            if focus not in hints:
                hints.append(focus)

        return hints

    def _suggest_test_inputs(self, annotation: PathAnnotation) -> Dict[str, Any]:
        """建议测试输入

        Args:
            annotation: 路径标注

        Returns:
            Dict[str, Any]: 建议的输入字典
        """
        inputs = {}

        if annotation.category == PathCategory.VALIDATION:
            inputs['valid'] = "有效的测试数据"
            inputs['boundary'] = "边界值数据"
            inputs['invalid'] = "无效的测试数据"
        elif annotation.category == PathCategory.QUERY_OPERATION:
            inputs['empty_result'] = "空结果查询"
            inputs['single_result'] = "单条结果查询"
            inputs['multiple_results'] = "多条结果查询"
        elif annotation.category == PathCategory.AUTHENTICATION:
            inputs['valid_creds'] = {"username": "valid_user", "password": "valid_pass"}
            inputs['invalid_creds'] = {"username": "invalid_user", "password": "wrong_pass"}

        return inputs

    def _find_related_paths(self, path_id: str) -> List[str]:
        """查找相关路径

        Args:
            path_id: 路径标识符

        Returns:
            List[str]: 相关路径列表
        """
        related = []

        for other_path in self.annotated_paths:
            if other_path.path_id != path_id:
                if other_path.annotation.category == self._get_path_annotation(path_id).category:
                    related.append(other_path.path_id)

        return related[:5]

    def _get_path_annotation(self, path_id: str) -> Optional[PathAnnotation]:
        """获取路径标注

        Args:
            path_id: 路径标识符

        Returns:
            Optional[PathAnnotation]: 路径标注
        """
        for ap in self.annotated_paths:
            if ap.path_id == path_id:
                return ap.annotation
        return None

    def _calculate_annotation_confidence(self, annotation: PathAnnotation) -> float:
        """计算标注置信度

        Args:
            annotation: 路径标注

        Returns:
            float: 置信度评分（0-1）
        """
        confidence = 0.3

        if annotation.category != PathCategory.UNKNOWN:
            confidence += 0.3

        if annotation.semantic_tags:
            confidence += min(0.2, len(annotation.semantic_tags) * 0.05)

        if annotation.annotations:
            confidence += min(0.2, len(annotation.annotations) * 0.05)

        if annotation.business_meaning:
            confidence += 0.2

        return min(1.0, confidence)

    def _create_annotation_result(self) -> AnnotationResult:
        """创建标注结果

        Returns:
            AnnotationResult: 标注结果汇总
        """
        result = AnnotationResult(
            total_paths=len(self.paths),
            annotated_paths=len(self.annotated_paths),
            annotated_paths_list=self.annotated_paths
        )

        category_dist = defaultdict(int)
        complexity_dist = defaultdict(int)

        for ap in self.annotated_paths:
            category_dist[ap.annotation.category.name] += 1
            complexity_dist[ap.annotation.complexity.name] += 1

        result.category_distribution = dict(category_dist)
        result.complexity_distribution = dict(complexity_dist)

        high_priority = [ap.path_id for ap in self.annotated_paths
                        if ap.annotation.coverage_importance >= 0.7]
        result.high_priority_paths = high_priority

        result.metadata = {
            'annotation_rate': result.get_annotation_rate(),
            'avg_confidence': sum(ap.confidence for ap in self.annotated_paths) / len(self.annotated_paths) if self.annotated_paths else 0,
            'high_priority_count': len(high_priority)
        }

        return result

    def _get_statistics(self) -> Dict[str, Any]:
        """获取统计信息

        Returns:
            Dict[str, Any]: 统计信息
        """
        if not self.annotation_result:
            return {}

        return {
            'total_paths': self.annotation_result.total_paths,
            'annotated_paths': self.annotation_result.annotated_paths,
            'annotation_rate': self.annotation_result.get_annotation_rate(),
            'category_distribution': self.annotation_result.category_distribution,
            'complexity_distribution': self.annotation_result.complexity_distribution,
            'high_priority_paths': len(self.annotation_result.high_priority_paths),
            'avg_confidence': self.annotation_result.metadata.get('avg_confidence', 0)
        }

    def get_paths_by_category(self, category: PathCategory) -> List[AnnotatedPath]:
        """按类别获取路径

        Args:
            category: 路径类别

        Returns:
            List[AnnotatedPath]: 该类别的路径列表
        """
        return [ap for ap in self.annotated_paths if ap.annotation.category == category]

    def get_high_priority_paths(self, threshold: float = 0.7) -> List[AnnotatedPath]:
        """获取高优先级路径

        Args:
            threshold: 优先级阈值

        Returns:
            List[AnnotatedPath]: 高优先级路径列表
        """
        return [ap for ap in self.annotated_paths
                if ap.annotation.coverage_importance >= threshold]

    def get_paths_by_risk(self, risk_level: str) -> List[AnnotatedPath]:
        """按风险等级获取路径

        Args:
            risk_level: 风险等级

        Returns:
            List[AnnotatedPath]: 该风险等级的路径列表
        """
        return [ap for ap in self.annotated_paths
                if ap.annotation.risk_level == risk_level]

    def export_annotated_paths(self) -> List[Dict[str, Any]]:
        """导出带标注的路径

        Returns:
            List[Dict[str, Any]]: 导出数据
        """
        return [ap.to_dict() for ap in self.annotated_paths]

    def suggest_test_sequence(self) -> List[str]:
        """建议测试执行顺序

        Returns:
            List[str]: 建议的测试路径顺序
        """
        sequence = []

        high_risk = self.get_paths_by_risk('high')
        high_risk.sort(key=lambda x: x.annotation.coverage_importance, reverse=True)
        sequence.extend([ap.path_id for ap in high_risk])

        medium_risk = self.get_paths_by_risk('medium')
        medium_risk.sort(key=lambda x: x.annotation.complexity.value)
        sequence.extend([ap.path_id for ap in medium_risk if ap.path_id not in sequence])

        low_risk = self.get_paths_by_risk('low')
        sequence.extend([ap.path_id for ap in low_risk if ap.path_id not in sequence])

        return sequence
