"""
Layer 12: Language Adapter Layer (多语言适配分发层)

该层负责识别源码语言类型，并将处理任务分发到对应的语言适配器。
V3.1版本增强了多语言支持，新增对新兴编程语言的适配。
"""

from typing import Any, Dict, List, Optional, Type
from abc import ABC, abstractmethod


class LanguageAdapter(ABC):
    """语言适配器抽象基类"""
    
    @abstractmethod
    def get_language_name(self) -> str:
        """获取语言名称"""
        pass
    
    @abstractmethod
    def can_handle(self, file_path: str, content: str) -> bool:
        """判断是否能处理该文件"""
        pass
    
    @abstractmethod
    def extract_code_elements(self, content: str) -> Dict[str, Any]:
        """提取代码元素"""
        pass
    
    @abstractmethod
    def normalize_syntax(self, content: str) -> str:
        """规范化语法"""
        pass


class PythonAdapter(LanguageAdapter):
    """Python语言适配器"""
    
    def get_language_name(self) -> str:
        return "python"
    
    def can_handle(self, file_path: str, content: str) -> bool:
        return file_path.endswith('.py')
    
    def extract_code_elements(self, content: str) -> Dict[str, Any]:
        import re
        functions = re.findall(r'def\s+(\w+)\s*\(', content)
        classes = re.findall(r'class\s+(\w+)', content)
        imports = re.findall(r'(?:from\s+[\w.]+\s+)?import\s+([\w.,\s]+)', content)
        return {
            "functions": functions,
            "classes": classes,
            "imports": [i.strip() for i in imports] if isinstance(imports, list) else imports.split(','),
            "decorators": re.findall(r'@\w+', content)
        }
    
    def normalize_syntax(self, content: str) -> str:
        import re
        content = re.sub(r'\s+', ' ', content)
        return content.strip()


class JavaScriptAdapter(LanguageAdapter):
    """JavaScript语言适配器"""
    
    def get_language_name(self) -> str:
        return "javascript"
    
    def can_handle(self, file_path: str, content: str) -> bool:
        return file_path.endswith(('.js', '.jsx'))
    
    def extract_code_elements(self, content: str) -> Dict[str, Any]:
        import re
        functions = re.findall(r'(?:function\s+(\w+)|const\s+(\w+)\s*=|(\w+)\s*\([^)]*\)\s*\{)', content)
        functions = [f[0] or f[1] or f[2] for f in functions]
        classes = re.findall(r'class\s+(\w+)', content)
        imports = re.findall(r'import\s+.*?from\s+[\'"](.+?)[\'"]', content)
        return {
            "functions": functions,
            "classes": classes,
            "imports": imports
        }
    
    def normalize_syntax(self, content: str) -> str:
        import re
        content = re.sub(r';\s*', ';\n', content)
        return content


class TypeScriptAdapter(LanguageAdapter):
    """TypeScript语言适配器"""
    
    def get_language_name(self) -> str:
        return "typescript"
    
    def can_handle(self, file_path: str, content: str) -> bool:
        return file_path.endswith(('.ts', '.tsx'))
    
    def extract_code_elements(self, content: str) -> Dict[str, Any]:
        import re
        interfaces = re.findall(r'interface\s+(\w+)', content)
        types = re.findall(r'type\s+(\w+)', content)
        classes = re.findall(r'class\s+(\w+)', content)
        functions = re.findall(r'(?:function|const|let)\s+(\w+)\s*[=:]\s*(?:async\s*)?\(', content)
        return {
            "interfaces": interfaces,
            "types": types,
            "classes": classes,
            "functions": functions
        }
    
    def normalize_syntax(self, content: str) -> str:
        import re
        content = re.sub(r':\s*(\w+)\s*=', ': ', content)
        return content


class JavaAdapter(LanguageAdapter):
    """Java语言适配器"""
    
    def get_language_name(self) -> str:
        return "java"
    
    def can_handle(self, file_path: str, content: str) -> bool:
        return file_path.endswith('.java')
    
    def extract_code_elements(self, content: str) -> Dict[str, Any]:
        import re
        classes = re.findall(r'(?:public|private|protected)?\s*class\s+(\w+)', content)
        interfaces = re.findall(r'(?:public|private|protected)?\s*interface\s+(\w+)', content)
        methods = re.findall(r'(?:public|private|protected)?\s*(?:static)?\s*\w+\s+(\w+)\s*\(', content)
        imports = re.findall(r'import\s+([\w.]+);', content)
        return {
            "classes": classes,
            "interfaces": interfaces,
            "methods": methods,
            "imports": imports
        }
    
    def normalize_syntax(self, content: str) -> str:
        import re
        content = re.sub(r'\{\s*', ' {\n', content)
        content = re.sub(r'\}\s*', '}\n', content)
        return content


class GoAdapter(LanguageAdapter):
    """Go语言适配器"""
    
    def get_language_name(self) -> str:
        return "go"
    
    def can_handle(self, file_path: str, content: str) -> bool:
        return file_path.endswith('.go')
    
    def extract_code_elements(self, content: str) -> Dict[str, Any]:
        import re
        functions = re.findall(r'func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)\s*\(', content)
        structs = re.findall(r'type\s+(\w+)\s+struct', content)
        interfaces = re.findall(r'type\s+(\w+)\s+interface', content)
        imports = re.findall(r'import\s+"([^"]+)"', content)
        return {
            "functions": functions,
            "structs": structs,
            "interfaces": interfaces,
            "imports": imports
        }
    
    def normalize_syntax(self, content: str) -> str:
        import re
        content = re.sub(r'func\s+', 'func ', content)
        return content


class RustAdapter(LanguageAdapter):
    """Rust语言适配器"""
    
    def get_language_name(self) -> str:
        return "rust"
    
    def can_handle(self, file_path: str, content: str) -> bool:
        return file_path.endswith('.rs')
    
    def extract_code_elements(self, content: str) -> Dict[str, Any]:
        import re
        functions = re.findall(r'fn\s+(\w+)', content)
        structs = re.findall(r'struct\s+(\w+)', content)
        enums = re.findall(r'enum\s+(\w+)', content)
        impls = re.findall(r'impl\s+(?:<[^>]+>\s+)?(\w+)', content)
        return {
            "functions": functions,
            "structs": structs,
            "enums": enums,
            "impls": impls
        }
    
    def normalize_syntax(self, content: str) -> str:
        return content.strip()


class CppAdapter(LanguageAdapter):
    """C++语言适配器"""
    
    def get_language_name(self) -> str:
        return "cpp"
    
    def can_handle(self, file_path: str, content: str) -> bool:
        return file_path.endswith(('.cpp', '.cc', '.cxx', '.hpp', '.hxx'))
    
    def extract_code_elements(self, content: str) -> Dict[str, Any]:
        import re
        classes = re.findall(r'class\s+(\w+)', content)
        functions = re.findall(r'(?:void|int|float|double|bool|string|auto)\s+(\w+)\s*\(', content)
        templates = re.findall(r'template\s*<[^>]+>', content)
        namespaces = re.findall(r'namespace\s+(\w+)', content)
        return {
            "classes": classes,
            "functions": functions,
            "templates": len(templates),
            "namespaces": namespaces
        }
    
    def normalize_syntax(self, content: str) -> str:
        import re
        content = re.sub(r'#include\s*<([^>]+)>', r'#include<\1>', content)
        return content


class CSharpAdapter(LanguageAdapter):
    """C#语言适配器"""
    
    def get_language_name(self) -> str:
        return "csharp"
    
    def can_handle(self, file_path: str, content: str) -> bool:
        return file_path.endswith('.cs')
    
    def extract_code_elements(self, content: str) -> Dict[str, Any]:
        import re
        classes = re.findall(r'(?:public|private|protected)?\s*class\s+(\w+)', content)
        interfaces = re.findall(r'interface\s+(\w+)', content)
        methods = re.findall(r'(?:public|private|protected)?\s*(?:static)?\s*\w+\s+(\w+)\s*\(', content)
        namespaces = re.findall(r'namespace\s+([\w.]+)', content)
        return {
            "classes": classes,
            "interfaces": interfaces,
            "methods": methods,
            "namespaces": namespaces
        }
    
    def normalize_syntax(self, content: str) -> str:
        return content


class AdaptationResult:
    """语言适配结果"""
    
    def __init__(self):
        self.language: str = ""
        self.adapter_name: str = ""
        self.processed_files: List[Dict[str, Any]] = []
        self.failed_files: List[str] = []
        self.code_elements: Dict[str, List[str]] = {}
        self.adaptation_stats: Dict[str, int] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "language": self.language,
            "adapter_name": self.adapter_name,
            "processed_files_count": len(self.processed_files),
            "failed_files_count": len(self.failed_files),
            "code_elements": self.code_elements,
            "adaptation_stats": self.adaptation_stats
        }


class LanguageAdapterLayer:
    """
    多语言适配分发层【V3.1升级】
    
    负责识别源码语言类型，并分发给对应的语言适配器进行处理。
    V3.1版本新增对Go、Rust等新兴语言的支持，增强了对现代开发语言的处理能力。
    
    核心功能：
    - 多语言识别和分类
    - 语言特定代码元素提取
    - 语法规范化处理
    - 统一代码表示
    
    Attributes:
        description: 层的功能描述
        input_type: 输入数据类型 (PipelineContext)
        output_type: 输出数据类型 (AdaptationResult)
    """
    
    description: str = "多语言适配分发层 - 识别语言类型并分发给对应适配器"
    input_type: str = "PipelineContext"
    output_type: str = "AdaptationResult"
    
    def __init__(self):
        """初始化语言适配器"""
        self._adapters: Dict[str, LanguageAdapter] = {
            'python': PythonAdapter(),
            'javascript': JavaScriptAdapter(),
            'typescript': TypeScriptAdapter(),
            'java': JavaAdapter(),
            'go': GoAdapter(),
            'rust': RustAdapter(),
            'cpp': CppAdapter(),
            'csharp': CSharpAdapter(),
        }
        self._default_adapter: Optional[LanguageAdapter] = None
    
    def process(self, context: Any) -> AdaptationResult:
        """
        执行语言适配和分发
        
        Args:
            context: PipelineContext对象，包含以下预期字段：
                - scanned_files: 扫描到的文件列表 (List[Dict])
                    - 每个Dict包含: file_path, content, language等
                - preprocessed_files: 预处理后的文件列表 (List[PreprocessedFile], 可选)
                - adapter_options: 适配器选项 (dict, 可选)
                    - languages: 指定要处理的语言列表 (List[str])
                    - extract_elements: 是否提取代码元素 (默认True)
                    - normalize_syntax: 是否规范化语法 (默认True)
                    - custom_adapters: 自定义适配器映射 (dict)
        
        Returns:
            AdaptationResult: 语言适配结果，包含：
                - language: 主要语言类型
                - adapter_name: 使用的适配器名称
                - processed_files: 已处理的文件列表
                - failed_files: 处理失败的文件列表
                - code_elements: 提取的代码元素（函数、类等）
                - adaptation_stats: 适配统计信息
        
        Process Flow:
            1. 获取待处理文件列表
            2. 识别每种文件的语言类型
            3. 选择对应的语言适配器
            4. 调用适配器提取代码元素
            5. 规范化代码语法
            6. 汇总统计信息
        
        Example:
            >>> layer = LanguageAdapterLayer()
            >>> ctx = create_context()
            >>> ctx.set('scanned_files', [{'file_path': 'main.py', 'content': '...'}])
            >>> result = layer.process(ctx)
            >>> print(f"主要语言: {result.language}")
        """
        scanned_files = context.get('scanned_files', [])
        preprocessed_files = context.get('preprocessed_files', [])
        adapter_options = context.get('adapter_options', {})
        
        languages_filter = adapter_options.get('languages', [])
        extract_elements = adapter_options.get('extract_elements', True)
        normalize_syntax = adapter_options.get('normalize_syntax', True)
        custom_adapters = adapter_options.get('custom_adapters', {})
        
        for lang, adapter in custom_adapters.items():
            self._adapters[lang] = adapter
        
        result = AdaptationResult()
        
        if preprocessed_files:
            files_to_process = [(pf.file_path, pf.cleaned_content, pf.language) for pf in preprocessed_files]
        else:
            files_to_process = [
                (f.get('file_path', ''), f.get('content', ''), f.get('language', ''))
                for f in scanned_files
            ]
        
        language_counts: Dict[str, int] = {}
        
        for file_path, content, language in files_to_process:
            if not file_path or not content:
                continue
            
            if languages_filter and language not in languages_filter:
                continue
            
            adapter = self._get_adapter(file_path, content, language)
            if not adapter:
                result.failed_files.append(file_path)
                continue
            
            try:
                if extract_elements:
                    elements = adapter.extract_code_elements(content)
                    self._merge_code_elements(result.code_elements, elements)
                
                if normalize_syntax:
                    normalized = adapter.normalize_syntax(content)
                    result.processed_files.append({
                        "file_path": file_path,
                        "language": adapter.get_language_name(),
                        "normalized_content": normalized,
                        "elements": elements if extract_elements else {}
                    })
                else:
                    result.processed_files.append({
                        "file_path": file_path,
                        "language": adapter.get_language_name(),
                        "content": content,
                        "elements": elements if extract_elements else {}
                    })
                
                lang = adapter.get_language_name()
                language_counts[lang] = language_counts.get(lang, 0) + 1
                
            except Exception as e:
                result.failed_files.append(file_path)
        
        if language_counts:
            result.language = max(language_counts.items(), key=lambda x: x[1])[0]
        
        if result.processed_files:
            result.adapter_name = result.processed_files[0].get('language', 'unknown')
        
        result.adaptation_stats = {
            "total_files": len(result.processed_files) + len(result.failed_files),
            "processed": len(result.processed_files),
            "failed": len(result.failed_files),
            "languages": language_counts
        }
        
        context.set('adaptation_result', result)
        context.set('primary_language', result.language)
        context.set('code_elements', result.code_elements)
        
        return result
    
    def _get_adapter(self, file_path: str, content: str, 
                     language: str) -> Optional[LanguageAdapter]:
        """获取合适的适配器"""
        if language and language in self._adapters:
            adapter = self._adapters[language]
            if adapter.can_handle(file_path, content):
                return adapter
        
        for adapter in self._adapters.values():
            if adapter.can_handle(file_path, content):
                return adapter
        
        return self._default_adapter
    
    def _merge_code_elements(self, target: Dict[str, List[str]], 
                            source: Dict[str, Any]):
        """合并代码元素"""
        for key, value in source.items():
            if key not in target:
                target[key] = []
            if isinstance(value, list):
                target[key].extend(value)
    
    def register_adapter(self, language: str, adapter: LanguageAdapter):
        """注册自定义语言适配器"""
        self._adapters[language] = adapter
    
    def unregister_adapter(self, language: str):
        """注销语言适配器"""
        if language in self._adapters:
            del self._adapters[language]
    
    def get_supported_languages(self) -> List[str]:
        """获取支持的语言列表"""
        return list(self._adapters.keys())
    
    def set_default_adapter(self, adapter: LanguageAdapter):
        """设置默认适配器"""
        self._default_adapter = adapter
    
    def get_adapter_stats(self) -> Dict[str, Any]:
        """获取适配器统计信息"""
        return {
            "supported_languages": len(self._adapters),
            "language_list": list(self._adapters.keys()),
            "has_default_adapter": self._default_adapter is not None
        }
