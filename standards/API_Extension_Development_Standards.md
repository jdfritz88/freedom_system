# API Extension Development Standards for Freedom System

## Overview
These standards ensure robust, maintainable, and debuggable API extensions for the Freedom System, particularly for Text-Generation-WebUI integrations and server-client architectures.

## 1. Configuration Management Standards

### 1.1 Multiple Configuration Files
Extensions that operate in different modes (standalone, integrated, remote) MUST maintain separate configuration files:

```python
# Example structure:
/extension_root/
├── config.json                    # Main server configuration
├── system/
│   └── remote_extension/
│       └── remote_config.json     # Remote client configuration
└── sync_config.py                 # Configuration synchronization module
```

### 1.2 Configuration Synchronization
**REQUIREMENT**: Extensions MUST implement automatic configuration synchronization on startup.

```python
def sync_all_configs():
    """
    Synchronize configurations across all config files
    Must be called during initialization
    """
    # 1. Scan for available resources (voices, models, etc.)
    resources = scan_resource_folder(resource_dir)
    
    # 2. Update all configuration files
    for config_path, update_func in config_files:
        if config_path.exists():
            update_func(config_path, resources)
    
    # 3. Validate configurations
    validate_config_integrity()
```

### 1.3 Configuration Persistence
**REQUIREMENT**: UI changes MUST persist to disk immediately:

```python
def update_setting_with_persistence(setting_name, value):
    """Example of proper setting update with persistence"""
    # Update in-memory config
    config["settings"][setting_name] = value
    
    # Save to disk immediately
    save_config()
    
    # Log the change
    print(f"[Extension] Updated {setting_name} to {value}")
```

## 2. Error Handling and Logging Standards

### 2.1 Comprehensive Error Logging
**REQUIREMENT**: All API calls MUST include detailed error logging:

```python
def make_api_request(endpoint, data):
    """Example of proper API error handling"""
    try:
        # Log request details
        print(f"[Extension] Sending request to {endpoint}")
        print(f"[Extension] Payload: {json.dumps(data, indent=2)}")
        
        response = requests.post(endpoint, json=data, timeout=60)
        
        # Log response details
        print(f"[Extension] Response status: {response.status_code}")
        print(f"[Extension] Response body: {response.text[:500]}")  # First 500 chars
        
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.HTTPError as e:
        print(f"[Extension] HTTP Error {e.response.status_code}")
        print(f"[Extension] Server error message: {e.response.text}")
        raise
    except requests.exceptions.RequestException as e:
        print(f"[Extension] Request failed: {str(e)}")
        raise
    except json.JSONDecodeError as e:
        print(f"[Extension] Failed to parse response: {str(e)}")
        print(f"[Extension] Raw response: {response.content}")
        raise
```

### 2.1.1 AllTalk TTS Specific Examples
**Real-world examples from AllTalk TTS extension:**

#### Script.py Error Logging Pattern:
```python
def output_modifier(string, state):
    """Text-Generation-WebUI output modifier with comprehensive logging"""
    print("[AllTalk TTS] output_modifier called")
    print(f"[AllTalk TTS] Input string length: {len(string) if string else 0}")
    print(f"[AllTalk TTS] State keys: {list(state.keys()) if state and hasattr(state, 'keys') else 'No state'}")
    
    # Validate inputs with detailed logging
    if not string or string.strip() == "":
        print("[AllTalk TTS] No text to process - skipping TTS generation")
        return string
    
    if not state or not hasattr(state, 'keys'):
        print("[AllTalk TTS] Warning: Invalid state object received")
        return string
    
    # Check server connectivity with retry logic
    if not check_server_connection():
        print("[AllTalk TTS] Error: Cannot connect to AllTalk server")
        return string
    
    try:
        # Process TTS with detailed logging
        print(f"[AllTalk TTS] Processing text: {string[:50]}...")
        result = process_tts_request(string, state)
        print(f"[AllTalk TTS] TTS processing completed successfully")
        return result
        
    except Exception as e:
        print(f"[AllTalk TTS] Error in output_modifier: {str(e)}")
        print(f"[AllTalk TTS] Exception type: {type(e).__name__}")
        import traceback
        print(f"[AllTalk TTS] Traceback: {traceback.format_exc()}")
        return string

def process_tts_request(text, state):
    """Process TTS request with comprehensive error logging"""
    try:
        # Build payload with validation
        payload = {
            "text_input": text,
            "voice": state.get('tts_voice', 'female_01.wav'),
            "language": state.get('tts_language', 'en'),
            "output_file_name": "tgwui_output",
            "output_file_timestamp": True
        }
        
        print(f"[AllTalk TTS] TTS Request payload:")
        print(f"[AllTalk TTS]   Text: {payload['text_input'][:100]}...")
        print(f"[AllTalk TTS]   Voice: {payload['voice']}")
        print(f"[AllTalk TTS]   Language: {payload['language']}")
        
        # Make API request with form data (not JSON)
        response = requests.post(
            "http://127.0.0.1:7851/api/tts-generate",
            data=payload,  # Form data, not json=payload
            timeout=60
        )
        
        print(f"[AllTalk TTS] API Response: {response.status_code}")
        print(f"[AllTalk TTS] Response headers: {dict(response.headers)}")
        
        if response.status_code == 500:
            print(f"[AllTalk TTS] Server Error 500: {response.text}")
            print("[AllTalk TTS] This often indicates invalid voice file selection")
            return text
        
        response.raise_for_status()
        
        response_data = response.json()
        print(f"[AllTalk TTS] Server response: {response_data}")
        
        return text
        
    except requests.exceptions.HTTPError as e:
        print(f"[AllTalk TTS] HTTP Error: {e.response.status_code}")
        print(f"[AllTalk TTS] Error response: {e.response.text}")
        return text
    except Exception as e:
        print(f"[AllTalk TTS] Unexpected error in TTS processing: {str(e)}")
        return text
```

#### Server Connection Check with Retry:
```python
def check_server_connection(max_retries=3, retry_delay=1):
    """Check AllTalk server connectivity with retry logic"""
    for attempt in range(max_retries):
        try:
            print(f"[AllTalk TTS] Connection attempt {attempt + 1}/{max_retries}")
            response = requests.get("http://127.0.0.1:7851/api/ready", timeout=3)
            
            if response.status_code == 200:
                print("[AllTalk TTS] Server connection successful")
                return True
            else:
                print(f"[AllTalk TTS] Server returned status {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("[AllTalk TTS] Connection refused - server may not be running")
        except requests.exceptions.Timeout:
            print("[AllTalk TTS] Connection timeout")
        except Exception as e:
            print(f"[AllTalk TTS] Connection error: {str(e)}")
        
        if attempt < max_retries - 1:
            print(f"[AllTalk TTS] Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
    
    print(f"[AllTalk TTS] Failed to connect after {max_retries} attempts")
    return False
```

#### Process Management Error Logging:
```python
def cleanup_process():
    """Clean shutdown of AllTalk subprocess with error logging"""
    global _state
    
    print("[AllTalk TTS] Starting cleanup process...")
    
    if _state.get("process") and _state["process"].poll() is None:
        print(f"[AllTalk TTS] Terminating subprocess PID: {_state['process'].pid}")
        
        try:
            _state["process"].terminate()
            
            # Wait for graceful shutdown
            try:
                _state["process"].wait(timeout=5)
                print("[AllTalk TTS] Subprocess terminated gracefully")
            except subprocess.TimeoutExpired:
                print("[AllTalk TTS] Graceful shutdown timeout, forcing kill")
                _state["process"].kill()
                _state["process"].wait()
                print("[AllTalk TTS] Subprocess killed")
                
        except Exception as e:
            print(f"[AllTalk TTS] Error during process cleanup: {str(e)}")
    else:
        print("[AllTalk TTS] No active subprocess to clean up")

def signal_handler(signum, frame):
    """Signal handler with null-safe process access"""
    print(f"[AllTalk TTS] Received signal {signum}")
    
    # NULL-SAFE: Always check if process exists before accessing
    if _state.get("process") is not None:
        if _state["process"].poll() is None:
            print("[AllTalk TTS] Cleaning up subprocess...")
            cleanup_process()
        else:
            print("[AllTalk TTS] Process already terminated")
    else:
        print("[AllTalk TTS] No process to clean up")
    
    print("[AllTalk TTS] Shutdown complete")
    sys.exit(0)
```

### 2.2 Debug Mode Implementation
**REQUIREMENT**: Extensions MUST implement hierarchical debug logging:

```python
class ExtensionDebugger:
    def __init__(self):
        self.debug_levels = {
            "standard": True,      # Always on
            "api_calls": False,    # API request/response
            "data_flow": False,    # Data transformation
            "function_trace": False # Function entry/exit
        }
    
    def log(self, message, level="standard", component="EXT"):
        if self.debug_levels.get(level, False):
            print(f"[{component}] {message}")
```

### 2.3 State Validation Logging
**REQUIREMENT**: Log state changes and validations:

```python
def output_modifier(string, state):
    """Example with proper state logging"""
    print(f"[Extension] output_modifier called")
    print(f"[Extension] Input length: {len(string) if string else 0}")
    print(f"[Extension] State keys: {list(state.keys()) if state else 'No state'}")
    
    # Validate state
    if not state or not hasattr(state, 'keys'):
        print("[Extension] Warning: Invalid state object")
        return string
    
    # Process...
    result = process_output(string, state)
    
    print(f"[Extension] Output length: {len(result) if result else 0}")
    return result
```

## 3. Resource Discovery Standards

### 3.1 Automatic Resource Discovery
**REQUIREMENT**: Extensions MUST automatically discover available resources on startup:

```python
def scan_resources_on_startup():
    """Scan and validate resources during initialization"""
    resources = {
        "voices": scan_folder("voices", "*.wav"),
        "models": scan_folder("models", "*.pt"),
        "configs": scan_folder("configs", "*.json")
    }
    
    # Validate resources
    for resource_type, items in resources.items():
        if not items:
            print(f"[Extension] Warning: No {resource_type} found")
        else:
            print(f"[Extension] Found {len(items)} {resource_type}")
    
    return resources
```

### 3.1.1 AllTalk Voice Synchronization Example
**Real-world implementation from AllTalk TTS:**

```python
def scan_voice_folder(voices_dir):
    """
    Scan the voices directory for available voice files
    
    Args:
        voices_dir: Path to the voices directory
        
    Returns:
        List of voice filenames (e.g., ['Arnold.wav', 'female_01.wav'])
    """
    voice_files = []
    
    if not voices_dir.exists():
        print(f"[AllTalk] Warning: Voices directory not found: {voices_dir}")
        return voice_files
    
    # Scan for .wav files (main voice files)
    for file_path in voices_dir.glob("*.wav"):
        voice_files.append(file_path.name)
    
    # Sort for consistent ordering
    voice_files.sort()
    
    print(f"[AllTalk] Found {len(voice_files)} voice files: {voice_files}")
    return voice_files

def sync_all_voices():
    """
    Main function to synchronize voices across all configuration files
    """
    print("[AllTalk] Starting voice synchronization...")
    
    # Get the base directory
    base_dir = Path(__file__).parent
    voices_dir = base_dir / "voices"
    
    # Scan for available voices
    voices = scan_voice_folder(voices_dir)
    
    if not voices:
        print("[AllTalk] Warning: No voice files found!")
        return
    
    # Update all configuration files
    config_files = [
        (base_dir / "confignew.json", update_main_config),
        (base_dir / "system" / "TGWUI_Extension" / "tgwui_remote_config.json", update_tgwui_remote_config),
        (base_dir / "system" / "tts_engines" / "xtts" / "model_settings.json", update_model_settings),
    ]
    
    for config_path, update_func in config_files:
        if config_path.exists():
            update_func(config_path, voices)
        else:
            print(f"[AllTalk] Config file not found: {config_path}")
    
    print(f"[AllTalk] Voice synchronization complete. {len(voices)} voices available.")
    return voices

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

# Integration in main extension startup
def ui():
    """Extension startup with voice synchronization"""
    print("[AllTalk TTS] Initializing extension...")
    
    # Import voice sync module with error handling
    try:
        from sync_voices import sync_all_voices
        print("[AllTalk TTS] Voice synchronization module loaded")
    except ImportError:
        print("[AllTalk TTS] Warning: Voice synchronization module not found")
        sync_all_voices = None
    
    # Run voice synchronization on startup
    if sync_all_voices:
        try:
            print("[AllTalk TTS] Synchronizing voice files with configurations...")
            sync_all_voices()
        except Exception as e:
            print(f"[AllTalk TTS] Warning: Voice synchronization failed: {e}")
    
    # Continue with rest of extension initialization...
```

### 3.2 Resource Validation
**REQUIREMENT**: Validate resources before use:

```python
def validate_resource(resource_path, resource_type):
    """Validate resource exists and is accessible"""
    if not os.path.exists(resource_path):
        # Don't use placeholder values like "Please Refresh Settings"
        # Use defaults or first available resource
        default = get_default_resource(resource_type)
        print(f"[Extension] Resource not found: {resource_path}, using default: {default}")
        return default
    return resource_path
```

## 4. Server-Client Communication Standards

### 4.1 Connection Health Checks
**REQUIREMENT**: Implement connection validation with retries:

```python
def check_server_connection(max_retries=3, retry_delay=1):
    """Verify server connectivity with retry logic"""
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{server_url}/api/ready", timeout=3)
            if response.status_code == 200:
                print("[Extension] Server connection successful")
                return True
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"[Extension] Connection attempt {attempt + 1} failed, retrying...")
                time.sleep(retry_delay)
            else:
                print(f"[Extension] Server connection failed after {max_retries} attempts")
    return False
```

### 4.2 API Response Validation
**REQUIREMENT**: Validate API responses thoroughly:

```python
def validate_api_response(response, expected_fields):
    """Validate API response structure"""
    if not response:
        raise ValueError("Empty response from API")
    
    missing_fields = [field for field in expected_fields if field not in response]
    if missing_fields:
        print(f"[Extension] Warning: Missing fields in response: {missing_fields}")
    
    return len(missing_fields) == 0
```

## 5. Process Management Standards

### 5.1 Subprocess Lifecycle Management
**REQUIREMENT**: Properly manage subprocess lifecycles:

```python
class SubprocessManager:
    def __init__(self):
        self.process = None
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def start_process(self):
        """Start subprocess with proper error handling"""
        if self.process and self.process.poll() is None:
            print("[Extension] Process already running")
            return
        
        self.process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"[Extension] Started process with PID: {self.process.pid}")
    
    def cleanup(self):
        """Clean shutdown of subprocess"""
        if self.process and self.process.poll() is None:
            print("[Extension] Terminating subprocess...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
```

### 5.2 Duplicate Process Prevention
**REQUIREMENT**: Prevent duplicate processes:

```python
def check_existing_process(port):
    """Check if process already running on port"""
    try:
        response = requests.get(f"http://127.0.0.1:{port}/api/ready", timeout=1)
        if response.status_code == 200:
            print(f"[Extension] Service already running on port {port}")
            return True
    except:
        pass
    return False
```

### 5.2.1 AllTalk Server Startup with Duplicate Prevention
**Real-world example from AllTalk TTS:**

```python
def check_alltalk_already_running():
    """Check if AllTalk server is already running by testing API connectivity."""
    import time
    max_retries = 3
    for attempt in range(max_retries):
        try:
            import requests
            response = requests.get("http://127.0.0.1:7851/api/ready", timeout=3)
            return response.status_code == 200
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"[AllTalk TTS] AllTalk connection attempt {attempt + 1} failed, retrying...")
                time.sleep(1)
            else:
                print(f"[AllTalk TTS] AllTalk connection failed after {max_retries} attempts")
    return False

def start_alltalk_server():
    """Start AllTalk server with duplicate process prevention"""
    global _state
    
    # Check if server already running
    if check_alltalk_already_running():
        print("[AllTalk TTS] AllTalk server already running, skipping startup")
        return
    
    # Check if we already have a process running
    if _state.get("process") and _state["process"].poll() is None:
        print("[AllTalk TTS] AllTalk process already managed by this extension")
        return
    
    print("[AllTalk TTS] Starting AllTalk server...")
    
    try:
        # Determine startup script path
        this_dir = Path(__file__).parent.resolve()
        start_script = this_dir / "start_alltalk.bat"
        
        if not start_script.exists():
            print(f"[AllTalk TTS] Error: Start script not found: {start_script}")
            return
        
        print(f"[AllTalk TTS] Using start script: {start_script}")
        
        # Start subprocess with proper error handling
        _state["process"] = subprocess.Popen(
            str(start_script),
            cwd=str(this_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True
        )
        
        print(f"[AllTalk TTS] Started AllTalk server with PID: {_state['process'].pid}")
        
        # Wait for server to become ready
        wait_for_server_ready()
        
    except Exception as e:
        print(f"[AllTalk TTS] Failed to start AllTalk server: {str(e)}")
        import traceback
        print(f"[AllTalk TTS] Traceback: {traceback.format_exc()}")

def wait_for_server_ready(timeout=60):
    """Wait for AllTalk server to become ready"""
    print("[AllTalk TTS] Waiting for server to become ready...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        if check_alltalk_already_running():
            elapsed = time.time() - start_time
            print(f"[AllTalk TTS] Server ready after {elapsed:.1f} seconds")
            return True
        
        time.sleep(2)
        print("[AllTalk TTS] Still waiting for server...")
    
    print(f"[AllTalk TTS] Timeout waiting for server after {timeout} seconds")
    return False

# Extension initialization with server management
def ui():
    """Main extension UI function with server startup"""
    print("[AllTalk TTS] Initializing AllTalk TTS extension...")
    
    # Set up signal handlers for clean shutdown
    atexit.register(cleanup_process)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Voice synchronization first
    if sync_all_voices:
        try:
            print("[AllTalk TTS] Synchronizing voice files...")
            sync_all_voices()
        except Exception as e:
            print(f"[AllTalk TTS] Voice sync failed: {e}")
    
    # Start server if not already running
    start_alltalk_server()
    
    # Verify server is accessible
    if not check_alltalk_already_running():
        print("[AllTalk TTS] Warning: Server not accessible after startup")
    else:
        print("[AllTalk TTS] Extension initialization complete")
    
    # Return gradio components or None
    return None
```

## 6. Data Format Standards

### 6.1 API Payload Formats
**REQUIREMENT**: Document and validate API payload formats:

```python
API_SCHEMAS = {
    "tts_generate": {
        "required": ["text_input"],
        "optional": ["voice", "language", "speed"],
        "types": {
            "text_input": str,
            "voice": str,
            "language": str,
            "speed": float
        }
    }
}

def validate_payload(endpoint, payload):
    """Validate payload against schema"""
    schema = API_SCHEMAS.get(endpoint)
    if not schema:
        return True  # No schema defined
    
    # Check required fields
    for field in schema["required"]:
        if field not in payload:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate types
    for field, value in payload.items():
        expected_type = schema["types"].get(field)
        if expected_type and not isinstance(value, expected_type):
            raise TypeError(f"Field {field} must be {expected_type.__name__}")
    
    return True
```

### 6.2 Form Data vs JSON
**REQUIREMENT**: Be explicit about data format expectations:

```python
def send_api_request(endpoint, data, format="json"):
    """Send API request with explicit format"""
    headers = {}
    
    if format == "json":
        headers["Content-Type"] = "application/json"
        response = requests.post(endpoint, json=data, headers=headers)
    elif format == "form":
        response = requests.post(endpoint, data=data)
    else:
        raise ValueError(f"Unknown format: {format}")
    
    return response
```

## 7. UI Integration Standards

### 7.1 Refresh Functionality
**REQUIREMENT**: Refresh buttons MUST update both UI and persistent storage:

```python
def refresh_settings():
    """Proper refresh implementation"""
    # 1. Fetch latest from server
    server_settings = fetch_server_settings()
    
    # 2. Update local config
    update_local_config(server_settings)
    
    # 3. Save to disk
    save_config()
    
    # 4. Update UI components
    return update_ui_components(server_settings)
```

### 7.2 Setting Change Handlers
**REQUIREMENT**: All setting changes must persist:

```python
def create_setting_handler(setting_name):
    """Create handler that persists changes"""
    def handler(value):
        # Update config
        config[setting_name] = value
        
        # Save immediately
        save_config()
        
        # Log change
        print(f"[Extension] {setting_name} changed to: {value}")
        
        return value
    
    return handler
```

## 8. Troubleshooting Methodology

### 8.1 Systematic Error Investigation Process
**REQUIREMENT**: Follow systematic debugging approach for complex issues:

#### 8.1.1 AllTalk TTS 500 Error Investigation Example
**Real-world troubleshooting process that led to discovering dual JSON config issue:**

```markdown
## Problem: 500 Internal Server Error from AllTalk API

### Step 1: Initial Error Analysis
- Error: HTTP 500 when calling /api/tts-generate
- Server logs showed file path error: "voices\Please Refresh Settings"
- Clear indication that placeholder text was being used as actual filename

### Step 2: UI Investigation  
- User reported: "The refresh button doesn't work. The default voice is arnold..."
- Screenshot showed AllTalk UI with non-functional refresh button
- Voice dropdown still showing "Please Refresh Settings" after refresh attempts

### Step 3: Configuration File Discovery
- Found confignew.json with proper voice settings: "tgwui_character_voice": "female_01.wav"
- BUT server was still trying to load "Please Refresh Settings"
- This indicated potential configuration file mismatch

### Step 4: Architecture Investigation
User question: "are there two json files?"
- Search revealed: confignew.json (main config)  
- Search revealed: tgwui_remote_config.json (TGWUI extension config)
- Discovery: TWO SEPARATE CONFIG SYSTEMS not synchronizing

### Step 5: Root Cause Analysis
- Main server config (confignew.json) had correct voice files
- TGWUI remote config had placeholder values
- UI refresh button only updated one config, not both
- Server was reading from different config than UI was updating

### Step 6: Solution Implementation
- Created voice synchronization system
- Updated all config files on startup
- Added config persistence to UI handlers
- Implemented refresh functionality for both configs

### Key Investigative Questions That Led to Discovery:
1. **"File path is not the issue. fix the file path but keep searching."** - User insisted to look beyond obvious path issues
2. **"Where are the files for the server?"** - Led to discovering server architecture
3. **"The refresh button doesn't work."** - Revealed UI persistence issues
4. **"are there two json files?"** - CRITICAL question that revealed dual config architecture
5. **"tell tgwui to use the correct json, dont update the one its looking for unless there is only one..."** - Showed understanding of config mismatch

### Investigation Techniques Used:
- **File system search** for config files (`confignew.json`, `tgwui_remote_config.json`)
- **API endpoint testing** to identify which config server actually reads
- **UI behavior analysis** through screenshots and user reports  
- **Log analysis** to trace server-side file path resolution
- **Process elimination** - ruling out simple path issues to find deeper architecture problems
```

#### 8.1.2 Debugging Questions to Ask
**When facing API extension issues, systematically check:**

```python
def diagnose_extension_issue():
    """Systematic diagnostic checklist"""
    
    # 1. Server Connectivity
    print("=== SERVER CONNECTIVITY ===")
    if not check_server_connection():
        print("ISSUE: Server not responding")
        print("CHECK: Is server process running?")
        print("CHECK: Are ports correct?")
        print("CHECK: Firewall blocking connections?")
        return
    
    # 2. Configuration Analysis  
    print("=== CONFIGURATION ANALYSIS ===")
    configs = find_all_config_files()
    for config_path in configs:
        print(f"Checking config: {config_path}")
        config = load_config(config_path)
        validate_config_values(config)
        
        # Check for placeholder values
        placeholder_values = ["Please Refresh Settings", "Select...", "Choose..."]
        for key, value in config.items():
            if value in placeholder_values:
                print(f"ISSUE: Placeholder value found: {key} = {value}")
    
    # 3. Resource Validation
    print("=== RESOURCE VALIDATION ===")
    resources = scan_resources()
    for resource_type, items in resources.items():
        if not items:
            print(f"ISSUE: No {resource_type} found")
        else:
            print(f"OK: Found {len(items)} {resource_type}")
            
        # Check if config references valid resources
        referenced_resources = get_config_resource_references(resource_type)
        for ref in referenced_resources:
            if ref not in items:
                print(f"ISSUE: Config references missing {resource_type}: {ref}")
    
    # 4. API Request/Response Analysis
    print("=== API TESTING ===")
    test_payload = create_test_payload()
    try:
        response = make_test_request(test_payload)
        print(f"API Response: {response.status_code}")
        
        if response.status_code == 500:
            print("INVESTIGATE: Check server logs for file path errors")
            print("INVESTIGATE: Look for placeholder values in actual usage")
            
    except Exception as e:
        print(f"API Error: {e}")
    
    # 5. UI State Investigation
    print("=== UI STATE ANALYSIS ===")
    print("CHECK: Do UI changes persist after refresh?")
    print("CHECK: Are there multiple config files that need sync?")
    print("CHECK: Is UI reading from same config server uses?")

def validate_config_values(config):
    """Validate configuration for common issues"""
    issues = []
    
    # Check for placeholder values
    placeholders = ["Please Refresh Settings", "Select...", "Choose...", ""]
    for key, value in config.items():
        if value in placeholders:
            issues.append(f"Placeholder value: {key} = '{value}'")
    
    # Check for file path references
    file_keys = [k for k in config.keys() if 'file' in k.lower() or 'voice' in k.lower()]
    for key in file_keys:
        file_path = config.get(key)
        if file_path and not os.path.exists(file_path):
            issues.append(f"Missing file: {key} = '{file_path}'")
    
    if issues:
        print("CONFIG ISSUES FOUND:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("Config validation passed")
    
    return len(issues) == 0
```

#### 8.1.3 Common Issue Patterns
**Patterns discovered during AllTalk troubleshooting:**

```python
COMMON_ISSUES = {
    "500_server_error": {
        "symptoms": ["HTTP 500", "Server internal error"],
        "likely_causes": [
            "Placeholder values used as actual file paths",
            "Missing or invalid resource files", 
            "Configuration file corruption",
            "Server reading different config than UI updates"
        ],
        "investigation_steps": [
            "Check server logs for file path errors",
            "Verify all config files have valid values",
            "Test with known-good configuration",
            "Compare UI config vs server config"
        ]
    },
    
    "ui_refresh_not_working": {
        "symptoms": ["Refresh button doesn't update values", "Changes don't persist"],
        "likely_causes": [
            "Multiple config files not synchronized",
            "UI updating different config than server reads",
            "Config changes not saved to disk",
            "Permission issues preventing file writes"
        ],
        "investigation_steps": [
            "Find all configuration files in extension",
            "Check which config server actually uses",
            "Verify UI handlers call save_config()",
            "Test file write permissions"
        ]
    },
    
    "placeholder_values_persist": {
        "symptoms": ["Settings show 'Please Refresh Settings'", "Default values don't load"],
        "likely_causes": [
            "Resource discovery not running on startup",
            "Config synchronization missing",
            "Invalid default values in config",
            "Resource folder empty or inaccessible"
        ],
        "investigation_steps": [
            "Check if resources exist in expected folders",
            "Verify resource discovery runs on startup",
            "Test config update functions manually",
            "Check folder permissions"
        ]
    }
}
```

## 9. Testing Requirements

### 9.1 Startup Testing
**REQUIREMENT**: Test both startup methods:

```python
def test_startup_methods():
    """Test all initialization paths"""
    # Test standalone startup
    test_standalone_startup()
    
    # Test integrated startup
    test_integrated_startup()
    
    # Test remote client startup
    test_remote_startup()
    
    # Verify configs are synchronized
    verify_config_sync()
```

### 8.2 Error Recovery Testing
**REQUIREMENT**: Test error recovery paths:

```python
def test_error_recovery():
    """Test error handling and recovery"""
    # Test server unavailable
    test_server_down_handling()
    
    # Test invalid configuration
    test_invalid_config_recovery()
    
    # Test missing resources
    test_missing_resource_handling()
    
    # Test API errors
    test_api_error_responses()
```

## 9. Documentation Requirements

### 9.1 Configuration Documentation
**REQUIREMENT**: Document all configuration files and their relationships:

```markdown
## Configuration Files

### Main Config (config.json)
- Purpose: Server-side configuration
- Location: /extension_root/config.json
- Updated by: Server startup, admin interface

### Remote Config (remote_config.json)
- Purpose: Client-side configuration for remote connections
- Location: /extension_root/system/remote/remote_config.json
- Updated by: Client UI, refresh operations

### Synchronization
- Both configs synchronized on startup via sync_config.py
- UI changes saved immediately to appropriate config
```

### 9.2 API Documentation
**REQUIREMENT**: Document all API endpoints and expected formats:

```markdown
## API Endpoints

### POST /api/generate
**Format**: application/x-www-form-urlencoded
**Required Fields**:
- text_input (string): Text to process
**Optional Fields**:
- voice (string): Voice selection
**Response**: JSON
**Error Codes**: 400, 500
```

## 10. Code Quality Standards

### 10.1 No Unicode Characters
**REQUIREMENT**: Use ASCII-only in code and comments:

```python
# BAD: print("✓ Success!")
# GOOD: print("[Success] Operation completed")

# BAD: # TODO: Fix this 🔧
# GOOD: # TODO: Fix this issue
```

### 10.2 Defensive Programming
**REQUIREMENT**: Always validate inputs and states:

```python
def process_data(data, state=None):
    """Example of defensive programming"""
    # Validate inputs
    if not data:
        print("[Extension] Warning: No data provided")
        return None
    
    # Validate state
    if state and not hasattr(state, 'keys'):
        print("[Extension] Warning: Invalid state object")
        state = {}
    
    # Safe access with defaults
    setting = state.get('setting', 'default') if state else 'default'
    
    # Process with error handling
    try:
        return do_processing(data, setting)
    except Exception as e:
        print(f"[Extension] Processing failed: {e}")
        return None
```

## Implementation Checklist

When creating a new API extension, ensure:

- [ ] Configuration files are properly structured and documented
- [ ] Automatic resource discovery is implemented
- [ ] Configuration synchronization runs on startup
- [ ] All API calls have comprehensive error logging
- [ ] Debug modes are implemented for troubleshooting
- [ ] Setting changes persist immediately
- [ ] Refresh functionality updates all relevant configs
- [ ] Process management prevents duplicates and handles cleanup
- [ ] All data formats are explicitly defined
- [ ] Error recovery paths are implemented and tested
- [ ] No Unicode characters in code
- [ ] Defensive programming practices throughout
- [ ] Documentation covers all configs and APIs
- [ ] Both startup methods are supported and tested

## Example Extension Structure

```
/my_extension/
├── extension.py              # Main extension code
├── sync_config.py           # Configuration synchronization
├── config.json              # Main configuration
├── system/
│   ├── remote/
│   │   └── remote_config.json  # Remote client config
│   └── api/
│       └── api_schemas.json    # API format definitions
├── resources/
│   └── voices/              # Resource folder (auto-scanned)
├── logs/
│   └── debug.log           # Debug output
└── README.md               # Documentation
```

---

## 11. Official OpenAI Extension Pattern Reference
The text-generation-webui OpenAI extension provides the official template:
- Location: `extensions/openai/script.py`
- Pattern: FastAPI server with threading - `Thread(target=run_server, daemon=True).start()`
- Port management with conflict resolution
- Proper integration with extension lifecycle

## 12. Message Injection Best Practices
**STANDARD**: Use API endpoints for message injection rather than internal hooks

**Rationale**: 
- API calls provide clean integration boundaries
- Easier to debug and monitor
- No risk of interfering with internal text-generation-webui logic
- Professional architecture following established patterns

**Implementation Requirements**:
- Always check OpenAI API availability before injection
- Implement comprehensive logging of all injection attempts
- Handle connection failures gracefully with retry logic
- Use consistent timeout values (30 seconds recommended)
- Log successful injections with context (emotion, timing, etc.)

## 13. Fixed Retry Pattern with Comprehensive Logging
**STANDARD**: Use fixed retry attempts (3 retries, 1-second delays) with detailed logging for localhost API calls

**Rationale**: 
- Localhost connections should be reliable and fast
- Fixed delays are predictable for user experience
- Follows AllTalk TTS proven pattern
- Comprehensive logging enables debugging retry scenarios

**Implementation Pattern**:
```python
async def api_call_with_retries(endpoint, payload, operation_name, max_retries=3, delay=1):
    """Standard retry pattern with comprehensive logging"""
    
    log_enhanced(f"Starting {operation_name}", "INFO", "api_call_with_retries", {
        "endpoint": endpoint,
        "max_retries": max_retries,
        "timeout": 30,
        "payload_size": len(str(payload))
    })
    
    for attempt in range(max_retries):
        try:
            attempt_start = time.time()
            
            log_enhanced(f"Attempt {attempt + 1}/{max_retries} for {operation_name}", "DEBUG", "api_call_with_retries", {
                "endpoint": endpoint,
                "attempt": attempt + 1
            })
            
            response = await requests.post(endpoint, json=payload, timeout=30)
            response_time = time.time() - attempt_start
            
            if response.status_code == 200:
                log_enhanced(f"{operation_name} succeeded on attempt {attempt + 1}", "INFO", "api_call_with_retries", {
                    "status_code": response.status_code,
                    "response_time_ms": round(response_time * 1000, 2),
                    "attempts_used": attempt + 1,
                    "response_length": len(response.text)
                })
                return True, response
            else:
                log_enhanced(f"{operation_name} HTTP error on attempt {attempt + 1}", "WARNING", "api_call_with_retries", {
                    "status_code": response.status_code,
                    "error_body": response.text[:200],
                    "response_time_ms": round(response_time * 1000, 2)
                })
                
        except requests.exceptions.Timeout:
            log_enhanced(f"{operation_name} timeout on attempt {attempt + 1}", "WARNING", "api_call_with_retries", {
                "timeout_seconds": 30,
                "endpoint": endpoint
            })
        except requests.exceptions.ConnectionError:
            log_enhanced(f"{operation_name} connection error on attempt {attempt + 1}", "WARNING", "api_call_with_retries", {
                "error_type": "ConnectionError",
                "endpoint": endpoint,
                "likely_cause": "Service not running"
            })
        except Exception as e:
            log_enhanced(f"{operation_name} unexpected error on attempt {attempt + 1}", "WARNING", "api_call_with_retries", {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "endpoint": endpoint
            })
        
        # Delay before retry (except on last attempt)
        if attempt < max_retries - 1:
            log_enhanced(f"Retrying {operation_name} in {delay} seconds...", "INFO", "api_call_with_retries", {
                "delay_seconds": delay,
                "remaining_attempts": max_retries - attempt - 1
            })
            await asyncio.sleep(delay)
    
    # All attempts failed
    log_enhanced(f"{operation_name} failed after {max_retries} attempts", "ERROR", "api_call_with_retries", {
        "endpoint": endpoint,
        "total_attempts": max_retries,
        "total_time_spent": max_retries * delay
    })
    
    return False, None
```

**Logging Requirements for Retry Operations**:
- Log each attempt with attempt number and timing
- Log specific error types (timeout, connection, HTTP error)
- Log successful attempts with response time and attempt count
- Log final failure with total time spent
- Include endpoint and operation context in all logs

---

*These standards ensure robust, maintainable extensions that handle errors gracefully, maintain configuration consistency, and provide excellent debugging capabilities for the Freedom System.*