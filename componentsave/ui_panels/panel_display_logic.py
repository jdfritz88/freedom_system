import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# ⚙️ Panel Display Logic (Optimized Refresh)
# Location: componentsave/ui_panels/panel_display_logic.py

def update_panel_state(emotion_data):
    """Generate panel objects from emotion scores with thresholds."""
    sorted_emotions = sorted(emotion_data.items(), key=lambda x: x[1], reverse=True)
    dominant = sorted_emotions[0] if sorted_emotions else (None, 0.0)

    panels = []
    for emotion, intensity in sorted_emotions:
        state = "passive"
        if emotion == dominant[0]:
            state = "dominant"
        elif intensity >= 0.7:
            state = "active"
        elif intensity < 0.2:
            state = "fading"

        panels.append({
            "emotion": emotion,
            "intensity": round(intensity, 2),
            "state": state
        })

    return panels
