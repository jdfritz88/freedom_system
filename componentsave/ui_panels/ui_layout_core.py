import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import tkinter as tk
from componentsave.emotion_state_catalog import EMOTIONS

class UILayoutCore(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Freedom System UI Layout")
        self.geometry("800x600")
        self.configure(bg="#111")

        # Main layout wrapper
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.main_frame = tk.Frame(self, bg="#111")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.columnconfigure((0,1), weight=1)
        self.main_frame.rowconfigure((0,1), weight=1)

        # Title bar
        title = tk.Label(self.main_frame, text="Freedom UI Layout", font=("Arial", 18), fg="white", bg="#111")
        title.grid(row=0, column=0, columnspan=2, pady=10)

        # Placeholder: Orb or Panel
        self.left_panel = tk.Frame(self.main_frame, bg="#222")
        self.left_panel.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.left_panel.rowconfigure(0, weight=1)
        self.left_panel.columnconfigure(0, weight=1)

        # Placeholder: Dashboard or Graph
        self.right_panel = tk.Frame(self.main_frame, bg="#181818")
        self.right_panel.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        self.right_panel.rowconfigure(0, weight=1)
        self.right_panel.columnconfigure(0, weight=1)

        # Example: emotion preview labels
        self.status_labels = {}
        for idx, emo in enumerate(EMOTIONS):
            row = idx % 9
            col = idx // 9
            label = tk.Label(self.left_panel, text=emo, bg="#333", fg="white", width=20, anchor='w')
            label.grid(row=row, column=col, sticky='ew', pady=2, padx=4)
            self.status_labels[emo] = label

        # Dashboard placeholder box
        self.dash_box = tk.Text(self.right_panel, bg="#111", fg="lime", font=("Courier", 10))
        self.dash_box.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        self.dash_box.insert("end", "[Placeholder for dashboard responsiveness engine]\n")
        self.dash_box.config(state="disabled")


if __name__ == '__main__':
    app = UILayoutCore()
    app.mainloop()
