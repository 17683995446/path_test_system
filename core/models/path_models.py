"""
Path models for the path testing system.

This module defines data models for representing execution paths,
path segments, and path-related analysis results.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class PathType(Enum):
    """
    Types of execution paths.

    Attributes:
        LINEAR: Simple linear path with no branches.
        CONDITIONAL: Path with conditional branches.
        LOOP: Path containing loop structures.
        RECURSIVE: Path involving recursive calls.
        CALL: Path with function calls.
        EXCEPTION: Path handling exceptions.
        COMPLEX: Complex path combining multiple path types.
    """
    LINEAR = "linear"
    CONDITIONAL = "conditional"
    LOOP = "loop"
    RECURSIVE = "recursive"
    CALL = "call"
    EXCEPTION = "exception"
    COMPLEX = "complex"


class NodeType(Enum):
    """
    Types of nodes in an execution path.

    Attributes:
        ENTRY: Entry point of a function or block.
        EXIT: Exit point of a function or block.
        STATEMENT: Regular statement execution.
        BRANCH: Branch decision point.
        LOOP_START: Start of a loop.
        LOOP_END: End of a loop.
        CALL: Function call.
        RETURN: Return statement.
        RAISE: Exception raise statement.
        CATCH: Exception catch block.
    """
    ENTRY = "entry"
    EXIT = "exit"
    STATEMENT = "statement"
    BRANCH = "branch"
    LOOP_START = "loop_start"
    LOOP_END = "loop_end"
    CALL = "call"
    RETURN = "return"
    RAISE = "raise"
    CATCH = "catch"


class SegmentType(Enum):
    """
    Types of path segments.

    Attributes:
        SEQUENCE: Sequential execution segment.
        BRANCH: Branch segment (if/else).
        LOOP: Loop segment (for/while).
        TRY: Try block segment.
        EXCEPT: Exception handler segment.
        FINALLY: Finally block segment.
        WITH: Context manager segment.
    """
    SEQUENCE = "sequence"
    BRANCH = "branch"
    LOOP = "loop"
    TRY = "try"
    EXCEPT = "except"
    FINALLY = "finally"
    WITH = "with"


@dataclass
class PathNode:
    """
    Represents a single node in an execution path.

    PathNode encapsulates information about a specific point
    in the code path, including its type, location, and metadata.

    Attributes:
        node_id: Unique identifier for this node.
        node_type: Type of the node.
        file_path: Path to the source file.
        line_number: Line number in the source file.
        column_number: Column number in the source file.
        function_name: Name of the containing function.
        code: Source code at this node.
        metadata: Additional node metadata.
        children: Optional list of child node IDs.
        parents: Optional list of parent node IDs.
    """
    node_id: str
    node_type: NodeType
    file_path: str
    line_number: int
    column_number: int = 0
    function_name: Optional[str] = None
    code: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    children: list[str] = field(default_factory=list)
    parents: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """
        Validate node data after initialization.
        """
        if not self.node_id:
            raise ValueError("node_id cannot be empty")
        if self.line_number < 0:
            raise ValueError("line_number cannot be negative")
        if self.column_number < 0:
            raise ValueError("column_number cannot be negative")

    def add_child(self, child_id: str) -> None:
        """
        Add a child node ID.

        Args:
            child_id: ID of the child node to add.
        """
        if child_id not in self.children:
            self.children.append(child_id)

    def add_parent(self, parent_id: str) -> None:
        """
        Add a parent node ID.

        Args:
            parent_id: ID of the parent node to add.
        """
        if parent_id not in self.parents:
            self.parents.append(parent_id)

    def is_branch(self) -> bool:
        """
        Check if this node is a branch point.

        Returns:
            True if the node is a branch, False otherwise.
        """
        return self.node_type == NodeType.BRANCH

    def is_entry(self) -> bool:
        """
        Check if this node is an entry point.

        Returns:
            True if the node is an entry point, False otherwise.
        """
        return self.node_type == NodeType.ENTRY

    def is_exit(self) -> bool:
        """
        Check if this node is an exit point.

        Returns:
            True if the node is an exit point, False otherwise.
        """
        return self.node_type == NodeType.EXIT

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the path node to a dictionary.

        Returns:
            Dictionary containing node data.
        """
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "column_number": self.column_number,
            "function_name": self.function_name,
            "code": self.code,
            "metadata": self.metadata,
            "children": self.children,
            "parents": self.parents,
        }


@dataclass
class PathSegment:
    """
    Represents a segment of an execution path.

    PathSegment groups related nodes together and represents
    a portion of the overall execution path.

    Attributes:
        segment_id: Unique identifier for this segment.
        segment_type: Type of the segment.
        start_node: ID of the starting node.
        end_node: ID of the ending node.
        nodes: List of node IDs in this segment.
        conditions: List of conditions controlling this segment.
        is_covered: Whether this segment was executed.
        execution_count: Number of times this segment was executed.
        depth: Nesting depth of this segment.
        parent_segment_id: Optional parent segment ID.
    """
    segment_id: str
    segment_type: SegmentType
    start_node: str
    end_node: str
    nodes: list[str] = field(default_factory=list)
    conditions: list[str] = field(default_factory=list)
    is_covered: bool = False
    execution_count: int = 0
    depth: int = 0
    parent_segment_id: Optional[str] = None

    def __post_init__(self) -> None:
        """
        Validate segment data after initialization.
        """
        if not self.segment_id:
            raise ValueError("segment_id cannot be empty")
        if not self.start_node:
            raise ValueError("start_node cannot be empty")
        if not self.end_node:
            raise ValueError("end_node cannot be empty")

    def add_node(self, node_id: str) -> None:
        """
        Add a node to this segment.

        Args:
            node_id: ID of the node to add.
        """
        if node_id not in self.nodes:
            self.nodes.append(node_id)

    def add_condition(self, condition: str) -> None:
        """
        Add a condition to this segment.

        Args:
            condition: The condition string to add.
        """
        if condition not in self.conditions:
            self.conditions.append(condition)

    def mark_covered(self) -> None:
        """
        Mark this segment as covered.
        """
        self.is_covered = True
        self.execution_count += 1

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the path segment to a dictionary.

        Returns:
            Dictionary containing segment data.
        """
        return {
            "segment_id": self.segment_id,
            "segment_type": self.segment_type.value,
            "start_node": self.start_node,
            "end_node": self.end_node,
            "nodes": self.nodes,
            "conditions": self.conditions,
            "is_covered": self.is_covered,
            "execution_count": self.execution_count,
            "depth": self.depth,
            "parent_segment_id": self.parent_segment_id,
        }


@dataclass
class Path:
    """
    Represents an execution path through code.

    Path encapsulates all information about a single execution
    path, including its nodes, segments, type, and coverage status.

    Attributes:
        path_id: Unique identifier for this path.
        path_type: Type of the execution path.
        nodes: Ordered list of node IDs in the path.
        segments: List of path segments.
        function_name: Name of the function containing this path.
        file_path: Path to the source file.
        length: Number of nodes in the path.
        complexity: Cyclomatic complexity of the path.
        is_feasible: Whether the path is feasible (can be executed).
        is_covered: Whether the path was executed during testing.
        test_case: Optional test case that exercises this path.
        execution_time: Optional execution time in milliseconds.
        coverage_weight: Weight for coverage prioritization.
        priority: Priority for test generation.
        metadata: Additional path metadata.
    """
    path_id: str
    path_type: PathType
    nodes: list[str] = field(default_factory=list)
    segments: list[PathSegment] = field(default_factory=list)
    function_name: Optional[str] = None
    file_path: Optional[str] = None
    length: int = 0
    complexity: int = 1
    is_feasible: bool = True
    is_covered: bool = False
    test_case: Optional[str] = None
    execution_time: Optional[float] = None
    coverage_weight: float = 1.0
    priority: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """
        Calculate path properties after initialization.
        """
        if not self.path_id:
            raise ValueError("path_id cannot be empty")
        self.length = len(self.nodes)

    def add_node(self, node_id: str) -> None:
        """
        Add a node to the path.

        Args:
            node_id: ID of the node to add.
        """
        if node_id not in self.nodes:
            self.nodes.append(node_id)
            self.length = len(self.nodes)

    def add_segment(self, segment: PathSegment) -> None:
        """
        Add a segment to the path.

        Args:
            segment: Path segment to add.
        """
        self.segments.append(segment)

    def mark_covered(self, test_case: Optional[str] = None) -> None:
        """
        Mark this path as covered.

        Args:
            test_case: Optional test case that covers this path.
        """
        self.is_covered = True
        if test_case:
            self.test_case = test_case
        for segment in self.segments:
            segment.mark_covered()

    def mark_infeasible(self, reason: Optional[str] = None) -> None:
        """
        Mark this path as infeasible.

        Args:
            reason: Optional reason why the path is infeasible.
        """
        self.is_feasible = False
        if reason:
            self.metadata["infeasible_reason"] = reason

    def get_node_count(self) -> int:
        """
        Get the number of nodes in the path.

        Returns:
            Number of nodes.
        """
        return len(self.nodes)

    def get_segment_count(self) -> int:
        """
        Get the number of segments in the path.

        Returns:
            Number of segments.
        """
        return len(self.segments)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the path to a dictionary.

        Returns:
            Dictionary containing path data.
        """
        return {
            "path_id": self.path_id,
            "path_type": self.path_type.value,
            "nodes": self.nodes,
            "segments": [seg.to_dict() for seg in self.segments],
            "function_name": self.function_name,
            "file_path": self.file_path,
            "length": self.length,
            "complexity": self.complexity,
            "is_feasible": self.is_feasible,
            "is_covered": self.is_covered,
            "test_case": self.test_case,
            "execution_time": self.execution_time,
            "coverage_weight": self.coverage_weight,
            "priority": self.priority,
            "metadata": self.metadata,
        }


@dataclass
class ExecutionPath:
    """
    Represents a complete execution path with full context.

    ExecutionPath provides comprehensive information about
    a code path including its representation, analysis results,
    and testing recommendations.

    Attributes:
        execution_id: Unique identifier for this execution.
        path: The path object.
        path_representation: String representation of the path.
        conditions: List of conditions along the path.
        variables: Variables accessed along the path.
        dependencies: External dependencies required.
        recommendations: Testing recommendations for this path.
        risk_level: Risk assessment level (low, medium, high).
        test_suggestions: Suggested test inputs for this path.
        is_prioritized: Whether this path is prioritized for testing.
        created_at: Timestamp when the path was created.
    """
    execution_id: str
    path: Path
    path_representation: str = ""
    conditions: list[str] = field(default_factory=list)
    variables: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    risk_level: str = "medium"
    test_suggestions: list[dict[str, Any]] = field(default_factory=list)
    is_prioritized: bool = False
    created_at: Optional[float] = None

    def __post_init__(self) -> None:
        """
        Validate execution path data after initialization.
        """
        if not self.execution_id:
            raise ValueError("execution_id cannot be empty")
        valid_risk_levels = {"low", "medium", "high", "critical"}
        if self.risk_level not in valid_risk_levels:
            raise ValueError(f"risk_level must be one of {valid_risk_levels}")

    def add_condition(self, condition: str) -> None:
        """
        Add a condition to the path.

        Args:
            condition: The condition string to add.
        """
        if condition not in self.conditions:
            self.conditions.append(condition)

    def add_variable(self, variable: str) -> None:
        """
        Add a variable to the path.

        Args:
            variable: The variable name to add.
        """
        if variable not in self.variables:
            self.variables.append(variable)

    def add_dependency(self, dependency: str) -> None:
        """
        Add a dependency to the path.

        Args:
            dependency: The dependency to add.
        """
        if dependency not in self.dependencies:
            self.dependencies.append(dependency)

    def add_recommendation(self, recommendation: str) -> None:
        """
        Add a testing recommendation.

        Args:
            recommendation: The recommendation to add.
        """
        if recommendation not in self.recommendations:
            self.recommendations.append(recommendation)

    def add_test_suggestion(self, input_values: dict[str, Any], description: str) -> None:
        """
        Add a test suggestion.

        Args:
            input_values: Dictionary of input values for the test.
            description: Description of the test case.
        """
        self.test_suggestions.append({
            "inputs": input_values,
            "description": description,
        })

    def prioritize(self) -> None:
        """
        Mark this path as prioritized for testing.
        """
        self.is_prioritized = True

    def get_coverage_weight(self) -> float:
        """
        Get the coverage weight for this path.

        Returns:
            Coverage weight value.
        """
        base_weight = self.path.coverage_weight
        if self.is_prioritized:
            base_weight *= 2.0
        if self.risk_level == "high":
            base_weight *= 1.5
        elif self.risk_level == "critical":
            base_weight *= 2.0
        return base_weight

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the execution path to a dictionary.

        Returns:
            Dictionary containing all execution path data.
        """
        return {
            "execution_id": self.execution_id,
            "path": self.path.to_dict(),
            "path_representation": self.path_representation,
            "conditions": self.conditions,
            "variables": self.variables,
            "dependencies": self.dependencies,
            "recommendations": self.recommendations,
            "risk_level": self.risk_level,
            "test_suggestions": self.test_suggestions,
            "is_prioritized": self.is_prioritized,
            "created_at": self.created_at,
        }
