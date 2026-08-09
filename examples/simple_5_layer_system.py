"""
5层系统精简测试示例

使用5层架构的简化测试系统（而非50层），适用于快速演示
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import time


@dataclass
class TestContext:
    """测试上下文"""
    input_data: str = ""
    output_data: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    execution_time: float = 0.0


class BaseLayer:
    """基础层"""

    name: str = "Base Layer"
    description: str = "基础层描述"

    def process(self, context: TestContext) -> TestContext:
        """处理上下文"""
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class Layer1_InteractionEntry(BaseLayer):
    """层1：交互入口"""

    name: str = "交互入口层"
    description: str = "接收用户输入，初始化上下文"

    def process(self, context: TestContext) -> TestContext:
        print(f"📥 层1: 接收输入 - {context.input_data[:30]}...")
        context.metadata["timestamp"] = time.time()
        context.metadata["step1"] = "completed"
        return context


class Layer2_Analysis(BaseLayer):
    """层2：分析层"""

    name: str = "分析层"
    description: str = "分析输入内容"

    def process(self, context: TestContext) -> TestContext:
        print(f"🔍 层2: 分析内容 - 长度: {len(context.input_data)} 字符")
        context.metadata["content_length"] = len(context.input_data)
        context.metadata["word_count"] = len(context.input_data.split())
        context.metadata["step2"] = "completed"
        return context


class Layer3_FreeModelIntegration(BaseLayer):
    """层3：免费模型集成"""

    name: str = "免费模型集成层"
    description: str = "使用免费模型进行智能处理"

    def __init__(self):
        from path_test_system.plugins.free_models import create_free_client
        self.client = create_free_client(provider="mock")

    def process(self, context: TestContext) -> TestContext:
        print("🤖 层3: 免费模型处理...")

        messages = [
            {"role": "system", "content": "你是一个专业的代码测试助手。"},
            {"role": "user", "content": context.input_data}
        ]

        response = self.client.chat(messages=messages)
        context.output_data = response.choices[0].message.content
        context.metadata["model_response"] = context.output_data
        context.metadata["step3"] = "completed"

        print("✅ 层3: 模型响应生成成功")
        return context


class Layer4_ResultProcess(BaseLayer):
    """层4：结果处理"""

    name: str = "结果处理层"
    description: str = "处理模型输出结果"

    def process(self, context: TestContext) -> TestContext:
        print("📝 层4: 处理结果...")

        if len(context.output_data) > 1000:
            context.output_data = context.output_data[:1000] + "..."

        context.metadata["output_length"] = len(context.output_data)
        context.metadata["step4"] = "completed"

        print(f"✅ 层4: 结果已处理 - 长度: {len(context.output_data)}")
        return context


class Layer5_Output(BaseLayer):
    """层5：输出层"""

    name: str = "输出层"
    description: str = "输出最终结果"

    def process(self, context: TestContext) -> TestContext:
        print("📤 层5: 生成输出...")
        context.metadata["step5"] = "completed"
        context.metadata["end_timestamp"] = time.time()

        if "timestamp" in context.metadata and "end_timestamp" in context.metadata:
            context.execution_time = context.metadata["end_timestamp"] - context.metadata["timestamp"]

        print(f"✅ 层5: 输出完成 - 耗时: {context.execution_time:.2f}秒")
        return context


class SimpleTestSystem:
    """简单测试系统（5层）"""

    def __init__(self):
        self.layers = [
            Layer1_InteractionEntry(),
            Layer2_Analysis(),
            Layer3_FreeModelIntegration(),
            Layer4_ResultProcess(),
            Layer5_Output()
        ]
        print(f"✅ 5层测试系统初始化成功")

    def run(self, user_input: str) -> TestContext:
        """
        运行完整流程

        Args:
            user_input: 用户输入

        Returns:
            TestContext: 处理后的上下文
        """
        print("\n" + "=" * 80)
        print("🚀 启动5层测试系统")
        print("=" * 80)

        context = TestContext(input_data=user_input)

        for i, layer in enumerate(self.layers, 1):
            print(f"\n{'=' * 80}")
            print(f"📍 执行层 {i}/{len(self.layers)}: {layer.name}")
            print(f"{'=' * 80}")

            try:
                context = layer.process(context)
                print(f"✅ 层 {i} 完成")
            except Exception as e:
                print(f"❌ 层 {i} 失败: {e}")
                context.errors.append(f"层{i}错误: {e}")

        print("\n" + "=" * 80)
        print("🎉 5层系统执行完成！")
        print("=" * 80)

        return context


def main():
    """主函数"""
    print("=" * 80)
    print("🎁 50层系统精简版 - 使用免费模型演示")
    print("=" * 80)

    # 创建系统
    system = SimpleTestSystem()

    # 测试1: 简单对话
    print("\n" + "=" * 80)
    print("📝 测试1: 简单对话")
    print("=" * 80)
    result = system.run("你好，请介绍一下自己")
    print("\n📄 输出结果:")
    print("-" * 80)
    print(result.output_data[:600])

    # 测试2: 代码分析
    print("\n" + "=" * 80)
    print("🔍 测试2: 代码分析")
    print("=" * 80)
    result = system.run("分析这段Python代码的复杂度和测试建议")
    print("\n📄 输出结果:")
    print("-" * 80)
    print(result.output_data[:600])

    # 测试3: 测试生成
    print("\n" + "=" * 80)
    print("🧪 测试3: 测试生成")
    print("=" * 80)
    result = system.run("为用户登录函数生成测试用例")
    print("\n📄 输出结果:")
    print("-" * 80)
    print(result.output_data[:600])

    # 总结
    print("\n" + "=" * 80)
    print("✅ 所有测试完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()
