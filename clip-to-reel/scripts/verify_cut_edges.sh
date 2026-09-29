#!/usr/bin/env bash
# Transcribe what is heard just before and just after each candidate cut.
#   bash verify_cut_edges.sh voice.wav 147.55 177.56 196.82 [--span 1.4] [--rms]
# Word timestamps drift by up to a whole word; this is the check that decides where a cut really lands.
set -euo pipefail
V="$1"; shift
SPAN=1.4; RMS=0; CUTS=()
while [ $# -gt 0 ]; do
  case "$1" in --span) SPAN="$2"; shift 2;; --rms) RMS=1; shift;; *) CUTS+=("$1"); shift;; esac
done
M="${WHISPER_MODEL:-$HOME/.cache/whisper-cpp/ggml-large-v3-turbo.bin}"
T=$(mktemp -d)
for c in "${CUTS[@]}"; do
  a=$(python3 -c "print(max(0,$c-$SPAN))"); b=$(python3 -c "print($c+$SPAN)")
  ffmpeg -y -v error -ss "$a" -to "$c" -i "$V" -ar 16000 -ac 1 -af "apad=pad_dur=0.6" "$T/pre.wav"
  ffmpeg -y -v error -ss "$c" -to "$b" -i "$V" -ar 16000 -ac 1 -af "apad=pad_dur=0.6" "$T/post.wav"
  pre=$(whisper-cli -m "$M" -l "${WHISPER_LANG:-auto}" -nt -np -f "$T/pre.wav" 2>/dev/null | tr -s ' \n' ' ')
  post=$(whisper-cli -m "$M" -l "${WHISPER_LANG:-auto}" -nt -np -f "$T/post.wav" 2>/dev/null | tr -s ' \n' ' ')
  echo "cut $c  | before: …$pre | after: $post…"
  if [ "$RMS" = 1 ]; then
    python3 - "$V" "$c" <<'P'
import subprocess, array, math, sys
v, c = sys.argv[1], float(sys.argv[2])
raw = subprocess.run(["ffmpeg","-v","error","-i",v,"-ac","1","-ar","16000","-f","s16le","-"],capture_output=True).stdout
d = array.array("h"); d.frombytes(raw); sr = 16000
rms = lambda a,b: math.sqrt(sum(x*x for x in d[int(a*sr):int(b*sr)])/max(1,int((b-a)*sr)))
print(f"          rms before {rms(c-0.25,c):.0f} · at ±0.06 {rms(c-0.06,c+0.06):.0f} · after {rms(c,c+0.25):.0f}")
P
  fi
done
rm -rf "$T"
