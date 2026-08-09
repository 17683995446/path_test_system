"""
Layer 11: File Preprocess Layer (文件预处理清洗层)

该层负责对源码文件进行预处理和清洗，包括：
- 移除注释和空行
- 规范化代码格式
- 识别编码格式
- 处理特殊字符和不可见字符
"""

from typing import Any, Dict, List, Optional, Tuple
import re
import unicodedata


class PreprocessedFile:
    """预处理后的文件数据"""
    
    def __init__(self, file_path: str, original_content: str,
                 cleaned_content: str, language: str,
                 encoding: str = 'utf-8'):
        self.file_path = file_path
        self.original_content = original_content
        self.cleaned_content = cleaned_content
        self.language = language
        self.encoding = encoding
        self.original_lines = original_content.split('\n')
        self.cleaned_lines = cleaned_content.split('\n')
        self.preprocessing_stats = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "file_path": self.file_path,
            "language": self.language,
            "encoding": self.encoding,
            "original_lines": len(self.original_lines),
            "cleaned_lines": len(self.cleaned_lines),
            "lines_removed": len(self.original_lines) - len(self.cleaned_lines),
            "preprocessing_stats": self.preprocessing_stats
        }


class FilePreprocessLayer:
    """
    文件预处理清洗层
    
    负责对源码文件进行预处理和清洗，以提高后续分析的准确性和效率。
    
    核心功能：
    - 注释移除（单行注释、多行注释、文档注释）
    - 空行和空白字符处理
    - 代码规范化（统一缩进、空格等）
    - 编码检测和转换
    - 特殊字符处理
    
    Attributes:
        description: 层的功能描述
        input_type: 输入数据类型 (PipelineContext)
        output_type: 输出数据类型 (List[PreprocessedFile])
    """
    
    description: str = "文件预处理清洗层 - 清洗和规范化源码文件"
    input_type: str = "PipelineContext"
    output_type: str = "List[PreprocessedFile]"
    
    COMMENT_PATTERNS: Dict[str, Dict[str, str]] = {
        'python': {
            'single': r'#.*$',
            'multi_start': r'"""',
            'multi_end': r'"""',
            'doc_start': r"'''",
            'doc_end': r"'''"
        },
        'javascript': {
            'single': r'//.*$',
            'multi_start': r'/\*',
            'multi_end': r'\*/'
        },
        'java': {
            'single': r'//.*$',
            'multi_start': r'/\*',
            'multi_end': r'\*/'
        },
        'typescript': {
            'single': r'//.*$',
            'multi_start': r'/\*',
            'multi_end': r'\*/'
        },
        'go': {
            'single': r'//.*$',
            'multi_start': r'/\*',
            'multi_end': r'\*/'
        },
        'rust': {
            'single': r'//.*$',
            'multi_start': r'/\*',
            'multi_end': r'\*/'
        },
        'c': {
            'single': r'//.*$',
            'multi_start': r'/\*',
            'multi_end': r'\*/'
        },
        'cpp': {
            'single': r'//.*$',
            'multi_start': r'/\*',
            'multi_end': r'\*/'
        },
        'csharp': {
            'single': r'//.*$',
            'multi_start': r'/\*',
            'multi_end': r'\*/'
        },
        'ruby': {
            'single': r'#.*$',
            'multi_start': r'=begin',
            'multi_end': r'=end'
        },
        'php': {
            'single': r'//.*$',
            'multi_start': r'/\*',
            'multi_end': r'\*/'
        },
        'swift': {
            'single': r'//.*$',
            'multi_start': r'/\*',
            'multi_end': r'\*/'
        },
        'kotlin': {
            'single': r'//.*$',
            'multi_start': r'/\*',
            'multi_end': r'\*/'
        },
        'html': {
            'multi_start': r'<!--',
            'multi_end': r'-->'
        },
        'css': {
            'multi_start': r'/\*',
            'multi_end': r'\*/'
        },
        'sql': {
            'single': r'--.*$',
            'multi_start': r'/\*',
            'multi_end': r'\*/'
        },
        'shell': {
            'single': r'#.*$'
        }
    }
    
    def process(self, context: Any) -> List[PreprocessedFile]:
        """
        预处理源码文件
        
        Args:
            context: PipelineContext对象，包含以下预期字段：
                - scanned_files: 扫描到的文件列表 (List[Dict])
                - preprocess_options: 预处理选项 (dict, 可选)
                    - remove_comments: 是否移除注释 (默认True)
                    - remove_empty_lines: 是否移除空行 (默认True)
                    - normalize_whitespace: 是否规范化空白字符 (默认True)
                    - preserve_docstrings: 是否保留文档字符串 (默认False)
                    - detect_encoding: 是否检测编码 (默认True)
        
        Returns:
            List[PreprocessedFile]: 预处理后的文件列表，每个元素包含：
                - file_path: 文件路径
                - original_content: 原始内容
                - cleaned_content: 清洗后的内容
                - language: 编程语言
                - encoding: 文件编码
                - preprocessing_stats: 预处理统计信息
        
        Process Flow:
            1. 遍历所有待处理文件
            2. 检测文件编码格式
            3. 移除注释（根据语言类型）
            4. 处理空行和空白字符
            5. 规范化代码格式
            6. 生成预处理统计信息
        
        Example:
            >>> layer = FilePreprocessLayer()
            >>> ctx = create_context()
            >>> ctx.set('scanned_files', [{'file_path': 'test.py', 'content': '...'}])
            >>> preprocessed = layer.process(ctx)
            >>> print(f"预处理了 {len(preprocessed)} 个文件")
        """
        scanned_files = context.get('scanned_files', [])
        preprocess_options = context.get('preprocess_options', {})
        
        remove_comments = preprocess_options.get('remove_comments', True)
        remove_empty_lines = preprocess_options.get('remove_empty_lines', True)
        normalize_whitespace = preprocess_options.get('normalize_whitespace', True)
        preserve_docstrings = preprocess_options.get('preserve_docstrings', False)
        detect_encoding = preprocess_options.get('detect_encoding', True)
        
        preprocessed_files: List[PreprocessedFile] = []
        
        for file_info in scanned_files:
            file_path = file_info.get('file_path', '')
            original_content = file_info.get('content', '')
            language = file_info.get('language', '')
            
            if not file_path or not original_content:
                continue
            
            cleaned_content = original_content
            
            if detect_encoding:
                encoding = self._detect_encoding(original_content)
            else:
                encoding = file_info.get('encoding', 'utf-8')
            
            stats = {'comments_removed': 0, 'lines_removed': 0, 'chars_normalized': 0}
            
            if remove_comments:
                cleaned_content, comment_count = self._remove_comments(
                    cleaned_content, language, preserve_docstrings
                )
                stats['comments_removed'] = comment_count
            
            if normalize_whitespace:
                cleaned_content, norm_count = self._normalize_whitespace(cleaned_content)
                stats['chars_normalized'] = norm_count
            
            if remove_empty_lines:
                cleaned_content, lines_removed = self._remove_empty_lines(cleaned_content)
                stats['lines_removed'] = lines_removed
            
            preprocessed_file = PreprocessedFile(
                file_path=file_path,
                original_content=original_content,
                cleaned_content=cleaned_content,
                language=language,
                encoding=encoding
            )
            preprocessed_file.preprocessing_stats = stats
            preprocessed_files.append(preprocessed_file)

        # 存储合并后的源代码（供后续层使用）
        combined_source = '\n'.join([f.cleaned_content for f in preprocessed_files])

        context.set('preprocessed_files', preprocessed_files)
        context.set('preprocessed_file_count', len(preprocessed_files))
        context.set('preprocessed_source', combined_source)

        return preprocessed_files
    
    def _detect_encoding(self, content: str) -> str:
        """检测文件编码"""
        try:
            content.encode('utf-8')
            return 'utf-8'
        except UnicodeEncodeError:
            pass
        
        try:
            content.encode('latin-1')
            return 'latin-1'
        except UnicodeEncodeError:
            pass
        
        return 'unknown'
    
    def _remove_comments(self, content: str, language: str,
                        preserve_docstrings: bool) -> Tuple[str, int]:
        """移除注释"""
        patterns = self.COMMENT_PATTERNS.get(language, {})
        
        if not patterns:
            return content, 0
        
        comment_count = 0
        result = content
        
        if 'single' in patterns:
            single_pattern = patterns['single']
            matches = re.findall(single_pattern, result, re.MULTILINE)
            comment_count += len(matches)
            result = re.sub(single_pattern, '', result, flags=re.MULTILINE)
        
        if 'multi_start' in patterns and 'multi_end' in patterns:
            multi_start = patterns['multi_start']
            multi_end = patterns['multi_end']
            
            if language in ['python'] and not preserve_docstrings:
                result = self._remove_python_docstrings(result)
            else:
                pattern = f'{re.escape(multi_start)}.*?{re.escape(multi_end)}'
                matches = re.findall(pattern, result, re.DOTALL)
                comment_count += len(matches)
                result = re.sub(pattern, '', result, flags=re.DOTALL)
        
        return result, comment_count
    
    def _remove_python_docstrings(self, content: str) -> str:
        """移除Python文档字符串"""
        result = []
        i = 0
        n = len(content)
        
        while i < n:
            if i < n - 2 and content[i:i+3] == '"""':
                end = content.find('"""', i + 3)
                if end != -1:
                    i = end + 3
                    continue
            if i < n - 2 and content[i:i+3] == "'''":
                end = content.find("'''", i + 3)
                if end != -1:
                    i = end + 3
                    continue
            result.append(content[i])
            i += 1
        
        return ''.join(result)
    
    def _normalize_whitespace(self, content: str) -> Tuple[str, int]:
        """规范化空白字符"""
        original_len = len(content)
        
        content = content.expandtabs(4)
        
        content = re.sub(r'[ \t]+', ' ', content)
        
        content = re.sub(r'\r\n', '\n', content)
        
        normalized_len = len(content)
        chars_normalized = original_len - normalized_len
        
        return content, chars_normalized
    
    def _remove_empty_lines(self, content: str) -> Tuple[str, int]:
        """移除空行"""
        lines = content.split('\n')
        original_count = len(lines)
        
        lines = [line for line in lines if line.strip()]
        
        lines_removed = original_count - len(lines)
        
        return '\n'.join(lines), lines_removed
    
    def get_preprocessing_stats(self, context: Any) -> Dict[str, Any]:
        """获取预处理统计信息"""
        preprocessed_files = context.get('preprocessed_files', [])
        
        total_original_lines = 0
        total_cleaned_lines = 0
        total_comments_removed = 0
        total_lines_removed = 0
        
        for pf in preprocessed_files:
            total_original_lines += pf.preprocessing_stats.get('original_lines', 0)
            total_cleaned_lines += pf.preprocessing_stats.get('cleaned_lines', 0)
            total_comments_removed += pf.preprocessing_stats.get('comments_removed', 0)
            total_lines_removed += pf.preprocessing_stats.get('lines_removed', 0)
        
        return {
            "total_files": len(preprocessed_files),
            "total_original_lines": total_original_lines,
            "total_cleaned_lines": total_cleaned_lines,
            "total_comments_removed": total_comments_removed,
            "total_lines_removed": total_lines_removed,
            "compression_ratio": total_cleaned_lines / total_original_lines if total_original_lines > 0 else 1.0
        }
