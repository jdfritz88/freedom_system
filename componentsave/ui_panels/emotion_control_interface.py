import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# 💬 UI Pause / Inject Controls (Backend Logic)
# ---------------------------------------------
# These methods let you pause emotion flow or manually trigger one

class EmotionControlInterface:
    def __init__(self, emotion_system):
        self.emotion_system = emotion_system
        self.paused = False

    def pause_emotion_flow(self):
        self.paused = True
        print("[CONTROL] Emotion flow paused.")

    def resume_emotion_flow(self):
        self.paused = False
        print("[CONTROL] Emotion flow resumed.")

    def inject_emotion(self, emotion, intensity):
        if not self.paused:
            self.emotion_system.emotion_queue.put((emotion, intensity))
            print(f"[CONTROL] Injected {emotion} @ {intensity:.2f}")
        else:
            print("[CONTROL] Cannot inject — flow is paused.")

__all__ = ["EmotionControlInterface"]
