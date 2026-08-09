# 🔄 50层全路径代码测试系统 - 全流程时序

## 📊 完整数据流图

```
用户输入
   │
   ▼
┌─────────────────────────────────────────────────────────────────┐
│                    第一部分：用户交互与任务定义 (层1-8)          │
├─────────────────────────────────────────────────────────────────┤
│  [层1] 交互入口层                                                │
│         ↓ 接收用户输入，初始化上下文                              │
│  [层2] 任务生命周期管理层                                          │
│         ↓ 管理任务状态，断点续跑                                    │
│  [层3] 全局配置规则层                                              │
│         ↓ 加载配置，设置参数                                        │
│  [层4] 自然语言命令解析层                                          │
│         ↓ NLP解析，提取意图                                        │
│  [层5] LLM全局能力适配层  ← 使用免费模型                           │
│         ↓ LLM调用，智能分析                                        │
│  [层6] LLM全局缓存管理层                                          │
│         ↓ 缓存管理，成本控制                                        │
│  [层7] 测试目标语义理解层                                          │
│         ↓ 深度理解测试目标                                        │
│  [层8] 需求-代码映射分析层                                          │
│         ↓ 需求-代码关联分析                                        │
└─────────────────────────────────────────────────────────────────┘
   │
   ▼ 任务上下文 + 源码路径
┌─────────────────────────────────────────────────────────────────┐
│                    第二部分：源码接入与预处理 (层9-16)            │
├─────────────────────────────────────────────────────────────────┤
│  [层9] 源码接入扫描层                                             │
│         ↓ 扫描源码目录，识别文件                                  │
│  [层10] 增量缓存决策层                                             │
│         ↓ 判断是否使用缓存                                        │
│  [层11] 文件预处理清洗层                                          │
│         ↓ 去除注释，清洗代码                                       │
│  [层12] 多语言适配分发层                                          │
│         ↓ 语言识别，分发解析器                                     │
│  [层13] 代码语义摘要生成层                                          │
│         ↓ 生成语义摘要                                             │
│  [层14] 代码质量预扫描层                                          │
│         ↓ 质量检查，代码异味检测                                  │
│  [层15] 敏感代码识别层                                             │
│         ↓ 敏感信息检测                                             │
│  [层16] 测试风险评估层                                             │
│         ↓ 风险评估，优先级排序                                     │
└─────────────────────────────────────────────────────────────────┘
   │
   ▼ 预处理源码 + 语义摘要
┌─────────────────────────────────────────────────────────────────┐
│                  第三部分：静态分析与路径生成 (层17-32)          │
├─────────────────────────────────────────────────────────────────┤
│  [层17] 词法分析Token化层                                          │
│         ↓ 词法分析，生成Token                                    │
│  [层18] 轻量AST构建层                                             │
│         ↓ 构建抽象语法树                                           │
│  [层19] 函数单元切片层                                             │
│         ↓ 函数提取，代码切片                                       │
│  [层20] 函数语义理解层                                             │
│         ↓ 函数语义分析                                            │
│  [层21] 函数依赖分析层                                             │
│         ↓ 依赖图谱构建                                            │
│  [层22] 控制流CFG构建层  ← V3.1升级：跨函数CFG                      │
│         ↓ 控制流图构建                                            │
│  [层23] 覆盖规则预匹配层                                           │
│         ↓ 匹配覆盖规则                                            │
│  [层24] 业务场景识别层                                             │
│         ↓ 业务场景识别                                            │
│  [层25] 路径语义标注层                                             │
│         ↓ 路径语义标注                                            │
│  [层26] 全路径枚举生成层                                           │
│         ↓ 枚举所有执行路径                                        │
│  [层27] LLM辅助路径剪枝层                                          │
│         ↓ LLM智能剪枝                                             │
│  [层28] 不可达路径验证层                                           │
│         ↓ 验证路径可达性                                          │
│  [层29] 路径优先级排序层                                           │
│         ↓ 优先级排序                                             │
│  [层30] 智能路径剪枝层                                             │
│         ↓ 多策略剪枝                                             │
│  [层31] 路径爆炸防护层                                             │
│         ↓ 防止路径爆炸                                             │
│  [层32] 测试数据生成指导层                                         │
│         ↓ 生成测试数据规范                                       │
└─────────────────────────────────────────────────────────────────┘
   │
   ▼ 优化路径集 + 测试数据规范
┌─────────────────────────────────────────────────────────────────┐
│                  第四部分：测试用例生成与执行 (层33-42)          │
├─────────────────────────────────────────────────────────────────┤
│  [层33] 测试数据推理层                                            │
│         ↓ 推理测试数据                                            │
│  [层34] LLM增强测试数据生成层  ← V3.1升级                         │
│         ↓ LLM生成复杂测试数据                                     │
│  [层35] 用例模板渲染层                                            │
│         ↓ 渲染测试用例                                            │
│  [层36] 测试用例质量评估层  ← V3.1升级                             │
│         ↓ 质量评估，改进建议                                     │
│  [层37] 测试用例优化层                                            │
│         ↓ 用例优化                                                │
│  [层38] 用例集合编排层                                            │
│         ↓ 用例编排，版本管理                                      │
│  [层39] Mock对象自动生成层  ← V3.1升级                            │
│         ↓ 自动生成Mock                                           │
│  [层40] 内存级隔离执行层                                          │
│         ↓ 隔离环境准备                                            │
│  [层41] 用例并发执行层                                            │
│         ↓ 并发执行用例                                            │
│  [层42] 执行异常智能诊断层  ← V3.1升级                             │
│         ↓ 异常诊断，根因分析                                      │
└─────────────────────────────────────────────────────────────────┘
   │
   ▼ 执行结果 + 异常信息
┌─────────────────────────────────────────────────────────────────┐
│                  第五部分：结果分析与输出 (层43-50)              │
├─────────────────────────────────────────────────────────────────┤
│  [层43] 执行轨迹采集层                                             │
│         ↓ 采集执行轨迹                                            │
│  [层44] 覆盖率统计分析层  ← V3.1升级                              │
│         ↓ 覆盖率计算和分析                                        │
│  [层45] 未覆盖路径智能分析层  ← V3.1升级                          │
│         ↓ 未覆盖路径分析                                          │
│  [层46] 缺陷智能分级与定位层                                       │
│         ↓ 缺陷分级定位                                            │
│  [层47] 代码修复建议生成层                                        │
│         ↓ 修复建议生成                                            │
│  [层48] 测试报告增强生成层  ← V3.1升级                            │
│         ↓ 增强报告生成                                            │
│  [层49] 自然语言查询接口层                                        │
│         ↓ NLP查询接口                                             │
│  [层50] 结果输出持久层  ← V3.1升级                                │
│         ↓ 结果持久化，文件输出                                    │
└─────────────────────────────────────────────────────────────────┘
   │
   ▼
最终输出：HTML/JSON/Markdown报告 + 测试用例代码 + 覆盖率数据
```

---

## ⏱️ 详细时序说明

### 阶段一：用户交互与任务定义 (T0 - T1)

| 时间点 | 层号 | 操作 | 输入 | 输出 | 关键文件 |
|-------|------|------|------|------|---------|
| T0 | 1 | 交互入口层接收输入 | 用户命令/HTTP请求/配置 | PipelineContext | [layer_1_entry.py](file:///workspace/path_test_system/layers/part1_interaction/layer_1_entry.py) |
| T0.1 | 2 | 初始化任务生命周期 | PipelineContext | 任务状态 | [layer_2_lifecycle.py](file:///workspace/path_test_system/layers/part1_interaction/layer_2_lifecycle.py) |
| T0.2 | 3 | 加载全局配置 | 任务上下文 | ConfigSnapshot | [layer_3_config.py](file:///workspace/path_test_system/layers/part1_interaction/layer_3_config.py) |
| T0.3 | 4 | NLP解析命令 | 用户输入 | 结构化指令 | [layer_4_nlp_parser.py](file:///workspace/path_test_system/layers/part1_interaction/layer_4_nlp_parser.py) |
| T0.4 | 5 | LLM适配层 🔑 | 任务上下文 | LLM响应 | [layer_5_llm_adapter.py](file:///workspace/path_test_system/layers/part1_interaction/layer_5_llm_adapter.py) |
| T0.5 | 6 | LLM缓存管理 | LLM请求 | 缓存结果 | [layer_6_cache.py](file:///workspace/path_test_system/layers/part1_interaction/layer_6_cache.py) |
| T0.6 | 7 | 测试目标理解 | 用户意图 | 测试策略 | [layer_7_test_strategy.py](file:///workspace/path_test_system/layers/part1_interaction/layer_7_test_strategy.py) |
| T0.7 | 8 | 需求-代码映射 | 需求+代码 | 映射关系 | [layer_8_req_mapping.py](file:///workspace/path_test_system/layers/part1_interaction/layer_8_req_mapping.py) |

### 阶段二：源码接入与预处理 (T1 - T2)

| 时间点 | 层号 | 操作 | 输入 | 输出 | 关键文件 |
|-------|------|------|------|------|---------|
| T1 | 9 | 源码扫描 | 源码路径 | 文件列表 | [layer_9_source_scan.py](file:///workspace/path_test_system/layers/part2_preprocessing/layer_9_source_scan.py) |
| T1.1 | 10 | 增量缓存决策 | 文件列表 | 待解析文件 | [layer_10_incremental_cache.py](file:///workspace/path_test_system/layers/part2_preprocessing/layer_10_incremental_cache.py) |
| T1.2 | 11 | 代码清洗 | 源码文件 | 标准化代码 | [layer_11_preprocess.py](file:///workspace/path_test_system/layers/part2_preprocessing/layer_11_preprocess.py) |
| T1.3 | 12 | 语言适配 | 标准化代码 | 语言识别结果 | [layer_12_language_adapter.py](file:///workspace/path_test_system/layers/part2_preprocessing/layer_12_language_adapter.py) |
| T1.4 | 13 | 语义摘要生成 | 代码 | 语义摘要 | [layer_13_semantic_summary.py](file:///workspace/path_test_system/layers/part2_preprocessing/layer_13_semantic_summary.py) |
| T1.5 | 14 | 代码质量扫描 | 代码 | 质量问题列表 | [layer_14_quality_scan.py](file:///workspace/path_test_system/layers/part2_preprocessing/layer_14_quality_scan.py) |
| T1.6 | 15 | 敏感代码识别 | 代码 | 敏感位置 | [layer_15_sensitive_detect.py](file:///workspace/path_test_system/layers/part2_preprocessing/layer_15_sensitive_detect.py) |
| T1.7 | 16 | 风险评估 | 质量+语义 | 风险评分 | [layer_16_risk_assessment.py](file:///workspace/path_test_system/layers/part2_preprocessing/layer_16_risk_assessment.py) |

### 阶段三：静态分析与路径生成 (T2 - T3)

| 时间点 | 层号 | 操作 | 输入 | 输出 | 关键文件 |
|-------|------|------|------|------|---------|
| T2 | 17 | 词法分析 | 代码 | Token流 | [layer_17_lexer.py](file:///workspace/path_test_system/layers/part3_analysis/layer_17_lexer.py) |
| T2.1 | 18 | AST构建 | Token流 | 轻量AST | [layer_18_ast.py](file:///workspace/path_test_system/layers/part3_analysis/layer_18_ast.py) |
| T2.2 | 19 | 函数切片 | AST | 函数切片列表 | [layer_19_slice.py](file:///workspace/path_test_system/layers/part3_analysis/layer_19_slice.py) |
| T2.3 | 20 | 函数语义理解 | 函数切片 | 函数语义 | [layer_20_func_semantic.py](file:///workspace/path_test_system/layers/part3_analysis/layer_20_func_semantic.py) |
| T2.4 | 21 | 依赖分析 | 函数切片 | 依赖图谱 | [layer_21_dependency.py](file:///workspace/path_test_system/layers/part3_analysis/layer_21_dependency.py) |
| T2.5 | 22 | CFG构建 | 函数切片+依赖 | 控制流图 | [layer_22_cfg.py](file:///workspace/path_test_system/layers/part3_analysis/layer_22_cfg.py) |
| T2.6 | 23 | 覆盖规则匹配 | CFG | 标记CFG | [layer_23_coverage_match.py](file:///workspace/path_test_system/layers/part3_analysis/layer_23_coverage_match.py) |
| T2.7 | 24 | 业务场景识别 | CFG+语义 | 业务场景 | [layer_24_business_recognize.py](file:///workspace/path_test_system/layers/part3_analysis/layer_24_business_recognize.py) |
| T2.8 | 25 | 路径语义标注 | 路径集 | 标注路径 | [layer_25_path_annotation.py](file:///workspace/path_test_system/layers/part3_analysis/layer_25_path_annotation.py) |
| T2.9 | 26 | 路径枚举 | CFG | 初始路径集 | [layer_26_path_enum.py](file:///workspace/path_test_system/layers/part3_analysis/layer_26_path_enum.py) |
| T2.10 | 27 | LLM路径剪枝 | 路径集 | 优化路径集 | [layer_27_path_prune_llm.py](file:///workspace/path_test_system/layers/part3_analysis/layer_27_path_prune_llm.py) |
| T2.11 | 28 | 不可达验证 | 标记路径 | 验证结果 | [layer_28_unreachable_verify.py](file:///workspace/path_test_system/layers/part3_analysis/layer_28_unreachable_verify.py) |
| T2.12 | 29 | 路径优先级排序 | 路径集 | 排序路径 | [layer_29_path_priority.py](file:///workspace/path_test_system/layers/part3_analysis/layer_29_path_priority.py) |
| T2.13 | 30 | 智能路径剪枝 | 路径集 | 最小路径集 | [layer_30_smart_prune.py](file:///workspace/path_test_system/layers/part3_analysis/layer_30_smart_prune.py) |
| T2.14 | 31 | 路径爆炸防护 | 路径集 | 可执行子集 | [layer_31_explosion_protect.py](file:///workspace/path_test_system/layers/part3_analysis/layer_31_explosion_protect.py) |
| T2.15 | 32 | 测试数据指导 | 路径集 | 数据生成规范 | [layer_32_testdata_guide.py](file:///workspace/path_test_system/layers/part3_analysis/layer_32_testdata_guide.py) |

### 阶段四：测试用例生成与执行 (T3 - T4)

| 时间点 | 层号 | 操作 | 输入 | 输出 | 关键文件 |
|-------|------|------|------|------|---------|
| T3 | 33 | 测试数据推理 | 路径+规范 | 基础测试数据 | [layer_33_testdata_infer.py](file:///workspace/path_test_system/layers/part4_execution/layer_33_testdata_infer.py) |
| T3.1 | 34 | LLM增强数据生成 | 基础数据 | 增强测试数据 | [layer_34_testdata_llm.py](file:///workspace/path_test_system/layers/part4_execution/layer_34_testdata_llm.py) |
| T3.2 | 35 | 模板渲染 | 测试数据 | 用例代码 | [layer_35_template_render.py](file:///workspace/path_test_system/layers/part4_execution/layer_35_template_render.py) |
| T3.3 | 36 | 用例质量评估 | 用例代码 | 质量评分 | [layer_36_quality_evaluate.py](file:///workspace/path_test_system/layers/part4_execution/layer_36_quality_evaluate.py) |
| T3.4 | 37 | 用例优化 | 低质量用例 | 优化用例 | [layer_37_optimize.py](file:///workspace/path_test_system/layers/part4_execution/layer_37_optimize.py) |
| T3.5 | 38 | 用例编排 | 用例集合 | 执行计划 | [layer_38_orchestrate.py](file:///workspace/path_test_system/layers/part4_execution/layer_38_orchestrate.py) |
| T3.6 | 39 | Mock生成 | 依赖分析 | Mock代码 | [layer_39_mock_generate.py](file:///workspace/path_test_system/layers/part4_execution/layer_39_mock_generate.py) |
| T3.7 | 40 | 隔离环境准备 | 执行计划 | 隔离环境 | [layer_40_isolation.py](file:///workspace/path_test_system/layers/part4_execution/layer_40_isolation.py) |
| T3.8 | 41 | 并发执行 | 执行计划 | 执行结果 | [layer_41_concurrent.py](file:///workspace/path_test_system/layers/part4_execution/layer_41_concurrent.py) |
| T3.9 | 42 | 异常诊断 | 失败结果 | 诊断报告 | [layer_42_diagnosis.py](file:///workspace/path_test_system/layers/part4_execution/layer_42_diagnosis.py) |

### 阶段五：结果分析与输出 (T4 - T5)

| 时间点 | 层号 | 操作 | 输入 | 输出 | 关键文件 |
|-------|------|------|------|------|---------|
| T4 | 43 | 轨迹采集 | 执行过程 | 轨迹数据 | [layer_43_trace_collect.py](file:///workspace/path_test_system/layers/part5_output/layer_43_trace_collect.py) |
| T4.1 | 44 | 覆盖率统计 | 轨迹数据 | 覆盖率报告 | [layer_44_coverage_stat.py](file:///workspace/path_test_system/layers/part5_output/layer_44_coverage_stat.py) |
| T4.2 | 45 | 未覆盖路径分析 | 覆盖率+路径 | 分析报告 | [layer_45_uncovered_analyze.py](file:///workspace/path_test_system/layers/part5_output/layer_45_uncovered_analyze.py) |
| T4.3 | 46 | 缺陷分级定位 | 失败结果 | 缺陷报告 | [layer_46_defect_grade.py](file:///workspace/path_test_system/layers/part5_output/layer_46_defect_grade.py) |
| T4.4 | 47 | 修复建议生成 | 缺陷报告 | 修复建议 | [layer_47_fix_suggest.py](file:///workspace/path_test_system/layers/part5_output/layer_47_fix_suggest.py) |
| T4.5 | 48 | 报告增强生成 | 所有结果 | 增强报告 | [layer_48_report_enhance.py](file:///workspace/path_test_system/layers/part5_output/layer_48_report_enhance.py) |
| T4.6 | 49 | NLP查询接口 | 用户查询 | 查询结果 | [layer_49_nl_query.py](file:///workspace/path_test_system/layers/part5_output/layer_49_nl_query.py) |
| T4.7 | 50 | 结果持久化 | 所有结果 | 文件输出 | [layer_50_persistence.py](file:///workspace/path_test_system/layers/part5_output/layer_50_persistence.py) |

---

## 🔑 关键数据流节点

### PipelineContext 传递

```
[层1] 创建 PipelineContext
    │
    ├─→ [层2-8] 补充任务信息
    │
    ├─→ [层9-16] 添加源码处理数据
    │
    ├─→ [层17-32] 添加分析结果和路径数据
    │
    ├─→ [层33-42] 添加测试执行数据
    │
    └─→ [层43-50] 添加报告和输出数据
```

### 免费模型集成点

```
[层5] LLM适配层 → 使用免费模型客户端
         ↑
         ├─ 模拟模式（默认）
         ├─ 硅基流动API
         └─ Ollama本地
```

---

## 📊 性能特点

| 阶段 | 复杂度 | 可并行度 | 耗时占比 |
|------|--------|---------|---------|
| 交互层 | 低 | 低 | 5% |
| 预处理层 | 中 | 高 | 15% |
| 分析层 | 高 | 中 | 40% |
| 执行层 | 高 | 高 | 25% |
| 输出层 | 中 | 低 | 15% |

---

## 🔗 相关文件

- 目录结构文档：[DIRECTORY_STRUCTURE.md](file:///workspace/path_test_system/docs/DIRECTORY_STRUCTURE.md)
- 免费模型使用：[FREE_MODELS_GUIDE.md](file:///workspace/path_test_system/docs/FREE_MODELS_GUIDE.md)
- 快速开始：[QUICK_START.md](file:///workspace/path_test_system/docs/QUICK_START.md)
