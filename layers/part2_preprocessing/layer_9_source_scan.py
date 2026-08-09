"""
Layer 9: Source Scan Layer (源码接入扫描层)

该层负责接入和扫描用户提供的源码，支持多种源码格式和来源。
进行初步的源码结构分析、文件类型识别和代码量统计。
"""

from typing import Any, Dict, List, Optional
import os
import hashlib
from pathlib import Path


class SourceFile:
    """源码文件数据结构"""
    
    def __init__(self, file_path: str, content: str, language: str):
        self.file_path = file_path
        self.content = content
        self.language = language
        self.lines = content.split('\n')
        self.line_count = len(self.lines)
        self.size_bytes = len(content.encode('utf-8'))
        self.checksum = hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "file_path": self.file_path,
            "content": self.content,  # 添加content字段供后续层使用
            "language": self.language,
            "line_count": self.line_count,
            "size_bytes": self.size_bytes,
            "checksum": self.checksum
        }


class SourceScanResult:
    """源码扫描结果"""
    
    def __init__(self, files: List[SourceFile], total_lines: int, 
                 languages: Dict[str, int], scan_time_ms: float):
        self.files = files
        self.total_lines = total_lines
        self.languages = languages
        self.scan_time_ms = scan_time_ms
        self.success = True
        self.errors = []
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "file_count": len(self.files),
            "total_lines": self.total_lines,
            "languages": self.languages,
            "scan_time_ms": self.scan_time_ms,
            "success": self.success,
            "errors": self.errors
        }


class SourceScanLayer:
    """
    源码接入扫描层
    
    负责接入和扫描用户提供的源码文件，支持：
    - 多种编程语言识别 (Python, Java, JavaScript, TypeScript, Go, Rust, C/C++, etc.)
    - 文件结构扫描和统计
    - 源码完整性校验
    - 代码量分析
    
    Attributes:
        description: 层的功能描述
        input_type: 输入数据类型 (PipelineContext)
        output_type: 输出数据类型 (SourceScanResult)
    """
    
    description: str = "源码接入扫描层 - 扫描和分析用户提供的源码文件"
    input_type: str = "PipelineContext"
    output_type: str = "SourceScanResult"
    
    LANGUAGE_EXTENSIONS: Dict[str, List[str]] = {
        'python': ['.py', '.pyw', '.pyi'],
        'javascript': ['.js', '.jsx', '.mjs'],
        'typescript': ['.ts', '.tsx'],
        'java': ['.java'],
        'go': ['.go'],
        'rust': ['.rs'],
        'c': ['.c', '.h'],
        'cpp': ['.cpp', '.cc', '.cxx', '.hpp', '.hxx'],
        'csharp': ['.cs'],
        'ruby': ['.rb'],
        'php': ['.php'],
        'swift': ['.swift'],
        'kotlin': ['.kt', '.kts'],
        'scala': ['.scala'],
        'html': ['.html', '.htm'],
        'css': ['.css', '.scss', '.sass', '.less'],
        'sql': ['.sql'],
        'shell': ['.sh', '.bash'],
    }
    
    EXCLUDE_PATTERNS: List[str] = [
        '__pycache__', '.git', '.svn', 'node_modules', 
        'venv', '.venv', 'env', '.env', 'build', 
        'dist', '.idea', '.vscode', '*.pyc', '*.class'
    ]
    
    def process(self, context: Any) -> SourceScanResult:
        """
        扫描和分析源码文件
        
        Args:
            context: PipelineContext对象，包含以下预期字段：
                - source_paths: 源码路径列表 (list[str])
                - scan_options: 扫描选项 (dict, 可选)
                    - recursive: 是否递归扫描子目录 (默认True)
                    - max_file_size: 最大文件大小 MB (默认10MB)
                    - follow_symlinks: 是否跟随符号链接 (默认False)
        
        Returns:
            SourceScanResult: 源码扫描结果，包含：
                - files: 扫描到的源码文件列表 (List[SourceFile])
                - total_lines: 总代码行数
                - languages: 各语言的代码行数统计 (Dict[str, int])
                - scan_time_ms: 扫描耗时（毫秒）
                - success: 是否成功
                - errors: 错误信息列表
        
        Process Flow:
            1. 从上下文获取源码路径
            2. 验证路径有效性
            3. 递归扫描文件（根据配置）
            4. 识别文件语言类型
            5. 读取并分析文件内容
            6. 统计代码量和结构
            7. 返回扫描结果
        
        Example:
            >>> from path_test_system import create_context
            >>> layer = SourceScanLayer()
            >>> ctx = create_context()
            >>> ctx.set('source_paths', ['/path/to/project'])
            >>> result = layer.process(ctx)
            >>> print(f"扫描到 {len(result.files)} 个文件")
        """
        import time
        start_time = time.time()
        
        source_paths = context.get('source_paths', [])
        scan_options = context.get('scan_options', {})
        
        recursive = scan_options.get('recursive', True)
        max_file_size_mb = scan_options.get('max_file_size', 10)
        follow_symlinks = scan_options.get('follow_symlinks', False)
        
        files: List[SourceFile] = []
        total_lines = 0
        languages: Dict[str, int] = {}
        errors: List[str] = []
        
        for path in source_paths:
            try:
                scanned_files, scanned_lines, lang_stats, scan_errors = \
                    self._scan_path(path, recursive, max_file_size_mb, follow_symlinks)
                files.extend(scanned_files)
                total_lines += scanned_lines
                for lang, count in lang_stats.items():
                    languages[lang] = languages.get(lang, 0) + count
                errors.extend(scan_errors)
            except Exception as e:
                errors.append(f"扫描路径 {path} 失败: {str(e)}")
        
        scan_time_ms = (time.time() - start_time) * 1000
        
        result = SourceScanResult(
            files=files,
            total_lines=total_lines,
            languages=languages,
            scan_time_ms=scan_time_ms
        )
        result.errors = errors
        
        context.set('source_scan_result', result)
        context.set('scanned_files', [f.to_dict() for f in files])
        context.set('total_code_lines', total_lines)
        context.set('language_breakdown', languages)
        
        return result
    
    def _scan_path(self, path: str, recursive: bool, 
                   max_file_size_mb: int, follow_symlinks: bool) -> tuple:
        """
        扫描单个路径
        
        Returns:
            tuple: (files, total_lines, languages, errors)
        """
        files: List[SourceFile] = []
        total_lines = 0
        languages: Dict[str, int] = {}
        errors: List[str] = []
        
        path_obj = Path(path)
        
        if not path_obj.exists():
            errors.append(f"路径不存在: {path}")
            return files, total_lines, languages, errors
        
        if path_obj.is_file():
            source_file = self._process_file(str(path_obj), max_file_size_mb)
            if source_file:
                files.append(source_file)
                total_lines += source_file.line_count
                languages[source_file.language] = languages.get(source_file.language, 0) + source_file.line_count
            return files, total_lines, languages, errors
        
        if path_obj.is_dir():
            pattern = '**/*' if recursive else '*'
            for file_path in path_obj.glob(pattern):
                if file_path.is_file() and not self._should_exclude(file_path):
                    try:
                        source_file = self._process_file(str(file_path), max_file_size_mb)
                        if source_file:
                            files.append(source_file)
                            total_lines += source_file.line_count
                            languages[source_file.language] = languages.get(source_file.language, 0) + source_file.line_count
                    except Exception as e:
                        errors.append(f"处理文件 {file_path} 失败: {str(e)}")
        
        return files, total_lines, languages, errors
    
    def _should_exclude(self, path: Path) -> bool:
        """检查是否应该排除该路径"""
        path_str = str(path)
        for pattern in self.EXCLUDE_PATTERNS:
            if pattern in path_str or path.name == pattern.replace('*', ''):
                return True
        return False
    
    def _process_file(self, file_path: str, max_file_size_mb: int) -> Optional[SourceFile]:
        """处理单个文件"""
        path_obj = Path(file_path)
        
        if path_obj.stat().st_size > max_file_size_mb * 1024 * 1024:
            return None
        
        language = self._detect_language(file_path)
        if not language:
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return SourceFile(file_path, content, language)
        except Exception:
            return None
    
    def _detect_language(self, file_path: str) -> Optional[str]:
        """根据文件扩展名检测语言"""
        ext = Path(file_path).suffix.lower()
        for language, extensions in self.LANGUAGE_EXTENSIONS.items():
            if ext in extensions:
                return language
        return None
    
    def get_supported_languages(self) -> List[str]:
        """获取支持的语言列表"""
        return list(self.LANGUAGE_EXTENSIONS.keys())
    
    def get_file_statistics(self, context: Any) -> Dict[str, Any]:
        """
        获取源码统计信息
        
        Args:
            context: PipelineContext对象
        
        Returns:
            Dict: 统计信息字典
        """
        scan_result = context.get('source_scan_result')
        if not scan_result:
            return {}
        
        return {
            'total_files': len(scan_result.files),
            'total_lines': scan_result.total_lines,
            'languages': scan_result.languages,
            'avg_lines_per_file': scan_result.total_lines / len(scan_result.files) if scan_result.files else 0,
            'scan_time_ms': scan_result.scan_time_ms
        }
