import os
import ast

MANDATORY_FILES = [
    "emotional_core_logic/emotion_broadcast_hub.py",
    "emotional_core_logic/emotion_system_core.py",
    "output_bridges/systems_voice/voice_emotion_bridge.py",
    "output_bridges/systems_voice/voice_emotion_driver.py",
    "output_bridges/systems_image/image_emotion_driver.py",
    "face_trainer/face_training_engine.py",
    "launchers/start_emotion_engine_flag_check.py",
    "ui_panels/gui_emotion_panels.py"
]

REQUIRED_FUNCTIONS = {
    "emotion_broadcast_hub.py": ["broadcast_emotion_status"],
    "emotion_system_core.py": ["blend_emotions"],
    "voice_emotion_bridge.py": ["trigger_voice_response"],
    "image_emotion_driver.py": ["generate_emotion_image"]
}


def file_has_functions(filepath, function_list):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
        funcs = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        return all(func in funcs for func in function_list)
    except Exception as e:
        return False


def main():
    base = os.path.dirname(__file__)
    components = os.path.join(base, "componentsave")

    print("[SCAN] Checking system files and functions...\n")
    missing = []
    broken = []

    for rel_path in MANDATORY_FILES:
        abs_path = os.path.join(components, rel_path)
        if not os.path.isfile(abs_path):
            missing.append(rel_path)
        else:
            file_name = os.path.basename(abs_path)
            if file_name in REQUIRED_FUNCTIONS:
                expected_funcs = REQUIRED_FUNCTIONS[file_name]
                if not file_has_functions(abs_path, expected_funcs):
                    broken.append(rel_path)

    if not missing and not broken:
        print("✅ All mandatory files and functions are present.")
    else:
        if missing:
            print("❌ Missing files:")
            for f in missing:
                print(f"  - {f}")

        if broken:
            print("⚠️  Files present but missing functions:")
            for f in broken:
                print(f"  - {f}")

        print("\n[FIX SUGGESTION]")
        for f in missing:
            print(f"Create placeholder: componentsave/{f} with a stub module and TODO comment")

        for f in broken:
            filename = os.path.basename(f)
            expected = REQUIRED_FUNCTIONS[filename]
            print(f"Edit {f} to include functions: {', '.join(expected)}")

if __name__ == '__main__':
    main()
