"""
Layer 18: LightASTLayer - 轻量AST构建层

本层负责将Token序列转换为轻量级的抽象语法树（AST），为后续的代码分析和切片提供结构化的语法表示。
相比完整的AST，本层专注于函数、类、控制流等核心结构的提取。
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum, auto
import ast


class ASTNodeType(Enum):
    """AST节点类型枚举"""
    MODULE = auto()
    FUNCTION_DEF = auto()
    CLASS_DEF = auto()
    IF_STATEMENT = auto()
    ELIF_CLAUSE = auto()
    ELSE_CLAUSE = auto()
    FOR_LOOP = auto()
    WHILE_LOOP = auto()
    TRY_STATEMENT = auto()
    EXCEPT_CLAUSE = auto()
    FINALLY_CLAUSE = auto()
    WITH_STATEMENT = auto()
    RETURN_STATEMENT = auto()
    YIELD_STATEMENT = auto()
    RAISE_STATEMENT = auto()
    ASSIGN_STATEMENT = auto()
    AUG_ASSIGN = auto()
    EXPR_STATEMENT = auto()
    CALL_EXPR = auto()
    BINARY_OP = auto()
    UNARY_OP = auto()
    COMPARE_OP = auto()
    BOOL_OP = auto()
    IF_EXPR = auto()
    LAMBDA_EXPR = auto()
    LIST_COMP = auto()
    DICT_COMP = auto()
    SET_COMP = auto()
    GENERATOR_EXPR = auto()
    SUBSCRIPT = auto()
    SLICE = auto()
    ATTRIBUTE = auto()
    NAME = auto()
    CONSTANT = auto()
    TUPLE = auto()
    LIST = auto()
    DICT = auto()
    SET = auto()
    ARGUMENTS = auto()
    ARG = auto()
    IMPORT = auto()
    IMPORT_FROM = auto()
    ANN_ASSIGN = auto()
    PASS = auto()
    BREAK = auto()
    CONTINUE = auto()
    ASSERT = auto()
    DELETE = auto()
    GLOBAL = auto()
    NONLOCAL = auto()
    AWAIT = auto()
    ASYNC_FOR = auto()
    ASYNC_WITH = auto()
    DECORATOR = auto()
    UNKNOWN = auto()


@dataclass
class ASTNode:
    """AST节点数据结构

    Attributes:
        node_type: 节点类型
        name: 节点名称（如函数名、类名）
        line: 起始行号
        column: 起始列号
        end_line: 结束行号
        end_column: 结束列号
        children: 子节点列表
        value: 节点值（用于字面量）
        metadata: 元数据字典
        parent: 父节点引用
    """
    node_type: ASTNodeType
    name: str = ""
    line: int = 0
    column: int = 0
    end_line: int = 0
    end_column: int = 0
    children: List['ASTNode'] = field(default_factory=list)
    value: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    parent: Optional['ASTNode'] = None

    def add_child(self, child: 'ASTNode'):
        """添加子节点

        Args:
            child: 子节点
        """
        child.parent = self
        self.children.append(child)

    def find_children(self, node_type: ASTNodeType) -> List['ASTNode']:
        """查找指定类型的子节点

        Args:
            node_type: 目标节点类型

        Returns:
            List[ASTNode]: 匹配的子节点列表
        """
        result = []
        for child in self.children:
            if child.node_type == node_type:
                result.append(child)
            result.extend(child.find_children(node_type))
        return result

    def get_source_segment(self, source_lines: List[str]) -> str:
        """获取节点对应的源代码片段

        Args:
            source_lines: 源代码行列表

        Returns:
            str: 源代码片段
        """
        if 0 < self.line <= len(source_lines):
            if self.line == self.end_line:
                return source_lines[self.line - 1][self.column:self.end_column]
            else:
                lines = [source_lines[self.line - 1][self.column:]]
                for i in range(self.line, self.end_line):
                    if 0 < i < len(source_lines):
                        lines.append(source_lines[i])
                if 0 < self.end_line <= len(source_lines):
                    lines.append(source_lines[self.end_line - 1][:self.end_column])
                return '\n'.join(lines)
        return ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "node_type": self.node_type.name,
            "name": self.name,
            "line": self.line,
            "column": self.column,
            "end_line": self.end_line,
            "end_column": self.end_column,
            "value": self.value,
            "metadata": self.metadata,
            "children": [child.to_dict() for child in self.children]
        }

    def get_function_definitions(self) -> List['ASTNode']:
        """获取所有函数定义节点

        Returns:
            List[ASTNode]: 函数定义节点列表
        """
        return self.find_children(ASTNodeType.FUNCTION_DEF)

    def get_class_definitions(self) -> List['ASTNode']:
        """获取所有类定义节点

        Returns:
            List[ASTNode]: 类定义节点列表
        """
        return self.find_children(ASTNodeType.CLASS_DEF)


class LightASTLayer:
    """轻量AST构建层

    功能描述：
        - 将Token序列转换为轻量级的抽象语法树（AST）
        - 提取函数、类、控制流等核心语法结构
        - 保留代码位置信息用于追踪
        - 支持Python等语言的AST构建
        - 可选择使用Python内置ast模块进行解析

    输入类型：
        - Token序列（List[Token]）或源代码字符串

    输出类型：
        - ASTNode对象，表示语法树的根节点
        - 包含完整的语法结构信息

    使用场景：
        - 为函数切片层提供结构化的语法信息
        - 支持代码搜索、重构和分析
        - 为控制流分析提供基础

    V3.1升级点：
        - 支持使用Python标准库ast模块进行准确解析
        - 增强对复杂表达式和推导式的支持
        - 提供更丰富的节点类型和元信息
    """

    description: str = "轻量AST构建层 - 将Token序列或源代码转换为语法树"
    input_type: str = "List[Token]或源代码字符串"
    output_type: str = "ASTNode - 语法树根节点"

    def __init__(self):
        """初始化AST构建层"""
        self.use_builtin_ast = True
        self.current_source = ""
        self.source_lines = []
        self.root_node: Optional[ASTNode] = None

    def set_options(self, use_builtin_ast: bool = True):
        """设置AST构建选项

        Args:
            use_builtin_ast: 是否优先使用Python内置ast模块
        """
        self.use_builtin_ast = use_builtin_ast

    def process(self, context) -> ASTNode:
        """处理Token序列或源代码，构建AST

        Args:
            context: PipelineContext对象，包含Token序列或源代码

        Returns:
            ASTNode: AST根节点，包含完整的语法树结构

        Raises:
            ValueError: 当输入为空或格式错误时
            SyntaxError: 当源代码存在语法错误时
        """
        tokens = None
        source = None

        if context.has('lexer_tokens'):
            tokens = context.get('lexer_tokens')

        if context.has('source'):
            source = context.get('source')

        if context.has('preprocessed_source'):
            source = context.get('preprocessed_source')

        if isinstance(source, list):
            self.source_lines = source
            self.current_source = '\n'.join(source)
        elif isinstance(source, str):
            self.current_source = source
            self.source_lines = source.split('\n')
        else:
            if tokens:
                self.current_source = self._reconstruct_source(tokens)
                self.source_lines = self.current_source.split('\n')
            else:
                raise ValueError("LightASTLayer: 无法获取源代码或Token序列")

        if self.use_builtin_ast:
            try:
                self.root_node = self._build_from_builtin_ast()
            except Exception as e:
                self.root_node = self._build_from_tokens(tokens if tokens else [])
        else:
            self.root_node = self._build_from_tokens(tokens if tokens else [])

        context.set('ast_root', self.root_node)
        context.set('ast_statistics', self._get_ast_statistics())

        return self.root_node

    def _reconstruct_source(self, tokens: List[Any]) -> str:
        """从Token序列重构源代码

        Args:
            tokens: Token序列

        Returns:
            str: 重构的源代码
        """
        source_parts = []
        for token in tokens:
            if hasattr(token, 'value'):
                source_parts.append(token.value)
            elif isinstance(token, dict) and 'value' in token:
                source_parts.append(token['value'])
        return ''.join(source_parts)

    def _build_from_builtin_ast(self) -> ASTNode:
        """使用Python内置ast模块构建AST

        Returns:
            ASTNode: AST根节点
        """
        try:
            tree = ast.parse(self.current_source)
            return self._convert_ast_node(tree)
        except SyntaxError as e:
            raise SyntaxError(f"源代码语法错误: {e}")

    def _convert_ast_node(self, node: ast.AST) -> ASTNode:
        """将ast.AST节点转换为自定义ASTNode

        Args:
            node: Python ast模块的节点

        Returns:
            ASTNode: 转换后的节点
        """
        node_type_map = {
            ast.Module: ASTNodeType.MODULE,
            ast.FunctionDef: ASTNodeType.FUNCTION_DEF,
            ast.AsyncFunctionDef: ASTNodeType.FUNCTION_DEF,
            ast.ClassDef: ASTNodeType.CLASS_DEF,
            ast.If: ASTNodeType.IF_STATEMENT,
            ast.For: ASTNodeType.FOR_LOOP,
            ast.AsyncFor: ASTNodeType.ASYNC_FOR,
            ast.While: ASTNodeType.WHILE_LOOP,
            ast.Try: ASTNodeType.TRY_STATEMENT,
            ast.With: ASTNodeType.WITH_STATEMENT,
            ast.AsyncWith: ASTNodeType.ASYNC_WITH,
            ast.Return: ASTNodeType.RETURN_STATEMENT,
            ast.Yield: ASTNodeType.YIELD_STATEMENT,
            ast.YieldFrom: ASTNodeType.YIELD_STATEMENT,
            ast.Raise: ASTNodeType.RAISE_STATEMENT,
            ast.Assign: ASTNodeType.ASSIGN_STATEMENT,
            ast.AugAssign: ASTNodeType.AUG_ASSIGN,
            ast.AnnAssign: ASTNodeType.ANN_ASSIGN,
            ast.Expr: ASTNodeType.EXPR_STATEMENT,
            ast.Call: ASTNodeType.CALL_EXPR,
            ast.BinOp: ASTNodeType.BINARY_OP,
            ast.UnaryOp: ASTNodeType.UNARY_OP,
            ast.Compare: ASTNodeType.COMPARE_OP,
            ast.BoolOp: ASTNodeType.BOOL_OP,
            ast.IfExp: ASTNodeType.IF_EXPR,
            ast.Lambda: ASTNodeType.LAMBDA_EXPR,
            ast.ListComp: ASTNodeType.LIST_COMP,
            ast.DictComp: ASTNodeType.DICT_COMP,
            ast.SetComp: ASTNodeType.SET_COMP,
            ast.GeneratorExp: ASTNodeType.GENERATOR_EXPR,
            ast.Subscript: ASTNodeType.SUBSCRIPT,
            ast.Slice: ASTNodeType.SLICE,
            ast.Attribute: ASTNodeType.ATTRIBUTE,
            ast.Name: ASTNodeType.NAME,
            ast.Constant: ASTNodeType.CONSTANT,
            ast.Tuple: ASTNodeType.TUPLE,
            ast.List: ASTNodeType.LIST,
            ast.Dict: ASTNodeType.DICT,
            ast.Set: ASTNodeType.SET,
            ast.arguments: ASTNodeType.ARGUMENTS,
            ast.arg: ASTNodeType.ARG,
            ast.Import: ASTNodeType.IMPORT,
            ast.ImportFrom: ASTNodeType.IMPORT_FROM,
            ast.Pass: ASTNodeType.PASS,
            ast.Break: ASTNodeType.BREAK,
            ast.Continue: ASTNodeType.CONTINUE,
            ast.Assert: ASTNodeType.ASSERT,
            ast.Delete: ASTNodeType.DELETE,
            ast.Global: ASTNodeType.GLOBAL,
            ast.Nonlocal: ASTNodeType.NONLOCAL,
            ast.Await: ASTNodeType.AWAIT,
            ast.Decorator: ASTNodeType.DECORATOR,
            ast.comprehension: ASTNodeType.UNKNOWN,
            ast.withitem: ASTNodeType.UNKNOWN,
        }

        ast_node_type = type(node)
        node_type = node_type_map.get(ast_node_type, ASTNodeType.UNKNOWN)

        line = getattr(node, 'lineno', 1)
        col = getattr(node, 'col_offset', 0)
        end_line = getattr(node, 'end_lineno', line)
        end_col = getattr(node, 'end_col_offset', col)

        name = ""
        value = None
        metadata = {}

        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            name = node.name
            metadata['is_async'] = isinstance(node, ast.AsyncFunctionDef)
            metadata['decorators'] = [ast.unparse(d) for d in getattr(node, 'decorator_list', [])]
            metadata['returns'] = ast.unparse(node.returns) if node.returns else None
            metadata['args'] = [(arg.arg, ast.unparse(arg.annotation) if arg.annotation else None) for arg in node.args.args]
        elif isinstance(node, ast.ClassDef):
            name = node.name
            metadata['bases'] = [ast.unparse(base) for base in node.bases]
            metadata['decorators'] = [ast.unparse(d) for d in getattr(node, 'decorator_list', [])]
        elif isinstance(node, ast.Constant):
            value = node.value
        elif isinstance(node, ast.Name):
            name = node.id
        elif isinstance(node, ast.BinOp):
            metadata['op'] = type(node.op).__name__
        elif isinstance(node, ast.UnaryOp):
            metadata['op'] = type(node.op).__name__
        elif isinstance(node, ast.BoolOp):
            metadata['op'] = type(node.op).__name__
        elif isinstance(node, ast.Compare):
            metadata['ops'] = [type(op).__name__ for op in node.ops]
        elif isinstance(node, ast.Call):
            metadata['func'] = ast.unparse(node.func) if hasattr(ast, 'unparse') else ""
        elif isinstance(node, ast.Attribute):
            name = node.attr
            metadata['value'] = ast.unparse(node.value) if hasattr(ast, 'unparse') else ""
        elif isinstance(node, ast.Subscript):
            metadata['slice'] = ast.unparse(node.slice) if hasattr(ast, 'unparse') else ""
        elif isinstance(node, ast.arg):
            name = node.arg
            metadata['annotation'] = ast.unparse(node.annotation) if node.annotation else None
        elif isinstance(node, ast.arguments):
            metadata['defaults'] = [ast.unparse(d) for d in node.defaults] if hasattr(ast, 'unparse') else []

        ast_node = ASTNode(
            node_type=node_type,
            name=name,
            line=line,
            column=col,
            end_line=end_line,
            end_column=end_col,
            value=value,
            metadata=metadata
        )

        for child in ast.iter_child_nodes(node):
            child_node = self._convert_ast_node(child)
            ast_node.add_child(child_node)

        return ast_node

    def _build_from_tokens(self, tokens: List[Any]) -> ASTNode:
        """从Token序列构建AST（轻量级实现）

        Args:
            tokens: Token序列

        Returns:
            ASTNode: AST根节点
        """
        root = ASTNode(
            node_type=ASTNodeType.MODULE,
            name="module",
            line=1,
            column=0,
            end_line=len(self.source_lines),
            end_column=0
        )

        current_function = None
        current_class = None
        current_block = root
        block_stack = [root]

        token_list = []
        if hasattr(tokens, '__iter__'):
            token_list = list(tokens)

        i = 0
        while i < len(token_list):
            token = token_list[i]

            if not hasattr(token, 'type'):
                i += 1
                continue

            if hasattr(token, 'value'):
                value = token.value
            else:
                value = ""

            if hasattr(token, 'line'):
                line = token.line
            else:
                line = 1

            if hasattr(token, 'column'):
                column = token.column
            else:
                column = 0

            if value == 'def':
                func_node = ASTNode(
                    node_type=ASTNodeType.FUNCTION_DEF,
                    name="",
                    line=line,
                    column=column
                )

                if i + 1 < len(token_list):
                    next_token = token_list[i + 1]
                    func_node.name = getattr(next_token, 'value', '') if hasattr(next_token, 'value') else ""

                current_function = func_node
                block_stack[-1].add_child(func_node)
                block_stack.append(func_node)
                current_block = func_node

            elif value == 'class':
                class_node = ASTNode(
                    node_type=ASTNodeType.CLASS_DEF,
                    name="",
                    line=line,
                    column=column
                )

                if i + 1 < len(token_list):
                    next_token = token_list[i + 1]
                    class_node.name = getattr(next_token, 'value', '') if hasattr(next_token, 'value') else ""

                current_class = class_node
                block_stack[-1].add_child(class_node)
                block_stack.append(class_node)
                current_block = class_node

            elif value == 'if':
                if_node = ASTNode(
                    node_type=ASTNodeType.IF_STATEMENT,
                    line=line,
                    column=column
                )
                current_block.add_child(if_node)
                block_stack.append(if_node)
                current_block = if_node

            elif value == 'for':
                for_node = ASTNode(
                    node_type=ASTNodeType.FOR_LOOP,
                    line=line,
                    column=column
                )
                current_block.add_child(for_node)
                block_stack.append(for_node)
                current_block = for_node

            elif value == 'while':
                while_node = ASTNode(
                    node_type=ASTNodeType.WHILE_LOOP,
                    line=line,
                    column=column
                )
                current_block.add_child(while_node)
                block_stack.append(while_node)
                current_block = while_node

            elif value == 'try':
                try_node = ASTNode(
                    node_type=ASTNodeType.TRY_STATEMENT,
                    line=line,
                    column=column
                )
                current_block.add_child(try_node)
                block_stack.append(try_node)
                current_block = try_node

            elif value in ('elif', 'else'):
                if block_stack and block_stack[-1].node_type == ASTNodeType.IF_STATEMENT:
                    block_stack.pop()

                if value == 'elif':
                    elif_node = ASTNode(
                        node_type=ASTNodeType.ELIF_CLAUSE,
                        line=line,
                        column=column
                    )
                    if block_stack:
                        block_stack[-1].add_child(elif_node)
                    block_stack.append(elif_node)
                    current_block = elif_node

            elif value == 'except':
                except_node = ASTNode(
                    node_type=ASTNodeType.EXCEPT_CLAUSE,
                    line=line,
                    column=column
                )
                if block_stack:
                    block_stack[-1].add_child(except_node)
                block_stack.append(except_node)
                current_block = except_node

            elif value == 'finally':
                finally_node = ASTNode(
                    node_type=ASTNodeType.FINALLY_CLAUSE,
                    line=line,
                    column=column
                )
                if block_stack:
                    block_stack[-1].add_child(finally_node)
                block_stack.append(finally_node)
                current_block = finally_node

            elif value == 'with':
                with_node = ASTNode(
                    node_type=ASTNodeType.WITH_STATEMENT,
                    line=line,
                    column=column
                )
                current_block.add_child(with_node)
                block_stack.append(with_node)
                current_block = with_node

            elif value == 'return':
                return_node = ASTNode(
                    node_type=ASTNodeType.RETURN_STATEMENT,
                    line=line,
                    column=column
                )
                current_block.add_child(return_node)

            elif value == 'import' or value == 'from':
                import_node = ASTNode(
                    node_type=ASTNodeType.IMPORT if value == 'import' else ASTNodeType.IMPORT_FROM,
                    line=line,
                    column=column
                )
                current_block.add_child(import_node)

            elif value in ('}', ')', ']', ':'):
                if len(block_stack) > 1:
                    block_stack.pop()
                    current_block = block_stack[-1]

                if value == '}':
                    if current_function:
                        if block_stack and block_stack[-1] == current_function:
                            if len(block_stack) > 1:
                                block_stack.pop()
                                current_block = block_stack[-1]
                        if block_stack and block_stack[-1] == current_class:
                            if len(block_stack) > 1:
                                block_stack.pop()
                                current_block = block_stack[-1]
                        current_function = None

                    if current_class:
                        if block_stack and block_stack[-1] == current_class:
                            if len(block_stack) > 1:
                                block_stack.pop()
                                current_block = block_stack[-1]
                        current_class = None

            i += 1

        return root

    def _get_ast_statistics(self) -> Dict[str, Any]:
        """获取AST统计信息

        Returns:
            Dict[str, Any]: 统计信息
        """
        if not self.root_node:
            return {}

        return {
            'total_nodes': self._count_nodes(self.root_node),
            'function_count': len(self.root_node.get_function_definitions()),
            'class_count': len(self.root_node.get_class_definitions()),
            'max_depth': self._get_max_depth(self.root_node),
            'node_types': self._count_node_types(self.root_node)
        }

    def _count_nodes(self, node: ASTNode) -> int:
        """统计节点总数

        Args:
            node: 根节点

        Returns:
            int: 节点总数
        """
        count = 1
        for child in node.children:
            count += self._count_nodes(child)
        return count

    def _get_max_depth(self, node: ASTNode, depth: int = 0) -> int:
        """获取AST最大深度

        Args:
            node: 当前节点
            depth: 当前深度

        Returns:
            int: 最大深度
        """
        max_depth = depth
        for child in node.children:
            child_depth = self._get_max_depth(child, depth + 1)
            max_depth = max(max_depth, child_depth)
        return max_depth

    def _count_node_types(self, node: ASTNode) -> Dict[str, int]:
        """统计各类型节点数量

        Args:
            node: 根节点

        Returns:
            Dict[str, int]: 各类型节点数量
        """
        counts = {node.node_type.name: 1}
        for child in node.children:
            child_counts = self._count_node_types(child)
            for node_type, count in child_counts.items():
                counts[node_type] = counts.get(node_type, 0) + count
        return counts

    def get_function_nodes(self) -> List[ASTNode]:
        """获取所有函数定义节点

        Returns:
            List[ASTNode]: 函数节点列表
        """
        if self.root_node:
            return self.root_node.get_function_definitions()
        return []

    def get_class_nodes(self) -> List[ASTNode]:
        """获取所有类定义节点

        Returns:
            List[ASTNode]: 类节点列表
        """
        if self.root_node:
            return self.root_node.get_class_definitions()
        return []

    def find_node_at_position(self, line: int, column: int) -> Optional[ASTNode]:
        """查找指定位置的节点

        Args:
            line: 行号
            column: 列号

        Returns:
            Optional[ASTNode]: 找到的节点，未找到返回None
        """
        if not self.root_node:
            return None

        return self._find_node_recursive(self.root_node, line, column)

    def _find_node_recursive(self, node: ASTNode, line: int, column: int) -> Optional[ASTNode]:
        """递归查找节点

        Args:
            node: 当前节点
            line: 目标行号
            column: 目标列号

        Returns:
            Optional[ASTNode]: 找到的节点
        """
        if node.line <= line <= node.end_line:
            if node.line == line and node.column > column:
                return None
            if node.end_line == line and node.end_column < column:
                return None

            for child in node.children:
                result = self._find_node_recursive(child, line, column)
                if result:
                    return result

            return node

        return None
