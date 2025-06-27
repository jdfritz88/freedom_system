import tkinter as tk
import sys
import os

# Setup import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui_panels.gui_emotion_tag_overlay import EmotionTagOverlay

if __name__ == "__main__":
    print("[TEST] Launching Emotion Tag Overlay...")

    root = tk.Tk()
    root.title("Emotion Tag Overlay Test")
    root.geometry("300x120")

    tag = EmotionTagOverlay(root)
    tag.pack(fill="both", expand=True, padx=10, pady=10)

    root.mainloop()
