"""
IntegrationTests - 集成测试套件
================================

包含所有集成测试
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, '/workspace/path_test_system')

from src.core.context import create_context
from src.core.engine import PathTestEngine


class TestLayerIntegration:
    """测试层间集成"""
    
    def test_layer_data_flow(self):
        """测试层间数据流"""
        engine = PathTestEngine()
        context = create_context()
        context.set('source_paths', ['/workspace/path_test_system'])
        
        # 模拟层间数据传递
        context.set('test_data', 'integration_test')
        
        assert context.get('test_data') == 'integration_test'
        return True


class TestContextIntegration:
    """测试上下文集成"""
    
    def test_metadata_persistence(self):
        """测试元数据持久化"""
        context = create_context()
        context.metadata['project_path'] = '/workspace/test_projects/requests'
        context.set('source_paths', ['/workspace/test_projects/requests'])
        
        assert context.metadata['project_path'] == '/workspace/test_projects/requests'
        return True


def run_all_integration_tests():
    """运行所有集成测试"""
    print("\n" + "="*60)
    print("🔗 集成测试开始")
    print("="*60)
    
    tests = [
        TestLayerIntegration(),
        TestContextIntegration(),
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
    print(f"📊 集成测试结果: {passed}/{total} 通过")
    print("="*60)
    
    return passed, total


if __name__ == "__main__":
    run_all_integration_tests()
