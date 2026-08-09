"""
Layer 24: BusinessRecognizeLayer - 业务场景识别层

本层负责从代码中识别业务场景和业务逻辑模式，帮助理解代码的业务含义。
基于函数语义、命名模式、代码结构等特征进行业务场景的智能识别。
"""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import defaultdict
import re


class BusinessDomain(Enum):
    """业务领域枚举"""
    ECOMMERCE = auto()
    USER_MANAGEMENT = auto()
    DATA_ANALYTICS = auto()
    FILE_MANAGEMENT = auto()
    COMMUNICATION = auto()
    PAYMENT = auto()
    SOCIAL_NETWORK = auto()
    SYSTEM_ADMIN = auto()
    API_GATEWAY = auto()
    DATABASE_OPERATION = auto()
    CACHE_MANAGEMENT = auto()
    LOGGING_MONITORING = auto()
    SECURITY_AUTH = auto()
    CONFIG_MANAGEMENT = auto()
    BUSINESS_WORKFLOW = auto()
    NOTIFICATION = auto()
    REPORTING = auto()
    IMPORT_EXPORT = auto()
    VALIDATION = auto()
    TRANSFORMATION = auto()
    UTILITY = auto()
    UNKNOWN = auto()


class BusinessScenario(Enum):
    """业务场景枚举"""
    USER_AUTHENTICATION = auto()
    USER_REGISTRATION = auto()
    PASSWORD_MANAGEMENT = auto()
    PRODUCT_CATALOG = auto()
    SHOPPING_CART = auto()
    ORDER_PROCESSING = auto()
    PAYMENT_PROCESSING = auto()
    INVENTORY_MANAGEMENT = auto()
    SHIPPING_LOGISTICS = auto()
    CUSTOMER_SERVICE = auto()
    DATA_IMPORT = auto()
    DATA_EXPORT = auto()
    REPORT_GENERATION = auto()
    NOTIFICATION_SENDING = auto()
    EMAIL_SENDING = auto()
    SMS_SENDING = auto()
    FILE_UPLOAD = auto()
    FILE_DOWNLOAD = auto()
    FILE_CONVERSION = auto()
    DATA_VALIDATION = auto()
    DATA_TRANSFORMATION = auto()
    DATA_AGGREGATION = auto()
    DATA_FILTERING = auto()
    SEARCH = auto()
    FILTERING = auto()
    SORTING = auto()
    PAGINATION = auto()
    CACHE_OPERATION = auto()
    SESSION_MANAGEMENT = auto()
    PERMISSION_CHECK = auto()
    AUDIT_LOGGING = auto()
    CONFIG_UPDATE = auto()
    HEALTH_CHECK = auto()
    METRICS_COLLECTION = auto()
    ERROR_HANDLING = auto()
    GRACEful_DEGRADATION = auto()
    RATE_LIMITING = auto()
    DATA_MIGRATION = auto()
    BACKUP_RESTORE = auto()
    API_VERSIONING = auto()
    WEBHOOK_PROCESSING = auto()
    ASYNC_TASK = auto()
    BATCH_PROCESSING = auto()
    UNKNOWN = auto()


class BusinessPattern(Enum):
    """业务模式枚举"""
    CRUD_OPERATION = auto()
    PAGINATION_QUERY = auto()
    FILTER_SORT = auto()
    CACHE_ASIDE = auto()
    EVENT_DRIVEN = auto()
    COMMAND_QUERY_SEPARATION = auto()
    TRANSACTION_MANAGEMENT = auto()
    RETRY_WITH_BACKOFF = auto()
    CIRCUIT_BREAKER = auto()
    BULK_OPERATION = auto()
    STREAM_PROCESSING = auto()
    SCHEMA_VALIDATION = auto()
    AUDIT_TRAIL = auto()
    SOFT_DELETE = auto()
    OPTIMISTIC_LOCKING = auto()
    PAGINATION_CURSOR = auto()


@dataclass
class BusinessEntity:
    """业务实体信息

    Attributes:
        name: 实体名称
        entity_type: 实体类型（如user, order, product等）
        fields: 实体字段列表
        relationships: 关联关系
        business_rules: 业务规则
        lifecycle: 生命周期阶段
    """
    name: str
    entity_type: str
    fields: List[Dict[str, Any]] = field(default_factory=list)
    relationships: List[Dict[str, str]] = field(default_factory=list)
    business_rules: List[str] = field(default_factory=list)
    lifecycle: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "entity_type": self.entity_type,
            "fields": self.fields,
            "relationships": self.relationships,
            "business_rules": self.business_rules,
            "lifecycle": self.lifecycle
        }


@dataclass
class BusinessScenarioInfo:
    """业务场景信息

    Attributes:
        scenario: 业务场景类型
        confidence: 置信度（0-1）
        matched_functions: 匹配的函数列表
        key_entities: 涉及的业务实体
        business_rules: 业务规则
        workflows: 工作流程
        dependencies: 依赖关系
        metadata: 其他元信息
    """
    scenario: BusinessScenario
    confidence: float
    matched_functions: List[str] = field(default_factory=list)
    key_entities: List[BusinessEntity] = field(default_factory=list)
    business_rules: List[str] = field(default_factory=list)
    workflows: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "scenario": self.scenario.name,
            "confidence": self.confidence,
            "matched_functions": self.matched_functions,
            "key_entities": [entity.to_dict() for entity in self.key_entities],
            "business_rules": self.business_rules,
            "workflows": self.workflows,
            "dependencies": self.dependencies,
            "metadata": self.metadata
        }


@dataclass
class BusinessRecognitionResult:
    """业务识别结果

    Attributes:
        primary_domain: 主要业务领域
        secondary_domains: 次要业务领域
        scenarios: 识别的业务场景列表
        entities: 业务实体列表
        patterns: 识别的业务模式
        relationships: 业务关系图
        test_recommendations: 测试建议
        complexity_assessment: 复杂度评估
        metadata: 其他元信息
    """
    primary_domain: BusinessDomain
    secondary_domains: List[BusinessDomain] = field(default_factory=list)
    scenarios: List[BusinessScenarioInfo] = field(default_factory=list)
    entities: List[BusinessEntity] = field(default_factory=list)
    patterns: List[BusinessPattern] = field(default_factory=list)
    relationships: Dict[str, List[str]] = field(default_factory=dict)
    test_recommendations: List[str] = field(default_factory=list)
    complexity_assessment: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "primary_domain": self.primary_domain.name,
            "secondary_domains": [d.name for d in self.secondary_domains],
            "scenarios": [s.to_dict() for s in self.scenarios],
            "entities": [e.to_dict() for e in self.entities],
            "patterns": [p.name for p in self.patterns],
            "relationships": self.relationships,
            "test_recommendations": self.test_recommendations,
            "complexity_assessment": self.complexity_assessment,
            "metadata": self.metadata
        }

    def get_scenario_by_type(self, scenario_type: BusinessScenario) -> Optional[BusinessScenarioInfo]:
        """根据类型获取场景信息

        Args:
            scenario_type: 场景类型

        Returns:
            Optional[BusinessScenarioInfo]: 找到的场景信息
        """
        for scenario_info in self.scenarios:
            if scenario_info.scenario == scenario_type:
                return scenario_info
        return None

    def get_high_confidence_scenarios(self, threshold: float = 0.7) -> List[BusinessScenarioInfo]:
        """获取高置信度场景

        Args:
            threshold: 置信度阈值

        Returns:
            List[BusinessScenarioInfo]: 高置信度场景列表
        """
        return [s for s in self.scenarios if s.confidence >= threshold]


class BusinessRecognizeLayer:
    """业务场景识别层

    功能描述：
        - 从代码中识别业务领域和业务场景
        - 发现业务实体和实体关系
        - 识别业务模式和业务流程
        - 分析业务规则和约束条件
        - 生成业务相关的测试建议
        - 评估业务逻辑的复杂度
        - 支持业务术语的智能识别

    输入类型：
        - 函数切片列表（List[FunctionSlice]）
        - 函数语义列表（List[FunctionSemantic]）
        - AST节点（用于提取业务实体）

    输出类型：
        - BusinessRecognitionResult: 业务识别结果对象
        - 包含领域、场景、实体、模式等完整信息

    使用场景：
        - 帮助测试人员理解业务逻辑
        - 生成业务导向的测试用例
        - 识别测试覆盖的业务盲点
        - 支持业务层面的代码审查
        - 指导端到端测试场景设计

    V3.1升级点：
        - 增强对微服务架构的业务识别能力
        - 支持跨服务的业务流程识别
        - 提供更精确的业务实体提取算法
        - 增加对业务规则的自动发现
        - 支持业务领域知识的自动学习
    """

    description: str = "业务场景识别层 - 识别代码中的业务领域和场景"
    input_type: str = "List[FunctionSlice]、List[FunctionSemantic]和AST"
    output_type: str = "BusinessRecognitionResult - 业务识别结果"

    def __init__(self):
        """初始化业务场景识别层"""
        self.function_slices = []
        self.function_semantics = []
        self.domain_patterns = self._init_domain_patterns()
        self.scenario_keywords = self._init_scenario_keywords()
        self.entity_patterns = self._init_entity_patterns()
        self.business_patterns = self._init_business_patterns()

    def _init_domain_patterns(self) -> Dict[BusinessDomain, Dict[str, Any]]:
        """初始化领域识别模式

        Returns:
            Dict[BusinessDomain, Dict[str, Any]]: 领域模式字典
        """
        return {
            BusinessDomain.ECOMMERCE: {
                'keywords': ['product', 'order', 'cart', 'checkout', 'payment', 'invoice', 'shipping', 'discount', 'coupon', 'inventory'],
                'entities': ['Product', 'Order', 'Customer', 'Cart', 'Payment', 'Shipment'],
                'patterns': ['cart.*add', 'order.*create', 'payment.*process']
            },
            BusinessDomain.USER_MANAGEMENT: {
                'keywords': ['user', 'account', 'profile', 'role', 'permission', 'group', 'registration', 'login'],
                'entities': ['User', 'Account', 'Profile', 'Role', 'Permission', 'Group'],
                'patterns': ['user.*authenticate', 'user.*register', 'role.*assign']
            },
            BusinessDomain.PAYMENT: {
                'keywords': ['payment', 'transaction', 'refund', 'balance', 'wallet', 'card', 'billing'],
                'entities': ['Payment', 'Transaction', 'Wallet', 'Card', 'Billing'],
                'patterns': ['payment.*process', 'transaction.*create', 'refund.*request']
            },
            BusinessDomain.DATA_ANALYTICS: {
                'keywords': ['analytics', 'report', 'metric', 'dashboard', 'chart', 'visualization', 'aggregate'],
                'entities': ['Report', 'Metric', 'Dashboard', 'Chart'],
                'patterns': ['report.*generate', 'metric.*calculate', 'data.*aggregate']
            },
            BusinessDomain.FILE_MANAGEMENT: {
                'keywords': ['upload', 'download', 'file', 'document', 'storage', 'bucket'],
                'entities': ['File', 'Document', 'Storage', 'Folder'],
                'patterns': ['file.*upload', 'file.*download', 'file.*convert']
            },
            BusinessDomain.COMMUNICATION: {
                'keywords': ['message', 'notification', 'email', 'sms', 'chat', 'webhook'],
                'entities': ['Message', 'Notification', 'Email', 'SMS'],
                'patterns': ['message.*send', 'notification.*push', 'email.*send']
            },
            BusinessDomain.SOCIAL_NETWORK: {
                'keywords': ['friend', 'follow', 'post', 'comment', 'like', 'share', 'timeline'],
                'entities': ['Post', 'Comment', 'Follow', 'Like', 'User'],
                'patterns': ['post.*create', 'comment.*add', 'user.*follow']
            },
            BusinessDomain.SYSTEM_ADMIN: {
                'keywords': ['config', 'setting', 'monitor', 'health', 'status', 'metric', 'log'],
                'entities': ['Config', 'Setting', 'Health', 'Metric'],
                'patterns': ['config.*update', 'health.*check', 'metric.*collect']
            },
            BusinessDomain.API_GATEWAY: {
                'keywords': ['route', 'endpoint', 'proxy', 'gateway', 'middleware', 'rate'],
                'entities': ['Route', 'Endpoint', 'Middleware'],
                'patterns': ['route.*forward', 'middleware.*apply', 'rate.*limit']
            },
            BusinessDomain.DATABASE_OPERATION: {
                'keywords': ['query', 'insert', 'update', 'delete', 'select', 'transaction'],
                'entities': ['Table', 'Index', 'View'],
                'patterns': ['db.*query', 'data.*persist', 'transaction.*commit']
            }
        }

    def _init_scenario_keywords(self) -> Dict[BusinessScenario, Dict[str, Any]]:
        """初始化场景关键词

        Returns:
            Dict[BusinessScenario, Dict[str, Any]]: 场景关键词字典
        """
        return {
            BusinessScenario.USER_AUTHENTICATION: {
                'keywords': ['login', 'authenticate', 'logout', 'session', 'token', 'jwt', 'oauth'],
                'weight': 1.0
            },
            BusinessScenario.USER_REGISTRATION: {
                'keywords': ['register', 'signup', 'create_account', 'verification'],
                'weight': 1.0
            },
            BusinessScenario.PRODUCT_CATALOG: {
                'keywords': ['product', 'catalog', 'category', 'search', 'filter'],
                'weight': 0.9
            },
            BusinessScenario.SHOPPING_CART: {
                'keywords': ['cart', 'add', 'remove', 'update', 'checkout'],
                'weight': 1.0
            },
            BusinessScenario.ORDER_PROCESSING: {
                'keywords': ['order', 'create', 'status', 'cancel', 'complete'],
                'weight': 1.0
            },
            BusinessScenario.PAYMENT_PROCESSING: {
                'keywords': ['payment', 'pay', 'charge', 'transaction', 'refund'],
                'weight': 1.0
            },
            BusinessScenario.FILE_UPLOAD: {
                'keywords': ['upload', 'file', 'storage', 'multipart'],
                'weight': 1.0
            },
            BusinessScenario.FILE_DOWNLOAD: {
                'keywords': ['download', 'file', 'export', 'stream'],
                'weight': 1.0
            },
            BusinessScenario.DATA_IMPORT: {
                'keywords': ['import', 'batch', 'upload', 'csv', 'excel'],
                'weight': 1.0
            },
            BusinessScenario.DATA_EXPORT: {
                'keywords': ['export', 'download', 'report', 'csv', 'pdf'],
                'weight': 1.0
            },
            BusinessScenario.REPORT_GENERATION: {
                'keywords': ['report', 'generate', 'pdf', 'chart', 'analytics'],
                'weight': 1.0
            },
            BusinessScenario.NOTIFICATION_SENDING: {
                'keywords': ['notification', 'push', 'send', 'deliver'],
                'weight': 1.0
            },
            BusinessScenario.DATA_VALIDATION: {
                'keywords': ['validate', 'check', 'verify', 'schema'],
                'weight': 0.8
            },
            BusinessScenario.SEARCH: {
                'keywords': ['search', 'query', 'find', 'match'],
                'weight': 0.9
            },
            BusinessScenario.PAGINATION: {
                'keywords': ['page', 'offset', 'limit', 'cursor', 'paginate'],
                'weight': 0.8
            },
            BusinessScenario.CACHE_OPERATION: {
                'keywords': ['cache', 'get', 'set', 'invalidate', 'ttl'],
                'weight': 1.0
            },
            BusinessScenario.PERMISSION_CHECK: {
                'keywords': ['permission', 'authorize', 'access', 'role', 'resource'],
                'weight': 1.0
            },
            BusinessScenario.AUDIT_LOGGING: {
                'keywords': ['audit', 'log', 'history', 'track', 'action'],
                'weight': 0.9
            }
        }

    def _init_entity_patterns(self) -> Dict[str, List[str]]:
        """初始化实体识别模式

        Returns:
            Dict[str, List[str]]: 实体模式字典
        """
        return {
            'User': ['user', 'account', 'customer', 'client', 'member'],
            'Product': ['product', 'item', 'goods', 'sku', 'article'],
            'Order': ['order', 'purchase', 'transaction', 'invoice'],
            'Payment': ['payment', 'transaction', 'refund', 'charge'],
            'Category': ['category', 'type', 'classification', 'tag'],
            'Address': ['address', 'location', 'shipping_address', 'billing_address'],
            'Review': ['review', 'rating', 'feedback', 'comment'],
            'Media': ['image', 'video', 'file', 'attachment', 'document'],
            'Configuration': ['config', 'setting', 'preference', 'option'],
            'Log': ['log', 'event', 'audit', 'history']
        }

    def _init_business_patterns(self) -> Dict[BusinessPattern, Dict[str, Any]]:
        """初始化业务模式

        Returns:
            Dict[BusinessPattern, Dict[str, Any]]: 业务模式字典
        """
        return {
            BusinessPattern.CRUD_OPERATION: {
                'keywords': ['create', 'read', 'update', 'delete', 'save', 'get', 'list'],
                'weight': 1.0
            },
            BusinessPattern.PAGINATION_QUERY: {
                'keywords': ['page', 'offset', 'limit', 'size', 'paginate'],
                'weight': 0.8
            },
            BusinessPattern.CACHE_ASIDE: {
                'keywords': ['cache', 'get_or_set', 'invalidate', 'evict'],
                'weight': 1.0
            },
            BusinessPattern.EVENT_DRIVEN: {
                'keywords': ['event', 'publish', 'subscribe', 'handler', 'listener'],
                'weight': 1.0
            },
            BusinessPattern.TRANSACTION_MANAGEMENT: {
                'keywords': ['transaction', 'commit', 'rollback', 'atomic'],
                'weight': 1.0
            },
            BusinessPattern.RETRY_WITH_BACKOFF: {
                'keywords': ['retry', 'backoff', 'attempt', 'max_retries'],
                'weight': 1.0
            },
            BusinessPattern.CIRCUIT_BREAKER: {
                'keywords': ['circuit', 'breaker', 'failure', 'fallback', 'open'],
                'weight': 1.0
            },
            BusinessPattern.BULK_OPERATION: {
                'keywords': ['bulk', 'batch', 'mass', 'many'],
                'weight': 0.9
            },
            BusinessPattern.AUDIT_TRAIL: {
                'keywords': ['audit', 'log', 'history', 'created_by', 'updated_by'],
                'weight': 0.9
            },
            BusinessPattern.SOFT_DELETE: {
                'keywords': ['deleted', 'active', 'is_deleted', 'archive'],
                'weight': 0.8
            }
        }

    def process(self, context) -> BusinessRecognitionResult:
        """处理函数切片和语义，识别业务场景

        Args:
            context: PipelineContext对象，包含函数切片和语义信息

        Returns:
            BusinessRecognitionResult: 业务识别结果

        Raises:
            ValueError: 当输入数据不足时
        """
        if not context.has('function_slices'):
            raise ValueError("BusinessRecognizeLayer: 缺少函数切片列表")

        self.function_slices = context.get('function_slices')

        if context.has('function_semantics'):
            self.function_semantics = context.get('function_semantics')

        result = BusinessRecognitionResult(
            primary_domain=BusinessDomain.UNKNOWN,
            secondary_domains=[],
            scenarios=[],
            entities=[],
            patterns=[]
        )

        result.primary_domain, result.secondary_domains = self._recognize_domains()

        result.scenarios = self._recognize_scenarios()

        result.entities = self._extract_entities()

        result.patterns = self._recognize_business_patterns()

        result.relationships = self._build_relationships()

        result.test_recommendations = self._generate_test_recommendations(result)

        result.complexity_assessment = self._assess_complexity(result)

        context.set('business_recognition_result', result)
        context.set('business_recognition_complete', True)
        context.set('business_statistics', self._get_statistics(result))

        return result

    def _recognize_domains(self) -> tuple:
        """识别业务领域

        Returns:
            tuple: (主要领域, 次要领域列表)
        """
        domain_scores = defaultdict(float)

        for slice_item in self.function_slices:
            func_name = getattr(slice_item, 'name', '').lower()
            source_code = getattr(slice_item, 'source_code', '').lower()

            for domain, patterns in self.domain_patterns.items():
                score = 0.0
                keywords = patterns['keywords']

                for keyword in keywords:
                    if keyword in func_name:
                        score += 0.5
                    if keyword in source_code:
                        score += 0.3

                domain_scores[domain] += score

        if not domain_scores:
            return BusinessDomain.UNKNOWN, []

        sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)

        primary = sorted_domains[0][0] if sorted_domains[0][1] > 0 else BusinessDomain.UNKNOWN
        secondary = [domain for domain, score in sorted_domains[1:5] if score > 0]

        return primary, secondary

    def _recognize_scenarios(self) -> List[BusinessScenarioInfo]:
        """识别业务场景

        Returns:
            List[BusinessScenarioInfo]: 业务场景信息列表
        """
        scenario_matches = defaultdict(lambda: {'count': 0, 'functions': [], 'confidence': 0.0})

        for slice_item in self.function_slices:
            func_name = getattr(slice_item, 'name', '').lower()
            qualified_name = getattr(slice_item, 'qualified_name', '').lower()
            source_code = getattr(slice_item, 'source_code', '').lower()

            for scenario, config in self.scenario_keywords.items():
                keywords = config['keywords']
                weight = config['weight']

                match_count = 0
                for keyword in keywords:
                    if keyword in func_name or keyword in qualified_name:
                        match_count += 2
                    if keyword in source_code:
                        match_count += 1

                if match_count > 0:
                    scenario_matches[scenario]['count'] += match_count
                    scenario_matches[scenario]['functions'].append(getattr(slice_item, 'name', ''))
                    scenario_matches[scenario]['confidence'] += match_count * weight

        scenario_infos = []

        for scenario, matches in scenario_matches.items():
            if matches['count'] > 0:
                max_possible = len(self.function_slices) * 3
                confidence = min(1.0, matches['confidence'] / max_possible)

                if confidence >= 0.1:
                    scenario_info = BusinessScenarioInfo(
                        scenario=scenario,
                        confidence=confidence,
                        matched_functions=matches['functions']
                    )
                    scenario_infos.append(scenario_info)

        scenario_infos.sort(key=lambda x: x.confidence, reverse=True)

        return scenario_infos

    def _extract_entities(self) -> List[BusinessEntity]:
        """提取业务实体

        Returns:
            List[BusinessEntity]: 业务实体列表
        """
        entities = []

        entity_names = set()

        for slice_item in self.function_slices:
            source_code = getattr(slice_item, 'source_code', '')

            for entity_type, patterns in self.entity_patterns.items():
                for pattern in patterns:
                    if pattern in source_code.lower():
                        entity_name = entity_type.capitalize()
                        if entity_name not in entity_names:
                            entity = BusinessEntity(
                                name=entity_name,
                                entity_type=entity_type,
                                fields=self._extract_entity_fields(source_code, entity_type),
                                lifecycle=self._infer_entity_lifecycle(entity_type)
                            )
                            entities.append(entity)
                            entity_names.add(entity_name)

        return entities

    def _extract_entity_fields(self, source_code: str, entity_type: str) -> List[Dict[str, Any]]:
        """提取实体字段

        Args:
            source_code: 源代码
            entity_type: 实体类型

        Returns:
            List[Dict[str, Any]]: 字段列表
        """
        fields = []

        field_patterns = [
            r'(\w+)\s*:\s*(\w+)',
            r'(\w+)\s*=\s*(?:str|int|float|bool|list|dict)',
            r'self\.(\w+)\s*='
        ]

        for pattern in field_patterns:
            matches = re.findall(pattern, source_code)
            for match in matches:
                if len(match) >= 2:
                    field_name = match[0]
                    field_type = match[1] if len(match) > 1 else 'Any'

                    if field_name not in ['self', 'cls', 'def', 'class']:
                        fields.append({
                            'name': field_name,
                            'type': field_type
                        })

        return fields[:10]

    def _infer_entity_lifecycle(self, entity_type: str) -> List[str]:
        """推断实体生命周期

        Args:
            entity_type: 实体类型

        Returns:
            List[str]: 生命周期阶段列表
        """
        lifecycle_map = {
            'User': ['create', 'activate', 'update', 'deactivate', 'delete'],
            'Product': ['create', 'publish', 'update', 'unpublish', 'archive'],
            'Order': ['create', 'confirm', 'pay', 'ship', 'deliver', 'complete', 'cancel'],
            'Payment': ['create', 'process', 'complete', 'fail', 'refund'],
            'Message': ['create', 'send', 'delivered', 'read', 'archived']
        }

        return lifecycle_map.get(entity_type, ['create', 'update', 'delete'])

    def _recognize_business_patterns(self) -> List[BusinessPattern]:
        """识别业务模式

        Returns:
            List[BusinessPattern]: 业务模式列表
        """
        pattern_matches = defaultdict(int)

        for slice_item in self.function_slices:
            func_name = getattr(slice_item, 'name', '').lower()
            source_code = getattr(slice_item, 'source_code', '').lower()

            for pattern, config in self.business_patterns.items():
                keywords = config['keywords']

                for keyword in keywords:
                    if keyword in func_name or keyword in source_code:
                        pattern_matches[pattern] += 1

        patterns = [pattern for pattern, count in pattern_matches.items() if count > 0]

        return patterns

    def _build_relationships(self) -> Dict[str, List[str]]:
        """构建业务关系图

        Returns:
            Dict[str, List[str]]: 关系图字典
        """
        relationships = defaultdict(list)

        for slice_item in self.function_slices:
            func_name = getattr(slice_item, 'name', '')

            calls = getattr(slice_item, 'calls', [])

            for call in calls:
                target_func = call.get('name', '')
                if target_func:
                    relationships[func_name].append(target_func)

        return dict(relationships)

    def _generate_test_recommendations(self, result: BusinessRecognitionResult) -> List[str]:
        """生成测试建议

        Args:
            result: 业务识别结果

        Returns:
            List[str]: 测试建议列表
        """
        recommendations = []

        if result.primary_domain != BusinessDomain.UNKNOWN:
            recommendations.append(f"主要业务领域: {result.primary_domain.name}，建议进行领域特定的边界测试")

        high_conf_scenarios = result.get_high_confidence_scenarios(0.5)
        if high_conf_scenarios:
            scenario_names = [s.scenario.name for s in high_conf_scenarios[:5]]
            recommendations.append(f"识别的核心业务场景: {', '.join(scenario_names)}")
            recommendations.append(f"建议对这些场景进行端到端的功能测试")

        if result.entities:
            entity_names = [e.name for e in result.entities[:5]]
            recommendations.append(f"发现业务实体: {', '.join(entity_names)}")
            recommendations.append(f"建议为每个实体编写CRUD测试用例")

        if result.patterns:
            pattern_names = [p.name for p in result.patterns[:5]]
            recommendations.append(f"识别业务模式: {', '.join(pattern_names)}")

        if BusinessPattern.TRANSACTION_MANAGEMENT in result.patterns:
            recommendations.append("检测到事务管理，需要测试事务的回滚和提交场景")

        if BusinessPattern.CACHE_ASIDE in result.patterns:
            recommendations.append("检测到缓存模式，需要测试缓存失效和数据一致性")

        if BusinessPattern.EVENT_DRIVEN in result.patterns:
            recommendations.append("检测到事件驱动模式，需要测试异步事件处理和错误恢复")

        return recommendations

    def _assess_complexity(self, result: BusinessRecognitionResult) -> Dict[str, Any]:
        """评估业务复杂度

        Args:
            result: 业务识别结果

        Returns:
            Dict[str, Any]: 复杂度评估结果
        """
        complexity = {
            'overall_level': 'low',
            'score': 0,
            'factors': {}
        }

        complexity['score'] = len(result.scenarios) * 5 + len(result.entities) * 3 + len(result.patterns) * 2

        complexity['factors']['scenario_count'] = len(result.scenarios)
        complexity['factors']['entity_count'] = len(result.entities)
        complexity['factors']['pattern_count'] = len(result.patterns)
        complexity['factors']['relationship_count'] = sum(len(rel) for rel in result.relationships.values())

        if complexity['score'] > 50:
            complexity['overall_level'] = 'high'
            complexity['recommendation'] = '建议分模块进行测试，优先覆盖核心场景'
        elif complexity['score'] > 20:
            complexity['overall_level'] = 'medium'
            complexity['recommendation'] = '建议按照业务场景分组进行测试'
        else:
            complexity['overall_level'] = 'low'
            complexity['recommendation'] = '业务逻辑相对简单，可以进行全面测试'

        return complexity

    def _get_statistics(self, result: BusinessRecognitionResult) -> Dict[str, Any]:
        """获取统计信息

        Args:
            result: 业务识别结果

        Returns:
            Dict[str, Any]: 统计信息
        """
        return {
            'primary_domain': result.primary_domain.name,
            'secondary_domains': [d.name for d in result.secondary_domains],
            'scenario_count': len(result.scenarios),
            'high_confidence_scenarios': len(result.get_high_confidence_scenarios()),
            'entity_count': len(result.entities),
            'pattern_count': len(result.patterns),
            'relationship_count': len(result.relationships),
            'complexity_score': result.complexity_assessment.get('score', 0),
            'complexity_level': result.complexity_assessment.get('overall_level', 'unknown')
        }

    def get_domain_functions(self, domain: BusinessDomain) -> List[str]:
        """获取指定领域的函数列表

        Args:
            domain: 业务领域

        Returns:
            List[str]: 函数名列表
        """
        functions = []

        if domain in self.domain_patterns:
            patterns = self.domain_patterns[domain]

            for slice_item in self.function_slices:
                func_name = getattr(slice_item, 'name', '').lower()
                source_code = getattr(slice_item, 'source_code', '').lower()

                for keyword in patterns['keywords']:
                    if keyword in func_name or keyword in source_code:
                        functions.append(getattr(slice_item, 'name', ''))
                        break

        return functions

    def get_scenario_functions(self, scenario: BusinessScenario) -> List[str]:
        """获取指定场景的函数列表

        Args:
            scenario: 业务场景

        Returns:
            List[str]: 函数名列表
        """
        for scenario_info in self.function_slices:
            if hasattr(scenario_info, 'scenario') and scenario_info.scenario == scenario:
                return scenario_info.matched_functions

        return []

    def suggest_test_sequence(self) -> List[str]:
        """建议测试执行顺序

        Returns:
            List[str]: 建议的测试函数顺序
        """
        sequence = []

        auth_functions = self.get_domain_functions(BusinessDomain.USER_MANAGEMENT)
        sequence.extend(auth_functions)

        core_functions = []
        for slice_item in self.function_slices:
            func_name = getattr(slice_item, 'name', '')
            if func_name not in sequence:
                if any(s.scenario.name in ['DATA_VALIDATION', 'PERMISSION_CHECK']
                      for s in self.function_slices if hasattr(s, 'scenario')):
                    core_functions.append(func_name)

        sequence.extend(core_functions)

        for slice_item in self.function_slices:
            func_name = getattr(slice_item, 'name', '')
            if func_name not in sequence:
                sequence.append(func_name)

        return sequence

    def identify_test_boundaries(self) -> List[Dict[str, Any]]:
        """识别测试边界

        Returns:
            List[Dict[str, Any]]: 测试边界信息列表
        """
        boundaries = []

        for entity in self.entities:
            boundary = {
                'entity': entity.name,
                'type': 'entity_boundary',
                'lifecycle': entity.lifecycle,
                'test_points': []
            }

            for stage in entity.lifecycle:
                boundary['test_points'].append({
                    'stage': stage,
                    'function': f"{entity.name.lower()}_{stage}",
                    'focus': f"测试{entity.name}的{stage}操作"
                })

            boundaries.append(boundary)

        return boundaries

    def generate_test_scenarios(self) -> List[Dict[str, Any]]:
        """生成测试场景描述

        Returns:
            List[Dict[str, Any]]: 测试场景列表
        """
        scenarios = []

        for scenario_info in self.function_slices:
            if hasattr(scenario_info, 'scenario'):
                scenario = {
                    'name': scenario_info.scenario.name,
                    'description': self._get_scenario_description(scenario_info.scenario),
                    'functions': scenario_info.matched_functions,
                    'confidence': scenario_info.confidence,
                    'test_focus': []
                }

                scenario['test_focus'].append(f"验证{scenario_info.scenario.name}的基本功能")
                scenario['test_focus'].append(f"测试异常情况和错误处理")
                scenario['test_focus'].append(f"验证边界条件和极端输入")

                scenarios.append(scenario)

        return scenarios

    def _get_scenario_description(self, scenario: BusinessScenario) -> str:
        """获取场景描述

        Args:
            scenario: 业务场景

        Returns:
            str: 场景描述
        """
        descriptions = {
            BusinessScenario.USER_AUTHENTICATION: "用户登录认证场景，包括密码验证、Token生成等",
            BusinessScenario.USER_REGISTRATION: "用户注册场景，包括信息验证、账户创建等",
            BusinessScenario.PRODUCT_CATALOG: "产品目录管理场景，包括产品展示、搜索、分类等",
            BusinessScenario.SHOPPING_CART: "购物车管理场景，包括添加、修改、删除商品等",
            BusinessScenario.ORDER_PROCESSING: "订单处理场景，包括订单创建、状态流转、取消等",
            BusinessScenario.PAYMENT_PROCESSING: "支付处理场景，包括支付、退款等",
            BusinessScenario.DATA_VALIDATION: "数据验证场景，包括输入校验、格式验证等",
            BusinessScenario.CACHE_OPERATION: "缓存操作场景，包括读写、失效、更新等"
        }

        return descriptions.get(scenario, f"{scenario.name}业务场景")
