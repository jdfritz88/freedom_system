import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# 🖼️ GUI Shell Launcher — Emotion Panel Dock (Optimized)
# Location: componentsave/ui_panels/gui_shell_launcher.py

import tkinter as tk
from componentsave.panel_display_logic import update_panel_state
from componentsave.panel_styling_bridge import apply_styles_to_panels
from componentsave.emotion_broadcast_hub import get_latest_emotion_state

class EmotionPanelApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Freedom Emotion Panels")
        self.configure(bg="#f0f0f0")
        self.after(100, self.refresh_ui)

    def refresh_ui(self):
        for widget in self.winfo_children():
            widget.destroy()

        emotion_data = get_latest_emotion_state()
        panels = update_panel_state(emotion_data)
        styled_panels = apply_styles_to_panels(panels)

        panel_frames = []
        for panel in styled_panels:
            style = panel["style"]
            frame = tk.Frame(self, bd=2, relief=tk.SOLID, bg=style["background"])
            frame.pack(padx=10, pady=5, anchor="w")
            label = tk.Label(
                frame,
                text=f"{panel['emotion']} (Intensity: {panel['intensity']})",
                bg=style["background"],
                fg="black",
                font=("Arial", 12, style["font_weight"]),
                wraplength=500,
                justify="left"
            )
            label.pack(padx=5, pady=5, anchor="w")
            panel_frames.append(frame)

        self.update_idletasks()
        total_height = sum(f.winfo_height() for f in panel_frames) + 50
        max_width = max((f.winfo_width() for f in panel_frames), default=300) + 40
        self.geometry(f"{max_width}x{total_height}")
        self.after(5000, self.refresh_ui)

if __name__ == "__main__":
    app = EmotionPanelApp()
    app.mainloop()
