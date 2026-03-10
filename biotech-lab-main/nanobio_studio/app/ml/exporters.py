"""
Export Utilities for ML Datasets and Results

Export datasets to CSV/Parquet and ranking results.
"""

import logging
from typing import Dict, List
import pandas as pd
import os


logger = logging.getLogger(__name__)


class DatasetExporter:
    """Export ML-ready datasets to various formats"""

    @staticmethod
    def to_csv(
        dataset: Dict,
        output_path: str,
        include_metadata: bool = True,
    ) -> str:
        """
        Export dataset to CSV.
        
        Args:
            dataset: Dataset dict from DatasetBuilder
            output_path: Path to save CSV
            include_metadata: Include traceability columns
            
        Returns:
            Path to saved file
        """
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        
        X = dataset['X'].copy()
        y = dataset['y']
        
        result = X.copy()
        result[dataset['target_name']] = y.values
        
        if include_metadata and 'metadata' in dataset and dataset['metadata'] is not None:
            for col in dataset['metadata'].columns:
                result[col] = dataset['metadata'][col].values
        
        result.to_csv(output_path, index=False)
        logger.info(f"Exported dataset to {output_path}")
        return output_path

    @staticmethod
    def to_parquet(
        dataset: Dict,
        output_path: str,
        include_metadata: bool = True,
    ) -> str:
        """Export dataset to Parquet"""
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        
        X = dataset['X'].copy()
        y = dataset['y']
        
        result = X.copy()
        result[dataset['target_name']] = y.values
        
        if include_metadata and 'metadata' in dataset and dataset['metadata'] is not None:
            for col in dataset['metadata'].columns:
                result[col] = dataset['metadata'][col].values
        
        result.to_parquet(output_path, compression='snappy')
        logger.info(f"Exported dataset to {output_path}")
        return output_path

    @staticmethod
    def export_train_valid_split(
        dataset: Dict,
        output_dir: str,
        format: str = "csv",
    ) -> Dict[str, str]:
        """
        Export train and validation splits separately.
        
        Args:
            dataset: Dataset dict
            output_dir: Directory for outputs
            format: "csv" or "parquet"
            
        Returns:
            Dict with paths to train/valid files
        """
        os.makedirs(output_dir, exist_ok=True)
        
        task_name = dataset['task_name']
        ext = f".{format}"
        
        train_path = os.path.join(output_dir, f"{task_name}_train{ext}")
        valid_path = os.path.join(output_dir, f"{task_name}_valid{ext}")
        
        # Build train dataframe
        X_train = dataset['X_train'].copy()
        y_train = dataset['y_train']
        
        train_df = X_train.copy()
        train_df[dataset['target_name']] = y_train.values
        
        if 'metadata_train' in dataset and dataset['metadata_train'] is not None:
            for col in dataset['metadata_train'].columns:
                train_df[col] = dataset['metadata_train'][col].values
        
        # Build valid dataframe
        X_valid = dataset['X_valid'].copy()
        y_valid = dataset['y_valid']
        
        valid_df = X_valid.copy()
        valid_df[dataset['target_name']] = y_valid.values
        
        if 'metadata_valid' in dataset and dataset['metadata_valid'] is not None:
            for col in dataset['metadata_valid'].columns:
                valid_df[col] = dataset['metadata_valid'][col].values
        
        # Save
        if format == "csv":
            train_df.to_csv(train_path, index=False)
            valid_df.to_csv(valid_path, index=False)
        else:
            train_df.to_parquet(train_path, compression='snappy')
            valid_df.to_parquet(valid_path, compression='snappy')
        
        logger.info(f"Exported splits to {output_dir}")
        return {'train': train_path, 'valid': valid_path}


class RankingResultExporter:
    """Export ranking results"""

    @staticmethod
    def to_csv(
        ranking_results: List,
        output_path: str,
    ) -> str:
        """
        Export ranking results to CSV.
        
        Args:
            ranking_results: List of RankingResult objects
            output_path: Path to save
            
        Returns:
            Path to saved file
        """
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        
        rows = []
        for result in ranking_results:
            breakdown = result.score_breakdown
            rows.append({
                'rank': result.rank,
                'formulation_id': breakdown.formulation_id,
                'composite_score': breakdown.composite_score,
                'uptake_score': breakdown.uptake_score,
                'toxicity_penalty': breakdown.toxicity_penalty,
                'size_preference_score': breakdown.size_preference_score,
                'pdi_penalty': breakdown.pdi_penalty,
                'target_match_bonus': breakdown.target_match_bonus,
                'payload_match_bonus': breakdown.payload_match_bonus,
                'predicted_uptake': breakdown.predicted_uptake,
                'predicted_toxicity': breakdown.predicted_toxicity,
                'predicted_particle_size_nm': breakdown.predicted_particle_size_nm,
                'predicted_pdi': breakdown.predicted_pdi,
                'recommended': result.recommended,
            })
        
        df = pd.DataFrame(rows)
        df.to_csv(output_path, index=False)
        logger.info(f"Exported {len(rows)} ranking results to {output_path}")
        return output_path

    @staticmethod
    def to_json(
        ranking_results: List,
        output_path: str,
    ) -> str:
        """Export ranking results to JSON"""
        import json
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        
        data = [result.dict() for result in ranking_results]
        
        # Make datetime JSON serializable
        for item in data:
            for key, value in item.items():
                if hasattr(value, 'isoformat'):
                    item[key] = value.isoformat()
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Exported ranking results to {output_path}")
        return output_path
