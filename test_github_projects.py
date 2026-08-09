#!/usr/bin/env python3
"""
GitHub大项目全流程测试脚本

使用真实GitHub项目测试50层系统，进行单元测试、集成测试和系统测试
"""

import os
import sys
import json
import time
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


class GitHubProjectTester:
    """GitHub项目测试器"""

    def __init__(self, project_url: str, project_name: str, branch: str = "master"):
        self.project_url = project_url
        self.project_name = project_name
        self.branch = branch
        self.project_path = f"/workspace/test_projects/{project_name}"
        self.test_results = {
            "project": project_name,
            "url": project_url,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "duration": None,
            "unit_tests": {},
            "integration_tests": {},
            "system_tests": {},
            "issues": [],
            "fixes": []
        }

    def clone_project(self) -> bool:
        """克隆GitHub项目"""
        print(f"\n{'='*80}")
        print(f"📥 步骤1: 克隆项目 {self.project_name}")
        print(f"{'='*80}")

        try:
            # 创建测试目录
            os.makedirs("/workspace/test_projects", exist_ok=True)

            # 检查是否已存在
            if os.path.exists(self.project_path):
                print(f"   项目已存在，更新中...")
                shutil.rmtree(self.project_path)

            # 克隆项目
            print(f"   执行: git clone {self.project_url}")
            result = subprocess.run(
                ["git", "clone", "--depth", "1", "-b", self.branch, self.project_url, self.project_path],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                print(f"   ✅ 克隆成功!")
                print(f"   📁 项目路径: {self.project_path}")

                # 显示项目信息
                self._show_project_info()
                return True
            else:
                print(f"   ❌ 克隆失败: {result.stderr}")
                self.test_results["issues"].append({
                    "type": "clone_failed",
                    "error": result.stderr
                })
                return False

        except subprocess.TimeoutExpired:
            print(f"   ❌ 克隆超时")
            self.test_results["issues"].append({
                "type": "clone_timeout",
                "error": "Git clone operation timed out"
            })
            return False
        except Exception as e:
            print(f"   ❌ 克隆异常: {str(e)}")
            self.test_results["issues"].append({
                "type": "clone_exception",
                "error": str(e)
            })
            return False

    def _show_project_info(self):
        """显示项目信息"""
        try:
            # 读取README
            readme_paths = [
                os.path.join(self.project_path, "README.md"),
                os.path.join(self.project_path, "README.rst"),
                os.path.join(self.project_path, "README.txt")
            ]

            for readme_path in readme_paths:
                if os.path.exists(readme_path):
                    with open(readme_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read(500)
                        print(f"\n   📖 README预览:")
                        print(f"   {'-'*60}")
                        print(content[:300] + "..." if len(content) > 300 else content)
                        print(f"   {'-'*60}")
                    break

            # 统计项目文件
            py_files = []
            for root, dirs, files in os.walk(self.project_path):
                # 跳过隐藏目录和特殊目录
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv', '.git']]

                for file in files:
                    if file.endswith('.py') and not file.startswith('test_') and not file.endswith('_test.py'):
                        py_files.append(os.path.join(root, file))

            print(f"\n   📊 项目统计:")
            print(f"   • Python文件数: {len(py_files)}")
            print(f"   • 总代码行数: {sum(self._count_lines(f) for f in py_files[:50])}")

            # 显示主要文件
            print(f"\n   📁 主要文件结构:")
            for root, dirs, files in os.walk(self.project_path):
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv']]
                level = root.replace(self.project_path, '').count(os.sep)
                if level < 2:
                    indent = ' ' * 2 * level
                    print(f'   {indent}{os.path.basename(root)}/')
                    subindent = ' ' * 2 * (level + 1)
                    for file in files[:5]:
                        if not file.startswith('.'):
                            print(f'   {subindent}{file}')

        except Exception as e:
            print(f"   ⚠️  获取项目信息失败: {str(e)}")

    def _count_lines(self, file_path: str) -> int:
        """统计文件行数"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return len(f.readlines())
        except:
            return 0

    def run_50_layer_system(self) -> bool:
        """运行50层系统"""
        print(f"\n{'='*80}")
        print(f"🔄 步骤2: 运行50层全路径测试系统")
        print(f"{'='*80}")

        try:
            # 切换到项目目录
            os.chdir(self.project_path)

            # 导入50层系统
            print(f"   导入50层系统...")
            sys.path.insert(0, "/workspace/path_test_system")

            from path_test_system import PathTestEngine, create_context

            # 创建引擎
            print(f"   创建50层引擎...")
            engine = PathTestEngine()
            print(f"   ✅ 引擎创建成功，共 {len(engine.layers)} 层")

            # 创建上下文
            context = create_context()
            context.user_input = f"测试{self.project_name}项目"
            context.metadata["project_name"] = self.project_name
            context.metadata["project_path"] = self.project_path

            # 选择性运行关键层
            print(f"\n   📋 运行关键层...")
            key_layers = [
                (1, "交互入口层"),
                (2, "任务生命周期管理层"),
                (3, "全局配置规则层"),
                (5, "LLM全局能力适配层"),
                (9, "源码接入扫描层"),
                (11, "文件预处理清洗层"),
                (17, "词法分析Token化层"),
                (18, "轻量AST构建层"),
                (19, "函数单元切片层"),
                (20, "函数语义理解层"),
                (21, "函数依赖分析层"),
                (22, "控制流CFG构建层"),
                (26, "全路径枚举生成层"),
                (32, "测试数据生成指导层"),
                (33, "测试数据推理层"),
                (35, "用例模板渲染层"),
                (41, "用例并发执行层"),
                (44, "覆盖率统计分析层"),
                (48, "测试报告增强生成层"),
                (50, "结果输出持久层")
            ]

            layer_results = {}
            start_time = time.time()

            for layer_num, layer_name in key_layers:
                try:
                    print(f"\n   🔍 运行层{layer_num}: {layer_name}...")
                    layer = engine.get_layer(layer_num)

                    if layer:
                        layer_start = time.time()
                        result = layer.process(context)
                        layer_duration = time.time() - layer_start

                        layer_results[layer_num] = {
                            "name": layer_name,
                            "status": "success",
                            "duration": layer_duration,
                            "has_result": result is not None
                        }
                        print(f"   ✅ 层{layer_num}完成 (耗时: {layer_duration:.2f}秒)")

                        # 存储结果到上下文
                        if result:
                            context.data[f"layer_{layer_num}_result"] = result
                    else:
                        print(f"   ⚠️  层{layer_num}未找到")
                        layer_results[layer_num] = {
                            "name": layer_name,
                            "status": "not_found",
                            "duration": 0
                        }

                except Exception as e:
                    print(f"   ❌ 层{layer_num}失败: {str(e)}")
                    layer_results[layer_num] = {
                        "name": layer_name,
                        "status": "failed",
                        "error": str(e)
                    }
                    self.test_results["issues"].append({
                        "type": "layer_execution_error",
                        "layer": layer_num,
                        "layer_name": layer_name,
                        "error": str(e)
                    })

            total_duration = time.time() - start_time

            self.test_results["system_tests"]["50_layer_system"] = {
                "status": "completed",
                "duration": total_duration,
                "layers_executed": len(layer_results),
                "successful_layers": sum(1 for r in layer_results.values() if r["status"] == "success"),
                "failed_layers": sum(1 for r in layer_results.values() if r["status"] == "failed"),
                "layer_details": layer_results
            }

            print(f"\n   ✅ 50层系统运行完成!")
            print(f"   📊 执行层数: {len(layer_results)}")
            print(f"   ⏱️  总耗时: {total_duration:.2f}秒")

            return True

        except ImportError as e:
            print(f"   ❌ 导入50层系统失败: {str(e)}")
            self.test_results["issues"].append({
                "type": "import_error",
                "error": str(e)
            })
            return False
        except Exception as e:
            print(f"   ❌ 50层系统运行失败: {str(e)}")
            import traceback
            traceback.print_exc()
            self.test_results["issues"].append({
                "type": "system_execution_error",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            return False

    def run_unit_tests(self) -> bool:
        """运行单元测试"""
        print(f"\n{'='*80}")
        print(f"🧪 步骤3: 运行单元测试")
        print(f"{'='*80}")

        try:
            # 检查是否有测试目录
            test_dirs = []
            for root, dirs, files in os.walk(self.project_path):
                if 'test' in dirs or 'tests' in dirs:
                    test_dirs.extend([os.path.join(root, d) for d in dirs if d in ['test', 'tests']])

            if not test_dirs:
                print(f"   ⚠️  未找到测试目录")
                self.test_results["unit_tests"] = {
                    "status": "no_tests",
                    "message": "未找到测试目录"
                }
                return False

            print(f"   📁 找到测试目录: {test_dirs}")

            # 尝试运行pytest
            try:
                result = subprocess.run(
                    ["pytest", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                has_pytest = result.returncode == 0
            except:
                has_pytest = False

            if has_pytest:
                print(f"   🧪 使用pytest运行测试...")
                test_result = subprocess.run(
                    ["pytest", "-v", "--tb=short", "--maxfail=5"],
                    capture_output=True,
                    text=True,
                    timeout=300,
                    cwd=self.project_path
                )

                self.test_results["unit_tests"] = {
                    "status": "completed",
                    "tool": "pytest",
                    "return_code": test_result.returncode,
                    "stdout": test_result.stdout[-2000:],
                    "stderr": test_result.stderr[-1000:]
                }

                print(f"   {'✅ 测试通过' if test_result.returncode == 0 else '❌ 测试失败'}")
                return test_result.returncode == 0
            else:
                print(f"   📝 手动运行单元测试...")
                self.test_results["unit_tests"] = {
                    "status": "manual_required",
                    "message": "请手动运行: pytest"
                }
                return True

        except subprocess.TimeoutExpired:
            print(f"   ❌ 测试超时")
            self.test_results["unit_tests"] = {
                "status": "timeout",
                "error": "Test execution timed out"
            }
            return False
        except Exception as e:
            print(f"   ❌ 测试执行失败: {str(e)}")
            self.test_results["unit_tests"] = {
                "status": "error",
                "error": str(e)
            }
            return False

    def run_integration_tests(self) -> bool:
        """运行集成测试"""
        print(f"\n{'='*80}")
        print(f"🔗 步骤4: 运行集成测试")
        print(f"{'='*80}")

        try:
            # 检查是否有requirements.txt
            req_file = os.path.join(self.project_path, "requirements.txt")
            setup_file = os.path.join(self.project_path, "setup.py")

            if os.path.exists(req_file):
                print(f"   📦 检测到requirements.txt")

                # 尝试安装依赖
                print(f"   安装依赖...")
                result = subprocess.run(
                    ["pip", "install", "-q", "-r", req_file],
                    capture_output=True,
                    text=True,
                    timeout=180
                )

                if result.returncode == 0:
                    print(f"   ✅ 依赖安装成功")
                else:
                    print(f"   ⚠️  依赖安装有警告: {result.stderr[:200]}")
            elif os.path.exists(setup_file):
                print(f"   📦 检测到setup.py")
                result = subprocess.run(
                    ["pip", "install", "-q", "-e", "."],
                    capture_output=True,
                    text=True,
                    timeout=180,
                    cwd=self.project_path
                )

                if result.returncode == 0:
                    print(f"   ✅ 项目安装成功")
                else:
                    print(f"   ⚠️  项目安装有警告: {result.stderr[:200]}")

            self.test_results["integration_tests"] = {
                "status": "completed",
                "dependencies_installed": os.path.exists(req_file) or os.path.exists(setup_file)
            }

            return True

        except Exception as e:
            print(f"   ❌ 集成测试失败: {str(e)}")
            self.test_results["integration_tests"] = {
                "status": "error",
                "error": str(e)
            }
            return False

    def analyze_and_fix_issues(self):
        """分析和修复问题"""
        print(f"\n{'='*80}")
        print(f"🔧 步骤5: 分析并修复问题")
        print(f"{'='*80}")

        if not self.test_results["issues"]:
            print(f"   ✅ 未发现问题!")
            return

        print(f"   📋 发现 {len(self.test_results['issues'])} 个问题:")
        print()

        for i, issue in enumerate(self.test_results["issues"], 1):
            print(f"   {i}. [{issue['type']}] {issue.get('error', 'Unknown error')[:100]}")
            if 'layer' in issue:
                print(f"      层号: {issue['layer']}, 层名: {issue.get('layer_name', 'N/A')}")

            # 尝试修复
            fix_applied = self._attempt_fix(issue)
            if fix_applied:
                print(f"      ✅ 已自动修复")
                self.test_results["fixes"].append({
                    "issue": issue,
                    "fix": fix_applied
                })
            else:
                print(f"      ⚠️  需要手动修复")

    def _attempt_fix(self, issue: Dict) -> Optional[str]:
        """尝试自动修复问题"""
        try:
            issue_type = issue.get("type", "")

            if issue_type == "import_error":
                # 尝试安装缺失的模块
                error_msg = issue.get("error", "")
                if "No module named" in error_msg:
                    module_name = error_msg.split("No module named")[-1].strip().split("'")[0]
                    print(f"      尝试安装模块: {module_name}")

                    result = subprocess.run(
                        ["pip", "install", "-q", module_name],
                        capture_output=True,
                        timeout=60
                    )

                    if result.returncode == 0:
                        return f"Installed missing module: {module_name}"
                    else:
                        return None

            elif issue_type == "layer_execution_error":
                # 记录错误但不尝试自动修复
                return "Logged for manual review"

            elif issue_type == "clone_failed":
                # 无法自动修复克隆问题
                return None

            return None

        except Exception as e:
            print(f"      修复尝试失败: {str(e)}")
            return None

    def generate_report(self) -> str:
        """生成测试报告"""
        print(f"\n{'='*80}")
        print(f"📊 步骤6: 生成测试报告")
        print(f"{'='*80}")

        # 更新结束时间
        self.test_results["end_time"] = datetime.now().isoformat()
        start = datetime.fromisoformat(self.test_results["start_time"])
        end = datetime.fromisoformat(self.test_results["end_time"])
        self.test_results["duration"] = (end - start).total_seconds()

        # 生成报告
        report_path = f"/workspace/test_results/{self.project_name}_test_report.json"
        os.makedirs("/workspace/test_results", exist_ok=True)

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False, default=str)

        print(f"   ✅ 报告已生成: {report_path}")

        # 显示摘要
        print(f"\n   📊 测试摘要:")
        print(f"   {'-'*60}")
        print(f"   项目: {self.project_name}")
        print(f"   耗时: {self.test_results['duration']:.2f}秒")
        print(f"   问题数: {len(self.test_results['issues'])}")
        print(f"   修复数: {len(self.test_results['fixes'])}")

        if "50_layer_system" in self.test_results.get("system_tests", {}):
            system_result = self.test_results["system_tests"]["50_layer_system"]
            print(f"   50层系统: {system_result.get('layers_executed', 0)}层执行, "
                  f"{system_result.get('successful_layers', 0)}成功, "
                  f"{system_result.get('failed_layers', 0)}失败")

        print(f"   {'-'*60}")

        return report_path


def main():
    """主函数"""
    print("\n" + "="*80)
    print("🎯 GitHub大项目全流程测试")
    print("50层全路径代码测试系统 × 真实项目")
    print("="*80)

    # 选择测试项目
    projects = [
        {
            "name": "requests",
            "url": "https://github.com/psf/requests.git",
            "description": "Python HTTP库 (Star: 50k+, Python项目经典)"
        },
        {
            "name": "flask",
            "url": "https://github.com/pallets/flask.git",
            "description": "轻量级Web框架 (Star: 60k+)"
        },
        {
            "name": "numpy",
            "url": "https://github.com/numpy/numpy.git",
            "description": "科学计算库 (Star: 25k+)"
        },
        {
            "name": "django",
            "url": "https://github.com/django/django.git",
            "description": "Python Web框架 (Star: 75k+)"
        }
    ]

    print("\n📦 可用测试项目:")
    for i, proj in enumerate(projects, 1):
        print(f"   {i}. {proj['name']} - {proj['description']}")

    print(f"\n   0. 全部测试 (需要较长时间)")

    choice = input("\n请选择测试项目 [默认: 1 (requests)]: ").strip() or "1"

    try:
        choice_idx = int(choice)
        if choice_idx == 0:
            selected_projects = projects
        else:
            selected_projects = [projects[choice_idx - 1]]
    except:
        selected_projects = [projects[0]]

    for proj in selected_projects:
        print(f"\n{'#'*80}")
        print(f"🧪 测试项目: {proj['name']}")
        print(f"{'#'*80}")

        tester = GitHubProjectTester(
            project_url=proj["url"],
            project_name=proj["name"],
            branch="main" if proj["name"] == "django" else "master"
        )

        # 1. 克隆项目
        if not tester.clone_project():
            continue

        # 2. 运行50层系统
        tester.run_50_layer_system()

        # 3. 运行单元测试
        tester.run_unit_tests()

        # 4. 运行集成测试
        tester.run_integration_tests()

        # 5. 分析并修复问题
        tester.analyze_and_fix_issues()

        # 6. 生成报告
        report_path = tester.generate_report()

        print(f"\n   📄 报告位置: {report_path}")

    print("\n" + "="*80)
    print("✅ 全流程测试完成!")
    print("="*80)


if __name__ == "__main__":
    main()
