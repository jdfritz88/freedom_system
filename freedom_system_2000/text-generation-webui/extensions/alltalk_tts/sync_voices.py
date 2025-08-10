#!/usr/bin/env python3
"""
Voice Synchronization Module for AllTalk TTS
Automatically scans the voices folder and updates all configuration files
"""

import json
import os
from pathlib import Path

def scan_voice_folder(voices_dir, previous_voices=None, enhanced_logging=False):
    """
    Scan the voices directory for available voice files
    
    Args:
        voices_dir: Path to the voices directory
        previous_voices: List of previously found voices to detect changes
        enhanced_logging: Whether to show detailed voice list
        
    Returns:
        Tuple of (voice_files, added_voices, removed_voices)
    """
    voice_files = []
    
    if not voices_dir.exists():
        print(f"[AllTalk] Warning: Voices directory not found: {voices_dir}")
        return voice_files, [], []
    
    # Scan for .wav files (main voice files)
    for file_path in voices_dir.glob("*.wav"):
        voice_files.append(file_path.name)
    
    # Sort for consistent ordering
    voice_files.sort()
    
    # Calculate changes if previous voices provided
    added_voices = []
    removed_voices = []
    
    if previous_voices is not None:
        added_voices = [v for v in voice_files if v not in previous_voices]
        removed_voices = [v for v in previous_voices if v not in voice_files]
    
    # Enhanced logging shows full voice list
    if enhanced_logging:
        print(f"[AllTalk] Found {len(voice_files)} voice files: {voice_files}")
    else:
        # Default logging shows summary with explicit counts
        added_count = len(added_voices)
        removed_count = len(removed_voices)
        print(f"[AllTalk] Found {len(voice_files)} voice files, {added_count} voice files added, {removed_count} voice files removed")
        
        if added_voices:
            print(f"[AllTalk] New voices: {added_voices}")
        if removed_voices:
            print(f"[AllTalk] Removed voices: {removed_voices}")
    
    return voice_files, added_voices, removed_voices

def update_main_config(config_path, voices):
    """
    Update the main confignew.json with available voices
    """
    try:
        # Load existing config
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Update voice settings if they're set to invalid values
        if 'tgwui' in config:
            current_char_voice = config['tgwui'].get('tgwui_character_voice', '')
            current_narr_voice = config['tgwui'].get('tgwui_narrator_voice', '')
            
            # Check if current voices are valid or placeholders
            if current_char_voice not in voices or current_char_voice == "Please Refresh Settings":
                config['tgwui']['tgwui_character_voice'] = voices[0] if voices else "female_01.wav"
                print(f"[AllTalk] Updated character voice to: {config['tgwui']['tgwui_character_voice']}")
            
            if current_narr_voice not in voices or current_narr_voice == "Please Refresh Settings":
                config['tgwui']['tgwui_narrator_voice'] = voices[1] if len(voices) > 1 else voices[0] if voices else "male_01.wav"
                print(f"[AllTalk] Updated narrator voice to: {config['tgwui']['tgwui_narrator_voice']}")
        
        # Save updated config
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
            
        print(f"[AllTalk] Updated main config: {config_path}")
        
    except Exception as e:
        print(f"[AllTalk] Error updating main config: {e}")

def update_tgwui_remote_config(config_path, voices):
    """
    Update the TGWUI remote configuration with available voices
    """
    try:
        # Load existing config
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if 'tgwui' in config:
            current_char_voice = config['tgwui'].get('tgwui_character_voice', '')
            current_narr_voice = config['tgwui'].get('tgwui_narrator_voice', '')
            
            # Check if current voices are valid or placeholders
            invalid_values = ["Please Refresh Settings", "en_US-ljspeech-high.onnx", ""]
            
            if current_char_voice in invalid_values or current_char_voice not in voices:
                config['tgwui']['tgwui_character_voice'] = voices[0] if voices else "female_01.wav"
                print(f"[AllTalk] Updated TGWUI character voice to: {config['tgwui']['tgwui_character_voice']}")
            
            if current_narr_voice in invalid_values or current_narr_voice not in voices:
                config['tgwui']['tgwui_narrator_voice'] = voices[1] if len(voices) > 1 else voices[0] if voices else "male_01.wav"
                print(f"[AllTalk] Updated TGWUI narrator voice to: {config['tgwui']['tgwui_narrator_voice']}")
        
        # Save updated config
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
            
        print(f"[AllTalk] Updated TGWUI remote config: {config_path}")
        
    except Exception as e:
        print(f"[AllTalk] Error updating TGWUI remote config: {e}")

def update_model_settings(settings_path, voices):
    """
    Update the model settings JSON with available voices
    """
    try:
        # Load existing settings
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        
        if 'settings' in settings:
            current_char_voice = settings['settings'].get('def_character_voice', '')
            current_narr_voice = settings['settings'].get('def_narrator_voice', '')
            
            # Check if current voices are valid
            if current_char_voice not in voices or current_char_voice == "Please Refresh Settings":
                settings['settings']['def_character_voice'] = voices[0] if voices else "female_01.wav"
                print(f"[AllTalk] Updated model character voice to: {settings['settings']['def_character_voice']}")
            
            if current_narr_voice not in voices or current_narr_voice == "Please Refresh Settings":
                settings['settings']['def_narrator_voice'] = voices[1] if len(voices) > 1 else voices[0] if voices else "male_01.wav"
                print(f"[AllTalk] Updated model narrator voice to: {settings['settings']['def_narrator_voice']}")
        
        # Save updated settings
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4)
            
        print(f"[AllTalk] Updated model settings: {settings_path}")
        
    except Exception as e:
        print(f"[AllTalk] Error updating model settings: {e}")

def sync_all_voices(enhanced_logging=False, previous_voices=None):
    """
    Main function to synchronize voices across all configuration files
    
    Args:
        enhanced_logging: Whether to show detailed logging
        previous_voices: List of previously found voices to detect changes
    """
    print("[AllTalk] Starting voice synchronization...")
    
    # Get the base directory
    base_dir = Path(__file__).parent
    voices_dir = base_dir / "voices"
    
    # Scan for available voices with change detection
    voices, added_voices, removed_voices = scan_voice_folder(voices_dir, previous_voices, enhanced_logging)
    
    if not voices:
        print("[AllTalk] Warning: No voice files found!")
        return voices, added_voices, removed_voices
    
    # Update all configuration files
    print("[AllTalk] This prevents broken configurations when voice files change.")
    config_files = [
        (base_dir / "confignew.json", update_main_config),
        (base_dir / "system" / "TGWUI_Extension" / "tgwui_remote_config.json", update_tgwui_remote_config),
        (base_dir / "system" / "tts_engines" / "xtts" / "model_settings.json", update_model_settings),
    ]
    
    for config_path, update_func in config_files:
        if config_path.exists():
            update_func(config_path, voices)
        else:
            if enhanced_logging:
                print(f"[AllTalk] Config file not found: {config_path}")
    
    print(f"[AllTalk] Voice synchronization complete. {len(voices)} voices available.")
    return voices, added_voices, removed_voices

if __name__ == "__main__":
    # Run synchronization when called directly
    sync_all_voices()