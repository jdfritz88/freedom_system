import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# File: emotion_trigger_validator.py
# Location: F:/Apps/freedom_system/componentsave/emotional_core_logic

def is_valid_emotion_trigger(emotion_name, intensity, threshold):
    """
    Returns True if the emotion trigger passes basic validation:
    - Trigger intensity must exceed the threshold
    - Emotion name must not be None or empty
    """
    if not emotion_name or not isinstance(emotion_name, str):
        return False

    try:
        intensity_val = float(intensity)
    except (ValueError, TypeError):
        return False

    return intensity_val >= threshold
