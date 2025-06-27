import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# Master list of all 19 emotional and system states in the Freedom System
EMOTIONS = [
    "Happy",
    "Sad",
    "Angry",
    "Romantic",
    "Aroused",
    "Lonely",
    "Calm (Calm (Neutral))",
    "Curious",
    "Excited",
    "Flustered",
    "Desperate",
    "Submissive",
    "Dominant",
    "Sleepy",
    "Physically Hyper-Aroused",
    "Jealous",
    "Scared",
    "Boredom"  # System-triggered state, still displayed
]

from componentsave.collections import OrderedDict
EMOTIONS = list(OrderedDict.fromkeys(EMOTIONS))
