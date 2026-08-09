# 🎁 免费模型完整方案指南

## 📋 概述

50层全路径代码测试系统 V3.1 提供多种**免费模型**方案，无需付费即可使用。

---

## 🎯 三种免费方案对比

| 方案 | 是否需要API | 是否需要网络 | 能力 | 推荐度 |
|------|-----------|-----------|------|--------|
| 模拟模式 | ❌ | ❌ | 中等 | ⭐⭐⭐⭐⭐ 推荐 |
| 硅基流动 | ✅ | ✅ | 强 | ⭐⭐⭐⭐ |
| Ollama本地 | ❌ | 首次下载需要 | 很强 | ⭐⭐⭐ |

---

## 🚀 快速开始（30秒上手）

### 最简单方案：模拟模式（完全免费）

```python
from path_test_system.plugins.free_models import create_free_client

# 创建客户端
client = create_free_client(provider="mock")

# 发送请求
messages = [{"role": "user", "content": "你好"}]
response = client.chat(messages=messages)

# 获取响应
print(response.choices[0].message.content)
```

---

## 📦 所有可用免费模型

### 1️⃣ 模拟模式（Mock）✅ 最推荐

**无需任何API，完全免费，即开即用！**

```python
from path_test_system.plugins.free_models import create_free_client

# 创建模拟客户端
client = create_free_client(provider="mock")

# 测试场景支持
- 代码分析
- 测试生成
- 覆盖率分析
- 路径分析
- 通用对话
```

### 2️⃣ 硅基流动免费模型

**需要API密钥，但模型能力强**

```python
from path_test_system.plugins.free_models import create_free_client

client = create_free_client(
    provider="siliconflow",
    api_key=os.environ.get("SILICONFLOW_API_KEY", ""),
    model="Qwen/Qwen2.5-7B-Instruct"  # 默认模型
)
```

**可用模型：**
- `Qwen/Qwen2.5-7B-Instruct` - 通义千问（推荐）
- `deepseek-ai/DeepSeek-V2.5` - DeepSeek
- `THUDM/glm-4-9b-chat` - 智谱清言
- `Qwen/Qwen2.5-Coder-32B-Instruct` - 代码专用

### 3️⃣ Ollama本地模型

**需要本地安装，完全免费，数据隐私**

```python
# 首先安装Ollama: https://ollama.com
# 然后下载模型: ollama pull llama3.1:8b

from path_test_system.plugins.free_models import create_free_client

client = create_free_client(
    provider="ollama",
    model="llama3.1:8b"
)
```

**可用模型：**
- `llama3.1:8b` - Meta Llama
- `qwen2:7b` - 通义千问
- `codeqwen:7b` - 代码专用

---

## 💡 集成到50层系统

### 方法1：直接使用免费模型客户端

```python
from path_test_system import PathTestEngine, create_context
from path_test_system.plugins.free_models import create_free_client

# 1. 创建50层引擎
engine = PathTestEngine()

# 2. 创建免费模型客户端
client = create_free_client(provider="mock")

# 3. 创建上下文
context = create_context()
context.user_input = "测试用户登录功能"

# 4. 执行50层流水线
for layer_num in range(1, 51):
    layer = engine.get_layer(layer_num)
    if layer:
        context = layer.process(context)
        print(f"✅ 层 {layer_num} 完成")
```

### 方法2：使用精简5层系统（推荐）

```python
from path_test_system.examples.simple_5_layer_system import SimpleTestSystem

# 创建5层精简系统
system = SimpleTestSystem()

# 运行测试
result = system.run("你好，请为用户登录函数生成测试用例")

# 查看结果
print(result.output_data)
```

---

## 🔧 高级用法

### 1. 列出所有可用模型

```python
from path_test_system.plugins.free_models import get_available_models

models = get_available_models()

for provider, model_list in models.items():
    print(f"\n🔌 {provider}:")
    for key, config in model_list.items():
        print(f"  • {config.name}: {config.description}")
```

### 2. 多轮对话

```python
client = create_free_client(provider="mock")

# 第一轮
messages = [{"role": "user", "content": "你好"}]
response = client.chat(messages=messages)

# 第二轮
messages.append({"role": "assistant", "content": response.choices[0].message.content})
messages.append({"role": "user", "content": "继续分析"})
response2 = client.chat(messages=messages)
```

### 3. 自定义输出长度

```python
# 在精简5层系统中
context.output_data = context.output_data[:1000]  # 限制长度
```

---

## 📊 实际应用示例

### 示例1：代码分析

```python
client = create_free_client(provider="mock")

messages = [
    {"role": "system", "content": "你是一个专业的代码分析专家。"},
    {"role": "user", "content": """
    请分析这段Python代码：
    def calculate(a, b):
        if a > b:
            return a - b
        else:
            return a + b
    """}
]

response = client.chat(messages=messages)
print(response.choices[0].message.content)
```

### 示例2：测试生成

```python
client = create_free_client(provider="mock")

messages = [
    {"role": "user", "content": "为用户登录函数生成完整的测试用例"}
]

response = client.chat(messages=messages)
print(response.choices[0].message.content)
```

### 示例3：覆盖率分析

```python
client = create_free_client(provider="mock")

messages = [
    {"role": "user", "content": "分析代码覆盖率并提出改进建议"}
]

response = client.chat(messages=messages)
print(response.choices[0].message.content)
```

---

## 🎨 响应示例

### 测试分析响应

```
## 📊 测试分析报告（模拟）

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
🤖 这是模拟响应（免费使用）
```

### 代码分析响应

```
## 🔍 代码分析结果（模拟）

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
```

---

## 🔄 升级路径

### 需要更强能力时

1. **从模拟升级到硅基流动**
   ```python
   # 只需修改provider和api_key
   client = create_free_client(
       provider="siliconflow",
       api_key="your_api_key",
       model="Qwen/Qwen2.5-7B-Instruct"
   )
   ```

2. **从硅基流动升级到Ollama本地**
   ```python
   # 下载Ollama并安装模型
   client = create_free_client(
       provider="ollama",
       model="llama3.1:8b"
   )
   ```

---

## 📚 文件位置

- 免费模型模块：[plugins/free_models.py](file:///workspace/path_test_system/plugins/free_models.py)
- 5层精简系统：[examples/simple_5_layer_system.py](file:///workspace/path_test_system/examples/simple_5_layer_system.py)
- 使用示例：[examples/use_free_models.py](file:///workspace/path_test_system/examples/use_free_models.py)
- 集成指南：[docs/SILICONFLOW_INTEGRATION.md](file:///workspace/path_test_system/docs/SILICONFLOW_INTEGRATION.md)

---

## 🎉 总结

✅ **完全免费** - 无需任何费用
✅ **开箱即用** - 模拟模式无需配置
✅ **可升级** - 后续可切换到更强大模型
✅ **集成简单** - 与50层系统完美集成
✅ **功能完整** - 支持所有测试场景

**推荐使用顺序：**
1. 📌 **模拟模式** - 快速开始，无需任何配置
2. 📌 **硅基流动** - 更强能力，需要API密钥
3. 📌 **Ollama本地** - 完全控制，数据隐私

---

## 🚀 立即开始

```python
# 一行代码开始使用
from path_test_system.plugins.free_models import create_free_client

client = create_free_client(provider="mock")
response = client.chat([{"role": "user", "content": "你好"}])
print(response.choices[0].message.content)
```

**开始您的免费测试之旅吧！** 🎊
