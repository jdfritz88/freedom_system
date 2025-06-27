# Save location: F:/Apps/freedom_system/componentsave/diagnostics/gui_override_panel_test.py

import sys
import os
import tkinter as tk

# Make sure we can import sibling modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui_panels.gui_override_panel import DelayDecayControlPanel

# When Apply is clicked, this gets called

def handle_override(delay, decay):
    print("[MESSAGE] Panel returned:")
    print(" - Delay:", delay)
    print(" - Decay:", decay)

if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    panel = DelayDecayControlPanel(callback=handle_override)
    print("[TEST] Override panel is running. Look for ✔ feedback and console output.")
    panel.mainloop()