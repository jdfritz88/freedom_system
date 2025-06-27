# dashboard_emotion_feed.py
# Keeps a rolling log of triggered emotions

from collections import deque

_emotion_feed = deque(maxlen=20)


def push_emotion_event(emotion: str, intensity: float):
    entry = f"{emotion.title()} ({intensity:.2f})"
    _emotion_feed.append(entry)
    print(f"[EMOTION FEED] + {entry}")


def get_emotion_feed() -> list:
    return list(_emotion_feed)


def clear_emotion_feed():
    _emotion_feed.clear()
    print("[EMOTION FEED] Cleared")
