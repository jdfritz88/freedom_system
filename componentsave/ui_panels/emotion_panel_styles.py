import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# 🎨 Emotion Panel Visual Styles (Final Visual Spec)
# Location: componentsave/ui_panels/emotion_panel_styles.py

EMOTION_PANEL_STYLES = {
    "dominant": {
        "border": "3px solid #FF3366",
        "background": "#ffe6eb",
        "font_weight": "bold",
        "pulse": True
    },
    "active": {
        "border": "2px solid #6699FF",
        "background": "#e6f0ff",
        "font_weight": "normal",
        "pulse": False
    },
    "passive": {
        "border": "2px solid #555555",
        "background": "#f2f2f2",
        "font_weight": "normal",
        "pulse": False
    },
    "fading": {
        "border": "2px solid #aaaaaa",
        "background": "#f8f8f8",
        "font_weight": "normal",
        "pulse": False
    }
}

print("[STYLE] Emotion panel visual styles updated for consistency.")
