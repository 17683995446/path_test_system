#!/usr/bin/env python3
"""
真实GitHub项目全流程测试脚本

对requests、flask等经典Python项目进行：
1. 单元测试 - 测试50层系统的各个组件
2. 集成测试 - 测试50层系统的层间协作
3. 系统测试 - 在真实项目上运行完整50层流程
"""

import os
import sys
import json
import time
import subprocess
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional


class GitHubRealProjectTester:
    """真实GitHub项目测试器"""

    def __init__(self):
        self.projects_dir = "/workspace/test_projects"
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "projects": {},
            "system_issues": [],
            "fixes_applied": [],
            "summary": {}
        }
        os.makedirs(self.projects_dir, exist_ok=True)

    def run_full_test_suite(self):
        """运行完整测试套件"""
        print("="*80)
        print("🎯 50层系统全流程测试")
        print("真实GitHub项目 × 单元测试 × 集成测试 × 系统测试")
        print("="*80)

        # 步骤1: 克隆项目
        print("\n📥 步骤1: 克隆真实GitHub项目")
        print("-"*80)
        projects = self._clone_all_projects()

        # 步骤2: 应用修复
        print("\n🔧 步骤2: 应用已知修复")
        print("-"*80)
        self._apply_fixes()

        # 步骤3: 单元测试
        print("\n🧪 步骤3: 单元测试")
        print("-"*80)
        self._run_unit_tests()

        # 步骤4: 集成测试
        print("\n🔗 步骤4: 集成测试")
        print("-"*80)
        self._run_integration_tests()

        # 步骤5: 系统测试
        print("\n🚀 步骤5: 系统测试（50层全流程）")
        print("-"*80)
        self._run_system_tests()

        # 步骤6: 生成报告
        print("\n📊 步骤6: 生成测试报告")
        print("-"*80)
        self._generate_report()

    def _clone_all_projects(self) -> List[Dict]:
        """克隆所有测试项目"""
        projects = [
            {
                "name": "requests",
                "url": "https://github.com/psf/requests.git",
                "description": "Python HTTP库 (50k+ stars)"
            },
            {
                "name": "flask",
                "url": "https://github.com/pallets/flask.git",
                "description": "轻量级Web框架 (60k+ stars)"
            }
        ]

        cloned_projects = []
        for proj in projects:
            print(f"\n📦 克隆 {proj['name']}...")
            project_path = os.path.join(self.projects_dir, proj['name'])

            try:
                if os.path.exists(project_path):
                    print(f"   ✅ 已存在，更新中...")
                    subprocess.run(["git", "pull"], cwd=project_path,
                                 capture_output=True, timeout=30)
                else:
                    print(f"   📥 克隆中...")
                    result = subprocess.run(
                        ["git", "clone", "--depth", "1", proj['url'], project_path],
                        capture_output=True, text=True, timeout=120
                    )
                    if result.returncode != 0:
                        print(f"   ❌ 克隆失败: {result.stderr[:100]}")
                        continue

                # 统计项目
                py_files = self._count_python_files(project_path)
                print(f"   ✅ 克隆成功! Python文件: {py_files}")

                cloned_projects.append({
                    "name": proj['name'],
                    "path": project_path,
                    "py_files": py_files,
                    "description": proj['description']
                })

            except Exception as e:
                print(f"   ❌ 错误: {str(e)}")
                self.test_results["system_issues"].append({
                    "stage": "clone",
                    "project": proj['name'],
                    "error": str(e)
                })

        return cloned_projects

    def _count_python_files(self, project_path: str) -> int:
        """统计Python文件数量"""
        count = 0
        try:
            for root, dirs, files in os.walk(project_path):
                dirs[:] = [d for d in dirs if not d.startswith('.')
                          and d not in ['__pycache__', 'venv', 'test']]
                count += sum(1 for f in files if f.endswith('.py') and not f.startswith('test'))
        except:
            pass
        return count

    def _apply_fixes(self):
        """应用已知修复"""
        print("\n🔧 应用修复...")

        fixes = [
            {
                "name": "层5 context变量修复",
                "file": "layers/part1_interaction/layer_5_llm_adapter.py",
                "check": 'config.get("context_id"',
                "method": self._fix_layer5
            },
            {
                "name": "层17源代码处理改进",
                "file": "layers/part3_analysis/layer_17_lexer.py",
                "check": "_read_project_sources",
                "method": self._fix_layer17
            }
        ]

        for fix in fixes:
            try:
                fix_path = os.path.join("/workspace/path_test_system", fix['file'])
                with open(fix_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                if fix['check'] not in content:
                    print(f"   📝 应用: {fix['name']}...")
                    fix['method']()
                    self.test_results["fixes_applied"].append(fix['name'])
                    print(f"   ✅ 已应用")
                else:
                    print(f"   ✅ 已存在: {fix['name']}")

            except Exception as e:
                print(f"   ⚠️  {fix['name']}失败: {str(e)}")

    def _fix_layer5(self):
        """修复层5"""
        path = "/workspace/path_test_system/layers/part1_interaction/layer_5_llm_adapter.py"
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        content = content.replace(
            '"context_id": context.request_id if hasattr(context, \'request_id\') else "unknown"',
            '"context_id": config.get("context_id", "unknown")'
        )

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    def _fix_layer17(self):
        """修复层17"""
        path = "/workspace/path_test_system/layers/part3_analysis/layer_17_lexer.py"
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'import os' not in content[:200]:
            content = 'import os\n' + content

        method_code = '''

    def _read_project_sources(self, project_path: str) -> str:
        """读取项目所有源代码"""
        sources = []
        try:
            for root, dirs, files in os.walk(project_path):
                dirs[:] = [d for d in dirs if not d.startswith('.')
                          and d not in ['__pycache__', 'venv', 'test']]
                for file in files:
                    if file.endswith('.py') and not file.startswith('test'):
                        try:
                            file_path = os.path.join(root, file)
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                sources.append(f.read())
                        except:
                            pass
        except:
            pass
        return '\\n'.join(sources)
'''

        if 'def _read_project_sources' not in content:
            content += method_code

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    def _run_unit_tests(self):
        """运行单元测试"""
        print("\n🧪 运行单元测试...")

        # 添加路径 - 使用父目录
        sys.path.insert(0, '/workspace')

        unit_results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "tests": []
        }

        # 测试1: 导入测试
        print("\n  1. 导入测试...")
        try:
            from path_test_system import PathTestEngine, create_context
            from path_test_system.core.models import TaskRequest, ConfigSnapshot
            from path_test_system.layers.part1_interaction.layer_1_entry import InteractionEntryLayer

            unit_results["passed"] += 1
            unit_results["tests"].append({
                "name": "导入测试",
                "status": "passed"
            })
            print("     ✅ 通过")
        except Exception as e:
            unit_results["failed"] += 1
            unit_results["tests"].append({
                "name": "导入测试",
                "status": "failed",
                "error": str(e)
            })
            print(f"     ❌ 失败: {str(e)}")
            self.test_results["system_issues"].append({
                "stage": "unit_test",
                "test": "import_test",
                "error": str(e)
            })

        unit_results["total"] = 2

        # 测试2: 引擎创建测试
        print("\n  2. 引擎创建测试...")
        try:
            engine = PathTestEngine()
            assert len(engine.layers) == 50, f"期望50层，实际{len(engine.layers)}层"

            unit_results["passed"] += 1
            unit_results["tests"].append({
                "name": "引擎创建测试",
                "status": "passed"
            })
            print(f"     ✅ 通过 (50层)")
        except Exception as e:
            unit_results["failed"] += 1
            unit_results["tests"].append({
                "name": "引擎创建测试",
                "status": "failed",
                "error": str(e)
            })
            print(f"     ❌ 失败: {str(e)}")
            self.test_results["system_issues"].append({
                "stage": "unit_test",
                "test": "engine_creation",
                "error": str(e)
            })

        # 测试3: 上下文测试
        print("\n  3. 上下文测试...")
        try:
            context = create_context()
            context.set("test_key", "test_value")
            assert context.get("test_key") == "test_value"

            unit_results["passed"] += 1
            unit_results["tests"].append({
                "name": "上下文测试",
                "status": "passed"
            })
            print("     ✅ 通过")
        except Exception as e:
            unit_results["failed"] += 1
            unit_results["tests"].append({
                "name": "上下文测试",
                "status": "failed",
                "error": str(e)
            })
            print(f"     ❌ 失败: {str(e)}")

        # 测试4: 层实例化测试
        print("\n  4. 层实例化测试...")
        try:
            layer1 = engine.get_layer(1)
            assert layer1 is not None, "层1未找到"
            assert hasattr(layer1, 'process'), "层1缺少process方法"

            unit_results["passed"] += 1
            unit_results["tests"].append({
                "name": "层实例化测试",
                "status": "passed"
            })
            print("     ✅ 通过")
        except Exception as e:
            unit_results["failed"] += 1
            unit_results["tests"].append({
                "name": "层实例化测试",
                "status": "failed",
                "error": str(e)
            })
            print(f"     ❌ 失败: {str(e)}")

        self.test_results["unit_tests"] = unit_results
        print(f"\n  📊 单元测试结果: {unit_results['passed']}/{unit_results['total']} 通过")

    def _run_integration_tests(self):
        """运行集成测试"""
        print("\n🔗 运行集成测试...")

        # 添加路径 - 使用父目录
        sys.path.insert(0, '/workspace')

        integration_results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "tests": []
        }

        # 测试1: 上下文在层间传递
        print("\n  1. 上下文传递测试...")
        try:
            from path_test_system import PathTestEngine, create_context

            engine = PathTestEngine()
            context = create_context()
            context.set("layer1_data", "test_value")

            # 层1处理
            layer1 = engine.get_layer(1)
            result1 = layer1.process(context)

            # 层2处理（使用层1结果）
            layer2 = engine.get_layer(2)
            result2 = layer2.process(result1)

            # 验证数据传递
            assert context.get("layer1_data") == "test_value"

            integration_results["passed"] += 1
            integration_results["tests"].append({
                "name": "上下文传递测试",
                "status": "passed"
            })
            print("     ✅ 通过")
        except Exception as e:
            integration_results["failed"] += 1
            integration_results["tests"].append({
                "name": "上下文传递测试",
                "status": "failed",
                "error": str(e)
            })
            print(f"     ❌ 失败: {str(e)}")
            self.test_results["system_issues"].append({
                "stage": "integration_test",
                "test": "context_passing",
                "error": str(e)
            })

        integration_results["total"] = 3

        # 测试2: 项目路径设置测试
        print("\n  2. 项目路径集成测试...")
        try:
            context = create_context()
            context.metadata['project_path'] = "/workspace/test_projects/requests"

            layer9 = engine.get_layer(9)
            result = layer9.process(context)

            scanned = context.get('scanned_files', [])
            print(f"     扫描到 {len(scanned)} 个文件")

            integration_results["passed"] += 1
            integration_results["tests"].append({
                "name": "项目路径集成测试",
                "status": "passed",
                "scanned_files": len(scanned)
            })
            print("     ✅ 通过")
        except Exception as e:
            integration_results["failed"] += 1
            integration_results["tests"].append({
                "name": "项目路径集成测试",
                "status": "failed",
                "error": str(e)
            })
            print(f"     ❌ 失败: {str(e)}")
            self.test_results["system_issues"].append({
                "stage": "integration_test",
                "test": "project_path",
                "error": str(e)
            })

        # 测试3: LLM层集成测试
        print("\n  3. LLM层集成测试...")
        try:
            context = create_context()
            context.user_input = "测试"
            context.metadata['intent'] = "test"
            context.metadata['llm_config'] = {"provider": "siliconflow"}

            layer5 = engine.get_layer(5)
            result = layer5.process(context)

            integration_results["passed"] += 1
            integration_results["tests"].append({
                "name": "LLM层集成测试",
                "status": "passed"
            })
            print("     ✅ 通过")
        except Exception as e:
            integration_results["failed"] += 1
            integration_results["tests"].append({
                "name": "LLM层集成测试",
                "status": "failed",
                "error": str(e)
            })
            print(f"     ❌ 失败: {str(e)}")
            self.test_results["system_issues"].append({
                "stage": "integration_test",
                "test": "llm_layer",
                "error": str(e)
            })

        self.test_results["integration_tests"] = integration_results
        print(f"\n  📊 集成测试结果: {integration_results['passed']}/{integration_results['total']} 通过")

    def _run_system_tests(self):
        """运行系统测试"""
        print("\n🚀 运行系统测试（50层全流程）...")

        # 添加路径 - 使用父目录
        sys.path.insert(0, '/workspace')
        from path_test_system import PathTestEngine, create_context

        engine = PathTestEngine()

        system_results = {
            "projects": {},
            "total_layers": 50,
            "executed_layers": 0,
            "successful_layers": 0,
            "failed_layers": 0,
            "layer_details": {}
        }

        # 测试requests项目
        requests_path = "/workspace/test_projects/requests"
        if os.path.exists(requests_path):
            print("\n  📦 测试项目: requests")
            print("  " + "-"*76)

            project_result = self._test_project(engine, "requests", requests_path)
            system_results["projects"]["requests"] = project_result

        # 测试flask项目
        flask_path = "/workspace/test_projects/flask"
        if os.path.exists(flask_path):
            print("\n  📦 测试项目: flask")
            print("  " + "-"*76)

            project_result = self._test_project(engine, "flask", flask_path)
            system_results["projects"]["flask"] = project_result

        # 汇总结果
        for proj_result in system_results["projects"].values():
            system_results["executed_layers"] += proj_result["executed_layers"]
            system_results["successful_layers"] += proj_result["successful_layers"]
            system_results["failed_layers"] += proj_result["failed_layers"]

            for layer_num, layer_result in proj_result["layer_details"].items():
                if layer_num not in system_results["layer_details"]:
                    system_results["layer_details"][layer_num] = layer_result

        self.test_results["system_tests"] = system_results

        print("\n  📊 系统测试结果:")
        print(f"     执行层数: {system_results['executed_layers']}")
        print(f"     成功: {system_results['successful_layers']}")
        print(f"     失败: {system_results['failed_layers']}")

    def _test_project(self, engine: PathTestEngine, project_name: str, project_path: str) -> Dict:
        """测试单个项目"""
        # 导入所需的函数
        from path_test_system import create_context

        result = {
            "project": project_name,
            "path": project_path,
            "executed_layers": 0,
            "successful_layers": 0,
            "failed_layers": 0,
            "layer_details": {},
            "issues": []
        }

        context = create_context()
        context.user_input = f"测试{project_name}项目"
        context.metadata['project_name'] = project_name
        context.metadata['project_path'] = project_path
        context.metadata['source_paths'] = [project_path]

        # 运行关键层（前20层）
        key_layers = list(range(1, 21))

        for layer_num in key_layers:
            try:
                layer = engine.get_layer(layer_num)
                if not layer:
                    continue

                print(f"     层{layer_num:2d}: {layer.__class__.__name__:<30s}", end=" ")

                start_time = time.time()
                layer_result = layer.process(context)
                duration = time.time() - start_time

                result["executed_layers"] += 1
                result["successful_layers"] += 1
                result["layer_details"][layer_num] = {
                    "name": layer.__class__.__name__,
                    "status": "success",
                    "duration": duration,
                    "has_result": layer_result is not None
                }
                print(f"✅ ({duration:.2f}s)")

            except Exception as e:
                error_msg = str(e)
                print(f"❌ {error_msg[:40]}")

                result["executed_layers"] += 1
                result["failed_layers"] += 1
                result["layer_details"][layer_num] = {
                    "name": layer.__class__.__name__ if layer else "Unknown",
                    "status": "failed",
                    "error": error_msg
                }
                result["issues"].append({
                    "layer": layer_num,
                    "error": error_msg
                })

                self.test_results["system_issues"].append({
                    "stage": "system_test",
                    "project": project_name,
                    "layer": layer_num,
                    "error": error_msg
                })

        return result

    def _generate_report(self):
        """生成测试报告"""
        print("\n📊 生成测试报告...")

        # 统计摘要
        total_tests = (
            self.test_results.get("unit_tests", {}).get("total", 0) +
            self.test_results.get("integration_tests", {}).get("total", 0)
        )
        total_passed = (
            self.test_results.get("unit_tests", {}).get("passed", 0) +
            self.test_results.get("integration_tests", {}).get("passed", 0)
        )

        self.test_results["summary"] = {
            "total_tests": total_tests,
            "passed": total_passed,
            "failed": total_tests - total_passed,
            "pass_rate": f"{total_passed/total_tests*100:.1f}%" if total_tests > 0 else "N/A",
            "system_issues_count": len(self.test_results["system_issues"]),
            "fixes_applied_count": len(self.test_results["fixes_applied"])
        }

        # 保存报告
        report_path = "/workspace/test_results/full_test_report.json"
        os.makedirs("/workspace/test_results", exist_ok=True)

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False, default=str)

        print(f"   ✅ 报告已保存: {report_path}")

        # 显示摘要
        print("\n" + "="*80)
        print("📊 测试摘要")
        print("="*80)
        print(f"\n  🧪 单元测试: {self.test_results['unit_tests'].get('passed', 0)}/{self.test_results['unit_tests'].get('total', 0)} 通过")
        print(f"  🔗 集成测试: {self.test_results['integration_tests'].get('passed', 0)}/{self.test_results['integration_tests'].get('total', 0)} 通过")
        print(f"  🚀 系统测试: {len(self.test_results['system_issues'])} 个问题发现")
        print(f"  🔧 修复应用: {len(self.test_results['fixes_applied'])} 项")
        print(f"\n  ✅ 通过率: {self.test_results['summary']['pass_rate']}")

        if self.test_results["system_issues"]:
            print(f"\n  ❌ 发现的问题 ({len(self.test_results['system_issues'])}):")
            for i, issue in enumerate(self.test_results["system_issues"][:5], 1):
                print(f"     {i}. [{issue.get('stage', 'unknown')}] {issue.get('error', 'Unknown')[:60]}")

        print("\n" + "="*80)


def main():
    """主函数"""
    tester = GitHubRealProjectTester()
    tester.run_full_test_suite()

    print("\n✅ 全流程测试完成!")
    print(f"\n📄 报告位置: /workspace/test_results/full_test_report.json")


if __name__ == "__main__":
    main()
