import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# 🎨 Emotion Panel Visual Styles (Initial Definitions)
# Location: componentsave/ui_panels/emotion_panel_styles.py

EMOTION_PANEL_STYLES = {
    "dominant": {
        "border": "3px solid #FF3366",
        "background": "linear-gradient(to bottom, #ffe6eb, #ffccd5)",
        "font_weight": "bold",
        "pulse": True
    },
    "active": {
        "border": "2px solid #6699FF",
        "background": "linear-gradient(to bottom, #e6f0ff, #cce0ff)",
        "font_weight": "normal",
        "pulse": False
    },
    "passive": {
        "border": "1px dashed #999999",
        "background": "#f2f2f2",
        "font_weight": "lighter",
        "pulse": False
    },
    "fading": {
        "border": "1px dotted #cccccc",
        "background": "#fafafa",
        "font_weight": "lighter",
        "pulse": False
    }
}

print("[STYLE] Emotion panel visual styles initialized.")
