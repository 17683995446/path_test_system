"""
硅基流动（SiliconFlow）LLM集成模块

提供对硅基流动API的集成支持，包括：
- 兼容OpenAI API格式的调用
- 多模型支持
- 流式输出支持
"""

import os
from typing import Any, Dict, List, Optional, Iterator
from dataclasses import dataclass


@dataclass
class SiliconFlowConfig:
    """硅基流动配置"""
    api_key: str
    base_url: str = "https://api.siliconflow.cn/v1"
    model: str = "Qwen/Qwen2.5-7B-Instruct"
    max_tokens: int = 4000
    temperature: float = 0.7
    timeout: int = 120


class SiliconFlowClient:
    """
    硅基流动API客户端

    支持调用硅基流动平台上的各种大模型，包括：
    - Qwen系列（免费）
    - DeepSeek系列
    - GLM系列
    - Yi系列
    """

    def __init__(self, config: Optional[SiliconFlowConfig] = None):
        """
        初始化硅基流动客户端

        Args:
            config: 硅基流动配置，如果为None则从环境变量读取
        """
        if config is None:
            api_key = os.getenv("SILICONFLOW_API_KEY", "")
            if not api_key:
                raise ValueError(
                    "请设置SILICONFLOW_API_KEY环境变量，"
                    "或传入SiliconFlowConfig对象"
                )
            config = SiliconFlowConfig(api_key=api_key)

        self.config = config
        self._client = None

    def _get_client(self):
        """获取OpenAI兼容客户端"""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(
                    api_key=self.config.api_key,
                    base_url=self.config.base_url,
                    timeout=self.config.timeout
                )
            except ImportError:
                raise ImportError(
                    "请安装openai库: pip install openai"
                )
        return self._client

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Any:
        """
        发送聊天请求

        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            model: 模型名称，默认为配置中的模型
            temperature: 温度参数
            max_tokens: 最大token数
            stream: 是否流式输出
            **kwargs: 其他参数

        Returns:
            模型响应
        """
        client = self._get_client()

        params = {
            "model": model or self.config.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.config.temperature,
            "max_tokens": max_tokens or self.config.max_tokens,
            "stream": stream,
            **kwargs
        }

        params = {k: v for k, v in params.items() if v is not None}

        if stream:
            return self._stream_chat(client, params)
        else:
            response = client.chat.completions.create(**params)
            return response

    def _stream_chat(self, client, params: Dict) -> Iterator[str]:
        """流式聊天"""
        stream = client.chat.completions.create(**params)
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def completion(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Any:
        """
        发送补全请求

        Args:
            prompt: 提示词
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数

        Returns:
            补全响应
        """
        messages = [{"role": "user", "content": prompt}]
        return self.chat(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

    def embedding(
        self,
        texts: List[str],
        model: str = "BAAI/bge-large-zh-v1.5"
    ) -> List[List[float]]:
        """
        获取文本嵌入向量

        Args:
            texts: 文本列表
            model: 嵌入模型

        Returns:
            嵌入向量列表
        """
        client = self._get_client()

        response = client.embeddings.create(
            model=model,
            input=texts
        )

        return [item.embedding for item in response.data]


# 预配置的免费模型列表
FREE_MODELS = {
    "qwen25-7b": "Qwen/Qwen2.5-7B-Instruct",
    "qwen25-14b": "Qwen/Qwen2.5-14B-Instruct",
    "qwen25-72b": "Qwen/Qwen2.5-72B-Instruct",
    "deepseek-v2.5": "deepseek-ai/DeepSeek-V2.5",
    "glm4-9b": "THUDM/glm-4-9b-chat",
    "yi-1.5-34b": "01-ai/Yi-1.5-34B-Chat",
    "qwen-coder-32b": "Qwen/Qwen2.5-Coder-32B-Instruct",
    "codestral-22b": "mistralai/Codestral-22B-Instruct-v0.1",
}


def get_default_client() -> SiliconFlowClient:
    """
    获取默认的硅基流动客户端

    从环境变量读取配置

    Returns:
        SiliconFlowClient实例
    """
    return SiliconFlowClient()


def create_client(api_key: str, model: str = "Qwen/Qwen2.5-7B-Instruct") -> SiliconFlowClient:
    """
    创建硅基流动客户端

    Args:
        api_key: API密钥
        model: 默认模型

    Returns:
        SiliconFlowClient实例
    """
    config = SiliconFlowConfig(
        api_key=api_key,
        model=model
    )
    return SiliconFlowClient(config)
