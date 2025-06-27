# This GUI panel will live inside either master_emotion_dashboard.py or gui_emotion_panels.py
# It exposes override controls for delay tuning and decay configuration with default snap labels, reset button, and callback support.

import tkinter as tk
from tkinter import ttk

class DelayDecayControlPanel(tk.Toplevel):
    def __init__(self, master=None, callback=None):
        super().__init__(master)
        self.title("Delay & Decay Override")
        self.geometry("340x270")
        self.resizable(False, False)

        self.default_delay = 0.3
        self.default_decay = 30.0
        self.callback = callback

        self.delay_var = tk.DoubleVar(value=self.default_delay)
        self.decay_var = tk.DoubleVar(value=self.default_decay)
        self.feedback_var = tk.StringVar(value="")

        self._build_ui()

    def _build_ui(self):
        ttk.Label(self, text="Delay Tuning (seconds)").pack(pady=(10, 0))
        delay_frame = tk.Frame(self)
        delay_frame.pack()
        tk.Scale(delay_frame, from_=0.0, to=2.0, resolution=0.1,
                 variable=self.delay_var, orient="horizontal", length=260).pack(side="left")
        ttk.Label(delay_frame, text=f"Default: {self.default_delay}s").pack(side="right", padx=(10,0))
        ttk.Label(self, textvariable=self.delay_var).pack()

        ttk.Label(self, text="Decay Duration (seconds)").pack(pady=(10, 0))
        decay_frame = tk.Frame(self)
        decay_frame.pack()
        tk.Scale(decay_frame, from_=5.0, to=60.0, resolution=1.0,
                 variable=self.decay_var, orient="horizontal", length=260).pack(side="left")
        ttk.Label(decay_frame, text=f"Default: {self.default_decay}s").pack(side="right", padx=(10,0))
        ttk.Label(self, textvariable=self.decay_var).pack()

        self.feedback_label = ttk.Label(self, textvariable=self.feedback_var, foreground="green")
        self.feedback_label.pack(pady=(5, 0))

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Apply Overrides", command=self._apply).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Reset to Default", command=self._reset_defaults).pack(side="right", padx=5)

    def _apply(self):
        delay_value = round(self.delay_var.get(), 2)
        decay_value = round(self.decay_var.get(), 1)
        print(f"[OVERRIDE] Delay set to {delay_value}s, Decay set to {decay_value}s")
        self.feedback_var.set("✔ Overrides applied!")
        self.after(3000, lambda: self.feedback_var.set(""))
        if self.callback:
            self.callback(delay=delay_value, decay=decay_value)

    def _reset_defaults(self):
        self.delay_var.set(self.default_delay)
        self.decay_var.set(self.default_decay)

# To use:
# panel = DelayDecayControlPanel(callback=your_function_here)
# panel.mainloop()
