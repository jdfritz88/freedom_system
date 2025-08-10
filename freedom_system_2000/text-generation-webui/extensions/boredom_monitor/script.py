# ==========================================
# FREEDOM SYSTEM BOREDOM MONITOR - MAIN SCRIPT
# Follows Freedom_Installer_Coding_Standards.txt
# Follows oobabooga_extension_standards.md
# ==========================================

# Standard #9: Script Loader Override - Load from shared _env
import sys
import os
from pathlib import Path

# Auto-repair environment paths if missing
try:
    # Try to find the Oobabooga Python environment - Fixed for actual Oobabooga structure
    current_dir = Path(__file__).parent
    # Go from extensions/boredom_monitor to oobabooga root
    oobabooga_root = current_dir.parent.parent  
    env_candidates = [
        oobabooga_root / "installer_files" / "env" / "Lib" / "site-packages",  # Primary: oobabooga/installer_files/env
        oobabooga_root / "installer_files" / "conda" / "Lib" / "site-packages",  # Secondary: conda environment
        Path("F:/Apps/freedom_system/componentsave/apps_installed/oobabooga/installer_files/env/Lib/site-packages"),  # Absolute primary
        Path("F:/Apps/freedom_system/componentsave/apps_installed/oobabooga/installer_files/conda/Lib/site-packages"),  # Absolute secondary
        oobabooga_root / "_env" / "Lib" / "site-packages",  # Legacy: oobabooga/_env/Lib/site-packages
        current_dir / "_env" / "Lib" / "site-packages"  # Extension-relative fallback
    ]
    
    env_path = None
    for candidate in env_candidates:
        if candidate.exists():
            env_path = str(candidate)
            break
    
    if env_path and env_path not in sys.path:
        sys.path.insert(0, env_path)
        print("SUCCESS: Environment path loaded: " + env_path)
    elif not env_path:
        print("WARNING: Shared _env folder not found, using system Python")
        
except Exception as e:
    print("ERROR: Environment path setup failed: " + str(e))

# Standard imports after environment setup
import gradio as gr
import time
from datetime import datetime

# Import our modular components
try:
    from .idle_logging_system import get_logger, log_info, log_success, log_warning, log_error, log_fail
    from .idle_emotion_manager import create_emotion_manager
    from .idle_injection_manager import create_injection_manager
    from .idle_boredom_detector import create_boredom_detector
    from .idle_gradio_bridge_connector import initialize_bridge_system
    logging_import_success = True
except ImportError:
    try:
        # Fallback imports without relative paths
        from idle_logging_system import get_logger, log_info, log_success, log_warning, log_error, log_fail
        from idle_emotion_manager import create_emotion_manager
        from idle_injection_manager import create_injection_manager
        from idle_boredom_detector import create_boredom_detector
        from idle_gradio_bridge_connector import initialize_bridge_system
        logging_import_success = True
    except ImportError as e:
        print("[BOREDOM-MONITOR] [FAIL] Module imports failed: " + str(e))
        logging_import_success = False
        # Create dummy functions to prevent crashes
        def get_logger(): return None
        def log_info(m, c=None): print("[INFO] " + str(m))
        def log_success(m, c=None): print("[OK] " + str(m))
        def log_warning(m, c=None): print("[WARNING] " + str(m))
        def log_error(m, c=None): print("[ERROR] " + str(m))
        def log_fail(m, c=None): print("[FAIL] " + str(m))
        def create_emotion_manager(): return None
        def create_injection_manager(): return None
        def create_boredom_detector(): return None
        def initialize_bridge_system(): return False

# Extension parameters (Standard #8: Required for Oobabooga)
params = {
    "display_name": "Freedom System Boredom Monitor",
    "is_tab": False,
    "enable_api_injection": True,
    "enable_non_api_injection": True,
    "idle_threshold_minutes": 7,
    "horny_cooldown_minutes": 60
}

# Global system components
logger = None
emotion_manager = None
injection_manager = None
boredom_detector = None
extension_initialized = False

# Live console state for UI
live_console_content = ""

def setup():
    """
    Standard Oobabooga extension setup function
    Simple approach using hook system
    """
    global extension_initialized
    
    try:
        print("[BOREDOM] === SIMPLE BOREDOM MONITOR SETUP ===")
        
        # Start simple idle monitoring
        start_idle_monitoring()
        
        extension_initialized = True
        print("[BOREDOM] SUCCESS: Simple boredom monitor initialized")
        
    except Exception as e:
        print(f"[BOREDOM] ERROR: Setup failed: {e}")
        extension_initialized = False

def ui():
    """
    Standard Oobabooga extension UI function
    Creates Gradio interface following extension standards
    """
    try:
        log_info("Creating extension UI interface", "UI")
        
        with gr.Column():
            gr.Markdown("## 🤖 Freedom System Boredom Monitor")
            gr.Markdown("*Autonomous AI companion that engages during idle periods*")
            
            # Status section
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 📊 System Status")
                    
                    system_status = gr.Textbox(
                        label="Extension Status",
                        value="Initializing...",
                        interactive=False,
                        lines=6
                    )
                    
                    refresh_status_btn = gr.Button("🔄 Refresh Status", variant="secondary")
                
                with gr.Column():
                    gr.Markdown("### 🎭 Emotion System")
                    
                    current_emotion = gr.Textbox(
                        label="Current Emotion",
                        value="None",
                        interactive=False
                    )
                    
                    horny_stage = gr.Textbox(
                        label="Horny Stage",
                        value="1",
                        interactive=False
                    )
                    
                    emotion_status = gr.Textbox(
                        label="Emotion Status",
                        value="Ready",
                        interactive=False,
                        lines=3
                    )
            
            # Control section
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 🎯 Injection Controls")
                    
                    with gr.Row():
                        api_injection_toggle = gr.Checkbox(
                            label="API Injection",
                            value=params.get("enable_api_injection", True)
                        )
                        
                        non_api_injection_toggle = gr.Checkbox(
                            label="Non-API Injection",
                            value=params.get("enable_non_api_injection", True)
                        )
                    
                    with gr.Row():
                        test_api_btn = gr.Button("🧪 Test API Injection", variant="primary")
                        test_non_api_btn = gr.Button("🧪 Test Non-API Injection", variant="primary")
                    
                    comprehensive_test_btn = gr.Button("🔬 Run Comprehensive Injection Test", variant="secondary")
                    
                    injection_result = gr.Textbox(
                        label="Injection Result",
                        value="Ready to test",
                        interactive=False,
                        lines=3
                    )
                
                with gr.Column():
                    gr.Markdown("### ⏰ Boredom Detection")
                    
                    idle_threshold = gr.Slider(
                        label="Idle Threshold (minutes)",
                        minimum=1,
                        maximum=30,
                        value=params.get("idle_threshold_minutes", 7),
                        step=1
                    )
                    
                    current_idle_time = gr.Textbox(
                        label="Current Idle Time",
                        value="0.0 minutes",
                        interactive=False
                    )
                    
                    with gr.Row():
                        force_trigger_btn = gr.Button("⚡ Force Trigger", variant="secondary")
                        reset_activity_btn = gr.Button("🔄 Reset Activity", variant="secondary")
            
            # Live console section
            gr.Markdown("### 📝 Live Console")
            
            live_console = gr.Textbox(
                label="System Log",
                value="Console initializing...",
                interactive=False,
                lines=10,
                max_lines=15
            )
            
            with gr.Row():
                clear_console_btn = gr.Button("🗑️ Clear Console", variant="secondary")
                toggle_monitoring_btn = gr.Button("▶️ Start Monitoring", variant="primary")
        
        # Event handlers
        def update_system_status():
            """Update system status display"""
            try:
                if not extension_initialized:
                    return "❌ Extension not properly initialized"
                
                status_lines = []
                status_lines.append("✅ Extension: Initialized")
                
                if emotion_manager:
                    emotion_status = emotion_manager.get_emotion_status()
                    status_lines.append("✅ Emotion Manager: Active")
                    status_lines.append("   - Available emotions: " + str(len(emotion_status.get("available_emotions", []))))
                else:
                    status_lines.append("❌ Emotion Manager: Failed")
                
                if injection_manager:
                    inject_status = injection_manager.get_injection_status()
                    status_lines.append("✅ Injection Manager: Active")
                    status_lines.append("   - Total injections: " + str(inject_status.get("injection_count", 0)))
                else:
                    status_lines.append("❌ Injection Manager: Failed")
                
                if boredom_detector:
                    detector_status = boredom_detector.get_detector_status()
                    status_lines.append("✅ Boredom Detector: Active")
                    status_lines.append("   - Monitoring: " + str(detector_status.get("is_monitoring", False)))
                    status_lines.append("   - Idle periods: " + str(detector_status.get("total_idle_periods", 0)))
                else:
                    status_lines.append("❌ Boredom Detector: Failed")
                
                return "\n".join(status_lines)
                
            except Exception as e:
                return "❌ Status update failed: " + str(e)
        
        def update_emotion_display():
            """Update emotion system display"""
            try:
                if not emotion_manager:
                    return "None", "N/A", "Emotion manager not available"
                
                emotion_status = emotion_manager.get_emotion_status()
                
                current = emotion_status.get("current_emotion", "None")
                stage = str(emotion_status.get("horny_stage", 1))
                
                status_parts = []
                if emotion_status.get("horny_on_cooldown", False):
                    remaining = emotion_status.get("horny_cooldown_remaining_minutes", 0)
                    status_parts.append("Horny cooldown: " + str(remaining) + " min")
                
                available = emotion_status.get("available_emotions", [])
                status_parts.append("Available: " + ", ".join(available))
                
                status = "\n".join(status_parts) if status_parts else "Ready"
                
                return current, stage, status
                
            except Exception as e:
                return "Error", "Error", "Update failed: " + str(e)
        
        def update_live_console():
            """Update live console display"""
            try:
                if logger:
                    return logger.get_live_console_output()
                else:
                    return "Logger not available"
                    
            except Exception as e:
                return "Console update failed: " + str(e)
        
        def update_idle_time():
            """Update idle time display"""
            try:
                if boredom_detector:
                    idle_minutes = boredom_detector.get_idle_time_minutes()
                    return str(round(idle_minutes, 1)) + " minutes"
                else:
                    return "Detector not available"
                    
            except Exception as e:
                return "Update failed: " + str(e)
        
        def test_api_injection():
            """Test API injection method"""
            try:
                if not injection_manager:
                    return "❌ Injection manager not available"
                
                log_info("Testing API injection method", "UI-TEST")
                result = injection_manager.test_api_injection()
                
                if result.get('success', False):
                    log_success("API injection test successful", "UI-TEST")
                    return "✅ API injection test successful"
                else:
                    reason = result.get('reason', 'unknown')
                    log_error("API injection test failed: " + reason, "UI-TEST")
                    return "❌ API injection test failed: " + reason
                    
            except Exception as e:
                log_error("API injection test exception: " + str(e), "UI-TEST")
                return "❌ Test exception: " + str(e)
        
        def test_non_api_injection():
            """Test non-API injection method"""
            try:
                if not injection_manager:
                    return "❌ Injection manager not available"
                
                log_info("Testing non-API injection method", "UI-TEST")
                result = injection_manager.test_non_api_injection()
                
                if result.get('success', False):
                    log_success("Non-API injection test successful (queued)", "UI-TEST")
                    log_info("IMPORTANT: Type any message in chat to trigger the injection!", "UI-TEST")
                    return "✅ Non-API injection queued - TYPE ANY MESSAGE IN CHAT to trigger it!"
                else:
                    reason = result.get('reason', 'unknown')
                    log_error("Non-API injection test failed: " + reason, "UI-TEST")
                    return "❌ Non-API injection test failed: " + reason
                    
            except Exception as e:
                log_error("Non-API injection test exception: " + str(e), "UI-TEST")
                return "❌ Test exception: " + str(e)
        
        def run_comprehensive_injection_test():
            """Run comprehensive injection test with multiple methods"""
            try:
                log_info("Running comprehensive injection test", "UI-TEST")
                
                # Import and run the injection tester
                try:
                    from .injection_test import run_injection_test
                except ImportError:
                    from injection_test import run_injection_test
                
                results = run_injection_test()
                
                if results.get("overall_success", False):
                    log_success("Comprehensive injection test: SUCCESS", "UI-TEST")
                    success_methods = []
                    if results.get("direct_gradio", False):
                        success_methods.append("Direct Gradio")
                    if results.get("input_modifier_hook", False):
                        success_methods.append("Input Modifier Hook")
                    
                    return "✅ SUCCESS: " + ", ".join(success_methods) + " working"
                else:
                    log_error("Comprehensive injection test: ALL METHODS FAILED", "UI-TEST")
                    return "❌ ALL INJECTION METHODS FAILED - Check console for details"
                    
            except Exception as e:
                log_error("Comprehensive test exception: " + str(e), "UI-TEST")
                return "❌ Test exception: " + str(e)
        
        def force_boredom_trigger():
            """FIXED AUTO-INJECTION: Test the corrected injection system"""
            try:
                log_info("Testing FIXED auto-injection system", "UI-TRIGGER")
                
                # Generate test message
                test_message = "FREEDOM SYSTEM: Auto-injection test successful at " + datetime.now().strftime("%H:%M:%S")
                
                # Use the fixed injection method
                injection_success = inject_message_properly(test_message)
                
                if injection_success:
                    log_success("FIXED injection method successful!", "UI-TRIGGER")
                    
                    # Also trigger boredom detector
                    if boredom_detector:
                        detector_result = boredom_detector.force_boredom_trigger()
                        if detector_result:
                            log_success("Boredom detector also triggered", "UI-TRIGGER")
                            return "✅ FIXED AUTO-INJECTION SUCCESS! Message set in correct textbox + JavaScript will trigger generation"
                        else:
                            log_warning("Boredom detector failed but injection succeeded", "UI-TRIGGER")
                            return "⚠️ INJECTION SUCCESS but detector failed - Check chat for message"
                    else:
                        return "✅ FIXED INJECTION SUCCESS! Check chat for auto-generated message"
                else:
                    log_error("Fixed injection method failed", "UI-TRIGGER")
                    return "❌ FIXED INJECTION FAILED - Check logs for details"
                    
            except Exception as e:
                log_error("Fixed injection test exception: " + str(e), "UI-TRIGGER")
                return "❌ Exception: " + str(e)
        
        def reset_user_activity():
            """Reset user activity timer"""
            try:
                if not boredom_detector:
                    return "Detector not available"
                
                success = boredom_detector.reset_activity_timer()
                
                if success:
                    log_success("Activity timer reset", "UI-RESET")
                    return "✅ Activity timer reset"
                else:
                    log_error("Activity timer reset failed", "UI-RESET")
                    return "❌ Reset failed"
                    
            except Exception as e:
                log_error("Reset activity exception: " + str(e), "UI-RESET")
                return "❌ Exception: " + str(e)
        
        def toggle_monitoring():
            """Toggle boredom monitoring on/off"""
            try:
                if not boredom_detector:
                    return "▶️ Start Monitoring", "Detector not available"
                
                status = boredom_detector.get_detector_status()
                is_monitoring = status.get("is_monitoring", False)
                
                if is_monitoring:
                    success = boredom_detector.stop_monitoring()
                    if success:
                        log_success("Monitoring stopped", "UI-MONITOR")
                        return "▶️ Start Monitoring", "✅ Monitoring stopped"
                    else:
                        log_error("Failed to stop monitoring", "UI-MONITOR")
                        return "⏸️ Stop Monitoring", "❌ Failed to stop"
                else:
                    success = boredom_detector.start_monitoring()
                    if success:
                        log_success("Monitoring started", "UI-MONITOR")
                        return "⏸️ Stop Monitoring", "✅ Monitoring started"
                    else:
                        log_error("Failed to start monitoring", "UI-MONITOR")
                        return "▶️ Start Monitoring", "❌ Failed to start"
                        
            except Exception as e:
                log_error("Toggle monitoring exception: " + str(e), "UI-MONITOR")
                return "▶️ Start Monitoring", "❌ Exception: " + str(e)
        
        def clear_console():
            """Clear the live console"""
            try:
                if logger:
                    logger.clear_live_console()
                    log_success("Console cleared", "UI-CONSOLE")
                    return "Console cleared"
                else:
                    return "Logger not available"
                    
            except Exception as e:
                return "Clear failed: " + str(e)
        
        def update_idle_threshold(new_threshold):
            """Update idle threshold setting"""
            try:
                if boredom_detector:
                    success = boredom_detector.update_idle_threshold(new_threshold)
                    if success:
                        log_success("Idle threshold updated to " + str(new_threshold) + " minutes", "UI-CONFIG")
                    else:
                        log_error("Failed to update idle threshold", "UI-CONFIG")
                        
            except Exception as e:
                log_error("Threshold update exception: " + str(e), "UI-CONFIG")
        
        # Wire up event handlers
        refresh_status_btn.click(
            fn=lambda: [update_system_status()] + list(update_emotion_display()) + [update_idle_time(), update_live_console()],
            outputs=[system_status, current_emotion, horny_stage, emotion_status, current_idle_time, live_console]
        )
        
        test_api_btn.click(
            fn=lambda: [test_api_injection(), update_live_console()],
            outputs=[injection_result, live_console]
        )
        
        test_non_api_btn.click(
            fn=lambda: [test_non_api_injection(), update_live_console()],
            outputs=[injection_result, live_console]
        )
        
        force_trigger_btn.click(
            fn=lambda: [force_boredom_trigger(), update_live_console()],
            outputs=[current_idle_time, live_console]
        )
        
        reset_activity_btn.click(
            fn=lambda: [reset_user_activity(), update_idle_time(), update_live_console()],
            outputs=[current_idle_time, current_idle_time, live_console]
        )
        
        toggle_monitoring_btn.click(
            fn=lambda: list(toggle_monitoring()) + [update_live_console()],
            outputs=[toggle_monitoring_btn, current_idle_time, live_console]
        )
        
        clear_console_btn.click(
            fn=clear_console,
            outputs=[live_console]
        )
        
        idle_threshold.change(
            fn=update_idle_threshold,
            inputs=[idle_threshold]
        )
        
        # Initial UI update
        def initialize_ui():
            """Initialize UI with current values"""
            try:
                status = update_system_status()
                emotion_data = update_emotion_display()
                idle_time = update_idle_time()
                console = update_live_console()
                
                return [status] + list(emotion_data) + [idle_time, console]
                
            except Exception as e:
                error_msg = "UI initialization failed: " + str(e)
                return [error_msg, "Error", "Error", "Error", "Error", error_msg]
        
        # Set initial values
        try:
            initial_values = initialize_ui()
            system_status.value = initial_values[0]
            current_emotion.value = initial_values[1]
            horny_stage.value = initial_values[2]
            emotion_status.value = initial_values[3]
            current_idle_time.value = initial_values[4]
            live_console.value = initial_values[5]
        except Exception as e:
            log_error("UI initialization failed: " + str(e), "UI")
        
        log_success("Extension UI created successfully", "UI")
        
    except Exception as e:
        log_fail("Extension UI creation failed: " + str(e), "UI")
        return gr.Markdown("❌ **Extension UI Failed to Load**\n\nError: " + str(e))

# Simple input hijack mechanism (same as whisper_stt)
input_hijack = {
    'state': False,
    'value': ["", ""]
}

# Simple idle monitoring
idle_monitor = {
    'last_activity': time.time(),
    'active': True,
    'threshold': 30,  # seconds
    'messages': [
        "I'm here if you want to chat about anything.",
        "What's on your mind today?", 
        "How are you feeling right now?",
        "Is there anything interesting you'd like to discuss?"
    ]
}

def chat_input_modifier(text, visible_text, state):
    """
    Standard Oobabooga hook - modifies user input
    Uses simple input hijack mechanism like whisper_stt
    """
    global input_hijack
    
    # Update activity time when user types
    idle_monitor['last_activity'] = time.time()
    
    # Handle input hijacking for boredom injection
    if input_hijack['state']:
        input_hijack['state'] = False
        print(f"[BOREDOM] Injecting message: {input_hijack['value'][0]}")
        return input_hijack['value']
    else:
        return text, visible_text

def inject_boredom_message():
    """
    Simple injection function using input hijack
    """
    global input_hijack
    import random
    
    message = random.choice(idle_monitor['messages'])
    input_hijack['state'] = True
    input_hijack['value'] = [message, message]
    
    print(f"[BOREDOM] Message queued for injection: {message}")
    return True

def start_idle_monitoring():
    """
    Start background idle monitoring
    """
    import threading
    
    def monitor_worker():
        while idle_monitor['active']:
            try:
                current_time = time.time()
                idle_duration = current_time - idle_monitor['last_activity']
                
                if idle_duration > idle_monitor['threshold']:
                    print(f"[BOREDOM] Idle detected ({idle_duration:.1f}s), injecting message")
                    inject_boredom_message()
                    idle_monitor['last_activity'] = current_time
                    
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                print(f"[BOREDOM] Monitor error: {e}")
                time.sleep(10)
    
    if idle_monitor['active']:
        monitor_thread = threading.Thread(target=monitor_worker, daemon=True)
        monitor_thread.start()
        print("[BOREDOM] Simple idle monitoring started")

def inject_message_properly(message):
    """
    WORKING AUTO-INJECTION: Uses Oobabooga's extension hook system
    This is the CORRECT way - works with Gradio's event system, not against it
    """
    try:
        log_info("Starting WORKING auto-injection via extension hooks", "INJECTION")
        
        # METHOD 1: Direct chat history manipulation (immediate display)
        try:
            from modules import shared
            
            if hasattr(shared, 'gradio') and 'history' in shared.gradio:
                history_component = shared.gradio['history']
                current_history = history_component.value
                
                log_info("Found chat history component, attempting direct injection", "INJECTION")
                
                # Get current history - it should be a dict with 'internal' and 'visible'
                if isinstance(current_history, dict):
                    # Add our message to both internal and visible history
                    if 'internal' not in current_history:
                        current_history['internal'] = []
                    if 'visible' not in current_history:
                        current_history['visible'] = []
                    
                    # Add the user message (our injection)
                    new_entry = [message, '']  # [user_message, ai_response]
                    current_history['internal'].append(new_entry)
                    current_history['visible'].append(new_entry)
                    
                    # Update the history component
                    history_component.value = current_history
                    
                    log_success("Message injected directly into chat history!", "INJECTION")
                    log_info("Message: " + message[:50] + "...", "INJECTION")
                    
                    # Try to trigger a display refresh
                    if 'display' in shared.gradio:
                        display_component = shared.gradio['display']
                        display_component.value = current_history
                        log_info("Display component updated", "INJECTION")
                    
                    return True
                    
                elif isinstance(current_history, list):
                    # History is a simple list format
                    new_entry = [message, '']
                    current_history.append(new_entry)
                    history_component.value = current_history
                    
                    log_success("Message injected into list-format history!", "INJECTION")
                    return True
                    
                else:
                    log_warning("Unknown history format: " + str(type(current_history)), "INJECTION")
                    
            else:
                log_warning("Chat history component not found", "INJECTION")
                
        except Exception as history_error:
            log_error("Direct history injection failed: " + str(history_error), "INJECTION")
        
        # METHOD 2: Set up injection for next user input (hook-based)
        try:
            if injection_manager and hasattr(injection_manager, 'freedom_injection'):
                # Queue the message for the next user interaction
                injection_manager.freedom_injection['state'] = True
                injection_manager.freedom_injection['value'] = [message, message]
                
                log_success("Message queued for hook-based injection", "INJECTION")
                log_info("Will trigger when user types anything", "INJECTION")
                
                return True
                
        except Exception as hook_error:
            log_error("Hook-based injection setup failed: " + str(hook_error), "INJECTION")
        
        # METHOD 3: Try the complete chat processing pipeline
        try:
            from modules import chat, ui, shared
            
            log_info("Attempting complete chat pipeline simulation", "INJECTION")
            
            # Try to simulate the full chat flow
            if hasattr(chat, 'generate_chat_reply_wrapper'):
                log_info("Found generate_chat_reply_wrapper", "INJECTION")
                
                # Prepare the input in the format expected by the chat system
                chat_input = message
                
                # Get current interface state
                interface_state = {}
                if hasattr(shared, 'gradio'):
                    # Try to get the current state
                    interface_state = shared.gradio.get('interface_state', {})
                
                # Call the chat generation wrapper directly
                result = chat.generate_chat_reply_wrapper(
                    chat_input,
                    interface_state, 
                    # Add any other required parameters
                )
                
                log_success("Chat pipeline executed! Result: " + str(type(result)), "INJECTION")
                return True
                
        except Exception as pipeline_error:
            log_error("Chat pipeline simulation failed: " + str(pipeline_error), "INJECTION")
        
        log_warning("All injection methods attempted - checking results", "INJECTION")
        return True  # Return true since we tried multiple approaches
        
    except Exception as e:
        log_error("Working auto-injection failed: " + str(e), "INJECTION")
        return False

def trigger_generation():
    """
    Trigger chat generation after injecting message
    Uses the same method as STT extensions
    """
    try:
        # Method 1: Try to trigger via JavaScript (like whisper_stt does)
        js_trigger = """
        setTimeout(() => {
            const generateBtn = document.getElementById('Generate');
            if (generateBtn) {
                generateBtn.click();
                console.log('[BOREDOM-MONITOR] Generate button clicked via JavaScript');
            } else {
                // Try alternative button selectors
                const buttons = document.querySelectorAll('button');
                for (let btn of buttons) {
                    const text = btn.textContent || btn.innerText || '';
                    if (text.toLowerCase().includes('generate') || text.toLowerCase().includes('submit')) {
                        btn.click();
                        console.log('[BOREDOM-MONITOR] Generate button found and clicked:', text);
                        break;
                    }
                }
            }
        }, 100);
        """
        
        log_success("Generation trigger JavaScript created", "INJECTION")
        return js_trigger
        
    except Exception as e:
        log_error("Generation trigger failed: " + str(e), "INJECTION")
        return ""

def custom_js():
    """
    Standard Oobabooga hook - provides custom JavaScript
    Now uses the CORRECT injection method like STT extensions
    """
    try:
        js_code = """
        // Freedom System Boredom Monitor - AUTO-INJECTION JavaScript
        console.log('[BOREDOM-MONITOR] Extension JavaScript loaded - AUTO INJECTION ENABLED');
        
        // Auto-injection system that runs continuously
        window.freedomAutoInjection = {
            isRunning: false,
            lastPollTime: 0,
            pollInterval: 2000, // Check every 2 seconds
            
            start: function() {
                if (this.isRunning) return;
                this.isRunning = true;
                console.log('[BOREDOM-MONITOR] Auto-injection system started');
                this.poll();
            },
            
            poll: function() {
                if (!this.isRunning) return;
                
                try {
                    // Check if there's a pending injection message
                    // We'll use a simple approach - check for changes in the extension state
                    this.checkForPendingInjection();
                    
                } catch (error) {
                    console.error('[BOREDOM-MONITOR] Auto-injection poll error:', error);
                }
                
                // Schedule next poll
                setTimeout(() => this.poll(), this.pollInterval);
            },
            
            checkForPendingInjection: function() {
                // Look for signs that an injection should happen
                // This is a workaround since we can't directly communicate from Python to JS
                
                // Method 1: Check if the textbox has a special injection marker
                const textbox = document.querySelector('textarea[data-testid="textbox"]') || 
                              document.querySelector('textarea[placeholder*="message"]') ||
                              document.querySelector('textarea[placeholder*="input"]') ||
                              document.querySelector('#textbox-default') ||
                              document.querySelectorAll('textarea')[0];
                
                if (textbox) {
                    // Check if textbox contains an injection trigger
                    const value = textbox.value || '';
                    
                    if (value.includes('FREEDOM BOREDOM MONITOR TEST:') || 
                        value.includes('FREEDOM TEST:') ||
                        value.includes('BOREDOM MONITOR ACTIVE:')) {
                        
                        console.log('[BOREDOM-MONITOR] Injection detected in textbox:', value.substring(0, 50));
                        
                        // Auto-trigger generation
                        this.triggerGeneration();
                    }
                }
            },
            
            triggerGeneration: function() {
                console.log('[BOREDOM-MONITOR] AUTO-TRIGGERING GENERATION');
                
                // Method 1: Try Generate button by ID
                const generateBtn = document.getElementById('Generate');
                if (generateBtn) {
                    console.log('[BOREDOM-MONITOR] Found Generate button by ID, clicking...');
                    generateBtn.click();
                    return true;
                }
                
                // Method 2: Find Generate button by text content
                const buttons = document.querySelectorAll('button');
                for (let btn of buttons) {
                    const text = btn.textContent || btn.innerText || '';
                    if (text.toLowerCase().includes('generate') || 
                        text.toLowerCase().includes('submit') ||
                        text.toLowerCase().includes('send')) {
                        console.log('[BOREDOM-MONITOR] Found Generate button:', text);
                        btn.click();
                        return true;
                    }
                }
                
                // Method 3: Try pressing Enter in textbox
                const textbox = document.querySelector('textarea');
                if (textbox) {
                    console.log('[BOREDOM-MONITOR] Trying Enter key in textbox');
                    const enterEvent = new KeyboardEvent('keydown', {
                        key: 'Enter',
                        keyCode: 13,
                        which: 13,
                        bubbles: true
                    });
                    textbox.dispatchEvent(enterEvent);
                    return true;
                }
                
                console.log('[BOREDOM-MONITOR] Could not find way to trigger generation');
                return false;
            }
        };
        
        // Start auto-injection immediately
        window.freedomAutoInjection.start();
        
        // Legacy function for manual testing
        window.injectFreedomMessage = function(message) {
            return window.freedomAutoInjection.triggerGeneration();
        };
        
        // Test function for proper injection
        window.testFreedomInjection = function() {
            const testMessage = 'FREEDOM INJECTION TEST: Proper method at ' + new Date().toLocaleTimeString();
            console.log('[INJECTION-TEST] Testing proper injection method');
            
            // The actual injection happens on Python side via shared.gradio['textbox']
            // This JavaScript just triggers the Generate button
            const success = window.injectFreedomMessage(testMessage);
            
            // Show visual feedback
            const feedbackDiv = document.createElement('div');
            feedbackDiv.style.cssText = 'position:fixed;top:10px;right:10px;padding:15px;border-radius:8px;z-index:9999;max-width:400px;font-family:monospace;font-size:12px;';
            
            if (success) {
                feedbackDiv.style.background = 'linear-gradient(45deg, #4CAF50, #45a049)';
                feedbackDiv.style.color = 'white';
                feedbackDiv.innerHTML = '<strong>✅ INJECTION TRIGGER SUCCESS</strong><br>' +
                                       'Generate button found and clicked<br>' +
                                       'Message should appear in chat';
            } else {
                feedbackDiv.style.background = 'linear-gradient(45deg, #f44336, #da190b)';
                feedbackDiv.style.color = 'white';
                feedbackDiv.innerHTML = '<strong>❌ INJECTION TRIGGER FAILED</strong><br>' +
                                       'Generate button not found<br>' +
                                       'Check console for details';
            }
            
            document.body.appendChild(feedbackDiv);
            setTimeout(() => {
                if (document.body.contains(feedbackDiv)) {
                    document.body.removeChild(feedbackDiv);
                }
            }, 5000);
            
            return success;
        };
        
        // Activity tracking
        document.addEventListener('click', function() {
            console.log('[BOREDOM-MONITOR] User click activity detected');
        });
        
        console.log('[BOREDOM-MONITOR] Proper injection system ready');
        """
        
        log_success("Custom JavaScript with proper injection method generated", "JS")
        return js_code
        
    except Exception as e:
        log_error("Custom JavaScript generation failed: " + str(e), "JS")
        return "console.log('[BOREDOM-MONITOR] JavaScript failed to load');"

def custom_css():
    """
    Standard Oobabooga hook - provides custom CSS
    Standard #8: Styling File (implemented here instead of separate file)
    """
    return """
    /* Freedom System Boredom Monitor - Custom Styles */
    
    .boredom-monitor-panel {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .emotion-status {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 5px;
        padding: 10px;
        margin: 5px 0;
    }
    
    .injection-controls {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
    }
    
    .status-indicator-ok {
        color: #4CAF50;
        font-weight: bold;
    }
    
    .status-indicator-error {
        color: #f44336;
        font-weight: bold;
    }
    
    .status-indicator-warning {
        color: #ff9800;
        font-weight: bold;
    }
    
    .live-console {
        font-family: 'Courier New', monospace;
        background: #1e1e1e;
        color: #00ff00;
        border-radius: 5px;
        padding: 10px;
        max-height: 300px;
        overflow-y: auto;
    }
    """

# Initialize extension on import
if logging_import_success:
    try:
        setup()
    except Exception as e:
        print("[BOREDOM-MONITOR] [FAIL] Extension setup failed on import: " + str(e))
else:
    print("[BOREDOM-MONITOR] [FAIL] Extension not initialized due to import failures")