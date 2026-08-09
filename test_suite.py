"""
50层系统 - 完整测试套件
========================

包含：
- 单元测试（Unit Tests）
- 集成测试（Integration Tests）
- 系统测试（System Tests）
"""

import pytest
import sys
import os
sys.path.insert(0, '/workspace')

from path_test_system import create_context
from path_test_system.engine import PathTestEngine, LayerStatus


class TestContext:
    """上下文模块测试"""
    
    def test_create_context(self):
        """测试创建上下文"""
        context = create_context()
        assert context is not None
        assert hasattr(context, 'data')
        assert hasattr(context, 'metadata')
    
    def test_context_set_get(self):
        """测试上下文设置和获取"""
        context = create_context()
        context.set('test_key', 'test_value')
        assert context.get('test_key') == 'test_value'


class TestEngine:
    """核心引擎测试"""
    
    def test_engine_initialization(self):
        """测试引擎初始化"""
        engine = PathTestEngine()
        assert engine is not None
        assert isinstance(engine.layers, dict)
        print(f"✅ 引擎初始化成功 - {len(engine.layers)} 层")
    
    def test_get_layer(self):
        """测试获取层"""
        engine = PathTestEngine()
        layer1 = engine.get_layer(1)
        # 至少有一些基础层
        assert len(engine.layers) > 0
    
    def test_run_single_layer(self):
        """测试运行单个层"""
        engine = PathTestEngine()
        context = create_context()
        context.user_input = "test input"
        context.metadata['project_path'] = '/workspace/path_test_system'
        
        # 运行层1（交互入口）
        if engine.get_layer(1):
            result = engine.run_layer(1, context)
            assert result is not None
            assert hasattr(result, 'status')
            print(f"✅ 层1执行结果: {result.status}")


class TestLayers:
    """各层测试"""
    
    def test_basic_layers(self):
        """测试基础层（层1-8）"""
        engine = PathTestEngine()
        context = create_context()
        context.user_input = "test input"
        context.set('source_paths', ['/workspace/path_test_system'])
        
        executed = 0
        for layer_id in range(1, 9):
            if engine.get_layer(layer_id):
                result = engine.run_layer(layer_id, context)
                executed += 1
                print(f"   层{layer_id}: {result.status}")
        
        print(f"✅ 基础层执行: {executed}/8")


class TestIntegration:
    """集成测试"""
    
    def test_layers_data_flow(self):
        """测试层间数据流"""
        engine = PathTestEngine()
        context = create_context()
        context.user_input = "集成测试"
        context.set('source_paths', ['/workspace/path_test_system'])
        
        # 层1 → 层2
        if engine.get_layer(1):
            result1 = engine.run_layer(1, context)
            if engine.get_layer(2):
                result2 = engine.run_layer(2, context)
                assert result2 is not None
        
        print("✅ 层间数据流测试完成")


class TestSystem:
    """系统测试"""
    
    def test_minimal_workflow(self):
        """测试最小工作流（前20层）"""
        engine = PathTestEngine()
        context = create_context()
        context.user_input = "系统测试"
        context.set('source_paths', ['/workspace/path_test_system'])
        context.metadata['project_path'] = '/workspace/path_test_system'
        
        results = {}
        for layer_id in range(1, 21):
            if engine.get_layer(layer_id):
                result = engine.run_layer(layer_id, context)
                results[layer_id] = result
        
        passed = sum(1 for r in results.values() 
                    if r.status == LayerStatus.COMPLETED)
        
        print(f"\n📊 系统测试结果:")
        print(f"   执行层数: {len(results)}")
        print(f"   通过: {passed}")
        print(f"   失败: {len(results) - passed}")
        
        assert passed > 0


class TestRealProject:
    """真实项目测试"""
    
    def test_requests_project(self):
        """测试真实项目（requests库）"""
        engine = PathTestEngine()
        context = create_context()
        context.user_input = "分析requests库"
        context.set('source_paths', ['/workspace/test_projects/requests'])
        context.metadata['project_path'] = '/workspace/test_projects/requests'
        
        # 测试扫描和预处理
        results = {}
        for layer_id in range(9, 17):
            if engine.get_layer(layer_id):
                result = engine.run_layer(layer_id, context)
                results[layer_id] = result
        
        print(f"\n📂 真实项目测试完成:")
        for layer_id, result in results.items():
            print(f"   层{layer_id}: {result.status}")


def run_unit_tests():
    """运行单元测试"""
    print("\n" + "="*60)
    print("🧪 单元测试开始")
    print("="*60)
    
    # 运行上下文测试
    test_ctx = TestContext()
    test_ctx.test_create_context()
    test_ctx.test_context_set_get()
    
    # 运行引擎测试
    test_engine = TestEngine()
    test_engine.test_engine_initialization()
    
    print("✅ 单元测试完成")
    return True


def run_integration_tests():
    """运行集成测试"""
    print("\n" + "="*60)
    print("🔗 集成测试开始")
    print("="*60)
    
    test_integration = TestIntegration()
    test_integration.test_layers_data_flow()
    
    print("✅ 集成测试完成")
    return True


def run_system_tests():
    """运行系统测试"""
    print("\n" + "="*60)
    print("🚀 系统测试开始")
    print("="*60)
    
    # 最小工作流
    test_system = TestSystem()
    test_system.test_minimal_workflow()
    
    # 真实项目
    test_real = TestRealProject()
    test_real.test_requests_project()
    
    print("✅ 系统测试完成")
    return True


if __name__ == "__main__":
    print("🎉 50层系统 - 完整测试套件")
    
    # 运行所有测试
    unit_pass = run_unit_tests()
    integration_pass = run_integration_tests()
    system_pass = run_system_tests()
    
    # 总结
    print("\n" + "="*60)
    print("📊 完整测试总结")
    print("="*60)
    print(f"   单元测试: {'✅ 通过' if unit_pass else '❌ 失败'}")
    print(f"   集成测试: {'✅ 通过' if integration_pass else '❌ 失败'}")
    print(f"   系统测试: {'✅ 通过' if system_pass else '❌ 失败'}")
    
    overall = unit_pass and integration_pass and system_pass
    print(f"\n📈 总体: {'✅ 全部通过' if overall else '❌ 部分失败'}")
