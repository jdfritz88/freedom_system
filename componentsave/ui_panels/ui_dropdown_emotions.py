import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# ui_dropdown_emotions.py

import threading
import time
from emotional_core_logic.freedom_emotion_blender import get_current_emotion_blend

# Thread-safe emotion blend cache
_cached_blend = {}
_blend_lock = threading.Lock()
_blend_thread_started = False

# Efficient updater using throttled background thread
def update_blend_cache():
    global _cached_blend
    while True:
        latest = get_current_emotion_blend()
        if latest is not None:
            with _blend_lock:
                _cached_blend = latest
        time.sleep(1.0)  # Energy-efficient interval


def get_dropdown_emotions():
    with _blend_lock:
        if not _cached_blend:
            return ["(No active emotions)"]
        return [f"{emotion}: {score:.2f}" for emotion, score in sorted(_cached_blend.items(), key=lambda x: x[1], reverse=True)]


def init_dropdown_tracker():
    global _blend_thread_started
    if not _blend_thread_started:
        thread = threading.Thread(target=update_blend_cache, daemon=True)
        thread.start()
        _blend_thread_started = True


# Debug/Test
if __name__ == "__main__":
    init_dropdown_tracker()
    try:
        while True:
            emotions = get_dropdown_emotions()
            print("\n[Dropdown] Current Emotion Blend:")
            for line in emotions:
                print(" -", line)
            time.sleep(3)
    except KeyboardInterrupt:
        print("[Dropdown] Tracker halted.")
