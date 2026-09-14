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
