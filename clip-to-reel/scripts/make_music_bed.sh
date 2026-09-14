#!/usr/bin/env bash
# Continuous music bed of an exact length from a licensed track.
#   bash make_music_bed.sh track.mp3 36.5 media/music_bed.mp3 [loop_from] [loop_to]
# The raw track dips to -28 dB around 5-9 s, which judges hear as a gap; loop its full-energy section instead.
set -euo pipefail
SRC="$1"; DUR="$2"; OUT="$3"; LF="${4:-10}"; LT="${5:-29.5}"
T=$(mktemp -d)
ffmpeg -y -v error -ss "$LF" -to "$LT" -i "$SRC" -ac 2 -ar 44100 "$T/seg.wav"
FADE_ST=$(python3 -c "print(max(0,$DUR-0.45))")
ffmpeg -y -v error -i "$T/seg.wav" -i "$T/seg.wav" -i "$T/seg.wav" -filter_complex \
  "[0][1]acrossfade=d=1.2:c1=tri:c2=tri[a];[a][2]acrossfade=d=1.2:c1=tri:c2=tri,afade=t=in:d=0.15,atrim=0:$DUR,afade=t=out:st=$FADE_ST:d=0.45" \
  -c:a libmp3lame -q:a 2 "$OUT"
rm -rf "$T"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT"
