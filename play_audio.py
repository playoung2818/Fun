#!/usr/bin/env python3
"""
play_audio.py

Cross-platform audio fallback for Hakuna Matata prank.
- Tries playsound (MP3/WAV)
- On Windows, also tries winsound for WAV
Usage:
    python play_audio.py assets/Hakuna_matata.mp3
"""

import sys, os

if len(sys.argv) < 2:
    print("usage: python play_audio.py <path-to-audio>")
    sys.exit(1)

path = sys.argv[1]
if not os.path.exists(path):
    print(f"[play_audio] file not found: {path}")
    sys.exit(1)

# Try playsound first
try:
    from playsound import playsound  # pip install playsound==1.2.2
    playsound(path)
    sys.exit(0)
except Exception as e:
    print("[play_audio] playsound failed:", e)

# Windows WAV fallback
if os.name == "nt" and path.lower().endswith((".wav",)):
    try:
        import winsound
        winsound.PlaySound(path, winsound.SND_FILENAME)
        sys.exit(0)
    except Exception as e:
        print("[play_audio] winsound failed:", e)

print("[play_audio] no working audio backend found.")
sys.exit(2)
