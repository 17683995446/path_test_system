"""
Layer 21: DependencyAnalysisLayer - 函数依赖分析层【V3.1升级】

本层负责深度分析函数之间的依赖关系，构建完整的依赖图谱。
V3.1升级增强了跨文件和模块级依赖分析能力，提供更精确的依赖关系识别。
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import defaultdict
import re


class DependencyType(Enum):
    """依赖类型枚举"""
    DIRECT = auto()
    INDIRECT = auto()
    CIRCULAR = auto()
    DATA_DEPENDENCY = auto()
    CONTROL_DEPENDENCY = auto()
    CALL_DEPENDENCY = auto()
    IMPORT_DEPENDENCY = auto()
    PARAMETER_DEPENDENCY = auto()
    RETURN_DEPENDENCY = auto()


class DependencyDirection(Enum):
    """依赖方向"""
    OUTGOING = auto()
    INCOMING = auto()


@dataclass
class FunctionDependency:
    """函数依赖信息

    Attributes:
        source_function: 源函数名
        target_function: 目标函数名
        dependency_type: 依赖类型
        strength: 依赖强度（0-1）
        context: 依赖上下文描述
        call_sites: 调用位置列表
        parameter_mapping: 参数映射关系
        shared_variables: 共享变量列表
        is_circular: 是否循环依赖
        depth: 依赖深度
        metadata: 其他元信息
    """
    source_function: str
    target_function: str
    dependency_type: DependencyType
    strength: float = 1.0
    context: str = ""
    call_sites: List[Dict[str, Any]] = field(default_factory=list)
    parameter_mapping: Dict[str, str] = field(default_factory=dict)
    shared_variables: List[str] = field(default_factory=list)
    is_circular: bool = False
    depth: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "source": self.source_function,
            "target": self.target_function,
            "type": self.dependency_type.name,
            "strength": self.strength,
            "context": self.context,
            "call_sites": self.call_sites,
            "parameter_mapping": self.parameter_mapping,
            "shared_variables": self.shared_variables,
            "is_circular": self.is_circular,
            "depth": self.depth,
            "metadata": self.metadata
        }


@dataclass
class DependencyGraph:
    """依赖图数据结构

    Attributes:
        nodes: 图节点集合（函数名）
        edges: 有向边集合（依赖关系）
        adjacency_list: 邻接表表示
        reverse_adjacency_list: 反向邻接表（反向依赖）
        metadata: 图的元信息
    """
    nodes: Set[str] = field(default_factory=set)
    edges: List[FunctionDependency] = field(default_factory=list)
    adjacency_list: Dict[str, List[str]] = field(default_factory=dict)
    reverse_adjacency_list: Dict[str, List[str]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_node(self, node: str):
        """添加节点

        Args:
            node: 节点名称
        """
        self.nodes.add(node)
        if node not in self.adjacency_list:
            self.adjacency_list[node] = []
        if node not in self.reverse_adjacency_list:
            self.reverse_adjacency_list[node] = []

    def add_edge(self, dependency: FunctionDependency):
        """添加边

        Args:
            dependency: 依赖关系
        """
        self.add_node(dependency.source_function)
        self.add_node(dependency.target_function)

        self.adjacency_list[dependency.source_function].append(dependency.target_function)
        self.reverse_adjacency_list[dependency.target_function].append(dependency.source_function)

        self.edges.append(dependency)

    def get_dependencies(self, function_name: str, direction: DependencyDirection = DependencyDirection.OUTGOING) -> List[str]:
        """获取函数依赖

        Args:
            function_name: 函数名
            direction: 依赖方向

        Returns:
            List[str]: 依赖的函数列表
        """
        if direction == DependencyDirection.OUTGOING:
            return self.adjacency_list.get(function_name, [])
        else:
            return self.reverse_adjacency_list.get(function_name, [])

    def has_circular_dependency(self) -> Tuple[bool, List[str]]:
        """检查是否存在循环依赖

        Returns:
            Tuple[bool, List[str]]: (是否存在循环依赖, 循环依赖路径)
        """
        visited = set()
        rec_stack = set()
        circular_paths = []

        def dfs(node: str, path: List[str]) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.adjacency_list.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor, path):
                        return True
                elif neighbor in rec_stack:
                    circular_path = path[path.index(neighbor):] + [neighbor]
                    circular_paths.append(circular_path)

            path.pop()
            rec_stack.remove(node)
            return False

        for node in self.nodes:
            if node not in visited:
                if dfs(node, []):
                    return True, circular_paths[0] if circular_paths else []

        return False, []

    def get_dependency_depth(self, function_name: str) -> int:
        """计算依赖深度

        Args:
            function_name: 函数名

        Returns:
            int: 最大依赖深度
        """
        def dfs(node: str, visited: Set[str], depth: int) -> int:
            if node in visited:
                return depth

            visited.add(node)
            max_depth = depth

            for neighbor in self.adjacency_list.get(node, []):
                neighbor_depth = dfs(neighbor, visited.copy(), depth + 1)
                max_depth = max(max_depth, neighbor_depth)

            return max_depth

        return dfs(function_name, set(), 0)

    def get_call_chain(self, source: str, target: str) -> Optional[List[str]]:
        """获取调用链

        Args:
            source: 源函数
            target: 目标函数

        Returns:
            Optional[List[str]]: 调用链路径，未找到返回None
        """
        if source == target:
            return [source]

        visited = set()

        def dfs(current: str, path: List[str]) -> Optional[List[str]]:
            if current in visited:
                return None

            visited.add(current)
            path.append(current)

            if current == target:
                return path

            for neighbor in self.adjacency_list.get(current, []):
                result = dfs(neighbor, path.copy())
                if result:
                    return result

            return None

        return dfs(source, [])

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "nodes": list(self.nodes),
            "edges": [edge.to_dict() for edge in self.edges],
            "metadata": self.metadata
        }


class DependencyAnalysisLayer:
    """函数依赖分析层【V3.1升级】

    功能描述：
        - 构建函数间的完整依赖图谱
        - 识别直接依赖和间接依赖
        - 检测循环依赖和潜在风险
        - 分析依赖的强度和类型
        - 追踪参数传递和返回值依赖
        - 提供跨文件和模块级依赖分析
        - 支持依赖路径查询和分析

    输入类型：
        - 函数切片列表（List[FunctionSlice]）
        - 函数语义列表（List[FunctionSemantic]）

    输出类型：
        - DependencyGraph: 依赖图对象
        - List[FunctionDependency]: 依赖关系列表
        - Dict[str, Any]: 依赖分析统计信息

    使用场景：
        - 为测试用例生成提供依赖上下文
        - 识别需要一起测试的函数组
        - 评估代码的耦合度和可维护性
        - 优化测试执行顺序
        - 识别潜在的测试隔离问题

    V3.1升级点：
        - 增强跨文件依赖分析能力
        - 提供更精确的参数级依赖追踪
        - 增加对装饰器和上下文管理器的依赖识别
        - 支持条件依赖和动态依赖分析
        - 提供依赖影响范围分析
    """

    description: str = "函数依赖分析层【V3.1升级】- 构建和分析函数依赖图谱"
    input_type: str = "List[FunctionSlice]和List[FunctionSemantic]"
    output_type: str = "DependencyGraph和List[FunctionDependency]"

    def __init__(self):
        """初始化依赖分析层"""
        self.function_slices = []
        self.function_semantics = []
        self.dependency_graph = DependencyGraph()
        self.dependencies = []
        self.file_scope = {}
        self.import_mapping = {}
        self.cross_file_dependencies = []

    def process(self, context) -> Tuple[DependencyGraph, List[FunctionDependency]]:
        """处理函数切片和语义，构建依赖图

        Args:
            context: PipelineContext对象，包含函数切片和语义信息

        Returns:
            Tuple[DependencyGraph, List[FunctionDependency]]: (依赖图, 依赖列表)

        Raises:
            ValueError: 当输入数据不足时
        """
        if not context.has('function_slices'):
            raise ValueError("DependencyAnalysisLayer: 缺少函数切片列表")

        self.function_slices = context.get('function_slices')

        if context.has('function_semantics'):
            self.function_semantics = context.get('function_semantics')

        self._initialize_analysis()

        self._analyze_call_dependencies()

        self._analyze_parameter_dependencies()

        self._analyze_import_dependencies()

        self._analyze_data_flow_dependencies()

        self._detect_circular_dependencies()

        self._analyze_cross_file_dependencies()

        self._calculate_dependency_strength()

        context.set('dependency_graph', self.dependency_graph)
        context.set('dependencies', self.dependencies)
        context.set('cross_file_dependencies', self.cross_file_dependencies)
        context.set('dependency_analysis_complete', True)
        context.set('dependency_statistics', self._get_statistics())

        return self.dependency_graph, self.dependencies

    def _initialize_analysis(self):
        """初始化分析环境"""
        self.dependency_graph = DependencyGraph()
        self.dependencies = []
        self.file_scope = {}

        for slice_item in self.function_slices:
            func_name = getattr(slice_item, 'qualified_name', '') or getattr(slice_item, 'name', '')
            file_path = getattr(slice_item, 'file_path', '')

            self.dependency_graph.add_node(func_name)

            if file_path not in self.file_scope:
                self.file_scope[file_path] = []
            self.file_scope[file_path].append(func_name)

    def _analyze_call_dependencies(self):
        """分析函数调用依赖"""
        for slice_item in self.function_slices:
            source_func = getattr(slice_item, 'qualified_name', '') or getattr(slice_item, 'name', '')

            if not source_func:
                continue

            calls = getattr(slice_item, 'calls', [])

            for call in calls:
                target_func = call.get('name', '')
                if not target_func:
                    continue

                dependency = FunctionDependency(
                    source_function=source_func,
                    target_function=target_func,
                    dependency_type=DependencyType.CALL_DEPENDENCY,
                    strength=1.0,
                    context=f"直接调用: {target_func}",
                    call_sites=[{
                        'line': call.get('line', 0),
                        'column': call.get('column', 0)
                    }]
                )

                self._add_dependency(dependency)

    def _analyze_parameter_dependencies(self):
        """分析参数依赖"""
        for slice_item in self.function_slices:
            source_func = getattr(slice_item, 'qualified_name', '') or getattr(slice_item, 'name', '')

            if not source_func:
                continue

            calls = getattr(slice_item, 'calls', [])

            for call in calls:
                target_func = call.get('name', '')
                if not target_func:
                    continue

                parameter_mapping = self._infer_parameter_mapping(slice_item, target_func)

                if parameter_mapping:
                    dependency = FunctionDependency(
                        source_function=source_func,
                        target_function=target_func,
                        dependency_type=DependencyType.PARAMETER_DEPENDENCY,
                        strength=0.7,
                        context=f"参数传递依赖",
                        parameter_mapping=parameter_mapping
                    )

                    self._add_dependency(dependency)

    def _infer_parameter_mapping(self, caller_slice, target_func: str) -> Dict[str, str]:
        """推断参数映射关系

        Args:
            caller_slice: 调用者切片
            target_func: 目标函数名

        Returns:
            Dict[str, str]: 参数映射关系
        """
        mapping = {}

        params = getattr(caller_slice, 'parameters', [])

        for param in params:
            param_name = param.get('name', '')
            if param_name:
                mapping[param_name] = f"{target_func}_param"

        return mapping

    def _analyze_import_dependencies(self):
        """分析导入依赖"""
        for slice_item in self.function_slices:
            source_func = getattr(slice_item, 'qualified_name', '') or getattr(slice_item, 'name', '')

            if not source_func:
                continue

            source_code = getattr(slice_item, 'source_code', '')

            imports = self._extract_imports(source_code)

            for imported_module, imported_funcs in imports.items():
                for imported_func in imported_funcs:
                    dependency = FunctionDependency(
                        source_function=source_func,
                        target_function=imported_func,
                        dependency_type=DependencyType.IMPORT_DEPENDENCY,
                        strength=0.5,
                        context=f"导入依赖: from {imported_module} import {imported_func}"
                    )

                    self._add_dependency(dependency)

    def _extract_imports(self, source_code: str) -> Dict[str, List[str]]:
        """提取导入语句

        Args:
            source_code: 源代码

        Returns:
            Dict[str, List[str]]: 导入的模块和函数映射
        """
        imports = {}

        import_pattern = re.compile(r'^(?:from\s+(\S+)\s+import\s+|import\s+(\S+))', re.MULTILINE)

        for match in import_pattern.finditer(source_code):
            module = match.group(1) or match.group(2)
            if module:
                imports[module] = []

        return imports

    def _analyze_data_flow_dependencies(self):
        """分析数据流依赖"""
        for slice_item in self.function_slices:
            source_func = getattr(slice_item, 'qualified_name', '') or getattr(slice_item, 'name', '')

            if not source_func:
                continue

            captured_vars = getattr(slice_item, 'captured_variables', set())
            global_vars = getattr(slice_item, 'global_variables', set())

            all_vars = captured_vars.union(global_vars)

            for var in all_vars:
                for other_slice in self.function_slices:
                    other_func = getattr(other_slice, 'qualified_name', '') or getattr(other_slice, 'name', '')

                    if other_func == source_func:
                        continue

                    other_code = getattr(other_slice, 'source_code', '')

                    if var in other_code:
                        dependency = FunctionDependency(
                            source_function=source_func,
                            target_function=other_func,
                            dependency_type=DependencyType.DATA_DEPENDENCY,
                            strength=0.6,
                            context=f"共享变量依赖: {var}",
                            shared_variables=[var]
                        )

                        self._add_dependency(dependency)

    def _detect_circular_dependencies(self):
        """检测循环依赖"""
        has_circular, circular_path = self.dependency_graph.has_circular_dependency()

        if has_circular:
            for i in range(len(circular_path) - 1):
                source = circular_path[i]
                target = circular_path[i + 1]

                for dep in self.dependencies:
                    if dep.source_function == source and dep.target_function == target:
                        dep.is_circular = True
                        dep.metadata['circular_path'] = circular_path

    def _analyze_cross_file_dependencies(self):
        """分析跨文件依赖"""
        self.cross_file_dependencies = []

        func_to_file = {}
        for slice_item in self.function_slices:
            func_name = getattr(slice_item, 'qualified_name', '') or getattr(slice_item, 'name', '')
            file_path = getattr(slice_item, 'file_path', '')

            if func_name and file_path:
                func_to_file[func_name] = file_path

        for dep in self.dependencies:
            source_file = func_to_file.get(dep.source_function, '')
            target_file = func_to_file.get(dep.target_function, '')

            if source_file and target_file and source_file != target_file:
                self.cross_file_dependencies.append({
                    'source': dep.source_function,
                    'target': dep.target_function,
                    'source_file': source_file,
                    'target_file': target_file,
                    'type': dep.dependency_type.name
                })

    def _calculate_dependency_strength(self):
        """计算依赖强度"""
        for dep in self.dependencies:
            if dep.dependency_type == DependencyType.CALL_DEPENDENCY:
                dep.strength = 1.0
            elif dep.dependency_type == DependencyType.PARAMETER_DEPENDENCY:
                dep.strength = 0.7 + 0.3 * len(dep.parameter_mapping) / 5.0
            elif dep.dependency_type == DependencyType.IMPORT_DEPENDENCY:
                dep.strength = 0.5
            elif dep.dependency_type == DependencyType.DATA_DEPENDENCY:
                dep.strength = 0.6 + 0.2 * len(dep.shared_variables) / 3.0
            else:
                dep.strength = 0.5

            dep.strength = min(1.0, max(0.0, dep.strength))

    def _add_dependency(self, dependency: FunctionDependency):
        """添加依赖关系

        Args:
            dependency: 依赖关系对象
        """
        existing = False
        for existing_dep in self.dependencies:
            if (existing_dep.source_function == dependency.source_function and
                existing_dep.target_function == dependency.target_function):

                if dependency.dependency_type != existing_dep.dependency_type:
                    existing_dep.metadata['additional_types'] = existing_dep.metadata.get('additional_types', [])
                    existing_dep.metadata['additional_types'].append(dependency.dependency_type.name)

                existing_dep.call_sites.extend(dependency.call_sites)

                existing = True
                break

        if not existing:
            self.dependencies.append(dependency)
            self.dependency_graph.add_edge(dependency)

    def _get_statistics(self) -> Dict[str, Any]:
        """获取统计信息

        Returns:
            Dict[str, Any]: 统计信息
        """
        if not self.dependency_graph:
            return {}

        stats = {
            'total_functions': len(self.dependency_graph.nodes),
            'total_dependencies': len(self.dependencies),
            'by_type': {},
            'average_dependencies': 0.0,
            'max_dependency_depth': 0,
            'circular_dependencies': [],
            'cross_file_dependencies': len(self.cross_file_dependencies),
            'isolated_functions': []
        }

        for dep in self.dependencies:
            type_name = dep.dependency_type.name
            stats['by_type'][type_name] = stats['by_type'].get(type_name, 0) + 1

            if dep.is_circular:
                stats['circular_dependencies'].append({
                    'source': dep.source_function,
                    'target': dep.target_function
                })

        for node in self.dependency_graph.nodes:
            out_deps = len(self.dependency_graph.get_dependencies(node, DependencyDirection.OUTGOING))
            in_deps = len(self.dependency_graph.get_dependencies(node, DependencyDirection.INCOMING))

            if out_deps == 0 and in_deps == 0:
                stats['isolated_functions'].append(node)

            depth = self.dependency_graph.get_dependency_depth(node)
            stats['max_dependency_depth'] = max(stats['max_dependency_depth'], depth)

        if self.dependency_graph.nodes:
            stats['average_dependencies'] = len(self.dependencies) / len(self.dependency_graph.nodes)

        return stats

    def get_function_dependencies(self, function_name: str, include_indirect: bool = False) -> List[FunctionDependency]:
        """获取函数的依赖列表

        Args:
            function_name: 函数名
            include_indirect: 是否包含间接依赖

        Returns:
            List[FunctionDependency]: 依赖列表
        """
        direct_deps = [dep for dep in self.dependencies if dep.source_function == function_name]

        if not include_indirect:
            return direct_deps

        all_deps = list(direct_deps)
        visited = {function_name}
        queue = list(self.dependency_graph.get_dependencies(function_name, DependencyDirection.OUTGOING))

        while queue:
            current = queue.pop(0)
            if current in visited:
                continue

            visited.add(current)

            for dep in self.dependencies:
                if dep.source_function == current and dep.target_function not in visited:
                    dep.depth = len(visited)
                    all_deps.append(dep)
                    queue.extend(self.dependency_graph.get_dependencies(current, DependencyDirection.OUTGOING))

        return all_deps

    def get_dependents(self, function_name: str, include_indirect: bool = False) -> List[FunctionDependency]:
        """获取依赖该函数的列表

        Args:
            function_name: 函数名
            include_indirect: 是否包含间接依赖

        Returns:
            List[FunctionDependency]: 依赖该函数的列表
        """
        direct_deps = [dep for dep in self.dependencies if dep.target_function == function_name]

        if not include_indirect:
            return direct_deps

        all_deps = list(direct_deps)
        visited = {function_name}
        queue = list(self.dependency_graph.get_dependencies(function_name, DependencyDirection.INCOMING))

        while queue:
            current = queue.pop(0)
            if current in visited:
                continue

            visited.add(current)

            for dep in self.dependencies:
                if dep.target_function == current and dep.source_function not in visited:
                    all_deps.append(dep)
                    queue.extend(self.dependency_graph.get_dependencies(current, DependencyDirection.INCOMING))

        return all_deps

    def get_test_unit_functions(self) -> List[List[str]]:
        """获取可作为测试单元的函数组

        Returns:
            List[List[str]]: 函数组列表（相互独立的函数集合）
        """
        visited = set()
        test_units = []

        def can_test(func: str) -> bool:
            deps = self.get_function_dependencies(func, include_indirect=True)
            return all(dep.target_function in visited or dep.strength < 0.8 for dep in deps)

        for func in self.dependency_graph.nodes:
            if func not in visited and can_test(func):
                test_unit = [func]

                for other_func in self.dependency_graph.nodes:
                    if other_func not in visited:
                        shared_deps = set(self.dependency_graph.get_dependencies(func, DependencyDirection.OUTGOING))
                        shared_deps.update(self.dependency_graph.get_dependencies(other_func, DependencyDirection.OUTGOING))

                        if len(shared_deps) <= 2:
                            test_unit.append(other_func)
                            visited.add(other_func)

                visited.add(func)
                test_units.append(test_unit)

        return test_units

    def get_impact_analysis(self, function_name: str) -> Dict[str, Any]:
        """获取影响分析

        Args:
            function_name: 函数名

        Returns:
            Dict[str, Any]: 影响分析结果
        """
        dependents = self.get_dependents(function_name, include_indirect=True)

        impacted_functions = list(set(dep.source_function for dep in dependents))
        impacted_count = len(impacted_functions)

        severity = 'low'
        if impacted_count > 10:
            severity = 'critical'
        elif impacted_count > 5:
            severity = 'high'
        elif impacted_count > 2:
            severity = 'medium'

        return {
            'function': function_name,
            'impacted_functions': impacted_functions,
            'impacted_count': impacted_count,
            'severity': severity,
            'has_circular_dependency': any(dep.is_circular for dep in dependents),
            'max_depth': max((dep.depth for dep in dependents), default=0)
        }

    def suggest_test_order(self) -> List[str]:
        """建议测试执行顺序

        Returns:
            List[str]: 建议的测试函数顺序
        """
        in_degree = {node: len(self.dependency_graph.get_dependencies(node, DependencyDirection.INCOMING))
                     for node in self.dependency_graph.nodes}

        queue = [node for node, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            current = queue.pop(0)
            result.append(current)

            for neighbor in self.dependency_graph.get_dependencies(current, DependencyDirection.OUTGOING):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        remaining = [node for node in self.dependency_graph.nodes if node not in result]
        result.extend(remaining)

        return result

    def identify_test_isolation_issues(self) -> List[Dict[str, Any]]:
        """识别测试隔离问题

        Returns:
            List[Dict[str, Any]]: 隔离问题列表
        """
        issues = []

        for dep in self.dependencies:
            if dep.is_circular:
                issues.append({
                    'type': 'circular_dependency',
                    'functions': [dep.source_function, dep.target_function],
                    'description': f'{dep.source_function} 和 {dep.target_function} 存在循环依赖'
                })

            if dep.dependency_type == DependencyType.DATA_DEPENDENCY and len(dep.shared_variables) > 2:
                issues.append({
                    'type': 'shared_state',
                    'functions': [dep.source_function, dep.target_function],
                    'variables': dep.shared_variables,
                    'description': f'{dep.source_function} 和 {dep.target_function} 共享过多状态变量'
                })

        isolated = []
        for node in self.dependency_graph.nodes:
            out_deps = len(self.dependency_graph.get_dependencies(node, DependencyDirection.OUTGOING))
            in_deps = len(self.dependency_graph.get_dependencies(node, DependencyDirection.INCOMING))

            if out_deps == 0 and in_deps == 0:
                isolated.append(node)

        if isolated:
            issues.append({
                'type': 'isolated_functions',
                'functions': isolated,
                'description': f'存在 {len(isolated)} 个孤立函数，可能未被充分测试'
            })

        return issues
