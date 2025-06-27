import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# emotion_vfx_overlay.py
# Controls visual overlays and environmental effects based on emotional state

EMOTION_TO_VFX = {
    "Aroused": "soft glow, heat shimmer",
    "Romantic": "pink overlay, light sparkles",
    "Sad": "blue tint, rain streaks",
    "Happy": "sunbeam rays, color bloom",
    "Angry": "red flash, camera shake",
    "Scared": "dark vignette, tremble blur",
    "Excited": "fast light pulses, motion streaks",
    "Lonely": "grayscale fade, depth fog",
    "Jealous": "green hue wash, vignette",
    "Flustered": "bloom flicker, red tint",
    "Desperate": "contrast spike, flickering frame",
    "Calm (Neutral)": "standard lighting",
    "Loving": "soft lens, golden tint",
    "Climactic": "light burst, bloom overload",
    "Submissive": "dimmer lights, narrow focus",
    "Dominant": "high contrast, spotlight center",
    "Sleepy": "soft blur, low saturation",
    "Curious": "zoom focus, light trails",
    "Physically Hyper-Aroused": "lens flare, ambient flicker"
}

ENABLED = True


def get_emotion_vfx(top_emotions):
    if not ENABLED:
        return ""
    e1 = top_emotions[0] if top_emotions else "Calm (Neutral)"
    return EMOTION_TO_VFX.get(e1, "standard lighting")

if __name__ == "__main__":
    current = ["Romantic"]
    print("[VFX Overlay] Active VFX:", get_emotion_vfx(current))
