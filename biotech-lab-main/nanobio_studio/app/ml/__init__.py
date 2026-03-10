"""
NanoBio Studio ML Layer

Phase 2: Machine Learning Preparation and Ranking

This module provides:
- Feature extraction from LNP experiment records
- ML-ready dataset building
- Baseline model training (regression and classification)
- Model evaluation and persistence
- Candidate formulation ranking engine
- Export to CSV/Parquet
"""

__version__ = "2.0.0"
__author__ = "Experts Group FZE"

from .schemas import (
    MLTaskConfig,
    DatasetBuildRequest,
    TrainRequest,
    TrainResponse,
    EvaluationSummary,
    RankingRequest,
    RankingResult,
)

from .feature_builder import FeatureBuilder
from .dataset_builder import DatasetBuilder
from .preprocess import PreprocessingPipeline
from .train import ModelTrainer
from .evaluate import ModelEvaluator
from .predict import ModelPredictor
from .ranker import CandidateRanker
from .exporters import DatasetExporter, RankingResultExporter
from .persistence import ModelPersistence

__all__ = [
    "MLTaskConfig",
    "DatasetBuildRequest",
    "TrainRequest",
    "TrainResponse",
    "EvaluationSummary",
    "RankingRequest",
    "RankingResult",
    "FeatureBuilder",
    "DatasetBuilder",
    "PreprocessingPipeline",
    "ModelTrainer",
    "ModelEvaluator",
    "ModelPredictor",
    "CandidateRanker",
    "DatasetExporter",
    "RankingResultExporter",
    "ModelPersistence",
]
