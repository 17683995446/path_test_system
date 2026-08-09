"""
Layer 4: Natural Language Parser Layer (自然语言命令解析层)

该层负责将用户的自然语言输入解析为结构化的测试意图和命令。
"""

from typing import Any, Dict, List, Optional, Tuple
from .layer_1_entry import PipelineContext


class IntentType:
    """意图类型定义"""
    GENERATE_TEST = "generate_test"
    MODIFY_TEST = "modify_test"
    DELETE_TEST = "delete_test"
    RUN_TEST = "run_test"
    QUERY_INFO = "query_info"
    OPTIMIZE_TEST = "optimize_test"
    UNKNOWN = "unknown"


class NaturalLanguageParserLayer:
    """
    自然语言命令解析层

    负责将用户的自然语言输入解析为结构化的测试意图和命令，包括：
    - 意图识别（Intent Detection）
    - 实体提取（Entity Extraction）
    - 参数解析（Parameter Parsing）
    - 语义角色标注（Semantic Role Labeling）

    Attributes:
        description: 层的功能描述
        input_type: 输入数据类型
        output_type: 输出数据类型
    """

    description: str = "自然语言命令解析层 - 将自然语言输入解析为结构化测试意图和命令"
    input_type: str = "PipelineContext"
    output_type: str = "PipelineContext"

    INTENT_KEYWORDS = {
        IntentType.GENERATE_TEST: ["生成", "创建", "编写", "新增", "generate", "create"],
        IntentType.MODIFY_TEST: ["修改", "更新", "调整", "编辑", "modify", "update"],
        IntentType.DELETE_TEST: ["删除", "移除", "清理", "delete", "remove"],
        IntentType.RUN_TEST: ["运行", "执行", "测试", "跑", "run", "execute"],
        IntentType.QUERY_INFO: ["查询", "查看", "获取", "搜索", "query", "check"],
        IntentType.OPTIMIZE_TEST: ["优化", "改进", "提升", "完善", "optimize", "improve"]
    }

    def __init__(self):
        self._intent_patterns = self._compile_intent_patterns()

    def process(self, context: PipelineContext) -> PipelineContext:
        """
        处理自然语言解析

        Args:
            context: PipelineContext对象，包含：
                - request_id: 请求唯一标识符
                - user_input: 用户输入的自然语言文本
                - metadata: 附加元数据

        Returns:
            PipelineContext: 更新后的上下文，包含解析结果：
                - intent: 识别的用户意图类型
                - entities: 提取的实体列表
                - parameters: 解析的参数字典
                - semantic_roles: 语义角色标注结果
                - confidence: 解析置信度

        Example:
            >>> layer = NaturalLanguageParserLayer()
            >>> ctx = layer.process(pipeline_context)
            >>> print(ctx.metadata["intent"])  # "generate_test"
            >>> print(ctx.metadata["entities"])  # [{"type": "function", "value": "login"}]
        """
        user_input = context.user_input

        intent = self._detect_intent(user_input)
        entities = self._extract_entities(user_input)
        parameters = self._parse_parameters(user_input, intent, entities)
        semantic_roles = self._label_semantic_roles(user_input)
        confidence = self._calculate_confidence(intent, entities, parameters)

        context.metadata["intent"] = intent
        context.metadata["entities"] = entities
        context.metadata["parameters"] = parameters
        context.metadata["semantic_roles"] = semantic_roles
        context.metadata["parse_confidence"] = confidence
        context.metadata["original_input"] = user_input

        return context

    def _compile_intent_patterns(self) -> Dict[str, List[str]]:
        """编译意图模式"""
        return self.INTENT_KEYWORDS.copy()

    def _detect_intent(self, text: str) -> str:
        """检测用户意图"""
        text_lower = text.lower()
        intent_scores = {}

        for intent, keywords in self.INTENT_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                intent_scores[intent] = score

        if not intent_scores:
            return IntentType.UNKNOWN

        return max(intent_scores.items(), key=lambda x: x[1])[0]

    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """提取实体"""
        entities = []

        function_patterns = [
            r'([a-zA-Z_][a-zA-Z0-9_]*)[\s]*[（\(]',
            r'函数[\s]*([a-zA-Z_][a-zA-Z0-9_]*)',
            r'method[\s]+([a-zA-Z_][a-zA-Z0-9_]*)'
        ]

        import re
        for pattern in function_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                entities.append({
                    "type": "function",
                    "value": match.group(1) if match.lastindex else match.group(0),
                    "position": match.span()
                })

        file_patterns = [
            r'([a-zA-Z_][a-zA-Z0-9_]*\.(py|js|java))',
            r'文件[\s]+([a-zA-Z_][a-zA-Z0-9_]*\.(py|js|java))'
        ]

        for pattern in file_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                entities.append({
                    "type": "file",
                    "value": match.group(0),
                    "position": match.span()
                })

        return entities

    def _parse_parameters(
        self,
        text: str,
        intent: str,
        entities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """解析参数"""
        parameters = {
            "intent": intent,
            "targets": [e["value"] for e in entities if e["type"] in ["function", "file"]],
            "options": {}
        }

        import re

        coverage_match = re.search(r'覆盖率[：:\s]*(\d+(?:\.\d+)?)', text)
        if coverage_match:
            parameters["options"]["coverage"] = float(coverage_match.group(1))

        priority_match = re.search(r'优先级[：:\s]*(高|中|低|high|medium|low)', text)
        if priority_match:
            parameters["options"]["priority"] = priority_match.group(1)

        return parameters

    def _label_semantic_roles(self, text: str) -> Dict[str, Any]:
        """语义角色标注"""
        return {
            "action": self._detect_intent(text),
            "theme": "test_cases",
            "agent": "user",
            "recipient": self._extract_targets(text)
        }

    def _extract_targets(self, text: str) -> List[str]:
        """提取目标"""
        import re
        pattern = r'([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)'
        return re.findall(pattern, text)

    def _calculate_confidence(
        self,
        intent: str,
        entities: List[Dict[str, Any]],
        parameters: Dict[str, Any]
    ) -> float:
        """计算解析置信度"""
        confidence = 0.5

        if intent != IntentType.UNKNOWN:
            confidence += 0.3

        if entities:
            confidence += 0.15

        if parameters.get("targets"):
            confidence += 0.05

        return min(confidence, 1.0)
