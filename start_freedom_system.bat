@echo off

:: Freedom System Startup Batch File
:: Location: F:/Apps/freedom_system/start_freedom_system.bat

:: 1. Set emotion engine boot flag
python launchers/emotion_engine_boot_flag.py

:: 2. Launch unified dashboard
start /B python componentsave/ui_panels/gui_dashboard_window.py

:: 3. Launch emotion engine
start /B python componentsave/emotional_core_logic/emotion_system_core.py

:: 4. (Optional) Launch voice system
:: start /B python componentsave/output_bridges/systems_voice/run_voice.py

pause
