# emotional_music_router.py
# Handles routing of emotion signals to music logic (internal only)

def route_emotion_signal(emotion_data):
    """
    Routes incoming emotion data to the appropriate handler.
    Expects format: {"emotion": intensity}.
    """
    from componentsave.output_bridges.systems_music.music_emotion_driver import handle_music_emotion

    if not isinstance(emotion_data, dict):
        print("[ROUTER] Invalid emotion data format. Expected dictionary.")
        return

    print(f"[ROUTER] Routing emotion: {emotion_data}")
    handle_music_emotion(emotion_data)


# music_emotion_driver.py
# Applies emotional response logic to music (internal state only)

def handle_music_emotion(emotion_data):
    """
    Handles internal music reaction logic based on emotional input.
    Uses top-2 emotion blending with positive bias.
    This module does NOT trigger music output.
    """
    if not isinstance(emotion_data, dict):
        print("[MUSIC DRIVER] Invalid emotion data format.")
        return

    # Extract and sort by intensity
    sorted_emotions = sorted(emotion_data.items(), key=lambda x: x[1], reverse=True)
    top_two = sorted_emotions[:2]

    dominant_emotion, intensity = top_two[0]
    print(f"[MUSIC DRIVER] Dominant: {dominant_emotion} ({intensity})")

    if len(top_two) > 1:
        second_emotion, second_intensity = top_two[1]
        print(f"[MUSIC DRIVER] Secondary: {second_emotion} ({second_intensity})")

    # Placeholder for actual effect logic (no music output)
    print("[MUSIC DRIVER] Reaction logic executed (internal only).")
