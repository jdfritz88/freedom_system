import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# ▶ Standalone UI Panel Launcher
# -------------------------------
# Save this as a launcher script to open the control panel

import subprocess

subprocess.run([
    "python",
    "F:\\Apps\\freedom_system\\componentsave\\ui_panels\\ui_control_panel.py"
])
