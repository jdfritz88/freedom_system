# Add to the top:
from emotional_core_logic.emotion_override_flag import current_emotion_override_flag
from emotional_core_logic.emotion_source_flag import current_emotion_source_flag

# Inside the function that broadcasts emotion data:

def broadcast_emotion(emotion: str, value: float, source: str = "system"):
    packet = {emotion: value}
    for callback in listeners:
        callback(packet)

    # Track override and source globally
    current_emotion_override_flag['is_override'] = (source == "override")
    current_emotion_source_flag['source'] = source
