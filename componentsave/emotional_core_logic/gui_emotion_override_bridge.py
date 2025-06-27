# GUI import header (required for cross-module access in Freedom System)
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import threading
import time
from emotion_delay_throttle import set_emotion_delay
from emotion_decay_module import set_emotion_decay
from emotion_system_status import log_override_update

# These could be hooked directly to GUI sliders or input fields
current_delay = 0.3  # default seconds
default_decay = 30.0  # default seconds

# Flags set by GUI events
override_delay = None
override_decay = None

# Thread-safe lock for GUI access
override_lock = threading.Lock()

def update_delay(value):
    global override_delay
    with override_lock:
        override_delay = value
        set_emotion_delay(value)
        log_override_update("Delay", value)

def update_decay(value):
    global override_decay
    with override_lock:
        override_decay = value
        set_emotion_decay(value)
        log_override_update("Decay", value)

def monitor_gui_override_loop():
    print("[GUI-BRIDGE] Emotion override monitor started.")
    last_delay, last_decay = None, None
    while True:
        time.sleep(1)
        with override_lock:
            if override_delay is not None and override_delay != last_delay:
                set_emotion_delay(override_delay)
                last_delay = override_delay
            if override_decay is not None and override_decay != last_decay:
                set_emotion_decay(override_decay)
                last_decay = override_decay

def start_gui_emotion_override_monitor():
    monitor_thread = threading.Thread(target=monitor_gui_override_loop, daemon=True)
    monitor_thread.start()
    print("[GUI-BRIDGE] GUI override thread launched.")

# 🔌 LIVE INTEGRATION HOOK (call this from emotion_system_core.py):
if __name__ == "__main__":
    start_gui_emotion_override_monitor()
