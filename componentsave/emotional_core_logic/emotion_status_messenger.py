import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# emotion_status_messenger.py

import time
from emotional_core_logic.freedom_emotion_blender import get_current_emotion_blend


def display_emotion_status():
    print("[EmotionStatus] Live emotional status messaging started.")
    while True:
        blend = get_current_emotion_blend()

        if not blend:
            print("[EmotionStatus] No active emotion.")
        else:
            # Sort by intensity
            sorted_emotions = sorted(blend.items(), key=lambda x: x[1], reverse=True)

            # Display top one or two
            if len(sorted_emotions) == 1:
                e1, v1 = sorted_emotions[0]
                print(f"[EmotionStatus] Dominant emotion: {e1} ({v1:.2f})")
            else:
                (e1, v1), (e2, v2) = sorted_emotions[:2]
                print(f"[EmotionStatus] Dominant: {e1} ({v1:.2f}), Blended with: {e2} ({v2:.2f})")

        time.sleep(1)


if __name__ == "__main__":
    try:
        display_emotion_status()
    except KeyboardInterrupt:
        print("[EmotionStatus] Messaging halted by user.")
