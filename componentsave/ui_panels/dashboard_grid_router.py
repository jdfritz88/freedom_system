# Add import
from ui_panels.ui_state_config import load_ui_state, save_ui_state

# Load and set initial state
        self.ui_state = load_ui_state()
        start_docked = self.ui_state.get("overlay_docked", False)

        self.tag_overlay_frame = DockableFrame(self.master, "Emotion Tag Overlay")
        self.tag_overlay = EmotionTagOverlay(self.tag_overlay_frame)
        self.tag_overlay_frame.attach_panel(self.tag_overlay)

        if start_docked:
            self.tag_overlay_frame.deiconify()
        else:
            self.tag_overlay_frame.withdraw()

# Update toggle_overlay to store state
    def toggle_overlay(self):
        if self.tag_overlay_frame.state() == "withdrawn":
            self.tag_overlay_frame.deiconify()
            self.ui_state["overlay_docked"] = True
        else:
            self.tag_overlay_frame.withdraw()
            self.ui_state["overlay_docked"] = False
        save_ui_state(self.ui_state)
