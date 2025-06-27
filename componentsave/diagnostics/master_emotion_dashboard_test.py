import sys
import os
import tkinter as tk

# Inject sibling folders
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui_panels.dashboard_grid_router import DashboardGridRouter

if __name__ == "__main__":
    print("[TEST] Launching Master Emotion Dashboard...")

    root = tk.Tk()
    root.title("Freedom Emotion Dashboard")
    root.geometry("800x400")

    grid = DashboardGridRouter(root)
    grid.pack(fill="both", expand=True)

    root.mainloop()
