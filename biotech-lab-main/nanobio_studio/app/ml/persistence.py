"""
Model Persistence and Artifact Management

Save and load trained models with metadata and preprocessing pipelines.
"""

import logging
from typing import Dict, Optional, List
import os
import json
from datetime import datetime
import joblib
from .schemas import TaskType, ModelType


logger = logging.getLogger(__name__)


class ModelPersistence:
    """
    Manages persistence of trained model bundles including:
    - Trained sklearn model
    - Preprocessing pipeline
    - Feature lists
    - Task configuration
    - Evaluation metrics
    - Training metadata
    """

    def __init__(self, models_dir: str = "models_store"):
        """
        Initialize persistence manager.
        
        Args:
            models_dir: Directory for model storage
        """
        self.models_dir = models_dir
        os.makedirs(models_dir, exist_ok=True)

    def save_model_bundle(
        self,
        model,
        preprocessing_pipeline,
        task_config: Dict,
        evaluation_summary: Dict,
        feature_builder=None,
        metadata: Optional[Dict] = None,
    ) -> str:
        """
        Save complete model bundle with metadata.
        
        Args:
            model: Trained sklearn model
            preprocessing_pipeline: Fitted PreprocessingPipeline
            task_config: Task configuration dict
            evaluation_summary: Evaluation results dict
            feature_builder: Optional FeatureBuilder instance
            metadata: Optional metadata dict
            
        Returns:
            Path to saved bundle
        """
        
        task_name = task_config.get('task_name', 'unknown_task')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        bundle_name = f"{task_name}_{timestamp}"
        bundle_path = os.path.join(self.models_dir, f"{bundle_name}.pkl")
        
        bundle = {
            'model': model,
            'preprocessing_pipeline': preprocessing_pipeline,
            'task_config': task_config,
            'evaluation_summary': evaluation_summary,
            'feature_builder': feature_builder,
            'metadata': metadata or {},
            'created_at': datetime.utcnow().isoformat(),
        }
        
        joblib.dump(bundle, bundle_path)
        logger.info(f"Saved model bundle to {bundle_path}")
        
        # Save metadata JSON for quick lookup
        metadata_path = bundle_path.replace('.pkl', '_metadata.json')
        self._save_metadata(bundle_path, task_config, evaluation_summary, metadata_path)
        
        return bundle_path

    def load_model_bundle(self, bundle_path: str) -> Dict:
        """
        Load model bundle from disk.
        
        Args:
            bundle_path: Path to model bundle
            
        Returns:
            Bundle dict with all components
        """
        
        bundle = joblib.load(bundle_path)
        logger.info(f"Loaded model bundle from {bundle_path}")
        return bundle

    def list_available_models(self) -> List[Dict]:
        """
        List all available model bundles.
        
        Returns:
            List of metadata dicts for each model
        """
        
        models = []
        
        for filename in os.listdir(self.models_dir):
            if filename.endswith('_metadata.json'):
                metadata_path = os.path.join(self.models_dir, filename)
                
                try:
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                        models.append(metadata)
                except Exception as e:
                    logger.warning(f"Error loading metadata from {metadata_path}: {e}")
        
        return models

    def get_best_model_for_task(self, task_name: str) -> Optional[Dict]:
        """
        Get the best (most recent) model bundle for a task.
        
        Args:
            task_name: Name of the task
            
        Returns:
            Model metadata or None if not found
        """
        
        models = self.list_available_models()
        task_models = [m for m in models if m.get('task_name') == task_name]
        
        if not task_models:
            return None
        
        # Sort by creation time, newest first
        task_models.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return task_models[0]

    def _save_metadata(
        self,
        bundle_path: str,
        task_config: Dict,
        evaluation_summary: Dict,
        metadata_path: str,
    ) -> None:
        """Save metadata JSON for quick lookup without loading full bundle"""
        
        metadata = {
            'bundle_path': bundle_path,
            'task_name': task_config.get('task_name'),
            'task_type': task_config.get('task_type'),
            'target_variable': task_config.get('target_variable'),
            'model_types': task_config.get('model_types'),
            'evaluation_summary': evaluation_summary,
            'created_at': datetime.utcnow().isoformat(),
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        logger.info(f"Saved metadata to {metadata_path}")

    @staticmethod
    def create_default_models_dir() -> str:
        """Create default models directory"""
        models_dir = "models_store"
        os.makedirs(models_dir, exist_ok=True)
        logger.info(f"Models directory: {models_dir}")
        return models_dir
