# Changelog

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
