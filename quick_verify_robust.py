#!/usr/bin/env python3
"""快速验证健壮性增强服务器"""

import requests
import time
import sys

BASE_URL = 'http://localhost:5174/api'

def test_health():
    """测试健康检查"""
    print('测试1: 健康检查...')
    try:
        r = requests.get(f'{BASE_URL}/health', timeout=5)
        print(f'  状态: {r.status_code}')
        data = r.json()
        print(f'  响应: {data}')
        return True
    except Exception as e:
        print(f'  ❌ 失败: {str(e)}')
        return False

def test_metrics():
    """测试指标获取"""
    print('\n测试2: 获取指标...')
    try:
        r = requests.get(f'{BASE_URL}/metrics', timeout=5)
        print(f'  状态: {r.status_code}')
        data = r.json()
        print(f'  资源: 活跃请求={data["resource"]["active_requests"]}, 成功率={data["resource"]["success_rate"]:.2f}%')
        print(f'  负载: 当前并发={data["load"]["current_concurrency"]}')
        return True
    except Exception as e:
        print(f'  ❌ 失败: {str(e)}')
        return False

def test_create_project():
    """测试创建项目"""
    print('\n测试3: 创建项目...')
    try:
        r = requests.post(f'{BASE_URL}/projects', json={
            'name': '测试_' + str(int(time.time())),
            'path': '/workspace/path_test_system',
            'description': '健壮性测试'
        }, timeout=5)
        print(f'  状态: {r.status_code}')
        print(f'  响应: {r.json()}')
        return r.status_code == 201
    except Exception as e:
        print(f'  ❌ 失败: {str(e)}')
        return False

def test_get_projects():
    """测试获取项目"""
    print('\n测试4: 获取项目...')
    try:
        r = requests.get(f'{BASE_URL}/projects', timeout=5)
        print(f'  状态: {r.status_code}')
        projects = r.json()
        print(f'  项目数: {len(projects)}')
        return True
    except Exception as e:
        print(f'  ❌ 失败: {str(e)}')
        return False

def main():
    print('=' * 70)
    print('🏆 健壮性增强服务器快速验证')
    print('=' * 70)
    
    tests = [
        test_health,
        test_metrics,
        test_create_project,
        test_get_projects,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print('\n' + '=' * 70)
    if all(results):
        print('✅ 所有测试通过！健壮性增强服务器运行正常！')
        print('=' * 70)
        sys.exit(0)
    else:
        print(f'❌ {len([r for r in results if not r])} 个测试失败')
        print('=' * 70)
        sys.exit(1)

if __name__ == '__main__':
    main()
