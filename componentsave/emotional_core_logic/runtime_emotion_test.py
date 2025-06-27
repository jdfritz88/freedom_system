# File: componentsave/emotional_core_logic/runtime_emotion_test.py

from componentsave.emotional_core_logic.emotion_trigger_handler import handle_emotion_trigger

if __name__ == "__main__":
    print("[START] Emotion System Runtime Test\n")

    test_emotions = [
        ("aroused", 0.8),
        ("sad", 0.5),
        ("romantic", 0.9),
        ("angry", 0.4),
        ("physically hyper-aroused", 1.0)
    ]

    for emotion, intensity in test_emotions:
        print(f"[TEST] Triggering emotion: {emotion} at intensity {intensity}")
        handle_emotion_trigger(emotion, intensity)

    print("\n[COMPLETE] Emotion System Test Finished")
