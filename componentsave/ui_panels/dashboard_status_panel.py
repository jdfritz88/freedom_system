# dashboard_status_panel.py (Backend Only)
# Manages real-time status messages from the system

from collections import deque

_status_log = deque(maxlen=10)  # ring buffer to keep last 10 messages


def push_status_message(msg: str):
    """
    Add a message to the system status panel log
    """
    _status_log.append(msg)
    print(f"[STATUS] {msg}")


def get_recent_status_log() -> list:
    """
    Return a copy of the recent status log
    """
    return list(_status_log)


def clear_status_log():
    """
    Wipe the log clean
    """
    _status_log.clear()
    print("[STATUS] Log cleared")
