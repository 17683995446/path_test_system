import os
"""
免费模型使用示例

展示如何使用各种免费模型方案
"""

print("=" * 80)
print("🎁 50层系统免费模型完整方案")
print("=" * 80)

# 方案1：模拟模式（完全免费，无需任何API）
print("\n" + "=" * 80)
print("📋 方案1：模拟模式（推荐）")
print("=" * 80)

from path_test_system.plugins.free_models import create_free_client, get_available_models

# 创建模拟客户端
client = create_free_client(provider="mock")
print("✅ 模拟模式客户端创建成功\n")

# 测试1: 通用对话
messages = [
    {"role": "user", "content": "你好"}
]
response = client.chat(messages=messages)
print("🤖 对话测试响应：")
print(response.choices[0].message.content[:400])

# 测试2: 代码分析
messages = [
    {"role": "user", "content": "分析这段代码的复杂度"}
]
response = client.chat(messages=messages)
print("\n🔍 代码分析响应：")
print(response.choices[0].message.content[:400])

# 测试3: 测试分析
messages = [
    {"role": "user", "content": "生成测试用例并分析覆盖率"}
]
response = client.chat(messages=messages)
print("\n📊 测试分析响应：")
print(response.choices[0].message.content[:400])

# 列出所有可用模型
print("\n" + "=" * 80)
print("📦 所有可用免费模型")
print("=" * 80)

models = get_available_models()
for provider, model_list in models.items():
    print(f"\n🔌 提供商: {provider}")
    print("-" * 80)
    for key, config in model_list.items():
        print(f"  • {config.name}")
        print(f"    模型ID: {config.model_id}")
        print(f"    描述: {config.description}")
        print(f"    需要API: {'是' if config.api_key_required else '否'}")

# 方案2：集成到50层系统
print("\n" + "=" * 80)
print("🏗️ 方案2：集成到50层系统")
print("=" * 80)

print("""
要在50层系统中使用免费模型：

1️⃣ 使用模拟模式（完全免费）：
   from path_test_system.plugins.free_models import create_free_client
   client = create_free_client(provider='mock')

2️⃣ 使用硅基流动免费模型（需要API密钥）：
   client = create_free_client(
       provider='siliconflow',
       api_key=os.environ.get("SILICONFLOW_API_KEY", ""),
       model='Qwen/Qwen2.5-7B-Instruct'
   )

3️⃣ 使用Ollama本地模型（需要本地安装）：
   client = create_free_client(
       provider='ollama',
       model='llama3.1:8b'
   )
""")

# 50层系统集成示例
print("\n" + "=" * 80)
print("🔗 50层系统集成示例")
print("=" * 80)

print("""
from path_test_system import PathTestEngine, create_context
from path_test_system.plugins.free_models import create_free_client

# 1. 创建引擎
engine = PathTestEngine()
print(f'✅ 引擎创建成功，包含 {len(engine.layers)} 层')

# 2. 创建免费模型客户端
client = create_free_client(provider='mock')
print(f'✅ 免费模型客户端创建成功')

# 3. 在50层系统中使用
context = create_context()
context.user_input = '测试用户登录功能'

# 4. 执行层处理
for layer_num in range(1, 51):
    layer = engine.get_layer(layer_num)
    if layer:
        context = layer.process(context)
        print(f'✅ 层 {layer_num} 执行完成')
""")

print("\n" + "=" * 80)
print("✅ 免费模型方案演示完成！")
print("=" * 80)
print("\n📚 下一步：")
print("   • 使用模拟模式进行开发和测试")
print("   • 集成到您的现有工作流程中")
print("   • 需要真实模型时再申请API")
