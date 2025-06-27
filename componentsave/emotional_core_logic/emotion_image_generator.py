from componentsave.output_bridges.systems_image.image_emotion_driver import dispatch_emotion_image

class EmotionImageGenerator:
    def generate(self, emotion, intensity):
        print(f"[IMAGE] Generating image for: {emotion} ({intensity})")
        dispatch_emotion_image(emotion, intensity)
