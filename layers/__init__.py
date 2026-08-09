"""
Layers module for the path testing system.

This module contains all 50 layers organized into 5 parts:
- Part 1: User Interaction and Task Definition (1-8)
- Part 2: Source Code Access and Preprocessing (9-16)
- Part 3: Static Analysis and Path Generation (17-32)
- Part 4: Test Case Generation and Execution (33-42)
- Part 5: Result Analysis and Output (43-50)
"""

from .part1_interaction import (
    InteractionEntryLayer,
    LifecycleManagementLayer,
    GlobalConfigLayer,
    NaturalLanguageParserLayer,
    LLMAdapterLayer,
    LLMCacheLayer,
    TestTargetUnderstandingLayer,
    RequirementMappingLayer,
)

from .part2_preprocessing import (
    SourceScanLayer,
    IncrementalCacheLayer,
    FilePreprocessLayer,
    LanguageAdapterLayer,
    SemanticSummaryLayer,
    QualityScanLayer,
    SensitiveDetectLayer,
    RiskAssessmentLayer,
)

from .part3_analysis import (
    LexerLayer,
    LightASTLayer,
    FunctionSliceLayer,
    FunctionSemanticLayer,
    DependencyAnalysisLayer,
    CFGConstructionLayer,
    CoverageMatchLayer,
    BusinessRecognizeLayer,
    PathAnnotationLayer,
    PathEnumerationLayer,
    LLMPathPruneLayer,
    UnreachableVerifyLayer,
    PathPriorityLayer,
    SmartPruneLayer,
    ExplosionProtectionLayer,
    TestDataGuideLayer,
)

from .part4_execution import (
    TestDataInferLayer,
    LLMTestDataLayer,
    TemplateRenderLayer,
    QualityEvaluateLayer,
    TestCaseOptimizeLayer,
    OrchestrateLayer,
    MockGenerateLayer,
    IsolationExecuteLayer,
    ConcurrentExecuteLayer,
    ExceptionDiagnosisLayer,
)

from .part5_output import (
    TraceCollectLayer,
    CoverageStatLayer,
    UncoveredAnalyzeLayer,
    DefectGradingLayer,
    FixSuggestionLayer,
    ReportEnhanceLayer,
    NLQueryLayer,
    PersistenceLayer,
)

__all__ = [
    # Part 1
    "InteractionEntryLayer",
    "LifecycleManagementLayer",
    "GlobalConfigLayer",
    "NaturalLanguageParserLayer",
    "LLMAdapterLayer",
    "LLMCacheLayer",
    "TestTargetUnderstandingLayer",
    "RequirementMappingLayer",
    # Part 2
    "SourceScanLayer",
    "IncrementalCacheLayer",
    "FilePreprocessLayer",
    "LanguageAdapterLayer",
    "SemanticSummaryLayer",
    "QualityScanLayer",
    "SensitiveDetectLayer",
    "RiskAssessmentLayer",
    # Part 3
    "LexerLayer",
    "LightASTLayer",
    "FunctionSliceLayer",
    "FunctionSemanticLayer",
    "DependencyAnalysisLayer",
    "CFGConstructionLayer",
    "CoverageMatchLayer",
    "BusinessRecognizeLayer",
    "PathAnnotationLayer",
    "PathEnumerationLayer",
    "LLMPathPruneLayer",
    "UnreachableVerifyLayer",
    "PathPriorityLayer",
    "SmartPruneLayer",
    "ExplosionProtectionLayer",
    "TestDataGuideLayer",
    # Part 4
    "TestDataInferLayer",
    "LLMTestDataLayer",
    "TemplateRenderLayer",
    "QualityEvaluateLayer",
    "TestCaseOptimizeLayer",
    "OrchestrateLayer",
    "MockGenerateLayer",
    "IsolationExecuteLayer",
    "ConcurrentExecuteLayer",
    "ExceptionDiagnosisLayer",
    # Part 5
    "TraceCollectLayer",
    "CoverageStatLayer",
    "UncoveredAnalyzeLayer",
    "DefectGradingLayer",
    "FixSuggestionLayer",
    "ReportEnhanceLayer",
    "NLQueryLayer",
    "PersistenceLayer",
]
