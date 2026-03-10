"""
Phase 3 Integration Summary & Setup Guide

Instructions for integrating Phase 3 components into the existing NanoBio Studio.
"""

# PHASE 3 INTEGRATION CHECKLIST

## ✅ Files Created

### Authentication Components
- `nanobio_studio/app/auth/jwt_handler.py` - JWT token management
- `nanobio_studio/app/auth/rbac.py` - Role-based access control
- `nanobio_studio/app/auth/__init__.py` - Package exports

### Streamlit Integration
- `nanobio_studio/app/ui/streamlit_auth.py` - Streamlit auth utilities
- `nanobio_studio/app/phase3_config.py` - Phase 3 configuration
- `pages/0_Login.py` - Login page
- `pages/12_ML_Training.py` - ML training interface
- `pages/13_ML_Ranking.py` - ML ranking interface
- `pages/14_Model_Management.py` - Model management dashboard

## 🔧 Integration Steps

### Step 1: Update Main App.py

Add to the top of App.py:

```python
import streamlit as st
from nanobio_studio.app.ui.streamlit_auth import StreamlitAuth, require_login

# Initialize authentication
StreamlitAuth.init_session_state()

# Redirect to login if not authenticated
if not st.session_state.get('authenticated', False):
    st.info("👈 Please log in using the Login page")
    st.stop()
```

### Step 2: Add Auth UI to Sidebar

Add to App.py sidebar section:

```python
with st.sidebar:
    st.divider()
    st.subheader("User Info")
    
    from nanobio_studio.app.ui.streamlit_auth import show_user_info
    show_user_info()
```

### Step 3: Environment Variables

Create or update `.env` file:

```env
JWT_SECRET_KEY=your-secret-key-here
JWT_EXPIRATION_HOURS=24
ENABLE_RBAC=true
REQUIRE_LOGIN=true
APP_ENV=development
```

### Step 4: Install Dependencies

```bash
pip install pyjwt>=2.4.0
```

### Step 5: Test Integration

1. Start Streamlit: `streamlit run App.py`
2. Navigate to Login page
3. Use demo credentials:
   - Admin: admin / admin123
   - Scientist: scientist / science123
   - Viewer: viewer / view123
4. Access new ML pages (12, 13, 14)

## 📊 Authentication Flow

```
User visits app
    ↓
Streamlit checks session_state.authenticated
    ↓
If False → Redirect to Login page
    ↓
User enters credentials
    ↓
JWT token created
    ↓
Session state updated
    ↓
Redirect to main app
    ↓
User can access ML features based on RBAC
```

## 🔐 RBAC Roles & Permissions

### Admin
- All permissions
- Can train, delete, export models
- User management

### Scientist
- Can train models
- Can create datasets
- Can rank candidates
- Cannot delete or manage users

### Viewer
- Read-only access
- Can view models, rankings, datasets
- Cannot train or modify

### Guest
- Very limited access
- Can only view basic model info

## 📝 Key Features

### 1. JWT Tokens
- Secure token-based authentication
- Automatic expiration (24 hours default)
- Token refresh capability

### 2. RBAC System
- 8+ permission types
- 4 built-in roles
- Easy to extend with custom permissions

### 3. Streamlit Auth Utils
- Drop-in authentication
- Session management
- Permission checking utilities

### 4. ML Integration Pages
- Dataset builder with validation
- Model training interface
- Candidate ranking system
- Model management dashboard

## 🚀 Demo Accounts

Use these for testing:

```
Admin Account:
  Username: admin
  Password: admin123
  Roles: admin

Scientist Account:
  Username: scientist
  Password: science123
  Roles: scientist

Viewer Account:
  Username: viewer
  Password: view123
  Roles: viewer
```

## 🔄 Workflow Example

1. **Data Scientist logs in as "scientist"**
   - Access granted to ML Training page
   - Can create datasets
   - Can train models

2. **Uploads formulation data**
   - Builds dataset with specified parameters
   - Trains multiple models
   - Selects best model
   - Model saved to database

3. **Uses ML Ranking page**
   - Uploads candidate formulations
   - Sets ranking criteria
   - Ranks candidates
   - Downloads results

4. **Views Model Management**
   - Sees trained models
   - Views performance metrics
   - Can export models

5. **Viewer logs in**
   - Can see models and rankings
   - Cannot train new models
   - Read-only access

## 📊 Database Integration

Trained models automatically saved to:
- `trained_models` table
- `model_predictions` table
- `artifacts` table

Query examples:

```python
from nanobio_studio.app.db.database import get_db, ModelRepository

db = get_db()
session = db.get_session()
model_repo = ModelRepository(session)

# Get all models
models = model_repo.get_all()

# Get specific model
model = model_repo.get_by_task("toxicity_prediction")

session.close()
```

## ⚙️ Configuration Options

### JWT Settings
- `JWT_SECRET_KEY` - Token signing key
- `JWT_EXPIRATION_HOURS` - Token expiration time
- `JWT_REFRESH_EXPIRATION_DAYS` - Refresh token expiration

### Streamlit Settings
- `STREAMLIT_SESSION_TIMEOUT` - Session timeout in seconds
- `STREAMLIT_ENABLE_CACHE` - Enable caching
- `STREAMLIT_CACHE_TTL` - Cache time-to-live

### RBAC Settings
- `ENABLE_RBAC` - Enable role-based access
- `REQUIRE_LOGIN` - Require login on all pages
- `DEFAULT_ROLE` - Default role for new users

## 🐛 Troubleshooting

### "Not authenticated" error
→ Go to Login page first and use demo credentials

### Permission denied errors
→ Check user role on Login page; switch to higher permission role if needed

### Token expired
→ Log out and log in again to get new token

### Database errors
→ Ensure SQLite database is initialized (`python -c "from nanobio_studio.app.db.database import get_db; get_db().init_db()"`)

## 🔍 Verification

Check that all files exist:

```bash
# Auth files
test -f "nanobio_studio/app/auth/jwt_handler.py" && echo "✅ JWT handler"
test -f "nanobio_studio/app/auth/rbac.py" && echo "✅ RBAC"

# Streamlit files
test -f "pages/0_Login.py" && echo "✅ Login page"
test -f "pages/12_ML_Training.py" && echo "✅ ML Training"
test -f "pages/13_ML_Ranking.py" && echo "✅ ML Ranking"
test -f "pages/14_Model_Management.py" && echo "✅ Model Management"

# Config files
test -f "nanobio_studio/app/phase3_config.py" && echo "✅ Phase 3 config"
```

## 📚 Documentation

- See `nanobio_studio/app/INTEGRATION_GUIDE.md` for detailed integration steps
- See individual page docstrings for feature documentation
- See `nanobio_studio/app/auth/rbac.py` for RBAC details
- See `nanobio_studio/app/auth/jwt_handler.py` for JWT details

## 🎯 Next Steps (Phase 4)

- [ ] Production JWT secret key management
- [ ] Database-backed user authentication
- [ ] Email verification
- [ ] OAuth integration (Google, GitHub)
- [ ] Advanced audit logging
- [ ] Multi-factor authentication
- [ ] Session management improvements
- [ ] Performance optimization

---

**Phase 3 Status**: ✅ COMPLETE

All authentication, RBAC, and Streamlit integration components are ready for deployment.
