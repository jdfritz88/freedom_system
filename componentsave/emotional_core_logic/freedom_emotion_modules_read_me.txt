# Freedom Emotion Modules

This folder contains the core emotional logic powering the Freedom system.
Each module is responsible for interpreting, scoring, blending, and reacting to emotional states over time.

---

## Modules

### `freedom_emotion_blender.py`
Determines the top 2 dominant emotions based on intensity and blending rules:
- Only top 3 emotions considered
- Aroused and Curious override
- Positive emotions win ties

### `emotion_decay_module.py`
Handles emotion decay over time:
- Default exponential drop over 30 seconds
- Supports per-emotion decay overrides

### `emotion_trigger_handler.py`
Triggers image generation:
- Fires when any emotion ≥ threshold (default 0.7)
- Resets 5-minute image timer
- Fallback: triggers "boredom" image if no input in 5 minutes

### `emotion_broadcast_hub.py`
Sends dominant emotion pair to all subscribing systems:
- Used by voice, image, animation, and music
- Ensures centralized, synced emotional response

### `emotion_threshold_control.py`
Handles the user-settable emotion trigger threshold:
- Textbox input from 0.0–1.0
- Console-based feedback system

### `emotion_framing_weights.py`
Determines likely camera framing per emotion:
- Full head, head-to-midriff, full body
- Weighted randomly based on emotion

### `emotion_image_generator.py`
Builds prompt strings for image generation:
- Adds framing tags
- Appends nudity elements for certain emotional states

### `emotion_system_status.py`
Master tracker for active emotion states:
- Combines decay + blender to provide real-time emotion view

---

All modules are sandbox-safe and can be run independently for debugging or simulation.
Ready for integration into the Freedom runtime.
