import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import tkinter as tk
from componentsave.emotion_orb_legend_view import EmotionOrbView, EmotionOrbLegend
from componentsave.emotion_panel_container import EmotionPanelContainer
from componentsave.master_emotion_dashboard import MasterEmotionDashboard
from componentsave.queue import Queue
from componentsave.threading import Thread
import random
import time

class UICoreLoader(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Freedom System UI Core")
        self.geometry("420x600")
        self.configure(bg="#111")

        self.update_queue = Queue()
        self.active_frame = None

        # UI Mode buttons
        btn_frame = tk.Frame(self, bg="#111")
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Orb", command=self.load_orb, width=10, bg="#333", fg="white").grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Panels", command=self.load_panels, width=10, bg="#333", fg="white").grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Dashboard", command=self.load_dashboard, width=10, bg="#333", fg="white").grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Legend", command=self.show_legend, width=10, bg="#333", fg="white").grid(row=0, column=3, padx=5)

        # Start fake data simulation
        Thread(target=self.simulate_emotion_updates, daemon=True).start()

    def clear_frame(self):
        if self.active_frame:
            self.active_frame.destroy()
            self.active_frame = None

    def load_orb(self):
        self.clear_frame()
        self.active_frame = EmotionOrbView(self, radius=140)
        self.active_frame.pack(pady=10)

    def load_panels(self):
        self.clear_frame()
        self.active_frame = EmotionPanelContainer(self.update_queue)
        self.active_frame.pack(pady=10, fill='both', expand=True)

    def load_dashboard(self):
        self.clear_frame()
        self.active_frame = MasterEmotionDashboard(self.update_queue)
        self.active_frame.pack(pady=10, fill='both', expand=True)

    def show_legend(self):
        EmotionOrbLegend(self)

    def simulate_emotion_updates(self):
        from emotion_state_catalog import EMOTIONS
        while True:
            emo = random.choice(EMOTIONS)
            val = random.uniform(0.0, 1.0)
            self.update_queue.put((emo, val))
            time.sleep(0.6)


if __name__ == '__main__':
    app = UICoreLoader()
    app.mainloop()
