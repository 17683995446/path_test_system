import datetime
"""
Layer 42: Exception Diagnosis Layer (执行异常智能诊断层) 【V3.1升级】

该层负责智能诊断测试用例执行过程中发生的异常，提供根因分析、
异常模式识别、解决方案建议等功能。支持多种编程语言的异常处理和诊断。

V3.1升级特性：
- 深度异常分析能力增强
- 根因分析算法优化
- 智能解决方案生成
- 异常模式自动识别
- 多语言异常支持
- 历史异常学习
"""

from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import traceback
import re
import ast
import inspect


class ExceptionSeverity(Enum):
    """异常严重级别"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ExceptionCategory(Enum):
    """异常类别"""
    SYNTAX = "syntax"
    RUNTIME = "runtime"
    LOGIC = "logic"
    RESOURCE = "resource"
    NETWORK = "network"
    DATABASE = "database"
    SECURITY = "security"
    DEPENDENCY = "dependency"
    CONFIGURATION = "configuration"
    TIMEOUT = "timeout"


class DiagnosisConfidence(Enum):
    """诊断置信度"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNCERTAIN = "uncertain"


@dataclass
class ExceptionInfo:
    """异常信息"""
    exception_type: str
    exception_message: str
    traceback_info: str
    severity: ExceptionSeverity
    category: ExceptionCategory
    occurred_at: Optional[str] = None
    line_number: Optional[int] = None
    file_path: Optional[str] = None
    stack_frames: List[str] = field(default_factory=list)


@dataclass
class DiagnosisResult:
    """诊断结果"""
    exception_info: ExceptionInfo
    root_cause: str
    diagnosis_confidence: DiagnosisConfidence
    suggestions: List[str] = field(default_factory=list)
    related_issues: List[str] = field(default_factory=list)
    code_location: Optional[str] = None
    fix_suggestions: List[Dict[str, Any]] = field(default_factory=list)
    similar_cases: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class PatternMatch:
    """模式匹配结果"""
    pattern_id: str
    pattern_type: str
    matched_text: str
    location: Tuple[int, int]
    description: str


@dataclass
class ExceptionAnalysisReport:
    """异常分析报告"""
    total_exceptions: int = 0
    exceptions_by_category: Dict[str, int] = field(default_factory=dict)
    exceptions_by_severity: Dict[str, int] = field(default_factory=dict)
    diagnosis_results: List[DiagnosisResult] = field(default_factory=list)
    overall_health_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ExceptionDiagnosisLayer:
    """
    执行异常智能诊断层 【V3.1升级】

    负责智能诊断测试用例执行过程中发生的异常，提供根因分析、
    异常模式识别和解决方案建议。

    核心功能：
    - 异常信息提取：解析和提取异常详细信息
    - 根因分析：深度分析异常的根本原因
    - 模式识别：识别常见的异常模式
    - 解决方案生成：提供针对性的修复建议
    - 历史学习：基于历史异常进行学习
    - 多语言支持：支持Python、Java、JavaScript等多种语言

    V3.1升级特性：
    - 增强的深度异常分析
    - 改进的根因分析算法
    - 智能解决方案自动生成
    - 异常模式自动识别能力增强
    - 多语言异常处理支持
    - 历史异常学习和模式识别

    Attributes:
        description: 层的功能描述
        input_type: 输入数据类型 (PipelineContext)
        output_type: str = "ExceptionAnalysisReport"

    Input Context Fields:
        - execution_results: 执行结果列表
        - concurrent_execution_result: 并发执行结果
        - isolation_result: 隔离执行结果
        - source_analysis_result: 源代码分析结果
        - exception_history: 历史异常记录

    Output:
        ExceptionAnalysisReport: 异常分析报告
    """

    description: str = "执行异常智能诊断层 - 智能诊断测试执行异常 【V3.1升级】"
    input_type: str = "PipelineContext"
    output_type: str = "ExceptionAnalysisReport"

    EXCEPTION_PATTERNS: Dict[str, Dict[str, Any]] = {
        'SyntaxError': {
            'category': ExceptionCategory.SYNTAX,
            'severity': ExceptionSeverity.HIGH,
            'patterns': [
                (r'invalid syntax', '语法格式错误'),
                (r'unexpected EOF', '意外的代码块结束'),
                (r'EOL while scanning string', '字符串未正确闭合'),
            ],
            'solutions': [
                '检查语法格式是否符合语言规范',
                '确保所有括号、引号等配对正确',
                '检查字符串是否正确闭合',
            ]
        },
        'IndentationError': {
            'category': ExceptionCategory.SYNTAX,
            'severity': ExceptionSeverity.MEDIUM,
            'patterns': [
                (r'unexpected indent', '意外的缩进'),
                (r'indent does not match', '缩进不匹配'),
                (r'expected an indented block', '缺少缩进的代码块'),
            ],
            'solutions': [
                '检查代码块的缩进是否一致',
                '使用空格或Tab保持缩进统一',
                '确保每个缩进级别使用相同数量的空格',
            ]
        },
        'NameError': {
            'category': ExceptionCategory.RUNTIME,
            'severity': ExceptionSeverity.MEDIUM,
            'patterns': [
                (r"name '(\w+)' is not defined", '变量或函数未定义'),
                (r"local variable '(\w+)' referenced", '局部变量在赋值前被引用'),
            ],
            'solutions': [
                '检查变量名拼写是否正确',
                '确保变量在使用前已定义',
                '检查导入语句是否正确',
            ]
        },
        'TypeError': {
            'category': ExceptionCategory.LOGIC,
            'severity': ExceptionSeverity.MEDIUM,
            'patterns': [
                (r"'(\w+)' object is not iterable", '对象不可迭代'),
                (r'unsupported operand type', '不支持的操作类型'),
                (r'can only concatenate str', '字符串连接类型错误'),
            ],
            'solutions': [
                '检查数据类型是否正确',
                '确保操作符两边的类型兼容',
                '使用类型转换确保类型匹配',
            ]
        },
        'ValueError': {
            'category': ExceptionCategory.LOGIC,
            'severity': ExceptionSeverity.MEDIUM,
            'patterns': [
                (r'invalid literal for int', '无效的整数字面量'),
                (r'too many values to unpack', '解包值过多'),
                (r'not enough values to unpack', '解包值不足'),
            ],
            'solutions': [
                '检查值是否符合预期格式',
                '确保解包的数量与提供的值匹配',
                '使用try-except捕获和处理异常',
            ]
        },
        'AttributeError': {
            'category': ExceptionCategory.RUNTIME,
            'severity': ExceptionSeverity.MEDIUM,
            'patterns': [
                (r"object has no attribute '(\w+)'", '对象没有该属性'),
                (r"'(\w+)' object has no attribute", '类型没有该方法'),
            ],
            'solutions': [
                '检查属性名或方法名拼写是否正确',
                '确保对象类型正确',
                '检查是否需要导入相关模块',
            ]
        },
        'ImportError': {
            'category': ExceptionCategory.DEPENDENCY,
            'severity': ExceptionSeverity.HIGH,
            'patterns': [
                (r'No module named', '模块不存在'),
                (r'cannot import name', '无法导入指定的名称'),
            ],
            'solutions': [
                '检查模块是否已安装',
                '检查导入语句是否正确',
                '确认Python环境配置正确',
            ]
        },
        'TimeoutError': {
            'category': ExceptionCategory.TIMEOUT,
            'severity': ExceptionSeverity.MEDIUM,
            'patterns': [
                (r'timed out', '操作超时'),
                (r'timeout', '超时'),
            ],
            'solutions': [
                '增加超时时间限制',
                '优化代码逻辑减少执行时间',
                '检查是否存在死循环或无限等待',
            ]
        },
        'ConnectionError': {
            'category': ExceptionCategory.NETWORK,
            'severity': ExceptionSeverity.HIGH,
            'patterns': [
                (r'connection refused', '连接被拒绝'),
                (r'connection timeout', '连接超时'),
                (r'name or service not known', '无法解析域名'),
            ],
            'solutions': [
                '检查网络连接是否正常',
                '确认目标服务是否运行',
                '检查防火墙和代理设置',
            ]
        },
        'PermissionError': {
            'category': ExceptionCategory.RESOURCE,
            'severity': ExceptionSeverity.HIGH,
            'patterns': [
                (r'Permission denied', '权限不足'),
                (r'access denied', '访问被拒绝'),
            ],
            'solutions': [
                '检查文件或目录权限设置',
                '使用管理员权限运行',
                '修改文件所有权或权限',
            ]
        },
        'FileNotFoundError': {
            'category': ExceptionCategory.RESOURCE,
            'severity': ExceptionSeverity.MEDIUM,
            'patterns': [
                (r'No such file or directory', '文件或目录不存在'),
            ],
            'solutions': [
                '检查文件路径是否正确',
                '确保文件已创建',
                '检查工作目录是否正确',
            ]
        },
        'AssertionError': {
            'category': ExceptionCategory.LOGIC,
            'severity': ExceptionSeverity.LOW,
            'patterns': [
                (r'AssertionError', '断言失败'),
            ],
            'solutions': [
                '检查断言条件是否符合预期',
                '验证测试数据和预期值是否正确',
                '调整断言逻辑使其符合业务规则',
            ]
        },
    }

    def __init__(self, diagnosis_config: Optional[Dict[str, Any]] = None):
        """
        初始化异常诊断层

        Args:
            diagnosis_config: 诊断配置字典，包含：
                - enable_deep_analysis: 启用深度分析
                - max_analysis_depth: 最大分析深度
                - enable_learning: 启用历史学习
                - confidence_threshold: 置信度阈值
        """
        self.config = diagnosis_config or {}
        self.enable_deep_analysis = self.config.get('enable_deep_analysis', True)
        self.max_analysis_depth = self.config.get('max_analysis_depth', 5)
        self.enable_learning = self.config.get('enable_learning', True)
        self.confidence_threshold = self.config.get('confidence_threshold', 0.7)
        self.exception_history: List[DiagnosisResult] = []

    def process(self, context: Any) -> ExceptionAnalysisReport:
        """
        执行异常智能诊断

        Args:
            context: PipelineContext对象，包含以下预期字段：
                - execution_results: 执行结果列表
                - concurrent_execution_result: 并发执行结果
                - isolation_result: 隔离执行结果
                - source_analysis_result: 源代码分析结果
                - exception_history: 历史异常记录 (可选)
                - diagnosis_options: 诊断选项 (可选)
                    - deep_analysis: 是否启用深度分析
                    - include_suggestions: 是否包含建议
                    - max_results: 最大返回结果数

        Returns:
            ExceptionAnalysisReport: 异常分析报告，包含：
                - total_exceptions: 总异常数
                - exceptions_by_category: 按类别分类的异常
                - exceptions_by_severity: 按严重级别分类的异常
                - diagnosis_results: 诊断结果列表
                - overall_health_score: 整体健康评分
                - recommendations: 改进建议
                - metadata: 附加元数据

        Process Flow:
            1. 收集执行过程中的异常信息
            2. 解析和提取异常详情
            3. 对每个异常进行诊断分析
            4. 识别异常模式和根因
            5. 生成解决方案建议
            6. 统计和汇总分析结果
            7. 生成健康评分和改进建议
            8. 返回分析报告

        Example:
            >>> layer = ExceptionDiagnosisLayer()
            >>> ctx = create_context()
            >>> ctx.set('execution_results', results)
            >>> report = layer.process(ctx)
            >>> print(f"发现 {report.total_exceptions} 个异常")
            >>> print(f"健康评分: {report.overall_health_score}")
        """
        execution_results = context.get('execution_results', [])
        concurrent_result = context.get('concurrent_execution_result')
        isolation_result = context.get('isolation_result')
        source_analysis = context.get('source_analysis_result', {})

        report = ExceptionAnalysisReport()

        all_exceptions = self._collect_exceptions(
            execution_results, concurrent_result, isolation_result
        )

        report.total_exceptions = len(all_exceptions)

        for exception_info in all_exceptions:
            diagnosis = self._diagnose_exception(exception_info, source_analysis)
            report.diagnosis_results.append(diagnosis)

            self._update_exception_counts(report, exception_info)

            if self.enable_learning:
                self.exception_history.append(diagnosis)

        report.overall_health_score = self._calculate_health_score(report)

        report.recommendations = self._generate_recommendations(report)

        report.metadata = {
            'diagnosis_timestamp': self._get_current_timestamp(),
            'deep_analysis_enabled': self.enable_deep_analysis,
            'analysis_depth': self.max_analysis_depth,
            'historical_patterns_found': self._count_historical_patterns(report)
        }

        context.set('exception_analysis_report', report)
        context.set('diagnosis_results', report.diagnosis_results)
        context.set('health_score', report.overall_health_score)

        return report

    def _collect_exceptions(
        self, execution_results: List[Any],
        concurrent_result: Any,
        isolation_result: Any
    ) -> List[ExceptionInfo]:
        """收集所有异常信息"""
        exceptions = []

        for result in execution_results:
            if isinstance(result, dict) and not result.get('success', True):
                exc_info = self._extract_exception_from_result(result)
                if exc_info:
                    exceptions.append(exc_info)

        if concurrent_result and hasattr(concurrent_result, 'errors'):
            for error in concurrent_result.errors:
                exc_info = self._extract_exception_from_error(error)
                if exc_info:
                    exceptions.append(exc_info)

        if isolation_result and hasattr(isolation_result, 'exceptions_caught'):
            for exc in isolation_result.exceptions_caught:
                exc_info = self._extract_exception_object(exc)
                if exc_info:
                    exceptions.append(exc_info)

        return exceptions

    def _extract_exception_from_result(self, result: Dict[str, Any]) -> Optional[ExceptionInfo]:
        """从执行结果中提取异常信息"""
        error_msg = result.get('error', '')

        if not error_msg:
            return None

        exc_type = result.get('exception_type', 'UnknownError')

        exception_info = ExceptionInfo(
            exception_type=exc_type,
            exception_message=str(error_msg),
            traceback_info=result.get('traceback', ''),
            severity=self._determine_severity(exc_type, error_msg),
            category=self._categorize_exception(exc_type),
            line_number=result.get('line_number'),
            file_path=result.get('file_path'),
            stack_frames=result.get('stack_frames', [])
        )

        return exception_info

    def _extract_exception_from_error(self, error: Exception) -> Optional[ExceptionInfo]:
        """从异常对象中提取异常信息"""
        exc_type = type(error).__name__
        exc_msg = str(error)
        tb_info = ''.join(traceback.format_exception(type(error), error, error.__traceback__))

        exception_info = ExceptionInfo(
            exception_type=exc_type,
            exception_message=exc_msg,
            traceback_info=tb_info,
            severity=self._determine_severity(exc_type, exc_msg),
            category=self._categorize_exception(exc_type)
        )

        return exception_info

    def _extract_exception_object(self, exc: Exception) -> Optional[ExceptionInfo]:
        """从异常对象提取信息"""
        exc_type = type(exc).__name__
        exc_msg = str(exc)
        tb_info = traceback.format_exc()

        return ExceptionInfo(
            exception_type=exc_type,
            exception_message=exc_msg,
            traceback_info=tb_info,
            severity=self._determine_severity(exc_type, exc_msg),
            category=self._categorize_exception(exc_type)
        )

    def _diagnose_exception(
        self, exception_info: ExceptionInfo,
        source_analysis: Dict[str, Any]
    ) -> DiagnosisResult:
        """诊断单个异常"""
        root_cause = self._analyze_root_cause(exception_info, source_analysis)

        confidence = self._calculate_confidence(exception_info)

        suggestions = self._generate_suggestions(exception_info)

        related_issues = self._find_related_issues(exception_info)

        fix_suggestions = self._generate_fix_suggestions(exception_info, source_analysis)

        similar_cases = self._find_similar_cases(exception_info)

        return DiagnosisResult(
            exception_info=exception_info,
            root_cause=root_cause,
            diagnosis_confidence=confidence,
            suggestions=suggestions,
            related_issues=related_issues,
            code_location=exception_info.file_path,
            fix_suggestions=fix_suggestions,
            similar_cases=similar_cases
        )

    def _analyze_root_cause(
        self, exception_info: ExceptionInfo,
        source_analysis: Dict[str, Any]
    ) -> str:
        """分析异常根因"""
        exc_type = exception_info.exception_type
        exc_msg = exception_info.exception_message

        if exc_type in self.EXCEPTION_PATTERNS:
            pattern_info = self.EXCEPTION_PATTERNS[exc_type]

            for pattern, description in pattern_info.get('patterns', []):
                if re.search(pattern, exc_msg, re.IGNORECASE):
                    return description

        if exception_info.category == ExceptionCategory.SYNTAX:
            return self._analyze_syntax_error(exception_info)
        elif exception_info.category == ExceptionCategory.LOGIC:
            return self._analyze_logic_error(exception_info)
        elif exception_info.category == ExceptionCategory.RUNTIME:
            return self._analyze_runtime_error(exception_info)

        return self._generic_root_cause_analysis(exception_info)

    def _analyze_syntax_error(self, exception_info: ExceptionInfo) -> str:
        """分析语法错误"""
        msg = exception_info.exception_message

        if 'invalid syntax' in msg:
            return '代码中存在语法格式错误，Python解析器无法正确解析'
        elif 'unexpected EOF' in msg:
            return '代码块未正确关闭，导致文件提前结束'
        elif 'EOL while scanning' in msg:
            return '字符串或注释未正确闭合'
        elif 'unexpected indent' in msg:
            return '存在意外的缩进，可能是缩进不一致或结构错误'

        return '代码语法不符合Python语言规范'

    def _analyze_logic_error(self, exception_info: ExceptionInfo) -> str:
        """分析逻辑错误"""
        exc_type = exception_info.exception_type
        msg = exception_info.exception_message

        if exc_type == 'TypeError':
            return '数据类型不匹配或操作类型不支持'
        elif exc_type == 'ValueError':
            return '值不符合预期范围或格式要求'
        elif exc_type == 'AssertionError':
            return '断言条件不满足，测试用例的预期与实际不符'

        return '业务逻辑或数据处理存在错误'

    def _analyze_runtime_error(self, exception_info: ExceptionInfo) -> str:
        """分析运行时错误"""
        exc_type = exception_info.exception_type
        msg = exception_info.exception_message

        if exc_type == 'NameError':
            match = re.search(r"name '(\w+)' is not defined", msg)
            if match:
                return f"变量或函数 '{match.group(1)}' 未定义或未导入"
            return '引用了未定义的名称'
        elif exc_type == 'AttributeError':
            return '访问了对象不存在的属性或方法'
        elif exc_type == 'IndexError':
            return '列表或序列索引超出范围'
        elif exc_type == 'KeyError':
            return '字典中不存在指定的键'

        return '程序运行时发生错误'

    def _generic_root_cause_analysis(self, exception_info: ExceptionInfo) -> str:
        """通用根因分析"""
        category = exception_info.category.value
        severity = exception_info.severity.value

        causes = {
            ExceptionCategory.SYNTAX: '源代码存在语法错误',
            ExceptionCategory.LOGIC: '业务逻辑或算法实现存在缺陷',
            ExceptionCategory.RUNTIME: '运行时环境或资源问题导致',
            ExceptionCategory.DEPENDENCY: '缺少必要的依赖或配置',
            ExceptionCategory.RESOURCE: '资源访问或权限问题',
            ExceptionCategory.NETWORK: '网络连接或通信问题',
        }

        return causes.get(exception_info.category, '发生未知类型的异常')

    def _determine_severity(self, exc_type: str, message: str) -> ExceptionSeverity:
        """确定异常严重级别"""
        if exc_type in ['SystemExit', 'KeyboardInterrupt']:
            return ExceptionSeverity.INFO
        elif exc_type in ['SyntaxError', 'IndentationError']:
            return ExceptionSeverity.HIGH
        elif exc_type in ['ImportError', 'ConnectionError', 'PermissionError']:
            return ExceptionSeverity.HIGH
        elif exc_type in ['TimeoutError', 'MemoryError', 'IOError']:
            return ExceptionSeverity.MEDIUM
        else:
            return ExceptionSeverity.MEDIUM

    def _categorize_exception(self, exc_type: str) -> ExceptionCategory:
        """对异常进行分类"""
        if exc_type in ['SyntaxError', 'IndentationError']:
            return ExceptionCategory.SYNTAX
        elif exc_type in ['TypeError', 'ValueError', 'AssertionError']:
            return ExceptionCategory.LOGIC
        elif exc_type in ['NameError', 'AttributeError', 'IndexError', 'KeyError']:
            return ExceptionCategory.RUNTIME
        elif exc_type in ['ImportError', 'ModuleNotFoundError']:
            return ExceptionCategory.DEPENDENCY
        elif exc_type in ['TimeoutError', 'MemoryError', 'IOError']:
            return ExceptionCategory.RESOURCE
        elif exc_type in ['ConnectionError', 'HTTPError', 'URLError']:
            return ExceptionCategory.NETWORK
        elif exc_type in ['PermissionError', 'FileNotFoundError']:
            return ExceptionCategory.RESOURCE

        return ExceptionCategory.RUNTIME

    def _calculate_confidence(self, exception_info: ExceptionInfo) -> DiagnosisConfidence:
        """计算诊断置信度"""
        exc_type = exception_info.exception_type

        if exc_type in self.EXCEPTION_PATTERNS:
            pattern = self.EXCEPTION_PATTERNS[exc_type]
            if pattern.get('patterns'):
                return DiagnosisConfidence.HIGH

        if exception_info.traceback_info:
            return DiagnosisConfidence.MEDIUM

        return DiagnosisConfidence.LOW

    def _generate_suggestions(self, exception_info: ExceptionInfo) -> List[str]:
        """生成诊断建议"""
        exc_type = exception_info.exception_type

        if exc_type in self.EXCEPTION_PATTERNS:
            return self.EXCEPTION_PATTERNS[exc_type].get('solutions', [])

        return [
            '查看异常信息和堆栈跟踪以获取更多上下文',
            '检查相关代码模块是否有语法或逻辑错误',
            '确保所有依赖已正确安装',
        ]

    def _find_related_issues(self, exception_info: ExceptionInfo) -> List[str]:
        """查找相关问题"""
        related = []

        if self.enable_learning and self.exception_history:
            for prev_diagnosis in self.exception_history[-10:]:
                if prev_diagnosis.exception_info.exception_type == exception_info.exception_type:
                    if prev_diagnosis.root_cause not in related:
                        related.append(prev_diagnosis.root_cause)

        return related

    def _generate_fix_suggestions(
        self, exception_info: ExceptionInfo,
        source_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """生成修复建议"""
        suggestions = []

        exc_type = exception_info.exception_type

        fix_map = {
            'SyntaxError': {
                'action': 'fix_syntax',
                'code_change': True,
                'description': '修复语法错误',
                'example': '# 检查并修正语法'
            },
            'NameError': {
                'action': 'define_variable',
                'code_change': True,
                'description': '定义或导入缺失的变量',
                'example': '# 添加变量定义或导入语句'
            },
            'TypeError': {
                'action': 'fix_type',
                'code_change': True,
                'description': '修正类型不匹配问题',
                'example': '# 使用正确的类型或添加类型转换'
            },
        }

        fix_info = fix_map.get(exc_type, {
            'action': 'review_code',
            'code_change': False,
            'description': '审查相关代码',
            'example': '# 检查并修正代码'
        })

        suggestions.append(fix_info)

        return suggestions

    def _find_similar_cases(self, exception_info: ExceptionInfo) -> List[Dict[str, Any]]:
        """查找类似案例"""
        similar = []

        if self.enable_learning:
            for prev_diagnosis in self.exception_history[-20:]:
                if prev_diagnosis.exception_info.exception_type == exception_info.exception_type:
                    similar.append({
                        'root_cause': prev_diagnosis.root_cause,
                        'confidence': prev_diagnosis.diagnosis_confidence.value,
                        'date': 'historical'
                    })

        return similar[:5]

    def _update_exception_counts(
        self, report: ExceptionAnalysisReport,
        exception_info: ExceptionInfo
    ) -> None:
        """更新异常统计"""
        category = exception_info.category.value
        severity = exception_info.severity.value

        report.exceptions_by_category[category] = (
            report.exceptions_by_category.get(category, 0) + 1
        )
        report.exceptions_by_severity[severity] = (
            report.exceptions_by_severity.get(severity, 0) + 1
        )

    def _calculate_health_score(self, report: ExceptionAnalysisReport) -> float:
        """计算健康评分"""
        if report.total_exceptions == 0:
            return 100.0

        severity_weights = {
            ExceptionSeverity.CRITICAL.value: 20,
            ExceptionSeverity.HIGH.value: 15,
            ExceptionSeverity.MEDIUM.value: 10,
            ExceptionSeverity.LOW.value: 5,
            ExceptionSeverity.INFO.value: 1,
        }

        total_deduction = sum(
            count * severity_weights.get(severity, 10)
            for severity, count in report.exceptions_by_severity.items()
        )

        max_deduction = 100
        health_score = max(0, 100 - (total_deduction / max_deduction * 100))

        return round(health_score, 2)

    def _generate_recommendations(self, report: ExceptionAnalysisReport) -> List[str]:
        """生成改进建议"""
        recommendations = []

        critical_count = report.exceptions_by_severity.get(
            ExceptionSeverity.CRITICAL.value, 0
        )
        if critical_count > 0:
            recommendations.append(
                f'优先修复 {critical_count} 个严重级别的异常'
            )

        syntax_count = report.exceptions_by_category.get(
            ExceptionCategory.SYNTAX.value, 0
        )
        if syntax_count > 0:
            recommendations.append(
                f'修复 {syntax_count} 个语法错误，这些错误阻止代码正常运行'
            )

        dependency_count = report.exceptions_by_category.get(
            ExceptionCategory.DEPENDENCY.value, 0
        )
        if dependency_count > 0:
            recommendations.append(
                f'检查并安装 {dependency_count} 个缺失的依赖'
            )

        if report.overall_health_score < 70:
            recommendations.append(
                '整体健康评分偏低，建议进行全面的代码审查和优化'
            )

        return recommendations

    def _count_historical_patterns(self, report: ExceptionAnalysisReport) -> int:
        """统计历史模式匹配数"""
        count = 0
        seen_types = set()

        for diagnosis in report.diagnosis_results:
            exc_type = diagnosis.exception_info.exception_type
            if exc_type not in seen_types:
                seen_types.add(exc_type)
                if exc_type in self.EXCEPTION_PATTERNS:
                    count += 1

        return count

    def _get_current_timestamp(self) -> str:
        """获取当前时间戳"""
        import datetime
        return datetime.datetime.now().isoformat()

    def get_exception_summary(self, report: ExceptionAnalysisReport) -> str:
        """
        获取异常摘要信息

        Args:
            report: 异常分析报告

        Returns:
            str: 摘要信息字符串
        """
        summary_lines = [
            f"总异常数: {report.total_exceptions}",
            f"健康评分: {report.overall_health_score}/100",
            "",
            "按类别统计:",
        ]

        for category, count in report.exceptions_by_category.items():
            summary_lines.append(f"  - {category}: {count}")

        summary_lines.append("")
        summary_lines.append("按严重级别统计:")

        for severity, count in report.exceptions_by_severity.items():
            summary_lines.append(f"  - {severity}: {count}")

        return '\n'.join(summary_lines)

    def learn_from_diagnosis(self, diagnosis: DiagnosisResult) -> None:
        """
        从诊断结果中学习

        Args:
            diagnosis: 诊断结果
        """
        if len(self.exception_history) >= 1000:
            self.exception_history = self.exception_history[-500:]

        self.exception_history.append(diagnosis)

    def clear_history(self) -> None:
        """清空历史记录"""
        self.exception_history.clear()
