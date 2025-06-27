# Add logging support to slider sync bridge
# Save to: F:\Apps\freedom_system\componentsave\output_bridges\systems_gui\slider_emotion_bridge.py

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from emotional_core_logic.emotion_delay_throttle import set_emotion_delay
from emotional_core_logic.emotion_decay_module import set_emotion_decay
from emotional_core_logic.emotion_threshold_control import set_threshold
from emotional_core_logic.freedom_emotion_blender import set_blending_factor
from output_bridges.systems_voice.voice_emotion_bridge import set_voice_lock_duration

from data_logging.sync_log_writer import log_slider_sync


def sync_sliders_to_emotion_engine(panel):
    delay = panel.delay_var.get()
    decay = panel.decay_var.get()
    threshold = panel.threshold_var.get()
    blend = panel.blend_var.get()
    lock = panel.lock_var.get()

    set_emotion_delay(delay)
    set_emotion_decay(decay)
    set_threshold(threshold)
    set_blending_factor(blend)
    set_voice_lock_duration(lock)

    print("[SYNC] All sliders updated → Delay, Decay, Threshold, Blend, Lock Time")
    log_slider_sync(delay, decay, threshold, blend, lock)
