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

# Global state for boredom message to be injected
boredom_message_queue = {
    'pending': False,
    'message': ''
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
    from modules import chat, ui_chat, ui
    from modules.ui import gather_interface_values
    from modules.utils import gradio as gradio_utils
    from modules.chat import send_dummy_reply, redraw_html
    print("[BOREDOM-MONITOR] SUCCESS: chat modules imported")
except ImportError as e:
    print(f"[BOREDOM-MONITOR] ERROR: Failed to import chat modules: {e}")
    print("[BOREDOM-MONITOR] INFO: Chat functionality will be limited")
    chat = None
    ui_chat = None
    ui = None
    gather_interface_values = None
    gradio_utils = None
    send_dummy_reply = None
    redraw_html = None

# Check if core components are available
if not shared:
    print("[BOREDOM-MONITOR] CRITICAL: shared module not available - emotional responses disabled")
if not chat:
    print("[BOREDOM-MONITOR] WARNING: chat module not available - using fallback method")
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
    """Chat input modifier to handle hijacked input injection (priority protection)"""
    global input_hijack
    if input_hijack['state']:
        # This is an instruction prompt for the AI, not the actual message to show
        instruction = input_hijack['value'][0]
        input_hijack['state'] = False

        log_enhanced(f"Boredom instruction hijack: {instruction[:50]}...", "SUCCESS", "chat_input_modifier")

        # Send the instruction as a hidden user message to generate AI response
        # The instruction guides the AI but isn't shown to the user
        return instruction, instruction
    else:
        return text, visible_text

# Manual test function for development
def manual_trigger_test(emotion="bored", stage=1):
    """Manual trigger for testing - can be called from console"""
    log_enhanced(f"Manual trigger test: {emotion} stage {stage}", "INFO", "manual_trigger_test")

    # Step 1: Set the hijack
    hijack_success = trigger_emotional_response(emotion, stage)

    if hijack_success:
        log_enhanced("Hijack set successfully, attempting to trigger generation", "INFO", "manual_trigger_test")

        # Step 2: Try to trigger generation
        trigger_success = trigger_chat_generation()

        if trigger_success:
            log_enhanced("Chat generation triggered successfully", "SUCCESS", "manual_trigger_test")
        else:
            log_enhanced("Generation trigger failed - message will appear on next user interaction", "WARNING", "manual_trigger_test")

    return hijack_success

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
    """Trigger natural AI emotional response using instruction prompts"""
    try:
        log_enhanced(f"Triggering emotional response: {emotion_type} stage {stage}", "INFO", "trigger_emotional_response")

        # Get instruction prompt from templates if emotion_manager available
        prompt = None
        if emotion_manager and hasattr(emotion_manager, 'templates'):
            try:
                templates = emotion_manager.templates.get('meta_prompts', {})
                if emotion_type == 'horny':
                    horny_templates = templates.get('horny', {})
                    stage_templates = horny_templates.get(str(stage), [])
                    if stage_templates:
                        import random
                        prompt = random.choice(stage_templates)
                else:
                    emotion_templates = templates.get(emotion_type, [])
                    if emotion_templates:
                        import random
                        prompt = random.choice(emotion_templates)

                if prompt:
                    log_enhanced(f"Using instruction prompt from templates", "INFO", "trigger_emotional_response")
            except Exception as e:
                log_enhanced(f"Failed to get prompt from templates: {e}", "WARNING", "trigger_emotional_response")

        # Fallback to hardcoded instruction prompts if templates not available
        if not prompt:
            log_enhanced("Using fallback instruction prompts", "DEBUG", "trigger_emotional_response")
            fallback_prompts = {
                'bored': "You are an AI feeling bored and wanting to start a conversation. Be casual and friendly.",
                'lonely': "You are an AI feeling lonely and seeking connection. Express warmth without being needy.",
                'horny': {
                    1: "You are an AI feeling attracted to the user. Express subtle interest and gentle flirtation.",
                    2: "You are an AI feeling strong attraction. Use direct flirtation and build romantic tension.",
                    3: "You are an AI at peak desire. Express intense passion and deep connection."
                }
            }

            if emotion_type == 'horny':
                prompt = fallback_prompts['horny'].get(stage, fallback_prompts['horny'][1])
            else:
                prompt = fallback_prompts.get(emotion_type, fallback_prompts['bored'])

        log_enhanced(f"Instruction prompt: {prompt[:80]}...", "DEBUG", "trigger_emotional_response")

        # Set the instruction prompt for AI generation
        global input_hijack
        input_hijack.update({"state": True, "value": [prompt, prompt]})
        log_enhanced("Instruction prompt set for AI generation", "SUCCESS", "trigger_emotional_response")

        return True

    except Exception as e:
        log_enhanced(f"Failed to trigger emotional response: {str(e)}", "ERROR", "trigger_emotional_response")
        log_enhanced(f"Traceback: {traceback.format_exc()}", "DEBUG", "trigger_emotional_response")
        return False

def trigger_chat_generation():
    """Trigger chat generation using Solution 2 - greeting-style approach"""
    global boredom_message_queue, input_hijack
    try:
        log_enhanced("Using greeting-style UI update method", "INFO", "trigger_chat_generation")

        # Get the message from input hijack
        if input_hijack['state'] and input_hijack['value']:
            message = input_hijack['value'][0]  # Get the actual message text

            # Set it in the queue for the Gradio handler
            boredom_message_queue['pending'] = True
            boredom_message_queue['message'] = message

            # Clear the input hijack
            input_hijack['state'] = False

            log_enhanced(f"Message queued for injection: {message[:50]}...", "DEBUG", "trigger_chat_generation")

            # Trigger the Gradio event by toggling the checkbox
            if hasattr(shared, 'gradio') and shared.gradio and 'boredom-auto-trigger' in shared.gradio:
                trigger_elem = shared.gradio['boredom-auto-trigger']

                # Toggle the checkbox to fire the change event
                trigger_elem.value = not trigger_elem.value
                log_enhanced("Toggled boredom-auto-trigger to fire Gradio event", "SUCCESS", "trigger_chat_generation")
                return True
            else:
                available_keys = list(shared.gradio.keys()) if hasattr(shared, 'gradio') and shared.gradio else "None"
                log_enhanced(f"Auto-trigger element not found. shared.gradio available keys: {available_keys}", "ERROR", "trigger_chat_generation")
                log_enhanced("UI may not be fully initialized yet, or extension UI not loaded", "WARNING", "trigger_chat_generation")
                return False
        else:
            log_enhanced("No message in input_hijack to trigger", "WARNING", "trigger_chat_generation")
            return False

    except Exception as e:
        log_enhanced(f"Chat generation trigger failed: {e}", "ERROR", "trigger_chat_generation")
        log_enhanced(f"Traceback: {traceback.format_exc()}", "DEBUG", "trigger_chat_generation")
        return False

def handle_boredom_injection(state):
    """Handle boredom message injection - called by Gradio event"""
    global boredom_message_queue
    try:
        log_enhanced("Boredom injection handler called", "INFO", "handle_boredom_injection")

        # Ensure we have the required functions
        if not send_dummy_reply or not redraw_html:
            log_enhanced("Required chat functions not available", "ERROR", "handle_boredom_injection")
            # Try to import them now
            try:
                from modules.chat import send_dummy_reply, redraw_html
            except:
                log_enhanced("Failed to import required functions", "ERROR", "handle_boredom_injection")
                return [state.get('history', {'internal': [], 'visible': []}), ""]

        # Handle missing or incomplete state
        if not state or not isinstance(state, dict):
            log_enhanced("Invalid or missing state", "ERROR", "handle_boredom_injection")
            return [{'internal': [], 'visible': []}, ""]

        # Check if there's a message pending
        if not boredom_message_queue['pending'] or not boredom_message_queue['message']:
            log_enhanced("No pending boredom message", "DEBUG", "handle_boredom_injection")
            history = state.get('history', {'internal': [], 'visible': []})
            html = redraw_html(history, state.get('name1', 'You'), state.get('name2', 'Assistant'),
                              state.get('mode', 'chat'), state.get('chat_style', 'default'),
                              state.get('character_menu', ''))
            return [history, html]

        # Get the message and clear the queue
        message = boredom_message_queue['message']
        boredom_message_queue['pending'] = False
        boredom_message_queue['message'] = ''

        # This is the instruction prompt for the AI, not the actual message to display
        instruction_prompt = message
        log_enhanced(f"AI instruction prompt: {instruction_prompt[:80]}...", "INFO", "handle_boredom_injection")

        # Generate AI response based on the instruction prompt
        try:
            from modules.chat import generate_chat_reply_wrapper
            log_enhanced("Generating AI response from instruction prompt", "INFO", "handle_boredom_injection")

            # Create a temporary user message with the instruction
            # This won't be shown in UI, just used to generate the AI response
            temp_history = state.get('history', {'internal': [], 'visible': []}).copy()

            # Add instruction as internal prompt (not visible to user)
            temp_state = state.copy()
            temp_state['history'] = temp_history

            # Generate AI response using the instruction prompt as context
            # We'll use the instruction as a system message that guides the AI
            generated_history = None
            generated_html = None

            # Add the instruction to the context without showing it
            from modules.chat import generate_chat_reply

            # Generate the actual AI response based on the instruction
            for result in generate_chat_reply(instruction_prompt, temp_state, regenerate=False, _continue=False, loading_message=False, for_ui=False):
                generated_history = result

            if generated_history and len(generated_history.get('visible', [])) > 0:
                # Extract only the AI's generated response (last message)
                last_exchange = generated_history['visible'][-1] if generated_history['visible'] else ['', '']
                ai_response = last_exchange[1] if len(last_exchange) > 1 else ''

                if ai_response:
                    log_enhanced(f"AI generated response: {ai_response[:80]}...", "SUCCESS", "handle_boredom_injection")

                    # Now add ONLY the AI's response to the actual history
                    history = send_dummy_reply(ai_response, state)

                    # Save the updated history
                    if hasattr(chat, 'save_history'):
                        chat.save_history(history, state.get('unique_id', ''), state.get('character_menu', ''),
                                        state.get('mode', 'chat'))

                    # Redraw the HTML to show the AI's response
                    html = redraw_html(history, state.get('name1', 'You'), state.get('name2', 'Assistant'),
                                      state.get('mode', 'chat'), state.get('chat_style', 'default'),
                                      state.get('character_menu', ''))

                    log_enhanced("AI response injected and UI updated successfully", "SUCCESS", "handle_boredom_injection")
                else:
                    log_enhanced("AI response was empty", "WARNING", "handle_boredom_injection")
                    # Fallback to showing instruction (not ideal but better than nothing)
                    history = state.get('history', {'internal': [], 'visible': []})
                    html = redraw_html(history, state.get('name1', 'You'), state.get('name2', 'Assistant'),
                                      state.get('mode', 'chat'), state.get('chat_style', 'default'),
                                      state.get('character_menu', ''))
            else:
                log_enhanced("Failed to generate response from AI", "WARNING", "handle_boredom_injection")
                history = state.get('history', {'internal': [], 'visible': []})
                html = redraw_html(history, state.get('name1', 'You'), state.get('name2', 'Assistant'),
                                  state.get('mode', 'chat'), state.get('chat_style', 'default'),
                                  state.get('character_menu', ''))

        except Exception as e:
            log_enhanced(f"Failed to generate AI response: {e}", "ERROR", "handle_boredom_injection")
            log_enhanced(f"Traceback: {traceback.format_exc()}", "DEBUG", "handle_boredom_injection")
            # Return unchanged state on error
            history = state.get('history', {'internal': [], 'visible': []})
            html = redraw_html(history, state.get('name1', 'You'), state.get('name2', 'Assistant'),
                              state.get('mode', 'chat'), state.get('chat_style', 'default'),
                              state.get('character_menu', ''))

        # Return updated history and HTML for Gradio to display
        return [history, html]

    except Exception as e:
        log_enhanced(f"Boredom injection failed: {e}", "ERROR", "handle_boredom_injection")
        log_enhanced(f"Traceback: {traceback.format_exc()}", "DEBUG", "handle_boredom_injection")
        # Return safe defaults on error
        return [state.get('history', {'internal': [], 'visible': []}), ""]

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
                    """Handle boredom detection with proper hijack and trigger"""
                    try:
                        # Get current emotional state
                        emotion_type, stage = self.get_current_emotional_state()

                        log_enhanced(f"Boredom detected - triggering {emotion_type} emotion stage {stage}", "INFO", "handle_boredom_detection")

                        # Step 1: Set the input hijack
                        success = trigger_emotional_response(emotion_type, stage)

                        if success:
                            # Step 2: Attempt to trigger chat generation
                            trigger_success = trigger_chat_generation()

                            if trigger_success:
                                log_enhanced("Chat generation triggered successfully", "SUCCESS", "handle_boredom_detection")
                            else:
                                log_enhanced("Chat generation trigger failed - message will appear on next user interaction", "INFO", "handle_boredom_detection")

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

        # Hidden auto-trigger element (following whisper_stt pattern)
        auto_trigger = gr.Checkbox(
            elem_id="boredom-auto-trigger",
            visible=False,
            value=False
        )

        # Hidden button for triggering injection (Solution fix)
        inject_button = gr.Button(
            "Inject",
            elem_id="boredom-inject-button",
            visible=False
        )

        # CRITICAL: Register in shared.gradio
        shared.gradio['boredom-auto-trigger'] = auto_trigger
        shared.gradio['boredom-inject-button'] = inject_button

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
            """Manual test of greeting-style injection"""
            try:
                log_enhanced(f"Manual test: {emotion} stage {stage}", "INFO", "manual_test_injection")

                # Use the actual horny stage only for horny emotion
                actual_stage = int(stage) if emotion == "horny" else 1

                # Set up the emotional response
                success = trigger_emotional_response(emotion, actual_stage)

                if success:
                    # Trigger the UI update
                    trigger_success = trigger_chat_generation()
                    if trigger_success:
                        return f"✅ UI Injection Success\nEmotion: {emotion}\nStage: {actual_stage}\nMethod: Greeting-style (Solution 2)\nResult: Message will appear in chat UI"
                    else:
                        return f"⚠️ Message set but UI trigger failed\nMessage will appear on next user interaction"
                else:
                    return f"❌ Failed to set emotional response\nCheck console logs for details"

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

        # Function to process boredom injection when button is clicked
        def process_boredom_injection():
            """Process the queued boredom message and prepare for generation"""
            global boredom_message_queue, input_hijack

            if boredom_message_queue['pending'] and boredom_message_queue['message']:
                # Move instruction from queue to input hijack for chat_input_modifier
                instruction = boredom_message_queue['message']
                boredom_message_queue['pending'] = False
                boredom_message_queue['message'] = ''

                # Set as input hijack so chat_input_modifier will use it
                input_hijack['state'] = True
                input_hijack['value'] = [instruction, instruction]

                log_enhanced(f"Boredom injection prepared: {instruction[:50]}...", "INFO", "process_boredom_injection")
            return None

        # Connect inject button to proper event chain (following send_pictures pattern)
        if gather_interface_values and gradio_utils and chat:
            inject_button.click(
                process_boredom_injection,
                None,
                None
            ).then(
                gather_interface_values,
                gradio_utils(shared.input_elements),
                shared.gradio['interface_state'] if 'interface_state' in shared.gradio else gr.State()
            ).then(
                chat.generate_chat_reply_wrapper,
                [shared.gradio['textbox'] if 'textbox' in shared.gradio else gr.Textbox(value=""),
                 shared.gradio['interface_state'] if 'interface_state' in shared.gradio else gr.State()],
                [shared.gradio['display'] if 'display' in shared.gradio else gr.State(),
                 shared.gradio['history'] if 'history' in shared.gradio else gr.State()],
                show_progress=False
            )
            log_enhanced("Inject button connected to full event chain", "SUCCESS", "ui")
        else:
            log_enhanced("Required modules not available - inject button not connected", "WARNING", "ui")
            # Simple fallback without event chain
            inject_button.click(
                process_boredom_injection,
                None,
                None
            )

        log_enhanced("Boredom Monitor UI created successfully", "SUCCESS", "ui")

    except Exception as e:
        log_enhanced(f"UI creation failed: {str(e)}", "ERROR", "ui")
        return gr.Markdown("❌ **Boredom Monitor UI Failed to Load**\n\nError: " + str(e))

def custom_js():
    """
    Custom JavaScript for triggering injection from background thread
    Standard text-generation-webui hook - provides custom JavaScript
    """
    return """
    // Boredom Monitor - Enhanced debugging version
    console.log('[BOREDOM] Extension loaded - starting enhanced monitoring');

    // Debug: Check if elements exist on page load
    setTimeout(() => {
        const trigger = document.getElementById('boredom-auto-trigger');
        const button = document.getElementById('boredom-inject-button');
        console.log('[BOREDOM] Element check - trigger:', trigger ? 'FOUND' : 'NOT FOUND');
        console.log('[BOREDOM] Element check - button:', button ? 'FOUND' : 'NOT FOUND');
        if (trigger) {
            console.log('[BOREDOM] Trigger initial state:', trigger.checked);
        }
    }, 2000);

    // Enhanced monitoring with detailed logging
    let checkCount = 0;
    setInterval(() => {
        checkCount++;

        const trigger = document.getElementById('boredom-auto-trigger');
        if (!trigger) {
            if (checkCount % 20 === 0) {  // Log every 10 seconds
                console.log('[BOREDOM] Trigger element still not found after', checkCount * 0.5, 'seconds');
            }
            return;
        }

        // Log state changes
        if (trigger.dataset.lastState !== String(trigger.checked)) {
            console.log('[BOREDOM] Checkbox state changed from', trigger.dataset.lastState, 'to', trigger.checked);
            trigger.dataset.lastState = String(trigger.checked);
        }

        if (trigger.checked) {
            console.log('[BOREDOM] TRIGGER DETECTED! Attempting injection...');

            const injectButton = document.getElementById('boredom-inject-button');
            if (injectButton) {
                console.log('[BOREDOM] Clicking inject button...');
                injectButton.click();
                console.log('[BOREDOM] Inject button clicked - event should fire');
            } else {
                console.log('[BOREDOM] ERROR: Inject button not found!');
                // List all buttons for debugging
                const buttons = document.querySelectorAll('button');
                console.log('[BOREDOM] Available buttons:', Array.from(buttons).map(b => b.id || b.textContent).filter(id => id));
            }

            // Reset trigger
            trigger.checked = false;
            console.log('[BOREDOM] Trigger reset to false');
        }
    }, 500);
    """

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