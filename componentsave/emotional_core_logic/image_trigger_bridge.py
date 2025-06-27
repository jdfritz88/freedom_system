import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# 🔗 Image Trigger Bridge
# Connects emotion scores to image generation logic

import time
from componentsave.emotion_broadcast_hub import get_latest_emotion_state
from componentsave.image_trigger_tuning import should_trigger_image

# Track last image trigger time
last_image_trigger = 0

def evaluate_image_trigger():
    global last_image_trigger
    emotion_data = get_latest_emotion_state()
    current_time = int(time.time())

    if should_trigger_image(emotion_data, last_image_trigger, current_time):
        last_image_trigger = current_time
        print("[TRIGGER] Image generation triggered.")
        return True
    else:
        print("[SKIP] No image trigger this cycle.")
        return False

if __name__ == "__main__":
    evaluate_image_trigger()
