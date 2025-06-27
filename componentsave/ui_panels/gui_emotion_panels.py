# gui_emotion_panels.py (backend logic only – no GUI)
# Emotion threshold + resolution control functions

_threshold = 0.7  # default value
_resolution = "512x512"  # default mode
_modes = ["384x384", "512x512", "768x512", "512x768"]


def set_emotion_threshold(value: float):
    global _threshold
    _threshold = max(0.0, min(1.0, value))
    print(f"[Threshold] Set to {_threshold:.2f}")


def get_emotion_threshold() -> float:
    return _threshold


def apply_threshold_override(tag: str, value: float):
    # Stubbed logic: override can be tracked per tag later
    set_emotion_threshold(value)
    print(f"[Threshold Override] Tag: {tag}, Value: {value}")


def set_default_resolution(mode: str):
    global _resolution
    if mode in _modes:
        _resolution = mode
        print(f"[Resolution] Set to {_resolution}")
    else:
        print(f"[Resolution] Invalid mode: {mode}")


def get_current_resolution() -> str:
    return _resolution


def toggle_resolution_mode():
    global _resolution
    idx = _modes.index(_resolution)
    _resolution = _modes[(idx + 1) % len(_modes)]
    print(f"[Resolution] Toggled to {_resolution}")
