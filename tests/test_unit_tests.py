"""
UnitTests - 单元测试套件
=========================

包含所有单元测试
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, '/workspace/path_test_system')

from src.core.context import PipelineContext, create_context
from src.core.engine import PathTestEngine, LayerExecutionStatus


class TestContextCreation:
    """测试上下文创建"""
    
    def test_create_pipeline_context(self):
        """测试创建管道上下文"""
        context = create_context()
        assert context is not None
        assert hasattr(context, 'data')
        assert hasattr(context, 'metadata')
        return True


class TestContextDataOperations:
    """测试上下文数据操作"""
    
    def test_set_and_get_data(self):
        """测试设置和获取数据"""
        context = create_context()
        context.set('test_key', 'test_value')
        assert context.get('test_key') == 'test_value'
        return True
    
    def test_get_with_default(self):
        """测试获取默认值"""
        context = create_context()
        value = context.get('nonexistent_key', 'default_value')
        assert value == 'default_value'
        return True


class TestEngineInitialization:
    """测试引擎初始化"""
    
    def test_engine_creation(self):
        """测试引擎创建"""
        engine = PathTestEngine()
        assert engine is not None
        assert isinstance(engine.layers, dict)
        return True
    
    def test_engine_has_plugins(self):
        """测试引擎有插件系统"""
        engine = PathTestEngine()
        assert hasattr(engine, 'plugins')
        return True


def run_all_unit_tests():
    """运行所有单元测试"""
    print("\n" + "="*60)
    print("🧪 单元测试开始")
    print("="*60)
    
    tests = [
        TestContextCreation(),
        TestContextDataOperations(),
        TestEngineInitialization(),
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
    print(f"📊 单元测试结果: {passed}/{total} 通过")
    print("="*60)
    
    return passed, total


if __name__ == "__main__":
    run_all_unit_tests()
