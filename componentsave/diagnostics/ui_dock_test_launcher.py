import tkinter as tk
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from componentsave.ui_panels.emotion_trigger_threshold_dock import EmotionTriggerThresholdPanel
from componentsave.ui_panels.emotion_delay_decay_dock import EmotionDelayDecayPanel
from componentsave.ui_panels.log_viewer_dock import LogViewerPanel
from componentsave.ui_panels.tooltip_help_dock import TooltipHelpPanel
from componentsave.ui_panels.master_status_dock import MasterStatusPanel
from componentsave.ui_panels.dashboard_grid_router_dock import DashboardGridRouterPanel
from componentsave.ui_panels.music_state_dock import MusicStatePanel
from componentsave.ui_panels.animation_driver_dock import AnimationDriverPanel

PANEL_CLASSES = [
    EmotionTriggerThresholdPanel,
    EmotionDelayDecayPanel,
    LogViewerPanel,
    TooltipHelpPanel,
    MasterStatusPanel,
    DashboardGridRouterPanel,
    MusicStatePanel,
    AnimationDriverPanel
]

PANEL_LABELS = [
    "Trigger Threshold",
    "Delay / Decay",
    "Log Viewer",
    "Tooltip Help",
    "Master Status",
    "Grid Router",
    "Music State",
    "Animation Driver"
]

def rebuild_all(floating):
    root.destroy()
    run_gui()

def run_gui():
    global root
    root = tk.Tk()
    root.title("Docked UI Panels Test")
    root.geometry("800x600")

    for cls, label in zip(PANEL_CLASSES, PANEL_LABELS):
        panel = cls(root, dock_callback=rebuild_all)
        if not panel.floating:
            panel.panel.pack(fill='both', expand=True, padx=5, pady=5)
        else:
            print(f"[FLOAT] {label} loaded in its own window")

    root.mainloop()

if __name__ == '__main__':
    run_gui()
