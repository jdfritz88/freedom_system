import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import tkinter as tk
from componentsave.tkinter import ttk
from componentsave.emotion_panel_modules import EmotionPanel
from componentsave.threading import Thread
from componentsave.queue import Queue

class EmotionPanelContainer(tk.Tk):
    def __init__(self, update_queue):
        super().__init__()
        self.title("Emotion Panel Grid")
        self.geometry("340x540")
        self.configure(bg="#1e1e1e")

        self.update_queue = update_queue
        self.canvas = tk.Canvas(self, borderwidth=0, bg="#1e1e1e")
        self.frame = tk.Frame(self.canvas, bg="#1e1e1e")
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

        self.frame.bind("<Configure>", self.on_frame_configure)

        self.emotions = ["Happy", "Sad", "Angry", "Romantic", "Aroused", "Lonely", "Calm (Neutral)",
                         "Scared", "Flustered", "Desperate", "Submissive", "Dominant",
                         "Jealous", "Excited", "Curious", "Sleepy", "Calm (Neutral)", "Physically Hyper-Aroused"]

        self.panels = []
        for emo in self.emotions:
            panel = EmotionPanel(self.frame, emo, self.update_queue)
            panel.pack(pady=4, padx=8, fill='x')
            self.panels.append(panel)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


def emotion_panel_container_simulator(update_queue):
    import random, time
    emotions = ["Happy", "Sad", "Angry", "Romantic", "Aroused", "Lonely", "Calm (Neutral)",
                "Scared", "Flustered", "Desperate", "Submissive", "Dominant",
                "Jealous", "Excited", "Curious", "Sleepy", "Calm (Neutral)", "Physically Hyper-Aroused"]
    while True:
        time.sleep(0.5)
        emo = random.choice(emotions)
        val = random.uniform(0.0, 1.0)
        update_queue.put((emo, val))


if __name__ == '__main__':
    q = Queue()
    Thread(target=emotion_panel_container_simulator, args=(q,), daemon=True).start()
    app = EmotionPanelContainer(q)
    app.mainloop()
