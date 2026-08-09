"""
50层全路径代码测试系统 V3.1
完整示例测试文件

本文件包含一个简单的示例代码，用于测试50层系统
"""

class Calculator:
    """计算器类 - 用于测试的示例代码"""

    def __init__(self):
        self.result = 0
        self.history = []

    def add(self, a: int, b: int) -> int:
        """加法运算"""
        self.result = a + b
        self.history.append(f"{a} + {b} = {self.result}")
        return self.result

    def subtract(self, a: int, b: int) -> int:
        """减法运算"""
        self.result = a - b
        self.history.append(f"{a} - {b} = {self.result}")
        return self.result

    def multiply(self, a: int, b: int) -> int:
        """乘法运算"""
        if a == 0 or b == 0:
            return 0
        self.result = a * b
        self.history.append(f"{a} * {b} = {self.result}")
        return self.result

    def divide(self, a: int, b: int) -> float:
        """除法运算"""
        if b == 0:
            raise ValueError("除数不能为零")
        self.result = a / b
        self.history.append(f"{a} / {b} = {self.result}")
        return self.result

    def power(self, base: int, exponent: int) -> int:
        """幂运算"""
        if exponent < 0:
            raise ValueError("指数不能为负数")
        self.result = base ** exponent
        self.history.append(f"{base} ^ {exponent} = {self.result}")
        return self.result

    def get_history(self) -> list:
        """获取计算历史"""
        return self.history.copy()

    def clear_history(self):
        """清空计算历史"""
        self.history.clear()
        self.result = 0


class StringProcessor:
    """字符串处理器类"""

    def __init__(self):
        self.data = ""

    def set_data(self, data: str):
        """设置数据"""
        self.data = data

    def to_uppercase(self) -> str:
        """转换为大写"""
        return self.data.upper()

    def to_lowercase(self) -> str:
        """转换为小写"""
        return self.data.lower()

    def reverse(self) -> str:
        """反转字符串"""
        return self.data[::-1]

    def get_length(self) -> int:
        """获取长度"""
        return len(self.data)

    def contains(self, substring: str) -> bool:
        """检查是否包含子串"""
        return substring in self.data


def process_user_input(username: str, age: int, email: str) -> dict:
    """处理用户输入"""
    if not username:
        raise ValueError("用户名不能为空")

    if age < 0 or age > 150:
        raise ValueError("年龄不合法")

    if "@" not in email or "." not in email:
        raise ValueError("邮箱格式不正确")

    return {
        "username": username,
        "age": age,
        "email": email,
        "status": "valid"
    }


def fibonacci(n: int) -> int:
    """计算斐波那契数列"""
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)


def factorial(n: int) -> int:
    """计算阶乘"""
    if n < 0:
        raise ValueError("负数没有阶乘")
    if n <= 1:
        return 1
    return n * factorial(n - 1)


def is_prime(n: int) -> bool:
    """判断素数"""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


def find_primes(max_num: int) -> list:
    """查找范围内的所有素数"""
    primes = []
    for num in range(2, max_num + 1):
        if is_prime(num):
            primes.append(num)
    return primes


if __name__ == "__main__":
    print("=" * 60)
    print("50层测试系统示例代码")
    print("=" * 60)

    calc = Calculator()
    print(f"\n10 + 5 = {calc.add(10, 5)}")
    print(f"10 - 3 = {calc.subtract(10, 3)}")
    print(f"6 * 7 = {calc.multiply(6, 7)}")
    print(f"20 / 4 = {calc.divide(20, 4)}")

    print(f"\n计算历史: {calc.get_history()}")

    proc = StringProcessor()
    proc.set_data("Hello World")
    print(f"\n原始字符串: {proc.data}")
    print(f"大写: {proc.to_uppercase()}")
    print(f"小写: {proc.to_lowercase()}")
    print(f"反转: {proc.reverse()}")

    print(f"\n素数查找 (100以内): {find_primes(100)}")
    print(f"5! = {factorial(5)}")
    print(f"斐波那契(10) = {fibonacci(10)}")

    user = process_user_input("张三", 25, "zhangsan@example.com")
    print(f"\n用户信息: {user}")

    print("\n" + "=" * 60)
    print("✅ 示例代码执行完成")
    print("=" * 60)
