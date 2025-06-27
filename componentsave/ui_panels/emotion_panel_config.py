import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# Emotion Panel Setup (Restored with update_panel_state)
# Location: componentsave/ui_panels/emotion_panel_config.py

EMOTION_PANEL_CONFIG = {
    "Aroused":        {"preview": 0.7, "priority": 10, "state": "dominant"},
    "Romantic":       {"preview": 0.6, "priority": 9,  "state": "active"},
    "Sad":            {"preview": 0.5, "priority": 7,  "state": "passive"},
    "Lonely":         {"preview": 0.5, "priority": 6,  "state": "passive"},
    "Happy":          {"preview": 0.6, "priority": 8,  "state": "active"},
    "Angry":          {"preview": 0.5, "priority": 5,  "state": "passive"},
    "Curious":        {"preview": 0.6, "priority": 9,  "state": "active"},
    "Excited":        {"preview": 0.6, "priority": 8,  "state": "active"},
    "Jealous":        {"preview": 0.4, "priority": 4,  "state": "passive"},
    "Flustered":      {"preview": 0.5, "priority": 6,  "state": "passive"},
    "Desperate":      {"preview": 0.5, "priority": 7,  "state": "passive"},
    "Calm (Neutral)":        {"preview": 0.3, "priority": 3,  "state": "fading"},
    "Submissive":     {"preview": 0.5, "priority": 6,  "state": "passive"},
    "Dominant":       {"preview": 0.6, "priority": 8,  "state": "active"},
    "Sleepy":         {"preview": 0.3, "priority": 2,  "state": "fading"},
    "Physically Hyper-Aroused": {"preview": 0.8, "priority": 10, "state": "dominant"}
}

def update_panel_state(current_emotions):
    """
    Given a dict of current emotions and their intensities,
    this updates each panel’s visual state based on the config.
    """
    display_panels = []

    for emotion, intensity in current_emotions.items():
        if emotion in EMOTION_PANEL_CONFIG:
            config = EMOTION_PANEL_CONFIG[emotion]
            display_panels.append({
                "emotion": emotion,
                "intensity": intensity,
                "preview": config["preview"],
                "priority": config["priority"],
                "state": config["state"]
            })

    # Sort panels by priority, highest first
    display_panels.sort(key=lambda x: x["priority"], reverse=True)

    return display_panels

print("[SETUP] Emotion panel configuration restored and active.")
