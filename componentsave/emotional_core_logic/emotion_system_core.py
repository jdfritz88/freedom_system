# GUI import header (required for cross-module access in Freedom System)
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gui_emotion_override_bridge import update_delay, update_decay, start_gui_emotion_override_monitor

# Emotion engine startup logic begins here...

# 🧠 Start the GUI override monitor during emotion system init
start_gui_emotion_override_monitor()

# Simulated heartbeat to confirm engine stays alive
import time
print("[CORE] Emotion system core is running...")

# Simulate GUI changes after a few cycles
def trigger_gui_test():
    time.sleep(6)
    update_delay(0.5)
    time.sleep(4)
    update_decay(42.0)

import threading
threading.Thread(target=trigger_gui_test, daemon=True).start()

while True:
    time.sleep(5)
    print("[CORE] Heartbeat...")
