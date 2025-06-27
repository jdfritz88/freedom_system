# gui_status_panel.py — Visual Rendering Layer
# Live display of system status messages in a dockable panel

import tkinter as tk
from componentsave.ui_panels.dashboard_status_panel import get_recent_status_log

__all__ = ["StatusPanel"]


class StatusPanel(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.pack_propagate(0)
        self.configure(width=300, height=140)

        self.label = tk.Label(self, text="System Status", font=("Arial", 10, "bold"))
        self.label.pack(anchor="w", padx=6, pady=(4, 0))

        self.textbox = tk.Text(self, wrap=tk.WORD, height=6, width=44, bg="black", fg="lime", font=("Consolas", 9))
        self.textbox.pack(padx=4, pady=4, fill=tk.BOTH, expand=True)
        self.textbox.config(state=tk.DISABLED)

        self.refresh()

    def refresh(self):
        self.textbox.config(state=tk.NORMAL)
        self.textbox.delete(1.0, tk.END)
        for line in get_recent_status_log():
            self.textbox.insert(tk.END, f"{line}\n")
        self.textbox.config(state=tk.DISABLED)
        self.after(2000, self.refresh)  # refresh every 2 seconds


if __name__ == '__main__':
    root = tk.Tk()
    root.title("Status Panel Test")
    panel = StatusPanel(master=root)
    panel.pack(fill=tk.BOTH, expand=True)
    root.mainloop()
