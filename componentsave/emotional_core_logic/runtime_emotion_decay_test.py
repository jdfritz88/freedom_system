import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# 🧪 Runtime Test: Emotion Decay Logic
# Folder: F:/Apps/freedom_system/componentsave/emotional_core_logic
# Purpose: Validate global decay curve and intensity drop over time

import importlib
import inspect
import time

results = []

# Load decay module and confirm decay behavior is time-based and global
try:
    decay_mod = importlib.import_module("emotional_core_logic.emotion_decay_module")
    funcs = [name for name, _ in inspect.getmembers(decay_mod, inspect.isfunction)]

    test_func = getattr(decay_mod, "simulate_emotion_decay", None)
    if test_func:
        # Start at full intensity
        intensity = 1.0
        decay_log = []
        for second in range(0, 35, 5):
            value = test_func(intensity, second)
            decay_log.append(f"t+{second}s: {value:.3f}")
        
        final_val = test_func(1.0, 30)
        if 0.0 <= final_val <= 0.01:
            results.append("✅ Emotion decays globally from 1.0 → 0 over 30s")
        else:
            results.append(f"❌ Final decay at 30s was too high: {final_val:.3f}")
        results.extend(decay_log)
    else:
        results.append("❌ simulate_emotion_decay() not found")

except Exception as e:
    results.append(f"❌ Emotion decay module failed: {e}")

# 📊 Output decay tracking results
print("\nEmotion Decay Runtime Check:")
for line in results:
    print(line)
