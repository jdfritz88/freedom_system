import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import time

# Fallback local imports (replace with actual module imports if present)
class EmotionDecay:
    def __init__(self):
        self.intensities = {}
        self.timestamps = {}

    def trigger_emotion(self, emotion, intensity):
        self.intensities[emotion] = intensity
        self.timestamps[emotion] = time.time()

    def get_emotion_levels(self):
        now = time.time()
        result = {}
        for emotion, value in self.intensities.items():
            elapsed = now - self.timestamps.get(emotion, now)
            remaining = max(0.0, value * (1 - elapsed / 30.0))
            if remaining > 0:
                result[emotion] = round(remaining, 3)
        return result

def blend_emotions(raw_scores):
    sorted_emotions = sorted(raw_scores.items(), key=lambda x: x[1], reverse=True)
    if not sorted_emotions:
        return ("Calm (Calm (Neutral))", "Calm (Calm (Neutral))")
    elif len(sorted_emotions) == 1:
        return (sorted_emotions[0][0], "Calm (Calm (Neutral))")
    else:
        return (sorted_emotions[0][0], sorted_emotions[1][0])

class EmotionSystemStatus:
    def __init__(self):
        self.decay = EmotionDecay()
        self.blend = ("Calm (Calm (Neutral))", "Calm (Calm (Neutral))")

    def trigger_emotion(self, emotion: str, intensity: float):
        self.decay.trigger_emotion(emotion, intensity)

    def update(self):
        current_levels = self.decay.get_emotion_levels()
        self.blend = blend_emotions(current_levels)
        return self.blend

    def get_status(self):
        return {
            "active_emotions": self.decay.get_emotion_levels(),
            "dominant_blend": self.blend
        }

class EmotionThresholdControl:
    def __init__(self, default_threshold: float = 0.7):
        self.threshold = default_threshold

    def set_threshold(self, new_value: float):
        if 0.0 <= new_value <= 1.0:
            self.threshold = new_value
            print(f"[THRESHOLD UPDATED] Set to: {self.threshold:.2f}")

class EmotionBroadcastHub:
    def __init__(self):
        self.subscribers = []

    def subscribe(self, name: str, callback):
        self.subscribers.append((name, callback))

    def broadcast(self, dominant_emotions):
        for name, callback in self.subscribers:
            try:
                callback(dominant_emotions)
            except Exception as e:
                print(f"[Broadcast Error] {name} failed: {e}")

class EmotionTriggerHandler:
    def __init__(self):
        self.last_interaction_time = time.time()
        self.last_image_time = 0
        self.threshold = 0.7

    def check_and_trigger(self, emotion_scores, trigger_image):
        now = time.time()
        for emotion, score in emotion_scores.items():
            if score >= self.threshold:
                trigger_image(emotion)
                self.last_image_time = now
                self.last_interaction_time = now
                return
        if now - self.last_interaction_time >= 300:
            trigger_image("BOREDOM_SYSTEM_TRIGGER")
            self.last_image_time = now
            self.last_interaction_time = now

# Minimal prompt generator fallback
def build_prompt(emotion: str) -> str:
    return f"Freedom, cinematic, emotion: {emotion}"

class EmotionRuntime:
    def __init__(self):
        self.status = EmotionSystemStatus()
        self.threshold_control = EmotionThresholdControl()
        self.broadcast_hub = EmotionBroadcastHub()
        self.trigger_handler = EmotionTriggerHandler()

    def trigger_emotion(self, emotion: str, intensity: float):
        self.status.trigger_emotion(emotion, intensity)

    def update_cycle(self):
        blend = self.status.update()
        self.broadcast_hub.broadcast(blend)
        emotion_levels = self.status.get_status()["active_emotions"]
        self.trigger_handler.check_and_trigger(emotion_levels, self.handle_image_generation)

    def handle_image_generation(self, trigger_source: str):
        prompt = build_prompt(trigger_source)
        print(f"[IMAGE] Triggered by: {trigger_source}\n{prompt}\n")

    def set_threshold(self, value: float):
        self.threshold_control.set_threshold(value)

    def attach_receiver(self, name: str, callback):
        self.broadcast_hub.subscribe(name, callback)

# Example debug usage
if __name__ == "__main__":
    runtime = EmotionRuntime()
    runtime.attach_receiver("voice", lambda em: print("[VOICE] Got:", em))

    runtime.trigger_emotion("Aroused", 1.0)
    runtime.trigger_emotion("Curious", 0.85)

    for _ in range(6):
        runtime.update_cycle()
        time.sleep(1)
