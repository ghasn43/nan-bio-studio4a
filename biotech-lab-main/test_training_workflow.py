#!/usr/bin/env python
"""Simulate the ML training workflow."""
import sys
import traceback
import pandas as pd

try:
    print("Step 1: Creating sample dataset...")
    # Simulate loading CSV
    df = pd.DataFrame({
        'particle_size': [100, 110, 105, 115],
        'pdi': [0.2, 0.25, 0.22, 0.28],
        'toxicity': [0.1, 0.15, 0.12, 0.18],
    })
    print("[OK] Created dataframe with {} rows".format(len(df)))
    
    print("\nStep 2: Creating MLTaskConfig...")
    from nanobio_studio.app.ml.schemas import MLTaskConfig, TaskType, ModelType, DatasetBuildRequest, TrainRequest
    
    config = MLTaskConfig(
        task_name="test_task",
        task_type=TaskType.PREDICT_TOXICITY,
        target_variable="toxicity",
        model_types=[ModelType.LINEAR_REGRESSION],
    )
    print("[OK] MLTaskConfig created")
    
    print("\nStep 3: Creating DatasetBuildRequest...")
    request_build = DatasetBuildRequest(task_config=config)
    print("[OK] DatasetBuildRequest created")
    
    print("\nStep 4: Creating TrainRequest...")
    request_train = TrainRequest(
        dataset_build_request=request_build,
        save_artifacts=True,
        artifact_name="test",
    )
    print("[OK] TrainRequest created")
    
    print("\nStep 5: Creating MLService and training...")
    from nanobio_studio.app.services.ml_service import MLService
    service = MLService()
    print("[OK] MLService created")
    
    # This should trigger the error if it exists
    response = service.train_models(df, request_train)
    print("[OK] Training completed successfully")
    
except Exception as e:
    print("\n[ERROR] {}".format(e))
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
