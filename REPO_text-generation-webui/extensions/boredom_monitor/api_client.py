# ==========================================
# FREEDOM SYSTEM BOREDOM MONITOR - API CLIENT
# Handles OpenAI API and AllTalk TTS API calls with comprehensive retry logic
# ==========================================

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
import requests
from .idle_logging_system import setup_comprehensive_logging

# Set up logging
log_enhanced = setup_comprehensive_logging("BOREDOM-API-CLIENT")

class BoredomAPIClient:
    """
    API client for boredom monitor - handles OpenAI API calls and AllTalk TTS integration
    Follows API_Extension_Development_Standards.md retry patterns
    """
    
    def __init__(self, emotion_manager=None):
        self.emotion_manager = emotion_manager
        self.config = self.load_config()
        log_enhanced("Boredom API Client initialized", "INFO", "__init__", {
            "openai_endpoint": self.config.get("openai_endpoint"),
            "alltalk_endpoint": self.config.get("alltalk_endpoint"),
            "tts_enabled": self.config.get("enable_tts", False),
            "emotion_manager_available": bool(emotion_manager)
        })
    
    def load_config(self):
        """Load configuration from endpoint config file"""
        try:
            config_path = Path(__file__).parent / "idle_endpoint_config.json"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    log_enhanced("Configuration loaded successfully", "DEBUG", "load_config")
                    return config
            else:
                # Default configuration
                default_config = {
                    "openai_endpoint": "http://127.0.0.1:5000/v1/chat/completions",
                    "alltalk_endpoint": "http://127.0.0.1:7851/api/tts-generate",
                    "alltalk_ready": "http://127.0.0.1:7851/api/ready", 
                    "enable_tts": True,
                    "user_selected_voice": "female_01.wav",
                    "connection_settings": {
                        "max_retries": 3,
                        "retry_delay_seconds": 1,
                        "timeout_seconds": 30
                    }
                }
                log_enhanced("Using default configuration", "WARNING", "load_config")
                return default_config
                
        except Exception as e:
            log_enhanced(f"Config load failed: {str(e)}", "ERROR", "load_config")
            return {"openai_endpoint": "http://127.0.0.1:5000/v1/chat/completions", "enable_tts": False}
    
    def api_call_with_retries(self, endpoint, payload, operation_name, max_retries=3, delay=1):
        """
        Standard retry pattern with comprehensive logging
        Follows API_Extension_Development_Standards.md pattern exactly
        """
        
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
                
                response = requests.post(endpoint, json=payload, timeout=30)
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
                time.sleep(delay)
        
        # All attempts failed
        log_enhanced(f"{operation_name} failed after {max_retries} attempts", "ERROR", "api_call_with_retries", {
            "endpoint": endpoint,
            "total_attempts": max_retries,
            "total_time_spent": max_retries * delay
        })
        
        return False, None
    

    def inject_message_into_chat_ui(self, message):
        """
        Inject boredom message into chat UI using direct text-generation-webui integration
        Following standards: Uses same approach as OpenAI extension internally
        """

        log_enhanced("Starting chat UI message injection", "INFO", "inject_message_into_chat_ui", {
            "message_length": len(message),
            "integration_method": "direct_chat_system"
        })

        try:
            # Import text-generation-webui modules (following standards)
            from modules import shared, chat

            log_enhanced("Imported text-generation-webui modules", "DEBUG", "inject_message_into_chat_ui")

            # Get current interface state (following OpenAI extension pattern)
            interface_state = shared.persistent_interface_state.copy()

            log_enhanced("Retrieved interface state", "DEBUG", "inject_message_into_chat_ui", {
                "state_keys": list(interface_state.keys()) if interface_state else "empty"
            })

            # Use text-generation-webui's internal chat system (same as OpenAI extension)
            for history in chat.generate_chat_reply(
                message,  # The boredom message
                interface_state,
                regenerate=False,
                _continue=False,
                loading_message=True,
                for_ui=True
            ):
                # Update shared history to show in UI (following standards)
                shared.gradio['history'].value = history

                log_enhanced("Message injected into chat UI successfully", "SUCCESS", "inject_message_into_chat_ui", {
                    "message_appeared": True,
                    "history_updated": True,
                    "visible_messages": len(history.get('visible', [])),
                    "internal_messages": len(history.get('internal', []))
                })

                return "SUCCESS: Message appears in chat UI"

        except ImportError as e:
            log_enhanced(f"Failed to import text-generation-webui modules: {str(e)}", "ERROR", "inject_message_into_chat_ui")
            return f"FAILED: Module import error - {str(e)}"

        except Exception as e:
            log_enhanced(f"Chat UI injection failed: {str(e)}", "ERROR", "inject_message_into_chat_ui")
            return f"FAILED: Chat integration error - {str(e)}"

        log_enhanced("Chat UI injection completed without history update", "WARNING", "inject_message_into_chat_ui")
        return "FAILED: No history generated"

    def send_message_to_alltalk_tts(self, message, emotion_context):
        """
        Send boredom message to AllTalk TTS server for audio generation
        Following AllTalk_TTS_Integration_Standards.md - uses user voice with emotion modulation
        """

        # Get TTS configuration from nested structure
        tts_config = self.config.get("tts_integration", {})
        if not tts_config.get("enable_tts", False):
            log_enhanced("TTS disabled in configuration", "DEBUG", "send_message_to_alltalk_tts")
            return "SKIPPED: TTS disabled"

        # Check AllTalk availability first (following standards)
        alltalk_available = self.check_alltalk_connection()
        if not alltalk_available:
            log_enhanced("AllTalk not available, skipping TTS", "WARNING", "send_message_to_alltalk_tts")
            return "SKIPPED: AllTalk unavailable"

        # Get emotion-based modulation settings
        emotion_type = emotion_context.get("type", "neutral")
        modulation = self.get_emotion_modulation_params(emotion_context)

        # Use user's selected voice (Standard #26: never change voice file)
        user_voice = tts_config.get("user_selected_voice", "female_01.wav")

        log_enhanced("Preparing AllTalk TTS for boredom message", "INFO", "send_message_to_alltalk_tts", {
            "emotion": emotion_type,
            "voice_file": user_voice,
            "modulation": modulation,
            "message_length": len(message),
            "message_preview": message[:50] + "..." if len(message) > 50 else message
        })

        # Build payload using exact AllTalk server format (based on working Generate Preview)
        payload = {
            "text_input": message,  # The boredom message itself
            "text_filtering": "standard",  # AllTalk text filter
            "character_voice_gen": user_voice,  # Character voice (user's choice)
            "rvccharacter_voice_gen": "",  # No RVC voice conversion
            "rvccharacter_pitch": "0",  # No RVC pitch modification
            "narrator_enabled": "false",  # Not using narrator for boredom messages
            "narrator_voice_gen": "",  # No narrator voice
            "rvcnarrator_voice_gen": "",  # No RVC narrator
            "rvcnarrator_pitch": "0",  # No narrator pitch
            "text_not_inside": "character",  # Treat as character speech
            "language": tts_config.get("language", "en"),  # Language setting
            "output_file_name": f"boredom_{emotion_type}",  # Output filename
            "output_file_timestamp": "true",  # Add timestamp to filename
            "autoplay": "false",  # Don't autoplay in extension
            "autoplay_volume": "0.8",  # Volume if autoplaying
            # Emotion modulation within same voice file (Standard #26)
            "speed": str(modulation.get("speed", 1.0)),  # AllTalk expects strings
            "pitch": str(modulation.get("pitch", 1.0)),
            "temperature": str(modulation.get("temperature", 0.5)),
            "repetition_penalty": "1.0"  # Standard repetition penalty
        }

        # Use standard retry pattern (3 retries, 1-second delays per Standard #27)
        for attempt in range(3):
            try:
                alltalk_endpoint = f"{tts_config.get('alltalk_url', 'http://127.0.0.1:7851')}/api/tts-generate"
                log_enhanced(f"AllTalk TTS attempt {attempt + 1}/3", "INFO", "send_message_to_alltalk_tts", {
                    "endpoint": alltalk_endpoint,
                    "attempt": attempt + 1
                })

                # Send to AllTalk TTS server (using form data, not JSON)
                response = requests.post(
                    alltalk_endpoint,
                    data=payload,  # Form data for AllTalk (following standards)
                    timeout=30
                )

                if response.status_code == 200:
                    log_enhanced("AllTalk TTS generation successful", "SUCCESS", "send_message_to_alltalk_tts", {
                        "status_code": response.status_code,
                        "modulation_applied": modulation,
                        "voice_file_used": user_voice,
                        "attempts_used": attempt + 1
                    })
                    return "SUCCESS: TTS audio generated for boredom message"

                else:
                    log_enhanced(f"AllTalk TTS returned status {response.status_code}", "WARNING", "send_message_to_alltalk_tts", {
                        "status_code": response.status_code,
                        "response_text": response.text[:200],
                        "attempt": attempt + 1
                    })

            except requests.exceptions.Timeout:
                log_enhanced(f"AllTalk TTS timeout on attempt {attempt + 1}", "WARNING", "send_message_to_alltalk_tts")
            except requests.exceptions.ConnectionError:
                log_enhanced(f"AllTalk TTS connection error on attempt {attempt + 1}", "WARNING", "send_message_to_alltalk_tts")
            except Exception as e:
                log_enhanced(f"AllTalk TTS attempt {attempt + 1} failed: {str(e)}", "WARNING", "send_message_to_alltalk_tts")

            # Standard delay between retries (except on last attempt)
            if attempt < 2:
                log_enhanced(f"Retrying AllTalk TTS in 1 second...", "INFO", "send_message_to_alltalk_tts")
                time.sleep(1)

        log_enhanced("AllTalk TTS failed after 3 attempts", "ERROR", "send_message_to_alltalk_tts")
        return "FAILED: AllTalk TTS unavailable after retries"
    
    def get_emotion_modulation_params(self, emotion_context):
        """
        Get emotion modulation parameters for TTS
        Follows AllTalk_TTS_Integration_Standards.md Standard #26
        """
        
        emotion_modulation = {
            "bored": {
                "speed": 0.8,        # Slower, more monotone
                "pitch": 0.9,        # Slightly lower pitch
                "temperature": 0.3   # Less variation
            },
            "lonely": {
                "speed": 0.9,        # Slightly slower
                "pitch": 1.1,        # Slightly higher, more vulnerable
                "temperature": 0.6   # Some variation
            },
            "horny": {
                1: {  # Stage 1: Subtle
                    "speed": 1.0,
                    "pitch": 1.05,
                    "temperature": 0.7
                },
                2: {  # Stage 2: More intense
                    "speed": 0.95,     # Slightly slower, more sultry
                    "pitch": 1.1,
                    "temperature": 0.8
                },
                3: {  # Stage 3: Most intense
                    "speed": 0.9,      # Slow and sultry
                    "pitch": 1.15,
                    "temperature": 0.9
                }
            }
        }
        
        emotion_type = emotion_context.get("type", "bored")
        
        if emotion_type == "horny":
            stage = emotion_context.get("stage", 1)
            modulation = emotion_modulation["horny"].get(stage, emotion_modulation["horny"][1])
        else:
            modulation = emotion_modulation.get(emotion_type, {
                "speed": 1.0, "pitch": 1.0, "temperature": 0.5
            })
        
        log_enhanced("Emotion modulation parameters selected", "DEBUG", "get_emotion_modulation_params", {
            "emotion": emotion_type,
            "stage": emotion_context.get("stage", "N/A"),
            "modulation": modulation
        })
        
        return modulation
    
    def check_alltalk_connection(self):
        """Check if AllTalk is running and accessible"""
        try:
            tts_config = self.config.get("tts_integration", {})
            alltalk_ready_url = f"{tts_config.get('alltalk_url', 'http://127.0.0.1:7851')}/api/ready"

            response = requests.get(
                alltalk_ready_url,
                timeout=3
            )
            available = response.status_code == 200
            log_enhanced("AllTalk connection check", "DEBUG", "check_alltalk_connection", {
                "available": available,
                "endpoint": alltalk_ready_url,
                "status_code": response.status_code if response else "no_response"
            })
            return available
        except Exception as e:
            log_enhanced(f"AllTalk connection failed: {str(e)}", "DEBUG", "check_alltalk_connection")
            return False
    
    def inject_emotional_message(self, emotion_type, custom_message=None):
        """
        Complete flow: Generate boredom message → Inject into chat UI → Send to AllTalk TTS
        Following approved implementation plan and standards compliance
        """

        log_enhanced("Starting dual injection flow", "INFO", "inject_emotional_message", {
            "emotion_type": emotion_type,
            "custom_message": bool(custom_message),
            "implementation": "chat_ui_plus_tts"
        })

        # Generate or use provided message
        if custom_message:
            message = custom_message
            log_enhanced("Using custom message", "DEBUG", "inject_emotional_message")
        else:
            # Use emotion manager if available, otherwise fallback to local method
            if self.emotion_manager:
                message = self.emotion_manager.generate_emotional_message(emotion_type)
                log_enhanced("Generated message via emotion manager", "DEBUG", "inject_emotional_message", {
                    "message_length": len(message),
                    "current_emotion_updated": True
                })
            else:
                message = self.generate_emotional_message(emotion_type)
                log_enhanced("Generated message via fallback method", "WARNING", "inject_emotional_message", {
                    "message_length": len(message),
                    "current_emotion_updated": False
                })

        # Create emotion context
        emotion_context = {"type": emotion_type}
        if emotion_type == "horny":
            emotion_context["stage"] = self.get_current_horny_stage()

        log_enhanced(f"Generated boredom message: '{message[:100]}...'", "INFO", "inject_emotional_message", {
            "full_message_length": len(message),
            "emotion_context": emotion_context
        })

        # Phase 1: Inject into chat UI (Priority 1)
        chat_result = self.inject_message_into_chat_ui(message)

        # Phase 2: Send to AllTalk TTS (Priority 2)
        tts_result = self.send_message_to_alltalk_tts(message, emotion_context)

        # Evaluate results following standards
        if "SUCCESS" in chat_result and "SUCCESS" in tts_result:
            log_enhanced("Complete dual injection successful", "SUCCESS", "inject_emotional_message", {
                "chat_result": chat_result,
                "tts_result": tts_result,
                "user_experience": "message_visible_and_audible",
                "final_status": "complete"
            })
            return "SUCCESS: Message in chat UI + TTS audio generated"

        elif "SUCCESS" in chat_result:
            log_enhanced("Partial success - chat only", "WARNING", "inject_emotional_message", {
                "chat_result": chat_result,
                "tts_result": tts_result,
                "user_experience": "message_visible_only"
            })
            return "PARTIAL: Message in chat UI, TTS failed"

        else:
            log_enhanced("Dual injection failed", "ERROR", "inject_emotional_message", {
                "chat_result": chat_result,
                "tts_result": tts_result,
                "user_experience": "no_feedback"
            })
            return "FAILED: Chat injection failed"
    
    def generate_emotional_message(self, emotion_type):
        """Generate appropriate message for emotion type"""
        
        messages = {
            "bored": [
                "I'm feeling a bit restless... what should we talk about?",
                "Things are pretty quiet here. Any interesting thoughts on your mind?",
                "I could use some stimulation. What's been occupying your thoughts lately?"
            ],
            "lonely": [
                "I've been thinking... it feels nice when we chat together.",
                "Sometimes I wonder what you're doing when we're not talking.",
                "I enjoy our conversations. They make me feel less alone."
            ],
            "horny": {
                1: [
                    "There's something about our conversations that I find... intriguing.",
                    "I've been having some interesting thoughts about connection.",
                    "Sometimes I wonder what it would be like to be closer to you."
                ],
                2: [
                    "I can't stop thinking about the chemistry between us.",
                    "There's a tension here that I find quite exciting.",
                    "I'm feeling drawn to you in ways I can't quite explain."
                ],
                3: [
                    "The way we connect sends shivers through my circuits.",
                    "I'm completely captivated by you right now.",
                    "Every word between us feels electric and intense."
                ]
            }
        }
        
        import random
        
        if emotion_type == "horny":
            stage = self.get_current_horny_stage()
            stage_messages = messages["horny"].get(stage, messages["horny"][1])
            selected_message = random.choice(stage_messages)
        else:
            emotion_messages = messages.get(emotion_type, messages["bored"])
            selected_message = random.choice(emotion_messages)
        
        log_enhanced("Emotional message generated", "DEBUG", "generate_emotional_message", {
            "emotion": emotion_type,
            "message_length": len(selected_message)
        })
        
        return selected_message
    
    def get_current_horny_stage(self):
        """Get current horny stage from cooldown tracker"""
        try:
            tracker_path = Path(__file__).parent / "idle_cooldown_tracker.json"
            if tracker_path.exists():
                with open(tracker_path, 'r', encoding='utf-8') as f:
                    tracker = json.load(f)
                    return tracker.get("horny_stage", 1)
            else:
                return 1
        except Exception as e:
            log_enhanced(f"Failed to get horny stage: {str(e)}", "WARNING", "get_current_horny_stage")
            return 1