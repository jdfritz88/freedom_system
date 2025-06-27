# File: F:/Apps/freedom_system/launchers/emotion_engine_boot_flag.py
# Sets boot flag for emotion engine startup.

with open('emotion_engine.flag', 'w') as f:
    f.write('READY')

print('[FLAG] Emotion engine boot flag created.')
