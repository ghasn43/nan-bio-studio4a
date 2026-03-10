"""
Model Training for LNP Formulation Prediction

Handles regression and classification model training with multiple algorithms,
evaluation, and model selection.
"""

import logging
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.ensemble import GradientBoostingRegressor, GradientBoostingClassifier
from sklearn.model_selection import cross_val_score
from .preprocess import PreprocessingPipeline
from .evaluate import ModelEvaluator
from .schemas import ModelType, TaskType


logger = logging.getLogger(__name__)


class ModelTrainer:
    """
    Trains multiple baseline models for LNP prediction tasks.
    
    Supports:
    - Regression (LinearRegression, RandomForest, GradientBoosting)
    - Classification (LogisticRegression, RandomForest, GradientBoosting)
    - Automatic model selection based on validation performance
    - Cross-validation for robust evaluation
    """

    def __init__(self):
        self.models = {}
        self.evaluator = ModelEvaluator()

    def train_regression_models(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_valid: np.ndarray,
        y_valid: np.ndarray,
        model_types: List[ModelType],
    ) -> Dict[str, Tuple]:
        """
        Train multiple regression models.
        
        Args:
            X_train: Training features
            y_train: Training targets
            X_valid: Validation features
            y_valid: Validation targets
            model_types: List of ModelType enums to train
            
        Returns:
            Dict mapping model_type to (model, train_metrics, valid_metrics)
        """
        
        results = {}
        
        for model_type in model_types:
            try:
                logger.info(f"Training regression model: {model_type}")
                
                if model_type == ModelType.LINEAR_REGRESSION:
                    model = LinearRegression()
                
                elif model_type == ModelType.RANDOM_FOREST_REGRESSION:
                    model = RandomForestRegressor(
                        n_estimators=100,
                        max_depth=10,
                        min_samples_split=5,
                        min_samples_leaf=2,
                        random_state=42,
                        n_jobs=-1
                    )
                
                elif model_type == ModelType.GRADIENT_BOOSTING_REGRESSION:
                    model = GradientBoostingRegressor(
                        n_estimators=100,
                        learning_rate=0.1,
                        max_depth=5,
                        min_samples_split=5,
                        min_samples_leaf=2,
                        random_state=42
                    )
                
                else:
                    logger.warning(f"Unknown regression model type: {model_type}")
                    continue
                
                # Train
                model.fit(X_train, y_train)
                
                # Evaluate
                y_train_pred = model.predict(X_train)
                y_valid_pred = model.predict(X_valid)
                
                train_metrics = self.evaluator.evaluate_regression(y_train, y_train_pred)
                valid_metrics = self.evaluator.evaluate_regression(y_valid, y_valid_pred)
                
                logger.info(
                    f"  Train R²: {train_metrics['r2']:.3f}, "
                    f"Valid R²: {valid_metrics['r2']:.3f}"
                )
                
                results[model_type] = (model, train_metrics, valid_metrics)
            
            except Exception as e:
                logger.error(f"Error training {model_type}: {e}")
        
        return results

    def train_classification_models(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_valid: np.ndarray,
        y_valid: np.ndarray,
        model_types: List[ModelType],
    ) -> Dict[str, Tuple]:
        """
        Train multiple classification models.
        
        Args:
            X_train: Training features
            y_train: Training targets
            X_valid: Validation features
            y_valid: Validation targets
            model_types: List of ModelType enums to train
            
        Returns:
            Dict mapping model_type to (model, train_metrics, valid_metrics)
        """
        
        results = {}
        
        for model_type in model_types:
            try:
                logger.info(f"Training classification model: {model_type}")
                
                if model_type == ModelType.LOGISTIC_REGRESSION:
                    model = LogisticRegression(
                        max_iter=1000,
                        random_state=42,
                        n_jobs=-1
                    )
                
                elif model_type == ModelType.RANDOM_FOREST_CLASSIFICATION:
                    model = RandomForestClassifier(
                        n_estimators=100,
                        max_depth=10,
                        min_samples_split=5,
                        min_samples_leaf=2,
                        random_state=42,
                        n_jobs=-1
                    )
                
                elif model_type == ModelType.GRADIENT_BOOSTING_CLASSIFICATION:
                    model = GradientBoostingClassifier(
                        n_estimators=100,
                        learning_rate=0.1,
                        max_depth=5,
                        min_samples_split=5,
                        min_samples_leaf=2,
                        random_state=42
                    )
                
                else:
                    logger.warning(f"Unknown classification model type: {model_type}")
                    continue
                
                # Train
                model.fit(X_train, y_train)
                
                # Evaluate
                y_train_pred = model.predict(X_train)
                y_valid_pred = model.predict(X_valid)
                
                train_metrics = self.evaluator.evaluate_classification(y_train, y_train_pred)
                valid_metrics = self.evaluator.evaluate_classification(y_valid, y_valid_pred)
                
                logger.info(
                    f"  Train F1: {train_metrics['f1']:.3f}, "
                    f"Valid F1: {valid_metrics['f1']:.3f}"
                )
                
                results[model_type] = (model, train_metrics, valid_metrics)
            
            except Exception as e:
                logger.error(f"Error training {model_type}: {e}")
        
        return results

    def select_best_model(
        self,
        results: Dict[str, Tuple],
        task_type: TaskType,
        metric: Optional[str] = None,
    ) -> Tuple[ModelType, object]:
        """
        Select best model from training results based on validation performance.
        
        Args:
            results: Dict from train_*_models
            task_type: Type of task (regression or classification)
            metric: Metric to optimize ("r2", "f1", "accuracy", etc.)
            
        Returns:
            Tuple of (best_model_type, best_model)
        """
        
        if not results:
            raise ValueError("No trained models to select from")
        
        if metric is None:
            # Default metrics by task type
            if task_type == TaskType.PREDICT_PARTICLE_SIZE:
                metric = "r2"
            else:
                metric = "f1" if "classify" in task_type.value else "r2"
        
        best_model_type = None
        best_score = -np.inf
        
        for model_type, (model, train_metrics, valid_metrics) in results.items():
            if metric in valid_metrics and valid_metrics[metric] is not None:
                score = valid_metrics[metric]
                if score > best_score:
                    best_score = score
                    best_model_type = model_type
        
        if best_model_type is None:
            logger.warning(f"No valid scores for metric '{metric}', selecting first model")
            best_model_type = list(results.keys())[0]
        
        best_model = results[best_model_type][0]
        logger.info(f"Selected best model: {best_model_type} ({metric}={best_score:.3f})")
        
        return best_model_type, best_model
