import tkinter as tk
from tkinter import ttk
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from componentsave.ui_panels.emotion_readout_dock import EmotionReadoutPanel
from componentsave.ui_panels.emotion_overlay_dock import EmotionOverlayPanel
from componentsave.ui_panels.emotion_trigger_threshold_dock import EmotionTriggerThresholdPanel
from componentsave.ui_panels.emotion_delay_decay_dock import EmotionDelayDecayPanel
from componentsave.ui_panels.log_viewer_dock import LogViewerPanel
from componentsave.ui_panels.tooltip_help_dock import TooltipHelpPanel
from componentsave.ui_panels.master_status_dock import MasterStatusPanel
from componentsave.ui_panels.dashboard_grid_router_dock import DashboardGridRouterPanel
from componentsave.ui_panels.music_state_dock import MusicStatePanel
from componentsave.ui_panels.animation_driver_dock import AnimationDriverPanel

class DashboardWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Freedom Emotion Dashboard")
        self.root.geometry("1000x800")

        self.panels = [
            EmotionReadoutPanel(root, self.rebuild),
            EmotionOverlayPanel(root, self.rebuild),
            EmotionTriggerThresholdPanel(root, self.rebuild),
            EmotionDelayDecayPanel(root, self.rebuild),
            LogViewerPanel(root, self.rebuild),
            TooltipHelpPanel(root, self.rebuild),
            MasterStatusPanel(root, self.rebuild),
            DashboardGridRouterPanel(root, self.rebuild),
            MusicStatePanel(root, self.rebuild),
            AnimationDriverPanel(root, self.rebuild)
        ]

        for panel in self.panels:
            if not panel.floating:
                panel.panel.pack(fill='both', expand=True, padx=4, pady=4)

    def rebuild(self, floating):
        self.root.destroy()
        main()

def main():
    root = tk.Tk()
    app = DashboardWindow(root)
    root.mainloop()

if __name__ == '__main__':
    main()
