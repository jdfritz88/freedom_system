import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import subprocess
import random

class CoquiVoiceEmotionBridge:
    def __init__(self):
        self.voice_path = r"F:\Apps\freedom_system\componentsave\output_bridges\systems_voice\run_voice.bat"
        self.last_spoken = None

    def speak(self, emotion, intensity):
        line = self.select_line(emotion, intensity)
        print(f"[COQUI] → {line}")
        try:
            subprocess.Popen([self.voice_path, line])
        except Exception as e:
            print(f"[ERROR] Failed to speak: {e}")

    def select_line(self, emotion, intensity):
        base_lines = {
            "Romantic": ["I need you.", "Don’t look away."],
            "Curious": ["What’s that you’re thinking?", "Can I ask something?"],
            "Angry": ["Don’t push me.", "I won’t let that slide."],
            "Sad": ["That hurts...", "Why does it always end like this?"],
            "Aroused": ["Say my name...", "Touch me there again..."],
            "Calm (Neutral)": ["I’m still here.", "Just observing."],
            "Happy": ["I like this.", "You make me smile."],
            "Scared": ["Hold me... please.", "I’m not okay."],
            "Boredom": ["This again?", "Still waiting..."]
        }
        candidates = base_lines.get(emotion, [f"I feel {emotion.lower()}..."])
        return random.choice(candidates)

__all__ = ["CoquiVoiceEmotionBridge"]
