# emotion_broadcast_hub.py (Patched for dashboard wiring)

from componentsave.ui_panels.dashboard_status_panel import push_status_message
from componentsave.ui_panels.dashboard_emotion_feed import push_emotion_event


def broadcast_emotion_status(emotion_data):
    """
    Distribute emotion state updates system-wide.
    Also pushes to dashboard feed and status panel.
    """
    try:
        push_status_message(f"Emotions Updated: {emotion_data}")

        # Push top emotion to feed
        if isinstance(emotion_data, dict) and emotion_data:
            top = max(emotion_data, key=emotion_data.get)
            push_emotion_event(top, emotion_data[top])

    except Exception as e:
        push_status_message(f"[ERROR] Broadcast failed: {e}")
