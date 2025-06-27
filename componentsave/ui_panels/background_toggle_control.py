# background_toggle_control.py (Logic Core)
# Real backend toggle state manager

# This module is NOT a GUI. It provides a global toggle interface for other systems.

_toggle_state = True  # Default: backgrounds enabled


def toggle_background():
    """
    Flip the background toggle state (ON <-> OFF)
    """
    global _toggle_state
    _toggle_state = not _toggle_state
    print(f"[Background Toggle] Now: {'ON' if _toggle_state else 'OFF'}")


def set_background_default(state: bool):
    """
    Explicitly set the background toggle state
    """
    global _toggle_state
    _toggle_state = bool(state)
    print(f"[Background Toggle] Default set to: {'ON' if _toggle_state else 'OFF'}")


def get_background_status() -> bool:
    """
    Return current background toggle state
    """
    return _toggle_state
