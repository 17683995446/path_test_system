#!/usr/bin/env python3
"""
大型测试项目 - 用于测试性能
"""

import os
import sys
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any

# 问题1: 硬编码的API密钥
API_KEY = "sk-1234567890abcdefghijklmnopqrstuvwxyz"
STRIPE_KEY = "sk_live_1234567890abcdefghijklmnop"
GITHUB_TOKEN = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"

DATABASE_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "admin",
    "password": "admin123",
    "database": "production_db"
}

class DataProcessor:
    def __init__(self):
        self.data = []
    
    # 问题2: 密码硬编码
    def connect_db(self):
        connection_string = f"postgresql://admin:admin123@localhost:5432/production_db"
        return connection_string
    
    def process_query(self, user_input):
        # 问题3: SQL注入漏洞
        query = f"SELECT * FROM users WHERE id = {user_input}"
        return query
    
    def execute_dynamic_code(self, code_str):
        # 问题4: eval使用
        result = eval(code_str)
        return result
    
    def hash_password(self, password):
        # 问题5: MD5弱哈希
        return hashlib.md5(password.encode()).hexdigest()
    
    def process_items(self, items):
        results = []
        for item in items:
            if item.get("active"):
                results.append(item)
        return results
    
    def validate_data(self, data):
        if not data:
            return False
        if len(data) > 1000:
            return False
        return True

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session_token = None
    
    def authenticate(self, username, password):
        # 问题6: 密码硬编码
        admin_password = "admin123"
        if password == admin_password:
            return True
        return False
    
    def fetch_data(self, endpoint):
        # 问题7: SQL注入
        query = f"api/data?filter={endpoint}&limit=100"
        return query
    
    def store_result(self, data):
        # 问题8: 敏感信息泄露
        log_entry = f"User data stored: {data}"
        print(log_entry)

class UserManager:
    def __init__(self):
        self.users = []
    
    def create_user(self, username, email, password):
        user = {
            "username": username,
            "email": email,
            "password": password,  # 明文存储
            "created_at": datetime.now().isoformat()
        }
        self.users.append(user)
        return user
    
    def authenticate_user(self, username, password):
        for user in self.users:
            # 问题9: 弱密码验证
            if user["username"] == username and user["password"] == password:
                return user
        return None
    
    def update_password(self, user_id, new_password):
        for user in self.users:
            if user.get("id") == user_id:
                # 问题10: 密码未加密
                user["password"] = new_password
                return True
        return False

def process_file(filename):
    with open(filename, 'r') as f:
        content = f.read()
    return len(content)

def calculate_checksum(data):
    return hashlib.md5(data.encode()).hexdigest()

class CacheManager:
    def __init__(self):
        self.cache = {}
    
    def set(self, key, value):
        self.cache[key] = value
    
    def get(self, key):
        return self.cache.get(key)
    
    def clear(self):
        self.cache.clear()

def validate_email(email):
    if "@" in email:
        return True
    return False

def sanitize_input(user_input):
    return user_input.replace("'", "").replace('"', "")

def generate_token(user_id):
    # 问题11: 弱随机数
    import random
    return str(random.randint(100000, 999999))

if __name__ == "__main__":
    processor = DataProcessor()
    client = APIClient("http://api.example.com")
    manager = UserManager()
    cache = CacheManager()
    
    # 测试数据
    test_data = [{"id": i, "name": f"user_{i}", "active": True} for i in range(100)]
    results = processor.process_items(test_data)
    print(f"Processed {len(results)} items")
