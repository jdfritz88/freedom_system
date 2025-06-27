import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# 🧪 Runtime Test: Voice Delay + Emotion Lock Sync
# Folder: F:/Apps/freedom_system/componentsave/emotional_core_logic
# Purpose: Ensure Coqui TTS respects emotion locking and delay throttle

import importlib
import inspect
import time

results = []

try:
    delay_mod = importlib.import_module("emotional_core_logic.emotion_delay_throttle")
    funcs = [name for name, _ in inspect.getmembers(delay_mod, inspect.isfunction)]

    test_func = getattr(delay_mod, "delay_voice_if_needed", None)
    if test_func:
        t0 = time.time()
        test_func("Excited")
        t1 = time.time()
        elapsed = t1 - t0

        if elapsed >= 0.3:
            results.append(f"✅ Voice delay enforced ({elapsed:.2f}s)")
        else:
            results.append(f"❌ Delay too short ({elapsed:.2f}s) — may overlap speech")
    else:
        results.append("❌ delay_voice_if_needed() not found")

except Exception as e:
    results.append(f"❌ Voice delay throttle module failed: {e}")

# 📊 Output delay sync results
print("\nVoice Delay Sync Runtime Check:")
for line in results:
    print(line)
