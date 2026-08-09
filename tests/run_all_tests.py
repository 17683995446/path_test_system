"""
CompleteTestSuite - 完整测试套件
=================================

运行所有测试
"""

import sys
import os
sys.path.insert(0, '/workspace/path_test_system')

from test_unit_tests import run_all_unit_tests
from test_integration_tests import run_all_integration_tests
from test_system_tests import run_all_system_tests


def count_lines_of_code():
    """统计代码行数"""
    total = 0
    file_count = 0
    
    root = '/workspace/path_test_system/src'
    if not os.path.exists(root):
        root = '/workspace/path_test_system'
    
    for current, dirs, files in os.walk(root):
        # 跳过特定目录
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules']]
        
        for f in files:
            if f.endswith('.py'):
                file_count += 1
                filepath = os.path.join(current, f)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as fp:
                        total += len(fp.readlines())
                except:
                    pass
    
    return file_count, total


def main():
    """主函数"""
    print("="*80)
    print("🎉 50层系统 - 完整测试套件 V3.2")
    print("="*80)
    
    # 统计代码
    print("\n📊 项目统计")
    print("-"*60)
    file_count, lines = count_lines_of_code()
    print(f"   文件数: {file_count}")
    print(f"   代码行数: {lines}")
    
    # 运行所有测试
    unit_pass, unit_total = run_all_unit_tests()
    int_pass, int_total = run_all_integration_tests()
    sys_pass, sys_total = run_all_system_tests()
    
    # 总结
    print("\n" + "="*80)
    print("📈 完整测试总结")
    print("="*80)
    
    total_pass = unit_pass + int_pass + sys_pass
    total_all = unit_total + int_total + sys_total
    
    print(f"\n   单元测试: {unit_pass}/{unit_total} 通过")
    print(f"   集成测试: {int_pass}/{int_total} 通过")
    print(f"   系统测试: {sys_pass}/{sys_total} 通过")
    print("-"*80)
    print(f"   总体: {total_pass}/{total_all} 通过率 {total_pass/total_all*100:.1f}%")
    
    overall = total_all > 0 and total_pass == total_all
    print(f"\n🎯 结果: {'✅ 全部通过' if overall else '⚠️ 部分通过'}")
    print("="*80)
    
    return total_pass, total_all


if __name__ == "__main__":
    main()
