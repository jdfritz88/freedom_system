import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# 🔪 Extended Runtime Test: UI Panel Threshold + Resolution Validation
# Folder: F:/Apps/freedom_system/componentsave/ui_panels

import importlib.util
import inspect

results = []

# Load gui_emotion_panels using direct path
module_path = os.path.join(os.path.dirname(__file__), "gui_emotion_panels.py")
spec = importlib.util.spec_from_file_location("gui_emotion_panels", module_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# 1. Emotion Threshold Control Validation
try:
    funcs = [name for name, _ in inspect.getmembers(mod, inspect.isfunction)]
    expected = ["set_emotion_threshold", "get_emotion_threshold", "apply_threshold_override"]
    present = [f for f in expected if f in funcs]

    if len(present) == len(expected):
        results.append("✅ Emotion threshold controls: All expected methods present")
    else:
        missing = set(expected) - set(present)
        results.append(f"❌ Missing threshold functions: {', '.join(missing)}")
except Exception as e:
    results.append(f"❌ Threshold check failed: {e}")

# 2. Image Resolution Preset Validation
try:
    expected = ["set_default_resolution", "get_current_resolution", "toggle_resolution_mode"]
    present = [f for f in expected if f in funcs]

    if len(present) == len(expected):
        results.append("✅ Resolution controls: All expected methods present")
    else:
        missing = set(expected) - set(present)
        results.append(f"❌ Missing resolution functions: {', '.join(missing)}")
except Exception as e:
    results.append(f"❌ Resolution check failed: {e}")

print("\n[EXTENDED UI PANEL TEST RESULTS]\n")
for line in results:
    print(line)
print("\n[END OF EXTENDED TEST]\n")
