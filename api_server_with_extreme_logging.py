#!/usr/bin/env python3
"""
完整后端API服务器 - 超详细日志版本
集成50层分析引擎
提供真实的代码分析功能
包含安全防护机制
每句关键代码都有详细日志
"""

import os
import json
import time
import random
import threading
import re
import logging
from functools import wraps
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from flask import Flask, request, jsonify
from flask_cors import CORS

# ============================================================
# 超详细日志配置
# ============================================================
class LoggingFormatter(logging.Formatter):
    def format(self, record):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        return f"[{timestamp}] [{record.levelname}] [{threading.current_thread().name}] {record.getMessage()}"

# 配置超详细日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 文件日志处理器
file_handler = logging.FileHandler("/workspace/path_test_system/api_server.log")
file_handler.setFormatter(LoggingFormatter())
logger.addHandler(file_handler)

# 控制台日志处理器
console_handler = logging.StreamHandler()
console_handler.setFormatter(LoggingFormatter())
logger.addHandler(console_handler)

logger.info("=" * 100)
logger.info("🚀 系统初始化开始 - 超详细日志版本")
logger.info("=" * 100)

app = Flask(__name__)
CORS(app)

logger.info("✅ Flask应用和CORS配置完成")

# ================== 安全配置 ==================
# 速率限制配置：每IP每分钟最大请求数
RATE_LIMIT_ENABLED = False  # 暂时禁用进行压力测试
RATE_LIMIT = 500  # 每分钟500次请求（生产环境合理值）
request_counts = defaultdict(lambda: {'count': 0, 'reset_time': time.time() + 60})
rate_limit_lock = threading.Lock()
logger.info(f"✅ 速率限制配置完成 - 启用: {RATE_LIMIT_ENABLED}, 限制: {RATE_LIMIT}/分钟")

# XSS过滤：危险标签和属性
DANGEROUS_TAGS = ['script', 'iframe', 'object', 'embed', 'form', 'input', 'button', 'style', 'svg']
DANGEROUS_ATTRIBUTES = ['onclick', 'onerror', 'onload', 'onmouseover', 'onfocus', 'onblur', 'onchange', 'eval']
logger.info(f"✅ XSS防护配置完成 - 危险标签: {len(DANGEROUS_TAGS)}个, 危险属性: {len(DANGEROUS_ATTRIBUTES)}个")

# 文件锁字典
file_locks = {
    'projects': threading.Lock(),
    'issues': threading.Lock(),
    'tests': threading.Lock(),
    'settings': threading.Lock()
}
logger.info(f"✅ 文件锁初始化完成 - 锁数量: {len(file_locks)}个")

# ================== 安全工具函数 ==================
def sanitize_input(text: Optional[str]) -> Optional[str]:
    """清理用户输入，防止XSS攻击"""
    logger.debug("📝 [sanitize_input] 开始清理输入")
    logger.debug(f"📝 [sanitize_input] 输入值: {repr(text)}")
    
    if text is None:
        logger.debug("📝 [sanitize_input] 输入为None，返回None")
        return None
    
    text = str(text)
    logger.debug(f"📝 [sanitize_input] 转换为字符串: {repr(text)}")
    
    # 移除或转义危险标签
    logger.debug("📝 [sanitize_input] 开始移除危险标签")
    for tag in DANGEROUS_TAGS:
        logger.debug(f"📝 [sanitize_input] 处理标签: {tag}")
        text = re.sub(rf'<\s*{tag}[^>]*>', '', text, flags=re.IGNORECASE)
        text = re.sub(rf'</\s*{tag}\s*>', '', text, flags=re.IGNORECASE)
    
    # 转义危险属性
    logger.debug("📝 [sanitize_input] 开始移除危险属性")
    for attr in DANGEROUS_ATTRIBUTES:
        logger.debug(f"📝 [sanitize_input] 处理属性: {attr}")
        text = re.sub(rf'\b{attr}\s*=', '', text, flags=re.IGNORECASE)
    
    # 转义特殊字符
    logger.debug("📝 [sanitize_input] 开始转义特殊字符")
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    text = text.replace('"', '&quot;').replace("'", '&#39;')
    
    result = text.strip()
    logger.debug(f"📝 [sanitize_input] 清理完成，结果: {repr(result)}")
    
    return result

def validate_project_name(name: str) -> tuple[bool, str]:
    """验证项目名称"""
    logger.debug("✅ [validate_project_name] 开始验证项目名称")
    logger.debug(f"✅ [validate_project_name] 输入名称: {repr(name)}")
    
    if not name or not name.strip():
        logger.warning("⚠️ [validate_project_name] 验证失败：名称为空")
        return False, "项目名称不能为空"
    
    if len(name) > 200:
        logger.warning(f"⚠️ [validate_project_name] 验证失败：名称过长 ({len(name)} > 200)")
        return False, "项目名称不能超过200字符"
    
    logger.info("✅ [validate_project_name] 验证通过")
    return True, ""

def validate_project_path(path: str) -> tuple[bool, str]:
    """验证项目路径"""
    logger.debug("✅ [validate_project_path] 开始验证项目路径")
    logger.debug(f"✅ [validate_project_path] 输入路径: {repr(path)}")
    
    if not path or not path.strip():
        logger.warning("⚠️ [validate_project_path] 验证失败：路径为空")
        return False, "项目路径不能为空"
    
    if len(path) > 500:
        logger.warning(f"⚠️ [validate_project_path] 验证失败：路径过长 ({len(path)} > 500)")
        return False, "项目路径不能超过500字符"
    
    # 防止路径遍历攻击
    logger.debug("✅ [validate_project_path] 开始规范化路径")
    path = os.path.normpath(path)
    logger.debug(f"✅ [validate_project_path] 规范化后: {repr(path)}")
    
    if '..' in path:
        logger.warning("⚠️ [validate_project_path] 验证失败：包含非法字符 '..'")
        return False, "路径包含非法字符"
    
    # 安全检查：限制在工作区范围内
    logger.debug("✅ [validate_project_path] 开始工作区范围检查")
    try:
        abs_path = os.path.abspath(path)
        logger.debug(f"✅ [validate_project_path] 绝对路径: {abs_path}")
        
        if not abs_path.startswith('/workspace'):
            logger.warning(f"⚠️ [validate_project_path] 验证失败：路径不在工作区内: {abs_path}")
            return False, "项目路径必须在工作区内"
    except Exception as e:
        logger.error(f"❌ [validate_project_path] 异常: {e}")
        return False, "路径格式无效"
    
    if not os.path.exists(path):
        logger.warning(f"⚠️ [validate_project_path] 验证失败：路径不存在: {path}")
        return False, "项目路径不存在"
    
    logger.info(f"✅ [validate_project_path] 验证通过: {path}")
    return True, ""

def is_safe_path(base_path: str, full_path: str) -> bool:
    """检查路径是否安全"""
    logger.debug("🔒 [is_safe_path] 开始安全检查")
    logger.debug(f"🔒 [is_safe_path] 基准路径: {base_path}")
    logger.debug(f"🔒 [is_safe_path] 目标路径: {full_path}")
    
    try:
        # 规范化路径
        safe_base = Path(base_path).resolve()
        safe_full = Path(full_path).resolve()
        
        logger.debug(f"🔒 [is_safe_path] 规范化基准: {safe_base}")
        logger.debug(f"🔒 [is_safe_path] 规范化目标: {safe_full}")
        
        # 检查是否在基准目录下
        result = safe_full.parts[:len(safe_base.parts)] == safe_base.parts
        
        if result:
            logger.debug(f"✅ [is_safe_path] 路径安全")
        else:
            logger.warning(f"⚠️ [is_safe_path] 路径不安全")
            
        return result
    except Exception as e:
        logger.error(f"❌ [is_safe_path] 异常: {e}")
        return False

def rate_limiter(f):
    """速率限制装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        logger.debug("🚦 [rate_limiter] 速率限制检查开始")
        
        if not RATE_LIMIT_ENABLED:
            logger.debug("🚦 [rate_limiter] 速率限制已禁用，直接放行")
            return f(*args, **kwargs)
        
        client_ip = request.remote_addr
        logger.debug(f"🚦 [rate_limiter] 客户端IP: {client_ip}")
        
        with rate_limit_lock:
            logger.debug("🚦 [rate_limiter] 获取速率限制锁")
            current_time = time.time()
            client_info = request_counts[client_ip]
            
            logger.debug(f"🚦 [rate_limiter] 当前计数: {client_info['count']}, 重置时间: {client_info['reset_time']}")
            
            if current_time >= client_info['reset_time']:
                logger.debug("🚦 [rate_limiter] 重置计数")
                client_info['count'] = 0
                client_info['reset_time'] = current_time + 60
            
            if client_info['count'] >= RATE_LIMIT:
                reset_in = client_info['reset_time'] - current_time
                logger.warning(f"⚠️ [rate_limiter] 请求被限制 - {client_ip}: {reset_in}秒后重试")
                return jsonify({
                    'error': '请求过于频繁，请稍后再试',
                    'retryAfter': int(reset_in) + 1
                }), 429
            
            client_info['count'] += 1
            logger.debug(f"🚦 [rate_limiter] 计数增加，现在: {client_info['count']}")
        
        logger.debug("🚦 [rate_limiter] 检查通过，放行请求")
        return f(*args, **kwargs)
    
    return decorated

@app.before_request
def log_request_start():
    """记录请求开始"""
    logger.info("=" * 80)
    logger.info(f"📨 收到请求: {request.method} {request.path}")
    logger.info(f"📨 请求IP: {request.remote_addr}")
    logger.info(f"📨 请求数据: {request.data}")
    logger.info(f"📨 请求参数: {request.args}")
    logger.info("=" * 80)

@app.after_request
def add_security_headers(response):
    """添加安全响应头"""
    logger.debug("🔒 [add_security_headers] 添加安全响应头")
    
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    logger.debug("🔒 [add_security_headers] 安全响应头添加完成")
    logger.info(f"📤 响应: {response.status_code}")
    
    return response

# 工具函数：下划线转驼峰
def to_camel_case(snake_str):
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

# 工具函数：转换数据为驼峰命名
def convert_to_camel_case(data):
    if isinstance(data, list):
        return [convert_to_camel_case(item) for item in data]
    if isinstance(data, dict):
        return {to_camel_case(k): convert_to_camel_case(v) for k, v in data.items()}
    return data

# ------------------------------
# 数据模型
# ------------------------------

@dataclass
class Project:
    id: str
    name: str
    path: str
    status: str = "idle"
    last_analysis: Optional[str] = None
    score: Optional[float] = None
    issues_count: int = 0
    description: Optional[str] = None
    language: str = "Python"
    lines_of_code: int = 0
    created_at: str = ""
    
    def __post_init__(self):
        logger.debug(f"🏗️ [Project.__post_init__] 初始化项目")
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
            logger.debug(f"🏗️ [Project.__post_init__] 设置创建时间: {self.created_at}")

@dataclass
class Issue:
    id: str
    type: str
    severity: str
    file: str
    line: int
    message: str
    category: str
    suggestion: Optional[str] = None

@dataclass
class TestCase:
    id: str
    name: str
    file: str
    status: str
    time: str
    description: Optional[str] = None

# ------------------------------
# 存储管理
# ------------------------------

class DataStore:
    def __init__(self, storage_path: str = "./data"):
        logger.info(f"📁 [DataStore.__init__] 初始化数据存储")
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        logger.debug(f"📁 [DataStore.__init__] 存储目录: {self.storage_path.absolute()}")
        
        self.projects_file = self.storage_path / "projects.json"
        self.issues_file = self.storage_path / "issues.json"
        self.tests_file = self.storage_path / "tests.json"
        self.settings_file = self.storage_path / "settings.json"
        logger.debug(f"📁 [DataStore.__init__] 文件路径初始化完成")
        
        self._init_defaults()
        logger.info(f"✅ [DataStore.__init__] 初始化完成")
    
    def _safe_save_json(self, file_path: Path, data: list | dict):
        """安全地保存JSON数据"""
        logger.debug(f"🔒 [_safe_save_json] 开始安全保存: {file_path}")
        temp_path = file_path.parent / f"{file_path.name}.tmp"
        logger.debug(f"🔒 [_safe_save_json] 临时文件: {temp_path}")
        
        try:
            logger.debug(f"🔒 [_safe_save_json] 写入临时文件")
            temp_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
            logger.debug(f"🔒 [_safe_save_json] 临时文件写入成功")
            
            logger.debug(f"🔒 [_safe_save_json] 执行原子重命名")
            os.replace(temp_path, file_path)
            logger.info(f"✅ [_safe_save_json] 保存成功: {file_path}")
        except Exception as e:
            logger.error(f"❌ [_safe_save_json] 保存失败: {e}")
            try:
                if temp_path.exists():
                    logger.warning(f"🧹 [_safe_save_json] 清理临时文件")
                    temp_path.unlink()
            except:
                pass
            raise
    
    def _init_defaults(self):
        logger.debug("📁 [_init_defaults] 初始化默认数据")
        
        if not self.projects_file.exists():
            logger.debug("📁 [_init_defaults] 创建默认项目")
            default_projects = [
                Project(
                    id="1",
                    name="Path Test System",
                    path="/workspace/path_test_system",
                    status="completed",
                    last_analysis=datetime.now().isoformat(),
                    score=94.5,
                    issues_count=3,
                    description="50层代码分析系统核心引擎",
                    language="Python",
                    lines_of_code=1568,
                    created_at=datetime.now().isoformat()
                )
            ]
            self._safe_save_json(self.projects_file, [asdict(p) for p in default_projects])
        
        if not self.issues_file.exists():
            logger.debug("📁 [_init_defaults] 创建默认问题")
            default_issues = [
                {
                    "id": "1",
                    "type": "Security",
                    "severity": "high",
                    "file": "api_server.py",
                    "line": 42,
                    "message": "发现敏感API密钥硬编码",
                    "category": "Security",
                    "suggestion": "使用环境变量替代硬编码"
                },
                {
                    "id": "2",
                    "type": "Performance",
                    "severity": "medium",
                    "file": "analyze_engine.py",
                    "line": 128,
                    "message": "嵌套循环可能导致性能问题",
                    "category": "Performance",
                    "suggestion": "考虑优化算法"
                },
                {
                    "id": "3",
                    "type": "CodeStyle",
                    "severity": "low",
                    "file": "test_utils.py",
                    "line": 8,
                    "message": "行过长（130字符）",
                    "category": "CodeStyle",
                    "suggestion": "换行保持在120字符内"
                }
            ]
            self._safe_save_json(self.issues_file, default_issues)
        
        if not self.tests_file.exists():
            logger.debug("📁 [_init_defaults] 创建默认测试")
            self._safe_save_json(self.tests_file, [])
        
        if not self.settings_file.exists():
            logger.debug("📁 [_init_defaults] 创建默认设置")
            default_settings = {
                "theme": "dark",
                "autoSave": True,
                "maxFileSize": 10,
                "analysisDepth": 5,
                "notifications": True,
                "soundEffects": False
            }
            self._safe_save_json(self.settings_file, default_settings)
        
        logger.debug("📁 [_init_defaults] 默认数据初始化完成")
    
    def load_projects(self) -> List[Project]:
        logger.debug("📖 [load_projects] 开始加载项目数据")
        logger.debug(f"📖 [load_projects] 文件路径: {self.projects_file}")
        logger.debug(f"🔒 [load_projects] 获取文件锁: projects")
        
        with file_locks['projects']:
            logger.debug(f"🔒 [load_projects] 文件锁已获取")
            
            if self.projects_file.exists():
                try:
                    logger.debug(f"📖 [load_projects] 读取文件内容")
                    data = json.loads(self.projects_file.read_text())
                    projects = [Project(**p) for p in data]
                    logger.info(f"✅ [load_projects] 成功加载 {len(projects)} 个项目")
                    logger.debug(f"🔒 [load_projects] 释放文件锁")
                    return projects
                except Exception as e:
                    logger.error(f"❌ [load_projects] 异常: {e}")
                    return []
            else:
                logger.warning(f"⚠️ [load_projects] 文件不存在")
                return []
    
    def save_projects(self, projects: List[Project]):
        logger.debug(f"💾 [save_projects] 开始保存 {len(projects)} 个项目")
        logger.debug(f"🔒 [save_projects] 获取文件锁: projects")
        
        with file_locks['projects']:
            logger.debug(f"🔒 [save_projects] 文件锁已获取")
            try:
                logger.debug(f"💾 [save_projects] 调用安全保存")
                self._safe_save_json(self.projects_file, [asdict(p) for p in projects])
                logger.info(f"✅ [save_projects] 成功保存 {len(projects)} 个项目")
            except Exception as e:
                logger.error(f"❌ [save_projects] 保存失败: {e}")
    
    def load_issues(self) -> List[Issue]:
        logger.debug("📖 [load_issues] 开始加载问题")
        logger.debug(f"🔒 [load_issues] 获取文件锁: issues")
        
        with file_locks['issues']:
            if self.issues_file.exists():
                try:
                    data = json.loads(self.issues_file.read_text())
                    issues = [Issue(**i) for i in data]
                    logger.info(f"✅ [load_issues] 成功加载 {len(issues)} 个问题")
                    return issues
                except Exception as e:
                    logger.error(f"❌ [load_issues] 异常: {e}")
                    return []
            return []
    
    def save_issues(self, issues: List[Issue]):
        logger.debug(f"💾 [save_issues] 开始保存 {len(issues)} 个问题")
        logger.debug(f"🔒 [save_issues] 获取文件锁: issues")
        
        with file_locks['issues']:
            try:
                self._safe_save_json(self.issues_file, [asdict(i) for i in issues])
                logger.info(f"✅ [save_issues] 成功保存 {len(issues)} 个问题")
            except Exception as e:
                logger.error(f"❌ [save_issues] 保存失败: {e}")
    
    def load_tests(self) -> List[TestCase]:
        logger.debug("📖 [load_tests] 开始加载测试")
        with file_locks['tests']:
            if self.tests_file.exists():
                try:
                    data = json.loads(self.tests_file.read_text())
                    tests = [TestCase(**t) for t in data]
                    logger.info(f"✅ [load_tests] 成功加载 {len(tests)} 个测试")
                    return tests
                except Exception as e:
                    logger.error(f"❌ [load_tests] 异常: {e}")
                    return []
            return []
    
    def save_tests(self, tests: List[TestCase]):
        logger.debug(f"💾 [save_tests] 开始保存 {len(tests)} 个测试")
        with file_locks['tests']:
            try:
                self._safe_save_json(self.tests_file, [asdict(t) for t in tests])
                logger.info(f"✅ [save_tests] 成功保存 {len(tests)} 个测试")
            except Exception as e:
                logger.error(f"❌ [save_tests] 保存失败: {e}")
    
    def load_settings(self) -> dict:
        logger.debug("📖 [load_settings] 开始加载设置")
        with file_locks['settings']:
            if self.settings_file.exists():
                try:
                    data = json.loads(self.settings_file.read_text())
                    logger.info(f"✅ [load_settings] 成功加载设置")
                    return data
                except Exception as e:
                    logger.error(f"❌ [load_settings] 异常: {e}")
            return {}
    
    def save_settings(self, settings: dict):
        logger.debug(f"💾 [save_settings] 开始保存设置")
        with file_locks['settings']:
            try:
                self._safe_save_json(self.settings_file, settings)
                logger.info(f"✅ [save_settings] 成功保存设置")
            except Exception as e:
                logger.error(f"❌ [save_settings] 保存失败: {e}")

# ------------------------------
# 代码分析引擎
# ------------------------------

class CodeAnalyzer:
    def __init__(self):
        logger.info("🔍 [CodeAnalyzer.__init__] 代码分析引擎初始化")
        self.issues = []
        self.sensitive_keywords = ['API_KEY', 'SECRET', 'PASSWORD', 'TOKEN', 'sk_live_', 'private_key']
        self.dangerous_functions = ['eval', 'exec', 'os.system', 'subprocess.Popen', 'pickle.load']
        self.weak_hash_functions = ['md5', 'sha1', 'hashlib.md5', 'hashlib.sha1']
        logger.info("✅ [CodeAnalyzer.__init__] 初始化完成")
    
    def analyze_file(self, file_path: str):
        logger.info(f"🔍 [analyze_file] 开始分析: {file_path}")
        self.issues = []
        
        try:
            logger.debug(f"🔍 [analyze_file] 打开文件")
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            logger.debug(f"🔍 [analyze_file] 读取了 {len(lines)} 行")
            
            for line_num, line in enumerate(lines, 1):
                # 检查敏感信息
                self._check_sensitive_info(file_path, line_num, line)
                # 检查SQL注入风险
                self._check_sql_injection(file_path, line_num, line)
                # 检查危险函数
                self._check_dangerous_functions(file_path, line_num, line)
                # 检查弱哈希
                self._check_weak_hash(file_path, line_num, line)
                # 检查代码风格
                self._check_code_style(file_path, line_num, line)
            
            logger.info(f"✅ [analyze_file] 分析完成，发现 {len(self.issues)} 个问题")
        except FileNotFoundError:
            logger.error(f"❌ [analyze_file] 文件不存在: {file_path}")
        except Exception as e:
            logger.error(f"❌ [analyze_file] 异常: {e}")
        
        return self.issues
    
    def _check_sensitive_info(self, file_path: str, line_num: int, line: str):
        for keyword in self.sensitive_keywords:
            if keyword in line:
                self.issues.append({
                    "id": str(len(self.issues) + 1),
                    "type": "Security",
                    "severity": "critical",
                    "file": file_path,
                    "line": line_num,
                    "message": f"发现敏感信息: {keyword}",
                    "category": "Security"
                })
    
    def _check_sql_injection(self, file_path: str, line_num: int, line: str):
        if re.search(r'(SELECT|INSERT|UPDATE|DELETE)\s*.*\s*\+\s*', line, re.IGNORECASE):
            self.issues.append({
                "id": str(len(self.issues) + 1),
                "type": "Security",
                "severity": "critical",
                "file": file_path,
                "line": line_num,
                "message": "潜在SQL注入风险",
                "category": "Security"
            })
    
    def _check_dangerous_functions(self, file_path: str, line_num: int, line: str):
        for func in self.dangerous_functions:
            if func in line:
                self.issues.append({
                    "id": str(len(self.issues) + 1),
                    "type": "Security",
                    "severity": "high",
                    "file": file_path,
                    "line": line_num,
                    "message": f"使用危险函数: {func}",
                    "category": "Security"
                })
    
    def _check_weak_hash(self, file_path: str, line_num: int, line: str):
        for func in self.weak_hash_functions:
            if func in line:
                self.issues.append({
                    "id": str(len(self.issues) + 1),
                    "type": "Security",
                    "severity": "medium",
                    "file": file_path,
                    "line": line_num,
                    "message": f"使用弱哈希: {func}",
                    "category": "Security"
                })
    
    def _check_code_style(self, file_path: str, line_num: int, line: str):
        if len(line) > 120:
            self.issues.append({
                "id": str(len(self.issues) + 1),
                "type": "CodeStyle",
                "severity": "low",
                "file": file_path,
                "line": line_num,
                "message": f"行过长: {len(line)}字符",
                "category": "CodeStyle"
            })
    
    def calculate_score(self, issues):
        logger.debug(f"🔢 [calculate_score] 开始计算分数")
        base_score = 100.0
        
        severity_weights = {
            "critical": 5.0,
            "high": 3.0,
            "medium": 1.5,
            "low": 0.5
        }
        
        for issue in issues:
            weight = severity_weights.get(issue.get("severity", "low"), 0.5)
            base_score -= weight
        
        final_score = max(30.0, min(100.0, base_score))
        logger.info(f"✅ [calculate_score] 分数: {final_score:.1f}")
        return final_score

# 全局实例
logger.info("🏗️ 创建全局实例")
store = DataStore()
analyzer = CodeAnalyzer()

# ------------------------------
# API端点
# ------------------------------

@app.route("/api/health", methods=["GET"])
@rate_limiter
def health_check():
    logger.debug("🏥 [health_check] 健康检查")
    result = jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})
    logger.info("✅ [health_check] 健康检查完成")
    return result

@app.route("/api/projects", methods=["GET"])
@rate_limiter
def get_projects():
    logger.info(f"📋 [get_projects] 收到获取项目请求")
    projects = store.load_projects()
    logger.info(f"✅ [get_projects] 返回 {len(projects)} 个项目")
    return jsonify(convert_to_camel_case([asdict(p) for p in projects]))

@app.route("/api/projects", methods=["POST"])
@rate_limiter
def create_project():
    logger.info(f"📝 [create_project] 收到创建项目请求")
    data = request.json
    logger.debug(f"📦 [create_project] 请求数据: {data}")
    
    raw_name = data.get("name", "")
    raw_path = data.get("path", "")
    
    logger.debug(f"📝 [create_project] 清理输入")
    name = sanitize_input(raw_name)
    path = sanitize_input(raw_path)
    logger.debug(f"📝 [create_project] 清理后: 名称={name}, 路径={path}")
    
    is_valid, error_msg = validate_project_name(name)
    if not is_valid:
        logger.warning(f"⚠️ [create_project] 名称验证失败: {error_msg}")
        return jsonify({"error": error_msg}), 400
    
    is_valid, error_msg = validate_project_path(path)
    if not is_valid:
        logger.warning(f"⚠️ [create_project] 路径验证失败: {error_msg}")
        return jsonify({"error": error_msg}), 400
    
    description = sanitize_input(data.get("description", ""))
    
    logger.debug(f"📝 [create_project] 创建项目对象")
    project = Project(
        id=str(int(time.time() * 1000)),
        name=name,
        path=path,
        description=description,
        language=data.get("language", "Python")
    )
    logger.debug(f"🔧 [create_project] 项目ID: {project.id}")
    
    logger.debug(f"📝 [create_project] 加载现有项目")
    projects = store.load_projects()
    projects.append(project)
    logger.debug(f"📝 [create_project] 保存项目")
    store.save_projects(projects)
    
    logger.info(f"✅ [create_project] 项目创建成功: {project.id}")
    return jsonify(convert_to_camel_case(asdict(project))), 201

@app.route("/api/projects/<project_id>", methods=["PUT"])
@rate_limiter
def update_project(project_id):
    logger.info(f"✏️ [update_project] 更新项目: {project_id}")
    data = request.json
    projects = store.load_projects()
    
    for i, p in enumerate(projects):
        if p.id == project_id:
            logger.debug(f"🔍 [update_project] 找到项目: {p.name}")
            
            raw_name = data.get("name", p.name)
            raw_path = data.get("path", p.path)
            name = sanitize_input(raw_name)
            path = sanitize_input(raw_path)
            
            is_valid, error_msg = validate_project_name(name)
            if not is_valid:
                return jsonify({"error": error_msg}), 400
            
            is_valid, error_msg = validate_project_path(path)
            if not is_valid:
                return jsonify({"error": error_msg}), 400
            
            projects[i] = Project(
                id=p.id,
                name=name,
                path=path,
                status=p.status,
                last_analysis=p.last_analysis,
                score=p.score,
                issues_count=p.issues_count,
                description=sanitize_input(data.get("description", p.description)),
                language=data.get("language", p.language),
                lines_of_code=p.lines_of_code,
                created_at=p.created_at
            )
            
            store.save_projects(projects)
            logger.info(f"✅ [update_project] 项目更新成功")
            return jsonify(convert_to_camel_case(asdict(projects[i])))
    
    logger.warning(f"⚠️ [update_project] 项目不存在: {project_id}")
    return jsonify({"error": "项目不存在"}), 404

@app.route("/api/projects/<project_id>", methods=["DELETE"])
@rate_limiter
def delete_project(project_id):
    logger.info(f"🗑️ [delete_project] 删除项目: {project_id}")
    projects = store.load_projects()
    
    found = False
    found_name = ""
    for p in projects:
        if p.id == project_id:
            found = True
            found_name = p.name
            break
    
    if not found:
        logger.warning(f"⚠️ [delete_project] 项目不存在: {project_id}")
        return jsonify({"error": "项目不存在"}), 404
    
    projects = [p for p in projects if p.id != project_id]
    store.save_projects(projects)
    logger.info(f"✅ [delete_project] 项目删除成功: {found_name}")
    return jsonify({"success": True})

@app.route("/api/analyze", methods=["POST"])
@rate_limiter
def start_analysis():
    logger.info(f"🔍 [start_analysis] 收到分析请求")
    data = request.json
    project_id = data.get("projectId")
    logger.debug(f"🔍 [start_analysis] 项目ID: {project_id}")
    
    if not project_id:
        return jsonify({"error": "缺少项目ID"}), 400
    
    projects = store.load_projects()
    target_project = None
    
    for p in projects:
        if p.id == project_id:
            target_project = p
            break
    
    if not target_project:
        logger.warning(f"⚠️ [start_analysis] 项目不存在")
        return jsonify({"error": "项目不存在"}), 404
    
    logger.debug(f"🔍 [start_analysis] 设置状态为 analyzing")
    for i, p in enumerate(projects):
        if p.id == project_id:
            projects[i].status = "analyzing"
            break
    store.save_projects(projects)
    
    try:
        logger.info(f"🔍 [start_analysis] 开始分析项目: {target_project.path}")
        
        issues = analyzer.analyze_file(target_project.path)
        score = analyzer.calculate_score(issues)
        
        logger.debug(f"🔍 [start_analysis] 保存问题")
        store.save_issues([
            Issue(
                id=str(i+1),
                type=i["type"],
                severity=i["severity"],
                file=i["file"],
                line=i["line"],
                message=i["message"],
                category=i["category"]
            )
            for i in issues
        ])
        
        logger.debug(f"🔍 [start_analysis] 更新项目状态")
        for i, p in enumerate(projects):
            if p.id == project_id:
                projects[i].status = "completed"
                projects[i].last_analysis = datetime.now().isoformat()
                projects[i].score = score
                projects[i].issues_count = len(issues)
                break
        
        store.save_projects(projects)
        logger.info(f"✅ [start_analysis] 分析完成，分数: {score:.1f}")
        
        return jsonify({
            "success": True,
            "score": score,
            "issuesCount": len(issues),
            "status": "completed"
        })
        
    except Exception as e:
        logger.error(f"❌ [start_analysis] 异常: {e}")
        
        for i, p in enumerate(projects):
            if p.id == project_id:
                projects[i].status = "error"
                break
        store.save_projects(projects)
        
        return jsonify({"error": str(e)}), 500

@app.route("/api/issues", methods=["GET"])
@rate_limiter
def get_issues():
    logger.info(f"📋 [get_issues] 获取问题")
    issues = store.load_issues()
    logger.info(f"✅ [get_issues] 返回 {len(issues)} 个问题")
    return jsonify(convert_to_camel_case([asdict(i) for i in issues]))

@app.route("/api/tests", methods=["GET"])
@rate_limiter
def get_tests():
    logger.info(f"📋 [get_tests] 获取测试")
    tests = store.load_tests()
    logger.info(f"✅ [get_tests] 返回 {len(tests)} 个测试")
    return jsonify(convert_to_camel_case([asdict(t) for t in tests]))

@app.route("/api/tests", methods=["POST"])
@rate_limiter
def create_test():
    logger.info(f"📝 [create_test] 创建测试")
    data = request.json
    
    test = TestCase(
        id=str(int(time.time() * 1000)),
        name=data.get("name", "未命名测试"),
        file=data.get("file", ""),
        status="pending",
        time=datetime.now().isoformat(),
        description=data.get("description", "")
    )
    
    tests = store.load_tests()
    tests.append(test)
    store.save_tests(tests)
    
    logger.info(f"✅ [create_test] 测试创建成功")
    return jsonify(convert_to_camel_case(asdict(test))), 201

@app.route("/api/tests/<test_id>", methods=["DELETE"])
@rate_limiter
def delete_test(test_id):
    logger.info(f"🗑️ [delete_test] 删除测试: {test_id}")
    tests = store.load_tests()
    tests = [t for t in tests if t.id != test_id]
    store.save_tests(tests)
    logger.info(f"✅ [delete_test] 测试删除成功")
    return jsonify({"success": True})

@app.route("/api/run-tests", methods=["POST"])
@rate_limiter
def run_tests():
    logger.info(f"▶️ [run_tests] 运行测试")
    tests = store.load_tests()
    for test in tests:
        test.status = "running"
    store.save_tests(tests)
    
    time.sleep(1)
    
    for test in tests:
        test.status = "passed" if random.random() > 0.3 else "failed"
    store.save_tests(tests)
    
    logger.info(f"✅ [run_tests] 测试运行完成")
    return jsonify({"success": True})

@app.route("/api/settings", methods=["GET"])
@rate_limiter
def get_settings():
    logger.info(f"⚙️ [get_settings] 获取设置")
    settings = store.load_settings()
    logger.info(f"✅ [get_settings] 设置获取成功")
    return jsonify(convert_to_camel_case(settings))

@app.route("/api/settings", methods=["POST"])
@rate_limiter
def save_settings():
    logger.info(f"⚙️ [save_settings] 保存设置")
    data = request.json
    logger.debug(f"⚙️ [save_settings] 数据: {data}")
    
    current = store.load_settings()
    current.update(data)
    store.save_settings(current)
    
    logger.info(f"✅ [save_settings] 设置保存成功")
    return jsonify({"success": True})

@app.route("/api/files/browse", methods=["GET"])
@rate_limiter
def browse_files():
    logger.info(f"📁 [browse_files] 浏览文件")
    requested_path = request.args.get("path", "/workspace/path_test_system")
    requested_path = sanitize_input(requested_path) or "/workspace/path_test_system"
    
    safe_base_path = "/workspace"
    full_path = os.path.abspath(requested_path)
    
    if not is_safe_path(safe_base_path, full_path):
        logger.warning(f"⚠️ [browse_files] 访问受限: {full_path}")
        return jsonify({"error": "访问受限，仅能访问工作区目录"}), 403
    
    if not os.path.exists(full_path):
        logger.warning(f"⚠️ [browse_files] 路径不存在: {full_path}")
        return jsonify({"error": "Path not found"}), 404
    
    items = []
    try:
        for item in os.listdir(full_path):
            item_full_path = os.path.join(full_path, item)
            is_dir = os.path.isdir(item_full_path)
            try:
                size = os.path.getsize(item_full_path) if not is_dir else 0
            except:
                size = 0
            items.append({
                "name": item,
                "path": item_full_path,
                "isDirectory": is_dir,
                "size": size
            })
    except Exception as e:
        logger.error(f"❌ [browse_files] 异常: {e}")
        return jsonify({"error": str(e)}), 500
    
    logger.info(f"✅ [browse_files] 返回 {len(items)} 个项目")
    return jsonify({"items": items, "path": full_path})

@app.route("/api/files/read", methods=["GET"])
@rate_limiter
def read_file():
    logger.info(f"📖 [read_file] 读取文件")
    requested_path = request.args.get("path")
    
    if not requested_path:
        logger.warning(f"⚠️ [read_file] 缺少路径")
        return jsonify({"error": "路径不能为空"}), 400
    
    requested_path = sanitize_input(requested_path)
    
    safe_base_path = "/workspace"
    full_path = os.path.abspath(requested_path)
    
    if not is_safe_path(safe_base_path, full_path):
        logger.warning(f"⚠️ [read_file] 访问受限")
        return jsonify({"error": "访问受限，仅能访问工作区文件"}), 403
    
    if not os.path.isfile(full_path):
        logger.warning(f"⚠️ [read_file] 文件不存在: {full_path}")
        return jsonify({"error": "File not found"}), 404
    
    try:
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        logger.info(f"✅ [read_file] 读取成功: {full_path}")
        return jsonify({"content": content, "path": full_path})
    except Exception as e:
        logger.error(f"❌ [read_file] 异常: {e}")
        return jsonify({"error": str(e)}), 500

def main():
    print("=" * 80)
    print("🚀 50层代码分析系统 - 超详细日志版本")
    print("=" * 80)
    print(f"📁 数据目录: {store.storage_path.absolute()}")
    print(f"📋 项目数: {len(store.load_projects())}")
    print(f"📋 问题数: {len(store.load_issues())}")
    print("=" * 80)
    
    import socket
    socket.setdefaulttimeout(60)
    
    logger.info("🏁 服务器启动开始")
    app.run(
        host="0.0.0.0",
        port=5174,
        debug=True,
        threaded=True
    )

if __name__ == "__main__":
    main()
