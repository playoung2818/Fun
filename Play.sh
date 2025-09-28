#!/usr/bin/env bash
set -euo pipefail

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MP3="$DIR/assets/Hakuna_matata.mp3"
PY="$DIR/animate.py"

play_song() {
  [[ ! -f "$MP3" ]] && { echo "[info] No assets/song.mp3 found — animation only."; return 0; }

  if command -v afplay >/dev/null 2>&1; then
    nohup afplay "$MP3" >/dev/null 2>&1 &  # macOS
    return 0
  fi
  if command -v mpg123 >/dev/null 2>&1; then
    nohup mpg123 -q "$MP3" >/dev/null 2>&1 &
    return 0
  fi
  if command -v ffplay >/dev/null 2>&1; then
    nohup ffplay -nodisp -autoexit -loglevel quiet "$MP3" >/dev/null 2>&1 &
    return 0
  fi
  if command -v aplay >/dev/null 2>&1; then
    nohup aplay "$MP3" >/dev/null 2>&1 &
    return 0
  fi

  echo "[warn] No audio player found (afplay/mpg123/ffplay/aplay). Continuing without audio."
}

play_song
# support test arg passthrough, e.g., --seconds 8
if command -v python3 >/dev/null 2>&1; then
  exec python3 "$PY" "$@"
else
  exec python "$PY" "$@"
fi
