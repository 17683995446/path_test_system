"""
Layer 49: NLQueryLayer - 自然语言查询接口层

本层负责提供自然语言查询接口，使用户能够通过自然语言查询测试系统中的各种数据，
包括覆盖率信息、缺陷状态、测试结果等，无需了解底层数据结构和查询语法。
"""

from typing import Any, Optional, List, Dict, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
import re
from collections import defaultdict


class QueryType(Enum):
    """查询类型枚举"""
    COVERAGE_QUERY = auto()
    DEFECT_QUERY = auto()
    TEST_RESULT_QUERY = auto()
    TREND_QUERY = auto()
    FUNCTION_QUERY = auto()
    FILE_QUERY = auto()
    METADATA_QUERY = auto()
    COMPOSITE_QUERY = auto()
    UNKNOWN = auto()


class QueryIntent(Enum):
    """查询意图枚举"""
    GET = auto()
    FILTER = auto()
    COMPARE = auto()
    AGGREGATE = auto()
    RANK = auto()
    EXPLAIN = auto()
    RECOMMEND = auto()
    UNKNOWN = auto()


class TimeRange(Enum):
    """时间范围枚举"""
    TODAY = auto()
    THIS_WEEK = auto()
    THIS_MONTH = auto()
    LAST_WEEK = auto()
    LAST_MONTH = auto()
    ALL_TIME = auto()
    CUSTOM = auto()


@dataclass
class QueryParameter:
    """查询参数

    Attributes:
        param_name: 参数名称
        param_type: 参数类型
        param_value: 参数值
        operator: 操作符
        description: 参数描述
    """
    param_name: str
    param_type: str
    param_value: Any = None
    operator: str = "="
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "param_name": self.param_name,
            "param_type": self.param_type,
            "param_value": self.param_value,
            "operator": self.operator,
            "description": self.description
        }


@dataclass
class ParsedQuery:
    """解析后的查询

    Attributes:
        original_query: 原始查询文本
        query_type: 查询类型
        intent: 查询意图
        parameters: 查询参数列表
        entities: 识别的实体列表
        conditions: 过滤条件
        aggregations: 聚合操作
        time_range: 时间范围
        limit: 返回数量限制
        offset: 偏移量
        sort_by: 排序字段
        sort_order: 排序方向
        confidence: 解析置信度
        alternative_queries: 替代查询建议
    """
    original_query: str
    query_type: QueryType = QueryType.UNKNOWN
    intent: QueryIntent = QueryIntent.GET
    parameters: List[QueryParameter] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    aggregations: List[str] = field(default_factory=list)
    time_range: Optional[TimeRange] = None
    limit: int = 10
    offset: int = 0
    sort_by: str = ""
    sort_order: str = "desc"
    confidence: float = 0.0
    alternative_queries: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "original_query": self.original_query,
            "query_type": self.query_type.name,
            "intent": self.intent.name,
            "parameters": [p.to_dict() for p in self.parameters],
            "entities": self.entities,
            "conditions": self.conditions,
            "aggregations": self.aggregations,
            "time_range": self.time_range.name if self.time_range else None,
            "limit": self.limit,
            "offset": self.offset,
            "sort_by": self.sort_by,
            "sort_order": self.sort_order,
            "confidence": self.confidence,
            "alternative_queries": self.alternative_queries
        }


@dataclass
class QueryResult:
    """查询结果

    Attributes:
        query: 解析后的查询
        results: 查询结果数据
        total_count: 总结果数
        page_info: 分页信息
        formatted_results: 格式化后的结果
        summary: 结果摘要
        suggestions: 后续建议
        execution_time: 执行时间
        metadata: 其他元信息
    """
    query: ParsedQuery
    results: List[Dict[str, Any]] = field(default_factory=list)
    total_count: int = 0
    page_info: Dict[str, Any] = field(default_factory=dict)
    formatted_results: str = ""
    summary: Dict[str, Any] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "query": self.query.to_dict(),
            "results": self.results,
            "total_count": self.total_count,
            "page_info": self.page_info,
            "formatted_results": self.formatted_results,
            "summary": self.summary,
            "suggestions": self.suggestions,
            "execution_time": self.execution_time,
            "metadata": self.metadata
        }

    def to_natural_language(self) -> str:
        """转换为自然语言描述

        Returns:
            str: 自然语言描述
        """
        lines = [f"查询结果（共{self.total_count}条）：\n"]

        for i, result in enumerate(self.results[:5], 1):
            if isinstance(result, dict):
                lines.append(f"{i}. {self._format_result_item(result)}")
            else:
                lines.append(f"{i}. {result}")

        if self.total_count > 5:
            lines.append(f"\n... 还有 {self.total_count - 5} 条结果")

        if self.summary:
            lines.append("\n摘要：")
            for key, value in self.summary.items():
                lines.append(f"- {key}: {value}")

        return "\n".join(lines)

    def _format_result_item(self, result: Dict[str, Any]) -> str:
        """格式化单个结果项"""
        parts = []
        for key, value in list(result.items())[:3]:
            if not isinstance(value, (dict, list)):
                parts.append(f"{key}={value}")
        return ", ".join(parts) if parts else str(result)


class NLQueryParser:
    """自然语言查询解析器

    功能描述：
        - 解析自然语言查询文本
        - 识别查询意图和类型
        - 提取查询参数和条件
        - 处理模糊查询和同义词
        - 生成结构化查询表示
    """

    def __init__(self):
        """初始化自然语言查询解析器"""
        self.intent_keywords = self._init_intent_keywords()
        self.type_keywords = self._init_type_keywords()
        self.entity_patterns = self._init_entity_patterns()
        self.operator_mappings = self._init_operator_mappings()

    def _init_intent_keywords(self) -> Dict[QueryIntent, List[str]]:
        """初始化意图关键词"""
        return {
            QueryIntent.GET: ["查询", "获取", "查看", "显示", "列出", "show", "get", "list", "find", "search"],
            QueryIntent.FILTER: ["过滤", "筛选", "条件", "where", "filter", "with", "between"],
            QueryIntent.COMPARE: ["比较", "对比", "差异", "compare", "versus", "vs"],
            QueryIntent.AGGREGATE: ["统计", "汇总", "总数", "平均", "sum", "count", "average", "total"],
            QueryIntent.RANK: ["排名", "排序", "top", "rank", "order", "sort"],
            QueryIntent.EXPLAIN: ["解释", "说明", "原因", "why", "explain", "reason"],
            QueryIntent.RECOMMEND: ["建议", "推荐", "最佳", "recommend", "suggest", "best"]
        }

    def _init_type_keywords(self) -> Dict[QueryType, List[str]]:
        """初始化类型关键词"""
        return {
            QueryType.COVERAGE_QUERY: ["覆盖率", "coverage", "lines", "branches", "functions"],
            QueryType.DEFECT_QUERY: ["缺陷", "bug", "问题", "issue", "defect", "error"],
            QueryType.TEST_RESULT_QUERY: ["测试", "test", "result", "pass", "fail", "通过", "失败"],
            QueryType.TREND_QUERY: ["趋势", "历史", "变化", "trend", "history", "change"],
            QueryType.FUNCTION_QUERY: ["函数", "function", "method", "api"],
            QueryType.FILE_QUERY: ["文件", "file", "module", "class"],
            QueryType.METADATA_QUERY: ["元数据", "metadata", "info", "信息"]
        }

    def _init_entity_patterns(self) -> Dict[str, str]:
        """初始化实体模式"""
        return {
            "file": r"[\w/\\]+\.\w+",
            "function": r"[\w_]+\([\w, ]*\)",
            "line_range": r"\d+-\d+",
            "number": r"\d+",
            "percentage": r"\d+%"
        }

    def _init_operator_mappings(self) -> Dict[str, str]:
        """初始化操作符映射"""
        return {
            "大于": ">",
            "小于": "<",
            "等于": "=",
            "不等于": "!=",
            "大于等于": ">=",
            "小于等于": "<=",
            "包含": "contains",
            "在...之间": "between",
            "高于": ">",
            "低于": "<"
        }

    def parse(self, query_text: str) -> ParsedQuery:
        """解析自然语言查询

        Args:
            query_text: 自然语言查询文本

        Returns:
            ParsedQuery: 解析后的查询对象
        """
        query = ParsedQuery(original_query=query_text)

        query.query_type = self._detect_query_type(query_text)
        query.intent = self._detect_intent(query_text)

        query.entities = self._extract_entities(query_text)
        query.conditions = self._extract_conditions(query_text)

        query.parameters = self._extract_parameters(query_text, query.query_type)

        query.aggregations = self._extract_aggregations(query_text)

        query.time_range = self._detect_time_range(query_text)

        query.limit = self._extract_limit(query_text)

        query.sort_by, query.sort_order = self._extract_sort_info(query_text)

        query.confidence = self._calculate_confidence(query)

        query.alternative_queries = self._generate_alternatives(query_text)

        return query

    def _detect_query_type(self, query_text: str) -> QueryType:
        """检测查询类型"""
        query_lower = query_text.lower()

        type_scores: Dict[QueryType, int] = defaultdict(int)

        for qtype, keywords in self.type_keywords.items():
            for keyword in keywords:
                if keyword.lower() in query_lower:
                    type_scores[qtype] += 1

        if type_scores:
            return max(type_scores.items(), key=lambda x: x[1])[0]

        return QueryType.UNKNOWN

    def _detect_intent(self, query_text: str) -> QueryIntent:
        """检测查询意图"""
        query_lower = query_text.lower()

        intent_scores: Dict[QueryIntent, int] = defaultdict(int)

        for intent, keywords in self.intent_keywords.items():
            for keyword in keywords:
                if keyword.lower() in query_lower:
                    intent_scores[intent] += 1

        if intent_scores:
            return max(intent_scores.items(), key=lambda x: x[1])[0]

        return QueryIntent.UNKNOWN

    def _extract_entities(self, query_text: str) -> List[str]:
        """提取实体"""
        entities = []

        for pattern_name, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, query_text)
            entities.extend(matches)

        return list(set(entities))

    def _extract_conditions(self, query_text: str) -> Dict[str, Any]:
        """提取过滤条件"""
        conditions: Dict[str, Any] = {}

        number_pattern = r"(\w+)\s*(大于|小于|等于|高于|低于|>=|<=|>|<|=)\s*(\d+\.?\d*)"
        matches = re.findall(number_pattern, query_text)
        for field, operator, value in matches:
            conditions[field] = {
                "operator": self.operator_mappings.get(operator, operator),
                "value": float(value) if '.' in value else int(value)
            }

        return conditions

    def _extract_parameters(self, query_text: str, query_type: QueryType) -> List[QueryParameter]:
        """提取查询参数"""
        parameters = []

        if query_type == QueryType.COVERAGE_QUERY:
            if "行" in query_text or "line" in query_text.lower():
                parameters.append(QueryParameter("type", "string", "line", description="行覆盖率"))
            elif "分支" in query_text or "branch" in query_text.lower():
                parameters.append(QueryParameter("type", "string", "branch", description="分支覆盖率"))
            elif "函数" in query_text or "function" in query_text.lower():
                parameters.append(QueryParameter("type", "string", "function", description="函数覆盖率"))

        return parameters

    def _extract_aggregations(self, query_text: str) -> List[str]:
        """提取聚合操作"""
        aggregations = []

        if any(k in query_text for k in ["总数", "total", "count"]):
            aggregations.append("count")
        if any(k in query_text for k in ["平均", "average", "avg"]):
            aggregations.append("average")
        if any(k in query_text for k in ["最大", "max", "最高"]):
            aggregations.append("max")
        if any(k in query_text for k in ["最小", "min", "最低"]):
            aggregations.append("min")

        return aggregations

    def _detect_time_range(self, query_text: str) -> Optional[TimeRange]:
        """检测时间范围"""
        if any(k in query_text for k in ["今天", "today"]):
            return TimeRange.TODAY
        elif any(k in query_text for k in ["本周", "this week"]):
            return TimeRange.THIS_WEEK
        elif any(k in query_text for k in ["本月", "this month"]):
            return TimeRange.THIS_MONTH
        elif any(k in query_text for k in ["上周", "last week"]):
            return TimeRange.LAST_WEEK
        elif any(k in query_text for k in ["上月", "last month"]):
            return TimeRange.LAST_MONTH

        return None

    def _extract_limit(self, query_text: str) -> int:
        """提取数量限制"""
        limit_pattern = r"(?:top|前|limit)\s*(\d+)"
        matches = re.findall(limit_pattern, query_text.lower())
        if matches:
            return int(matches[0])
        return 10

    def _extract_sort_info(self, query_text: str) -> Tuple[str, str]:
        """提取排序信息"""
        sort_by = ""
        sort_order = "desc"

        if any(k in query_text for k in ["升序", "asc"]):
            sort_order = "asc"
        elif any(k in query_text for k in ["降序", "desc"]):
            sort_order = "desc"

        if "时间" in query_text or "time" in query_text.lower():
            sort_by = "timestamp"
        elif "覆盖率" in query_text or "coverage" in query_text.lower():
            sort_by = "coverage"
        elif "严重" in query_text or "severity" in query_text.lower():
            sort_by = "severity"

        return sort_by, sort_order

    def _calculate_confidence(self, query: ParsedQuery) -> float:
        """计算解析置信度"""
        confidence = 0.5

        if query.query_type != QueryType.UNKNOWN:
            confidence += 0.2

        if query.intent != QueryIntent.UNKNOWN:
            confidence += 0.1

        if query.entities:
            confidence += 0.1

        if query.conditions:
            confidence += 0.1

        return min(1.0, confidence)

    def _generate_alternatives(self, query_text: str) -> List[str]:
        """生成替代查询建议"""
        alternatives = []

        if len(query_text) < 10:
            alternatives.append(f"{query_text}的详细信息")
            alternatives.append(f"查看{query_text}相关数据")

        return alternatives


class NLQueryExecutor:
    """自然语言查询执行器

    功能描述：
        - 执行结构化查询
        - 从上下文获取数据
        - 处理查询结果
        - 生成自然语言响应
    """

    def __init__(self):
        """初始化查询执行器"""
        self.execution_stats: Dict[str, float] = {}

    def execute(self, query: ParsedQuery, context: Any) -> QueryResult:
        """执行查询

        Args:
            query: 解析后的查询
            context: 上下文对象

        Returns:
            QueryResult: 查询结果
        """
        import time
        start_time = time.time()

        results: List[Dict[str, Any]] = []

        if query.query_type == QueryType.COVERAGE_QUERY:
            results = self._execute_coverage_query(query, context)
        elif query.query_type == QueryType.DEFECT_QUERY:
            results = self._execute_defect_query(query, context)
        elif query.query_type == QueryType.TEST_RESULT_QUERY:
            results = self._execute_test_result_query(query, context)
        elif query.query_type == QueryType.FILE_QUERY:
            results = self._execute_file_query(query, context)
        elif query.query_type == QueryType.FUNCTION_QUERY:
            results = self._execute_function_query(query, context)
        elif query.query_type == QueryType.TREND_QUERY:
            results = self._execute_trend_query(query, context)
        else:
            results = self._execute_general_query(query, context)

        execution_time = time.time() - start_time
        self.execution_stats[query.query_type.name] = execution_time

        result = QueryResult(
            query=query,
            results=results,
            total_count=len(results),
            execution_time=execution_time
        )

        result.page_info = self._generate_page_info(result, query.limit, query.offset)

        result.formatted_results = result.to_natural_language()

        result.summary = self._generate_summary(results, query)

        result.suggestions = self._generate_suggestions(query, results)

        return result

    def _execute_coverage_query(self, query: ParsedQuery, context: Any) -> List[Dict[str, Any]]:
        """执行覆盖率查询"""
        results = []

        if context.has('coverage_statistics_result'):
            coverage_result = context.get('coverage_statistics_result')

            if hasattr(coverage_result, 'overall_coverage'):
                results.append({
                    "type": "overall",
                    "coverage": coverage_result.overall_coverage,
                    "target": coverage_result.target_coverage,
                    "gap": coverage_result.target_coverage - coverage_result.overall_coverage
                })

            if hasattr(coverage_result, 'metrics'):
                for metric_name, metric in coverage_result.metrics.items():
                    results.append({
                        "type": metric_name,
                        "covered": metric.covered_count,
                        "total": metric.total_count,
                        "rate": metric.coverage_rate
                    })

            if hasattr(coverage_result, 'file_details'):
                for file_path, detail in coverage_result.file_details.items():
                    file_info = {
                        "type": "file",
                        "file": file_path,
                        "line_coverage": getattr(detail, 'line_coverage', 0),
                        "branch_coverage": getattr(detail, 'branch_coverage', 0),
                        "function_coverage": getattr(detail, 'function_coverage', 0)
                    }
                    results.append(file_info)

        return results

    def _execute_defect_query(self, query: ParsedQuery, context: Any) -> List[Dict[str, Any]]:
        """执行缺陷查询"""
        results = []

        if context.has('defect_grading_result'):
            defect_result = context.get('defect_grading_result')

            if hasattr(defect_result, 'defects'):
                for defect in defect_result.defects:
                    defect_info = {
                        "defect_id": getattr(defect, 'defect_id', 'N/A')[:12],
                        "title": getattr(defect, 'title', 'N/A'),
                        "severity": getattr(defect, 'severity', 'N/A').name if hasattr(getattr(defect, 'severity', None), 'name') else 'N/A',
                        "priority": getattr(defect, 'priority', 'N/A').name if hasattr(getattr(defect, 'priority', None), 'name') else 'N/A',
                        "status": getattr(defect, 'status', 'N/A').name if hasattr(getattr(defect, 'status', None), 'name') else 'N/A'
                    }
                    results.append(defect_info)

            if hasattr(defect_result, 'statistics'):
                stats = defect_result.statistics
                results.append({
                    "type": "summary",
                    "total_defects": stats.get('total_defects', 0),
                    "by_severity": stats.get('by_severity', {}),
                    "risk_level": defect_result.risk_summary.get('overall_risk_level', 'N/A')
                })

        return results

    def _execute_test_result_query(self, query: ParsedQuery, context: Any) -> List[Dict[str, Any]]:
        """执行测试结果查询"""
        results = []

        if context.has('test_results'):
            test_results = context.get('test_results')

            if isinstance(test_results, dict):
                for test_id, result in test_results.items():
                    test_info = {
                        "test_id": test_id,
                        "status": result.get('status', 'unknown'),
                        "duration": result.get('duration', 0),
                        "message": result.get('message', '')
                    }
                    results.append(test_info)

        return results

    def _execute_file_query(self, query: ParsedQuery, context: Any) -> List[Dict[str, Any]]:
        """执行文件查询"""
        results = []
        file_names = query.entities

        if context.has('source_files'):
            source_files = context.get('source_files', [])
            for file_path in source_files:
                if not file_names or any(name in file_path for name in file_names):
                    results.append({
                        "file": file_path,
                        "type": "source"
                    })

        return results

    def _execute_function_query(self, query: ParsedQuery, context: Any) -> List[Dict[str, Any]]:
        """执行函数查询"""
        results = []
        func_names = query.entities

        if context.has('function_slices'):
            func_slices = context.get('function_slices', [])
            for func in func_slices:
                func_name = getattr(func, 'name', '')
                if not func_names or any(name in func_name for name in func_names):
                    results.append({
                        "function": func_name,
                        "qualified_name": getattr(func, 'qualified_name', func_name),
                        "file": getattr(func, 'file_path', 'N/A')
                    })

        return results

    def _execute_trend_query(self, query: ParsedQuery, context: Any) -> List[Dict[str, Any]]:
        """执行趋势查询"""
        results = []

        if context.has('coverage_statistics_result'):
            coverage_result = context.get('coverage_statistics_result')

            if hasattr(coverage_result, 'trends'):
                for trend in coverage_result.trends:
                    results.append({
                        "timestamp": getattr(trend, 'timestamp', 0),
                        "overall_coverage": getattr(trend, 'overall_coverage', 0),
                        "line_coverage": getattr(trend, 'line_coverage', 0),
                        "branch_coverage": getattr(trend, 'branch_coverage', 0)
                    })

        return results

    def _execute_general_query(self, query: ParsedQuery, context: Any) -> List[Dict[str, Any]]:
        """执行通用查询"""
        results = []

        if context.has('session_id'):
            results.append({
                "type": "session",
                "session_id": context.get('session_id'),
                "overall_coverage": context.get('overall_coverage', 0)
            })

        return results

    def _generate_page_info(self, result: QueryResult, limit: int, offset: int) -> Dict[str, Any]:
        """生成分页信息"""
        total = result.total_count
        page = offset // limit + 1 if limit > 0 else 1
        total_pages = (total + limit - 1) // limit if limit > 0 else 1

        return {
            "page": page,
            "limit": limit,
            "offset": offset,
            "total": total,
            "total_pages": total_pages,
            "has_next": offset + limit < total,
            "has_prev": offset > 0
        }

    def _generate_summary(self, results: List[Dict[str, Any]], query: ParsedQuery) -> Dict[str, Any]:
        """生成结果摘要"""
        summary: Dict[str, Any] = {
            "total_results": len(results)
        }

        if query.query_type == QueryType.COVERAGE_QUERY and results:
            coverages = [r.get('coverage', 0) or r.get('line_coverage', 0) for r in results if isinstance(r, dict)]
            if coverages:
                summary['avg_coverage'] = sum(coverages) / len(coverages)
                summary['max_coverage'] = max(coverages)
                summary['min_coverage'] = min(coverages)

        elif query.query_type == QueryType.DEFECT_QUERY and results:
            severities = [r.get('severity', 'N/A') for r in results if isinstance(r, dict)]
            if severities:
                summary['severity_distribution'] = {
                    s: severities.count(s) for s in set(severities)
                }

        return summary

    def _generate_suggestions(self, query: ParsedQuery, results: List[Dict[str, Any]]) -> List[str]:
        """生成后续建议"""
        suggestions = []

        if not results:
            suggestions.append("未找到匹配结果，请尝试放宽查询条件")
            suggestions.append("可以尝试使用更通用的关键词")

        elif len(results) > 100:
            suggestions.append("结果较多，建议添加更多过滤条件")
            suggestions.append("可以使用'limit'参数限制返回数量")

        if query.query_type == QueryType.COVERAGE_QUERY:
            suggestions.append("可以查看具体的未覆盖代码行以了解详细情况")
            suggestions.append("建议针对低覆盖率文件增加测试用例")

        elif query.query_type == QueryType.DEFECT_QUERY:
            suggestions.append("建议优先处理高严重程度的缺陷")
            suggestions.append("可以查看缺陷详情了解具体问题")

        return suggestions


class NLQueryLayer:
    """NLQueryLayer - 自然语言查询接口层

    功能描述：
        - 提供自然语言查询接口
        - 解析和理解用户查询意图
        - 从测试系统中提取相关数据
        - 生成自然语言查询结果
        - 支持多种查询类型（覆盖率、缺陷、测试结果等）
        - 提供智能建议和后续操作推荐

    输入类型：
        - PipelineContext: 包含所有测试数据和结果
        - 自然语言查询文本

    输出类型：
        - QueryResult: 查询结果对象
        - 包含结果数据、摘要、建议等

    使用场景：
        - 测试报告的数据查询
        - 覆盖率信息的快速检索
        - 缺陷状态的自然语言查询
        - 交互式测试分析
        - 智能测试助手

    V3.1升级点：
        - 增强的自然语言理解能力
        - 上下文感知查询
        - 多轮对话支持
        - 智能纠错和建议
        - 支持中文和英文查询
    """

    description: str = "NLQueryLayer - 自然语言查询接口层"
    input_type: str = "PipelineContext - 包含测试数据 + 自然语言查询"
    output_type: str = "QueryResult - 查询结果对象"

    def __init__(self):
        """初始化自然语言查询接口层"""
        self.parser = NLQueryParser()
        self.executor = NLQueryExecutor()
        self.query_history: List[ParsedQuery] = []

    def process(self, context: Any) -> QueryResult:
        """处理自然语言查询

        Args:
            context: PipelineContext对象，包含测试数据和查询文本

        Returns:
            QueryResult: 查询结果

        Raises:
            ValueError: 当缺少查询文本时
        """
        if not context.has('nl_query'):
            raise ValueError("NLQueryLayer: 缺少自然语言查询文本，请提供 'nl_query' 参数")

        query_text = context.get('nl_query', '')

        parsed_query = self.parser.parse(query_text)

        self.query_history.append(parsed_query)

        result = self.executor.execute(parsed_query, context)

        context.set('nl_query_result', result)
        context.set('query_result', result.results)
        context.set('query_execution_time', result.execution_time)

        return result

    def query(self, query_text: str, context: Any) -> QueryResult:
        """执行自然语言查询

        Args:
            query_text: 自然语言查询文本
            context: 上下文对象

        Returns:
            QueryResult: 查询结果
        """
        context.set('nl_query', query_text)
        return self.process(context)

    def parse_query(self, query_text: str) -> ParsedQuery:
        """解析查询文本

        Args:
            query_text: 查询文本

        Returns:
            ParsedQuery: 解析后的查询
        """
        return self.parser.parse(query_text)

    def get_query_history(self) -> List[ParsedQuery]:
        """获取查询历史

        Returns:
            List[ParsedQuery]: 查询历史列表
        """
        return self.query_history.copy()

    def clear_history(self) -> None:
        """清除查询历史"""
        self.query_history.clear()

    def get_common_queries(self) -> List[str]:
        """获取常用查询建议

        Returns:
            List[str]: 常用查询列表
        """
        return [
            "查询整体覆盖率",
            "查看高优先级缺陷",
            "列出未覆盖的文件",
            "显示测试通过率",
            "查看分支覆盖率",
            "列出Critical级别缺陷",
            "查询函数覆盖率",
            "查看风险评估摘要"
        ]

    def explain_query(self, query_text: str) -> Dict[str, Any]:
        """解释查询的含义

        Args:
            query_text: 查询文本

        Returns:
            Dict[str, Any]: 查询解释
        """
        parsed = self.parser.parse(query_text)

        return {
            "original_query": query_text,
            "query_type": parsed.query_type.name,
            "intent": parsed.intent.name,
            "entities_found": parsed.entities,
            "conditions": parsed.conditions,
            "confidence": parsed.confidence,
            "explanation": self._generate_explanation(parsed)
        }

    def _generate_explanation(self, query: ParsedQuery) -> str:
        """生成查询解释

        Args:
            query: 解析后的查询

        Returns:
            str: 解释文本
        """
        parts = [f"这是一个{query.query_type.name.replace('_', ' ')}查询"]

        if query.intent != QueryIntent.UNKNOWN:
            intent_map = {
                QueryIntent.GET: "获取",
                QueryIntent.FILTER: "过滤筛选",
                QueryIntent.AGGREGATE: "统计汇总",
                QueryIntent.RANK: "排序排名"
            }
            parts.append(f"意图是{intent_map.get(query.intent, '获取')}数据")

        if query.entities:
            parts.append(f"涉及实体: {', '.join(query.entities[:3])}")

        if query.conditions:
            parts.append(f"包含过滤条件: {len(query.conditions)}个")

        return "，".join(parts)

    def suggest_queries(self, context: Any) -> List[str]:
        """根据上下文建议查询

        Args:
            context: 上下文对象

        Returns:
            List[str]: 建议的查询列表
        """
        suggestions = []

        if context.has('coverage_statistics_result'):
            coverage_result = context.get('coverage_statistics_result')
            if hasattr(coverage_result, 'overall_coverage'):
                coverage = coverage_result.overall_coverage
                if coverage < 80:
                    suggestions.append(f"查询低于目标的文件（当前覆盖率: {coverage:.1f}%）")

        if context.has('defect_grading_result'):
            defect_result = context.get('defect_grading_result')
            if hasattr(defect_result, 'get_critical_defects'):
                critical = defect_result.get_critical_defects()
                if critical:
                    suggestions.append(f"查看{len(critical)}个关键缺陷详情")

        if context.has('source_files'):
            source_files = context.get('source_files', [])
            suggestions.append(f"查询前10个文件的覆盖率")
            suggestions.append(f"查看{len(source_files)}个源文件的测试状态")

        return suggestions[:5]
