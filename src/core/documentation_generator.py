"""
文档自动化系统
======================================================================

自动生成API文档、架构文档、使用指南
"""

import os
import inspect
from typing import Dict, List, Any, Optional, Type
from pathlib import Path
import json


class DocumentationGenerator:
    """文档生成器"""
    
    def __init__(self, output_dir: str = "docs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.documentation: Dict[str, Any] = {
            "modules": [],
            "classes": [],
            "functions": []
        }
    
    def document_module(self, module_obj: Any, module_name: str) -> Dict:
        """文档化模块"""
        doc = {
            "name": module_name,
            "docstring": inspect.getdoc(module_obj) or "",
            "functions": [],
            "classes": []
        }
        
        for name, member in inspect.getmembers(module_obj):
            if inspect.isfunction(member):
                func_doc = self._document_function(member, name)
                doc["functions"].append(func_doc)
            elif inspect.isclass(member):
                class_doc = self._document_class(member, name)
                doc["classes"].append(class_doc)
        
        self.documentation["modules"].append(doc)
        return doc
    
    def _document_function(self, func: Any, name: str) -> Dict:
        """文档化函数"""
        signature = str(inspect.signature(func)) if hasattr(inspect, 'signature') else ""
        return {
            "name": name,
            "signature": signature,
            "docstring": inspect.getdoc(func) or ""
        }
    
    def _document_class(self, cls: Type, name: str) -> Dict:
        """文档化类"""
        methods = []
        for attr_name, attr in inspect.getmembers(cls):
            if inspect.isfunction(attr) or inspect.ismethod(attr):
                methods.append({
                    "name": attr_name,
                    "docstring": inspect.getdoc(attr) or ""
                })
        
        return {
            "name": name,
            "docstring": inspect.getdoc(cls) or "",
            "methods": methods
        }
    
    def generate_markdown_summary(self, title: str = "Documentation") -> str:
        """生成Markdown摘要"""
        lines = [f"# {title}", ""]
        
        for module in self.documentation["modules"]:
            lines.append(f"## Module: {module['name']}")
            lines.append(f"")
            if module['docstring']:
                lines.append(module['docstring'])
                lines.append("")
            
            if module['classes']:
                lines.append("### Classes:")
                for cls in module['classes']:
                    lines.append(f"- **{cls['name']}**: {cls['docstring'][:100] if cls['docstring'] else 'No description'}")
                lines.append("")
            
            if module['functions']:
                lines.append("### Functions:")
                for func in module['functions']:
                    lines.append(f"- **{func['name']}**{func['signature']}")
                lines.append("")
        
        return "\n".join(lines)
    
    def save_json(self, filename: str = "documentation.json") -> None:
        """保存为JSON"""
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.documentation, f, indent=2, ensure_ascii=False)
    
    def save_markdown(self, title: str = "Documentation", filename: str = "documentation.md") -> None:
        """保存为Markdown"""
        filepath = self.output_dir / filename
        content = self.generate_markdown_summary(title)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)


def create_documentation_generator(output_dir: str = "docs") -> DocumentationGenerator:
    """创建文档生成器"""
    return DocumentationGenerator(output_dir)


if __name__ == "__main__":
    generator = create_documentation_generator()
    print("✅ 文档生成器初始化完成")
