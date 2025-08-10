#!/usr/bin/env python3
"""
AllTalk Configuration Fixer
Automatically fixes common configuration issues that cause 500 errors
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

def backup_file(file_path):
    """Create backup of configuration file"""
    if file_path.exists():
        backup_name = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(file_path, backup_name)
        print(f"[BACKUP] Created backup: {backup_name}")
        return True
    return False

def fix_placeholder_values(config_data, config_name):
    """Replace all placeholder values with valid defaults"""
    changes_made = 0
    
    # Define valid defaults
    valid_voices = ["female_01.wav", "male_01.wav", "Arnold.wav"]
    default_voice = "female_01.wav"
    
    # Placeholder values to replace
    placeholders = ["Please Refresh Settings", "Select...", "Choose...", "", None]
    
    def replace_in_dict(d, path=""):
        nonlocal changes_made
        
        for key, value in d.items():
            current_path = f"{path}.{key}" if path else key
            
            # Check if this is a voice-related field
            if "voice" in key.lower():
                if value in placeholders:
                    print(f"[FIX] {config_name}: Replacing '{value}' with '{default_voice}' in {current_path}")
                    d[key] = default_voice
                    changes_made += 1
                elif isinstance(value, str) and value.endswith(".wav"):
                    # Verify voice file exists
                    voice_path = Path("voices") / value
                    if not voice_path.exists() and value not in ["Disabled"]:
                        print(f"[FIX] {config_name}: Voice file '{value}' not found, using default")
                        d[key] = default_voice
                        changes_made += 1
            
            # Recurse into nested dictionaries
            elif isinstance(value, dict):
                replace_in_dict(value, current_path)
            
            # Check lists
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if item in placeholders:
                        print(f"[FIX] {config_name}: Replacing list item '{item}' in {current_path}[{i}]")
                        d[key][i] = default_voice if "voice" in key.lower() else "default"
                        changes_made += 1
    
    replace_in_dict(config_data)
    return changes_made

def fix_config_file(config_path, config_name):
    """Fix a single configuration file"""
    print(f"\n[PROCESSING] {config_name}")
    print("=" * 50)
    
    if not config_path.exists():
        print(f"[SKIP] File not found: {config_path}")
        return False
    
    try:
        # Backup original
        backup_file(config_path)
        
        # Load configuration
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # Fix placeholder values
        changes = fix_placeholder_values(config_data, config_name)
        
        if changes > 0:
            # Save fixed configuration
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            
            print(f"[SUCCESS] Fixed {changes} issues in {config_name}")
            return True
        else:
            print(f"[INFO] No issues found in {config_name}")
            return True
            
    except Exception as e:
        print(f"[ERROR] Failed to fix {config_name}: {str(e)}")
        return False

def verify_voice_files():
    """Verify that voice files actually exist"""
    print("\n[VOICE FILES CHECK]")
    print("=" * 50)
    
    voices_dir = Path("voices")
    
    if not voices_dir.exists():
        print("[ERROR] Voices directory not found!")
        return False
    
    voice_files = list(voices_dir.glob("*.wav"))
    
    if not voice_files:
        print("[ERROR] No voice files found in voices directory!")
        return False
    
    print(f"[INFO] Found {len(voice_files)} voice files:")
    for voice in voice_files[:10]:  # Show first 10
        print(f"  - {voice.name}")
    
    if len(voice_files) > 10:
        print(f"  ... and {len(voice_files) - 10} more")
    
    # Check for essential voices
    essential_voices = ["female_01.wav", "male_01.wav"]
    missing = []
    
    for voice in essential_voices:
        if not (voices_dir / voice).exists():
            missing.append(voice)
    
    if missing:
        print(f"[WARNING] Missing essential voices: {', '.join(missing)}")
        
        # Try to use first available voice as default
        if voice_files:
            print(f"[INFO] Will use {voice_files[0].name} as default")
            return voice_files[0].name
    
    return "female_01.wav"

def synchronize_voice_settings(default_voice):
    """Ensure all configs use the same voice settings"""
    print("\n[SYNCHRONIZING VOICE SETTINGS]")
    print("=" * 50)
    
    configs_to_sync = {
        "Main Config": Path("confignew.json"),
        "Remote Config": Path("system/TGWUI_Extension/tgwui_remote_config.json"),
        "Model Settings": Path("system/tts_engines/xtts/model_settings.json")
    }
    
    # Determine the best voice to use
    print(f"[INFO] Using default voice: {default_voice}")
    
    for config_name, config_path in configs_to_sync.items():
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Update voice settings based on config structure
                if "tgwui" in config:
                    if "tgwui_character_voice" in config["tgwui"]:
                        config["tgwui"]["tgwui_character_voice"] = default_voice
                    if "tgwui_narrator_voice" in config["tgwui"]:
                        config["tgwui"]["tgwui_narrator_voice"] = default_voice
                
                if "settings" in config:
                    if "def_character_voice" in config["settings"]:
                        config["settings"]["def_character_voice"] = default_voice
                    if "def_narrator_voice" in config["settings"]:
                        config["settings"]["def_narrator_voice"] = default_voice
                
                # Save updated config
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=4, ensure_ascii=False)
                
                print(f"[SUCCESS] Synchronized {config_name}")
                
            except Exception as e:
                print(f"[ERROR] Failed to sync {config_name}: {str(e)}")

def main():
    print("\n" + "=" * 60)
    print("ALLTALK CONFIGURATION FIXER")
    print("=" * 60)
    print("\nThis script will fix common configuration issues that cause 500 errors")
    
    # Check if we're in the right directory
    if not Path("confignew.json").exists() and not Path("system").exists():
        print("\n[ERROR] This script must be run from the alltalk_tts directory")
        print("Please navigate to: extensions/alltalk_tts/")
        return
    
    # Step 1: Verify voice files
    default_voice = verify_voice_files()
    
    if not default_voice:
        print("\n[CRITICAL] No voice files available. Please add .wav files to the voices/ directory")
        return
    
    # Step 2: Fix configuration files
    configs = [
        (Path("confignew.json"), "Main Configuration"),
        (Path("system/TGWUI_Extension/tgwui_remote_config.json"), "Remote Configuration"),
        (Path("system/tts_engines/xtts/model_settings.json"), "Model Settings"),
    ]
    
    fixed_count = 0
    for config_path, config_name in configs:
        if fix_config_file(config_path, config_name):
            fixed_count += 1
    
    # Step 3: Synchronize voice settings
    synchronize_voice_settings(default_voice)
    
    # Summary
    print("\n" + "=" * 60)
    print("CONFIGURATION FIX COMPLETE")
    print("=" * 60)
    
    print(f"\n[SUMMARY]")
    print(f"  - Fixed {fixed_count}/{len(configs)} configuration files")
    print(f"  - Default voice set to: {default_voice}")
    print(f"  - Backups created for all modified files")
    
    print("\n[NEXT STEPS]")
    print("1. Restart the AllTalk server")
    print("2. Restart text-generation-webui")
    print("3. Run test_alltalk_api.py to verify fixes")
    
    print("\n[RESTORE]")
    print("If issues persist, restore from backups (.backup_* files)")

if __name__ == "__main__":
    main()
    print("\nPress Enter to exit...")
    input()