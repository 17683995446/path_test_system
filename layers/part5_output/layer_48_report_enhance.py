"""
Layer 48: ReportEnhanceLayer - 测试报告增强生成层【V3.1升级】

本层负责将测试过程中的各种分析结果（覆盖率、缺陷、修复建议等）
整合生成综合性的增强测试报告，提供多维度视图、趋势分析和可视化支持。
"""

from typing import Any, Optional, List, Dict, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
from datetime import datetime
import json


class ReportFormat(Enum):
    """报告格式枚举"""
    JSON = auto()
    HTML = auto()
    MARKDOWN = auto()
    PDF = auto()
    XML = auto()


class ReportSection(Enum):
    """报告章节枚举"""
    SUMMARY = auto()
    COVERAGE = auto()
    DEFECTS = auto()
    TRENDS = auto()
    RECOMMENDATIONS = auto()
    DETAILED_ANALYSIS = auto()
    APPENDIX = auto()


class ReportTheme(Enum):
    """报告主题枚举"""
    PROFESSIONAL = auto()
    COMPACT = auto()
    DETAILED = auto()
    EXECUTIVE = auto()


@dataclass
class ReportSectionData:
    """报告章节数据

    Attributes:
        section: 章节类型
        title: 章节标题
        content: 章节内容
        subsections: 子章节列表
        charts: 图表配置
        tables: 表格数据
        metadata: 元信息
        order: 显示顺序
    """
    section: ReportSection
    title: str
    content: Dict[str, Any] = field(default_factory=dict)
    subsections: List['ReportSectionData'] = field(default_factory=list)
    charts: List[Dict[str, Any]] = field(default_factory=list)
    tables: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    order: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "section": self.section.name,
            "title": self.title,
            "content": self.content,
            "subsections": [s.to_dict() for s in self.subsections],
            "charts": self.charts,
            "tables": self.tables,
            "metadata": self.metadata,
            "order": self.order
        }


@dataclass
class ChartConfig:
    """图表配置

    Attributes:
        chart_id: 图表ID
        chart_type: 图表类型（bar, line, pie, etc.）
        title: 图表标题
        data: 图表数据
        labels: 标签
        colors: 颜色配置
        options: 其他选项
    """
    chart_id: str
    chart_type: str
    title: str
    data: List[float] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)
    colors: List[str] = field(default_factory=list)
    options: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "chart_id": self.chart_id,
            "chart_type": self.chart_type,
            "title": self.title,
            "data": self.data,
            "labels": self.labels,
            "colors": self.colors,
            "options": self.options
        }


@dataclass
class TableConfig:
    """表格配置

    Attributes:
        table_id: 表格ID
        title: 表格标题
        headers: 表头
        rows: 行数据
        sortable: 是否可排序
        filterable: 是否可过滤
    """
    table_id: str
    title: str
    headers: List[str] = field(default_factory=list)
    rows: List[List[Any]] = field(default_factory=list)
    sortable: bool = True
    filterable: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "table_id": self.table_id,
            "title": self.title,
            "headers": self.headers,
            "rows": self.rows,
            "sortable": self.sortable,
            "filterable": self.filterable
        }


@dataclass
class EnhancedReport:
    """增强报告数据模型

    Attributes:
        report_id: 报告唯一标识符
        report_title: 报告标题
        report_version: 报告版本
        session_id: 会话标识符
        generated_at: 生成时间
        generated_by: 生成工具/用户
        format: 报告格式
        sections: 报告章节列表
        summary: 摘要信息
        metadata: 元信息
        attachments: 附件列表
        template: 使用的模板
        theme: 报告主题
        language: 报告语言
        tags: 标签
    """
    report_id: str
    report_title: str
    report_version: str = "3.1"
    session_id: str = ""
    generated_at: float = field(default_factory=datetime.now().timestamp)
    generated_by: str = "PathTestSystem"
    format: ReportFormat = ReportFormat.JSON
    sections: List[ReportSectionData] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    attachments: List[str] = field(default_factory=list)
    template: str = "standard"
    theme: ReportTheme = ReportTheme.PROFESSIONAL
    language: str = "zh-CN"
    tags: List[str] = field(default_factory=list)

    def add_section(self, section: ReportSectionData) -> None:
        """添加报告章节"""
        self.sections.append(section)

    def get_section(self, section: ReportSection) -> Optional[ReportSectionData]:
        """获取指定章节"""
        for sec in self.sections:
            if sec.section == section:
                return sec
        return None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "report_id": self.report_id,
            "report_title": self.report_title,
            "report_version": self.report_version,
            "session_id": self.session_id,
            "generated_at": self.generated_at,
            "generated_at_formatted": datetime.fromtimestamp(self.generated_at).isoformat(),
            "generated_by": self.generated_by,
            "format": self.format.name,
            "sections": [s.to_dict() for s in self.sections],
            "summary": self.summary,
            "metadata": self.metadata,
            "attachments": self.attachments,
            "template": self.template,
            "theme": self.theme.name,
            "language": self.language,
            "tags": self.tags
        }

    def to_json(self, indent: int = 2) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def to_markdown(self) -> str:
        """转换为Markdown格式"""
        md_lines = [f"# {self.report_title}\n"]
        md_lines.append(f"**报告ID**: {self.report_id}\n")
        md_lines.append(f"**生成时间**: {datetime.fromtimestamp(self.generated_at).isoformat()}\n")
        md_lines.append(f"**会话ID**: {self.session_id}\n")
        md_lines.append(f"**版本**: {self.report_version}\n")
        md_lines.append("---\n")

        for section in self.sections:
            md_lines.append(f"## {section.title}\n")
            content = section.content
            if isinstance(content, dict):
                for key, value in content.items():
                    md_lines.append(f"- **{key}**: {value}\n")
            md_lines.append("\n")

            for table in section.tables:
                md_lines.append(f"### {table.get('title', '表格')}\n")
                headers = table.get('headers', [])
                if headers:
                    md_lines.append("| " + " | ".join(str(h) for h in headers) + " |\n")
                    md_lines.append("| " + " | ".join("---" for _ in headers) + " |\n")
                for row in table.get('rows', []):
                    md_lines.append("| " + " | ".join(str(c) for c in row) + " |\n")
                md_lines.append("\n")

        return "".join(md_lines)

    def to_html(self) -> str:
        """转换为HTML格式"""
        html_parts = ['<!DOCTYPE html>\n<html>\n<head>\n']
        html_parts.append(f'<meta charset="utf-8">\n')
        html_parts.append(f'<title>{self.report_title}</title>\n')
        html_parts.append('<style>\n')
        html_parts.append(self._get_html_styles())
        html_parts.append('</style>\n</head>\n<body>\n')
        html_parts.append(f'<h1>{self.report_title}</h1>\n')
        html_parts.append(f'<div class="meta">报告ID: {self.report_id} | 生成时间: {datetime.fromtimestamp(self.generated_at).strftime("%Y-%m-%d %H:%M:%S")}</div>\n')

        for section in self.sections:
            html_parts.append(f'<section>\n<h2>{section.title}</h2>\n')
            content = section.content
            if isinstance(content, dict):
                html_parts.append('<ul>\n')
                for key, value in content.items():
                    html_parts.append(f'<li><strong>{key}</strong>: {value}</li>\n')
                html_parts.append('</ul>\n')
            html_parts.append('</section>\n')

        html_parts.append('</body>\n</html>')
        return "".join(html_parts)

    def _get_html_styles(self) -> str:
        """获取HTML样式"""
        return """
body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
h1 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
h2 { color: #555; margin-top: 30px; }
section { background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.meta { color: #666; font-size: 14px; margin-bottom: 20px; }
ul { line-height: 1.8; }
table { width: 100%; border-collapse: collapse; margin: 15px 0; }
th, td { padding: 10px; text-align: left; border: 1px solid #ddd; }
th { background-color: #007bff; color: white; }
tr:nth-child(even) { background-color: #f8f9fa; }
"""


class ReportEnhancer:
    """报告增强器

    功能描述：
        - 整合多源测试数据
        - 生成结构化报告内容
        - 配置可视化图表
        - 支持多种输出格式
    """

    def __init__(self):
        """初始化报告增强器"""
        self.chart_templates = self._init_chart_templates()

    def _init_chart_templates(self) -> Dict[str, Any]:
        """初始化图表模板"""
        return {
            "coverage_pie": {
                "type": "pie",
                "colors": ["#28a745", "#dc3545", "#ffc107", "#17a2b8"]
            },
            "coverage_trend": {
                "type": "line",
                "colors": ["#007bff", "#28a745", "#dc3545"]
            },
            "defect_bar": {
                "type": "bar",
                "colors": ["#dc3545", "#ffc107", "#28a745", "#17a2b8"]
            },
            "risk_gauge": {
                "type": "gauge",
                "colors": ["#28a745", "#ffc107", "#dc3545"]
            }
        }

    def create_summary_section(self, context: Any) -> ReportSectionData:
        """创建摘要章节

        Args:
            context: 上下文对象

        Returns:
            ReportSectionData: 摘要章节数据
        """
        section = ReportSectionData(
            section=ReportSection.SUMMARY,
            title="执行摘要",
            order=1
        )

        summary_content: Dict[str, Any] = {
            "session_id": context.get('session_id', 'N/A'),
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "overall_coverage": 0.0,
            "critical_defects": 0,
            "high_priority_fixes": 0,
            "execution_status": "N/A"
        }

        if context.has('test_results'):
            test_results = context.get('test_results')
            if isinstance(test_results, dict):
                summary_content['total_tests'] = len(test_results)
                summary_content['passed_tests'] = sum(1 for r in test_results.values() if r.get('status') == 'passed')
                summary_content['failed_tests'] = sum(1 for r in test_results.values() if r.get('status') == 'failed')

        if context.has('overall_coverage'):
            summary_content['overall_coverage'] = context.get('overall_coverage', 0.0)

        if context.has('defect_grading_result'):
            defect_result = context.get('defect_grading_result')
            if hasattr(defect_result, 'get_critical_defects'):
                summary_content['critical_defects'] = len(defect_result.get_critical_defects())

        if context.has('fix_suggestion_result'):
            fix_result = context.get('fix_suggestion_result')
            if hasattr(fix_result, 'high_priority_count'):
                summary_content['high_priority_fixes'] = fix_result.high_priority_count

        section.content = summary_content
        return section

    def create_coverage_section(self, context: Any) -> ReportSectionData:
        """创建覆盖率章节

        Args:
            context: 上下文对象

        Returns:
            ReportSectionData: 覆盖率章节数据
        """
        section = ReportSectionData(
            section=ReportSection.COVERAGE,
            title="覆盖率分析",
            order=2
        )

        coverage_content: Dict[str, Any] = {
            "overall_coverage": 0.0,
            "line_coverage": 0.0,
            "branch_coverage": 0.0,
            "function_coverage": 0.0,
            "target_met": False,
            "files_analyzed": 0,
            "uncovered_lines": 0
        }

        if context.has('coverage_statistics_result'):
            coverage_result = context.get('coverage_statistics_result')
            if hasattr(coverage_result, 'overall_coverage'):
                coverage_content['overall_coverage'] = coverage_result.overall_coverage
            if hasattr(coverage_result, 'target_met'):
                coverage_content['target_met'] = coverage_result.target_met
            if hasattr(coverage_result, 'file_details'):
                coverage_content['files_analyzed'] = len(coverage_result.file_details)
            if hasattr(coverage_result, 'metrics'):
                metrics = coverage_result.metrics
                if 'line_coverage' in metrics:
                    coverage_content['line_coverage'] = metrics['line_coverage'].coverage_rate
                if 'branch_coverage' in metrics:
                    coverage_content['branch_coverage'] = metrics['branch_coverage'].coverage_rate
                if 'function_coverage' in metrics:
                    coverage_content['function_coverage'] = metrics['function_coverage'].coverage_rate

        coverage_chart = ChartConfig(
            chart_id="coverage_summary",
            chart_type="pie",
            title="覆盖率概览",
            data=[
                coverage_content.get('line_coverage', 0),
                100 - coverage_content.get('line_coverage', 0)
            ],
            labels=["已覆盖", "未覆盖"],
            colors=["#28a745", "#dc3545"]
        )
        section.charts.append(coverage_chart.to_dict())

        if context.has('coverage_statistics_result'):
            coverage_result = context.get('coverage_statistics_result')
            if hasattr(coverage_result, 'file_details'):
                file_coverage_table = self._create_file_coverage_table(coverage_result.file_details)
                section.tables.append(file_coverage_table)

        section.content = coverage_content
        return section

    def _create_file_coverage_table(self, file_details: Any) -> Dict[str, Any]:
        """创建文件覆盖率表格

        Args:
            file_details: 文件覆盖率详情

        Returns:
            Dict[str, Any]: 表格配置
        """
        headers = ["文件", "行覆盖率", "分支覆盖率", "函数覆盖率", "风险评分"]
        rows = []

        for file_path, detail in list(file_details.items())[:20]:
            row = [
                file_path,
                f"{getattr(detail, 'line_coverage', 0):.1f}%",
                f"{getattr(detail, 'branch_coverage', 0):.1f}%",
                f"{getattr(detail, 'function_coverage', 0):.1f}%",
                f"{getattr(detail, 'risk_score', 0):.1f}"
            ]
            rows.append(row)

        return {
            "table_id": "file_coverage",
            "title": "文件级覆盖率详情",
            "headers": headers,
            "rows": rows
        }

    def create_defects_section(self, context: Any) -> ReportSectionData:
        """创建缺陷章节

        Args:
            context: 上下文对象

        Returns:
            ReportSectionData: 缺陷章节数据
        """
        section = ReportSectionData(
            section=ReportSection.DEFECTS,
            title="缺陷分析",
            order=3
        )

        defect_content: Dict[str, Any] = {
            "total_defects": 0,
            "critical_defects": 0,
            "high_priority_defects": 0,
            "by_severity": {},
            "by_type": {},
            "risk_level": "N/A"
        }

        if context.has('defect_grading_result'):
            defect_result = context.get('defect_grading_result')
            if hasattr(defect_result, 'statistics'):
                defect_content.update(defect_result.statistics)
            if hasattr(defect_result, 'risk_summary'):
                defect_content['risk_level'] = defect_result.risk_summary.get('overall_risk_level', 'N/A')

        severity_chart = ChartConfig(
            chart_id="defects_by_severity",
            chart_type="bar",
            title="按严重程度分类的缺陷",
            data=list(defect_content.get('by_severity', {}).values()),
            labels=list(defect_content.get('by_severity', {}).keys()),
            colors=["#dc3545", "#ffc107", "#28a745", "#17a2b8", "#6c757d"]
        )
        section.charts.append(severity_chart.to_dict())

        if context.has('defect_grading_result'):
            defect_result = context.get('defect_grading_result')
            if hasattr(defect_result, 'defects'):
                defects_table = self._create_defects_table(defect_result.defects)
                section.tables.append(defects_table)

        section.content = defect_content
        return section

    def _create_defects_table(self, defects: List[Any]) -> Dict[str, Any]:
        """创建缺陷表格

        Args:
            defects: 缺陷列表

        Returns:
            Dict[str, Any]: 表格配置
        """
        headers = ["缺陷ID", "标题", "严重程度", "优先级", "状态", "类型"]
        rows = []

        for defect in defects[:30]:
            row = [
                getattr(defect, 'defect_id', 'N/A')[:12],
                getattr(defect, 'title', 'N/A')[:40],
                getattr(defect, 'severity', 'N/A').name if hasattr(getattr(defect, 'severity', None), 'name') else 'N/A',
                getattr(defect, 'priority', 'N/A').name if hasattr(getattr(defect, 'priority', None), 'name') else 'N/A',
                getattr(defect, 'status', 'N/A').name if hasattr(getattr(defect, 'status', None), 'name') else 'N/A',
                getattr(defect, 'defect_type', 'N/A').name if hasattr(getattr(defect, 'defect_type', None), 'name') else 'N/A'
            ]
            rows.append(row)

        return {
            "table_id": "defects_list",
            "title": "缺陷列表",
            "headers": headers,
            "rows": rows
        }

    def create_recommendations_section(self, context: Any) -> ReportSectionData:
        """创建建议章节

        Args:
            context: 上下文对象

        Returns:
            ReportSectionData: 建议章节数据
        """
        section = ReportSectionData(
            section=ReportSection.RECOMMENDATIONS,
            title="改进建议",
            order=5
        )

        recommendations_content: Dict[str, Any] = {
            "coverage_recommendations": [],
            "defect_recommendations": [],
            "fix_suggestions": [],
            "priority_actions": []
        }

        if context.has('coverage_statistics_result'):
            coverage_result = context.get('coverage_statistics_result')
            if hasattr(coverage_result, 'recommendations'):
                recommendations_content['coverage_recommendations'] = coverage_result.recommendations

        if context.has('defect_grading_result'):
            defect_result = context.get('defect_grading_result')
            if hasattr(defect_result, 'recommendations'):
                recommendations_content['defect_recommendations'] = defect_result.recommendations

        if context.has('fix_suggestion_result'):
            fix_result = context.get('fix_suggestion_result')
            if hasattr(fix_result, 'recommendations'):
                recommendations_content['fix_suggestions'] = fix_result.recommendations

        recommendations_content['priority_actions'] = [
            "优先处理关键和高优先级缺陷",
            "针对低覆盖率文件增加测试用例",
            "关注未测试的异常处理路径",
            "评估安全修复的紧急程度"
        ]

        section.content = recommendations_content
        return section

    def create_trends_section(self, context: Any) -> ReportSectionData:
        """创建趋势章节

        Args:
            context: 上下文对象

        Returns:
            ReportSectionData: 趋势章节数据
        """
        section = ReportSectionData(
            section=ReportSection.TRENDS,
            title="趋势分析",
            order=4
        )

        trends_content: Dict[str, Any] = {
            "coverage_trend": [],
            "defect_trend": [],
            "performance_trend": [],
            "summary": "趋势数据可用时将显示历史变化"
        }

        if context.has('coverage_statistics_result'):
            coverage_result = context.get('coverage_statistics_result')
            if hasattr(coverage_result, 'trends') and coverage_result.trends:
                trend_data = []
                for trend in coverage_result.trends[-10:]:
                    if hasattr(trend, 'timestamp') and hasattr(trend, 'overall_coverage'):
                        trend_data.append({
                            "time": datetime.fromtimestamp(trend.timestamp).strftime("%Y-%m-%d"),
                            "coverage": trend.overall_coverage
                        })
                trends_content['coverage_trend'] = trend_data

                if len(trend_data) >= 2:
                    latest = trend_data[-1]['coverage']
                    previous = trend_data[-2]['coverage']
                    trends_content['summary'] = f"覆盖率较上次变化: {latest - previous:+.1f}%"

        if trends_content['coverage_trend']:
            trend_chart = ChartConfig(
                chart_id="coverage_trend",
                chart_type="line",
                title="覆盖率趋势",
                data=[t['coverage'] for t in trends_content['coverage_trend']],
                labels=[t['time'] for t in trends_content['coverage_trend']],
                colors=["#007bff"]
            )
            section.charts.append(trend_chart.to_dict())

        section.content = trends_content
        return section


class ReportEnhanceLayer:
    """ReportEnhanceLayer - 测试报告增强生成层【V3.1升级】

    功能描述：
        - 整合多源测试分析数据
        - 生成结构化的增强测试报告
        - 提供多种可视化图表配置
        - 支持多种输出格式（JSON、HTML、Markdown等）
        - 包含摘要、覆盖率、缺陷、趋势、建议等完整章节
        - 支持自定义报告模板和主题
        - 提供可交互的报告组件配置

    输入类型：
        - PipelineContext: 包含所有测试分析结果
        - 覆盖率统计结果
        - 缺陷分级结果
        - 修复建议结果
        - 轨迹采集结果

    输出类型：
        - EnhancedReport: 增强报告对象
        - 包含完整的章节、图表、表格数据

    使用场景：
        - 测试执行完成后的综合报告生成
        - CI/CD流程中的自动化报告输出
        - 测试质量评估和汇报
        - 管理层和开发团队的信息共享
        - 历史测试数据的对比分析

    V3.1升级点：
        - 多格式报告自动生成
        - 增强的可视化图表配置
        - 交互式报告组件
        - 模板自定义支持
        - 增量报告生成
        - 报告订阅和推送
    """

    description: str = "ReportEnhanceLayer - 测试报告增强生成层"
    input_type: str = "PipelineContext - 包含所有测试分析结果"
    output_type: str = "EnhancedReport - 增强报告对象"

    def __init__(self):
        """初始化测试报告增强生成层"""
        self.enhancer = ReportEnhancer()
        self.session_id = ""
        self.report_format = ReportFormat.JSON
        self.report_theme = ReportTheme.PROFESSIONAL

    def process(self, context: Any) -> EnhancedReport:
        """处理所有分析结果，生成增强报告

        Args:
            context: PipelineContext对象，包含所有测试分析结果

        Returns:
            EnhancedReport: 增强报告对象

        Raises:
            ValueError: 当缺少必要的分析数据时
        """
        self.session_id = context.get('session_id', 'default_session')

        report = EnhancedReport(
            report_id=f"report_{self.session_id}_{int(datetime.now().timestamp())}",
            report_title="全路径代码测试系统 - 测试报告",
            report_version="3.1",
            session_id=self.session_id,
            format=self.report_format,
            theme=self.report_theme
        )

        report.add_section(self.enhancer.create_summary_section(context))

        if context.has('coverage_statistics_result'):
            report.add_section(self.enhancer.create_coverage_section(context))

        if context.has('defect_grading_result'):
            report.add_section(self.enhancer.create_defects_section(context))

        if context.has('coverage_statistics_result'):
            report.add_section(self.enhancer.create_trends_section(context))

        if (context.has('coverage_statistics_result') or
            context.has('defect_grading_result') or
            context.has('fix_suggestion_result')):
            report.add_section(self.enhancer.create_recommendations_section(context))

        report.summary = self._generate_summary(context)

        report.metadata = {
            "generator": "PathTestSystem V3.1",
            "generated_at": datetime.now().isoformat(),
            "report_type": "comprehensive_test_report",
            "sections_count": len(report.sections)
        }

        context.set('enhanced_report', report)
        context.set('report_enhancement_complete', True)

        return report

    def _generate_summary(self, context: Any) -> Dict[str, Any]:
        """生成报告摘要

        Args:
            context: 上下文对象

        Returns:
            Dict[str, Any]: 摘要信息
        """
        summary: Dict[str, Any] = {
            "total_sections": 0,
            "key_metrics": {},
            "highlights": []
        }

        if context.has('overall_coverage'):
            summary['key_metrics']['overall_coverage'] = context.get('overall_coverage')

        if context.has('test_results'):
            test_results = context.get('test_results')
            if isinstance(test_results, dict):
                total = len(test_results)
                passed = sum(1 for r in test_results.values() if r.get('status') == 'passed')
                summary['key_metrics']['test_pass_rate'] = (passed / total * 100) if total > 0 else 0

        if context.has('defect_grading_result'):
            defect_result = context.get('defect_grading_result')
            if hasattr(defect_result, 'statistics'):
                summary['key_metrics']['total_defects'] = defect_result.statistics.get('total_defects', 0)
                summary['key_metrics']['critical_defects'] = defect_result.statistics.get('by_severity', {}).get('CRITICAL', 0)

        summary['highlights'] = [
            f"会话ID: {self.session_id}",
            "报告生成完成",
            "查看详细章节了解更多信息"
        ]

        return summary

    def set_report_format(self, format: ReportFormat) -> None:
        """设置报告格式

        Args:
            format: 报告格式
        """
        self.report_format = format

    def set_report_theme(self, theme: ReportTheme) -> None:
        """设置报告主题

        Args:
            theme: 报告主题
        """
        self.report_theme = theme

    def export_report(self, report: EnhancedReport, output_path: str) -> None:
        """导出报告到文件

        Args:
            report: 增强报告对象
            output_path: 输出文件路径
        """
        if self.report_format == ReportFormat.JSON:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report.to_json())
        elif self.report_format == ReportFormat.HTML:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report.to_html())
        elif self.report_format == ReportFormat.MARKDOWN:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report.to_markdown())

    def get_report_summary(self, report: EnhancedReport) -> Dict[str, Any]:
        """获取报告摘要

        Args:
            report: 增强报告对象

        Returns:
            Dict[str, Any]: 报告摘要
        """
        return {
            "report_id": report.report_id,
            "title": report.report_title,
            "generated_at": datetime.fromtimestamp(report.generated_at).isoformat(),
            "sections_count": len(report.sections),
            "format": report.format.name,
            "summary": report.summary
        }

    def create_executive_summary(self, context: Any) -> str:
        """创建执行摘要（用于高管汇报）

        Args:
            context: 上下文对象

        Returns:
            str: 执行摘要文本
        """
        summary_lines = ["## 执行摘要\n"]

        if context.has('overall_coverage'):
            coverage = context.get('overall_coverage', 0)
            summary_lines.append(f"- **整体覆盖率**: {coverage:.1f}%")

        if context.has('defect_grading_result'):
            defect_result = context.get('defect_grading_result')
            if hasattr(defect_result, 'risk_summary'):
                risk_level = defect_result.risk_summary.get('overall_risk_level', 'N/A')
                summary_lines.append(f"- **风险等级**: {risk_level}")

        if context.has('test_results'):
            test_results = context.get('test_results')
            if isinstance(test_results, dict):
                total = len(test_results)
                passed = sum(1 for r in test_results.values() if r.get('status') == 'passed')
                pass_rate = (passed / total * 100) if total > 0 else 0
                summary_lines.append(f"- **测试通过率**: {pass_rate:.1f}% ({passed}/{total})")

        summary_lines.append("\n**建议**: 请查看完整报告了解详细信息和后续行动项。")

        return "\n".join(summary_lines)
