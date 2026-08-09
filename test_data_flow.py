#!/usr/bin/env python3
"""
修复后的完整测试脚本

测试层11-20的数据流是否正确传递
"""

import sys
import os

sys.path.insert(0, '/workspace')
from path_test_system import PathTestEngine, create_context


def test_data_flow():
    """测试层间数据流"""
    print("="*80)
    print("测试层间数据流")
    print("="*80)

    engine = PathTestEngine()
    context = create_context()

    project_path = "/workspace/test_projects/requests"
    context.metadata['project_path'] = project_path
    context.set('source_paths', [project_path])  # 使用context.set而非metadata

    layers_to_test = [
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

            if layer_num == 11:
                preprocessed = context.get('preprocessed_source', '')
                print(f"   预处理代码长度: {len(preprocessed)} 字符")

            elif layer_num == 17:
                tokens = context.get('tokens', [])
                print(f"   Token数量: {len(tokens)}")

            elif layer_num == 18:
                ast_root = context.get('ast_root')
                print(f"   AST根节点: {ast_root is not None}")

            elif layer_num == 19:
                slices = context.get('function_slices', [])
                print(f"   函数切片数量: {len(slices)}")

            elif layer_num == 20:
                semantics = context.get('function_semantics', [])
                print(f"   函数语义数量: {len(semantics)}")

            results[layer_num] = {"status": "success"}

        except Exception as e:
            print(f"   失败: {str(e)}")
            results[layer_num] = {"status": "failed", "error": str(e)}

    success = sum(1 for r in results.values() if r["status"] == "success")
    failed = sum(1 for r in results.values() if r["status"] == "failed")

    print(f"\n结果: 成功 {success}, 失败 {failed}")

    return results


if __name__ == "__main__":
    test_data_flow()
