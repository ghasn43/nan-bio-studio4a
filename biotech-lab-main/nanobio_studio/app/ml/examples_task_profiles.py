"""
Example: Using Task Profiles Programmatically

This script demonstrates how to use the pre-configured task profiles
to quickly set up ML training configurations.
"""

import pandas as pd
from nanobio_studio.app.ml.task_profiles import (
    get_profile_choices,
    get_profile_descriptions,
    get_profile,
    apply_profile,
    TASK_PROFILES,
)
from nanobio_studio.app.ml.schemas import DatasetBuildRequest, TrainRequest
from nanobio_studio.app.services.ml_service import MLService


def example_1_list_profiles():
    """Example 1: List all available profiles"""
    print("=" * 70)
    print("EXAMPLE 1: List All Available Profiles")
    print("=" * 70)
    
    names = get_profile_choices()
    descriptions = get_profile_descriptions()
    
    for name in names:
        print(f"  • {name}")
        print(f"    └─ {descriptions[name]}\n")


def example_2_get_profile_details():
    """Example 2: Get detailed information about a specific profile"""
    print("=" * 70)
    print("EXAMPLE 2: Get Profile Details (Toxicity Prediction)")
    print("=" * 70)
    
    profile = get_profile("toxicity_prediction")
    
    if profile:
        print(f"Task Name: {profile.task_name}")
        print(f"Task Type: {profile.task_type.value}")
        print(f"Description: {profile.description}")
        print(f"Default Target: {profile.default_target_variable}")
        print(f"Recommended Targets: {profile.recommended_target_variables}")
        print(f"Model Types: {[m.value for m in profile.model_types]}")
        print(f"Test Split: {profile.test_split}")
        print(f"Exclude Features: {profile.exclude_features}")
        print()


def example_3_apply_profile():
    """Example 3: Apply profile to a dataset"""
    print("=" * 70)
    print("EXAMPLE 3: Apply Profile to Dataset")
    print("=" * 70)
    
    # Load sample data
    df = pd.read_csv("comprehensive_lnp_dataset.csv")
    
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)}\n")
    
    # Apply toxicity prediction profile
    config, excludes, target = apply_profile("toxicity_prediction", df)
    
    print(f"Applied Profile: toxicity_prediction")
    print(f"Task Name: {config.task_name}")
    print(f"Task Type: {config.task_type.value}")
    print(f"Target Variable: {target}")
    print(f"Exclude Features: {excludes}")
    print(f"Test Split: {config.test_split}\n")


def example_4_build_dataset_with_profile():
    """Example 4: Build dataset using profile configuration"""
    print("=" * 70)
    print("EXAMPLE 4: Build Dataset with Profile")
    print("=" * 70)
    
    # Load data
    df = pd.read_csv("comprehensive_lnp_dataset.csv")
    
    # Apply profile
    config, excludes, target = apply_profile("toxicity_prediction", df)
    
    # Build request
    request = DatasetBuildRequest(task_config=config)
    
    # Build dataset
    ml_service = MLService()
    dataset = ml_service.build_dataset(df, request)
    
    print(f"Dataset Built!")
    print(f"  Total Samples: {dataset['n_samples']}")
    print(f"  Features: {dataset['n_features']}")
    print(f"  Training Samples: {len(dataset['X_train'])}")
    print(f"  Validation Samples: {len(dataset['X_valid'])}\n")


def example_5_customize_profile():
    """Example 5: Customize a profile for specific needs"""
    print("=" * 70)
    print("EXAMPLE 5: Customize Profile")
    print("=" * 70)
    
    # Load base profile
    profile = get_profile("toxicity_prediction")
    
    print(f"Original Profile:")
    print(f"  Exclude Features: {profile.exclude_features}")
    
    # Customize the profile
    profile.exclude_features.append("Endotoxin_EU_mL")
    profile.test_split = 0.15  # Use 85/15 split instead of 80/20
    
    print(f"\nCustomized Profile:")
    print(f"  Exclude Features: {profile.exclude_features}")
    print(f"  Test Split: {profile.test_split}\n")


def example_6_quick_reference():
    """Example 6: Print quick reference for all profiles"""
    print("=" * 70)
    print("EXAMPLE 6: Quick Reference - All Profiles")
    print("=" * 70)
    print()
    
    for profile_name, profile in TASK_PROFILES.items():
        print(f"📋 {profile_name.upper().replace('_', ' ')}")
        print(f"   Type: {profile.task_type.value}")
        print(f"   Target: {profile.default_target_variable}")
        print(f"   Models: {', '.join([m.value for m in profile.model_types])}")
        print()


if __name__ == "__main__":
    print("\n")
    print("🤖 NanoBio Studio - Task Profiles Examples")
    print("=" * 70)
    print()
    
    # Run examples
    example_1_list_profiles()
    print()
    example_2_get_profile_details()
    print()
    example_6_quick_reference()
    
    # Skip dataset-based examples if file doesn't exist
    try:
        import os
        if os.path.exists("comprehensive_lnp_dataset.csv"):
            example_3_apply_profile()
            print()
            example_5_customize_profile()
            print()
    except Exception as e:
        print(f"Dataset examples skipped: {e}\n")
    
    print("=" * 70)
    print("✅ Examples complete!")
    print("=" * 70)
