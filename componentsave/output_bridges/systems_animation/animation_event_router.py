import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# animation_event_router.py
# Freedom System: Routes emotion events to animation logic modules

class AnimationEventRouter:
    def __init__(self):
        self.driver = None

    def connect_driver(self, animation_driver):
        """
        Attach an animation driver instance (e.g., AnimationEmotionDriver)
        """
        self.driver = animation_driver
        print("[AnimationEventRouter] Animation driver connected.")

    def forward_emotion(self, emotion_packet):
        """
        Passes the emotion data to the connected animation driver.
        """
        if not self.driver:
            print("[AnimationEventRouter] No animation driver connected.")
            return

        print(f"[AnimationEventRouter] Forwarding emotion: {emotion_packet}")
        self.driver.receive_emotion(emotion_packet)


# Test mode
if __name__ == "__main__":
    from animation_emotion_driver import AnimationEmotionDriver

    router = AnimationEventRouter()
    driver = AnimationEmotionDriver()
    router.connect_driver(driver)

    test_emotion = {"name": "Flustered", "intensity": 0.75}
    router.forward_emotion(test_emotion)
