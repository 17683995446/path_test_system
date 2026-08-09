"""
Layer 13: Semantic Summary Layer (代码语义摘要生成层)

该层负责对代码进行语义级别的分析和摘要生成，提取代码的核心语义信息。
V3.1版本增强了语义理解能力，支持更复杂的代码模式和业务逻辑识别。
"""

from typing import Any, Dict, List, Optional, Set, Tuple
import re
from collections import defaultdict
import hashlib


class CodeEntity:
    """代码实体数据结构"""
    
    def __init__(self, name: str, entity_type: str, 
                 line_number: int, end_line: int):
        self.name = name
        self.entity_type = entity_type
        self.line_number = line_number
        self.end_line = end_line
        self.dependencies: List[str] = []
        self.docstring: Optional[str] = None
        self.complexity: int = 1
        self.access_modifier: str = "public"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "name": self.name,
            "type": self.entity_type,
            "line_number": self.line_number,
            "end_line": self.end_line,
            "dependencies": self.dependencies,
            "docstring": self.docstring,
            "complexity": self.complexity,
            "access_modifier": self.access_modifier
        }


class SemanticSummary:
    """代码语义摘要"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.entities: List[CodeEntity] = []
        self.summary_text: str = ""
        self.business_keywords: List[str] = []
        self.technical_stack: List[str] = []
        self.api_endpoints: List[Dict[str, Any]] = []
        self.data_structures: List[str] = []
        self.error_handling: List[str] = []
        self.confidence_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "file_path": self.file_path,
            "entity_count": len(self.entities),
            "entities": [e.to_dict() for e in self.entities],
            "summary_text": self.summary_text,
            "business_keywords": self.business_keywords,
            "technical_stack": self.technical_stack,
            "api_endpoints": self.api_endpoints,
            "data_structures": self.data_structures,
            "error_handling": self.error_handling,
            "confidence_score": self.confidence_score
        }


class SemanticSummaryLayer:
    """
    代码语义摘要生成层【V3.1升级】
    
    负责对代码进行深度语义分析和摘要生成，提取代码的核心语义信息。
    V3.1版本增强了语义理解能力，支持更复杂的代码模式识别和业务逻辑分析。
    
    核心功能：
    - 代码实体识别（类、函数、接口等）
    - 语义摘要自动生成
    - 业务关键词提取
    - API端点识别
    - 数据结构识别
    - 错误处理模式分析
    
    Attributes:
        description: 层的功能描述
        input_type: 输入数据类型 (PipelineContext)
        output_type: 输出数据类型 (List[SemanticSummary])
    """
    
    description: str = "代码语义摘要生成层 - 深度语义分析和摘要生成"
    input_type: str = "PipelineContext"
    output_type: str = "List[SemanticSummary]"
    
    BUSINESS_KEYWORDS: Set[str] = {
        'user', 'customer', 'order', 'product', 'payment', 'account',
        'auth', 'login', 'register', 'profile', 'session', 'token',
        'cart', 'checkout', 'invoice', 'transaction', 'refund',
        'notification', 'email', 'sms', 'webhook', 'api', 'rest',
        'analytics', 'report', 'dashboard', 'metric', 'statistics',
        'permission', 'role', 'access', 'policy', 'security',
        'cache', 'queue', 'job', 'task', 'worker', 'scheduler',
        'upload', 'download', 'file', 'storage', 'bucket',
        'search', 'filter', 'sort', 'pagination', 'query',
        'validation', 'verification', 'confirmation', 'approval'
    }
    
    TECHNICAL_PATTERNS: Dict[str, List[str]] = {
        'database': ['select', 'insert', 'update', 'delete', 'query', 'cursor', 'transaction'],
        'web': ['http', 'request', 'response', 'route', 'controller', 'middleware', 'handler'],
        'async': ['async', 'await', 'promise', 'callback', 'event', 'listener', 'publish'],
        'testing': ['test', 'mock', 'assert', 'expect', 'suite', 'fixture', 'coverage'],
        'logging': ['log', 'debug', 'info', 'warn', 'error', 'trace', 'audit']
    }
    
    def process(self, context: Any) -> List[SemanticSummary]:
        """
        执行代码语义分析和摘要生成
        
        Args:
            context: PipelineContext对象，包含以下预期字段：
                - scanned_files: 扫描到的文件列表 (List[Dict])
                - preprocessed_files: 预处理后的文件列表 (List[PreprocessedFile])
                - adaptation_result: 语言适配结果 (AdaptationResult, 可选)
                - semantic_options: 语义分析选项 (dict, 可选)
                    - extract_entities: 是否提取代码实体 (默认True)
                    - generate_summary: 是否生成摘要文本 (默认True)
                    - detect_business_logic: 是否识别业务逻辑 (默认True)
                    - confidence_threshold: 置信度阈值 (默认0.5)
        
        Returns:
            List[SemanticSummary]: 语义摘要列表，每个元素包含：
                - file_path: 文件路径
                - entities: 代码实体列表
                - summary_text: 摘要文本
                - business_keywords: 业务关键词
                - technical_stack: 技术栈识别
                - api_endpoints: API端点
                - data_structures: 数据结构
                - error_handling: 错误处理
                - confidence_score: 置信度分数
        
        Process Flow:
            1. 获取待分析文件列表
            2. 遍历每个文件进行语义分析
            3. 识别代码实体（类、函数等）
            4. 提取业务关键词和技术模式
            5. 生成语义摘要文本
            6. 计算置信度评分
        
        Example:
            >>> layer = SemanticSummaryLayer()
            >>> ctx = create_context()
            >>> ctx.set('preprocessed_files', [preprocessed_file])
            >>> summaries = layer.process(ctx)
            >>> print(f"分析了 {len(summaries)} 个文件的语义")
        """
        scanned_files = context.get('scanned_files', [])
        preprocessed_files = context.get('preprocessed_files', [])
        adaptation_result = context.get('adaptation_result')
        semantic_options = context.get('semantic_options', {})
        
        extract_entities = semantic_options.get('extract_entities', True)
        generate_summary = semantic_options.get('generate_summary', True)
        detect_business_logic = semantic_options.get('detect_business_logic', True)
        confidence_threshold = semantic_options.get('confidence_threshold', 0.5)
        
        summaries: List[SemanticSummary] = []
        
        files_to_analyze = []
        
        if preprocessed_files:
            for pf in preprocessed_files:
                files_to_analyze.append({
                    'file_path': pf.file_path,
                    'content': pf.cleaned_content,
                    'language': pf.language
                })
        else:
            files_to_analyze = [
                {
                    'file_path': f.get('file_path', ''),
                    'content': f.get('content', ''),
                    'language': f.get('language', '')
                }
                for f in scanned_files
            ]
        
        for file_info in files_to_analyze:
            file_path = file_info['file_path']
            content = file_info['content']
            language = file_info['language']
            
            if not file_path or not content:
                continue
            
            summary = SemanticSummary(file_path)
            
            if extract_entities:
                entities = self._extract_entities(content, language)
                summary.entities = entities
            
            if detect_business_logic:
                keywords = self._extract_business_keywords(content)
                summary.business_keywords = keywords
                
                tech_stack = self._detect_technical_stack(content)
                summary.technical_stack = tech_stack
                
                api_endpoints = self._detect_api_endpoints(content, language)
                summary.api_endpoints = api_endpoints
                
                data_structures = self._extract_data_structures(content, language)
                summary.data_structures = data_structures
                
                error_handling = self._extract_error_handling(content, language)
                summary.error_handling = error_handling
            
            if generate_summary:
                summary.summary_text = self._generate_summary_text(summary, language)
            
            summary.confidence_score = self._calculate_confidence(summary)
            
            if summary.confidence_score >= confidence_threshold:
                summaries.append(summary)
        
        project_summary = self._generate_project_summary(summaries)
        context.set('semantic_summaries', summaries)
        context.set('project_semantic_summary', project_summary)
        context.set('analyzed_files_count', len(summaries))
        
        return summaries
    
    def _extract_entities(self, content: str, language: str) -> List[CodeEntity]:
        """提取代码实体"""
        entities: List[CodeEntity] = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            entity = self._parse_entity_line(line, language, i)
            if entity:
                entities.append(entity)
        
        return entities
    
    def _parse_entity_line(self, line: str, language: str, 
                          line_number: int) -> Optional[CodeEntity]:
        """解析单行代码识别实体"""
        patterns = {
            'python': {
                'class': r'class\s+(\w+)',
                'function': r'def\s+(\w+)',
                'async_function': r'async\s+def\s+(\w+)'
            },
            'javascript': {
                'class': r'class\s+(\w+)',
                'function': r'function\s+(\w+)',
                'const_function': r'const\s+(\w+)\s*='
            },
            'java': {
                'class': r'(?:public|private|protected)?\s*class\s+(\w+)',
                'interface': r'(?:public|private|protected)?\s*interface\s+(\w+)',
                'method': r'(?:public|private|protected)?\s*\w+\s+(\w+)\s*\('
            },
            'go': {
                'struct': r'type\s+(\w+)\s+struct',
                'function': r'func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)',
                'interface': r'type\s+(\w+)\s+interface'
            },
            'rust': {
                'struct': r'struct\s+(\w+)',
                'function': r'fn\s+(\w+)',
                'enum': r'enum\s+(\w+)',
                'impl': r'impl\s+(?:<[^>]+>\s+)?(\w+)'
            }
        }
        
        lang_patterns = patterns.get(language, patterns.get('python', {}))
        
        for entity_type, pattern in lang_patterns.items():
            match = re.search(pattern, line)
            if match:
                name = match.group(1)
                end_line = self._find_entity_end(lines, line_number - 1, language)
                return CodeEntity(name, entity_type, line_number, end_line)
        
        return None
    
    def _find_entity_end(self, lines: List[str], start_idx: int, 
                        language: str) -> int:
        """查找实体的结束行"""
        brace_count = 0
        in_entity = False
        
        for i in range(start_idx, len(lines)):
            line = lines[i]
            brace_count += line.count('{') - line.count('}')
            
            if '{' in line:
                in_entity = True
            
            if in_entity and brace_count == 0:
                return i + 1
        
        return start_idx + 1
    
    def _extract_business_keywords(self, content: str) -> List[str]:
        """提取业务关键词"""
        content_lower = content.lower()
        found_keywords = []
        
        for keyword in self.BUSINESS_KEYWORDS:
            if keyword in content_lower:
                found_keywords.append(keyword)
        
        return list(set(found_keywords))
    
    def _detect_technical_stack(self, content: str) -> List[str]:
        """检测技术栈"""
        content_lower = content.lower()
        detected_stack = []
        
        for stack_type, keywords in self.TECHNICAL_PATTERNS.items():
            matches = sum(1 for kw in keywords if kw in content_lower)
            if matches >= 2:
                detected_stack.append(stack_type)
        
        return detected_stack
    
    def _detect_api_endpoints(self, content: str, language: str) -> List[Dict[str, Any]]:
        """检测API端点"""
        endpoints = []
        
        patterns = {
            'python': [
                r'@(?:app|router)\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
                r'def\s+\w+\s*\(.*?(?:request|Request).*?\):'
            ],
            'javascript': [
                r'(?:app|router)\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
                r'(?:app|router)\.(get|post|put|delete|patch)\(`([^`]+)`'
            ],
            'java': [
                r'@(?:GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping)\(["\']([^"\']+)["\']',
                r'@(?:RequestMapping)\([^)]*value=["\']([^"\']+)["\']'
            ]
        }
        
        lang_patterns = patterns.get(language, [])
        
        for pattern in lang_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) >= 2:
                    method = match.group(1).upper()
                    path = match.group(2)
                    endpoints.append({
                        'method': method,
                        'path': path,
                        'line': content[:match.start()].count('\n') + 1
                    })
                elif len(match.groups()) == 1:
                    endpoints.append({
                        'method': 'UNKNOWN',
                        'path': match.group(1),
                        'line': content[:match.start()].count('\n') + 1
                    })
        
        return endpoints
    
    def _extract_data_structures(self, content: str, language: str) -> List[str]:
        """提取数据结构"""
        structures = []
        
        common_structures = [
            'list', 'dict', 'set', 'tuple', 'array', 'map', 'queue',
            'stack', 'tree', 'graph', 'hash', 'heap', 'linked', 'vector'
        ]
        
        content_lower = content.lower()
        
        for struct in common_structures:
            if struct in content_lower:
                structures.append(struct)
        
        return list(set(structures))
    
    def _extract_error_handling(self, content: str, language: str) -> List[str]:
        """提取错误处理模式"""
        error_patterns = {
            'try': r'try\s*\{?',
            'catch': r'catch\s*\(',
            'except': r'except\s*',
            'finally': r'finally\s*',
            'throw': r'throw\s+',
            'raise': r'raise\s+',
            'error': r'(?:new\s+)?Error\s*\('
        }
        
        detected = []
        
        for error_type, pattern in error_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                detected.append(error_type)
        
        return detected
    
    def _generate_summary_text(self, summary: SemanticSummary, 
                             language: str) -> str:
        """生成摘要文本"""
        parts = []
        
        if summary.entities:
            entity_types = {}
            for entity in summary.entities:
                entity_types[entity.entity_type] = entity_types.get(entity.entity_type, 0) + 1
            
            entity_desc = []
            for etype, count in entity_types.items():
                entity_desc.append(f"{etype}:{count}")
            parts.append(f"代码包含 {', '.join(entity_desc)}")
        
        if summary.business_keywords:
            keywords_str = ', '.join(summary.business_keywords[:5])
            parts.append(f"涉及业务领域: {keywords_str}")
        
        if summary.technical_stack:
            tech_str = ', '.join(summary.technical_stack)
            parts.append(f"技术栈: {tech_str}")
        
        if summary.api_endpoints:
            parts.append(f"包含 {len(summary.api_endpoints)} 个API端点")
        
        if summary.error_handling:
            parts.append(f"具有错误处理: {', '.join(summary.error_handling)}")
        
        return '. '.join(parts) if parts else "代码摘要生成中..."
    
    def _calculate_confidence(self, summary: SemanticSummary) -> float:
        """计算置信度"""
        score = 0.0
        max_score = 1.0
        
        if summary.entities:
            score += 0.3 * min(len(summary.entities) / 10, 1.0)
        
        if summary.business_keywords:
            score += 0.3 * min(len(summary.business_keywords) / 5, 1.0)
        
        if summary.technical_stack:
            score += 0.2
        
        if summary.api_endpoints:
            score += 0.1 * min(len(summary.api_endpoints) / 5, 1.0)
        
        if summary.error_handling:
            score += 0.1
        
        return min(score / max_score, 1.0)
    
    def _generate_project_summary(self, summaries: List[SemanticSummary]) -> Dict[str, Any]:
        """生成项目级语义摘要"""
        all_keywords = []
        all_tech_stack = []
        all_api_endpoints = []
        total_entities = 0
        
        for summary in summaries:
            all_keywords.extend(summary.business_keywords)
            all_tech_stack.extend(summary.technical_stack)
            all_api_endpoints.extend(summary.api_endpoints)
            total_entities += len(summary.entities)
        
        keyword_counts = defaultdict(int)
        for kw in all_keywords:
            keyword_counts[kw] += 1
        
        top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        tech_counts = defaultdict(int)
        for tech in all_tech_stack:
            tech_counts[tech] += 1
        
        return {
            'total_files': len(summaries),
            'total_entities': total_entities,
            'total_api_endpoints': len(all_api_endpoints),
            'top_business_keywords': [kw for kw, _ in top_keywords],
            'detected_technical_areas': list(tech_counts.keys())
        }
    
    def get_semantic_stats(self, context: Any) -> Dict[str, Any]:
        """获取语义分析统计信息"""
        summaries = context.get('semantic_summaries', [])
        
        total_entities = sum(len(s.entity_types for s in summaries))
        total_keywords = sum(len(s.business_keywords) for s in summaries)
        avg_confidence = sum(s.confidence_score for s in summaries) / len(summaries) if summaries else 0
        
        return {
            'total_files_analyzed': len(summaries),
            'total_entities_extracted': total_entities,
            'total_keywords_found': total_keywords,
            'average_confidence': avg_confidence,
            'high_confidence_files': sum(1 for s in summaries if s.confidence_score > 0.7)
        }
