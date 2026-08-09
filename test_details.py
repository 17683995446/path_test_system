#!/usr/bin/env python3
"""
详细系统测试 - 查看失败的9层
"""

import sys
import os

sys.path.insert(0, '/workspace')
from path_test_system import PathTestEngine, create_context

print('=' * 80)
print('🔍 50层全路径代码测试系统 - 失败详情分析')
print('=' * 80)

# 初始化引擎和上下文
engine = PathTestEngine()
context = create_context()

print('✅ 系统初始化成功！共 {} 层'.format(len(engine.layers)))

# 设置测试项目
context.metadata['project_path'] = '/workspace/test_projects/requests'
context.metadata['source_paths'] = ['/workspace/test_projects/requests']
context.metadata['project_name'] = 'requests'
context.user_input = '测试requests项目'

# 运行完整流程
print('\n🚀 开始完整系统测试...')
test_results = {'passed': 0, 'failed': 0, 'details': []}
failed_layers = []

for layer_num in range(1, 51):
    try:
        layer = engine.get_layer(layer_num)
        if layer:
            result = layer.process(context)
            test_results['passed'] += 1
            test_results['details'].append({
                'layer': layer_num,
                'name': layer.__class__.__name__,
                'status': 'success',
                'result': type(result).__name__ if result else 'None'
            })
    except Exception as e:
        test_results['failed'] += 1
        error_detail = str(e)
        failed_layers.append({
            'layer': layer_num,
            'name': layer.__class__.__name__ if layer else 'Unknown',
            'error': error_detail
        })
        test_results['details'].append({
            'layer': layer_num,
            'status': 'failed',
            'error': error_detail
        })

# 打印失败详情
if failed_layers:
    print('\n❌ 失败详情:')
    print('=' * 80)
    for fail in failed_layers:
        print('\n🎯 层 {} - {}'.format(fail['layer'], fail['name']))
        print('   错误: {}'.format(fail['error'][:200]))

# 打印结果摘要
print('\n' + '=' * 80)
print('📊 测试结果')
print('=' * 80)
print('✅ 通过: {}'.format(test_results['passed']))
print('❌ 失败: {}'.format(test_results['failed']))
print('📈 通过率: {:.1f}%'.format(test_results['passed']/50*100))
print()
print('💡 关键数据:')

if context.get('scanned_files'):
    print('   - 扫描的文件数: {}'.format(len(context.get('scanned_files'))))

if context.get('function_slices'):
    print('   - 函数切片数: {}'.format(len(context.get('function_slices'))))

if context.get('preprocessed_source'):
    print('   - 预处理代码量: {}'.format(len(context.get('preprocessed_source'))))

print('\n✅ 系统测试完成！')
