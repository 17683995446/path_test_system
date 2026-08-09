"""
Layer 46: DefectGradingLayer - 缺陷智能分级与定位层

本层负责对测试过程中发现的缺陷进行智能分级和精确定位，综合考虑缺陷的严重程度、
影响范围、复现概率、可修复性等因素，生成缺陷分析报告和定位建议。
"""

from typing import Any, Optional, List, Dict, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import defaultdict
import hashlib


class DefectSeverity(Enum):
    """缺陷严重程度枚举"""
    BLOCKER = auto()
    CRITICAL = auto()
    MAJOR = auto()
    MINOR = auto()
    TRIVIAL = auto()


class DefectPriority(Enum):
    """缺陷优先级枚举"""
    P0_CRITICAL = auto()
    P1_HIGH = auto()
    P2_MEDIUM = auto()
    P3_LOW = auto()
    P4_TRIVIAL = auto()


class DefectStatus(Enum):
    """缺陷状态枚举"""
    OPEN = auto()
    CONFIRMED = auto()
    IN_PROGRESS = auto()
    RESOLVED = auto()
    VERIFIED = auto()
    CLOSED = auto()
    WONT_FIX = auto()


class DefectType(Enum):
    """缺陷类型枚举"""
    FUNCTIONAL = auto()
    LOGIC_ERROR = auto()
    BOUNDARY_ERROR = auto()
    NULL_POINTER = auto()
    RACE_CONDITION = auto()
    DEADLOCK = auto()
    MEMORY_LEAK = auto()
    RESOURCE_LEAK = auto()
    SECURITY_VULNERABILITY = auto()
    PERFORMANCE_ISSUE = auto()
    UI_DEFECT = auto()
    DATA_INCONSISTENCY = auto()
    CONFIGURATION_ERROR = auto()
    ENVIRONMENT_ISSUE = auto()
    DOCUMENTATION = auto()
    UNKNOWN = auto()


class RootCauseCategory(Enum):
    """根因类别枚举"""
    REQUIREMENT = auto()
    DESIGN = auto()
    IMPLEMENTATION = auto()
    TEST_DESIGN = auto()
    ENVIRONMENT = auto()
    DATA = auto()
    INTEGRATION = auto()
    MIGRATION = auto()
    CONFIGURATION = auto()
    EXTERNAL_DEPENDENCY = auto()
    UNKNOWN = auto()


@dataclass
class DefectLocation:
    """缺陷位置信息

    Attributes:
        file_path: 文件路径
        line_number: 行号
        column_number: 列号
        function_name: 函数名称
        class_name: 类名
        module_name: 模块名称
        method_signature: 方法签名
        api_endpoint: API端点
        service_name: 服务名称
    """
    file_path: str = ""
    line_number: int = 0
    column_number: int = 0
    function_name: str = ""
    class_name: str = ""
    module_name: str = ""
    method_signature: str = ""
    api_endpoint: str = ""
    service_name: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "file_path": self.file_path,
            "line_number": self.line_number,
            "column_number": self.column_number,
            "function_name": self.function_name,
            "class_name": self.class_name,
            "module_name": self.module_name,
            "method_signature": self.method_signature,
            "api_endpoint": self.api_endpoint,
            "service_name": self.service_name
        }


@dataclass
class DefectEvidence:
    """缺陷证据信息

    Attributes:
        evidence_type: 证据类型
        description: 描述
        stack_trace: 堆栈跟踪
        test_case_id: 触发缺陷的测试用例ID
        input_data: 触发缺陷的输入数据
        expected_result: 预期结果
        actual_result: 实际结果
        screenshot_path: 截图路径
        log_snippet: 日志片段
        memory_dump: 内存转储路径
        timestamp: 发现时间戳
    """
    evidence_type: str = ""
    description: str = ""
    stack_trace: str = ""
    test_case_id: str = ""
    input_data: Dict[str, Any] = field(default_factory=dict)
    expected_result: Any = None
    actual_result: Any = None
    screenshot_path: str = ""
    log_snippet: str = ""
    memory_dump: str = ""
    timestamp: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "evidence_type": self.evidence_type,
            "description": self.description,
            "stack_trace": self.stack_trace,
            "test_case_id": self.test_case_id,
            "input_data": self.input_data,
            "expected_result": str(self.expected_result) if self.expected_result else None,
            "actual_result": str(self.actual_result) if self.actual_result else None,
            "screenshot_path": self.screenshot_path,
            "log_snippet": self.log_snippet,
            "timestamp": self.timestamp
        }


@dataclass
class Defect:
    """缺陷数据模型

    Attributes:
        defect_id: 缺陷唯一标识符
        title: 缺陷标题
        description: 缺陷描述
        severity: 严重程度
        priority: 优先级
        status: 状态
        defect_type: 缺陷类型
        location: 缺陷位置
        evidence: 缺陷证据
        root_cause: 根因分析
        root_cause_category: 根因类别
        affected_components: 受影响的组件列表
        related_defects: 相关缺陷ID列表
        tags: 标签列表
        assignee: 负责人
        reporter: 报告人
        created_at: 创建时间
        updated_at: 更新时间
        resolved_at: 解决时间
        fix_version: 修复版本
        test_coverage_impact: 对测试覆盖率的影响
        risk_assessment: 风险评估
    """
    defect_id: str
    title: str
    description: str = ""
    severity: DefectSeverity = DefectSeverity.MAJOR
    priority: DefectPriority = DefectPriority.P2_MEDIUM
    status: DefectStatus = DefectStatus.OPEN
    defect_type: DefectType = DefectType.UNKNOWN
    location: DefectLocation = field(default_factory=DefectLocation)
    evidence: DefectEvidence = field(default_factory=DefectEvidence)
    root_cause: str = ""
    root_cause_category: RootCauseCategory = RootCauseCategory.UNKNOWN
    affected_components: List[str] = field(default_factory=list)
    related_defects: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    assignee: str = ""
    reporter: str = ""
    created_at: float = 0.0
    updated_at: float = 0.0
    resolved_at: float = 0.0
    fix_version: str = ""
    test_coverage_impact: float = 0.0
    risk_assessment: Dict[str, Any] = field(default_factory=dict)

    def generate_id(self) -> str:
        """生成缺陷ID"""
        content = f"{self.location.file_path}:{self.location.line_number}:{self.title}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def calculate_priority(self) -> DefectPriority:
        """根据严重程度和其他因素计算优先级

        Returns:
            DefectPriority: 计算后的优先级
        """
        severity_map = {
            DefectSeverity.BLOCKER: DefectPriority.P0_CRITICAL,
            DefectSeverity.CRITICAL: DefectPriority.P0_CRITICAL,
            DefectSeverity.MAJOR: DefectPriority.P1_HIGH,
            DefectSeverity.MINOR: DefectPriority.P2_MEDIUM,
            DefectSeverity.TRIVIAL: DefectPriority.P3_LOW
        }

        base_priority = severity_map.get(self.severity, DefectPriority.P2_MEDIUM)

        if self.defect_type == DefectType.SECURITY_VULNERABILITY:
            return DefectPriority.P0_CRITICAL
        elif self.defect_type == DefectType.RACE_CONDITION:
            return DefectPriority.P1_HIGH
        elif self.defect_type == DefectType.PERFORMANCE_ISSUE:
            return DefectPriority.P1_HIGH

        return base_priority

    def assess_risk(self) -> Dict[str, Any]:
        """评估风险

        Returns:
            Dict[str, Any]: 风险评估结果
        """
        severity_weights = {
            DefectSeverity.BLOCKER: 100,
            DefectSeverity.CRITICAL: 80,
            DefectSeverity.MAJOR: 60,
            DefectSeverity.MINOR: 30,
            DefectSeverity.TRIVIAL: 10
        }

        base_risk = severity_weights.get(self.severity, 50)

        impact_multiplier = 1.0
        if len(self.affected_components) > 3:
            impact_multiplier = 1.5
        elif len(self.affected_components) > 1:
            impact_multiplier = 1.2

        if self.defect_type == DefectType.SECURITY_VULNERABILITY:
            impact_multiplier = 2.0
        elif self.defect_type == DefectType.DATA_INCONSISTENCY:
            impact_multiplier = 1.5

        risk_score = base_risk * impact_multiplier

        risk_level = "low"
        if risk_score >= 80:
            risk_level = "critical"
        elif risk_score >= 60:
            risk_level = "high"
        elif risk_score >= 30:
            risk_level = "medium"

        self.risk_assessment = {
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "impact_multiplier": impact_multiplier,
            "components_affected": len(self.affected_components)
        }

        return self.risk_assessment

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "defect_id": self.defect_id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity.name,
            "priority": self.priority.name,
            "status": self.status.name,
            "defect_type": self.defect_type.name,
            "location": self.location.to_dict(),
            "evidence": self.evidence.to_dict(),
            "root_cause": self.root_cause,
            "root_cause_category": self.root_cause_category.name,
            "affected_components": self.affected_components,
            "related_defects": self.related_defects,
            "tags": self.tags,
            "assignee": self.assignee,
            "reporter": self.reporter,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "resolved_at": self.resolved_at,
            "fix_version": self.fix_version,
            "risk_assessment": self.risk_assessment
        }


@dataclass
class DefectGradingResult:
    """缺陷分级结果

    Attributes:
        session_id: 会话标识符
        defects: 缺陷列表
        defects_by_severity: 按严重程度分类的缺陷
        defects_by_priority: 按优先级分类的缺陷
        defects_by_type: 按类型分类的缺陷
        defects_by_component: 按组件分类的缺陷
        statistics: 统计信息
        risk_summary: 风险摘要
        recommendations: 建议
        metadata: 其他元信息
    """
    session_id: str
    defects: List[Defect] = field(default_factory=list)
    defects_by_severity: Dict[DefectSeverity, List[Defect]] = field(default_factory=dict)
    defects_by_priority: Dict[DefectPriority, List[Defect]] = field(default_factory=dict)
    defects_by_type: Dict[DefectType, List[Defect]] = field(default_factory=dict)
    defects_by_component: Dict[str, List[Defect]] = field(default_factory=dict)
    statistics: Dict[str, Any] = field(default_factory=dict)
    risk_summary: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_defect(self, defect: Defect) -> None:
        """添加缺陷"""
        self.defects.append(defect)

        if defect.severity not in self.defects_by_severity:
            self.defects_by_severity[defect.severity] = []
        self.defects_by_severity[defect.severity].append(defect)

        if defect.priority not in self.defects_by_priority:
            self.defects_by_priority[defect.priority] = []
        self.defects_by_priority[defect.priority].append(defect)

        if defect.defect_type not in self.defects_by_type:
            self.defects_by_type[defect.defect_type] = []
        self.defects_by_type[defect.defect_type].append(defect)

        for component in defect.affected_components:
            if component not in self.defects_by_component:
                self.defects_by_component[component] = []
            self.defects_by_component[component].append(defect)

    def get_critical_defects(self) -> List[Defect]:
        """获取关键缺陷

        Returns:
            List[Defect]: 关键缺陷列表
        """
        critical = self.defects_by_severity.get(DefectSeverity.CRITICAL, [])
        blocker = self.defects_by_severity.get(DefectSeverity.BLOCKER, [])
        return blocker + critical

    def get_high_priority_defects(self) -> List[Defect]:
        """获取高优先级缺陷

        Returns:
            List[Defect]: 高优先级缺陷列表
        """
        return self.defects_by_priority.get(DefectPriority.P0_CRITICAL, []) + \
               self.defects_by_priority.get(DefectPriority.P1_HIGH, [])

    def calculate_statistics(self) -> Dict[str, Any]:
        """计算统计信息"""
        self.statistics = {
            "total_defects": len(self.defects),
            "by_severity": {
                sev.name: len(defs) for sev, defs in self.defects_by_severity.items()
            },
            "by_priority": {
                pri.name: len(defs) for pri, defs in self.defects_by_priority.items()
            },
            "by_type": {
                dtype.name: len(defs) for dtype, defs in self.defects_by_type.items()
            },
            "by_component": {
                comp: len(defs) for comp, defs in self.defects_by_component.items()
            },
            "open_defects": sum(1 for d in self.defects if d.status == DefectStatus.OPEN),
            "resolved_defects": sum(1 for d in self.defects if d.status == DefectStatus.RESOLVED),
            "avg_risk_score": sum(d.risk_assessment.get('risk_score', 0) for d in self.defects) / len(self.defects) if self.defects else 0
        }
        return self.statistics

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "session_id": self.session_id,
            "total_defects": len(self.defects),
            "defects": [d.to_dict() for d in self.defects],
            "statistics": self.statistics,
            "risk_summary": self.risk_summary,
            "recommendations": self.recommendations,
            "metadata": self.metadata
        }


class DefectGrader:
    """缺陷分级器

    功能描述：
        - 对缺陷进行自动分级
        - 分析缺陷类型和根因
        - 评估风险和影响范围
        - 定位缺陷代码位置
    """

    def __init__(self):
        """初始化缺陷分级器"""
        self.severity_keywords = self._init_severity_keywords()
        self.type_patterns = self._init_type_patterns()
        self.root_cause_patterns = self._init_root_cause_patterns()

    def _init_severity_keywords(self) -> Dict[DefectSeverity, List[str]]:
        """初始化严重程度关键词"""
        return {
            DefectSeverity.BLOCKER: ["crash", "hang", "deadlock", "data_loss", "security_bypass"],
            DefectSeverity.CRITICAL: ["corruption", "breach", "fatal", "unrecoverable", "major_loss"],
            DefectSeverity.MAJOR: ["broken", "incorrect", "missing", "failed", "wrong"],
            DefectSeverity.MINOR: ["typo", "cosmetic", "minor", "inconvenience"],
            DefectSeverity.TRIVIAL: ["trivial", "formatting", "whitespace", "naming"]
        }

    def _init_type_patterns(self) -> Dict[DefectType, List[str]]:
        """初始化缺陷类型模式"""
        return {
            DefectType.FUNCTIONAL: ["does not", "fails to", "unable to", "cannot"],
            DefectType.LOGIC_ERROR: ["logic", "condition", "wrong result", "incorrect calculation"],
            DefectType.BOUNDARY_ERROR: ["boundary", "edge case", "overflow", "underflow", "limit"],
            DefectType.NULL_POINTER: ["null", "none", "undefined", "NoneType", "null reference"],
            DefectType.RACE_CONDITION: ["race", "concurrent", "thread", "timing", "synchronization"],
            DefectType.SECURITY_VULNERABILITY: ["security", "injection", "xss", "csrf", "authentication"],
            DefectType.PERFORMANCE_ISSUE: ["slow", "performance", "timeout", "memory", "cpu"],
            DefectType.MEMORY_LEAK: ["memory leak", "out of memory", "oom", "allocation"]
        }

    def _init_root_cause_patterns(self) -> Dict[RootCauseCategory, List[str]]:
        """初始化根因模式"""
        return {
            RootCauseCategory.REQUIREMENT: ["requirement", "specification", "user story", "acceptance criteria"],
            RootCauseCategory.DESIGN: ["design", "architecture", "pattern", "structure"],
            RootCauseCategory.IMPLEMENTATION: ["coding", "implementation", "logic", "algorithm"],
            RootCauseCategory.TEST_DESIGN: ["test case", "test data", "test coverage", "test strategy"],
            RootCauseCategory.ENVIRONMENT: ["environment", "configuration", "deployment", "infrastructure"],
            RootCauseCategory.INTEGRATION: ["integration", "interface", "api", "communication"]
        }

    def grade_defect(self, title: str, description: str,
                   location: DefectLocation,
                   evidence: DefectEvidence) -> Defect:
        """对缺陷进行分级

        Args:
            title: 缺陷标题
            description: 缺陷描述
            location: 缺陷位置
            evidence: 缺陷证据

        Returns:
            Defect: 分级后的缺陷
        """
        defect = Defect(
            defect_id="",
            title=title,
            description=description,
            location=location,
            evidence=evidence
        )

        defect.defect_id = defect.generate_id()

        defect.severity = self._determine_severity(title, description, evidence)
        defect.defect_type = self._determine_defect_type(title, description, evidence)
        defect.root_cause = self._analyze_root_cause(title, description)
        defect.root_cause_category = self._determine_root_cause_category(defect.root_cause)
        defect.priority = defect.calculate_priority()
        defect.risk_assessment = defect.assess_risk()

        return defect

    def _determine_severity(self, title: str, description: str,
                          evidence: DefectEvidence) -> DefectSeverity:
        """确定严重程度

        Args:
            title: 缺陷标题
            description: 缺陷描述
            evidence: 缺陷证据

        Returns:
            DefectSeverity: 严重程度
        """
        content = f"{title} {description}".lower()

        for severity, keywords in self.severity_keywords.items():
            for keyword in keywords:
                if keyword in content:
                    return severity

        if evidence.evidence_type == "crash":
            return DefectSeverity.CRITICAL
        elif evidence.evidence_type == "error":
            return DefectSeverity.MAJOR

        return DefectSeverity.MAJOR

    def _determine_defect_type(self, title: str, description: str,
                             evidence: DefectEvidence) -> DefectType:
        """确定缺陷类型

        Args:
            title: 缺陷标题
            description: 缺陷描述
            evidence: 缺陷证据

        Returns:
            DefectType: 缺陷类型
        """
        content = f"{title} {description}".lower()

        if evidence.stack_trace:
            if "NullPointer" in evidence.stack_trace or "NoneType" in evidence.stack_trace:
                return DefectType.NULL_POINTER
            elif "Timeout" in evidence.stack_trace or "timed out" in content:
                return DefectType.PERFORMANCE_ISSUE

        for dtype, patterns in self.type_patterns.items():
            for pattern in patterns:
                if pattern in content:
                    return dtype

        return DefectType.UNKNOWN

    def _analyze_root_cause(self, title: str, description: str) -> str:
        """分析根因

        Args:
            title: 缺陷标题
            description: 缺陷描述

        Returns:
            str: 根因描述
        """
        content = f"{title} {description}".lower()

        root_causes = []

        if "requirement" in content or "spec" in content:
            root_causes.append("需求理解偏差或需求变更未同步")
        if "design" in content or "architecture" in content:
            root_causes.append("设计缺陷或架构不合理")
        if "logic" in content or "condition" in content:
            root_causes.append("逻辑实现错误")
        if "boundary" in content or "edge case" in content:
            root_causes.append("边界条件未充分考虑")
        if "null" in content or "none" in content:
            root_causes.append("空值处理不完善")
        if "concurrent" in content or "race" in content:
            root_causes.append("并发控制不当")

        if not root_causes:
            root_causes.append("代码实现问题")

        return "; ".join(root_causes)

    def _determine_root_cause_category(self, root_cause: str) -> RootCauseCategory:
        """确定根因类别

        Args:
            root_cause: 根因描述

        Returns:
            RootCauseCategory: 根因类别
        """
        root_cause_lower = root_cause.lower()

        for category, patterns in self.root_cause_patterns.items():
            for pattern in patterns:
                if pattern in root_cause_lower:
                    return category

        return RootCauseCategory.IMPLEMENTATION


class DefectGradingLayer:
    """DefectGradingLayer - 缺陷智能分级与定位层

    功能描述：
        - 自动识别和收集测试过程中的缺陷
        - 对缺陷进行多维度分级（严重程度、优先级）
        - 精确定位缺陷代码位置
        - 分析缺陷类型和根因
        - 评估缺陷影响范围和风险
        - 生成缺陷分析报告
        - 提供缺陷修复建议

    输入类型：
        - PipelineContext: 包含测试结果和错误信息
        - 异常堆栈跟踪
        - 断言失败信息
        - 运行时错误日志

    输出类型：
        - DefectGradingResult: 缺陷分级结果
        - 包含缺陷列表、分类统计、风险评估

    使用场景：
        - 自动化缺陷管理
        - 质量评估报告
        - 回归测试分析
        - 发布风险评估
        - 测试策略优化

    V3.1升级点：
        - 增强智能根因分析
        - 自动化风险评分算法
        - 缺陷关联性分析
        - 影响范围智能评估
        - 修复建议自动生成
    """

    description: str = "DefectGradingLayer - 缺陷智能分级与定位"
    input_type: str = "PipelineContext - 包含测试结果、错误和异常信息"
    output_type: str = "DefectGradingResult - 缺陷分级结果"

    def __init__(self):
        """初始化缺陷智能分级与定位层"""
        self.grader = DefectGrader()
        self.session_id = ""

    def process(self, context: Any) -> DefectGradingResult:
        """处理测试结果，识别和分级缺陷

        Args:
            context: PipelineContext对象，包含测试结果和错误信息

        Returns:
            DefectGradingResult: 缺陷分级结果

        Raises:
            ValueError: 当缺少必要的测试结果数据时
        """
        self.session_id = context.get('session_id', 'default_session')

        result = DefectGradingResult(session_id=self.session_id)

        if context.has('test_failures'):
            test_failures = context.get('test_failures')
            self._process_test_failures(test_failures, result)

        if context.has('exceptions'):
            exceptions = context.get('exceptions')
            self._process_exceptions(exceptions, result, context)

        if context.has('assertion_failures'):
            assertion_failures = context.get('assertion_failures')
            self._process_assertion_failures(assertion_failures, result, context)

        if context.has('runtime_errors'):
            runtime_errors = context.get('runtime_errors')
            self._process_runtime_errors(runtime_errors, result, context)

        if context.has('coverage_gap_analysis'):
            gap_analysis = context.get('coverage_gap_analysis')
            self._supplement_from_gap_analysis(gap_analysis, result)

        result.calculate_statistics()
        result.risk_summary = self._generate_risk_summary(result)
        result.recommendations = self._generate_recommendations(result)

        result.metadata = {
            "session_id": self.session_id,
            "processing_complete": True,
            "defects_identified": len(result.defects)
        }

        context.set('defect_grading_result', result)
        context.set('defect_grading_complete', True)
        context.set('critical_defects', result.get_critical_defects())

        return result

    def _process_test_failures(self, test_failures: Any, result: DefectGradingResult) -> None:
        """处理测试失败

        Args:
            test_failures: 测试失败数据
            result: 缺陷分级结果
        """
        if isinstance(test_failures, dict):
            for test_id, failure_info in test_failures.items():
                if isinstance(failure_info, dict):
                    title = failure_info.get('name', test_id)
                    description = failure_info.get('message', failure_info.get('error', ''))

                    location = DefectLocation(
                        file_path=failure_info.get('file_path', ''),
                        line_number=failure_info.get('line_number', 0),
                        function_name=failure_info.get('test_name', '')
                    )

                    evidence = DefectEvidence(
                        evidence_type="test_failure",
                        description=description,
                        test_case_id=test_id,
                        expected_result=failure_info.get('expected'),
                        actual_result=failure_info.get('actual'),
                        timestamp=failure_info.get('timestamp', 0.0)
                    )

                    defect = self.grader.grade_defect(title, description, location, evidence)
                    result.add_defect(defect)

    def _process_exceptions(self, exceptions: Any, result: DefectGradingResult,
                          context: Any) -> None:
        """处理异常

        Args:
            exceptions: 异常数据
            result: 缺陷分级结果
            context: 上下文对象
        """
        if isinstance(exceptions, list):
            for i, exc in enumerate(exceptions):
                exception_type = type(exc).__name__ if hasattr(exc, '__class__') else 'Exception'
                exception_message = str(exc)

                title = f"异常: {exception_type}"
                description = exception_message

                stack_trace = ""
                if hasattr(exc, '__traceback__'):
                    import traceback
                    stack_trace = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))

                location = self._extract_location_from_stack(stack_trace)

                evidence = DefectEvidence(
                    evidence_type="exception",
                    description=description,
                    stack_trace=stack_trace,
                    timestamp=0.0
                )

                defect = self.grader.grade_defect(title, description, location, evidence)
                result.add_defect(defect)

    def _process_assertion_failures(self, assertion_failures: Any,
                                    result: DefectGradingResult,
                                    context: Any) -> None:
        """处理断言失败

        Args:
            assertion_failures: 断言失败数据
            result: 缺陷分级结果
            context: 上下文对象
        """
        if isinstance(assertion_failures, list):
            for failure in assertion_failures:
                if isinstance(failure, dict):
                    title = failure.get('test_case', '断言失败')
                    description = failure.get('message', '断言失败')

                    location = DefectLocation(
                        file_path=failure.get('file_path', ''),
                        line_number=failure.get('line_number', 0),
                        function_name=failure.get('function', '')
                    )

                    evidence = DefectEvidence(
                        evidence_type="assertion",
                        description=description,
                        test_case_id=failure.get('test_id', ''),
                        expected_result=failure.get('expected'),
                        actual_result=failure.get('actual')
                    )

                    defect = self.grader.grade_defect(title, description, location, evidence)
                    result.add_defect(defect)

    def _process_runtime_errors(self, runtime_errors: Any,
                               result: DefectGradingResult,
                               context: Any) -> None:
        """处理运行时错误

        Args:
            runtime_errors: 运行时错误数据
            result: 缺陷分级结果
            context: 上下文对象
        """
        if isinstance(runtime_errors, list):
            for error in runtime_errors:
                if isinstance(error, dict):
                    error_type = error.get('type', 'RuntimeError')
                    title = f"运行时错误: {error_type}"
                    description = error.get('message', '')

                    location = DefectLocation(
                        file_path=error.get('file_path', ''),
                        line_number=error.get('line_number', 0)
                    )

                    evidence = DefectEvidence(
                        evidence_type="runtime_error",
                        description=description,
                        stack_trace=error.get('stack_trace', ''),
                        log_snippet=error.get('log', '')
                    )

                    defect = self.grader.grade_defect(title, description, location, evidence)
                    result.add_defect(defect)

    def _supplement_from_gap_analysis(self, gap_analysis: Any,
                                     result: DefectGradingResult) -> None:
        """从覆盖率差距分析补充缺陷信息

        Args:
            gap_analysis: 覆盖率差距分析
            result: 缺陷分级结果
        """
        if hasattr(gap_analysis, 'critical_gaps'):
            for gap in gap_analysis.critical_gaps:
                title = f"覆盖率盲点: {gap.get('file', '')}:{gap.get('line', 0)}"
                description = f"未覆盖的关键代码路径，风险评分: {gap.get('risk_score', 0)}"

                location = DefectLocation(
                    file_path=gap.get('file', ''),
                    line_number=gap.get('line', 0)
                )

                evidence = DefectEvidence(
                    evidence_type="coverage_gap",
                    description=description
                )

                defect = self.grader.grade_defect(title, description, location, evidence)
                defect.severity = DefectSeverity.MINOR
                defect.defect_type = DefectType.FUNCTIONAL
                result.add_defect(defect)

    def _extract_location_from_stack(self, stack_trace: str) -> DefectLocation:
        """从堆栈跟踪提取位置信息

        Args:
            stack_trace: 堆栈跟踪字符串

        Returns:
            DefectLocation: 缺陷位置
        """
        import re

        location = DefectLocation()

        pattern = r'File "([^"]+)", line (\d+)'
        matches = re.findall(pattern, stack_trace)

        if matches:
            file_path, line_number = matches[0]
            location.file_path = file_path
            location.line_number = int(line_number)

        func_pattern = r'in (\w+)\('
        func_matches = re.findall(func_pattern, stack_trace)
        if func_matches:
            location.function_name = func_matches[0]

        return location

    def _generate_risk_summary(self, result: DefectGradingResult) -> Dict[str, Any]:
        """生成风险摘要

        Args:
            result: 缺陷分级结果

        Returns:
            Dict[str, Any]: 风险摘要
        """
        critical_count = len(result.get_critical_defects())
        high_priority_count = len(result.get_high_priority_defects())

        total_risk = sum(d.risk_assessment.get('risk_score', 0) for d in result.defects)
        avg_risk = total_risk / len(result.defects) if result.defects else 0

        risk_level = "low"
        if critical_count > 0 or avg_risk >= 80:
            risk_level = "critical"
        elif high_priority_count > 0 or avg_risk >= 60:
            risk_level = "high"
        elif avg_risk >= 30:
            risk_level = "medium"

        return {
            "overall_risk_level": risk_level,
            "critical_defects": critical_count,
            "high_priority_defects": high_priority_count,
            "average_risk_score": round(avg_risk, 2),
            "total_defects": len(result.defects),
            "recommendation": self._get_risk_recommendation(risk_level)
        }

    def _get_risk_recommendation(self, risk_level: str) -> str:
        """获取风险建议

        Args:
            risk_level: 风险等级

        Returns:
            str: 建议文本
        """
        recommendations = {
            "critical": "存在关键缺陷，建议立即停止发布并进行修复",
            "high": "存在高风险缺陷，建议优先修复后再发布",
            "medium": "存在中等风险，建议评估后决定是否发布",
            "low": "风险可控，可以继续发布流程"
        }
        return recommendations.get(risk_level, "")

    def _generate_recommendations(self, result: DefectGradingResult) -> List[str]:
        """生成建议

        Args:
            result: 缺陷分级结果

        Returns:
            List[str]: 建议列表
        """
        recommendations = []

        critical = result.get_critical_defects()
        if critical:
            recommendations.append(f"发现{len(critical)}个关键缺陷，需要立即处理")

        blocker = result.defects_by_severity.get(DefectSeverity.BLOCKER, [])
        if blocker:
            recommendations.append(f"存在{len(blocker)}个阻塞性缺陷，测试流程无法继续")

        security_defects = result.defects_by_type.get(DefectType.SECURITY_VULNERABILITY, [])
        if security_defects:
            recommendations.append(f"发现{len(security_defects)}个安全漏洞，必须在发布前修复")

        performance_defects = result.defects_by_type.get(DefectType.PERFORMANCE_ISSUE, [])
        if performance_defects:
            recommendations.append(f"发现{len(performance_defects)}个性能问题，建议进行性能优化")

        logic_defects = result.defects_by_type.get(DefectType.LOGIC_ERROR, [])
        if logic_defects:
            recommendations.append(f"发现{len(logic_defects)}个逻辑错误，需要检查相关业务逻辑")

        open_count = sum(1 for d in result.defects if d.status == DefectStatus.OPEN)
        if open_count > 0:
            recommendations.append(f"仍有{open_count}个缺陷待处理，请尽快分配和修复")

        return recommendations

    def get_defects_by_filter(self, result: DefectGradingResult,
                            severity: DefectSeverity = None,
                            priority: DefectPriority = None,
                            defect_type: DefectType = None) -> List[Defect]:
        """根据过滤条件获取缺陷

        Args:
            result: 缺陷分级结果
            severity: 严重程度过滤
            priority: 优先级过滤
            defect_type: 缺陷类型过滤

        Returns:
            List[Defect]: 过滤后的缺陷列表
        """
        defects = result.defects

        if severity:
            defects = [d for d in defects if d.severity == severity]
        if priority:
            defects = [d for d in defects if d.priority == priority]
        if defect_type:
            defects = [d for d in defects if d.defect_type == defect_type]

        return defects

    def export_defect_report(self, result: DefectGradingResult,
                           format: str = "dict") -> Any:
        """导出缺陷报告

        Args:
            result: 缺陷分级结果
            format: 输出格式

        Returns:
            Any: 报告数据
        """
        if format == "dict":
            return result.to_dict()
        elif format == "summary":
            return {
                "total_defects": len(result.defects),
                "critical": len(result.get_critical_defects()),
                "risk_level": result.risk_summary.get("overall_risk_level", "unknown"),
                "recommendations": result.recommendations
            }
        else:
            return result.to_dict()
