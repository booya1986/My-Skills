# Gotchas — each one cost a render, a judge round or an approval round

## Speech
- **Never cut on subtitle cue boundaries (.srt/.vtt)** — they split on line length, not syntax. Mid-sentence cuts were rejected three times. Cut only on silences from `find_cuts.py`.
- **Word timestamps lie by up to a whole word.** A quiet bump before a pause was breath (whisper hallucinated
  a filler word); the real filler came after it. Transcribe the snippet on each side of every cut.
- **Fillers:** remove only with a pause on both sides; otherwise keep and report it.
- De-essing/compression lowered loudness to −15.4 LUFS — always re-measure after voice FX.

## Picture
- Sources often have burned-in subtitles, lower thirds or callout cards. Find their rows on the grid sheet and crop around them.
- Some screen recorders animate the bubble between sizes — a fixed crop catches half a face. Track it.
- Full-frame windows have ~0.2 s dissolves at each edge; cover them with a graphic scene.
- Face sharpening → noise/halos; strong denoise → wax. Use the recipe in media-recipes.md.
- Push-ins above ~1.04 on an upscaled face make it visibly soft and crop the head.
- Dark stock footage looks muddy next to crisp icons — grade bright and frame it.
- Paper grain made from SVG `feTurbulence` barely shows in the render; stretched noise looks like wood streaks.
  Use `make_paper_grain.py`.

## HyperFrames / lint
- A `<video data-start>` inside a timed scene div fails lint — keep videos in untimed wrappers.
- Never tween `autoAlpha` on a `class="clip"` element; animate an inner wrapper.
- Repeated `tl.fromTo` on one element without a baseline → warning; use `tl.set` + `tl.to`, or `immediateRender:false`.
- Exits ending on a clip boundary need a matching `tl.set(…, {autoAlpha:0}, boundary)`.
- A lint **error** silently disables the layout and contrast audits — clear errors first.
- Assets must live inside the project folder; no `../` paths.
- `data-duration` of an `<audio>` must not exceed the file (click.wav 0.09 s, tick.wav 0.05 s).

## Text
- Only the embedded font subsets render; emoji, arrows, ✓ become boxes. `check_glyphs.py` must print NONE.
- A leading digit flips to the wrong end in RTL; spell numbers or isolate them in `.ltr` spans.
- Hebrew in `data-var-text` variables turns into mojibake — author Hebrew literally.
- Rust `#B84A26` passes contrast on paper; `#E4643A` does not for small text.

## Shell / tooling
- zsh does not word-split `set -- $r` inside for loops — wrap such loops in `bash <<'B' … B`.
- `python3 - <<'P' … P || exit 1` — otherwise a failed edit still renders the old file.
- Edits on the composition via python `str.replace` should `assert s.count(old)==1` so a stale anchor fails loud.
- File delivery to a phone caps at 30 MB — always send the `_share.mp4` copy.
- Social-network players often refuse to load in automation browsers; use `yt-dlp` for a reference reel.

## Judge loop
- Judges disagree by ±3 points; don't chase noise. Stop after ~3 rounds without a trend and name the real limit.
- Keep each judge blind to previous scores and tell it about the deliberate style choices (CTA card, sans word, web card).

## Learned on the second run (a 45 s passage with only ~10 s of face)
- **Passages that are mostly animation in the source have little lip-synced face.** Put the split scenes exactly on
  the face windows (measure them: the bubble region's mean/std jumps on the frame of the cut) and never reuse face
  footage under other audio. Tell the judge up front so it scores execution, not the source.
- **A single uncut take beats a filler cut.** If the only pause is ~70 ms, don't cut — take the whole block and
  trim length elsewhere (a 45 s take with a 2.4 s CTA card scored fine).
- **`select='gt(scene,0.25)'` misses light-to-light cuts** (studio→studio, paper→studio score 0.07–0.25). Give
  the judge both 0.25 and 0.10 thresholds, and make cuts read by alternating full-screen backgrounds white studio ↔
  cool grey `.studio2`; keep beige paper for split tops and the CTA only (paper in full-screen scenes was penalised).
- **Windows must never leave the frame.** Scales multiply: snap × push-in × punch-in × the element's own pop. A
  900 px window under push 1.14 × punch 1.18 is 1210 px wide and gets cut on both sides. Budget it: element width ×
  every scale on it ≤ 1040. For 860–900 px windows use push ≤ 1.03–1.04 and punch-in `set(1.13)` → `to(1.10)`; keep
  side-by-side cards ≥ 110 px from the edges. `scripts/check_frame_fit.sh` is the gate — it must print NONE.
- **Punch-in cuts inside long scenes** add real cuts: `tl.set(snap,{transformOrigin, scale:1.13})` → `to(1.10)`.
  Keep content above the caption row: with push-in Y' and scale k, origin y ≥ (k·Y' − 1180)/(k − 1).
- **A split longer than ~4 s reads as one hold** — break it with a 1.5 s full-screen studio insert of that beat's
  graphic, moving the overlapping chips to `#capLow`.
- **Auto-grouped captions split phrases badly** (e.g. a chip ending mid-phrase). Write chips by hand from the cue text, 1–3 words,
  split by meaning, and cut chips at mode boundaries.
- **Check that the render actually finished** before copying "the newest file": compare its mtime/duration.
- Scores on run 2: 63 → 69 → 77 → (round 4). Rising scores = keep iterating; flat ±3 = stop.

## Learned building style B (editorial collage)
- **Never show a face bigger than ~1.2× its source pixels.** A 164 px webcam bubble shown at half-screen looked
  pixelated to the user, and neither ByteDance (1 credit/min-ish) nor Topaz (1 credit/s) upscaling added real
  detail to a ~60 px face. Use the small face card.
- **GSAP `fromTo` ignores props that appear only in the from-vars.** `fromTo(card,{autoAlpha:1,y:160},{y:0})` never
  showed a card hidden earlier by `set(autoAlpha:0)`. Put every prop in the to-vars too.
- **A JavaScript error in the timeline script is not a lint error.** Symptoms: `check` suddenly reports contrast
  failures on hidden elements, and `check_frame_fit.sh` times out waiting for `__timelines`. A `const` used before
  its declaration (TDZ) was the cause — declare shared tables at the top of the script.
- **The HyperFrames mixer can pull integrated loudness down ~2 dB** when many SFX tracks overlap. Always measure the
  render and, if needed, finish with a two-pass `loudnorm=I=-14:TP=-1:LRA=7:linear=true` (video `-c copy`).
- **zsh reads `$var:l` as a modifier** (lower-case) — write `${var}:linear=true`.
- **ffmpeg inside a `bash <<EOF` loop eats the heredoc** — add `-nostdin`.
- **Judges misread timestamps** by a few seconds on long reels; map their notes to your scene table before editing.
  Also give the judge the client decisions (small card, brand colour, no face where the source has none), or it
  keeps asking to fake lip-sync.
- **Generated collages come out in the model's favourite red/blue.** Ask for the brand colour in the prompt, or run
  `recolor_accents.py` (free). Mapping every accent to the brand colour looked flat — one band to brand, the rest to
  charcoal.
- **Recurring judge asks for style B:** no blank frame between a burst and the next scene (extend the last burst
  shot by 1 frame); no UI stretch over ~5 s without motion (stop-motion steps on a blurred collage backdrop behind
  the UI fixed it); don't reuse the CTA plate in a burst; split chips longer than ~1.2 s.
- **Style B scores on an 81 s test reel:** 65 → 81 → 79 → 80 → 84 → 83 → 85 → 84. The ceiling was the small, soft
  face and the absence of a face in a third of the source.
