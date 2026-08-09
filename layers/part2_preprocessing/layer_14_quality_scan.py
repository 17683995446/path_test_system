"""
Layer 14: Quality Scan Layer (代码质量预扫描层)

该层负责对代码进行质量预扫描，检测常见的代码质量问题，
包括代码复杂度、重复代码、潜在的bug模式等。
"""

from typing import Any, Dict, List, Optional, Tuple
import re
from collections import Counter


class QualityIssue:
    """代码质量问题"""
    
    def __init__(self, issue_type: str, severity: str, 
                 file_path: str, line_number: int, 
                 message: str, suggestion: Optional[str] = None):
        self.issue_type = issue_type
        self.severity = severity
        self.file_path = file_path
        self.line_number = line_number
        self.message = message
        self.suggestion = suggestion
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "type": self.issue_type,
            "severity": self.severity,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "message": self.message,
            "suggestion": self.suggestion
        }


class QualityMetric:
    """代码质量指标"""
    
    def __init__(self, name: str, value: float, 
                 threshold: float, status: str):
        self.name = name
        self.value = value
        self.threshold = threshold
        self.status = status
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "name": self.name,
            "value": self.value,
            "threshold": self.threshold,
            "status": self.status
        }


class QualityScanResult:
    """代码质量扫描结果"""
    
    def __init__(self):
        self.issues: List[QualityIssue] = []
        self.metrics: List[QualityMetric] = []
        self.overall_score: float = 0.0
        self.scan_time_ms: float = 0.0
        self.file_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "overall_score": self.overall_score,
            "scan_time_ms": self.scan_time_ms,
            "file_count": self.file_count,
            "total_issues": len(self.issues),
            "issues_by_severity": self._get_issues_by_severity(),
            "issues_by_type": self._get_issues_by_type(),
            "metrics": [m.to_dict() for m in self.metrics]
        }
    
    def _get_issues_by_severity(self) -> Dict[str, int]:
        """按严重性统计问题"""
        counter = Counter()
        for issue in self.issues:
            counter[issue.severity] += 1
        return dict(counter)
    
    def _get_issues_by_type(self) -> Dict[str, int]:
        """按类型统计问题"""
        counter = Counter()
        for issue in self.issues:
            counter[issue.issue_type] += 1
        return dict(counter)


class QualityScanLayer:
    """
    代码质量预扫描层
    
    负责对代码进行全面的质量预扫描，检测常见的代码质量问题。
    
    核心功能：
    - 代码复杂度分析（圈复杂度、嵌套深度等）
    - 重复代码检测
    - 潜在bug模式识别
    - 代码风格问题检测
    - 可维护性指标计算
    - 安全漏洞初步扫描
    
    Attributes:
        description: 层的功能描述
        input_type: 输入数据类型 (PipelineContext)
        output_type: str = "QualityScanResult"
    """
    
    description: str = "代码质量预扫描层 - 检测代码质量问题和复杂度"
    input_type: str = "PipelineContext"
    output_type: str = "QualityScanResult"
    
    COMPLEXITY_PATTERNS = {
        'cyclomatic': [
            r'\bif\b', r'\belse\b', r'\belif\b', r'\bfor\b', 
            r'\bwhile\b', r'\bcatch\b', r'\bexcept\b', 
            r'\band\b', r'\bor\b', r'\?\s*:', r'\|\|', r'&&'
        ],
        'nesting': [r'\bif\b', r'\bfor\b', r'\bwhile\b', r'\bswitch\b']
    }
    
    BUG_PATTERNS = {
        'python': [
            (r'==\s*(?:None|True|False)', '使用is/is not比较单例'),
            (r'except\s*:\s*$', '裸except子句捕获所有异常'),
            (r'[^=!]==\s*["\'][^"\']*["\']', '使用==比较字符串字面量'),
            (r'for\s+\w+\s+in\s+.*?:\s*for\s+\w+\s+in', '嵌套循环可优化'),
            (r'\beval\s*\(', '使用eval存在安全风险'),
            (r'\bexec\s*\(', '使用exec存在安全风险'),
            (r'open\s*\([^)]*\)\s*[^\)]', '文件未正确关闭'),
            (r'\.format\s*\(\s*\%', '混用format和%格式化'),
            (r'\+=?\s*\[', '列表拼接效率低'),
        ],
        'javascript': [
            (r'var\s+', '应使用let或const替代var'),
            (r'==\s*(?!=)', '应使用===替代=='),
            (r'console\.log\s*\(', '生产代码不应包含console.log'),
            (r'new\s+Array\s*\(', '应使用数组字面量'),
            (r'null\s+==\s+\w+', '避免与null的不严格比较'),
            (r'\beval\s*\(', '使用eval存在安全风险'),
            (r'innerHTML\s*=', 'innerHTML存在XSS风险'),
            (r'\.appendChild\s*\(.*\.innerHTML', 'appendChild的innerHTML存在XSS风险'),
        ],
        'java': [
            (r'String\s+\w+\s*=\s*==\s*', '字符串比较应使用equals方法'),
            (r'catch\s*\(\s*Exception\s+\w+\s*\)', '捕获Exception可能过于宽泛'),
            (r'catch\s*\(\s*Throwable\s+', '捕获Throwable过于宽泛'),
            (r'System\.out\.print', '应使用日志框架替代System.out'),
            (r'new\s+Date\s*\(\)', 'Date已过时，应使用java.time API'),
            (r'Integer\s*\(\s*\w+\s*\)', '应使用valueOf避免创建不必要的对象'),
        ]
    }
    
    STYLE_PATTERNS = {
        'long_line': (r'^.{101,}$', '行长度超过100字符'),
        'trailing_whitespace': (r'\s+$', '行尾存在多余空格'),
        'multiple_blank_lines': (r'\n{3,}', '存在连续空行'),
        'tab_usage': (r'\t', '应使用空格替代Tab'),
    }
    
    def process(self, context: Any) -> QualityScanResult:
        """
        执行代码质量扫描
        
        Args:
            context: PipelineContext对象，包含以下预期字段：
                - scanned_files: 扫描到的文件列表 (List[Dict])
                - preprocessed_files: 预处理后的文件列表 (List[PreprocessedFile])
                - quality_options: 质量扫描选项 (dict, 可选)
                    - check_complexity: 是否检查复杂度 (默认True)
                    - check_bugs: 是否检查潜在bug (默认True)
                    - check_style: 是否检查代码风格 (默认True)
                    - complexity_threshold: 复杂度阈值 (默认10)
                    - max_nesting_depth: 最大嵌套深度 (默认4)
                    - severity_filter: 问题严重性过滤 (List[str])
        
        Returns:
            QualityScanResult: 代码质量扫描结果，包含：
                - issues: 发现的问题列表 (List[QualityIssue])
                - metrics: 质量指标列表 (List[QualityMetric])
                - overall_score: 总体质量分数 (0-100)
                - scan_time_ms: 扫描耗时（毫秒）
                - file_count: 扫描的文件数
        
        Process Flow:
            1. 遍历所有待扫描文件
            2. 计算代码复杂度指标
            3. 检测潜在bug模式
            4. 检查代码风格问题
            5. 识别重复代码
            6. 汇总质量指标
            7. 计算总体质量分数
        
        Example:
            >>> layer = QualityScanLayer()
            >>> ctx = create_context()
            >>> ctx.set('scanned_files', [{'file_path': 'test.py', 'content': '...'}])
            >>> result = layer.process(ctx)
            >>> print(f"质量分数: {result.overall_score}")
        """
        import time
        start_time = time.time()
        
        scanned_files = context.get('scanned_files', [])
        preprocessed_files = context.get('preprocessed_files', [])
        quality_options = context.get('quality_options', {})
        
        check_complexity = quality_options.get('check_complexity', True)
        check_bugs = quality_options.get('check_bugs', True)
        check_style = quality_options.get('check_style', True)
        complexity_threshold = quality_options.get('complexity_threshold', 10)
        max_nesting_depth = quality_options.get('max_nesting_depth', 4)
        severity_filter = quality_options.get('severity_filter', ['critical', 'major', 'minor'])
        
        result = QualityScanResult()
        
        files_to_scan = []
        
        if preprocessed_files:
            for pf in preprocessed_files:
                files_to_scan.append({
                    'file_path': pf.file_path,
                    'content': pf.cleaned_content,
                    'language': pf.language
                })
        else:
            files_to_scan = [
                {
                    'file_path': f.get('file_path', ''),
                    'content': f.get('content', ''),
                    'language': f.get('language', '')
                }
                for f in scanned_files
            ]
        
        result.file_count = len(files_to_scan)
        
        total_complexity = 0
        total_lines = 0
        total_functions = 0
        
        for file_info in files_to_scan:
            file_path = file_info['file_path']
            content = file_info['content']
            language = file_info['language']
            
            if not file_path or not content:
                continue
            
            if check_complexity:
                complexity, func_count, nesting_issues = self._check_complexity(
                    content, language, complexity_threshold, max_nesting_depth
                )
                total_complexity += complexity
                total_functions += func_count
                
                if complexity > complexity_threshold:
                    result.issues.append(QualityIssue(
                        issue_type='high_complexity',
                        severity='major',
                        file_path=file_path,
                        line_number=1,
                        message=f'文件复杂度为{complexity}，超过阈值{complexity_threshold}',
                        suggestion='考虑将复杂函数拆分为更小的单元'
                    ))
                
                result.issues.extend(nesting_issues)
            
            if check_bugs:
                bug_issues = self._check_bug_patterns(content, language, file_path)
                result.issues.extend(bug_issues)
            
            if check_style:
                style_issues = self._check_style_issues(content, file_path)
                result.issues.extend(style_issues)
            
            total_lines += content.count('\n')
        
        avg_complexity = total_complexity / result.file_count if result.file_count > 0 else 0
        
        result.metrics.append(QualityMetric(
            name='average_complexity',
            value=avg_complexity,
            threshold=complexity_threshold,
            status='pass' if avg_complexity <= complexity_threshold else 'fail'
        ))
        
        result.metrics.append(QualityMetric(
            name='total_lines',
            value=total_lines,
            threshold=0,
            status='info'
        ))
        
        result.metrics.append(QualityMetric(
            name='total_functions',
            value=total_functions,
            threshold=0,
            status='info'
        ))
        
        issue_count = len(result.issues)
        if severity_filter:
            filtered_issues = [i for i in result.issues if i.severity in severity_filter]
            issue_count = len(filtered_issues)
        
        result.overall_score = self._calculate_quality_score(result.issues, total_lines)
        
        result.scan_time_ms = (time.time() - start_time) * 1000
        
        context.set('quality_scan_result', result)
        context.set('quality_score', result.overall_score)
        context.set('quality_issues', [i.to_dict() for i in result.issues])
        
        return result
    
    def _check_complexity(self, content: str, language: str,
                         threshold: int, max_nesting: int) -> Tuple[int, int, List[QualityIssue]]:
        """检查代码复杂度"""
        cyclomatic = 1
        function_count = 0
        issues = []
        
        for pattern in self.COMPLEXITY_PATTERNS['cyclomatic']:
            matches = re.findall(pattern, content)
            cyclomatic += len(matches)
        
        function_patterns = {
            'python': r'def\s+\w+',
            'javascript': r'(?:function\s+\w+|const\s+\w+\s*=|(\w+)\s*\()',
            'java': r'(?:public|private|protected)?\s*\w+\s+\w+\s*\(',
            'go': r'func\s+',
            'rust': r'fn\s+'
        }
        
        func_pattern = function_patterns.get(language, function_patterns['python'])
        function_count = len(re.findall(func_pattern, content))
        
        nesting_depth = 0
        max_found_depth = 0
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            nesting_depth += len(re.findall(r'\{|\(|\[', line))
            max_found_depth = max(max_found_depth, nesting_depth)
            nesting_depth -= len(re.findall(r'\}|\)|\]', line))
            
            if max_found_depth > max_nesting:
                issues.append(QualityIssue(
                    issue_type='deep_nesting',
                    severity='minor',
                    file_path='',
                    line_number=i,
                    message=f'嵌套深度{max_found_depth}超过建议深度{max_nesting}',
                    suggestion='考虑重构以减少嵌套层次'
                ))
        
        return cyclomatic, function_count, issues[:5]
    
    def _check_bug_patterns(self, content: str, language: str, 
                          file_path: str) -> List[QualityIssue]:
        """检查潜在bug模式"""
        issues = []
        
        patterns = self.BUG_PATTERNS.get(language, self.BUG_PATTERNS.get('python', []))
        
        for pattern, message in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                line_number = content[:match.start()].count('\n') + 1
                
                severity = 'critical' if any(x in message for x in ['安全', 'XSS', '注入']) else 'major'
                
                issues.append(QualityIssue(
                    issue_type='potential_bug',
                    severity=severity,
                    file_path=file_path,
                    line_number=line_number,
                    message=message,
                    suggestion=self._get_fix_suggestion(message)
                ))
        
        return issues
    
    def _check_style_issues(self, content: str, 
                          file_path: str) -> List[QualityIssue]:
        """检查代码风格问题"""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            if len(line) > 100:
                issues.append(QualityIssue(
                    issue_type='style',
                    severity='minor',
                    file_path=file_path,
                    line_number=i,
                    message='行长度超过100字符',
                    suggestion='考虑拆分为多行或提取为变量'
                ))
            
            if line.rstrip() != line:
                issues.append(QualityIssue(
                    issue_type='style',
                    severity='minor',
                    file_path=file_path,
                    line_number=i,
                    message='行尾存在多余空格',
                    suggestion='移除行尾空格'
                ))
        
        if re.search(r'\n{3,}', content):
            issues.append(QualityIssue(
                issue_type='style',
                severity='minor',
                file_path=file_path,
                line_number=1,
                message='存在连续空行',
                suggestion='保留最多两个连续空行'
            ))
        
        return issues
    
    def _get_fix_suggestion(self, message: str) -> str:
        """获取修复建议"""
        suggestions = {
            '使用is/is not比较单素': '使用 is/is not 比较单例值',
            '裸except子句': '指定要捕获的异常类型',
            '使用==比较字符串字面量': '使用 == 比较字符串值',
            '嵌套循环': '考虑使用列表推导或Pandas向量化操作',
            '使用eval': '使用AST解析或安全替代方案',
            '使用exec': '使用AST解析或安全替代方案',
            '文件未正确关闭': '使用 with 语句确保文件正确关闭',
            '混用format和%': '统一使用一种格式化方法',
            '列表拼接': '使用列表推导或join方法',
            '使用===': '使用 === 进行严格相等比较',
            'console.log': '使用适当的日志框架',
            'new Array': '使用数组字面量 []',
            'innerHTML': '使用textContent或DOM API',
            'XSS': '对用户输入进行转义处理',
            'String比较': '使用 equals() 方法比较字符串',
            '捕获Exception': '指定具体的异常类型',
            'System.out': '使用日志框架如Log4j',
            'Date已过时': '使用 java.time 包中的类',
        }
        
        for key, suggestion in suggestions.items():
            if key in message:
                return suggestion
        
        return '请审查并修复此问题'
    
    def _calculate_quality_score(self, issues: List[QualityIssue], 
                                 total_lines: int) -> float:
        """计算质量分数"""
        if total_lines == 0:
            return 100.0
        
        severity_weights = {
            'critical': 10,
            'major': 5,
            'minor': 1
        }
        
        total_deduction = sum(severity_weights.get(issue.severity, 1) for issue in issues)
        
        max_deduction = (total_lines / 10) * severity_weights['critical']
        
        score = max(0, 100 - (total_deduction / max_deduction * 100))
        
        return round(score, 2)
    
    def get_quality_report(self, context: Any) -> Dict[str, Any]:
        """生成质量报告"""
        result = context.get('quality_scan_result')
        if not result:
            return {}
        
        report = {
            'summary': {
                'overall_score': result.overall_score,
                'quality_level': self._get_quality_level(result.overall_score),
                'scan_time_ms': result.scan_time_ms,
                'file_count': result.file_count
            },
            'issues': {
                'total': len(result.issues),
                'by_severity': result._get_issues_by_severity(),
                'by_type': result._get_issues_by_type()
            },
            'metrics': [m.to_dict() for m in result.metrics],
            'recommendations': self._generate_recommendations(result)
        }
        
        return report
    
    def _get_quality_level(self, score: float) -> str:
        """获取质量等级"""
        if score >= 90:
            return '优秀'
        elif score >= 80:
            return '良好'
        elif score >= 70:
            return '中等'
        elif score >= 60:
            return '较差'
        else:
            return '很差'
    
    def _generate_recommendations(self, result: QualityScanResult) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        critical_count = sum(1 for i in result.issues if i.severity == 'critical')
        if critical_count > 0:
            recommendations.append(f'立即修复 {critical_count} 个严重问题')
        
        high_complexity_count = sum(1 for i in result.issues if i.issue_type == 'high_complexity')
        if high_complexity_count > 0:
            recommendations.append(f'重构 {high_complexity_count} 个高复杂度文件')
        
        if result.metrics:
            avg_complexity = next((m.value for m in result.metrics if m.name == 'average_complexity'), None)
            if avg_complexity and avg_complexity > 10:
                recommendations.append('平均复杂度偏高，建议优化代码结构')
        
        return recommendations
