"""
Model Evaluation Metrics

Computes regression and classification metrics for model validation.
"""

import logging
from typing import Dict, Optional
import numpy as np
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
)


logger = logging.getLogger(__name__)


class ModelEvaluator:
    """
    Computes evaluation metrics for regression and classification models.
    
    Regression metrics:
    - MAE: Mean Absolute Error
    - RMSE: Root Mean Squared Error
    - R²: Coefficient of Determination
    
    Classification metrics:
    - Accuracy
    - Precision
    - Recall
    - F1 Score
    - ROC-AUC (for binary classification)
    """

    @staticmethod
    def evaluate_regression(
        y_true: np.ndarray,
        y_pred: np.ndarray,
    ) -> Dict[str, Optional[float]]:
        """
        Evaluate regression predictions.
        
        Args:
            y_true: Ground truth values
            y_pred: Predicted values
            
        Returns:
            Dict with MAE, RMSE, R² scores
        """
        
        try:
            mae = mean_absolute_error(y_true, y_pred)
            rmse = np.sqrt(mean_squared_error(y_true, y_pred))
            r2 = r2_score(y_true, y_pred)
            
            return {
                'mae': float(mae),
                'rmse': float(rmse),
                'r2': float(r2),
            }
        
        except Exception as e:
            logger.error(f"Error computing regression metrics: {e}")
            return {'mae': None, 'rmse': None, 'r2': None}

    @staticmethod
    def evaluate_classification(
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_pred_proba: Optional[np.ndarray] = None,
    ) -> Dict[str, Optional[float]]:
        """
        Evaluate classification predictions.
        
        Args:
            y_true: Ground truth labels
            y_pred: Predicted labels
            y_pred_proba: Prediction probabilities (for ROC-AUC)
            
        Returns:
            Dict with accuracy, precision, recall, F1, ROC-AUC
        """
        
        try:
            accuracy = accuracy_score(y_true, y_pred)
            
            # Handle binary vs multiclass
            try:
                precision = precision_score(y_true, y_pred, average='weighted')
                recall = recall_score(y_true, y_pred, average='weighted')
                f1 = f1_score(y_true, y_pred, average='weighted')
            except ValueError:
                precision = precision_score(y_true, y_pred, average='binary', zero_division=0)
                recall = recall_score(y_true, y_pred, average='binary', zero_division=0)
                f1 = f1_score(y_true, y_pred, average='binary', zero_division=0)
            
            # ROC-AUC for binary classification only
            roc_auc = None
            if len(np.unique(y_true)) == 2 and y_pred_proba is not None:
                try:
                    roc_auc = roc_auc_score(y_true, y_pred_proba[:, 1])
                except Exception:
                    pass
            
            return {
                'accuracy': float(accuracy),
                'precision': float(precision),
                'recall': float(recall),
                'f1': float(f1),
                'roc_auc': float(roc_auc) if roc_auc is not None else None,
            }
        
        except Exception as e:
            logger.error(f"Error computing classification metrics: {e}")
            return {
                'accuracy': None,
                'precision': None,
                'recall': None,
                'f1': None,
                'roc_auc': None,
            }
