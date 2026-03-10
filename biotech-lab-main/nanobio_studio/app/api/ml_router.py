"""
ML API Routes

REST API endpoints for ML operations: dataset building, training, prediction, and ranking.
"""

from typing import List, Optional
import logging
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from ..services.ml_service import MLService, RankingService
from ..ml.schemas import (
    DatasetBuildRequest,
    TrainRequest,
    TrainResponse,
    RankingRequest,
)
from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ml", tags=["ml"])
ml_service = MLService()
ranking_service = RankingService()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(status="ok", version="1.0.0")


@router.post("/dataset/build")
async def build_dataset(
    file: UploadFile = File(...),
    config: DatasetBuildRequest = Depends(DatasetBuildRequest),
):
    """
    Build a training dataset from uploaded data.
    
    Args:
        file: CSV file with formulation/assay data
        config: DatasetBuildRequest with task configuration
        
    Returns:
        Dataset metadata and summary
    """
    
    try:
        # Load data
        df = pd.read_csv(file.file)
        
        # Build dataset
        dataset = ml_service.build_dataset(df, config)
        
        return {
            "status": "success",
            "n_samples": dataset['n_samples'],
            "n_features": dataset['n_features'],
            "numeric_features": dataset['numeric_features'],
            "categorical_features": dataset['categorical_features'],
            "train_size": len(dataset['X_train']),
            "valid_size": len(dataset['X_valid']),
        }
    except Exception as e:
        logger.error(f"Error building dataset: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/train", response_model=TrainResponse)
async def train_models(
    file: UploadFile = File(...),
    request: TrainRequest = Depends(TrainRequest),
):
    """
    Train ML models on provided data.
    
    Args:
        file: CSV file with formulation/assay data
        request: TrainRequest with configuration
        
    Returns:
        TrainResponse with best model and metrics
    """
    
    try:
        # Load data
        df = pd.read_csv(file.file)
        
        # Train models
        response = ml_service.train_models(df, request)
        
        return response
    except Exception as e:
        logger.error(f"Error training models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rank")
async def rank_candidates(request: RankingRequest):
    """
    Rank candidate formulations.
    
    Args:
        request: RankingRequest with candidates and criteria
        
    Returns:
        Ranked candidates with scores
    """
    
    try:
        results = ranking_service.rank_candidates(request.candidates, request)
        return {
            "status": "success",
            "n_candidates": len(request.candidates),
            "results": results,
        }
    except Exception as e:
        logger.error(f"Error ranking candidates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def get_available_models():
    """Get list of available trained models"""
    
    try:
        models = ranking_service.get_available_tasks()
        return {
            "status": "success",
            "models": models,
        }
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        raise HTTPException(status_code=500, detail=str(e))
