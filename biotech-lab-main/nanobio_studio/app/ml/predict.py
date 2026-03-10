"""
Model Prediction for LNP Candidates

Handles inference using trained models on new formulations.
"""

import logging
from typing import Dict, List, Optional, Union
import pandas as pd
import numpy as np
from .preprocess import PreprocessingPipeline
from .feature_builder import FeatureBuilder
import joblib


logger = logging.getLogger(__name__)


class ModelPredictor:
    """
    Makes predictions using trained models.
    
    Features:
    - Load trained model bundles
    - Apply preprocessing consistently
    - Batch prediction on formulations
    - Uncertainty quantification (when available)
    """

    def __init__(
        self,
        model,
        preprocessing_pipeline: PreprocessingPipeline,
        feature_builder: Optional[FeatureBuilder] = None,
    ):
        """
        Initialize predictor with model and preprocessing.
        
        Args:
            model: Trained sklearn model
            preprocessing_pipeline: fitted PreprocessingPipeline
            feature_builder: FeatureBuilder for feature extraction
        """
        self.model = model
        self.preprocessing_pipeline = preprocessing_pipeline
        self.feature_builder = feature_builder or FeatureBuilder()

    def predict(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        include_uncertainty: bool = False,
    ) -> Union[np.ndarray, tuple]:
        """
        Make predictions on new formulations.
        
        Args:
            X: Feature dataframe or array
            include_uncertainty: Try to get prediction intervals
            
        Returns:
            Predictions array, optionally with uncertainties
        """
        
        if isinstance(X, pd.DataFrame):
            X_transformed = self.preprocessing_pipeline.transform(X)
        else:
            X_transformed = X
        
        predictions = self.model.predict(X_transformed)
        
        if include_uncertainty:
            # Get uncertainty from model if available (RandomForest, GradientBoosting)
            uncertainties = self._get_uncertainties(X_transformed)
            return predictions, uncertainties
        
        return predictions

    def predict_proba(
        self,
        X: Union[pd.DataFrame, np.ndarray],
    ) -> np.ndarray:
        """
        Get probability predictions for classification models.
        
        Args:
            X: Feature dataframe or array
            
        Returns:
            Probability predictions
        """
        
        if not hasattr(self.model, 'predict_proba'):
            raise ValueError("Model does not support predict_proba")
        
        if isinstance(X, pd.DataFrame):
            X_transformed = self.preprocessing_pipeline.transform(X)
        else:
            X_transformed = X
        
        return self.model.predict_proba(X_transformed)

    def _get_uncertainties(self, X: np.ndarray) -> np.ndarray:
        """
        Try to extract prediction uncertainties from ensemble models.
        
        Args:
            X: Transformed features
            
        Returns:
            Uncertainty estimates
        """
        
        try:
            # For RandomForest, use std of tree predictions
            if hasattr(self.model, 'estimators_'):
                predictions = np.array([
                    tree.predict(X) for tree in self.model.estimators_
                ])
                uncertainties = np.std(predictions, axis=0)
                return uncertainties
        except Exception as e:
            logger.debug(f"Could not extract uncertainties: {e}")
        
        return np.zeros_like(self.model.predict(X))

    def predict_from_records(
        self,
        records: pd.DataFrame,
        target_variable: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Predict from raw formulation records (auto-extract features).
        
        Args:
            records: Raw formulation dataframe
            target_variable: If provided, exclude from features
            
        Returns:
            Original records with predictions added
        """
        
        # Extract features
        X = self.feature_builder.build_features(records, target_variable=target_variable)
        
        # Ensure same columns as training
        expected_cols = self.preprocessing_pipeline.get_numeric_features() + \
                       self.preprocessing_pipeline.get_categorical_features()
        
        # Align columns
        for col in expected_cols:
            if col not in X.columns:
                X[col] = 0  # Default for missing categories
        
        X = X[expected_cols]
        
        # Predict
        predictions = self.predict(X)
        
        # Add to records
        records_with_pred = records.copy()
        records_with_pred['prediction'] = predictions
        
        return records_with_pred

    @staticmethod
    def load_from_bundle(bundle_path: str) -> "ModelPredictor":
        """Load predictor from saved model bundle"""
        bundle = joblib.load(bundle_path)
        
        model = bundle['model']
        preprocessing_pipeline = bundle['preprocessing_pipeline']
        feature_builder = bundle.get('feature_builder')
        
        logger.info(f"Loaded model bundle from {bundle_path}")
        
        return ModelPredictor(
            model=model,
            preprocessing_pipeline=preprocessing_pipeline,
            feature_builder=feature_builder,
        )
