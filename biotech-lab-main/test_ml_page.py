"""
Test ML Training page loading
"""

import os
import sys
os.chdir('d:\\nano_bio_studio_last\\biotech-lab-main')
sys.path.insert(0, os.getcwd())

print("="*80)
print("ML TRAINING PAGE TEST")
print("="*80)

# Test imports
print("\nTesting imports...")
try:
    from nanobio_studio.app.db.database import get_db, ModelRepository
    print("✅ Database imports OK")
except Exception as e:
    print(f"❌ Database imports failed: {e}")

try:
    from nanobio_studio.app.auth import Permission
    from nanobio_studio.app.ui.streamlit_auth import (
        require_login,
        require_permission,
        show_user_info,
        StreamlitAuth,
    )
    print("✅ Auth imports OK")
except Exception as e:
    print(f"❌ Auth imports failed: {e}")

try:
    from nanobio_studio.app.services.ml_service import MLService
    print("✅ MLService import OK")
except Exception as e:
    print(f"❌ MLService import failed: {e}")

try:
    from nanobio_studio.app.ml.schemas import (
        MLTaskConfig,
        TaskType,
        DatasetBuildRequest,
        TrainRequest,
    )
    print("✅ Schema imports OK")
except Exception as e:
    print(f"❌ Schema imports failed: {e}")

# Test database retrieval directly
print("\n" + "-"*80)
print("Testing direct database query (simulating Training History tab)...")
print("-"*80)

try:
    from nanobio_studio.app.db.database import get_db, ModelRepository
    from sqlalchemy import text
    import pandas as pd
    
    db = get_db()
    session = db.get_session()
    
    # Raw count
    result = session.execute(text("SELECT COUNT(*) FROM trained_models"))
    row_count = result.scalar()
    print(f"✅ Raw count: {row_count} training records")
    
    # Repository retrieval (what the UI does)
    model_repo = ModelRepository(session)
    trained_models = model_repo.get_all()
    print(f"✅ ModelRepository.get_all() returned: {len(trained_models)} models")
    
    if trained_models:
        print("\n✅ Sample record:")
        model = trained_models[0]
        print(f"   Task: {model.task_name}")
        print(f"   Model: {model.model_type}")
        print(f"   Samples: {model.n_training_samples}")
        print(f"   Features: {model.n_features}")
        print(f"   Train R²: {model.train_score}")
        print(f"   Valid R²: {model.validation_score}")
        print(f"   Created: {model.created_at}")
    
    session.expunge_all()
    session.close()
    
    # Try to display as dataframe (like the UI does)
    print("\n✅ Converting to DataFrame...")
    models_data = []
    for model in trained_models:
        models_data.append({
            "Task": model.task_name,
            "Model Type": model.model_type,
            "Samples": model.n_training_samples,
            "Features": model.n_features,
            "Train R²": f"{model.train_score:.4f}" if model.train_score else "N/A",
            "Valid R²": f"{model.validation_score:.4f}" if model.validation_score else "N/A",
            "Created": model.created_at.strftime("%Y-%m-%d %H:%M:%S") if model.created_at else "N/A",
        })
    
    models_df = pd.DataFrame(models_data)
    print(f"✅ DataFrame created successfully:")
    print(models_df.to_string())
    
except Exception as e:
    import traceback
    print(f"\n❌ ERROR: {str(e)}")
    print(f"\nTraceback:")
    traceback.print_exc()

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
