import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# 🧪 Runtime Test: Startup Launcher + Flag Checks
# Folder: F:/Apps/freedom_system/componentsave/launchers
# Purpose: Confirm critical startup modules load and link correctly

import importlib
import inspect

results = []

# List of essential launcher modules to verify
launchers = {
    "emotion_engine_boot_flag": ["check_flag", "write_flag"],
    "face_training_launcher": ["launch_face_trainer", "check_face_session"],
    "start_emotion_engine_flag_check": ["run_flag_check", "validate_paths"]
}

for modname, required_funcs in launchers.items():
    try:
        module = importlib.import_module(f"launchers.{modname}")
        funcs = [name for name, _ in inspect.getmembers(module, inspect.isfunction)]

        present = [f for f in required_funcs if f in funcs]
        if len(present) == len(required_funcs):
            results.append(f"✅ {modname}: all expected functions present")
        else:
            missing = set(required_funcs) - set(present)
            results.append(f"❌ {modname}: missing functions: {', '.join(missing)}")

    except Exception as e:
        results.append(f"❌ {modname} failed to load: {e}")

# 📊 Output launcher results
print("\nStartup Launcher Flag Check:")
for line in results:
    print(line)
