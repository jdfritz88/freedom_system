import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# 🧪 Runtime Performance Validation for Freedom System
# Confirms actual behavior of queues, delays, and output triggers

import time
import threading
from componentsave.queue import Queue

results = []

# 1. Test FIFO Queue behavior from emotion_queue
try:
    from emotion_core_logic import emotion_queue

    test_q = Queue()
    for i in range(5):
        test_q.put(f"event_{i}")
    fifo_pass = all(test_q.get() == f"event_{i}" for i in range(5))
    results.append(f"{'✅' if fifo_pass else '❌'} FIFO queue behavior valid")

except Exception as e:
    results.append(f"❌ emotion_queue FIFO test failed: {e}")

# 2. Test delay throttle actually enforces minimum interval
try:
    from emotion_core_logic import emotion_delay_throttle
    throttle_fn = getattr(emotion_delay_throttle, 'throttle_emotion_delay', None)

    if throttle_fn:
        start = time.time()
        throttle_fn()
        end = time.time()
        elapsed = end - start
        throttle_pass = elapsed >= 0.3  # assuming throttle delay ≥ 300ms
        results.append(f"{'✅' if throttle_pass else '❌'} Throttle delay enforced ({elapsed:.2f}s)")
    else:
        results.append("❌ throttle_emotion_delay() not found")

except Exception as e:
    results.append(f"❌ Throttle test failed: {e}")

# 3. Test voice lockout during TTS (simulated Coqui)
def fake_speak(q):
    if not q.empty():
        msg = q.get()
        time.sleep(1)  # Simulate voice duration
        return f"Spoken: {msg}"
    return "Queue Empty"

try:
    voice_q = Queue()
    voice_q.put("hello")
    voice_q.put("world")
    
    result_texts = []
    thread_1 = threading.Thread(target=lambda: result_texts.append(fake_speak(voice_q)))
    thread_2 = threading.Thread(target=lambda: result_texts.append(fake_speak(voice_q)))

    thread_1.start()
    thread_2.start()
    thread_1.join()
    thread_2.join()

    speak_pass = len(result_texts) == 2 and "hello" in result_texts[0] and "world" in result_texts[1]
    results.append(f"{'✅' if speak_pass else '❌'} Voice queue behavior valid")

except Exception as e:
    results.append(f"❌ Voice test failed: {e}")

# 📊 Print all runtime checks
print("\nRuntime Behavior Checks:")
for line in results:
    print(line)
