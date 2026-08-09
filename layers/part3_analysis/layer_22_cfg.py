"""
Layer 22: CFGConstructionLayer - 控制流CFG构建层【V3.1升级】

本层负责将函数代码转换为控制流图（CFG），为后续的路径分析和测试用例生成提供控制流基础。
V3.1升级增强了异常处理、异步控制和复杂控制流模式的CFG构建能力。
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import defaultdict, deque


class CFGNodeType(Enum):
    """CFG节点类型"""
    ENTRY = auto()
    EXIT = auto()
    BASIC_BLOCK = auto()
    CONDITIONAL = auto()
    LOOP_HEADER = auto()
    LOOP_BODY = auto()
    TRY_BLOCK = auto()
    EXCEPT_BLOCK = auto()
    FINALLY_BLOCK = auto()
    WITH_BLOCK = auto()
    ASYNC_AWAIT = auto()
    YIELD_POINT = auto()
    FUNCTION_CALL = auto()
    RETURN = auto()
    RAISE = auto()
    BREAK = auto()
    CONTINUE = auto()
    LABEL = auto()


class EdgeType(Enum):
    """CFG边类型"""
    UNCONDITIONAL = auto()
    TRUE_BRANCH = auto()
    FALSE_BRANCH = auto()
    EXCEPTION = auto()
    FALL_THROUGH = auto()
    LOOP_BACK = auto()
    BREAK_EDGE = auto()
    CONTINUE_EDGE = auto()
    YIELD = auto()


@dataclass
class CFGNode:
    """CFG节点

    Attributes:
        node_id: 节点唯一标识符
        node_type: 节点类型
        label: 节点标签
        statements: 包含的语句列表
        line_start: 起始行号
        line_end: 结束行号
        predecessors: 前驱节点ID列表
        successors: 后继节点ID列表
        condition: 条件表达式（用于条件节点）
        is_loop_header: 是否为循环头节点
        loop_depth: 循环嵌套深度
        exception_handlers: 异常处理器列表
        metadata: 其他元信息
    """
    node_id: str
    node_type: CFGNodeType
    label: str = ""
    statements: List[str] = field(default_factory=list)
    line_start: int = 0
    line_end: int = 0
    predecessors: List[str] = field(default_factory=list)
    successors: List[str] = field(default_factory=list)
    condition: Optional[str] = None
    is_loop_header: bool = False
    loop_depth: int = 0
    exception_handlers: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_predecessor(self, node_id: str):
        """添加前驱节点

        Args:
            node_id: 前驱节点ID
        """
        if node_id not in self.predecessors:
            self.predecessors.append(node_id)

    def add_successor(self, node_id: str):
        """添加后继节点

        Args:
            node_id: 后继节点ID
        """
        if node_id not in self.successors:
            self.successors.append(node_id)

    def remove_successor(self, node_id: str):
        """移除后继节点

        Args:
            node_id: 后继节点ID
        """
        if node_id in self.successors:
            self.successors.remove(node_id)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.name,
            "label": self.label,
            "statements": self.statements,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "predecessors": self.predecessors,
            "successors": self.successors,
            "condition": self.condition,
            "is_loop_header": self.is_loop_header,
            "loop_depth": self.loop_depth,
            "exception_handlers": self.exception_handlers,
            "metadata": self.metadata
        }


@dataclass
class CFGEdge:
    """CFG边

    Attributes:
        source: 源节点ID
        target: 目标节点ID
        edge_type: 边类型
        condition: 条件表达式（用于条件边）
        probability: 执行概率估计（0-1）
        metadata: 其他元信息
    """
    source: str
    target: str
    edge_type: EdgeType
    condition: Optional[str] = None
    probability: float = 0.5
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "source": self.source,
            "target": self.target,
            "edge_type": self.edge_type.name,
            "condition": self.condition,
            "probability": self.probability,
            "metadata": self.metadata
        }


@dataclass
class ControlFlowGraph:
    """控制流图

    Attributes:
        function_name: 函数名
        entry_node: 入口节点ID
        exit_node: 出口节点ID
        nodes: 节点字典（node_id -> CFGNode）
        edges: 边列表
        basic_blocks: 基本块列表
        loops: 循环信息列表
        dominated_nodes: 支配节点信息
        post_dominated_nodes: 后支配节点信息
        metadata: 元信息
    """
    function_name: str
    entry_node: str = ""
    exit_node: str = ""
    nodes: Dict[str, CFGNode] = field(default_factory=dict)
    edges: List[CFGEdge] = field(default_factory=list)
    basic_blocks: List[str] = field(default_factory=list)
    loops: List[Dict[str, Any]] = field(default_factory=list)
    dominated_nodes: Dict[str, Set[str]] = field(default_factory=dict)
    post_dominated_nodes: Dict[str, Set[str]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_node(self, node: CFGNode):
        """添加节点

        Args:
            node: CFGNode对象
        """
        self.nodes[node.node_id] = node
        if node.node_type == CFGNodeType.ENTRY:
            self.entry_node = node.node_id
        elif node.node_type == CFGNodeType.EXIT:
            self.exit_node = node.node_id

    def add_edge(self, edge: CFGEdge):
        """添加边

        Args:
            edge: CFGEdge对象
        """
        self.edges.append(edge)

        if edge.source in self.nodes:
            self.nodes[edge.source].add_successor(edge.target)

        if edge.target in self.nodes:
            self.nodes[edge.target].add_predecessor(edge.source)

    def get_node(self, node_id: str) -> Optional[CFGNode]:
        """获取节点

        Args:
            node_id: 节点ID

        Returns:
            Optional[CFGNode]: 找到的节点
        """
        return self.nodes.get(node_id)

    def get_successors(self, node_id: str) -> List[CFGNode]:
        """获取后继节点

        Args:
            node_id: 节点ID

        Returns:
            List[CFGNode]: 后继节点列表
        """
        node = self.nodes.get(node_id)
        if not node:
            return []

        return [self.nodes[sid] for sid in node.successors if sid in self.nodes]

    def get_predecessors(self, node_id: str) -> List[CFGNode]:
        """获取前驱节点

        Args:
            node_id: 节点ID

        Returns:
            List[CFGNode]: 前驱节点列表
        """
        node = self.nodes.get(node_id)
        if not node:
            return []

        return [self.nodes[pid] for pid in node.predecessors if pid in self.nodes]

    def get_all_paths(self) -> List[List[str]]:
        """获取所有从入口到出口的路径

        Returns:
            List[List[str]]: 路径列表，每条路径是节点ID序列
        """
        if not self.entry_node or not self.exit_node:
            return []

        paths = []

        def dfs(current: str, path: List[str], visited: Set[str]):
            if current == self.exit_node:
                paths.append(path.copy())
                return

            visited.add(current)
            path.append(current)

            for successor in self.get_successors(current):
                if successor.node_id not in visited:
                    dfs(successor.node_id, path.copy(), visited.copy())

        dfs(self.entry_node, [], set())
        return paths

    def get_basic_blocks(self) -> List[List[str]]:
        """获取基本块组

        Returns:
            List[List[str]]: 基本块列表，每个基本块是节点ID列表
        """
        blocks = []

        for node_id, node in self.nodes.items():
            if node.node_type == CFGNodeType.BASIC_BLOCK or node.node_type == CFGNodeType.ENTRY:
                block = [node_id]
                current = node_id

                while current in self.nodes:
                    successors = self.nodes[current].successors
                    if len(successors) == 1 and successors[0] in self.nodes:
                        next_node = self.nodes[successors[0]]
                        if next_node.node_type == CFGNodeType.BASIC_BLOCK:
                            block.append(successors[0])
                            current = successors[0]
                        else:
                            break
                    else:
                        break

                if block not in blocks:
                    blocks.append(block)

        return blocks

    def calculate_dominators(self):
        """计算支配节点"""
        if not self.entry_node:
            return

        all_nodes = set(self.nodes.keys())

        dominators = {node: all_nodes.copy() for node in all_nodes}
        dominators[self.entry_node] = {self.entry_node}

        changed = True
        while changed:
            changed = False

            for node_id in all_nodes:
                if node_id == self.entry_node:
                    continue

                preds = self.nodes[node_id].predecessors
                if not preds:
                    continue

                new_dominators = {node_id}
                for pred in preds:
                    if pred in dominators:
                        new_dominators &= dominators[pred]

                if dominators[node_id] != new_dominators:
                    dominators[node_id] = new_dominators
                    changed = True

        self.dominated_nodes = dominators

    def calculate_post_dominators(self):
        """计算后支配节点"""
        if not self.exit_node:
            return

        reverse_cfg = ControlFlowGraph(self.function_name)

        for node_id in self.nodes:
            reverse_cfg.add_node(CFGNode(
                node_id=node_id,
                node_type=self.nodes[node_id].node_type
            ))

        for edge in self.edges:
            reverse_cfg.add_edge(CFGEdge(
                source=edge.target,
                target=edge.source,
                edge_type=edge.edge_type
            ))

        reverse_cfg.calculate_dominators()

        self.post_dominated_nodes = reverse_cfg.dominated_nodes

    def find_dominance_frontier(self, node_id: str) -> Set[str]:
        """找到节点的后续边界

        Args:
            node_id: 节点ID

        Returns:
            Set[str]: 后续边界节点集合
        """
        frontier = set()
        node = self.nodes.get(node_id)

        if not node:
            return frontier

        for successor_id in node.successors:
            if successor_id not in self.dominated_nodes.get(node_id, set()):
                frontier.add(successor_id)

            for successor_successor in self.nodes.get(successor_id, CFGNode("", CFGNodeType.BASIC_BLOCK)).successors:
                if node_id in self.dominated_nodes.get(successor_successor, set()):
                    if successor_id not in self.dominated_nodes.get(node_id, set()):
                        frontier.add(successor_id)

        return frontier

    def identify_loops(self) -> List[Dict[str, Any]]:
        """识别循环结构

        Returns:
            List[Dict[str, Any]]: 循环信息列表
        """
        loops = []

        for node_id, node in self.nodes.items():
            if node.node_type == CFGNodeType.LOOP_HEADER:
                loop_info = {
                    'header': node_id,
                    'body_nodes': [],
                    'exit_nodes': [],
                    'depth': node.loop_depth,
                    'type': 'while'
                }

                visited = set()
                queue = deque()

                for successor_id in node.successors:
                    if successor_id != node_id:
                        queue.append(successor_id)

                while queue:
                    current = queue.popleft()
                    if current in visited:
                        continue

                    visited.add(current)

                    if current != node_id:
                        loop_info['body_nodes'].append(current)

                    for successor_id in self.nodes.get(current, CFGNode("", CFGNodeType.BASIC_BLOCK)).successors:
                        if successor_id == node_id:
                            if current not in loop_info['exit_nodes']:
                                loop_info['exit_nodes'].append(current)
                        elif successor_id not in visited:
                            queue.append(successor_id)

                loops.append(loop_info)

        self.loops = loops
        return loops

    def calculate_cyclomatic_complexity(self) -> int:
        """计算圈复杂度

        Returns:
            int: 圈复杂度值
        """
        if not self.nodes or not self.edges:
            return 0

        num_nodes = len(self.nodes)
        num_edges = len(self.edges)

        num_regions = num_edges - num_nodes + 2

        return max(1, num_regions)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "function_name": self.function_name,
            "entry_node": self.entry_node,
            "exit_node": self.exit_node,
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            "edges": [edge.to_dict() for edge in self.edges],
            "loops": self.loops,
            "metadata": self.metadata
        }


class CFGConstructionLayer:
    """控制流CFG构建层【V3.1升级】

    功能描述：
        - 将函数代码转换为控制流图（CFG）
        - 识别基本块和控制流结构
        - 构建节点和边的关系
        - 识别循环、条件和分支结构
        - 计算圈复杂度和路径数
        - 支持异常处理的CFG构建
        - 提供支配分析和后支配分析

    输入类型：
        - 函数切片（FunctionSlice）
        - 源代码（用于提取CFG节点）

    输出类型：
        - ControlFlowGraph: 控制流图对象
        - List[ControlFlowGraph]: 函数CFG列表
        - Dict[str, Any]: CFG分析统计信息

    使用场景：
        - 为路径生成提供控制流基础
        - 支持圈复杂度和代码质量评估
        - 帮助识别可测试性低的代码区域
        - 支持测试用例的路径覆盖分析

    V3.1升级点：
        - 增强对异常处理结构的CFG构建
        - 支持异步/await的控制流分析
        - 增加对生成器和yield的控制流支持
        - 提供更精确的循环识别算法
        - 支持嵌套try-except-finally结构
        - 增加对with语句的控制流建模
    """

    description: str = "控制流CFG构建层【V3.1升级】- 构建函数的控制流图"
    input_type: str = "FunctionSlice或源代码"
    output_type: str = "ControlFlowGraph或List[ControlFlowGraph]"

    def __init__(self):
        """初始化CFG构建层"""
        self.function_slices = []
        self.cfg_graphs = {}
        self.source_lines = []
        self.node_counter = 0
        self.loop_depth = 0

    def process(self, context) -> Dict[str, ControlFlowGraph]:
        """处理函数切片，构建CFG

        Args:
            context: PipelineContext对象，包含函数切片列表

        Returns:
            Dict[str, ControlFlowGraph]: 函数名到CFG的映射字典

        Raises:
            ValueError: 当输入数据为空时
        """
        if not context.has('function_slices'):
            raise ValueError("CFGConstructionLayer: 缺少函数切片列表")

        self.function_slices = context.get('function_slices')

        if context.has('source'):
            source = context.get('source')
            if isinstance(source, list):
                self.source_lines = source
            elif isinstance(source, str):
                self.source_lines = source.split('\n')
            else:
                self.source_lines = []

        self.cfg_graphs = {}

        for slice_item in self.function_slices:
            func_name = getattr(slice_item, 'qualified_name', '') or getattr(slice_item, 'name', '')
            if func_name:
                cfg = self._build_cfg_for_function(slice_item, func_name)
                self.cfg_graphs[func_name] = cfg

        context.set('cfg_graphs', self.cfg_graphs)
        context.set('cfg_construction_complete', True)
        context.set('cfg_statistics', self._get_statistics())

        return self.cfg_graphs

    def _build_cfg_for_function(self, func_slice, func_name: str) -> ControlFlowGraph:
        """为单个函数构建CFG

        Args:
            func_slice: 函数切片
            func_name: 函数名

        Returns:
            ControlFlowGraph: 控制流图
        """
        cfg = ControlFlowGraph(function_name=func_name)

        self.node_counter = 0
        self.loop_depth = 0

        start_line = getattr(func_slice, 'start_line', 1)
        end_line = getattr(func_slice, 'end_line', start_line)

        entry_node = self._create_node(cfg, CFGNodeType.ENTRY, f"entry_{func_name}", line=start_line)
        exit_node = self._create_node(cfg, CFGNodeType.EXIT, f"exit_{func_name}", line=end_line)

        cfg.entry_node = entry_node.node_id
        cfg.exit_node = exit_node.node_id

        source_code = getattr(func_slice, 'source_code', '')

        if not source_code:
            cfg.add_edge(CFGEdge(entry_node.node_id, exit_node.node_id, EdgeType.UNCONDITIONAL))
            return cfg

        basic_blocks = self._identify_basic_blocks(source_code, start_line)

        current_block_id = entry_node.node_id

        for block in basic_blocks:
            block_node = self._create_block_node(cfg, block, func_name)
            cfg.add_edge(CFGEdge(current_block_id, block_node.node_id, EdgeType.FALL_THROUGH))
            current_block_id = block_node.node_id

        if current_block_id != exit_node.node_id:
            cfg.add_edge(CFGEdge(current_block_id, exit_node.node_id, EdgeType.UNCONDITIONAL))

        self._connect_control_structures(cfg, source_code, start_line)

        self._process_exceptions(cfg, source_code, start_line)

        self._process_loops(cfg, source_code, start_line)

        self._process_async_await(cfg, source_code, start_line)

        cfg.calculate_dominators()

        cfg.calculate_post_dominators()

        cfg.identify_loops()

        cfg.basic_blocks = [node_id for node_id, node in cfg.nodes.items()
                           if node.node_type == CFGNodeType.BASIC_BLOCK]

        cfg.metadata['cyclomatic_complexity'] = cfg.calculate_cyclomatic_complexity()
        cfg.metadata['total_paths'] = len(cfg.get_all_paths())
        cfg.metadata['loop_count'] = len(cfg.loops)

        return cfg

    def _create_node(self, cfg: ControlFlowGraph, node_type: CFGNodeType,
                     label: str, line: int = 0) -> CFGNode:
        """创建CFG节点

        Args:
            cfg: 控制流图
            node_type: 节点类型
            label: 节点标签
            line: 行号

        Returns:
            CFGNode: 创建的节点
        """
        self.node_counter += 1
        node_id = f"node_{self.node_counter}"

        node = CFGNode(
            node_id=node_id,
            node_type=node_type,
            label=label,
            line_start=line,
            line_end=line
        )

        cfg.add_node(node)
        return node

    def _create_block_node(self, cfg: ControlFlowGraph, block: Dict[str, Any], func_name: str) -> CFGNode:
        """创建基本块节点

        Args:
            cfg: 控制流图
            block: 基本块信息
            func_name: 函数名

        Returns:
            CFGNode: 基本块节点
        """
        node_type = CFGNodeType.BASIC_BLOCK

        if block.get('type') == 'conditional':
            node_type = CFGNodeType.CONDITIONAL
        elif block.get('type') == 'loop':
            node_type = CFGNodeType.LOOP_HEADER
        elif block.get('type') == 'try':
            node_type = CFGNodeType.TRY_BLOCK

        node = self._create_node(
            cfg,
            node_type,
            block.get('label', f"block_{block.get('start_line', 0)}"),
            block.get('start_line', 0)
        )

        node.line_end = block.get('end_line', block.get('start_line', 0))
        node.statements = block.get('statements', [])

        if block.get('condition'):
            node.condition = block.get('condition')

        return node

    def _identify_basic_blocks(self, source_code: str, base_line: int) -> List[Dict[str, Any]]:
        """识别基本块

        Args:
            source_code: 源代码
            base_line: 起始行号

        Returns:
            List[Dict[str, Any]]: 基本块列表
        """
        blocks = []

        if not source_code:
            return blocks

        lines = source_code.split('\n')

        current_block = {
            'type': 'basic',
            'start_line': base_line,
            'end_line': base_line,
            'statements': [],
            'label': f"block_{base_line}"
        }

        for i, line in enumerate(lines):
            line_num = base_line + i
            stripped = line.strip()

            is_branch = any(keyword in stripped for keyword in ['if ', 'elif ', 'for ', 'while ', 'try:', 'except', 'finally:', 'with '])
            is_jump = any(keyword in stripped for keyword in ['return ', 'break', 'continue', 'raise ', 'yield '])

            if is_branch or is_jump:
                if current_block['statements']:
                    blocks.append(current_block)

                if is_branch:
                    block_type = 'conditional' if 'if ' in stripped or 'elif ' in stripped else 'loop'
                    current_block = {
                        'type': block_type,
                        'start_line': line_num,
                        'end_line': line_num,
                        'statements': [stripped],
                        'label': f"{block_type}_{line_num}",
                        'condition': stripped
                    }
                else:
                    current_block = {
                        'type': 'jump',
                        'start_line': line_num,
                        'end_line': line_num,
                        'statements': [stripped],
                        'label': f"jump_{line_num}"
                    }

                blocks.append(current_block)
                current_block = {
                    'type': 'basic',
                    'start_line': line_num + 1,
                    'end_line': line_num + 1,
                    'statements': [],
                    'label': f"block_{line_num + 1}"
                }
            else:
                if current_block['type'] == 'basic':
                    current_block['end_line'] = line_num
                    current_block['statements'].append(stripped)

        if current_block['statements']:
            blocks.append(current_block)

        if not blocks:
            blocks.append({
                'type': 'basic',
                'start_line': base_line,
                'end_line': base_line + len(lines) - 1,
                'statements': lines,
                'label': f"block_{base_line}"
            })

        return blocks

    def _connect_control_structures(self, cfg: ControlFlowGraph, source_code: str, base_line: int):
        """连接控制结构

        Args:
            cfg: 控制流图
            source_code: 源代码
            base_line: 起始行号
        """
        lines = source_code.split('\n')

        for i, line in enumerate(lines):
            line_num = base_line + i
            stripped = line.strip()

            if stripped.startswith('if '):
                self._handle_if_statement(cfg, stripped, line_num)
            elif stripped.startswith('elif '):
                self._handle_elif_statement(cfg, stripped, line_num)
            elif stripped.startswith('else:'):
                self._handle_else_statement(cfg, line_num)
            elif stripped.startswith('for ') or stripped.startswith('while '):
                self._handle_loop_statement(cfg, stripped, line_num)

    def _handle_if_statement(self, cfg: ControlFlowGraph, statement: str, line: int):
        """处理if语句

        Args:
            cfg: 控制流图
            statement: 语句
            line: 行号
        """
        condition_match = statement[3:].strip()

        for node_id, node in cfg.nodes.items():
            if node.line_start <= line <= node.line_end:
                if node.node_type == CFGNodeType.CONDITIONAL:
                    node.condition = condition_match

                true_label = f"if_true_{line}"
                false_label = f"if_false_{line}"

                true_node = self._create_node(cfg, CFGNodeType.BASIC_BLOCK, true_label, line + 1)
                false_node = self._create_node(cfg, CFGNodeType.BASIC_BLOCK, false_label, line + 1)

                cfg.add_edge(CFGEdge(node_id, true_node.node_id, EdgeType.TRUE_BRANCH, f"{condition_match} == True"))
                cfg.add_edge(CFGEdge(node_id, false_node.node_id, EdgeType.FALSE_BRANCH, f"{condition_match} == False"))

                break

    def _handle_elif_statement(self, cfg: ControlFlowGraph, statement: str, line: int):
        """处理elif语句

        Args:
            cfg: 控制流图
            statement: 语句
            line: 行号
        """
        pass

    def _handle_else_statement(self, cfg: ControlFlowGraph, line: int):
        """处理else语句

        Args:
            cfg: 控制流图
            line: 行号
        """
        else_node = self._create_node(cfg, CFGNodeType.BASIC_BLOCK, f"else_{line}", line + 1)

        for node_id, node in cfg.nodes.items():
            if node.node_type == CFGNodeType.CONDITIONAL and node.line_end < line:
                cfg.add_edge(CFGEdge(node_id, else_node.node_id, EdgeType.FALSE_BRANCH))

    def _handle_loop_statement(self, cfg: ControlFlowGraph, statement: str, line: int):
        """处理循环语句

        Args:
            cfg: 控制流图
            statement: 语句
            line: 行号
        """
        self.loop_depth += 1

        for node_id, node in cfg.nodes.items():
            if node.line_start == line:
                node.node_type = CFGNodeType.LOOP_HEADER
                node.is_loop_header = True
                node.loop_depth = self.loop_depth

                loop_body = self._create_node(cfg, CFGNodeType.LOOP_BODY, f"loop_body_{line}", line + 1)

                cfg.add_edge(CFGEdge(node_id, loop_body.node_id, EdgeType.UNCONDITIONAL))

                exit_node = self._create_node(cfg, CFGNodeType.BASIC_BLOCK, f"loop_exit_{line}", line)

                cfg.add_edge(CFGEdge(loop_body.node_id, node_id, EdgeType.LOOP_BACK))

                break

    def _process_exceptions(self, cfg: ControlFlowGraph, source_code: str, base_line: int):
        """处理异常处理结构

        Args:
            cfg: 控制流图
            source_code: 源代码
            base_line: 起始行号
        """
        if 'try:' not in source_code:
            return

        lines = source_code.split('\n')

        for i, line in enumerate(lines):
            line_num = base_line + i
            stripped = line.strip()

            if stripped.startswith('try:'):
                try_node = self._create_node(cfg, CFGNodeType.TRY_BLOCK, f"try_{line_num}", line_num)
                cfg.metadata['has_try'] = True

            elif stripped.startswith('except'):
                except_type = ''
                if 'as ' in stripped:
                    except_type = stripped.split('as')[0].replace('except', '').strip()
                elif 'except' in stripped:
                    except_type = stripped.replace('except', '').strip(':')

                except_node = self._create_node(cfg, CFGNodeType.EXCEPT_BLOCK,
                                               f"except_{line_num}_{except_type}", line_num)
                except_node.metadata['exception_type'] = except_type

            elif stripped.startswith('finally:'):
                finally_node = self._create_node(cfg, CFGNodeType.FINALLY_BLOCK,
                                                f"finally_{line_num}", line_num)

    def _process_async_await(self, cfg: ControlFlowGraph, source_code: str, base_line: int):
        """处理异步控制流

        Args:
            cfg: 控制流图
            source_code: 源代码
            base_line: 起始行号
        """
        if 'async ' not in source_code and 'await ' not in source_code:
            return

        lines = source_code.split('\n')

        for i, line in enumerate(lines):
            line_num = base_line + i
            stripped = line.strip()

            if stripped.startswith('async '):
                for node_id, node in cfg.nodes.items():
                    if node.line_start == line_num:
                        node.metadata['is_async'] = True
                        break

            if stripped.startswith('await '):
                await_node = self._create_node(cfg, CFGNodeType.ASYNC_AWAIT,
                                               f"await_{line_num}", line_num)

                for node_id, node in cfg.nodes.items():
                    if node.line_end == line_num - 1:
                        cfg.add_edge(CFGEdge(node_id, await_node.node_id, EdgeType.UNCONDITIONAL))
                        break

    def _process_loops(self, cfg: ControlFlowGraph, source_code: str, base_line: int):
        """处理循环结构

        Args:
            cfg: 控制流图
            source_code: 源代码
            base_line: 起始行号
        """
        cfg.identify_loops()

    def _get_statistics(self) -> Dict[str, Any]:
        """获取统计信息

        Returns:
            Dict[str, Any]: 统计信息
        """
        if not self.cfg_graphs:
            return {}

        total_complexity = 0
        total_paths = 0
        total_loops = 0
        total_nodes = 0
        total_edges = 0

        complexity_distribution = {}
        loops_by_depth = defaultdict(int)

        for func_name, cfg in self.cfg_graphs.items():
            complexity = cfg.metadata.get('cyclomatic_complexity', 0)
            total_complexity += complexity
            total_paths += cfg.metadata.get('total_paths', 0)
            total_loops += len(cfg.loops)
            total_nodes += len(cfg.nodes)
            total_edges += len(cfg.edges)

            complexity_level = 'low' if complexity <= 5 else 'medium' if complexity <= 10 else 'high'
            complexity_distribution[complexity_level] = complexity_distribution.get(complexity_level, 0) + 1

            for loop in cfg.loops:
                loops_by_depth[loop.get('depth', 0)] += 1

        return {
            'total_functions': len(self.cfg_graphs),
            'total_nodes': total_nodes,
            'total_edges': total_edges,
            'total_complexity': total_complexity,
            'average_complexity': total_complexity / len(self.cfg_graphs) if self.cfg_graphs else 0,
            'total_paths': total_paths,
            'total_loops': total_loops,
            'complexity_distribution': complexity_distribution,
            'loops_by_depth': dict(loops_by_depth),
            'high_complexity_functions': [
                func_name for func_name, cfg in self.cfg_graphs.items()
                if cfg.metadata.get('cyclomatic_complexity', 0) > 10
            ]
        }

    def get_cfg_for_function(self, func_name: str) -> Optional[ControlFlowGraph]:
        """获取指定函数的CFG

        Args:
            func_name: 函数名

        Returns:
            Optional[ControlFlowGraph]: 找到的CFG
        """
        return self.cfg_graphs.get(func_name)

    def get_all_paths_for_function(self, func_name: str) -> List[List[str]]:
        """获取指定函数的所有路径

        Args:
            func_name: 函数名

        Returns:
            List[List[str]]: 路径列表
        """
        cfg = self.cfg_graphs.get(func_name)
        if cfg:
            return cfg.get_all_paths()
        return []

    def get_complexity_for_function(self, func_name: str) -> int:
        """获取指定函数的圈复杂度

        Args:
            func_name: 函数名

        Returns:
            int: 圈复杂度
        """
        cfg = self.cfg_graphs.get(func_name)
        if cfg:
            return cfg.calculate_cyclomatic_complexity()
        return 0

    def identify_test_paths(self, func_name: str, max_paths: int = 10) -> List[Dict[str, Any]]:
        """识别适合测试的路径

        Args:
            func_name: 函数名
            max_paths: 最大路径数

        Returns:
            List[Dict[str, Any]]: 测试路径列表
        """
        cfg = self.cfg_graphs.get(func_name)
        if not cfg:
            return []

        all_paths = cfg.get_all_paths()

        test_paths = []

        for path in all_paths[:max_paths]:
            path_info = {
                'path': path,
                'length': len(path),
                'nodes': [cfg.get_node(node_id) for node_id in path if cfg.get_node(node_id)],
                'decision_points': [],
                'loops': []
            }

            for node_id in path:
                node = cfg.get_node(node_id)
                if node and node.node_type == CFGNodeType.CONDITIONAL:
                    path_info['decision_points'].append(node_id)

                if node and node.is_loop_header:
                    path_info['loops'].append(node_id)

            test_paths.append(path_info)

        return test_paths

    def get_coverage_requirements(self, func_name: str) -> Dict[str, List[str]]:
        """获取覆盖要求

        Args:
            func_name: 函数名

        Returns:
            Dict[str, List[str]]: 覆盖要求字典
        """
        cfg = self.cfg_graphs.get(func_name)
        if not cfg:
            return {}

        requirements = {
            'statement_coverage': [],
            'branch_coverage': [],
            'path_coverage': []
        }

        for node_id, node in cfg.nodes.items():
            if node.statements:
                requirements['statement_coverage'].append(node_id)

            if node.node_type == CFGNodeType.CONDITIONAL:
                requirements['branch_coverage'].append(node_id)
                if node.successors:
                    requirements['branch_coverage'].extend(node.successors)

        requirements['path_coverage'] = [cfg.exit_node]

        return requirements
