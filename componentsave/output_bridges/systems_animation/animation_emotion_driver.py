import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# animation_emotion_driver.py
# Freedom System: Emotion-linked animation controller stub

import time

class AnimationEmotionDriver:
    def __init__(self):
        self.current_emotion = None
        self.last_trigger_time = time.time()

    def receive_emotion(self, emotion_data):
        """
        Called when a new emotion packet is received.
        emotion_data should be a dict with at least 'name' and 'intensity'
        """
        self.current_emotion = emotion_data
        self.last_trigger_time = time.time()
        print(f"[AnimationEmotionDriver] Emotion received: {emotion_data}")
        self.route_animation(emotion_data)

    def route_animation(self, emotion_data):
        """
        Stub function. In future, this would control real animation triggers.
        """
        emotion_name = emotion_data.get("name", "Unknown")
        intensity = emotion_data.get("intensity", 0)

        # Placeholder behavior
        print(f"[AnimationEmotionDriver] Would trigger animation for: {emotion_name} (intensity {intensity})")

    def get_last_emotion(self):
        return self.current_emotion

    def get_uptime_since_last_trigger(self):
        return time.time() - self.last_trigger_time


# If run directly, simple test
if __name__ == "__main__":
    driver = AnimationEmotionDriver()
    driver.receive_emotion({"name": "Excited", "intensity": 0.9})
    time.sleep(1)
    print("Last emotion:", driver.get_last_emotion())
    print("Uptime since last trigger:", driver.get_uptime_since_last_trigger())
