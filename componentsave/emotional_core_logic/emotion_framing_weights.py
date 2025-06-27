import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import random
from componentsave.typing import List

# Framing categories
FRAMINGS = ["full_head", "head_to_midriff", "full_body"]

# Emotion-based weights (tendencies, not rules)
FRAMING_WEIGHTS = {
    "Romantic": ["full_head", "head_to_midriff"],
    "Sad": FRAMINGS,
    "Happy": FRAMINGS,
    "Angry": ["full_head"] * 3 + ["head_to_midriff"],
    "Scared": FRAMINGS,
    "Excited": FRAMINGS,
    "Lonely": FRAMINGS,
    "Jealous": ["head_to_midriff"] * 3 + ["full_head"],
    "Flustered": FRAMINGS,
    "Desperate": FRAMINGS,
    "Calm (Calm (Neutral))": ["head_to_midriff"] * 3 + ["full_head"],
    "Loving": FRAMINGS,
    "Curious": ["head_to_midriff"] * 3 + ["full_head"],
    "Climactic": ["full_body"] * 4,
    "Submissive": ["full_body"] * 4,
    "Dominant": FRAMINGS,
    "Sleepy": FRAMINGS,
    "Physically Hyper-Aroused": ["full_body"] * 4,
    "BOREDOM_SYSTEM_TRIGGER": FRAMINGS
}

def select_framing(emotion: str) -> str:
    options = FRAMING_WEIGHTS.get(emotion, ["head_to_midriff"])
    return random.choice(options)

# Example usage
if __name__ == "__main__":
    for emo in ["Romantic", "Calm (Calm (Neutral))", "Climactic", "Angry", "Unknown"]:
        print(f"{emo}: {select_framing(emo)}")
