# NanoBio ML Module - Phase 2 Implementation

Complete ML system for biotech lab applications including dataset building, model training, prediction, and candidate ranking.

## Architecture Overview

```
nanobio_studio/app/
├── main.py                     # FastAPI app factory
├── config.py                   # Configuration management
├── services/
│   └── ml_service.py          # High-level ML orchestration
├── api/
│   └── ml_router.py           # REST API endpoints
├── db/
│   ├── models.py              # SQLAlchemy ORM models
│   └── database.py            # Database utilities
└── ml/
    ├── dataset_builder.py     # Dataset construction
    ├── feature_builder.py     # Feature engineering
    ├── preprocess.py          # Data preprocessing
    ├── train.py               # Model training
    ├── predict.py             # Prediction interface
    ├── ranker.py              # Candidate ranking
    ├── persistence.py         # Model artifacts storage
    └── schemas.py             # Pydantic models
```

## Key Components

### ML Pipeline
- **DatasetBuilder**: Creates train/validation splits from raw formulation/assay records
- **FeatureBuilder**: Generates domain-specific features with optional engineering
- **PreprocessingPipeline**: Scales numeric features, encodes categorical variables
- **ModelTrainer**: Trains multiple models (regression/classification) in parallel
- **CandidateRanker**: Ranks formulations by multiple criteria
- **ModelPersistence**: Saves/loads models with preprocessing pipelines

### Services Layer
- **MLService**: Orchestrates dataset building, training, evaluation
- **RankingService**: Handles candidate ranking operations
- Dependency injection via FastAPI

### REST API
- `GET /api/v1/ml/health` - Health check
- `POST /api/v1/ml/dataset/build` - Build training dataset
- `POST /api/v1/ml/train` - Train models
- `POST /api/v1/ml/rank` - Rank candidates
- `GET /api/v1/ml/models` - List available models

### Database
- **SQLAlchemy ORM** models for:
  - Formulations (with flexible JSON schema)
  - Assays (linked to formulations)
  - Trained models (with evaluation metrics)
  - Model predictions
  - Ranking results
- CRUD repositories with clean abstraction
- Support for SQLite (dev) and PostgreSQL (prod)

## Usage

### 1. Installation

```bash
# Install dependencies
pip install fastapi uvicorn sqlalchemy pandas scikit-learn pydantic

# Or use requirements.txt from core ml module
pip install -r requirements.txt
```

### 2. Configuration

Create `.env` file or set environment variables:

```env
ENV=development
DATABASE_URL=sqlite:///ml_module.db
API_TITLE=NanoBio ML API
MODELS_DIR=models_store
LOG_LEVEL=INFO
```

### 3. Start API Server

```python
# method 1: Direct import
from nanobio_studio.app import app
import uvicorn

uvicorn.run(app, host="0.0.0.0", port=8000)

# method 2: Command line
uvicorn nanobio_studio.app.main:app --reload
```

### 4. Use ML Service (Programmatic)

```python
from nanobio_studio.app.services.ml_service import MLService
from nanobio_studio.app.schemas import (
    MLTaskConfig, TaskType, DatasetBuildRequest, TrainRequest
)
import pandas as pd

# Load data
records = pd.read_csv("formulations.csv")

# Create service
ml_service = MLService(models_dir="models_store")

# Build dataset
dataset_request = DatasetBuildRequest(
    task_config=MLTaskConfig(
        task_name="toxicity_prediction",
        task_type=TaskType.REGRESSION,
        target_variable="toxicity_score",
    )
)
dataset = ml_service.build_dataset(records, dataset_request)
print(f"Dataset: {dataset['n_samples']} samples, {dataset['n_features']} features")

# Train models
train_request = TrainRequest(
    dataset_build_request=dataset_request,
    save_artifacts=True,
)
response = ml_service.train_models(records, train_request)
print(f"Best model: {response.best_model_type}")
for summary in response.evaluation_summaries:
    print(f"  {summary.model_type}: validation_score={summary.validation_metrics.accuracy}")
```

### 5. Use REST API (with client)

```python
import requests
import pandas as pd

# Build dataset
with open("formulations.csv", "rb") as f:
    files = {"file": f}
    data = {
        "task_name": "toxicity_prediction",
        "task_type": "regression",
        "target_variable": "toxicity_score",
    }
    response = requests.post(
        "http://localhost:8000/api/v1/ml/dataset/build",
        files=files,
        data=data,
    )
    print(response.json())

# Train models
with open("formulations.csv", "rb") as f:
    files = {"file": f}
    data = {
        "dataset_build_request": {
            "task_config": {
                "task_name": "toxicity_prediction",
                "task_type": "regression",
                "target_variable": "toxicity_score",
            }
        },
        "save_artifacts": True,
    }
    response = requests.post(
        "http://localhost:8000/api/v1/ml/train",
        files=files,
        json=data,
    )
    print(response.json())

# Rank candidates
candidates = [
    {"component_a": 10, "component_b": 20, ...},
    {"component_a": 15, "component_b": 25, ...},
]
response = requests.post(
    "http://localhost:8000/api/v1/ml/rank",
    json={
        "candidates": candidates,
        "criteria": {"toxicity": "minimize"},
    }
)
print(response.json())
```

## Integration with Existing NanoBio Studio

### Database Integration

```python
# In your existing database module
from nanobio_studio.app.db import Base, get_db

# share Base for multi-DB setup
from sqlalchemy.orm import Session

def init_ml_database(existing_engine):
    """Initialize ML tables in existing database"""
    Base.metadata.create_all(bind=existing_engine)

def get_ml_session(existing_session: Session) -> Session:
    """Use existing session context"""
    pass
```

### UI Integration (Streamlit)

```python
# In your Streamlit pages
import streamlit as st
from nanobio_studio.app.services.ml_service import MLService

st.title("ML Training")

ml_service = MLService()

# File upload
uploaded_file = st.file_uploader("Upload data", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    # Build dataset
    if st.button("Build Dataset"):
        dataset = ml_service.build_dataset(df, dataset_request)
        st.write(dataset)
    
    # Train models
    if st.button("Train Models"):
        response = ml_service.train_models(df, train_request)
        st.write(response)
```

## Testing

```python
# pytest tests/app/test_ml_service.py -v

import pytest
from nanobio_studio.app.services.ml_service import MLService

@pytest.fixture
def ml_service():
    return MLService(models_dir="/tmp/test_models")

def test_build_dataset(ml_service, sample_records):
    """Test dataset building"""
    dataset = ml_service.build_dataset(sample_records, config)
    assert dataset['n_samples'] > 0
    assert dataset['n_features'] > 0
    assert 'X_train' in dataset
    assert 'y_train' in dataset

def test_train_models(ml_service, sample_records):
    """Test model training"""
    response = ml_service.train_models(sample_records, request)
    assert response.best_model_type is not None
    assert len(response.evaluation_summaries) > 0
```

## Migration Guide (from old AI engine)

If migrating from the old AI engine:

```python
# Old approach
from nanobio_studio.ai_engine import Simulator
sim = Simulator()
results = sim.run_simulation(config)

# New approach
from nanobio_studio.app.services.ml_service import MLService
ml_service = MLService()
response = ml_service.train_models(records, train_request)
```

Key differences:
- **Modular**: Each component is independently testable
- **Scalable**: Ready for distributed training
- **REST-based**: Can be deployed as microservice
- **Database-backed**: Persistent model management
- **Type-safe**: Full Pydantic validation

## Deployment

### Local Development
```bash
uvicorn nanobio_studio.app.main:app --reload --port 8000
```

### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY nanobio_studio ./nanobio_studio
EXPOSE 8000
CMD ["uvicorn", "nanobio_studio.app.main:app", "--host", "0.0.0.0"]
```

### Production (Gunicorn + Nginx)
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker nanobio_studio.app.main:app
```

## Documentation

- **API Docs**: `http://localhost:8000/docs` (auto-generated Swagger)
- **Core ML Module**: See [../core/QUICK_START.md](../core/QUICK_START.md)
- **AI Engine**: See [../ai_engine/README.md](../ai_engine/README.md)

## Troubleshooting

### Import errors
- Ensure `PYTHONPATH` includes workspace root
- Check `__init__.py` files exist in all packages

### Database issues
- Delete `ml_module.db` to reset
- Check `DATABASE_URL` environment variable
- SQLite: verify write permissions

### Training issues
- Check data format matches schema
- Verify target variable exists
- Check numeric/categorical feature lists

## Performance Optimization

- Model training uses `n_jobs=-1` (all cores)
- Preprocessing pipeline cached
- Feature engineering optional
- Batch prediction support

## Future Enhancements

- [ ] Hyperparameter optimization (Optuna)
- [ ] Ensemble methods
- [ ] Online learning support
- [ ] Model versioning with DVC
- [ ] Feature importance ranking
- [ ] SHAP explainability
- [ ] Distributed training (Ray/Dask)
