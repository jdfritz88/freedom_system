# This script verifies Freedom System readiness by checking:
# - Emotion Engine
# - Voice System
# - Image Generation
# - Music Reaction
# - UI Panels
# - Launchers

import os

ROOT = "F:/Apps/freedom_system/componentsave"
MODULES = {
    "emotional_core_logic": [
        "emotion_broadcast_hub.py", "emotion_decay_module.py", "emotion_delay_throttle.py",
        "emotion_framer.py", "emotion_framing_weights.py", "emotion_image_generator.py",
        "emotion_queue.py", "emotion_system_core.py", "emotion_system_status.py",
        "emotion_threshold_control.py", "emotion_trigger_handler.py", "emotion_trigger_validator.py",
        "freedom_emotion_blender.py", "freedom_emotion_module_loader.py"
    ],
    "output_bridges/systems_voice": [
        "voice_emotion_bridge.py", "voice_emotion_driver.py", "emotion_vfx_overlay.py"
    ],
    "output_bridges/systems_image": [
        "image_emotion_driver.py"
    ],
    "output_bridges/systems_music": [
        "emotional_music_router.py", "music_emotion_driver.py"
    ],
    "face_trainer": ["face_training_engine.py"],
    "ui_panels": ["background_toggle_control.py", "gui_emotion_panels.py"],
    "launchers": ["emotion_engine_boot_flag.py", "face_training_launcher.py", "start_emotion_engine_flag_check.py"]
}

def check_status():
    report = []
    for module, files in MODULES.items():
        module_path = os.path.join(ROOT, module)
        if not os.path.exists(module_path):
            report.append(f"[MISSING MODULE FOLDER] {module_path}")
            continue

        for file in files:
            file_path = os.path.join(module_path, file)
            if not os.path.isfile(file_path):
                report.append(f"[MISSING FILE] {file_path}")
            else:
                report.append(f"[OK] {file_path}")

    log_path = os.path.join(ROOT, "diagnostics", "freedom_manifest_check_log.txt")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report))

    print(f"[DONE] Manifest check complete. Log saved to: {log_path}")

if __name__ == "__main__":
    check_status()
