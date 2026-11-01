#!/usr/bin/env bash
# Rebuild the two Python environments the blocky engine needs, outside the repo. Nothing here is committed
# because it's large and rebuilds the same way every time: the models, faces, sets and stories are all code.
#
#   bash blocky/setup.sh [dir]      # default dir: ~/.blocky
#   then: export BLOCKY_BPY=<dir>/bpy-venv/bin/python BLOCKY_TTS=<dir>/tts-venv/bin/python
#
# Needs python3.11 (Blender's bpy module is built for it). On Ubuntu/Debian it also installs espeak-ng (Kokoro's
# phonemizer for unknown words) and the EGL/GL libraries bpy loads, with apt.
set -euo pipefail
DIR="${1:-$HOME/.blocky}"
mkdir -p "$DIR"
if command -v apt-get >/dev/null; then
  SUDO=""; [ "$(id -u)" = 0 ] || SUDO="sudo"
  $SUDO apt-get install -y espeak-ng libegl1 libgl1 libxi6 libxxf86vm1 libxfixes3 libxrender1 libxkbcommon0 libsm6 \
    || { $SUDO apt-get update && $SUDO apt-get install -y espeak-ng libegl1 libgl1 libxi6 libxxf86vm1 libxfixes3 libxrender1 libxkbcommon0 libsm6; }
fi
PY=$(command -v python3.11 || true)
[ -n "$PY" ] || { echo "python3.11 is needed for Blender's bpy module"; exit 1; }
[ -x "$DIR/bpy-venv/bin/python" ] || "$PY" -m venv "$DIR/bpy-venv"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
"$DIR/bpy-venv/bin/pip" install -q -r "$ROOT/requirements.txt" -r "$ROOT/requirements-bpy.txt"
[ -x "$DIR/tts-venv/bin/python" ] || "$PY" -m venv "$DIR/tts-venv"
"$DIR/tts-venv/bin/pip" install -q --extra-index-url https://download.pytorch.org/whl/cpu -r "$ROOT/requirements.txt" -r "$ROOT/requirements-tts.txt" faster-whisper
"$DIR/bpy-venv/bin/python" -c "import bpy; print('bpy', bpy.app.version_string)"
"$DIR/tts-venv/bin/python" -c "import kokoro, faster_whisper; print('kokoro and faster-whisper ok')"
echo "export BLOCKY_BPY=$DIR/bpy-venv/bin/python BLOCKY_TTS=$DIR/tts-venv/bin/python"
