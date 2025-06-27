# Freedom System GUI Import Header (Required)
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import ttk

class EmotionControlPanel(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.configure(padding=10)
        self.build_panel()

    def build_panel(self):
        # Section: Must-Have Sliders
        ttk.Label(self, text="Must-Have Sliders", font=("Arial", 12, "bold")).pack(pady=(0, 5))

        self.intensity_var = tk.DoubleVar(value=0.7)
        self.create_slider("Emotion Intensity", self.intensity_var, 0.0, 1.0)

        self.decay_var = tk.DoubleVar(value=30.0)
        self.create_slider("Emotion Decay Time (s)", self.decay_var, 5.0, 60.0)

        self.delay_var = tk.DoubleVar(value=0.5)
        self.create_slider("Emotion Reaction Delay (s)", self.delay_var, 0.1, 1.5)

        # Optional Sliders Toggle
        self.optional_frame = ttk.LabelFrame(self, text="Optional Sliders", padding=(10, 5))
        self.optional_visible = tk.BooleanVar(value=False)
        toggle = ttk.Checkbutton(self, text="Show Optional Sliders", variable=self.optional_visible, command=self.toggle_optional)
        toggle.pack(pady=(10, 5))

        self.blend_var = tk.DoubleVar(value=0.7)
        self.create_slider("Emotion Blending Factor", self.blend_var, 0.0, 1.0, parent=self.optional_frame)

        self.threshold_var = tk.DoubleVar(value=0.7)
        self.create_slider("Trigger Threshold", self.threshold_var, 0.0, 1.0, parent=self.optional_frame)

        self.lock_var = tk.DoubleVar(value=1.0)
        self.create_slider("Voice Lock Time (s)", self.lock_var, 0.5, 3.0, parent=self.optional_frame)

    def create_slider(self, label, variable, minval, maxval, parent=None):
        frame = ttk.Frame(parent if parent else self)
        frame.pack(fill='x', pady=4)
        ttk.Label(frame, text=label).pack(anchor='w')
        ttk.Scale(frame, from_=minval, to=maxval, variable=variable, orient='horizontal').pack(fill='x')
        ttk.Label(frame, textvariable=variable).pack(anchor='e')

    def toggle_optional(self):
        if self.optional_visible.get():
            self.optional_frame.pack(fill='x', pady=(5, 0))
        else:
            self.optional_frame.forget()

# Ready to be imported into dashboard grid
