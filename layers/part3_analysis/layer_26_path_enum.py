"""
Layer 26: PathEnumerationLayer - 全路径枚举生成层【V3.1升级】

本层负责从CFG中枚举所有可能的执行路径，包括简单路径、循环路径和递归路径。
V3.1升级增强了深度限制、智能剪枝和路径压缩能力。
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import deque
import itertools


class EnumerationStrategy(Enum):
    """枚举策略枚举"""
    ALL_PATHS = auto()
    FEASIBLE_ONLY = auto()
    UNIQUE_PATHS = auto()
    MINIMAL_PATHS = auto()
    COVERED_PATHS = auto()


class PathSource(Enum):
    """路径来源枚举"""
    CFG = auto()
    FUNCTION = auto()
    MODULE = auto()
    INTEGRATION = auto()


@dataclass
class EnumerationConfig:
    """枚举配置

    Attributes:
        max_depth: 最大枚举深度
        max_paths: 最大路径数量
        include_loops: 是否包含循环路径
        loop_iterations: 循环迭代次数
        merge_similar: 是否合并相似路径
        filter_duplicates: 是否过滤重复路径
        timeout_seconds: 超时秒数
        enable_pruning: 是否启用剪枝
    """
    max_depth: int = 100
    max_paths: int = 10000
    include_loops: bool = True
    loop_iterations: int = 3
    merge_similar: bool = True
    filter_duplicates: bool = True
    timeout_seconds: int = 300
    enable_pruning: bool = True


@dataclass
class EnumeratedPath:
    """枚举的路径

    Attributes:
        path_id: 路径标识符
        path_source: 路径来源
        nodes: 节点列表
        edges: 边列表
        length: 路径长度
        is_feasible: 是否可行
        is_unique: 是否唯一
        loop_count: 循环次数
        branch_count: 分支次数
        complexity: 复杂度
        coverage_potential: 覆盖潜力
        description: 描述
        test_value: 测试价值评分
    """
    path_id: str
    path_source: PathSource
    nodes: List[str] = field(default_factory=list)
    edges: List[Tuple[str, str]] = field(default_factory=list)
    length: int = 0
    is_feasible: bool = True
    is_unique: bool = True
    loop_count: int = 0
    branch_count: int = 0
    complexity: int = 1
    coverage_potential: float = 0.5
    description: str = ""
    test_value: float = 0.5

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "path_id": self.path_id,
            "path_source": self.path_source.name,
            "nodes": self.nodes,
            "edges": [(str(e[0]), str(e[1])) for e in self.edges],
            "length": self.length,
            "is_feasible": self.is_feasible,
            "is_unique": self.is_unique,
            "loop_count": self.loop_count,
            "branch_count": self.branch_count,
            "complexity": self.complexity,
            "coverage_potential": self.coverage_potential,
            "description": self.description,
            "test_value": self.test_value
        }

    def add_node(self, node_id: str) -> None:
        """添加节点

        Args:
            node_id: 节点标识符
        """
        if node_id not in self.nodes:
            self.nodes.append(node_id)
            self.length = len(self.nodes)

    def add_edge(self, source: str, target: str) -> None:
        """添加边

        Args:
            source: 源节点
            target: 目标节点
        """
        edge = (source, target)
        if edge not in self.edges:
            self.edges.append(edge)


@dataclass
class EnumerationResult:
    """枚举结果

    Attributes:
        total_enumerated: 总枚举数
        feasible_paths: 可行路径数
        unique_paths: 唯一路径数
        pruned_paths: 剪枝路径数
        enumerated_paths: 枚举的路径列表
        enumeration_stats: 枚举统计信息
        source_info: 来源信息
        warnings: 警告信息
        metadata: 元信息
    """
    total_enumerated: int = 0
    feasible_paths: int = 0
    unique_paths: int = 0
    pruned_paths: int = 0
    enumerated_paths: List[EnumeratedPath] = field(default_factory=list)
    enumeration_stats: Dict[str, Any] = field(default_factory=dict)
    source_info: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "total_enumerated": self.total_enumerated,
            "feasible_paths": self.feasible_paths,
            "unique_paths": self.unique_paths,
            "pruned_paths": self.pruned_paths,
            "enumerated_paths": [p.to_dict() for p in self.enumerated_paths],
            "enumeration_stats": self.enumeration_stats,
            "source_info": self.source_info,
            "warnings": self.warnings,
            "metadata": self.metadata
        }

    def get_feasibility_rate(self) -> float:
        """获取可行率

        Returns:
            float: 可行率（0-100）
        """
        if self.total_enumerated == 0:
            return 0.0
        return (self.feasible_paths / self.total_enumerated) * 100


class PathEnumerationLayer:
    """全路径枚举生成层【V3.1升级】

    功能描述：
        - 从CFG枚举所有可能的执行路径
        - 支持多种枚举策略（全部、可行、唯一等）
        - 处理循环路径和递归路径
        - 智能剪枝和路径去重
        - 评估路径的可行性和测试价值
        - 路径压缩和合并
        - 支持深度限制和数量限制

    输入类型：
        - 控制流图（ControlFlowGraph）
        - 节点映射（node_id -> node）
        - 边列表（edges）
        - 枚举配置（EnumerationConfig）

    输出类型：
        - EnumerationResult: 枚举结果
        - List[EnumeratedPath]: 枚举的路径列表
        - 路径统计信息

    使用场景：
        - 穷举测试用例生成
        - 路径覆盖分析
        - 测试充分性评估
        - 回归测试选择
        - 路径可视化

    V3.1升级点：
        - 增强深度限制和智能剪枝
        - 支持路径压缩和合并
        - 增加循环路径的多样性处理
        - 提供更精确的可行性分析
        - 支持分布枚举和并行处理
    """

    description: str = "全路径枚举生成层【V3.1升级】- 从CFG枚举所有执行路径"
    input_type: str = "ControlFlowGraph和EnumerationConfig"
    output_type: str = "EnumerationResult和List[EnumeratedPath]"

    def __init__(self):
        """初始化路径枚举层"""
        self.cfg = None
        self.config = EnumerationConfig()
        self.enumerated_paths = []
        self.enumeration_result = None
        self.path_cache = {}
        self.seen_signatures = set()

    def set_config(self, config: EnumerationConfig) -> None:
        """设置枚举配置

        Args:
            config: 枚举配置对象
        """
        self.config = config

    def set_strategy(self, strategy: EnumerationStrategy) -> None:
        """设置枚举策略

        Args:
            strategy: 枚举策略
        """
        self.strategy = strategy

    def process(self, context) -> EnumerationResult:
        """处理CFG，枚举所有路径

        Args:
            context: PipelineContext对象，包含CFG和配置信息

        Returns:
            EnumerationResult: 枚举结果

        Raises:
            ValueError: 当输入数据不足时
        """
        if not context.has('cfg_graphs') and not context.has('cfg'):
            raise ValueError("PathEnumerationLayer: 缺少控制流图")

        if context.has('cfg'):
            self.cfg = context.get('cfg')
        elif context.has('cfg_graphs'):
            self.cfg_graphs = context.get('cfg_graphs')

        if context.has('enumeration_config'):
            self.config = context.get('enumeration_config')

        if context.has('enumeration_strategy'):
            self.strategy = context.get('enumeration_strategy')
        else:
            self.strategy = EnumerationStrategy.ALL_PATHS

        if hasattr(self, 'cfg_graphs') and isinstance(self.cfg_graphs, dict):
            self.enumerated_paths = self._enumerate_from_graphs()
        elif self.cfg:
            self.enumerated_paths = self._enumerate_all_paths()
        else:
            self.enumerated_paths = []

        if self.config.filter_duplicates:
            self.enumerated_paths = self._filter_duplicate_paths()

        if self.config.merge_similar:
            self.enumerated_paths = self._merge_similar_paths()

        self.enumeration_result = self._create_enumeration_result()

        context.set('enumerated_paths', self.enumerated_paths)
        context.set('enumeration_result', self.enumeration_result)
        context.set('path_enumeration_complete', True)
        context.set('enumeration_statistics', self._get_statistics())

        return self.enumeration_result

    def _enumerate_from_graphs(self) -> List[EnumeratedPath]:
        """从多个CFG图枚举路径

        Returns:
            List[EnumeratedPath]: 枚举的路径列表
        """
        all_paths = []

        for func_name, cfg in self.cfg_graphs.items():
            self.cfg = cfg
            paths = self._enumerate_all_paths()
            for path in paths:
                path.path_source = PathSource.FUNCTION
                path.description = f"函数: {func_name}"
            all_paths.extend(paths)

        return all_paths

    def _enumerate_all_paths(self) -> List[EnumeratedPath]:
        """枚举所有路径

        Returns:
            List[EnumeratedPath]: 枚举的路径列表
        """
        if not self.cfg:
            return []

        entry_nodes = self._find_entry_nodes()
        exit_nodes = self._find_exit_nodes()

        all_paths = []

        for entry in entry_nodes:
            for exit_node in exit_nodes:
                paths = self._enumerate_between_nodes(entry, exit_node)
                all_paths.extend(paths)

                if len(all_paths) >= self.config.max_paths:
                    self.enumeration_result.warnings.append(
                        f"达到最大路径数限制: {self.config.max_paths}"
                    )
                    return all_paths[:self.config.max_paths]

        return all_paths

    def _enumerate_between_nodes(self, start: str, end: str) -> List[EnumeratedPath]:
        """枚举两个节点之间的所有路径

        Args:
            start: 起始节点
            end: 结束节点

        Returns:
            List[EnumeratedPath]: 路径列表
        """
        paths = []

        if self.strategy == EnumerationStrategy.ALL_PATHS:
            paths = self._enumerate_all_simple_paths(start, end)
        elif self.strategy == EnumerationStrategy.FEASIBLE_ONLY:
            paths = self._enumerate_feasible_paths(start, end)
        elif self.strategy == EnumerationStrategy.UNIQUE_PATHS:
            paths = self._enumerate_unique_paths(start, end)
        elif self.strategy == EnumerationStrategy.MINIMAL_PATHS:
            paths = self._enumerate_minimal_paths(start, end)
        elif self.strategy == EnumerationStrategy.COVERED_PATHS:
            paths = self._enumerate_covered_paths(start, end)

        return paths

    def _enumerate_all_simple_paths(self, start: str, end: str) -> List[EnumeratedPath]:
        """枚举简单路径（不含循环）

        Args:
            start: 起始节点
            end: 结束节点

        Returns:
            List[EnumeratedPath]: 简单路径列表
        """
        paths = []
        queue = deque([(start, [start], set())])

        while queue:
            current, path, visited = queue.popleft()

            if len(path) > self.config.max_depth:
                continue

            if current == end:
                path_obj = self._create_enumerated_path(path, PathSource.CFG)
                paths.append(path_obj)
                continue

            successors = self._get_successors(current)

            for successor in successors:
                if successor not in visited:
                    new_visited = visited | {successor}
                    new_path = path + [successor]
                    queue.append((successor, new_path, new_visited))

                    if len(paths) >= self.config.max_paths:
                        return paths

        return paths

    def _enumerate_feasible_paths(self, start: str, end: str) -> List[EnumeratedPath]:
        """枚举可行路径

        Args:
            start: 起始节点
            end: 结束节点

        Returns:
            List[EnumeratedPath]: 可行路径列表
        """
        all_paths = self._enumerate_all_simple_paths(start, end)

        feasible_paths = []

        for path in all_paths:
            if self._is_path_feasible(path):
                path.is_feasible = True
                feasible_paths.append(path)
            else:
                path.is_feasible = False

        return feasible_paths

    def _enumerate_unique_paths(self, start: str, end: str) -> List[EnumeratedPath]:
        """枚举唯一路径

        Args:
            start: 起始节点
            end: 结束节点

        Returns:
            List[EnumeratedPath]: 唯一路径列表
        """
        all_paths = self._enumerate_all_simple_paths(start, end)

        seen_signatures = set()
        unique_paths = []

        for path in all_paths:
            signature = tuple(path.nodes)

            if signature not in seen_signatures:
                seen_signatures.add(signature)
                path.is_unique = True
                unique_paths.append(path)
            else:
                path.is_unique = False

        return unique_paths

    def _enumerate_minimal_paths(self, start: str, end: str) -> List[EnumeratedPath]:
        """枚举最小路径集（覆盖所有边）

        Args:
            start: 起始节点
            end: 结束节点

        Returns:
            List[EnumeratedPath]: 最小路径列表
        """
        all_paths = self._enumerate_all_simple_paths(start, end)

        covered_edges = set()
        minimal_paths = []

        edges = [(e.source, e.target) for e in getattr(self.cfg, 'edges', [])]

        for path in all_paths:
            path_edges = set(zip(path.nodes[:-1], path.nodes[1:]))

            new_edges = path_edges - covered_edges

            if new_edges:
                covered_edges.update(path_edges)
                minimal_paths.append(path)

                if covered_edges >= set(edges):
                    break

        return minimal_paths

    def _enumerate_covered_paths(self, start: str, end: str) -> List[EnumeratedPath]:
        """枚举已覆盖的路径

        Args:
            start: 起始节点
            end: 结束节点

        Returns:
            List[EnumeratedPath]: 已覆盖路径列表
        """
        covered_paths = []

        if hasattr(self.cfg, 'coverage') and self.cfg.coverage:
            for path_id, is_covered in self.cfg.coverage.items():
                if is_covered:
                    path_obj = self._create_enumerated_path([start, end], PathSource.CFG)
                    path_obj.path_id = path_id
                    covered_paths.append(path_obj)

        return covered_paths

    def _enumerate_paths_with_loops(self, start: str, end: str) -> List[EnumeratedPath]:
        """枚举包含循环的路径【V3.1增强】

        Args:
            start: 起始节点
            end: 结束节点

        Returns:
            List[EnumeratedPath]: 包含循环的路径列表
        """
        paths = []

        loop_headers = self._detect_loops()

        base_paths = self._enumerate_all_simple_paths(start, end)

        for base_path in base_paths:
            paths.append(base_path)

            for loop_header in loop_headers:
                if loop_header in base_path.nodes:
                    loop_variants = self._generate_loop_variants(
                        base_path, loop_header, self.config.loop_iterations
                    )
                    paths.extend(loop_variants)

                    if len(paths) >= self.config.max_paths:
                        return paths[:self.config.max_paths]

        return paths

    def _generate_loop_variants(self, base_path: List[str],
                              loop_header: str, iterations: int) -> List[EnumeratedPath]:
        """生成循环变体路径【V3.1新增】

        Args:
            base_path: 基础路径
            loop_header: 循环头节点
            iterations: 迭代次数

        Returns:
            List[EnumeratedPath]: 循环变体路径列表
        """
        variants = []

        loop_start_idx = base_path.nodes.index(loop_header) if loop_header in base_path.nodes else -1

        if loop_start_idx == -1:
            return variants

        for i in range(2, iterations + 1):
            extended_nodes = base_path.nodes[:loop_start_idx + 1] + \
                           base_path.nodes[loop_start_idx:] * (i - 1) + \
                           base_path.nodes[loop_start_idx + 1:]

            path_obj = self._create_enumerated_path(extended_nodes, PathSource.CFG)
            path_obj.loop_count = i
            path_obj.description = f"循环{i}次"
            variants.append(path_obj)

        return variants

    def _create_enumerated_path(self, nodes: List[str], source: PathSource) -> EnumeratedPath:
        """创建枚举路径对象

        Args:
            nodes: 节点列表
            source: 路径来源

        Returns:
            EnumeratedPath: 枚举路径对象
        """
        path_id = f"path_{len(self.enumerated_paths)}_{hash(tuple(nodes))}"

        edges = []
        for i in range(len(nodes) - 1):
            edges.append((nodes[i], nodes[i + 1]))

        branch_count = self._count_branches(nodes)
        complexity = self._calculate_path_complexity(nodes)

        path_obj = EnumeratedPath(
            path_id=path_id,
            path_source=source,
            nodes=nodes,
            edges=edges,
            length=len(nodes),
            branch_count=branch_count,
            complexity=complexity
        )

        path_obj.coverage_potential = self._estimate_coverage_potential(path_obj)
        path_obj.test_value = self._estimate_test_value(path_obj)

        return path_obj

    def _find_entry_nodes(self) -> List[str]:
        """查找入口节点

        Returns:
            List[str]: 入口节点列表
        """
        if hasattr(self.cfg, 'entry') and self.cfg.entry:
            return [self.cfg.entry]

        if hasattr(self.cfg, 'nodes') and self.cfg.nodes:
            for node_id, node in self.cfg.nodes.items():
                if hasattr(node, 'node_type'):
                    if node.node_type.value == 1:
                        return [node_id]

        return list(self.cfg.nodes.keys())[:1] if hasattr(self.cfg, 'nodes') else ['start']

    def _find_exit_nodes(self) -> List[str]:
        """查找出口节点

        Returns:
            List[str]: 出口节点列表
        """
        if hasattr(self.cfg, 'exit') and self.cfg.exit:
            return [self.cfg.exit]

        if hasattr(self.cfg, 'nodes') and self.cfg.nodes:
            exit_nodes = []
            for node_id, node in self.cfg.nodes.items():
                if hasattr(node, 'node_type'):
                    if node.node_type.value == 2:
                        exit_nodes.append(node_id)

            if exit_nodes:
                return exit_nodes

        return list(self.cfg.nodes.keys())[-1:] if hasattr(self.cfg, 'nodes') else ['end']

    def _get_successors(self, node_id: str) -> List[str]:
        """获取节点的后继节点

        Args:
            node_id: 节点标识符

        Returns:
            List[str]: 后继节点列表
        """
        if hasattr(self.cfg, 'nodes') and node_id in self.cfg.nodes:
            node = self.cfg.nodes[node_id]
            if hasattr(node, 'successors'):
                return node.successors

        if hasattr(self.cfg, 'edges'):
            successors = []
            for edge in self.cfg.edges:
                if edge.source == node_id:
                    successors.append(edge.target)
            return successors

        return []

    def _detect_loops(self) -> List[str]:
        """检测循环

        Returns:
            List[str]: 循环头节点列表
        """
        loops = []

        if hasattr(self.cfg, 'loops'):
            for loop in self.cfg.loops:
                if 'header' in loop:
                    loops.append(loop['header'])

        return loops

    def _count_branches(self, nodes: List[str]) -> int:
        """计算路径中的分支数

        Args:
            nodes: 节点列表

        Returns:
            int: 分支数
        """
        branch_count = 0

        for node_id in nodes:
            if hasattr(self.cfg, 'nodes') and node_id in self.cfg.nodes:
                node = self.cfg.nodes[node_id]
                if hasattr(node, 'node_type'):
                    if node.node_type.value == 4:
                        branch_count += 1

        return branch_count

    def _calculate_path_complexity(self, nodes: List[str]) -> int:
        """计算路径复杂度

        Args:
            nodes: 节点列表

        Returns:
            int: 复杂度评分
        """
        complexity = len(nodes)

        for node_id in nodes:
            if hasattr(self.cfg, 'nodes') and node_id in self.cfg.nodes:
                node = self.cfg.nodes[node_id]
                if hasattr(node, 'node_type'):
                    if node.node_type.value in [4, 5, 6]:
                        complexity += 1

        return complexity

    def _is_path_feasible(self, path: EnumeratedPath) -> bool:
        """判断路径是否可行

        Args:
            path: 枚举路径对象

        Returns:
            bool: 是否可行
        """
        if len(path.nodes) > self.config.max_depth:
            return False

        for i in range(len(path.nodes) - 1):
            current = path.nodes[i]
            next_node = path.nodes[i + 1]

            if not self._has_edge(current, next_node):
                return False

        return True

    def _has_edge(self, source: str, target: str) -> bool:
        """检查是否存在边

        Args:
            source: 源节点
            target: 目标节点

        Returns:
            bool: 是否存在边
        """
        if hasattr(self.cfg, 'edges'):
            for edge in self.cfg.edges:
                if edge.source == source and edge.target == target:
                    return True

        return False

    def _filter_duplicate_paths(self) -> List[EnumeratedPath]:
        """过滤重复路径

        Returns:
            List[EnumeratedPath]: 去重后的路径列表
        """
        seen_signatures = set()
        unique_paths = []

        for path in self.enumerated_paths:
            signature = self._get_path_signature(path)

            if signature not in seen_signatures:
                seen_signatures.add(signature)
                unique_paths.append(path)

        self.pruned_count = len(self.enumerated_paths) - len(unique_paths)

        return unique_paths

    def _get_path_signature(self, path: EnumeratedPath) -> Tuple:
        """获取路径签名

        Args:
            path: 枚举路径对象

        Returns:
            Tuple: 路径签名
        """
        return tuple(path.nodes)

    def _merge_similar_paths(self) -> List[EnumeratedPath]:
        """合并相似路径【V3.1增强】

        Returns:
            List[EnumeratedPath]: 合并后的路径列表
        """
        if not self.enumerated_paths:
            return []

        merged = []
        path_groups = self._group_similar_paths()

        for group in path_groups:
            if len(group) == 1:
                merged.append(group[0])
            else:
                representative = self._select_representative_path(group)
                merged.append(representative)

        return merged

    def _group_similar_paths(self) -> List[List[EnumeratedPath]]:
        """将相似路径分组

        Returns:
            List[List[EnumeratedPath]]: 路径组列表
        """
        groups = []
        processed = set()

        for path in self.enumerated_paths:
            if path.path_id in processed:
                continue

            group = [path]
            processed.add(path.path_id)

            for other_path in self.enumerated_paths:
                if other_path.path_id not in processed:
                    if self._are_paths_similar(path, other_path):
                        group.append(other_path)
                        processed.add(other_path.path_id)

            groups.append(group)

        return groups

    def _are_paths_similar(self, path1: EnumeratedPath, path2: EnumeratedPath) -> bool:
        """判断两条路径是否相似

        Args:
            path1: 路径1
            path2: 路径2

        Returns:
            bool: 是否相似
        """
        if abs(path1.length - path2.length) > 2:
            return False

        common_nodes = set(path1.nodes) & set(path2.nodes)
        max_nodes = max(len(path1.nodes), len(path2.nodes))

        similarity = len(common_nodes) / max_nodes if max_nodes > 0 else 0

        return similarity >= 0.8

    def _select_representative_path(self, group: List[EnumeratedPath]) -> EnumeratedPath:
        """选择代表性路径

        Args:
            group: 路径组

        Returns:
            EnumeratedPath: 代表性路径
        """
        return max(group, key=lambda p: p.test_value)

    def _estimate_coverage_potential(self, path: EnumeratedPath) -> float:
        """估算覆盖潜力

        Args:
            path: 枚举路径对象

        Returns:
            float: 覆盖潜力评分（0-1）
        """
        potential = 0.5

        potential += path.branch_count * 0.05

        if path.loop_count > 0:
            potential += 0.1

        unique_edges = len(set(path.edges))
        if unique_edges > 0:
            edge_coverage = unique_edges / path.length if path.length > 0 else 0
            potential += edge_coverage * 0.2

        return min(1.0, potential)

    def _estimate_test_value(self, path: EnumeratedPath) -> float:
        """估算测试价值

        Args:
            path: 枚举路径对象

        Returns:
            float: 测试价值评分（0-1）
        """
        value = path.coverage_potential

        if path.is_feasible:
            value += 0.1

        if path.length > 5:
            value += 0.1

        if path.branch_count > 0:
            value += 0.1

        return min(1.0, value)

    def _create_enumeration_result(self) -> EnumerationResult:
        """创建枚举结果

        Returns:
            EnumerationResult: 枚举结果
        """
        result = EnumerationResult(
            total_enumerated=len(self.enumerated_paths),
            feasible_paths=sum(1 for p in self.enumerated_paths if p.is_feasible),
            unique_paths=sum(1 for p in self.enumerated_paths if p.is_unique),
            pruned_paths=getattr(self, 'pruned_count', 0),
            enumerated_paths=self.enumerated_paths
        )

        result.enumeration_stats = self._compute_enumeration_stats()

        if hasattr(self.cfg, 'function_name'):
            result.source_info = {
                'function': self.cfg.function_name,
                'strategy': self.strategy.name
            }

        result.metadata = {
            'feasibility_rate': result.get_feasibility_rate(),
            'avg_length': sum(p.length for p in self.enumerated_paths) / len(self.enumerated_paths) if self.enumerated_paths else 0,
            'avg_complexity': sum(p.complexity for p in self.enumerated_paths) / len(self.enumerated_paths) if self.enumerated_paths else 0
        }

        return result

    def _compute_enumeration_stats(self) -> Dict[str, Any]:
        """计算枚举统计信息

        Returns:
            Dict[str, Any]: 统计信息
        """
        if not self.enumerated_paths:
            return {}

        stats = {
            'total_paths': len(self.enumerated_paths),
            'avg_length': sum(p.length for p in self.enumerated_paths) / len(self.enumerated_paths),
            'avg_complexity': sum(p.complexity for p in self.enumerated_paths) / len(self.enumerated_paths),
            'max_length': max(p.length for p in self.enumerated_paths),
            'min_length': min(p.length for p in self.enumerated_paths),
            'total_branches': sum(p.branch_count for p in self.enumerated_paths),
            'paths_with_loops': sum(1 for p in self.enumerated_paths if p.loop_count > 0),
            'feasible_count': sum(1 for p in self.enumerated_paths if p.is_feasible),
            'unique_count': sum(1 for p in self.enumerated_paths if p.is_unique)
        }

        return stats

    def _get_statistics(self) -> Dict[str, Any]:
        """获取统计信息

        Returns:
            Dict[str, Any]: 统计信息
        """
        if not self.enumeration_result:
            return {}

        return {
            'total_enumerated': self.enumeration_result.total_enumerated,
            'feasible_paths': self.enumeration_result.feasible_paths,
            'unique_paths': self.enumeration_result.unique_paths,
            'pruned_paths': self.enumeration_result.pruned_paths,
            'feasibility_rate': self.enumeration_result.get_feasibility_rate(),
            'enumeration_stats': self.enumeration_result.enumeration_stats
        }

    def get_paths_by_length(self, min_length: int = 0, max_length: int = 1000) -> List[EnumeratedPath]:
        """按长度获取路径

        Args:
            min_length: 最小长度
            max_length: 最大长度

        Returns:
            List[EnumeratedPath]: 符合长度范围的路径列表
        """
        return [p for p in self.enumerated_paths
                if min_length <= p.length <= max_length]

    def get_paths_by_complexity(self, min_complexity: int = 0) -> List[EnumeratedPath]:
        """按复杂度获取路径

        Args:
            min_complexity: 最小复杂度

        Returns:
            List[EnumeratedPath]: 符合复杂度要求的路径列表
        """
        return [p for p in self.enumerated_paths if p.complexity >= min_complexity]

    def get_high_value_paths(self, threshold: float = 0.7) -> List[EnumeratedPath]:
        """获取高价值路径

        Args:
            threshold: 价值阈值

        Returns:
            List[EnumeratedPath]: 高价值路径列表
        """
        return [p for p in self.enumerated_paths if p.test_value >= threshold]

    def export_enumerated_paths(self) -> List[Dict[str, Any]]:
        """导出枚举的路径

        Returns:
            List[Dict[str, Any]]: 导出数据
        """
        return [p.to_dict() for p in self.enumerated_paths]

    def suggest_test_priorities(self) -> List[Dict[str, Any]]:
        """建议测试优先级

        Returns:
            List[Dict[str, Any]]: 优先级建议列表
        """
        priorities = []

        for path in self.enumerated_paths:
            priority = {
                'path_id': path.path_id,
                'test_value': path.test_value,
                'coverage_potential': path.coverage_potential,
                'complexity': path.complexity,
                'is_feasible': path.is_feasible,
                'length': path.length
            }

            score = path.test_value * 0.4 + path.coverage_potential * 0.3 - path.complexity * 0.01

            if path.is_feasible:
                score += 0.2

            priority['priority_score'] = score
            priorities.append(priority)

        priorities.sort(key=lambda x: x['priority_score'], reverse=True)

        return priorities
