# ML Module Integration Guide

Step-by-step guide to integrate the new ML Module with existing NanoBio Studio components.

## Prerequisites

- Python 3.8+
- Existing NanoBio Studio installation
- SQLAlchemy-compatible database (SQLite for dev, PostgreSQL for prod)

## Phase 1: Setup

### 1.1 Install Dependencies

```bash
# Install new dependencies
pip install fastapi uvicorn sqlalchemy pydantic

# Add to requirements.txt
echo "fastapi>=0.95.0" >> requirements.txt
echo "uvicorn>=0.21.0" >> requirements.txt
echo "sqlalchemy>=2.0" >> requirements.txt
echo "pydantic>=1.10" >> requirements.txt
```

### 1.2 Environment Configuration

Create `.env` file:

```env
# Database
DATABASE_URL=sqlite:///ml_module.db

# API
API_TITLE=NanoBio ML API
API_VERSION=1.0.0
API_PREFIX=/api/v1

# ML Models
MODELS_DIR=models_store
SUPPORTED_MODEL_TYPES=linear_regression,random_forest,gradient_boosting

# Training
DEFAULT_TEST_SPLIT=0.2
DEFAULT_RANDOM_STATE=42

# Logging
LOG_LEVEL=INFO
```

## Phase 2: Database Integration

### 2.1 Shared Database Setup

If using existing database:

```python
# app/db/database.py modifications
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use existing engine if available
def get_engine():
    from nanobio_studio.models import engine  # from existing models
    return engine

# Or create new engine with same connection
db_url = os.getenv("DATABASE_URL")
engine = create_engine(db_url)
```

### 2.2 Initialize Tables

```python
# In your existing init script
from nanobio_studio.app.db.models import Base
from sqlalchemy import create_engine

engine = create_engine(os.getenv("DATABASE_URL"))
Base.metadata.create_all(bind=engine)
```

### 2.3 Migrate Existing Data

```python
# If you have existing formulation/assay data
from nanobio_studio.app.db.database import get_db, FormulationRepository
from nanobio_studio.app.db.models import Formulation, Assay
import uuid

def migrate_formulations(existing_data):
    """Migrate existing formulation records"""
    session = get_db().get_session()
    repo = FormulationRepository(session)
    
    for item in existing_data:
        formulation = Formulation(
            id=str(uuid.uuid4()),
            name=item['name'],
            components=item['components'],  # JSON
            properties=item['properties'],
        )
        repo.create(formulation)
    
    session.close()
```

## Phase 3: Service Layer Integration

### 3.1 Add ML Service to Existing Architecture

```python
# In your main App.py or similar
from nanobio_studio.app.services.ml_service import MLService

# Initialize globally (or per-request)
ml_service = MLService(models_dir="models_store")

# Make available to other modules
app_context = {
    'ml_service': ml_service,
    # ... other services
}
```

### 3.2 Use in Existing Components

```python
# In existing Streamlit pages
import streamlit as st
from nanobio_studio.app.services.ml_service import MLService

ml_service = MLService()

# Build dataset from uploaded data
uploaded_file = st.file_uploader("Upload formulation data")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    dataset = ml_service.build_dataset(df, dataset_request)
    st.success(f"Built dataset: {dataset['n_samples']} samples")
```

## Phase 4: API Integration

### 4.1 Add FastAPI to Streamlit

Option A: Run FastAPI alongside Streamlit

```bash
# Terminal 1: Start FastAPI
uvicorn nanobio_studio.app.main:app --port 8001

# Terminal 2: Start Streamlit
streamlit run App.py
```

Option B: Embed FastAPI with Streamlit using threading

```python
# In App.py startup
import threading
import uvicorn
from nanobio_studio.app.main import app as fastapi_app

def run_api():
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8001)

# Start API in background
api_thread = threading.Thread(target=run_api, daemon=True)
api_thread.start()
```

### 4.2 Call API from Streamlit

```python
# pages/train_models.py
import requests
import streamlit as st

API_BASE = "http://localhost:8001/api/v1/ml"

def train_models_via_api():
    st.title("Train Models (via API)")
    
    uploaded_file = st.file_uploader("Upload CSV")
    if uploaded_file:
        # Call API
        files = {"file": uploaded_file}
        response = requests.post(
            f"{API_BASE}/train",
            files=files,
            json={"save_artifacts": True}
        )
        
        if response.status_code == 200:
            result = response.json()
            st.success(f"Best model: {result['best_model_type']}")
        else:
            st.error(f"API error: {response.text}")

if __name__ == "__main__":
    train_models_via_api()
```

## Phase 5: UI Integration

### 5.1 Add ML Pages to Menu

Create new Streamlit pages:

```python
# pages/11_ML_Training.py
import streamlit as st
from nanobio_studio.app.services.ml_service import MLService

st.set_page_config(page_title="ML Training", page_icon="🤖")

def main():
    st.title("🤖 ML Training Module")
    
    tab1, tab2, tab3 = st.tabs(["Dataset Builder", "Train Models", "Ranking"])
    
    with tab1:
        st.header("Build Dataset")
        # ... UI for dataset building
    
    with tab2:
        st.header("Train Models")
        # ... UI for model training
    
    with tab3:
        st.header("Rank Formulations")
        # ... UI for ranking

if __name__ == "__main__":
    main()
```

### 5.2 Integrate with Existing Tabs

```python
# tabs/ml.py
import streamlit as st
import pandas as pd
from nanobio_studio.app.services.ml_service import MLService

def render_ml_tab():
    """Render ML module tab in main app"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Dataset Building")
        if st.button("Build Dataset"):
            # ... implementation
            pass
    
    with col2:
        st.subheader("Model Training")
        if st.button("Train Models"):
            # ... implementation
            pass
```

## Phase 6: Authentication Integration

### 6.1 Protect API Routes

```python
# app/api/ml_router.py modifications
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(credentials = Depends(security)):
    """Verify JWT token"""
    # Integrate with existing auth
    from nanobio_studio.auth import verify_token
    return verify_token(credentials.credentials)

@router.post("/train")
async def train_models(
    file: UploadFile,
    request: TrainRequest,
    token = Depends(verify_token),  # Add auth
):
    # ... implementation
    pass
```

### 6.2 Streamlit Authentication Check

```python
# pages/11_ML_Training.py
import streamlit as st

def main():
    # Use existing auth from utils
    from nanobio_studio.ui.auth_gate import require_login
    
    require_login()
    
    # Rest of page
    st.title("ML Training")
```

## Phase 7: RBAC Integration

### 7.1 Add ML Permissions

```python
# Update existing RBAC config
ML_PERMISSIONS = {
    "ROLE_ADMIN": ["ml:read", "ml:write", "ml:delete"],
    "ROLE_SCIENTIST": ["ml:read", "ml:write"],
    "ROLE_VIEWER": ["ml:read"],
}
```

### 7.2 Protect Routes with RBAC

```python
# app/api/ml_router.py
from nanobio_studio.rbac import has_permission

@router.post("/train")
async def train_models(
    request: TrainRequest,
    token = Depends(verify_token),
):
    # Check permission
    if not has_permission(token.user_id, "ml:write"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    # ... implementation
```

## Phase 8: Testing Integration

### 8.1 Run Tests

```bash
# Test ML module
pytest tests/app/test_ml_service.py -v

# Test API
pytest tests/app/test_api.py -v

# Test integration
pytest tests/integration/test_ml_streamlit.py -v
```

### 8.2 Create Integration Tests

```python
# tests/integration/test_ml_streamlit.py
import pytest
from nanobio_studio.app.services.ml_service import MLService

def test_ml_service_with_real_data():
    """Test ML service with real formulation data"""
    
    ml_service = MLService()
    
    # Load test data from existing fixtures
    records = pd.read_csv("tests/fixtures/formulations.csv")
    
    # Build dataset
    dataset = ml_service.build_dataset(records, config)
    assert dataset['n_samples'] > 0
    
    # Train models
    response = ml_service.train_models(records, request)
    assert response.best_model_type is not None
```

## Phase 9: Data Migration (Optional)

If migrating from old AI engine:

```python
# scripts/migrate_ai_engine_to_ml.py
"""Migrate old AI engine models to new ML module"""

import os
import shutil
from nanobio_studio.app.db.database import get_db
from nanobio_studio.app.db.models import Artifact

def migrate_models():
    """Migrate old engine artifacts"""
    
    old_dir = "nanobio_studio/ai_engine/artifacts"
    new_dir = "models_store"
    
    # Copy files
    for filename in os.listdir(old_dir):
        src = os.path.join(old_dir, filename)
        dst = os.path.join(new_dir, filename)
        shutil.copy2(src, dst)

def migrate_db_records():
    """Migrate database records"""
    
    session = get_db().get_session()
    
    # Copy relevant records from old tables to new
    # ... implementation

if __name__ == "__main__":
    migrate_models()
    migrate_db_records()
    print("Migration complete")
```

## Phase 10: Documentation & Training

### 10.1 Update Main README

Add section to main README.md:

```markdown
## ML Module

NanoBio Studio now includes a full ML module for:
- Dataset building from formulation records
- Model training and evaluation
- Candidate ranking

See [nanobio_studio/app/README.md](nanobio_studio/app/README.md) for details.
```

### 10.2 Create User Guide

```markdown
# ML Module User Guide

## Quick Start

1. Upload formulation data (CSV)
2. Configure dataset building (target variable, features)
3. Train models (automatic model selection)
4. Use trained model for predictions
```

## Deployment Checklist

- [ ] Dependencies installed
- [ ] Database initialized
- [ ] Environment variables configured
- [ ] API running successfully
- [ ] Authentication integrated
- [ ] RBAC rules configured
- [ ] Streamlit pages updated
- [ ] Tests passing
- [ ] Documentation complete

## Troubleshooting

### FAQ

**Q: API won't start due to import errors**
- A: Ensure `PYTHONPATH` includes project root
- A: Check all `__init__.py` files exist

**Q: Database lock errors**
- A: Close all connections: `get_db().close()`
- A: Delete `ml_module.db` and reinitialize

**Q: Slow training**
- A: Use smaller dataset
- A: Reduce number of models to train
- A: Consider distributed training

## Support

- Issues: Create GitHub issue with `[ml-module]` tag
- Questions: Check README and user guide
- Performance: See optimization section in README

## Next Steps

1. ✅ Phase 2: Complete implementation
2. ⏳ Phase 3: Integration with existing components
3. ⏳ Phase 4: Testing and validation
4. ⏳ Phase 5: Deployment and monitoring
