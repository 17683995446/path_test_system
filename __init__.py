"""
50层全路径代码测试系统
============================

高度模块化、企业级产品化架构

Architecture:
├── src/
│   ├── core/              # 核心模块
│   ├── layers/            # 50层实现
│   ├── utils/             # 工具函数
│   └── plugins/           # 插件
├── tests/                 # 测试套件
├── docs/                  # 文档
├── config/                # 配置
└── examples/              # 示例
"""

__version__ = "3.2.0"
__author__ = "PathTestSystem Team"
__license__ = "MIT"

from src.core.engine import PathTestEngine
from src.core.context import PipelineContext, create_context

__all__ = [
    "PathTestEngine",
    "PipelineContext",
    "create_context",
    "__version__",
]
