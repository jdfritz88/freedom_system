import tkinter as tk
from tkinter import ttk
import os
import sys
import json

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'data_logging', 'ui_state_config.json')

class MusicStatePanel:
    def __init__(self, master, dock_callback):
        self.master = master
        self.dock_callback = dock_callback
        self.floating = False
        self.panel = None
        self.load_state()
        self.build_panel()

    def build_panel(self):
        if self.floating:
            self.panel = tk.Toplevel(self.master)
            self.panel.title("Music State")
            self.panel.geometry("300x150+150+150")
            self.panel.lift()
            self.panel.attributes('-topmost', True)
            self.panel.after(200, lambda: self.panel.attributes('-topmost', False))
        else:
            self.panel = ttk.Frame(self.master)
        self.draw_contents()

    def draw_contents(self):
        for child in self.panel.winfo_children():
            child.destroy()
        label = ttk.Label(self.panel, text="Music State")
        label.pack(padx=10, pady=10)
        toggle_btn = ttk.Button(self.panel, text="Dock/Undock", command=self.toggle_dock)
        toggle_btn.pack(pady=(0, 10))

    def toggle_dock(self):
        self.floating = not self.floating
        self.save_state()
        if callable(self.dock_callback):
            self.dock_callback(self.floating)

    def save_state(self):
        try:
            config = {}
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, 'r') as f:
                    config = json.load(f)
            config['music_state_docked'] = not self.floating
            with open(CONFIG_PATH, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print("[ERROR] Saving music_state state:", e)

    def load_state(self):
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, 'r') as f:
                    config = json.load(f)
                self.floating = not config.get('music_state_docked', True)
        except Exception as e:
            print("[ERROR] Loading music_state state:", e)
            self.floating = False
