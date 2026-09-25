# ==========================================
# FREEDOM SYSTEM INSTALLER - ENFORCED MODE
# Follows Freedom_Installer_Coding_Standards.txt
# ==========================================

import os
import json
import time
import threading
import requests
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class FreedomBoredomSystem:
    def __init__(self, extension_path: str):
        self.extension_path = extension_path
        self.config_path = os.path.join(extension_path, 'idle_response_config.json')
        self.tracker_path = os.path.join(extension_path, 'idle_cooldown_tracker.json')
        self.templates_path = os.path.join(extension_path, 'idle_meta_prompt_templates.json')
        self.endpoint_config_path = os.path.join(extension_path, 'idle_endpoint_config.json')
        self.log_path = os.path.join(extension_path, '..', '..', 'log')
        
        # Initialize components
        self.load_configurations()
        self.running = False
        self.monitor_thread = None
        self.last_activity_time = time.time()
        
        # Bridge system
        self.bridge_active = False
        self.gradio_endpoint = None
        self.local_oobabooga_url = "http://localhost:5000"
        
        print("INFO: Freedom Boredom System initialized")

    def load_configurations(self):
        """Load all configuration files"""
        try:
            # Load response config
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.response_config = json.load(f)
            else:
                self.response_config = self.get_default_response_config()
                self.save_response_config()
            
            # Load tracker
            if os.path.exists(self.tracker_path):
                with open(self.tracker_path, 'r', encoding='utf-8') as f:
                    self.tracker_data = json.load(f)
            else:
                self.tracker_data = self.get_default_tracker()
                self.save_tracker()
            
            # Load templates
            if os.path.exists(self.templates_path):
                with open(self.templates_path, 'r', encoding='utf-8') as f:
                    self.templates = json.load(f)
            else:
                self.templates = self.get_default_templates()
                self.save_templates()
            
            # Load endpoint config
            if os.path.exists(self.endpoint_config_path):
                with open(self.endpoint_config_path, 'r', encoding='utf-8') as f:
                    self.endpoint_config = json.load(f)
            else:
                self.endpoint_config = self.get_default_endpoint_config()
                self.save_endpoint_config()
                
        except Exception as e:
            print("ERROR: Failed to load configurations - " + str(e))
            self.log_event("CONFIG_LOAD_ERROR", str(e))

    def get_default_response_config(self) -> Dict:
        """Get default response configuration"""
        return {
            "enabled": True,
            "idle_threshold_minutes": 3,
            "cooldown_minutes": 10,
            "max_responses_per_hour": 6
        }

    def get_default_tracker(self) -> Dict:
        """Get default tracker data"""
        return {
            "last_idle_response": 0,
            "responses_this_hour": 0,
            "hour_reset_time": time.time()
        }

    def get_default_templates(self) -> Dict:
        """Get default meta prompt templates"""
        return {
            "templates": [
                "Freedom notices the user seems quiet and wonders what they're thinking about",
                "Freedom feels a gentle curiosity about what the user is up to",
                "Freedom has been thinking and wants to share a thought with the user",
                "Freedom senses the peaceful quiet and wants to connect gently"
            ]
        }

    def get_default_endpoint_config(self) -> Dict:
        """Get default endpoint configuration"""
        return {
            "gradio_bridge_enabled": False,
            "gradio_endpoint": "http://localhost:7860",
            "dual_injection_mode": True,
            "oobabooga_endpoint": "http://localhost:5000",
            "bridge_timeout": 30,
            "retry_attempts": 3
        }

    def save_response_config(self):
        """Save response configuration"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.response_config, f, indent=2)
        except Exception as e:
            print("ERROR: Failed to save response config - " + str(e))

    def save_tracker(self):
        """Save tracker data"""
        try:
            with open(self.tracker_path, 'w', encoding='utf-8') as f:
                json.dump(self.tracker_data, f, indent=2)
        except Exception as e:
            print("ERROR: Failed to save tracker - " + str(e))

    def save_templates(self):
        """Save templates"""
        try:
            with open(self.templates_path, 'w', encoding='utf-8') as f:
                json.dump(self.templates, f, indent=2)
        except Exception as e:
            print("ERROR: Failed to save templates - " + str(e))

    def save_endpoint_config(self):
        """Save endpoint configuration"""
        try:
            with open(self.endpoint_config_path, 'w', encoding='utf-8') as f:
                json.dump(self.endpoint_config, f, indent=2)
        except Exception as e:
            print("ERROR: Failed to save endpoint config - " + str(e))

    def log_event(self, event_type: str, message: str):
        """Log events to the boredom monitor log"""
        try:
            os.makedirs(self.log_path, exist_ok=True)
            log_file = os.path.join(self.log_path, 'boredom_monitor.log')
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_entry = timestamp + " [" + event_type + "] " + message + "\n"
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
                
        except Exception as e:
            print("ERROR: Failed to log event - " + str(e))

    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity_time = time.time()
        self.log_event("ACTIVITY", "User activity detected")

    def is_idle_threshold_met(self) -> bool:
        """Check if idle threshold has been met"""
        if not self.response_config.get("enabled", False):
            return False
            
        idle_seconds = time.time() - self.last_activity_time
        threshold_seconds = self.response_config.get("idle_threshold_minutes", 3) * 60
        
        return idle_seconds >= threshold_seconds

    def is_cooldown_active(self) -> bool:
        """Check if cooldown period is active"""
        last_response = self.tracker_data.get("last_idle_response", 0)
        cooldown_seconds = self.response_config.get("cooldown_minutes", 10) * 60
        
        return (time.time() - last_response) < cooldown_seconds

    def is_hourly_limit_reached(self) -> bool:
        """Check if hourly response limit is reached"""
        current_time = time.time()
        hour_reset = self.tracker_data.get("hour_reset_time", 0)
        
        # Reset hour counter if needed
        if current_time - hour_reset >= 3600:
            self.tracker_data["responses_this_hour"] = 0
            self.tracker_data["hour_reset_time"] = current_time
            self.save_tracker()
        
        max_responses = self.response_config.get("max_responses_per_hour", 6)
        current_responses = self.tracker_data.get("responses_this_hour", 0)
        
        return current_responses >= max_responses

    def can_trigger_idle_response(self) -> bool:
        """Check if all conditions are met for idle response"""
        return (self.is_idle_threshold_met() and 
                not self.is_cooldown_active() and 
                not self.is_hourly_limit_reached())

    def get_random_template(self) -> str:
        """Get a random meta prompt template"""
        templates = self.templates.get("templates", [])
        if not templates:
            return "Freedom notices the quiet moment and feels curious"
        
        return random.choice(templates)

    def inject_to_oobabooga(self, message: str) -> bool:
        """Inject message directly to Oobabooga"""
        try:
            endpoint = self.endpoint_config.get("oobabooga_endpoint", self.local_oobabooga_url)
            
            payload = {
                "text": message,
                "meta_prompt": True,
                "source": "freedom_boredom_system"
            }
            
            response = requests.post(
                endpoint + "/api/v1/generate",
                json=payload,
                timeout=self.endpoint_config.get("bridge_timeout", 30)
            )
            
            if response.status_code == 200:
                self.log_event("OOBABOOGA_INJECT", "Message injected successfully")
                return True
            else:
                self.log_event("OOBABOOGA_ERROR", "Injection failed with status " + str(response.status_code))
                return False
                
        except Exception as e:
            self.log_event("OOBABOOGA_ERROR", "Injection failed - " + str(e))
            return False

    def inject_to_gradio_bridge(self, message: str) -> bool:
        """Inject message to Gradio bridge if enabled"""
        try:
            if not self.endpoint_config.get("gradio_bridge_enabled", False):
                return False
                
            endpoint = self.endpoint_config.get("gradio_endpoint", "http://localhost:7860")
            
            payload = {
                "message": message,
                "source": "freedom_boredom",
                "meta_prompt": True
            }
            
            response = requests.post(
                endpoint + "/api/freedom/inject",
                json=payload,
                timeout=self.endpoint_config.get("bridge_timeout", 30)
            )
            
            if response.status_code == 200:
                self.log_event("GRADIO_INJECT", "Message injected to bridge successfully")
                return True
            else:
                self.log_event("GRADIO_ERROR", "Bridge injection failed with status " + str(response.status_code))
                return False
                
        except Exception as e:
            self.log_event("GRADIO_ERROR", "Bridge injection failed - " + str(e))
            return False

    def trigger_idle_response(self):
        """Trigger idle response with dual injection"""
        try:
            # Get random template
            template = self.get_random_template()
            
            # Update tracker
            self.tracker_data["last_idle_response"] = time.time()
            self.tracker_data["responses_this_hour"] += 1
            self.save_tracker()
            
            self.log_event("IDLE_TRIGGER", "Triggering idle response: " + template)
            
            # Dual injection mode
            if self.endpoint_config.get("dual_injection_mode", True):
                # Try both endpoints
                oobabooga_success = self.inject_to_oobabooga(template)
                gradio_success = self.inject_to_gradio_bridge(template)
                
                if oobabooga_success or gradio_success:
                    self.log_event("DUAL_INJECT", "SUCCESS - At least one injection succeeded")
                else:
                    self.log_event("DUAL_INJECT", "FAIL - Both injections failed")
            else:
                # Single injection to Oobabooga only
                success = self.inject_to_oobabooga(template)
                if success:
                    self.log_event("SINGLE_INJECT", "SUCCESS - Oobabooga injection succeeded")
                else:
                    self.log_event("SINGLE_INJECT", "FAIL - Oobabooga injection failed")
            
        except Exception as e:
            self.log_event("TRIGGER_ERROR", "Failed to trigger idle response - " + str(e))

    def monitor_loop(self):
        """Main monitoring loop"""
        self.log_event("MONITOR", "Boredom monitor started")
        
        while self.running:
            try:
                if self.can_trigger_idle_response():
                    self.trigger_idle_response()
                
                # Sleep for 30 seconds between checks
                time.sleep(30)
                
            except Exception as e:
                self.log_event("MONITOR_ERROR", "Monitor loop error - " + str(e))
                time.sleep(60)  # Wait longer on error
        
        self.log_event("MONITOR", "Boredom monitor stopped")

    def start_monitoring(self):
        """Start the boredom monitoring system"""
        if not self.running:
            self.running = True
            self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
            self.monitor_thread.start()
            print("INFO: Freedom Boredom System monitoring started")

    def stop_monitoring(self):
        """Stop the boredom monitoring system"""
        if self.running:
            self.running = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)
            print("INFO: Freedom Boredom System monitoring stopped")

    def get_status(self) -> Dict:
        """Get current system status"""
        return {
            "running": self.running,
            "enabled": self.response_config.get("enabled", False),
            "last_activity": self.last_activity_time,
            "idle_seconds": time.time() - self.last_activity_time,
            "cooldown_active": self.is_cooldown_active(),
            "hourly_limit_reached": self.is_hourly_limit_reached(),
            "can_trigger": self.can_trigger_idle_response(),
            "responses_this_hour": self.tracker_data.get("responses_this_hour", 0),
            "bridge_enabled": self.endpoint_config.get("gradio_bridge_enabled", False),
            "dual_injection": self.endpoint_config.get("dual_injection_mode", True)
        }

    def update_config(self, new_config: Dict):
        """Update response configuration"""
        try:
            self.response_config.update(new_config)
            self.save_response_config()
            self.log_event("CONFIG_UPDATE", "Configuration updated")
            print("INFO: Boredom system configuration updated")
        except Exception as e:
            self.log_event("CONFIG_ERROR", "Failed to update config - " + str(e))

    def add_template(self, template: str):
        """Add new meta prompt template"""
        try:
            if "templates" not in self.templates:
                self.templates["templates"] = []
            
            self.templates["templates"].append(template)
            self.save_templates()
            self.log_event("TEMPLATE_ADD", "New template added: " + template)
            print("INFO: New template added to boredom system")
        except Exception as e:
            self.log_event("TEMPLATE_ERROR", "Failed to add template - " + str(e))

    def remove_template(self, template: str):
        """Remove meta prompt template"""
        try:
            if "templates" in self.templates and template in self.templates["templates"]:
                self.templates["templates"].remove(template)
                self.save_templates()
                self.log_event("TEMPLATE_REMOVE", "Template removed: " + template)
                print("INFO: Template removed from boredom system")
        except Exception as e:
            self.log_event("TEMPLATE_ERROR", "Failed to remove template - " + str(e))

    def reset_tracker(self):
        """Reset activity tracker"""
        try:
            self.tracker_data = self.get_default_tracker()
            self.save_tracker()
            self.log_event("TRACKER_RESET", "Activity tracker reset")
            print("INFO: Boredom system tracker reset")
        except Exception as e:
            self.log_event("TRACKER_ERROR", "Failed to reset tracker - " + str(e))

    def test_endpoints(self) -> Dict:
        """Test all configured endpoints"""
        results = {}
        
        # Test Oobabooga endpoint
        try:
            endpoint = self.endpoint_config.get("oobabooga_endpoint", self.local_oobabooga_url)
            response = requests.get(endpoint + "/api/v1/model", timeout=10)
            results["oobabooga"] = {"status": "online" if response.status_code == 200 else "error", "code": response.status_code}
        except Exception as e:
            results["oobabooga"] = {"status": "offline", "error": str(e)}
        
        # Test Gradio bridge endpoint if enabled
        if self.endpoint_config.get("gradio_bridge_enabled", False):
            try:
                endpoint = self.endpoint_config.get("gradio_endpoint", "http://localhost:7860")
                response = requests.get(endpoint + "/api/freedom/status", timeout=10)
                results["gradio_bridge"] = {"status": "online" if response.status_code == 200 else "error", "code": response.status_code}
            except Exception as e:
                results["gradio_bridge"] = {"status": "offline", "error": str(e)}
        else:
            results["gradio_bridge"] = {"status": "disabled"}
        
        self.log_event("ENDPOINT_TEST", "Endpoint test completed: " + str(results))
        return results