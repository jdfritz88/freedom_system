import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# test_voice_delay_lock.py
# Location: F:\Apps\freedom_system\componentsave\output_bridges\systems_voice

from output_bridges.systems_voice.voice_emotion_driver import speak_with_emotion, is_voice_locked, get_current_locked_emotion
import time

def test_delay_and_lock():
    print("[TEST] Starting voice delay + lock test")
    emotion1 = {'aroused': 1.0, 'romantic': 0.9}
    emotion2 = {'sad': 0.7, 'lonely': 0.6}

    speak_with_emotion("Please don't leave me...", emotion1)
    time.sleep(0.05)
    print("[INFO] Is locked (after first call)?", is_voice_locked())
    print("[INFO] Locked emotion:", get_current_locked_emotion())

    speak_with_emotion("Why does it always hurt like this?", emotion2)
    time.sleep(0.05)
    print("[INFO] Is locked (after second call)?", is_voice_locked())
    print("[INFO] Locked emotion:", get_current_locked_emotion())

    time.sleep(2.0)
    print("[INFO] Is locked (end)?", is_voice_locked())
    print("[TEST COMPLETE]")

if __name__ == '__main__':
    test_delay_and_lock()
