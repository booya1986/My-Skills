#!/usr/bin/env bash
# Continuous music bed of an exact length from the series music.
#   bash make_music_bed.sh ".../edits/10-ending/music.mp3" 36.5 media/music_bed.mp3 [loop_from] [loop_to]
# The raw track dips to -28 dB around 5-9 s, which judges hear as a gap; loop its full-energy section instead.
set -euo pipefail
SRC="$1"; DUR="$2"; OUT="$3"; LF="${4:-10}"; LT="${5:-29.5}"
T=$(mktemp -d)
ffmpeg -y -v error -ss "$LF" -to "$LT" -i "$SRC" -ac 2 -ar 44100 "$T/seg.wav"
FADE_ST=$(python3 -c "print(max(0,$DUR-0.45))")
# enough copies to cover DUR (each join loses 1.2 s to the crossfade)
N=$(python3 -c "import math,subprocess;L=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0','$T/seg.wav']));print(max(2,math.ceil(($DUR-1.2)/(L-1.2))+1))")
IN=""; FC=""; prev="[0]"
for i in $(seq 0 $((N-1))); do IN="$IN -i $T/seg.wav"; done
for i in $(seq 1 $((N-1))); do FC="$FC${prev}[$i]acrossfade=d=1.2:c1=tri:c2=tri[m$i];"; prev="[m$i]"; done
ffmpeg -y -v error $IN -filter_complex \
  "${FC}${prev}afade=t=in:d=0.15,atrim=0:$DUR,afade=t=out:st=$FADE_ST:d=0.45" \
  -c:a libmp3lame -q:a 2 "$OUT"
rm -rf "$T"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT"
