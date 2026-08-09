"""
50层全路径代码测试系统
快速使用示例

本文件展示如何使用Python API快速调用50层测试系统
"""

from path_test_system import PathTestEngine, create_context
from path_test_system.core.models.task_request import TaskRequest, TaskPriority
from path_test_system.core.models.config_snapshot import ConfigSnapshot


def example_basic_usage():
    """基础使用示例"""
    print("=" * 60)
    print("示例1：基础使用")
    print("=" * 60)

    # 创建引擎实例
    engine = PathTestEngine()
    context = create_context()

    # 创建任务请求
    task_request = TaskRequest(
        task_id="demo_task_001",
        source_path="./sample_code",
        priority=TaskPriority.HIGH,
        test_strategy="full-coverage",
        coverage_types=["statement", "branch", "path"],
        output_format="html",
        language="python"
    )

    # 存储到上下文
    context.set("task_request", task_request)

    # 执行流水线
    for layer_num in range(1, 51):
        layer = engine.get_layer(layer_num)
        if layer:
            context = layer.process(context)
            print(f"✅ 层{layer_num}执行完成")

    print("\n🎉 测试流水线执行完成！")
    return context


def example_specific_layers():
    """指定层使用示例"""
    print("\n" + "=" * 60)
    print("示例2：使用特定层")
    print("=" * 60)

    engine = PathTestEngine()

    # 只执行第9-16层（源码预处理部分）
    print("\n📦 执行源码预处理流水线（层9-16）...")

    for layer_num in range(9, 17):
        layer = engine.get_layer(layer_num)
        if layer:
            print(f"   层{layer_num}: {layer.__class__.__name__}")


def example_custom_config():
    """自定义配置示例"""
    print("\n" + "=" * 60)
    print("示例3：自定义配置")
    print("=" * 60)

    # 创建自定义配置
    config = ConfigSnapshot(
        llm_model="gpt-4",
        max_token_limit=8000,
        temperature=0.5,
        cache_enabled=True
    )

    print(f"\nLLM模型: {config.llm_model}")
    print(f"最大Token: {config.max_token_limit}")
    print(f"温度参数: {config.temperature}")
    print(f"缓存启用: {config.cache_enabled}")


def example_layer_info():
    """查看层信息示例"""
    print("\n" + "=" * 60)
    print("示例4：查看层信息")
    print("=" * 60)

    engine = PathTestEngine()

    # 查看所有层的信息
    print("\n📊 50层系统层级结构：")
    print("-" * 80)

    for layer_num in range(1, 51):
        info = engine.get_layer_info(layer_num)
        if info:
            print(f"层{layer_num:2d}: {info['name']}")


def example_context_usage():
    """上下文使用示例"""
    print("\n" + "=" * 60)
    print("示例5：上下文数据管理")
    print("=" * 60)

    context = create_context()

    # 存储数据
    context.set("user_name", "张三")
    context.set("task_id", "12345")
    context.set("is_vip", True)

    # 读取数据
    print(f"\n用户名: {context.get('user_name')}")
    print(f"任务ID: {context.get('task_id')}")
    print(f"VIP状态: {context.get('is_vip')}")

    # 检查是否存在
    print(f"\n是否存在 'score' 键: {context.has('score')}")
    print(f"是否存在 'task_id' 键: {context.has('task_id')}")

    # 使用默认值
    print(f"\n不存在的键，使用默认值: {context.get('nonexistent', '默认值')}")

    # 记录执行历史
    context.record_layer_execution(1, {"result": "success"})
    context.record_layer_execution(2, {"result": "success"})

    print(f"\n执行历史: {context.metadata['execution_history']}")


def main():
    """运行所有示例"""
    print("\n" + "=" * 80)
    print("🚀 50层全路径代码测试系统 V3.1 - 使用示例")
    print("=" * 80)

    try:
        example_custom_config()
        example_layer_info()
        example_context_usage()
        example_specific_layers()

        print("\n" + "=" * 80)
        print("✅ 所有示例执行成功！")
        print("=" * 80)

        print("\n📚 进一步学习：")
        print("   - 查看 cli.py 了解命令行用法")
        print("   - 查看 layers/ 目录了解各层实现")
        print("   - 查看 config/default_config.json 了解默认配置")

    except Exception as e:
        print(f"\n❌ 示例执行失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
