import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# 🔌 Wire EmotionControlInterface to Runtime
# ------------------------------------------
# Add to EmotionSystemRuntimeBridge in runtime_emotion_output_bridge_test.py

from componentsave.emotion_control_interface import EmotionControlInterface

class EmotionSystemRuntimeBridge:
    def __init__(self):
        self.core = EmotionSystemCore()

        # 💬 Attach UI control interface
        self.control = EmotionControlInterface(self.core)

        # Now accessible:
        # self.control.pause_emotion_flow()
        # self.control.resume_emotion_flow()
        # self.control.inject_emotion("Aroused", 0.95)
