"""
Layer 5: LLM Adapter Layer (LLM全局能力适配层)

该层负责统一管理和适配各种LLM能力，支持硅基流动等提供商。
"""

from typing import Any, Dict, List, Optional, Callable
import os


class LLMProvider:
    """LLM提供者枚举"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    SILICONFLOW = "siliconflow"
    LOCAL = "local"
    CUSTOM = "custom"


class LLMResponse:
    """LLM响应数据结构"""

    def __init__(
        self,
        content: str,
        model: str,
        usage: Dict[str, int],
        finish_reason: str,
        provider: str = "unknown",
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.content = content
        self.model = model
        self.usage = usage
        self.finish_reason = finish_reason
        self.provider = provider
        self.metadata = metadata or {}

    def __repr__(self) -> str:
        return f"LLMResponse(model={self.model}, usage={self.usage})"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "content": self.content,
            "model": self.model,
            "usage": self.usage,
            "finish_reason": self.finish_reason,
            "provider": self.provider,
            "metadata": self.metadata
        }


class LLMAdapterLayer:
    """
    LLM全局能力适配层

    负责统一管理和适配各种LLM能力，包括：
    - 多LLM提供者支持（OpenAI、硅基流动、Local等）
    - 请求标准化和响应解析
    - 模型选择和路由
    - 错误处理和降级策略
    - 成本控制和限流

    Attributes:
        description: 层的功能描述
        input_type: 输入数据类型
        output_type: 输出数据类型
    """

    description: str = "LLM全局能力适配层 - 统一管理和适配各种LLM能力"
    input_type: str = "PipelineContext"
    output_type: str = "PipelineContext"

    def __init__(
        self,
        default_provider: str = LLMProvider.SILICONFLOW,
        default_model: str = "Qwen/Qwen2.5-7B-Instruct"
    ):
        """
        初始化LLM适配层

        Args:
            default_provider: 默认LLM提供者
            default_model: 默认模型名称
        """
        self._default_provider = default_provider
        self._default_model = default_model
        self._providers: Dict[str, Callable] = {}
        self._model_configs: Dict[str, Dict[str, Any]] = {}
        self._client = None

        self._init_siliconflow_provider()

    def _init_siliconflow_provider(self):
        """初始化硅基流动提供者"""
        try:
            from path_test_system.plugins.siliconflow import SiliconFlowClient, SiliconFlowConfig

            api_key = os.getenv("SILICONFLOW_API_KEY", "")
            if api_key:
                config = SiliconFlowConfig(
                    api_key=api_key,
                    model=self._default_model
                )
                self._client = SiliconFlowClient(config)
                self._providers[LLMProvider.SILICONFLOW] = self._client
        except ImportError:
            pass

    def process(self, context) -> Any:
        """
        处理LLM适配

        Args:
            context: PipelineContext对象，包含：
                - request_id: 请求唯一标识符
                - user_input: 用户输入
                - metadata: 包含llm_config等配置信息

        Returns:
            PipelineContext: 更新后的上下文，包含LLM适配结果：
                - llm_request: 构造的LLM请求对象
                - llm_response: LLM响应结果
                - provider_info: 使用的LLM提供者信息
                - model_info: 使用的模型信息
        """
        llm_config = context.metadata.get("llm_config", {})
        intent = context.metadata.get("intent", "unknown")

        provider = llm_config.get("provider", self._default_provider)
        model = llm_config.get("model", self._default_model)

        prompt = self._construct_prompt(context)

        llm_request = self._build_llm_request(
            prompt=prompt,
            provider=provider,
            model=model,
            intent=intent,
            config=llm_config
        )

        llm_response = self._call_llm(llm_request)

        context.metadata["llm_request"] = llm_request
        context.metadata["llm_response"] = llm_response
        context.metadata["provider_info"] = {
            "provider": provider,
            "model": model,
            "finish_reason": llm_response.finish_reason
        }
        context.metadata["model_info"] = self._model_configs.get(
            model,
            {"name": model, "version": "unknown"}
        )

        return context

    def _construct_prompt(self, context) -> str:
        """构造LLM提示词"""
        intent = context.metadata.get("intent", "unknown")
        entities = context.metadata.get("entities", [])
        parameters = context.metadata.get("parameters", {})

        prompt_parts = [
            f"Task Type: {intent}",
            f"User Request: {context.user_input}",
        ]

        if entities:
            prompt_parts.append(f"Identified Entities: {', '.join([e['value'] for e in entities])}")

        if parameters.get("targets"):
            prompt_parts.append(f"Target Objects: {', '.join(parameters['targets'])}")

        return "\n".join(prompt_parts)

    def _build_llm_request(
        self,
        prompt: str,
        provider: str,
        model: str,
        intent: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """构建LLM请求"""
        return {
            "prompt": prompt,
            "provider": provider,
            "model": model,
            "intent": intent,
            "temperature": config.get("temperature", 0.7),
            "max_tokens": config.get("max_tokens", 2000),
            "top_p": config.get("top_p", 1.0),
            "metadata": {
                "request_type": intent,
                "context_id": config.get("context_id", "unknown")
            }
        }

    def _call_llm(self, request: Dict[str, Any]) -> LLMResponse:
        """调用LLM"""
        provider = request["provider"]
        model = request["model"]

        if provider == LLMProvider.SILICONFLOW and self._client:
            return self._call_siliconflow(request)
        else:
            return self._simulate_llm_call(request)

    def _call_siliconflow(self, request: Dict[str, Any]) -> LLMResponse:
        """调用硅基流动API"""
        try:
            messages = [{"role": "user", "content": request["prompt"]}]

            response = self._client.chat(
                messages=messages,
                model=request["model"],
                temperature=request.get("temperature", 0.7),
                max_tokens=request.get("max_tokens", 2000)
            )

            content = response.choices[0].message.content

            usage = {}
            if hasattr(response, 'usage') and response.usage:
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens or 0,
                    "completion_tokens": response.usage.completion_tokens or 0,
                    "total_tokens": response.usage.total_tokens or 0
                }

            return LLMResponse(
                content=content,
                model=request["model"],
                usage=usage,
                finish_reason=response.choices[0].finish_reason,
                provider=LLMProvider.SILICONFLOW
            )

        except Exception as e:
            return LLMResponse(
                content=f"Error calling SiliconFlow API: {str(e)}",
                model=request["model"],
                usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                finish_reason="error",
                provider=LLMProvider.SILICONFLOW
            )

    def _simulate_llm_call(self, request: Dict[str, Any]) -> LLMResponse:
        """模拟LLM调用（当没有真实API时）"""
        return LLMResponse(
            content=f"[Simulation] Analyzed request for {request['intent']} with model {request['model']}: {request['prompt'][:100]}...",
            model=request["model"],
            usage={
                "prompt_tokens": len(request["prompt"].split()),
                "completion_tokens": 20,
                "total_tokens": len(request["prompt"].split()) + 20
            },
            finish_reason="stop",
            provider=request["provider"]
        )

    def register_provider(self, name: str, provider_func: Callable) -> None:
        """注册LLM提供者"""
        self._providers[name] = provider_func

    def configure_model(self, model: str, config: Dict[str, Any]) -> None:
        """配置模型参数"""
        self._model_configs[model] = config

    def get_supported_providers(self) -> List[str]:
        """获取支持的LLM提供者列表"""
        providers = list(self._providers.keys())
        if not providers:
            providers = [LLMProvider.SILICONFLOW, LLMProvider.OPENAI, LLMProvider.LOCAL]
        return providers

    def set_api_key(self, api_key: str) -> None:
        """设置API密钥并初始化客户端"""
        os.environ["SILICONFLOW_API_KEY"] = api_key
        self._init_siliconflow_provider()
