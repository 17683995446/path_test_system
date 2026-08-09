"""
Layer 35: Template Render Layer (用例模板渲染层)

该层负责将测试用例数据渲染到预定义的测试用例模板中，
支持多种测试框架（pytest、unittest、JUnit等），生成可执行的测试代码。
提供灵活的模板引擎，支持变量替换、条件渲染和循环渲染。
"""

from typing import Any, Dict, List, Optional, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import re


class TestFramework(Enum):
    """测试框架类型"""
    PYTEST = "pytest"
    UNITTEST = "unittest"
    JUNIT = "junit"
    TESTNG = "testng"
    GTEST = "gtest"
    CATCH2 = "catch2"
    GO_TEST = "go_test"


class TemplateType(Enum):
    """模板类型"""
    FUNCTION_TEST = "function_test"
    CLASS_TEST = "class_test"
    INTEGRATION_TEST = "integration_test"
    API_TEST = "api_test"
    UI_TEST = "ui_test"
    PERFORMANCE_TEST = "performance_test"


@dataclass
class TemplateVariable:
    """模板变量"""
    name: str
    value: Any
    variable_type: str = "string"
    is_required: bool = True
    default_value: Any = None
    description: str = ""


@dataclass
class RenderedTestCase:
    """渲染后的测试用例"""
    test_id: str
    test_name: str
    test_code: str
    framework: TestFramework
    template_type: TemplateType
    imports: List[str] = field(default_factory=list)
    fixtures: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    line_count: int = 0


@dataclass
class Template:
    """测试用例模板"""
    template_id: str
    template_type: TemplateType
    framework: TestFramework
    template_content: str
    variables: List[TemplateVariable] = field(default_factory=list)
    supported_languages: List[str] = field(default_factory=lambda: ["python", "java", "javascript", "go"])
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TemplateRenderResult:
    """模板渲染结果"""
    rendered_cases: List[RenderedTestCase] = field(default_factory=list)
    total_cases: int = 0
    success_count: int = 0
    failure_count: int = 0
    total_lines: int = 0
    framework_used: TestFramework = TestFramework.PYTEST
    metadata: Dict[str, Any] = field(default_factory=dict)


class TemplateRenderLayer:
    """
    用例模板渲染层

    负责将测试用例数据渲染到预定义的测试用例模板中，
    支持多种测试框架和编程语言。

    核心功能：
    - 多框架支持：pytest、unittest、JUnit、TestNG、Google Test等
    - 灵活模板引擎：支持变量替换、条件渲染、循环渲染
    - 智能变量解析：自动识别和处理模板变量
    - 代码生成优化：格式化、导入优化、注释生成
    - 模板管理：模板的创建、验证、版本管理

    Attributes:
        description: 层的功能描述
        input_type: 输入数据类型 (PipelineContext)
        output_type: str = "TemplateRenderResult"

    Input Context Fields:
        - test_cases: 测试用例数据列表
        - test_framework: 使用的测试框架
        - template_type: 模板类型
        - language: 目标编程语言
        - templates: 自定义模板字典（可选）
        - render_options: 渲染选项

    Output:
        TemplateRenderResult: 渲染后的测试用例结果
    """

    description: str = "用例模板渲染层 - 将测试数据渲染为可执行测试代码"
    input_type: str = "PipelineContext"
    output_type: str = "TemplateRenderResult"

    PYTEST_FUNCTION_TEMPLATE = '''"""
{test_docstring}
"""

import pytest
{imports}


class Test{class_name}:
    """测试类：{class_name}"""

    {fixtures}

    def test_{test_name}(self{fixture_params}):
        """
        测试方法：{test_name}
        
        测试场景：{scenario}
        """
        {setup_code}
        
        # 执行被测试函数
        {actual_code}
        
        # 断言验证
        {assertions}
        
        {teardown_code}
'''

    PYTEST_CLASS_TEMPLATE = '''"""
{test_docstring}
"""

import pytest
{imports}


@pytest.fixture
def {fixture_name}():
    """测试fixture：{fixture_name}"""
    {fixture_setup}
    yield
    {fixture_teardown}


class Test{class_name}:
    """测试类：{class_name}"""
    
    {class_docstring}

    @pytest.fixture(autouse=True)
    def setup_method(self, {fixture_name}):
        """每个测试方法执行前的setup"""
        {setup_code}

    {test_methods}

    def teardown_method(self):
        """每个测试方法执行后的teardown"""
        {teardown_code}
'''

    UNITTEST_TEMPLATE = '''"""
{test_docstring}
"""

import unittest
{imports}


class Test{class_name}(unittest.TestCase):
    """测试类：{class_name}"""

    def setUp(self):
        """测试前的setup"""
        {setup_code}

    def tearDown(self):
        """测试后的teardown"""
        {teardown_code}

    {test_methods}
'''

    JUNIT_TEMPLATE = '''package {package_name};

import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

/**
 * 测试类：{class_name}
 * {test_docstring}
 */

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class Test{class_name} {{

    {setup_method}

    @AfterEach
    void tearDown() {{
        {teardown_code}
    }}

    {test_methods}
}}
'''

    def __init__(self, default_framework: TestFramework = TestFramework.PYTEST):
        """
        初始化模板渲染层

        Args:
            default_framework: 默认测试框架
        """
        self.default_framework = default_framework
        self.templates: Dict[str, Template] = {}
        self._initialize_default_templates()

    def _initialize_default_templates(self) -> None:
        """初始化默认模板"""
        self.templates['pytest_function'] = Template(
            template_id='pytest_function',
            template_type=TemplateType.FUNCTION_TEST,
            framework=TestFramework.PYTEST,
            template_content=self.PYTEST_FUNCTION_TEMPLATE,
            supported_languages=['python']
        )

        self.templates['pytest_class'] = Template(
            template_id='pytest_class',
            template_type=TemplateType.CLASS_TEST,
            framework=TestFramework.PYTEST,
            template_content=self.PYTEST_CLASS_TEMPLATE,
            supported_languages=['python']
        )

        self.templates['unittest'] = Template(
            template_id='unittest',
            template_type=TemplateType.CLASS_TEST,
            framework=TestFramework.UNITTEST,
            template_content=self.UNITTEST_TEMPLATE,
            supported_languages=['python']
        )

        self.templates['junit'] = Template(
            template_id='junit',
            template_type=TemplateType.CLASS_TEST,
            framework=TestFramework.JUNIT,
            template_content=self.JUNIT_TEMPLATE,
            supported_languages=['java']
        )

    def process(self, context: Any) -> TemplateRenderResult:
        """
        执行模板渲染

        Args:
            context: PipelineContext对象，包含以下预期字段：
                - test_cases: 测试用例数据列表
                - llm_test_data_result: LLM生成的测试数据
                - inferred_test_data: 推断的测试数据
                - test_framework: 使用的测试框架 (TestFramework)
                - template_type: 模板类型 (TemplateType)
                - language: 目标编程语言
                - templates: 自定义模板字典（可选）
                - render_options: 渲染选项字典 (可选)
                    - include_docstrings: 是否包含文档字符串
                    - include_comments: 是否包含注释
                    - code_style: 代码风格 (pep8, google, etc.)
                    - max_line_length: 最大行长度

        Returns:
            TemplateRenderResult: 渲染结果，包含：
                - rendered_cases: 渲染后的测试用例列表
                - total_cases: 总用例数
                - success_count: 成功渲染的用例数
                - failure_count: 渲染失败的用例数
                - total_lines: 总代码行数
                - framework_used: 使用的测试框架
                - metadata: 附加元数据

        Process Flow:
            1. 获取测试用例数据和渲染配置
            2. 选择或加载模板
            3. 预处理测试用例数据
            4. 执行模板渲染
            5. 后处理渲染结果（格式化、导入优化等）
            6. 统计和返回结果

        Example:
            >>> layer = TemplateRenderLayer()
            >>> ctx = create_context()
            >>> ctx.set('test_cases', test_cases_list)
            >>> ctx.set('test_framework', TestFramework.PYTEST)
            >>> result = layer.process(ctx)
            >>> print(f"渲染成功: {result.success_count} 个用例")
        """
        test_cases = self._extract_test_cases(context)
        framework = context.get('test_framework', self.default_framework)
        template_type = context.get('template_type', TemplateType.FUNCTION_TEST)
        language = context.get('language', 'python')
        render_options = context.get('render_options', {})

        result = TemplateRenderResult()
        result.framework_used = framework if isinstance(framework, TestFramework) else TestFramework[framework.upper()]

        template = self._select_template(framework, template_type, language)

        for i, test_case in enumerate(test_cases):
            try:
                rendered = self._render_test_case(
                    test_case, template, framework, render_options, i
                )
                result.rendered_cases.append(rendered)
                result.success_count += 1
                result.total_lines += rendered.line_count
            except Exception as e:
                result.failure_count += 1
                result.metadata[f'error_{i}'] = str(e)

        result.total_cases = len(test_cases)

        result.metadata = {
            'template_type': template_type.value if isinstance(template_type, TemplateType) else template_type,
            'language': language,
            'render_options': render_options,
            'total_imports': sum(len(c.imports) for c in result.rendered_cases)
        }

        context.set('rendered_test_cases', result.rendered_cases)
        context.set('template_render_result', result)

        return result

    def _extract_test_cases(self, context: Any) -> List[Any]:
        """提取测试用例"""
        test_cases = context.get('test_cases', [])

        if not test_cases:
            llm_result = context.get('llm_test_data_result')
            if llm_result and hasattr(llm_result, 'generated_cases'):
                test_cases = llm_result.generated_cases

        return test_cases

    def _select_template(
        self, framework: TestFramework,
        template_type: TemplateType,
        language: str
    ) -> Template:
        """选择合适的模板"""
        framework_key = framework.value if isinstance(framework, TestFramework) else framework

        if framework_key == 'pytest':
            if template_type == TemplateType.FUNCTION_TEST:
                return self.templates.get('pytest_function')
            else:
                return self.templates.get('pytest_class')
        elif framework_key == 'unittest':
            return self.templates.get('unittest')
        elif framework_key in ('junit', 'testng'):
            return self.templates.get('junit')

        return self.templates.get('pytest_function')

    def _render_test_case(
        self, test_case: Any,
        template: Template,
        framework: TestFramework,
        options: Dict[str, Any],
        index: int
    ) -> RenderedTestCase:
        """渲染单个测试用例"""
        if hasattr(test_case, 'to_dict'):
            case_data = test_case.to_dict()
        else:
            case_data = test_case if isinstance(test_case, dict) else {}

        test_name = self._sanitize_test_name(
            case_data.get('name', case_data.get('test_name', f'test_case_{index}'))
        )

        class_name = self._to_class_name(
            case_data.get('function_name', case_data.get('class_name', 'TestClass'))
        )

        render_context = {
            'test_docstring': self._generate_docstring(case_data, options),
            'test_name': test_name,
            'class_name': class_name,
            'scenario': case_data.get('scenario', '测试场景'),
            'imports': self._generate_imports(framework, case_data),
            'fixtures': self._generate_fixtures(framework, case_data),
            'fixture_params': self._generate_fixture_params(case_data),
            'setup_code': self._generate_setup_code(framework, case_data),
            'actual_code': self._generate_actual_code(framework, case_data),
            'assertions': self._generate_assertions(framework, case_data),
            'teardown_code': self._generate_teardown_code(framework, case_data),
            'test_methods': self._generate_test_methods(framework, case_data),
            'fixture_setup': self._generate_fixture_setup(case_data),
            'fixture_teardown': self._generate_fixture_teardown(case_data),
            'package_name': case_data.get('package_name', 'com.test'),
        }

        test_code = template.template_content.format(**render_context)
        test_code = self._format_code(test_code, options)

        line_count = len(test_code.split('\n'))

        return RenderedTestCase(
            test_id=case_data.get('id', case_data.get('case_id', f'case_{index}')),
            test_name=test_name,
            test_code=test_code,
            framework=framework,
            template_type=template.template_type,
            imports=render_context['imports'],
            fixtures=render_context['fixtures'],
            metadata=case_data.get('metadata', {}),
            line_count=line_count
        )

    def _sanitize_test_name(self, name: str) -> str:
        """清理测试名称"""
        name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        name = re.sub(r'_+', '_', name)
        name = name.strip('_')
        if not name.startswith('test'):
            name = f'test_{name}'
        return name.lower()

    def _to_class_name(self, name: str) -> str:
        """转换为类名格式"""
        words = re.findall(r'[A-Z][a-z]*|[a-z]+', name)
        if not words:
            return 'TestClass'
        return ''.join(word.capitalize() for word in words)

    def _generate_docstring(self, case_data: Dict[str, Any], options: Dict[str, Any]) -> str:
        """生成文档字符串"""
        if not options.get('include_docstrings', True):
            return ''

        lines = []
        if case_data.get('description'):
            lines.append(case_data['description'])
        if case_data.get('tags'):
            lines.append(f"Tags: {', '.join(case_data['tags'])}")

        return '\n'.join(lines) if lines else '测试用例文档'

    def _generate_imports(self, framework: TestFramework, case_data: Dict[str, Any]) -> List[str]:
        """生成导入语句"""
        imports = []

        if framework == TestFramework.PYTEST:
            imports.append('import pytest')
        elif framework == TestFramework.UNITTEST:
            imports.append('import unittest')

        return imports

    def _generate_fixtures(self, framework: TestFramework, case_data: Dict[str, Any]) -> str:
        """生成fixtures"""
        if framework not in (TestFramework.PYTEST,):
            return ''

        fixtures = case_data.get('fixtures', [])
        if fixtures:
            return '\n    '.join(fixtures)
        return ''

    def _generate_fixture_params(self, case_data: Dict[str, Any]) -> str:
        """生成fixture参数"""
        fixtures = case_data.get('fixtures', [])
        if fixtures:
            return ', ' + ', '.join(fixtures)
        return ''

    def _generate_setup_code(self, framework: TestFramework, case_data: Dict[str, Any]) -> str:
        """生成setup代码"""
        setup = case_data.get('setup', case_data.get('setup_code', ''))
        return setup if setup else 'pass'

    def _generate_actual_code(self, framework: TestFramework, case_data: Dict[str, Any]) -> str:
        """生成实际执行代码"""
        function_name = case_data.get('function_name', 'function_to_test')
        inputs = case_data.get('inputs', case_data.get('input_data', {}))

        if isinstance(inputs, dict):
            args = ', '.join(f'{k}={repr(v)}' for k, v in inputs.items())
        else:
            args = ', '.join(repr(v) for v in inputs)

        return f'result = {function_name}({args})'

    def _generate_assertions(self, framework: TestFramework, case_data: Dict[str, Any]) -> str:
        """生成断言代码"""
        assertions = []
        expected_output = case_data.get('expected_output', case_data.get('expected', None))

        if expected_output is not None:
            if framework == TestFramework.PYTEST:
                assertions.append(f'assert result == {repr(expected_output)}')
            elif framework == TestFramework.UNITTEST:
                assertions.append(f'self.assertEqual(result, {repr(expected_output)})')

        return '\n        '.join(assertions) if assertions else 'pass'

    def _generate_teardown_code(self, framework: TestFramework, case_data: Dict[str, Any]) -> str:
        """生成teardown代码"""
        teardown = case_data.get('teardown', case_data.get('teardown_code', ''))
        return teardown if teardown else 'pass'

    def _generate_test_methods(self, framework: TestFramework, case_data: Dict[str, Any]) -> str:
        """生成测试方法"""
        return ''

    def _generate_fixture_setup(self, case_data: Dict[str, Any]) -> str:
        """生成fixture setup"""
        return 'pass'

    def _generate_fixture_teardown(self, case_data: Dict[str, Any]) -> str:
        """生成fixture teardown"""
        return 'pass'

    def _format_code(self, code: str, options: Dict[str, Any]) -> str:
        """格式化代码"""
        max_line_length = options.get('max_line_length', 120)

        lines = code.split('\n')
        formatted_lines = []

        for line in lines:
            if len(line) > max_line_length and '    ' in line:
                indent = len(line) - len(line.lstrip())
                words = line.split()
                new_line = words[0]
                current_length = len(new_line)

                for word in words[1:]:
                    if current_length + len(word) + 1 > max_line_length:
                        formatted_lines.append(new_line)
                        new_line = '    ' + word
                        current_length = len(new_line)
                    else:
                        new_line += ' ' + word
                        current_length += len(word) + 1

                formatted_lines.append(new_line)
            else:
                formatted_lines.append(line)

        return '\n'.join(formatted_lines)

    def register_template(self, template: Template) -> None:
        """
        注册自定义模板

        Args:
            template: Template对象
        """
        self.templates[template.template_id] = template

    def get_template(self, template_id: str) -> Optional[Template]:
        """
        获取模板

        Args:
            template_id: 模板ID

        Returns:
            Template对象或None
        """
        return self.templates.get(template_id)
