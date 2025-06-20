import os

# Hardcoded Windows Startup path
startup_dir = r"C:\\Users\\jespe\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
launcher_path = r"F:\\Apps\\freedom_system\\freedom_autopush_launcher.py"

# Create a .bat file to launch the Python script silently
bat_path = os.path.join(startup_dir, "FreedomAutoPush.bat")

try:
    os.makedirs(startup_dir, exist_ok=True)
    with open(bat_path, "w") as f:
        f.write(f"start /min pythonw \"{launcher_path}\"\n")
    print(f"✅ Auto-push will now run at startup from: {bat_path}")
except Exception as e:
    print(f"❌ Failed to create startup script: {e}")
