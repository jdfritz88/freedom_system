import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# ui_toggle_controls.py

import threading

# Toggle states and their labels
toggles = {
    "background_visible": True,
    "show_legend": False,
    "preview_enabled": True
}

_toggle_lock = threading.Lock()

# Toggle state accessors
def get_toggle_state(name):
    with _toggle_lock:
        return toggles.get(name, None)


def set_toggle_state(name, value):
    with _toggle_lock:
        if name in toggles:
            toggles[name] = bool(value)
            return True
        return False


def toggle_state(name):
    with _toggle_lock:
        if name in toggles:
            toggles[name] = not toggles[name]
            return toggles[name]
        return None


def get_all_toggles():
    with _toggle_lock:
        return toggles.copy()


# Debug/Test
if __name__ == "__main__":
    print("[ToggleControls] Initial toggle states:")
    for k, v in get_all_toggles().items():
        print(f" - {k}: {v}")

    print("\n[ToggleControls] Flipping 'show_legend' and 'preview_enabled'...")
    toggle_state("show_legend")
    toggle_state("preview_enabled")

    print("\n[ToggleControls] Updated toggle states:")
    for k, v in get_all_toggles().items():
        print(f" - {k}: {v}")
