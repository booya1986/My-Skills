#!/usr/bin/env bash
# Create a ready-to-edit reel project with everything the template needs.
#   bash setup_project.sh reel-<slug> [script-family]
#   script-family: Google Fonts family for chips/headlines, default "Noto Sans Hebrew"
#                  (use "Noto Sans" for Latin-only, "Noto Sans Arabic", ...)
# Result: index.html (the approved composition), gsap.min.js, fonts/, media/sfx/, media/paper_grain.png,
# media/logos/, package.json with a pinned hyperframes. Re-running is safe: existing files are kept.
set -euo pipefail
DIR="$1"; FAMILY="${2:-Noto Sans Hebrew}"
SK="$(cd "$(dirname "$0")/.." && pwd)"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124 Safari/537.36"
need() { command -v "$1" >/dev/null || { echo "missing dependency: $1 ($2)" >&2; exit 1; }; }
need ffmpeg "brew install ffmpeg"; need python3 "install Python 3"; need npx "install Node.js"; need curl "install curl"
python3 -c "import numpy, PIL" 2>/dev/null || { echo "missing python packages: pip install numpy Pillow" >&2; exit 1; }

mkdir -p "$DIR/fonts" "$DIR/media/sfx" "$DIR/media/logos"
[ -f "$DIR/index.html" ] || cp "$SK/assets/reference-composition.html" "$DIR/index.html"

# HyperFrames project files (pinned so renders are reproducible)
if [ ! -f "$DIR/package.json" ]; then
  V=$(npm view hyperframes version 2>/dev/null || echo latest)
  cat > "$DIR/package.json" <<EOF
{ "name": "$(basename "$DIR")", "private": true, "type": "module",
  "scripts": { "check": "npx --yes hyperframes@$V check", "render": "npx --yes hyperframes@$V render",
               "dev": "npx --yes hyperframes@$V preview" } }
EOF
fi
[ -f "$DIR/hyperframes.json" ] || [ ! -f "$SK/assets/scaffold/hyperframes.json" ] || cp "$SK/assets/scaffold/hyperframes.json" "$DIR/"

# GSAP (the template loads ./gsap.min.js)
[ -f "$DIR/gsap.min.js" ] || { [ -f "$SK/assets/scaffold/gsap.min.js" ] && cp "$SK/assets/scaffold/gsap.min.js" "$DIR/"; } \
  || curl -sfL -o "$DIR/gsap.min.js" "https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"

# Fonts: fetch the woff2 subsets the template's @font-face rules reference
fetch_subset() { # family weight subset-comment out
  local css url
  css=$(curl -sfL -A "$UA" "https://fonts.googleapis.com/css2?family=$(echo "$1" | tr ' ' '+'):wght@$2&display=swap") || return 1
  url=$(printf '%s\n' "$css" | awk -v s="/* $3 */" 'index($0,s){f=1} f&&/src:/{match($0,/https:[^)]+/);print substr($0,RSTART,RLENGTH);exit}')
  [ -n "$url" ] && curl -sfL -o "$4" "$url"
}
for f in $(grep -o 'fonts/[A-Za-z0-9_-]*\.woff2' "$DIR/index.html" | sort -u); do
  out="$DIR/$f"; [ -f "$out" ] && continue
  [ -f "$SK/assets/scaffold/$f" ] && { cp "$SK/assets/scaffold/$f" "$out"; continue; }
  case "$f" in
    *JetBrainsMono-400*) fetch_subset "JetBrains Mono" 400 latin "$out" ;;
    *JetBrainsMono-700*) fetch_subset "JetBrains Mono" 700 latin "$out" ;;
    *-latin*)            fetch_subset "$FAMILY" "300..900" latin "$out" || fetch_subset "$FAMILY" 800 latin "$out" ;;
    *)                   sub=$(echo "$FAMILY" | awk '{print tolower($NF)}'); [ "$sub" = sans ] && sub=latin
                         fetch_subset "$FAMILY" "300..900" "$sub" "$out" || fetch_subset "$FAMILY" 800 "$sub" "$out" ;;
  esac
  [ -s "$out" ] && echo "font  $f" || echo "WARN: could not fetch $f — download it from fonts.google.com" >&2
done

# Logos used by the template (simple-icons, CC0)
for slug in $(grep -o 'media/logos/[a-z0-9]*\.svg' "$DIR/index.html" | sed 's#media/logos/##; s#\.svg##' | sort -u); do
  [ -f "$DIR/media/logos/$slug.svg" ] || { [ -f "$SK/assets/scaffold/media/logos/$slug.svg" ] && cp "$SK/assets/scaffold/media/logos/$slug.svg" "$DIR/media/logos/"; } \
    || curl -sfL -o "$DIR/media/logos/$slug.svg" "https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/$slug.svg" \
    || echo "WARN: logo $slug not found on simple-icons; supply media/logos/$slug.svg" >&2
done

# Synthesized SFX + paper grain
ls "$DIR/media/sfx/"*.wav >/dev/null 2>&1 || python3 "$SK/scripts/make_sfx.py" "$DIR/media/sfx"
[ -f "$DIR/media/paper_grain.png" ] || python3 "$SK/scripts/make_paper_grain.py" "$DIR/media/paper_grain.png"
cp -n "$SK/scripts/check_glyphs.py" "$DIR/check_glyphs.py" 2>/dev/null || true

echo "ready: $DIR  (next: add media/vo.wav, face clips, music bed, b-roll; edit index.html)"
