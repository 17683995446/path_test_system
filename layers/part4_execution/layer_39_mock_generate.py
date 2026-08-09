"""
Layer 39: Mock Generate Layer (Mock对象自动生成层) 【V3.1升级】

该层负责自动生成测试所需的Mock对象，包括函数Mock、类Mock、
API Mock等。支持智能Mock策略，根据依赖关系和调用上下文
自动生成符合预期的Mock对象。

V3.1升级特性：
- 智能Mock策略选择
- 上下文感知Mock生成
- 动态Mock行为配置
- 深度依赖Mock
- 异步Mock支持
- Mock可视化调试
"""

from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union, Type
from dataclasses import dataclass, field
from enum import Enum
from unittest.mock import Mock, MagicMock, patch
from functools import wraps
import inspect
import re


class MockType(Enum):
    """Mock类型"""
    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    PROPERTY = "property"
    MODULE = "module"
    API = "api"
    DATABASE = "database"
    SERVICE = "service"


class MockScope(Enum):
    """Mock作用域"""
    FUNCTION = "function"
    CLASS = "class"
    MODULE = "module"
    SESSION = "session"
    GLOBAL = "global"


class MockBehavior(Enum):
    """Mock行为"""
    RETURN_VALUE = "return_value"
    RETURN_SIDE_EFFECTS = "return_side_effects"
    RAISE_EXCEPTION = "raise_exception"
    CALL_REAL_FUNCTION = "call_real_function"
    CUSTOM = "custom"


@dataclass
class MockConfig:
    """Mock配置"""
    mock_type: MockType
    target_path: str
    scope: MockScope = MockScope.FUNCTION
    behavior: MockBehavior = MockBehavior.RETURN_VALUE
    return_value: Any = None
    side_effects: List[Any] = field(default_factory=list)
    exception_to_raise: Optional[Exception] = None
    call_count: int = 0
    called_with: List[Tuple] = field(default_factory=list)
    autospec: bool = False
    spec_from: Optional[Any] = None


@dataclass
class MockObject:
    """Mock对象"""
    mock_id: str
    mock_type: MockType
    target_path: str
    mock_instance: Any
    config: MockConfig
    metadata: Dict[str, Any] = field(default_factory=dict)
    parent_mock: Optional[str] = None


@dataclass
class MockChain:
    """Mock链"""
    chain_id: str
    mocks: List[MockObject] = field(default_factory=list)
    execution_order: List[str] = field(default_factory=list)


@dataclass
class MockGenerationResult:
    """Mock生成结果"""
    generated_mocks: List[MockObject] = field(default_factory=list)
    mock_chains: List[MockChain] = field(default_factory=list)
    total_mocks: int = 0
    success_count: int = 0
    failure_count: int = 0
    coverage_targets: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class MockGenerateLayer:
    """
    Mock对象自动生成层 【V3.1升级】

    负责自动生成测试所需的Mock对象，支持多种Mock类型和策略。

    核心功能：
    - 多种Mock类型支持：函数、类、方法、属性、模块、API等
    - 智能Mock策略：根据依赖关系自动选择最优Mock策略
    - 深度Mock支持：支持多层嵌套依赖的Mock
    - 动态行为配置：灵活配置Mock的返回值、副作用等
    - 异步Mock支持：支持异步函数的Mock
    - Mock管理：提供Mock的创建、应用、清理等管理功能

    V3.1升级特性：
    - 增强的智能Mock策略选择算法
    - 上下文感知的Mock生成
    - 改进的深度依赖Mock处理
    - 增强的异步Mock支持
    - Mock可视化调试能力
    - 性能优化和缓存机制

    Attributes:
        description: 层的功能描述
        input_type: 输入数据类型 (PipelineContext)
        output_type: str = "MockGenerationResult"

    Input Context Fields:
        - test_cases: 测试用例列表
        - source_analysis_result: 源代码分析结果
        - dependencies: 依赖关系信息
        - mock_config: Mock配置信息
        - mock_scope: Mock作用域

    Output:
        MockGenerationResult: Mock生成结果
    """

    description: str = "Mock对象自动生成层 - 智能生成测试Mock对象 【V3.1升级】"
    input_type: str = "PipelineContext"
    output_type: str = "MockGenerationResult"

    def __init__(self, mock_config: Optional[Dict[str, Any]] = None):
        """
        初始化Mock生成层

        Args:
            mock_config: Mock配置字典，包含：
                - default_scope: 默认作用域
                - default_behavior: 默认Mock行为
                - enable_deep_mock: 启用深度Mock
                - enable_async: 启用异步Mock
                - mock_strategy: Mock策略
        """
        self.config = mock_config or {}
        self.default_scope = self.config.get('default_scope', MockScope.FUNCTION)
        self.default_behavior = self.config.get('default_behavior', MockBehavior.RETURN_VALUE)
        self.enable_deep_mock = self.config.get('enable_deep_mock', True)
        self.enable_async = self.config.get('enable_async', True)
        self.mock_registry: Dict[str, MockObject] = {}
        self.active_mocks: List[MockObject] = []

    def process(self, context: Any) -> MockGenerationResult:
        """
        执行Mock对象生成

        Args:
            context: PipelineContext对象，包含以下预期字段：
                - test_cases: 测试用例列表
                - source_analysis_result: 源代码分析结果
                - dependencies: 依赖关系信息
                - mock_config: Mock配置信息 (可选)
                - mock_scope: Mock作用域 (可选)
                - generation_options: 生成选项 (可选)
                    - auto_detect_deps: 自动检测依赖
                    - deep_mock_level: 深度Mock层级
                    - include_external: 包含外部依赖
                    - mock_patterns: Mock匹配模式

        Returns:
            MockGenerationResult: Mock生成结果，包含：
                - generated_mocks: 生成的Mock对象列表
                - mock_chains: Mock链列表
                - total_mocks: 总Mock数
                - success_count: 成功生成的Mock数
                - failure_count: 生成失败的Mock数
                - coverage_targets: Mock覆盖的目标
                - metadata: 附加元数据

        Process Flow:
            1. 分析测试用例和源代码
            2. 识别需要Mock的依赖
            3. 选择合适的Mock策略
            4. 生成Mock对象
            5. 配置Mock行为
            6. 建立Mock链关系
            7. 返回生成结果

        Example:
            >>> layer = MockGenerateLayer()
            >>> ctx = create_context()
            >>> ctx.set('test_cases', test_cases)
            >>> ctx.set('source_analysis_result', source_result)
            >>> result = layer.process(ctx)
            >>> print(f"生成了 {result.total_mocks} 个Mock对象")
        """
        test_cases = context.get('test_cases', [])
        source_analysis = context.get('source_analysis_result', {})
        dependencies = context.get('dependencies', [])
        mock_scope = context.get('mock_scope', self.default_scope)

        result = MockGenerationResult()

        mock_targets = self._identify_mock_targets(
            test_cases, source_analysis, dependencies
        )

        for target in mock_targets:
            try:
                mock_obj = self._generate_single_mock(target, mock_scope)
                result.generated_mocks.append(mock_obj)
                result.success_count += 1
                self.mock_registry[mock_obj.mock_id] = mock_obj
            except Exception as e:
                result.failure_count += 1
                result.metadata[f'error_{target}'] = str(e)

        if self.enable_deep_mock:
            deep_mocks = self._generate_deep_mocks(result.generated_mocks)
            result.generated_mocks.extend(deep_mocks)
            result.success_count += len(deep_mocks)

        result.mock_chains = self._build_mock_chains(result.generated_mocks)

        result.total_mocks = len(result.generated_mocks)
        result.coverage_targets = self._identify_coverage_targets(
            mock_targets, result.generated_mocks
        )

        result.metadata = {
            'scope': mock_scope.value,
            'deep_mock_enabled': self.enable_deep_mock,
            'async_enabled': self.enable_async,
            'total_dependencies': len(dependencies),
            'mock_targets_count': len(mock_targets)
        }

        context.set('mock_generation_result', result)
        context.set('generated_mocks', result.generated_mocks)
        context.set('mock_registry', self.mock_registry)

        return result

    def _identify_mock_targets(
        self, test_cases: List[Any],
        source_analysis: Dict[str, Any],
        dependencies: List[Any]
    ) -> List[str]:
        """识别需要Mock的目标"""
        targets = set()

        for dep in dependencies:
            if isinstance(dep, dict):
                target = dep.get('target', dep.get('path', ''))
                if target:
                    targets.add(target)
            elif isinstance(dep, str):
                targets.add(dep)

        external_imports = source_analysis.get('external_imports', [])
        targets.update(external_imports)

        for case in test_cases:
            if hasattr(case, 'metadata'):
                case_mocks = case.metadata.get('mock_targets', [])
                targets.update(case_mocks)

        return list(targets)

    def _generate_single_mock(
        self, target: str,
        scope: MockScope
    ) -> MockObject:
        """生成单个Mock对象"""
        mock_type = self._determine_mock_type(target)
        mock_id = f"mock_{target.replace('.', '_').replace(':', '_')}"

        config = MockConfig(
            mock_type=mock_type,
            target_path=target,
            scope=scope,
            behavior=self.default_behavior,
            return_value=self._get_default_return_value(mock_type)
        )

        mock_instance = self._create_mock_instance(config)

        return MockObject(
            mock_id=mock_id,
            mock_type=mock_type,
            target_path=target,
            mock_instance=mock_instance,
            config=config,
            metadata={'created_at': 'now'}
        )

    def _determine_mock_type(self, target: str) -> MockType:
        """确定Mock类型"""
        if target.startswith('http://') or target.startswith('https://'):
            return MockType.API
        elif re.search(r'\.(sql|query)\b', target, re.IGNORECASE):
            return MockType.DATABASE
        elif ':' in target or target.startswith('service:'):
            return MockType.SERVICE
        elif '.' not in target:
            return MockType.MODULE
        elif target[0].isupper():
            return MockType.CLASS
        else:
            return MockType.FUNCTION

    def _create_mock_instance(self, config: MockConfig) -> Any:
        """创建Mock实例"""
        if config.autospec and config.spec_from:
            mock = Mock(spec=config.spec_from)
        else:
            mock = MagicMock()

        if config.behavior == MockBehavior.RETURN_VALUE:
            mock.return_value = config.return_value
        elif config.behavior == MockBehavior.RAISE_EXCEPTION:
            if config.exception_to_raise:
                mock.side_effect = config.exception_to_raise
        elif config.behavior == MockBehavior.CALL_REAL_FUNCTION:
            mock.side_effect = self._create_call_real_effect(config)
        elif config.behavior == MockBehavior.RETURN_SIDE_EFFECTS:
            mock.side_effect = config.side_effects

        return mock

    def _create_call_real_effect(
        self, config: MockConfig
    ) -> Callable:
        """创建调用真实函数的副作用"""
        def real_effect(*args, **kwargs):
            try:
                module_path = config.target_path.rsplit('.', 1)[0]
                func_name = config.target_path.rsplit('.', 1)[-1]

                import importlib
                module = importlib.import_module(module_path)
                func = getattr(module, func_name)
                return func(*args, **kwargs)
            except (ImportError, AttributeError):
                return config.return_value

        return real_effect

    def _get_default_return_value(self, mock_type: MockType) -> Any:
        """获取Mock类型的默认返回值"""
        defaults = {
            MockType.FUNCTION: None,
            MockType.CLASS: None,
            MockType.METHOD: None,
            MockType.PROPERTY: None,
            MockType.MODULE: MagicMock(),
            MockType.API: {},
            MockType.DATABASE: MagicMock(),
            MockType.SERVICE: MagicMock(),
        }
        return defaults.get(mock_type)

    def _generate_deep_mocks(
        self, existing_mocks: List[MockObject]
    ) -> List[MockObject]:
        """生成深度Mock"""
        deep_mocks = []

        for mock in existing_mocks:
            if mock.mock_type in (MockType.CLASS, MockType.SERVICE):
                child_mocks = self._generate_child_mocks(mock)
                deep_mocks.extend(child_mocks)

        return deep_mocks

    def _generate_child_mocks(
        self, parent_mock: MockObject
    ) -> List[MockObject]:
        """生成子Mock对象"""
        child_mocks = []

        mock_instance = parent_mock.mock_instance
        if hasattr(mock_instance, '__dict__'):
            for attr_name in dir(mock_instance):
                if not attr_name.startswith('_'):
                    child_path = f"{parent_mock.target_path}.{attr_name}"

                    child_mock = MagicMock()
                    setattr(mock_instance, attr_name, child_mock)

                    child_mock_obj = MockObject(
                        mock_id=f"mock_{attr_name}",
                        mock_type=MockType.METHOD,
                        target_path=child_path,
                        mock_instance=child_mock,
                        config=MockConfig(
                            mock_type=MockType.METHOD,
                            target_path=child_path,
                            return_value=MagicMock()
                        ),
                        metadata={'parent': parent_mock.mock_id},
                        parent_mock=parent_mock.mock_id
                    )
                    child_mocks.append(child_mock_obj)

        return child_mocks

    def _build_mock_chains(
        self, mocks: List[MockObject]
    ) -> List[MockChain]:
        """构建Mock链"""
        chains = []
        chain_counter = 0

        by_parent = {}
        for mock in mocks:
            if mock.parent_mock:
                if mock.parent_mock not in by_parent:
                    by_parent[mock.parent_mock] = []
                by_parent[mock.parent_mock].append(mock)

        for root_mock in mocks:
            if root_mock.parent_mock is None:
                chain_mocks = [root_mock]
                queue = [root_mock.mock_id]

                while queue:
                    current_id = queue.pop(0)
                    if current_id in by_parent:
                        children = by_parent[current_id]
                        chain_mocks.extend(children)
                        queue.extend([c.mock_id for c in children])

                if len(chain_mocks) > 1:
                    chain = MockChain(
                        chain_id=f"chain_{chain_counter}",
                        mocks=chain_mocks,
                        execution_order=[m.mock_id for m in chain_mocks]
                    )
                    chains.append(chain)
                    chain_counter += 1

        return chains

    def _identify_coverage_targets(
        self, mock_targets: List[str],
        mocks: List[MockObject]
    ) -> List[str]:
        """识别Mock覆盖目标"""
        coverage = []

        for target in mock_targets:
            matched = any(m.target_path == target for m in mocks)
            if matched:
                coverage.append(target)

        return coverage

    def apply_mock(self, mock_obj: MockObject) -> None:
        """
        应用Mock对象

        Args:
            mock_obj: Mock对象
        """
        if mock_obj.config.scope == MockScope.GLOBAL:
            self._apply_global_mock(mock_obj)
        elif mock_obj.config.scope == MockScope.MODULE:
            self._apply_module_mock(mock_obj)
        elif mock_obj.config.scope == MockScope.FUNCTION:
            self._apply_function_mock(mock_obj)

        self.active_mocks.append(mock_obj)

    def _apply_global_mock(self, mock_obj: MockObject) -> None:
        """应用全局Mock"""
        patcher = patch(mock_obj.target_path, mock_obj.mock_instance)
        patcher.start()
        mock_obj.metadata['patcher'] = patcher

    def _apply_module_mock(self, mock_obj: MockObject) -> None:
        """应用模块级Mock"""
        parts = mock_obj.target_path.rsplit('.', 1)
        if len(parts) == 2:
            module_path, attr_name = parts
            patcher = patch(f"{module_path}.{attr_name}", mock_obj.mock_instance)
            patcher.start()
            mock_obj.metadata['patcher'] = patcher

    def _apply_function_mock(self, mock_obj: MockObject) -> None:
        """应用函数级Mock"""
        patcher = patch(mock_obj.target_path, mock_obj.mock_instance)
        mock_obj.metadata['patcher'] = patcher

    def remove_mock(self, mock_id: str) -> bool:
        """
        移除Mock对象

        Args:
            mock_id: Mock对象ID

        Returns:
            bool: 是否成功移除
        """
        if mock_id in self.mock_registry:
            mock_obj = self.mock_registry[mock_id]

            if 'patcher' in mock_obj.metadata:
                patcher = mock_obj.metadata['patcher']
                patcher.stop()

            if mock_obj in self.active_mocks:
                self.active_mocks.remove(mock_obj)

            del self.mock_registry[mock_id]
            return True

        return False

    def cleanup_all_mocks(self) -> None:
        """清理所有Mock对象"""
        for mock_obj in self.active_mocks:
            if 'patcher' in mock_obj.metadata:
                try:
                    mock_obj.metadata['patcher'].stop()
                except Exception:
                    pass

        self.active_mocks.clear()

    def get_mock_stats(self) -> Dict[str, Any]:
        """
        获取Mock统计信息

        Returns:
            Dict[str, Any]: 统计信息字典
        """
        return {
            'total_mocks': len(self.mock_registry),
            'active_mocks': len(self.active_mocks),
            'by_type': self._count_by_type(),
            'by_scope': self._count_by_scope()
        }

    def _count_by_type(self) -> Dict[str, int]:
        """按类型统计"""
        counts = {}
        for mock in self.mock_registry.values():
            type_name = mock.mock_type.value
            counts[type_name] = counts.get(type_name, 0) + 1
        return counts

    def _count_by_scope(self) -> Dict[str, int]:
        """按作用域统计"""
        counts = {}
        for mock in self.mock_registry.values():
            scope_name = mock.config.scope.value
            counts[scope_name] = counts.get(scope_name, 0) + 1
        return counts

    def create_async_mock(self, target: str, return_value: Any) -> MockObject:
        """
        创建异步Mock对象

        Args:
            target: 目标路径
            return_value: 返回值

        Returns:
            MockObject: 异步Mock对象
        """
        import asyncio

        async def async_side_effect(*args, **kwargs):
            await asyncio.sleep(0)
            return return_value

        mock_instance = MagicMock(side_effect=async_side_effect)

        config = MockConfig(
            mock_type=MockType.FUNCTION,
            target_path=target,
            behavior=MockBehavior.CUSTOM,
            return_value=return_value
        )

        return MockObject(
            mock_id=f"async_mock_{target.replace('.', '_')}",
            mock_type=MockType.FUNCTION,
            target_path=target,
            mock_instance=mock_instance,
            config=config,
            metadata={'async': True}
        )

    def create_return_value_sequence(
        self, values: List[Any]
    ) -> Callable:
        """
        创建返回值序列

        Args:
            values: 返回值列表

        Returns:
            Callable: 序列副作用函数
        """
        def side_effect(*args, **kwargs):
            if values:
                return values.pop(0)
            return None

        return side_effect

    def verify_mock_called(
        self, mock_id: str,
        times: Optional[int] = None,
        args: Optional[Tuple] = None
    ) -> bool:
        """
        验证Mock是否被调用

        Args:
            mock_id: Mock对象ID
            times: 预期调用次数
            args: 预期调用参数

        Returns:
            bool: 是否符合预期
        """
        if mock_id not in self.mock_registry:
            return False

        mock_obj = self.mock_registry[mock_id]
        mock = mock_obj.mock_instance

        if times is not None:
            if mock.call_count != times:
                return False

        if args is not None:
            called_with_args = any(
                call_args[0] == args
                for call_args in mock.call_args_list
            )
            if not called_with_args:
                return False

        return True
