import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# ui_override_controls.py

import threading

# Emotion override state
_override_lock = threading.Lock()
_override_state = {
    "active": False,
    "emotion": None,
    "intensity": 0.0
}

# Get current override
def get_override():
    with _override_lock:
        return _override_state.copy()

# Set override (emotion name and intensity)
def set_override(emotion_name, intensity):
    with _override_lock:
        _override_state["active"] = True
        _override_state["emotion"] = emotion_name
        _override_state["intensity"] = round(float(intensity), 2)

# Clear override manually
def clear_override():
    with _override_lock:
        _override_state["active"] = False
        _override_state["emotion"] = None
        _override_state["intensity"] = 0.0

# Check if override is active
def is_override_active():
    with _override_lock:
        return _override_state["active"]


# Debug/Test
if __name__ == "__main__":
    print("[Override] Initial state:", get_override())
    print("[Override] Setting override: Aroused @ 0.85")
    set_override("Aroused", 0.85)
    print("[Override] Active:", is_override_active())
    print("[Override] Current state:", get_override())
    print("[Override] Clearing override...")
    clear_override()
    print("[Override] Final state:", get_override())
