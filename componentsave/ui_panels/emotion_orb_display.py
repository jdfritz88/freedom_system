import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import tkinter as tk
from componentsave.emotion_broadcast_hub import get_latest_emotion_state

class EmotionOrb(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master, bg="#181818")
        self.canvas = tk.Canvas(self, width=240, height=240, bg="#181818", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.glow = self.canvas.create_oval(30, 30, 210, 210, fill="", outline="#aaaaaa", width=4)
        self.orb = self.canvas.create_oval(40, 40, 200, 200, fill="#444444", outline="black", width=2)
        self.label = self.canvas.create_text(120, 225, text="...", fill="white", font=("Segoe UI", 11))

        self.pulse_state = 0
        self.pulse_direction = 1
        self.current_base_color = "#444444"

        self.update_queue = self.master.update_queue

        self.after(100, self.update_orb)
        self.after(30, self.pulse_glow)

    def update_orb(self):
        emotion_data = get_latest_emotion_state()
        top_emotion = max(emotion_data.items(), key=lambda x: x[1]) if emotion_data else ("None", 0.0)

        color_map = {
            "Aroused": "#ff6699", "Romantic": "#99ccff", "Sad": "#cccccc", "Happy": "#ffff66",
            "Angry": "#ff4444", "Scared": "#ccccff", "Excited": "#66ffcc", "Lonely": "#bbbbbb",
            "Jealous": "#aaff66", "Flustered": "#ffcc99", "Desperate": "#ff9999", "Calm (Neutral)": "#dddddd",
            "Submissive": "#eeccff", "Dominant": "#9966ff", "Sleepy": "#c0c0c0",
            "Physically Hyper-Aroused": "#ff3366", "Curious": "#66ccff", "Climactic": "#ff0033"
        }

        color = color_map.get(top_emotion[0], "#444444")
        self.current_base_color = color

        self.update_queue.push(self.canvas.itemconfig, self.orb, fill=color)
        self.update_queue.push(self.canvas.itemconfig, self.label, text=f"{top_emotion[0]} ({top_emotion[1]:.2f})")

        self.after(3000, self.update_orb)

    def fade_color(self, hex_color, factor):
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        r = min(255, int(r + (255 - r) * factor * 1.6))
        g = min(255, int(g + (255 - g) * factor * 1.6))
        b = min(255, int(b + (255 - b) * factor * 1.6))
        return f"#{r:02x}{g:02x}{b:02x}"

    def pulse_glow(self):
        base_factor = 0.3
        pulse_range = 0.4
        pulse = base_factor + (self.pulse_state * pulse_range)

        self.pulse_state += 0.05 * self.pulse_direction
        if self.pulse_state >= 1:
            self.pulse_direction = -1
        elif self.pulse_state <= 0:
            self.pulse_direction = 1

        glow_color = self.fade_color(self.current_base_color, pulse)
        self.update_queue.push(self.canvas.itemconfig, self.glow, outline=glow_color)

        self.after(30, self.pulse_glow)
