"""
硅基流动API测试脚本

用于验证50层测试系统与硅基流动API的集成
"""

import os
import sys

# 设置API密钥
os.environ["SILICONFLOW_API_KEY"] = "${SILICONFLOW_API_KEY}"

print("=" * 60)
print("🚀 50层测试系统 × 硅基流动API 集成测试")
print("=" * 60)

# 测试1: 导入硅基流动模块
print("\n📝 测试1: 导入硅基流动模块...")
try:
    from path_test_system.plugins.siliconflow import (
        SiliconFlowClient,
        SiliconFlowConfig,
        create_client,
        FREE_MODELS
    )
    print("✅ 硅基流动模块导入成功")
except Exception as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

# 测试2: 查看可用模型
print("\n📝 测试2: 可用的免费模型...")
for name, model_id in FREE_MODELS.items():
    print(f"   • {name}: {model_id}")

# 测试3: 创建客户端并测试连接
print("\n📝 测试3: 创建硅基流动客户端...")
try:
    client = create_client(
        api_key=os.environ.get("SILICONFLOW_API_KEY", ""),
        model="Qwen/Qwen2.5-7B-Instruct"
    )
    print(f"✅ 客户端创建成功")
    print(f"   模型: {client.config.model}")
    print(f"   API地址: {client.config.base_url}")
except Exception as e:
    print(f"❌ 客户端创建失败: {e}")
    sys.exit(1)

# 测试4: 发送测试请求
print("\n📝 测试4: 发送测试请求...")
try:
    messages = [
        {"role": "system", "content": "你是一个专业的代码测试助手。"},
        {"role": "user", "content": "请解释一下什么是全路径覆盖测试？"}
    ]

    print("   发送请求中...")
    response = client.chat(
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )

    content = response.choices[0].message.content
    print(f"\n✅ 请求成功!")
    print(f"\n📄 模型响应:")
    print("-" * 60)
    print(content[:500] + "..." if len(content) > 500 else content)
    print("-" * 60)

    if hasattr(response, 'usage') and response.usage:
        print(f"\n📊 Token使用统计:")
        print(f"   输入Token: {response.usage.prompt_tokens}")
        print(f"   输出Token: {response.usage.completion_tokens}")
        print(f"   总Token: {response.usage.total_tokens}")

except Exception as e:
    print(f"❌ 请求失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试5: 测试50层系统的LLM层
print("\n" + "=" * 60)
print("📝 测试5: 测试50层系统LLM层集成...")
print("=" * 60)

try:
    from path_test_system import PathTestEngine, create_context
    from path_test_system.layers.part1_interaction.layer_5_llm_adapter import LLMAdapterLayer

    engine = PathTestEngine()
    llm_layer = engine.get_layer(5)

    print(f"✅ LLM层获取成功")
    print(f"   层类型: {llm_layer.__class__.__name__}")
    print(f"   默认模型: {llm_layer._default_model}")
    print(f"   支持的提供者: {llm_layer.get_supported_providers()}")

    # 设置API密钥
    llm_layer.set_api_key("${SILICONFLOW_API_KEY}")

    # 创建测试上下文
    ctx = create_context()
    ctx.user_input = "测试代码覆盖率分析"
    ctx.metadata = {
        "intent": "code_analysis",
        "entities": [{"type": "function", "value": "calculate_sum"}],
        "llm_config": {
            "provider": "siliconflow",
            "model": "Qwen/Qwen2.5-7B-Instruct",
            "temperature": 0.7
        }
    }

    # 执行LLM层
    print("\n   执行LLM层...")
    result_ctx = llm_layer.process(ctx)

    llm_response = result_ctx.metadata.get("llm_response")
    if llm_response:
        print(f"\n✅ LLM层执行成功!")
        print(f"   响应内容: {llm_response.content[:200]}...")
        print(f"   提供者: {llm_response.provider}")
        print(f"   模型: {llm_response.model}")

except Exception as e:
    print(f"❌ LLM层测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("🎉 所有测试完成!")
print("=" * 60)

print("\n📚 进一步使用指南:")
print("   1. 在代码中使用:")
print("      from path_test_system.plugins.siliconflow import create_client")
print("      client = create_client('your-api-key')")
print()
print("   2. 在50层系统中自动使用:")
print("      设置环境变量 SILICONFLOW_API_KEY")
print("      系统将自动使用硅基流动API")
print()
print("   3. 可用免费模型:")
for name, model_id in list(FREE_MODELS.items())[:3]:
    print(f"      • {name}")
