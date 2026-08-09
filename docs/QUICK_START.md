"""
50层测试系统快速开始指南
"""

print("=" * 80)
print("🎉 50层全路径代码测试系统 V3.1 - 快速开始")
print("=" * 80)

print("""
📚 快速开始步骤
================================================================================

1️⃣  硅基流动API配置（已完成）
    ✅ API密钥已配置: ${SILICONFLOW_API_KEY}
    ✅ 可用免费模型: Qwen2.5-7B-Instruct 等8种模型
    ✅ 智能降级: API余额不足时自动切换模拟模式

2️⃣  基础使用示例
    ================================================================================

    from path_test_system.plugins.siliconflow_smart import create_smart_client

    # 创建客户端
    client = create_smart_client('${SILICONFLOW_API_KEY}')

    # 发送请求
    messages = [
        {'role': 'system', 'content': '你是一个专业的代码测试助手。'},
        {'role': 'user', 'content': '请分析代码覆盖率的关键指标'}
    ]

    response = client.chat(messages=messages)
    print(response.choices[0].message.content)


3️⃣  50层系统使用
    ================================================================================

    from path_test_system import PathTestEngine, create_context

    # 创建引擎
    engine = PathTestEngine()
    print(f'引擎包含 {len(engine.layers)} 层')

    # 执行单个层
    layer1 = engine.get_layer(1)
    ctx = layer1.process('测试登录功能')

    # 执行完整流水线
    for i in range(1, 51):
        layer = engine.get_layer(i)
        ctx = layer.process(ctx)


4️⃣  可用免费模型
    ================================================================================

    • Qwen/Qwen2.5-7B-Instruct         (推荐 - 通识对话)
    • Qwen/Qwen2.5-14B-Instruct        (更强理解能力)
    • Qwen/Qwen2.5-72B-Instruct        (旗舰模型)
    • deepseek-ai/DeepSeek-V2.5        (DeepSeek系列)
    • THUDM/glm-4-9b-chat              (智谱清言)
    • Qwen/Qwen2.5-Coder-32B-Instruct  (代码专用)
    • mistralai/Codestral-22B-Instruct (代码专家)


5️⃣  测试脚本位置
    ================================================================================

    • examples/basic_usage.py          - 基础使用示例
    • examples/test_siliconflow.py      - 硅基流动API测试
    • examples/sample_code.py           - 示例测试代码
    • plugins/siliconflow.py            - 硅基流动客户端
    • plugins/siliconflow_smart.py       - 智能客户端（推荐）


6️⃣  文档资源
    ================================================================================

    • docs/SILICONFLOW_INTEGRATION.md   - 硅基流动集成指南
    • config/default_config.json         - 默认配置
    • config/siliconflow.ini            - 硅基流动配置
    • README.md                         - 项目说明文档


7️⃣  常见问题
    ================================================================================

    Q: API余额不足怎么办？
    A: 系统会自动切换到模拟模式，所有功能逻辑仍然正常。

    Q: 如何切换到其他模型？
    A: 在创建客户端时指定model参数。

    Q: 如何查看Token使用量？
    A: response.usage.total_tokens 可以查看。

    Q: 支持哪些编程语言？
    A: Python、Java、JavaScript、Go、Rust等主流语言。


8️⃣  下一步
    ================================================================================

    运行示例代码：
    cd /workspace
    python -c "from path_test_system.plugins.siliconflow_smart import create_smart_client; \
    client = create_smart_client('${SILICONFLOW_API_KEY}'); \
    print(client.chat([{'role': 'user', 'content': '你好'}]).choices[0].message.content)"

    或者查看详细文档：
    cat /workspace/path_test_system/docs/SILICONFLOW_INTEGRATION.md

""")

print("=" * 80)
print("✅ 准备就绪！50层系统已配置硅基流动API，可以开始使用了。")
print("=" * 80)
