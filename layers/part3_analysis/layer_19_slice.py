"""
Layer 19: FunctionSliceLayer - 函数单元切片层

本层负责将AST拆分为独立的函数单元，为后续的函数级语义分析和依赖分析做准备。
每个函数单元包含函数定义、函数体以及相关的元信息。
"""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum, auto
from path_test_system.layers.part3_analysis.layer_18_ast import ASTNodeType


class SliceType(Enum):
    """切片类型枚举"""
    FUNCTION = auto()
    CLASS_METHOD = auto()
    STATIC_METHOD = auto()
    CLASS_METHOD_V2 = auto()
    PROPERTY = auto()
    LAMBDA = auto()
    NESTED_FUNCTION = auto()
    MODULE_LEVEL = auto()


@dataclass
class FunctionSlice:
    """函数切片数据结构

    Attributes:
        slice_id: 切片唯一标识符
        slice_type: 切片类型
        name: 函数/方法名称
        qualified_name: 完全限定名称（包含类名）
        start_line: 起始行号
        end_line: 结束行号
        source_code: 源代码片段
        ast_root: AST根节点
        parameters: 参数列表
        decorators: 装饰器列表
        return_type: 返回类型注解
        is_async: 是否为异步函数
        is_generator: 是否为生成器函数
        local_functions: 嵌套函数列表
        captured_variables: 闭包捕获的变量
        global_variables: 使用的全局变量
        calls: 函数调用列表
        class_name: 所属类名（如果是方法）
        file_path: 源文件路径
        metadata: 其他元信息
    """
    slice_id: str
    slice_type: SliceType
    name: str
    qualified_name: str = ""
    start_line: int = 0
    end_line: int = 0
    source_code: str = ""
    ast_root: Any = None
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)
    return_type: Optional[str] = None
    is_async: bool = False
    is_generator: bool = False
    local_functions: List[str] = field(default_factory=list)
    captured_variables: Set[str] = field(default_factory=set)
    global_variables: Set[str] = field(default_factory=set)
    calls: List[Dict[str, Any]] = field(default_factory=list)
    class_name: Optional[str] = None
    file_path: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_parameter_names(self) -> List[str]:
        """获取参数名称列表

        Returns:
            List[str]: 参数名称列表
        """
        return [param['name'] for param in self.parameters]

    def get_call_names(self) -> List[str]:
        """获取所有调用的函数名

        Returns:
            List[str]: 函数名列表
        """
        return [call['name'] for call in self.calls]

    def has_call(self, func_name: str) -> bool:
        """检查是否调用了指定函数

        Args:
            func_name: 函数名

        Returns:
            bool: 是否调用
        """
        return func_name in self.get_call_names()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "slice_id": self.slice_id,
            "slice_type": self.slice_type.name,
            "name": self.name,
            "qualified_name": self.qualified_name,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "source_code": self.source_code,
            "parameters": self.parameters,
            "decorators": self.decorators,
            "return_type": self.return_type,
            "is_async": self.is_async,
            "is_generator": self.is_generator,
            "local_functions": self.local_functions,
            "captured_variables": list(self.captured_variables),
            "global_variables": list(self.global_variables),
            "calls": self.calls,
            "class_name": self.class_name,
            "file_path": self.file_path,
            "metadata": self.metadata
        }

    def get_code_lines(self) -> List[str]:
        """获取代码行列表

        Returns:
            List[str]: 代码行列表
        """
        if self.source_code:
            return self.source_code.split('\n')
        return []

    def get_line_range(self) -> tuple:
        """获取行号范围

        Returns:
            tuple: (start_line, end_line)
        """
        return (self.start_line, self.end_line)


class FunctionSliceLayer:
    """函数单元切片层

    功能描述：
        - 将AST拆分为独立的函数单元切片
        - 识别函数、方法、嵌套函数等不同类型的可调用单元
        - 提取每个函数的元信息（参数、装饰器、返回值等）
        - 识别函数调用关系和变量依赖
        - 支持类方法和静态方法的特殊处理

    输入类型：
        - AST根节点（ASTNode）
        - 源代码（用于提取代码片段）

    输出类型：
        - List[FunctionSlice]: 函数切片列表

    使用场景：
        - 为函数语义分析提供独立的分析单元
        - 支持基于函数的代码搜索和重构
        - 为测试用例生成提供函数级别的上下文

    V3.1升级点：
        - 增强对嵌套函数的识别和处理
        - 支持装饰器的完整解析
        - 增加对闭包变量的追踪
        - 提供更精确的函数调用关系分析
    """

    description: str = "函数单元切片层 - 将AST拆分为独立的函数单元"
    input_type: str = "ASTNode - 语法树根节点和源代码"
    output_type: str = "List[FunctionSlice] - 函数切片列表"

    def __init__(self):
        """初始化函数切片层"""
        self.slices: List[FunctionSlice] = []
        self.source_lines: List[str] = []
        self.current_file_path: str = ""
        self.slice_counter: int = 0

    def process(self, context) -> List[FunctionSlice]:
        """处理AST，生成函数切片列表

        Args:
            context: PipelineContext对象，包含AST和源代码

        Returns:
            List[FunctionSlice]: 函数切片列表

        Raises:
            ValueError: 当AST为空或格式错误时
        """
        if not context.has('ast_root'):
            raise ValueError("FunctionSliceLayer: 缺少AST根节点")

        ast_root = context.get('ast_root')

        if context.has('source'):
            source = context.get('source')
            if isinstance(source, list):
                self.source_lines = source
            elif isinstance(source, str):
                self.source_lines = source.split('\n')
            else:
                self.source_lines = []

        if context.has('file_path'):
            self.current_file_path = context.get('file_path')

        self.slices = []
        self.slice_counter = 0

        self._extract_slices_recursive(ast_root, "")

        context.set('function_slices', self.slices)
        context.set('slice_count', len(self.slices))
        context.set('slice_statistics', self._get_statistics())

        return self.slices

    def _extract_slices_recursive(self, node: Any, class_context: str):
        """递归提取函数切片

        Args:
            node: AST节点
            class_context: 类上下文（如果有）
        """
        if not node:
            return

        node_type = getattr(node, 'node_type', None)
        if node_type:
            if node_type == ASTNodeType.FUNCTION_DEF:
                self._extract_function_slice(node, class_context)

            elif node_type == ASTNodeType.CLASS_DEF:
                new_class_context = class_context
                if hasattr(node, 'name') and node.name:
                    new_class_context = f"{class_context}.{node.name}" if class_context else node.name

                for child in getattr(node, 'children', []):
                    self._extract_slices_recursive(child, new_class_context)

        for child in getattr(node, 'children', []):
            self._extract_slices_recursive(child, class_context)

    def _extract_function_slice(self, func_node: Any, class_context: str):
        """提取单个函数切片

        Args:
            func_node: 函数定义节点
            class_context: 类上下文
        """

        self.slice_counter += 1
        func_name = getattr(func_node, 'name', f"anonymous_{self.slice_counter}")
        metadata = getattr(func_node, 'metadata', {})

        is_async = metadata.get('is_async', False)
        is_static = 'staticmethod' in metadata.get('decorators', [])
        is_classmethod = 'classmethod' in metadata.get('decorators', [])

        if class_context:
            if is_static or is_classmethod:
                slice_type = SliceType.CLASS_METHOD if is_classmethod else SliceType.STATIC_METHOD
                qualified_name = f"{class_context}.{func_name}"
            else:
                slice_type = SliceType.CLASS_METHOD_V2
                qualified_name = f"{class_context}.{func_name}"
        else:
            slice_type = SliceType.FUNCTION
            qualified_name = func_name

        start_line = getattr(func_node, 'line', 1)
        end_line = getattr(func_node, 'end_line', start_line)

        source_code = self._extract_source_code(start_line, end_line)

        parameters = []
        if 'args' in metadata:
            parameters = [
                {'name': arg[0], 'annotation': arg[1]}
                for arg in metadata['args']
            ]

        return_type = metadata.get('returns')

        calls = self._extract_function_calls(func_node)

        nested_functions = self._extract_nested_functions(func_node)

        captured_vars = self._extract_captured_variables(func_node)

        global_vars = self._extract_global_variables(func_node)

        function_slice = FunctionSlice(
            slice_id=f"slice_{self.slice_counter}",
            slice_type=slice_type,
            name=func_name,
            qualified_name=qualified_name,
            start_line=start_line,
            end_line=end_line,
            source_code=source_code,
            ast_root=func_node,
            parameters=parameters,
            decorators=metadata.get('decorators', []),
            return_type=return_type,
            is_async=is_async,
            is_generator=self._check_if_generator(func_node),
            local_functions=nested_functions,
            captured_variables=captured_vars,
            global_variables=global_vars,
            calls=calls,
            class_name=class_context if class_context else None,
            file_path=self.current_file_path,
            metadata={
                'is_static': is_static,
                'is_classmethod': is_classmethod,
                'arg_count': len(parameters)
            }
        )

        self.slices.append(function_slice)

    def _extract_source_code(self, start_line: int, end_line: int) -> str:
        """提取源代码片段

        Args:
            start_line: 起始行号
            end_line: 结束行号

        Returns:
            str: 源代码片段
        """
        if not self.source_lines:
            return ""

        lines = []
        for i in range(start_line - 1, min(end_line, len(self.source_lines))):
            if 0 <= i < len(self.source_lines):
                lines.append(self.source_lines[i])

        return '\n'.join(lines)

    def _extract_function_calls(self, func_node: Any) -> List[Dict[str, Any]]:
        """提取函数调用

        Args:
            func_node: 函数节点

        Returns:
            List[Dict[str, Any]]: 函数调用列表
        """

        calls = []

        def traverse(node):
            if not node:
                return

            node_type = getattr(node, 'node_type', None)
            if node_type == ASTNodeType.CALL_EXPR:
                func_name = getattr(node, 'name', '')
                if not func_name:
                    func_name = node.metadata.get('func', '')

                call_info = {
                    'name': func_name,
                    'line': getattr(node, 'line', 0),
                    'column': getattr(node, 'column', 0)
                }
                calls.append(call_info)

            for child in getattr(node, 'children', []):
                traverse(child)

        traverse(func_node)
        return calls

    def _extract_nested_functions(self, func_node: Any) -> List[str]:
        """提取嵌套函数

        Args:
            func_node: 函数节点

        Returns:
            List[str]: 嵌套函数名列表
        """

        nested_funcs = []

        def traverse(node):
            if not node:
                return

            node_type = getattr(node, 'node_type', None)
            if node_type == ASTNodeType.FUNCTION_DEF:
                func_name = getattr(node, 'name', '')
                if func_name:
                    nested_funcs.append(func_name)

            for child in getattr(node, 'children', []):
                traverse(child)

        for child in getattr(func_node, 'children', []):
            traverse(child)

        return nested_funcs

    def _extract_captured_variables(self, func_node: Any) -> Set[str]:
        """提取闭包捕获的变量

        Args:
            func_node: 函数节点

        Returns:
            Set[str]: 捕获的变量集合
        """
        captured = set()

        def traverse(node):
            if not node:
                return

            node_type = getattr(node, 'node_type', None)
            if node_type:
                if node_type == ASTNodeType.NONLOCAL:
                    metadata = getattr(node, 'metadata', {})
                    if 'names' in metadata:
                        captured.update(metadata['names'])

                if node_type == ASTNodeType.NAME:
                    name = getattr(node, 'name', '')
                    if name:
                        captured.add(name)

            for child in getattr(node, 'children', []):
                traverse(child)

        traverse(func_node)
        return captured

    def _extract_global_variables(self, func_node: Any) -> Set[str]:
        """提取全局变量使用

        Args:
            func_node: 函数节点

        Returns:
            Set[str]: 全局变量集合
        """
        global_vars = set()

        def traverse(node):
            if not node:
                return

            node_type = getattr(node, 'node_type', None)
            if node_type:
                if node_type == ASTNodeType.GLOBAL:
                    metadata = getattr(node, 'metadata', {})
                    if 'names' in metadata:
                        global_vars.update(metadata['names'])

            for child in getattr(node, 'children', []):
                traverse(child)

        traverse(func_node)
        return global_vars

    def _check_if_generator(self, func_node: Any) -> bool:
        """检查是否为生成器函数

        Args:
            func_node: 函数节点

        Returns:
            bool: 是否为生成器
        """

        def traverse(node):
            if not node:
                return False

            node_type = getattr(node, 'node_type', None)
            if node_type == ASTNodeType.YIELD_STATEMENT or node_type == ASTNodeType.YIELD:
                return True

            for child in getattr(node, 'children', []):
                if traverse(child):
                    return True

            return False

        for child in getattr(func_node, 'children', []):
            if traverse(child):
                return True

        return False

    def _get_statistics(self) -> Dict[str, Any]:
        """获取切片统计信息

        Returns:
            Dict[str, Any]: 统计信息
        """
        stats = {
            'total_slices': len(self.slices),
            'by_type': {},
            'async_functions': 0,
            'generator_functions': 0,
            'with_decorators': 0,
            'total_calls': 0
        }

        for slice_item in self.slices:
            type_name = slice_item.slice_type.name
            stats['by_type'][type_name] = stats['by_type'].get(type_name, 0) + 1

            if slice_item.is_async:
                stats['async_functions'] += 1

            if slice_item.is_generator:
                stats['generator_functions'] += 1

            if slice_item.decorators:
                stats['with_decorators'] += 1

            stats['total_calls'] += len(slice_item.calls)

        return stats

    def get_slice_by_name(self, name: str) -> Optional[FunctionSlice]:
        """根据名称获取切片

        Args:
            name: 函数名称或完全限定名称

        Returns:
            Optional[FunctionSlice]: 找到的切片
        """
        for slice_item in self.slices:
            if slice_item.name == name or slice_item.qualified_name == name:
                return slice_item
        return None

    def get_slices_by_class(self, class_name: str) -> List[FunctionSlice]:
        """根据类名获取所有方法切片

        Args:
            class_name: 类名

        Returns:
            List[FunctionSlice]: 方法切片列表
        """
        return [
            slice_item for slice_item in self.slices
            if slice_item.class_name == class_name
        ]

    def get_call_graph(self) -> Dict[str, List[str]]:
        """获取函数调用图

        Returns:
            Dict[str, List[str]]: 函数名到被调用函数列表的映射
        """
        call_graph = {}

        for slice_item in self.slices:
            called_funcs = slice_item.get_call_names()
            call_graph[slice_item.qualified_name] = called_funcs

        return call_graph

    def get_slice_dependencies(self, slice_item: FunctionSlice) -> Dict[str, List[str]]:
        """获取切片的依赖关系

        Args:
            slice_item: 函数切片

        Returns:
            Dict[str, List[str]]: 依赖关系字典
        """
        return {
            'calls': slice_item.get_call_names(),
            'captured': list(slice_item.captured_variables),
            'globals': list(slice_item.global_variables),
            'nested_functions': slice_item.local_functions
        }

    def filter_slices(self, predicate) -> List[FunctionSlice]:
        """根据条件过滤切片

        Args:
            predicate: 过滤函数

        Returns:
            List[FunctionSlice]: 过滤后的切片列表
        """
        return [s for s in self.slices if predicate(s)]

    def get_public_functions(self) -> List[FunctionSlice]:
        """获取公开函数（不以_开头）

        Returns:
            List[FunctionSlice]: 公开函数列表
        """
        return self.filter_slices(
            lambda s: not s.name.startswith('_') and s.slice_type in [
                SliceType.FUNCTION,
                SliceType.CLASS_METHOD_V2,
                SliceType.STATIC_METHOD,
                SliceType.CLASS_METHOD
            ]
        )

    def get_private_functions(self) -> List[FunctionSlice]:
        """获取私有函数（以_开头）

        Returns:
            List[FunctionSlice]: 私有函数列表
        """
        return self.filter_slices(
            lambda s: s.name.startswith('_') and s.slice_type in [
                SliceType.FUNCTION,
                SliceType.CLASS_METHOD_V2
            ]
        )
