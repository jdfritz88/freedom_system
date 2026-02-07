# ==========================================
# FREEDOM SYSTEM INSTALLER - ENFORCED MODE
# Follows Freedom_Installer_Coding_Standards.txt
# ==========================================

"""
Comprehensive AllTalk TTS Extension Fix
Addresses all identified issues:
1. save_config -> save_settings method name fix
2. Enhanced logging throughout
3. Voice selection validation
4. Prevents invalid voice names from reaching API
"""

import sys
import os
import shutil
import json
import time
from datetime import datetime

def print_message(msg, level="INFO"):
    """Print formatted message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("[" + timestamp + "] [" + level + "] " + msg)
    log_to_file(timestamp, level, msg)

def log_to_file(timestamp, level, msg):
    """Log all messages to file"""
    log_path = "F:\\Apps\\freedom_system\\log\\alltalk_comprehensive_fix.log"
    try:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write("[" + timestamp + "] [" + level + "] " + msg + "\n")
    except:
        pass  # Silent fail for logging

def backup_file(filepath):
    """Create timestamped backup"""
    if not os.path.exists(filepath):
        print_message("File not found: " + filepath, "ERROR")
        return False
    
    backup_path = filepath + ".backup_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    try:
        shutil.copy2(filepath, backup_path)
        print_message("Created backup: " + backup_path, "SUCCESS")
        return True
    except Exception as e:
        print_message("Backup failed: " + str(e), "ERROR")
        return False

def read_file(filepath):
    """Read file with error handling"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print_message("Read failed for " + filepath + ": " + str(e), "ERROR")
        return None

def write_file(filepath, content):
    """Write file with error handling"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print_message("Updated file: " + filepath, "SUCCESS")
        return True
    except Exception as e:
        print_message("Write failed: " + str(e), "ERROR")
        return False

def fix_save_config_method():
    """Fix save_config -> save_settings"""
    print_message("STEP 1: Fixing save_config method calls...")
    
    script_path = "F:\\Apps\\freedom_system\\app_cabinet\\text-generation-webui\\extensions\\alltalk_tts\\system\\TGWUI_Extension\\script.py"
    
    if not backup_file(script_path):
        return False
    
    content = read_file(script_path)
    if not content:
        return False
    
    # Count and fix
    count = content.count("mode_manager.save_config()")
    if count == 0:
        print_message("No save_config() calls found", "INFO")
        return True
    
    print_message("Found " + str(count) + " save_config() calls to fix", "INFO")
    fixed_content = content.replace("mode_manager.save_config()", "mode_manager.save_settings()")
    
    if write_file(script_path, fixed_content):
        print_message("Fixed " + str(count) + " method calls", "SUCCESS")
        return True
    return False

def add_enhanced_logging():
    """Add comprehensive logging throughout the script"""
    print_message("STEP 2: Adding enhanced logging...")
    
    script_path = "F:\\Apps\\freedom_system\\app_cabinet\\text-generation-webui\\extensions\\alltalk_tts\\system\\TGWUI_Extension\\script.py"
    
    content = read_file(script_path)
    if not content:
        return False
    
    # Add logging helper function after imports
    logging_helper = '''
# Enhanced logging for debugging
def log_alltalk(message, level="INFO", function_name=""):
    """Enhanced logging with timestamp and function tracking"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    prefix = "[AllTalk TTS]"
    if function_name:
        prefix = prefix + " [" + function_name + "]"
    
    full_message = prefix + " [" + level + "] " + message
    print(full_message)
    
    # Also log to file
    try:
        log_file = "F:/Apps/freedom_system/log/alltalk_operations.log"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write("[" + timestamp + "] " + full_message + "\\n")
    except:
        pass  # Silent fail for file logging

'''
    
    # Find where to insert (after imports)
    import_end = content.find("class TGWUIModeManager")
    if import_end == -1:
        print_message("Could not find class definition", "ERROR")
        return False
    
    # Check if logging already exists
    if "def log_alltalk" not in content:
        content = content[:import_end] + logging_helper + "\n" + content[import_end:]
        print_message("Added logging helper function", "SUCCESS")
    
    # Add logging to key functions
    logging_points = [
        ("def update_character_voice(x):", 
         '            log_alltalk("Character voice changed to: " + str(x), "INFO", "update_character_voice")'),
        ("def update_narrator_voice(x):",
         '            log_alltalk("Narrator voice changed to: " + str(x), "INFO", "update_narrator_voice")'),
        ("def send_tts_request(",
         '        log_alltalk("TTS request for text length: " + str(len(text)), "INFO", "send_tts_request")'),
        ("response = requests.post",
         '        log_alltalk("API request to: " + api_url, "DEBUG", "send_tts_request")'),
        ("if response.status_code == 200:",
         '            log_alltalk("TTS generation successful", "SUCCESS", "send_tts_request")'),
        ("except Exception as e:",
         '            log_alltalk("TTS generation failed: " + str(e), "ERROR", "send_tts_request")')
    ]
    
    for search_text, log_line in logging_points:
        if search_text in content and log_line not in content:
            # Find the line and add logging after it
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if search_text in line:
                    # Get indentation
                    indent = len(line) - len(line.lstrip())
                    # Insert log line with same indentation
                    lines.insert(i + 1, ' ' * indent + log_line)
                    break
            content = '\n'.join(lines)
    
    if write_file(script_path, content):
        print_message("Enhanced logging added", "SUCCESS")
        return True
    return False

def add_voice_validation():
    """Add validation to prevent invalid voice names"""
    print_message("STEP 3: Adding voice validation...")
    
    script_path = "F:\\Apps\\freedom_system\\app_cabinet\\text-generation-webui\\extensions\\alltalk_tts\\system\\TGWUI_Extension\\script.py"
    
    content = read_file(script_path)
    if not content:
        return False
    
    # Add validation function
    validation_func = '''
def validate_voice_selection(voice_name, voice_type="character"):
    """Validate that selected voice is not a placeholder"""
    invalid_names = ["Please Refresh Settings", "Refreshing...", "Loading...", ""]
    
    if voice_name in invalid_names:
        log_alltalk("Invalid voice name detected: " + voice_name, "WARNING", "validate_voice")
        # Try to get first valid voice
        if mode_manager.voices and len(mode_manager.voices) > 0:
            for voice in mode_manager.voices:
                if voice not in invalid_names:
                    log_alltalk("Using fallback voice: " + voice, "INFO", "validate_voice")
                    return voice
        log_alltalk("No valid voices available", "ERROR", "validate_voice")
        return None
    
    log_alltalk("Voice validated: " + voice_name, "SUCCESS", "validate_voice")
    return voice_name

def test_voice_selection(voice_name):
    """Test if a voice actually works by trying a small sample"""
    log_alltalk("Testing voice: " + voice_name, "INFO", "test_voice")
    
    test_text = "Testing voice selection."
    test_params = {
        "text": test_text,
        "voice": voice_name,
        "language": "en",
        "temperature": 0.3,
        "repetition_penalty": 10,
        "speed": 1.0
    }
    
    try:
        api_url = mode_manager.get_api_url("/api/tts-generate")
        response = requests.post(api_url, json=test_params, timeout=5)
        
        if response.status_code == 200:
            log_alltalk("Voice test successful: " + voice_name, "SUCCESS", "test_voice")
            return True
        else:
            log_alltalk("Voice test failed with status: " + str(response.status_code), "ERROR", "test_voice")
            return False
    except Exception as e:
        log_alltalk("Voice test error: " + str(e), "ERROR", "test_voice")
        return False

'''
    
    # Insert validation functions
    import_end = content.find("class TGWUIModeManager")
    if import_end > 0 and "def validate_voice_selection" not in content:
        content = content[:import_end] + validation_func + "\n" + content[import_end:]
        print_message("Added voice validation functions", "SUCCESS")
    
    # Modify update_character_voice to use validation
    old_update = '''        def update_character_voice(x):
            mode_manager.config["tgwui"].update({"tgwui_character_voice": x})
            mode_manager.save_settings()
            return None'''
    
    new_update = '''        def update_character_voice(x):
            log_alltalk("Voice selection attempt: " + str(x), "INFO", "update_character_voice")
            validated_voice = validate_voice_selection(x, "character")
            if validated_voice:
                # Test the voice before saving
                if test_voice_selection(validated_voice):
                    mode_manager.config["tgwui"].update({"tgwui_character_voice": validated_voice})
                    mode_manager.save_settings()
                    log_alltalk("Voice successfully changed to: " + validated_voice, "SUCCESS", "update_character_voice")
                else:
                    log_alltalk("Voice test failed, not saving: " + str(x), "ERROR", "update_character_voice")
            else:
                log_alltalk("Invalid voice rejected: " + str(x), "WARNING", "update_character_voice")
            return None'''
    
    if old_update in content:
        content = content.replace(old_update, new_update)
        print_message("Updated character voice selection with validation", "SUCCESS")
    
    if write_file(script_path, content):
        print_message("Voice validation added", "SUCCESS")
        return True
    return False

def add_api_request_logging():
    """Add detailed logging to API requests"""
    print_message("STEP 4: Adding API request logging...")
    
    script_path = "F:\\Apps\\freedom_system\\app_cabinet\\text-generation-webui\\extensions\\alltalk_tts\\system\\TGWUI_Extension\\script.py"
    
    content = read_file(script_path)
    if not content:
        return False
    
    # Find send_tts_request or similar function and enhance it
    if "def send_tts_request" in content:
        # Add detailed logging around API calls
        lines = content.split('\n')
        in_function = False
        
        for i, line in enumerate(lines):
            if "def send_tts_request" in line:
                in_function = True
            elif in_function and "requests.post" in line:
                # Add logging before the request
                indent = len(line) - len(line.lstrip())
                log_before = ' ' * indent + 'log_alltalk("Sending TTS request with voice: " + str(params.get("voice", "unknown")), "DEBUG", "api_request")'
                lines.insert(i, log_before)
                break
        
        content = '\n'.join(lines)
    
    if write_file(script_path, content):
        print_message("API logging enhanced", "SUCCESS")
        return True
    return False

def verify_alltalk_server():
    """Check if AllTalk server is running"""
    print_message("STEP 5: Verifying AllTalk server...")
    
    try:
        import requests
        response = requests.get("http://127.0.0.1:7851/api/ready", timeout=3)
        if response.status_code == 200:
            print_message("AllTalk server is running", "SUCCESS")
            
            # Try to get voices
            voices_response = requests.get("http://127.0.0.1:7851/api/voices", timeout=3)
            if voices_response.status_code == 200:
                voices = voices_response.json().get("voices", [])
                print_message("Found " + str(len(voices)) + " voices available", "INFO")
                for voice in voices[:5]:  # Show first 5
                    print_message("  - " + voice, "INFO")
            return True
    except Exception as e:
        print_message("AllTalk server check failed: " + str(e), "WARNING")
    
    print_message("AllTalk server may not be running", "WARNING")
    print_message("Please ensure AllTalk is started", "INFO")
    return False

def main():
    """Execute all fixes"""
    print_message("="*60)
    print_message("AllTalk TTS Comprehensive Fix Starting")
    print_message("="*60)
    
    results = []
    
    # Fix 1: Method name
    print_message("\n--- Fix 1: Method Name ---")
    if fix_save_config_method():
        results.append("SUCCESS: Fixed save_config method calls")
    else:
        results.append("FAILED: Method name fix")
    
    # Fix 2: Enhanced logging
    print_message("\n--- Fix 2: Enhanced Logging ---")
    if add_enhanced_logging():
        results.append("SUCCESS: Added enhanced logging")
    else:
        results.append("FAILED: Enhanced logging")
    
    # Fix 3: Voice validation
    print_message("\n--- Fix 3: Voice Validation ---")
    if add_voice_validation():
        results.append("SUCCESS: Added voice validation")
    else:
        results.append("FAILED: Voice validation")
    
    # Fix 4: API logging
    print_message("\n--- Fix 4: API Request Logging ---")
    if add_api_request_logging():
        results.append("SUCCESS: Enhanced API logging")
    else:
        results.append("FAILED: API logging")
    
    # Fix 5: Server check
    print_message("\n--- Fix 5: Server Verification ---")
    if verify_alltalk_server():
        results.append("SUCCESS: Server verified")
    else:
        results.append("WARNING: Server needs attention")
    
    # Summary
    print_message("\n" + "="*60)
    print_message("SUMMARY OF FIXES:")
    for result in results:
        print_message("  " + result)
    
    # Check if we have failures
    failures = [r for r in results if "FAILED" in r]
    if not failures:
        print_message("\n[DONE] All fixes applied successfully!")
        print_message("NEXT STEPS:")
        print_message("  1. Restart text-generation-webui")
        print_message("  2. Click 'Refresh settings & voices' in AllTalk tab")
        print_message("  3. Select a voice and it will be tested before saving")
        print_message("  4. Check F:/Apps/freedom_system/log/alltalk_operations.log for detailed logs")
    else:
        print_message("\n[PARTIAL] Some fixes failed - manual review needed")
    
    return len(failures) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)