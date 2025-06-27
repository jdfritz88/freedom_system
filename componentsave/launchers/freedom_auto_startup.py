import os

# Step 1: Windows Startup Folder
startup_dir = r"C:\\Users\\jespe\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"

# Step 2: Path to the local server + autosave script
script_path = r"F:\\Apps\\freedom_system\\componentsave\\launchers\\startup_file_server_launcher.py"

# Step 3: Create the .bat file
bat_path = os.path.join(startup_dir, "FreedomSystemStartup.bat")

try:
    os.makedirs(startup_dir, exist_ok=True)
    with open(bat_path, "w") as f:
        f.write(f"start /min pythonw \"{script_path}\"\n")
    print(f"✅ Startup launcher created: {bat_path}")
except Exception as e:
    print(f"❌ Failed to create startup script: {e}")
