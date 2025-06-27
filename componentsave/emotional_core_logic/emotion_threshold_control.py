import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# EmotionThresholdControl - Final Version
# ---------------------------------------
# Controls which emotion signals are strong enough to trigger output actions

class EmotionThresholdControl:
    def __init__(self, threshold=0.7):
        self.threshold = threshold
        self.last_passed = {}  # optional tracking

    def check(self, emotion, value):
        passed = value >= self.threshold
        if passed:
            self.last_passed[emotion] = value
        return passed

    def set_threshold(self, new_threshold):
        self.threshold = float(new_threshold)

    def get_threshold(self):
        return self.threshold

__all__ = ["EmotionThresholdControl"]
