# ==========================================
# FREEDOM SYSTEM - IDLE BOREDOM DETECTOR
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
import json
import time
import threading
from datetime import datetime, timedelta

class IdleBoredomDetector:
    """
    Monitors user activity and triggers boredom injections for the Freedom System
    Tracks idle time and coordinates with emotion and injection managers
    
    Follows Standards:
    - #1: Folder Isolation - Lives in boredom_monitor extension folder
    - #2: Environment Usage - Uses shared _env folder
    - #9: Script Loader Override - Overrides Python paths for _env
    - #11: Log Placement - Logs to root log folder
    - #12: Log Format - Includes timestamps, component names, status indicators
    """
    
    def __init__(self, config_path=None):
        self.component_name = "BOREDOM-DETECTOR"
        
        # Standard #11: Log Placement - Use root log folder
        self.log_file = Path("F:/Apps/freedom_system/log/boredom_monitor.log")
        
        # Configuration - Fixed to use extension directory
        extension_dir = Path(__file__).parent
        self.config_path = config_path or (extension_dir / "idle_response_config.json")
        self.config = self._load_config()
        
        # Activity tracking
        self.last_user_activity = time.time()
        self.idle_threshold_minutes = self.config.get("idle_minutes", 7)
        self.is_monitoring = False
        self.monitor_thread = None
        
        # Integration with other managers
        self.emotion_manager = None
        self.injection_manager = None
        
        # Statistics
        self.total_idle_periods = 0
        self.total_injections_triggered = 0
        self.last_injection_time = 0
        
        # Monitoring control
        self.monitor_interval_seconds = self.config.get("monitor_interval_seconds", 30)
        self.shutdown_event = threading.Event()
        
        self.initialization_success = False
        
        try:
            self._initialize_managers()
            self.initialization_success = True
            self.log("IdleBoredomDetector initialized successfully", "[OK]")
            
        except Exception as e:
            self.log("IdleBoredomDetector initialization failed: " + str(e), "[FAIL]")
    
    def log(self, message, status="[INFO]"):
        """
        Standard #12: Log Format - Include timestamp, component name, action result
        Logs to both console and root log folder
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = "[" + timestamp + "] [" + self.component_name + "] " + status + " " + str(message)
        
        # Console output
        print(log_entry)
        
        # File logging to root log folder
        try:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")
        except Exception as e:
            print("[" + timestamp + "] [" + self.component_name + "] [ERROR] Failed to write log: " + str(e))
    
    def _load_config(self):
        """Load boredom detection configuration from JSON file"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.log("Boredom detector configuration loaded from " + str(config_file), "[OK]")
                return config
            else:
                # Default configuration
                default_config = {
                    "idle_minutes": 7,
                    "monitor_interval_seconds": 30,
                    "enable_logging": True,
                    "auto_start_monitoring": True
                }
                self.log("Using default boredom detector configuration", "[INFO]")
                return default_config
                
        except Exception as e:
            self.log("Failed to load boredom detector config: " + str(e), "[ERROR]")
            return {}
    
    def _initialize_managers(self):
        """Initialize connections to emotion and injection managers"""
        try:
            # Initialize emotion manager
            try:
                from .idle_emotion_manager import create_emotion_manager
                self.emotion_manager = create_emotion_manager()
                if self.emotion_manager:
                    self.log("Emotion manager connected successfully", "[OK]")
                else:
                    self.log("Emotion manager creation failed", "[ERROR]")
            except ImportError:
                try:
                    from idle_emotion_manager import create_emotion_manager
                    self.emotion_manager = create_emotion_manager()
                    if self.emotion_manager:
                        self.log("Emotion manager connected successfully (fallback import)", "[OK]")
                    else:
                        self.log("Emotion manager creation failed (fallback)", "[ERROR]")
                except ImportError:
                    self.log("Emotion manager not available", "[WARNING]")
                    self.emotion_manager = None
            
            # Initialize injection manager
            try:
                from .idle_injection_manager import create_injection_manager
                self.injection_manager = create_injection_manager()
                if self.injection_manager:
                    self.log("Injection manager connected successfully", "[OK]")
                else:
                    self.log("Injection manager creation failed", "[ERROR]")
            except ImportError:
                try:
                    from idle_injection_manager import create_injection_manager
                    self.injection_manager = create_injection_manager()
                    if self.injection_manager:
                        self.log("Injection manager connected successfully (fallback import)", "[OK]")
                    else:
                        self.log("Injection manager creation failed (fallback)", "[ERROR]")
                except ImportError:
                    self.log("Injection manager not available", "[WARNING]")
                    self.injection_manager = None
            
            # Auto-start monitoring if configured
            if self.config.get("auto_start_monitoring", True):
                self.start_monitoring()
                
        except Exception as e:
            self.log("Manager initialization failed: " + str(e), "[ERROR]")
            raise
    
    def record_user_activity(self, activity_type="general"):
        """
        Record user activity to reset idle timer
        Should be called from script.py when user interactions are detected
        """
        try:
            self.last_user_activity = time.time()
            self.log("User activity recorded: " + activity_type, "[INFO]")
            
        except Exception as e:
            self.log("Failed to record user activity: " + str(e), "[ERROR]")
    
    def get_idle_time_minutes(self):
        """Get current idle time in minutes"""
        try:
            current_time = time.time()
            idle_seconds = current_time - self.last_user_activity
            idle_minutes = idle_seconds / 60.0
            return idle_minutes
            
        except Exception as e:
            self.log("Failed to calculate idle time: " + str(e), "[ERROR]")
            return 0.0
    
    def is_user_idle(self):
        """Check if user has been idle long enough to trigger boredom"""
        try:
            idle_minutes = self.get_idle_time_minutes()
            is_idle = idle_minutes >= self.idle_threshold_minutes
            
            if is_idle:
                self.log("User is idle: " + str(round(idle_minutes, 1)) + " minutes (threshold: " + 
                        str(self.idle_threshold_minutes) + ")", "[INFO]")
            
            return is_idle
            
        except Exception as e:
            self.log("Idle check failed: " + str(e), "[ERROR]")
            return False
    
    def start_monitoring(self):
        """Start the background monitoring thread"""
        try:
            if self.is_monitoring:
                self.log("Monitoring already active", "[WARNING]")
                return True
            
            if not self.emotion_manager or not self.injection_manager:
                self.log("Cannot start monitoring - managers not available", "[ERROR]")
                return False
            
            self.is_monitoring = True
            self.shutdown_event.clear()
            self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitor_thread.start()
            
            self.log("Boredom monitoring started (interval: " + str(self.monitor_interval_seconds) + "s)", "[OK]")
            return True
            
        except Exception as e:
            self.log("Failed to start monitoring: " + str(e), "[FAIL]")
            return False
    
    def stop_monitoring(self):
        """Stop the background monitoring thread"""
        try:
            if not self.is_monitoring:
                self.log("Monitoring not active", "[INFO]")
                return True
            
            self.is_monitoring = False
            self.shutdown_event.set()
            
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)
            
            self.log("Boredom monitoring stopped", "[OK]")
            return True
            
        except Exception as e:
            self.log("Failed to stop monitoring: " + str(e), "[ERROR]")
            return False
    
    def _monitoring_loop(self):
        """Main monitoring loop that runs in background thread"""
        self.log("Monitoring loop started", "[INFO]")
        
        try:
            while self.is_monitoring and not self.shutdown_event.is_set():
                try:
                    # Check if user is idle
                    if self.is_user_idle():
                        self._handle_idle_period()
                    
                    # Wait for next check or shutdown signal
                    if self.shutdown_event.wait(timeout=self.monitor_interval_seconds):
                        break  # Shutdown requested
                        
                except Exception as e:
                    self.log("Monitoring loop iteration failed: " + str(e), "[ERROR]")
                    time.sleep(5)  # Longer delay on error
            
        except Exception as e:
            self.log("Monitoring loop crashed: " + str(e), "[FAIL]")
        
        finally:
            self.is_monitoring = False
            self.log("Monitoring loop stopped", "[INFO]")
    
    def _handle_idle_period(self):
        """Handle detected idle period by triggering boredom injection"""
        try:
            self.total_idle_periods += 1
            current_time = time.time()
            
            # Check if enough time has passed since last injection
            min_injection_interval = self.config.get("min_injection_interval_minutes", 5) * 60
            
            if current_time - self.last_injection_time < min_injection_interval:
                remaining = (min_injection_interval - (current_time - self.last_injection_time)) / 60
                self.log("Idle detected but injection on cooldown for " + str(round(remaining, 1)) + " more minutes", "[INFO]")
                return
            
            self.log("Handling idle period #" + str(self.total_idle_periods), "[INFO]")
            
            # Generate emotional message
            if not self.emotion_manager:
                self.log("Cannot generate message - emotion manager not available", "[ERROR]")
                return
            
            emotional_message = self.emotion_manager.generate_emotional_message()
            if not emotional_message:
                self.log("Failed to generate emotional message", "[ERROR]")
                return
            
            self.log("Generated emotional message: " + emotional_message[:50] + "...", "[OK]")
            
            # Inject the message
            if not self.injection_manager:
                self.log("Cannot inject message - injection manager not available", "[ERROR]")
                return
            
            injection_result = self.injection_manager.inject_freedom_message(emotional_message)
            
            if injection_result.get('success', False):
                self.total_injections_triggered += 1
                self.last_injection_time = current_time
                
                # Reset activity timer to prevent immediate re-trigger
                self.last_user_activity = current_time
                
                method = injection_result.get('method', 'unknown')
                self.log("Boredom injection successful via " + method + " (total: " + str(self.total_injections_triggered) + ")", "[OK]")
            else:
                reason = injection_result.get('reason', 'unknown')
                self.log("Boredom injection failed: " + reason, "[ERROR]")
            
        except Exception as e:
            self.log("Idle period handling failed: " + str(e), "[FAIL]")
    
    def force_boredom_trigger(self):
        """Manually trigger a boredom injection for testing"""
        try:
            self.log("Forcing boredom trigger for testing", "[INFO]")
            self._handle_idle_period()
            return True
            
        except Exception as e:
            self.log("Force trigger failed: " + str(e), "[ERROR]")
            return False
    
    def get_detector_status(self):
        """Get current boredom detector status"""
        try:
            idle_minutes = self.get_idle_time_minutes()
            is_idle = self.is_user_idle()
            
            status = {
                "initialization_success": self.initialization_success,
                "is_monitoring": self.is_monitoring,
                "idle_threshold_minutes": self.idle_threshold_minutes,
                "current_idle_minutes": round(idle_minutes, 1),
                "is_user_idle": is_idle,
                "total_idle_periods": self.total_idle_periods,
                "total_injections_triggered": self.total_injections_triggered,
                "last_injection_time": self.last_injection_time,
                "last_user_activity": self.last_user_activity,
                "emotion_manager_available": self.emotion_manager is not None,
                "injection_manager_available": self.injection_manager is not None,
                "monitor_interval_seconds": self.monitor_interval_seconds
            }
            
            # Add time until next potential injection
            if self.last_injection_time > 0:
                min_interval = self.config.get("min_injection_interval_minutes", 5) * 60
                time_diff = time.time() - self.last_injection_time
                if time_diff < min_interval:
                    status["injection_cooldown_remaining_minutes"] = round((min_interval - time_diff) / 60, 1)
                else:
                    status["injection_cooldown_remaining_minutes"] = 0
            else:
                status["injection_cooldown_remaining_minutes"] = 0
            
            self.log("Detector status retrieved successfully", "[OK]")
            return status
            
        except Exception as e:
            self.log("Failed to get detector status: " + str(e), "[ERROR]")
            return {
                "initialization_success": False,
                "error": str(e)
            }
    
    def update_idle_threshold(self, minutes):
        """Update the idle threshold for testing"""
        try:
            old_threshold = self.idle_threshold_minutes
            self.idle_threshold_minutes = max(1, minutes)  # Minimum 1 minute
            
            self.log("Idle threshold updated from " + str(old_threshold) + " to " + str(self.idle_threshold_minutes) + " minutes", "[OK]")
            return True
            
        except Exception as e:
            self.log("Failed to update idle threshold: " + str(e), "[ERROR]")
            return False
    
    def reset_activity_timer(self):
        """Reset the activity timer to current time"""
        try:
            self.last_user_activity = time.time()
            self.log("Activity timer reset to current time", "[OK]")
            return True
            
        except Exception as e:
            self.log("Failed to reset activity timer: " + str(e), "[ERROR]")
            return False


# Factory function for easy usage
def create_boredom_detector():
    """Create and return a configured boredom detector"""
    try:
        detector = IdleBoredomDetector()
        if detector.initialization_success:
            print("[BOREDOM-DETECTOR] [OK] Factory function completed successfully")
            return detector
        else:
            print("[BOREDOM-DETECTOR] [FAIL] Factory function failed during initialization")
            return None
            
    except Exception as e:
        print("[BOREDOM-DETECTOR] [FAIL] Factory function exception: " + str(e))
        return None


# Testing functions for diagnostics
def test_boredom_detection():
    """Test boredom detection functionality"""
    print("=== BOREDOM DETECTOR TEST ===")
    
    detector = create_boredom_detector()
    if not detector:
        print("[FAIL] Could not create boredom detector")
        return False
    
    try:
        # Show initial status
        status = detector.get_detector_status()
        print("Initial status:", status)
        
        # Test activity recording
        print("Recording user activity...")
        detector.record_user_activity("test_activity")
        
        # Test idle check
        print("Checking idle status...")
        is_idle = detector.is_user_idle()
        idle_time = detector.get_idle_time_minutes()
        print("Is idle:", is_idle, "Idle time:", round(idle_time, 1), "minutes")
        
        # Test forced trigger
        print("Testing forced boredom trigger...")
        trigger_result = detector.force_boredom_trigger()
        print("Force trigger result:", trigger_result)
        
        # Show final status
        final_status = detector.get_detector_status()
        print("Final status:", final_status)
        
        print("[OK] Boredom detection test completed")
        return True
        
    except Exception as e:
        print("[FAIL] Boredom detection test failed: " + str(e))
        return False
    
    finally:
        # Clean up
        detector.stop_monitoring()


# Main execution for testing
if __name__ == "__main__":
    print("=== IDLE BOREDOM DETECTOR DIAGNOSTICS ===")
    
    # Run initialization test
    detector = create_boredom_detector()
    if detector:
        print("[OK] Initialization successful")
        
        # Run tests
        test_boredom_detection()
        
        print("[DONE] All diagnostics completed")
    else:
        print("[FAIL] Initialization failed")
        print("[FAIL] Diagnostics could not run")