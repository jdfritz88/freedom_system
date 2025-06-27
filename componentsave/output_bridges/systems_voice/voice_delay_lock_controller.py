import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# voice_delay_lock_controller.py
# Located at: componentsave/output_bridges/systems_voice

import threading
import time
from componentsave.queue import Queue

class VoiceDelayLockController:
    def __init__(self, delay_ms=120):
        self.delay = delay_ms / 1000.0  # convert to seconds
        self.lock = threading.Lock()
        self.queue = Queue()
        self.current_emotion = None
        self.is_speaking = False

    def enqueue_speech(self, emotion_state, text, callback):
        self.queue.put((emotion_state.copy(), text, callback))

    def start_processing(self):
        threading.Thread(target=self._process_queue_wrapper, daemon=True).start()

    def _process_queue_wrapper(self):
        while True:
            self._process_queue()

    def _process_queue(self):
        emotion_state, text, callback = self.queue.get()
        with self.lock:
            self.current_emotion = emotion_state
            self.is_speaking = True
        callback(text, emotion_state)
        # Check more frequently during the lock period
        start_time = time.time()
        while time.time() - start_time < self.delay:
            time.sleep(0.01)
        with self.lock:
            self.is_speaking = False
            self.current_emotion = None

    def get_locked_emotion(self):
        with self.lock:
            return self.current_emotion.copy() if self.current_emotion else None

    def is_locked(self):
        with self.lock:
            return self.is_speaking
