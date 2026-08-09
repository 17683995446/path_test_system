# 📂 50层全路径代码测试系统 - 文件目录结构

## 完整目录树

```
/workspace/path_test_system/
├── 📄 __init__.py                      # 主包入口，包含PathTestEngine类
├── 📄 api_server.py                    # REST API服务器
├── 📄 cli.py                           # 命令行接口
├── 📄 pyproject.toml                   # Python项目配置
├── 📄 requirements.txt                 # 依赖列表
├── 📂 config/                          # 配置文件
│   ├── 📄 default_config.json         # 默认配置
│   └── 📄 siliconflow.ini             # 硅基流动配置
├── 📂 core/                           # 核心模块
│   ├── 📄 __init__.py
│   ├── 📄 context.py                  # 流水线上下文（PipelineContext）
│   └── 📂 models/                    # 数据模型
│       ├── 📄 __init__.py
│       ├── 📄 config_snapshot.py      # 配置快照模型
│       ├── 📄 coverage_models.py      # 覆盖率模型
│       ├── 📄 llm_models.py           # LLM请求/响应模型
│       ├── 📄 path_models.py          # 路径分析模型
│       ├── 📄 task_context.py         # 任务上下文模型
│       ├── 📄 task_request.py         # 任务请求模型
│       └── 📄 test_strategy.py        # 测试策略模型
├── 📂 docs/                           # 文档
│   ├── 📄 FREE_MODELS_GUIDE.md       # 免费模型使用指南
│   ├── 📄 QUICK_START.md              # 快速开始
│   └── 📄 SILICONFLOW_INTEGRATION.md # 硅基流动集成指南
├── 📂 examples/                       # 示例代码
│   ├── 📄 basic_usage.py              # 基础使用示例
│   ├── 📄 sample_code.py              # 示例测试代码
│   ├── 📄 simple_5_layer_system.py   # 5层精简系统
│   ├── 📄 test_siliconflow.py        # 硅基流动API测试
│   └── 📄 use_free_models.py         # 免费模型使用示例
├── 📂 layers/                        # 50层实现（核心模块）
│   ├── 📄 __init__.py
│   ├── 📂 part1_interaction/        # 第一部分：用户交互与任务定义（层1-8）
│   │   ├── 📄 __init__.py
│   │   ├── 📄 layer_1_entry.py        # 层1：交互入口层
│   │   ├── 📄 layer_2_lifecycle.py    # 层2：任务生命周期管理层
│   │   ├── 📄 layer_3_config.py       # 层3：全局配置规则层
│   │   ├── 📄 layer_4_nlp_parser.py   # 层4：自然语言命令解析层
│   │   ├── 📄 layer_5_llm_adapter.py  # 层5：LLM全局能力适配层
│   │   ├── 📄 layer_6_cache.py        # 层6：LLM全局缓存管理层
│   │   ├── 📄 layer_7_test_strategy.py # 层7：测试目标语义理解层
│   │   └── 📄 layer_8_req_mapping.py  # 层8：需求-代码映射分析层
│   ├── 📂 part2_preprocessing/       # 第二部分：源码接入与预处理（层9-16）
│   │   ├── 📄 __init__.py
│   │   ├── 📄 layer_9_source_scan.py  # 层9：源码接入扫描层
│   │   ├── 📄 layer_10_incremental_cache.py # 层10：增量缓存决策层
│   │   ├── 📄 layer_11_preprocess.py  # 层11：文件预处理清洗层
│   │   ├── 📄 layer_12_language_adapter.py # 层12：多语言适配分发层
│   │   ├── 📄 layer_13_semantic_summary.py # 层13：代码语义摘要生成层
│   │   ├── 📄 layer_14_quality_scan.py # 层14：代码质量预扫描层
│   │   ├── 📄 layer_15_sensitive_detect.py # 层15：敏感代码识别层
│   │   └── 📄 layer_16_risk_assessment.py # 层16：测试风险评估层
│   ├── 📂 part3_analysis/            # 第三部分：静态分析与路径生成（层17-32）
│   │   ├── 📄 __init__.py
│   │   ├── 📄 layer_17_lexer.py       # 层17：词法分析Token化层
│   │   ├── 📄 layer_18_ast.py         # 层18：轻量AST构建层
│   │   ├── 📄 layer_19_slice.py       # 层19：函数单元切片层
│   │   ├── 📄 layer_20_func_semantic.py # 层20：函数语义理解层
│   │   ├── 📄 layer_21_dependency.py  # 层21：函数依赖分析层
│   │   ├── 📄 layer_22_cfg.py         # 层22：控制流CFG构建层
│   │   ├── 📄 layer_23_coverage_match.py # 层23：覆盖规则预匹配层
│   │   ├── 📄 layer_24_business_recognize.py # 层24：业务场景识别层
│   │   ├── 📄 layer_25_path_annotation.py # 层25：路径语义标注层
│   │   ├── 📄 layer_26_path_enum.py   # 层26：全路径枚举生成层
│   │   ├── 📄 layer_27_path_prune_llm.py # 层27：LLM辅助路径剪枝层
│   │   ├── 📄 layer_28_unreachable_verify.py # 层28：不可达路径验证层
│   │   ├── 📄 layer_29_path_priority.py # 层29：路径优先级排序层
│   │   ├── 📄 layer_30_smart_prune.py # 层30：智能路径剪枝层
│   │   ├── 📄 layer_31_explosion_protect.py # 层31：路径爆炸防护层
│   │   └── 📄 layer_32_testdata_guide.py # 层32：测试数据生成指导层
│   ├── 📂 part4_execution/           # 第四部分：测试用例生成与执行（层33-42）
│   │   ├── 📄 __init__.py
│   │   ├── 📄 layer_33_testdata_infer.py # 层33：测试数据推理层
│   │   ├── 📄 layer_34_testdata_llm.py # 层34：LLM增强测试数据生成层
│   │   ├── 📄 layer_35_template_render.py # 层35：用例模板渲染层
│   │   ├── 📄 layer_36_quality_evaluate.py # 层36：测试用例质量评估层
│   │   ├── 📄 layer_37_optimize.py    # 层37：测试用例优化层
│   │   ├── 📄 layer_38_orchestrate.py # 层38：用例集合编排层
│   │   ├── 📄 layer_39_mock_generate.py # 层39：Mock对象自动生成层
│   │   ├── 📄 layer_40_isolation.py   # 层40：内存级隔离执行层
│   │   ├── 📄 layer_41_concurrent.py  # 层41：用例并发执行层
│   │   └── 📄 layer_42_diagnosis.py   # 层42：执行异常智能诊断层
│   └── 📂 part5_output/              # 第五部分：结果分析与输出（层43-50）
│       ├── 📄 __init__.py
│       ├── 📄 layer_43_trace_collect.py # 层43：执行轨迹采集层
│       ├── 📄 layer_44_coverage_stat.py # 层44：覆盖率统计分析层
│       ├── 📄 layer_45_uncovered_analyze.py # 层45：未覆盖路径智能分析层
│       ├── 📄 layer_46_defect_grade.py # 层46：缺陷智能分级与定位层
│       ├── 📄 layer_47_fix_suggest.py # 层47：代码修复建议生成层
│       ├── 📄 layer_48_report_enhance.py # 层48：测试报告增强生成层
│       ├── 📄 layer_49_nl_query.py    # 层49：自然语言查询接口层
│       └── 📄 layer_50_persistence.py # 层50：结果输出持久层
└── 📂 plugins/                       # 插件模块
    ├── 📄 siliconflow.py             # 硅基流动API客户端
    ├── 📄 siliconflow_smart.py       # 硅基流动智能客户端
    └── 📄 free_models.py             # 免费模型统一客户端
```

---

## 📋 目录说明

### 🔵 核心模块

| 目录 | 说明 | 关键文件 |
|------|------|---------|
| `/` | 项目根目录 | [__init__.py](file:///workspace/path_test_system/__init__.py), [cli.py](file:///workspace/path_test_system/cli.py) |
| `config/` | 配置文件 | [default_config.json](file:///workspace/path_test_system/config/default_config.json) |
| `core/` | 核心数据模型和上下文 | [context.py](file:///workspace/path_test_system/core/context.py), [models/](file:///workspace/path_test_system/core/models/) |
| `docs/` | 文档 | [FREE_MODELS_GUIDE.md](file:///workspace/path_test_system/docs/FREE_MODELS_GUIDE.md) |
| `examples/` | 示例代码 | [simple_5_layer_system.py](file:///workspace/path_test_system/examples/simple_5_layer_system.py) |
| `layers/` | 50层实现 | [part1-5](file:///workspace/path_test_system/layers/) |
| `plugins/` | 插件 | [free_models.py](file:///workspace/path_test_system/plugins/free_models.py) |

### 🟢 50层组织

| 部分 | 层号 | 功能 | 目录 |
|------|------|------|------|
| 第一部分 | 1-8 | 用户交互与任务定义 | [layers/part1_interaction/](file:///workspace/path_test_system/layers/part1_interaction/) |
| 第二部分 | 9-16 | 源码接入与预处理 | [layers/part2_preprocessing/](file:///workspace/path_test_system/layers/part2_preprocessing/) |
| 第三部分 | 17-32 | 静态分析与路径生成 | [layers/part3_analysis/](file:///workspace/path_test_system/layers/part3_analysis/) |
| 第四部分 | 33-42 | 测试用例生成与执行 | [layers/part4_execution/](file:///workspace/path_test_system/layers/part4_execution/) |
| 第五部分 | 43-50 | 结果分析与输出 | [layers/part5_output/](file:///workspace/path_test_system/layers/part5_output/) |

---

## 🔗 关键引用路径

### 主入口
- 包入口：[path_test_system/__init__.py](file:///workspace/path_test_system/__init__.py)
- 命令行：[path_test_system/cli.py](file:///workspace/path_test_system/cli.py)
- API服务：[path_test_system/api_server.py](file:///workspace/path_test_system/api_server.py)

### 核心数据模型
- 上下文：[path_test_system/core/context.py](file:///workspace/path_test_system/core/context.py)
- 数据模型：[path_test_system/core/models/](file:///workspace/path_test_system/core/models/)

### 50层实现
- 交互层：[layers/part1_interaction/](file:///workspace/path_test_system/layers/part1_interaction/)
- 分析层：[layers/part3_analysis/](file:///workspace/path_test_system/layers/part3_analysis/)
- 输出层：[layers/part5_output/](file:///workspace/path_test_system/layers/part5_output/)

### 免费模型
- 免费模型客户端：[plugins/free_models.py](file:///workspace/path_test_system/plugins/free_models.py)
- 硅基流动：[plugins/siliconflow_smart.py](file:///workspace/path_test_system/plugins/siliconflow_smart.py)
