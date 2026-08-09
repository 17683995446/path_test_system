"""
集成专业开源工具集
=================

不重复造轮子，站在巨人的肩膀上：
- ast/astroid: AST解析
- libcst: 代码转换
- rich/click: 终端UI
- pytest: 测试框架
"""

import sys
import os
import subprocess
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class OpenSourceTool:
    """开源工具定义"""
    name: str
    description: str
    import_name: str
    pip_package: str
    use_case: str


# 核心工具集
PROFESSIONAL_TOOLS = [
    # 代码分析
    OpenSourceTool(
        name="ast",
        description="Python官方抽象语法树",
        import_name="ast",
        pip_package="(built-in)",
        use_case="AST解析和遍历"
    ),
    OpenSourceTool(
        name="astroid",
        description="高级AST库，支持推理",
        import_name="astroid",
        pip_package="astroid",
        use_case="复杂的代码静态分析"
    ),
    OpenSourceTool(
        name="libcst",
        description="带语法树的精确转换",
        import_name="libcst",
        pip_package="libcst",
        use_case="代码重构和转换"
    ),
    
    # UI工具
    OpenSourceTool(
        name="rich",
        description="富文本和格式化",
        import_name="rich",
        pip_package="rich",
        use_case="终端美化、进度条、表格"
    ),
    OpenSourceTool(
        name="click",
        description="命令行接口工具",
        import_name="click",
        pip_package="click",
        use_case="CLI构建"
    ),
    
    # 测试工具
    OpenSourceTool(
        name="pytest",
        description="Python测试框架",
        import_name="pytest",
        pip_package="pytest",
        use_case="单元/集成/系统测试"
    ),
    
    # 其他
    OpenSourceTool(
        name="loguru",
        description="简单强大的日志库",
        import_name="loguru",
        pip_package="loguru",
        use_case="结构化日志"
    )
]


def check_available_tools() -> Dict[str, bool]:
    """检查哪些工具已安装"""
    available = {}
    for tool in PROFESSIONAL_TOOLS:
        try:
            if tool.import_name != '(built-in)':
                __import__(tool.import_name)
            available[tool.name] = True
        except ImportError:
            available[tool.name] = False
    return available


def install_missing_tools():
    """尝试安装缺失的工具"""
    available = check_available_tools()
    
    to_install = []
    for tool in PROFESSIONAL_TOOLS:
        if not available.get(tool.name, False) and tool.pip_package != '(built-in)':
            to_install.append(tool.pip_package)
    
    if to_install:
        print(f"📦 正在安装 {len(to_install)} 个开源工具...")
        
        for package in to_install:
            try:
                print(f"   安装: {package}")
                subprocess.run([sys.executable, "-m", "pip", "install", "-q", package])
                print(f"   ✅ {package} 安装完成")
            except Exception as e:
                print(f"   ⚠️  {package} 安装失败: {e}")
        
        print("✅ 工具安装完成！")
    else:
        print("✅ 所有核心工具已就绪！")
    
    return check_available_tools()


def print_tools_status():
    """打印工具状态"""
    available = check_available_tools()
    
    print("\n" + "="*80)
    print("🛠️  集成的专业开源工具集")
    print("="*80)
    
    print(f"\n{'工具名称':<20} {'状态':<10} {'用途':<40}")
    print("-"*80)
    
    for tool in PROFESSIONAL_TOOLS:
        status = "✅ 可用" if available.get(tool.name, False) else "❌ 未安装"
        print(f"{tool.name:<20} {status:<10} {tool.use_case:<40}")
    
    print("\n" + "="*80)
    print(f"  总计: {sum(1 for v in available.values() if v)}/{len(PROFESSIONAL_TOOLS)} 个工具可用")
    print("="*80)


def demonstrate_ast_analysis():
    """演示使用AST分析代码（使用Python官方ast）"""
    import ast
    
    print("\n" + "="*80)
    print("📊 使用Python官方AST进行代码分析")
    print("="*80)
    
    sample_code = """
def add(x, y):
    \"\"\"Add two numbers\"\"\"
    return x + y

class Calculator:
    def multiply(self, a, b):
        return a * b
"""
    
    try:
        tree = ast.parse(sample_code)
        
        # 分析
        function_count = 0
        class_count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                print(f"  ✅ 发现函数: {node.name}")
                function_count += 1
            elif isinstance(node, ast.ClassDef):
                print(f"  ✅ 发现类: {node.name}")
                class_count += 1
        
        print(f"\n  📈 统计: {function_count} 个函数, {class_count} 个类")
        
    except Exception as e:
        print(f"  ⚠️  分析失败: {e}")


def main():
    """主函数 - 演示工具集成"""
    print("="*80)
    print("🚀 专业开源工具集成 - 不重复造轮子")
    print("="*80)
    
    # 1. 检查工具
    print("\n🔍 检查工具可用性...")
    print_tools_status()
    
    # 2. 尝试安装缺失的
    install_missing_tools()
    
    # 3. 演示AST分析
    demonstrate_ast_analysis()
    
    print("\n" + "="*80)
    print("✅ 工具集成完成！")
    print("="*80)


if __name__ == "__main__":
    main()
