#!/usr/bin/env bash
# Word-level transcript in Scribe shape: {"words":[{"text","start","end","type":"word"}]}
#   bash transcribe.sh SOURCE.(mp4|wav) out.json [lang]
# Uses whisper.cpp with large-v3-turbo (set WHISPER_MODEL). Language auto-detects unless given (he, en, ...).
set -euo pipefail
SRC="$1"; OUT="$2"; LANG_ARG="${3:-auto}"
M="${WHISPER_MODEL:-$HOME/.cache/whisper-cpp/ggml-large-v3-turbo.bin}"
[ -f "$M" ] || { echo "whisper model not found; set WHISPER_MODEL" >&2; exit 1; }
T=$(mktemp -d)
ffmpeg -y -v error -i "$SRC" -ar 16000 -ac 1 "$T/a.wav"
whisper-cli -m "$M" -l "$LANG_ARG" -ojf -of "$T/out" -f "$T/a.wav" >/dev/null 2>&1
python3 - "$T/out.json" "$OUT" <<'P'
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8", errors="surrogateescape"))
words = []
for seg in d.get("transcription", []):
    for tok in seg.get("tokens", []):
        t = tok.get("text", "")
        if t.startswith("[") or not t.strip():
            continue
        o = tok.get("offsets", {})
        if t.startswith(" ") or not words:
            words.append({"text": t.strip(), "start": o.get("from", 0) / 1000, "end": o.get("to", 0) / 1000, "type": "word"})
        else:
            words[-1]["text"] += t; words[-1]["end"] = o.get("to", 0) / 1000
json.dump({"words": words}, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
print(f"wrote {sys.argv[2]} ({len(words)} words)")
P
rm -rf "$T"
