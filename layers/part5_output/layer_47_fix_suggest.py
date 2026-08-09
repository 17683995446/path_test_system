"""
Layer 47: FixSuggestionLayer - 代码修复建议生成层

本层负责根据缺陷分析结果和代码上下文，智能生成代码修复建议。
分析缺陷模式、代码结构、测试用例，提供具体的修复方案和最佳实践。
"""

from typing import Any, Optional, List, Dict, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto


class FixCategory(Enum):
    """修复类别枚举"""
    SYNTAX_FIX = auto()
    LOGIC_FIX = auto()
    ERROR_HANDLING_FIX = auto()
    BOUNDARY_FIX = auto()
    NULL_SAFETY_FIX = auto()
    CONCURRENCY_FIX = auto()
    PERFORMANCE_FIX = auto()
    SECURITY_FIX = auto()
    TEST_ADDITION = auto()
    CONFIGURATION_FIX = auto()
    REFACTORING = auto()
    DOCUMENTATION_FIX = auto()


class FixComplexity(Enum):
    """修复复杂度枚举"""
    TRIVIAL = auto()
    SIMPLE = auto()
    MODERATE = auto()
    COMPLEX = auto()


class FixConfidence(Enum):
    """修复置信度枚举"""
    HIGH = auto()
    MEDIUM = auto()
    LOW = auto()


@dataclass
class FixSuggestion:
    """修复建议数据模型

    Attributes:
        suggestion_id: 建议唯一标识符
        defect_id: 关联的缺陷ID
        title: 修复建议标题
        description: 详细描述
        category: 修复类别
        complexity: 复杂度
        confidence: 置信度
        original_code: 原代码片段
        suggested_code: 建议的修复代码
        file_path: 文件路径
        line_number: 行号
        function_name: 函数名称
        class_name: 类名
        rationale: 修复理由
        impact: 影响分析
        risks: 潜在风险
        test_cases_to_add: 需要添加的测试用例
        related_fixes: 相关修复建议
        references: 参考资料链接
        estimated_effort: 预估工作量（小时）
        priority: 优先级
        best_practices: 最佳实践建议
        before_after: 修复前后的对比
    """
    suggestion_id: str
    defect_id: str
    title: str
    description: str = ""
    category: FixCategory = FixCategory.LOGIC_FIX
    complexity: FixComplexity = FixComplexity.MODERATE
    confidence: FixConfidence = FixConfidence.MEDIUM
    original_code: str = ""
    suggested_code: str = ""
    file_path: str = ""
    line_number: int = 0
    function_name: str = ""
    class_name: str = ""
    rationale: str = ""
    impact: Dict[str, Any] = field(default_factory=dict)
    risks: List[str] = field(default_factory=list)
    test_cases_to_add: List[Dict[str, str]] = field(default_factory=list)
    related_fixes: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    estimated_effort: float = 0.0
    priority: int = 1
    best_practices: List[str] = field(default_factory=list)
    before_after: Dict[str, str] = field(default_factory=dict)

    def calculate_priority(self) -> int:
        """计算优先级分数

        Returns:
            int: 优先级分数（越高越紧急）
        """
        category_priority = {
            FixCategory.SECURITY_FIX: 100,
            FixCategory.CRITICAL_BUG: 90,
            FixCategory.NULL_SAFETY_FIX: 80,
            FixCategory.ERROR_HANDLING_FIX: 70,
            FixCategory.LOGIC_FIX: 60,
            FixCategory.BOUNDARY_FIX: 50,
            FixCategory.CONCURRENCY_FIX: 45,
            FixCategory.PERFORMANCE_FIX: 40,
            FixCategory.SYNTAX_FIX: 30,
            FixCategory.REFACTORING: 20,
            FixCategory.CONFIGURATION_FIX: 15,
            FixCategory.DOCUMENTATION_FIX: 10,
            FixCategory.TEST_ADDITION: 5
        }

        complexity_factor = {
            FixComplexity.TRIVIAL: 10,
            FixComplexity.SIMPLE: 8,
            FixComplexity.MODERATE: 5,
            FixComplexity.COMPLEX: 2
        }

        confidence_factor = {
            FixConfidence.HIGH: 10,
            FixConfidence.MEDIUM: 5,
            FixConfidence.LOW: 0
        }

        base_priority = category_priority.get(self.category, 50)
        base_priority += complexity_factor.get(self.complexity, 5)
        base_priority += confidence_factor.get(self.confidence, 5)

        return base_priority

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "suggestion_id": self.suggestion_id,
            "defect_id": self.defect_id,
            "title": self.title,
            "description": self.description,
            "category": self.category.name,
            "complexity": self.complexity.name,
            "confidence": self.confidence.name,
            "priority_score": self.calculate_priority(),
            "original_code": self.original_code,
            "suggested_code": self.suggested_code,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "function_name": self.function_name,
            "class_name": self.class_name,
            "rationale": self.rationale,
            "impact": self.impact,
            "risks": self.risks,
            "test_cases_to_add": self.test_cases_to_add,
            "related_fixes": self.related_fixes,
            "references": self.references,
            "estimated_effort": self.estimated_effort,
            "best_practices": self.best_practices,
            "before_after": self.before_after
        }


@dataclass
class FixGroup:
    """修复建议分组

    Attributes:
        group_id: 分组ID
        group_type: 分组类型
        title: 分组标题
        suggestions: 分组内的修复建议
        summary: 分组摘要
        sequential_order: 是否需要按顺序执行
    """
    group_id: str
    group_type: str
    title: str
    suggestions: List[FixSuggestion] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    sequential_order: bool = False

    def add_suggestion(self, suggestion: FixSuggestion) -> None:
        """添加修复建议"""
        self.suggestions.append(suggestion)

    def get_total_effort(self) -> float:
        """获取总工作量"""
        return sum(s.estimated_effort for s in self.suggestions)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "group_id": self.group_id,
            "group_type": self.group_type,
            "title": self.title,
            "suggestion_count": len(self.suggestions),
            "total_effort": self.get_total_effort(),
            "sequential_order": self.sequential_order,
            "summary": self.summary,
            "suggestions": [s.to_dict() for s in self.suggestions]
        }


@dataclass
class FixSuggestionResult:
    """修复建议结果

    Attributes:
        session_id: 会话标识符
        suggestions: 修复建议列表
        groups: 分组列表
        by_category: 按类别分类的建议
        by_file: 按文件分类的建议
        by_function: 按函数分类的建议
        total_effort: 总预估工作量
        high_priority_count: 高优先级建议数量
        security_fixes: 安全修复建议
        statistics: 统计信息
        recommendations: 总体建议
        metadata: 其他元信息
    """
    session_id: str
    suggestions: List[FixSuggestion] = field(default_factory=list)
    groups: List[FixGroup] = field(default_factory=list)
    by_category: Dict[FixCategory, List[FixSuggestion]] = field(default_factory=dict)
    by_file: Dict[str, List[FixSuggestion]] = field(default_factory=dict)
    by_function: Dict[str, List[FixSuggestion]] = field(default_factory=dict)
    total_effort: float = 0.0
    high_priority_count: int = 0
    security_fixes: List[FixSuggestion] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_suggestion(self, suggestion: FixSuggestion) -> None:
        """添加修复建议"""
        self.suggestions.append(suggestion)
        self.total_effort += suggestion.estimated_effort

        if suggestion.category == FixCategory.SECURITY_FIX:
            self.security_fixes.append(suggestion)

        if suggestion.calculate_priority() >= 70:
            self.high_priority_count += 1

        if suggestion.category not in self.by_category:
            self.by_category[suggestion.category] = []
        self.by_category[suggestion.category].append(suggestion)

        if suggestion.file_path:
            if suggestion.file_path not in self.by_file:
                self.by_file[suggestion.file_path] = []
            self.by_file[suggestion.file_path].append(suggestion)

        if suggestion.function_name:
            if suggestion.function_name not in self.by_function:
                self.by_function[suggestion.function_name] = []
            self.by_function[suggestion.function_name].append(suggestion)

    def get_high_priority_suggestions(self) -> List[FixSuggestion]:
        """获取高优先级建议"""
        return [s for s in self.suggestions if s.calculate_priority() >= 70]

    def get_sorted_by_priority(self) -> List[FixSuggestion]:
        """按优先级排序"""
        return sorted(self.suggestions, key=lambda s: s.calculate_priority(), reverse=True)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "session_id": self.session_id,
            "total_suggestions": len(self.suggestions),
            "total_effort": self.total_effort,
            "high_priority_count": self.high_priority_count,
            "security_fixes_count": len(self.security_fixes),
            "by_category": {
                cat.name: len(sugs) for cat, sugs in self.by_category.items()
            },
            "suggestions": [s.to_dict() for s in self.suggestions],
            "groups": [g.to_dict() for g in self.groups],
            "statistics": self.statistics,
            "recommendations": self.recommendations,
            "metadata": self.metadata
        }


class FixSuggestionGenerator:
    """修复建议生成器

    功能描述：
        - 分析缺陷代码上下文
        - 生成具体修复方案
        - 评估修复复杂度和风险
        - 提供测试用例建议
    """

    def __init__(self):
        """初始化修复建议生成器"""
        self.pattern_templates = self._init_pattern_templates()
        self.best_practices = self._init_best_practices()

    def _init_pattern_templates(self) -> Dict[str, Any]:
        """初始化模式模板"""
        return {
            "null_check": {
                "pattern": r"(?P<before>(\w+)\.(\w+))",
                "fix": "添加空值检查: if {var} is not None: {original}",
                "confidence": FixConfidence.HIGH
            },
            "exception_handling": {
                "pattern": r"(?P<code>.*(?:try|except).*)",
                "fix": "增强异常处理: 添加具体的异常类型和日志记录",
                "confidence": FixConfidence.MEDIUM
            },
            "boundary_check": {
                "pattern": r"(?P<comparison>(\w+)\s*([<>]=?)\s*(\d+))",
                "fix": "确保边界条件正确处理",
                "confidence": FixConfidence.HIGH
            },
            "resource_cleanup": {
                "pattern": r"(?P<resource>(?:file|connection|cursor|handle))",
                "fix": "使用try-finally或with语句确保资源释放",
                "confidence": FixConfidence.HIGH
            },
            "concurrency": {
                "pattern": r"(?P<shared>(?:shared|global|static).*)",
                "fix": "添加适当的同步机制或使用线程安全的数据结构",
                "confidence": FixConfidence.MEDIUM
            }
        }

    def _init_best_practices(self) -> Dict[FixCategory, List[str]]:
        """初始化最佳实践"""
        return {
            FixCategory.NULL_SAFETY_FIX: [
                "使用可选链操作符(?.)避免空指针异常",
                "在访问对象属性前进行空值检查",
                "考虑使用None合并运算符??提供默认值",
                "在函数参数中使用类型注解和默认值"
            ],
            FixCategory.ERROR_HANDLING_FIX: [
                "捕获具体异常类型而非通用Exception",
                "在异常处理中记录足够的上下文信息",
                "不要在异常处理中吞掉错误",
                "考虑使用自定义异常类"
            ],
            FixCategory.BOUNDARY_FIX: [
                "测试边界值: 最小值、最大值、临界值",
                "处理整数溢出和浮点数精度问题",
                "验证输入数据的有效范围",
                "考虑使用卫语句提前检查边界条件"
            ],
            FixCategory.SECURITY_FIX: [
                "对所有输入进行验证和清理",
                "使用参数化查询防止SQL注入",
                "对敏感数据进行加密存储和传输",
                "实现适当的访问控制"
            ],
            FixCategory.CONCURRENCY_FIX: [
                "使用线程安全的数据结构",
                "正确使用锁和同步原语",
                "避免死锁: 总是以相同顺序获取锁",
                "考虑使用异步编程模型"
            ]
        }

    def generate_fix_for_defect(self, defect: Any, context: Any) -> FixSuggestion:
        """为缺陷生成修复建议

        Args:
            defect: 缺陷对象
            context: 上下文信息

        Returns:
            FixSuggestion: 修复建议
        """
        defect_id = getattr(defect, 'defect_id', 'unknown')
        title = f"修复: {getattr(defect, 'title', '代码缺陷')}"
        description = getattr(defect, 'description', '')

        location = getattr(defect, 'location', None)
        file_path = getattr(location, 'file_path', '') if location else ''
        line_number = getattr(location, 'line_number', 0) if location else 0
        function_name = getattr(location, 'function_name', '') if location else ''

        defect_type = getattr(defect, 'defect_type', 'UNKNOWN')
        category = self._map_defect_type_to_category(defect_type)

        original_code = self._get_original_code(file_path, line_number, context)
        suggested_code = self._generate_code_fix(category, original_code, defect)

        complexity = self._assess_complexity(category, original_code)
        confidence = self._assess_confidence(category, original_code)
        rationale = self._generate_rationale(category, original_code)
        best_practices = self.best_practices.get(category, [])

        suggestion = FixSuggestion(
            suggestion_id=f"fix_{defect_id}",
            defect_id=defect_id,
            title=title,
            description=description,
            category=category,
            complexity=complexity,
            confidence=confidence,
            original_code=original_code,
            suggested_code=suggested_code,
            file_path=file_path,
            line_number=line_number,
            function_name=function_name,
            rationale=rationale,
            best_practices=best_practices
        )

        suggestion.estimated_effort = self._estimate_effort(suggestion)
        suggestion.test_cases_to_add = self._suggest_test_cases(category, suggestion)
        suggestion.before_after = {
            "before": original_code,
            "after": suggested_code
        }

        return suggestion

    def generate_fix_for_uncovered(self, uncovered_item: Any, context: Any) -> FixSuggestion:
        """为未覆盖代码生成修复建议

        Args:
            uncovered_item: 未覆盖项
            context: 上下文信息

        Returns:
            FixSuggestion: 修复建议
        """
        item_id = getattr(uncovered_item, 'item_id', 'uncovered')
        item_type = getattr(uncovered_item, 'item_type', 'line')
        reason = getattr(uncovered_item, 'reason', 'UNKNOWN')

        file_path = getattr(uncovered_item, 'file_path', '')
        line_number = getattr(uncovered_item, 'line_number', 0)
        function_name = getattr(uncovered_item, 'function_name', '')

        title = f"增加测试覆盖: {file_path}:{line_number}"

        category = self._map_reason_to_category(reason)
        original_code = self._get_original_code(file_path, line_number, context)
        suggested_code = self._generate_coverage_fix(category, original_code)

        suggestion = FixSuggestion(
            suggestion_id=f"coverage_{item_id}",
            defect_id="",
            title=title,
            description=f"需要增加测试用例覆盖此代码路径",
            category=FixCategory.TEST_ADDITION,
            complexity=FixComplexity.SIMPLE,
            confidence=FixConfidence.HIGH,
            original_code=original_code,
            suggested_code=suggested_code,
            file_path=file_path,
            line_number=line_number,
            function_name=function_name,
            rationale="增加测试覆盖率，减少代码风险"
        )

        suggestion.estimated_effort = 0.5
        suggestion.test_cases_to_add = self._suggest_test_cases(category, suggestion)

        return suggestion

    def _map_defect_type_to_category(self, defect_type: str) -> FixCategory:
        """映射缺陷类型到修复类别"""
        mapping = {
            "NULL_POINTER": FixCategory.NULL_SAFETY_FIX,
            "BOUNDARY_ERROR": FixCategory.BOUNDARY_FIX,
            "LOGIC_ERROR": FixCategory.LOGIC_FIX,
            "RACE_CONDITION": FixCategory.CONCURRENCY_FIX,
            "SECURITY_VULNERABILITY": FixCategory.SECURITY_FIX,
            "PERFORMANCE_ISSUE": FixCategory.PERFORMANCE_FIX,
            "FUNCTIONAL": FixCategory.LOGIC_FIX
        }
        return mapping.get(defect_type, FixCategory.LOGIC_FIX)

    def _map_reason_to_category(self, reason: str) -> FixCategory:
        """映射未覆盖原因到修复类别"""
        mapping = {
            "EXCEPTION_PATH_NOT_TESTED": FixCategory.ERROR_HANDLING_FIX,
            "BOUNDARY_CONDITION_NOT_COVERED": FixCategory.BOUNDARY_FIX,
            "ERROR_HANDLING_NOT_TESTED": FixCategory.ERROR_HANDLING_FIX,
            "NORMAL_PATH_NOT_EXECUTED": FixCategory.TEST_ADDITION
        }
        return mapping.get(reason, FixCategory.TEST_ADDITION)

    def _get_original_code(self, file_path: str, line_number: int,
                          context: Any) -> str:
        """获取原始代码"""
        if context and context.has('source_code_cache'):
            cache = context.get('source_code_cache')
            if file_path in cache:
                lines = cache[file_path]
                if 0 <= line_number - 1 < len(lines):
                    return lines[line_number - 1]
        return f"[Code at {file_path}:{line_number}]"

    def _generate_code_fix(self, category: FixCategory, original_code: str,
                          defect: Any) -> str:
        """生成代码修复"""
        if category == FixCategory.NULL_SAFETY_FIX:
            return self._generate_null_check_fix(original_code)
        elif category == FixCategory.ERROR_HANDLING_FIX:
            return self._generate_error_handling_fix(original_code)
        elif category == FixCategory.BOUNDARY_FIX:
            return self._generate_boundary_fix(original_code)
        elif category == FixCategory.SECURITY_FIX:
            return self._generate_security_fix(original_code)
        else:
            return f"# 建议修复:\n{original_code}"

    def _generate_null_check_fix(self, original_code: str) -> str:
        """生成空值检查修复"""
        return f"""if variable is not None:
    {original_code}
else:
    # 处理空值情况
    pass"""

    def _generate_error_handling_fix(self, original_code: str) -> str:
        """生成错误处理修复"""
        return f"""try:
    {original_code}
except SpecificException as e:
    logger.error(f"Error occurred: {{e}}")
    # 处理特定异常
    raise
except Exception as e:
    logger.exception("Unexpected error")
    # 处理其他异常
    raise"""

    def _generate_boundary_fix(self, original_code: str) -> str:
        """生成边界检查修复"""
        return f"""# 添加边界检查
if not (min_value <= input_value <= max_value):
    raise ValueError("Input value out of bounds")
{original_code}"""

    def _generate_security_fix(self, original_code: str) -> str:
        """生成安全修复"""
        return f"""# 输入验证
sanitized_input = validate_and_sanitize(user_input)
# 使用参数化查询
# 使用安全的数据处理方式
{sanitized_input if 'sanitized' in original_code.lower() else original_code}"""

    def _generate_coverage_fix(self, category: FixCategory, original_code: str) -> str:
        """生成覆盖率修复"""
        test_template = """def test_{function_name}_{scenario}():
    # 测试场景描述
    {test_code}
    assert expected_result == actual_result"""

        return test_template.format(
            function_name="function",
            scenario="scenario",
            test_code="# 实现测试逻辑"
        )

    def _assess_complexity(self, category: FixCategory, code: str) -> FixComplexity:
        """评估修复复杂度"""
        if category in [FixCategory.SECURITY_FIX, FixCategory.CONCURRENCY_FIX]:
            return FixComplexity.COMPLEX
        elif category in [FixCategory.ERROR_HANDLING_FIX, FixCategory.BOUNDARY_FIX]:
            return FixComplexity.MODERATE
        else:
            return FixComplexity.SIMPLE

    def _assess_confidence(self, category: FixCategory, code: str) -> FixConfidence:
        """评估修复置信度"""
        if category in [FixCategory.NULL_SAFETY_FIX, FixCategory.BOUNDARY_FIX]:
            return FixConfidence.HIGH
        elif category in [FixCategory.ERROR_HANDLING_FIX, FixCategory.LOGIC_FIX]:
            return FixConfidence.MEDIUM
        else:
            return FixConfidence.LOW

    def _generate_rationale(self, category: FixCategory, code: str) -> str:
        """生成修复理由"""
        rationale_map = {
            FixCategory.NULL_SAFETY_FIX: "添加空值检查可以防止NullPointerException，提高代码健壮性",
            FixCategory.ERROR_HANDLING_FIX: "增强错误处理可以提供更好的调试信息和恢复机制",
            FixCategory.BOUNDARY_FIX: "边界检查可以防止边界条件下的错误和潜在的安全问题",
            FixCategory.SECURITY_FIX: "安全修复可以消除潜在的安全漏洞，保护系统安全",
            FixCategory.TEST_ADDITION: "增加测试覆盖率可以提高代码质量，减少回归风险"
        }
        return rationale_map.get(category, "根据代码分析推荐的修复方案")

    def _estimate_effort(self, suggestion: FixSuggestion) -> float:
        """估算工作量"""
        complexity_hours = {
            FixComplexity.TRIVIAL: 0.25,
            FixComplexity.SIMPLE: 0.5,
            FixComplexity.MODERATE: 1.0,
            FixComplexity.COMPLEX: 2.0
        }

        base_effort = complexity_hours.get(suggestion.complexity, 1.0)

        if suggestion.category == FixCategory.SECURITY_FIX:
            base_effort *= 1.5
        elif suggestion.category == FixCategory.TEST_ADDITION:
            base_effort = 0.5

        return base_effort

    def _suggest_test_cases(self, category: FixCategory,
                          suggestion: FixSuggestion) -> List[Dict[str, str]]:
        """建议测试用例"""
        test_cases = []

        if category == FixCategory.NULL_SAFETY_FIX:
            test_cases.append({
                "name": "test_null_input_handling",
                "description": "测试空输入的处理",
                "input": "None",
                "expected": "优雅处理或抛出明确异常"
            })
        elif category == FixCategory.BOUNDARY_FIX:
            test_cases.append({
                "name": "test_boundary_conditions",
                "description": "测试边界条件",
                "input": "min_value, max_value, min_value-1, max_value+1",
                "expected": "正确处理所有边界情况"
            })
        elif category == FixCategory.ERROR_HANDLING_FIX:
            test_cases.append({
                "name": "test_exception_handling",
                "description": "测试异常处理",
                "input": "触发异常的输入",
                "expected": "捕获并正确处理异常"
            })

        return test_cases


class FixSuggestionLayer:
    """FixSuggestionLayer - 代码修复建议生成层

    功能描述：
        - 分析缺陷代码上下文
        - 智能生成修复建议
        - 提供具体的修复代码示例
        - 评估修复复杂度和风险
        - 推荐需要添加的测试用例
        - 提供最佳实践指导
        - 生成修复优先级排序

    输入类型：
        - PipelineContext: 包含缺陷分析结果和未覆盖代码信息
        - 源代码上下文
        - 测试结果

    输出类型：
        - FixSuggestionResult: 修复建议结果
        - 包含建议列表、分组、统计信息

    使用场景：
        - 开发人员代码修复指导
        - 自动化代码审查
        - 技术债务管理
        - 测试覆盖率提升指导
        - 代码质量改进

    V3.1升级点：
        - 增强的代码理解能力
        - 多语言支持
        - 智能修复代码生成
        - 修复效果预估
        - 回归风险评估
    """

    description: str = "FixSuggestionLayer - 代码修复建议生成层"
    input_type: str = "PipelineContext - 包含缺陷分析和代码上下文"
    output_type: str = "FixSuggestionResult - 修复建议结果"

    def __init__(self):
        """初始化代码修复建议生成层"""
        self.generator = FixSuggestionGenerator()
        self.session_id = ""

    def process(self, context: Any) -> FixSuggestionResult:
        """处理缺陷和覆盖率数据，生成修复建议

        Args:
            context: PipelineContext对象，包含缺陷分析和覆盖率信息

        Returns:
            FixSuggestionResult: 修复建议结果

        Raises:
            ValueError: 当缺少必要的分析数据时
        """
        self.session_id = context.get('session_id', 'default_session')

        result = FixSuggestionResult(session_id=self.session_id)

        if context.has('defect_grading_result'):
            defect_result = context.get('defect_grading_result')
            self._process_defects(defect_result, result, context)

        if context.has('coverage_gap_analysis'):
            gap_analysis = context.get('coverage_gap_analysis')
            self._process_gap_analysis(gap_analysis, result, context)

        self._create_groups(result)

        result.statistics = self._calculate_statistics(result)
        result.recommendations = self._generate_recommendations(result)

        result.metadata = {
            "session_id": self.session_id,
            "processing_complete": True,
            "total_suggestions": len(result.suggestions)
        }

        context.set('fix_suggestion_result', result)
        context.set('fix_suggestion_complete', True)
        context.set('high_priority_fixes', result.get_high_priority_suggestions())

        return result

    def _process_defects(self, defect_result: Any, result: FixSuggestionResult,
                        context: Any) -> None:
        """处理缺陷，生成修复建议

        Args:
            defect_result: 缺陷分级结果
            result: 修复建议结果
            context: 上下文对象
        """
        if hasattr(defect_result, 'defects'):
            for defect in defect_result.defects:
                suggestion = self.generator.generate_fix_for_defect(defect, context)
                result.add_suggestion(suggestion)

    def _process_gap_analysis(self, gap_analysis: Any, result: FixSuggestionResult,
                             context: Any) -> None:
        """处理覆盖率差距分析，生成修复建议

        Args:
            gap_analysis: 覆盖率差距分析
            result: 修复建议结果
            context: 上下文对象
        """
        if hasattr(gap_analysis, 'uncovered_items'):
            for item in gap_analysis.uncovered_items:
                suggestion = self.generator.generate_fix_for_uncovered(item, context)
                result.add_suggestion(suggestion)

    def _create_groups(self, result: FixSuggestionResult) -> None:
        """创建修复建议分组

        Args:
            result: 修复建议结果
        """
        if result.security_fixes:
            security_group = FixGroup(
                group_id="security_fixes",
                group_type="security",
                title="安全修复",
                sequential_order=False
            )
            for fix in result.security_fixes:
                security_group.add_suggestion(fix)
            security_group.summary = {
                "count": len(security_group.suggestions),
                "total_effort": security_group.get_total_effort()
            }
            result.groups.append(security_group)

        high_priority = result.get_high_priority_suggestions()
        if high_priority:
            critical_group = FixGroup(
                group_id="critical_fixes",
                group_type="priority",
                title="高优先级修复",
                sequential_order=False
            )
            for suggestion in high_priority[:10]:
                critical_group.add_suggestion(suggestion)
            critical_group.summary = {
                "count": len(critical_group.suggestions),
                "total_effort": critical_group.get_total_effort()
            }
            result.groups.append(critical_group)

        if result.by_file:
            for file_path, suggestions in result.by_file.items():
                if len(suggestions) > 2:
                    file_group = FixGroup(
                        group_id=f"file_{hash(file_path) % 1000}",
                        group_type="file",
                        title=f"文件修复: {file_path}",
                        sequential_order=False
                    )
                    for suggestion in suggestions:
                        file_group.add_suggestion(suggestion)
                    result.groups.append(file_group)

    def _calculate_statistics(self, result: FixSuggestionResult) -> Dict[str, Any]:
        """计算统计信息

        Args:
            result: 修复建议结果

        Returns:
            Dict[str, Any]: 统计信息
        """
        by_category = {
            cat.name: len(sugs) for cat, sugs in result.by_category.items()
        }

        high_priority = result.get_high_priority_suggestions()

        complexity_distribution = {
            "trivial": 0,
            "simple": 0,
            "moderate": 0,
            "complex": 0
        }
        for suggestion in result.suggestions:
            complexity_distribution[suggestion.complexity.name.lower()] += 1

        return {
            "total_suggestions": len(result.suggestions),
            "by_category": by_category,
            "high_priority_count": len(high_priority),
            "security_fixes_count": len(result.security_fixes),
            "total_effort_hours": result.total_effort,
            "files_affected": len(result.by_file),
            "complexity_distribution": complexity_distribution
        }

    def _generate_recommendations(self, result: FixSuggestionResult) -> List[str]:
        """生成建议

        Args:
            result: 修复建议结果

        Returns:
            List[str]: 建议列表
        """
        recommendations = []

        if result.security_fixes:
            recommendations.append(
                f"发现{len(result.security_fixes)}个安全修复建议，必须优先处理"
            )

        high_priority = result.get_high_priority_suggestions()
        if high_priority:
            recommendations.append(
                f"建议优先处理{len(high_priority)}个高优先级修复"
            )

        if result.total_effort > 0:
            recommendations.append(
                f"预计总工作量约为{result.total_effort}小时"
            )

        sorted_suggestions = result.get_sorted_by_priority()[:5]
        if sorted_suggestions:
            recommendations.append(
                "最紧急的修复: " + ", ".join(s.title for s in sorted_suggestions[:3])
            )

        return recommendations

    def get_suggestions_by_file(self, result: FixSuggestionResult,
                              file_path: str) -> List[FixSuggestion]:
        """获取指定文件的修复建议

        Args:
            result: 修复建议结果
            file_path: 文件路径

        Returns:
            List[FixSuggestion]: 该文件的修复建议列表
        """
        return result.by_file.get(file_path, [])

    def get_suggestions_by_category(self, result: FixSuggestionResult,
                                   category: FixCategory) -> List[FixSuggestion]:
        """获取指定类别的修复建议

        Args:
            result: 修复建议结果
            category: 修复类别

        Returns:
            List[FixSuggestion]: 该类别的修复建议列表
        """
        return result.by_category.get(category, [])

    def export_fix_plan(self, result: FixSuggestionResult,
                      format: str = "dict") -> Any:
        """导出修复计划

        Args:
            result: 修复建议结果
            format: 输出格式

        Returns:
            Any: 修复计划数据
        """
        if format == "dict":
            return result.to_dict()
        elif format == "summary":
            return {
                "total_fixes": len(result.suggestions),
                "priority_fixes": result.high_priority_count,
                "security_fixes": len(result.security_fixes),
                "estimated_effort": result.total_effort,
                "recommendations": result.recommendations
            }
        else:
            return result.to_dict()
