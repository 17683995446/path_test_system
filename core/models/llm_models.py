"""
LLM models for the path testing system.

This module defines LLMRequest and LLMResponse classes for
interfacing with Large Language Model providers.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class MessageRole(Enum):
    """
    Roles for messages in LLM conversations.

    Attributes:
        SYSTEM: System-level instructions or context.
        USER: User-generated content.
        ASSISTANT: LLM-generated responses.
        FUNCTION: Function call results or tool outputs.
    """
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


@dataclass
class Message:
    """
    Represents a single message in an LLM conversation.

    Attributes:
        role: The role of the message sender.
        content: The content of the message.
        name: Optional name for function calls.
        function_call: Optional function call specification.
    """
    role: MessageRole
    content: str
    name: Optional[str] = None
    function_call: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the message to a dictionary representation.

        Returns:
            Dictionary containing the message data.
        """
        result: dict[str, Any] = {
            "role": self.role.value,
            "content": self.content,
        }
        if self.name:
            result["name"] = self.name
        if self.function_call:
            result["function_call"] = self.function_call
        return result


@dataclass
class LLMRequest:
    """
    Represents a request to an LLM provider.

    LLMRequest encapsulates all parameters needed to make a request
    to a Large Language Model, including model selection, messages,
    and generation parameters.

    Attributes:
        model: The LLM model identifier (e.g., "gpt-4", "claude-3").
        messages: List of conversation messages.
        temperature: Sampling temperature for generation (0.0-2.0).
        max_tokens: Maximum number of tokens to generate.
        top_p: Nucleus sampling probability threshold.
        frequency_penalty: Penalty for token frequency.
        presence_penalty: Penalty for token presence.
        stop_sequences: Optional list of stop sequences.
        system_prompt: Optional system prompt to prepend.
        functions: Optional list of function specifications for tool use.
        function_call: Optional function call request.
        timeout: Request timeout in seconds.
        retry_count: Number of times the request has been retried.
        metadata: Additional request metadata.

    Example:
        >>> request = LLMRequest(
        ...     model="gpt-4",
        ...     messages=[
        ...         Message(role=MessageRole.SYSTEM, content="You are a helpful assistant."),
        ...         Message(role=MessageRole.USER, content="Analyze this code path.")
        ...     ],
        ...     temperature=0.7,
        ...     max_tokens=1000
        ... )
    """

    model: str
    messages: list[Message] = field(default_factory=list)
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: Optional[list[str]] = None
    system_prompt: Optional[str] = None
    functions: Optional[list[dict[str, Any]]] = None
    function_call: Optional[str] = None
    timeout: float = 60.0
    retry_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """
        Validate LLM request parameters after initialization.
        """
        if not self.model:
            raise ValueError("model cannot be empty")
        if not self.messages and not self.system_prompt:
            raise ValueError("At least one message or system_prompt is required")
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("temperature must be between 0.0 and 2.0")
        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        if not 0.0 <= self.top_p <= 1.0:
            raise ValueError("top_p must be between 0.0 and 1.0")
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")

    def add_message(self, role: MessageRole, content: str, name: Optional[str] = None) -> None:
        """
        Add a message to the request.

        Args:
            role: The role of the message sender.
            content: The content of the message.
            name: Optional name for the message sender.
        """
        self.messages.append(Message(role=role, content=content, name=name))

    def add_system_message(self, content: str) -> None:
        """
        Add a system message to the request.

        Args:
            content: The system message content.
        """
        self.add_message(MessageRole.SYSTEM, content)

    def add_user_message(self, content: str) -> None:
        """
        Add a user message to the request.

        Args:
            content: The user message content.
        """
        self.add_message(MessageRole.USER, content)

    def add_assistant_message(self, content: str) -> None:
        """
        Add an assistant message to the request.

        Args:
            content: The assistant message content.
        """
        self.add_message(MessageRole.ASSISTANT, content)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the LLM request to a dictionary representation.

        Returns:
            Dictionary containing all request data.
        """
        result: dict[str, Any] = {
            "model": self.model,
            "messages": [msg.to_dict() for msg in self.messages],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "timeout": self.timeout,
            "retry_count": self.retry_count,
            "metadata": self.metadata,
        }
        if self.stop_sequences:
            result["stop_sequences"] = self.stop_sequences
        if self.system_prompt:
            result["system_prompt"] = self.system_prompt
        if self.functions:
            result["functions"] = self.functions
        if self.function_call:
            result["function_call"] = self.function_call
        return result


@dataclass
class LLMResponse:
    """
    Represents a response from an LLM provider.

    LLMResponse encapsulates the generated content and metadata
    returned by the LLM provider.

    Attributes:
        content: The generated text content.
        model: The model that generated the response.
        finish_reason: Reason for completion (stop, length, function_call, etc.).
        usage: Token usage statistics.
        id: Unique identifier for the response.
        created: Timestamp of response creation.
        prompt_tokens: Number of tokens in the prompt.
        completion_tokens: Number of tokens in the completion.
        total_tokens: Total number of tokens used.
        function_call: Optional function call from the response.
        error: Optional error message if the request failed.
        raw_response: Raw response data from the provider.
        latency_ms: Request latency in milliseconds.

    Example:
        >>> response = LLMResponse(
        ...     content="Based on the analysis, this path handles edge cases...",
        ...     model="gpt-4",
        ...     finish_reason="stop",
        ...     usage={"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}
        ... )
        >>> print(f"Generated {response.completion_tokens} tokens")
    """

    content: str
    model: str
    finish_reason: Optional[str] = None
    usage: Optional[dict[str, int]] = None
    id: Optional[str] = None
    created: Optional[int] = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    function_call: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    raw_response: Optional[dict[str, Any]] = None
    latency_ms: Optional[float] = None

    def __post_init__(self) -> None:
        """
        Initialize usage statistics if provided as a dict.
        """
        if self.usage:
            self.prompt_tokens = self.usage.get("prompt_tokens", 0)
            self.completion_tokens = self.usage.get("completion_tokens", 0)
            self.total_tokens = self.usage.get("total_tokens", 0)

    @property
    def is_error(self) -> bool:
        """
        Check if the response contains an error.

        Returns:
            True if an error is present, False otherwise.
        """
        return self.error is not None

    @property
    def has_function_call(self) -> bool:
        """
        Check if the response contains a function call.

        Returns:
            True if a function call is present, False otherwise.
        """
        return self.function_call is not None

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the LLM response to a dictionary representation.

        Returns:
            Dictionary containing all response data.
        """
        return {
            "content": self.content,
            "model": self.model,
            "finish_reason": self.finish_reason,
            "usage": self.usage,
            "id": self.id,
            "created": self.created,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "function_call": self.function_call,
            "error": self.error,
            "raw_response": self.raw_response,
            "latency_ms": self.latency_ms,
        }

    @classmethod
    def from_error(cls, error: str, model: str = "unknown") -> "LLMResponse":
        """
        Create an error response.

        Args:
            error: The error message.
            model: The model that was being used.

        Returns:
            A new LLMResponse with the error set.
        """
        return cls(
            content="",
            model=model,
            error=error,
        )
