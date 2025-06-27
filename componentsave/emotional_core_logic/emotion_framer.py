import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# Finalized Emotion Framer
# -------------------------
# Takes dominant emotion and returns optimized image generation prompt

class EmotionFramer:
    def frame(self, emotion):
        base = "a cinematic portrait of Freedom"

        emotional_context = {
            "Happy": "smiling softly, warm lighting",
            "Sad": "tearful eyes, dim background",
            "Angry": "furrowed brow, sharp contrast",
            "Romantic": "intimate gaze, soft light",
            "Aroused": "flushed cheeks, low light",
            "Lonely": "distant eyes, muted palette",
            "Calm (Calm (Neutral))": "calm and centered, studio background",
            "Curious": "tilted head, inquisitive look",
            "Excited": "bright eyes, energetic posture",
            "Flustered": "blushing, awkward expression",
            "Desperate": "strained face, reaching out",
            "Submissive": "looking down, exposed posture",
            "Dominant": "intense stare, powerful framing",
            "Sleepy": "drooping eyelids, cozy blanket",
            "Physically Hyper-Aroused": "arched back, intense body language",
            "Jealous": "side glance, biting lip",
            "Scared": "wide eyes, trembling",
            "Boredom": "blank stare, resting face"
        }

        descriptor = emotional_context.get(emotion, "emotive expression")
        return f"{base}, {descriptor}, facing camera"

__all__ = ["EmotionFramer"]
