# ==========================================
# FREEDOM SYSTEM BOREDOM MONITOR - BOREDOM DETECTOR
# Idle detection and emotional message injection trigger system
# Follows API_Extension_Development_Standards.md retry patterns
# ==========================================

import asyncio
import json
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from .idle_logging_system import setup_comprehensive_logging

# Set up logging
log_enhanced = setup_comprehensive_logging("BOREDOM-DETECTOR")

class BoredomDetector:
    """
    Detects user idle periods and triggers emotional message injections
    Follows API_Extension_Development_Standards.md patterns
    """
    
    def __init__(self, api_client, emotion_manager):
        self.api_client = api_client
        self.emotion_manager = emotion_manager
        self.config = self.load_config()
        
        # State tracking
        self.monitoring_active = False
        self.last_activity_time = datetime.now()
        self.detection_thread = None
        self.injection_history = []
        
        log_enhanced("Boredom detector initialized", "INFO", "__init__", {
            "idle_threshold": self.config.get("idle_threshold_minutes", 7),
            "api_client_available": bool(api_client),
            "emotion_manager_available": bool(emotion_manager)
        })
    
    def load_config(self):
        """Load configuration from response config file"""
        try:
            config_path = Path(__file__).parent / "idle_response_config.json"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    log_enhanced("Configuration loaded successfully", "DEBUG", "load_config")
                    return config
            else:
                # Default configuration
                default_config = {
                    "idle_threshold_minutes": 7,
                    "emotion_weights": {
                        "bored": 0.4,
                        "lonely": 0.3,
                        "horny": 0.3
                    },
                    "horny_cooldown_minutes": 60,
                    "min_injection_interval_minutes": 2
                }
                log_enhanced("Using default configuration", "WARNING", "load_config")
                return default_config
                
        except Exception as e:
            log_enhanced(f"Config load failed: {str(e)}", "ERROR", "load_config")
            return {"idle_threshold_minutes": 7, "min_injection_interval_minutes": 2}
    
    def start_monitoring(self):
        """Start idle detection monitoring in background thread"""
        if self.monitoring_active:
            log_enhanced("Monitoring already active", "WARNING", "start_monitoring")
            return
        
        try:
            self.monitoring_active = True
            self.last_activity_time = datetime.now()
            
            # Start monitoring thread
            self.detection_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True,
                name="BoredomDetector"
            )
            self.detection_thread.start()
            
            log_enhanced("Boredom monitoring started", "SUCCESS", "start_monitoring", {
                "idle_threshold": self.config.get("idle_threshold_minutes", 7),
                "thread_name": self.detection_thread.name
            })
            
        except Exception as e:
            log_enhanced(f"Failed to start monitoring: {str(e)}", "ERROR", "start_monitoring")
            self.monitoring_active = False
    
    def stop_monitoring(self):
        """Stop idle detection monitoring"""
        if not self.monitoring_active:
            log_enhanced("Monitoring not active", "DEBUG", "stop_monitoring")
            return
        
        try:
            self.monitoring_active = False
            
            if self.detection_thread and self.detection_thread.is_alive():
                # Wait for thread to finish gracefully
                self.detection_thread.join(timeout=5.0)
            
            log_enhanced("Boredom monitoring stopped", "INFO", "stop_monitoring")
            
        except Exception as e:
            log_enhanced(f"Error stopping monitoring: {str(e)}", "ERROR", "stop_monitoring")
    
    def record_user_activity(self):
        """Record user activity to reset idle timer"""
        try:
            self.last_activity_time = datetime.now()
            
            log_enhanced("User activity recorded", "DEBUG", "record_user_activity", {
                "activity_time": self.last_activity_time.strftime("%H:%M:%S")
            })
            
        except Exception as e:
            log_enhanced(f"Failed to record activity: {str(e)}", "ERROR", "record_user_activity")
    
    def is_idle(self):
        """Check if user has been idle beyond threshold"""
        try:
            idle_threshold = self.config.get("idle_threshold_minutes", 7)
            current_time = datetime.now()
            idle_duration = current_time - self.last_activity_time
            idle_minutes = idle_duration.total_seconds() / 60
            
            is_currently_idle = idle_minutes >= idle_threshold
            
            if is_currently_idle:
                log_enhanced(f"User idle detected", "INFO", "is_idle", {
                    "idle_minutes": round(idle_minutes, 1),
                    "threshold": idle_threshold
                })
            
            return is_currently_idle
            
        except Exception as e:
            log_enhanced(f"Idle check failed: {str(e)}", "ERROR", "is_idle")
            return False
    
    def can_inject_message(self):
        """Check if enough time has passed since last injection"""
        try:
            min_interval = self.config.get("min_injection_interval_minutes", 2)
            
            if not self.injection_history:
                return True
            
            last_injection = self.injection_history[-1]["timestamp"]
            current_time = datetime.now()
            time_since_last = current_time - last_injection
            minutes_since_last = time_since_last.total_seconds() / 60
            
            can_inject = minutes_since_last >= min_interval
            
            if not can_inject:
                log_enhanced(f"Injection too recent", "DEBUG", "can_inject_message", {
                    "minutes_since_last": round(minutes_since_last, 1),
                    "min_interval": min_interval
                })
            
            return can_inject
            
        except Exception as e:
            log_enhanced(f"Injection check failed: {str(e)}", "ERROR", "can_inject_message")
            return True  # Default to allowing injection
    
    def _monitoring_loop(self):
        """Main monitoring loop - runs in background thread"""
        log_enhanced("Monitoring loop started", "INFO", "_monitoring_loop")
        
        try:
            while self.monitoring_active:
                # Check if conditions are met for injection
                if self.is_idle() and self.can_inject_message():
                    # Trigger emotional message injection
                    asyncio.run(self._trigger_emotional_injection())
                
                # Sleep for 30 seconds before next check
                time.sleep(30)
                
        except Exception as e:
            log_enhanced(f"Monitoring loop error: {str(e)}", "ERROR", "_monitoring_loop")
        
        log_enhanced("Monitoring loop ended", "INFO", "_monitoring_loop")
    
    async def _trigger_emotional_injection(self):
        """Trigger emotional message injection via API client"""
        try:
            log_enhanced("Triggering emotional injection", "INFO", "_trigger_emotional_injection")
            
            # Generate emotional message
            emotion_type = self.emotion_manager.select_emotion_type()
            
            # Create emotion context
            emotion_context = {"type": emotion_type}
            if emotion_type == "horny":
                emotion_context["stage"] = self.emotion_manager.get_current_horny_stage()
            
            # Record injection attempt
            injection_record = {
                "timestamp": datetime.now(),
                "emotion_type": emotion_type,
                "emotion_context": emotion_context,
                "status": "attempted"
            }
            
            # Attempt injection via API client
            if self.api_client:
                result = await self.api_client.inject_emotional_message(emotion_type)
                
                injection_record["status"] = "success" if "SUCCESS" in result else "failed"
                injection_record["result"] = result
                
                log_enhanced("Emotional injection completed", "SUCCESS", "_trigger_emotional_injection", {
                    "emotion": emotion_type,
                    "stage": emotion_context.get("stage", "N/A"),
                    "result": result[:100]
                })
            else:
                injection_record["status"] = "failed"
                injection_record["result"] = "API client not available"
                
                log_enhanced("Emotional injection failed - no API client", "ERROR", "_trigger_emotional_injection")
            
            # Update injection history
            self.injection_history.append(injection_record)
            
            # Keep only last 50 injection records
            if len(self.injection_history) > 50:
                self.injection_history = self.injection_history[-50:]
            
            # Reset activity timer to prevent immediate re-injection
            self.record_user_activity()
            
        except Exception as e:
            log_enhanced(f"Emotional injection trigger failed: {str(e)}", "ERROR", "_trigger_emotional_injection")
    
    async def manual_injection(self, emotion_type=None, custom_message=None):
        """Manually trigger injection for testing"""
        try:
            log_enhanced("Manual injection triggered", "INFO", "manual_injection", {
                "emotion_type": emotion_type,
                "custom_message": bool(custom_message)
            })
            
            if not self.api_client:
                return "FAILED: API client not available"
            
            if not self.emotion_manager:
                return "FAILED: Emotion manager not available"
            
            # Use provided emotion or let emotion manager select
            if emotion_type:
                selected_emotion = emotion_type
            else:
                selected_emotion = self.emotion_manager.select_emotion_type()
            
            # Perform injection
            result = await self.api_client.inject_emotional_message(
                selected_emotion, 
                custom_message=custom_message
            )
            
            # Record manual injection
            injection_record = {
                "timestamp": datetime.now(),
                "emotion_type": selected_emotion,
                "manual": True,
                "custom_message": bool(custom_message),
                "status": "success" if "SUCCESS" in result else "failed",
                "result": result
            }
            
            self.injection_history.append(injection_record)
            
            log_enhanced("Manual injection completed", "SUCCESS", "manual_injection", {
                "emotion": selected_emotion,
                "result": result[:100]
            })
            
            return result
            
        except Exception as e:
            error_msg = f"Manual injection failed: {str(e)}"
            log_enhanced(error_msg, "ERROR", "manual_injection")
            return f"FAILED: {error_msg}"
    
    def get_detection_status(self):
        """Get current detection system status"""
        try:
            current_time = datetime.now()
            idle_duration = current_time - self.last_activity_time
            idle_minutes = idle_duration.total_seconds() / 60
            
            status = {
                "monitoring_active": self.monitoring_active,
                "last_activity": self.last_activity_time.strftime("%Y-%m-%d %H:%M:%S"),
                "idle_minutes": round(idle_minutes, 1),
                "idle_threshold": self.config.get("idle_threshold_minutes", 7),
                "is_idle": self.is_idle(),
                "can_inject": self.can_inject_message(),
                "total_injections": len(self.injection_history),
                "thread_alive": bool(self.detection_thread and self.detection_thread.is_alive())
            }
            
            # Add recent injection info
            if self.injection_history:
                last_injection = self.injection_history[-1]
                status["last_injection"] = {
                    "timestamp": last_injection["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                    "emotion": last_injection["emotion_type"],
                    "status": last_injection["status"]
                }
            
            log_enhanced("Detection status retrieved", "DEBUG", "get_detection_status")
            return status
            
        except Exception as e:
            log_enhanced(f"Failed to get detection status: {str(e)}", "ERROR", "get_detection_status")
            return {"error": str(e), "monitoring_active": False}
    
    def get_injection_history(self, limit=10):
        """Get recent injection history"""
        try:
            recent_history = self.injection_history[-limit:] if self.injection_history else []
            
            formatted_history = []
            for record in recent_history:
                formatted_record = {
                    "timestamp": record["timestamp"].strftime("%H:%M:%S"),
                    "emotion": record["emotion_type"],
                    "status": record["status"],
                    "manual": record.get("manual", False)
                }
                
                if "result" in record:
                    formatted_record["result"] = record["result"][:50] + "..." if len(record["result"]) > 50 else record["result"]
                
                formatted_history.append(formatted_record)
            
            log_enhanced(f"Retrieved injection history", "DEBUG", "get_injection_history", {
                "count": len(formatted_history)
            })
            
            return formatted_history
            
        except Exception as e:
            log_enhanced(f"Failed to get injection history: {str(e)}", "ERROR", "get_injection_history")
            return []