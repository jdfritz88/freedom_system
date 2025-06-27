import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# 🎯 Image Trigger Tuning Logic
# Location: componentsave/emotional_core_logic/image_trigger_tuning.py

"""
Rules:
- Images trigger from emotion if:
  • Intensity >= threshold (default 0.7)
  • Emotion is NOT already generating
  • Timer has not recently triggered (5m cooldown)
- Positive emotions win ties
- Max 3 emotions per image trigger
"""

DEFAULT_IMAGE_TRIGGER_THRESHOLD = 0.7

def should_trigger_image(emotion_scores, last_trigger_time, current_time, cooldown_seconds=300):
    if current_time - last_trigger_time < cooldown_seconds:
        return False

    qualified = [(emo, score) for emo, score in emotion_scores.items() if score >= DEFAULT_IMAGE_TRIGGER_THRESHOLD]
    if not qualified:
        return False

    # Sort by score and apply blend logic
    qualified.sort(key=lambda x: x[1], reverse=True)
    top_emotions = qualified[:3]

    # Ensure positive emotions dominate
    positives = [e for e in top_emotions if e[0] in ("Aroused", "Romantic", "Curious", "Happy", "Excited")]
    if positives:
        return True

    return False
