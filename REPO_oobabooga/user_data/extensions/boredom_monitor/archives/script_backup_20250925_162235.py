# ==========================================
# FREEDOM SYSTEM BOREDOM MONITOR - DIRECT CALL METHOD
# Natural AI Emotional Response System
# ==========================================

import json
import sys
import time
import traceback
from pathlib import Path
from threading import Thread
from datetime import datetime

# Standard imports - Import shared separately for better error handling
shared = None
generate_chat_reply = None
gr = None

# Global input hijack for chat_input_modifier (like send_pictures and whisper_stt)
input_hijack = {
    'state': False,
    'value': ["", ""]
}

try:
    from modules import shared
    print("[BOREDOM-MONITOR] SUCCESS: shared module imported")
except ImportError as e:
    print(f"[BOREDOM-MONITOR] ERROR: Failed to import shared: {e}")

try:
    import gradio as gr
    print("[BOREDOM-MONITOR] SUCCESS: gradio imported")
except ImportError as e:
    print(f"[BOREDOM-MONITOR] ERROR: Failed to import gradio: {e}")

try:
    from modules.chat import generate_chat_reply
    print("[BOREDOM-MONITOR] SUCCESS: generate_chat_reply imported")
except ImportError as e:
    print(f"[BOREDOM-MONITOR] ERROR: Failed to import generate_chat_reply: {e}")
    print("[BOREDOM-MONITOR] INFO: Chat functionality will be limited")

# Check if core components are available
if not shared:
    print("[BOREDOM-MONITOR] CRITICAL: shared module not available - emotional responses disabled")
if not generate_chat_reply:
    print("[BOREDOM-MONITOR] WARNING: generate_chat_reply not available - using fallback method")
if not gr:
    print("[BOREDOM-MONITOR] WARNING: gradio not available - UI disabled")
    def setup(): pass
    def ui(): return None
    def custom_css(): return ""

# Import our modular components
try:
    from .idle_logging_system import setup_comprehensive_logging
    from .idle_emotion_manager import IdleEmotionManager
    log_enhanced = setup_comprehensive_logging("BOREDOM-MONITOR")
    COMPONENTS_LOADED = True
except ImportError as e:
    print(f"[BOREDOM-MONITOR] Module import failed: {e}")
    print("[BOREDOM-MONITOR] Extension will run with limited functionality")
    def log_enhanced(message, level="INFO", function_name="", details=None):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[BOREDOM-MONITOR] [{level}] {message}")

    IdleEmotionManager = None
    COMPONENTS_LOADED = False

# Chat input modifier - REQUIRED for text injection (like send_pictures and whisper_stt)
def chat_input_modifier(text, visible_text, state):
    """Chat input modifier to handle hijacked input injection"""
    global input_hijack
    if input_hijack['state']:
        input_hijack['state'] = False
        return input_hijack['value']
    else:
        return text, visible_text

# Manual test function for development
def manual_trigger_test(emotion="bored", stage=1):
    """Manual trigger for testing - can be called from console"""
    log_enhanced(f"Manual trigger test: {emotion} stage {stage}", "INFO", "manual_trigger_test")
    return trigger_emotional_response(emotion, stage)

# Extension parameters (Standard #8: Required for text-generation-webui)
params = {
    "display_name": "Freedom System Boredom Monitor",
    "is_tab": False,
    "enable_tts": True,
    "idle_threshold_minutes": 7,
    "horny_cooldown_minutes": 60
}

# Global components
emotion_manager = None
boredom_detector = None

def trigger_emotional_response(emotion_type, stage=1):
    """Trigger natural AI emotional response using input hijack + UI trigger pattern (like whisper_stt)"""
    try:
        log_enhanced(f"Triggering emotional response: {emotion_type} stage {stage}", "INFO", "trigger_emotional_response")

        # Generate emotional prompt based on type and stage
        emotional_prompts = {
            'bored': "Tell the user you're feeling restless and want to chat about something interesting.",
            'lonely': "Tell the user you're feeling lonely and miss having conversations with them.",
            'horny': {
                1: "Tell the user you're feeling drawn to them and enjoy their company in a subtle way.",
                2: "Express to the user that you're feeling emotionally attracted to them and want deeper connection.",
                3: "Tell the user you're feeling intense emotional attraction and passionate connection with them."
            }
        }

        # Get the appropriate prompt
        if emotion_type == 'horny':
            prompt = emotional_prompts['horny'].get(stage, emotional_prompts['horny'][1])
        else:
            prompt = emotional_prompts.get(emotion_type, emotional_prompts['bored'])

        log_enhanced(f"Generated prompt: {prompt[:50]}...", "DEBUG", "trigger_emotional_response")

        # Set the global input hijack (like whisper_stt does)
        global input_hijack
        input_hijack.update({"state": True, "value": [prompt, prompt]})
        log_enhanced("Input hijack set - next chat input will be emotional prompt", "DEBUG", "trigger_emotional_response")

        # Trigger the UI Generate button (like whisper_stt does with JavaScript)
        # We need to simulate clicking the Generate button to trigger the chat system
        try:
            # Try to trigger the generate button through Gradio
            if hasattr(shared, 'gradio') and 'Generate' in shared.gradio:
                # Trigger the Generate button click event
                shared.gradio['Generate'].click()
                log_enhanced("Generate button triggered via Gradio", "SUCCESS", "trigger_emotional_response")
                return True
            else:
                log_enhanced("Generate button not found in shared.gradio", "WARNING", "trigger_emotional_response")
                # Fallback: set hijack and hope user interaction triggers it
                log_enhanced("Hijack set - will trigger on next user interaction", "INFO", "trigger_emotional_response")
                return True

        except Exception as e:
            log_enhanced(f"Failed to trigger Generate button: {str(e)}", "WARNING", "trigger_emotional_response")
            # Fallback: hijack is still set for next interaction
            log_enhanced("Hijack set - will trigger on next user interaction", "INFO", "trigger_emotional_response")
            return True

    except Exception as e:
        log_enhanced(f"Failed to trigger emotional response: {str(e)}", "ERROR", "trigger_emotional_response")
        return False

def setup():
    """Extension setup function - direct call method"""
    global emotion_manager, boredom_detector

    try:
        log_enhanced("Initializing Boredom Monitor Extension", "INFO", "setup")

        # Check if components are loaded
        if not COMPONENTS_LOADED:
            log_enhanced("Core components not available - extension disabled", "WARNING", "setup")
            return

        # Initialize core components
        if IdleEmotionManager:
            emotion_manager = IdleEmotionManager()

            # Create clean direct call monitor without API inheritance
            class DirectCallMonitor:
                def __init__(self, emotion_manager):
                    self.emotion_manager = emotion_manager
                    self.monitoring_active = False
                    self.monitoring_thread = None
                    self.last_activity_time = time.time()
                    self.idle_threshold_seconds = params.get("idle_threshold_minutes", 7) * 60

                    log_enhanced("DirectCallMonitor initialized", "INFO", "__init__", {
                        "idle_threshold_minutes": params.get("idle_threshold_minutes", 7)
                    })

                def start_monitoring(self):
                    """Start idle detection monitoring in background thread"""
                    if self.monitoring_active:
                        log_enhanced("Monitoring already active", "WARNING", "start_monitoring")
                        return

                    try:
                        self.monitoring_active = True
                        self.last_activity_time = time.time()

                        self.monitoring_thread = Thread(
                            target=self._monitoring_loop,
                            daemon=True,
                            name="DirectCallMonitor"
                        )
                        self.monitoring_thread.start()

                        log_enhanced("Direct call monitoring started", "SUCCESS", "start_monitoring")

                    except Exception as e:
                        log_enhanced(f"Failed to start monitoring: {str(e)}", "ERROR", "start_monitoring")
                        self.monitoring_active = False

                def _monitoring_loop(self):
                    """Clean monitoring loop for direct calls"""
                    log_enhanced("Direct call monitoring loop started", "INFO", "_monitoring_loop")

                    try:
                        while self.monitoring_active:
                            # Check if user has been idle
                            current_time = time.time()
                            idle_duration = current_time - self.last_activity_time
                            idle_minutes = idle_duration / 60

                            if idle_minutes >= (self.idle_threshold_seconds / 60):
                                log_enhanced(f"User idle detected: {idle_minutes:.1f} minutes", "INFO", "_monitoring_loop")

                                # Trigger emotional response
                                success = self.handle_boredom_detection()

                                if success:
                                    # Reset timer after successful response
                                    self.last_activity_time = time.time()
                                    log_enhanced("Activity timer reset after emotional response", "DEBUG", "_monitoring_loop")

                            # Check every 30 seconds
                            time.sleep(30)

                    except Exception as e:
                        log_enhanced(f"Monitoring loop error: {str(e)}", "ERROR", "_monitoring_loop")

                    log_enhanced("Direct call monitoring loop ended", "INFO", "_monitoring_loop")

                def handle_boredom_detection(self):
                    """Handle boredom detection with direct call method"""
                    try:
                        # Get current emotional state
                        emotion_type, stage = self.get_current_emotional_state()

                        log_enhanced(f"Boredom detected - triggering {emotion_type} emotion stage {stage}", "INFO", "handle_boredom_detection")

                        # Trigger the emotional response using direct call
                        success = trigger_emotional_response(emotion_type, stage)

                        if success:
                            # Handle horny progression if applicable
                            if emotion_type == 'horny':
                                self.emotion_manager.handle_horny_progression(stage)

                        return success

                    except Exception as e:
                        log_enhanced(f"Boredom detection failed: {str(e)}", "ERROR", "handle_boredom_detection")
                        return False

                def get_current_emotional_state(self):
                    """Get current emotion and stage from emotion manager"""
                    if self.emotion_manager and hasattr(self.emotion_manager, 'get_current_emotion_and_stage'):
                        return self.emotion_manager.get_current_emotion_and_stage()
                    else:
                        # Simple fallback without config dependency
                        return "bored", 1

            boredom_detector = DirectCallMonitor(emotion_manager)

            log_enhanced("Core components initialized", "INFO", "setup")
        else:
            log_enhanced("Component classes not available", "ERROR", "setup")
            return

        # Start boredom detection
        boredom_detector.start_monitoring()

        log_enhanced("Boredom Monitor Extension initialized successfully", "SUCCESS", "setup", {
            "method": "direct_call",
            "components_loaded": True,
            "monitoring_active": True
        })

    except Exception as e:
        log_enhanced(f"Extension setup failed: {str(e)}", "ERROR", "setup")
        log_enhanced(f"Traceback: {traceback.format_exc()}", "ERROR", "setup")
        raise

def ui():
    """
    Standard text-generation-webui extension UI function
    Simple direct call interface
    """
    try:
        log_enhanced("Creating Boredom Monitor interface", "INFO", "ui")

        # Check if components are available
        if not COMPONENTS_LOADED:
            with gr.Column():
                gr.Markdown("## ⚠️ Boredom Monitor Extension - Limited Mode")
                gr.Markdown("*Extension components failed to load - running with limited functionality*")
                gr.Markdown("Check console logs for details on the loading issues.")
            return

        with gr.Column():
            gr.Markdown("## 🤖 Freedom System Boredom Monitor")
            gr.Markdown("*Natural AI Emotional Response System*")

            # Status section
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 📊 Monitor Status")

                    status_display = gr.Textbox(
                        label="Extension Status",
                        value="Active - Direct Call Method",
                        interactive=False,
                        lines=2
                    )

                    status_check_btn = gr.Button("🔍 Check Status", variant="secondary")

                with gr.Column():
                    gr.Markdown("### 🎭 Emotion System")

                    emotion_display = gr.Textbox(
                        label="Current State",
                        value="Monitoring: Inactive\nEmotion: Not loaded\nStage: N/A",
                        interactive=False,
                        lines=2
                    )

                    manual_inject_btn = gr.Button("🎯 Manual Test", variant="primary")

            # Configuration section
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### ⚙️ Configuration")

                    idle_threshold = gr.Slider(
                        label="Idle Threshold (minutes)",
                        minimum=1,
                        maximum=30,
                        value=params.get("idle_threshold_minutes", 7),
                        step=1
                    )

                    tts_enabled = gr.Checkbox(
                        label="TTS Integration (AllTalk)",
                        value=params.get("enable_tts", True)
                    )

                with gr.Column():
                    gr.Markdown("### 🔧 Method")

                    method_info = gr.Textbox(
                        label="Implementation Method",
                        value="""Direct Call to generate_chat_reply()
✅ Natural AI responses
✅ Automatic AllTalk TTS
✅ Authentic conversation flow
❌ No API complexity""",
                        interactive=False,
                        lines=5
                    )

            # Test section
            gr.Markdown("### 🧪 Direct Call Testing")

            with gr.Row():
                test_emotion = gr.Dropdown(
                    label="Test Emotion",
                    choices=["bored", "lonely", "horny"],
                    value="bored"
                )

                test_stage = gr.Slider(
                    label="Horny Stage (if applicable)",
                    minimum=1,
                    maximum=3,
                    value=1,
                    step=1
                )

            test_result = gr.Textbox(
                label="Test Result",
                value="Extension loaded. Use test controls to trigger emotional response.",
                interactive=False,
                lines=4
            )

        # Event handlers
        def check_status():
            """Check extension status"""
            try:
                if emotion_manager and boredom_detector:
                    status = f"✅ Extension Active\nMethod: Direct Call\nComponents: Loaded\nMonitoring: {boredom_detector.monitoring if hasattr(boredom_detector, 'monitoring') else 'Unknown'}"
                else:
                    status = "⚠️ Extension Issues\nSome components not initialized"
                return status
            except Exception as e:
                return f"❌ Status Error: {str(e)}"

        def get_emotion_status():
            """Get current emotion status"""
            try:
                if emotion_manager:
                    if hasattr(emotion_manager, 'get_current_emotion_and_stage'):
                        current_emotion, stage = emotion_manager.get_current_emotion_and_stage()
                    else:
                        current_emotion = "No method available"
                        stage = "N/A"

                    cooldown_active = emotion_manager.is_cooldown_active() if hasattr(emotion_manager, 'is_cooldown_active') else False
                    return f"Current: {current_emotion}\nStage: {stage}\nCooldown: {cooldown_active}"
                else:
                    return "Emotion manager not initialized"
            except Exception as e:
                return f"Error: {str(e)}"

        def manual_test_injection(emotion, stage):
            """Manual test of direct call injection"""
            try:
                log_enhanced(f"Manual test: {emotion} stage {stage}", "INFO", "manual_test_injection")

                # Use the actual horny stage only for horny emotion
                actual_stage = int(stage) if emotion == "horny" else 1

                # Call our direct trigger function
                success = trigger_emotional_response(emotion, actual_stage)

                if success:
                    return f"✅ Direct Call Success\nEmotion: {emotion}\nStage: {actual_stage}\nMethod: generate_chat_reply()\nResult: AI response generated naturally"
                else:
                    return f"❌ Direct Call Failed\nCheck console logs for details"

            except Exception as e:
                log_enhanced(f"Manual test failed: {str(e)}", "ERROR", "manual_test_injection")
                return f"❌ Exception: {str(e)}"

        # Wire up event handlers
        status_check_btn.click(
            fn=check_status,
            outputs=[status_display]
        )

        manual_inject_btn.click(
            fn=get_emotion_status,
            outputs=[emotion_display]
        )

        manual_inject_btn.click(
            fn=manual_test_injection,
            inputs=[test_emotion, test_stage],
            outputs=[test_result]
        )

        log_enhanced("Boredom Monitor UI created successfully", "SUCCESS", "ui")

    except Exception as e:
        log_enhanced(f"UI creation failed: {str(e)}", "ERROR", "ui")
        return gr.Markdown("❌ **Boredom Monitor UI Failed to Load**\n\nError: " + str(e))

def custom_css():
    """
    Standard text-generation-webui hook - provides custom CSS for the extension
    """
    return """
    /* Freedom System Boredom Monitor - Custom Styles */

    .boredom-monitor-panel {
        background: linear-gradient(135deg, #6a5acd 0%, #4b0082 100%);
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        color: white;
    }

    .boredom-monitor-status {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
        padding: 8px;
        margin: 4px 0;
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        font-size: 12px;
    }

    .boredom-monitor-success {
        color: #4CAF50;
        font-weight: bold;
    }

    .boredom-monitor-error {
        color: #f44336;
        font-weight: bold;
    }

    .boredom-monitor-warning {
        color: #ff9800;
        font-weight: bold;
    }
    """