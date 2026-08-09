"""
AdvancedSyntaxValidation - 高级语法验证系统
==========================================

完整的语法验证框架，支持：
- Python AST完整遍历和分析
- 语法错误检测和定位
- 代码质量规则检查
- 最佳实践建议
- 多级别错误报告

功能模块：
1. Python AST遍历器 - 完整语法树分析
2. 语法错误检测器 - 错误定位和分类
3. 代码质量规则引擎 - 最佳实践检查
4. 错误报告生成器 - 格式化错误输出
5. 验证结果聚合器 - 批量文件验证

作者：PathTestSystem
版本：2.0.0
"""

import ast
import os
from typing import Dict, List, Any, Optional, Set, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
from pathlib import Path


class ErrorSeverity(Enum):
    """错误严重级别"""
    SYNTAX_ERROR = "syntax_error"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    STYLE = "style"


class ErrorCategory(Enum):
    """错误类别"""
    SYNTAX = "syntax"
    NAMING = "naming"
    IMPORTS = "imports"
    COMPLEXITY = "complexity"
    STYLE = "style"
    SECURITY = "security"
    PERFORMANCE = "performance"
    BEST_PRACTICE = "best_practice"


@dataclass
class ValidationError:
    """验证错误"""
    error_id: str
    severity: ErrorSeverity
    category: ErrorCategory
    message: str
    file_path: str
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    end_line: Optional[int] = None
    end_column: Optional[int] = None
    suggestion: Optional[str] = None
    code_snippet: Optional[str] = None
    rule_id: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'error_id': self.error_id,
            'severity': self.severity.value,
            'category': self.category.value,
            'message': self.message,
            'file_path': self.file_path,
            'line_number': self.line_number,
            'column_number': self.column_number,
            'suggestion': self.suggestion,
            'rule_id': self.rule_id
        }


@dataclass
class ValidationResult:
    """验证结果"""
    file_path: str
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    info_messages: List[ValidationError]
    summary: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_error_count(self) -> int:
        return len(self.errors)
    
    def get_warning_count(self) -> int:
        return len(self.warnings)
    
    def to_summary(self) -> Dict:
        return {
            'file': self.file_path,
            'valid': self.is_valid,
            'errors': self.get_error_count(),
            'warnings': self.get_warning_count(),
            'info': len(self.info_messages),
            'summary': self.summary
        }


class PythonASTTraverser:
    """
    Python AST遍历器
    ================
    
    完整遍历Python抽象语法树，提取所有代码元素
    """
    
    def __init__(self):
        self.current_file = None
        self.current_source = None
        self.all_nodes = []
        self.node_count = defaultdict(int)
        self.line_to_node = {}
    
    def traverse(self, tree: ast.AST, source: str, file_path: str) -> Dict[str, Any]:
        """
        遍历AST树
        
        Args:
            tree: AST树
            source: 源代码
            file_path: 文件路径
        
        Returns:
            遍历结果
        """
        self.current_file = file_path
        self.current_source = source
        
        result = {
            'functions': [],
            'classes': [],
            'imports': [],
            'async_functions': [],
            'decorators': [],
            'global_variables': [],
            'constants': [],
            'complex_functions': [],
            'nested_depth': 0
        }
        
        for node in ast.walk(tree):
            self.all_nodes.append(node)
            self.node_count[type(node).__name__] += 1
            
            if hasattr(node, 'lineno'):
                self.line_to_node[node.lineno] = node
            
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_info = self._extract_function_info(node)
                if isinstance(node, ast.AsyncFunctionDef):
                    result['async_functions'].append(func_info)
                else:
                    result['functions'].append(func_info)
                
                if self._is_complex_function(node):
                    result['complex_functions'].append(func_info['name'])
            
            elif isinstance(node, ast.ClassDef):
                result['classes'].append(self._extract_class_info(node))
            
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                result['imports'].extend(self._extract_imports(node))
            
            elif isinstance(node, ast.Assign):
                result['global_variables'].extend(self._extract_assignments(node))
        
        result['max_nesting_depth'] = self._calculate_max_nesting(tree)
        
        return result
    
    def _extract_function_info(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> Dict:
        """提取函数信息"""
        return {
            'name': node.name,
            'lineno': node.lineno,
            'end_lineno': node.end_lineno,
            'args': self._extract_args(node.args),
            'decorators': [d.attr if isinstance(d, ast.Attribute) else d.id if isinstance(d, ast.Name) else str(d) 
                          for d in node.decorator_list],
            'docstring': ast.get_docstring(node),
            'returns': ast.unparse(node.returns) if node.returns else None,
            'is_async': isinstance(node, ast.AsyncFunctionDef),
            'is_method': any(isinstance(parent, ast.ClassDef) for parent in ast.walk(type(node))),
            'complexity': self._calculate_function_complexity(node)
        }
    
    def _extract_class_info(self, node: ast.ClassDef) -> Dict:
        """提取类信息"""
        return {
            'name': node.name,
            'lineno': node.lineno,
            'end_lineno': node.end_lineno,
            'bases': [ast.unparse(base) for base in node.bases],
            'decorators': [d.attr if isinstance(d, ast.Attribute) else d.id if isinstance(d, ast.Name) else str(d) 
                          for d in node.decorator_list],
            'docstring': ast.get_docstring(node),
            'methods': [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        }
    
    def _extract_imports(self, node: ast.Import | ast.ImportFrom) -> List[Dict]:
        """提取导入信息"""
        imports = []
        
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append({
                    'module': alias.name,
                    'name': alias.asname or alias.name,
                    'lineno': node.lineno
                })
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for alias in node.names:
                imports.append({
                    'module': module,
                    'name': alias.name,
                    'asname': alias.asname,
                    'lineno': node.lineno
                })
        
        return imports
    
    def _extract_assignments(self, node: ast.Assign) -> List[Dict]:
        """提取赋值信息"""
        return [{
            'targets': [ast.unparse(target) for target in node.targets],
            'value': ast.unparse(node.value) if node.value else None,
            'lineno': node.lineno
        }]
    
    def _extract_args(self, args: ast.arguments) -> Dict:
        """提取函数参数"""
        return {
            'args': [arg.arg for arg in args.args],
            'vararg': args.vararg.arg if args.vararg else None,
            'kwarg': args.kwarg.arg if args.kwarg else None,
            'defaults': len(args.defaults),
            'kwonlyargs': [arg.arg for arg in args.kwonlyargs]
        }
    
    def _is_complex_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        """判断是否为复杂函数"""
        complexity = self._calculate_function_complexity(node)
        return complexity > 10
    
    def _calculate_function_complexity(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
        """计算函数复杂度"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _calculate_max_nesting(self, tree: ast.AST) -> int:
        """计算最大嵌套深度"""
        max_depth = [0]
        current_depth = [0]
        
        def visit_node(node: ast.AST, depth: int):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.With, ast.ExceptHandler)):
                new_depth = depth + 1
                current_depth[0] = max(current_depth[0], new_depth)
                max_depth[0] = max(max_depth[0], new_depth)
            else:
                new_depth = depth
            
            for child in ast.iter_child_nodes(node):
                visit_node(child, new_depth)
        
        visit_node(tree, 0)
        return max_depth[0]


class SyntaxErrorDetector:
    """
    语法错误检测器
    ==============
    
    检测Python语法错误
    """
    
    def __init__(self):
        self.error_count = 0
    
    def detect_syntax_errors(self, source: str, file_path: str) -> List[ValidationError]:
        """
        检测语法错误
        
        Args:
            source: 源代码
            file_path: 文件路径
        
        Returns:
            错误列表
        """
        errors = []
        
        try:
            ast.parse(source)
        except SyntaxError as e:
            error = ValidationError(
                error_id=f"syn_{self.error_count}",
                severity=ErrorSeverity.SYNTAX_ERROR,
                category=ErrorCategory.SYNTAX,
                message=f"Syntax error: {e.msg}",
                file_path=file_path,
                line_number=e.lineno,
                column_number=e.offset,
                code_snippet=self._get_code_snippet(source, e.lineno),
                suggestion=self._get_syntax_suggestion(e)
            )
            errors.append(error)
            self.error_count += 1
        except Exception as e:
            error = ValidationError(
                error_id=f"syn_{self.error_count}",
                severity=ErrorSeverity.ERROR,
                category=ErrorCategory.SYNTAX,
                message=f"Parse error: {str(e)}",
                file_path=file_path
            )
            errors.append(error)
            self.error_count += 1
        
        return errors
    
    def _get_code_snippet(self, source: str, line_number: int, context: int = 2) -> str:
        """获取代码片段"""
        lines = source.split('\n')
        start = max(0, line_number - context - 1)
        end = min(len(lines), line_number + context)
        
        snippet = []
        for i, line in enumerate(lines[start:end], start + 1):
            marker = ">>> " if i == line_number else "    "
            snippet.append(f"{marker}{line.rstrip()}")
        
        return '\n'.join(snippet)
    
    def _get_syntax_suggestion(self, error: SyntaxError) -> str:
        """获取语法建议"""
        suggestions = {
            'invalid syntax': 'Check for missing colons, parentheses, or incorrect indentation',
            'expected ': 'Check for missing colons after function/class definitions',
            'unterminated': 'Check for unclosed quotes or brackets',
            'EOL while scanning': 'Check for unclosed quotes',
            'unexpected EOF': 'Check for unclosed brackets or parentheses'
        }
        
        for key, suggestion in suggestions.items():
            if key in error.msg:
                return suggestion
        
        return 'Review the syntax near the error location'


class CodeQualityRuleEngine:
    """
    代码质量规则引擎
    =================
    
    应用代码质量规则，检查最佳实践
    """
    
    def __init__(self):
        self.rules = self._init_rules()
        self.violations = []
    
    def _init_rules(self) -> Dict[str, Dict]:
        """初始化规则"""
        return {
            'S001': {
                'name': 'Line too long',
                'severity': ErrorSeverity.STYLE,
                'category': ErrorCategory.STYLE,
                'check': self._check_line_length,
                'max_length': 120
            },
            'S002': {
                'name': 'Trailing whitespace',
                'severity': ErrorSeverity.STYLE,
                'category': ErrorCategory.STYLE,
                'check': self._check_trailing_whitespace
            },
            'S003': {
                'name': 'Missing docstring',
                'severity': ErrorSeverity.INFO,
                'category': ErrorCategory.BEST_PRACTICE,
                'check': self._check_missing_docstring
            },
            'S004': {
                'name': 'Complex function',
                'severity': ErrorSeverity.WARNING,
                'category': ErrorCategory.COMPLEXITY,
                'check': self._check_complex_function,
                'max_complexity': 10
            },
            'S005': {
                'name': 'Too many arguments',
                'severity': ErrorSeverity.WARNING,
                'category': ErrorCategory.COMPLEXITY,
                'check': self._check_too_many_arguments,
                'max_args': 5
            },
            'S006': {
                'name': 'Unused import',
                'severity': ErrorSeverity.WARNING,
                'category': ErrorCategory.IMPORTS,
                'check': self._check_unused_import
            },
            'S007': {
                'name': 'Dangerous default argument',
                'severity': ErrorSeverity.WARNING,
                'category': ErrorCategory.BEST_PRACTICE,
                'check': self._check_dangerous_default
            },
            'S008': {
                'name': 'Shadowing built-in',
                'severity': ErrorSeverity.WARNING,
                'category': ErrorCategory.NAMING,
                'check': self._check_shadowing_builtin
            },
            'S009': {
                'name': 'Invalid variable naming',
                'severity': ErrorSeverity.STYLE,
                'category': ErrorCategory.NAMING,
                'check': self._check_variable_naming
            }
        }
    
    def apply_rules(self, tree: ast.AST, source: str, file_path: str, 
                   traversed: Dict) -> List[ValidationError]:
        """
        应用所有规则
        
        Args:
            tree: AST树
            source: 源代码
            file_path: 文件路径
            traversed: 遍历结果
        
        Returns:
            违规列表
        """
        violations = []
        
        for rule_id, rule in self.rules.items():
            try:
                errors = rule['check'](tree, source, file_path, traversed)
                violations.extend(errors)
            except Exception:
                pass
        
        return violations
    
    def _check_line_length(self, tree: ast.AST, source: str, 
                          file_path: str, traversed: Dict) -> List[ValidationError]:
        """检查行长度"""
        errors = []
        max_length = self.rules['S001']['max_length']
        
        for i, line in enumerate(source.split('\n'), 1):
            if len(line) > max_length:
                errors.append(ValidationError(
                    error_id='S001',
                    severity=ErrorSeverity.STYLE,
                    category=ErrorCategory.STYLE,
                    message=f'Line too long ({len(line)} > {max_length} characters)',
                    file_path=file_path,
                    line_number=i
                ))
        
        return errors
    
    def _check_trailing_whitespace(self, tree: ast.AST, source: str, 
                                   file_path: str, traversed: Dict) -> List[ValidationError]:
        """检查尾随空格"""
        errors = []
        
        for i, line in enumerate(source.split('\n'), 1):
            if line.rstrip() != line.rstrip('\n'):
                errors.append(ValidationError(
                    error_id='S002',
                    severity=ErrorSeverity.STYLE,
                    category=ErrorCategory.STYLE,
                    message='Trailing whitespace detected',
                    file_path=file_path,
                    line_number=i
                ))
        
        return errors
    
    def _check_missing_docstring(self, tree: ast.AST, source: str, 
                                  file_path: str, traversed: Dict) -> List[ValidationError]:
        """检查缺失文档字符串"""
        errors = []
        
        for func in traversed.get('functions', []):
            if not func.get('docstring'):
                errors.append(ValidationError(
                    error_id='S003',
                    severity=ErrorSeverity.INFO,
                    category=ErrorCategory.BEST_PRACTICE,
                    message=f'Missing docstring in function "{func["name"]}"',
                    file_path=file_path,
                    line_number=func['lineno'],
                    suggestion='Add a docstring to describe the function purpose'
                ))
        
        for cls in traversed.get('classes', []):
            if not cls.get('docstring'):
                errors.append(ValidationError(
                    error_id='S003',
                    severity=ErrorSeverity.INFO,
                    category=ErrorCategory.BEST_PRACTICE,
                    message=f'Missing docstring in class "{cls["name"]}"',
                    file_path=file_path,
                    line_number=cls['lineno'],
                    suggestion='Add a docstring to describe the class purpose'
                ))
        
        return errors
    
    def _check_complex_function(self, tree: ast.AST, source: str, 
                               file_path: str, traversed: Dict) -> List[ValidationError]:
        """检查复杂函数"""
        errors = []
        max_complexity = self.rules['S004']['max_complexity']
        
        for func in traversed.get('functions', []):
            complexity = func.get('complexity', 0)
            if complexity > max_complexity:
                errors.append(ValidationError(
                    error_id='S004',
                    severity=ErrorSeverity.WARNING,
                    category=ErrorCategory.COMPLEXITY,
                    message=f'Function "{func["name"]}" is too complex (complexity: {complexity})',
                    file_path=file_path,
                    line_number=func['lineno'],
                    suggestion=f'Consider refactoring to reduce complexity (target: {max_complexity})'
                ))
        
        return errors
    
    def _check_too_many_arguments(self, tree: ast.AST, source: str, 
                                  file_path: str, traversed: Dict) -> List[ValidationError]:
        """检查参数过多"""
        errors = []
        max_args = self.rules['S005']['max_args']
        
        for func in traversed.get('functions', []):
            args = func.get('args', {})
            arg_count = len(args.get('args', [])) + len(args.get('kwonlyargs', []))
            
            if arg_count > max_args:
                errors.append(ValidationError(
                    error_id='S005',
                    severity=ErrorSeverity.WARNING,
                    category=ErrorCategory.COMPLEXITY,
                    message=f'Function "{func["name"]}" has too many arguments ({arg_count} > {max_args})',
                    file_path=file_path,
                    line_number=func['lineno'],
                    suggestion=f'Consider using a configuration object or splitting the function'
                ))
        
        return errors
    
    def _check_unused_import(self, tree: ast.AST, source: str, 
                            file_path: str, traversed: Dict) -> List[ValidationError]:
        """检查未使用的导入"""
        errors = []
        
        all_imports = set(imp['name'] for imp in traversed.get('imports', []))
        used_names = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name):
                    used_names.add(node.value.id)
        
        for imp in traversed.get('imports', []):
            name = imp['name']
            if name not in used_names and not any(u in used_names for u in name.split('.')):
                errors.append(ValidationError(
                    error_id='S006',
                    severity=ErrorSeverity.WARNING,
                    category=ErrorCategory.IMPORTS,
                    message=f'Import "{name}" may be unused',
                    file_path=file_path,
                    line_number=imp['lineno'],
                    suggestion='Consider removing unused imports or using them in the code'
                ))
        
        return errors
    
    def _check_dangerous_default(self, tree: ast.AST, source: str, 
                                 file_path: str, traversed: Dict) -> List[ValidationError]:
        """检查危险默认参数"""
        errors = []
        dangerous_defaults = {'[]', '{}", set()'}
        
        for func in traversed.get('functions', []):
            args = func.get('args', {})
            defaults = args.get('defaults', [])
            
            if defaults > 0:
                for i, default in enumerate(defaults):
                    default_str = ast.unparse(default) if hasattr(ast, 'unparse') else ''
                    if default_str in dangerous_defaults:
                        errors.append(ValidationError(
                            error_id='S007',
                            severity=ErrorSeverity.WARNING,
                            category=ErrorCategory.BEST_PRACTICE,
                            message=f'Dangerous default value in function "{func["name"]}"',
                            file_path=file_path,
                            line_number=func['lineno'],
                            suggestion='Use None as default and initialize inside the function'
                        ))
        
        return errors
    
    def _check_shadowing_builtin(self, tree: ast.AST, source: str, 
                                 file_path: str, traversed: Dict) -> List[ValidationError]:
        """检查遮蔽内置函数"""
        errors = []
        builtins = {'list', 'dict', 'set', 'str', 'int', 'float', 'bool', 'type', 'object'}
        
        for assignment in traversed.get('global_variables', []):
            for target in assignment.get('targets', []):
                if target in builtins:
                    errors.append(ValidationError(
                        error_id='S008',
                        severity=ErrorSeverity.WARNING,
                        category=ErrorCategory.NAMING,
                        message=f'Variable name "{target}" shadows builtin',
                        file_path=file_path,
                        line_number=assignment['lineno'],
                        suggestion=f'Use a different name to avoid shadowing the builtin'
                    ))
        
        return errors
    
    def _check_variable_naming(self, tree: ast.AST, source: str, 
                               file_path: str, traversed: Dict) -> List[ValidationError]:
        """检查变量命名"""
        errors = []
        
        for assignment in traversed.get('global_variables', []):
            for target in assignment.get('targets', []):
                if isinstance(target, ast.Name):
                    name = target.id
                    if name[0].isupper() and name[0] not in ('_',):
                        errors.append(ValidationError(
                            error_id='S009',
                            severity=ErrorSeverity.STYLE,
                            category=ErrorCategory.NAMING,
                            message=f'Variable name "{name}" should be lowercase',
                            file_path=file_path,
                            line_number=assignment['lineno'],
                            suggestion='Use snake_case for variable names'
                        ))
        
        return errors


class ValidationReporter:
    """
    验证报告生成器
    ==============
    
    生成格式化的验证报告
    """
    
    def __init__(self, format: str = 'text'):
        self.format = format
    
    def generate_report(self, result: ValidationResult) -> str:
        """
        生成报告
        
        Args:
            result: 验证结果
        
        Returns:
            报告文本
        """
        if self.format == 'text':
            return self._generate_text_report(result)
        elif self.format == 'json':
            return self._generate_json_report(result)
        elif self.format == 'compact':
            return self._generate_compact_report(result)
        else:
            return self._generate_text_report(result)
    
    def _generate_text_report(self, result: ValidationResult) -> str:
        """生成文本报告"""
        lines = []
        
        lines.append("=" * 80)
        lines.append(f"Syntax Validation Report: {result.file_path}")
        lines.append("=" * 80)
        lines.append(f"Valid: {result.is_valid}")
        lines.append(f"Errors: {result.get_error_count()}")
        lines.append(f"Warnings: {result.get_warning_count()}")
        lines.append(f"Info: {len(result.info_messages)}")
        lines.append("=" * 80)
        
        if result.errors:
            lines.append("\nERRORS:")
            lines.append("-" * 80)
            for error in result.errors:
                lines.append(self._format_error(error))
        
        if result.warnings:
            lines.append("\nWARNINGS:")
            lines.append("-" * 80)
            for warning in result.warnings:
                lines.append(self._format_error(warning))
        
        if result.info_messages:
            lines.append("\nINFO:")
            lines.append("-" * 80)
            for info in result.info_messages[:10]:
                lines.append(self._format_error(info))
            if len(result.info_messages) > 10:
                lines.append(f"... and {len(result.info_messages) - 10} more info messages")
        
        return '\n'.join(lines)
    
    def _generate_json_report(self, result: ValidationResult) -> str:
        """生成JSON报告"""
        import json
        
        return json.dumps({
            'file': result.file_path,
            'valid': result.is_valid,
            'errors': [e.to_dict() for e in result.errors],
            'warnings': [w.to_dict() for w in result.warnings],
            'info': [i.to_dict() for i in result.info_messages],
            'summary': result.summary
        }, indent=2)
    
    def _generate_compact_report(self, result: ValidationResult) -> str:
        """生成紧凑报告"""
        return f"{result.file_path}: {result.get_error_count()} errors, {result.get_warning_count()} warnings"
    
    def _format_error(self, error: ValidationError) -> str:
        """格式化错误"""
        lines = []
        
        location = f"{error.file_path}:{error.line_number or '?'}"
        if error.column_number:
            location += f":{error.column_number}"
        
        lines.append(f"  [{error.error_id}] {error.severity.value.upper()}: {error.message}")
        lines.append(f"    Location: {location}")
        
        if error.code_snippet:
            lines.append(f"    Code:\n{error.code_snippet}")
        
        if error.suggestion:
            lines.append(f"    Suggestion: {error.suggestion}")
        
        return '\n'.join(lines)


class AdvancedSyntaxValidator:
    """
    高级语法验证器 - 主控制器
    ==========================
    
    整合所有语法验证组件
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.traverser = PythonASTTraverser()
        self.error_detector = SyntaxErrorDetector()
        self.rule_engine = CodeQualityRuleEngine()
        self.reporter = ValidationReporter()
        
        self.validation_count = 0
    
    def validate_file(self, file_path: str) -> ValidationResult:
        """
        验证文件
        
        Args:
            file_path: 文件路径
        
        Returns:
            验证结果
        """
        self.validation_count += 1
        
        if not os.path.exists(file_path):
            return ValidationResult(
                file_path=file_path,
                is_valid=False,
                errors=[ValidationError(
                    error_id='F001',
                    severity=ErrorSeverity.ERROR,
                    category=ErrorCategory.SYNTAX,
                    message=f'File not found: {file_path}',
                    file_path=file_path
                )],
                warnings=[],
                info_messages=[],
                summary={}
            )
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
        except Exception as e:
            return ValidationResult(
                file_path=file_path,
                is_valid=False,
                errors=[ValidationError(
                    error_id='F002',
                    severity=ErrorSeverity.ERROR,
                    category=ErrorCategory.SYNTAX,
                    message=f'Cannot read file: {str(e)}',
                    file_path=file_path
                )],
                warnings=[],
                info_messages=[],
                summary={}
            )
        
        syntax_errors = self.error_detector.detect_syntax_errors(source, file_path)
        
        if syntax_errors:
            return ValidationResult(
                file_path=file_path,
                is_valid=False,
                errors=syntax_errors,
                warnings=[],
                info_messages=[],
                summary={'syntax_errors': len(syntax_errors)}
            )
        
        try:
            tree = ast.parse(source)
        except Exception:
            return ValidationResult(
                file_path=file_path,
                is_valid=False,
                errors=[],
                warnings=[],
                info_messages=[],
                summary={'parse_error': True}
            )
        
        traversed = self.traverser.traverse(tree, source, file_path)
        
        rule_violations = self.rule_engine.apply_rules(tree, source, file_path, traversed)
        
        errors = [v for v in rule_violations if v.severity == ErrorSeverity.ERROR]
        warnings = [v for v in rule_violations if v.severity == ErrorSeverity.WARNING]
        info = [v for v in rule_violations if v.severity in (ErrorSeverity.INFO, ErrorSeverity.STYLE)]
        
        summary = {
            'functions': len(traversed['functions']),
            'async_functions': len(traversed['async_functions']),
            'classes': len(traversed['classes']),
            'imports': len(traversed['imports']),
            'complex_functions': len(traversed['complex_functions']),
            'max_nesting': traversed.get('max_nesting_depth', 0),
            'total_lines': source.count('\n') + 1,
            'rule_violations': len(rule_violations)
        }
        
        return ValidationResult(
            file_path=file_path,
            is_valid=True,
            errors=errors,
            warnings=warnings,
            info_messages=info,
            summary=summary,
            metadata=traversed
        )
    
    def validate_files(self, file_paths: List[str]) -> List[ValidationResult]:
        """
        批量验证文件
        
        Args:
            file_paths: 文件路径列表
        
        Returns:
            验证结果列表
        """
        results = []
        
        for file_path in file_paths:
            result = self.validate_file(file_path)
            results.append(result)
        
        return results
    
    def generate_report(self, result: ValidationResult, format: str = 'text') -> str:
        """
        生成报告
        
        Args:
            result: 验证结果
            format: 报告格式
        
        Returns:
            报告文本
        """
        reporter = ValidationReporter(format)
        return reporter.generate_report(result)


def create_syntax_validator(config: Optional[Dict] = None) -> AdvancedSyntaxValidator:
    """
    创建语法验证器工厂函数
    
    Args:
        config: 配置字典
    
    Returns:
        AdvancedSyntaxValidator实例
    """
    return AdvancedSyntaxValidator(config)


if __name__ == "__main__":
    validator = create_syntax_validator()
    
    test_files = [
        '/workspace/path_test_system/src/core/engine_integrated.py',
        '/workspace/path_test_system/src/core/error_recovery.py'
    ]
    
    existing_files = [f for f in test_files if os.path.exists(f)]
    
    print("=" * 80)
    print("Advanced Syntax Validation Test")
    print("=" * 80)
    
    for file_path in existing_files:
        print(f"\nValidating: {file_path}")
        print("-" * 80)
        
        result = validator.validate_file(file_path)
        
        report = validator.generate_report(result, format='text')
        print(report)
        print()
    
    print("=" * 80)
    print("Validation Complete")
    print("=" * 80)
