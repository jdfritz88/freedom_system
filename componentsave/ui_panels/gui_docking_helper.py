import tkinter as tk

class DockableFrame(tk.Toplevel):
    def __init__(self, parent, title="Undocked Panel"):
        super().__init__(parent)
        self.title(title)
        self.protocol("WM_DELETE_WINDOW", self.hide)
        self.withdraw()  # Start hidden
        self.resizable(True, True)

    def attach_panel(self, widget):
        widget.pack(fill="both", expand=True)
        self.deiconify()

    def hide(self):
        self.withdraw()

    def toggle(self):
        if self.state() == "withdrawn":
            self.deiconify()
        else:
            self.withdraw()
