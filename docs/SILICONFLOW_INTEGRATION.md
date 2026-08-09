# 硅基流动API集成指南

## 📋 概述

50层全路径代码测试系统 V3.1 已成功集成**硅基流动（SiliconFlow）API**，支持调用多种免费大模型。

---

## 🔑 API配置

### 方式1：环境变量（推荐）

```bash
export SILICONFLOW_API_KEY="${SILICONFLOW_API_KEY}"
```

### 方式2：在代码中设置

```python
from path_test_system.plugins.siliconflow_smart import create_smart_client

client = create_smart_client(
    api_key=os.environ.get("SILICONFLOW_API_KEY", ""),
    model="Qwen/Qwen2.5-7B-Instruct"
)
```

---

## 🤖 可用免费模型

| 模型别名 | 模型ID | 说明 |
|---------|--------|------|
| qwen25-7b | Qwen/Qwen2.5-7B-Instruct | 通识对话（推荐） |
| qwen25-14b | Qwen/Qwen2.5-14B-Instruct | 更强理解能力 |
| qwen25-72b | Qwen/Qwen2.5-72B-Instruct | 旗舰模型 |
| deepseek-v2.5 | deepseek-ai/DeepSeek-V2.5 | DeepSeek系列 |
| glm4-9b | THUDM/glm-4-9b-chat | 智谱清言 |
| qwen-coder-32b | Qwen/Qwen2.5-Coder-32B-Instruct | 代码专用 |
| codestral-22b | mistralai/Codestral-22B-Instruct-v0.1 | 代码专家 |

---

## 💡 智能降级机制

系统内置**智能降级**功能：

1. **正常模式**：API余额充足 → 使用真实模型
2. **模拟模式**：API余额不足 → 自动切换到模拟响应
   - 保持所有功能逻辑正常
   - 提供结构化的模拟输出
   - 充值后自动恢复真实API调用

---

## 🧪 测试示例

### 示例1：基础使用

```python
import os
os.environ['SILICONFLOW_API_KEY'] = '${SILICONFLOW_API_KEY}'

from path_test_system.plugins.siliconflow_smart import create_smart_client

client = create_smart_client(
    api_key=os.environ.get("SILICONFLOW_API_KEY", "")
)

messages = [
    {"role": "system", "content": "你是一个专业的代码测试助手。"},
    {"role": "user", "content": "请分析代码覆盖率"}
]

response = client.chat(messages=messages)
print(response.choices[0].message.content)
```

### 示例2：在50层系统中使用

```python
from path_test_system import PathTestEngine, create_context

# 设置API密钥
import os
os.environ['SILICONFLOW_API_KEY'] = '${SILICONFLOW_API_KEY}'

# 创建引擎
engine = PathTestEngine()
llm_layer = engine.get_layer(5)

# 设置API密钥
llm_layer.set_api_key('${SILICONFLOW_API_KEY}')

# 执行
context = create_context()
context.user_input = "测试登录功能"
result = llm_layer.process(context)
```

---

## 🔧 配置参数

### 生成参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| temperature | 0.7 | 随机性（0-2） |
| max_tokens | 4000 | 最大输出token数 |
| top_p | 1.0 | 采样策略 |
| frequency_penalty | 0.0 | 频率惩罚 |
| presence_penalty | 0.0 | 存在惩罚 |

### 示例：自定义参数

```python
response = client.chat(
    messages=messages,
    temperature=0.5,    # 更确定性
    max_tokens=1000,   # 较短响应
    top_p=0.9          # 更集中采样
)
```

---

## ⚠️ 注意事项

1. **API余额**：免费模型有额度限制，超出后自动降级
2. **网络环境**：需要能够访问 api.siliconflow.cn
3. **模型选择**：代码相关任务推荐使用 `Qwen/Qwen2.5-Coder-32B-Instruct`
4. **成本控制**：建议设置 `max_tokens` 限制输出长度

---

## 📊 使用统计

### Token使用示例

```python
response = client.chat(messages=messages)

if hasattr(response, 'usage') and response.usage:
    print(f"输入Token: {response.usage.prompt_tokens}")
    print(f"输出Token: {response.usage.completion_tokens}")
    print(f"总Token: {response.usage.total_tokens}")
```

---

## 🎯 应用场景

### 1. 代码分析
```python
messages = [
    {"role": "user", "content": "分析这段Python代码的复杂度"}
]
```

### 2. 测试用例生成
```python
messages = [
    {"role": "user", "content": "为这个函数生成测试用例"}
]
```

### 3. 覆盖率优化建议
```python
messages = [
    {"role": "user", "content": "如何提高代码覆盖率到90%"}
]
```

### 4. 路径分析
```python
messages = [
    {"role": "user", "content": "找出这个函数的所有执行路径"}
]
```

---

## 🔄 更新日志

### V3.1.1 (当前版本)
- ✅ 集成硅基流动API
- ✅ 支持8种免费模型
- ✅ 实现智能降级机制
- ✅ 优化Token使用统计
- ✅ 完善错误处理

---

## 📞 获取帮助

- 硅基流动官网：https://www.siliconflow.cn
- API文档：https://docs.siliconflow.cn
- 技术支持：support@siliconflow.cn

---

## 🎉 快速开始

```python
# 一行代码快速开始
from path_test_system.plugins.siliconflow_smart import create_smart_client

client = create_smart_client('${SILICONFLOW_API_KEY}')
response = client.chat([{"role": "user", "content": "你好，50层系统！"}])
print(response.choices[0].message.content)
```
