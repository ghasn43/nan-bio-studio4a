#!/usr/bin/env python
"""Direct test of training save functionality"""

import os
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

# Setup path
sys.path.insert(0, str(Path(__file__).parent))
os.chdir(Path(__file__).parent)

print(f"Test started at: {datetime.now()}")
print(f"Working directory: {os.getcwd()}\n")

try:
    # Create sample dataset
    print("Creating sample dataset...")
    data = {
        'formulation_code': ['F001', 'F002', 'F003', 'F004', 'F005'] * 40,
        'temperature': [25, 30, 25, 30, 25] * 40,
        'pressure': [100, 150, 100, 150, 100] * 40,
        'ph': [3, 7, 5, 7, 4] * 40,
        'toxicity_score': [0.2, 0.5, 0.3, 0.6, 0.4] * 40,
    }
    df = pd.DataFrame(data)
    print(f"Sample dataset created: {len(df)} rows\n")
    
    # Import ML service
    print("Importing ML service...")
    from nanobio_studio.app.services.ml_service import MLService
    from nanobio_studio.app.ml.schemas import TrainRequest, DatasetBuildRequest, TaskType, MLTaskConfig
    
    print("✅ Imports successful\n")
    
    # Create training request
    print("Creating training request...")
    task_config = MLTaskConfig(
        task_name="test_toxicity_prediction",
        task_type=TaskType.PREDICT_TOXICITY,
        target_variable="toxicity_score",
        features=["temperature", "pressure", "ph"],
        model_types=["linear_regression"],
    )
    
    request = TrainRequest(
        dataset_build_request=DatasetBuildRequest(task_config=task_config),
        save_artifacts=False,
        artifact_name="test_model",
    )
    print("✅ Request created\n")
    
    # Run training
    print("="*60)
    print("STARTING TRAINING TEST")
    print("="*60)
    print()
    
    ml_service = MLService()
    response = ml_service.train_models(df, request)
    
    print()
    print("="*60)
    print("TRAINING COMPLETE")
    print("="*60)
    print(f"✅ Training succeeded")
    print(f"   Best model: {response.best_model_type}")
    print(f"   Samples: {response.n_samples}")
    print()
    
    # Check database
    print("="*70)
    print("CHECKING DATABASE AFTER TRAINING")
    print("="*70)
    
    from nanobio_studio.app.db.database import get_db
    from sqlalchemy import text
    
    # Check file first
    db_file = "ml_module.db"
    if os.path.exists(db_file):
        mod_time = os.path.getmtime(db_file)
        mod_datetime = datetime.fromtimestamp(mod_time)
        time_diff = (datetime.now() - mod_datetime).total_seconds()
        print(f"Database file modified {time_diff:.1f} seconds ago")
    
    # Query database
    db = get_db()
    session = db.get_session()
    
    result = session.execute(text("SELECT COUNT(*) FROM trained_models"))
    total_count = result.scalar()
    print(f"Total records in database: {total_count}")
    
    # Check for records created today
    result = session.execute(text("""
        SELECT id, task_name, created_at FROM trained_models 
        ORDER BY created_at DESC LIMIT 1
    """))
    latest = result.first()
    if latest:
        print(f"\nLatest record:")
        print(f"  ID: {latest[0]}")
        print(f"  Task: {latest[1]}")
        print(f"  Created: {latest[2]}")
    
    session.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
