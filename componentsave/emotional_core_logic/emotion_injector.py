import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# 🧪 Manual Emotion Injection Tool (Standalone)
# ---------------------------------------------
# Save as: emotion_injector.py
# Run this script any time the emotion engine is live

from componentsave.emotion_system_core import EmotionSystemCore
import time

# 🔧 CONFIGURE
EMOTION = "Romantic"
INTENSITY = 0.92

# ⚠️ This assumes the EmotionSystemCore is already running elsewhere
# This directly connects to the global queue and injects a one-time pulse

if __name__ == '__main__':
    core = EmotionSystemCore()
    print(f"[INJECT] Sending {EMOTION} @ {INTENSITY}")
    core.emotion_queue.put((EMOTION, INTENSITY))
    time.sleep(1)
    print("[INJECT] Complete")
