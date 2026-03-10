"""
ML Layer Pydantic Schemas

Define request/response models for ML operations including feature engineering,
dataset building, training, evaluation, and ranking.
"""

from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field


class TaskType(str, Enum):
    """Supported ML task types"""
    PREDICT_PARTICLE_SIZE = "predict_particle_size"
    PREDICT_PDI = "predict_pdi"
    PREDICT_TOXICITY = "predict_toxicity"
    PREDICT_UPTAKE = "predict_uptake"
    PREDICT_TRANSFECTION = "predict_transfection"
    CLASSIFY_TOXICITY_BAND = "classify_toxicity_band"
    CLASSIFY_UPTAKE_BAND = "classify_uptake_band"
    CLASSIFY_QC_PASS = "classify_qc_pass"


class ModelType(str, Enum):
    """Supported model types"""
    LINEAR_REGRESSION = "linear_regression"
    RANDOM_FOREST_REGRESSION = "random_forest_regression"
    GRADIENT_BOOSTING_REGRESSION = "gradient_boosting_regression"
    LOGISTIC_REGRESSION = "logistic_regression"
    RANDOM_FOREST_CLASSIFICATION = "random_forest_classification"
    GRADIENT_BOOSTING_CLASSIFICATION = "gradient_boosting_classification"


class MLTaskConfig(BaseModel):
    """Configuration for an ML task"""
    task_name: str = Field(..., description="Unique task identifier")
    task_type: TaskType = Field(..., description="Type of task: regression or classification")
    target_variable: str = Field(..., description="Column name to predict")
    model_types: List[ModelType] = Field(
        default=[ModelType.RANDOM_FOREST_REGRESSION],
        description="Models to train"
    )
    test_split: float = Field(default=0.2, ge=0.1, le=0.4)
    random_state: int = Field(default=42)
    filter_assay_type: Optional[str] = Field(None, description="Filter by assay type")
    filter_payload_type: Optional[str] = Field(None, description="Filter by payload type")
    filter_target: Optional[str] = Field(None, description="Filter by intended target")
    exclude_features: List[str] = Field(default_factory=list, description="Features to exclude")

    class Config:
        use_enum_values = False


class DatasetBuildRequest(BaseModel):
    """Request to build a training dataset"""
    task_config: MLTaskConfig
    include_metadata: bool = Field(default=True, description="Include traceability columns")
    handle_missing: str = Field(default="drop", description="How to handle missing values")


class TrainRequest(BaseModel):
    """Request to train models"""
    dataset_build_request: DatasetBuildRequest
    save_artifacts: bool = Field(default=True, description="Persist model artifacts")
    artifact_name: Optional[str] = Field(None, description="Custom model bundle name")


class MetricDict(BaseModel):
    """Container for evaluation metrics"""
    mae: Optional[float] = None  # Regression
    rmse: Optional[float] = None  # Regression
    r2: Optional[float] = None  # Regression
    accuracy: Optional[float] = None  # Classification
    precision: Optional[float] = None  # Classification
    recall: Optional[float] = None  # Classification
    f1: Optional[float] = None  # Classification
    roc_auc: Optional[float] = None  # Classification


class EvaluationSummary(BaseModel):
    """Summary of model evaluation on validation set"""
    model_type: ModelType
    train_metrics: MetricDict
    validation_metrics: MetricDict
    best_model: bool = Field(default=False, description="Whether this was selected as best")


class TrainResponse(BaseModel):
    """Response from training request"""
    task_name: str
    best_model_type: ModelType
    n_samples: int
    n_features: int
    evaluation_summaries: List[EvaluationSummary]
    artifact_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CandidateScoreBreakdown(BaseModel):
    """Breakdown of ranking score for a formulation"""
    formulation_id: str
    uptake_score: float = Field(0.0, ge=0.0, le=100.0)
    toxicity_penalty: float = Field(0.0, ge=0.0, le=100.0)
    size_preference_score: float = Field(0.0, ge=0.0, le=100.0)
    pdi_penalty: float = Field(0.0, ge=0.0, le=100.0)
    target_match_bonus: float = Field(0.0, ge=0.0, le=100.0)
    payload_match_bonus: float = Field(0.0, ge=0.0, le=100.0)
    predicted_particle_size_nm: Optional[float] = None
    predicted_pdi: Optional[float] = None
    predicted_toxicity: Optional[float] = None
    predicted_uptake: Optional[float] = None
    composite_score: float = Field(..., ge=0.0, le=100.0)

    class Config:
        schema_extra = {
            "example": {
                "formulation_id": "LNP-001",
                "uptake_score": 85.0,
                "toxicity_penalty": 10.0,
                "size_preference_score": 90.0,
                "pdi_penalty": 5.0,
                "target_match_bonus": 15.0,
                "payload_match_bonus": 10.0,
                "predicted_particle_size_nm": 95.5,
                "predicted_pdi": 0.12,
                "predicted_toxicity": 2.3,
                "predicted_uptake": 65.0,
                "composite_score": 78.5,
            }
        }


class RankingRequest(BaseModel):
    """Request to rank candidate formulations"""
    candidates: List[Dict[str, Any]] = Field(..., description="List of formulation candidates")
    target: str = Field(..., description="Intended biological target")
    payload_type: str = Field(..., description="Payload type (mRNA, protein, siRNA, etc.)")
    maximize_uptake: bool = Field(default=True)
    minimize_toxicity: bool = Field(default=True)
    preferred_size_range_nm: tuple = Field(default=(80, 120), description="Preferred particle size range")
    max_pdi: float = Field(default=0.2, ge=0.01, le=0.5)
    weights: Optional[Dict[str, float]] = Field(
        None,
        description="Custom scoring weights (uptake, toxicity, size, pdi, target, payload)"
    )


class RankingResult(BaseModel):
    """Result of ranking formulations"""
    rank: int = Field(..., ge=1, description="Rank (1 = best)")
    score_breakdown: CandidateScoreBreakdown
    recommended: bool = Field(default=False, description="Top recommendation flag")


class RankedFormulations(BaseModel):
    """Full ranking results"""
    target: str
    payload_type: str
    candidates_ranked: int
    top_recommendations: List[RankingResult] = Field(
        description="Top ranked formulations"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
