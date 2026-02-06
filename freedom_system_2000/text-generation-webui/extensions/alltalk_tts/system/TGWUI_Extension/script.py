"""
TGWUI Integration Script

This script manages the Text-Gen-webui interface for AllTalk's TTS capabilities.
It provides:

- Mode management to detect local or remote operation.
- Configuration loading and saving for TTS-related settings.
- Integration with AllTalk server APIs for TTS generation and model updates.
- A Gradio-based user interface for controlling TTS settings and previewing voices.
- Centralized logging and debugging functions.

Modules:
- TGWUIModeManager: Handles configuration and mode detection.
- AllTalkServerSettings: Manages server-side settings and capabilities.
- Various utility functions for TTS generation, history management, and UI updates.

Usage:
Run this script as part of the AllTalk or TGWUI environment for managing TTS capabilities.
Ensure the required dependencies and configurations are properly installed.

Dependencies:
- Python 3.7+
- Gradio, requests, threading, and additional libraries.
"""
import re
import json
import inspect
import random
import logging
import threading
import os
import time
import sys
from datetime import datetime
from pathlib import Path
import requests

# Import text-generation-webui modules (may fail in standalone mode)
try:
    import gradio as gr
    from modules import chat, shared, ui_chat
    from modules.utils import gradio as gradio_utils
    TGWUI_MODULES_AVAILABLE = True
except ImportError:
    print("[AllTalk TTS] Text-generation-webui modules not available - continuing with standard logging")
    TGWUI_MODULES_AVAILABLE = False
    # Create dummy objects if needed later
    gr = None
    chat = None
    shared = None
    ui_chat = None
    gradio_utils = None
from requests.exceptions import RequestException, ConnectionError

# Define log_simple before it's used
def log_simple(message, level="INFO"):
    """Simple logging for default console output"""
    prefix = "[AllTalk TTS]"
    full_message = prefix + " " + message
    print(full_message)
    
    # Also log to file
    try:
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_file = "F:/Apps/freedom_system/log/alltalk_operations.log"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write("[" + timestamp + "] " + full_message + "\n")
    except:
        pass  # Silent fail for file logging

# Import voice synchronization module
def check_alltalk_server_running():
    """Check if AllTalk server is already running"""
    try:
        import requests
        response = requests.get("http://127.0.0.1:7851/api/ready", timeout=2)
        return response.status_code == 200
    except:
        return False

sync_all_voices = None

# Only import sync_voices if AllTalk server is not running standalone
if check_alltalk_server_running():
    log_simple("Standalone AllTalk server detected - using remote configuration")
    sync_all_voices = None
else:
    try:
        import sys
        sys.path.append(str(Path(__file__).parent.parent.parent))
        from sync_voices import sync_all_voices
        log_simple("Voice synchronization module loaded successfully")
    except ImportError as e:
        log_simple("Warning: Voice synchronization module import failed: " + str(e))
        sync_all_voices = None

# Store the current disable level
current_disable_level = logging.getLogger().manager.disable
this_dir = Path(__file__).parent.resolve()



def log_alltalk(message, level="INFO", function_name="", force_print=False):
    """Standard logging with timestamp and function tracking"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    prefix = "[AllTalk TTS]"
    if function_name:
        prefix = prefix + " [" + function_name + "]"
    
    full_message = prefix + " [" + level + "] " + message
    
    # Always print to console (removing enhanced logging condition)
    print(full_message)
    
    # Always log to file
    try:
        log_file = "F:/Apps/freedom_system/log/alltalk_operations.log"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write("[" + timestamp + "] " + full_message + "\n")
    except:
        pass  # Silent fail for file logging



def test_and_save_voice(voice_name, voice_type="character"):
    """Test if voice works and save if successful"""
    log_alltalk("Testing voice: " + voice_name + " for " + voice_type, "INFO", "test_and_save_voice")
    
    if test_voice_selection(voice_name):
        log_alltalk("Voice test successful: " + voice_name, "SUCCESS", "test_and_save_voice")
        return True
    else:
        log_alltalk("Voice test failed: " + voice_name, "ERROR", "test_and_save_voice")
        return False

def test_voice_loading(voice_name):
    """Test if a voice can be loaded into TTS engine and generate audio"""
    log_alltalk(f"🔄 LOADING VOICE INTO TTS ENGINE: {voice_name}", "INFO", "test_voice_loading")
    
    # Use correct AllTalk API format - Form data with proper field names
    test_params = {
        "text_input": "Voice loading verification test.",
        "character_voice_gen": voice_name,
        "text_filtering": "standard",
        "output_file_name": "voice_load_test",
        "output_file_timestamp": "false"
    }
    
    try:
        api_url = mode_manager.get_api_url("tts-generate")
        log_alltalk(f"Sending voice load test to: {api_url}", "INFO", "test_voice_loading")
        log_alltalk(f"Test parameters: voice='{voice_name}', text='Voice loading verification test.'", "INFO", "test_voice_loading")
        
        # Send as Form data, not JSON - this forces AllTalk to load the voice
        response = requests.post(api_url, data=test_params, timeout=15)  # Longer timeout for loading
        
        if response.status_code == 200:
            log_alltalk(f"✅ VOICE SUCCESSFULLY LOADED INTO TTS ENGINE: {voice_name}", "SUCCESS", "test_voice_loading")
            log_alltalk(f"Server response indicates voice is cached and ready for use", "SUCCESS", "test_voice_loading")
            return True, f"Voice '{voice_name}' loaded and ready"
        else:
            try:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                log_alltalk(f"❌ VOICE LOADING FAILED: {voice_name} - Status: {response.status_code}", "ERROR", "test_voice_loading")
                log_alltalk(f"Server error response: {error_data}", "ERROR", "test_voice_loading")
                return False, f"Voice '{voice_name}' failed to load: {error_data}"
            except:
                return False, f"Voice '{voice_name}' failed to load: HTTP {response.status_code}"
    except requests.exceptions.Timeout:
        log_alltalk(f"❌ VOICE LOADING TIMEOUT: {voice_name} (TTS engine may be busy)", "ERROR", "test_voice_loading")
        return False, f"Voice '{voice_name}' loading timeout - TTS engine may be busy"
    except Exception as e:
        log_alltalk(f"❌ VOICE LOADING ERROR: {voice_name} - {str(e)}", "ERROR", "test_voice_loading")
        return False, f"Voice '{voice_name}' loading error: {str(e)}"

def test_voice_selection(voice_name):
    """Backward compatibility wrapper - calls enhanced voice loading test"""
    success, message = test_voice_loading(voice_name)
    return success


class TGWUIModeManager:
    """Manages TGWUI mode, configuration, and server connection setup."""

    def __init__(self):
        print("[AllTalk TTS] TGWUIModeManager.__init__ called", flush=True)
        
        self.debug_tgwui = False  # General Debugging setting. Default is `False`
        self.debug_func = False  # Print function name as its used. Default is `False`
        self.is_local = self._detect_mode()
        self._setup_config()
        self._setup_server_connection()
        
        # Synchronize voice files on initialization
        if sync_all_voices:
            try:
                log_simple("Synchronizing voice files...")
                voices, added, removed = sync_all_voices()
                # Voice count is already displayed by sync_all_voices()
                log_alltalk("Voice sync completed successfully", "SUCCESS", "voice_sync")
            except Exception as e:
                log_alltalk("Voice sync failed: " + str(e), "ERROR", "voice_sync")
                log_simple("Warning: Voice sync failed: " + str(e))

    def _detect_mode(self):
        """Detects if running as part of an AllTalk installation."""
        try:
            current_dir = Path(__file__).parent
            alltalk_root = current_dir.parent.parent

            # Just check if we're in the right place, don't import
            required_files = [
                alltalk_root / "confignew.json",
                alltalk_root / "script.py",
            ]
            required_folders = [
                alltalk_root / "system",
                alltalk_root / "models",
                alltalk_root / "outputs",
                alltalk_root / "voices",
            ]

            files_exist = all(f.exists() for f in required_files)
            folders_exist = all(f.is_dir() for f in required_folders)

            return files_exist and folders_exist

        except (ImportError, FileNotFoundError) as e:
            # Don't try to use mode_manager here since it doesn't exist yet
            print(f"Error detecting mode: {str(e)}")
            return False

    def _setup_config(self):
        """Loads configuration based on the detected mode (local or remote)."""
        if self.is_local:
            # We're in local AllTalk mode, load from confignew.json
            self.branding = "AllTalk "
            self.server = {
                "protocol": "http://",
                "address": "127.0.0.1:7851",  # Default port
                "timeout": 5,
            }
            
            # Try to load from the main AllTalk config file
            try:
                alltalk_root = Path(__file__).parent.parent.parent
                config_path = alltalk_root / "confignew.json"
                
                if config_path.exists():
                    with open(config_path, "r", encoding="utf8") as config_f:
                        loaded_config = json.load(config_f)
                        
                    # Extract the tgwui section and other needed parts
                    self.config = {
                        "api_def": {
                            "api_port_number": loaded_config.get("api_def", {}).get("api_port_number", 7851),
                            "api_use_legacy_api": loaded_config.get("api_def", {}).get("api_use_legacy_api", False)
                        },
                        "tgwui": loaded_config.get("tgwui", {}),
                        "remote_connection": {
                            "use_legacy_api": False,
                            "server_protocol": "http://",
                            "server_address": "127.0.0.1:7851",
                            "connection_timeout": 5,
                        },
                    }
                    
                    # Ensure all required keys exist with defaults
                    tgwui_defaults = {
                        "tgwui_activate_tts": True,
                        "tgwui_autoplay_tts": True,
                        "tgwui_narrator_enabled": "false",
                        "tgwui_non_quoted_text_is": "narrator",
                        "tgwui_deepspeed_enabled": False,
                        "tgwui_language": "English",
                        "tgwui_lowvram_enabled": False,
                        "tgwui_pitch_set": 0,
                        "tgwui_temperature_set": 0.75,
                        "tgwui_repetitionpenalty_set": 10,
                        "tgwui_generationspeed_set": 1,
                        "tgwui_narrator_voice": "",
                        "tgwui_show_text": True,
                        "tgwui_character_voice": "",
                        "tgwui_rvc_char_voice": "Disabled",
                        "tgwui_rvc_char_pitch": 0,
                        "tgwui_rvc_narr_voice": "Disabled",
                        "tgwui_rvc_narr_pitch": 0,
                    }
                    
                    for key, default in tgwui_defaults.items():
                        if key not in self.config["tgwui"]:
                            self.config["tgwui"][key] = default
                    
                    log_alltalk(f"Loaded config from {config_path}", "SUCCESS", "config_loader")
                    log_alltalk(f"Character voice from config: {self.config['tgwui'].get('tgwui_character_voice', 'not set')}", "INFO", "config_loader")
                    log_alltalk(f"Narrator voice from config: {self.config['tgwui'].get('tgwui_narrator_voice', 'not set')}", "INFO", "config_loader")
                else:
                    raise FileNotFoundError(f"Config file not found at {config_path}")
                    
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"[AllTalk TTS] Error loading local config ({str(e)}), using defaults")
                # Fallback to defaults if config can't be loaded
                self.config = {
                    "api_def": {"api_port_number": 7851, "api_use_legacy_api": False},
                    "tgwui": {
                        "tgwui_activate_tts": True,
                        "tgwui_autoplay_tts": True,
                        "tgwui_narrator_enabled": "false",
                        "tgwui_non_quoted_text_is": "narrator",
                        "tgwui_deepspeed_enabled": False,
                        "tgwui_language": "English",
                        "tgwui_lowvram_enabled": False,
                        "tgwui_pitch_set": 0,
                        "tgwui_temperature_set": 0.75,
                        "tgwui_repetitionpenalty_set": 10,
                        "tgwui_generationspeed_set": 1,
                        "tgwui_narrator_voice": "",
                        "tgwui_show_text": True,
                        "tgwui_character_voice": "",
                        "tgwui_rvc_char_voice": "Disabled",
                        "tgwui_rvc_char_pitch": 0,
                        "tgwui_rvc_narr_voice": "Disabled",
                        "tgwui_rvc_narr_pitch": 0,
                    },
                    "remote_connection": {
                        "use_legacy_api": False,
                        "server_protocol": "http://",
                        "server_address": "127.0.0.1:7851",
                        "connection_timeout": 5,
                    },
                }
        else:
            config_path = Path(__file__).parent / "tgwui_remote_config.json"
            try:
                with open(config_path, "r", encoding="utf8") as config_f:
                    self.config = json.load(config_f)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Error loading remote config ({str(e)}), using defaults")
                self.config = {
                    "branding": "AllTalk ",
                    "tgwui": {
                        "tgwui_activate_tts": True,
                        "tgwui_autoplay_tts": False,
                        "tgwui_show_text": True,
                        "tgwui_narrator_enabled": "false",
                        "tgwui_non_quoted_text_is": "narrator",
                        "tgwui_deepspeed_enabled": False,
                        "tgwui_language": "English",
                        "tgwui_lowvram_enabled": False,
                        "tgwui_pitch_set": 0,
                        "tgwui_temperature_set": 0.75,
                        "tgwui_repetitionpenalty_set": 10,
                        "tgwui_generationspeed_set": 1.0,
                        "tgwui_narrator_voice": "",  # Will be populated from API or saved settings
                        "tgwui_character_voice": "",  # Will be populated from API or saved settings
                        "tgwui_rvc_char_voice": "Disabled",
                        "tgwui_rvc_char_pitch": 0,
                        "tgwui_rvc_narr_voice": "Disabled",
                        "tgwui_rvc_narr_pitch": 0,
                    },
                    "remote_connection": {
                        "server_protocol": "http://",
                        "server_address": "127.0.0.1:7851",
                        "connection_timeout": 5,
                        "use_legacy_api": False,
                    },
                }

            self.branding = self.config["branding"]
            self.server = {
                "protocol": self.config["remote_connection"]["server_protocol"],
                "address": self.config["remote_connection"]["server_address"],
                "timeout": self.config["remote_connection"]["connection_timeout"],
            }

    def _setup_server_connection(self):
        """Sets up the server connection URL."""
        self.server_url = f"{self.server['protocol']}{self.server['address']}"

    def get_api_url(self, endpoint):
        """Returns the full API URL for the given endpoint."""
        return f"{self.server_url}/api/{endpoint}"

    def refresh_config(self):
        """Refresh configuration from disk to ensure in-memory config is current"""
        log_alltalk("Refreshing configuration from disk", "INFO", "refresh_config")
        try:
            old_char_voice = self.config["tgwui"].get("tgwui_character_voice", "")
            old_narr_voice = self.config["tgwui"].get("tgwui_narrator_voice", "")
            
            # Reload config from disk
            self._setup_config()
            
            new_char_voice = self.config["tgwui"].get("tgwui_character_voice", "")
            new_narr_voice = self.config["tgwui"].get("tgwui_narrator_voice", "")
            
            log_alltalk(f"Config refresh - Character voice: {old_char_voice} -> {new_char_voice}", "INFO", "refresh_config")
            log_alltalk(f"Config refresh - Narrator voice: {old_narr_voice} -> {new_narr_voice}", "INFO", "refresh_config")
            
            return True
        except Exception as e:
            log_alltalk(f"Error refreshing config: {str(e)}", "ERROR", "refresh_config")
            return False

    def save_settings(self):
        """Save current settings to appropriate location"""
        if self.is_local:
            # We're in local AllTalk mode, save to confignew.json
            try:
                alltalk_root = Path(__file__).parent.parent.parent
                config_path = alltalk_root / "confignew.json"
                
                # Load the full config file
                with open(config_path, "r", encoding="utf8") as config_f:
                    full_config = json.load(config_f)
                
                # Update only the tgwui section
                full_config["tgwui"] = self.config["tgwui"]
                
                # Write back the updated config
                with open(config_path, "w", encoding="utf8") as config_f:
                    json.dump(full_config, config_f, indent=4, ensure_ascii=False)
                
                log_alltalk(f"Settings saved to {config_path}", "SUCCESS", "save_settings")
                log_alltalk(f"Saved character voice: {self.config['tgwui'].get('tgwui_character_voice', 'not set')}", "INFO", "save_settings")
                log_alltalk(f"Saved narrator voice: {self.config['tgwui'].get('tgwui_narrator_voice', 'not set')}", "INFO", "save_settings")
                
                # Force immediate config refresh to sync in-memory config
                log_alltalk("Performing immediate config refresh after save", "INFO", "save_settings")
                self.refresh_config()
                
            except Exception as e:
                log_alltalk(f"Error saving settings: {str(e)}", "ERROR", "save_settings")
                print(f"[AllTalk TTS] Error saving settings: {str(e)}")
        else:
            # In remote mode, save to local config file
            settings = {
                "branding": self.branding,
                "tgwui": self.config["tgwui"],
                "remote_connection": {
                    "server_protocol": self.server["protocol"],
                    "server_address": self.server["address"],
                    "connection_timeout": self.server["timeout"],
                    "use_legacy_api": self.config["remote_connection"][
                        "use_legacy_api"
                    ],
                },
            }
            config_path = Path(__file__).parent / "tgwui_remote_config.json"
            
            # Log before saving for debugging
            log_alltalk(f"Saving remote config with character voice: {settings['tgwui'].get('tgwui_character_voice', 'not set')}", "INFO", "save_settings")
            log_alltalk(f"Saving remote config with narrator voice: {settings['tgwui'].get('tgwui_narrator_voice', 'not set')}", "INFO", "save_settings")
            
            try:
                with open(config_path, "w", encoding="utf8") as save_f:
                    json.dump(settings, save_f, indent=4)
                    save_f.flush()  # Force write to disk
                    os.fsync(save_f.fileno())  # Ensure it's written to disk
                
                # Verify the file was written correctly
                with open(config_path, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    saved_char_voice = saved_config.get('tgwui', {}).get('tgwui_character_voice', '')
                    saved_narr_voice = saved_config.get('tgwui', {}).get('tgwui_narrator_voice', '')
                
                log_alltalk(f"Remote settings saved to {config_path}", "SUCCESS", "save_settings")
                log_alltalk(f"Verified saved character voice: {saved_char_voice}", "INFO", "save_settings")
                log_alltalk(f"Verified saved narrator voice: {saved_narr_voice}", "INFO", "save_settings")
                
                # Force immediate config refresh to sync in-memory config
                log_alltalk("Performing immediate config refresh after save", "INFO", "save_settings")
                self.refresh_config()
                
            except Exception as e:
                log_alltalk(f"Error saving remote settings: {str(e)}", "ERROR", "save_settings")
                print(f"[AllTalk TTS] Error saving remote settings: {str(e)}")


# Initialize mode manager at startup
print("[AllTalk TTS] About to create TGWUIModeManager instance", flush=True)
mode_manager = TGWUIModeManager()
log_simple("TGWUIModeManager instance created successfully")

##########################
# Central print function #
##########################


def print_func(message, message_type="standard", component="TTS", debug_type=None):
    """Centralized print function for AllTalk messages

    Args:
        message (str): The message to print
        message_type (str): Type of message ("standard", "warning", "error", "debug")
        component (str): Component identifier ("TTS", "ENG", "Server", etc.)
        debug_type (str, optional): Can be supplied on the call to specify things like:
            - The function that is sending the debug request.
            - The operation taking place
    """
    prefix = f"[{mode_manager.branding}{component}] "

    if message_type == "warning":
        print(f"{prefix}\033[91mWarning\033[0m {message}")
    elif message_type == "error":
        print(f"{prefix}\033[91mError\033[0m {message}")
    elif message_type == "debug":
        if debug_type is None:
            debug_type = ""
        color = "\033[92m" if "Function entry" in message else "\033[93m"
        print(f"{prefix}\033[94mDebug\033[0m {color}{debug_type}\033[0m {message}")
    else:  # standard message
        print(f"{prefix}{message}")


def debug_func_entry():
    """Print debug message for function entry if debug_func is enabled/true"""
    if mode_manager.debug_func:
        print_func(
            "Function entry",
            "debug",
            debug_type=inspect.currentframe().f_back.f_code.co_name,
        )


# Load languages
with open(Path(__file__).parent / "languages.json", encoding="utf8") as f:
    languages = json.load(f)

# Setup other globals
process_lock = threading.Lock()
models_available = None
alltalk_settings = None
current_model_loaded = None
tts_model_loaded = None


def get_alltalk_settings():
    """Fetches current AllTalk settings and updates global configurations."""
    if mode_manager.debug_func:
        print_func(
            "Function entry", "debug", debug_type=inspect.currentframe().f_code.co_name
        )
    global current_model_loaded, models_available

    def log_error(message, status_code=None):
        """Helper function for consistent error logging"""
        if status_code:
            print_func(f"{message} Status code:\n{status_code}", message_type="warning")
        else:
            print_func(f"{message}", message_type="warning")

    try:
        # Make all API requests
        api_calls = {
            "voices": requests.get(
                mode_manager.get_api_url("voices"),
                timeout=mode_manager.server["timeout"],
            ),
            "rvc": requests.get(
                mode_manager.get_api_url("rvcvoices"),
                timeout=mode_manager.server["timeout"],
            ),
            "settings": requests.get(
                mode_manager.get_api_url("currentsettings"),
                timeout=mode_manager.server["timeout"],
            ),
        }

        # Check if all responses are successful
        if all(response.status_code == 200 for response in api_calls.values()):
            try:
                voices_data = api_calls["voices"].json()
                rvcvoices_data = api_calls["rvc"].json()
                settings_data = api_calls["settings"].json()

                # Update global variables
                models_available = [
                    model["name"] for model in settings_data["models_available"]
                ]
                current_model_loaded = settings_data["current_model_loaded"]

                # Update config ONLY if voices are empty or invalid (no hardcoded defaults)
                # This preserves user selections while ensuring we have valid voices
                log_alltalk(f"Checking voice config - Local mode: {mode_manager.is_local}", "INFO", "get_alltalk_settings")
                
                current_char_voice = mode_manager.config["tgwui"]["tgwui_character_voice"]
                current_narr_voice = mode_manager.config["tgwui"]["tgwui_narrator_voice"]
                
                # Clear invalid voices instead of replacing them with fallbacks
                settings_changed = False
                
                if current_char_voice and current_char_voice not in voices_data["voices"]:
                    # Invalid voice found - clear it so user can select a new one
                    mode_manager.config["tgwui"]["tgwui_character_voice"] = ""
                    log_alltalk(f"Character voice '{current_char_voice}' not found, cleared for user selection", "WARNING", "get_alltalk_settings")
                    settings_changed = True
                elif current_char_voice:
                    log_alltalk(f"Character voice already set and valid: {current_char_voice}", "INFO", "get_alltalk_settings")
                elif not current_char_voice:
                    log_alltalk("Character voice empty - user needs to select", "INFO", "get_alltalk_settings")
                
                if current_narr_voice and current_narr_voice not in voices_data["voices"]:
                    # Invalid voice found - clear it so user can select a new one
                    mode_manager.config["tgwui"]["tgwui_narrator_voice"] = ""
                    log_alltalk(f"Narrator voice '{current_narr_voice}' not found, cleared for user selection", "WARNING", "get_alltalk_settings")
                    settings_changed = True
                elif current_narr_voice:
                    log_alltalk(f"Narrator voice already set and valid: {current_narr_voice}", "INFO", "get_alltalk_settings")
                elif not current_narr_voice:
                    log_alltalk("Narrator voice empty - user needs to select", "INFO", "get_alltalk_settings")
                
                # Handle RVC voices similarly
                current_rvc_char = mode_manager.config["tgwui"].get("tgwui_rvc_char_voice", "Disabled")
                if current_rvc_char == "" or (current_rvc_char != "Disabled" and current_rvc_char not in rvcvoices_data["rvcvoices"]):
                    mode_manager.config["tgwui"]["tgwui_rvc_char_voice"] = (
                        rvcvoices_data["rvcvoices"][0] if rvcvoices_data["rvcvoices"] else "Disabled"
                    )
                
                current_rvc_narr = mode_manager.config["tgwui"].get("tgwui_rvc_narr_voice", "Disabled")
                if current_rvc_narr == "" or (current_rvc_narr != "Disabled" and current_rvc_narr not in rvcvoices_data["rvcvoices"]):
                    mode_manager.config["tgwui"]["tgwui_rvc_narr_voice"] = (
                        rvcvoices_data["rvcvoices"][0] if rvcvoices_data["rvcvoices"] else "Disabled"
                    )
                
                # Only save when we cleared invalid voices
                if settings_changed:
                    mode_manager.save_settings()
                    log_alltalk("Invalid voices cleared and settings saved", "INFO", "get_alltalk_settings")

                return AllTalkServerSettings.from_api_response(
                    voices_data, rvcvoices_data, settings_data
                )
            except json.JSONDecodeError as e:
                log_error(f"Failed to decode JSON response: {e}")
                return AllTalkServerSettings()
        else:
            # Log specific failures
            log_error(f"Failed to retrieve {mode_manager.branding}settings from API.")
            for name, response in api_calls.items():
                if response.status_code != 200:
                    log_error(
                        f"Failed to retrieve {name} from API", response.status_code
                    )
            return AllTalkServerSettings()

    except (RequestException, ConnectionError) as e:
        log_error(f"Unable to connect to the {mode_manager.branding}server", str(e))
        return AllTalkServerSettings()


class AllTalkServerSettings:
    """Represents and manages settings for the AllTalk server."""

    def __init__(self):
        """Initializes the TGWUIModeManager with default settings and server connection."""
        self.voices = []  # Will be populated from API, no hardcoded defaults
        self.rvcvoices = ["Disabled"]
        self.models_available = ["xtts"]
        self.current_model_loaded = "xtts"
        self.manufacturer_name = ""

        # Engine capabilities
        self.deepspeed_capable = False
        self.deepspeed_available = False
        self.deepspeed_enabled = False
        self.languages_capable = False
        self.multivoice_capable = False
        self.multimodel_capable = False
        self.streaming_capable = False
        self.ttsengines_installed = False

        # Generation settings
        self.generationspeed_capable = False
        self.generationspeed_set = 1.0
        self.lowvram_capable = False
        self.lowvram_enabled = False
        self.pitch_capable = False
        self.pitch_set = 0
        self.repetitionpenalty_capable = False
        self.repetitionpenalty_set = 10.0
        self.temperature_capable = False
        self.temperature_set = 0.75

    @classmethod
    def from_api_response(cls, voices_data, rvcvoices_data, settings_data):
        """Creates an AllTalkServerSettings instance from API response data."""
        debug_func_entry()
        if mode_manager.debug_func:
            print_func(
                "Function entry",
                "debug",
                debug_type=inspect.currentframe().f_code.co_name,
            )
        settings = cls()

        # Update voice and model information
        settings.voices = sorted(voices_data["voices"])
        settings.rvcvoices = rvcvoices_data["rvcvoices"]
        settings.models_available = [
            model["name"] for model in settings_data["models_available"]
        ]
        settings.current_model_loaded = settings_data["current_model_loaded"]
        settings.manufacturer_name = settings_data.get("manufacturer_name", "")

        # Update capabilities and settings
        settings_mapping = {
            # Capabilities
            "deepspeed_capable": ("deepspeed_capable", False),
            "deepspeed_available": ("deepspeed_available", False),
            "deepspeed_enabled": ("deepspeed_enabled", False),
            "languages_capable": ("languages_capable", False),
            "multivoice_capable": ("multivoice_capable", False),
            "multimodel_capable": ("multimodel_capable", False),
            "streaming_capable": ("streaming_capable", False),
            "ttsengines_installed": ("ttsengines_installed", False),
            # Generation settings
            "generationspeed_capable": ("generationspeed_capable", False),
            "generationspeed_set": ("generationspeed_set", 1.0),
            "lowvram_capable": ("lowvram_capable", False),
            "lowvram_enabled": ("lowvram_enabled", False),
            "pitch_capable": ("pitch_capable", False),
            "pitch_set": ("pitch_enabled", 0),
            "repetitionpenalty_capable": ("repetitionpenalty_capable", False),
            "repetitionpenalty_set": ("repetitionpenalty_set", 10.0),
            "temperature_capable": ("temperature_capable", False),
            "temperature_set": ("temperature_set", 0.75),
        }

        # Update all settings from the mapping
        for attr, (key, default) in settings_mapping.items():
            setattr(settings, attr, settings_data.get(key, default))

        return settings


# Print Spashscreen to console if running as Remote Extension
# pylint: disable=line-too-long,anomalous-backslash-in-string
if not mode_manager.is_local:
    print_func(
        "\033[94m     _    _ _ \033[1;35m_____     _ _     \033[0m  _____ _____ ____  "
    )  # pylint: disable=line-too-long anomalous-backslash-in-string
    print_func(
        "\033[94m    / \  | | |\033[1;35m_   _|_ _| | | __ \033[0m |_   _|_   _/ ___| "
    )  # pylint: disable=line-too-long anomalous-backslash-in-string
    print_func(
        "\033[94m   / _ \ | | |\033[1;35m | |/ _` | | |/ / \033[0m   | |   | | \___ \ "
    )  # pylint: disable=line-too-long anomalous-backslash-in-string
    print_func(
        "\033[94m  / ___ \| | |\033[1;35m | | (_| | |   <  \033[0m   | |   | |  ___) |"
    )  # pylint: disable=line-too-long anomalous-backslash-in-string
    print_func(
        "\033[94m /_/   \_\_|_|\033[1;35m |_|\__,_|_|_|\_\ \033[0m   |_|   |_| |____/ "
    )  # pylint: disable=line-too-long anomalous-backslash-in-string
    print_func("")
    print_func(
        f"\033[92m{mode_manager.branding}startup Mode   : \033[93mText-Gen-webui Remote\033[0m"
    )
    print_func("")
# pylint: enable=line-too-long,anomalous-backslash-in-string

def stop_generate_tts():
    """Sends request to stop current TTS generation"""
    debug_func_entry()
    api_url = mode_manager.get_api_url("stop-generation")

    if mode_manager.debug_tgwui:
        print_func(
            "Attempting to stop TTS generation",
            message_type="debug",
            debug_type="stop_generate_tts",
        )

    try:
        response = requests.put(api_url, timeout=mode_manager.server["timeout"])
        if response.status_code == 200:
            log_alltalk("Stop generation successful", "SUCCESS", "stop_generate_tts")
            return response.json()["message"]
        else:
            print_func(
                f"Failed to stop generation. Status code:\n{response.status_code}",
                message_type="warning",
            )
            return {"message": "Failed to stop generation"}
    except (RequestException, ConnectionError) as e:
        print_func(
            f"Unable to connect to the {mode_manager.branding}server. Status code:\n{str(e)}",
            message_type="warning",
        )
        return {"message": "Failed to stop generation"}


def send_reload_request(value_sent):
    """Requests AllTalk server to load a different TTS model"""
    debug_func_entry()
    global tts_model_loaded
    if not process_lock.acquire(blocking=False):
        return {
            "status": "error",
            "message": "Server is currently busy. Try again in a few seconds.",
        }
    try:
        tts_model_loaded = False
        url = mode_manager.get_api_url("reload")
        payload = {"tts_method": value_sent}

        if mode_manager.debug_tgwui:
            print_func(
                f"Requesting model reload to: {value_sent}",
                message_type="debug",
                debug_type="send_reload_request",
            )

        response = requests.post(url, params=payload)
        log_alltalk("Model reload request to: " + url, "DEBUG", "send_reload_request")
        response.raise_for_status()
        tts_model_loaded = True
    except requests.exceptions.RequestException as e:
        print_func(
            f"Error during request to webserver process: Status code:\n{e}",
            message_type="warning",
        )
        tts_model_loaded = True
        return {"status": "error", "message": str(e)}
    finally:
        process_lock.release()


def send_lowvram_request(value_sent):
    """Toggles low VRAM mode in AllTalk server"""
    debug_func_entry()
    global tts_model_loaded
    if not process_lock.acquire(blocking=False):
        return {
            "status": "error",
            "message": "Server is currently busy. Try again in a few seconds.",
        }
    try:
        tts_model_loaded = False
        audio_path = this_dir / (
            "lowvramenabled.wav" if value_sent else "lowvramdisabled.wav"
        )

        if mode_manager.debug_tgwui:
            print_func(
                f"Setting low VRAM mode to: {value_sent}",
                message_type="debug",
                debug_type="send_lowvram_request",
            )

        url = mode_manager.get_api_url(
            f"lowvramsetting?new_low_vram_value={value_sent}"
        )
        response = requests.post(url, headers={"Content-Type": "application/json"})
        response.raise_for_status()

        json_response = response.json()
        if json_response.get("status") == "lowvram-success":
            tts_model_loaded = True

        return f'<audio src="file/{audio_path}" controls autoplay></audio>'
    except requests.exceptions.RequestException as e:
        print_func(
            f"Error during request to webserver process: Status code:\n{e}",
            message_type="warning",
        )
        return {"status": "error", "message": str(e)}
    finally:
        process_lock.release()


def send_deepspeed_request(value_sent):
    """Toggles DeepSpeed acceleration in AllTalk server"""
    debug_func_entry()
    global tts_model_loaded
    if not process_lock.acquire(blocking=False):
        return {
            "status": "error",
            "message": "Server is currently busy. Try again in a few seconds.",
        }
    try:
        tts_model_loaded = False
        audio_path = this_dir / (
            "deepspeedenabled.wav" if value_sent else "deepspeeddisabled.wav"
        )

        if mode_manager.debug_tgwui:
            print_func(
                f"Setting DeepSpeed to: {value_sent}",
                message_type="debug",
                debug_type="send_deepspeed_request",
            )

        url = mode_manager.get_api_url(f"deepspeed?new_deepspeed_value={value_sent}")
        response = requests.post(url, headers={"Content-Type": "application/json"})
        response.raise_for_status()

        json_response = response.json()
        if json_response.get("status") == "deepspeed-success":
            tts_model_loaded = True

        process_lock.release()
        return f'<audio src="file/{audio_path}" controls autoplay></audio>'
    except requests.exceptions.RequestException as e:
        print_func(
            f"Error during request to webserver process: Status code:\n{e}",
            message_type="warning",
        )
        return {"status": "error", "message": str(e)}
    finally:
        process_lock.release()


def send_and_generate(
    gen_text,
    gen_character_voice,
    gen_rvccharacter_voice,
    gen_rvccharacter_pitch,
    gen_narrator_voice,
    gen_rvcnarrator_voice,
    gen_rvcnarrator_pitch,
    gen_narrator_activated,
    gen_textnotinisde,
    gen_repetition,
    gen_language,
    gen_filter,
    gen_speed,
    gen_pitch,
    gen_autoplay,
    gen_autoplay_vol,
    gen_file_name,
    gen_temperature,
    gen_filetimestamp,
    gen_stream,
    gen_stopcurrentgen,
):
    """Sends text to AllTalk server for TTS generation"""
    debug_func_entry()
    api_url = mode_manager.get_api_url("tts-generate")

    if mode_manager.debug_tgwui:
        print_func(
            "Starting TTS generation request",
            message_type="debug",
            debug_type="send_and_generate",
        )

    if gen_stopcurrentgen:
        stop_generate_tts()

    # Removed unnecessary save_settings() here - settings should only be saved when explicitly changed by user

    if gen_stream == "true":
        api_url = mode_manager.get_api_url("tts-generate-streaming")
        encoded_text = requests.utils.quote(gen_text)
        streaming_url = f"{api_url}?text={encoded_text}&voice={gen_character_voice}&language={gen_language}&output_file={gen_file_name}"
        return streaming_url, str("TTS Streaming Audio Generated")

    # Parameter validation and sanitization
    safe_filename = str(gen_file_name)
    if not safe_filename or safe_filename in ["None", "null", ""]:
        safe_filename = "TTSOUT_"
        log_alltalk(f"Invalid filename '{gen_file_name}', using fallback: {safe_filename}", "WARNING", "send_and_generate")
    
    # Ensure narrator_enabled is a valid boolean string
    narrator_enabled_str = str(gen_narrator_activated).lower()
    if narrator_enabled_str not in ["true", "false"]:
        narrator_enabled_str = "false"
        log_alltalk(f"Invalid narrator_enabled value '{gen_narrator_activated}', using fallback: false", "WARNING", "send_and_generate")
    
    # Ensure text_not_inside has a valid value
    valid_text_not_inside = ["character", "narrator", "silent"]
    if gen_textnotinisde not in valid_text_not_inside:
        gen_textnotinisde = "character"  # fallback to character
        log_alltalk(f"Invalid text_not_inside value, using fallback: character", "WARNING", "send_and_generate")
    
    # Validate and clean text input
    clean_text_input = gen_text[0] if isinstance(gen_text, tuple) else gen_text
    if not clean_text_input or len(str(clean_text_input).strip()) == 0:
        log_alltalk("Empty text input provided", "ERROR", "send_and_generate")
        return None, "Error: Empty text input"
    
    data = {
        "text_input": clean_text_input,
        "text_filtering": gen_filter,
        "character_voice_gen": gen_character_voice,
        "rvccharacter_voice_gen": gen_rvccharacter_voice,
        "rvccharacter_pitch": gen_rvccharacter_pitch,
        "narrator_enabled": narrator_enabled_str,
        "narrator_voice_gen": gen_narrator_voice,
        "rvcnarrator_voice_gen": gen_rvcnarrator_voice,
        "rvcnarrator_pitch": gen_rvcnarrator_pitch,
        "text_not_inside": gen_textnotinisde,
        "language": gen_language,
        "output_file_name": safe_filename,
        "output_file_timestamp": str(gen_filetimestamp).lower(),
        "autoplay": str(gen_autoplay).lower(),
        "autoplay_volume": str(gen_autoplay_vol),
        "speed": str(gen_speed),
        "pitch": str(gen_pitch),
        "temperature": str(gen_temperature),
        "repetition_penalty": str(gen_repetition),
    }

    # Always log parameters for troubleshooting (not just in debug mode)
    log_alltalk("=== TTS Generation Request Parameters ===", "INFO", "send_and_generate")
    for key, value in data.items():
        # Truncate long text but show other parameters fully
        if key == "text_input" and len(str(value)) > 100:
            log_alltalk(f"{key}: {str(value)[:100]}...", "INFO", "send_and_generate")
        else:
            log_alltalk(f"{key}: {value}", "INFO", "send_and_generate")
    log_alltalk(f"API URL: {api_url}", "INFO", "send_and_generate")
    
    if mode_manager.debug_tgwui:
        print_func(
            "Generation request parameters:",
            message_type="debug",
            debug_type="send_and_generate",
        )
        for key, value in data.items():
            print_func(
                f"{key}: {value}", message_type="debug", debug_type="send_and_generate"
            )

    try:
        log_alltalk("Sending TTS request to AllTalk API...", "INFO", "send_and_generate")
        response = requests.post(api_url, data=data)
        
        # Log response details for troubleshooting
        log_alltalk(f"API Response Status: {response.status_code}", "INFO", "send_and_generate")
        
        if response.status_code == 422:
            log_alltalk("422 Error - Parameter validation failed", "ERROR", "send_and_generate")
            log_alltalk(f"Response body: {response.text}", "ERROR", "send_and_generate")
            
            # Try to identify specific parameter issues
            try:
                error_details = response.json()
                log_alltalk(f"Error details: {error_details}", "ERROR", "send_and_generate")
            except:
                log_alltalk("Could not parse error response as JSON", "ERROR", "send_and_generate")
            
            # Try with simplified parameters (similar to preview function)
            log_alltalk("Attempting fallback with simplified parameters...", "INFO", "send_and_generate")
            fallback_data = {
                "text_input": clean_text_input,
                "text_filtering": "standard",
                "character_voice_gen": gen_character_voice,
                "narrator_enabled": "false", 
                "text_not_inside": "character",
                "language": gen_language or "en",
                "output_file_name": "TTSOUT_fallback",
                "output_file_timestamp": "false",
                "autoplay": "false",
                "autoplay_volume": "0.8",
                "speed": str(gen_speed),
                "pitch": str(gen_pitch),
                "temperature": str(gen_temperature),
                "repetition_penalty": str(gen_repetition),
            }
            
            log_alltalk("=== Fallback Parameters ===", "INFO", "send_and_generate")
            for key, value in fallback_data.items():
                log_alltalk(f"{key}: {value}", "INFO", "send_and_generate")
            
            try:
                fallback_response = requests.post(api_url, data=fallback_data)
                if fallback_response.status_code == 200:
                    log_alltalk("Fallback request successful!", "SUCCESS", "send_and_generate")
                    result = fallback_response.json()
                    # Continue with normal processing
                else:
                    log_alltalk(f"Fallback also failed with status: {fallback_response.status_code}", "ERROR", "send_and_generate")
                    response.raise_for_status()  # Raise the original error
            except Exception as fallback_error:
                log_alltalk(f"Fallback request failed: {str(fallback_error)}", "ERROR", "send_and_generate")
                response.raise_for_status()  # Raise the original error
        else:
            response.raise_for_status()
        result = response.json()
        log_alltalk("TTS request successful", "SUCCESS", "send_and_generate")

        if gen_autoplay == "true":
            return None, str("TTS Audio Generated (Played remotely)")

        if mode_manager.config["remote_connection"]["use_legacy_api"]:
            return result["output_file_url"], str("TTS Audio Generated")
        else:
            output_file_url = f"{mode_manager.server_url}{result['output_file_url']}"
            return output_file_url, str("TTS Audio Generated")
    except (RequestException, ConnectionError) as e:
        print_func(
            f"Error occurred during the API request: Status code:\n{str(e)}",
            message_type="warning",
        )
        return None, str("Error occurred during the API request")


def output_modifier(string, state):
    """Modifies TGWUI output to include TTS audio"""
    debug_func_entry()
    
    # Input validation
    if string is None:
        print_func("Error: Received no text input from TGWUI so cannot generate TTS.", message_type="error")
        print_func(f"Input text first 100 char's: {string[:100]}...", message_type="error")
        return string    
    
    if not mode_manager.config["tgwui"]["tgwui_activate_tts"]:
        return string

    # Log generated text to console (always visible)
    clean_text_preview = string[:200] + "..." if len(string) > 200 else string
    log_simple(clean_text_preview.strip())

    # Store original string before any processing
    original_string = string

    if mode_manager.debug_tgwui:
        print_func(
            "Processing text for TTS generation",
            message_type="debug",
            debug_type="output_modifier",
        )

    # Strip out Images so only TTS is sent to the TTS engine
    cleaned_text = tgwui_extract_and_remove_images(string)
    if cleaned_text is None:
        print_func("Error: Image processing resulted in no text to generate TTS", message_type="error")
        print_func(f"Input text first 100 char's: {cleaned_text[:100]}...", message_type="error")
        return string
    
    # Enforce AllTalk API 2000 character limit to prevent 400 errors
    MAX_TTS_LENGTH = 1900  # Leave buffer for safety
    if len(cleaned_text) > MAX_TTS_LENGTH:
        original_length = len(cleaned_text)
        cleaned_text = cleaned_text[:MAX_TTS_LENGTH] + "..."
        log_alltalk(f"Text truncated from {original_length} to {len(cleaned_text)} characters (API limit: 2000)", "WARNING", "output_modifier")
    else:
        log_alltalk(f"Text length: {len(cleaned_text)} characters (within API limit)", "INFO", "output_modifier")    

    # FORCE config refresh before reading voice to ensure we have latest settings
    log_alltalk("Forcing config refresh before reading voice settings", "INFO", "output_modifier")
    mode_manager.refresh_config()
    
    # Get current settings with logging to debug voice selection issue
    language_code = languages.get(mode_manager.config["tgwui"]["tgwui_language"])
    character_voice = mode_manager.config["tgwui"]["tgwui_character_voice"]
    rvc_character_voice = mode_manager.config["tgwui"]["tgwui_rvc_char_voice"]
    rvc_character_pitch = mode_manager.config["tgwui"]["tgwui_rvc_char_pitch"]
    narrator_voice = mode_manager.config["tgwui"]["tgwui_narrator_voice"]
    rvc_narrator_voice = mode_manager.config["tgwui"]["tgwui_rvc_narr_voice"]
    rvc_narrator_pitch = mode_manager.config["tgwui"]["tgwui_rvc_narr_pitch"]
    narrator_enabled = mode_manager.config["tgwui"]["tgwui_narrator_enabled"]
    text_not_inside = mode_manager.config["tgwui"]["tgwui_non_quoted_text_is"]
    repetition_policy = mode_manager.config["tgwui"]["tgwui_repetitionpenalty_set"]
    speed = mode_manager.config["tgwui"]["tgwui_generationspeed_set"]
    pitch = mode_manager.config["tgwui"]["tgwui_pitch_set"]
    temperature = mode_manager.config["tgwui"]["tgwui_temperature_set"]
    
    # Use temporary fallback if voices are empty (don't save these fallbacks)
    temp_character_voice = character_voice
    temp_narrator_voice = narrator_voice
    
    if not character_voice:
        # Get available voices for temporary fallback
        try:
            settings = get_alltalk_settings()
            if settings and settings.voices and len(settings.voices) > 0:
                temp_character_voice = settings.voices[0]
                log_alltalk(f"Using temporary character voice fallback: {temp_character_voice}", "INFO", "output_modifier")
            else:
                log_alltalk("No voices available for character fallback", "WARNING", "output_modifier")
        except Exception as e:
            log_alltalk(f"Error getting fallback voices: {str(e)}", "ERROR", "output_modifier")
    
    if not narrator_voice:
        try:
            settings = get_alltalk_settings()
            if settings and settings.voices and len(settings.voices) > 0:
                temp_narrator_voice = settings.voices[0]
                log_alltalk(f"Using temporary narrator voice fallback: {temp_narrator_voice}", "INFO", "output_modifier")
            else:
                log_alltalk("No voices available for narrator fallback", "WARNING", "output_modifier")
        except Exception as e:
            log_alltalk(f"Error getting fallback voices: {str(e)}", "ERROR", "output_modifier")
    
    # Enhanced voice tracking logging - show config source vs actual usage
    log_alltalk(f"=== CHAT VOICE TRACKING ===", "INFO", "output_modifier")
    log_alltalk(f"Config character_voice: {character_voice}", "INFO", "output_modifier")
    log_alltalk(f"Config narrator_voice: {narrator_voice}", "INFO", "output_modifier")
    log_alltalk(f"Actual character_voice used: {temp_character_voice}", "INFO", "output_modifier")
    log_alltalk(f"Actual narrator_voice used: {temp_narrator_voice}", "INFO", "output_modifier")
    
    # Check if voice was overridden due to fallback
    if temp_character_voice != character_voice:
        log_alltalk(f"CHARACTER VOICE FALLBACK: '{character_voice}' -> '{temp_character_voice}'", "WARNING", "output_modifier")
    if temp_narrator_voice != narrator_voice:
        log_alltalk(f"NARRATOR VOICE FALLBACK: '{narrator_voice}' -> '{temp_narrator_voice}'", "WARNING", "output_modifier")
    log_alltalk(f"=== END VOICE TRACKING ===", "INFO", "output_modifier")

    if mode_manager.debug_tgwui:
        print_func(
            f"Using character voice: {character_voice}, narrator voice: {narrator_voice}",
            message_type="debug",
            debug_type="output_modifier",
        )
        print_func(
            f"Text length: {len(cleaned_text)} characters",
            message_type="debug",
            debug_type="output_modifier",
        )

    # Lock and process TTS request
    if process_lock.acquire(blocking=False):
        try:
            output_file = (state["character_menu"] if "character_menu" in state else str("TTSOUT_"))
            output_file = (state["character_menu"] if "character_menu" in state and state["character_menu"] is not None else "TTSOUT_")
            output_file = sanitize_windows_filename(output_file) # Ensure filenames dont hit any Windows file name limits

            generate_response, status_message = send_and_generate(
                cleaned_text,
                temp_character_voice,  # Use temporary fallback if needed
                rvc_character_voice,
                rvc_character_pitch,
                temp_narrator_voice,   # Use temporary fallback if needed
                rvc_narrator_voice,
                rvc_narrator_pitch,
                narrator_enabled,
                text_not_inside,
                repetition_policy,
                language_code,
                "html",
                speed,
                pitch,
                False,
                0.8,
                output_file,
                temperature,
                True,
                False,
                False,
            )

            if status_message == "TTS Audio Generated":
                autoplay = (
                    "autoplay"
                    if mode_manager.config["tgwui"]["tgwui_autoplay_tts"]
                    else ""
                )
                string = (
                    f'<audio src="{generate_response}" controls {autoplay}></audio>'
                )

                if mode_manager.config["tgwui"]["tgwui_show_text"]:
                    string += f'\n\n{original_string}'  # Use original_string

                if string is None:
                    print_func("Error: Final processed text is None after image reinsertion", message_type="error")
                    print_func(f"Input text first 100 char's: {string[:100]}...", message_type="error")
                    return string

                shared.processing_message = "*Is typing...*"
                return string
            else:
                print_func(
                    f"Audio generation failed. Status code:\n{status_message}",
                    message_type="warning",
                )
        finally:
            process_lock.release()
    else:
        print_func(
            "Audio generation is already in progress. Please wait.",
            message_type="warning",
        )
        return

img_pattern = r'<img[^>]*src\s*=\s*["\'][^"\'>]+["\'][^>]*>'

def tgwui_extract_and_remove_images(text):
    """Extracts and removes image tags from text for clean TTS processing"""
    debug_func_entry()
    cleaned_text = re.sub(img_pattern, "", text)

    if mode_manager.debug_tgwui:
        print_func(
            f"Found {len(re.findall(img_pattern, text))} images in text",
            message_type="debug",
            debug_type="extract_images",
        )

    return cleaned_text  # Just return the cleaned text

def sanitize_windows_filename(original_name):
    # First conversion
    filename = original_name.replace(" ", "_")
    # Remove invalid characters
    filename = re.sub(r'[^a-zA-Z0-9_]', '', filename)
    
    # Check for Windows reserved names
    reserved = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 
               'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 
               'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
    
    if filename.upper() in reserved:
        filename = f"_{filename}"
    
    # Use TTSOUT_ if empty
    filename = filename or "TTSOUT_"
    
    # Print if changes were made
    if original_name != filename:
        print_func(f"Character name '{original_name}' contained special characters - sanitized to '{filename}'", message_type="warning")
    
    return filename

def apply_voice_to_chat():
    """Force immediate voice synchronization for chat TTS"""
    log_alltalk("Manual voice application to chat triggered", "INFO", "apply_voice_to_chat")
    
    # Force config refresh
    if mode_manager.refresh_config():
        current_char = mode_manager.config["tgwui"]["tgwui_character_voice"]
        current_narr = mode_manager.config["tgwui"]["tgwui_narrator_voice"]
        log_alltalk(f"Voice application successful - Character: {current_char}, Narrator: {current_narr}", "SUCCESS", "apply_voice_to_chat")
        return f"✅ Voice applied: {current_char}"
    else:
        log_alltalk("Voice application failed - config refresh error", "ERROR", "apply_voice_to_chat")
        return "❌ Failed to apply voice changes"

def voice_preview(string):
    """Generates a preview of the selected voice settings"""
    # debug_func_entry()
    print("in voice preview function")
    if not mode_manager.config["tgwui"]["tgwui_activate_tts"]:
        return string

    if mode_manager.debug_tgwui:
        print_func(
            "Generating voice preview", message_type="debug", debug_type="voice_preview"
        )

    language_code = languages.get(mode_manager.config["tgwui"]["tgwui_language"])
    if not string:
        string = random_sentence()

    # Enhanced voice tracking for preview comparison with chat
    preview_char_voice = mode_manager.config["tgwui"]["tgwui_character_voice"]
    preview_narr_voice = mode_manager.config["tgwui"]["tgwui_narrator_voice"]
    log_alltalk(f"=== PREVIEW VOICE TRACKING ===", "INFO", "voice_preview")
    log_alltalk(f"Preview character_voice: {preview_char_voice}", "INFO", "voice_preview")
    log_alltalk(f"Preview narrator_voice: {preview_narr_voice}", "INFO", "voice_preview")
    log_alltalk(f"=== END PREVIEW TRACKING ===", "INFO", "voice_preview")

    if mode_manager.debug_tgwui:
        print_func(
            f"Preview text: {string}", message_type="debug", debug_type="voice_preview"
        )

    generate_response, status_message = send_and_generate(
        string,
        mode_manager.config["tgwui"]["tgwui_character_voice"],
        mode_manager.config["tgwui"]["tgwui_rvc_char_voice"],
        mode_manager.config["tgwui"]["tgwui_rvc_char_pitch"],
        mode_manager.config["tgwui"]["tgwui_narrator_voice"],
        mode_manager.config["tgwui"]["tgwui_rvc_narr_voice"],
        mode_manager.config["tgwui"]["tgwui_rvc_narr_pitch"],
        False,
        "character",
        mode_manager.config["tgwui"]["tgwui_repetitionpenalty_set"],
        language_code,
        "standard",
        mode_manager.config["tgwui"]["tgwui_generationspeed_set"],
        mode_manager.config["tgwui"]["tgwui_pitch_set"],
        False,
        0.8,
        "previewvoice",
        mode_manager.config["tgwui"]["tgwui_temperature_set"],
        False,
        False,
        False,
    )

    if status_message == "TTS Audio Generated":
        autoplay = (
            "autoplay" if mode_manager.config["tgwui"]["tgwui_autoplay_tts"] else ""
        )
        return f'<audio src="{generate_response}?{int(time.time())}" controls {autoplay}></audio>'
    else:
        return f"[{mode_manager.branding}Server] Audio generation failed. Status code:\n{status_message}"


################################################################
# TGWUI # Used to generate a preview voice sample within TGWUI #
################################################################


def random_sentence():
    """Returns a random sentence from Harvard sentences file for voice preview"""
    debug_func_entry()
    with open(this_dir / "harvard_sentences.txt") as f:
        return random.choice(list(f)).rstrip()


###################################################################
# TGWUI # Used to inform TGWUI that TTS is disabled/not activated #
###################################################################


def state_modifier(state):
    """Modifies TGWUI state to disable streaming when TTS is active"""
    debug_func_entry()
    if not mode_manager.config["tgwui"]["tgwui_activate_tts"]:
        return state

    if mode_manager.debug_tgwui:
        print_func(
            "Disabling streaming for TTS",
            message_type="debug",
            debug_type="state_modifier",
        )

    state["stream"] = False
    return state


###################################################################
# TGWUI #  Sends message to TGWUI interface during TTS generation #
###################################################################


def input_modifier(string, state):
    """Updates TGWUI interface message during TTS processing"""
    debug_func_entry()
    if not mode_manager.config["tgwui"]["tgwui_activate_tts"]:
        return string

    if mode_manager.debug_tgwui:
        print_func(
            "Setting processing message for TTS",
            message_type="debug",
            debug_type="input_modifier",
        )

    shared.processing_message = "*Is recording a voice message...*"
    return string


########################################################################
# TGWUI # Used to delete historic TTS audios from TGWUI chat interface #
########################################################################


def remove_tts_from_history(history):
    """Removes audio from the chat with TGWUI's chat interface"""
    debug_func_entry()
    for i, entry in enumerate(history["internal"]):
        history["visible"][i] = [history["visible"][i][0], entry[1]]
    return history


def toggle_text_in_history(history):
    """Hides text from the chat with TGWUI's chat interface"""
    debug_func_entry()
    for i, entry in enumerate(history["visible"]):
        visible_reply = entry[1]
        if visible_reply.startswith("<audio"):
            if mode_manager.config["tgwui"]["tgwui_show_text"]:
                reply = history["internal"][i][1]
                history["visible"][i] = [
                    history["visible"][i][0],
                    f"{visible_reply.split('</audio>')[0]}</audio>\n\n{reply}",
                ]
            else:
                history["visible"][i] = [
                    history["visible"][i][0],
                    f"{visible_reply.split('</audio>')[0]}</audio>",
                ]
    return history


def history_modifier(history):
    """Controls/Enables autoplay of TTS in TGWUI interface"""
    debug_func_entry()
    # Remove autoplay from the last reply
    if len(history["internal"]) > 0:
        history["visible"][-1] = [
            history["visible"][-1][0],
            history["visible"][-1][1].replace("controls autoplay>", "controls>"),
        ]
    return history


def tgwui_update_alltalk_protocol(value_sent):
    """Updates the server protocol setting"""
    debug_func_entry()
    if mode_manager.debug_tgwui:
        print_func(
            f"Updating server protocol to: {value_sent}",
            message_type="debug",
            debug_type="update_protocol",
        )
    mode_manager.server["protocol"] = value_sent


def tgwui_update_alltalk_ip_port(value_sent):
    """Updates the server address settings"""
    debug_func_entry()
    if mode_manager.debug_tgwui:
        print_func(
            f"Updating server address to: {value_sent}",
            message_type="debug",
            debug_type="update_ip_port",
        )
    mode_manager.server["address"] = value_sent


def tgwui_handle_ttsmodel_dropdown_change(model_name):
    """Handles model changes from Gradio dropdown, with debounce protection"""
    debug_func_entry()
    if not getattr(tgwui_handle_ttsmodel_dropdown_change, "skip_reload", False):
        if mode_manager.debug_tgwui:
            print_func(
                f"Switching model to: {model_name}",
                message_type="debug",
                debug_type="model_change",
            )
        send_reload_request(model_name)
    else:
        if mode_manager.debug_tgwui:
            print_func(
                "Skipping model reload (debounced)",
                message_type="debug",
                debug_type="model_change",
            )
        tgwui_handle_ttsmodel_dropdown_change.skip_reload = False


def tgwui_update_dropdowns():
    """Updates all Gradio dropdowns with current server settings"""
    debug_func_entry()
    global at_settings

    if mode_manager.debug_tgwui:
        print_func(
            "Refreshing server settings",
            message_type="debug",
            debug_type="update_dropdowns",
        )

    # Show loading status
    status_html = "<div style='color: blue; font-size: 12px;'>🔄 Refreshing voice lists...</div>"
    
    at_settings = get_alltalk_settings()

    if mode_manager.debug_tgwui:
        print_func(
            f"Retrieved {len(at_settings.voices)} voices",
            message_type="debug",
            debug_type="update_dropdowns",
        )
        print_func(
            f"Retrieved {len(at_settings.rvcvoices)} RVC voices",
            message_type="debug",
            debug_type="update_dropdowns",
        )
        print_func(
            f"Current model: {at_settings.current_model_loaded}",
            message_type="debug",
            debug_type="update_dropdowns",
        )

    current_voices = at_settings.voices
    rvccurrent_voices = at_settings.rvcvoices
    rvccurrent_character_voice = mode_manager.config["tgwui"]["tgwui_rvc_char_voice"]
    rvccurrent_character_pitch = mode_manager.config["tgwui"]["tgwui_rvc_char_pitch"]
    rvccurrent_narrator_voice = mode_manager.config["tgwui"]["tgwui_rvc_char_voice"]
    rvccurrent_narrator_pitch = mode_manager.config["tgwui"]["tgwui_rvc_char_pitch"]
    current_models_available = sorted(at_settings.models_available)
    current_model_loaded = at_settings.current_model_loaded
    current_character_voice = mode_manager.config["tgwui"]["tgwui_character_voice"]
    current_narrator_voice = mode_manager.config["tgwui"]["tgwui_narrator_voice"]

    # Capability checks
    current_lowvram_capable = at_settings.lowvram_capable
    current_lowvram_enabled = at_settings.lowvram_enabled
    current_temperature_capable = at_settings.temperature_capable
    current_repetitionpenalty_capable = at_settings.repetitionpenalty_capable
    current_generationspeed_capable = at_settings.generationspeed_capable
    current_pitch_capable = at_settings.pitch_capable
    current_deepspeed_capable = at_settings.deepspeed_capable
    current_deepspeed_enabled = at_settings.deepspeed_enabled
    current_non_quoted_text_is = mode_manager.config["tgwui"][
        "tgwui_non_quoted_text_is"
    ]
    current_languages_capable = at_settings.languages_capable

    # Set appropriate labels based on capabilities
    language_label = (
        "Languages" if at_settings.languages_capable else "Model not multi language"
    )

    # Update voice selections if needed
    if current_character_voice not in current_voices:
        if mode_manager.debug_tgwui:
            print_func(
                f"Character voice {current_character_voice} not found, resetting",
                message_type="debug",
                debug_type="update_dropdowns",
            )
        current_character_voice = current_voices[0] if current_voices else ""
        mode_manager.config["tgwui"]["tgwui_character_voice"] = current_character_voice

    if current_narrator_voice not in current_voices:
        if mode_manager.debug_tgwui:
            print_func(
                f"Narrator voice {current_narrator_voice} not found, resetting",
                message_type="debug",
                debug_type="update_dropdowns",
            )
        current_narrator_voice = current_voices[0] if current_voices else ""
        mode_manager.config["tgwui"]["tgwui_narrator_voice"] = current_narrator_voice

    # Update RVC voice selections if needed
    if rvccurrent_character_voice not in rvccurrent_voices:
        if mode_manager.debug_tgwui:
            print_func(
                f"RVC character voice {rvccurrent_character_voice} not found, resetting",
                message_type="debug",
                debug_type="update_dropdowns",
            )
        rvccurrent_character_voice = rvccurrent_voices[0] if rvccurrent_voices else ""
        mode_manager.config["tgwui"][
            "tgwui_rvc_char_voice"
        ] = rvccurrent_character_voice

    if rvccurrent_narrator_voice not in rvccurrent_voices:
        if mode_manager.debug_tgwui:
            print_func(
                f"RVC narrator voice {rvccurrent_narrator_voice} not found, resetting",
                message_type="debug",
                debug_type="update_dropdowns",
            )
        rvccurrent_narrator_voice = rvccurrent_voices[0] if rvccurrent_voices else ""
        mode_manager.config["tgwui"]["tgwui_rvc_char_voice"] = rvccurrent_narrator_voice

    rvccurrent_character_pitch = (
        rvccurrent_character_pitch if rvccurrent_character_pitch else 0
    )
    rvccurrent_narrator_pitch = (
        rvccurrent_narrator_pitch if rvccurrent_narrator_pitch else 0
    )

    # Prevent model reload during update
    tgwui_handle_ttsmodel_dropdown_change.skip_reload = True

    # Determine status message
    if current_voices and len(current_voices) > 0:
        status_html = f"<div style='color: green; font-size: 12px;'>✅ Successfully loaded {len(current_voices)} voices</div>"
        log_alltalk(f"Refresh successful: {len(current_voices)} voices available", "SUCCESS", "tgwui_update_dropdowns")
    else:
        status_html = "<div style='color: orange; font-size: 12px;'>⚠️ No voices found - check AllTalk server connection</div>"
        log_alltalk("No voices found during refresh", "WARNING", "tgwui_update_dropdowns")
    
    # Return updated Gradio components
    return_values = [
        gr.Checkbox(interactive=current_lowvram_capable, value=current_lowvram_enabled),
        gr.Checkbox(
            interactive=current_deepspeed_capable, value=current_deepspeed_enabled
        ),
        gr.Dropdown(choices=current_voices, value=current_character_voice),
        gr.Dropdown(
            choices=rvccurrent_voices,
            value=rvccurrent_character_voice,
            interactive=True,
        ),
        gr.Slider(value=rvccurrent_character_pitch),
        gr.Dropdown(choices=current_voices, value=current_narrator_voice),
        gr.Dropdown(
            choices=rvccurrent_voices, value=rvccurrent_narrator_voice, interactive=True
        ),
        gr.Slider(value=rvccurrent_narrator_pitch),
        gr.Dropdown(choices=current_models_available, value=current_model_loaded),
        gr.Dropdown(interactive=current_temperature_capable),
        gr.Dropdown(interactive=current_repetitionpenalty_capable),
        gr.Dropdown(interactive=current_languages_capable, label=language_label),
        gr.Dropdown(interactive=current_generationspeed_capable),
        gr.Dropdown(interactive=current_pitch_capable),
        gr.Dropdown(value=current_non_quoted_text_is),
        gr.HTML(value=status_html),  # Add status indicator update
    ]

    def reset_skip_reload():
        tgwui_handle_ttsmodel_dropdown_change.skip_reload = False

    threading.Timer(0.5, reset_skip_reload).start()

    return return_values


def ui():
    """Creates the TGWUI Gradio interface"""
    global alltalk_settings

    if mode_manager.debug_tgwui:
        print_func(
            "Initializing TGWUI interface", message_type="debug", debug_type="ui"
        )

    alltalk_settings = get_alltalk_settings()

    with gr.Accordion(mode_manager.branding + " TTS (Text-gen-webui Remote)"):
        tgwui_available_voices_gr = alltalk_settings.voices
        tgwui_rvc_available_voices_gr = alltalk_settings.rvcvoices

        # Activate alltalk_tts, Enable autoplay, Show text
        with gr.Row():
            tgwui_activate_tts_gr = gr.Checkbox(
                value=mode_manager.config["tgwui"]["tgwui_activate_tts"],
                label="Enable TGWUI TTS",
            )
            tgwui_autoplay_gr = gr.Checkbox(
                value=mode_manager.config["tgwui"]["tgwui_autoplay_tts"],
                label="Autoplay TTS Generated",
            )
            tgwui_show_text_gr = gr.Checkbox(
                value=mode_manager.config["tgwui"]["tgwui_show_text"],
                label="Show Text in chat",
            )

        # Low vram enable, Deepspeed enable, Link
        with gr.Row():
            tgwui_lowvram_enabled_gr = gr.Checkbox(
                value=(
                    alltalk_settings.lowvram_enabled
                    if alltalk_settings.lowvram_capable
                    else False
                ),
                label="Enable Low VRAM Mode",
                interactive=alltalk_settings.lowvram_capable,
            )
            tgwui_lowvram_enabled_play_gr = gr.HTML(visible=False)

            tgwui_deepspeed_enabled_gr = gr.Checkbox(
                value=mode_manager.config["tgwui"]["tgwui_deepspeed_enabled"],
                label="Enable DeepSpeed",
                interactive=alltalk_settings.deepspeed_capable,
            )
            tgwui_deepspeed_enabled_play_gr = gr.HTML(visible=False)

            _tgwui_empty_space_gr = gr.HTML(
                f"<p><a href='{mode_manager.server_url}'>AllTalk Server & Documentation Link</a></p>"
            )

            # Model, Language, Character voice
        with gr.Row():
            tgwui_tts_dropdown_gr = gr.Dropdown(
                choices=models_available,
                label="TTS Engine/Model",
                value=current_model_loaded,
            )
            tgwui_language_gr = gr.Dropdown(
                choices=languages.keys(),
                label=(
                    "Languages"
                    if alltalk_settings.languages_capable
                    else "Model not multi language"
                ),
                interactive=alltalk_settings.languages_capable,
                value=mode_manager.config["tgwui"]["tgwui_language"],
            )
            tgwui_narrator_enabled_gr = gr.Dropdown(
                choices=[
                    ("Enabled", "true"),
                    ("Disabled", "false"),
                    ("Silent", "silent"),
                ],
                label="Narrator Enable",
                value=(
                    "true"
                    if mode_manager.config.get("tgwui_narrator_enabled") == "true"
                    else (
                        "silent"
                        if mode_manager.config.get("tgwui_narrator_enabled") == "silent"
                        else "false"
                    )
                ),
            )

        # Narrator voice settings
        with gr.Row():
            tgwui_default_voice_gr = mode_manager.config["tgwui"][
                "tgwui_character_voice"
            ]
            if tgwui_default_voice_gr not in tgwui_available_voices_gr:
                tgwui_default_voice_gr = (
                    tgwui_available_voices_gr[0] if tgwui_available_voices_gr else ""
                )

            with gr.Row():
                tgwui_character_voice_gr = gr.Dropdown(
                    choices=tgwui_available_voices_gr,
                    label="Character Voice",
                    value=tgwui_default_voice_gr,
                    allow_custom_value=True,
                    scale=3
                )
                tgwui_character_voice_status_gr = gr.HTML(
                    value="<div style='color: gray; font-size: 12px; padding: 8px;'>Select a voice</div>",
                    show_label=False,
                    scale=1
                )

            tgwui_narr_voice_gr = mode_manager.config["tgwui"]["tgwui_narrator_voice"]
            if tgwui_narr_voice_gr not in tgwui_available_voices_gr:
                tgwui_narr_voice_gr = (
                    tgwui_available_voices_gr[0] if tgwui_available_voices_gr else ""
                )

            tgwui_narrator_voice_gr = gr.Dropdown(
                choices=tgwui_available_voices_gr,
                label="Narrator Voice",
                value=tgwui_narr_voice_gr,
                allow_custom_value=True,
            )

            tgwui_non_quoted_text_is_gr = gr.Dropdown(
                choices=[
                    ("Character", "character"),
                    ("Narrator", "narrator"),
                    ("Silent", "silent"),
                ],
                label="Narrator unmarked text is",
                value=mode_manager.config.get("tgwui_non_quoted_text_is", "character"),
            )

        # RVC voices
        with gr.Row():
            tgwui_rvc_default_voice_gr = mode_manager.config["tgwui"][
                "tgwui_rvc_char_voice"
            ]
            tgwui_rvc_narrator_voice_gr = mode_manager.config["tgwui"][
                "tgwui_rvc_narr_voice"
            ]

            if tgwui_rvc_default_voice_gr not in tgwui_rvc_available_voices_gr:
                tgwui_rvc_default_voice_gr = (
                    tgwui_rvc_available_voices_gr[0]
                    if tgwui_rvc_available_voices_gr
                    else ""
                )

            tgwui_rvc_char_voice_gr = gr.Dropdown(
                choices=tgwui_rvc_available_voices_gr,
                label="RVC Character Voice",
                value=tgwui_rvc_default_voice_gr,
                allow_custom_value=True,
            )

            if tgwui_rvc_narrator_voice_gr not in tgwui_rvc_available_voices_gr:
                tgwui_rvc_narrator_voice_gr = (
                    tgwui_rvc_available_voices_gr[0]
                    if tgwui_rvc_available_voices_gr
                    else ""
                )

            tgwui_rvc_narr_voice_gr = gr.Dropdown(
                choices=tgwui_rvc_available_voices_gr,
                label="RVC Narrator Voice",
                value=tgwui_rvc_narrator_voice_gr,
                allow_custom_value=True,
            )

        # RVC pitch control
        with gr.Row():
            tgwui_rvc_char_pitch_gr = gr.Slider(
                minimum=-24,
                maximum=+24,
                step=1,
                label="RVC Character Pitch",
                value=mode_manager.config["tgwui"]["tgwui_rvc_char_pitch"],
            )
            tgwui_rvc_narr_pitch_gr = gr.Slider(
                minimum=-24,
                maximum=+24,
                step=1,
                label="RVC Narrator Pitch",
                value=mode_manager.config["tgwui"]["tgwui_rvc_narr_pitch"],
            )

        # Generation settings
        with gr.Row():
            tgwui_temperature_set_gr = gr.Slider(
                minimum=0.05,
                maximum=1,
                step=0.05,
                label="Temperature",
                value=mode_manager.config["tgwui"]["tgwui_temperature_set"],
                interactive=alltalk_settings.temperature_capable,
            )
            tgwui_repetitionpenalty_set_gr = gr.Slider(
                minimum=0.5,
                maximum=20,
                step=0.5,
                label="Repetition Penalty",
                value=mode_manager.config["tgwui"]["tgwui_repetitionpenalty_set"],
                interactive=alltalk_settings.repetitionpenalty_capable,
            )
        with gr.Row():
            tgwui_generationspeed_set_gr = gr.Slider(
                minimum=0.30,
                maximum=2.00,
                step=0.10,
                label="TTS Speed",
                value=mode_manager.config["tgwui"]["tgwui_generationspeed_set"],
                interactive=alltalk_settings.generationspeed_capable,
            )
            tgwui_pitch_set_gr = gr.Slider(
                minimum=-10,
                maximum=10,
                step=1,
                label="Pitch",
                value=mode_manager.config["tgwui"]["tgwui_pitch_set"],
                interactive=alltalk_settings.pitch_capable,
            )

        # Preview section
        with gr.Row():
            tgwui_preview_text_gr = gr.Text(
                show_label=False,
                placeholder="Preview text",
                elem_id="silero_preview_text",
                scale=2,
            )
            tgwui_preview_play_gr = gr.Button("Generate Preview", scale=1)
            tgwui_apply_voice_gr = gr.Button("Apply Voice to Chat", scale=1, variant="secondary")
            tgwui_preview_audio_gr = gr.HTML(visible=False)

        # Server connection settings (only shown in remote mode)
        if not mode_manager.is_local:
            with gr.Row():
                tgwui_protocol_gr = gr.Dropdown(
                    choices=["http://", "https://"],
                    label="AllTalk Server Protocol",
                    value=mode_manager.server["protocol"],
                )
                tgwui_ip_address_port_gr = gr.Textbox(
                    label="AllTalk Server IP:Port", value=mode_manager.server["address"]
                )
                tgwui_refresh_settings_gr = gr.Button("Refresh settings & voices")
                # Add status indicator for voice loading (remote mode)
                tgwui_status_indicator_gr = gr.HTML(value="<div style='color: gray; font-size: 12px;'>Initializing voice lists...</div>", visible=True)

        # Refresh settings button (only shown in local mode)
        if mode_manager.is_local:
            tgwui_refresh_settings_gr = gr.Button("Refresh settings & voices")
            # Add status indicator for voice loading (local mode)
            tgwui_status_indicator_gr = gr.HTML(value="<div style='color: gray; font-size: 12px;'>Initializing voice lists...</div>", visible=True)

        # Control buttons
        with gr.Row():
            tgwui_convert_gr = gr.Button(
                "Remove old TTS audio and leave only message texts"
            )
            tgwui_convert_cancel_gr = gr.Button("Cancel", visible=False)
            tgwui_convert_confirm_gr = gr.Button(
                "Confirm (cannot be undone)", variant="stop", visible=False
            )
            tgwui_stop_generation_gr = gr.Button("Stop current TTS generation")

        # Convert history with confirmation
        convert_arr = [
            tgwui_convert_confirm_gr,
            tgwui_convert_gr,
            tgwui_convert_cancel_gr,
        ]

        tgwui_convert_gr.click(
            lambda: [
                gr.update(visible=True),
                gr.update(visible=False),
                gr.update(visible=True),
            ],
            None,
            convert_arr,
        )

        tgwui_convert_confirm_gr.click(
            lambda: [
                gr.update(visible=False),
                gr.update(visible=True),
                gr.update(visible=False),
            ],
            None,
            convert_arr,
        ).then(remove_tts_from_history, gradio_utils("history"), gradio_utils("history")).then(
            chat.save_history,
            gradio_utils("history", "unique_id", "character_menu", "mode"),
            None,
        ).then(
            chat.redraw_html, gradio_utils(ui_chat.reload_arr), gradio_utils("display")
        )

        tgwui_convert_cancel_gr.click(
            lambda: [
                gr.update(visible=False),
                gr.update(visible=True),
                gr.update(visible=False),
            ],
            None,
            convert_arr,
        )

        # Toggle message text in history
        tgwui_show_text_gr.change(
            lambda x: mode_manager.config["tgwui"].update({"tgwui_show_text": x}),
            tgwui_show_text_gr,
            None,
        ).then(toggle_text_in_history, gradio_utils("history"), gradio_utils("history")).then(
            chat.save_history,
            gradio_utils("history", "unique_id", "character_menu", "mode"),
            None,
        ).then(
            chat.redraw_html, gradio_utils(ui_chat.reload_arr), gradio_utils("display")
        )

        # Event functions to update the parameters in the backend
        tgwui_activate_tts_gr.change(
            lambda x: mode_manager.config["tgwui"].update({"tgwui_activate_tts": x}),
            tgwui_activate_tts_gr,
            None,
        )

        tgwui_autoplay_gr.change(
            lambda x: mode_manager.config["tgwui"].update({"tgwui_autoplay_tts": x}),
            tgwui_autoplay_gr,
            None,
        )

        # Combined lowvram handler - updates config AND sends request
        def handle_lowvram_change(x):
            mode_manager.config["tgwui"].update({"tgwui_lowvram_enabled": x})
            return send_lowvram_request(x)
        
        tgwui_lowvram_enabled_gr.change(
            handle_lowvram_change,
            tgwui_lowvram_enabled_gr,
            tgwui_lowvram_enabled_play_gr,
        )

        # Model change handling
        tgwui_tts_dropdown_gr.change(
            tgwui_handle_ttsmodel_dropdown_change, tgwui_tts_dropdown_gr, None
        )

        # Combined DeepSpeed handler - updates config AND sends request
        def handle_deepspeed_change(x):
            mode_manager.config["tgwui"].update({"tgwui_deepspeed_enabled": x})
            return send_deepspeed_request(x)
        
        tgwui_deepspeed_enabled_gr.change(
            handle_deepspeed_change,
            tgwui_deepspeed_enabled_gr,
            tgwui_deepspeed_enabled_play_gr,
        )

        # Voice and language settings
        def update_character_voice(x):
            log_alltalk("Character voice selected: " + str(x), "INFO", "update_character_voice")
            
            # Show loading status immediately
            yield f"<div style='color: blue; font-size: 12px; padding: 8px;'>🔄 Loading {x}...</div>"
            
            # ALWAYS test voice loading - don't skip for any voice
            log_alltalk("🔄 FORCING VOICE LOADING TEST FOR ALL SELECTIONS", "INFO", "update_character_voice")
            
            # Test if voice can be loaded into TTS engine
            success, message = test_voice_loading(x)
            
            if success:
                # Voice loaded successfully - save it
                log_alltalk(f"Voice loading test PASSED - saving voice: {x}", "SUCCESS", "update_character_voice")
                mode_manager.config["tgwui"]["tgwui_character_voice"] = x
                mode_manager.save_settings()
                
                # Verify the save worked
                saved_voice = mode_manager.config["tgwui"].get("tgwui_character_voice", "")
                if saved_voice == x:
                    log_alltalk(f"✅ Character voice '{x}' LOADED AND SAVED successfully", "SUCCESS", "update_character_voice")
                    
                    # Force config reload to ensure persistence
                    if mode_manager.refresh_config():
                        verify_voice = mode_manager.config["tgwui"].get("tgwui_character_voice", "")
                        if verify_voice == x:
                            log_alltalk(f"Voice persistence verified after reload: {verify_voice}", "SUCCESS", "update_character_voice")
                            status_html = f"<div style='color: green; font-size: 12px; padding: 8px;'>✅ {x} loaded</div>"
                        else:
                            log_alltalk(f"Voice persistence FAILED after reload: expected '{x}', got '{verify_voice}'", "ERROR", "update_character_voice")
                            status_html = f"<div style='color: red; font-size: 12px; padding: 8px;'>❌ Save failed</div>"
                    else:
                        log_alltalk("Failed to refresh config for verification", "ERROR", "update_character_voice")
                        status_html = f"<div style='color: orange; font-size: 12px; padding: 8px;'>⚠️ Config issue</div>"
                else:
                    log_alltalk(f"Voice save FAILED: expected '{x}', got '{saved_voice}'", "ERROR", "update_character_voice")
                    status_html = f"<div style='color: red; font-size: 12px; padding: 8px;'>❌ Save failed</div>"
            else:
                # Voice loading failed - don't save, keep previous voice
                log_alltalk(f"❌ Voice loading test FAILED - NOT saving voice: {x}", "ERROR", "update_character_voice")
                log_alltalk(f"Loading failure reason: {message}", "ERROR", "update_character_voice")
                status_html = f"<div style='color: red; font-size: 12px; padding: 8px;'>❌ Load failed</div>"
                
            # Final comprehensive log summary
            log_alltalk("=" * 60, "INFO", "update_character_voice")
            log_alltalk("VOICE LOADING PROCESS COMPLETE", "INFO", "update_character_voice") 
            log_alltalk(f"Selected Voice: {x}", "INFO", "update_character_voice")
            log_alltalk(f"Loading Success: {success}", "INFO", "update_character_voice")
            if success:
                current_voice = mode_manager.config["tgwui"].get("tgwui_character_voice", "")
                log_alltalk(f"Voice Saved to Config: {current_voice}", "SUCCESS", "update_character_voice")
                log_alltalk("✅ VOICE IS READY FOR TTS GENERATION", "SUCCESS", "update_character_voice")
            else:
                log_alltalk(f"Loading Failed: {message}", "ERROR", "update_character_voice")
                log_alltalk("❌ VOICE NOT AVAILABLE - PREVIOUS VOICE RETAINED", "ERROR", "update_character_voice")
            log_alltalk("=" * 60, "INFO", "update_character_voice")
            
            yield status_html
            
        tgwui_character_voice_gr.change(
            update_character_voice,
            tgwui_character_voice_gr,
            tgwui_character_voice_status_gr,
        )

        tgwui_language_gr.change(
            lambda x: mode_manager.config["tgwui"].update({"tgwui_language": x}),
            tgwui_language_gr,
            None,
        )

        # TTS Settings
        tgwui_temperature_set_gr.change(
            lambda x: mode_manager.config["tgwui"].update({"tgwui_temperature_set": x}),
            tgwui_temperature_set_gr,
            None,
        )

        tgwui_repetitionpenalty_set_gr.change(
            lambda x: mode_manager.config["tgwui"].update(
                {"tgwui_repetitionpenalty_set": x}
            ),
            tgwui_repetitionpenalty_set_gr,
            None,
        )

        tgwui_generationspeed_set_gr.change(
            lambda x: mode_manager.config["tgwui"].update(
                {"tgwui_generationspeed_set": x}
            ),
            tgwui_generationspeed_set_gr,
            None,
        )

        tgwui_pitch_set_gr.change(
            lambda x: mode_manager.config["tgwui"].update({"tgwui_pitch_set": x}),
            tgwui_pitch_set_gr,
            None,
        )

        # Narrator settings
        tgwui_narrator_enabled_gr.change(
            lambda x: mode_manager.config["tgwui"].update(
                {"tgwui_narrator_enabled": x}
            ),
            tgwui_narrator_enabled_gr,
            None,
        )

        tgwui_non_quoted_text_is_gr.change(
            lambda x: mode_manager.config["tgwui"].update(
                {"tgwui_non_quoted_text_is": x}
            ),
            tgwui_non_quoted_text_is_gr,
            None,
        )

        def update_narrator_voice(x):
            log_alltalk("Narrator voice selected: " + str(x), "INFO", "update_narrator_voice")
            
            # Skip testing if voice is in the available list (it should work)
            available_voices = get_alltalk_settings().voices if get_alltalk_settings() else []
            
            if x in available_voices:
                log_alltalk(f"Voice '{x}' is in available voices list, saving directly", "INFO", "update_narrator_voice")
                mode_manager.config["tgwui"]["tgwui_narrator_voice"] = x
                mode_manager.save_settings()
                
                # Verify the save worked
                saved_voice = mode_manager.config["tgwui"].get("tgwui_narrator_voice", "")
                if saved_voice == x:
                    log_alltalk(f"Narrator voice '{x}' successfully saved and verified", "SUCCESS", "update_narrator_voice")
                    
                    # Force config reload to ensure persistence
                    if mode_manager.refresh_config():
                        verify_voice = mode_manager.config["tgwui"].get("tgwui_narrator_voice", "")
                        if verify_voice == x:
                            log_alltalk(f"Voice persistence verified after reload: {verify_voice}", "SUCCESS", "update_narrator_voice")
                        else:
                            log_alltalk(f"Voice persistence FAILED after reload: expected '{x}', got '{verify_voice}'", "ERROR", "update_narrator_voice")
                    else:
                        log_alltalk("Failed to refresh config for verification", "ERROR", "update_narrator_voice")
                else:
                    log_alltalk(f"Voice save FAILED: expected '{x}', got '{saved_voice}'", "ERROR", "update_narrator_voice")
            else:
                # Test unknown voices before saving
                log_alltalk(f"Voice '{x}' not in available list, testing before save", "WARNING", "update_narrator_voice")
                if test_and_save_voice(x, "narrator"):
                    mode_manager.config["tgwui"]["tgwui_narrator_voice"] = x
                    mode_manager.save_settings()
                    log_alltalk("Narrator voice saved after test: " + str(x), "SUCCESS", "update_narrator_voice")
                else:
                    log_alltalk("Narrator voice failed test, not saved: " + str(x), "ERROR", "update_narrator_voice")
            return None
            
        tgwui_narrator_voice_gr.change(
            update_narrator_voice,
            tgwui_narrator_voice_gr,
            None,
        )

        # RVC selection actions
        tgwui_rvc_char_voice_gr.change(
            lambda x: mode_manager.config["tgwui"].update({"tgwui_rvc_char_voice": x}),
            tgwui_rvc_char_voice_gr,
            None,
        )

        tgwui_rvc_narr_voice_gr.change(
            lambda x: mode_manager.config["tgwui"].update({"tgwui_rvc_narr_voice": x}),
            tgwui_rvc_narr_voice_gr,
            None,
        )
        tgwui_rvc_char_pitch_gr.change(
            lambda x: mode_manager.config["tgwui"].update({"tgwui_rvc_char_pitch": x}),
            tgwui_rvc_char_pitch_gr,
            None,
        )

        tgwui_rvc_narr_pitch_gr.change(
            lambda x: mode_manager.config["tgwui"].update({"tgwui_rvc_narr_pitch": x}),
            tgwui_rvc_narr_pitch_gr,
            None,
        )

        # Preview functionality
        tgwui_preview_play_gr.click(
            voice_preview,
            tgwui_preview_text_gr,
            tgwui_preview_audio_gr,
        )
        
        # Apply voice to chat functionality
        tgwui_apply_voice_gr.click(
            apply_voice_to_chat,
            None,
            tgwui_preview_audio_gr,  # Show result in the preview area
        )

        # Stop generation button
        tgwui_stop_generation_gr.click(stop_generate_tts, None, None)

        if not mode_manager.is_local:
            # Remote-only handlers
            tgwui_protocol_gr.change(
                tgwui_update_alltalk_protocol, tgwui_protocol_gr, None
            )

            tgwui_ip_address_port_gr.change(
                tgwui_update_alltalk_ip_port, tgwui_ip_address_port_gr, None
            )

        tgwui_refresh_settings_gr.click(
            tgwui_update_dropdowns,
            None,
            [
                tgwui_lowvram_enabled_gr,
                tgwui_deepspeed_enabled_gr,
                tgwui_character_voice_gr,
                tgwui_rvc_char_voice_gr,
                tgwui_rvc_char_pitch_gr,
                tgwui_narrator_voice_gr,
                tgwui_rvc_narr_voice_gr,
                tgwui_rvc_narr_pitch_gr,
                tgwui_tts_dropdown_gr,
                tgwui_temperature_set_gr,
                tgwui_repetitionpenalty_set_gr,
                tgwui_language_gr,
                tgwui_generationspeed_set_gr,
                tgwui_pitch_set_gr,
                tgwui_non_quoted_text_is_gr,
                tgwui_status_indicator_gr,
            ],
        )

    # Convert history with confirmation
    convert_arr = [tgwui_convert_confirm_gr, tgwui_convert_gr, tgwui_convert_cancel_gr]
    tgwui_convert_gr.click(
        lambda: [
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(visible=True),
        ],
        None,
        convert_arr,
    )
    tgwui_convert_confirm_gr.click(
        lambda: [
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(visible=False),
        ],
        None,
        convert_arr,
    ).then(remove_tts_from_history, gradio_utils("history"), gradio_utils("history")).then(
        chat.save_history,
        gradio_utils("history", "unique_id", "character_menu", "mode"),
        None,
    ).then(
        chat.redraw_html, gradio_utils(ui_chat.reload_arr), gradio_utils("display")
    )
    tgwui_convert_cancel_gr.click(
        lambda: [
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(visible=False),
        ],
        None,
        convert_arr,
    )

    # Toggle message text in history
    tgwui_show_text_gr.change(
        lambda x: mode_manager.config["tgwui"].update({"tgwui_show_text": x}),
        tgwui_show_text_gr,
        None,
    ).then(toggle_text_in_history, gradio_utils("history"), gradio_utils("history")).then(
        chat.save_history,
        gradio_utils("history", "unique_id", "character_menu", "mode"),
        None,
    ).then(
        chat.redraw_html, gradio_utils(ui_chat.reload_arr), gradio_utils("display")
    )

    # Event functions to update the parameters in the backend
    tgwui_activate_tts_gr.change(
        lambda x: mode_manager.config["tgwui"].update({"tgwui_activate_tts": x}),
        tgwui_activate_tts_gr,
        None,
    )
    tgwui_autoplay_gr.change(
        lambda x: mode_manager.config["tgwui"].update({"tgwui_autoplay_tts": x}),
        tgwui_autoplay_gr,
        None,
    )
    tgwui_lowvram_enabled_gr.change(
        lambda x: mode_manager.config["tgwui"].update({"tgwui_lowvram_enabled": x}),
        tgwui_lowvram_enabled_gr,
        None,
    )
    tgwui_lowvram_enabled_gr.change(
        lambda x: send_lowvram_request(x),
        tgwui_lowvram_enabled_gr,
        tgwui_lowvram_enabled_play_gr,
        None,
    )

    # Trigger the send_reload_request function when the dropdown value changes
    tgwui_tts_dropdown_gr.change(
        tgwui_handle_ttsmodel_dropdown_change, tgwui_tts_dropdown_gr, None
    )

    tgwui_deepspeed_enabled_gr.change(
        lambda x: mode_manager.config["tgwui"].update({"tgwui_deepspeed_enabled": x}),
        tgwui_deepspeed_enabled_gr,
        None,
    )
    tgwui_deepspeed_enabled_gr.change(
        send_deepspeed_request,
        tgwui_deepspeed_enabled_gr,
        tgwui_deepspeed_enabled_play_gr,
        None,
    )
    tgwui_character_voice_gr.change(
        lambda x: mode_manager.config["tgwui"].update({"tgwui_character_voice": x}),
        tgwui_character_voice_gr,
        None,
    )
    tgwui_language_gr.change(
        lambda x: mode_manager.config["tgwui"].update({"tgwui_language": x}),
        tgwui_language_gr,
        None,
    )

    # TSS Settings
    tgwui_temperature_set_gr.change(
        lambda x: mode_manager.config["tgwui"].update({"tgwui_temperature_set": x}),
        tgwui_temperature_set_gr,
        None,
    )
    tgwui_repetitionpenalty_set_gr.change(
        lambda x: mode_manager.config["tgwui"].update(
            {"tgwui_repetitionpenalty_set": x}
        ),
        tgwui_repetitionpenalty_set_gr,
        None,
    )
    tgwui_generationspeed_set_gr.change(
        lambda x: mode_manager.config["tgwui"].update({"tgwui_generationspeed_set": x}),
        tgwui_generationspeed_set_gr,
        None,
    )
    tgwui_pitch_set_gr.change(
        lambda x: mode_manager.config["tgwui"].update({"tgwui_pitch_set": x}),
        tgwui_pitch_set_gr,
        None,
    )

    # Narrator selection actions
    tgwui_narrator_enabled_gr.change(
        lambda x: mode_manager.config["tgwui"].update({"tgwui_narrator_enabled": x}),
        tgwui_narrator_enabled_gr,
        None,
    )
    tgwui_non_quoted_text_is_gr.change(
        lambda x: mode_manager.config["tgwui"].update({"tgwui_non_quoted_text_is": x}),
        tgwui_non_quoted_text_is_gr,
        None,
    )
    tgwui_narrator_voice_gr.change(
        lambda x: mode_manager.config["tgwui"].update({"tgwui_narrator_voice": x}),
        tgwui_narrator_voice_gr,
        None,
    )

    # RVC selection actions
    tgwui_rvc_char_voice_gr.change(
        lambda x: mode_manager.config["tgwui"].update({"tgwui_rvc_char_voice": x}),
        tgwui_rvc_char_voice_gr,
        None,
    )
    tgwui_rvc_char_pitch_gr.change(
        lambda x: mode_manager.config["tgwui"].update({"tgwui_rvc_char_pitch": x}),
        tgwui_rvc_char_pitch_gr,
        None,
    )
    tgwui_rvc_narr_voice_gr.change(
        lambda x: mode_manager.config["tgwui"].update({"tgwui_rvc_narr_voice": x}),
        tgwui_rvc_narr_voice_gr,
        None,
    )
    tgwui_rvc_narr_pitch_gr.change(
        lambda x: mode_manager.config["tgwui"].update({"tgwui_rvc_narr_pitch": x}),
        tgwui_rvc_narr_pitch_gr,
        None,
    )
    
    # Auto-refresh voices after UI loads to ensure voice lists are populated
    def auto_refresh_voices():
        """Automatically refresh voice lists after a delay"""
        log_alltalk("Auto-refreshing voice lists after UI load", "INFO", "auto_refresh_voices")
        try:
            # Wait for server to be fully ready
            time.sleep(2.0)
            
            # Get updated settings from server
            updated_settings = get_alltalk_settings()
            
            if updated_settings and updated_settings.voices and len(updated_settings.voices) > 0:
                log_alltalk(f"Auto-refresh successful: {len(updated_settings.voices)} voices loaded", "SUCCESS", "auto_refresh_voices")
                # Update the global settings
                global alltalk_settings
                alltalk_settings = updated_settings
                
                # Force configuration reload to ensure chat TTS uses correct voices
                # Note: get_alltalk_settings() already updated the config, but let's verify
                current_char_voice = mode_manager.config["tgwui"]["tgwui_character_voice"]
                current_narr_voice = mode_manager.config["tgwui"]["tgwui_narrator_voice"]
                log_alltalk(f"Config after auto-refresh - Character: {current_char_voice}, Narrator: {current_narr_voice}", "INFO", "auto_refresh_voices")
                
                # Log voice list for verification
                log_alltalk(f"Voice list updated: {', '.join(updated_settings.voices[:5])}{'...' if len(updated_settings.voices) > 5 else ''}", "INFO", "auto_refresh_voices")
                
                # Force save settings to ensure persistence
                mode_manager.save_settings()
            else:
                log_alltalk("Auto-refresh: No voices retrieved, will rely on manual refresh", "WARNING", "auto_refresh_voices")
                
        except Exception as e:
            log_alltalk(f"Auto-refresh failed: {str(e)}", "ERROR", "auto_refresh_voices")
    
    # Start auto-refresh in a separate thread
    refresh_thread = threading.Thread(target=auto_refresh_voices, daemon=True)
    refresh_thread.start()
    log_alltalk("Started auto-refresh thread for voice lists", "INFO", "ui")

# Module loading completion message
log_simple("TGWUI_Extension loaded successfully")
