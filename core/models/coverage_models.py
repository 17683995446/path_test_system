"""
Coverage models for the path testing system.

This module defines data models for tracking and representing
code coverage metrics during testing.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class CoverageType(Enum):
    """
    Types of coverage metrics tracked by the system.

    Attributes:
        LINE: Line coverage (statements executed).
        BRANCH: Branch coverage (decision points).
        FUNCTION: Function/method coverage.
        CONDITION: Condition coverage (sub-expressions).
        PATH: Path coverage (unique execution paths).
        STATEMENT: Statement coverage.
        TOGGLE: Toggle coverage for boolean conditions.
    """
    LINE = "line"
    BRANCH = "branch"
    FUNCTION = "function"
    CONDITION = "condition"
    PATH = "path"
    STATEMENT = "statement"
    TOGGLE = "toggle"


@dataclass
class CoverageStats:
    """
    Statistics for a single coverage metric.

    Attributes:
        covered: Number of items covered.
        total: Total number of items.
        percentage: Coverage percentage (0.0-100.0).
    """
    covered: int = 0
    total: int = 0
    percentage: float = 0.0

    def __post_init__(self) -> None:
        """
        Calculate percentage after initialization if not provided.
        """
        if self.total > 0 and self.percentage == 0.0:
            self.percentage = (self.covered / self.total) * 100.0
        self.percentage = min(100.0, max(0.0, self.percentage))

    @property
    def is_complete(self) -> bool:
        """
        Check if coverage is 100%.

        Returns:
            True if all items are covered, False otherwise.
        """
        return self.covered >= self.total

    def to_dict(self) -> dict[str, Any]:
        """
        Convert coverage stats to a dictionary.

        Returns:
            Dictionary containing coverage statistics.
        """
        return {
            "covered": self.covered,
            "total": self.total,
            "percentage": round(self.percentage, 2),
        }


@dataclass
class LineCoverage:
    """
    Line coverage information for a source file.

    Attributes:
        file_path: Path to the source file.
        covered_lines: Set of line numbers that were executed.
        executable_lines: Total number of executable lines.
        uncovered_lines: Set of line numbers that were not executed.
        coverage_stats: Aggregated coverage statistics.
    """
    file_path: str
    covered_lines: set[int] = field(default_factory=set)
    executable_lines: int = 0
    uncovered_lines: set[int] = field(default_factory=set)
    coverage_stats: Optional[CoverageStats] = None

    def __post_init__(self) -> None:
        """
        Calculate coverage statistics after initialization.
        """
        self.uncovered_lines = set(range(1, self.executable_lines + 1)) - self.covered_lines
        self.coverage_stats = CoverageStats(
            covered=len(self.covered_lines),
            total=self.executable_lines,
        )

    def add_covered_line(self, line_number: int) -> None:
        """
        Mark a line as covered.

        Args:
            line_number: The line number to mark as covered.
        """
        self.covered_lines.add(line_number)
        self.uncovered_lines.discard(line_number)
        self.coverage_stats = CoverageStats(
            covered=len(self.covered_lines),
            total=self.executable_lines,
        )

    def get_coverage_percentage(self) -> float:
        """
        Get the current coverage percentage.

        Returns:
            Coverage percentage (0.0-100.0).
        """
        return self.coverage_stats.percentage if self.coverage_stats else 0.0

    def to_dict(self) -> dict[str, Any]:
        """
        Convert line coverage to a dictionary.

        Returns:
            Dictionary containing line coverage data.
        """
        return {
            "file_path": self.file_path,
            "covered_lines": sorted(list(self.covered_lines)),
            "executable_lines": self.executable_lines,
            "uncovered_lines": sorted(list(self.uncovered_lines)),
            "coverage_stats": self.coverage_stats.to_dict() if self.coverage_stats else None,
        }


@dataclass
class BranchCoverage:
    """
    Branch coverage information for a source file.

    Attributes:
        file_path: Path to the source file.
        branches: Dictionary mapping branch IDs to coverage status.
        total_branches: Total number of branches.
        covered_branches: Number of branches that were executed.
        uncovered_branches: List of branch IDs not executed.
        coverage_stats: Aggregated coverage statistics.
    """
    file_path: str
    branches: dict[str, bool] = field(default_factory=dict)
    total_branches: int = 0
    covered_branches: int = 0
    uncovered_branches: list[str] = field(default_factory=list)
    coverage_stats: Optional[CoverageStats] = None

    def __post_init__(self) -> None:
        """
        Calculate coverage statistics after initialization.
        """
        self.total_branches = len(self.branches)
        self.covered_branches = sum(1 for covered in self.branches.values() if covered)
        self.uncovered_branches = [bid for bid, covered in self.branches.items() if not covered]
        self.coverage_stats = CoverageStats(
            covered=self.covered_branches,
            total=self.total_branches,
        )

    def mark_branch_covered(self, branch_id: str) -> None:
        """
        Mark a branch as covered.

        Args:
            branch_id: The branch identifier to mark as covered.
        """
        self.branches[branch_id] = True
        if branch_id in self.uncovered_branches:
            self.uncovered_branches.remove(branch_id)
        self.covered_branches = sum(1 for covered in self.branches.values() if covered)
        self.coverage_stats = CoverageStats(
            covered=self.covered_branches,
            total=self.total_branches,
        )

    def get_coverage_percentage(self) -> float:
        """
        Get the current branch coverage percentage.

        Returns:
            Coverage percentage (0.0-100.0).
        """
        return self.coverage_stats.percentage if self.coverage_stats else 0.0

    def to_dict(self) -> dict[str, Any]:
        """
        Convert branch coverage to a dictionary.

        Returns:
            Dictionary containing branch coverage data.
        """
        return {
            "file_path": self.file_path,
            "total_branches": self.total_branches,
            "covered_branches": self.covered_branches,
            "uncovered_branches": self.uncovered_branches,
            "coverage_stats": self.coverage_stats.to_dict() if self.coverage_stats else None,
        }


@dataclass
class FunctionCoverage:
    """
    Function coverage information for a source file or module.

    Attributes:
        file_path: Path to the source file (optional for module-level).
        module_name: Name of the module (optional).
        functions: Dictionary mapping function names to coverage status.
        total_functions: Total number of functions.
        covered_functions: Number of functions that were called.
        uncovered_functions: List of function names not called.
        coverage_stats: Aggregated coverage statistics.
    """
    file_path: Optional[str] = None
    module_name: Optional[str] = None
    functions: dict[str, bool] = field(default_factory=dict)
    total_functions: int = 0
    covered_functions: int = 0
    uncovered_functions: list[str] = field(default_factory=list)
    coverage_stats: Optional[CoverageStats] = None

    def __post_init__(self) -> None:
        """
        Calculate coverage statistics after initialization.
        """
        self.total_functions = len(self.functions)
        self.covered_functions = sum(1 for covered in self.functions.values() if covered)
        self.uncovered_functions = [fname for fname, covered in self.functions.items() if not covered]
        self.coverage_stats = CoverageStats(
            covered=self.covered_functions,
            total=self.total_functions,
        )

    def mark_function_called(self, function_name: str) -> None:
        """
        Mark a function as called.

        Args:
            function_name: The name of the function to mark as called.
        """
        self.functions[function_name] = True
        if function_name in self.uncovered_functions:
            self.uncovered_functions.remove(function_name)
        self.covered_functions = sum(1 for covered in self.functions.values() if covered)
        self.coverage_stats = CoverageStats(
            covered=self.covered_functions,
            total=self.total_functions,
        )

    def get_coverage_percentage(self) -> float:
        """
        Get the current function coverage percentage.

        Returns:
            Coverage percentage (0.0-100.0).
        """
        return self.coverage_stats.percentage if self.coverage_stats else 0.0

    def to_dict(self) -> dict[str, Any]:
        """
        Convert function coverage to a dictionary.

        Returns:
            Dictionary containing function coverage data.
        """
        return {
            "file_path": self.file_path,
            "module_name": self.module_name,
            "total_functions": self.total_functions,
            "covered_functions": self.covered_functions,
            "uncovered_functions": self.uncovered_functions,
            "coverage_stats": self.coverage_stats.to_dict() if self.coverage_stats else None,
        }


@dataclass
class CoverageMetrics:
    """
    Comprehensive coverage metrics for a testing session.

    CoverageMetrics aggregates all coverage data including line,
    branch, function, and path coverage into a unified view.

    Attributes:
        session_id: Unique identifier for the testing session.
        line_coverage: Line coverage data by file.
        branch_coverage: Branch coverage data by file.
        function_coverage: Function coverage data by file/module.
        overall_percentage: Overall coverage percentage.
        coverage_by_type: Coverage statistics by coverage type.
        uncovered_items: List of uncovered items with details.
        coverage_history: Historical coverage data points.
        target_met: Whether the coverage target was achieved.
        generated_at: Timestamp when metrics were generated.
    """
    session_id: str
    line_coverage: dict[str, LineCoverage] = field(default_factory=dict)
    branch_coverage: dict[str, BranchCoverage] = field(default_factory=dict)
    function_coverage: dict[str, FunctionCoverage] = field(default_factory=dict)
    overall_percentage: float = 0.0
    coverage_by_type: dict[str, CoverageStats] = field(default_factory=dict)
    uncovered_items: list[dict[str, Any]] = field(default_factory=list)
    coverage_history: list[dict[str, Any]] = field(default_factory=list)
    target_met: bool = False
    generated_at: Optional[float] = None

    def add_line_coverage(self, file_path: str, coverage: LineCoverage) -> None:
        """
        Add line coverage data for a file.

        Args:
            file_path: Path to the source file.
            coverage: Line coverage data.
        """
        self.line_coverage[file_path] = coverage
        self._recalculate_overall()

    def add_branch_coverage(self, file_path: str, coverage: BranchCoverage) -> None:
        """
        Add branch coverage data for a file.

        Args:
            file_path: Path to the source file.
            coverage: Branch coverage data.
        """
        self.branch_coverage[file_path] = coverage
        self._recalculate_overall()

    def add_function_coverage(self, key: str, coverage: FunctionCoverage) -> None:
        """
        Add function coverage data.

        Args:
            key: Key to store the coverage (file path or module name).
            coverage: Function coverage data.
        """
        self.function_coverage[key] = coverage
        self._recalculate_overall()

    def _recalculate_overall(self) -> None:
        """
        Recalculate the overall coverage percentage.
        """
        all_stats: list[CoverageStats] = []

        for lc in self.line_coverage.values():
            if lc.coverage_stats:
                all_stats.append(lc.coverage_stats)

        for bc in self.branch_coverage.values():
            if bc.coverage_stats:
                all_stats.append(bc.coverage_stats)

        for fc in self.function_coverage.values():
            if fc.coverage_stats:
                all_stats.append(fc.coverage_stats)

        if all_stats:
            total_covered = sum(s.covered for s in all_stats)
            total_total = sum(s.total for s in all_stats)
            self.overall_percentage = (total_covered / total_total * 100.0) if total_total > 0 else 0.0

    def get_coverage_summary(self) -> dict[str, Any]:
        """
        Get a summary of coverage metrics.

        Returns:
            Dictionary containing coverage summary.
        """
        return {
            "session_id": self.session_id,
            "overall_percentage": round(self.overall_percentage, 2),
            "files_with_coverage": len(self.line_coverage),
            "target_met": self.target_met,
            "line_coverage": {
                path: lc.get_coverage_percentage()
                for path, lc in self.line_coverage.items()
            },
            "branch_coverage": {
                path: bc.get_coverage_percentage()
                for path, bc in self.branch_coverage.items()
            },
            "function_coverage": {
                key: fc.get_coverage_percentage()
                for key, fc in self.function_coverage.items()
            },
        }

    def to_dict(self) -> dict[str, Any]:
        """
        Convert coverage metrics to a dictionary.

        Returns:
            Dictionary containing all coverage data.
        """
        return {
            "session_id": self.session_id,
            "line_coverage": {k: v.to_dict() for k, v in self.line_coverage.items()},
            "branch_coverage": {k: v.to_dict() for k, v in self.branch_coverage.items()},
            "function_coverage": {k: v.to_dict() for k, v in self.function_coverage.items()},
            "overall_percentage": round(self.overall_percentage, 2),
            "coverage_by_type": {k: v.to_dict() for k, v in self.coverage_by_type.items()},
            "uncovered_items": self.uncovered_items,
            "coverage_history": self.coverage_history,
            "target_met": self.target_met,
            "generated_at": self.generated_at,
        }
