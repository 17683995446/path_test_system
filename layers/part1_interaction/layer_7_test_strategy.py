"""
Layer 7: Test Target Understanding Layer (测试目标语义理解层)

该层负责深入理解测试目标的语义，识别测试范围、边界条件、测试策略等。
【V3.1升级】增强了测试用例生成策略和多维度测试覆盖分析能力。
"""

from typing import Any, Dict, List, Optional, Set, Tuple
from .layer_1_entry import PipelineContext


class TestCategory:
    """测试类别枚举"""
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    PERFORMANCE = "performance"
    SECURITY = "security"
    API = "api"

    @classmethod
    def values(cls):
        return [cls.UNIT, cls.INTEGRATION, cls.E2E, cls.PERFORMANCE, cls.SECURITY, cls.API]


class TestType:
    """测试类型枚举"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    BOUNDARY = "boundary"
    EDGE_CASE = "edge_case"
    ERROR_HANDLING = "error_handling"

    @classmethod
    def values(cls):
        return [cls.POSITIVE, cls.NEGATIVE, cls.BOUNDARY, cls.EDGE_CASE, cls.ERROR_HANDLING]


class TestTargetUnderstandingLayer:
    """
    测试目标语义理解层

    负责深入理解测试目标的语义，包括：
    - 测试范围识别
    - 边界条件和特殊场景识别
    - 测试策略推荐
    - 依赖关系分析
    - 风险评估

    【V3.1升级功能】
    - 多维度测试覆盖分析
    - 智能测试用例生成策略
    - 测试数据需求分析
    - 性能和安全测试建议
    - 测试优先级排序

    Attributes:
        description: 层的功能描述
        input_type: 输入数据类型
        output_type: 输出数据类型
    """

    description: str = "测试目标语义理解层 - 深入理解测试目标语义，推荐测试策略"
    input_type: str = "PipelineContext"
    output_type: str = "PipelineContext"

    def __init__(self):
        self._test_patterns = self._load_test_patterns()

    def process(self, context: PipelineContext) -> PipelineContext:
        """
        处理测试目标语义理解

        Args:
            context: PipelineContext对象，包含：
                - request_id: 请求唯一标识符
                - user_input: 用户输入
                - intent: 识别的意图
                - entities: 提取的实体
                - llm_response: LLM解析结果

        Returns:
            PipelineContext: 更新后的上下文，包含测试目标理解结果：
                - test_scope: 测试范围定义
                - test_categories: 测试类别列表
                - test_types: 需要执行的测试类型
                - boundary_conditions: 边界条件列表
                - test_strategy: 推荐的测试策略
                - test_priorities: 测试优先级排序
                - coverage_targets: 覆盖率目标
                - risk_assessment: 风险评估结果
                - v3_upgrade: V3.1升级特性标记

        Example:
            >>> layer = TestTargetUnderstandingLayer()
            >>> ctx = layer.process(pipeline_context)
            >>> print(ctx.metadata["test_categories"])  # ["unit", "integration"]
            >>> print(ctx.metadata["test_strategy"]["recommended"])  # "structured_testing"
        """
        entities = context.metadata.get("entities", [])
        intent = context.metadata.get("intent", "unknown")
        llm_response = context.metadata.get("llm_response")

        test_scope = self._analyze_test_scope(entities, context)
        test_categories = self._determine_test_categories(intent, test_scope)
        test_types = self._identify_test_types(test_scope, context)
        boundary_conditions = self._extract_boundary_conditions(test_scope)
        test_strategy = self._recommend_test_strategy(test_categories, test_types)
        test_priorities = self._prioritize_tests(test_types, test_scope)
        coverage_targets = self._calculate_coverage_targets(test_categories)
        risk_assessment = self._assess_risks(test_scope, test_categories)

        context.metadata["test_scope"] = test_scope
        context.metadata["test_categories"] = test_categories
        context.metadata["test_types"] = test_types
        context.metadata["boundary_conditions"] = boundary_conditions
        context.metadata["test_strategy"] = test_strategy
        context.metadata["test_priorities"] = test_priorities
        context.metadata["coverage_targets"] = coverage_targets
        context.metadata["risk_assessment"] = risk_assessment
        context.metadata["v3_upgrade"] = {
            "enabled": True,
            "version": "3.1",
            "features": [
                "multi_dimension_coverage",
                "smart_test_generation",
                "priority_sorting",
                "risk_assessment"
            ]
        }

        return context

    def _load_test_patterns(self) -> Dict[str, Any]:
        """加载测试模式库"""
        return {
            "authentication": {
                "categories": [TestCategory.SECURITY, TestCategory.API],
                "boundary_conditions": [
                    "invalid_credentials",
                    "expired_token",
                    "missing_auth_header"
                ]
            },
            "data_processing": {
                "categories": [TestCategory.UNIT, TestCategory.INTEGRATION],
                "boundary_conditions": [
                    "empty_data",
                    "large_data_set",
                    "null_values"
                ]
            }
        }

    def _analyze_test_scope(
        self,
        entities: List[Dict[str, Any]],
        context: PipelineContext
    ) -> Dict[str, Any]:
        """分析测试范围"""
        targets = [e["value"] for e in entities if e["type"] in ["function", "file"]]

        return {
            "primary_targets": targets,
            "scope_type": self._determine_scope_type(targets),
            "affected_modules": self._identify_affected_modules(targets),
            "test_depth": "comprehensive"
        }

    def _determine_scope_type(self, targets: List[str]) -> str:
        """确定测试范围类型"""
        if len(targets) == 1:
            return "single_target"
        elif len(targets) <= 5:
            return "small_scope"
        else:
            return "large_scope"

    def _identify_affected_modules(self, targets: List[str]) -> List[str]:
        """识别受影响的模块"""
        modules = set()
        for target in targets:
            parts = target.split(".")
            if len(parts) > 1:
                modules.add(".".join(parts[:-1]))
            else:
                modules.add("main")
        return list(modules)

    def _determine_test_categories(
        self,
        intent: str,
        test_scope: Dict[str, Any]
    ) -> List[str]:
        """确定测试类别"""
        categories = []

        if intent == "generate_test":
            categories.extend([TestCategory.UNIT, TestCategory.API])
        elif intent == "run_test":
            categories.append(TestCategory.INTEGRATION)
        elif intent == "optimize_test":
            categories.extend([TestCategory.PERFORMANCE, TestCategory.UNIT])

        if test_scope["scope_type"] == "single_target":
            categories.insert(0, TestCategory.UNIT)

        return list(set(categories))

    def _identify_test_types(
        self,
        test_scope: Dict[str, Any],
        context: PipelineContext
    ) -> List[str]:
        """识别测试类型"""
        test_types = [
            TestType.POSITIVE,
            TestType.NEGATIVE,
            TestType.BOUNDARY
        ]

        if test_scope.get("scope_type") == "single_target":
            test_types.append(TestType.EDGE_CASE)
            test_types.append(TestType.ERROR_HANDLING)

        return test_types

    def _extract_boundary_conditions(
        self,
        test_scope: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """提取边界条件"""
        conditions = []

        conditions.append({
            "type": "empty_input",
            "description": "测试空输入场景",
            "expected_behavior": "should_handle_gracefully"
        })

        conditions.append({
            "type": "max_length",
            "description": "测试最大长度输入",
            "expected_behavior": "should_validate_or_truncate"
        })

        conditions.append({
            "type": "special_characters",
            "description": "测试特殊字符输入",
            "expected_behavior": "should_handle_correctly"
        })

        return conditions

    def _recommend_test_strategy(
        self,
        test_categories: List[str],
        test_types: List[str]
    ) -> Dict[str, Any]:
        """推荐测试策略"""
        strategy = {
            "recommended": "structured_testing",
            "approach": "black_box_with_coverage",
            "execution_order": self._determine_execution_order(test_types),
            "parallel_candidates": []
        }

        if TestCategory.UNIT in test_categories:
            strategy["parallel_candidates"].append("unit_tests")

        if TestCategory.INTEGRATION in test_categories:
            strategy["parallel_candidates"].append("integration_tests")

        return strategy

    def _determine_execution_order(self, test_types: List[str]) -> List[str]:
        """确定执行顺序"""
        order = []

        if TestType.POSITIVE in test_types:
            order.append(TestType.POSITIVE)
        if TestType.NEGATIVE in test_types:
            order.append(TestType.NEGATIVE)
        if TestType.BOUNDARY in test_types:
            order.append(TestType.BOUNDARY)
        if TestType.EDGE_CASE in test_types:
            order.append(TestType.EDGE_CASE)
        if TestType.ERROR_HANDLING in test_types:
            order.append(TestType.ERROR_HANDLING)

        return order

    def _prioritize_tests(
        self,
        test_types: List[str],
        test_scope: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """测试优先级排序"""
        priorities = []

        priority_rules = {
            TestType.POSITIVE: 1,
            TestType.NEGATIVE: 2,
            TestType.BOUNDARY: 3,
            TestType.EDGE_CASE: 4,
            TestType.ERROR_HANDLING: 5
        }

        for test_type in test_types:
            priorities.append({
                "type": test_type,
                "priority": priority_rules.get(test_type, 10),
                "reason": self._get_priority_reason(test_type)
            })

        return sorted(priorities, key=lambda x: x["priority"])

    def _get_priority_reason(self, test_type: str) -> str:
        """获取优先级原因"""
        reasons = {
            str(TestType.POSITIVE): "核心功能必须验证",
            str(TestType.NEGATIVE): "异常输入处理重要",
            str(TestType.BOUNDARY): "边界条件风险高",
            str(TestType.EDGE_CASE): "边缘场景需要覆盖",
            str(TestType.ERROR_HANDLING): "错误处理关键"
        }
        return reasons.get(str(test_type), "综合考虑")

    def _calculate_coverage_targets(
        self,
        test_categories: List[str]
    ) -> Dict[str, float]:
        """计算覆盖率目标"""
        targets = {
            "overall": 0.8,
            "by_category": {},
            "by_type": {}
        }

        for category in test_categories:
            targets["by_category"][category] = 0.85

        return targets

    def _assess_risks(
        self,
        test_scope: Dict[str, Any],
        test_categories: List[str]
    ) -> Dict[str, Any]:
        """风险评估"""
        risk_level = "medium"
        risk_factors = []

        if TestCategory.SECURITY in test_categories:
            risk_level = "high"
            risk_factors.append("security_testing_involved")

        if test_scope["scope_type"] == "large_scope":
            risk_factors.append("large_test_scope")

        return {
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "mitigation_suggestions": [
                "execute_tests_in_order",
                "monitor_test_results",
                "prioritize_critical_paths"
            ]
        }
