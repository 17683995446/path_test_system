"""
SourceCodeProcessingLayers - 源代码处理层 (11-16)
=================================================

第二部分：源码接入与预处理
- 第11层：合并源代码
- 第12层：语法验证
- 第13层：语义理解
- 第14层：上下文感知解析
- 第15层：依赖关系提取
- 第16层：抽象语法树生成

作者：PathTestSystem
版本：1.0.0
"""

import os
import ast
import hashlib
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SourceCodeFile:
    """源代码文件"""
    file_path: str
    content: str
    lines: List[str] = field(default_factory=list)
    size: int = 0
    encoding: str = "utf-8"
    hash: str = ""
    
    def __post_init__(self):
        if not self.lines:
            self.lines = self.content.splitlines()
        self.size = len(self.content)
        if not self.hash:
            self.hash = hashlib.md5(self.content.encode()).hexdigest()


@dataclass
class MergedSourceCode:
    """合并后的源代码"""
    files: List[SourceCodeFile] = field(default_factory=list)
    total_files: int = 0
    total_lines: int = 0
    total_size: int = 0
    imports: Dict[str, List[str]] = field(default_factory=dict)
    
    def __post_init__(self):
        self.total_files = len(self.files)
        self.total_lines = sum(len(f.lines) for f in self.files)
        self.total_size = sum(f.size for f in self.files)


class SourceCodeMerger:
    """
    源代码合并器
    ============
    
    负责合并多个源代码文件
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.encoding = self.config.get('encoding', 'utf-8')
        self.max_file_size = self.config.get('max_file_size', 10 * 1024 * 1024)
    
    def load_file(self, file_path: str) -> Optional[SourceCodeFile]:
        """
        加载单个源代码文件
        
        Args:
            file_path: 文件路径
        
        Returns:
            SourceCodeFile对象或None
        """
        try:
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            if stat.st_size > self.max_file_size:
                return None
            
            with open(file_path, 'r', encoding=self.encoding, errors='ignore') as f:
                content = f.read()
            
            return SourceCodeFile(
                file_path=file_path,
                content=content
            )
        except Exception:
            return None
    
    def load_directory(self, directory: str, extensions: List[str] = ['.py']) -> List[SourceCodeFile]:
        """
        加载目录下的所有源代码文件
        
        Args:
            directory: 目录路径
            extensions: 文件扩展名列表
        
        Returns:
            源代码文件列表
        """
        files = []
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                if any(filename.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, filename)
                    source_file = self.load_file(file_path)
                    if source_file:
                        files.append(source_file)
        return files
    
    def merge_files(self, file_paths: List[str]) -> MergedSourceCode:
        """
        合并多个文件
        
        Args:
            file_paths: 文件路径列表
        
        Returns:
            合并后的源代码对象
        """
        merged = MergedSourceCode()
        
        for path in file_paths:
            if os.path.isfile(path):
                source_file = self.load_file(path)
                if source_file:
                    merged.files.append(source_file)
            elif os.path.isdir(path):
                files = self.load_directory(path)
                merged.files.extend(files)
        
        return merged
    
    def extract_imports(self, source_code: SourceCodeFile) -> List[str]:
        """
        提取导入语句
        
        Args:
            source_code: 源代码文件
        
        Returns:
            导入列表
        """
        imports = []
        try:
            tree = ast.parse(source_code.content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
        except Exception:
            pass
        return imports


class SyntaxValidator:
    """
    语法验证器
    ==========
    
    验证Python源代码语法
    """
    
    def __init__(self):
        self.errors: List[Dict] = []
    
    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """
        验证文件语法
        
        Args:
            file_path: 文件路径
        
        Returns:
            验证结果
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            ast.parse(content)
        except SyntaxError as e:
            result['valid'] = False
            result['errors'].append({
                'type': 'syntax',
                'message': str(e),
                'line': e.lineno,
                'offset': e.offset
            })
        except Exception as e:
            result['valid'] = False
            result['errors'].append({
                'type': 'general',
                'message': str(e)
            })
        
        return result
    
    def validate_content(self, content: str) -> Dict[str, Any]:
        """
        验证内容语法
        
        Args:
            content: 源代码内容
        
        Returns:
            验证结果
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            ast.parse(content)
        except SyntaxError as e:
            result['valid'] = False
            result['errors'].append({
                'type': 'syntax',
                'message': str(e),
                'line': e.lineno,
                'offset': e.offset
            })
        except Exception as e:
            result['valid'] = False
            result['errors'].append({
                'type': 'general',
                'message': str(e)
            })
        
        return result


class SemanticAnalyzer:
    """
    语义分析器
    ==========
    
    进行源代码的语义分析
    """
    
    def __init__(self):
        self.functions: Dict[str, List[str]] = {}
        self.classes: Dict[str, List[str]] = {}
        self.variables: Dict[str, Set[str]] = {}
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        分析文件语义
        
        Args:
            file_path: 文件路径
        
        Returns:
            分析结果
        """
        result = {
            'functions': [],
            'classes': [],
            'imports': [],
            'docstring': None
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    func_info = {
                        'name': node.name,
                        'lineno': node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                        'docstring': ast.get_docstring(node)
                    }
                    result['functions'].append(func_info)
                
                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        'name': node.name,
                        'lineno': node.lineno,
                        'bases': [base.id if isinstance(base, ast.Name) else str(base) for base in node.bases],
                        'docstring': ast.get_docstring(node)
                    }
                    result['classes'].append(class_info)
                
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    pass
            
            if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant):
                result['docstring'] = tree.body[0].value.value
        
        except Exception:
            pass
        
        return result
    
    def extract_call_graph(self, file_path: str) -> Dict[str, List[str]]:
        """
        提取调用图
        
        Args:
            file_path: 文件路径
        
        Returns:
            调用关系字典
        """
        call_graph: Dict[str, List[str]] = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    calls = []
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            if isinstance(child.func, ast.Name):
                                calls.append(child.func.id)
                            elif isinstance(child.func, ast.Attribute):
                                calls.append(child.func.attr)
                    
                    call_graph[node.name] = calls
        
        except Exception:
            pass
        
        return call_graph


class ContextAwareParser:
    """
    上下文感知解析器
    ================
    
    考虑上下文的解析器
    """
    
    def __init__(self):
        self.context_stack: List[Dict] = []
        self.scope_stack: List[Set[str]] = [set()]
    
    def parse_with_context(self, content: str) -> Dict[str, Any]:
        """
        带上下文的解析
        
        Args:
            content: 源代码内容
        
        Returns:
            解析结果
        """
        result = {
            'ast': None,
            'context': [],
            'scope': {}
        }
        
        try:
            tree = ast.parse(content)
            result['ast'] = tree
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    local_vars = set()
                    for child in ast.walk(node):
                        if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store):
                            local_vars.add(child.id)
                    result['scope'][node.name] = local_vars
                    result['context'].append({
                        'type': 'function',
                        'name': node.name,
                        'lineno': node.lineno,
                        'local_vars': list(local_vars)
                    })
                
                elif isinstance(node, ast.ClassDef):
                    result['context'].append({
                        'type': 'class',
                        'name': node.name,
                        'lineno': node.lineno
                    })
        
        except Exception:
            pass
        
        return result


class DependencyExtractor:
    """
    依赖关系提取器
    ==============
    
    提取模块间的依赖关系
    """
    
    def __init__(self):
        self.dependency_graph: Dict[str, Set[str]] = {}
    
    def extract_dependencies(self, file_path: str) -> Set[str]:
        """
        提取文件依赖
        
        Args:
            file_path: 文件路径
        
        Returns:
            依赖集合
        """
        dependencies = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dependencies.add(alias.name.split('.')[0])
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        dependencies.add(node.module.split('.')[0])
        
        except Exception:
            pass
        
        return dependencies
    
    def build_dependency_graph(self, file_paths: List[str]) -> Dict[str, Set[str]]:
        """
        构建依赖图
        
        Args:
            file_paths: 文件路径列表
        
        Returns:
            依赖图
        """
        graph = {}
        
        for path in file_paths:
            try:
                module_name = os.path.basename(path).replace('.py', '')
                deps = self.extract_dependencies(path)
                graph[module_name] = deps
            except Exception:
                pass
        
        return graph
    
    def find_circular_dependencies(self, graph: Dict[str, Set[str]]) -> List[List[str]]:
        """
        查找循环依赖
        
        Args:
            graph: 依赖图
        
        Returns:
            循环依赖列表
        """
        cycles = []
        visited = set()
        path = []
        
        def dfs(node: str):
            if node in path:
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
            
            if node in visited:
                return
            
            visited.add(node)
            path.append(node)
            
            for dep in graph.get(node, []):
                if dep in graph:
                    dfs(dep)
            
            path.pop()
        
        for node in graph:
            if node not in visited:
                dfs(node)
        
        return cycles


class AbstractSyntaxTreeGenerator:
    """
    抽象语法树生成器
    ================
    
    生成和管理AST树
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.cache_enabled = self.config.get('cache_enabled', True)
        self.ast_cache: Dict[str, ast.AST] = {}
    
    def generate_tree(self, content: str) -> Optional[ast.AST]:
        """
        生成AST树
        
        Args:
            content: 源代码内容
        
        Returns:
            AST树或None
        """
        try:
            return ast.parse(content)
        except Exception:
            return None
    
    def generate_from_file(self, file_path: str, use_cache: bool = True) -> Optional[ast.AST]:
        """
        从文件生成AST树
        
        Args:
            file_path: 文件路径
            use_cache: 是否使用缓存
        
        Returns:
            AST树或None
        """
        if use_cache and self.cache_enabled and file_path in self.ast_cache:
            return self.ast_cache[file_path]
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = self.generate_tree(content)
            
            if tree and self.cache_enabled:
                self.ast_cache[file_path] = tree
            
            return tree
        
        except Exception:
            return None
    
    def clear_cache(self):
        """清空缓存"""
        self.ast_cache.clear()
    
    def get_cache_stats(self) -> Dict[str, int]:
        """获取缓存统计"""
        return {
            'cached_files': len(self.ast_cache)
        }


class SourceCodeProcessor:
    """
    源代码处理器 - 主控制器
    =========================
    
    整合所有源代码处理功能
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        self.merger = SourceCodeMerger(self.config)
        self.validator = SyntaxValidator()
        self.semantic_analyzer = SemanticAnalyzer()
        self.context_parser = ContextAwareParser()
        self.dependency_extractor = DependencyExtractor()
        self.ast_generator = AbstractSyntaxTreeGenerator(self.config)
    
    def process_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        处理文件列表
        
        Args:
            file_paths: 文件路径列表
        
        Returns:
            处理结果
        """
        result = {
            'merged_code': None,
            'validation_results': [],
            'semantic_results': [],
            'dependency_graph': {},
            'summary': {}
        }
        
        merged = self.merger.merge_files(file_paths)
        result['merged_code'] = merged
        
        for file_path in file_paths:
            if os.path.isfile(file_path):
                validation = self.validator.validate_file(file_path)
                result['validation_results'].append(validation)
                
                semantic = self.semantic_analyzer.analyze_file(file_path)
                result['semantic_results'].append(semantic)
        
        result['dependency_graph'] = self.dependency_extractor.build_dependency_graph(file_paths)
        
        result['summary'] = {
            'total_files': merged.total_files,
            'total_lines': merged.total_lines,
            'total_size': merged.total_size,
            'valid_files': sum(1 for v in result['validation_results'] if v['valid']),
            'invalid_files': sum(1 for v in result['validation_results'] if not v['valid']),
            'total_functions': sum(len(s['functions']) for s in result['semantic_results']),
            'total_classes': sum(len(s['classes']) for s in result['semantic_results'])
        }
        
        return result


def create_source_processor(config: Optional[Dict] = None) -> SourceCodeProcessor:
    """
    创建源代码处理器工厂函数
    
    Args:
        config: 配置字典
    
    Returns:
        SourceCodeProcessor实例
    """
    return SourceCodeProcessor(config)


if __name__ == "__main__":
    processor = create_source_processor()
    
    test_files = [
        '/workspace/path_test_system/src/core/engine_optimized.py',
        '/workspace/path_test_system/src/core/error_recovery.py',
        '/workspace/path_test_system/src/core/incremental_cache.py'
    ]
    
    existing_files = [f for f in test_files if os.path.exists(f)]
    
    if existing_files:
        result = processor.process_files(existing_files)
        print("处理结果:")
        print(f"  总文件数: {result['summary']['total_files']}")
        print(f"  总行数: {result['summary']['total_lines']}")
        print(f"  有效文件: {result['summary']['valid_files']}")
        print(f"  总函数: {result['summary']['total_functions']}")
        print(f"  总类: {result['summary']['total_classes']}")
    else:
        print("未找到测试文件")
