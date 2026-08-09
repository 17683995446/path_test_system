"""
50层系统 - 深度优化架构
=====================

高度模块化、产品化、基于专业开源工具集
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod


# ============== 核心数据模型 ==============
class LayerStatus(Enum):
    """层执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"


@dataclass
class LayerResult:
    """层执行结果"""
    layer_id: str
    layer_name: str
    status: LayerStatus
    output: Any = None
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class PipelineContext:
    """
    管道上下文管理器
    ==================
    
    基于专业设计模式的上下文容器
    """
    context_id: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取数据"""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any):
        """设置数据"""
        self.data[key] = value
    
    def get_meta(self, key: str, default: Any = None) -> Any:
        """获取元数据"""
        return self.metadata.get(key, default)
    
    def set_meta(self, key: str, value: Any):
        """设置元数据"""
        self.metadata[key] = value


# ============== 基础接口 ==============
class BaseLayer(ABC):
    """
    基础层接口
    ===========
    
    所有层必须实现的接口
    """
    
    layer_id: str = "base"
    layer_name: str = "Base Layer"
    layer_description: str = "Base layer interface"
    is_optional: bool = False
    depends_on: List[str] = field(default_factory=list)
    
    @abstractmethod
    def should_run(self, context: PipelineContext) -> bool:
        """判断是否应该运行"""
        return True
    
    @abstractmethod
    def run(self, context: PipelineContext) -> Any:
        """运行层 - 核心逻辑"""
        pass
    
    def validate(self, context: PipelineContext) -> bool:
        """验证前置条件"""
        return True
    
    def cleanup(self, context: PipelineContext):
        """清理资源"""
        pass


class BasePlugin(ABC):
    """
    基础插件接口
    ============
    
    可插拔的插件系统
    """
    
    plugin_id: str = "base_plugin"
    plugin_name: str = "Base Plugin"
    plugin_version: str = "1.0.0"
    
    def on_init(self, engine: Any):
        """初始化钩子"""
        pass
    
    def on_layer_start(self, layer: BaseLayer, context: PipelineContext):
        """层开始钩子"""
        pass
    
    def on_layer_complete(self, layer: BaseLayer, result: LayerResult, context: PipelineContext):
        """层完成钩子"""
        pass
    
    def on_layer_error(self, layer: BaseLayer, error: Exception, context: PipelineContext):
        """层错误钩子"""
        pass
    
    def on_shutdown(self):
        """关闭钩子"""
        pass


# ============== 核心引擎 ==============
class PathTestEngine:
    """
    50层路径测试引擎 - 高度优化版
    ==============================
    
    设计原则：
    - 高度模块化
    - 插件化架构
    - 容错性强
    - 可观测性好
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.layers: Dict[str, BaseLayer] = {}
        self.plugins: List[BasePlugin] = []
        self.results: Dict[str, LayerResult] = {}
        self.start_time = None
        
        # 初始化
        self._init_plugins()
        self._init_layers()
        
        print(f"🚀 PathTestEngine 优化版初始化完成")
    
    def _init_plugins(self):
        """初始化内置插件"""
        # 1. 日志插件
        self.plugins.append(LoggingPlugin())
        # 2. 计时插件
        self.plugins.append(TimingPlugin())
        # 3. 统计插件
        self.plugins.append(StatsPlugin())
    
    def _init_layers(self):
        """初始化各层（示例层）"""
        # 实际应用中，这里会加载所有50个真实层
        self.layers['input'] = InputLayer()
        self.layers['analyze'] = AnalysisLayer()
        self.layers['output'] = OutputLayer()
    
    def register_layer(self, layer: BaseLayer):
        """注册层"""
        self.layers[layer.layer_id] = layer
    
    def register_plugin(self, plugin: BasePlugin):
        """注册插件"""
        self.plugins.append(plugin)
        plugin.on_init(self)
    
    def run_pipeline(self, user_input: str, source_paths: List[str]) -> Dict:
        """
        运行完整管道
        
        支持容错、故障恢复、统计完整
        """
        self.start_time = time.time()
        
        # 创建上下文
        context = PipelineContext(
            context_id=f"pipeline-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            config=self.config
        )
        context.set('user_input', user_input)
        context.set('source_paths', source_paths)
        
        print(f"\n{'='*80}")
        print(f"🚀 开始执行管道: {context.context_id}")
        print(f"{'='*80}")
        
        # 运行所有层（按顺序）
        success_count = 0
        fail_count = 0
        
        for layer_id, layer in self.layers.items():
            result = self._run_single_layer(layer, context)
            self.results[layer_id] = result
            
            if result.status == LayerStatus.COMPLETED:
                success_count += 1
                print(f"  ✅ [{layer.layer_id}] {layer.layer_name} - 成功 ({result.execution_time:.2f}秒)")
            elif result.status == LayerStatus.FAILED:
                fail_count += 1
                print(f"  ❌ [{layer.layer_id}] {layer.layer_name} - 失败: {result.error}")
            else:
                print(f"  ⏭️ [{layer.layer_id}] {layer.layer_name} - {result.status.value}")
        
        # 总结
        total_time = time.time() - self.start_time
        print(f"\n{'='*80}")
        print(f"📊 管道执行完成")
        print(f"{'='*80}")
        print(f"  总耗时: {total_time:.2f}秒")
        print(f"  成功: {success_count}/{len(self.layers)}")
        print(f"  失败: {fail_count}/{len(self.layers)}")
        
        return {
            'context': context,
            'results': self.results,
            'success_count': success_count,
            'fail_count': fail_count,
            'total_time': total_time
        }
    
    def _run_single_layer(self, layer: BaseLayer, context: PipelineContext) -> LayerResult:
        """运行单个层，包含完整的错误处理"""
        start_time = time.time()
        
        # 前置检查
        if not layer.should_run(context):
            return LayerResult(
                layer_id=layer.layer_id,
                layer_name=layer.layer_name,
                status=LayerStatus.SKIPPED
            )
        
        if not layer.validate(context):
            return LayerResult(
                layer_id=layer.layer_id,
                layer_name=layer.layer_name,
                status=LayerStatus.FAILED,
                error="Validation failed"
            )
        
        # 插件 - 开始钩子
        for plugin in self.plugins:
            plugin.on_layer_start(layer, context)
        
        try:
            # 执行
            output = layer.run(context)
            execution_time = time.time() - start_time
            
            result = LayerResult(
                layer_id=layer.layer_id,
                layer_name=layer.layer_name,
                status=LayerStatus.COMPLETED,
                output=output,
                execution_time=execution_time
            )
            
            # 插件 - 完成钩子
            for plugin in self.plugins:
                plugin.on_layer_complete(layer, result, context)
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            result = LayerResult(
                layer_id=layer.layer_id,
                layer_name=layer.layer_name,
                status=LayerStatus.FAILED,
                error=str(e),
                execution_time=execution_time
            )
            
            # 插件 - 错误钩子
            for plugin in self.plugins:
                plugin.on_layer_error(layer, e, context)
            
            return result
        finally:
            layer.cleanup(context)


# ============== 示例层 ==============
class InputLayer(BaseLayer):
    """输入层 - 数据接入"""
    
    layer_id = "input"
    layer_name = "Input Layer"
    layer_description = "接收用户输入和项目配置"
    
    def should_run(self, context: PipelineContext) -> bool:
        return True
    
    def run(self, context: PipelineContext) -> Any:
        # 模拟真实的文件扫描（可以集成真正的开源工具）
        source_paths = context.get('source_paths', [])
        
        files_found = []
        for path in source_paths:
            if os.path.exists(path):
                if os.path.isdir(path):
                    for root, _, files in os.walk(path):
                        for file in files:
                            if file.endswith('.py'):
                                files_found.append(os.path.join(root, file))
                elif path.endswith('.py'):
                    files_found.append(path)
        
        context.set('files_found', files_found)
        
        return {
            'files_count': len(files_found),
            'files': files_found
        }


class AnalysisLayer(BaseLayer):
    """分析层 - 核心静态分析"""
    
    layer_id = "analyze"
    layer_name = "Analysis Layer"
    layer_description = "代码静态分析"
    
    def should_run(self, context: PipelineContext) -> bool:
        return len(context.get('files_found', [])) > 0
    
    def run(self, context: PipelineContext) -> Any:
        # 模拟静态分析（在真实实现中会集成 astroid, libcst等）
        files = context.get('files_found', [])
        analysis_results = {
            'total_files': len(files),
            'functions_count': 0,
            'classes_count': 0,
            'complexity_score': 0
        }
        
        # 简单统计
        for file in files[:10]:  # 前10个文件演示
            try:
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    analysis_results['functions_count'] += content.count('def ')
                    analysis_results['classes_count'] += content.count('class ')
            except:
                pass
        
        context.set('analysis_results', analysis_results)
        return analysis_results


class OutputLayer(BaseLayer):
    """输出层 - 结果报告"""
    
    layer_id = "output"
    layer_name = "Output Layer"
    layer_description = "生成报告和输出"
    
    def should_run(self, context: PipelineContext) -> bool:
        return True
    
    def run(self, context: PipelineContext) -> Any:
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': context.get('analysis_results', {}),
            'input': context.get('user_input', '')
        }
        context.set('final_report', report)
        return report


# ============== 内置插件 ==============
class LoggingPlugin(BasePlugin):
    """日志插件 - 记录执行过程"""
    
    plugin_id = "logging"
    plugin_name = "Logging Plugin"
    
    def on_layer_start(self, layer: BaseLayer, context: PipelineContext):
        print(f"  ⏳ 开始: [{layer.layer_id}] {layer.layer_name}")


class TimingPlugin(BasePlugin):
    """计时插件 - 性能监控"""
    
    plugin_id = "timing"
    plugin_name = "Timing Plugin"
    
    def __init__(self):
        self.timings = {}


class StatsPlugin(BasePlugin):
    """统计插件 - 数据收集"""
    
    plugin_id = "stats"
    plugin_name = "Stats Plugin"


# ============== 快捷函数 ==============
def create_engine(config: Optional[Dict] = None) -> PathTestEngine:
    """创建引擎实例"""
    return PathTestEngine(config)


def run_simple_test():
    """运行简单测试"""
    engine = create_engine()
    result = engine.run_pipeline(
        user_input="Test pandas",
        source_paths=["/workspace/test_projects/pandas"]
    )
    return result


if __name__ == "__main__":
    run_simple_test()
