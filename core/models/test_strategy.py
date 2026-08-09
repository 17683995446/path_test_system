"""
Test strategy model for the path testing system.

This module defines the TestStrategy class which represents
a structured approach to testing path coverage.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class StrategyType(Enum):
    """
    Types of test strategies available.

    Attributes:
        RANDOM: Random test case generation.
        BRANCH_COVERAGE: Branch-focused coverage strategy.
        PATH_COVERAGE: Path-based coverage strategy.
        COMBINATION: Combined approach using multiple strategies.
        ADAPTIVE: Adaptive strategy that adjusts based on results.
        CONSTRAINT: Constraint-based test generation.
        GENERATIVE: LLM-driven generative testing approach.
    """
    RANDOM = "random"
    BRANCH_COVERAGE = "branch_coverage"
    PATH_COVERAGE = "path_coverage"
    COMBINATION = "combination"
    ADAPTIVE = "adaptive"
    CONSTRAINT = "constraint"
    GENERATIVE = "generative"


class StrategyPriority(Enum):
    """
    Priority levels for strategy selection.

    Attributes:
        SPEED: Prioritize execution speed.
        COVERAGE: Prioritize code coverage.
        BALANCED: Balance between speed and coverage.
        EXHAUSTIVE: Maximize thoroughness over efficiency.
    """
    SPEED = "speed"
    COVERAGE = "coverage"
    BALANCED = "balanced"
    EXHAUSTIVE = "exhaustive"


@dataclass
class StrategyConfig:
    """
    Configuration parameters for a test strategy.

    Attributes:
        max_iterations: Maximum number of test iterations.
        max_test_cases: Maximum number of test cases to generate.
        timeout_per_case: Timeout for each test case in seconds.
        min_coverage_target: Minimum coverage percentage to achieve.
        seed: Random seed for reproducibility.
        early_stop: Whether to stop early when target is met.
        parallel_execution: Whether to enable parallel test execution.
        verbose: Verbosity level for strategy execution.
    """
    max_iterations: int = 1000
    max_test_cases: int = 100
    timeout_per_case: float = 30.0
    min_coverage_target: float = 80.0
    seed: Optional[int] = None
    early_stop: bool = True
    parallel_execution: bool = True
    verbose: bool = False


@dataclass
class TestStrategy:
    """
    Represents a structured approach to testing path coverage.

    TestStrategy defines how test cases will be generated, selected,
    and executed to achieve optimal path coverage. It encapsulates
    strategy type, configuration, and metadata for execution tracking.

    Attributes:
        strategy_id: Unique identifier for this strategy.
        strategy_type: Type of testing strategy to use.
        name: Human-readable name for the strategy.
        description: Detailed description of the strategy.
        config: Strategy configuration parameters.
        priority: Strategy priority level.
        target_functions: List of function names to target.
        excluded_functions: List of function names to exclude.
        enabled_heuristics: Set of enabled testing heuristics.
        metadata: Additional strategy metadata.
        created_at: Timestamp when the strategy was created.
        updated_at: Timestamp when the strategy was last updated.
        is_active: Whether the strategy is currently active.
        parent_strategy_id: Optional parent strategy ID for inheritance.

    Example:
        >>> strategy = TestStrategy(
        ...     strategy_id="strat_001",
        ...     strategy_type=StrategyType.BRANCH_COVERAGE,
        ...     name="Branch Coverage Strategy",
        ...     description="Focus on achieving high branch coverage",
        ...     config=StrategyConfig(max_iterations=500, min_coverage_target=90.0)
        ... )
        >>> strategy.add_target_function("calculate_total")
        >>> strategy.add_target_function("process_payment")
    """

    strategy_id: str
    strategy_type: StrategyType
    name: str
    description: str = ""
    config: StrategyConfig = field(default_factory=StrategyConfig)
    priority: StrategyPriority = StrategyPriority.BALANCED
    target_functions: list[str] = field(default_factory=list)
    excluded_functions: list[str] = field(default_factory=list)
    enabled_heuristics: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: Optional[float] = None
    updated_at: Optional[float] = None
    is_active: bool = True
    parent_strategy_id: Optional[str] = None

    def __post_init__(self) -> None:
        """
        Validate the test strategy after initialization.
        """
        if not self.strategy_id:
            raise ValueError("strategy_id cannot be empty")
        if not self.name:
            raise ValueError("name cannot be empty")
        if self.config.max_iterations <= 0:
            raise ValueError("max_iterations must be positive")
        if self.config.max_test_cases <= 0:
            raise ValueError("max_test_cases must be positive")
        if self.config.timeout_per_case <= 0:
            raise ValueError("timeout_per_case must be positive")
        if not 0.0 <= self.config.min_coverage_target <= 100.0:
            raise ValueError("min_coverage_target must be between 0.0 and 100.0")

    def add_target_function(self, func_name: str) -> None:
        """
        Add a function to the target list.

        Args:
            func_name: Name of the function to add.
        """
        if func_name not in self.target_functions:
            self.target_functions.append(func_name)

    def remove_target_function(self, func_name: str) -> None:
        """
        Remove a function from the target list.

        Args:
            func_name: Name of the function to remove.
        """
        if func_name in self.target_functions:
            self.target_functions.remove(func_name)

    def add_excluded_function(self, func_name: str) -> None:
        """
        Add a function to the exclusion list.

        Args:
            func_name: Name of the function to exclude.
        """
        if func_name not in self.excluded_functions:
            self.excluded_functions.append(func_name)

    def enable_heuristic(self, heuristic: str) -> None:
        """
        Enable a testing heuristic.

        Args:
            heuristic: Name of the heuristic to enable.
        """
        if heuristic not in self.enabled_heuristics:
            self.enabled_heuristics.append(heuristic)

    def disable_heuristic(self, heuristic: str) -> None:
        """
        Disable a testing heuristic.

        Args:
            heuristic: Name of the heuristic to disable.
        """
        if heuristic in self.enabled_heuristics:
            self.enabled_heuristics.remove(heuristic)

    def is_function_targeted(self, func_name: str) -> bool:
        """
        Check if a function is in the target list.

        Args:
            func_name: Name of the function to check.

        Returns:
            True if the function is targeted, False otherwise.
        """
        if not self.target_functions:
            return True
        return func_name in self.target_functions

    def is_function_excluded(self, func_name: str) -> bool:
        """
        Check if a function is in the exclusion list.

        Args:
            func_name: Name of the function to check.

        Returns:
            True if the function is excluded, False otherwise.
        """
        return func_name in self.excluded_functions

    def should_test_function(self, func_name: str) -> bool:
        """
        Determine if a function should be tested.

        Args:
            func_name: Name of the function to check.

        Returns:
            True if the function should be tested, False otherwise.
        """
        if self.is_function_excluded(func_name):
            return False
        return self.is_function_targeted(func_name)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the test strategy to a dictionary representation.

        Returns:
            Dictionary containing all strategy data.
        """
        return {
            "strategy_id": self.strategy_id,
            "strategy_type": self.strategy_type.value,
            "name": self.name,
            "description": self.description,
            "config": {
                "max_iterations": self.config.max_iterations,
                "max_test_cases": self.config.max_test_cases,
                "timeout_per_case": self.config.timeout_per_case,
                "min_coverage_target": self.config.min_coverage_target,
                "seed": self.config.seed,
                "early_stop": self.config.early_stop,
                "parallel_execution": self.config.parallel_execution,
                "verbose": self.config.verbose,
            },
            "priority": self.priority.value,
            "target_functions": self.target_functions,
            "excluded_functions": self.excluded_functions,
            "enabled_heuristics": self.enabled_heuristics,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_active": self.is_active,
            "parent_strategy_id": self.parent_strategy_id,
        }

    def copy_with_overrides(self, **overrides: Any) -> "TestStrategy":
        """
        Create a copy of the strategy with overridden values.

        Args:
            **overrides: Keyword arguments specifying values to override.

        Returns:
            A new TestStrategy with the specified overrides applied.
        """
        import copy
        return TestStrategy(
            strategy_id=overrides.get("strategy_id", self.strategy_id),
            strategy_type=overrides.get("strategy_type", self.strategy_type),
            name=overrides.get("name", self.name),
            description=overrides.get("description", self.description),
            config=overrides.get("config", copy.deepcopy(self.config)),
            priority=overrides.get("priority", self.priority),
            target_functions=overrides.get("target_functions", list(self.target_functions)),
            excluded_functions=overrides.get("excluded_functions", list(self.excluded_functions)),
            enabled_heuristics=overrides.get("enabled_heuristics", list(self.enabled_heuristics)),
            metadata=overrides.get("metadata", copy.deepcopy(self.metadata)),
            created_at=overrides.get("created_at", self.created_at),
            updated_at=overrides.get("updated_at", self.updated_at),
            is_active=overrides.get("is_active", self.is_active),
            parent_strategy_id=overrides.get("parent_strategy_id", self.parent_strategy_id),
        )
