import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# ui_master_orb.py

import threading
import time
from emotional_core_logic.freedom_emotion_blender import get_current_emotion_blend

# Orb state cache
_cached_emotions = None
_cache_lock = threading.Lock()
_orb_thread_started = False

# Event handler to throttle updates
def update_orb_state():
    global _cached_emotions
    while True:
        blend = get_current_emotion_blend()
        with _cache_lock:
            _cached_emotions = blend
        time.sleep(1.0)  # Throttle refresh to 1/sec for CPU + battery savings


def get_orb_display_state():
    with _cache_lock:
        if not _cached_emotions:
            return "[Orb] No emotion active."

        sorted_emotions = sorted(_cached_emotions.items(), key=lambda x: x[1], reverse=True)

        if len(sorted_emotions) == 1:
            e1, v1 = sorted_emotions[0]
            return f"[Orb] Dominant: {e1} ({v1:.2f})"
        else:
            (e1, v1), (e2, v2) = sorted_emotions[:2]
            return f"[Orb] {e1} ({v1:.2f}) + {e2} ({v2:.2f})"


def init_orb_tracker():
    global _orb_thread_started
    if not _orb_thread_started:
        thread = threading.Thread(target=update_orb_state, daemon=True)
        thread.start()
        _orb_thread_started = True


# Debug/Test
if __name__ == "__main__":
    init_orb_tracker()
    try:
        while True:
            print(get_orb_display_state())
            time.sleep(2)
    except KeyboardInterrupt:
        print("[Orb] Display loop halted.")
