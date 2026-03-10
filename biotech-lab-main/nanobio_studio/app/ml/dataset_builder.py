"""
Dataset Builder for ML Training

Constructs ML-ready training datasets from LNP experiment and biological assay records,
with support for different tasks, filtering, and traceability.
"""

import logging
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from .feature_builder import FeatureBuilder, FeatureConfig


logger = logging.getLogger(__name__)


class DatasetBuilder:
    """
    Builds training datasets for various ML tasks on LNP formulations and assays.
    
    Supports:
    - Regression tasks (predict particle size, PDI, toxicity, uptake)
    - Classification tasks (classify toxicity band, uptake band, QC status)
    - Filtering by assay type, payload type, target
    - Traceability (preserves formulation_id, experiment_id)
    """

    def __init__(self):
        self.feature_builder = FeatureBuilder()

    def build_dataset(
        self,
        records: pd.DataFrame,
        task_name: str,
        target_variable: str,
        test_split: float = 0.2,
        random_state: int = 42,
        include_metadata: bool = True,
        handle_missing: str = "drop",
        filter_assay_type: Optional[str] = None,
        filter_payload_type: Optional[str] = None,
        filter_target: Optional[str] = None,
        exclude_features: Optional[List[str]] = None,
    ) -> Dict:
        """
        Build a complete training dataset for a task.
        
        Args:
            records: Flattened dataframe of formulation/assay records
            task_name: Name of the ML task
            target_variable: Column name to predict
            test_split: Fraction for validation set
            random_state: Random seed
            include_metadata: Include traceability columns
            handle_missing: How to handle missing values
            filter_assay_type: Filter to specific assay type
            filter_payload_type: Filter to specific payload type
            filter_target: Filter to specific intended target
            exclude_features: Additional features to exclude
            
        Returns:
            Dict with keys: X, y, X_train, X_valid, y_train, y_valid,
                           metadata, feature_names, target_name, task_name
        """
        
        # Copy to avoid mutation
        df = records.copy()
        
        # Apply filters
        if filter_assay_type and 'assay_type' in df.columns:
            df = df[df['assay_type'].str.lower() == filter_assay_type.lower()]
            logger.info(f"Filtered to assay_type='{filter_assay_type}', {len(df)} records remaining")
        
        if filter_payload_type and 'payload_type' in df.columns:
            df = df[df['payload_type'].str.lower() == filter_payload_type.lower()]
            logger.info(f"Filtered to payload_type='{filter_payload_type}', {len(df)} records remaining")
        
        if filter_target and 'intended_target' in df.columns:
            df = df[df['intended_target'].str.lower() == filter_target.lower()]
            logger.info(f"Filtered to intended_target='{filter_target}', {len(df)} records remaining")
        
        # Check target variable exists
        if target_variable not in df.columns:
            raise ValueError(f"Target variable '{target_variable}' not in dataframe")
        
        # Extract target
        y = pd.to_numeric(df[target_variable], errors='coerce')
        
        # Handle missing targets
        if handle_missing == "drop":
            valid_idx = y.notna()
            df = df[valid_idx]
            y = y[valid_idx]
        
        if len(y) == 0:
            raise ValueError(f"No valid samples for task '{task_name}'")
        
        logger.info(f"Building dataset for task '{task_name}' with {len(df)} samples")
        
        # Extract features
        X = self.feature_builder.build_features(df, target_variable=target_variable)
        
        # Remove excluded features
        if exclude_features:
            X = X.drop(columns=[col for col in exclude_features if col in X.columns])
        
        # Handle missing values in features
        if handle_missing == "drop":
            valid_idx = X.notna().all(axis=1)
            X = X[valid_idx]
            y = y[valid_idx]
        elif handle_missing == "mean":
            numeric_cols = X.select_dtypes(include=['number']).columns
            X[numeric_cols] = X[numeric_cols].fillna(X[numeric_cols].mean())
        elif handle_missing == "median":
            numeric_cols = X.select_dtypes(include=['number']).columns
            X[numeric_cols] = X[numeric_cols].fillna(X[numeric_cols].median())
        
        # Check minimum samples
        if len(X) < 10:
            logger.warning(f"Very few samples ({len(X)}) for task '{task_name}'")
        
        # Preserve metadata for traceability
        metadata = pd.DataFrame()
        if include_metadata:
            for col in ['formulation_id', 'experiment_id', 'assay_id']:
                if col in df.columns:
                    metadata[col] = df[col].values
        
        # Train/validation split
        n_samples = len(X)
        n_train = int(n_samples * (1 - test_split))
        
        indices = np.arange(n_samples)
        np.random.seed(random_state)
        np.random.shuffle(indices)
        
        train_idx = indices[:n_train]
        valid_idx = indices[n_train:]
        
        X_train = X.iloc[train_idx].reset_index(drop=True)
        X_valid = X.iloc[valid_idx].reset_index(drop=True)
        y_train = y.iloc[train_idx].reset_index(drop=True)
        y_valid = y.iloc[valid_idx].reset_index(drop=True)
        
        metadata_train = metadata.iloc[train_idx].reset_index(drop=True) if len(metadata) > 0 else None
        metadata_valid = metadata.iloc[valid_idx].reset_index(drop=True) if len(metadata) > 0 else None
        
        logger.info(
            f"Dataset split: {len(X_train)} train, {len(X_valid)} validation. "
            f"Features: {X.shape[1]}"
        )
        
        return {
            'X': X.reset_index(drop=True),
            'y': y.reset_index(drop=True),
            'X_train': X_train,
            'X_valid': X_valid,
            'y_train': y_train,
            'y_valid': y_valid,
            'metadata': metadata,
            'metadata_train': metadata_train,
            'metadata_valid': metadata_valid,
            'feature_names': list(X.columns),
            'target_name': target_variable,
            'task_name': task_name,
            'n_samples': len(X),
            'n_features': X.shape[1],
            'test_split': test_split,
            'numeric_features': self.feature_builder.get_numeric_features(),
            'categorical_features': self.feature_builder.get_categorical_features(),
        }

    def export_to_csv(
        self,
        dataset: Dict,
        output_path: str,
        include_metadata: bool = True,
    ) -> None:
        """Export dataset to CSV files for external validation"""
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Full dataset
        X = dataset['X']
        y = dataset['y']
        
        combined = X.copy()
        combined[dataset['target_name']] = y
        
        if include_metadata and dataset['metadata'] is not None:
            combined = pd.concat([combined, dataset['metadata']], axis=1)
        
        combined.to_csv(output_path, index=False)
        logger.info(f"Exported full dataset to {output_path}")
        
        # Train/valid splits
        train_path = output_path.replace('.csv', '_train.csv')
        valid_path = output_path.replace('.csv', '_valid.csv')
        
        X_train = dataset['X_train'].copy()
        y_train = dataset['y_train']
        X_train[dataset['target_name']] = y_train
        if include_metadata and dataset['metadata_train'] is not None:
            X_train = pd.concat([X_train, dataset['metadata_train']], axis=1)
        X_train.to_csv(train_path, index=False)
        
        X_valid = dataset['X_valid'].copy()
        y_valid = dataset['y_valid']
        X_valid[dataset['target_name']] = y_valid
        if include_metadata and dataset['metadata_valid'] is not None:
            X_valid = pd.concat([X_valid, dataset['metadata_valid']], axis=1)
        X_valid.to_csv(valid_path, index=False)
        
        logger.info(f"Exported splits to {train_path} and {valid_path}")

    def export_to_parquet(
        self,
        dataset: Dict,
        output_path: str,
        include_metadata: bool = True,
    ) -> None:
        """Export dataset to Parquet for efficient storage"""
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        X = dataset['X']
        y = dataset['y']
        
        combined = X.copy()
        combined[dataset['target_name']] = y
        
        if include_metadata and dataset['metadata'] is not None:
            combined = pd.concat([combined, dataset['metadata']], axis=1)
        
        combined.to_parquet(output_path, compression='snappy')
        logger.info(f"Exported full dataset to {output_path}")
        
        # Train/valid splits
        train_path = output_path.replace('.parquet', '_train.parquet')
        valid_path = output_path.replace('.parquet', '_valid.parquet')
        
        X_train = dataset['X_train'].copy()
        y_train = dataset['y_train']
        X_train[dataset['target_name']] = y_train
        if include_metadata and dataset['metadata_train'] is not None:
            X_train = pd.concat([X_train, dataset['metadata_train']], axis=1)
        X_train.to_parquet(train_path, compression='snappy')
        
        X_valid = dataset['X_valid'].copy()
        y_valid = dataset['y_valid']
        X_valid[dataset['target_name']] = y_valid
        if include_metadata and dataset['metadata_valid'] is not None:
            X_valid = pd.concat([X_valid, dataset['metadata_valid']], axis=1)
        X_valid.to_parquet(valid_path, compression='snappy')
        
        logger.info(f"Exported splits to {train_path} and {valid_path}")
