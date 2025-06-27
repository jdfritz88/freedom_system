# gui_emotion_feed.py — Emotion Feed Panel
# Shows a scrollable list of recent emotion triggers

import tkinter as tk
from componentsave.ui_panels.dashboard_emotion_feed import get_emotion_feed


class EmotionFeedPanel(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(width=300, height=150)
        self.pack_propagate(0)

        self.label = tk.Label(self, text="Emotion Feed", font=("Arial", 10, "bold"))
        self.label.pack(anchor="w", padx=6, pady=(4, 0))

        self.listbox = tk.Listbox(self, bg="black", fg="cyan", font=("Courier", 9))
        self.listbox.pack(padx=4, pady=4, fill=tk.BOTH, expand=True)

        self.refresh()

    def refresh(self):
        self.listbox.delete(0, tk.END)
        for item in get_emotion_feed():
            self.listbox.insert(tk.END, item)
        self.after(3000, self.refresh)


if __name__ == '__main__':
    root = tk.Tk()
    root.title("Emotion Feed Test")
    panel = EmotionFeedPanel(master=root)
    panel.pack(fill=tk.BOTH, expand=True)
    root.mainloop()
