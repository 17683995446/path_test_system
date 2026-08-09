#!/usr/bin/env python3
"""
极端测试项目 - 包含大量代码问题
用于测试系统在极端情况下的性能
"""

import os
import sys
import json
import hashlib
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any

# ========== 问题1: 大量硬编码密钥 ==========
API_KEY_1 = "sk_live_1234567890abcdefghijklmnop"
API_KEY_2 = "sk_test_abcdefghijklmnopqrstuvwxyz"
GITHUB_TOKEN = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"
STRIPE_KEY = "sk_live_abcdefghijklmnopqrstuvwxyz"
AWS_KEY = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
DATABASE_URL = "postgresql://admin:password123@localhost:5432/prod"
REDIS_URL = "redis://:password123@localhost:6379/0"
SMTP_PASS = "smtp_password_123"

# ========== 问题2: 硬编码密码 ==========
ADMIN_PASSWORD = "admin123"
ROOT_PASSWORD = "root_secret_password"
DB_PASSWORD = "database_password_123"
API_SECRET = "api_secret_key_456"

# ========== 问题3: SQL注入漏洞 ==========
def query_users_unsafe(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return query

def search_products_unsafe(search_term):
    query = f"SELECT * FROM products WHERE name LIKE '%{search_term}%'"
    return query

def get_user_orders_unsafe(username):
    query = f"SELECT * FROM orders WHERE username = '{username}'"
    return query

# ========== 问题4: eval使用 ==========
def execute_code_unsafe(code_str):
    result = eval(code_str)
    return result

def dynamic_calculation(expr):
    return eval(f"2 {expr} 3")

def process_template(template, data):
    return eval(f"f'{template}'")

# ========== 问题5: 弱哈希算法 ==========
def hash_md5(data):
    return hashlib.md5(data.encode()).hexdigest()

def hash_sha1(data):
    return hashlib.sha1(data.encode()).hexdigest()

# ========== 问题6: 命令注入 ==========
def execute_command_unsafe(cmd):
    os.system(cmd)

def read_file_unsafe(filename):
    os.popen(f"cat {filename}")

# ========== 问题7: 敏感信息泄露 ==========
def log_sensitive_data(username, password):
    print(f"User: {username}, Password: {password}")

def save_to_log(data):
    with open('/tmp/app.log', 'a') as f:
        f.write(f"{data}\n")

# ========== 问题8: XSS漏洞 ==========
def render_html_unsafe(user_input):
    return f"<div>{user_input}</div>"

def format_email_unsafe(content):
    return f"<html><body>{content}</body></html>"

# ========== 业务逻辑代码 ==========
class UserManager:
    def __init__(self):
        self.users = []
    
    def create_user(self, username, email, password):
        user = {
            "username": username,
            "email": email,
            "password": password,
            "api_key": API_KEY_1,
            "created_at": datetime.now().isoformat()
        }
        self.users.append(user)
        return user
    
    def authenticate(self, username, password):
        if password == ADMIN_PASSWORD:
            return True
        return False

class DatabaseManager:
    def __init__(self):
        self.connection_string = DATABASE_URL
    
    def connect(self):
        conn = sqlite3.connect(':memory:')
        return conn
    
    def execute_unsafe(self, sql):
        conn = self.connect()
        cursor = conn.cursor()
        result = cursor.execute(sql)
        return result.fetchall()

class APIClient:
    def __init__(self):
        self.base_url = "https://api.example.com"
        self.api_key = API_KEY_1
    
    def fetch_data(self, endpoint):
        query = f"api/data?key={self.api_key}&endpoint={endpoint}"
        return query
    
    def upload_file(self, filename):
        log_sensitive_data(filename, self.api_key)

class CacheManager:
    def __init__(self):
        self.redis_url = REDIS_URL
    
    def get(self, key):
        os.system(f"redis-cli get {key}")
    
    def set(self, key, value):
        os.system(f"redis-cli set {key} {value}")

# ========== 更多危险函数 ==========
def process_input(user_input):
    return eval(user_input)

def evaluate_expression(expr):
    return eval(expr)

def render_template(template, context):
    return eval(f'f"""{template}"""')

def process_file_upload(filename):
    os.system(f"cp {filename} /uploads/")

def execute_sql_query(table, field, value):
    sql = f"SELECT * FROM {table} WHERE {field} = '{value}'"
    return sql

# ========== 测试代码 ==========
if __name__ == "__main__":
    manager = UserManager()
    db = DatabaseManager()
    api = APIClient()
    cache = CacheManager()
    
    # 测试用户创建
    user = manager.create_user("testuser", "test@example.com", "password123")
    print(f"Created user: {user}")
    
    # 测试数据库操作
    users = db.execute_unsafe("SELECT * FROM users")
    print(f"Found {len(users)} users")
    
    # 测试API调用
    endpoint = api.fetch_data("/users")
    print(f"API endpoint: {endpoint}")
