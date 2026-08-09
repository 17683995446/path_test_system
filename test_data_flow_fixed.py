#!/usr/bin/env python3
"""
修复后的数据流测试脚本

测试层9-20的数据流是否正确传递
"""

import sys
import os

sys.path.insert(0, '/workspace')
from path_test_system import PathTestEngine, create_context


def test_data_flow():
    """测试层间数据流"""
    print("="*80)
    print("测试层间数据流 (修复版)")
    print("="*80)

    engine = PathTestEngine()
    context = create_context()

    project_path = "/workspace/test_projects/requests"
    context.metadata['project_path'] = project_path
    context.set('source_paths', [project_path])

    # 按顺序测试
    layers_to_test = [
        (9, "源码接入扫描层"),
        (10, "增量缓存决策层"),
        (11, "文件预处理清洗层"),
        (17, "词法分析Token化层"),
        (18, "轻量AST构建层"),
        (19, "函数单元切片层"),
        (20, "函数语义理解层"),
    ]

    results = {}
    for layer_num, layer_name in layers_to_test:
        try:
            print(f"\n层{layer_num}: {layer_name}...")
            layer = engine.get_layer(layer_num)
            result = layer.process(context)

            # 显示关键数据
            if layer_num == 9:
                scanned = context.get('scanned_files', [])
                print(f"   ✅ 扫描到 {len(scanned)} 个文件")
                if scanned:
                    print(f"      第一个文件: {scanned[0].get('file_path', 'N/A')}")
                    print(f"      文件内容长度: {len(scanned[0].get('content', ''))} 字符")

            elif layer_num == 10:
                cache_decision = context.get('cache_decision', {})
                print(f"   ✅ 缓存决策完成")

            elif layer_num == 11:
                preprocessed = context.get('preprocessed_files', [])
                combined_source = context.get('preprocessed_source', '')
                print(f"   ✅ 预处理文件数: {len(preprocessed)}")
                print(f"      合并代码长度: {len(combined_source)} 字符")

            elif layer_num == 17:
                tokens = context.get('tokens', [])
                print(f"   ✅ Token数量: {len(tokens)}")

            elif layer_num == 18:
                ast_root = context.get('ast_root')
                print(f"   ✅ AST根节点: {type(ast_root).__name__ if ast_root else 'None'}")

            elif layer_num == 19:
                slices = context.get('function_slices', [])
                print(f"   ✅ 函数切片数量: {len(slices)}")

            elif layer_num == 20:
                semantics = context.get('function_semantics', [])
                print(f"   ✅ 函数语义数量: {len(semantics)}")

            results[layer_num] = {"status": "success"}

        except Exception as e:
            import traceback
            print(f"   ❌ 失败: {str(e)}")
            results[layer_num] = {"status": "failed", "error": str(e)}
            traceback.print_exc()

    # 显示结果摘要
    success = sum(1 for r in results.values() if r["status"] == "success")
    failed = sum(1 for r in results.values() if r["status"] == "failed")

    print("\n" + "="*80)
    print(f"结果: 成功 {success}/{len(results)}, 失败 {failed}")
    print("="*80)

    return results


if __name__ == "__main__":
    test_data_flow()
