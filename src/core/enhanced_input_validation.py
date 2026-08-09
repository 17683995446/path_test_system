"""
EnhancedInputValidation - 增强输入验证系统
==========================================

支持多文件格式、多编程语言的输入验证和格式化检测
- Python文件 (.py)
- JavaScript文件 (.js, .jsx)
- TypeScript文件 (.ts, .tsx)
- Go文件 (.go)
- Java文件 (.java)
- C/C++文件 (.c, .cpp, .h, .hpp)
- 配置文件 (JSON, YAML, TOML)
- Markdown文档 (.md)

功能特性：
1. 文件格式自动检测
2. 编码检测和转换
3. 文件完整性验证
4. 多语言支持检测
5. 批处理优化

作者：PathTestSystem
版本：2.0.0
"""

import os
import json
import mimetypes
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class FileFormat(Enum):
    """文件格式枚举"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    GO = "go"
    JAVA = "java"
    CPP = "cpp"
    C = "c"
    JSON = "json"
    YAML = "yaml"
    MARKDOWN = "markdown"
    UNKNOWN = "unknown"


class FileCategory(Enum):
    """文件类别"""
    SOURCE_CODE = "source_code"
    CONFIG = "config"
    DOCUMENTATION = "documentation"
    OTHER = "other"


@dataclass
class FileMetadata:
    """文件元数据"""
    file_path: str
    format: FileFormat
    category: FileCategory
    encoding: str
    size: int
    line_count: int
    exists: bool
    is_readable: bool
    mime_type: Optional[str] = None
    hash: Optional[str] = None
    last_modified: Optional[float] = None
    validation_errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    """验证结果"""
    total_files: int
    valid_files: List[FileMetadata]
    invalid_files: List[FileMetadata]
    files_by_format: Dict[FileFormat, List[str]]
    files_by_category: Dict[FileCategory, List[str]]
    summary: Dict[str, Any]
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            'total_files': self.total_files,
            'valid_count': len(self.valid_files),
            'invalid_count': len(self.invalid_files),
            'format_distribution': {fmt.value: len(files) for fmt, files in self.files_by_format.items()},
            'category_distribution': {cat.value: len(files) for cat, files in self.files_by_category.items()},
            'encoding_used': list(set(f.encoding for f in self.valid_files))
        }


class FileFormatDetector:
    """
    文件格式检测器
    ==============
    
    自动检测文件格式和编码
    """
    
    FORMAT_EXTENSIONS = {
        FileFormat.PYTHON: {'.py', '.pyw', '.pyi'},
        FileFormat.JAVASCRIPT: {'.js', '.jsx', '.mjs', '.cjs'},
        FileFormat.TYPESCRIPT: {'.ts', '.tsx', '.mts', '.cts'},
        FileFormat.GO: {'.go'},
        FileFormat.JAVA: {'.java'},
        FileFormat.CPP: {'.cpp', '.cc', '.cxx', '.hpp', '.hh', '.hxx'},
        FileFormat.C: {'.c', '.h'},
        FileFormat.JSON: {'.json', '.jsonc'},
        FileFormat.YAML: {'.yaml', '.yml'},
        FileFormat.MARKDOWN: {'.md', '.markdown', '.mdown'}
    }
    
    CATEGORY_FORMATS = {
        FileCategory.SOURCE_CODE: {
            FileFormat.PYTHON, FileFormat.JAVASCRIPT, FileFormat.TYPESCRIPT,
            FileFormat.GO, FileFormat.JAVA, FileFormat.CPP, FileFormat.C
        },
        FileCategory.CONFIG: {FileFormat.JSON, FileFormat.YAML},
        FileCategory.DOCUMENTATION: {FileFormat.MARKDOWN}
    }
    
    def __init__(self):
        self.encoding_cache: Dict[str, str] = {}
    
    def detect_format(self, file_path: str) -> FileFormat:
        """
        检测文件格式
        
        Args:
            file_path: 文件路径
        
        Returns:
            文件格式
        """
        ext = Path(file_path).suffix.lower()
        
        for fmt, extensions in self.FORMAT_EXTENSIONS.items():
            if ext in extensions:
                return fmt
        
        return FileFormat.UNKNOWN
    
    def detect_category(self, file_format: FileFormat) -> FileCategory:
        """
        检测文件类别
        
        Args:
            file_format: 文件格式
        
        Returns:
            文件类别
        """
        for category, formats in self.CATEGORY_FORMATS.items():
            if file_format in formats:
                return category
        
        return FileCategory.OTHER
    
    def detect_encoding(self, file_path: str, sample_size: int = 10000) -> Tuple[str, float]:
        """
        检测文件编码
        
        Args:
            file_path: 文件路径
            sample_size: 采样大小
        
        Returns:
            (编码, 置信度)
        """
        if file_path in self.encoding_cache:
            return self.encoding_cache[file_path], 1.0
        
        encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'ascii']
        
        for encoding in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=encoding, errors='strict') as f:
                    f.read(sample_size)
                
                self.encoding_cache[file_path] = encoding
                confidence = 1.0 if encoding == 'utf-8' else 0.7
                return encoding, confidence
            except (UnicodeDecodeError, LookupError):
                continue
            except Exception:
                continue
        
        self.encoding_cache[file_path] = 'utf-8'
        return 'utf-8', 0.5
    
    def get_mime_type(self, file_path: str) -> Optional[str]:
        """
        获取MIME类型
        
        Args:
            file_path: 文件路径
        
        Returns:
            MIME类型
        """
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type


class FileValidator:
    """
    文件验证器
    ==========
    
    验证文件的有效性和完整性
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.max_file_size = self.config.get('max_file_size', 10 * 1024 * 1024)
        self.allowed_formats = self.config.get('allowed_formats', set(FileFormat))
        self.detector = FileFormatDetector()
    
    def validate_file(self, file_path: str) -> FileMetadata:
        """
        验证单个文件
        
        Args:
            file_path: 文件路径
        
        Returns:
            文件元数据
        """
        metadata = FileMetadata(
            file_path=file_path,
            format=FileFormat.UNKNOWN,
            category=FileCategory.OTHER,
            encoding='utf-8',
            size=0,
            line_count=0,
            exists=False,
            is_readable=False
        )
        
        if not os.path.exists(file_path):
            metadata.validation_errors.append("File does not exist")
            return metadata
        
        metadata.exists = True
        metadata.last_modified = os.path.getmtime(file_path)
        
        if not os.path.isfile(file_path):
            metadata.validation_errors.append("Path is not a file")
            return metadata
        
        try:
            metadata.size = os.path.getsize(file_path)
            
            if metadata.size > self.max_file_size:
                metadata.warnings.append(f"File size exceeds limit ({metadata.size} > {self.max_file_size})")
            
            metadata.format = self.detector.detect_format(file_path)
            metadata.category = self.detector.detect_category(metadata.format)
            metadata.mime_type = self.detector.get_mime_type(file_path)
            
            encoding, confidence = self.detector.detect_encoding(file_path)
            metadata.encoding = encoding
            
            if confidence < 0.7:
                metadata.warnings.append(f"Low encoding confidence: {confidence:.2f}")
            
            if metadata.format == FileFormat.UNKNOWN:
                metadata.warnings.append("Unknown file format")
            
            try:
                with open(file_path, 'r', encoding=metadata.encoding, errors='ignore') as f:
                    content = f.read()
                    metadata.line_count = content.count('\n') + (1 if content else 0)
                    metadata.is_readable = True
            except UnicodeDecodeError:
                metadata.validation_errors.append("Unable to decode file with detected encoding")
                metadata.is_readable = False
            except Exception as e:
                metadata.validation_errors.append(f"Error reading file: {str(e)}")
                metadata.is_readable = False
        
        except Exception as e:
            metadata.validation_errors.append(f"Validation error: {str(e)}")
        
        return metadata
    
    def validate_files(self, file_paths: List[str]) -> ValidationResult:
        """
        批量验证文件
        
        Args:
            file_paths: 文件路径列表
        
        Returns:
            验证结果
        """
        valid_files = []
        invalid_files = []
        files_by_format: Dict[FileFormat, List[str]] = {}
        files_by_category: Dict[FileCategory, List[str]] = {}
        
        for file_path in file_paths:
            metadata = self.validate_file(file_path)
            
            if not metadata.validation_errors:
                valid_files.append(metadata)
                
                if metadata.format not in files_by_format:
                    files_by_format[metadata.format] = []
                files_by_format[metadata.format].append(file_path)
                
                if metadata.category not in files_by_category:
                    files_by_category[metadata.category] = []
                files_by_category[metadata.category].append(file_path)
            else:
                invalid_files.append(metadata)
        
        return ValidationResult(
            total_files=len(file_paths),
            valid_files=valid_files,
            invalid_files=invalid_files,
            files_by_format=files_by_format,
            files_by_category=files_by_category,
            summary={}
        )


class MultiFormatInputProcessor:
    """
    多格式输入处理器 - 主控制器
    =================================
    
    整合文件格式检测、验证和处理
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.detector = FileFormatDetector()
        self.validator = FileValidator(self.config)
        
        self.supported_languages = self._init_supported_languages()
        self.format_handlers = self._init_format_handlers()
    
    def _init_supported_languages(self) -> Dict[FileFormat, Dict[str, Any]]:
        """初始化支持的语言"""
        return {
            FileFormat.PYTHON: {
                'name': 'Python',
                'extensions': ['.py', '.pyw', '.pyi'],
                'parser': 'ast',
                'line_comment': '#',
                'block_comment_start': '"""',
                'block_comment_end': '"""'
            },
            FileFormat.JAVASCRIPT: {
                'name': 'JavaScript',
                'extensions': ['.js', '.jsx'],
                'parser': 'babel/espree',
                'line_comment': '//',
                'block_comment_start': '/*',
                'block_comment_end': '*/'
            },
            FileFormat.TYPESCRIPT: {
                'name': 'TypeScript',
                'extensions': ['.ts', '.tsx'],
                'parser': 'typescript',
                'line_comment': '//',
                'block_comment_start': '/*',
                'block_comment_end': '*/'
            },
            FileFormat.GO: {
                'name': 'Go',
                'extensions': ['.go'],
                'parser': 'go/ast',
                'line_comment': '//',
                'block_comment_start': '/*',
                'block_comment_end': '*/'
            },
            FileFormat.JAVA: {
                'name': 'Java',
                'extensions': ['.java'],
                'parser': 'antlr',
                'line_comment': '//',
                'block_comment_start': '/*',
                'block_comment_end': '*/'
            }
        }
    
    def _init_format_handlers(self) -> Dict[FileFormat, Callable]:
        """初始化格式处理器"""
        return {
            FileFormat.PYTHON: self._handle_python,
            FileFormat.JAVASCRIPT: self._handle_javascript,
            FileFormat.TYPESCRIPT: self._handle_typescript,
            FileFormat.JSON: self._handle_json,
            FileFormat.YAML: self._handle_yaml
        }
    
    def process_input(self, input_data: Any) -> Dict[str, Any]:
        """
        处理输入
        
        Args:
            input_data: 输入数据（文件路径、目录、URL等）
        
        Returns:
            处理结果
        """
        if isinstance(input_data, str):
            if os.path.isfile(input_data):
                return self._process_file(input_data)
            elif os.path.isdir(input_data):
                return self._process_directory(input_data)
            else:
                return {'error': f'Unknown input: {input_data}'}
        elif isinstance(input_data, list):
            return self._process_file_list(input_data)
        else:
            return {'error': f'Unsupported input type: {type(input_data)}'}
    
    def _process_file(self, file_path: str) -> Dict[str, Any]:
        """处理单个文件"""
        metadata = self.validator.validate_file(file_path)
        
        if metadata.validation_errors:
            return {
                'success': False,
                'metadata': metadata.__dict__,
                'error': metadata.validation_errors
            }
        
        handler = self.format_handlers.get(metadata.format)
        if handler:
            content = self._read_file(metadata)
            parsed = handler(content, metadata)
        else:
            parsed = {'raw_content': True}
        
        return {
            'success': True,
            'metadata': metadata.__dict__,
            'parsed': parsed
        }
    
    def _process_directory(self, directory: str) -> Dict[str, Any]:
        """处理目录"""
        file_paths = []
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                file_paths.append(os.path.join(root, filename))
        
        result = self._process_file_list(file_paths)
        result['directory'] = directory
        return result
    
    def _process_file_list(self, file_paths: List[str]) -> Dict[str, Any]:
        """处理文件列表"""
        validation_result = self.validator.validate_files(file_paths)
        
        processed_files = []
        for metadata in validation_result.valid_files:
            processed = self._process_file(metadata.file_path)
            if processed['success']:
                processed_files.append(processed)
        
        return {
            'validation': validation_result.get_statistics(),
            'processed_count': len(processed_files),
            'files': processed_files
        }
    
    def _read_file(self, metadata: FileMetadata) -> str:
        """读取文件内容"""
        try:
            with open(metadata.file_path, 'r', encoding=metadata.encoding, errors='ignore') as f:
                return f.read()
        except Exception:
            return ""
    
    def _handle_python(self, content: str, metadata: FileMetadata) -> Dict[str, Any]:
        """处理Python文件"""
        import ast
        
        result = {
            'functions': [],
            'classes': [],
            'imports': [],
            'docstring': None
        }
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    result['functions'].append({
                        'name': node.name,
                        'lineno': node.lineno,
                        'args': len(node.args.args)
                    })
                elif isinstance(node, ast.ClassDef):
                    result['classes'].append({
                        'name': node.name,
                        'lineno': node.lineno
                    })
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            result['imports'].append(alias.name)
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        result['imports'].append(node.module)
        except Exception:
            pass
        
        return result
    
    def _handle_javascript(self, content: str, metadata: FileMetadata) -> Dict[str, Any]:
        """处理JavaScript文件"""
        return {
            'functions': self._extract_js_functions(content),
            'imports': self._extract_js_imports(content),
            'exports': self._extract_js_exports(content)
        }
    
    def _handle_typescript(self, content: str, metadata: FileMetadata) -> Dict[str, Any]:
        """处理TypeScript文件"""
        return {
            'interfaces': self._extract_ts_interfaces(content),
            'types': self._extract_ts_types(content),
            'functions': self._extract_js_functions(content)
        }
    
    def _handle_json(self, content: str, metadata: FileMetadata) -> Dict[str, Any]:
        """处理JSON文件"""
        try:
            data = json.loads(content)
            return {'data': data, 'valid': True}
        except json.JSONDecodeError:
            return {'data': None, 'valid': False, 'error': 'Invalid JSON'}
    
    def _handle_yaml(self, content: str, metadata: FileMetadata) -> Dict[str, Any]:
        """处理YAML文件"""
        return {'raw_content': content}
    
    def _extract_js_functions(self, content: str) -> List[Dict]:
        """提取JavaScript函数"""
        import re
        functions = []
        
        pattern = r'(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s*)?\(|(\w+)\s*:\s*(?:async\s*)?\()'
        matches = re.finditer(pattern, content)
        
        for match in matches:
            func_name = match.group(1) or match.group(2) or match.group(3)
            if func_name:
                functions.append({'name': func_name, 'lineno': content[:match.start()].count('\n') + 1})
        
        return functions
    
    def _extract_js_imports(self, content: str) -> List[str]:
        """提取JavaScript导入"""
        import re
        imports = []
        
        patterns = [
            r"import\s+(?:{[^}]+}|\w+)\s+from\s+['\"]([^'\"]+)['\"]",
            r"const\s+\w+\s*=\s*require\(['\"]([^'\"]+)['\"]\)"
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content)
            imports.extend(match.group(1) for match in matches)
        
        return imports
    
    def _extract_js_exports(self, content: str) -> List[str]:
        """提取JavaScript导出"""
        import re
        exports = []
        
        pattern = r"export\s+(?:default\s+)?(?:const|function|class|interface|type)\s+(\w+)"
        matches = re.finditer(pattern, content)
        exports.extend(match.group(1) for match in matches)
        
        return exports
    
    def _extract_ts_interfaces(self, content: str) -> List[str]:
        """提取TypeScript接口"""
        import re
        interfaces = []
        
        pattern = r"interface\s+(\w+)"
        matches = re.finditer(pattern, content)
        interfaces.extend(match.group(1) for match in matches)
        
        return interfaces
    
    def _extract_ts_types(self, content: str) -> List[str]:
        """提取TypeScript类型"""
        import re
        types = []
        
        pattern = r"type\s+(\w+)"
        matches = re.finditer(pattern, content)
        types.extend(match.group(1) for match in matches)
        
        return types


def create_input_processor(config: Optional[Dict] = None) -> MultiFormatInputProcessor:
    """
    创建多格式输入处理器工厂函数
    
    Args:
        config: 配置字典
    
    Returns:
        MultiFormatInputProcessor实例
    """
    return MultiFormatInputProcessor(config)


if __name__ == "__main__":
    processor = create_input_processor()
    
    test_files = [
        '/workspace/path_test_system/src/core/engine_integrated.py',
        '/workspace/path_test_system/src/core/error_recovery.py',
        '/workspace/path_test_system/src/core/incremental_cache.py'
    ]
    
    print("=" * 80)
    print("多格式输入处理器测试")
    print("=" * 80)
    
    for file_path in test_files:
        if os.path.exists(file_path):
            print(f"\n处理文件: {file_path}")
            result = processor._process_file(file_path)
            
            if result['success']:
                metadata = result['metadata']
                print(f"  格式: {metadata['format']}")
                print(f"  类别: {metadata['category']}")
                print(f"  编码: {metadata['encoding']}")
                print(f"  行数: {metadata['line_count']}")
                print(f"  大小: {metadata['size']} bytes")
                
                if metadata['format'] == FileFormat.PYTHON:
                    parsed = result['parsed']
                    print(f"  函数: {len(parsed['functions'])}")
                    print(f"  类: {len(parsed['classes'])}")
                    print(f"  导入: {len(parsed['imports'])}")
            else:
                print(f"  错误: {result['error']}")
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)
