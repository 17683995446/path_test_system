"""
Layer 34: LLM Test Data Generation Layer (LLM增强测试数据生成层) 【V3.1升级】

该层利用大语言模型增强测试数据生成能力，能够基于代码上下文、
业务语义和测试策略智能生成高质量的测试数据。支持复杂场景的
测试用例数据自动构造和增强。

V3.1升级特性：
- 深度语义理解能力增强
- 上下文感知的数据生成
- 多样化测试场景覆盖
- 智能边界值推测
- 业务规则自动学习
"""

from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import random


class LLMModelType(Enum):
    """LLM模型类型"""
    GPT4 = "gpt-4"
    GPT35 = "gpt-3.5-turbo"
    CLAUDE = "claude-3"
    LOCAL = "local-model"
    HYBRID = "hybrid"


class TestDataGenerationStrategy(Enum):
    """测试数据生成策略"""
    SEMANTIC = "semantic"  # 基于语义的生成
    BOUNDARY = "boundary"  # 边界值分析
    EQUIVALENCE = "equivalence"  # 等价类划分
    COMBINATORIAL = "combinatorial"  # 组合测试
    FUZZING = "fuzzing"  # 模糊测试
    SEMANTIC_FUZZING = "semantic_fuzzing"  # 语义模糊测试


@dataclass
class GenerationPrompt:
    """生成提示词"""
    template: str
    context_data: Dict[str, Any]
    constraints: List[str] = field(default_factory=list)
    examples: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TestDataCase:
    """测试数据用例"""
    case_id: str
    case_name: str
    input_data: Dict[str, Any]
    expected_output: Optional[Any] = None
    generation_strategy: TestDataGenerationStrategy = TestDataGenerationStrategy.SEMANTIC
    confidence_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


@dataclass
class LLMPromptTemplate:
    """LLM提示词模板"""
    system_prompt: str = """你是一个专业的测试数据生成专家，精通各种编程语言和测试框架。
你的任务是分析给定的代码上下文和业务规则，生成高质量、多样化的测试数据。"""
    
    data_generation_template: str = """
## 任务
为以下函数/方法生成测试数据：

### 代码上下文
```python
{function_code}
```

### 函数签名
{function_signature}

### 业务规则
{business_rules}

### 类型约束
{type_constraints}

## 要求
1. 生成至少{min_cases}个测试用例
2. 覆盖正常场景、边界场景、异常场景
3. 考虑数据类型的多样性（空值、特殊字符、大小写等）
4. 提供每个用例的预期输入和输出

## 输出格式
请以JSON格式输出：
{{
    "test_cases": [
        {{
            "name": "测试用例名称",
            "inputs": {{"param1": 值, "param2": 值}},
            "expected_output": 预期输出,
            "scenario": "场景描述",
            "tags": ["tag1", "tag2"]
        }}
    ]
}}
"""


@dataclass
class LLMTestDataResult:
    """LLM增强测试数据生成结果"""
    generated_cases: List[TestDataCase] = field(default_factory=list)
    total_cases: int = 0
    generation_strategies_used: List[TestDataGenerationStrategy] = field(default_factory=list)
    llm_calls: int = 0
    generation_time_ms: float = 0.0
    quality_score: float = 0.0
    coverage_improvement: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class LLMTestDataLayer:
    """
    LLM增强测试数据生成层 【V3.1升级】

    利用大语言模型增强测试数据生成能力，基于代码上下文和业务语义
    智能生成高质量的测试数据用例。

    核心功能：
    - 深度语义理解：理解代码的业务逻辑和功能意图
    - 上下文感知生成：基于函数签名、类型注解、注释等上下文信息生成数据
    - 多样化覆盖：生成涵盖正常、边界、异常等多种场景的测试数据
    - 智能边界推测：通过语义分析推测潜在的边界条件
    - 业务规则学习：从代码和文档中提取业务规则并应用于数据生成

    V3.1升级特性：
    - 增强的语义分析引擎
    - 改进的上下文理解能力
    - 更智能的边界值推测算法
    - 支持多种LLM模型集成
    - 质量评估和覆盖率分析

    Attributes:
        description: 层的功能描述
        input_type: 输入数据类型 (PipelineContext)
        output_type: 输出数据类型 (LLMTestDataResult)

    Input Context Fields:
        - inferred_test_data: 从TestDataInferLayer推断的测试数据
        - source_analysis_result: 源代码分析结果
        - semantic_summary: 语义摘要信息
        - business_rules: 业务规则列表
        - llm_config: LLM配置信息
        - generation_strategies: 使用的生成策略列表

    Output:
        LLMTestDataResult: LLM增强生成的测试数据结果
    """

    description: str = "LLM增强测试数据生成层 - 基于语义和上下文智能生成测试数据 【V3.1升级】"
    input_type: str = "PipelineContext"
    output_type: str = "LLMTestDataResult"

    DEFAULT_LLM_CONFIG: Dict[str, Any] = {
        'model_type': LLMModelType.GPT35,
        'temperature': 0.7,
        'max_tokens': 2000,
        'timeout': 30,
        'retry_count': 3
    }

    def __init__(self, llm_config: Optional[Dict[str, Any]] = None):
        """
        初始化LLM增强测试数据生成层

        Args:
            llm_config: LLM配置字典，包含：
                - model_type: LLM模型类型
                - temperature: 生成温度
                - max_tokens: 最大token数
                - timeout: 超时时间
                - retry_count: 重试次数
        """
        self.llm_config = {**self.DEFAULT_LLM_CONFIG, **(llm_config or {})}
        self.prompt_template = LLMPromptTemplate()

    def process(self, context: Any) -> LLMTestDataResult:
        """
        执行LLM增强测试数据生成

        Args:
            context: PipelineContext对象，包含以下预期字段：
                - inferred_test_data: 从TestDataInferLayer推断的测试数据
                - source_analysis_result: 源代码分析结果
                - semantic_summary: 语义摘要信息
                - business_rules: 业务规则列表
                - function_signatures: 函数签名列表
                - type_hints: 类型注解信息
                - llm_config: LLM配置信息 (可选)
                - generation_strategies: 使用的生成策略列表 (可选)

        Returns:
            LLMTestDataResult: LLM增强生成的测试数据结果，包含：
                - generated_cases: 生成的测试用例列表
                - total_cases: 总用例数
                - generation_strategies_used: 使用的生成策略
                - llm_calls: LLM调用次数
                - generation_time_ms: 生成耗时（毫秒）
                - quality_score: 质量评分
                - coverage_improvement: 覆盖率提升
                - metadata: 附加元数据

        Process Flow:
            1. 收集代码上下文和语义信息
            2. 构建LLM提示词
            3. 调用LLM生成测试数据
            4. 解析和验证生成的数据
            5. 应用多种生成策略增强数据
            6. 质量评估和覆盖率分析
            7. 返回最终结果

        Example:
            >>> layer = LLMTestDataLayer()
            >>> ctx = create_context()
            >>> ctx.set('inferred_test_data', inferred_data)
            >>> ctx.set('business_rules', ['规则1', '规则2'])
            >>> result = layer.process(ctx)
            >>> print(f"生成用例数: {result.total_cases}")
            >>> print(f"质量评分: {result.quality_score}")
        """
        import time
        start_time = time.time()

        inferred_test_data = context.get('inferred_test_data')
        source_analysis = context.get('source_analysis_result', {})
        semantic_summary = context.get('semantic_summary', {})
        business_rules = context.get('business_rules', [])
        function_signatures = context.get('function_signatures', [])
        generation_strategies = context.get(
            'generation_strategies',
            [TestDataGenerationStrategy.SEMANTIC]
        )

        result = LLMTestDataResult()
        result.generation_strategies_used = list(generation_strategies)

        context_data = self._prepare_context_data(
            inferred_test_data, source_analysis, semantic_summary
        )

        for strategy in generation_strategies:
            if strategy == TestDataGenerationStrategy.SEMANTIC:
                semantic_cases = self._generate_semantic_cases(
                    function_signatures, business_rules, context_data
                )
                result.generated_cases.extend(semantic_cases)
                result.llm_calls += 1

            elif strategy == TestDataGenerationStrategy.BOUNDARY:
                boundary_cases = self._generate_boundary_cases(
                    inferred_test_data, business_rules
                )
                result.generated_cases.extend(boundary_cases)

            elif strategy == TestDataGenerationStrategy.EQUIVALENCE:
                equivalence_cases = self._generate_equivalence_cases(
                    inferred_test_data, context_data
                )
                result.generated_cases.extend(equivalence_cases)
                result.llm_calls += 1

            elif strategy == TestDataGenerationStrategy.SEMANTIC_FUZZING:
                fuzz_cases = self._generate_semantic_fuzzing_cases(
                    function_signatures, business_rules
                )
                result.generated_cases.extend(fuzz_cases)
                result.llm_calls += 1

        self._remove_duplicates(result.generated_cases)

        result.total_cases = len(result.generated_cases)
        result.generation_time_ms = (time.time() - start_time) * 1000

        result.quality_score = self._calculate_quality_score(result.generated_cases)

        if inferred_test_data:
            result.coverage_improvement = self._calculate_coverage_improvement(
                result.generated_cases, inferred_test_data
            )

        result.metadata = {
            'llm_config': self.llm_config,
            'context_size': len(json.dumps(context_data)),
            'strategies_applied': len(generation_strategies),
            'unique_scenarios': len(set(c.scenario for c in result.generated_cases if hasattr(c, 'scenario'))),
            'generation_timestamp': time.time()
        }

        context.set('llm_test_data_result', result)
        context.set('enhanced_test_cases', result.generated_cases)
        context.set('test_data_quality_score', result.quality_score)

        return result

    def _prepare_context_data(
        self, inferred_test_data: Any,
        source_analysis: Dict[str, Any],
        semantic_summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """准备LLM上下文数据"""
        context = {
            'source_info': {
                'file_count': source_analysis.get('file_count', 0),
                'functions': source_analysis.get('functions', []),
                'classes': source_analysis.get('classes', [])
            },
            'semantic_info': semantic_summary,
            'inferred_data_summary': {
                'total_functions': len(inferred_test_data.function_test_data_list)
                    if inferred_test_data else 0,
                'total_params': sum(
                    len(ftd.test_data_specs)
                    for ftd in (inferred_test_data.function_test_data_list or [])
                )
            }
        }
        return context

    def _generate_semantic_cases(
        self, function_signatures: List[Dict[str, Any]],
        business_rules: List[str],
        context_data: Dict[str, Any]
    ) -> List[TestDataCase]:
        """基于语义生成测试用例"""
        cases = []
        prompt = self._build_semantic_prompt(function_signatures, business_rules, context_data)

        llm_response = self._call_llm(prompt)

        parsed_cases = self._parse_llm_response(llm_response)

        for i, parsed in enumerate(parsed_cases):
            case = TestDataCase(
                case_id=f"semantic_{i+1}",
                case_name=parsed.get('name', f'semantic_case_{i+1}'),
                input_data=parsed.get('inputs', {}),
                expected_output=parsed.get('expected_output'),
                generation_strategy=TestDataGenerationStrategy.SEMANTIC,
                confidence_score=0.85,
                metadata={'scenario': parsed.get('scenario', 'semantic')},
                tags=parsed.get('tags', [])
            )
            cases.append(case)

        return cases

    def _generate_boundary_cases(
        self, inferred_test_data: Any,
        business_rules: List[str]
    ) -> List[TestDataCase]:
        """生成边界值测试用例"""
        cases = []

        if not inferred_test_data:
            return cases

        for ftd in (inferred_test_data.function_test_data_list or []):
            for spec in ftd.test_data_specs:
                type_info = spec.type_info

                for boundary_value in spec.boundary_values[:5]:
                    case = TestDataCase(
                        case_id=f"boundary_{ftd.function_name}_{spec.param_name}_{boundary_value}",
                        case_name=f"{ftd.function_name}_{spec.param_name}_boundary_{boundary_value}",
                        input_data={spec.param_name: boundary_value},
                        generation_strategy=TestDataGenerationStrategy.BOUNDARY,
                        confidence_score=0.9,
                        metadata={
                            'parameter': spec.param_name,
                            'type': type_info.type_name,
                            'category': 'boundary'
                        },
                        tags=['boundary', type_info.type_name]
                    )
                    cases.append(case)

        return cases

    def _generate_equivalence_cases(
        self, inferred_test_data: Any,
        context_data: Dict[str, Any]
    ) -> List[TestDataCase]:
        """生成等价类测试用例"""
        cases = []

        if not inferred_test_data:
            return cases

        for ftd in (inferred_test_data.function_test_data_list or []):
            for spec in ftd.test_data_specs:
                inferred_values = spec.inferred_values[:3]

                for value in inferred_values:
                    case = TestDataCase(
                        case_id=f"equivalence_{ftd.function_name}_{spec.param_name}_{value}",
                        case_name=f"{ftd.function_name}_{spec.param_name}_eq_{type(value).__name__}",
                        input_data={spec.param_name: value},
                        generation_strategy=TestDataGenerationStrategy.EQUIVALENCE,
                        confidence_score=0.8,
                        metadata={
                            'parameter': spec.param_name,
                            'equivalence_class': type(value).__name__,
                            'category': 'equivalence'
                        },
                        tags=['equivalence', type(value).__name__]
                    )
                    cases.append(case)

        return cases

    def _generate_semantic_fuzzing_cases(
        self, function_signatures: List[Dict[str, Any]],
        business_rules: List[str]
    ) -> List[TestDataCase]:
        """生成语义模糊测试用例"""
        cases = []
        fuzz_templates = [
            {'type': 'string', 'values': ['test', 'TEST', 'Test123', '', ' ', '\n\t', '<script>alert(1)</script>']},
            {'type': 'number', 'values': [0, 1, -1, 999999, 2147483647, 0.0, -0.0]},
            {'type': 'boolean', 'values': [True, False, None]},
            {'type': 'null', 'values': [None, 'null', 'NULL', '']},
        ]

        for sig in function_signatures[:3]:
            func_name = sig.get('name', 'unknown')
            params = sig.get('params', [])

            if not params:
                fuzz_input = random.choice(fuzz_templates)
                case = TestDataCase(
                    case_id=f"fuzz_{func_name}_{random.randint(1000, 9999)}",
                    case_name=f"{func_name}_fuzzing",
                    input_data={'value': random.choice(fuzz_input['values'])},
                    generation_strategy=TestDataGenerationStrategy.SEMANTIC_FUZZING,
                    confidence_score=0.7,
                    metadata={'category': 'fuzzing', 'strategy': 'semantic'},
                    tags=['fuzzing', 'semantic']
                )
                cases.append(case)

        return cases

    def _build_semantic_prompt(
        self, function_signatures: List[Dict[str, Any]],
        business_rules: List[str],
        context_data: Dict[str, Any]
    ) -> GenerationPrompt:
        """构建语义生成提示词"""
        template = self.prompt_template.data_generation_template

        function_code = self._extract_function_code(function_signatures)
        function_sig_str = '\n'.join([
            f"{sig.get('name', 'unknown')}({', '.join([p.get('type', 'Any') for p in sig.get('params', [])])})"
            for sig in function_signatures[:5]
        ])

        business_rules_str = '\n'.join([f"- {rule}" for rule in business_rules[:10]])

        type_constraints_str = json.dumps(
            context_data.get('semantic_info', {}),
            indent=2,
            ensure_ascii=False
        )

        filled_template = template.format(
            function_code=function_code or '# No code available',
            function_signature=function_sig_str or 'unknown()',
            business_rules=business_rules_str or 'No business rules specified',
            type_constraints=type_constraints_str or '{}',
            min_cases=5
        )

        return GenerationPrompt(
            template=filled_template,
            context_data=context_data,
            constraints=['保持数据类型一致性', '考虑空值和异常情况']
        )

    def _extract_function_code(self, function_signatures: List[Dict[str, Any]]) -> str:
        """提取函数代码"""
        codes = []
        for sig in function_signatures[:3]:
            name = sig.get('name', 'unknown')
            params = sig.get('params', [])
            return_type = sig.get('return_type', 'Any')

            param_str = ', '.join([
                f"{p.get('name', 'arg')}: {p.get('type', 'Any')}"
                for p in params
            ])

            codes.append(f"def {name}({param_str}) -> {return_type}:\\n    pass")
        return '\n\n'.join(codes)

    def _call_llm(self, prompt: GenerationPrompt) -> str:
        """
        调用LLM生成测试数据

        这里应该集成实际的LLM API调用
        当前实现为模拟响应
        """
        model_type = self.llm_config.get('model_type', LLMModelType.GPT35)

        mock_response = {
            "test_cases": [
                {
                    "name": "正常输入场景",
                    "inputs": {"value": "test"},
                    "expected_output": None,
                    "scenario": "验证基本功能",
                    "tags": ["normal", "basic"]
                },
                {
                    "name": "边界值测试",
                    "inputs": {"value": ""},
                    "expected_output": None,
                    "scenario": "空字符串边界",
                    "tags": ["boundary", "edge"]
                },
                {
                    "name": "特殊字符测试",
                    "inputs": {"value": "!@#$%^&*()"},
                    "expected_output": None,
                    "scenario": "特殊字符处理",
                    "tags": ["special", "character"]
                }
            ]
        }

        return json.dumps(mock_response, ensure_ascii=False)

    def _parse_llm_response(self, response: str) -> List[Dict[str, Any]]:
        """解析LLM响应"""
        try:
            data = json.loads(response)
            return data.get('test_cases', [])
        except (json.JSONDecodeError, KeyError):
            return []

    def _remove_duplicates(self, cases: List[TestDataCase]) -> None:
        """移除重复用例"""
        seen = set()
        unique_cases = []

        for case in cases:
            case_signature = json.dumps(case.input_data, sort_keys=True)
            if case_signature not in seen:
                seen.add(case_signature)
                unique_cases.append(case)

        cases.clear()
        cases.extend(unique_cases)

    def _calculate_quality_score(self, cases: List[TestDataCase]) -> float:
        """计算生成质量评分"""
        if not cases:
            return 0.0

        total_score = 0.0

        for case in cases:
            score = case.confidence_score

            if case.input_data:
                score += 0.1
            if case.expected_output is not None:
                score += 0.1
            if len(case.tags) > 0:
                score += 0.05

            total_score += min(score, 1.0)

        avg_score = total_score / len(cases)
        return round(avg_score * 100, 2)

    def _calculate_coverage_improvement(
        self, generated_cases: List[TestDataCase],
        inferred_test_data: Any
    ) -> float:
        """计算覆盖率提升"""
        if not inferred_test_data:
            return 0.0

        base_coverage = inferred_test_data.type_coverage or 0.0

        unique_types = set()
        for case in generated_cases:
            for value in case.input_data.values():
                unique_types.add(type(value).__name__)

        new_coverage = min(base_coverage + len(unique_types) * 5, 100.0)

        improvement = new_coverage - base_coverage
        return round(improvement, 2)
