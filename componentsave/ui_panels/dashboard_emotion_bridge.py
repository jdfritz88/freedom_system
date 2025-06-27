import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# 📦 Dashboard Integration — Emotion Panel Injection Layer
# Location: componentsave/ui_panels/dashboard_emotion_bridge.py

from componentsave.panel_display_logic import render_emotion_panels
from componentsave.emotion_broadcast_hub import get_latest_emotion_state

def update_dashboard_from_emotions():
    try:
        emotion_data = get_latest_emotion_state()
        print("[DASHBOARD] Updating emotion panels with live data...")
        render_emotion_panels(emotion_data)
    except Exception as e:
        print(f"[ERROR] Emotion panel update failed: {e}")

if __name__ == "__main__":
    update_dashboard_from_emotions()
