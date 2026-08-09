"""
Layer 20: FunctionSemanticLayer - 函数语义理解层

本层负责对函数切片进行深度语义分析，理解函数的功能、行为特征和业务含义。
为后续的路径生成、测试用例生成等提供语义基础。
"""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum, auto
import re


class FunctionComplexity(Enum):
    """函数复杂度等级"""
    TRIVIAL = auto()
    SIMPLE = auto()
    MODERATE = auto()
    COMPLEX = auto()
    VERY_COMPLEX = auto()


class SideEffectType(Enum):
    """副作用类型"""
    FILE_IO = auto()
    NETWORK = auto()
    DATABASE = auto()
    GLOBAL_STATE = auto()
    RANDOM = auto()
    PRINT = auto()
    MUTATION = auto()
    NONE = auto()


class SemanticCategory(Enum):
    """语义分类"""
    DATA_PROCESSING = auto()
    ALGORITHM = auto()
    VALIDATION = auto()
    TRANSFORMATION = auto()
    UTILITY = auto()
    BUSINESS_LOGIC = auto()
    API_HANDLER = auto()
    DATABASE_OPERATION = auto()
    NETWORK_OPERATION = auto()
    UI_COMPONENT = auto()
    CONFIGURATION = auto()
    ERROR_HANDLING = auto()
    INITIALIZATION = auto()
    COMPUTATION = auto()
    SERIALIZATION = auto()
    PARSING = auto()
    SECURITY = auto()
    LOGGING = auto()
    CACHING = auto()
    FILE_IO = auto()
    UNKNOWN = auto()


@dataclass
class ParameterSemantic:
    """参数语义信息

    Attributes:
        name: 参数名称
        semantic_type: 语义类型（input, output, inout）
        data_type: 数据类型描述
        constraints: 约束条件
        business_meaning: 业务含义
        optional: 是否可选
        default_value: 默认值
        validation_rules: 验证规则
    """
    name: str
    semantic_type: str = "input"
    data_type: str = "Any"
    constraints: List[str] = field(default_factory=list)
    business_meaning: str = ""
    optional: bool = False
    default_value: Optional[Any] = None
    validation_rules: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "semantic_type": self.semantic_type,
            "data_type": self.data_type,
            "constraints": self.constraints,
            "business_meaning": self.business_meaning,
            "optional": self.optional,
            "default_value": self.default_value,
            "validation_rules": self.validation_rules
        }


@dataclass
class FunctionSemantic:
    """函数语义信息

    Attributes:
        function_id: 函数标识符
        name: 函数名称
        purpose: 函数目的描述
        functionality: 功能描述
        complexity: 复杂度等级
        semantic_category: 语义分类
        parameters: 参数语义列表
        return_semantic: 返回值语义
        side_effects: 副作用类型集合
        exceptions: 可能的异常列表
        business_domain: 业务领域
        algorithm_type: 算法类型
        data_flow: 数据流描述
        control_flow_pattern: 控制流模式
        performance_hints: 性能提示
        testability_score: 可测试性评分（0-10）
        test_guidance: 测试指导
        dependencies: 依赖描述
        preconditions: 前置条件
        postconditions: 后置条件
        invariants: 不变式
        examples: 使用示例
        notes: 备注
        metadata: 其他元信息
    """
    function_id: str
    name: str
    purpose: str = ""
    functionality: str = ""
    complexity: FunctionComplexity = FunctionComplexity.SIMPLE
    semantic_category: SemanticCategory = SemanticCategory.UNKNOWN
    parameters: List[ParameterSemantic] = field(default_factory=list)
    return_semantic: Dict[str, Any] = field(default_factory=dict)
    side_effects: Set[SideEffectType] = field(default_factory=set)
    exceptions: List[Dict[str, str]] = field(default_factory=list)
    business_domain: str = ""
    algorithm_type: str = ""
    data_flow: str = ""
    control_flow_pattern: str = ""
    performance_hints: Dict[str, Any] = field(default_factory=dict)
    testability_score: float = 5.0
    test_guidance: str = ""
    dependencies: List[str] = field(default_factory=list)
    preconditions: List[str] = field(default_factory=list)
    postconditions: List[str] = field(default_factory=list)
    invariants: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "function_id": self.function_id,
            "name": self.name,
            "purpose": self.purpose,
            "functionality": self.functionality,
            "complexity": self.complexity.name,
            "semantic_category": self.semantic_category.name,
            "parameters": [p.to_dict() for p in self.parameters],
            "return_semantic": self.return_semantic,
            "side_effects": [e.name for e in self.side_effects],
            "exceptions": self.exceptions,
            "business_domain": self.business_domain,
            "algorithm_type": self.algorithm_type,
            "data_flow": self.data_flow,
            "control_flow_pattern": self.control_flow_pattern,
            "performance_hints": self.performance_hints,
            "testability_score": self.testability_score,
            "test_guidance": self.test_guidance,
            "dependencies": self.dependencies,
            "preconditions": self.preconditions,
            "postconditions": self.postconditions,
            "invariants": self.invariants,
            "examples": self.examples,
            "notes": self.notes,
            "metadata": self.metadata
        }

    def has_side_effect(self) -> bool:
        """检查是否有副作用

        Returns:
            bool: 是否有副作用
        """
        return SideEffectType.NONE not in self.side_effects and len(self.side_effects) > 0

    def get_side_effect_types(self) -> List[str]:
        """获取副作用类型列表

        Returns:
            List[str]: 副作用类型列表
        """
        return [e.name for e in self.side_effects if e != SideEffectType.NONE]

    def is_pure_function(self) -> bool:
        """判断是否为纯函数

        Returns:
            bool: 是否为纯函数
        """
        return len(self.side_effects) == 0 or (len(self.side_effects) == 1 and SideEffectType.NONE in self.side_effects)


class FunctionSemanticLayer:
    """函数语义理解层

    功能描述：
        - 对函数切片进行深度语义分析
        - 识别函数的功能、目的和业务含义
        - 分析参数和返回值的语义
        - 识别副作用和外部依赖
        - 评估函数的复杂度和可测试性
        - 生成测试指导和建议
        - 识别业务领域和算法类型

    输入类型：
        - 函数切片列表（List[FunctionSlice]）
        - AST节点和源代码

    输出类型：
        - List[FunctionSemantic]: 函数语义列表
        - 包含每个函数的详细语义信息

    使用场景：
        - 为测试用例生成提供语义基础
        - 支持基于语义的代码搜索
        - 帮助理解函数的业务含义
        - 指导测试用例的设计

    V3.1升级点：
        - 增强对复杂业务逻辑的识别能力
        - 提供更精确的可测试性评估
        - 增加对现代编程模式的语义理解
        - 支持跨函数的语义关联分析
    """

    description: str = "函数语义理解层 - 深度分析函数的功能和业务含义"
    input_type: str = "List[FunctionSlice] - 函数切片列表"
    output_type: str = "List[FunctionSemantic] - 函数语义列表"

    def __init__(self):
        """初始化函数语义层"""
        self.function_slices = []
        self.semantic_results = []
        self.patterns = self._init_patterns()
        self.keywords = self._init_keywords()

    def _init_patterns(self) -> Dict[str, re.Pattern]:
        """初始化正则表达式模式

        Returns:
            Dict[str, re.Pattern]: 模式字典
        """
        return {
            'validation': re.compile(r'validate|check|verify|assert|require|ensure', re.IGNORECASE),
            'transformation': re.compile(r'transform|convert|parse|format|encode|decode', re.IGNORECASE),
            'calculation': re.compile(r'calculate|compute|sum|average|count|aggregate', re.IGNORECASE),
            'io_operation': re.compile(r'read|write|load|save|open|close', re.IGNORECASE),
            'network': re.compile(r'request|fetch|send|http|api|endpoint', re.IGNORECASE),
            'database': re.compile(r'query|insert|update|delete|select|commit|rollback', re.IGNORECASE),
            'file_io': re.compile(r'file|directory|path|folder', re.IGNORECASE),
            'algorithm': re.compile(r'sort|search|find|match|iterate|traverse|walk', re.IGNORECASE),
            'data_processing': re.compile(r'filter|map|reduce|group|split|merge|join', re.IGNORECASE),
            'business': re.compile(r'order|user|customer|product|payment|inventory', re.IGNORECASE),
            'security': re.compile(r'auth|encrypt|decrypt|hash|permission|access|login', re.IGNORECASE),
            'logging': re.compile(r'log|debug|info|warn|error|trace', re.IGNORECASE),
            'exception': re.compile(r'try|catch|except|raise|error|exception', re.IGNORECASE),
            'async': re.compile(r'async|await|promise|future|callback|event', re.IGNORECASE),
            'performance': re.compile(r'cache|memoize|optimize|benchmark|profile', re.IGNORECASE),
            'configuration': re.compile(r'config|setting|option|param|environment', re.IGNORECASE),
            'serialization': re.compile(r'serialize|deserialize|json|xml|pickle|dump|load', re.IGNORECASE)
        }

    def _init_keywords(self) -> Dict[SemanticCategory, List[str]]:
        """初始化语义关键词

        Returns:
            Dict[SemanticCategory, List[str]]: 关键词映射
        """
        return {
            SemanticCategory.VALIDATION: ['validate', 'check', 'verify', 'assert', 'require', 'is_valid', 'ensure'],
            SemanticCategory.TRANSFORMATION: ['transform', 'convert', 'parse', 'format', 'encode', 'decode', 'to'],
            SemanticCategory.COMPUTATION: ['calculate', 'compute', 'sum', 'average', 'count', 'aggregate'],
            SemanticCategory.DATA_PROCESSING: ['filter', 'map', 'reduce', 'group', 'split', 'merge', 'join'],
            SemanticCategory.ALGORITHM: ['sort', 'search', 'find', 'match', 'iterate', 'traverse', 'walk', 'binary'],
            SemanticCategory.API_HANDLER: ['request', 'handle', 'endpoint', 'route', 'controller', 'middleware'],
            SemanticCategory.DATABASE_OPERATION: ['query', 'insert', 'update', 'delete', 'select', 'commit'],
            SemanticCategory.NETWORK_OPERATION: ['fetch', 'send', 'http', 'api', 'client', 'server'],
            SemanticCategory.FILE_IO: ['read', 'write', 'load', 'save', 'open', 'close', 'file'],
            SemanticCategory.SERIALIZATION: ['serialize', 'deserialize', 'json', 'xml', 'pickle', 'dump', 'load'],
            SemanticCategory.SECURITY: ['auth', 'encrypt', 'decrypt', 'hash', 'permission', 'access', 'login'],
            SemanticCategory.LOGGING: ['log', 'debug', 'info', 'warn', 'error', 'trace'],
            SemanticCategory.CACHING: ['cache', 'memoize', 'store', 'remember', 'remember_result'],
            SemanticCategory.BUSINESS_LOGIC: ['order', 'user', 'customer', 'product', 'payment', 'invoice'],
            SemanticCategory.UTILITY: ['util', 'helper', 'tool', 'common', 'shared', 'generic'],
            SemanticCategory.CONFIGURATION: ['config', 'setting', 'option', 'param', 'environment', 'init']
        }

    def process(self, context) -> List[FunctionSemantic]:
        """处理函数切片，生成语义信息

        Args:
            context: PipelineContext对象，包含函数切片列表

        Returns:
            List[FunctionSemantic]: 函数语义列表

        Raises:
            ValueError: 当函数切片列表为空时
        """
        if not context.has('function_slices'):
            raise ValueError("FunctionSemanticLayer: 缺少函数切片列表")

        self.function_slices = context.get('function_slices')

        if not self.function_slices:
            raise ValueError("FunctionSemanticLayer: 函数切片列表为空")

        self.semantic_results = []

        for function_slice in self.function_slices:
            semantic = self._analyze_function_semantic(function_slice)
            self.semantic_results.append(semantic)

        context.set('function_semantics', self.semantic_results)
        context.set('semantic_analysis_complete', True)
        context.set('semantic_statistics', self._get_statistics())

        return self.semantic_results

    def _analyze_function_semantic(self, function_slice) -> FunctionSemantic:
        """分析单个函数的语义

        Args:
            function_slice: 函数切片

        Returns:
            FunctionSemantic: 函数语义对象
        """
        semantic = FunctionSemantic(
            function_id=getattr(function_slice, 'slice_id', 'unknown'),
            name=getattr(function_slice, 'name', 'unknown')
        )

        semantic.purpose = self._infer_purpose(function_slice)
        semantic.functionality = self._infer_functionality(function_slice)
        semantic.complexity = self._calculate_complexity(function_slice)
        semantic.semantic_category = self._classify_semantic(function_slice)
        semantic.parameters = self._analyze_parameters(function_slice)
        semantic.return_semantic = self._analyze_return_value(function_slice)
        semantic.side_effects = self._analyze_side_effects(function_slice)
        semantic.exceptions = self._analyze_exceptions(function_slice)
        semantic.business_domain = self._infer_business_domain(function_slice)
        semantic.algorithm_type = self._identify_algorithm_type(function_slice)
        semantic.data_flow = self._describe_data_flow(function_slice)
        semantic.control_flow_pattern = self._identify_control_flow_pattern(function_slice)
        semantic.performance_hints = self._extract_performance_hints(function_slice)
        semantic.testability_score = self._evaluate_testability(function_slice)
        semantic.test_guidance = self._generate_test_guidance(function_slice, semantic)
        semantic.dependencies = getattr(function_slice, 'calls', [])
        semantic.preconditions = self._infer_preconditions(function_slice)
        semantic.postconditions = self._infer_postconditions(function_slice)
        semantic.invariants = self._identify_invariants(function_slice)
        semantic.examples = self._generate_examples(function_slice)

        return semantic

    def _infer_purpose(self, function_slice) -> str:
        """推断函数目的

        Args:
            function_slice: 函数切片

        Returns:
            str: 函数目的描述
        """
        func_name = getattr(function_slice, 'name', '').lower()
        source_code = getattr(function_slice, 'source_code', '').lower()

        for category, keywords in self.keywords.items():
            for keyword in keywords:
                if keyword in func_name or keyword in source_code:
                    return self._get_category_purpose(category)

        return f"执行{func_name}定义的操作"

    def _get_category_purpose(self, category: SemanticCategory) -> str:
        """获取类别目的描述

        Args:
            category: 语义类别

        Returns:
            str: 目的描述
        """
        purposes = {
            SemanticCategory.VALIDATION: "验证输入数据的有效性和完整性",
            SemanticCategory.TRANSFORMATION: "将数据从一种格式或结构转换为另一种",
            SemanticCategory.COMPUTATION: "执行数学或逻辑计算",
            SemanticCategory.DATA_PROCESSING: "对数据集进行过滤、映射、聚合等操作",
            SemanticCategory.ALGORITHM: "实现特定的算法逻辑",
            SemanticCategory.API_HANDLER: "处理API请求和响应",
            SemanticCategory.DATABASE_OPERATION: "执行数据库的CRUD操作",
            SemanticCategory.NETWORK_OPERATION: "处理网络通信和数据传输",
            SemanticCategory.FILE_IO: "读写文件和目录操作",
            SemanticCategory.SERIALIZATION: "序列化和反序列化数据",
            SemanticCategory.SECURITY: "处理安全认证和加密操作",
            SemanticCategory.LOGGING: "记录日志和调试信息",
            SemanticCategory.CACHING: "缓存数据以提高性能",
            SemanticCategory.BUSINESS_LOGIC: "执行业务规则和流程",
            SemanticCategory.UTILITY: "提供通用的工具函数",
            SemanticCategory.CONFIGURATION: "管理和加载配置信息"
        }
        return purposes.get(category, "执行特定功能")

    def _infer_functionality(self, function_slice) -> str:
        """推断函数功能描述

        Args:
            function_slice: 函数切片

        Returns:
            str: 功能描述
        """
        func_name = getattr(function_slice, 'name', '')
        params = getattr(function_slice, 'parameters', [])
        calls = getattr(function_slice, 'calls', [])

        param_names = [p.get('name', '') for p in params]
        call_names = [c.get('name', '') for c in calls[:5]]

        functionality_parts = [f"函数名: {func_name}"]

        if param_names:
            functionality_parts.append(f"输入参数: {', '.join(param_names)}")

        if call_names:
            functionality_parts.append(f"调用其他函数: {', '.join(call_names)}")

        return "; ".join(functionality_parts)

    def _calculate_complexity(self, function_slice) -> FunctionComplexity:
        """计算函数复杂度

        Args:
            function_slice: 函数切片

        Returns:
            FunctionComplexity: 复杂度等级
        """
        source_code = getattr(function_slice, 'source_code', '')

        if_stmt_count = source_code.count('if') + source_code.count('elif')
        loop_count = source_code.count('for') + source_code.count('while')
        try_count = source_code.count('try')

        branch_count = if_stmt_count + 1
        cyclomatic_complexity = branch_count + loop_count * 2 + try_count

        lines = len(source_code.split('\n'))

        if cyclomatic_complexity <= 3 and lines <= 10:
            return FunctionComplexity.TRIVIAL
        elif cyclomatic_complexity <= 5 and lines <= 20:
            return FunctionComplexity.SIMPLE
        elif cyclomatic_complexity <= 10 and lines <= 50:
            return FunctionComplexity.MODERATE
        elif cyclomatic_complexity <= 20 and lines <= 100:
            return FunctionComplexity.COMPLEX
        else:
            return FunctionComplexity.VERY_COMPLEX

    def _classify_semantic(self, function_slice) -> SemanticCategory:
        """分类函数语义

        Args:
            function_slice: 函数切片

        Returns:
            SemanticCategory: 语义类别
        """
        func_name = getattr(function_slice, 'name', '').lower()
        source_code = getattr(function_slice, 'source_code', '').lower()

        best_match_category = SemanticCategory.UNKNOWN
        best_match_count = 0

        for category, keywords in self.keywords.items():
            match_count = 0
            for keyword in keywords:
                if keyword in func_name or keyword in source_code:
                    match_count += 1

            if match_count > best_match_count:
                best_match_count = match_count
                best_match_category = category

        return best_match_category

    def _analyze_parameters(self, function_slice) -> List[ParameterSemantic]:
        """分析参数语义

        Args:
            function_slice: 函数切片

        Returns:
            List[ParameterSemantic]: 参数语义列表
        """
        params = getattr(function_slice, 'parameters', [])
        param_semantics = []

        for param in params:
            param_semantic = ParameterSemantic(
                name=param.get('name', 'unknown'),
                data_type=param.get('annotation', 'Any'),
                optional=param.get('default_value') is not None,
                default_value=param.get('default_value')
            )

            param_semantic.constraints = self._infer_param_constraints(param)

            param_semantics.append(param_semantic)

        return param_semantics

    def _infer_param_constraints(self, param: Dict[str, Any]) -> List[str]:
        """推断参数约束

        Args:
            param: 参数信息

        Returns:
            List[str]: 约束列表
        """
        constraints = []
        param_name = param.get('name', '').lower()
        data_type = str(param.get('annotation', '')).lower()

        if 'id' in param_name:
            constraints.append("必须提供有效的标识符")

        if 'name' in param_name:
            constraints.append("非空字符串")

        if 'count' in param_name or 'size' in param_name:
            constraints.append("非负整数")

        if 'rate' in param_name or 'price' in param_name:
            constraints.append("正数")

        if 'email' in param_name:
            constraints.append("有效的邮箱格式")

        if 'url' in param_name or 'uri' in param_name:
            constraints.append("有效的URL格式")

        if 'date' in param_name:
            constraints.append("有效的日期格式")

        if data_type == 'bool':
            constraints.append("布尔值（True/False）")

        if data_type in ('int', 'float'):
            constraints.append("数值类型")

        return constraints

    def _analyze_return_value(self, function_slice) -> Dict[str, Any]:
        """分析返回值语义

        Args:
            function_slice: 函数切片

        Returns:
            Dict[str, Any]: 返回值语义
        """
        return_type = getattr(function_slice, 'return_type', None)

        return_semantic = {
            'type': return_type if return_type else 'Any',
            'meaning': '',
            'nullable': True,
            'collection': False
        }

        source_code = getattr(function_slice, 'source_code', '')
        if 'return None' in source_code:
            return_semantic['meaning'] = '无返回值'
        elif 'return True' in source_code or 'return False' in source_code:
            return_semantic['meaning'] = '布尔值结果'
            return_semantic['nullable'] = False
        elif 'return' in source_code:
            return_semantic['meaning'] = '函数执行结果'
            return_semantic['nullable'] = 'return None' in source_code

        if 'list' in str(return_type).lower() or '[]' in str(return_type):
            return_semantic['collection'] = True
            return_semantic['meaning'] = '列表类型的结果集合'

        return return_semantic

    def _analyze_side_effects(self, function_slice) -> Set[SideEffectType]:
        """分析副作用

        Args:
            function_slice: 函数切片

        Returns:
            Set[SideEffectType]: 副作用类型集合
        """
        side_effects = set()
        calls = getattr(function_slice, 'calls', [])
        source_code = getattr(function_slice, 'source_code', '').lower()

        call_names = [c.get('name', '').lower() for c in calls]

        io_keywords = ['open', 'read', 'write', 'close', 'file', 'io']
        if any(keyword in ' '.join(call_names) or keyword in source_code for keyword in io_keywords):
            side_effects.add(SideEffectType.FILE_IO)

        network_keywords = ['request', 'fetch', 'http', 'api', 'client', 'url', 'socket']
        if any(keyword in ' '.join(call_names) or keyword in source_code for keyword in network_keywords):
            side_effects.add(SideEffectType.NETWORK)

        db_keywords = ['query', 'insert', 'update', 'delete', 'commit', 'rollback', 'sql', 'database', 'db']
        if any(keyword in ' '.join(call_names) or keyword in source_code for keyword in db_keywords):
            side_effects.add(SideEffectType.DATABASE)

        random_keywords = ['random', 'uuid', 'time', 'timestamp']
        if any(keyword in ' '.join(call_names) for keyword in random_keywords):
            side_effects.add(SideEffectType.RANDOM)

        print_keywords = ['print', 'log', 'debug', 'info', 'warn', 'error']
        if any(keyword in ' '.join(call_names) or keyword in source_code for keyword in print_keywords):
            side_effects.add(SideEffectType.PRINT)

        global_keywords = ['global', '_variable', 'GLOBAL']
        if any(keyword in source_code for keyword in global_keywords):
            side_effects.add(SideEffectType.GLOBAL_STATE)

        if not side_effects:
            side_effects.add(SideEffectType.NONE)

        return side_effects

    def _analyze_exceptions(self, function_slice) -> List[Dict[str, str]]:
        """分析异常

        Args:
            function_slice: 函数切片

        Returns:
            List[Dict[str, str]]: 异常列表
        """
        exceptions = []
        source_code = getattr(function_slice, 'source_code', '')

        if 'try' in source_code and 'except' in source_code:
            exception_types = ['Exception', 'ValueError', 'TypeError', 'RuntimeError', 'KeyError', 'IndexError']
            for exc_type in exception_types:
                if exc_type in source_code:
                    exceptions.append({
                        'type': exc_type,
                        'description': f'处理{self._get_exception_description(exc_type)}'
                    })

        return exceptions

    def _get_exception_description(self, exc_type: str) -> str:
        """获取异常描述

        Args:
            exc_type: 异常类型

        Returns:
            str: 异常描述
        """
        descriptions = {
            'ValueError': '无效的值参数',
            'TypeError': '类型不匹配',
            'RuntimeError': '运行时错误',
            'KeyError': '字典键不存在',
            'IndexError': '索引超出范围',
            'Exception': '一般性异常'
        }
        return descriptions.get(exc_type, '未知异常')

    def _infer_business_domain(self, function_slice) -> str:
        """推断业务领域

        Args:
            function_slice: 函数切片

        Returns:
            str: 业务领域
        """
        source_code = getattr(function_slice, 'source_code', '').lower()

        domain_patterns = {
            '电子商务': ['order', 'product', 'cart', 'checkout', 'payment', 'invoice', 'shipping'],
            '用户管理': ['user', 'account', 'login', 'register', 'profile', 'permission', 'role'],
            '数据分析': ['analytics', 'report', 'metric', 'dashboard', 'chart', 'visualization'],
            '文件处理': ['upload', 'download', 'file', 'document', 'attachment', 'storage'],
            '通信服务': ['message', 'notification', 'email', 'sms', 'chat', 'websocket'],
            '支付系统': ['transaction', 'payment', 'refund', 'balance', 'wallet', 'card'],
            '社交网络': ['friend', 'follow', 'post', 'comment', 'like', 'share'],
            '系统管理': ['config', 'setting', 'monitor', 'health', 'status', 'metric']
        }

        for domain, keywords in domain_patterns.items():
            if any(keyword in source_code for keyword in keywords):
                return domain

        return '通用业务'

    def _identify_algorithm_type(self, function_slice) -> str:
        """识别算法类型

        Args:
            function_slice: 函数切片

        Returns:
            str: 算法类型
        """
        source_code = getattr(function_slice, 'source_code', '').lower()

        if 'sort' in source_code:
            return '排序算法'
        elif 'search' in source_code or 'find' in source_code:
            return '搜索算法'
        elif 'binary' in source_code:
            return '二分查找'
        elif 'recursiv' in source_code:
            return '递归算法'
        elif 'loop' in source_code or 'iterate' in source_code:
            return '迭代算法'
        elif 'dynamic' in source_code or 'dp' in source_code:
            return '动态规划'
        elif 'graph' in source_code or 'node' in source_code:
            return '图算法'
        elif 'tree' in source_code:
            return '树结构操作'

        return '通用逻辑'

    def _describe_data_flow(self, function_slice) -> str:
        """描述数据流

        Args:
            function_slice: 函数切片

        Returns:
            str: 数据流描述
        """
        params = getattr(function_slice, 'parameters', [])
        calls = getattr(function_slice, 'calls', [])

        if not params:
            return '无输入参数'

        input_params = [p.get('name', '') for p in params]

        if calls:
            return f'输入({", ".join(input_params)}) -> 处理 -> 输出结果'
        else:
            return f'输入({", ".join(input_params)}) -> 简单处理 -> 输出'

    def _identify_control_flow_pattern(self, function_slice) -> str:
        """识别控制流模式

        Args:
            function_slice: 函数切片

        Returns:
            str: 控制流模式
        """
        source_code = getattr(function_slice, 'source_code', '')

        has_if = 'if ' in source_code or 'elif ' in source_code
        has_loop = 'for ' in source_code or 'while ' in source_code
        has_try = 'try:' in source_code
        has_recursion = getattr(function_slice, 'name', '') in source_code and 'def ' in source_code

        patterns = []

        if has_if:
            patterns.append('条件分支')
        if has_loop:
            patterns.append('循环')
        if has_try:
            patterns.append('异常处理')
        if has_recursion:
            patterns.append('递归')

        if not patterns:
            return '顺序执行'
        elif len(patterns) == 1:
            return patterns[0]
        else:
            return ' + '.join(patterns)

    def _extract_performance_hints(self, function_slice) -> Dict[str, Any]:
        """提取性能提示

        Args:
            function_slice: 函数切片

        Returns:
            Dict[str, Any]: 性能提示
        """
        hints = {
            'time_complexity': 'O(n)',
            'space_complexity': 'O(1)',
            'optimization_opportunities': []
        }

        source_code = getattr(function_slice, 'source_code', '')

        if source_code.count('for') > 1 or source_code.count('while') > 1:
            hints['time_complexity'] = 'O(n²)'
            hints['optimization_opportunities'].append('嵌套循环可能影响性能')

        if 'sort' in source_code:
            hints['time_complexity'] = 'O(n log n)'

        if 'list comprehension' in source_code or '[x for' in source_code:
            hints['optimization_opportunities'].append('列表推导式已优化')

        if 'cache' in source_code or 'memo' in source_code:
            hints['optimization_opportunities'].append('已使用缓存优化')

        return hints

    def _evaluate_testability(self, function_slice) -> float:
        """评估可测试性

        Args:
            function_slice: 函数切片

        Returns:
            float: 可测试性评分（0-10）
        """
        score = 10.0

        source_code = getattr(function_slice, 'source_code', '')

        side_effects = self._analyze_side_effects(function_slice)
        if SideEffectType.NETWORK in side_effects:
            score -= 2.0
        if SideEffectType.DATABASE in side_effects:
            score -= 1.5
        if SideEffectType.FILE_IO in side_effects:
            score -= 1.0

        if hasattr(function_slice, 'is_async') and getattr(function_slice, 'is_async', False):
            score -= 1.0

        complexity = self._calculate_complexity(function_slice)
        if complexity == FunctionComplexity.COMPLEX:
            score -= 2.0
        elif complexity == FunctionComplexity.VERY_COMPLEX:
            score -= 3.0

        if 'random' in source_code.lower():
            score -= 1.0

        if hasattr(function_slice, 'parameters'):
            param_count = len(getattr(function_slice, 'parameters', []))
            if param_count > 5:
                score -= 0.5

        return max(0.0, min(10.0, score))

    def _generate_test_guidance(self, function_slice, semantic: FunctionSemantic) -> str:
        """生成测试指导

        Args:
            function_slice: 函数切片
            semantic: 函数语义

        Returns:
            str: 测试指导
        """
        guidance_parts = []

        guidance_parts.append(f"测试目标: {semantic.purpose}")

        if semantic.parameters:
            guidance_parts.append("\n测试要点:")
            for param in semantic.parameters:
                guidance_parts.append(f"- 参数'{param.name}': {', '.join(param.constraints) if param.constraints else '验证基本类型'}")

        guidance_parts.append(f"\n预期复杂度: {semantic.complexity.name}")

        if semantic.side_effects and SideEffectType.NONE not in semantic.side_effects:
            guidance_parts.append(f"\n需要Mock: {', '.join([e.name for e in semantic.side_effects if e != SideEffectType.NONE])}")

        guidance_parts.append(f"\n建议边界测试数量: {self._suggest_test_count(semantic)}")

        return '\n'.join(guidance_parts)

    def _suggest_test_count(self, semantic: FunctionSemantic) -> int:
        """建议测试数量

        Args:
            semantic: 函数语义

        Returns:
            int: 建议的测试数量
        """
        base_count = 3

        if semantic.complexity == FunctionComplexity.TRIVIAL:
            return 1
        elif semantic.complexity == FunctionComplexity.SIMPLE:
            return 2
        elif semantic.complexity == FunctionComplexity.MODERATE:
            return 4
        elif semantic.complexity == FunctionComplexity.COMPLEX:
            return 6
        else:
            return 8

    def _infer_preconditions(self, function_slice) -> List[str]:
        """推断前置条件

        Args:
            function_slice: 函数切片

        Returns:
            List[str]: 前置条件列表
        """
        preconditions = []
        params = getattr(function_slice, 'parameters', [])

        for param in params:
            param_name = param.get('name', '')
            constraints = self._infer_param_constraints(param)

            for constraint in constraints:
                preconditions.append(f"{param_name}: {constraint}")

        return preconditions if preconditions else ["输入参数必须符合函数签名"]

    def _infer_postconditions(self, function_slice) -> List[str]:
        """推断后置条件

        Args:
            function_slice: 函数切片

        Returns:
            List[str]: 后置条件列表
        """
        return_semantic = self._analyze_return_value(function_slice)

        postconditions = []

        if return_semantic['meaning']:
            postconditions.append(f"返回值: {return_semantic['meaning']}")

        if not return_semantic['nullable']:
            postconditions.append("返回值不应为None")

        if return_semantic['collection']:
            postconditions.append("返回集合类型")

        return postconditions if postconditions else ["函数正常执行完成"]

    def _identify_invariants(self, function_slice) -> List[str]:
        """识别不变式

        Args:
            function_slice: 函数切片

        Returns:
            List[str]: 不变式列表
        """
        invariants = []
        source_code = getattr(function_slice, 'source_code', '')

        if 'assert' in source_code:
            invariants.append("断言条件保持为真")

        if 'lock' in source_code.lower() or 'mutex' in source_code.lower():
            invariants.append("并发访问的互斥性")

        return invariants if invariants else ["函数执行过程中保持数据一致性"]

    def _generate_examples(self, function_slice) -> List[str]:
        """生成使用示例

        Args:
            function_slice: 函数切片

        Returns:
            List[str]: 示例列表
        """
        func_name = getattr(function_slice, 'name', 'unknown')
        params = getattr(function_slice, 'parameters', [])

        examples = []

        if params:
            example_args = []
            for param in params[:3]:
                param_name = param.get('name', '')
                example_args.append(f"{param_name}=None")

            examples.append(f"{func_name}({', '.join(example_args)})")

        examples.append(f"# 调用{func_name}执行{semantic.purpose if hasattr(self, 'semantic') else '操作'}")

        return examples

    def _get_statistics(self) -> Dict[str, Any]:
        """获取统计信息

        Returns:
            Dict[str, Any]: 统计信息
        """
        if not self.semantic_results:
            return {}

        stats = {
            'total_functions': len(self.semantic_results),
            'by_category': {},
            'by_complexity': {},
            'pure_functions': 0,
            'with_side_effects': 0,
            'average_testability': 0.0,
            'total_exceptions': 0
        }

        total_testability = 0.0

        for semantic in self.semantic_results:
            category_name = semantic.semantic_category.name
            stats['by_category'][category_name] = stats['by_category'].get(category_name, 0) + 1

            complexity_name = semantic.complexity.name
            stats['by_complexity'][complexity_name] = stats['by_complexity'].get(complexity_name, 0) + 1

            if semantic.is_pure_function():
                stats['pure_functions'] += 1
            else:
                stats['with_side_effects'] += 1

            total_testability += semantic.testability_score
            stats['total_exceptions'] += len(semantic.exceptions)

        if self.semantic_results:
            stats['average_testability'] = total_testability / len(self.semantic_results)

        return stats

    def get_semantic_by_function_id(self, function_id: str) -> Optional[FunctionSemantic]:
        """根据函数ID获取语义

        Args:
            function_id: 函数ID

        Returns:
            Optional[FunctionSemantic]: 找到的语义对象
        """
        for semantic in self.semantic_results:
            if semantic.function_id == function_id:
                return semantic
        return None

    def get_functions_by_category(self, category: SemanticCategory) -> List[FunctionSemantic]:
        """根据类别获取函数

        Args:
            category: 语义类别

        Returns:
            List[FunctionSemantic]: 匹配的函数列表
        """
        return [s for s in self.semantic_results if s.semantic_category == category]

    def get_impure_functions(self) -> List[FunctionSemantic]:
        """获取所有非纯函数

        Returns:
            List[FunctionSemantic]: 非纯函数列表
        """
        return [s for s in self.semantic_results if not s.is_pure_function()]

    def get_hard_to_test_functions(self) -> List[FunctionSemantic]:
        """获取难以测试的函数

        Returns:
            List[FunctionSemantic]: 可测试性评分低于5的函数列表
        """
        return [s for s in self.semantic_results if s.testability_score < 5.0]
