"""
Task context model for the path testing system.

This module defines the TaskContext class which holds the global
context information for task execution within the testing framework.
"""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class TaskContext:
    """
    Represents the global task context for the path testing system.

    TaskContext provides a centralized container for all contextual information
    needed during task execution, including session information, user preferences,
    runtime state, and shared resources.

    Attributes:
        session_id: Unique identifier for the current testing session.
        root_path: Root directory path for the testing project.
        source_files: List of source file paths to be analyzed.
        test_files: List of test file paths used or generated.
        config: Configuration dictionary with system settings.
        variables: Global variables shared across tasks.
        state: Current runtime state of the testing session.
        user_preferences: User-specific preferences and settings.
        working_directory: Current working directory for task execution.
        environment: Environment variables for the testing session.
        cache_enabled: Whether caching is enabled for the session.
        verbose: Verbosity level for logging and output.
        max_workers: Maximum number of parallel workers.
        session_start_time: Timestamp when the session started.
        session_end_time: Optional timestamp when the session ended.

    Example:
        >>> ctx = TaskContext(
        ...     session_id="session_abc123",
        ...     root_path="/project/root",
        ...     source_files=["src/main.py", "src/utils.py"],
        ...     config={"timeout": 30, "retries": 3}
        ... )
        >>> ctx.variables["last_result"] = {"paths_found": 42}
    """

    session_id: str
    root_path: str
    source_files: list[str] = field(default_factory=list)
    test_files: list[str] = field(default_factory=list)
    config: dict[str, Any] = field(default_factory=dict)
    variables: dict[str, Any] = field(default_factory=dict)
    state: dict[str, Any] = field(default_factory=dict)
    user_preferences: dict[str, Any] = field(default_factory=dict)
    working_directory: Optional[str] = None
    environment: dict[str, str] = field(default_factory=dict)
    cache_enabled: bool = True
    verbose: bool = False
    max_workers: int = 4
    session_start_time: Optional[float] = None
    session_end_time: Optional[float] = None

    def __post_init__(self) -> None:
        """
        Validate and initialize the task context after dataclass initialization.
        """
        if not self.session_id:
            raise ValueError("session_id cannot be empty")
        if not self.root_path:
            raise ValueError("root_path cannot be empty")
        if self.max_workers < 1:
            raise ValueError("max_workers must be at least 1")

    def get_variable(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a variable from the context.

        Args:
            key: The variable key to retrieve.
            default: Default value if the key is not found.

        Returns:
            The variable value or the default.
        """
        return self.variables.get(key, default)

    def set_variable(self, key: str, value: Any) -> None:
        """
        Set a variable in the context.

        Args:
            key: The variable key to set.
            value: The value to assign.
        """
        self.variables[key] = value

    def clear_variables(self) -> None:
        """
        Clear all variables from the context.
        """
        self.variables.clear()

    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a configuration value.

        Args:
            key: The configuration key to retrieve.
            default: Default value if the key is not found.

        Returns:
            The configuration value or the default.
        """
        return self.config.get(key, default)

    def set_config(self, key: str, value: Any) -> None:
        """
        Set a configuration value.

        Args:
            key: The configuration key to set.
            value: The value to assign.
        """
        self.config[key] = value

    def add_source_file(self, path: str) -> None:
        """
        Add a source file to the context.

        Args:
            path: Path to the source file to add.
        """
        if path not in self.source_files:
            self.source_files.append(path)

    def remove_source_file(self, path: str) -> None:
        """
        Remove a source file from the context.

        Args:
            path: Path to the source file to remove.
        """
        if path in self.source_files:
            self.source_files.remove(path)

    def add_test_file(self, path: str) -> None:
        """
        Add a test file to the context.

        Args:
            path: Path to the test file to add.
        """
        if path not in self.test_files:
            self.test_files.append(path)

    def remove_test_file(self, path: str) -> None:
        """
        Remove a test file from the context.

        Args:
            path: Path to the test file to remove.
        """
        if path in self.test_files:
            self.test_files.remove(path)

    def update_state(self, updates: dict[str, Any]) -> None:
        """
        Update the runtime state with new values.

        Args:
            updates: Dictionary of state updates to apply.
        """
        self.state.update(updates)

    def get_state(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a state value.

        Args:
            key: The state key to retrieve.
            default: Default value if the key is not found.

        Returns:
            The state value or the default.
        """
        return self.state.get(key, default)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the task context to a dictionary representation.

        Returns:
            Dictionary containing all context data.
        """
        return {
            "session_id": self.session_id,
            "root_path": self.root_path,
            "source_files": self.source_files,
            "test_files": self.test_files,
            "config": self.config,
            "variables": self.variables,
            "state": self.state,
            "user_preferences": self.user_preferences,
            "working_directory": self.working_directory,
            "environment": self.environment,
            "cache_enabled": self.cache_enabled,
            "verbose": self.verbose,
            "max_workers": self.max_workers,
            "session_start_time": self.session_start_time,
            "session_end_time": self.session_end_time,
        }

    def copy(self) -> "TaskContext":
        """
        Create a deep copy of the task context.

        Returns:
            A new TaskContext instance with copied data.
        """
        import copy
        return TaskContext(
            session_id=self.session_id,
            root_path=self.root_path,
            source_files=list(self.source_files),
            test_files=list(self.test_files),
            config=copy.deepcopy(self.config),
            variables=copy.deepcopy(self.variables),
            state=copy.deepcopy(self.state),
            user_preferences=copy.deepcopy(self.user_preferences),
            working_directory=self.working_directory,
            environment=dict(self.environment),
            cache_enabled=self.cache_enabled,
            verbose=self.verbose,
            max_workers=self.max_workers,
            session_start_time=self.session_start_time,
            session_end_time=self.session_end_time,
        )
