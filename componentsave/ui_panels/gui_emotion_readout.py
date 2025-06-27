# ... previous imports remain the same
from emotional_core_logic.emotion_override_flag import current_emotion_override_flag
from emotional_core_logic.emotion_source_flag import current_emotion_source_flag

# ... inside __init__ of EmotionReadoutPanel
        self.source_status = tk.StringVar(value="")
        self.label_source = ttk.Label(self.frame, textvariable=self.source_status, foreground="blue")
        self.label_source.grid(row=1, column=3, sticky="w", padx=(10, 0))

# ... inside process_queue
                    source_map = {
                        "override": "🕹️ Override",
                        "voice": "🎙️ Voice",
                        "system": "🧠 System",
                        "music": "🎵 Music"
                    }
                    self.source_status.set(source_map.get(current_emotion_source_flag['source'], ""))
