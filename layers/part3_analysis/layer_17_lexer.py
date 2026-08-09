import os
"""
Layer 17: LexerLayer - 词法分析Token化层

本层负责将预处理后的源代码转换为Token序列，为后续的AST构建和语法分析做准备。
支持多种编程语言的词法分析，采用状态机驱动的Token识别算法。
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum, auto
import re


class TokenType(Enum):
    """Token类型枚举"""
    KEYWORD = auto()
    IDENTIFIER = auto()
    OPERATOR = auto()
    DELIMITER = auto()
    LITERAL_STRING = auto()
    LITERAL_NUMBER = auto()
    LITERAL_BOOLEAN = auto()
    COMMENT = auto()
    WHITESPACE = auto()
    NEWLINE = auto()
    EOF = auto()
    UNKNOWN = auto()


@dataclass
class Token:
    """Token数据结构"""
    type: TokenType
    value: str
    line: int
    column: int
    length: int
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "type": self.type.name,
            "value": self.value,
            "line": self.line,
            "column": self.column,
            "length": self.length,
            "metadata": self.metadata
        }


class LexerLayer:
    """词法分析Token化层

    功能描述：
        - 将源代码文本转换为标准化的Token序列
        - 识别关键字、标识符、运算符、分隔符等语法元素
        - 过滤注释和空白符（可选保留）
        - 记录Token的位置信息（行号、列号）
        - 支持多种编程语言的词法规则

    输入类型：
        - 预处理后的源代码（字符串或字符串列表）

    输出类型：
        - Token序列（List[Token]）
        - 每个Token包含类型、值、位置等元信息

    使用场景：
        - 为AST构建层提供标准化的Token流
        - 支持语法高亮和代码可视化
        - 为静态分析工具提供词法基础

    V3.1升级点：
        - 增加对Python、JavaScript、Java、Go等多语言支持
        - 优化Unicode标识符识别
        - 增加对现代语言特性的Token支持（如f-string、template literal）
    """

    description: str = "词法分析Token化层 - 将源代码转换为Token序列"
    input_type: str = "源代码字符串或字符串列表"
    output_type: str = "List[Token] - Token序列"

    KEYWORDS = {
        'python': {
            'and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue',
            'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from',
            'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not',
            'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield',
            'True', 'False', 'None'
        },
        'javascript': {
            'break', 'case', 'catch', 'continue', 'debugger', 'default', 'delete',
            'do', 'else', 'finally', 'for', 'function', 'if', 'in', 'instanceof',
            'new', 'return', 'switch', 'this', 'throw', 'try', 'typeof', 'var',
            'void', 'while', 'with', 'class', 'const', 'enum', 'export', 'extends',
            'import', 'super', 'implements', 'interface', 'let', 'package', 'private',
            'protected', 'public', 'static', 'yield', 'async', 'await', 'of', 'true', 'false', 'null', 'undefined'
        },
        'java': {
            'abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch',
            'char', 'class', 'const', 'continue', 'default', 'do', 'double',
            'else', 'enum', 'extends', 'final', 'finally', 'float', 'for',
            'goto', 'if', 'implements', 'import', 'instanceof', 'int', 'interface',
            'long', 'native', 'new', 'package', 'private', 'protected', 'public',
            'return', 'short', 'static', 'strictfp', 'super', 'switch', 'synchronized',
            'this', 'throw', 'throws', 'transient', 'try', 'void', 'volatile', 'while',
            'true', 'false', 'null', 'var', 'record'
        }
    }

    OPERATORS = {
        '+', '-', '*', '/', '%', '=', '==', '!=', '<', '>', '<=', '>=',
        '&&', '||', '!', '&', '|', '^', '~', '<<', '>>', '>>>',
        '++', '--', '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=', '<<=', '>>=',
        '->', '=>', '?', ':', '::', '...', '**', '//', '**=', '//='
    }

    DELIMITERS = {
        '(', ')', '[', ']', '{', '}', ';', ',', '.', '@', '#', '$'
    }

    def __init__(self):
        """初始化词法分析器"""
        self.current_language = 'python'
        self.preserve_whitespace = False
        self.preserve_comments = False
        self.tokens: List[Token] = []
        self.position = 0
        self.line = 1
        self.column = 1

    def set_language(self, language: str):
        """设置编程语言

        Args:
            language: 目标语言（python, javascript, java, go等）
        """
        if language in self.KEYWORDS:
            self.current_language = language
        else:
            self.current_language = 'python'

    def set_options(self, preserve_whitespace: bool = False, preserve_comments: bool = False):
        """设置词法分析选项

        Args:
            preserve_whitespace: 是否保留空白符Token
            preserve_comments: 是否保留注释Token
        """
        self.preserve_whitespace = preserve_whitespace
        self.preserve_comments = preserve_comments

    def process(self, context) -> List[Token]:
        """处理源代码，生成Token序列

        Args:
            context: PipelineContext对象，包含预处理后的源代码

        Returns:
            List[Token]: Token序列，包含所有识别出的Token

        Raises:
            ValueError: 当源代码为空或格式错误时
            LexerError: 当词法分析过程中遇到无法识别的字符时
        """
        if not context.has('preprocessed_source'):
            source = context.get('source', '')
        else:
            source = context.get('preprocessed_source', '')

        if not source:
            raise ValueError("LexerLayer: 源代码为空")

        if isinstance(source, list):
            source = '\n'.join(source)

        self._reset_state()
        self.tokens = []

        source_chars = list(source)
        source_length = len(source_chars)

        while self.position < source_length:
            char = source_chars[self.position]

            if char in '\t ':
                self._handle_whitespace(source_chars)
            elif char == '\n':
                self._handle_newline()
            elif char == '#' and self.current_language == 'python':
                self._handle_python_comment(source_chars)
            elif char in '"\'':
                self._handle_string_literal(source_chars)
            elif char.isdigit():
                self._handle_number(source_chars)
            elif char.isalpha() or char == '_' or ord(char) > 127:
                self._handle_identifier(source_chars)
            elif char in self.OPERATORS or self._starts_with_operator(source_chars):
                self._handle_operator(source_chars)
            elif char in self.DELIMITERS:
                self._handle_delimiter(source_chars)
            else:
                self._handle_unknown(source_chars)

        self.tokens.append(Token(
            type=TokenType.EOF,
            value='',
            line=self.line,
            column=self.column,
            length=0
        ))

        context.set('lexer_tokens', self.tokens)
        context.set('lexer_language', self.current_language)
        context.set('token_count', len(self.tokens))

        return self.tokens

    def _reset_state(self):
        """重置词法分析器状态"""
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []

    def _handle_whitespace(self, source_chars: List[str]):
        """处理空白符"""
        start_column = self.column
        value = ''

        while self.position < len(source_chars) and source_chars[self.position] in '\t ':
            value += source_chars[self.position]
            self.position += 1
            self.column += 1

        if self.preserve_whitespace:
            self.tokens.append(Token(
                type=TokenType.WHITESPACE,
                value=value,
                line=self.line,
                column=start_column,
                length=len(value)
            ))

    def _handle_newline(self):
        """处理换行符"""
        self.tokens.append(Token(
            type=TokenType.NEWLINE,
            value='\n',
            line=self.line,
            column=self.column,
            length=1
        ))
        self.line += 1
        self.column = 1
        self.position += 1

    def _handle_python_comment(self, source_chars: List[str]):
        """处理Python注释"""
        start_line = self.line
        start_column = self.column
        value = ''

        while self.position < len(source_chars) and source_chars[self.position] != '\n':
            value += source_chars[self.position]
            self.position += 1
            self.column += 1

        if self.preserve_comments:
            self.tokens.append(Token(
                type=TokenType.COMMENT,
                value=value,
                line=start_line,
                column=start_column,
                length=len(value),
                metadata={'language': 'python'}
            ))

    def _handle_string_literal(self, source_chars: List[str]):
        """处理字符串字面量"""
        start_line = self.line
        start_column = self.column
        quote_char = source_chars[self.position]
        value = quote_char
        self.position += 1
        self.column += 1

        if self.position < len(source_chars) - 1 and source_chars[self.position] == quote_char:
            if source_chars[self.position + 1] == quote_char:
                value += '""'
                self.position += 2
                self.column += 2
                while self.position < len(source_chars) - 2:
                    if (source_chars[self.position] == quote_char and
                        source_chars[self.position + 1] == quote_char and
                        source_chars[self.position + 2] == quote_char):
                        value += '"""'
                        self.position += 3
                        self.column += 3
                        break
                    value += source_chars[self.position]
                    if source_chars[self.position] == '\n':
                        self.line += 1
                        self.column = 1
                    else:
                        self.column += 1
                    self.position += 1

        while self.position < len(source_chars) and source_chars[self.position] != quote_char:
            if source_chars[self.position] == '\\':
                if self.position + 1 < len(source_chars):
                    value += source_chars[self.position]
                    self.position += 1
                    self.column += 1
            value += source_chars[self.position]
            if source_chars[self.position] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1

        if self.position < len(source_chars):
            value += source_chars[self.position]
            self.position += 1
            self.column += 1

        self.tokens.append(Token(
            type=TokenType.LITERAL_STRING,
            value=value,
            line=start_line,
            column=start_column,
            length=len(value),
            metadata={'quote_type': quote_char}
        ))

    def _handle_number(self, source_chars: List[str]):
        """处理数字字面量"""
        start_line = self.line
        start_column = self.column
        value = ''
        num_type = 'int'

        while self.position < len(source_chars) and source_chars[self.position] in '0123456789':
            value += source_chars[self.position]
            self.position += 1
            self.column += 1

        if self.position < len(source_chars) and source_chars[self.position] == '.':
            if self.position + 1 < len(source_chars) and source_chars[self.position + 1].isdigit():
                num_type = 'float'
                value += source_chars[self.position]
                self.position += 1
                self.column += 1
                while self.position < len(source_chars) and source_chars[self.position] in '0123456789':
                    value += source_chars[self.position]
                    self.position += 1
                    self.column += 1

        if self.position < len(source_chars) and source_chars[self.position] in 'eE':
            num_type = 'float'
            value += source_chars[self.position]
            self.position += 1
            self.column += 1
            if self.position < len(source_chars) and source_chars[self.position] in '+-':
                value += source_chars[self.position]
                self.position += 1
                self.column += 1
            while self.position < len(source_chars) and source_chars[self.position] in '0123456789':
                value += source_chars[self.position]
                self.position += 1
                self.column += 1

        if self.position < len(source_chars) and source_chars[self.position] in 'xXbBoO':
            num_type = 'hex' if source_chars[self.position] in 'xX' else 'binary' if source_chars[self.position] in 'bB' else 'octal'
            value += source_chars[self.position]
            self.position += 1
            self.column += 1
            while self.position < len(source_chars) and source_chars[self.position] in '0123456789abcdefABCDEF':
                value += source_chars[self.position]
                self.position += 1
                self.column += 1

        self.tokens.append(Token(
            type=TokenType.LITERAL_NUMBER,
            value=value,
            line=start_line,
            column=start_column,
            length=len(value),
            metadata={'num_type': num_type}
        ))

    def _handle_identifier(self, source_chars: List[str]):
        """处理标识符和关键字"""
        start_line = self.line
        start_column = self.column
        value = ''

        while self.position < len(source_chars):
            char = source_chars[self.position]
            if char.isalnum() or char == '_' or ord(char) > 127:
                value += char
                self.position += 1
                self.column += 1
            else:
                break

        if value in self.KEYWORDS.get(self.current_language, set()):
            token_type = TokenType.KEYWORD
        elif value in ('True', 'False', 'true', 'false'):
            token_type = TokenType.LITERAL_BOOLEAN
        else:
            token_type = TokenType.IDENTIFIER

        self.tokens.append(Token(
            type=token_type,
            value=value,
            line=start_line,
            column=start_column,
            length=len(value)
        ))

    def _starts_with_operator(self, source_chars: List[str]) -> bool:
        """检查是否以运算符开头"""
        remaining = ''.join(source_chars[self.position:])
        for op in sorted(self.OPERATORS, key=len, reverse=True):
            if remaining.startswith(op):
                return True
        return False

    def _handle_operator(self, source_chars: List[str]):
        """处理运算符"""
        start_line = self.line
        start_column = self.column
        remaining = ''.join(source_chars[self.position:])

        matched_op = None
        for op in sorted(self.OPERATORS, key=len, reverse=True):
            if remaining.startswith(op):
                matched_op = op
                break

        if matched_op:
            self.tokens.append(Token(
                type=TokenType.OPERATOR,
                value=matched_op,
                line=start_line,
                column=start_column,
                length=len(matched_op)
            ))
            self.position += len(matched_op)
            self.column += len(matched_op)
        else:
            self._handle_unknown(source_chars)

    def _handle_delimiter(self, source_chars: List[str]):
        """处理分隔符"""
        char = source_chars[self.position]
        self.tokens.append(Token(
            type=TokenType.DELIMITER,
            value=char,
            line=self.line,
            column=self.column,
            length=1
        ))
        self.position += 1
        self.column += 1

    def _handle_unknown(self, source_chars: List[str]):
        """处理未知字符"""
        char = source_chars[self.position]
        self.tokens.append(Token(
            type=TokenType.UNKNOWN,
            value=char,
            line=self.line,
            column=self.column,
            length=1,
            metadata={'error': f'无法识别的字符: {repr(char)}'}
        ))
        self.position += 1
        self.column += 1

    def get_token_statistics(self) -> Dict[str, Any]:
        """获取Token统计信息

        Returns:
            Dict[str, Any]: Token统计信息，包括各类型Token数量等
        """
        stats = {
            'total_tokens': len(self.tokens),
            'token_types': {}
        }

        for token in self.tokens:
            type_name = token.type.name
            stats['token_types'][type_name] = stats['token_types'].get(type_name, 0) + 1

        return stats


    def _read_project_sources(self, project_path: str) -> str:
        """读取项目所有源代码"""
        sources = []
        try:
            for root, dirs, files in os.walk(project_path):
                dirs[:] = [d for d in dirs if not d.startswith('.')
                          and d not in ['__pycache__', 'venv', 'test']]
                for file in files:
                    if file.endswith('.py') and not file.startswith('test'):
                        try:
                            file_path = os.path.join(root, file)
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                sources.append(f.read())
                        except:
                            pass
        except:
            pass
        return '\n'.join(sources)
