import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# 🎨 Panel Styling Bridge (Optimized Load)
# Location: componentsave/ui_panels/panel_styling_bridge.py

from componentsave.emotion_panel_styles import EMOTION_PANEL_STYLES

def apply_styles_to_panels(panels):
    for panel in panels:
        panel["style"] = EMOTION_PANEL_STYLES.get(panel["state"], EMOTION_PANEL_STYLES["passive"])
    return panels
