"""
ResultAggregationOutputLayers - 结果聚合与输出层 (31-40)
=====================================================

第五部分：结果聚合与反馈优化
- 第31层：结果聚合
- 第32层：报告生成
- 第33层：数据可视化
- 第34层：反馈收集
- 第35层：性能评估
- 第36层：优化建议
- 第37层：配置更新
- 第38层：系统监控
- 第39层：日志记录
- 第40层：完成确认

作者：PathTestSystem
版本：1.0.0
"""

import os
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from collections import defaultdict


class AggregationType(Enum):
    """聚合类型"""
    BY_FILE = "by_file"
    BY_FUNCTION = "by_function"
    BY_CLASS = "by_class"
    BY_MODULE = "by_module"
    BY_TIME = "by_time"


class ReportFormat(Enum):
    """报告格式"""
    JSON = "json"
    HTML = "html"
    MARKDOWN = "markdown"
    TEXT = "text"


@dataclass
class AggregationResult:
    """聚合结果"""
    result_id: str
    aggregation_type: AggregationType
    total_items: int
    grouped_data: Dict[str, Any] = field(default_factory=dict)
    statistics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestReport:
    """测试报告"""
    report_id: str
    title: str
    summary: Dict[str, Any] = field(default_factory=dict)
    details: List[Dict[str, Any]] = field(default_factory=list)
    charts: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    duration: float = 0.0


@dataclass
class FeedbackData:
    """反馈数据"""
    feedback_id: str
    feedback_type: str
    content: Dict[str, Any]
    source: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    priority: int = 1
    status: str = "pending"


@dataclass
class PerformanceMetrics:
    """性能指标"""
    metric_name: str
    value: float
    unit: str
    timestamp: float
    category: str = "general"


class ResultAggregator:
    """
    结果聚合器
    ==========
    
    聚合测试和分析结果
    """
    
    def __init__(self):
        self.results: List[Dict] = []
        self.aggregations: Dict[AggregationType, AggregationResult] = {}
    
    def add_result(self, result: Dict):
        """
        添加结果
        
        Args:
            result: 结果字典
        """
        self.results.append(result)
    
    def add_results(self, results: List[Dict]):
        """
        批量添加结果
        
        Args:
            results: 结果列表
        """
        self.results.extend(results)
    
    def aggregate_by_file(self) -> AggregationResult:
        """按文件聚合"""
        grouped = defaultdict(list)
        
        for result in self.results:
            file_path = result.get('file_path', 'unknown')
            grouped[file_path].append(result)
        
        statistics = {
            'total_files': len(grouped),
            'total_results': len(self.results),
            'files_with_issues': sum(1 for items in grouped.values() if any(r.get('has_issue') for r in items))
        }
        
        return AggregationResult(
            result_id=f"agg_file_{int(time.time())}",
            aggregation_type=AggregationType.BY_FILE,
            total_items=len(grouped),
            grouped_data=dict(grouped),
            statistics=statistics
        )
    
    def aggregate_by_function(self) -> AggregationResult:
        """按函数聚合"""
        grouped = defaultdict(list)
        
        for result in self.results:
            function_name = result.get('function_name', 'unknown')
            grouped[function_name].append(result)
        
        statistics = {
            'total_functions': len(grouped),
            'total_results': len(self.results),
            'functions_with_tests': sum(1 for items in grouped.values() if items)
        }
        
        return AggregationResult(
            result_id=f"agg_func_{int(time.time())}",
            aggregation_type=AggregationType.BY_FUNCTION,
            total_items=len(grouped),
            grouped_data=dict(grouped),
            statistics=statistics
        )
    
    def aggregate_by_time(self, interval: str = "hour") -> AggregationResult:
        """按时序聚合"""
        grouped = defaultdict(list)
        
        for result in self.results:
            timestamp = result.get('timestamp', time.time())
            
            if isinstance(timestamp, (int, float)):
                dt = datetime.fromtimestamp(timestamp)
                if interval == "hour":
                    key = dt.strftime("%Y-%m-%d %H:00")
                elif interval == "day":
                    key = dt.strftime("%Y-%m-%d")
                elif interval == "week":
                    key = dt.strftime("%Y-W%U")
                else:
                    key = dt.isoformat()
            else:
                key = "unknown"
            
            grouped[key].append(result)
        
        statistics = {
            'total_intervals': len(grouped),
            'total_results': len(self.results)
        }
        
        return AggregationResult(
            result_id=f"agg_time_{int(time.time())}",
            aggregation_type=AggregationType.BY_TIME,
            total_items=len(grouped),
            grouped_data=dict(grouped),
            statistics=statistics
        )
    
    def aggregate_all(self) -> Dict[str, AggregationResult]:
        """聚合所有类型"""
        return {
            AggregationType.BY_FILE: self.aggregate_by_file(),
            AggregationType.BY_FUNCTION: self.aggregate_by_function(),
            AggregationType.BY_TIME: self.aggregate_by_time()
        }


class ReportGenerator:
    """
    报告生成器
    ==========
    
    生成各种格式的测试报告
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.report_template = self._init_template()
    
    def _init_template(self) -> Dict[str, str]:
        """初始化报告模板"""
        return {
            'summary': "测试执行摘要",
            'details': "详细结果",
            'recommendations': "改进建议"
        }
    
    def generate_summary(self, aggregated_results: Dict[str, AggregationResult]) -> Dict[str, Any]:
        """
        生成摘要
        
        Args:
            aggregated_results: 聚合结果
        
        Returns:
            摘要字典
        """
        summary = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'coverage_percentage': 0.0,
            'duration': 0.0
        }
        
        for agg_type, agg_result in aggregated_results.items():
            summary['total_tests'] += agg_result.total_items
        
        return summary
    
    def generate_json_report(self, report: TestReport) -> str:
        """
        生成JSON报告
        
        Args:
            report: 测试报告
        
        Returns:
            JSON字符串
        """
        return json.dumps({
            'report_id': report.report_id,
            'title': report.title,
            'summary': report.summary,
            'details': report.details,
            'recommendations': report.recommendations,
            'timestamp': report.timestamp,
            'duration': report.duration
        }, indent=2, ensure_ascii=False)
    
    def generate_markdown_report(self, report: TestReport) -> str:
        """
        生成Markdown报告
        
        Args:
            report: 测试报告
        
        Returns:
            Markdown字符串
        """
        md = f"# {report.title}\n\n"
        md += f"**生成时间**: {report.timestamp}\n\n"
        md += f"**执行时长**: {report.duration:.2f}秒\n\n"
        
        md += "## 摘要\n\n"
        for key, value in report.summary.items():
            md += f"- **{key}**: {value}\n"
        md += "\n"
        
        if report.details:
            md += "## 详细结果\n\n"
            for detail in report.details[:10]:
                md += f"- {detail}\n"
            if len(report.details) > 10:
                md += f"- ... 还有 {len(report.details) - 10} 条结果\n"
            md += "\n"
        
        if report.recommendations:
            md += "## 改进建议\n\n"
            for i, rec in enumerate(report.recommendations, 1):
                md += f"{i}. {rec}\n"
            md += "\n"
        
        return md
    
    def generate_html_report(self, report: TestReport) -> str:
        """
        生成HTML报告
        
        Args:
            report: 测试报告
        
        Returns:
            HTML字符串
        """
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{report.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #2196F3; color: white; padding: 20px; }}
        .summary {{ background: #f5f5f5; padding: 15px; margin: 20px 0; }}
        .detail {{ margin: 10px 0; padding: 10px; border-left: 3px solid #2196F3; }}
        .recommendation {{ background: #fff3cd; padding: 10px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{report.title}</h1>
        <p>生成时间: {report.timestamp}</p>
    </div>
    
    <div class="summary">
        <h2>摘要</h2>
        {''.join(f'<p><strong>{k}:</strong> {v}</p>' for k, v in report.summary.items())}
    </div>
    
    <h2>详细结果</h2>
    {''.join(f'<div class="detail">{d}</div>' for d in report.details[:20])}
    
    <h2>改进建议</h2>
    {''.join(f'<div class="recommendation">{i+1}. {r}</div>' for i, r in enumerate(report.recommendations))}
</body>
</html>"""
        
        return html
    
    def create_report(self, title: str, aggregated_results: Dict[str, AggregationResult],
                     details: Optional[List[Dict]] = None) -> TestReport:
        """
        创建完整报告
        
        Args:
            title: 报告标题
            aggregated_results: 聚合结果
            details: 详细结果
        
        Returns:
            TestReport对象
        """
        summary = self.generate_summary(aggregated_results)
        recommendations = self._generate_recommendations(summary)
        
        return TestReport(
            report_id=f"report_{int(time.time())}",
            title=title,
            summary=summary,
            details=details or [],
            recommendations=recommendations,
            duration=summary.get('duration', 0)
        )
    
    def _generate_recommendations(self, summary: Dict[str, Any]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if summary.get('failed', 0) > 0:
            recommendations.append(f"有 {summary['failed']} 个测试失败，建议优先修复失败的测试")
        
        coverage = summary.get('coverage_percentage', 0)
        if coverage < 80:
            recommendations.append(f"代码覆盖率仅为 {coverage:.1f}%，建议增加更多测试用例")
        
        if summary.get('skipped', 0) > summary.get('total_tests', 1) * 0.1:
            recommendations.append("跳过测试比例较高，建议检查测试环境配置")
        
        if not recommendations:
            recommendations.append("测试结果良好，继续保持!")
        
        return recommendations


class DataVisualizer:
    """
    数据可视化器
    ============
    
    生成图表数据
    """
    
    def __init__(self):
        self.chart_types = ['bar', 'line', 'pie', 'scatter', 'heatmap']
    
    def create_coverage_chart(self, coverage_data: Dict[str, float]) -> Dict[str, Any]:
        """
        创建覆盖率图表
        
        Args:
            coverage_data: 覆盖率数据
        
        Returns:
            图表数据
        """
        return {
            'type': 'bar',
            'title': '代码覆盖率',
            'data': {
                'labels': list(coverage_data.keys()),
                'datasets': [{
                    'label': '覆盖率 (%)',
                    'data': list(coverage_data.values())
                }]
            },
            'options': {
                'responsive': True,
                'scales': {
                    'y': {
                        'beginAtZero': True,
                        'max': 100
                    }
                }
            }
        }
    
    def create_performance_chart(self, metrics: List[PerformanceMetrics]) -> Dict[str, Any]:
        """
        创建性能图表
        
        Args:
            metrics: 性能指标
        
        Returns:
            图表数据
        """
        data_by_category = defaultdict(list)
        for metric in metrics:
            data_by_category[metric.category].append({
                'x': metric.timestamp,
                'y': metric.value
            })
        
        datasets = []
        for category, points in data_by_category.items():
            datasets.append({
                'label': category,
                'data': points
            })
        
        return {
            'type': 'line',
            'title': '性能趋势',
            'data': {
                'datasets': datasets
            },
            'options': {
                'responsive': True
            }
        }
    
    def create_test_results_pie(self, passed: int, failed: int, skipped: int) -> Dict[str, Any]:
        """
        创建测试结果饼图
        
        Args:
            passed: 通过数
            failed: 失败数
            skipped: 跳过数
        
        Returns:
            图表数据
        """
        return {
            'type': 'pie',
            'title': '测试结果分布',
            'data': {
                'labels': ['通过', '失败', '跳过'],
                'datasets': [{
                    'data': [passed, failed, skipped],
                    'backgroundColor': ['#4caf50', '#f44336', '#ffc107']
                }]
            }
        }


class FeedbackCollector:
    """
    反馈收集器
    ==========
    
    收集测试执行反馈
    """
    
    def __init__(self):
        self.feedback_list: List[FeedbackData] = []
    
    def collect_feedback(self, feedback_type: str, content: Dict[str, Any], 
                       source: str, priority: int = 1) -> FeedbackData:
        """
        收集反馈
        
        Args:
            feedback_type: 反馈类型
            content: 反馈内容
            source: 来源
            priority: 优先级
        
        Returns:
            FeedbackData对象
        """
        feedback = FeedbackData(
            feedback_id=f"fb_{int(time.time())}_{len(self.feedback_list)}",
            feedback_type=feedback_type,
            content=content,
            source=source,
            priority=priority
        )
        
        self.feedback_list.append(feedback)
        return feedback
    
    def get_pending_feedback(self) -> List[FeedbackData]:
        """获取待处理的反馈"""
        return [f for f in self.feedback_list if f.status == "pending"]
    
    def mark_processed(self, feedback_id: str):
        """标记反馈已处理"""
        for feedback in self.feedback_list:
            if feedback.feedback_id == feedback_id:
                feedback.status = "processed"
                break
    
    def get_high_priority_feedback(self) -> List[FeedbackData]:
        """获取高优先级反馈"""
        return sorted(
            [f for f in self.feedback_list if f.priority >= 4],
            key=lambda x: x.priority,
            reverse=True
        )


class PerformanceEvaluator:
    """
    性能评估器
    ==========
    
    评估测试性能
    """
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.baseline: Optional[Dict[str, float]] = None
    
    def add_metric(self, metric_name: str, value: float, unit: str, category: str = "general"):
        """
        添加指标
        
        Args:
            metric_name: 指标名称
            value: 值
            unit: 单位
            category: 类别
        """
        metric = PerformanceMetrics(
            metric_name=metric_name,
            value=value,
            unit=unit,
            timestamp=time.time(),
            category=category
        )
        self.metrics.append(metric)
    
    def set_baseline(self, baseline: Dict[str, float]):
        """
        设置基准线
        
        Args:
            baseline: 基准数据
        """
        self.baseline = baseline
    
    def evaluate_performance(self) -> Dict[str, Any]:
        """
        评估性能
        
        Returns:
            评估结果
        """
        if not self.metrics:
            return {'status': 'no_data'}
        
        metrics_by_name = defaultdict(list)
        for metric in self.metrics:
            metrics_by_name[metric.metric_name].append(metric)
        
        evaluation = {
            'total_metrics': len(self.metrics),
            'categories': {},
            'trends': {}
        }
        
        for name, metric_list in metrics_by_name.items():
            values = [m.value for m in metric_list]
            avg_value = sum(values) / len(values) if values else 0
            
            evaluation['categories'][name] = {
                'average': avg_value,
                'min': min(values) if values else 0,
                'max': max(values) if values else 0,
                'count': len(values)
            }
            
            if self.baseline and name in self.baseline:
                baseline_value = self.baseline[name]
                change_percent = ((avg_value - baseline_value) / baseline_value * 100) if baseline_value != 0 else 0
                evaluation['trends'][name] = {
                    'baseline': baseline_value,
                    'current': avg_value,
                    'change_percent': change_percent
                }
        
        return evaluation


class OptimizationAdvisor:
    """
    优化建议器
    ==========
    
    生成优化建议
    """
    
    def __init__(self):
        self.rules: List[Dict] = self._init_rules()
    
    def _init_rules(self) -> List[Dict]:
        """初始化规则"""
        return [
            {
                'condition': lambda eval_data: eval_data.get('categories', {}).get('coverage', {}).get('average', 0) < 80,
                'suggestion': '增加测试覆盖率到80%以上'
            },
            {
                'condition': lambda eval_data: eval_data.get('categories', {}).get('execution_time', {}).get('average', 0) > 60,
                'suggestion': '优化测试执行时间，减少不必要的等待'
            },
            {
                'condition': lambda eval_data: eval_data.get('categories', {}).get('memory', {}).get('average', 0) > 500,
                'suggestion': '优化内存使用，考虑使用流式处理'
            }
        ]
    
    def generate_suggestions(self, evaluation: Dict[str, Any]) -> List[str]:
        """
        生成建议
        
        Args:
            evaluation: 评估结果
        
        Returns:
            建议列表
        """
        suggestions = []
        
        for rule in self.rules:
            if rule['condition'](evaluation):
                suggestions.append(rule['suggestion'])
        
        if not suggestions:
            suggestions.append('当前性能良好，继续保持')
        
        return suggestions


class ConfigurationUpdater:
    """
    配置更新器
    ==========
    
    更新系统配置
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config.json"
        self.config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self):
        """加载配置"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
            except Exception:
                self.config = {}
    
    def save_config(self):
        """保存配置"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception:
            pass
    
    def update_config(self, key: str, value: Any):
        """
        更新配置
        
        Args:
            key: 配置键
            value: 配置值
        """
        self.config[key] = value
        self.save_config()
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        获取配置
        
        Args:
            key: 配置键
            default: 默认值
        
        Returns:
            配置值
        """
        return self.config.get(key, default)


class SystemMonitor:
    """
    系统监控器
    ==========
    
    监控系统状态
    """
    
    def __init__(self):
        self.start_time = time.time()
        self.checkpoints: List[Dict] = []
        self.alerts: List[Dict] = []
    
    def add_checkpoint(self, name: str, data: Optional[Dict] = None):
        """
        添加检查点
        
        Args:
            name: 检查点名称
            data: 相关数据
        """
        checkpoint = {
            'name': name,
            'timestamp': time.time(),
            'elapsed': time.time() - self.start_time,
            'data': data or {}
        }
        self.checkpoints.append(checkpoint)
    
    def add_alert(self, alert_type: str, message: str, severity: str = "info"):
        """
        添加告警
        
        Args:
            alert_type: 告警类型
            message: 告警消息
            severity: 严重程度
        """
        alert = {
            'type': alert_type,
            'message': message,
            'severity': severity,
            'timestamp': time.time()
        }
        self.alerts.append(alert)
    
    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        return {
            'uptime': time.time() - self.start_time,
            'checkpoints': len(self.checkpoints),
            'alerts': len(self.alerts),
            'recent_alerts': self.alerts[-10:] if self.alerts else []
        }


class Logger:
    """
    日志记录器
    ==========
    
    记录系统日志
    """
    
    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file or "execution.log"
        self.entries: List[Dict] = []
    
    def log(self, level: str, message: str, data: Optional[Dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别
            message: 日志消息
            data: 附加数据
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'data': data or {}
        }
        
        self.entries.append(entry)
        
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception:
            pass
    
    def get_recent_logs(self, count: int = 100) -> List[Dict]:
        """获取最近日志"""
        return self.entries[-count:]


class CompletionConfirmator:
    """
    完成确认器
    ==========
    
    确认任务完成
    """
    
    def __init__(self):
        self.completion_status = 'pending'
        self.completion_time: Optional[float] = None
        self.completion_details: Dict[str, Any] = {}
    
    def confirm_completion(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """
        确认完成
        
        Args:
            details: 完成详情
        
        Returns:
            完成状态
        """
        self.completion_status = 'completed'
        self.completion_time = time.time()
        self.completion_details = details
        
        return {
            'status': 'completed',
            'completed_at': datetime.now().fromtimestamp(self.completion_time).isoformat(),
            'details': details
        }
    
    def get_completion_report(self) -> Dict[str, Any]:
        """获取完成报告"""
        return {
            'status': self.completion_status,
            'completed_at': self.completion_time,
            'details': self.completion_details
        }


class ResultOutputController:
    """
    结果输出控制器 - 主控制器
    =========================
    
    整合所有结果聚合和输出功能
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        self.aggregator = ResultAggregator()
        self.report_generator = ReportGenerator(self.config)
        self.visualizer = DataVisualizer()
        self.feedback_collector = FeedbackCollector()
        self.performance_evaluator = PerformanceEvaluator()
        self.optimization_advisor = OptimizationAdvisor()
        self.config_updater = ConfigurationUpdater()
        self.system_monitor = SystemMonitor()
        self.logger = Logger()
        self.completion_confirmator = CompletionConfirmator()
    
    def process_and_output(self, results: List[Dict], title: str = "Test Report") -> TestReport:
        """
        处理并输出结果
        
        Args:
            results: 结果列表
            title: 报告标题
        
        Returns:
            测试报告
        """
        self.system_monitor.add_checkpoint('start_processing')
        
        for result in results:
            self.aggregator.add_result(result)
        
        aggregated = self.aggregator.aggregate_all()
        
        report = self.report_generator.create_report(title, aggregated, results)
        
        self.feedback_collector.collect_feedback(
            feedback_type='report_generated',
            content=report.summary,
            source='system',
            priority=2
        )
        
        evaluation = self.performance_evaluator.evaluate_performance()
        
        if evaluation:
            suggestions = self.optimization_advisor.generate_suggestions(evaluation)
            report.recommendations.extend(suggestions)
        
        self.system_monitor.add_checkpoint('processing_complete')
        
        self.logger.log('info', f'Report generated: {report.report_id}')
        
        return report
    
    def finalize(self) -> Dict[str, Any]:
        """最终化处理"""
        completion = self.completion_confirmator.confirm_completion({
            'status': 'success',
            'report_generated': True
        })
        
        return {
            'completion': completion,
            'monitor_status': self.system_monitor.get_status(),
            'logs': self.logger.get_recent_logs(10)
        }


def create_result_controller(config: Optional[Dict] = None) -> ResultOutputController:
    """
    创建结果输出控制器工厂函数
    
    Args:
        config: 配置字典
    
    Returns:
        ResultOutputController实例
    """
    return ResultOutputController(config)


if __name__ == "__main__":
    controller = create_result_controller()
    
    sample_results = [
        {'file_path': 'test1.py', 'passed': True, 'duration': 0.1},
        {'file_path': 'test2.py', 'passed': False, 'duration': 0.2},
        {'file_path': 'test3.py', 'passed': True, 'duration': 0.15}
    ]
    
    report = controller.process_and_output(sample_results, "Sample Test Report")
    
    print("报告生成完成:")
    print(f"  报告ID: {report.report_id}")
    print(f"  标题: {report.title}")
    print(f"  摘要: {report.summary}")
    print(f"  建议: {report.recommendations}")
    
    finalization = controller.finalize()
    print(f"  完成状态: {finalization['completion']['status']}")
