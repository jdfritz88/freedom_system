# music_emotion_driver.py
# Applies emotional response logic to music (internal state only)
import time
import threading

# Global emotion lock and cooldown
_last_trigger_time = 0
_delay_seconds = 1.5
_decay_seconds = 30
_emotion_lock = threading.Lock()
_current_emotion_state = {}

def handle_music_emotion(emotion_data):
    """
    Handles internal music reaction logic based on emotional input.
    Uses top-2 emotion blending with positive bias.
    Includes delay throttle and emotion decay timer.
    This module does NOT trigger music output.
    """
    global _last_trigger_time, _current_emotion_state

    if not isinstance(emotion_data, dict):
        print("[MUSIC DRIVER] Invalid emotion data format.")
        return

    now = time.time()
    if now - _last_trigger_time < _delay_seconds:
        print("[MUSIC DRIVER] Skipped: Throttle delay not met.")
        return

    _last_trigger_time = now
    with _emotion_lock:
        _current_emotion_state = emotion_data.copy()

    # Sort emotions by intensity
    sorted_emotions = sorted(emotion_data.items(), key=lambda x: x[1], reverse=True)
    top_two = sorted_emotions[:2]

    dominant_emotion, intensity = top_two[0]
    print(f"[MUSIC DRIVER] Dominant: {dominant_emotion} ({intensity})")

    if len(top_two) > 1:
        second_emotion, second_intensity = top_two[1]
        print(f"[MUSIC DRIVER] Secondary: {second_emotion} ({second_intensity})")

    print("[MUSIC DRIVER] Reaction logic executed (internal only).")

    # Launch decay thread
    threading.Thread(target=_decay_emotion_state, daemon=True).start()

def _decay_emotion_state():
    global _current_emotion_state
    time.sleep(_decay_seconds)
    with _emotion_lock:
        _current_emotion_state.clear()
    print("[MUSIC DRIVER] Emotion state decayed to neutral.")
