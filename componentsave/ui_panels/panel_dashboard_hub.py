import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# 📊 Master Emotion Dashboard Hub
# Location: componentsave/ui_panels/panel_dashboard_hub.py

from componentsave.gui_shell_launcher import EmotionPanelApp

if __name__ == "__main__":
    print("[DASHBOARD] Launching master emotion panel dashboard...")
    EmotionPanelApp().mainloop()
