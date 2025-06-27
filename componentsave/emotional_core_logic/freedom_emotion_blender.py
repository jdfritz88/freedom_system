import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from componentsave.typing import Dict, Tuple

# Emotions are stored with float intensities, e.g., {"Happy": 0.6, "Sad": 0.2}
# Aroused and Curious are dominant; positive emotions win ties

POSITIVE_EMOTIONS = {"Happy", "Loving", "Curious", "Romantic", "Excited", "Calm (Calm (Neutral))"}
DOMINANT_EMOTIONS = {"Aroused", "Curious"}

def blend_emotions(raw_scores: Dict[str, float]) -> Tuple[str, str]:
    """
    Given a dict of emotion scores, returns a tuple of the two dominant emotions
    after applying blend logic.
    """
    if not raw_scores:
        return ("Calm (Calm (Neutral))", "Calm (Calm (Neutral))")

    # Sort by intensity, highest first
    sorted_emotions = sorted(raw_scores.items(), key=lambda x: x[1], reverse=True)

    # Pull top three to examine
    top = sorted_emotions[:3]

    # Filter out emotions below threshold
    top = [(emotion, score) for emotion, score in top if score >= 0.7]
    if not top:
        return ("Calm (Calm (Neutral))", "Calm (Calm (Neutral))")

    # If more than two qualify, apply dominance rules
    dominant = []

    for emotion, score in top:
        if emotion in DOMINANT_EMOTIONS:
            dominant.append((emotion, score))

    if len(dominant) >= 2:
        # Two dominant emotions are strongest
        return (dominant[0][0], dominant[1][0])
    elif dominant:
        # One dominant, pick next strongest
        for e, s in top:
            if e != dominant[0][0]:
                return (dominant[0][0], e)

    # No dominant override, apply positive bias
    pos = [e for e in top if e[0] in POSITIVE_EMOTIONS]
    if len(pos) >= 2:
        return (pos[0][0], pos[1][0])
    elif pos:
        return (pos[0][0], top[0][0] if pos[0][0] != top[0][0] else top[1][0])

    # Fallback: just top 2 by score
    return (top[0][0], top[1][0]) if len(top) >= 2 else (top[0][0], "Calm (Calm (Neutral))")
