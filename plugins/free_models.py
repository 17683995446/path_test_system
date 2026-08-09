"""
免费模型使用方案

提供多种免费模型接入方案：
1. 硅基流动免费模型（API方式）
2. Hugging Face免费模型（API方式）
3. 本地开源模型（本地运行）
"""

import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class FreeModelConfig:
    """免费模型配置"""
    name: str
    model_id: str
    provider: str
    api_key_required: bool
    description: str


# 免费模型列表
FREE_MODELS = {
    "siliconflow": {
        "qwen25-7b": FreeModelConfig(
            name="Qwen2.5-7B",
            model_id="Qwen/Qwen2.5-7B-Instruct",
            provider="siliconflow",
            api_key_required=True,
            description="通义千问2.5 7B - 免费"
        ),
        "deepseek-v2.5": FreeModelConfig(
            name="DeepSeek-V2.5",
            model_id="deepseek-ai/DeepSeek-V2.5",
            provider="siliconflow",
            api_key_required=True,
            description="DeepSeek V2.5 - 免费"
        ),
        "glm4-9b": FreeModelConfig(
            name="GLM-4-9B",
            model_id="THUDM/glm-4-9b-chat",
            provider="siliconflow",
            api_key_required=True,
            description="智谱清言 GLM-4 - 免费"
        )
    },
    "ollama": {
        "llama3.1-8b": FreeModelConfig(
            name="Llama3.1-8B",
            model_id="llama3.1:8b",
            provider="ollama",
            api_key_required=False,
            description="Meta Llama3.1 8B - 本地运行"
        ),
        "qwen2-7b": FreeModelConfig(
            name="Qwen2-7B",
            model_id="qwen2:7b",
            provider="ollama",
            api_key_required=False,
            description="通义千问2 7B - 本地运行"
        ),
        "codeqwen-7b": FreeModelConfig(
            name="CodeQwen-7B",
            model_id="codeqwen:7b",
            provider="ollama",
            api_key_required=False,
            description="CodeQwen 7B - 代码专用"
        )
    },
    "mock": {
        "test-model": FreeModelConfig(
            name="测试模型",
            model_id="test-model",
            provider="mock",
            api_key_required=False,
            description="模拟模型 - 无需API"
        )
    }
}


class FreeModelClient:
    """
    免费模型统一客户端

    支持多种免费模型接入方式：
    - 硅基流动 API
    - Ollama 本地模型
    - 模拟模式（无需任何API）
    """

    def __init__(
        self,
        provider: str = "mock",
        model: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        初始化免费模型客户端

        Args:
            provider: 提供商 (siliconflow/ollama/mock)
            model: 模型名称
            api_key: API密钥（如果需要）
        """
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self._client = None
        self._init_client()

    def _init_client(self):
        """初始化客户端"""
        if self.provider == "siliconflow":
            self._init_siliconflow()
        elif self.provider == "ollama":
            self._init_ollama()
        else:
            self._init_mock()

    def _init_siliconflow(self):
        """初始化硅基流动客户端"""
        try:
            from path_test_system.plugins.siliconflow_smart import create_smart_client
            api_key = self.api_key or os.getenv("SILICONFLOW_API_KEY", "")
            self._client = create_smart_client(api_key, self.model or "Qwen/Qwen2.5-7B-Instruct")
            print(f"✅ 硅基流动客户端初始化成功")
        except Exception as e:
            print(f"⚠️  硅基流动初始化失败，使用模拟模式: {e}")
            self._init_mock()

    def _init_ollama(self):
        """初始化Ollama客户端"""
        try:
            # 简单实现，可以后续完善
            print(f"🤖 Ollama模式 - 使用本地模型: {self.model}")
            print("ℹ️  Ollama需要本地安装，请访问 https://ollama.com")
            self._init_mock()
        except Exception as e:
            print(f"⚠️  Ollama初始化失败，使用模拟模式: {e}")
            self._init_mock()

    def _init_mock(self):
        """初始化模拟客户端"""
        print(f"🎭 模拟模式 - 无需API密钥")
        self._client = MockModelClient()

    def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Any:
        """
        发送聊天请求

        Args:
            messages: 消息列表
            **kwargs: 其他参数

        Returns:
            模型响应
        """
        return self._client.chat(messages, **kwargs)


class MockModelClient:
    """
    模拟模型客户端

    提供高质量的模拟响应，适用于开发和测试
    """

    def __init__(self):
        self.conversation_history = []

    def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Any:
        """
        模拟聊天响应

        Args:
            messages: 消息列表
            **kwargs: 其他参数

        Returns:
            模拟响应对象
        """
        last_message = messages[-1]["content"] if messages else ""

        response_content = self._generate_response(last_message)

        return MockResponse(
            content=response_content,
            model="mock-model",
            usage=MockUsage(
                prompt_tokens=len(str(messages)) // 4,
                completion_tokens=len(response_content) // 4,
                total_tokens=(len(str(messages)) + len(response_content)) // 4
            )
        )

    def _generate_response(self, prompt: str) -> str:
        """根据提示生成模拟响应"""
        prompt_lower = prompt.lower()

        if any(keyword in prompt_lower for keyword in ["测试", "test", "覆盖率", "coverage"]):
            return self._test_analysis_response()
        elif any(keyword in prompt_lower for keyword in ["代码", "code", "函数", "function"]):
            return self._code_analysis_response()
        elif any(keyword in prompt_lower for keyword in ["路径", "path", "分支", "branch"]):
            return self._path_analysis_response()
        elif any(keyword in prompt_lower for keyword in ["你好", "hello", "hi"]):
            return self._greeting_response()
        else:
            return self._general_response()

    def _test_analysis_response(self) -> str:
        """测试分析响应"""
        return """## 📊 测试分析报告（模拟）

### 覆盖率指标
- **语句覆盖率**: 87.5%
- **分支覆盖率**: 72.3%
- **路径覆盖率**: 45.8%
- **函数覆盖率**: 90.0%

### 分析建议
1. 🎯 **重点测试**: 异常处理分支（第15-20行）
2. 📋 **补充用例**: 边界值测试（负数、零值、极大值）
3. 🔄 **回归测试**: 添加修改后的代码单元测试

### 执行时间
- 总测试数: 156个
- 通过: 148个
- 失败: 8个
- 通过率: 94.87%

---
🤖 这是模拟响应（免费使用）"""

    def _code_analysis_response(self) -> str:
        """代码分析响应"""
        return """## 🔍 代码分析结果（模拟）

### 代码结构
- 函数数量: 12个
- 类数量: 3个
- 总代码行: 456行
- 平均圈复杂度: 4.2

### 复杂度分布
- 低复杂度 (<5): 9个函数
- 中等复杂度 (5-10): 2个函数
- 高复杂度 (>10): 1个函数

### 建议优化
1. 函数 `process_data()` 可拆分
2. 考虑使用枚举替代魔法数字
3. 添加类型注解提升可读性

---
🤖 这是模拟响应（免费使用）"""

    def _path_analysis_response(self) -> str:
        """路径分析响应"""
        return """## 🗺️ 路径分析报告（模拟）

### 执行路径统计
- 总路径数: 18条
- 可行路径: 15条
- 不可达路径: 3条

### 路径优先级
- **P0 关键路径**: 正常业务流程（4条）
- **P1 重要路径**: 异常处理路径（6条）
- **P2 普通路径**: 边界条件路径（5条）

### 路径示例
```
路径1: start → validate → process → save → success
路径2: start → validate → error → return
路径3: start → validate → process → error → rollback
```

---
🤖 这是模拟响应（免费使用）"""

    def _greeting_response(self) -> str:
        """问候响应"""
        return """👋 你好！我是50层全路径测试系统的AI助手。

### 我可以帮你：

1. 📊 **代码分析** - 分析代码结构和复杂度
2. 🧪 **测试生成** - 自动生成测试用例
3. 📈 **覆盖率分析** - 检查代码覆盖率
4. 🗺️ **路径分析** - 分析执行路径
5. 🔧 **优化建议** - 提供代码优化建议

### 试试问我：
- "分析这段代码"
- "生成测试用例"
- "如何提高覆盖率"
- "找出所有执行路径"

---
🤖 这是模拟响应（免费使用）"""

    def _general_response(self) -> str:
        """通用响应"""
        return f"""## 💡 通用分析（模拟）

### 已接收请求
您的请求已成功处理，正在分析中...

### 当前系统状态
- ✅ 50层测试系统运行正常
- ✅ 免费模式已启用
- ✅ 所有功能可用

### 下一步建议
1. 提供具体的代码进行分析
2. 说明您想要测试的功能
3. 描述您期望的测试目标

---
🤖 这是模拟响应（免费使用）"""


@dataclass
class MockResponse:
    """模拟响应对象"""
    content: str
    model: str
    usage: Any

    @property
    def choices(self):
        return [MockChoice(content=self.content)]


@dataclass
class MockChoice:
    """模拟选择对象"""
    message: Any

    def __init__(self, content: str):
        self.message = MockMessage(content=content)


@dataclass
class MockMessage:
    """模拟消息对象"""
    content: str


@dataclass
class MockUsage:
    """模拟使用统计"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


def create_free_client(
    provider: str = "mock",
    model: Optional[str] = None,
    api_key: Optional[str] = None
) -> FreeModelClient:
    """
    工厂函数：创建免费模型客户端

    Args:
        provider: 提供商 (siliconflow/ollama/mock)
        model: 模型名称
        api_key: API密钥

    Returns:
        FreeModelClient实例
    """
    return FreeModelClient(
        provider=provider,
        model=model,
        api_key=api_key
    )


def get_available_models() -> Dict[str, List[FreeModelConfig]]:
    """获取可用免费模型列表"""
    return FREE_MODELS


if __name__ == "__main__":
    print("=" * 70)
    print("🎁 免费模型使用示例")
    print("=" * 70)

    # 1. 使用模拟模式（最推荐，无需任何API）
    print("\n1️⃣  模拟模式（无需API）")
    client = create_free_client(provider="mock")

    # 发送测试请求
    messages = [
        {"role": "user", "content": "你好，请分析代码覆盖率"}
    ]
    response = client.chat(messages=messages)
    print(response.choices[0].message.content[:500])

    # 2. 列出可用模型
    print("\n2️⃣  可用免费模型列表:")
    models = get_available_models()
    for provider, model_list in models.items():
        print(f"\n   🔌 {provider}:")
        for key, config in model_list.items():
            print(f"      • {config.name}: {config.description}")

    print("\n" + "=" * 70)
    print("✅ 免费模型客户端演示完成！")
    print("=" * 70)
