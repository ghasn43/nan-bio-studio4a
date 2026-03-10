"""
Preprocessing Pipeline for ML Models

Handles categorical encoding, scaling, and consistent transformation
of features across training and inference.
"""

import logging
from typing import List, Dict, Optional, Tuple
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib


logger = logging.getLogger(__name__)


class PreprocessingPipeline:
    """
    Encapsulates feature preprocessing with consistent encoding and scaling.
    
    Features:
    - Separates numeric and categorical columns
    - One-hot encodes categorical variables
    - Optional scaling (StandardScaler or MinMaxScaler)
    - Consistent encoding for both training and inference
    - Persistence to disk
    """

    def __init__(
        self,
        numeric_features: Optional[List[str]] = None,
        categorical_features: Optional[List[str]] = None,
        scale_numeric: bool = True,
        scaler_type: str = "standard",  # "standard" or "minmax"
    ):
        """
        Initialize preprocessing pipeline.
        
        Args:
            numeric_features: List of numeric column names
            categorical_features: List of categorical column names
            scale_numeric: Whether to scale numeric features
            scaler_type: Type of scaler ("standard" or "minmax")
        """
        self.numeric_features = numeric_features or []
        self.categorical_features = categorical_features or []
        self.scale_numeric = scale_numeric
        self.scaler_type = scaler_type
        self.transformer = None
        self.is_fitted = False

    def fit(self, X: pd.DataFrame) -> "PreprocessingPipeline":
        """
        Fit the preprocessing pipeline on training data.
        
        Args:
            X: Training feature dataframe
            
        Returns:
            Self for chaining
        """
        
        # Auto-detect numeric and categorical if not provided
        if not self.numeric_features:
            self.numeric_features = list(X.select_dtypes(include=['number']).columns)
        
        if not self.categorical_features:
            self.categorical_features = list(X.select_dtypes(include=['object', 'category']).columns)
        
        logger.info(
            f"Fitting preprocessing: {len(self.numeric_features)} numeric, "
            f"{len(self.categorical_features)} categorical"
        )
        
        # Build transformer with separate pipelines for numeric and categorical
        transformers = []
        
        if self.numeric_features:
            if self.scale_numeric:
                if self.scaler_type == "minmax":
                    numeric_transformer = Pipeline(steps=[
                        ('scaler', MinMaxScaler())
                    ])
                else:
                    numeric_transformer = Pipeline(steps=[
                        ('scaler', StandardScaler())
                    ])
            else:
                numeric_transformer = 'passthrough'
            
            transformers.append(
                ('num', numeric_transformer, self.numeric_features)
            )
        
        if self.categorical_features:
            categorical_transformer = Pipeline(steps=[
                ('onehot', OneHotEncoder(
                    sparse_output=False,
                    handle_unknown='ignore',
                    drop='first'  # Avoid multicollinearity
                ))
            ])
            transformers.append(
                ('cat', categorical_transformer, self.categorical_features)
            )
        
        self.transformer = ColumnTransformer(
            transformers=transformers,
            remainder='drop'
        )
        
        self.transformer.fit(X)
        self.is_fitted = True
        
        logger.info("Preprocessing pipeline fitted successfully")
        return self

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        """
        Apply preprocessing transformation.
        
        Args:
            X: Feature dataframe
            
        Returns:
            numpy array of transformed features
        """
        if not self.is_fitted:
            raise ValueError("Preprocessing pipeline not fitted. Call fit() first.")
        
        return self.transformer.transform(X)

    def fit_transform(self, X: pd.DataFrame) -> np.ndarray:
        """Fit and transform in one step"""
        self.fit(X)
        return self.transform(X)

    def get_feature_names_out(self) -> List[str]:
        """Get transformed feature names after encoding"""
        if not self.is_fitted:
            raise ValueError("Preprocessing pipeline not fitted")
        
        return list(self.transformer.get_feature_names_out())

    def get_numeric_features(self) -> List[str]:
        """Get numeric features"""
        return self.numeric_features

    def get_categorical_features(self) -> List[str]:
        """Get categorical features"""
        return self.categorical_features

    def save(self, path: str) -> None:
        """Save preprocessing pipeline to disk"""
        if not self.is_fitted:
            raise ValueError("Cannot save unfitted pipeline")
        
        joblib.dump(self, path)
        logger.info(f"Preprocessing pipeline saved to {path}")

    @staticmethod
    def load(path: str) -> "PreprocessingPipeline":
        """Load preprocessing pipeline from disk"""
        pipeline = joblib.load(path)
        logger.info(f"Preprocessing pipeline loaded from {path}")
        return pipeline

    def to_dict(self) -> Dict:
        """Serialize pipeline configuration"""
        return {
            'numeric_features': self.numeric_features,
            'categorical_features': self.categorical_features,
            'scale_numeric': self.scale_numeric,
            'scaler_type': self.scaler_type,
            'is_fitted': self.is_fitted,
        }


class SimpleImputer:
    """Simple missing value imputation"""

    @staticmethod
    def impute_numeric(X: pd.DataFrame, strategy: str = "median") -> pd.DataFrame:
        """Impute numeric columns"""
        X_imputed = X.copy()
        numeric_cols = X_imputed.select_dtypes(include=['number']).columns
        
        for col in numeric_cols:
            if strategy == "median":
                X_imputed[col].fillna(X_imputed[col].median(), inplace=True)
            elif strategy == "mean":
                X_imputed[col].fillna(X_imputed[col].mean(), inplace=True)
            elif strategy == "forward_fill":
                X_imputed[col].fillna(method='ffill', inplace=True)
        
        return X_imputed

    @staticmethod
    def impute_categorical(X: pd.DataFrame, strategy: str = "mode") -> pd.DataFrame:
        """Impute categorical columns"""
        X_imputed = X.copy()
        categorical_cols = X_imputed.select_dtypes(include=['object', 'category']).columns
        
        for col in categorical_cols:
            if strategy == "mode":
                mode_val = X_imputed[col].mode()[0] if len(X_imputed[col].mode()) > 0 else "unknown"
                X_imputed[col].fillna(mode_val, inplace=True)
            elif strategy == "unknown":
                X_imputed[col].fillna("unknown", inplace=True)
        
        return X_imputed
