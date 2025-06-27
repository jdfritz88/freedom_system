import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from output_bridges.systems_image.image_emotion_driver import generate_emotion_image

print("[TEST] Starting Image Emotion Driver Test")

# Simulate an emotion blend
emotion_input = {
    'aroused': 0.8,
    'romantic': 0.9
}

result = generate_emotion_image(emotion_input)

if result:
    print(f"[PASS] Image generated for emotion blend: {emotion_input}")
else:
    print(f"[FAIL] No image generated for: {emotion_input}")
