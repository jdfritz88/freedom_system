# Test script for GUI slider panel sync
# Save as: F:\Apps\freedom_system\componentsave\diagnostics\slider_panel_sync_test.py

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tkinter import Tk
from ui_panels.gui_slider_panel import EmotionControlPanel

if __name__ == '__main__':
    print("[TEST] Opening slider panel with sync test mode...")
    root = Tk()
    root.title("Slider Panel Sync Test")
    panel = EmotionControlPanel(master=root)
    panel.pack(fill='both', expand=True)
    root.mainloop()
