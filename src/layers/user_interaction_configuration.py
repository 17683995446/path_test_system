"""
UserInteractionConfigurationLayers - 用户交互与配置管理层 (41-50)
=============================================================

第一部分：用户交互与配置管理
- 第41层：用户输入解析
- 第42层：交互反馈处理
- 第43层：命令系统集成
- 第44层：配置文件加载
- 第45层：运行时配置更新
- 第46层：环境变量管理
- 第47层：插件系统初始化
- 第48层：扩展点注册
- 第49层：系统启动引导
- 第50层：健康检查完成

作者：PathTestSystem
版本：1.0.0
"""

import os
import sys
import json
import time
import argparse
from typing import Dict, List, Any, Optional, Callable, Type
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from collections import defaultdict


class InputType(Enum):
    """输入类型"""
    COMMAND = "command"
    FILE_PATH = "file_path"
    DIRECTORY = "directory"
    CONFIG = "config"
    QUERY = "query"


class FeedbackLevel(Enum):
    """反馈级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    DEBUG = "debug"


@dataclass
class UserInput:
    """用户输入"""
    input_type: InputType
    raw_content: str
    parsed_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=lambda: time.time())


@dataclass
class UserFeedback:
    """用户反馈"""
    level: FeedbackLevel
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: float = field(default_factory=lambda: time.time())
    dismissible: bool = True


@dataclass
class Command:
    """命令"""
    name: str
    description: str
    handler: Callable
    args_schema: Dict[str, Any] = field(default_factory=dict)
    aliases: List[str] = field(default_factory=list)


class UserInputParser:
    """
    用户输入解析器
    ==============
    
    解析用户输入
    """
    
    def __init__(self):
        self.parsers: Dict[InputType, Callable] = {
            InputType.COMMAND: self._parse_command,
            InputType.FILE_PATH: self._parse_file_path,
            InputType.DIRECTORY: self._parse_directory,
            InputType.CONFIG: self._parse_config,
            InputType.QUERY: self._parse_query
        }
    
    def parse(self, raw_input: str) -> UserInput:
        """
        解析用户输入
        
        Args:
            raw_input: 原始输入
        
        Returns:
            解析后的用户输入
        """
        input_type = self._detect_input_type(raw_input)
        parser = self.parsers.get(input_type, self._parse_generic)
        parsed_data = parser(raw_input)
        
        return UserInput(
            input_type=input_type,
            raw_content=raw_input,
            parsed_data=parsed_data
        )
    
    def _detect_input_type(self, raw_input: str) -> InputType:
        """检测输入类型"""
        raw_input = raw_input.strip()
        
        if raw_input.startswith('/') or raw_input.startswith('-'):
            return InputType.COMMAND
        
        if os.path.isfile(raw_input):
            return InputType.FILE_PATH
        
        if os.path.isdir(raw_input):
            return InputType.DIRECTORY
        
        if raw_input.startswith('{') or raw_input.startswith('['):
            return InputType.CONFIG
        
        if '?' in raw_input or raw_input.lower().startswith(('what', 'how', 'why', 'when', 'where')):
            return InputType.QUERY
        
        return InputType.COMMAND
    
    def _parse_command(self, raw_input: str) -> Dict[str, Any]:
        """解析命令"""
        parts = raw_input.split()
        command = parts[0] if parts else ""
        args = parts[1:] if len(parts) > 1 else []
        
        return {
            'command': command.lstrip('/-'),
            'args': args,
            'flags': self._extract_flags(args)
        }
    
    def _extract_flags(self, args: List[str]) -> Dict[str, bool]:
        """提取标志"""
        flags = {}
        for arg in args:
            if arg.startswith('-'):
                flag_name = arg.lstrip('-')
                flags[flag_name] = True
        return flags
    
    def _parse_file_path(self, raw_input: str) -> Dict[str, Any]:
        """解析文件路径"""
        return {
            'path': raw_input,
            'exists': os.path.exists(raw_input),
            'is_file': os.path.isfile(raw_input),
            'size': os.path.getsize(raw_input) if os.path.isfile(raw_input) else 0
        }
    
    def _parse_directory(self, raw_input: str) -> Dict[str, Any]:
        """解析目录"""
        file_count = 0
        dir_count = 0
        
        if os.path.isdir(raw_input):
            for item in os.listdir(raw_input):
                item_path = os.path.join(raw_input, item)
                if os.path.isfile(item_path):
                    file_count += 1
                elif os.path.isdir(item_path):
                    dir_count += 1
        
        return {
            'path': raw_input,
            'exists': os.path.isdir(raw_input),
            'file_count': file_count,
            'dir_count': dir_count
        }
    
    def _parse_config(self, raw_input: str) -> Dict[str, Any]:
        """解析配置"""
        try:
            config = json.loads(raw_input)
            return {'config': config, 'valid': True}
        except json.JSONDecodeError:
            return {'config': {}, 'valid': False, 'error': 'Invalid JSON'}
    
    def _parse_query(self, raw_input: str) -> Dict[str, Any]:
        """解析查询"""
        return {
            'query': raw_input,
            'tokens': raw_input.lower().split(),
            'intent': self._detect_intent(raw_input)
        }
    
    def _detect_intent(self, query: str) -> str:
        """检测意图"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['find', 'search', 'locate']):
            return 'search'
        elif any(word in query_lower for word in ['fix', 'repair', 'resolve']):
            return 'fix'
        elif any(word in query_lower for word in ['analyze', 'examine', 'check']):
            return 'analyze'
        elif any(word in query_lower for word in ['generate', 'create', 'make']):
            return 'generate'
        
        return 'unknown'
    
    def _parse_generic(self, raw_input: str) -> Dict[str, Any]:
        """通用解析"""
        return {
            'content': raw_input,
            'words': raw_input.split()
        }


class InteractiveFeedbackHandler:
    """
    交互反馈处理器
    ==============
    
    处理用户交互反馈
    """
    
    def __init__(self):
        self.feedback_history: List[UserFeedback] = []
        self.handlers: Dict[FeedbackLevel, List[Callable]] = {
            level: [] for level in FeedbackLevel
        }
    
    def register_handler(self, level: FeedbackLevel, handler: Callable):
        """
        注册处理器
        
        Args:
            level: 反馈级别
            handler: 处理函数
        """
        self.handlers[level].append(handler)
    
    def send_feedback(self, level: FeedbackLevel, message: str, 
                     details: Optional[Dict[str, Any]] = None):
        """
        发送反馈
        
        Args:
            level: 反馈级别
            message: 消息
            details: 详情
        """
        feedback = UserFeedback(
            level=level,
            message=message,
            details=details
        )
        
        self.feedback_history.append(feedback)
        
        for handler in self.handlers[level]:
            handler(feedback)
        
        self._display_feedback(feedback)
    
    def _display_feedback(self, feedback: UserFeedback):
        """显示反馈"""
        icons = {
            FeedbackLevel.INFO: "ℹ️",
            FeedbackLevel.WARNING: "⚠️",
            FeedbackLevel.ERROR: "❌",
            FeedbackLevel.SUCCESS: "✅",
            FeedbackLevel.DEBUG: "🔍"
        }
        
        icon = icons.get(feedback.level, "📝")
        print(f"{icon} {feedback.message}")
        
        if feedback.details:
            print(f"   详情: {json.dumps(feedback.details, ensure_ascii=False)}")
    
    def get_feedback_history(self, level: Optional[FeedbackLevel] = None) -> List[UserFeedback]:
        """
        获取反馈历史
        
        Args:
            level: 过滤级别
        
        Returns:
            反馈列表
        """
        if level:
            return [f for f in self.feedback_history if f.level == level]
        return self.feedback_history
    
    def clear_history(self):
        """清空历史"""
        self.feedback_history.clear()


class CommandSystemIntegrator:
    """
    命令系统集成器
    ==============
    
    集成命令行系统
    """
    
    def __init__(self):
        self.commands: Dict[str, Command] = {}
        self.aliases: Dict[str, str] = {}
    
    def register_command(self, name: str, handler: Callable, 
                        description: str = "", aliases: Optional[List[str]] = None):
        """
        注册命令
        
        Args:
            name: 命令名
            handler: 处理函数
            description: 描述
            aliases: 别名
        """
        command = Command(
            name=name,
            description=description,
            handler=handler,
            aliases=aliases or []
        )
        
        self.commands[name] = command
        
        for alias in aliases or []:
            self.aliases[alias] = name
    
    def execute_command(self, command_name: str, args: Dict[str, Any]) -> Any:
        """
        执行命令
        
        Args:
            command_name: 命令名
            args: 参数
        
        Returns:
            执行结果
        """
        if command_name in self.aliases:
            command_name = self.aliases[command_name]
        
        if command_name not in self.commands:
            raise ValueError(f"Unknown command: {command_name}")
        
        command = self.commands[command_name]
        return command.handler(args)
    
    def list_commands(self) -> List[Dict[str, Any]]:
        """列出所有命令"""
        return [
            {
                'name': cmd.name,
                'description': cmd.description,
                'aliases': cmd.aliases
            }
            for cmd in self.commands.values()
        ]
    
    def get_command(self, name: str) -> Optional[Command]:
        """获取命令"""
        if name in self.aliases:
            name = self.aliases[name]
        return self.commands.get(name)


class ConfigurationFileLoader:
    """
    配置文件加载器
    ===============
    
    加载和管理配置文件
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = config_dir or self._get_default_config_dir()
        self.configs: Dict[str, Dict[str, Any]] = {}
        self.watchers: Dict[str, Callable] = {}
    
    def _get_default_config_dir(self) -> str:
        """获取默认配置目录"""
        home = os.path.expanduser("~")
        return os.path.join(home, ".path_test_system")
    
    def load_config(self, config_name: str, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        加载配置
        
        Args:
            config_name: 配置名
            config_path: 配置路径
        
        Returns:
            配置字典
        """
        if config_path is None:
            config_path = os.path.join(self.config_dir, f"{config_name}.json")
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.configs[config_name] = config
                    return config
            except Exception:
                pass
        
        return {}
    
    def save_config(self, config_name: str, config_data: Dict[str, Any], 
                   config_path: Optional[str] = None):
        """
        保存配置
        
        Args:
            config_name: 配置名
            config_data: 配置数据
            config_path: 配置路径
        """
        if config_path is None:
            config_path = os.path.join(self.config_dir, f"{config_name}.json")
        
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        self.configs[config_name] = config_data
        
        if config_name in self.watchers:
            self.watchers[config_name](config_data)
    
    def register_watcher(self, config_name: str, watcher: Callable):
        """
        注册配置监视器
        
        Args:
            config_name: 配置名
            watcher: 监视函数
        """
        self.watchers[config_name] = watcher
    
    def get_config(self, config_name: str, default: Optional[Dict] = None) -> Dict[str, Any]:
        """
        获取配置
        
        Args:
            config_name: 配置名
            default: 默认值
        
        Returns:
            配置字典
        """
        return self.configs.get(config_name, default or {})


class RuntimeConfigurationUpdater:
    """
    运行时配置更新器
    =================
    
    支持运行时更新配置
    """
    
    def __init__(self):
        self.runtime_configs: Dict[str, Any] = {}
        self.listeners: Dict[str, List[Callable]] = defaultdict(list)
        self.change_history: List[Dict] = []
    
    def update_config(self, key: str, value: Any):
        """
        更新配置
        
        Args:
            key: 配置键
            value: 配置值
        """
        old_value = self.runtime_configs.get(key)
        self.runtime_configs[key] = value
        
        change = {
            'key': key,
            'old_value': old_value,
            'new_value': value,
            'timestamp': time.time()
        }
        self.change_history.append(change)
        
        for listener in self.listeners.get(key, []):
            listener(old_value, value)
        
        for listener in self.listeners.get('*', []):
            listener(key, old_value, value)
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        获取配置
        
        Args:
            key: 配置键
            default: 默认值
        
        Returns:
            配置值
        """
        return self.runtime_configs.get(key, default)
    
    def register_listener(self, key: str, listener: Callable):
        """
        注册监听器
        
        Args:
            key: 配置键
            listener: 监听函数
        """
        self.listeners[key].append(listener)
    
    def get_change_history(self) -> List[Dict]:
        """获取变更历史"""
        return self.change_history


class EnvironmentVariableManager:
    """
    环境变量管理器
    ==============
    
    管理环境变量
    """
    
    def __init__(self):
        self.env_prefix = "PATH_TEST_"
        self.defaults: Dict[str, Any] = self._load_defaults()
    
    def _load_defaults(self) -> Dict[str, Any]:
        """加载默认值"""
        return {
            'LOG_LEVEL': 'INFO',
            'MAX_WORKERS': '4',
            'CACHE_ENABLED': 'true',
            'TIMEOUT': '30',
            'DEBUG': 'false'
        }
    
    def get(self, key: str, default: Optional[str] = None) -> str:
        """
        获取环境变量
        
        Args:
            key: 变量名
            default: 默认值
        
        Returns:
            变量值
        """
        full_key = f"{self.env_prefix}{key}"
        return os.environ.get(full_key, default or self.defaults.get(key, ""))
    
    def set(self, key: str, value: str):
        """
        设置环境变量
        
        Args:
            key: 变量名
            value: 变量值
        """
        full_key = f"{self.env_prefix}{key}"
        os.environ[full_key] = str(value)
    
    def get_int(self, key: str, default: int = 0) -> int:
        """获取整数环境变量"""
        value = self.get(key)
        try:
            return int(value)
        except ValueError:
            return default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """获取布尔环境变量"""
        value = self.get(key).lower()
        return value in ('true', '1', 'yes', 'on')
    
    def list_all(self) -> Dict[str, str]:
        """列出所有相关环境变量"""
        result = {}
        for key, value in os.environ.items():
            if key.startswith(self.env_prefix):
                short_key = key[len(self.env_prefix):]
                result[short_key] = value
        return result


class PluginSystemInitializer:
    """
    插件系统初始化器
    =================
    
    初始化插件系统
    """
    
    def __init__(self):
        self.plugins: Dict[str, Any] = {}
        self.plugin_metadata: Dict[str, Dict] = {}
        self.enabled_plugins: Set[str] = set()
    
    def register_plugin(self, plugin_id: str, plugin_instance: Any, 
                       metadata: Optional[Dict] = None):
        """
        注册插件
        
        Args:
            plugin_id: 插件ID
            plugin_instance: 插件实例
            metadata: 插件元数据
        """
        self.plugins[plugin_id] = plugin_instance
        self.plugin_metadata[plugin_id] = metadata or {}
    
    def enable_plugin(self, plugin_id: str):
        """
        启用插件
        
        Args:
            plugin_id: 插件ID
        """
        if plugin_id in self.plugins:
            self.enabled_plugins.add(plugin_id)
            
            plugin = self.plugins[plugin_id]
            if hasattr(plugin, 'on_enable'):
                plugin.on_enable()
    
    def disable_plugin(self, plugin_id: str):
        """
        禁用插件
        
        Args:
            plugin_id: 插件ID
        """
        if plugin_id in self.enabled_plugins:
            self.enabled_plugins.remove(plugin_id)
            
            plugin = self.plugins.get(plugin_id)
            if plugin and hasattr(plugin, 'on_disable'):
                plugin.on_disable()
    
    def get_plugin(self, plugin_id: str) -> Optional[Any]:
        """获取插件"""
        return self.plugins.get(plugin_id)
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """列出所有插件"""
        return [
            {
                'id': pid,
                'enabled': pid in self.enabled_plugins,
                'metadata': self.plugin_metadata.get(pid, {})
            }
            for pid in self.plugins
        ]


class ExtensionPointRegistry:
    """
    扩展点注册表
    =============
    
    注册和管理扩展点
    """
    
    def __init__(self):
        self.extension_points: Dict[str, Dict] = {}
        self.extensions: Dict[str, List[Any]] = defaultdict(list)
    
    def register_extension_point(self, point_id: str, description: str,
                                 interface: Optional[Type] = None):
        """
        注册扩展点
        
        Args:
            point_id: 扩展点ID
            description: 描述
            interface: 接口类型
        """
        self.extension_points[point_id] = {
            'description': description,
            'interface': interface,
            'extensions': []
        }
    
    def register_extension(self, point_id: str, extension: Any,
                          metadata: Optional[Dict] = None):
        """
        注册扩展
        
        Args:
            point_id: 扩展点ID
            extension: 扩展实例
            metadata: 元数据
        """
        if point_id not in self.extension_points:
            self.register_extension_point(point_id, f"Extension point: {point_id}")
        
        self.extensions[point_id].append({
            'instance': extension,
            'metadata': metadata or {}
        })
        
        self.extension_points[point_id]['extensions'].append(extension)
    
    def get_extensions(self, point_id: str) -> List[Any]:
        """获取扩展"""
        return self.extensions.get(point_id, [])
    
    def get_extension_points(self) -> List[Dict[str, Any]]:
        """获取所有扩展点"""
        return [
            {
                'id': ep_id,
                'description': ep['description'],
                'extension_count': len(ep['extensions'])
            }
            for ep_id, ep in self.extension_points.items()
        ]


class SystemBootstrap:
    """
    系统启动引导器
    ==============
    
    系统启动和初始化
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.boot_sequence: List[Tuple[str, Callable]] = []
        self.boot_history: List[Dict] = []
        self.bootstrapped = False
    
    def register_boot_step(self, step_name: str, step_func: Callable):
        """
        注册启动步骤
        
        Args:
            step_name: 步骤名
            step_func: 步骤函数
        """
        self.boot_sequence.append((step_name, step_func))
    
    def bootstrap(self) -> Dict[str, Any]:
        """
        执行启动引导
        
        Returns:
            启动结果
        """
        results = {
            'success': True,
            'steps': [],
            'total_time': 0.0
        }
        
        start_time = time.time()
        
        for step_name, step_func in self.boot_sequence:
            step_start = time.time()
            step_result = {'name': step_name, 'success': False, 'error': None}
            
            try:
                step_func()
                step_result['success'] = True
            except Exception as e:
                step_result['error'] = str(e)
                results['success'] = False
            
            step_result['duration'] = time.time() - step_start
            results['steps'].append(step_result)
            self.boot_history.append(step_result)
        
        results['total_time'] = time.time() - start_time
        self.bootstrapped = True
        
        return results
    
    def get_boot_history(self) -> List[Dict]:
        """获取启动历史"""
        return self.boot_history


class HealthCheckCompletor:
    """
    健康检查完成器
    ==============
    
    执行健康检查
    """
    
    def __init__(self):
        self.checks: Dict[str, Callable] = {}
        self.check_results: Dict[str, bool] = {}
        self.last_check_time: Optional[float] = None
    
    def register_check(self, check_name: str, check_func: Callable):
        """
        注册检查
        
        Args:
            check_name: 检查名
            check_func: 检查函数
        """
        self.checks[check_name] = check_func
    
    def run_health_check(self) -> Dict[str, Any]:
        """
        运行健康检查
        
        Returns:
            检查结果
        """
        results = {
            'healthy': True,
            'checks': {},
            'timestamp': time.time(),
            'summary': ''
        }
        
        for check_name, check_func in self.checks.items():
            try:
                check_result = check_func()
                self.check_results[check_name] = check_result
                results['checks'][check_name] = {
                    'passed': check_result,
                    'message': 'OK' if check_result else 'Failed'
                }
                
                if not check_result:
                    results['healthy'] = False
            except Exception as e:
                self.check_results[check_name] = False
                results['checks'][check_name] = {
                    'passed': False,
                    'message': f'Error: {str(e)}'
                }
                results['healthy'] = False
        
        passed_count = sum(1 for r in results['checks'].values() if r['passed'])
        total_count = len(results['checks'])
        results['summary'] = f"{passed_count}/{total_count} checks passed"
        
        self.last_check_time = time.time()
        
        return results
    
    def is_healthy(self) -> bool:
        """检查是否健康"""
        if not self.check_results:
            return True
        return all(self.check_results.values())


class UserInteractionConfigController:
    """
    用户交互配置控制器 - 主控制器
    ============================
    
    整合所有用户交互和配置管理功能
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        self.input_parser = UserInputParser()
        self.feedback_handler = InteractiveFeedbackHandler()
        self.command_system = CommandSystemIntegrator()
        self.config_loader = ConfigurationFileLoader()
        self.runtime_updater = RuntimeConfigurationUpdater()
        self.env_manager = EnvironmentVariableManager()
        self.plugin_initializer = PluginSystemInitializer()
        self.extension_registry = ExtensionPointRegistry()
        self.bootstrap = SystemBootstrap(self.config)
        self.health_check = HealthCheckCompletor()
        
        self._init_default_commands()
        self._init_default_health_checks()
    
    def _init_default_commands(self):
        """初始化默认命令"""
        self.command_system.register_command(
            'help', 
            lambda args: self.command_system.list_commands(),
            '显示帮助信息'
        )
        
        self.command_system.register_command(
            'status',
            lambda args: self.health_check.run_health_check(),
            '显示系统状态'
        )
        
        self.command_system.register_command(
            'quit',
            lambda args: {'action': 'quit'},
            '退出系统'
        )
    
    def _init_default_health_checks(self):
        """初始化默认健康检查"""
        self.health_check.register_check('config', lambda: True)
        self.health_check.register_check('plugins', lambda: True)
        self.health_check.register_check('extensions', lambda: True)
    
    def process_input(self, raw_input: str) -> Dict[str, Any]:
        """
        处理用户输入
        
        Args:
            raw_input: 原始输入
        
        Returns:
            处理结果
        """
        user_input = self.input_parser.parse(raw_input)
        
        if user_input.input_type == InputType.COMMAND:
            parsed = user_input.parsed_data
            command_name = parsed.get('command', '')
            
            try:
                result = self.command_system.execute_command(command_name, parsed)
                self.feedback_handler.send_feedback(
                    FeedbackLevel.SUCCESS,
                    f"Command '{command_name}' executed successfully"
                )
                return {'success': True, 'result': result}
            except Exception as e:
                self.feedback_handler.send_feedback(
                    FeedbackLevel.ERROR,
                    f"Command failed: {str(e)}"
                )
                return {'success': False, 'error': str(e)}
        
        return {'success': True, 'input': user_input}
    
    def start_system(self) -> Dict[str, Any]:
        """
        启动系统
        
        Returns:
            启动结果
        """
        bootstrap_result = self.bootstrap.bootstrap()
        
        health_result = self.health_check.run_health_check()
        
        if bootstrap_result['success'] and health_result['healthy']:
            self.feedback_handler.send_feedback(
                FeedbackLevel.SUCCESS,
                "System started successfully"
            )
        else:
            self.feedback_handler.send_feedback(
                FeedbackLevel.WARNING,
                "System started with warnings"
            )
        
        return {
            'bootstrap': bootstrap_result,
            'health': health_result
        }
    
    def shutdown_system(self):
        """关闭系统"""
        for plugin_id in list(self.plugin_initializer.enabled_plugins):
            self.plugin_initializer.disable_plugin(plugin_id)
        
        self.feedback_handler.send_feedback(
            FeedbackLevel.INFO,
            "System shutdown complete"
        )


def create_interaction_controller(config: Optional[Dict] = None) -> UserInteractionConfigController:
    """
    创建用户交互配置控制器工厂函数
    
    Args:
        config: 配置字典
    
    Returns:
        UserInteractionConfigController实例
    """
    return UserInteractionConfigController(config)


if __name__ == "__main__":
    controller = create_interaction_controller()
    
    print("测试用户输入解析:")
    test_inputs = [
        '/help',
        '/workspace/path_test_system/src/core',
        '{"setting": "value"}',
        'How to analyze this code?'
    ]
    
    for inp in test_inputs:
        result = controller.process_input(inp)
        print(f"  输入: {inp}")
        print(f"  结果: {result}")
        print()
    
    print("\n系统启动:")
    start_result = controller.start_system()
    print(f"  启动成功: {start_result['bootstrap']['success']}")
    print(f"  健康检查: {start_result['health']['summary']}")
    
    controller.shutdown_system()
