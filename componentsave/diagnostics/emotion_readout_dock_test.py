import tkinter as tk
import sys
import os

# Inject path to allow module import from componentsave
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from componentsave.ui_panels.emotion_readout_dock import EmotionReadoutPanel

def rebuild_panel(floating):
    print(f"[UI] Emotion Readout Panel is now {'Floating' if floating else 'Docked'}")
    root.destroy()
    run_gui()

def run_gui():
    global root
    root = tk.Tk()
    root.title("Emotion Readout Panel Test")
    root.geometry("400x200")
    root.lift()
    root.after(50, lambda: root.focus_force())

    panel = EmotionReadoutPanel(root, dock_callback=rebuild_panel)
    if panel.floating:
        panel.panel.lift()
        panel.panel.focus_force()
        panel.panel.after(150, lambda: panel.panel.attributes('-topmost', False))
        panel.panel.mainloop()
    else:
        panel.panel.pack(fill='both', expand=True)
        root.mainloop()

if __name__ == '__main__':
    run_gui()
