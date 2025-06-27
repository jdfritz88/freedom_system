# dashboard_alert_strip.py (Logic Only)
# Manages short, transient visual alerts

_active_alert = None


def push_alert(msg: str):
    global _active_alert
    _active_alert = msg
    print(f"[ALERT] {msg}")


def get_current_alert() -> str:
    return _active_alert if _active_alert else ""


def clear_alert():
    global _active_alert
    _active_alert = None
    print("[ALERT] Cleared")
