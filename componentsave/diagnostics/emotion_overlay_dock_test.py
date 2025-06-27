import tkinter as tk
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from componentsave.ui_panels.emotion_overlay_dock import EmotionOverlayPanel

def rebuild_panel(floating):
    print(f"[UI] Emotion Orb Overlay is now {'Floating' if floating else 'Docked'}")
    root.destroy()
    run_gui()

def run_gui():
    global root
    root = tk.Tk()
    root.title("Emotion Orb Overlay Test")
    root.geometry("400x200")

    panel = EmotionOverlayPanel(root, dock_callback=rebuild_panel)
    if panel.floating:
        panel.panel.lift()
        panel.panel.attributes('-topmost', True)
        panel.panel.after(200, lambda: panel.panel.attributes('-topmost', False))
        panel.panel.mainloop()
    else:
        panel.panel.pack(fill='both', expand=True)
        root.mainloop()

if __name__ == '__main__':
    run_gui()
