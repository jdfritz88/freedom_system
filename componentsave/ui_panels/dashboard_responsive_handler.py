import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# dashboard_responsive_handler.py

import ctypes

# Get screen dimensions (cross-platform using ctypes for Windows)
def get_screen_dimensions():
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    width = user32.GetSystemMetrics(0)
    height = user32.GetSystemMetrics(1)
    return width, height


# Determine layout mode based on screen size
def get_current_layout_mode():
    width, height = get_screen_dimensions()
    aspect_ratio = width / height

    if width >= 1600:
        return "wide"
    elif height >= 1000 and aspect_ratio < 1.0:
        return "tall"
    else:
        return "compact"


# Debug/Test mode
if __name__ == "__main__":
    mode = get_current_layout_mode()
    print(f"[DashboardResponsive] Current layout mode: {mode}")
