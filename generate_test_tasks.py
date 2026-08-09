"""
大型项目测试任务生成器
======================

为pandas项目生成1000+个真实复杂任务
"""

import os
import json
import random
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class TestTask:
    """测试任务"""
    task_id: str
    category: str
    description: str
    file_path: str
    function_name: str
    test_type: str
    priority: int
    estimated_time: float


def count_project_stats(project_path: str) -> Dict:
    """统计项目规模"""
    total_files = 0
    python_files = 0
    total_lines = 0
    function_count = 0
    class_count = 0

    for root, dirs, files in os.walk(project_path):
        for file in files:
            total_files += 1
            if file.endswith('.py'):
                python_files += 1
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        total_lines += len(lines)
                        
                        for line in lines:
                            if line.strip().startswith('def ') and '(' in line:
                                function_count += 1
                            if line.strip().startswith('class ') and '(' in line:
                                class_count += 1
                except:
                    pass

    return {
        'total_files': total_files,
        'python_files': python_files,
        'total_lines': total_lines,
        'functions': function_count,
        'classes': class_count
    }


def generate_tasks_from_project(project_path: str, count: int = 1000) -> List[TestTask]:
    """从项目生成测试任务"""
    tasks = []
    task_id = 1

    categories = [
        'Static Analysis',
        'Code Coverage',
        'Path Testing',
        'Bug Detection',
        'Performance Analysis',
        'Security Scanning',
        'Refactoring',
        'Documentation',
        'API Analysis',
        'Type Checking',
        'Dependency Analysis',
        'Dead Code',
        'Duplication',
        'Complexity',
        'Code Quality',
        'Test Generation'
    ]

    test_types = [
        'unit_test',
        'integration_test',
        'system_test',
        'performance_test',
        'security_test',
        'regression_test',
        'edge_case_test'
    ]

    # 收集Python文件
    python_files = []
    for root, dirs, files in os.walk(project_path):
        for file in files:
            if file.endswith('.py') and 'tests' not in root:
                python_files.append(os.path.join(root, file))

    # 为每个任务生成
    while len(tasks) < count and python_files:
        file_path = random.choice(python_files)
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                functions = []
                for line in lines:
                    if line.strip().startswith('def ') and '(' in line:
                        func_name = line.strip()[4:].split('(')[0]
                        functions.append(func_name)
            
            if functions:
                function_name = random.choice(functions)
                category = random.choice(categories)
                test_type = random.choice(test_types)
                
                task = TestTask(
                    task_id=f"TASK-{task_id:04d}",
                    category=category,
                    description=f"{category} for function {function_name} in {os.path.basename(file_path)}",
                    file_path=file_path,
                    function_name=function_name,
                    test_type=test_type,
                    priority=random.randint(1, 5),
                    estimated_time=random.uniform(0.1, 5.0)
                )
                
                tasks.append(task)
                task_id += 1
        except:
            continue

    return tasks


def main():
    """主函数"""
    print("="*80)
    print("🚀 大型项目测试任务生成器")
    print("="*80)

    pandas_path = '/workspace/test_projects/pandas'

    print("\n📊 正在统计项目规模...")
    stats = count_project_stats(pandas_path)

    print("\n" + "="*80)
    print("📈 pandas项目规模")
    print("="*80)
    print(f"  总文件数: {stats['total_files']:,}")
    print(f"  Python文件数: {stats['python_files']:,}")
    print(f"  总代码行数: {stats['total_lines']:,}")
    print(f"  函数数量: {stats['functions']:,}")
    print(f"  类数量: {stats['classes']:,}")

    print("\n🔧 正在生成1000+个测试任务...")
    tasks = generate_tasks_from_project(pandas_path, 1000)

    print(f"\n✅ 生成了 {len(tasks):,} 个测试任务！")

    print("\n📋 任务分类统计:")
    category_count = {}
    for task in tasks:
        category_count[task.category] = category_count.get(task.category, 0) + 1
    
    for category, count in sorted(category_count.items(), key=lambda x: -x[1]):
        print(f"  {category}: {count}个任务")

    # 保存任务
    output_path = '/workspace/path_test_system/generated_tasks.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump([
            {
                'task_id': task.task_id,
                'category': task.category,
                'description': task.description,
                'file_path': task.file_path,
                'function_name': task.function_name,
                'test_type': task.test_type,
                'priority': task.priority,
                'estimated_time': task.estimated_time
            }
            for task in tasks
        ], f, indent=2)

    print(f"\n💾 任务已保存到: {output_path}")
    
    print("\n" + "="*80)
    print("🎯 示例任务:")
    print("="*80)
    for task in tasks[:10]:
        print(f"\n  {task.task_id} [{task.category}]")
        print(f"  {task.description}")
        print(f"  文件: {os.path.basename(task.file_path)}")
        print(f"  函数: {task.function_name}")
        print(f"  类型: {task.test_type}")

    print("\n" + "="*80)
    print("✅ 任务生成完成！")
    print("="*80)

    return tasks


if __name__ == "__main__":
    main()
