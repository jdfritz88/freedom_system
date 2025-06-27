import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# 🧪 Runtime Test: Emotion Trigger Threshold
# Folder: F:/Apps/freedom_system/componentsave/emotional_core_logic
# Purpose: Ensure trigger activates only when intensity exceeds threshold

import importlib
import inspect

results = []

# Load threshold control module and verify logic
try:
    threshold_mod = importlib.import_module("emotional_core_logic.emotion_threshold_control")
    funcs = [name for name, _ in inspect.getmembers(threshold_mod, inspect.isfunction)]

    eval_func = getattr(threshold_mod, "should_trigger_emotion", None)
    if eval_func:
        low_trigger = eval_func(0.65, 0.7)  # Below threshold
        high_trigger = eval_func(0.75, 0.7)  # Above threshold

        if not low_trigger and high_trigger:
            results.append("✅ Threshold gate triggers only when intensity exceeds threshold")
        else:
            results.append("❌ Trigger logic misfires: check comparison or float handling")
    else:
        results.append("❌ should_trigger_emotion() not found")

except Exception as e:
    results.append(f"❌ Threshold control module failed: {e}")

# 📊 Output results
print("\nEmotion Threshold Trigger Check:")
for line in results:
    print(line)
