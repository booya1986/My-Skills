#!/usr/bin/env bash
# Frame-fit gate: every window/card stays inside the frame for the whole timeline.
#   bash check_frame_fit.sh reel-<slug>/index.html [margin=20] [step=0.05]
# Prints NONE and exits 0 when clean. Installs Playwright + Chromium on first use.
set -euo pipefail
export FIT_SCRIPT="$(cd "$(dirname "$0")" && pwd)/check_frame_fit.mjs"
export FIT_FILE="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")" FIT_MARGIN="${2:-20}" FIT_STEP="${3:-0.05}"
npx --yes -p playwright@1 -c 'playwright install chromium >/dev/null 2>&1 || true
  PW_MODULES="$(cd "$(dirname "$(command -v playwright)")/.." && pwd)" node "$FIT_SCRIPT" "$FIT_FILE" "$FIT_MARGIN" "$FIT_STEP"'
