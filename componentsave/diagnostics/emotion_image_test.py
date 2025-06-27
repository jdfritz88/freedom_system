import sys
import os
import time

# Ensure root path is in sys.path
ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT_PATH not in sys.path:
    sys.path.insert(0, ROOT_PATH)

from componentsave.emotional_core_logic.emotion_image_generator import EmotionImageGenerator
from componentsave.emotional_core_logic.emotion_queue import push_to_emotion_queue, get_emotion_queue

# Initialize the image generator
image_generator = EmotionImageGenerator()

def test_emotion_triggered_image_system():
    test_emotions = [
        {"emotion": "aroused", "intensity": 0.9},
        {"emotion": "sad", "intensity": 0.5},
        {"emotion": "romantic", "intensity": 0.95},
        {"emotion": "angry", "intensity": 0.7},
        {"emotion": "physically_hyper_aroused", "intensity": 1.0},
    ]

    print("[TEST] Starting emotion-triggered image generation system test")

    for item in test_emotions:
        emotion = item["emotion"]
        intensity = item["intensity"]
        print(f"[QUEUE] Adding to queue: {emotion} ({intensity})")
        push_to_emotion_queue(emotion, intensity)
        time.sleep(0.5)  # Simulate natural pacing

    print("[PROCESSING] Dispatching emotions to image generator...")
    for emotion, intensity in get_emotion_queue():
        print(f"[GENERATING] Triggered image for: {emotion} at intensity {intensity}")
        image_generator.generate(emotion, intensity)
        time.sleep(1.0)  # Simulate image generation time

    print("[COMPLETE] Emotion-triggered image generation test finished")


if __name__ == "__main__":
    test_emotion_triggered_image_system()
