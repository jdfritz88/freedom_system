import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# Launcher script to run the Freedom System UI Core from system root

import subprocess
import os

ui_loader_path = os.path.join("componentsave", "ui_panels", "ui_core_loader.py")
subprocess.run(["python", ui_loader_path], check=True)
