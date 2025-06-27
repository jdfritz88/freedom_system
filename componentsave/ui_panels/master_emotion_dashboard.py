# Add to: F:\Apps\freedom_system\componentsave\ui_panels\master_emotion_dashboard.py
# Place after slider panel import and setup

import os

class MasterEmotionDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Freedom System - Master Emotion Dashboard")
        self.geometry("800x600")
        self.configure(padx=10, pady=10)

        self.build_grid()

    def build_grid(self):
        # Top row - system status (placeholder)
        top_frame = ttk.Frame(self)
        top_frame.grid(row=0, column=0, sticky="ew")
        ttk.Label(top_frame, text="System Status: ONLINE", font=("Arial", 12)).pack(anchor='w')

        # Main center - control panels
        center_frame = ttk.Frame(self)
        center_frame.grid(row=1, column=0, sticky="nsew")
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        # Insert EmotionControlPanel here
        slider_panel = EmotionControlPanel(master=center_frame)
        slider_panel.pack(fill='both', expand=True)

        # Log Viewer (Dropdown)
        self.log_visible = tk.BooleanVar(value=False)
        ttk.Checkbutton(self, text="Show Slider Sync Log", variable=self.log_visible, command=self.toggle_log_view).pack(pady=5)
        self.log_frame = ttk.Frame(self)
        self.log_text = tk.Text(self.log_frame, height=10, state='disabled')
        self.log_text.pack(fill='both', expand=True)

        # Bottom row
        bottom_frame = ttk.Frame(self)
        bottom_frame.grid(row=2, column=0, sticky="ew")
        ttk.Label(bottom_frame, text="Freedom System v1.0 - Emotional Dashboard").pack(anchor='center')

    def toggle_log_view(self):
        if self.log_visible.get():
            self.log_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=5)
            self.display_log()
        else:
            self.log_frame.grid_forget()

    def display_log(self):
        log_path = os.path.join(os.path.dirname(__file__), '..', '..', 'log', 'ui_panels', 'slider_sync_log.txt')
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', 'end')
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                lines = f.readlines()[-10:]
                for line in lines:
                    self.log_text.insert('end', line)
        else:
            self.log_text.insert('end', '[Log file not found]\n')
        self.log_text.config(state='disabled')
