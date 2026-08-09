"""
50层全路径代码测试系统
命令行入口程序
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from path_test_system import PathTestEngine, create_context
from path_test_system.core.models.task_request import TaskRequest, TaskPriority, TaskStatus
from path_test_system.core.models.task_context import TaskContext
from path_test_system.core.models.config_snapshot import ConfigSnapshot


class CLIRunner:
    """命令行运行器"""

    def __init__(self):
        self.engine: Optional[PathTestEngine] = None
        self.context: Optional[PipelineContext] = None

    def initialize(self):
        """初始化测试引擎"""
        print("🚀 初始化50层全路径测试系统...")
        self.engine = PathTestEngine()
        self.context = create_context()
        print(f"✅ 系统初始化完成，共 {len(self.engine.layers)} 层")

    def run(self, args):
        """执行测试任务"""
        print(f"\n📋 接收测试任务: {args.source_path}")

        # 第一层：交互入口
        task_request = TaskRequest(
            task_id="task_" + str(hash(args.source_path))[:8],
            source_path=args.source_path,
            priority=TaskPriority.HIGH if args.priority == "high" else TaskPriority.NORMAL,
            test_strategy=args.strategy,
            coverage_types=args.coverage.split(",") if args.coverage else ["statement", "branch"],
            output_format=args.output_format,
            language=args.language
        )

        self.context.set("task_request", task_request)

        # 第二层：任务生命周期管理
        lifecycle_layer = self.engine.get_layer(2)
        self.context = lifecycle_layer.process(self.context)

        print("✅ 任务生命周期初始化完成")

        # 第三层：全局配置加载
        config_layer = self.engine.get_layer(3)
        config_snapshot = ConfigSnapshot(
            llm_model=args.llm_model,
            max_token_limit=args.max_tokens,
            temperature=args.temperature
        )
        self.context.set("config_snapshot", config_snapshot)
        self.context = config_layer.process(self.context)
        print("✅ 全局配置加载完成")

        # 第四层：自然语言解析
        if args.command:
            nlp_layer = self.engine.get_layer(4)
            self.context.set("natural_language_command", args.command)
            self.context = nlp_layer.process(self.context)
            print("✅ 自然语言命令解析完成")

        # 第五层：LLM适配层初始化
        llm_layer = self.engine.get_layer(5)
        self.context = llm_layer.process(self.context)
        print("✅ LLM适配层初始化完成")

        # 第六层：LLM缓存层初始化
        cache_layer = self.engine.get_layer(6)
        self.context = cache_layer.process(self.context)
        print("✅ LLM缓存层初始化完成")

        # 第七层：测试目标语义理解
        test_target_layer = self.engine.get_layer(7)
        self.context = test_target_layer.process(self.context)
        print("✅ 测试目标语义理解完成")

        # 第八层：需求-代码映射
        mapping_layer = self.engine.get_layer(8)
        self.context = mapping_layer.process(self.context)
        print("✅ 需求-代码映射分析完成")

        # 第九层：源码扫描
        scan_layer = self.engine.get_layer(9)
        self.context = scan_layer.process(self.context)
        print("✅ 源码扫描完成")

        # 第十层：增量缓存决策
        cache_decision_layer = self.engine.get_layer(10)
        self.context = cache_decision_layer.process(self.context)
        print("✅ 增量缓存决策完成")

        # 第十一层：文件预处理
        preprocess_layer = self.engine.get_layer(11)
        self.context = preprocess_layer.process(self.context)
        print("✅ 文件预处理完成")

        # 第十二层：多语言适配
        language_layer = self.engine.get_layer(12)
        self.context = language_layer.process(self.context)
        print("✅ 多语言适配完成")

        # 第十三层：语义摘要生成
        summary_layer = self.engine.get_layer(13)
        self.context = summary_layer.process(self.context)
        print("✅ 语义摘要生成完成")

        # 第十四层：代码质量扫描
        quality_layer = self.engine.get_layer(14)
        self.context = quality_layer.process(self.context)
        print("✅ 代码质量扫描完成")

        # 第十五层：敏感代码检测
        sensitive_layer = self.engine.get_layer(15)
        self.context = sensitive_layer.process(self.context)
        print("✅ 敏感代码检测完成")

        # 第十六层：测试风险评估
        risk_layer = self.engine.get_layer(16)
        self.context = risk_layer.process(self.context)
        print("✅ 测试风险评估完成")

        # 第十七层：词法分析
        lexer_layer = self.engine.get_layer(17)
        self.context = lexer_layer.process(self.context)
        print("✅ 词法分析完成")

        # 第十八层：AST构建
        ast_layer = self.engine.get_layer(18)
        self.context = ast_layer.process(self.context)
        print("✅ AST构建完成")

        # 第十九层：函数切片
        slice_layer = self.engine.get_layer(19)
        self.context = slice_layer.process(self.context)
        print("✅ 函数切片完成")

        # 第二十层：函数语义理解
        func_semantic_layer = self.engine.get_layer(20)
        self.context = func_semantic_layer.process(self.context)
        print("✅ 函数语义理解完成")

        # 第二十一层：依赖分析
        dep_layer = self.engine.get_layer(21)
        self.context = dep_layer.process(self.context)
        print("✅ 函数依赖分析完成")

        # 第二十二层：CFG构建
        cfg_layer = self.engine.get_layer(22)
        self.context = cfg_layer.process(self.context)
        print("✅ 控制流CFG构建完成")

        # 第二十三层：覆盖规则匹配
        coverage_match_layer = self.engine.get_layer(23)
        self.context = coverage_match_layer.process(self.context)
        print("✅ 覆盖规则匹配完成")

        # 第二十四层：业务场景识别
        business_layer = self.engine.get_layer(24)
        self.context = business_layer.process(self.context)
        print("✅ 业务场景识别完成")

        # 第二十五层：路径语义标注
        annotation_layer = self.engine.get_layer(25)
        self.context = annotation_layer.process(self.context)
        print("✅ 路径语义标注完成")

        # 第二十六层：路径枚举
        enum_layer = self.engine.get_layer(26)
        self.context = enum_layer.process(self.context)
        print("✅ 全路径枚举完成")

        # 第二十七层：LLM路径剪枝
        prune_llm_layer = self.engine.get_layer(27)
        self.context = prune_llm_layer.process(self.context)
        print("✅ LLM路径剪枝完成")

        # 第二十八层：不可达路径验证
        unreachable_layer = self.engine.get_layer(28)
        self.context = unreachable_layer.process(self.context)
        print("✅ 不可达路径验证完成")

        # 第二十九层：路径优先级排序
        priority_layer = self.engine.get_layer(29)
        self.context = priority_layer.process(self.context)
        print("✅ 路径优先级排序完成")

        # 第三十层：智能路径剪枝
        smart_prune_layer = self.engine.get_layer(30)
        self.context = smart_prune_layer.process(self.context)
        print("✅ 智能路径剪枝完成")

        # 第三十一层：路径爆炸防护
        explosion_layer = self.engine.get_layer(31)
        self.context = explosion_layer.process(self.context)
        print("✅ 路径爆炸防护完成")

        # 第三十二层：测试数据指导
        testdata_guide_layer = self.engine.get_layer(32)
        self.context = testdata_guide_layer.process(self.context)
        print("✅ 测试数据生成指导完成")

        # 第三十三层：测试数据推理
        testdata_infer_layer = self.engine.get_layer(33)
        self.context = testdata_infer_layer.process(self.context)
        print("✅ 测试数据推理完成")

        # 第三十四层：LLM增强测试数据
        testdata_llm_layer = self.engine.get_layer(34)
        self.context = testdata_llm_layer.process(self.context)
        print("✅ LLM增强测试数据生成完成")

        # 第三十五层：模板渲染
        template_layer = self.engine.get_layer(35)
        self.context = template_layer.process(self.context)
        print("✅ 用例模板渲染完成")

        # 第三十六层：用例质量评估
        quality_evaluate_layer = self.engine.get_layer(36)
        self.context = quality_evaluate_layer.process(self.context)
        print("✅ 测试用例质量评估完成")

        # 第三十七层：用例优化
        optimize_layer = self.engine.get_layer(37)
        self.context = optimize_layer.process(self.context)
        print("✅ 测试用例优化完成")

        # 第三十八层：用例编排
        orchestrate_layer = self.engine.get_layer(38)
        self.context = orchestrate_layer.process(self.context)
        print("✅ 用例集合编排完成")

        # 第三十九层：Mock对象生成
        mock_layer = self.engine.get_layer(39)
        self.context = mock_layer.process(self.context)
        print("✅ Mock对象自动生成完成")

        # 第四十层：隔离执行环境
        isolation_layer = self.engine.get_layer(40)
        self.context = isolation_layer.process(self.context)
        print("✅ 内存级隔离执行环境创建完成")

        # 第四十一层：用例并发执行
        concurrent_layer = self.engine.get_layer(41)
        self.context = concurrent_layer.process(self.context)
        print("✅ 用例并发执行完成")

        # 第四十二层：异常诊断
        diagnosis_layer = self.engine.get_layer(42)
        self.context = diagnosis_layer.process(self.context)
        print("✅ 执行异常智能诊断完成")

        # 第四十三层：轨迹采集
        trace_layer = self.engine.get_layer(43)
        self.context = trace_layer.process(self.context)
        print("✅ 执行轨迹采集完成")

        # 第四十四层：覆盖率统计
        coverage_stat_layer = self.engine.get_layer(44)
        self.context = coverage_stat_layer.process(self.context)
        print("✅ 覆盖率统计分析完成")

        # 第四十五层：未覆盖分析
        uncovered_layer = self.engine.get_layer(45)
        self.context = uncovered_layer.process(self.context)
        print("✅ 未覆盖路径智能分析完成")

        # 第四十六层：缺陷分级
        defect_layer = self.engine.get_layer(46)
        self.context = defect_layer.process(self.context)
        print("✅ 缺陷智能分级与定位完成")

        # 第四十七层：修复建议
        fix_layer = self.engine.get_layer(47)
        self.context = fix_layer.process(self.context)
        print("✅ 代码修复建议生成完成")

        # 第四十八层：报告增强
        report_layer = self.engine.get_layer(48)
        self.context = report_layer.process(self.context)
        print("✅ 测试报告增强生成完成")

        # 第四十九层：自然语言查询
        nl_query_layer = self.engine.get_layer(49)
        self.context = nl_query_layer.process(self.context)
        print("✅ 自然语言查询接口就绪")

        # 第五十层：结果持久化
        persistence_layer = self.engine.get_layer(50)
        self.context = persistence_layer.process(self.context)
        print("✅ 结果输出持久化完成")

        print("\n" + "=" * 60)
        print("🎉 所有50层执行完成！")
        print("=" * 60)

        return self.context

    def print_layer_info(self):
        """打印所有层的元信息"""
        if not self.engine:
            self.initialize()

        print("\n📊 50层系统层级结构：\n")
        print("=" * 70)
        print(f"{'层号':<6} {'名称':<30} {'输入类型':<15} {'输出类型':<15}")
        print("=" * 70)

        for layer_num in range(1, 51):
            info = self.engine.get_layer_info(layer_num)
            if info:
                name = info["name"].replace("Layer", "")
                input_type = info["input_type"] or "-"
                output_type = info["output_type"] or "-"
                print(f"{layer_num:<6} {name:<30} {input_type:<15} {output_type:<15}")

        print("=" * 70)


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        description="50层全路径代码测试系统 V3.1",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法：
  %(prog)s --source-path ./src --strategy full-coverage
  %(prog)s --source-path ./src --coverage statement,branch,path
  %(prog)s --source-path ./src --command "测试用户登录功能"
  %(prog)s --list-layers
        """
    )

    parser.add_argument(
        "--source-path",
        type=str,
        required=False,
        help="源码路径（文件或目录）"
    )

    parser.add_argument(
        "--strategy",
        type=str,
        default="full-coverage",
        choices=["full-coverage", "risk-based", "smart", "minimal"],
        help="测试策略 (默认: full-coverage)"
    )

    parser.add_argument(
        "--coverage",
        type=str,
        default="statement,branch",
        help="覆盖率类型，逗号分隔 (默认: statement,branch)"
    )

    parser.add_argument(
        "--output-format",
        type=str,
        default="html",
        choices=["html", "json", "markdown", "all"],
        help="输出报告格式 (默认: html)"
    )

    parser.add_argument(
        "--language",
        type=str,
        default="auto",
        choices=["auto", "python", "java", "javascript", "go", "rust"],
        help="编程语言 (默认: auto)"
    )

    parser.add_argument(
        "--priority",
        type=str,
        default="normal",
        choices=["high", "normal", "low"],
        help="任务优先级 (默认: normal)"
    )

    parser.add_argument(
        "--command",
        type=str,
        help="自然语言测试命令"
    )

    parser.add_argument(
        "--llm-model",
        type=str,
        default="gpt-4",
        help="LLM模型 (默认: gpt-4)"
    )

    parser.add_argument(
        "--max-tokens",
        type=int,
        default=4000,
        help="最大Token数 (默认: 4000)"
    )

    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="LLM温度参数 (默认: 0.7)"
    )

    parser.add_argument(
        "--list-layers",
        action="store_true",
        help="列出所有50层的详细信息"
    )

    args = parser.parse_args()

    if args.list_layers:
        runner = CLIRunner()
        runner.print_layer_info()
        return 0

    if not args.source_path:
        parser.print_help()
        print("\n❌ 错误：必须提供 --source-path 参数")
        return 1

    try:
        runner = CLIRunner()
        runner.initialize()
        runner.run(args)
        print("\n✅ 测试执行成功！")
        return 0
    except Exception as e:
        print(f"\n❌ 测试执行失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
