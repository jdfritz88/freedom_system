import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import tkinter as tk
from componentsave.tkinter import Toplevel

class DashboardGrid(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Freedom System Dashboard")
        self.geometry("1200x800")
        self.configure(bg='black')

        # Initialize the Emotion Orb Panel
        self.init_emotion_orb_panel()

    def init_emotion_orb_panel(self):
        orb_panel = Toplevel(self)
        orb_panel.title("Emotion Orb")
        orb_panel.geometry("300x300+900+0")  # Upper right corner
        orb_panel.configure(bg='black')
        orb_panel.overrideredirect(False)  # Allow movement across screens

        # Example canvas for orb visual
        canvas = tk.Canvas(orb_panel, width=300, height=300, bg='black', highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        # Draw Orb (circle with glow outline)
        orb = canvas.create_oval(50, 50, 250, 250, fill="purple", outline="magenta", width=6)

        # Optional pulse logic placeholder
        self.pulse_orb(canvas, orb, 0)

    def pulse_orb(self, canvas, orb, frame):
        # Basic pulse effect
        scale = 1.0 + 0.02 * (frame % 10)
        canvas.scale(orb, 150, 150, scale, scale)
        self.after(100, lambda: self.pulse_orb(canvas, orb, frame + 1))

if __name__ == '__main__':
    app = DashboardGrid()
    app.mainloop()
