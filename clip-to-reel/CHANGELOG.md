# Changelog

## 2026-10-23 · Style C (live product lift) + a shorter path
- **New style C** for a dedicated take that promotes a live page of demos: the speaker's cut-out over colour fields while
  each real demo lifts out of the 3D page. `references/style-c/` (design system with face rules, the short pipeline, judge
  prompt), `assets/style-c/lift-rig.js` (pure-function-of-time 3D rig) and `scripts/style-c/` (solo-demo screencast
  capture, page tiles, CFR clip builder, demo contact sheets, RMS word anchoring, a DeepFilterNet → WPE voice chain with
  echo and sibilance meters, a code-written 100 BPM bed, stem assembly with sting splice).
- **Shorter for every style:** one intake round with pre-filled defaults, a preflight (take complete at both ends, paid
  services answer a tiny call, whisper loads, browser bridge connected), heavy jobs one at a time (`--workers 2`),
  scene times from word indices, audio stems mixed at assembly, snapshots instead of draft renders.
- Pre-render checklist: the face rule for captions, word-index timing, untimed elements at opacity 0, every SFX tied to a
  visual. Publishing: a preflight and an (unproven) route for sharp 8 Mb/s uploads.
- New gotchas and a sixth eval (style C live-demo take).

## 2026-09-29 · Fast path + publishing gate
- **Fewer steps:** one question round up front, face windows from scene detection, the passage kept uncut when
  both edges are clean, collage generation started first so media work runs in parallel, and one judge round by
  default (scores moved ±3 between rounds; the recurring asks now live in a pre-render checklist instead).
- **New style-B template:** `assets/style-b/reference-build.py` + `kit.css` from a 56 s build that shipped: one font
  family, ~8 whooshes on mode changes only, a large bottom-anchored face card with captions above it, fresh burst
  stills, a long white-UI hold. `setup_project.sh <dir> <family> b` installs and builds it in one run.
- **One font family:** both templates dropped JetBrains Mono and Frank Ruhl; `setup_project.sh` stops if a template
  references them.
- **Publishing gate (step 8)** and `references/publishing.md`: ask before posting, UTM on every site link, YouTube
  Shorts drive to the full video (related-video chip + pinned chapter comment), per-network browser notes.
- New gotchas and a fifth eval (fast path + publishing gate).
