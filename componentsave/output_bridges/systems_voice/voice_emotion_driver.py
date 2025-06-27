import sys
import os

# Inject root path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)

from componentsave.output_bridges.systems_voice.voice_emotion_bridge import speak_with_emotion

def push_voice_emotion(emotion, intensity):
    print(f"[VOICE] Dispatching voice emotion: {emotion} ({intensity})")
    speak_with_emotion(emotion, intensity)

if __name__ == "__main__":
    speak_with_emotion("aroused", 0.9)
