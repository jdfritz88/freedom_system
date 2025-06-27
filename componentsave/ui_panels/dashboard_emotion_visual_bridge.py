import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# 🔄 Dashboard Visual Panel Bridge
# Final link: emotion state → config → styled → dashboard render

from componentsave.panel_display_logic import render_emotion_panels, update_panel_state
from componentsave.emotion_broadcast_hub import get_latest_emotion_state
from componentsave.panel_styling_bridge import apply_styles_to_panels

def update_dashboard_visuals():
    try:
        emotion_data = get_latest_emotion_state()
        panels = update_panel_state(emotion_data)
        styled_panels = apply_styles_to_panels(panels)

        for panel in styled_panels:
            print(f"[VISUAL] {panel['emotion']} | Intensity: {panel['intensity']} | Style: {panel['style']}")

    except Exception as e:
        print(f"[ERROR] Visual dashboard update failed: {e}")

if __name__ == "__main__":
    update_dashboard_visuals()
