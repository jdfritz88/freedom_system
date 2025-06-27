import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# ui_status_area.py

import threading
import time
from emotional_core_logic.emotion_system_status import get_emotion_system_status

# Status cache for battery-safe refresh
_status_lock = threading.Lock()
_cached_status = "(Status not available)"
_status_thread_started = False

# Background update thread (throttled)
def update_status():
    global _cached_status
    while True:
        latest = get_emotion_system_status()
        if latest:
            with _status_lock:
                _cached_status = latest
        time.sleep(1.5)  # Optimized delay: updates every 1.5 sec

# Public getter
def get_current_status():
    with _status_lock:
        return _cached_status

# Safe init of thread
def init_status_tracker():
    global _status_thread_started
    if not _status_thread_started:
        thread = threading.Thread(target=update_status, daemon=True)
        thread.start()
        _status_thread_started = True


# Debug/Test
if __name__ == "__main__":
    init_status_tracker()
    try:
        while True:
            print("[StatusArea]", get_current_status())
            time.sleep(2.5)
    except KeyboardInterrupt:
        print("[StatusArea] Tracker stopped.")
