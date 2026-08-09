"""
Layer 16: Risk Assessment Layer (测试风险评估层)

该层负责评估测试过程中的风险，包括：
- 代码变更风险
- 测试覆盖风险
- 环境依赖风险
- 性能风险
- 安全性风险
"""

from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum


class RiskLevel(Enum):
    """风险等级枚举"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class RiskCategory(Enum):
    """风险类别枚举"""
    CODE_CHANGE = "code_change"
    COVERAGE = "coverage"
    ENVIRONMENT = "environment"
    PERFORMANCE = "performance"
    SECURITY = "security"
    DEPENDENCY = "dependency"
    COMPLEXITY = "complexity"


@dataclass
class RiskItem:
    """风险项"""
    category: str
    level: str
    title: str
    description: str
    affected_files: List[str]
    suggestion: str
    confidence: float = 0.8


@dataclass
class RiskScore:
    """风险评分"""
    overall_score: float
    coverage_score: float
    complexity_score: float
    security_score: float
    dependency_score: float


class RiskAssessmentResult:
    """风险评估结果"""
    
    def __init__(self):
        self.risks: List[RiskItem] = []
        self.risk_score: Optional[RiskScore] = None
        self.high_risk_files: List[str] = []
        self.medium_risk_files: List[str] = []
        self.test_priority_suggestions: List[Dict[str, Any]] = []
        self.total_files_assessed: int = 0
        self.assessment_time_ms: float = 0.0
    
    def add_risk(self, risk: RiskItem):
        """添加风险项"""
        self.risks.append(risk)
        if risk.level in ['critical', 'high']:
            for file_path in risk.affected_files:
                if file_path not in self.high_risk_files:
                    self.high_risk_files.append(file_path)
        elif risk.level == 'medium':
            for file_path in risk.affected_files:
                if file_path not in self.medium_risk_files:
                    self.medium_risk_files.append(file_path)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "total_files_assessed": self.total_files_assessed,
            "total_risks": len(self.risks),
            "high_risk_files": self.high_risk_files,
            "medium_risk_files": self.medium_risk_files,
            "assessment_time_ms": self.assessment_time_ms,
            "risks_by_category": self._get_risks_by_category(),
            "risks_by_level": self._get_risks_by_level(),
            "test_priority_suggestions": self.test_priority_suggestions,
            "risk_score": self.risk_score.__dict__ if self.risk_score else {}
        }
    
    def _get_risks_by_category(self) -> Dict[str, int]:
        """按类别统计风险"""
        from collections import Counter
        categories = [r.category for r in self.risks]
        return dict(Counter(categories))
    
    def _get_risks_by_level(self) -> Dict[str, int]:
        """按级别统计风险"""
        from collections import Counter
        levels = [r.level for r in self.risks]
        return dict(Counter(levels))


class RiskAssessmentLayer:
    """
    测试风险评估层
    
    负责评估测试过程中的各类风险，为测试用例优先级排序提供依据。
    
    核心功能：
    - 代码变更风险评估
    - 测试覆盖风险分析
    - 环境依赖风险识别
    - 性能风险评估
    - 安全性风险检测
    - 复杂度和耦合度分析
    - 测试优先级建议
    
    Attributes:
        description: 层的功能描述
        input_type: 输入数据类型 (PipelineContext)
        output_type: 输出数据类型 (RiskAssessmentResult)
    """
    
    description: str = "测试风险评估层 - 评估测试过程中的各类风险"
    input_type: str = "PipelineContext"
    output_type: str = "RiskAssessmentResult"
    
    RISK_WEIGHTS = {
        'critical': 10,
        'high': 5,
        'medium': 2,
        'low': 1,
        'info': 0
    }
    
    COVERAGE_THRESHOLDS = {
        'low': 0.3,
        'medium': 0.6,
        'high': 0.8
    }
    
    COMPLEXITY_THRESHOLDS = {
        'low': 5,
        'medium': 10,
        'high': 15
    }
    
    def process(self, context: Any) -> RiskAssessmentResult:
        """
        执行风险评估
        
        Args:
            context: PipelineContext对象，包含以下预期字段：
                - scanned_files: 扫描到的文件列表 (List[Dict])
                - semantic_summaries: 语义摘要列表 (List[SemanticSummary])
                - quality_scan_result: 质量扫描结果 (QualityScanResult)
                - sensitive_detection_result: 敏感信息检测结果 (SensitiveDetectResult)
                - risk_options: 风险评估选项 (dict, 可选)
                    - evaluate_coverage: 是否评估覆盖风险 (默认True)
                    - evaluate_complexity: 是否评估复杂度风险 (默认True)
                    - evaluate_security: 是否评估安全风险 (默认True)
                    - evaluate_dependency: 是否评估依赖风险 (默认True)
                    - min_confidence: 最小置信度阈值 (默认0.6)
                    - risk_thresholds: 自定义风险阈值 (dict)
        
        Returns:
            RiskAssessmentResult: 风险评估结果，包含：
                - risks: 识别出的风险列表 (List[RiskItem])
                - risk_score: 综合风险评分 (RiskScore)
                - high_risk_files: 高风险文件列表
                - medium_risk_files: 中风险文件列表
                - test_priority_suggestions: 测试优先级建议
                - total_files_assessed: 评估的文件总数
                - assessment_time_ms: 评估耗时（毫秒）
        
        Process Flow:
            1. 收集各层分析结果
            2. 评估代码覆盖风险
            3. 评估复杂度风险
            4. 评估安全风险
            5. 评估依赖风险
            6. 计算综合风险评分
            7. 生成测试优先级建议
        
        Example:
            >>> layer = RiskAssessmentLayer()
            >>> ctx = create_context()
            >>> ctx.set('scanned_files', [{'file_path': 'main.py', 'content': '...'}])
            >>> result = layer.process(ctx)
            >>> print(f"发现 {len(result.risks)} 个风险项")
        """
        import time
        start_time = time.time()
        
        scanned_files = context.get('scanned_files', [])
        semantic_summaries = context.get('semantic_summaries', [])
        quality_scan_result = context.get('quality_scan_result')
        sensitive_detection_result = context.get('sensitive_detection_result')
        risk_options = context.get('risk_options', {})
        
        evaluate_coverage = risk_options.get('evaluate_coverage', True)
        evaluate_complexity = risk_options.get('evaluate_complexity', True)
        evaluate_security = risk_options.get('evaluate_security', True)
        evaluate_dependency = risk_options.get('evaluate_dependency', True)
        min_confidence = risk_options.get('min_confidence', 0.6)
        
        result = RiskAssessmentResult()
        result.total_files_assessed = len(scanned_files)
        
        file_data_map = {}
        for sf in scanned_files:
            file_path = sf.get('file_path', '')
            file_data_map[file_path] = sf
        
        summary_map = {}
        for summary in semantic_summaries:
            summary_map[summary.file_path] = summary
        
        if evaluate_coverage:
            coverage_risks = self._assess_coverage_risk(
                scanned_files, semantic_summaries, risk_options
            )
            for risk in coverage_risks:
                if risk.confidence >= min_confidence:
                    result.add_risk(risk)
        
        if evaluate_complexity:
            complexity_risks = self._assess_complexity_risk(
                scanned_files, quality_scan_result, risk_options
            )
            for risk in complexity_risks:
                if risk.confidence >= min_confidence:
                    result.add_risk(risk)
        
        if evaluate_security:
            security_risks = self._assess_security_risk(
                scanned_files, sensitive_detection_result, risk_options
            )
            for risk in security_risks:
                if risk.confidence >= min_confidence:
                    result.add_risk(risk)
        
        if evaluate_dependency:
            dependency_risks = self._assess_dependency_risk(
                scanned_files, semantic_summaries, risk_options
            )
            for risk in dependency_risks:
                if risk.confidence >= min_confidence:
                    result.add_risk(risk)
        
        result.risk_score = self._calculate_risk_score(result, scanned_files)
        
        result.test_priority_suggestions = self._generate_test_priorities(
            result, scanned_files, summary_map
        )
        
        result.assessment_time_ms = (time.time() - start_time) * 1000
        
        context.set('risk_assessment_result', result)
        context.set('risk_score', result.risk_score.overall_score if result.risk_score else 100.0)
        context.set('high_risk_files', result.high_risk_files)
        context.set('test_priorities', result.test_priority_suggestions)
        
        return result
    
    def _assess_coverage_risk(self, scanned_files: List[Dict],
                             semantic_summaries: List,
                             options: Dict) -> List[RiskItem]:
        """评估覆盖风险"""
        risks = []
        
        summary_entities = set()
        for summary in semantic_summaries:
            for entity in summary.entities:
                summary_entities.add(f"{summary.file_path}:{entity.name}")
        
        files_without_entities = []
        for sf in scanned_files:
            file_path = sf.get('file_path', '')
            if file_path not in [s.file_path for s in semantic_summaries]:
                files_without_entities.append(file_path)
        
        if len(files_without_entities) > len(scanned_files) * 0.3:
            risks.append(RiskItem(
                category=RiskCategory.COVERAGE.value,
                level=RiskLevel.MEDIUM.value,
                title='低代码实体识别率',
                description=f'有 {len(files_without_entities)} 个文件未能识别代码实体，可能影响测试覆盖分析',
                affected_files=files_without_entities[:10],
                suggestion='检查文件语言支持情况，或手动审查这些文件的重要性',
                confidence=0.75
            ))
        
        for summary in semantic_summaries:
            if len(summary.entities) > 50:
                risks.append(RiskItem(
                    category=RiskCategory.COVERAGE.value,
                    level=RiskLevel.LOW.value,
                    title='文件包含大量代码实体',
                    description=f'{summary.file_path} 包含 {len(summary.entities)} 个代码实体，测试覆盖可能不完整',
                    affected_files=[summary.file_path],
                    suggestion='优先为该文件设计全面的测试用例',
                    confidence=0.7
                ))
        
        return risks
    
    def _assess_complexity_risk(self, scanned_files: List[Dict],
                               quality_result: Any,
                               options: Dict) -> List[RiskItem]:
        """评估复杂度风险"""
        risks = []
        
        if not quality_result:
            return risks
        
        for metric in quality_result.metrics:
            if metric.name == 'average_complexity':
                if metric.value > 15:
                    risks.append(RiskItem(
                        category=RiskCategory.COMPLEXITY.value,
                        level=RiskLevel.HIGH.value,
                        title='代码平均复杂度过高',
                        description=f'项目平均圈复杂度为 {metric.value:.1f}，超过建议阈值 {metric.threshold}',
                        affected_files=[],
                        suggestion='重构高复杂度函数，拆分为更小的单元以提高可测试性',
                        confidence=0.85
                    ))
                elif metric.value > 10:
                    risks.append(RiskItem(
                        category=RiskCategory.COMPLEXITY.value,
                        level=RiskLevel.MEDIUM.value,
                        title='代码复杂度偏高',
                        description=f'项目平均圈复杂度为 {metric.value:.1f}，需要关注',
                        affected_files=[],
                        suggestion='审查高复杂度文件，优化代码结构',
                        confidence=0.75
                    ))
        
        high_complexity_issues = [
            i for i in quality_result.issues 
            if i.issue_type == 'high_complexity'
        ]
        
        if len(high_complexity_issues) > 5:
            affected_files = [i.file_path for i in high_complexity_issues[:10]]
            risks.append(RiskItem(
                category=RiskCategory.COMPLEXITY.value,
                level=RiskLevel.HIGH.value,
                title=f'存在 {len(high_complexity_issues)} 个高复杂度文件',
                description='多个文件超出复杂度阈值，测试用例设计难度增加',
                affected_files=affected_files,
                suggestion='优先测试核心业务逻辑，逐步覆盖边缘情况',
                confidence=0.8
            ))
        
        return risks
    
    def _assess_security_risk(self, scanned_files: List[Dict],
                             sensitive_result: Any,
                             options: Dict) -> List[RiskItem]:
        """评估安全风险"""
        risks = []
        
        if not sensitive_result:
            return risks
        
        critical_secrets = [
            m for m in sensitive_result.matches 
            if m.severity == 'critical'
        ]
        
        if critical_secrets:
            affected_files = list(set([m.file_path for m in critical_secrets]))
            risks.append(RiskItem(
                category=RiskCategory.SECURITY.value,
                level=RiskLevel.CRITICAL.value,
                title=f'发现 {len(critical_secrets)} 个高危敏感信息',
                description='代码中存在关键敏感信息（私钥、证书、AWS密钥等），测试时需特别注意数据隔离',
                affected_files=affected_files,
                suggestion='测试环境中使用脱敏数据，确保敏感信息不泄露到测试日志',
                confidence=0.95
            ))
        
        high_secrets = [
            m for m in sensitive_result.matches 
            if m.severity == 'high' and m.sensitive_type == 'password'
        ]
        
        if high_secrets:
            affected_files = list(set([m.file_path for m in high_secrets]))
            risks.append(RiskItem(
                category=RiskCategory.SECURITY.value,
                level=RiskLevel.HIGH.value,
                title=f'发现 {len(high_secrets)} 个密码硬编码',
                description='代码中存在硬编码密码，可能导致安全风险',
                affected_files=affected_files,
                suggestion='测试时使用测试专用账户，不要使用真实密码',
                confidence=0.9
            ))
        
        return risks
    
    def _assess_dependency_risk(self, scanned_files: List[Dict],
                               semantic_summaries: List,
                               options: Dict) -> List[RiskItem]:
        """评估依赖风险"""
        risks = []
        
        all_imports = []
        for summary in semantic_summaries:
            imports = summary.data_structures if hasattr(summary, 'data_structures') else []
            all_imports.extend(imports)
        
        from collections import Counter
        import_counts = Counter(all_imports)
        
        high_freq_imports = [
            imp for imp, count in import_counts.items() 
            if count > len(semantic_summaries) * 0.5
        ]
        
        if high_freq_imports:
            risks.append(RiskItem(
                category=RiskCategory.DEPENDENCY.value,
                level=RiskLevel.MEDIUM.value,
                title='存在高频依赖模块',
                description=f'发现 {len(high_freq_imports)} 个高频使用的依赖模块',
                affected_files=[],
                suggestion='确保测试环境正确配置这些依赖，关注版本兼容性',
                confidence=0.7
            ))
        
        return risks
    
    def _calculate_risk_score(self, result: RiskAssessmentResult,
                             scanned_files: List[Dict]) -> RiskScore:
        """计算风险评分"""
        total_weight = 0
        weighted_sum = 0
        
        for risk in result.risks:
            weight = self.RISK_WEIGHTS.get(risk.level, 0)
            total_weight += weight
            weighted_sum += weight * risk.confidence
        
        overall_score = 100.0
        if total_weight > 0:
            deduction = (weighted_sum / total_weight) * (100.0 / len(result.risks)) if result.risks else 0
            overall_score = max(0, 100 - deduction)
        
        coverage_risks = [r for r in result.risks if r.category == RiskCategory.COVERAGE.value]
        coverage_score = 100 - (len(coverage_risks) * 5)
        
        complexity_risks = [r for r in result.risks if r.category == RiskCategory.COMPLEXITY.value]
        complexity_score = 100 - (len(complexity_risks) * 8)
        
        security_risks = [r for r in result.risks if r.category == RiskCategory.SECURITY.value]
        security_score = 100 - (len(security_risks) * 15)
        
        dependency_risks = [r for r in result.risks if r.category == RiskCategory.DEPENDENCY.value]
        dependency_score = 100 - (len(dependency_risks) * 3)
        
        return RiskScore(
            overall_score=round(overall_score, 2),
            coverage_score=max(0, coverage_score),
            complexity_score=max(0, complexity_score),
            security_score=max(0, security_score),
            dependency_score=max(0, dependency_score)
        )
    
    def _generate_test_priorities(self, result: RiskAssessmentResult,
                                 scanned_files: List[Dict],
                                 summary_map: Dict) -> List[Dict[str, Any]]:
        """生成测试优先级建议"""
        priorities = []
        
        high_risk_files = set(result.high_risk_files)
        medium_risk_files = set(result.medium_risk_files)
        
        priority_files = []
        for sf in scanned_files:
            file_path = sf.get('file_path', '')
            priority_score = 0
            
            if file_path in high_risk_files:
                priority_score += 50
            if file_path in medium_risk_files:
                priority_score += 25
            
            if file_path in summary_map:
                summary = summary_map[file_path]
                priority_score += len(summary.business_keywords) * 2
                priority_score += len(summary.api_endpoints) * 5
                priority_score += len(summary.error_handling) * 3
            
            if priority_score > 0:
                priority_files.append((file_path, priority_score))
        
        priority_files.sort(key=lambda x: x[1], reverse=True)
        
        for file_path, score in priority_files[:20]:
            priorities.append({
                'file_path': file_path,
                'priority_score': score,
                'priority_level': self._get_priority_level(score),
                'suggestion': self._get_priority_suggestion(file_path, result)
            })
        
        return priorities
    
    def _get_priority_level(self, score: float) -> str:
        """获取优先级级别"""
        if score >= 80:
            return 'P0 - Critical'
        elif score >= 60:
            return 'P1 - High'
        elif score >= 40:
            return 'P2 - Medium'
        else:
            return 'P3 - Low'
    
    def _get_priority_suggestion(self, file_path: str, 
                               result: RiskAssessmentResult) -> str:
        """获取优先级建议"""
        file_risks = [r for r in result.risks if file_path in r.affected_files]
        
        if not file_risks:
            return '按照常规流程进行测试覆盖'
        
        risk_categories = set([r.category for r in file_risks])
        
        suggestions = []
        if RiskCategory.SECURITY.value in risk_categories:
            suggestions.append('重点关注安全测试')
        if RiskCategory.COMPLEXITY.value in risk_categories:
            suggestions.append('设计边界条件测试用例')
        if RiskCategory.COVERAGE.value in risk_categories:
            suggestions.append('确保高覆盖率的测试设计')
        
        return '; '.join(suggestions) if suggestions else '全面测试'
    
    def get_risk_summary(self, context: Any) -> Dict[str, Any]:
        """获取风险摘要"""
        result = context.get('risk_assessment_result')
        if not result:
            return {}
        
        return {
            'overview': {
                'overall_score': result.risk_score.overall_score if result.risk_score else 100,
                'risk_level': self._get_risk_level(result.risk_score.overall_score if result.risk_score else 100),
                'total_risks': len(result.risks),
                'high_risk_count': len(result.high_risk_files),
                'medium_risk_count': len(result.medium_risk_files)
            },
            'scores': {
                'coverage': result.risk_score.coverage_score if result.risk_score else 100,
                'complexity': result.risk_score.complexity_score if result.risk_score else 100,
                'security': result.risk_score.security_score if result.risk_score else 100,
                'dependency': result.risk_score.dependency_score if result.risk_score else 100
            },
            'top_risks': [
                {
                    'title': r.title,
                    'level': r.level,
                    'category': r.category,
                    'affected_files': len(r.affected_files)
                }
                for r in sorted(result.risks, 
                              key=lambda x: self.RISK_WEIGHTS.get(x.level, 0), 
                              reverse=True)[:5]
            ],
            'recommendations': self._generate_recommendations(result)
        }
    
    def _get_risk_level(self, score: float) -> str:
        """根据评分获取风险等级"""
        if score >= 90:
            return '低风险'
        elif score >= 70:
            return '中等风险'
        elif score >= 50:
            return '较高风险'
        else:
            return '高风险'
    
    def _generate_recommendations(self, result: RiskAssessmentResult) -> List[str]:
        """生成风险应对建议"""
        recommendations = []
        
        if result.risk_score and result.risk_score.security_score < 60:
            recommendations.append('优先处理安全问题，测试时使用脱敏数据')
        
        if len(result.high_risk_files) > 0:
            recommendations.append(f'优先测试 {len(result.high_risk_files)} 个高风险文件')
        
        critical_risks = [r for r in result.risks if r.level == RiskLevel.CRITICAL.value]
        if critical_risks:
            recommendations.append('立即处理所有严重风险项')
        
        if result.risk_score and result.risk_score.complexity_score < 70:
            recommendations.append('考虑重构高复杂度代码以提高可测试性')
        
        return recommendations
