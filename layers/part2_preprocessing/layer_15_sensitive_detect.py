"""
Layer 15: Sensitive Detect Layer (敏感代码识别层)

该层负责识别和检测代码中的敏感信息，包括：
- API密钥和密码
- 数据库连接字符串
- 私钥和证书
- 令牌和会话信息
- 个人身份信息(PII)
"""

from typing import Any, Dict, List, Optional, Tuple
import re
from dataclasses import dataclass


@dataclass
class SensitiveMatch:
    """敏感信息匹配结果"""
    sensitive_type: str
    pattern_name: str
    file_path: str
    line_number: int
    line_content: str
    matched_value: str
    severity: str
    is_likely_false_positive: bool = False


class SensitiveInfoType:
    """敏感信息类型定义"""
    
    API_KEY = 'api_key'
    PASSWORD = 'password'
    SECRET_KEY = 'secret_key'
    PRIVATE_KEY = 'private_key'
    TOKEN = 'token'
    DATABASE_URL = 'database_url'
    AWS_CREDENTIALS = 'aws_credentials'
    PERSONAL_INFO = 'personal_info'
    CREDIT_CARD = 'credit_card'
    PHONE_NUMBER = 'phone_number'
    EMAIL = 'email'
    IP_ADDRESS = 'ip_address'
    SSH_KEY = 'ssh_key'


class SensitiveDetectResult:
    """敏感信息检测结果"""
    
    def __init__(self):
        self.matches: List[SensitiveMatch] = []
        self.files_with_secrets: List[str] = []
        self.secrets_by_type: Dict[str, List[SensitiveMatch]] = {}
        self.total_secrets_found: int = 0
        self.high_severity_count: int = 0
        self.medium_severity_count: int = 0
        self.low_severity_count: int = 0
        self.false_positive_count: int = 0
    
    def add_match(self, match: SensitiveMatch):
        """添加匹配结果"""
        self.matches.append(match)
        if match.file_path not in self.files_with_secrets:
            self.files_with_secrets.append(match.file_path)
        
        if match.sensitive_type not in self.secrets_by_type:
            self.secrets_by_type[match.sensitive_type] = []
        self.secrets_by_type[match.sensitive_type].append(match)
        
        self.total_secrets_found += 1
        if not match.is_likely_false_positive:
            if match.severity == 'high':
                self.high_severity_count += 1
            elif match.severity == 'medium':
                self.medium_severity_count += 1
            else:
                self.low_severity_count += 1
        
        if match.is_likely_false_positive:
            self.false_positive_count += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "total_secrets_found": self.total_secrets_found,
            "files_with_secrets": self.files_with_secrets,
            "secrets_by_type": {
                stype: len(matches) for stype, matches in self.secrets_by_type.items()
            },
            "high_severity_count": self.high_severity_count,
            "medium_severity_count": self.medium_severity_count,
            "low_severity_count": self.low_severity_count,
            "false_positive_count": self.false_positive_count,
            "matches": [
                {
                    "type": m.sensitive_type,
                    "file": m.file_path,
                    "line": m.line_number,
                    "severity": m.severity,
                    "likely_false_positive": m.is_likely_false_positive
                }
                for m in self.matches[:10]
            ]
        }


class SensitiveDetectLayer:
    """
    敏感代码识别层
    
    负责检测代码中的敏感信息，包括API密钥、密码、私钥等安全相关内容。
    支持多种检测模式和自定义规则。
    
    核心功能：
    - API密钥检测（AWS、Google、Azure等）
    - 密码和秘钥检测
    - 数据库连接字符串检测
    - 私钥和证书检测
    - 个人身份信息(PII)检测
    - 令牌和会话信息检测
    
    Attributes:
        description: 层的功能描述
        input_type: 输入数据类型 (PipelineContext)
        output_type: 输出数据类型 (SensitiveDetectResult)
    """
    
    description: str = "敏感代码识别层 - 检测代码中的敏感信息和安全隐患"
    input_type: str = "PipelineContext"
    output_type: str = "SensitiveDetectResult"
    
    SECRET_PATTERNS: Dict[str, List[Tuple[str, str, str]]] = {
        SensitiveInfoType.API_KEY: [
            (r'api[_-]?key\s*[=:]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', 'API Key赋值', 'high'),
            (r'apikey\s*[=:]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', 'API Key赋值', 'high'),
            (r'api[_-]?secret\s*[=:]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', 'API Secret赋值', 'high'),
            (r'public[_-]?key\s*[=:]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', 'Public Key', 'medium'),
        ],
        SensitiveInfoType.PASSWORD: [
            (r'password\s*[=:]\s*["\']([^"\']{8,})["\']', '密码赋值', 'high'),
            (r'passwd\s*[=:]\s*["\']([^"\']{8,})["\']', '密码赋值', 'high'),
            (r'pwd\s*[=:]\s*["\']([^"\']{8,})["\']', '密码赋值', 'high'),
            (r'secret\s*[=:]\s*["\']([^"\']{8,})["\']', '秘钥赋值', 'high'),
            (r'pass\s*[=:]\s*["\']([^"\']{8,})["\']', '密码赋值', 'high'),
        ],
        SensitiveInfoType.SECRET_KEY: [
            (r'secret[_-]?key\s*[=:]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', '秘钥赋值', 'high'),
            (r'access[_-]?key[_-]?secret\s*[=:]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', '访问密钥', 'high'),
            (r'app[_-]?secret\s*[=:]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', '应用秘钥', 'high'),
            (r'encryption[_-]?key\s*[=:]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', '加密密钥', 'high'),
        ],
        SensitiveInfoType.TOKEN: [
            (r'bearer\s+[a-zA-Z0-9_\-\.]+', 'Bearer Token', 'high'),
            (r'auth[_-]?token\s*[=:]\s*["\']([a-zA-Z0-9_\-\.]{20,})["\']', '认证令牌', 'high'),
            (r'access[_-]?token\s*[=:]\s*["\']([a-zA-Z0-9_\-\.]{20,})["\']', '访问令牌', 'high'),
            (r'refresh[_-]?token\s*[=:]\s*["\']([a-zA-Z0-9_\-\.]{20,})["\']', '刷新令牌', 'high'),
            (r'session[_-]?id\s*[=:]\s*["\']([a-zA-Z0-9_\-\.]{20,})["\']', '会话ID', 'medium'),
            (r'xoxp-[a-zA-Z0-9_\-]+', 'Slack Token', 'high'),
            (r'ghp_[a-zA-Z0-9]{36}', 'GitHub Token', 'high'),
            (r'xoxb-[a-zA-Z0-9_\-]+', 'Slack Bot Token', 'high'),
            (r'AIza[0-9A-Za-z\-_]{35}', 'Google API Key', 'high'),
        ],
        SensitiveInfoType.DATABASE_URL: [
            (r'(?:mysql|postgres|postgresql|mongodb|redis):\/\/[^\s"\']+', '数据库连接URL', 'high'),
            (r'jdbc:[a-z]+://[^\s"\']+', 'JDBC连接字符串', 'high'),
            (r'mongodb\+srv:\/\/[^\s"\']+', 'MongoDB连接字符串', 'high'),
            (r'redis:\/\/[^\s"\']+', 'Redis连接字符串', 'high'),
        ],
        SensitiveInfoType.AWS_CREDENTIALS: [
            (r'AKIA[0-9A-Z]{16}', 'AWS Access Key ID', 'critical'),
            (r'[a-zA-Z0-9\/+]{40}', 'Potential AWS Secret Key', 'high'),
            (r'aws[_-]?access[_-]?key[_-]?id\s*[=:]\s*["\'][^"\']+["\']', 'AWS Access Key ID', 'critical'),
            (r'aws[_-]?secret[_-]?access[_-]?key\s*[=:]\s*["\'][^"\']+["\']', 'AWS Secret Key', 'critical'),
        ],
        SensitiveInfoType.PRIVATE_KEY: [
            (r'-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----', '私钥', 'critical'),
            (r'-----BEGIN CERTIFICATE-----', '证书', 'critical'),
            (r'private[_-]?key\s*[=:]\s*["\'][^"\']+["\']', '私钥配置', 'critical'),
        ],
        SensitiveInfoType.PERSONAL_INFO: [
            (r'\b\d{3}-\d{2}-\d{4}\b', 'SSN (美国社会安全号)', 'critical'),
            (r'\b\d{9}\b', 'Potential Passport Number', 'critical'),
            (r'\b[A-Z]{1,2}\d{6,8}\b', 'National ID', 'critical'),
        ],
        SensitiveInfoType.CREDIT_CARD: [
            (r'\b4[0-9]{12}(?:[0-9]{3})?\b', 'Visa卡号', 'critical'),
            (r'\b5[1-5][0-9]{14}\b', 'MasterCard号', 'critical'),
            (r'\b3[47][0-9]{13}\b', 'American Express卡号', 'critical'),
            (r'\b6(?:011|5[0-9]{2})[0-9]{12}\b', 'Discover卡号', 'critical'),
            (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '银行卡号格式', 'high'),
        ],
        SensitiveInfoType.EMAIL: [
            (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '邮箱地址', 'low'),
        ],
        SensitiveInfoType.PHONE_NUMBER: [
            (r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '美国电话号', 'medium'),
            (r'\+86\s?\d{3,4}[-\s]?\d{4}[-\s]?\d{4}', '中国电话号', 'medium'),
            (r'\+1\s?\d{3}[-.]?\d{3}[-.]?\d{4}', '加拿大电话号', 'medium'),
        ],
    }
    
    EXCLUDE_PATTERNS: List[str] = [
        r'example\.com',
        r'your_[a-z]+',
        r'your-[a-z]+',
        r'test[a-z]*',
        r'sample',
        r'placeholder',
        r'foo',
        r'bar',
        r'baz',
        r'xxx+',
        r'000000',
        r'123456',
        r'\${',
        r'\$\{',
    ]
    
    def __init__(self):
        """初始化敏感信息检测层"""
        self.custom_patterns: Dict[str, List[Tuple[str, str, str]]] = {}
    
    def process(self, context: Any) -> SensitiveDetectResult:
        """
        检测敏感信息
        
        Args:
            context: PipelineContext对象，包含以下预期字段：
                - scanned_files: 扫描到的文件列表 (List[Dict])
                - preprocessed_files: 预处理后的文件列表 (List[PreprocessedFile])
                - detect_options: 检测选项 (dict, 可选)
                    - check_types: 要检查的敏感信息类型 (List[str])
                    - exclude_patterns: 排除模式 (List[str])
                    - include_emails: 是否检测邮箱 (默认False)
                    - include_phones: 是否检测电话号码 (默认False)
                    - min_severity: 最小严重性级别 (默认'medium')
                    - custom_patterns: 自定义检测模式 (dict)
        
        Returns:
            SensitiveDetectResult: 敏感信息检测结果，包含：
                - matches: 所有匹配结果列表 (List[SensitiveMatch])
                - files_with_secrets: 包含敏感信息的文件列表
                - secrets_by_type: 按类型统计的敏感信息数量
                - total_secrets_found: 总数
                - high_severity_count: 高危敏感信息数量
                - medium_severity_count: 中危敏感信息数量
                - low_severity_count: 低危敏感信息数量
                - false_positive_count: 可能的误报数量
        
        Process Flow:
            1. 遍历所有待检测文件
            2. 应用预定义检测模式
            3. 应用自定义检测模式（如果有）
            4. 过滤已知的误报模式
            5. 评估匹配结果的可信度
            6. 汇总统计信息
        
        Example:
            >>> layer = SensitiveDetectLayer()
            >>> ctx = create_context()
            >>> ctx.set('scanned_files', [{'file_path': 'config.py', 'content': '...'}])
            >>> result = layer.process(ctx)
            >>> print(f"发现 {result.total_secrets_found} 个敏感信息")
        """
        scanned_files = context.get('scanned_files', [])
        preprocessed_files = context.get('preprocessed_files', [])
        detect_options = context.get('detect_options', {})
        
        check_types = detect_options.get('check_types', list(self.SECRET_PATTERNS.keys()))
        exclude_patterns = detect_options.get('exclude_patterns', self.EXCLUDE_PATTERNS)
        include_emails = detect_options.get('include_emails', False)
        include_phones = detect_options.get('include_phones', False)
        min_severity = detect_options.get('min_severity', 'medium')
        custom_patterns = detect_options.get('custom_patterns', {})
        
        if custom_patterns:
            self.custom_patterns = custom_patterns
            for ptype, patterns in custom_patterns.items():
                if ptype not in self.SECRET_PATTERNS:
                    self.SECRET_PATTERNS[ptype] = []
                self.SECRET_PATTERNS[ptype].extend(patterns)
        
        if not include_emails and SensitiveInfoType.EMAIL in check_types:
            check_types.remove(SensitiveInfoType.EMAIL)
        
        if not include_phones and SensitiveInfoType.PHONE_NUMBER in check_types:
            check_types.remove(SensitiveInfoType.PHONE_NUMBER)
        
        result = SensitiveDetectResult()
        
        files_to_scan = []
        
        if preprocessed_files:
            for pf in preprocessed_files:
                files_to_scan.append({
                    'file_path': pf.file_path,
                    'content': pf.original_content
                })
        else:
            files_to_scan = [
                {
                    'file_path': f.get('file_path', ''),
                    'content': f.get('content', '')
                }
                for f in scanned_files
            ]
        
        for file_info in files_to_scan:
            file_path = file_info['file_path']
            content = file_info['content']
            
            if not file_path or not content:
                continue
            
            for sensitive_type in check_types:
                if sensitive_type not in self.SECRET_PATTERNS:
                    continue
                
                patterns = self.SECRET_PATTERNS[sensitive_type]
                
                for pattern, pattern_name, severity in patterns:
                    matches = self._scan_pattern(content, pattern, file_path, sensitive_type, pattern_name, severity)
                    
                    for match in matches:
                        if self._is_valid_match(match, exclude_patterns):
                            if self._meets_severity_threshold(match.severity, min_severity):
                                result.add_match(match)
        
        context.set('sensitive_detection_result', result)
        context.set('sensitive_files', result.files_with_secrets)
        context.set('total_secrets_found', result.total_secrets_found)
        
        return result
    
    def _scan_pattern(self, content: str, pattern: str, 
                     file_path: str, sensitive_type: str,
                     pattern_name: str, severity: str) -> List[SensitiveMatch]:
        """扫描单个模式"""
        matches = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            found_matches = re.finditer(pattern, line, re.IGNORECASE)
            
            for match in found_matches:
                matched_value = match.group(0) if match.groups() else match.group(0)
                
                sensitive_match = SensitiveMatch(
                    sensitive_type=sensitive_type,
                    pattern_name=pattern_name,
                    file_path=file_path,
                    line_number=i,
                    line_content=line.strip(),
                    matched_value=matched_value[:50] + '...' if len(matched_value) > 50 else matched_value,
                    severity=severity
                )
                
                matches.append(sensitive_match)
        
        return matches
    
    def _is_valid_match(self, match: SensitiveMatch, 
                       exclude_patterns: List[str]) -> bool:
        """检查是否为有效匹配（非误报）"""
        matched_text = match.matched_value.lower()
        line_text = match.line_content.lower()
        
        for exclude_pattern in exclude_patterns:
            if re.search(exclude_pattern, matched_text, re.IGNORECASE):
                match.is_likely_false_positive = True
                return False
        
        if 'example' in matched_text or 'test' in matched_text or 'dummy' in matched_text:
            match.is_likely_false_positive = True
            return False
        
        common_test_patterns = [
            r'test[a-z_]*',
            r'example[a-z_]*',
            r'sample[a-z_]*',
            r'demo[a-z_]*',
            r'dummy[a-z_]*',
            r'placeholder'
        ]
        
        for pattern in common_test_patterns:
            if re.search(pattern, matched_text):
                match.is_likely_false_positive = True
                return False
        
        if match.severity in ['high', 'critical'] and len(match.matched_value) < 8:
            return False
        
        return True
    
    def _meets_severity_threshold(self, severity: str, 
                                  min_severity: str) -> bool:
        """检查是否满足严重性阈值"""
        severity_levels = {
            'critical': 4,
            'high': 3,
            'medium': 2,
            'low': 1
        }
        
        match_level = severity_levels.get(severity, 0)
        min_level = severity_levels.get(min_severity, 2)
        
        return match_level >= min_level
    
    def add_custom_pattern(self, sensitive_type: str, 
                           pattern: str, pattern_name: str,
                           severity: str = 'high'):
        """添加自定义检测模式"""
        if sensitive_type not in self.custom_patterns:
            self.custom_patterns[sensitive_type] = []
        
        self.custom_patterns[sensitive_type].append((pattern, pattern_name, severity))
        
        if sensitive_type not in self.SECRET_PATTERNS:
            self.SECRET_PATTERNS[sensitive_type] = []
        
        self.SECRET_PATTERNS[sensitive_type].append((pattern, pattern_name, severity))
    
    def get_detection_summary(self, context: Any) -> Dict[str, Any]:
        """获取检测摘要"""
        result = context.get('sensitive_detection_result')
        if not result:
            return {}
        
        return {
            'summary': {
                'total_secrets': result.total_secrets_found,
                'files_affected': len(result.files_with_secrets),
                'high_risk': result.high_severity_count,
                'medium_risk': result.medium_severity_count,
                'low_risk': result.low_severity_count
            },
            'by_type': {
                stype: len(matches) 
                for stype, matches in result.secrets_by_type.items()
            },
            'recommendations': self._generate_recommendations(result)
        }
    
    def _generate_recommendations(self, result: SensitiveDetectResult) -> List[str]:
        """生成处理建议"""
        recommendations = []
        
        if result.high_severity_count > 0:
            recommendations.append(
                f'立即处理 {result.high_severity_count} 个高危敏感信息，'
                '使用环境变量或密钥管理服务替代硬编码'
            )
        
        if SensitiveInfoType.API_KEY in result.secrets_by_type:
            recommendations.append(
                '将API密钥迁移到环境变量或密钥管理服务（如AWS Secrets Manager）'
            )
        
        if SensitiveInfoType.PASSWORD in result.secrets_by_type:
            recommendations.append(
                '密码不应硬编码在代码中，考虑使用密码管理器或环境变量'
            )
        
        if SensitiveInfoType.AWS_CREDENTIALS in result.secrets_by_type:
            recommendations.append(
                'AWS凭证必须立即轮换，使用IAM角色和临时凭证更安全'
            )
        
        if SensitiveInfoType.PRIVATE_KEY in result.secrets_by_type:
            recommendations.append(
                '私钥和证书必须使用安全的密钥存储方案，不要放在代码仓库中'
            )
        
        return recommendations
    
    def export_findings(self, context: Any, format: str = 'json') -> str:
        """导出检测结果"""
        result = context.get('sensitive_detection_result')
        if not result:
            return '{}'
        
        if format == 'json':
            import json
            return json.dumps(result.to_dict(), indent=2)
        elif format == 'csv':
            lines = ['Type,File,Line,Severity,False Positive']
            for match in result.matches:
                lines.append(
                    f'{match.sensitive_type},{match.file_path},{match.line_number},'
                    f'{match.severity},{match.is_likely_false_positive}'
                )
            return '\n'.join(lines)
        
        return str(result.to_dict())
