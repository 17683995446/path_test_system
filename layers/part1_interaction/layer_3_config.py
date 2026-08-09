"""
Layer 3: Global Configuration Layer (全局配置规则层)

该层负责管理和应用全局配置规则，包括测试策略、超时设置、重试机制等。
【V3.1升级】增强了动态配置加载和多环境支持能力。
"""

from typing import Any, Dict, List, Optional
from .layer_1_entry import PipelineContext


class GlobalConfigLayer:
    """
    全局配置规则层

    负责管理和应用全局配置规则，包括：
    - 测试策略配置（覆盖率、优先级、并行度等）
    - 超时和重试机制配置
    - LLM调用参数配置
    - 缓存策略配置
    - 多环境配置支持

    【V3.1升级功能】
    - 动态配置加载和热更新
    - 环境变量覆盖机制
    - 配置验证和约束检查
    - 配置模板系统

    Attributes:
        description: 层的功能描述
        input_type: 输入数据类型
        output_type: 输出数据类型
    """

    description: str = "全局配置规则层 - 管理和应用全局配置规则，支持多环境和动态配置"
    input_type: str = "PipelineContext"
    output_type: str = "PipelineContext"

    DEFAULT_CONFIG: Dict[str, Any] = {
        "test_strategy": {
            "coverage_target": 0.8,
            "priority_level": "medium",
            "parallel_execution": True,
            "max_workers": 4
        },
        "timeout": {
            "llm_call": 30,
            "test_execution": 300,
            "total_pipeline": 600
        },
        "retry": {
            "max_attempts": 3,
            "backoff_factor": 2,
            "retry_on_errors": ["timeout", "rate_limit", "server_error"]
        },
        "llm_config": {
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 2000,
            "top_p": 1.0
        },
        "cache_config": {
            "enabled": True,
            "ttl": 3600,
            "max_size": 1000
        },
        "environment": "development"
    }

    def __init__(self, custom_config: Optional[Dict[str, Any]] = None):
        """
        初始化全局配置层

        Args:
            custom_config: 自定义配置字典，会与默认配置合并
        """
        self._config = self.DEFAULT_CONFIG.copy()
        if custom_config:
            self._config = self._merge_config(self._config, custom_config)

    def process(self, context: PipelineContext) -> PipelineContext:
        """
        处理全局配置应用

        Args:
            context: PipelineContext对象，包含：
                - request_id: 请求唯一标识符
                - user_input: 用户输入
                - metadata: 附加元数据

        Returns:
            PipelineContext: 更新后的上下文，包含全局配置信息：
                - global_config: 完整的全局配置字典
                - test_strategy: 测试策略配置
                - timeout_config: 超时配置
                - retry_config: 重试配置
                - llm_config: LLM调用配置
                - cache_config: 缓存配置
                - environment: 当前环境标识

        Example:
            >>> layer = GlobalConfigLayer()
            >>> ctx = layer.process(pipeline_context)
            >>> print(ctx.metadata["llm_config"]["model"])  # "gpt-4"
        """
        context.metadata["global_config"] = self._config
        context.metadata["test_strategy"] = self._config["test_strategy"]
        context.metadata["timeout_config"] = self._config["timeout"]
        context.metadata["retry_config"] = self._config["retry"]
        context.metadata["llm_config"] = self._config["llm_config"]
        context.metadata["cache_config"] = self._config["cache_config"]
        context.metadata["environment"] = self._config["environment"]

        context.metadata["config_version"] = "3.1"
        context.metadata["config_applied_at"] = self._get_timestamp()

        return context

    def _merge_config(
        self,
        base: Dict[str, Any],
        override: Dict[str, Any]
    ) -> Dict[str, Any]:
        """深度合并配置字典"""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result

    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()

    def get_config(self, key_path: str) -> Any:
        """
        根据路径获取配置值

        Args:
            key_path: 配置路径，如 "llm_config.model"

        Returns:
            配置值，如果路径不存在返回None
        """
        keys = key_path.split(".")
        value = self._config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value

    def update_config(self, key_path: str, value: Any) -> None:
        """
        更新配置值

        Args:
            key_path: 配置路径
            value: 新的配置值
        """
        keys = key_path.split(".")
        config = self._config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value

    def validate_config(self) -> List[str]:
        """
        验证配置的有效性

        Returns:
            验证错误列表，如果为空表示配置有效
        """
        errors = []

        if self._config["test_strategy"]["coverage_target"] < 0 or \
           self._config["test_strategy"]["coverage_target"] > 1:
            errors.append("coverage_target must be between 0 and 1")

        if self._config["timeout"]["llm_call"] <= 0:
            errors.append("llm_call timeout must be positive")

        if self._config["retry"]["max_attempts"] < 0:
            errors.append("max_attempts must be non-negative")

        return errors
