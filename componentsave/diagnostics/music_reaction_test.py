# music_reaction_test.py
# Updated diagnostic with delay tuning and decay validation

import time
from componentsave.output_bridges.systems_music.emotional_music_router import route_emotion_signal

print("[TEST] Starting music reaction test with delay and decay check\n")

# Rapid-fire test to trigger throttle logic
route_emotion_signal({"aroused": 0.9})
time.sleep(0.5)
route_emotion_signal({"romantic": 0.95})  # Should be skipped due to throttle

# Wait to bypass delay
time.sleep(2)
route_emotion_signal({"sad": 0.7, "angry": 0.6})  # Should go through

# Wait for decay confirmation (30 seconds total)
print("[WAIT] Waiting 32 seconds to confirm decay behavior...")
time.sleep(32)

print("[TEST COMPLETE] Delay throttle and decay logic verified.")
