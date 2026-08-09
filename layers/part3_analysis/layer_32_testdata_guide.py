"""
Layer 32: TestDataGuideLayer - 测试数据生成指导层【V3.1升级】

本层负责为测试用例生成提供测试数据指导，根据路径特征、参数类型和
业务规则生成合适的测试数据建议，确保测试用例的有效性。
V3.1升级增强了智能数据生成和约束推理能力。
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import defaultdict


class DataType(Enum):
    """数据类型枚举"""
    STRING = auto()
    INTEGER = auto()
    FLOAT = auto()
    BOOLEAN = auto()
    LIST = auto()
    DICT = auto()
    DATE = auto()
    DATETIME = auto()
    EMAIL = auto()
    URL = auto()
    PHONE = auto()
    UUID = auto()
    ENUM = auto()
    CUSTOM = auto()


class TestDataCategory(Enum):
    """测试数据类别枚举"""
    NORMAL = auto()
    BOUNDARY = auto()
    EDGE_CASE = auto()
    ERROR_CASE = auto()
    RANDOM = auto()
    MOCK = auto()


@dataclass
class DataRequirement:
    """数据需求

    Attributes:
        param_name: 参数名称
        data_type: 数据类型
        constraints: 约束条件
        description: 描述
        examples: 示例值
        generation_hint: 生成提示
    """
    param_name: str
    data_type: DataType
    constraints: List[str] = field(default_factory=list)
    description: str = ""
    examples: List[Any] = field(default_factory=list)
    generation_hint: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "param_name": self.param_name,
            "data_type": self.data_type.name,
            "constraints": self.constraints,
            "description": self.description,
            "examples": [str(e) for e in self.examples],
            "generation_hint": self.generation_hint
        }


@dataclass
class TestDataSpec:
    """测试数据规格

    Attributes:
        path_id: 路径标识符
        data_requirements: 数据需求列表
        input_spec: 输入规格
        output_spec: 输出规格
        setup_data: 前置数据
        teardown_data: 清理数据
        test_data_hints: 测试数据提示
    """
    path_id: str
    data_requirements: List[DataRequirement] = field(default_factory=list)
    input_spec: Dict[str, Any] = field(default_factory=dict)
    output_spec: Dict[str, Any] = field(default_factory=dict)
    setup_data: Dict[str, Any] = field(default_factory=dict)
    teardown_data: Dict[str, Any] = field(default_factory=dict)
    test_data_hints: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "path_id": self.path_id,
            "data_requirements": [r.to_dict() for r in self.data_requirements],
            "input_spec": self.input_spec,
            "output_spec": self.output_spec,
            "setup_data": self.setup_data,
            "teardown_data": self.teardown_data,
            "test_data_hints": self.test_data_hints
        }


@dataclass
class GeneratedTestData:
    """生成的测试数据

    Attributes:
        test_case_id: 测试用例标识符
        path_id: 路径标识符
        category: 数据类别
        input_data: 输入数据
        expected_output: 预期输出
        metadata: 元数据
    """
    test_case_id: str
    path_id: str
    category: TestDataCategory
    input_data: Dict[str, Any] = field(default_factory=dict)
    expected_output: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "test_case_id": self.test_case_id,
            "path_id": self.path_id,
            "category": self.category.name,
            "input_data": self.input_data,
            "expected_output": self.expected_output,
            "metadata": self.metadata
        }


@dataclass
class TestDataGuideResult:
    """测试数据指导结果

    Attributes:
        total_paths: 总路径数
        data_specs: 数据规格列表
        generated_data: 生成的测试数据列表
        data_statistics: 数据统计
        recommendations: 建议
        constraints: 约束信息
        warnings: 警告
        metadata: 元信息
    """
    total_paths: int = 0
    data_specs: List[TestDataSpec] = field(default_factory=list)
    generated_data: List[GeneratedTestData] = field(default_factory=list)
    data_statistics: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "total_paths": self.total_paths,
            "data_specs": [s.to_dict() for s in self.data_specs],
            "generated_data": [d.to_dict() for d in self.generated_data],
            "data_statistics": self.data_statistics,
            "recommendations": self.recommendations,
            "constraints": self.constraints,
            "warnings": self.warnings,
            "metadata": self.metadata
        }


class TestDataGuideLayer:
    """测试数据生成指导层【V3.1升级】

    功能描述：
        - 分析路径的输入输出特征
        - 生成测试数据需求规格
        - 提供边界值和异常数据建议
        - 推断数据约束条件
        - 生成Mock数据和测试夹具
        - 支持多种数据类型的生成
        - 生成完整的测试数据套件

    输入类型：
        - 路径列表（List[Path]）
        - 函数签名（List[FunctionSlice]）
        - 业务规则（BusinessRecognitionResult）
        - 路径标注（List[PathAnnotation]）

    输出类型：
        - TestDataGuideResult: 测试数据指导结果
        - List[TestDataSpec]: 数据规格列表
        - List[GeneratedTestData]: 生成的测试数据
        - 统计信息和约束建议

    使用场景：
        - 测试用例数据生成
        - 边界值测试设计
        - 异常场景测试数据
        - 回归测试数据准备
        - 测试数据自动化
        - 参数化测试设计

    V3.1升级点：
        - 增强智能数据生成算法
        - 支持复杂约束推理
        - 提供更精确的边界值分析
        - 增加数据依赖处理
        - 支持批量数据生成
    """

    description: str = "测试数据生成指导层【V3.1升级】- 为测试用例生成提供数据指导"
    input_type: str = "List[Path]、FunctionSlice和BusinessRecognitionResult"
    output_type: str = "TestDataGuideResult和List[TestDataSpec]"

    def __init__(self):
        """初始化测试数据生成指导层"""
        self.paths = []
        self.function_slices = []
        self.business_result = None
        self.annotations = {}
        self.data_specs = []
        self.generated_data = []
        self.guide_result = None

    def process(self, context) -> TestDataGuideResult:
        """处理路径，生成测试数据指导

        Args:
            context: PipelineContext对象，包含路径和函数信息

        Returns:
            TestDataGuideResult: 测试数据指导结果

        Raises:
            ValueError: 当输入数据不足时
        """
        if not context.has('paths') and not context.has('enumerated_paths'):
            if not context.has('execution_paths'):
                raise ValueError("TestDataGuideLayer: 缺少路径数据")

        if context.has('paths'):
            self.paths = context.get('paths')
        elif context.has('enumerated_paths'):
            self.paths = context.get('enumerated_paths')
        elif context.has('execution_paths'):
            self.paths = context.get('execution_paths')

        if context.has('function_slices'):
            self.function_slices = context.get('function_slices')

        if context.has('business_recognition_result'):
            self.business_result = context.get('business_recognition_result')

        if context.has('path_annotations'):
            self.annotations = context.get('path_annotations')

        self._analyze_all_paths()

        self._generate_data_specs()

        self._generate_test_data()

        self._infer_constraints()

        self.guide_result = self._create_guide_result()

        context.set('test_data_specs', self.data_specs)
        context.set('generated_test_data', self.generated_data)
        context.set('test_data_guide_result', self.guide_result)
        context.set('test_data_guide_complete', True)
        context.set('test_data_statistics', self._get_statistics())

        return self.guide_result

    def _analyze_all_paths(self) -> None:
        """分析所有路径的数据需求"""
        for path in self.paths:
            path_id = self._get_path_id(path)

            data_spec = self._analyze_path_data_requirements(path, path_id)

            self.data_specs.append(data_spec)

    def _analyze_path_data_requirements(self, path, path_id: str) -> TestDataSpec:
        """分析路径的数据需求

        Args:
            path: 路径对象
            path_id: 路径标识符

        Returns:
            TestDataSpec: 测试数据规格
        """
        data_requirements = []

        if hasattr(path, 'variables'):
            for var in path.variables:
                requirement = self._infer_data_requirement(var, path)
                if requirement:
                    data_requirements.append(requirement)

        func_name = getattr(path, 'function_name', '')

        for slice_item in self.function_slices:
            slice_name = getattr(slice_item, 'name', '') or getattr(slice_item, 'qualified_name', '')
            if slice_name == func_name:
                params = getattr(slice_item, 'parameters', [])
                for param in params:
                    requirement = self._create_requirement_from_param(param, func_name)
                    if requirement:
                        data_requirements.append(requirement)

        input_spec = self._generate_input_spec(path)

        output_spec = self._generate_output_spec(path)

        setup_data = self._generate_setup_data(path)

        teardown_data = self._generate_teardown_data(path)

        hints = self._generate_data_hints(path)

        return TestDataSpec(
            path_id=path_id,
            data_requirements=data_requirements,
            input_spec=input_spec,
            output_spec=output_spec,
            setup_data=setup_data,
            teardown_data=teardown_data,
            test_data_hints=hints
        )

    def _infer_data_requirement(self, var: str, path) -> Optional[DataRequirement]:
        """推断数据需求

        Args:
            var: 变量名
            path: 路径对象

        Returns:
            Optional[DataRequirement]: 数据需求
        """
        data_type = self._infer_variable_type(var)

        constraints = self._infer_constraints(var, path)

        description = f"变量 {var} 的测试数据"

        examples = self._generate_examples(var, data_type)

        hint = self._generate_generation_hint(var, data_type, constraints)

        return DataRequirement(
            param_name=var,
            data_type=data_type,
            constraints=constraints,
            description=description,
            examples=examples,
            generation_hint=hint
        )

    def _infer_variable_type(self, var: str) -> DataType:
        """推断变量类型

        Args:
            var: 变量名

        Returns:
            DataType: 数据类型
        """
        var_lower = var.lower()

        if 'email' in var_lower:
            return DataType.EMAIL
        elif 'url' in var_lower or 'uri' in var_lower:
            return DataType.URL
        elif 'phone' in var_lower or 'mobile' in var_lower:
            return DataType.PHONE
        elif 'id' in var_lower:
            return DataType.UUID
        elif 'date' in var_lower and 'time' not in var_lower:
            return DataType.DATE
        elif 'time' in var_lower or 'datetime' in var_lower:
            return DataType.DATETIME
        elif 'count' in var_lower or 'num' in var_lower or 'size' in var_lower:
            return DataType.INTEGER
        elif 'price' in var_lower or 'rate' in var_lower or 'amount' in var_lower:
            return DataType.FLOAT
        elif 'is_' in var_lower or 'has_' in var_lower or 'enabled' in var_lower:
            return DataType.BOOLEAN
        elif 'list' in var_lower or 'items' in var_lower:
            return DataType.LIST
        elif 'config' in var_lower or 'data' in var_lower:
            return DataType.DICT
        else:
            return DataType.STRING

    def _infer_constraints(self, var: str, path) -> List[str]:
        """推断约束条件

        Args:
            var: 变量名
            path: 路径对象

        Returns:
            List[str]: 约束条件列表
        """
        constraints = []

        var_lower = var.lower()

        if 'id' in var_lower:
            constraints.append("有效的标识符格式")
        if 'name' in var_lower:
            constraints.append("非空字符串")
            constraints.append("长度限制（如果适用）")
        if 'email' in var_lower:
            constraints.append("有效的邮箱格式")
        if 'url' in var_lower or 'uri' in var_lower:
            constraints.append("有效的URL格式")
        if 'count' in var_lower or 'num' in var_lower or 'size' in var_lower:
            constraints.append("非负整数")
        if 'price' in var_lower or 'rate' in var_lower:
            constraints.append("正数")
        if 'phone' in var_lower or 'mobile' in var_lower:
            constraints.append("有效的电话号码格式")

        if hasattr(path, 'conditions'):
            for condition in path.conditions:
                if var in condition:
                    inferred = self._extract_constraint_from_condition(condition, var)
                    if inferred:
                        constraints.append(inferred)

        return constraints

    def _extract_constraint_from_condition(self, condition: str, var: str) -> Optional[str]:
        """从条件中提取约束

        Args:
            condition: 条件字符串
            var: 变量名

        Returns:
            Optional[str]: 约束条件
        """
        if '>' in condition and var in condition:
            return f"{var} 需要满足特定的大小关系"
        if '<' in condition and var in condition:
            return f"{var} 需要满足特定的大小关系"
        if '==' in condition and var in condition:
            return f"{var} 需要等于特定值"
        if '!=' in condition and var in condition:
            return f"{var} 不能等于特定值"

        return None

    def _generate_examples(self, var: str, data_type: DataType) -> List[Any]:
        """生成示例值

        Args:
            var: 变量名
            data_type: 数据类型

        Returns:
            List[Any]: 示例值列表
        """
        examples = []

        if data_type == DataType.STRING:
            examples = ["test_value", "sample", "example"]
        elif data_type == DataType.INTEGER:
            examples = [0, 1, 100, -1]
        elif data_type == DataType.FLOAT:
            examples = [0.0, 1.0, 99.99, -1.5]
        elif data_type == DataType.BOOLEAN:
            examples = [True, False]
        elif data_type == DataType.EMAIL:
            examples = ["test@example.com", "user@domain.org"]
        elif data_type == DataType.URL:
            examples = ["https://example.com", "http://test.org/path"]
        elif data_type == DataType.PHONE:
            examples = ["1234567890", "+1234567890"]
        elif data_type == DataType.UUID:
            examples = ["550e8400-e29b-41d4-a716-446655440000"]
        elif data_type == DataType.DATE:
            examples = ["2024-01-01", "2024-12-31"]
        elif data_type == DataType.DATETIME:
            examples = ["2024-01-01T00:00:00", "2024-12-31T23:59:59"]
        elif data_type == DataType.LIST:
            examples = [[], [1, 2, 3], ["a", "b"]]
        elif data_type == DataType.DICT:
            examples = [{}, {"key": "value"}]

        return examples

    def _generate_generation_hint(self, var: str, data_type: DataType,
                                 constraints: List[str]) -> str:
        """生成生成提示

        Args:
            var: 变量名
            data_type: 数据类型
            constraints: 约束条件

        Returns:
            str: 生成提示
        """
        hints = []

        hints.append(f"为 {var} 生成 {data_type.name} 类型的数据")

        if constraints:
            hints.append(f"需要满足约束: {', '.join(constraints[:2])}")

        type_hints = {
            DataType.STRING: "可使用 Faker 库生成真实感的字符串",
            DataType.INTEGER: "注意边界值如 0, 1, -1, 最大值",
            DataType.FLOAT: "注意浮点数精度问题",
            DataType.EMAIL: "使用有效邮箱格式",
            DataType.URL: "使用有效URL格式",
            DataType.PHONE: "使用有效电话号码格式",
            DataType.UUID: "使用标准UUID格式",
            DataType.DATE: "注意日期格式和范围",
            DataType.DATETIME: "注意时区和格式",
            DataType.LIST: "考虑空列表、单元素、多元素情况",
            DataType.DICT: "考虑空字典和嵌套结构"
        }

        if data_type in type_hints:
            hints.append(type_hints[data_type])

        return " | ".join(hints)

    def _create_requirement_from_param(self, param: Dict, func_name: str) -> Optional[DataRequirement]:
        """从参数创建需求

        Args:
            param: 参数信息
            func_name: 函数名

        Returns:
            Optional[DataRequirement]: 数据需求
        """
        param_name = param.get('name', '')
        if not param_name:
            return None

        annotation = param.get('annotation', '')
        data_type = self._parse_type_annotation(annotation)

        constraints = []
        if param.get('required', True):
            constraints.append("必填参数")
        if param.get('default'):
            constraints.append(f"默认值: {param.get('default')}")

        examples = self._generate_examples(param_name, data_type)

        hint = self._generate_generation_hint(param_name, data_type, constraints)

        return DataRequirement(
            param_name=param_name,
            data_type=data_type,
            constraints=constraints,
            description=f"函数 {func_name} 的参数 {param_name}",
            examples=examples,
            generation_hint=hint
        )

    def _parse_type_annotation(self, annotation: str) -> DataType:
        """解析类型注解

        Args:
            annotation: 类型注解字符串

        Returns:
            DataType: 数据类型
        """
        annotation_lower = annotation.lower()

        type_mapping = {
            'str': DataType.STRING,
            'string': DataType.STRING,
            'int': DataType.INTEGER,
            'integer': DataType.INTEGER,
            'float': DataType.FLOAT,
            'double': DataType.FLOAT,
            'bool': DataType.BOOLEAN,
            'boolean': DataType.BOOLEAN,
            'list': DataType.LIST,
            'array': DataType.LIST,
            'dict': DataType.DICT,
            'map': DataType.DICT,
            'date': DataType.DATE,
            'datetime': DataType.DATETIME,
            'email': DataType.EMAIL,
            'url': DataType.URL,
            'uri': DataType.URL,
            'phone': DataType.PHONE,
            'uuid': DataType.UUID
        }

        return type_mapping.get(annotation_lower, DataType.STRING)

    def _generate_input_spec(self, path) -> Dict[str, Any]:
        """生成输入规格

        Args:
            path: 路径对象

        Returns:
            Dict[str, Any]: 输入规格
        """
        spec = {
            'required_params': [],
            'optional_params': [],
            'data_types': {},
            'constraints': []
        }

        if hasattr(path, 'variables'):
            spec['required_params'] = list(path.variables[:5])

        for var in spec.get('required_params', []):
            data_type = self._infer_variable_type(var)
            spec['data_types'][var] = data_type.name

        return spec

    def _generate_output_spec(self, path) -> Dict[str, Any]:
        """生成输出规格

        Args:
            path: 路径对象

        Returns:
            Dict[str, Any]: 输出规格
        """
        spec = {
            'expected_return': None,
            'side_effects': [],
            'exceptions': []
        }

        func_name = getattr(path, 'function_name', '')

        if 'get' in func_name.lower() or 'find' in func_name.lower() or 'query' in func_name.lower():
            spec['expected_return'] = 'result_or_none'
        elif 'create' in func_name.lower() or 'add' in func_name.lower():
            spec['expected_return'] = 'created_object'
        elif 'update' in func_name.lower() or 'modify' in func_name.lower():
            spec['expected_return'] = 'updated_object'
        elif 'delete' in func_name.lower() or 'remove' in func_name.lower():
            spec['expected_return'] = 'boolean_or_none'

        return spec

    def _generate_setup_data(self, path) -> Dict[str, Any]:
        """生成前置数据

        Args:
            path: 路径对象

        Returns:
            Dict[str, Any]: 前置数据
        """
        setup = {}

        func_name = getattr(path, 'function_name', '')

        if self.business_result:
            for entity in self.business_result.entities[:3]:
                setup[entity.name] = self._generate_mock_entity(entity)

        if hasattr(path, 'dependencies'):
            for dep in path.dependencies[:3]:
                setup[dep] = f"mock_{dep}"

        return setup

    def _generate_mock_entity(self, entity) -> Dict[str, Any]:
        """生成Mock实体

        Args:
            entity: 业务实体

        Returns:
            Dict[str, Any]: Mock数据
        """
        mock_data = {
            'id': 'test_id_001',
            'name': 'Test Entity',
            'is_active': True
        }

        if hasattr(entity, 'fields'):
            for field in entity.fields[:5]:
                field_name = field.get('name', '')
                field_type = field.get('type', 'string')
                mock_data[field_name] = self._generate_mock_value(field_type)

        return mock_data

    def _generate_mock_value(self, field_type: str) -> Any:
        """生成Mock值

        Args:
            field_type: 字段类型

        Returns:
            Any: Mock值
        """
        if 'int' in field_type.lower():
            return 1
        elif 'float' in field_type.lower():
            return 1.0
        elif 'bool' in field_type.lower():
            return True
        elif 'list' in field_type.lower() or 'array' in field_type.lower():
            return []
        elif 'dict' in field_type.lower() or 'map' in field_type.lower():
            return {}
        else:
            return "test_value"

    def _generate_teardown_data(self, path) -> Dict[str, Any]:
        """生成清理数据

        Args:
            path: 路径对象

        Returns:
            Dict[str, Any]: 清理数据
        """
        teardown = {
            'cleanup_required': True,
            'resources_to_release': []
        }

        if hasattr(path, 'dependencies'):
            for dep in path.dependencies[:3]:
                teardown['resources_to_release'].append(dep)

        return teardown

    def _generate_data_hints(self, path) -> List[str]:
        """生成数据提示

        Args:
            path: 路径对象

        Returns:
            List[str]: 数据提示列表
        """
        hints = []

        hints.append("使用真实的测试数据以提高测试有效性")

        hints.append("包含边界值测试")

        hints.append("测试空值和None情况")

        if hasattr(path, 'function_name'):
            func_name = path.function_name.lower()
            if 'validate' in func_name or 'check' in func_name:
                hints.append("测试有效和无效两种情况")
            if 'auth' in func_name or 'login' in func_name:
                hints.append("准备多种用户凭证测试")

        return hints

    def _generate_data_specs(self) -> None:
        """生成数据规格列表"""
        for path in self.paths:
            path_id = self._get_path_id(path)

            existing = [s for s in self.data_specs if s.path_id == path_id]
            if existing:
                continue

            data_spec = self._analyze_path_data_requirements(path, path_id)
            self.data_specs.append(data_spec)

    def _generate_test_data(self) -> None:
        """生成测试数据"""
        self.generated_data = []

        test_case_id = 0

        for data_spec in self.data_specs:
            normal_data = self._generate_category_data(
                data_spec, TestDataCategory.NORMAL, "normal"
            )
            normal_data.test_case_id = f"test_{test_case_id}"
            test_case_id += 1
            self.generated_data.append(normal_data)

            boundary_data = self._generate_category_data(
                data_spec, TestDataCategory.BOUNDARY, "boundary"
            )
            boundary_data.test_case_id = f"test_{test_case_id}"
            test_case_id += 1
            self.generated_data.append(boundary_data)

            error_data = self._generate_category_data(
                data_spec, TestDataCategory.ERROR_CASE, "error"
            )
            error_data.test_case_id = f"test_{test_case_id}"
            test_case_id += 1
            self.generated_data.append(error_data)

    def _generate_category_data(self, data_spec: TestDataSpec,
                               category: TestDataCategory,
                               suffix: str) -> GeneratedTestData:
        """生成特定类别的测试数据

        Args:
            data_spec: 数据规格
            category: 数据类别
            suffix: 后缀

        Returns:
            GeneratedTestData: 生成的测试数据
        """
        input_data = {}
        expected_output = {}

        for requirement in data_spec.data_requirements:
            if category == TestDataCategory.NORMAL:
                input_data[requirement.param_name] = self._generate_normal_value(requirement)
            elif category == TestDataCategory.BOUNDARY:
                input_data[requirement.param_name] = self._generate_boundary_value(requirement)
            elif category == TestDataCategory.ERROR_CASE:
                input_data[requirement.param_name] = self._generate_error_value(requirement)

        expected_output = self._generate_expected_output(data_spec)

        return GeneratedTestData(
            test_case_id=f"{data_spec.path_id}_{suffix}",
            path_id=data_spec.path_id,
            category=category,
            input_data=input_data,
            expected_output=expected_output,
            metadata={
                'generated_from': 'TestDataGuideLayer',
                'data_spec_id': data_spec.path_id
            }
        )

    def _generate_normal_value(self, requirement: DataRequirement) -> Any:
        """生成正常值

        Args:
            requirement: 数据需求

        Returns:
            Any: 正常值
        """
        if requirement.examples:
            return requirement.examples[0]

        if requirement.data_type == DataType.STRING:
            return "test_value"
        elif requirement.data_type == DataType.INTEGER:
            return 1
        elif requirement.data_type == DataType.FLOAT:
            return 1.0
        elif requirement.data_type == DataType.BOOLEAN:
            return True
        else:
            return None

    def _generate_boundary_value(self, requirement: DataRequirement) -> Any:
        """生成边界值

        Args:
            requirement: 数据需求

        Returns:
            Any: 边界值
        """
        if requirement.data_type == DataType.INTEGER:
            return 0
        elif requirement.data_type == DataType.FLOAT:
            return 0.0
        elif requirement.data_type == DataType.STRING:
            return ""
        elif requirement.data_type == DataType.LIST:
            return []
        else:
            return None

    def _generate_error_value(self, requirement: DataRequirement) -> Any:
        """生成错误值

        Args:
            requirement: 数据需求

        Returns:
            Any: 错误值
        """
        if requirement.data_type == DataType.INTEGER:
            return -999999
        elif requirement.data_type == DataType.STRING:
            return None
        elif requirement.data_type == DataType.BOOLEAN:
            return None
        else:
            return None

    def _generate_expected_output(self, data_spec: TestDataSpec) -> Dict[str, Any]:
        """生成预期输出

        Args:
            data_spec: 数据规格

        Returns:
            Dict[str, Any]: 预期输出
        """
        output = {
            'should_succeed': True,
            'expected_result': None
        }

        if data_spec.output_spec.get('expected_return'):
            output['expected_result'] = data_spec.output_spec['expected_return']

        return output

    def _infer_constraints(self) -> None:
        """推断约束信息"""
        self.constraints = {
            'global_constraints': [],
            'path_specific': {}
        }

        for data_spec in self.data_specs:
            path_constraints = []

            for requirement in data_spec.data_requirements:
                if requirement.constraints:
                    path_constraints.extend(requirement.constraints)

            if path_constraints:
                self.constraints['path_specific'][data_spec.path_id] = list(set(path_constraints))

    def _create_guide_result(self) -> TestDataGuideResult:
        """创建指导结果

        Returns:
            TestDataGuideResult: 测试数据指导结果
        """
        result = TestDataGuideResult(
            total_paths=len(self.paths),
            data_specs=self.data_specs,
            generated_data=self.generated_data
        )

        result.data_statistics = self._compute_data_statistics()

        result.recommendations = self._generate_recommendations()

        result.constraints = self.constraints

        result.metadata = {
            'total_data_specs': len(self.data_specs),
            'total_test_cases': len(self.generated_data),
            'avg_requirements_per_path': sum(len(s.data_requirements) for s in self.data_specs) / len(self.data_specs) if self.data_specs else 0
        }

        return result

    def _compute_data_statistics(self) -> Dict[str, Any]:
        """计算数据统计

        Returns:
            Dict[str, Any]: 数据统计
        """
        stats = {
            'total_paths': len(self.paths),
            'total_data_specs': len(self.data_specs),
            'total_test_cases': len(self.generated_data),
            'by_category': defaultdict(int)
        }

        for data in self.generated_data:
            stats['by_category'][data.category.name] += 1

        stats['by_category'] = dict(stats['by_category'])

        data_type_counts = defaultdict(int)
        for spec in self.data_specs:
            for req in spec.data_requirements:
                data_type_counts[req.data_type.name] += 1

        stats['data_types'] = dict(data_type_counts)

        return stats

    def _generate_recommendations(self) -> List[str]:
        """生成建议

        Returns:
            List[str]: 建议列表
        """
        recommendations = []

        recommendations.append("为每个路径生成多种测试数据类别")

        recommendations.append("包含边界值和异常值测试")

        recommendations.append("使用真实感数据提高测试有效性")

        if self.generated_data:
            normal_count = sum(1 for d in self.generated_data
                            if d.category == TestDataCategory.NORMAL)
            if normal_count < len(self.generated_data) * 0.3:
                recommendations.append("建议增加正常值测试用例")

        recommendations.append("注意测试数据的清理和隔离")

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
        if not self.guide_result:
            return {}

        return {
            'total_paths': self.guide_result.total_paths,
            'total_data_specs': len(self.data_specs),
            'total_test_cases': len(self.generated_data),
            'data_statistics': self.guide_result.data_statistics,
            'recommendations': self.guide_result.recommendations
        }

    def get_data_spec(self, path_id: str) -> Optional[TestDataSpec]:
        """获取指定路径的数据规格

        Args:
            path_id: 路径标识符

        Returns:
            Optional[TestDataSpec]: 数据规格
        """
        for spec in self.data_specs:
            if spec.path_id == path_id:
                return spec
        return None

    def get_test_data_by_category(self, category: TestDataCategory) -> List[GeneratedTestData]:
        """按类别获取测试数据

        Args:
            category: 数据类别

        Returns:
            List[GeneratedTestData]: 测试数据列表
        """
        return [d for d in self.generated_data if d.category == category]

    def export_test_data(self) -> List[Dict[str, Any]]:
        """导出测试数据

        Returns:
            List[Dict[str, Any]]: 测试数据列表
        """
        return [d.to_dict() for d in self.generated_data]

    def export_data_specs(self) -> List[Dict[str, Any]]:
        """导出数据规格

        Returns:
            List[Dict[str, Any]]: 数据规格列表
        """
        return [s.to_dict() for s in self.data_specs]

    def suggest_data_enhancements(self) -> List[str]:
        """建议数据增强

        Returns:
            List[str]: 增强建议
        """
        suggestions = []

        suggestions.append("考虑使用Faker库生成真实感数据")

        suggestions.append("添加数据依赖关系模拟")

        suggestions.append("实现数据模板以支持多种场景")

        return suggestions
