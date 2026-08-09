"""
Layer 8: Requirement Mapping Layer (需求-代码映射分析层)

该层负责分析用户需求与代码实现之间的映射关系，识别关键路径和测试点。
"""

from typing import Any, Dict, List, Optional, Set, Tuple
from .layer_1_entry import PipelineContext


class MappingType:
    """映射类型枚举"""
    DIRECT = "direct"
    INDIRECT = "indirect"
    DERIVED = "derived"
    TRANSITIVE = "transitive"


class RequirementMappingLayer:
    """
    需求-代码映射分析层

    负责分析用户需求与代码实现之间的映射关系，包括：
    - 需求分解和追踪
    - 代码路径识别
    - 关键函数映射
    - 测试覆盖映射
    - 依赖关系分析

    Attributes:
        description: 层的功能描述
        input_type: 输入数据类型
        output_type: 输出数据类型
    """

    description: str = "需求-代码映射分析层 - 分析需求与代码的映射关系"
    input_type: str = "PipelineContext"
    output_type: str = "PipelineContext"

    def __init__(self):
        self._mapping_cache: Dict[str, List[Dict[str, Any]]] = {}

    def process(self, context: PipelineContext) -> PipelineContext:
        """
        处理需求-代码映射分析

        Args:
            context: PipelineContext对象，包含：
                - request_id: 请求唯一标识符
                - user_input: 用户输入
                - intent: 识别的意图
                - entities: 提取的实体
                - test_scope: 测试范围
                - test_types: 测试类型

        Returns:
            PipelineContext: 更新后的上下文，包含映射分析结果：
                - requirements: 分解的需求列表
                - code_mappings: 需求-代码映射关系
                - key_paths: 关键代码路径
                - test_points: 测试点列表
                - coverage_mapping: 覆盖率映射
                - dependency_graph: 依赖关系图

        Example:
            >>> layer = RequirementMappingLayer()
            >>> ctx = layer.process(pipeline_context)
            >>> print(ctx.metadata["requirements"])  # [{"id": "req_1", "description": "..."}]
            >>> print(ctx.metadata["test_points"])  # [{"function": "login", "type": "unit"}]
        """
        entities = context.metadata.get("entities", [])
        test_scope = context.metadata.get("test_scope", {})
        test_types = context.metadata.get("test_types", [])

        requirements = self._decompose_requirements(context)
        code_mappings = self._analyze_code_mappings(requirements, entities)
        key_paths = self._identify_key_paths(entities, test_scope)
        test_points = self._extract_test_points(code_mappings, test_types)
        coverage_mapping = self._analyze_coverage_mapping(test_points, requirements)
        dependency_graph = self._build_dependency_graph(entities)

        context.metadata["requirements"] = requirements
        context.metadata["code_mappings"] = code_mappings
        context.metadata["key_paths"] = key_paths
        context.metadata["test_points"] = test_points
        context.metadata["coverage_mapping"] = coverage_mapping
        context.metadata["dependency_graph"] = dependency_graph

        return context

    def _decompose_requirements(
        self,
        context: PipelineContext
    ) -> List[Dict[str, Any]]:
        """分解需求"""
        requirements = []

        user_input = context.user_input
        intent = context.metadata.get("intent", "unknown")

        requirements.append({
            "id": f"req_{context.request_id[:8]}",
            "type": "functional",
            "description": user_input,
            "intent": intent,
            "priority": "high",
            "acceptance_criteria": self._generate_acceptance_criteria(intent)
        })

        return requirements

    def _generate_acceptance_criteria(self, intent: str) -> List[str]:
        """生成验收标准"""
        criteria_map = {
            "generate_test": [
                "测试用例成功生成",
                "测试覆盖率达到目标",
                "测试可正常执行"
            ],
            "modify_test": [
                "测试修改成功应用",
                "原有功能不受影响",
                "测试通过率保持"
            ],
            "run_test": [
                "测试执行完成",
                "测试结果准确",
                "无异常错误"
            ],
            "optimize_test": [
                "性能指标提升",
                "覆盖率不降低",
                "执行时间减少"
            ]
        }

        return criteria_map.get(intent, ["满足基本要求"])

    def _analyze_code_mappings(
        self,
        requirements: List[Dict[str, Any]],
        entities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """分析代码映射"""
        mappings = []

        for req in requirements:
            for entity in entities:
                if entity["type"] in ["function", "file"]:
                    mapping = {
                        "requirement_id": req["id"],
                        "code_element": entity["value"],
                        "element_type": entity["type"],
                        "mapping_type": MappingType.DIRECT.value,
                        "confidence": 0.9,
                        "related_requirements": []
                    }
                    mappings.append(mapping)

        return mappings

    def _identify_key_paths(
        self,
        entities: List[Dict[str, Any]],
        test_scope: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """识别关键路径"""
        paths = []

        targets = test_scope.get("primary_targets", [])

        for i, target in enumerate(targets):
            path = {
                "path_id": f"path_{i+1}",
                "entry_point": target,
                "sequence": self._trace_execution_path(target),
                "critical": i == 0,
                "test_priority": "high" if i == 0 else "medium"
            }
            paths.append(path)

        return paths

    def _trace_execution_path(self, entry_point: str) -> List[str]:
        """追踪执行路径"""
        path = [entry_point]

        common_patterns = ["main", "handler", "process", "execute"]

        for pattern in common_patterns:
            if pattern in entry_point.lower():
                path.append(f"{entry_point}_init")
                path.append(f"{entry_point}_validate")
                break

        path.append(f"{entry_point}_cleanup")

        return path

    def _extract_test_points(
        self,
        code_mappings: List[Dict[str, Any]],
        test_types: List[str]
    ) -> List[Dict[str, Any]]:
        """提取测试点"""
        test_points = []

        for mapping in code_mappings:
            for test_type in test_types:
                test_point = {
                    "function": mapping["code_element"],
                    "test_type": test_type,
                    "element_type": mapping["element_type"],
                    "mapping_type": mapping["mapping_type"],
                    "expected_coverage": 0.85,
                    "test_approach": self._determine_test_approach(test_type)
                }
                test_points.append(test_point)

        return test_points

    def _determine_test_approach(self, test_type: str) -> str:
        """确定测试方法"""
        approaches = {
            "positive": "verify_correct_behavior",
            "negative": "verify_error_handling",
            "boundary": "verify_boundary_conditions",
            "edge_case": "verify_edge_scenarios",
            "error_handling": "verify_exception_handling"
        }
        return approaches.get(test_type, "standard_test")

    def _analyze_coverage_mapping(
        self,
        test_points: List[Dict[str, Any]],
        requirements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """分析覆盖率映射"""
        coverage_mapping = {
            "by_requirement": {},
            "by_function": {},
            "overall_coverage": 0.0
        }

        for req in requirements:
            coverage_mapping["by_requirement"][req["id"]] = {
                "covered": False,
                "test_points": [],
                "coverage_percentage": 0.0
            }

        for point in test_points:
            function = point["function"]
            if function not in coverage_mapping["by_function"]:
                coverage_mapping["by_function"][function] = {
                    "covered": True,
                    "test_types": [],
                    "coverage_percentage": 1.0
                }
            coverage_mapping["by_function"][function]["test_types"].append(
                point["test_type"]
            )

        if test_points:
            coverage_mapping["overall_coverage"] = min(
                len(set(p["function"] for p in test_points)) / max(len(coverage_mapping["by_function"]), 1),
                1.0
            )

        return coverage_mapping

    def _build_dependency_graph(
        self,
        entities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """构建依赖关系图"""
        graph = {
            "nodes": [],
            "edges": [],
            "cycles": []
        }

        for entity in entities:
            if entity["type"] in ["function", "file"]:
                node = {
                    "id": entity["value"],
                    "type": entity["type"],
                    "dependencies": self._find_dependencies(entity["value"])
                }
                graph["nodes"].append(node)

                for dep in node["dependencies"]:
                    graph["edges"].append({
                        "from": entity["value"],
                        "to": dep,
                        "type": "depends_on"
                    })

        graph["cycles"] = self._detect_cycles(graph)

        return graph

    def _find_dependencies(self, code_element: str) -> List[str]:
        """查找依赖"""
        dependencies = []

        common_patterns = ["utils", "helper", "service", "client"]

        for pattern in common_patterns:
            if pattern.lower() in code_element.lower():
                dependencies.append(f"{pattern}_module")

        return dependencies

    def _detect_cycles(self, graph: Dict[str, Any]) -> List[List[str]]:
        """检测循环依赖"""
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node: str, path: List[str]) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for edge in graph["edges"]:
                if edge["from"] == node:
                    neighbor = edge["to"]
                    if neighbor not in visited:
                        dfs(neighbor, path.copy())
                    elif neighbor in rec_stack:
                        cycle_start = path.index(neighbor)
                        cycles.append(path[cycle_start:] + [neighbor])

            rec_stack.remove(node)

        for node in graph["nodes"]:
            if node["id"] not in visited:
                dfs(node["id"], [])

        return cycles

    def get_mapping_by_requirement(
        self,
        requirement_id: str
    ) -> List[Dict[str, Any]]:
        """根据需求ID获取映射关系"""
        return self._mapping_cache.get(requirement_id, [])

    def validate_mapping_coverage(self, context: PipelineContext) -> Dict[str, Any]:
        """验证映射覆盖率"""
        test_points = context.metadata.get("test_points", [])
        requirements = context.metadata.get("requirements", [])

        return {
            "total_test_points": len(test_points),
            "total_requirements": len(requirements),
            "coverage_rate": len(test_points) / max(len(requirements), 1),
            "validation_status": "pass" if len(test_points) >= len(requirements) else "needs_improvement"
        }
