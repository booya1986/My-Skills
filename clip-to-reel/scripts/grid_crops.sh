#!/usr/bin/env bash
# Layout survey of a passage: 6 evenly spaced frames with a 40 px measuring grid, tiled 3x2.
#   bash grid_crops.sh SOURCE.mp4 FROM TO out.jpg
# Use it to classify full-frame face vs webcam bubble vs no face, to read the bubble's anchored corner,
# and to spot burned-in subtitles/callouts that crops must avoid.
set -euo pipefail
SRC="$1"; FROM="$2"; TO="$3"; OUT="$4"; T=$(mktemp -d)
for i in 0 1 2 3 4 5; do
  t=$(python3 -c "print($FROM + ($TO-$FROM)*($i+0.5)/6)")
  ffmpeg -y -v error -ss "$t" -i "$SRC" -frames:v 1 -vf "drawgrid=w=40:h=40:t=1:c=yellow@0.30,drawtext=text='t=$t':x=10:y=10:fontsize=36:fontcolor=yellow:box=1:boxcolor=black@0.6" "$T/g$i.png" 2>/dev/null \
  || ffmpeg -y -v error -ss "$t" -i "$SRC" -frames:v 1 -vf "drawgrid=w=40:h=40:t=1:c=yellow@0.30" "$T/g$i.png"
done
ffmpeg -y -v error -i "$T/g0.png" -i "$T/g1.png" -i "$T/g2.png" -i "$T/g3.png" -i "$T/g4.png" -i "$T/g5.png" \
  -filter_complex "[0][1][2]hstack=3[a];[3][4][5]hstack=3[b];[a][b]vstack,scale=iw/2:-2" "$OUT"
rm -rf "$T"; echo "wrote $OUT (frames at half scale: multiply measured px by 2)"
