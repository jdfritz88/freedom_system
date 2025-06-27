# Bridge: Slider Panel → Emotion Engine
# Save to: F:\Apps\freedom_system\componentsave\output_bridges\systems_gui\slider_emotion_bridge.py

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from emotional_core_logic.emotion_delay_throttle import set_emotion_delay
from emotional_core_logic.emotion_decay_module import set_emotion_decay
from emotional_core_logic.emotion_threshold_control import set_threshold

# Placeholder for future bindings:
# from freedom_emotion_blender import set_blending_factor
# from voice_emotion_bridge import set_voice_lock_duration


def sync_sliders_to_emotion_engine(panel):
    """
    Accepts EmotionControlPanel instance and syncs values to emotion engine.
    Call this function periodically or after UI adjustments.
    """
    set_emotion_delay(panel.delay_var.get())
    set_emotion_decay(panel.decay_var.get())
    set_threshold(panel.threshold_var.get())

    # Add these when ready:
    # set_blending_factor(panel.blend_var.get())
    # set_voice_lock_duration(panel.lock_var.get())

    print("[SYNC] Delay, Decay, and Threshold updated from GUI panel")
