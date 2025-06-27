# ... existing imports remain
from emotional_core_logic.emotion_override_flag import current_emotion_override_flag
from emotional_core_logic.emotion_source_flag import current_emotion_source_flag

# ... inside draw_emotion_label
        tag = "🔒 Overridden" if current_emotion_override_flag['is_override'] else ""
        source_map = {
            "override": "🕹️ Override",
            "voice": "🎙️ Voice",
            "system": "🧠 System",
            "music": "🎵 Music"
        }
        source_tag = source_map.get(current_emotion_source_flag['source'], "")
        self.canvas.create_text(
            150, 40,
            text=f"{emotion.capitalize()} ({intensity:.2f}) {tag}",
            font=("Segoe UI", 14, "bold"),
            tags="text"
        )
        self.canvas.create_text(
            150, 70,
            text=source_tag,
            font=("Segoe UI", 10, "italic"),
            tags="text"
        )
