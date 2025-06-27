import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# 💬 UI Control Panel for Emotion Flow
# -------------------------------------
# Updated: Adds live feedback text to confirm actions

import sys
import os
sys.path.append(os.path.abspath("F:/Apps/freedom_system/componentsave/emotional_core_logic"))

import tkinter as tk
from componentsave.tkinter import ttk
from componentsave.emotion_control_interface import EmotionControlInterface
from componentsave.emotion_system_core import EmotionSystemCore

class EmotionControlPanel(tk.Tk):
    def __init__(self, emotion_system):
        super().__init__()
        self.title("Freedom Emotion Control")
        self.geometry("320x220")
        self.control = EmotionControlInterface(emotion_system)

        self.create_widgets()

    def create_widgets(self):
        ttk.Button(self, text="Pause", command=self.pause_flow).pack(pady=4)
        ttk.Button(self, text="Resume", command=self.resume_flow).pack(pady=4)

        self.emotion_entry = ttk.Entry(self)
        self.emotion_entry.insert(0, "Aroused")
        self.emotion_entry.pack(pady=4)

        self.intensity_entry = ttk.Entry(self)
        self.intensity_entry.insert(0, "0.95")
        self.intensity_entry.pack(pady=4)

        ttk.Button(self, text="Inject", command=self.inject_emotion).pack(pady=4)

        self.feedback_label = ttk.Label(self, text="")
        self.feedback_label.pack(pady=4)

    def pause_flow(self):
        self.control.pause_emotion_flow()
        self.feedback_label.config(text="[Paused] Emotion flow paused")

    def resume_flow(self):
        self.control.resume_emotion_flow()
        self.feedback_label.config(text="[Resumed] Emotion flow resumed")

    def inject_emotion(self):
        emotion = self.emotion_entry.get()
        try:
            intensity = float(self.intensity_entry.get())
            self.control.inject_emotion(emotion, intensity)
            self.feedback_label.config(text=f"[Injected] {emotion} @ {intensity:.2f}")
        except ValueError:
            self.feedback_label.config(text="[Error] Invalid intensity format")

if __name__ == '__main__':
    core = EmotionSystemCore()
    app = EmotionControlPanel(core)
    app.mainloop()
