import tkinter as tk
from tkinter import ttk
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from componentsave.ui_panels.emotion_readout_dock import EmotionReadoutPanel
from componentsave.ui_panels.emotion_overlay_dock import EmotionOverlayPanel

class DashboardWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Freedom Emotion Dashboard")
        self.root.geometry("600x400")

        self.readout = EmotionReadoutPanel(root, dock_callback=self.rebuild_readout)
        self.overlay = EmotionOverlayPanel(root, dock_callback=self.rebuild_overlay)

        # Only pack docked panels
        if not self.readout.floating:
            self.readout.panel.pack(side="left", fill="both", expand=True)
        if not self.overlay.floating:
            self.overlay.panel.pack(side="right", fill="both", expand=True)

    def rebuild_readout(self, floating):
        self.root.destroy()
        main()

    def rebuild_overlay(self, floating):
        self.root.destroy()
        main()

def main():
    root = tk.Tk()
    app = DashboardWindow(root)
    root.mainloop()

if __name__ == '__main__':
    main()
