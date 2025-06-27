import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import tkinter as tk
from componentsave.threading import Thread
from componentsave.queue import Queue

class EmotionPanel(tk.Frame):
    def __init__(self, master, emotion_name, update_queue, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.emotion_name = emotion_name
        self.update_queue = update_queue
        self.configure(bg='#292929')

        self.label = tk.Label(self, text=emotion_name, font=("Arial", 12), fg="white", bg="#292929")
        self.label.pack(side='left', padx=5)

        self.status = tk.Label(self, text="--", font=("Arial", 12), fg="gray", bg="#292929")
        self.status.pack(side='right', padx=5)

        self.after(100, self.listen_for_update)

    def listen_for_update(self):
        try:
            while not self.update_queue.empty():
                emo, value = self.update_queue.get(False)
                if emo == self.emotion_name:
                    self.status.config(text=f"{value:.2f}", fg="lime")
        except Exception:
            pass
        self.after(100, self.listen_for_update)


def spawn_panel(root, emotion_name, update_queue):
    panel = EmotionPanel(root, emotion_name, update_queue)
    panel.pack(pady=5, fill='x', padx=10)
    return panel


def emotion_panel_simulator(update_queue):
    import random, time
    emotions = ["Happy", "Sad", "Angry", "Romantic", "Aroused", "Lonely", "Calm (Neutral)"]
    while True:
        time.sleep(0.6)
        emo = random.choice(emotions)
        val = random.uniform(0.0, 1.0)
        update_queue.put((emo, val))


if __name__ == '__main__':
    root = tk.Tk()
    root.title("Emotion Panel Modules")
    root.geometry("300x500")
    root.configure(bg="#1e1e1e")

    update_queue = Queue()
    Thread(target=emotion_panel_simulator, args=(update_queue,), daemon=True).start()

    emotions = ["Happy", "Sad", "Angry", "Romantic", "Aroused", "Lonely", "Calm (Neutral)"]
    panels = [spawn_panel(root, emo, update_queue) for emo in emotions]

    root.mainloop()
