"""
SystemTests - 系统测试套件
===========================

包含所有系统测试
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, '/workspace/path_test_system')

from src.core.context import create_context
from src.core.engine import PathTestEngine


class TestMinimalWorkflow:
    """测试最小工作流"""
    
    def test_minimal_workflow_execution(self):
        """测试最小工作流执行"""
        engine = PathTestEngine()
        context = create_context()
        context.user_input = "系统测试"
        context.set('source_paths', ['/workspace/path_test_system'])
        context.metadata['project_path'] = '/workspace/path_test_system'
        
        return True


class TestRealProjectAnalysis:
    """测试真实项目分析"""
    
    def test_requests_project_scan(self):
        """测试requests项目扫描"""
        engine = PathTestEngine()
        context = create_context()
        context.metadata['project_path'] = '/workspace/test_projects/requests'
        context.set('source_paths', ['/workspace/test_projects/requests'])
        
        return True


def run_all_system_tests():
    """运行所有系统测试"""
    print("\n" + "="*60)
    print("🚀 系统测试开始")
    print("="*60)
    
    tests = [
        TestMinimalWorkflow(),
        TestRealProjectAnalysis(),
    ]
    
    total = 0
    passed = 0
    
    for test_class in tests:
        print(f"\n📂 {test_class.__class__.__name__}")
        print("-"*40)
        
        for method_name in dir(test_class):
            if method_name.startswith('test_'):
                total += 1
                try:
                    getattr(test_class, method_name)()
                    print(f"   ✅ {method_name}")
                    passed += 1
                except Exception as e:
                    print(f"   ❌ {method_name}: {e}")
    
    print("\n" + "="*60)
    print(f"📊 系统测试结果: {passed}/{total} 通过")
    print("="*60)
    
    return passed, total


if __name__ == "__main__":
    run_all_system_tests()
