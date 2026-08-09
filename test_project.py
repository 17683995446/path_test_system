#!/usr/bin/env python3
"""
真实测试项目 - 一个完整的Web应用
包含各种常见的代码问题用于测试
"""

# ------------------------------
# 测试项目代码库 - 真实复杂应用
# ------------------------------

import os
import sys
import json
import hashlib
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import sqlite3
import base64

# 问题1: 敏感信息硬编码
API_KEY = "sk_live_1234567890abcdef"
DATABASE_PASSWORD = "password123"
SECRET_TOKEN = "secret_00000"

# 问题2: 未使用的导入
import math
import random
import time

# 问题3: 全局变量
user_cache = {}
session_data = {}

# 问题4: 类型安全问题
def unsafe_function(data):
    return data + 42  # 类型不安全

@dataclass
class User:
    id: int
    name: str
    email: str
    password: str  # 问题5: 密码明文存储

class Database:
    def __init__(self, db_path: str = "test.db"):
        self.db_path = db_path
        self.conn = None
        self.connect()
    
    def connect(self):
        # 问题6: 没有错误处理
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users
            (id INTEGER PRIMARY KEY, name TEXT, email TEXT, password TEXT)
        """)
        self.conn.commit()
    
    def add_user(self, user: User) -> bool:
        # 问题7: SQL注入风险
        query = f"INSERT INTO users VALUES ({user.id}, '{user.name}', '{user.email}', '{user.password}')"
        cursor = self.conn.cursor()
        cursor.execute(query)
        self.conn.commit()
        return True
    
    def get_user(self, user_id: int) -> Optional[User]:
        # 问题8: 相同的查询应该使用参数化
        query = f"SELECT * FROM users WHERE id = {user_id}"
        cursor = self.conn.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        if row:
            return User(id=row[0], name=row[1], email=row[2], password=row[3])
        return None

class AuthService:
    def __init__(self, db: Database):
        self.db = db
    
    def hash_password(self, password: str) -> str:
        # 问题9: 弱密码哈希（使用MD5）
        return hashlib.md5(password.encode()).hexdigest()
    
    def login(self, email: str, password: str) -> Optional[User]:
        # 问题10: 不安全的密码验证
        user = self.db.get_user(1)  # 假设用户ID=1
        if user and user.password == password:
            return user
        return None

class FileStorage:
    def __init__(self, storage_path: str = "./storage"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
    
    def save_file(self, filename: str, content: bytes) -> str:
        # 问题11: 路径遍历风险
        filepath = os.path.join(self.storage_path, filename)
        with open(filepath, 'wb') as f:
            f.write(content)
        return filepath
    
    def read_file(self, filename: str) -> Optional[bytes]:
        # 问题12: 没有文件类型检查
        try:
            filepath = os.path.join(self.storage_path, filename)
            with open(filepath, 'rb') as f:
                return f.read()
        except:
            return None

class Calculator:
    def __init__(self):
        self.history = []
    
    def calculate(self, expression: str) -> float:
        # 问题13: 危险的eval使用
        self.history.append(expression)
        return eval(expression)
    
    def complex_calculation(self, x: float, y: float) -> float:
        # 问题14: 函数复杂度过高
        result = 0
        for i in range(100):
            for j in range(100):
                for k in range(100):
                    result += x * y * i * j * k
        result = result * math.sin(x) * math.cos(y)
        result = result / (x * y + 1)
        result = math.sqrt(result + 1)
        result = math.pow(result, 2)
        result = math.factorial(10) * result
        return result
    
    def unused_method(self):
        # 问题15: 未使用的方法
        pass

class WebAPI:
    def __init__(self):
        self.db = Database()
        self.auth = AuthService(self.db)
        self.storage = FileStorage()
        self.calculator = Calculator()
    
    def handle_request(self, request: Dict) -> Dict:
        # 问题16: 没有输入验证
        action = request.get("action")
        
        if action == "login":
            email = request.get("email")
            password = request.get("password")
            user = self.auth.login(email, password)
            if user:
                return {"success": True, "user": {"id": user.id, "name": user.name}}
            return {"success": False, "error": "Invalid credentials"}
        
        elif action == "calculate":
            expr = request.get("expression")
            try:
                result = self.calculator.calculate(expr)
                return {"success": True, "result": result}
            except:
                return {"success": False, "error": "Calculation error"}
        
        elif action == "save_file":
            filename = request.get("filename")
            content = request.get("content", "").encode()
            self.storage.save_file(filename, base64.b64decode(content))
            return {"success": True}
        
        elif action == "read_file":
            filename = request.get("filename")
            content = self.storage.read_file(filename)
            if content:
                return {"success": True, "content": base64.b64encode(content).decode()}
            return {"success": False, "error": "File not found"}
        
        return {"success": False, "error": "Unknown action"}

# 问题17: 大型类，功能过多
class HugeClass:
    def __init__(self):
        self.data = {}
        self.counter = 0
    
    def method1(self):
        pass
    
    def method2(self):
        pass
    
    def method3(self):
        pass
    
    def method4(self):
        pass
    
    def method5(self):
        pass
    
    def method6(self):
        pass
    
    def method7(self):
        pass
    
    def method8(self):
        pass
    
    def method9(self):
        pass
    
    def method10(self):
        pass
    
    def method11(self):
        pass
    
    def method12(self):
        pass
    
    def method13(self):
        pass
    
    def method14(self):
        pass
    
    def method15(self):
        pass
    
    def method16(self):
        pass
    
    def method17(self):
        pass
    
    def method18(self):
        pass
    
    def method19(self):
        pass
    
    def method20(self):
        pass

# 问题18: 无用的函数
def helper_function_not_used():
    print("This function is never called")

# 问题19: 可变默认参数
def function_with_mutable_default(x: List = []):
    x.append(1)
    return x

# 问题20: 未完成的功能
def unfinished_feature():
    pass  # TODO: implement this
    # TODO: add validation
    # TODO: add error handling

# 主程序
def main():
    # 创建测试数据
    api = WebAPI()
    
    # 添加测试用户
    test_user = User(id=1, name="Test User", email="test@example.com", password="test123")
    api.db.add_user(test_user)
    
    # 测试计算
    result = api.handle_request({"action": "calculate", "expression": "2 + 2"})
    print("Calculation result:", result)
    
    # 测试登录
    login_result = api.handle_request({"action": "login", "email": "test@example.com", "password": "test123"})
    print("Login result:", login_result)
    
    # 问题21: 未使用的变量
    temp_var = "this is never used"
    
    # 问题22: 资源泄漏（没有关闭数据库连接）
    print("Test completed!")

if __name__ == "__main__":
    main()
