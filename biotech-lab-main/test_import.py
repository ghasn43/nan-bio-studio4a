import sys
import traceback

try:
    print("Attempting to import pages._12_ML_Training...")
    # Try importing directly without going through pages namespace
    import importlib.util
    spec = importlib.util.spec_from_file_location("_12_ML_Training", "./pages/12_ML_Training.py")
    module = importlib.util.module_from_spec(spec)
    print("Module spec created, executing...")
    try:
        spec.loader.exec_module(module)
        print("SUCCESS")
    except Exception as e:
        print(f"ERROR during module execution: {e}")
        traceback.print_exc()
except Exception as e:
    print(f"ERROR: {e}")
    traceback.print_exc()
