# File: componentsave/emotional_core_logic/emotion_trigger_handler.py

from typing import Dict, Callable
from componentsave.emotional_core_logic.emotion_queue import push_to_emotion_queue

emotion_callbacks: Dict[str, Callable[[float], None]] = {}


def register_emotion_callback(emotion: str, callback: Callable[[float], None]):
    emotion_callbacks[emotion.lower()] = callback


def handle_emotion_trigger(emotion: str, intensity: float):
    print(f"[HANDLER] Emotion: {emotion}, Intensity: {intensity}")
    push_to_emotion_queue(emotion.lower(), intensity)

    if emotion.lower() in emotion_callbacks:
        print(f"[CALLBACK] Triggering registered callback for {emotion}")
        emotion_callbacks[emotion.lower()](intensity)
    else:
        print(f"[CALLBACK] No registered callback for {emotion}")
