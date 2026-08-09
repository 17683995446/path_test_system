"""
Layer 36: Quality Evaluation Layer (测试用例质量评估层) 【V3.1升级】

该层负责对生成的测试用例进行全面的质量评估，包括可读性、可维护性、
有效性、覆盖率等多个维度。提供智能的质量评分和改进建议。

V3.1升级特性：
- 多维度质量评估体系
- 智能缺陷检测能力增强
- 语义质量分析
- 覆盖率优化建议
- 自动化质量分级
"""

from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import re


class QualityDimension(Enum):
    """质量维度"""
    READABILITY = "readability"
    MAINTAINABILITY = "maintainability"
    EFFECTIVENESS = "effectiveness"
    COVERAGE = "coverage"
    RELIABILITY = "reliability"
    COMPLETENESS = "completeness"


class QualityLevel(Enum):
    """质量等级"""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    NEEDS_IMPROVEMENT = "needs_improvement"
    POOR = "poor"


@dataclass
class QualityMetric:
    """质量指标"""
    dimension: QualityDimension
    metric_name: str
    score: float
    max_score: float = 100.0
    weight: float = 1.0
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityIssue:
    """质量问题"""
    issue_id: str
    severity: str
    dimension: QualityDimension
    description: str
    location: Optional[str] = None
    suggestion: str = ""
    auto_fixable: bool = False
    estimated_effort: str = "low"


@dataclass
class QualityEvaluationResult:
    """质量评估结果"""
    overall_score: float = 0.0
    quality_level: QualityLevel = QualityLevel.ACCEPTABLE
    dimensions: Dict[QualityDimension, float] = field(default_factory=dict)
    metrics: List[QualityMetric] = field(default_factory=list)
    issues: List[QualityIssue] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    total_cases: int = 0
    passed_cases: int = 0
    failed_cases: int = 0
    evaluation_time_ms: float = 0.0


@dataclass
class TestCaseQualityProfile:
    """测试用例质量画像"""
    case_id: str
    case_name: str
    overall_score: float
    dimension_scores: Dict[QualityDimension, float]
    issues: List[QualityIssue]
    improvement_potential: float


class QualityEvaluateLayer:
    """
    测试用例质量评估层 【V3.1升级】

    负责对生成的测试用例进行全面的质量评估，提供详细的
    质量分析报告和改进建议。

    核心功能：
    - 多维度质量评估：可读性、可维护性、有效性、覆盖率、可靠性、完整性
    - 智能缺陷检测：识别测试用例中的潜在问题
    - 语义质量分析：理解测试用例的语义质量
    - 覆盖率分析：评估测试用例的代码覆盖能力
    - 自动化分级：基于评分自动确定质量等级
    - 改进建议：提供针对性的优化建议

    V3.1升级特性：
    - 增强的质量评估算法
    - 更智能的缺陷检测
    - 语义理解能力提升
    - 实时质量监控
    - 历史趋势分析支持

    Attributes:
        description: 层的功能描述
        input_type: 输入数据类型 (PipelineContext)
        output_type: 输出数据类型 (QualityEvaluationResult)

    Input Context Fields:
        - rendered_test_cases: 渲染后的测试用例列表
        - template_render_result: 模板渲染结果
        - test_cases: 原始测试用例数据
        - source_analysis_result: 源代码分析结果
        - quality_thresholds: 质量阈值配置

    Output:
        QualityEvaluationResult: 质量评估结果
    """

    description: str = "测试用例质量评估层 - 多维度评估测试用例质量 【V3.1升级】"
    input_type: str = "PipelineContext"
    output_type: str = "QualityEvaluationResult"

    QUALITY_WEIGHTS: Dict[QualityDimension, float] = {
        QualityDimension.READABILITY: 0.15,
        QualityDimension.MAINTAINABILITY: 0.15,
        QualityDimension.EFFECTIVENESS: 0.25,
        QualityDimension.COVERAGE: 0.25,
        QualityDimension.RELIABILITY: 0.10,
        QualityDimension.COMPLETENESS: 0.10,
    }

    SCORE_THRESHOLDS: Dict[QualityLevel, Tuple[float, float]] = {
        QualityLevel.EXCELLENT: (90, 100),
        QualityLevel.GOOD: (75, 90),
        QualityLevel.ACCEPTABLE: (60, 75),
        QualityLevel.NEEDS_IMPROVEMENT: (40, 60),
        QualityLevel.POOR: (0, 40),
    }

    def __init__(self, quality_config: Optional[Dict[str, Any]] = None):
        """
        初始化质量评估层

        Args:
            quality_config: 质量评估配置字典，包含：
                - custom_weights: 自定义维度权重
                - thresholds: 自定义阈值
                - enable_specific_checks: 启用的检查项
        """
        self.quality_config = quality_config or {}
        self.weights = {**self.QUALITY_WEIGHTS}
        if 'custom_weights' in self.quality_config:
            self.weights.update(self.quality_config['custom_weights'])

    def process(self, context: Any) -> QualityEvaluationResult:
        """
        执行测试用例质量评估

        Args:
            context: PipelineContext对象，包含以下预期字段：
                - rendered_test_cases: 渲染后的测试用例列表
                - template_render_result: 模板渲染结果
                - test_cases: 原始测试用例数据
                - source_analysis_result: 源代码分析结果
                - test_data_result: 测试数据结果
                - quality_thresholds: 质量阈值配置 (可选)
                - evaluation_options: 评估选项 (可选)
                    - strict_mode: 严格模式
                    - include_suggestions: 包含改进建议
                    - min_quality_score: 最低质量分数

        Returns:
            QualityEvaluationResult: 质量评估结果，包含：
                - overall_score: 总体质量分数 (0-100)
                - quality_level: 质量等级
                - dimensions: 各维度评分
                - metrics: 详细质量指标列表
                - issues: 发现的问题列表
                - recommendations: 改进建议
                - strengths: 优势分析
                - total_cases: 评估的用例总数
                - passed_cases: 通过评估的用例数
                - failed_cases: 未通过评估的用例数
                - evaluation_time_ms: 评估耗时

        Process Flow:
            1. 收集待评估的测试用例
            2. 进行多维度质量评估
            3. 检测质量问题和缺陷
            4. 计算综合质量分数
            5. 确定质量等级
            6. 生成改进建议和优势分析
            7. 返回评估结果

        Example:
            >>> layer = QualityEvaluateLayer()
            >>> ctx = create_context()
            >>> ctx.set('rendered_test_cases', rendered_cases)
            >>> result = layer.process(ctx)
            >>> print(f"质量等级: {result.quality_level.value}")
            >>> print(f"总体分数: {result.overall_score}")
        """
        import time
        start_time = time.time()

        rendered_cases = context.get('rendered_test_cases', [])
        template_result = context.get('template_render_result')
        source_analysis = context.get('source_analysis_result', {})
        quality_thresholds = context.get('quality_thresholds', {})

        result = QualityEvaluationResult()
        result.total_cases = len(rendered_cases)

        if not rendered_cases and template_result:
            rendered_cases = template_result.rendered_cases

        all_metrics = []
        all_issues = []

        for case in rendered_cases:
            case_metrics, case_issues = self._evaluate_single_case(case, source_analysis)
            all_metrics.extend(case_metrics)
            all_issues.extend(case_issues)

            if self._is_case_acceptable(case_metrics, quality_thresholds):
                result.passed_cases += 1
            else:
                result.failed_cases += 1

        result.metrics = all_metrics

        dimension_scores = self._calculate_dimension_scores(all_metrics)
        result.dimensions = dimension_scores

        result.overall_score = self._calculate_overall_score(dimension_scores)

        result.quality_level = self._determine_quality_level(result.overall_score)

        result.issues = all_issues

        result.recommendations = self._generate_recommendations(
            dimension_scores, all_issues, rendered_cases
        )

        result.strengths = self._identify_strengths(dimension_scores, all_issues)

        result.evaluation_time_ms = (time.time() - start_time) * 1000

        context.set('quality_evaluation_result', result)
        context.set('quality_score', result.overall_score)
        context.set('quality_issues', [self._issue_to_dict(i) for i in result.issues])

        return result

    def _evaluate_single_case(
        self, test_case: Any,
        source_analysis: Dict[str, Any]
    ) -> Tuple[List[QualityMetric], List[QualityIssue]]:
        """评估单个测试用例"""
        metrics = []
        issues = []

        readability_score, readability_issues = self._evaluate_readability(test_case)
        metrics.append(QualityMetric(
            dimension=QualityDimension.READABILITY,
            metric_name='code_readability',
            score=readability_score,
            details={'issues': len(readability_issues)}
        ))
        issues.extend(readability_issues)

        maintainability_score, maintainability_issues = self._evaluate_maintainability(test_case)
        metrics.append(QualityMetric(
            dimension=QualityDimension.MAINTAINABILITY,
            metric_name='code_maintainability',
            score=maintainability_score,
            details={'issues': len(maintainability_issues)}
        ))
        issues.extend(maintainability_issues)

        effectiveness_score, effectiveness_issues = self._evaluate_effectiveness(test_case)
        metrics.append(QualityMetric(
            dimension=QualityDimension.EFFECTIVENESS,
            metric_name='test_effectiveness',
            score=effectiveness_score,
            details={'issues': len(effectiveness_issues)}
        ))
        issues.extend(effectiveness_issues)

        coverage_score = self._evaluate_coverage(test_case, source_analysis)
        metrics.append(QualityMetric(
            dimension=QualityDimension.COVERAGE,
            metric_name='code_coverage',
            score=coverage_score
        ))

        reliability_score, reliability_issues = self._evaluate_reliability(test_case)
        metrics.append(QualityMetric(
            dimension=QualityDimension.RELIABILITY,
            metric_name='test_reliability',
            score=reliability_score,
            details={'issues': len(reliability_issues)}
        ))
        issues.extend(reliability_issues)

        completeness_score, completeness_issues = self._evaluate_completeness(test_case)
        metrics.append(QualityMetric(
            dimension=QualityDimension.COMPLETENESS,
            metric_name='test_completeness',
            score=completeness_score,
            details={'issues': len(completeness_issues)}
        ))
        issues.extend(completeness_issues)

        return metrics, issues

    def _evaluate_readability(
        self, test_case: Any
    ) -> Tuple[float, List[QualityIssue]]:
        """评估可读性"""
        score = 100.0
        issues = []

        code = self._get_test_code(test_case)
        lines = code.split('\n')

        if len(lines) > 100:
            score -= 10
            issues.append(QualityIssue(
                issue_id='readability_long_method',
                severity='minor',
                dimension=QualityDimension.READABILITY,
                description=f'测试方法过长 ({len(lines)} 行)',
                suggestion='考虑将测试方法拆分为更小的部分',
                auto_fixable=False,
                estimated_effort='medium'
            ))

        avg_line_length = sum(len(line) for line in lines) / len(lines) if lines else 0
        if avg_line_length > 80:
            score -= 5
            issues.append(QualityIssue(
                issue_id='readability_long_lines',
                severity='minor',
                dimension=QualityDimension.READABILITY,
                description=f'平均行长度过长 ({avg_line_length:.1f} 字符)',
                suggestion='缩短代码行长度，提高可读性',
                auto_fixable=False,
                estimated_effort='low'
            ))

        if not any('"""' in code or "'''" in code for code in lines):
            if not re.search(r'#.*[A-Z]', code):
                score -= 5

        return max(score, 0), issues

    def _evaluate_maintainability(
        self, test_case: Any
    ) -> Tuple[float, List[QualityIssue]]:
        """评估可维护性"""
        score = 100.0
        issues = []

        code = self._get_test_code(test_case)

        if code.count('assert') == 0:
            score -= 20
            issues.append(QualityIssue(
                issue_id='maintainability_no_assertions',
                severity='critical',
                dimension=QualityDimension.MAINTAINABILITY,
                description='测试用例没有断言语句',
                suggestion='添加适当的断言来验证预期行为',
                auto_fixable=False,
                estimated_effort='low'
            ))

        hardcoded_values = len(re.findall(r'[0-9]{5,}', code))
        if hardcoded_values > 5:
            score -= 10
            issues.append(QualityIssue(
                issue_id='maintainability_hardcoded_values',
                severity='major',
                dimension=QualityDimension.MAINTAINABILITY,
                description=f'存在 {hardcoded_values} 个硬编码值',
                suggestion='使用常量或配置替代硬编码值',
                auto_fixable=False,
                estimated_effort='medium'
            ))

        nested_depth = self._calculate_nesting_depth(code)
        if nested_depth > 4:
            score -= 10
            issues.append(QualityIssue(
                issue_id='maintainability_deep_nesting',
                severity='major',
                dimension=QualityDimension.MAINTAINABILITY,
                description=f'嵌套深度过深 ({nested_depth})',
                suggestion='重构代码以减少嵌套层次',
                auto_fixable=False,
                estimated_effort='medium'
            ))

        return max(score, 0), issues

    def _evaluate_effectiveness(
        self, test_case: Any
    ) -> Tuple[float, List[QualityIssue]]:
        """评估有效性"""
        score = 80.0
        issues = []

        case_data = test_case if isinstance(test_case, dict) else {}
        code = self._get_test_code(test_case)

        if case_data.get('expected_output') is None and 'assert' not in code.lower():
            score -= 15
            issues.append(QualityIssue(
                issue_id='effectiveness_no_verification',
                severity='critical',
                dimension=QualityDimension.EFFECTIVENESS,
                description='测试用例缺少结果验证',
                suggestion='添加断言或验证逻辑',
                auto_fixable=False,
                estimated_effort='low'
            ))

        if 'pass' in code.split('\n')[-1] and 'assert' not in code:
            score -= 10
            issues.append(QualityIssue(
                issue_id='effectiveness_empty_test',
                severity='major',
                dimension=QualityDimension.EFFECTIVENESS,
                description='测试方法为空或仅包含pass',
                suggestion='实现实际的测试逻辑',
                auto_fixable=True,
                estimated_effort='medium'
            ))

        unique_inputs = len(case_data.get('input_data', {}))
        if unique_inputs == 0:
            score -= 5

        return max(score, 0), issues

    def _evaluate_coverage(
        self, test_case: Any,
        source_analysis: Dict[str, Any]
    ) -> float:
        """评估覆盖率"""
        score = 70.0

        functions = source_analysis.get('functions', [])
        if not functions:
            return score

        code = self._get_test_code(test_case)

        function_names = [f.get('name') for f in functions]
        covered_functions = sum(1 for name in function_names if name in code)

        if covered_functions > 0:
            coverage_ratio = covered_functions / len(functions)
            score = 70 + (coverage_ratio * 30)

        return min(score, 100)

    def _evaluate_reliability(
        self, test_case: Any
    ) -> Tuple[float, List[QualityIssue]]:
        """评估可靠性"""
        score = 100.0
        issues = []

        code = self._get_test_code(test_case)

        flaky_patterns = [
            (r'time\.sleep', '使用time.sleep可能导致测试不稳定'),
            (r'random\.', '使用随机值可能导致测试结果不确定'),
            (r'\.now\(\)', '使用当前时间可能导致时区问题'),
        ]

        for pattern, message in flaky_patterns:
            if re.search(pattern, code):
                score -= 10
                issues.append(QualityIssue(
                    issue_id='reliability_flaky_pattern',
                    severity='major',
                    dimension=QualityDimension.RELIABILITY,
                    description=message,
                    suggestion='避免可能导致测试不稳定的设计',
                    auto_fixable=False,
                    estimated_effort='medium'
                ))

        return max(score, 0), issues

    def _evaluate_completeness(
        self, test_case: Any
    ) -> Tuple[float, List[QualityIssue]]:
        """评估完整性"""
        score = 70.0
        issues = []

        code = self._get_test_code(test_case)
        case_data = test_case if isinstance(test_case, dict) else {}

        required_elements = {
            'docstring': '"""' in code or "'''" in code or '# ' in code,
            'setup': 'def setUp' in code or 'setup' in code.lower(),
            'teardown': 'def tearDown' in code or 'teardown' in code.lower(),
            'assertion': 'assert' in code,
        }

        missing = [k for k, v in required_elements.items() if not v]
        score -= len(missing) * 8

        if missing:
            issues.append(QualityIssue(
                issue_id='completeness_missing_elements',
                severity='minor',
                dimension=QualityDimension.COMPLETENESS,
                description=f'缺少必要元素: {", ".join(missing)}',
                suggestion=f'添加以下元素: {", ".join(missing)}',
                auto_fixable=True,
                estimated_effort='low'
            ))

        edge_cases = case_data.get('edge_cases', [])
        if len(edge_cases) < 3:
            score -= 5

        return max(score, 0), issues

    def _get_test_code(self, test_case: Any) -> str:
        """获取测试代码"""
        if hasattr(test_case, 'test_code'):
            return test_case.test_code
        elif isinstance(test_case, dict):
            return test_case.get('test_code', '')
        return str(test_case)

    def _calculate_nesting_depth(self, code: str) -> int:
        """计算嵌套深度"""
        max_depth = 0
        current_depth = 0

        for char in code:
            if char in '({[':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char in ')}]':
                current_depth = max(0, current_depth - 1)

        return max_depth

    def _calculate_dimension_scores(
        self, metrics: List[QualityMetric]
    ) -> Dict[QualityDimension, float]:
        """计算各维度评分"""
        dimension_scores = {}

        for dimension in QualityDimension:
            dim_metrics = [m for m in metrics if m.dimension == dimension]
            if dim_metrics:
                avg_score = sum(m.score for m in dim_metrics) / len(dim_metrics)
                dimension_scores[dimension] = round(avg_score, 2)
            else:
                dimension_scores[dimension] = 0.0

        return dimension_scores

    def _calculate_overall_score(
        self, dimension_scores: Dict[QualityDimension, float]
    ) -> float:
        """计算总体质量分数"""
        weighted_score = 0.0
        total_weight = 0.0

        for dimension, score in dimension_scores.items():
            weight = self.weights.get(dimension, 1.0)
            weighted_score += score * weight
            total_weight += weight

        if total_weight == 0:
            return 0.0

        overall_score = weighted_score / total_weight
        return round(overall_score, 2)

    def _determine_quality_level(self, score: float) -> QualityLevel:
        """确定质量等级"""
        for level, (min_score, max_score) in self.SCORE_THRESHOLDS.items():
            if min_score <= score <= max_score:
                return level
        return QualityLevel.POOR

    def _is_case_acceptable(
        self, metrics: List[QualityMetric],
        thresholds: Dict[str, float]
    ) -> bool:
        """判断用例是否可接受"""
        min_score = thresholds.get('min_quality_score', 60.0)

        if not metrics:
            return False

        avg_score = sum(m.score for m in metrics) / len(metrics)
        return avg_score >= min_score

    def _generate_recommendations(
        self, dimension_scores: Dict[QualityDimension, float],
        issues: List[QualityIssue],
        cases: List[Any]
    ) -> List[str]:
        """生成改进建议"""
        recommendations = []

        critical_issues = [i for i in issues if i.severity == 'critical']
        if critical_issues:
            recommendations.append(
                f'立即修复 {len(critical_issues)} 个严重质量问题'
            )

        low_dimensions = [
            dim for dim, score in dimension_scores.items()
            if score < 60
        ]
        for dim in low_dimensions:
            recommendations.append(f'重点改进 {dim.value} 维度，当前分数: {dimension_scores[dim]}')

        if not any(d == QualityDimension.COVERAGE for d in dimension_scores):
            recommendations.append('增加测试覆盖率，添加更多边界和异常场景测试')

        duplicate_issues = self._find_duplicate_patterns(issues)
        if duplicate_issues:
            recommendations.append(
                f'发现 {len(duplicate_issues)} 个可系统性修复的问题模式'
            )

        return recommendations

    def _identify_strengths(
        self, dimension_scores: Dict[QualityDimension, float],
        issues: List[QualityIssue]
    ) -> List[str]:
        """识别优势"""
        strengths = []

        high_dimensions = [
            dim for dim, score in dimension_scores.items()
            if score >= 85
        ]
        for dim in high_dimensions:
            strengths.append(f'{dim.value} 维度表现优秀 ({dimension_scores[dim]})')

        if not any(i.severity == 'critical' for i in issues):
            strengths.append('无严重质量问题')

        return strengths

    def _find_duplicate_patterns(
        self, issues: List[QualityIssue]
    ) -> Dict[str, int]:
        """查找重复的问题模式"""
        patterns = {}

        for issue in issues:
            if issue.auto_fixable:
                pattern = issue.issue_id.split('_')[0]
                patterns[pattern] = patterns.get(pattern, 0) + 1

        return {k: v for k, v in patterns.items() if v > 1}

    def _issue_to_dict(self, issue: QualityIssue) -> Dict[str, Any]:
        """将问题转换为字典"""
        return {
            'id': issue.issue_id,
            'severity': issue.severity,
            'dimension': issue.dimension.value,
            'description': issue.description,
            'suggestion': issue.suggestion,
            'auto_fixable': issue.auto_fixable
        }
