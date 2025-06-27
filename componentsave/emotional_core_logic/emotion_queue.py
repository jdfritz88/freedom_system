# File: componentsave/emotional_core_logic/emotion_queue.py

from componentsave.output_bridges.systems_voice.voice_emotion_driver import push_voice_emotion

emotion_queue = []

def push_to_emotion_queue(emotion, intensity):
    emotion_queue.append((emotion, intensity))
    print(f"[QUEUE] Added: {emotion} ({intensity})")
    push_voice_emotion(emotion, intensity)

def get_emotion_queue():
    return list(emotion_queue)
