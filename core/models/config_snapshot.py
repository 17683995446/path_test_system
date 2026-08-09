"""
Configuration snapshot model for the path testing system.

This module defines the ConfigSnapshot class which represents an
immutable snapshot of global configuration settings.
"""

from dataclasses import dataclass, field
from typing import Any, FrozenSet, Optional


@dataclass(frozen=True)
class ConfigSnapshot:
    """
    Represents an immutable snapshot of global configuration settings.

    ConfigSnapshot captures a point-in-time view of all system configuration,
    including paths, limits, feature flags, and LLM provider settings.
    Once created, the snapshot is immutable to ensure consistency across
    concurrent task executions.

    Attributes:
        max_path_length: Maximum allowed path length for analysis.
        max_paths_per_function: Maximum number of paths to generate per function.
        max_recursion_depth: Maximum depth for recursive analysis.
        max_execution_time: Maximum execution time in seconds.
        max_memory_mb: Maximum memory usage in megabytes.
        max_workers: Maximum number of parallel workers.
        enable_cache: Whether caching is enabled.
        cache_ttl_seconds: Cache time-to-live in seconds.
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR).
        log_file: Optional path to log file.
        llm_provider: LLM provider name (e.g., "openai", "anthropic").
        llm_model: LLM model identifier.
        llm_temperature: LLM sampling temperature.
        llm_max_tokens: Maximum tokens for LLM responses.
        llm_timeout: LLM request timeout in seconds.
        coverage_threshold: Minimum required coverage percentage.
        branch_coverage_threshold: Minimum required branch coverage percentage.
        enabled_features: Set of enabled feature flags.
        disabled_features: Set of disabled feature flags.
        custom_settings: Custom configuration settings.
        snapshot_id: Unique identifier for this snapshot.
        parent_snapshot_id: Optional parent snapshot ID for configuration inheritance.
        created_at: Timestamp when the snapshot was created.

    Example:
        >>> config = ConfigSnapshot(
        ...     max_path_length=100,
        ...     max_paths_per_function=50,
        ...     llm_provider="openai",
        ...     llm_model="gpt-4",
        ...     enabled_features=frozenset({"auto_test_gen", "path_analysis"})
        ... )
        >>> print(config.llm_model)
        gpt-4
    """

    max_path_length: int = 100
    max_paths_per_function: int = 50
    max_recursion_depth: int = 10
    max_execution_time: float = 300.0
    max_memory_mb: int = 2048
    max_workers: int = 4
    enable_cache: bool = True
    cache_ttl_seconds: int = 3600
    log_level: str = "INFO"
    log_file: Optional[str] = None
    llm_provider: str = "openai"
    llm_model: str = "gpt-4"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 4096
    llm_timeout: float = 60.0
    coverage_threshold: float = 80.0
    branch_coverage_threshold: float = 70.0
    enabled_features: FrozenSet[str] = field(default_factory=frozenset)
    disabled_features: FrozenSet[str] = field(default_factory=frozenset)
    custom_settings: tuple[tuple[str, Any], ...] = field(default_factory=tuple)
    snapshot_id: Optional[str] = None
    parent_snapshot_id: Optional[str] = None
    created_at: Optional[float] = None

    def __post_init__(self) -> None:
        """
        Validate configuration values after dataclass initialization.
        """
        if self.max_path_length <= 0:
            raise ValueError("max_path_length must be positive")
        if self.max_paths_per_function <= 0:
            raise ValueError("max_paths_per_function must be positive")
        if self.max_recursion_depth < 0:
            raise ValueError("max_recursion_depth cannot be negative")
        if self.max_execution_time <= 0:
            raise ValueError("max_execution_time must be positive")
        if self.max_memory_mb <= 0:
            raise ValueError("max_memory_mb must be positive")
        if self.max_workers < 1:
            raise ValueError("max_workers must be at least 1")
        if not 0.0 <= self.llm_temperature <= 2.0:
            raise ValueError("llm_temperature must be between 0.0 and 2.0")
        if self.llm_max_tokens <= 0:
            raise ValueError("llm_max_tokens must be positive")
        if self.llm_timeout <= 0:
            raise ValueError("llm_timeout must be positive")
        if not 0.0 <= self.coverage_threshold <= 100.0:
            raise ValueError("coverage_threshold must be between 0.0 and 100.0")
        if not 0.0 <= self.branch_coverage_threshold <= 100.0:
            raise ValueError("branch_coverage_threshold must be between 0.0 and 100.0")
        valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.log_level not in valid_log_levels:
            raise ValueError(f"log_level must be one of {valid_log_levels}")

    def is_feature_enabled(self, feature: str) -> bool:
        """
        Check if a feature is enabled.

        Args:
            feature: The feature name to check.

        Returns:
            True if the feature is enabled, False otherwise.
        """
        if feature in self.disabled_features:
            return False
        return feature in self.enabled_features or len(self.enabled_features) == 0

    def get_custom_setting(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a custom configuration setting.

        Args:
            key: The setting key to retrieve.
            default: Default value if the key is not found.

        Returns:
            The setting value or the default.
        """
        settings_dict = dict(self.custom_settings)
        return settings_dict.get(key, default)

    def with_overrides(self, **overrides: Any) -> "ConfigSnapshot":
        """
        Create a new snapshot with overridden values.

        Args:
            **overrides: Keyword arguments specifying values to override.

        Returns:
            A new ConfigSnapshot with the specified overrides applied.
        """
        import copy
        current_dict = {
            "max_path_length": self.max_path_length,
            "max_paths_per_function": self.max_paths_per_function,
            "max_recursion_depth": self.max_recursion_depth,
            "max_execution_time": self.max_execution_time,
            "max_memory_mb": self.max_memory_mb,
            "max_workers": self.max_workers,
            "enable_cache": self.enable_cache,
            "cache_ttl_seconds": self.cache_ttl_seconds,
            "log_level": self.log_level,
            "log_file": self.log_file,
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model,
            "llm_temperature": self.llm_temperature,
            "llm_max_tokens": self.llm_max_tokens,
            "llm_timeout": self.llm_timeout,
            "coverage_threshold": self.coverage_threshold,
            "branch_coverage_threshold": self.branch_coverage_threshold,
            "enabled_features": self.enabled_features,
            "disabled_features": self.disabled_features,
            "custom_settings": self.custom_settings,
            "snapshot_id": self.snapshot_id,
            "parent_snapshot_id": self.parent_snapshot_id,
            "created_at": self.created_at,
        }
        current_dict.update(overrides)
        return ConfigSnapshot(**current_dict)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the configuration snapshot to a dictionary representation.

        Returns:
            Dictionary containing all configuration data.
        """
        return {
            "max_path_length": self.max_path_length,
            "max_paths_per_function": self.max_paths_per_function,
            "max_recursion_depth": self.max_recursion_depth,
            "max_execution_time": self.max_execution_time,
            "max_memory_mb": self.max_memory_mb,
            "max_workers": self.max_workers,
            "enable_cache": self.enable_cache,
            "cache_ttl_seconds": self.cache_ttl_seconds,
            "log_level": self.log_level,
            "log_file": self.log_file,
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model,
            "llm_temperature": self.llm_temperature,
            "llm_max_tokens": self.llm_max_tokens,
            "llm_timeout": self.llm_timeout,
            "coverage_threshold": self.coverage_threshold,
            "branch_coverage_threshold": self.branch_coverage_threshold,
            "enabled_features": list(self.enabled_features),
            "disabled_features": list(self.disabled_features),
            "custom_settings": dict(self.custom_settings),
            "snapshot_id": self.snapshot_id,
            "parent_snapshot_id": self.parent_snapshot_id,
            "created_at": self.created_at,
        }
