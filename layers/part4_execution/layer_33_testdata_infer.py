"""
Layer 33: Test Data Inference Layer (测试数据推理层)

该层负责根据函数签名、类型注解和业务语义智能推断测试数据。
能够基于源代码分析自动生成符合类型约束和业务规则的测试用例输入数据。
"""

from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
import re


@dataclass
class TypeInfo:
    """类型信息"""
    type_name: str
    is_optional: bool = False
    is_collection: bool = False
    collection_inner_type: Optional[str] = None
    default_value: Any = None
    constraints: List[str] = field(default_factory=list)


@dataclass
class TestDataSpec:
    """测试数据规格"""
    param_name: str
    type_info: TypeInfo
    inferred_values: List[Any] = field(default_factory=list)
    boundary_values: List[Any] = field(default_factory=list)
    edge_cases: List[Any] = field(default_factory=list)
    generation_strategy: str = "auto"


@dataclass
class FunctionTestData:
    """函数测试数据"""
    function_name: str
    function_signature: str
    test_data_specs: List[TestDataSpec] = field(default_factory=list)
    return_type: Optional[str] = None
    expected_behaviors: List[str] = field(default_factory=list)


@dataclass
class InferredTestData:
    """推断的测试数据"""
    function_test_data_list: List[FunctionTestData] = field(default_factory=list)
    total_cases: int = 0
    inference_confidence: float = 0.0
    type_coverage: float = 0.0


class TestDataInferLayer:
    """
    测试数据推理层

    负责根据函数签名、类型注解和业务语义智能推断测试数据。
    能够自动分析源代码中的类型信息、默认值、约束条件，
    生成高质量的测试数据规格。

    核心功能：
    - 函数签名解析和类型推断
    - 基于类型约束的边界值分析
    - 业务规则和约束条件识别
    - 常见测试数据模式自动生成
    - 异常情况和边界条件覆盖

    Attributes:
        description: 层的功能描述
        input_type: 输入数据类型 (PipelineContext)
        output_type: 输出数据类型 (InferredTestData)

    Input Context Fields:
        - source_analysis_result: 源代码分析结果
        - semantic_summary: 语义摘要信息
        - function_signatures: 函数签名列表
        - type_hints: 类型注解信息
        - business_rules: 业务规则列表

    Output:
        InferredTestData: 包含推断的测试数据规格
    """

    description: str = "测试数据推理层 - 基于类型和语义推断测试数据"
    input_type: str = "PipelineContext"
    output_type: str = "InferredTestData"

    PRIMITIVE_TYPES: Set[str] = {
        'int', 'float', 'str', 'bool', 'bytes',
        'Integer', 'Float', 'String', 'Boolean',
        'long', 'double', 'char', 'byte'
    }

    COLLECTION_TYPES: Set[str] = {
        'list', 'dict', 'set', 'tuple', 'frozenset',
        'List', 'Dict', 'Set', 'Tuple', 'Array',
        'Collection', 'List[]', 'Map', 'HashMap'
    }

    BOUNDARY_VALUES_CONFIG: Dict[str, Tuple[Any, ...]] = {
        'int': (0, 1, -1, 127, 128, 255, 256, 32767, 32768, -32768, -32769, 2147483647, -2147483648),
        'float': (0.0, 1.0, -1.0, 0.1, -0.1, float('inf'), float('-inf'), float('nan')),
        'str': ('', 'a', 'A', '0', 'test', 'Test', 'TEST', '123', '!@#$%^&*()', ' ' * 100),
        'bool': (True, False),
    }

    def process(self, context: Any) -> InferredTestData:
        """
        执行测试数据推理

        Args:
            context: PipelineContext对象，包含以下预期字段：
                - source_analysis_result: 源代码分析结果
                - semantic_summary: 语义摘要信息
                - function_signatures: 函数签名列表
                - type_hints: 类型注解信息
                - business_rules: 业务规则列表

        Returns:
            InferredTestData: 推断的测试数据，包含：
                - function_test_data_list: 每个函数的测试数据列表
                - total_cases: 总测试用例数
                - inference_confidence: 推理置信度
                - type_coverage: 类型覆盖率

        Process Flow:
            1. 解析函数签名和类型注解
            2. 识别参数类型和约束条件
            3. 生成边界值测试数据
            4. 生成特殊值和异常测试数据
            5. 生成业务规则约束的测试数据
            6. 计算覆盖率指标

        Example:
            >>> layer = TestDataInferLayer()
            >>> ctx = create_context()
            >>> ctx.set('function_signatures', [{'name': 'add', 'params': [{'name': 'a', 'type': 'int'}, {'name': 'b', 'type': 'int'}]}])
            >>> result = layer.process(ctx)
            >>> print(f"生成测试用例数: {result.total_cases}")
        """
        function_signatures = context.get('function_signatures', [])
        type_hints = context.get('type_hints', {})
        business_rules = context.get('business_rules', [])

        result = InferredTestData()
        result.function_test_data_list = []

        for sig in function_signatures:
            func_test_data = self._infer_function_test_data(
                sig, type_hints, business_rules
            )
            result.function_test_data_list.append(func_test_data)

        result.total_cases = sum(
            len(ftd.test_data_specs) * 5
            for ftd in result.function_test_data_list
        )

        result.inference_confidence = self._calculate_inference_confidence(
            result.function_test_data_list
        )

        result.type_coverage = self._calculate_type_coverage(
            result.function_test_data_list
        )

        context.set('inferred_test_data', result)
        context.set('test_data_cases', result.total_cases)
        context.set('type_coverage', result.type_coverage)

        return result

    def _infer_function_test_data(
        self, signature: Dict[str, Any],
        type_hints: Dict[str, Any],
        business_rules: List[str]
    ) -> FunctionTestData:
        """推理单个函数的测试数据"""
        func_name = signature.get('name', 'unknown')
        params = signature.get('params', [])

        func_test_data = FunctionTestData(
            function_name=func_name,
            function_signature=self._build_signature_string(signature)
        )

        for param in params:
            param_name = param.get('name', 'unknown')
            param_type = param.get('type', 'Any')

            type_info = self._infer_type_info(param_type, type_hints)

            test_data_spec = TestDataSpec(
                param_name=param_name,
                type_info=type_info,
                inferred_values=self._generate_inferred_values(type_info),
                boundary_values=self._generate_boundary_values(type_info),
                edge_cases=self._generate_edge_cases(type_info, business_rules),
                generation_strategy='auto'
            )

            func_test_data.test_data_specs.append(test_data_spec)

        func_test_data.return_type = signature.get('return_type', 'Any')
        func_test_data.expected_behaviors = self._infer_expected_behaviors(
            func_name, signature, business_rules
        )

        return func_test_data

    def _infer_type_info(self, param_type: str, type_hints: Dict[str, Any]) -> TypeInfo:
        """推断类型信息"""
        type_info = TypeInfo(type_name=param_type)

        is_optional = False
        if 'Optional' in param_type or '?' in param_type:
            is_optional = True
            type_info.is_optional = True

        clean_type = param_type.replace('Optional[', '').replace('?', '').strip()
        if 'List[' in clean_type or 'Dict[' in clean_type or 'Set[' in clean_type:
            type_info.is_collection = True
            type_info.collection_inner_type = self._extract_inner_type(clean_type)

        type_info.default_value = self._get_default_value_for_type(clean_type)

        if clean_type in self.PRIMITIVE_TYPES:
            type_info.constraints = self._get_constraints_for_type(clean_type)

        return type_info

    def _extract_inner_type(self, collection_type: str) -> str:
        """提取集合类型的内部类型"""
        match = re.search(r'\[([^\]]+)\]', collection_type)
        if match:
            return match.group(1)
        return 'Any'

    def _get_default_value_for_type(self, type_name: str) -> Any:
        """获取类型的默认值"""
        defaults = {
            'int': 0, 'Integer': 0,
            'float': 0.0, 'Float': 0.0,
            'str': '', 'String': '',
            'bool': False, 'Boolean': False,
        }
        return defaults.get(type_name, None)

    def _get_constraints_for_type(self, type_name: str) -> List[str]:
        """获取类型的约束条件"""
        constraints_map = {
            'int': ['min_value', 'max_value'],
            'float': ['precision', 'range'],
            'str': ['min_length', 'max_length', 'pattern'],
        }
        return constraints_map.get(type_name, [])

    def _generate_inferred_values(self, type_info: TypeInfo) -> List[Any]:
        """生成推断的正常值"""
        values = []

        if type_info.type_name in self.PRIMITIVE_TYPES:
            values.extend(self._get_typical_values(type_info.type_name))

        if type_info.is_collection:
            values.extend(self._get_typical_collection_values(type_info))

        if type_info.default_value is not None:
            values.append(type_info.default_value)

        if type_info.is_optional:
            values.append(None)

        return values

    def _get_typical_values(self, type_name: str) -> List[Any]:
        """获取类型的典型值"""
        typical_map = {
            'int': [0, 1, 10, 100, -1],
            'float': [0.0, 1.0, -1.0, 3.14],
            'str': ['test', 'hello', 'world', 'TEST123'],
            'bool': [True, False],
        }
        return typical_map.get(type_name, [])

    def _get_typical_collection_values(self, type_info: TypeInfo) -> List[Any]:
        """获取典型集合值"""
        inner_type = type_info.collection_inner_type
        if inner_type == 'int':
            return [[], [1], [1, 2, 3], list(range(100))]
        elif inner_type == 'str':
            return [[], ['a'], ['hello', 'world'], ['test' * 100]]
        elif inner_type == 'Any':
            return [[], [1, 'test', True], ['a', 1]]
        return [[], [type_info.default_value]]

    def _generate_boundary_values(self, type_info: TypeInfo) -> List[Any]:
        """生成边界值"""
        if type_info.type_name in self.BOUNDARY_VALUES_CONFIG:
            return list(self.BOUNDARY_VALUES_CONFIG[type_info.type_name])

        if type_info.is_collection:
            return [[], [type_info.default_value], [type_info.default_value] * 1000]

        return [type_info.default_value]

    def _generate_edge_cases(
        self, type_info: TypeInfo,
        business_rules: List[str]
    ) -> List[Any]:
        """生成边界情况和异常测试数据"""
        edge_cases = []

        if type_info.type_name == 'str':
            edge_cases.extend([
                '', ' ', '\n', '\t', '\r',
                '中文', '日本語', '한국어',
                '🎉', 'emoji', '🔐',
                'a' * 10000,  # 超长字符串
                '<script>alert(1)</script>',  # XSS测试
                "' OR '1'='1",  # SQL注入测试
            ])

        if type_info.type_name in ('int', 'float'):
            edge_cases.extend([
                0, -1, 1,
                2147483647, -2147483648,  # 32位整数边界
                9223372036854775807, -9223372036854775808,  # 64位整数边界
                float('inf'), float('-inf'),
            ])

        if type_info.is_collection:
            edge_cases.extend([
                [],
                None,
                [None],
                [type_info.default_value, None],
            ])

        return edge_cases

    def _infer_expected_behaviors(
        self, func_name: str,
        signature: Dict[str, Any],
        business_rules: List[str]
    ) -> List[str]:
        """推断期望行为"""
        behaviors = []

        if signature.get('return_type') != 'void' and signature.get('return_type') != 'None':
            behaviors.append('应返回符合类型注解的值')

        behaviors.append('应处理边界情况不崩溃')

        return behaviors

    def _build_signature_string(self, signature: Dict[str, Any]) -> str:
        """构建函数签名字符串"""
        func_name = signature.get('name', 'unknown')
        params = signature.get('params', [])
        return_type = signature.get('return_type', 'Any')

        param_strs = [
            f"{p.get('name', 'arg')}: {p.get('type', 'Any')}"
            for p in params
        ]

        return f"{func_name}({', '.join(param_strs)}) -> {return_type}"

    def _calculate_inference_confidence(
        self, func_test_data_list: List[FunctionTestData]
    ) -> float:
        """计算推理置信度"""
        if not func_test_data_list:
            return 0.0

        total_params = sum(len(ftd.test_data_specs) for ftd in func_test_data_list)
        if total_params == 0:
            return 0.0

        params_with_type = sum(
            1 for ftd in func_test_data_list
            for spec in ftd.test_data_specs
            if spec.type_info.type_name != 'Any'
        )

        confidence = (params_with_type / total_params) * 100
        return round(confidence, 2)

    def _calculate_type_coverage(
        self, func_test_data_list: List[FunctionTestData]
    ) -> float:
        """计算类型覆盖率"""
        all_types = set()
        covered_types = set()

        for ftd in func_test_data_list:
            for spec in ftd.test_data_specs:
                type_name = spec.type_info.type_name
                all_types.add(type_name)

                if len(spec.inferred_values) > 0:
                    covered_types.add(type_name)

        if not all_types:
            return 0.0

        coverage = (len(covered_types) / len(all_types)) * 100
        return round(coverage, 2)
