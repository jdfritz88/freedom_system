# gui_alert_strip.py — Visual Alert Banner
# Displays the latest alert in bold banner style

import tkinter as tk
from componentsave.ui_panels.dashboard_alert_strip import get_current_alert


class AlertStrip(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg="red", height=28)

        self.label = tk.Label(self, text="", fg="white", bg="red", font=("Arial", 10, "bold"))
        self.label.pack(fill=tk.BOTH, expand=True)

        self.refresh()

    def refresh(self):
        msg = get_current_alert()
        self.label.config(text=msg)
        self.after(1000, self.refresh)  # poll every 1s


if __name__ == '__main__':
    root = tk.Tk()
    root.title("Alert Strip Test")
    banner = AlertStrip(master=root)
    banner.pack(fill=tk.X)
    root.mainloop()
