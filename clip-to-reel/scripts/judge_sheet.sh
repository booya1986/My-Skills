#!/usr/bin/env bash
# 1 fps contact sheet (10 columns x 4 rows, 216 px wide frames) for the judge agent.
#   bash judge_sheet.sh video.mp4 sheet.jpg
set -euo pipefail
V="$1"; OUT="$2"; T=$(mktemp -d)
ffmpeg -y -v error -i "$V" -vf "fps=1,scale=216:-2" "$T/s%03d.jpg"
ffmpeg -y -v error -framerate 1 -i "$T/s%03d.jpg" -vf "tile=10x4:padding=4:color=black" -frames:v 1 "$OUT"
rm -rf "$T"; echo "wrote $OUT"
