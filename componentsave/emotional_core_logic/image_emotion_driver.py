# image_emotion_driver.py (Patched for dashboard integration)

from componentsave.ui_panels.dashboard_status_panel import push_status_message
from componentsave.ui_panels.dashboard_alert_strip import push_alert


def push_image_emotion(emotion_name, intensity, framing):
    """
    Handles image generation based on current emotion.
    """
    push_alert("🖼️ Image Generated")
    push_status_message(f"[Image] {emotion_name} @ {intensity:.2f}, framing: {framing}")
    print(f"[Image] Triggered image gen for {emotion_name} (intensity: {intensity}, framing: {framing})")
    # TODO: link to real SDXL image process


def generate_emotion_image(emotion_state):
    if not isinstance(emotion_state, dict):
        push_status_message("[ERROR] Invalid emotion input to image gen")
        return False

    top_emotion = max(emotion_state, key=emotion_state.get)
    intensity = emotion_state[top_emotion]
    framing = "default"

    push_image_emotion(top_emotion, intensity, framing)
    return True
