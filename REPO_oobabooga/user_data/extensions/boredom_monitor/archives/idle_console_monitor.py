# ==========================================
# FREEDOM SYSTEM - CONSOLE MONITOR
# Monitors Oobabooga console output for activity detection
# Watches for "Output generated in..." messages
# Signals activity to the main idle monitor
# ==========================================

import threading
import queue
import time
import os
import traceback
from datetime import datetime

class ConsoleMonitor:
    def __init__(self, log_callback=None):
        """Initialize console monitor with logging callback"""
        self.log_callback = log_callback or print
        self.monitoring_active = False
        self.activity_queue = queue.Queue()
        self.console_thread = None
        self.activity_detected_flag = False
        
    def log(self, message, level="INFO"):
        """Log messages using callback"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] [CONSOLE-{level}] {message}"
        self.log_callback(formatted_message)
    
    def start_monitoring(self):
        """Start monitoring Oobabooga console output for activity"""
        try:
            self.log("Starting console monitoring for Oobabooga output...", "STARTUP")
            self.monitoring_active = True
            
            # Start console reader thread
            self.console_thread = threading.Thread(target=self._console_reader_thread, daemon=True)
            self.console_thread.start()
            
            self.log("Console monitoring thread started", "STARTUP")
            return True
            
        except Exception as e:
            self.log(f"Error starting console monitoring: {e}", "ERROR")
            return False
    
    def stop_monitoring(self):
        """Stop console monitoring"""
        self.monitoring_active = False
        self.log("Console monitoring stopped", "SHUTDOWN")
    
    def _console_reader_thread(self):
        """Background thread to read console output and detect activity"""
        try:
            self.log("Console reader thread active - monitoring for 'Output generated' messages", "THREAD")
            
            # Try multiple approaches to capture Oobabooga output
            methods = [
                self._monitor_log_files,
                self._monitor_api_heartbeat
            ]
            
            for method in methods:
                if self._try_console_method(method):
                    break
            else:
                self.log("All console monitoring methods failed - using timer-only mode", "WARNING")
                
        except Exception as e:
            self.log(f"Console reader thread error: {e}", "ERROR")
            self.log(f"Console reader traceback: {traceback.format_exc()}", "ERROR")
    
    def _try_console_method(self, method):
        """Try a specific console monitoring method"""
        try:
            self.log(f"Trying console monitoring method: {method.__name__}", "ATTEMPT")
            return method()
        except Exception as e:
            self.log(f"Console method {method.__name__} failed: {e}", "ATTEMPT")
            return False
    
    def _monitor_log_files(self):
        """Monitor potential Oobabooga log files for activity"""
        try:
            # Common log file locations for text-generation-webui
            potential_log_paths = [
                "logs/console.log",
                "console.log", 
                "text-generation-webui.log",
                "../text-generation-webui/logs/console.log",
                "../text-generation-webui/console.log",
                "../../text-generation-webui/console.log",
                "oobabooga.log"
            ]
            
            for log_path in potential_log_paths:
                if os.path.exists(log_path):
                    self.log(f"Found potential log file: {log_path}", "DISCOVERY")
                    return self._tail_log_file(log_path)
            
            self.log("No Oobabooga log files found", "WARNING")
            return False
            
        except Exception as e:
            self.log(f"Log file monitoring error: {e}", "ERROR")
            return False
    
    def _tail_log_file(self, log_path):
        """Tail a log file and watch for activity patterns"""
        try:
            self.log(f"Monitoring log file: {log_path}", "ACTIVE")
            
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Go to end of file
                f.seek(0, 2)
                
                while self.monitoring_active:
                    line = f.readline()
                    if line:
                        self._process_console_line(line.strip())
                    else:
                        time.sleep(0.5)  # Brief pause if no new lines
                        
            return True
            
        except Exception as e:
            self.log(f"Error tailing log file {log_path}: {e}", "ERROR")
            return False
    
    def _monitor_api_heartbeat(self):
        """Use API calls as a heartbeat to detect activity patterns"""
        try:
            self.log("Starting API heartbeat monitoring (fallback method)", "FALLBACK")
            
            last_check_time = 0
            
            while self.monitoring_active:
                try:
                    current_time = time.time()
                    
                    # Simple time-based activity detection
                    # This is a placeholder for more sophisticated API monitoring
                    if current_time - last_check_time > 60:  # Check every minute
                        self.log("API heartbeat check", "HEARTBEAT")
                        last_check_time = current_time
                    
                    time.sleep(10)  # Check every 10 seconds
                    
                except Exception as e:
                    self.log(f"API heartbeat error: {e}", "ERROR")
                    time.sleep(30)  # Longer pause on error
            
            return True
            
        except Exception as e:
            self.log(f"API heartbeat monitoring error: {e}", "ERROR")
            return False
    
    def _process_console_line(self, line):
        """Process a line from console output to detect activity"""
        try:
            # Look for the key phrases that indicate generation completion
            activity_patterns = [
                "Output generated in",
                "eval time =",
                "total time =",
                "tokens/s"
            ]
            
            line_lower = line.lower()
            for pattern in activity_patterns:
                if pattern.lower() in line_lower:
                    self.log(f"Activity detected in console: {line[:100]}", "ACTIVITY")
                    self._signal_activity_detected(f"Console pattern: {pattern}")
                    return
                    
        except Exception as e:
            self.log(f"Error processing console line: {e}", "ERROR")
    
    def _signal_activity_detected(self, source):
        """Signal that activity has been detected"""
        try:
            self.activity_detected_flag = True
            self.activity_queue.put(("activity", source, time.time()))
            self.log(f"Activity signal from {source}", "SIGNAL")
        except Exception as e:
            self.log(f"Error signaling activity: {e}", "ERROR")
    
    def check_for_activity(self):
        """Check if any console activity has been detected"""
        try:
            activity_found = False
            
            # Process any queued activity signals
            while not self.activity_queue.empty():
                try:
                    signal_type, source, timestamp = self.activity_queue.get_nowait()
                    if signal_type == "activity":
                        self.log(f"Console activity processed from: {source}", "PROCESSED")
                        activity_found = True
                except queue.Empty:
                    break
            
            # Check the activity flag
            if self.activity_detected_flag:
                self.activity_detected_flag = False
                activity_found = True
            
            return activity_found
            
        except Exception as e:
            self.log(f"Console monitoring check error: {e}", "ERROR")
            return False
    
    def is_monitoring_active(self):
        """Check if console monitoring is currently active"""
        return self.monitoring_active

# Helper function for easy import
def get_console_monitor(log_callback=None):
    """Factory function to create console monitor"""
    return ConsoleMonitor(log_callback)

# Test function if run directly
if __name__ == "__main__":
    print("Testing Console Monitor...")
    
    def test_log(message):
        print(f"TEST: {message}")
    
    monitor = get_console_monitor(test_log)
    
    if monitor.start_monitoring():
        print("\nConsole monitoring started successfully")
        print("Monitoring for 30 seconds...")
        
        # Monitor for 30 seconds
        for i in range(30):
            time.sleep(1)
            if monitor.check_for_activity():
                print(f"Activity detected at second {i+1}")
        
        monitor.stop_monitoring()
        print("Console monitoring test completed")
    else:
        print("Failed to start console monitoring")