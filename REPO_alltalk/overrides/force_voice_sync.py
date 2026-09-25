#!/usr/bin/env python3
"""
Force Voice Synchronization Script
Updates the configuration file to use dynamically discovered voices instead of hard-coded defaults
"""

import json
from pathlib import Path

def get_first_available_voice():
    """Dynamically discover the first available voice file"""
    voices_dir = Path(__file__).parent / "voices"

    if not voices_dir.exists():
        print(f"[WARNING] Voices directory not found: {voices_dir}")
        return "female_01.wav"  # Ultimate fallback

    # Get all .wav files in voices directory
    voice_files = list(voices_dir.glob("*.wav"))

    if not voice_files:
        print(f"[WARNING] No voice files found in {voices_dir}")
        return "female_01.wav"  # Ultimate fallback

    # Sort for consistent ordering
    voice_files.sort()
    first_voice = voice_files[0].name

    print(f"[DYNAMIC] First available voice discovered: {first_voice}")
    return first_voice

def update_config_file():
    """Update the TGWUI remote config with dynamic voice"""
    config_path = Path(__file__).parent / "system" / "TGWUI_Extension" / "tgwui_remote_config.json"

    if not config_path.exists():
        print(f"[ERROR] Config file not found: {config_path}")
        return False

    # Get dynamic voice
    dynamic_voice = get_first_available_voice()
    print(f"[UPDATE] Using dynamic voice: {dynamic_voice}")

    # Load config
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Update voice settings
        old_char = config.get('tgwui', {}).get('tgwui_character_voice', 'not set')
        old_narr = config.get('tgwui', {}).get('tgwui_narrator_voice', 'not set')

        config['tgwui']['tgwui_character_voice'] = dynamic_voice
        config['tgwui']['tgwui_narrator_voice'] = dynamic_voice

        # Save updated config
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)

        print(f"[SUCCESS] Config updated!")
        print(f"  Character voice: {old_char} -> {dynamic_voice}")
        print(f"  Narrator voice: {old_narr} -> {dynamic_voice}")
        print(f"  Config file: {config_path}")

        return True

    except Exception as e:
        print(f"[ERROR] Failed to update config: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("FORCE VOICE SYNCHRONIZATION")
    print("=" * 60)

    success = update_config_file()

    if success:
        print("\n[COMPLETE] Voice synchronization successful!")
        print("You can now restart AllTalk to see the changes.")
    else:
        print("\n[FAILED] Voice synchronization failed!")
        print("Please check the error messages above.")
