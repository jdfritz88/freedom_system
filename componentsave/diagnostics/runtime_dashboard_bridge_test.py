import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from componentsave.ui_panels.dashboard_status_panel import push_status_message, get_recent_status_log
from componentsave.ui_panels.dashboard_alert_strip import push_alert, get_current_alert
from componentsave.ui_panels.dashboard_emotion_feed import push_emotion_event, get_emotion_feed

print("\n[TEST] Starting Dashboard Bridge Diagnostic\n")

# Trigger each system
push_status_message("System online and ready.")
push_alert("🔔 Diagnostic Alert Triggered")
push_emotion_event("excited", 0.92)

# Check feed contents
print("\n[STATUS LOG]:")
for line in get_recent_status_log():
    print(f" - {line}")

print("\n[ALERT STRIP]:")
print(get_current_alert())

print("\n[EMOTION FEED]:")
for line in get_emotion_feed():
    print(f" - {line}")

print("\n[TEST COMPLETE]\n")
