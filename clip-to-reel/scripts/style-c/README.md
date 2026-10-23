# Style C scripts

Run order and reasons: `references/style-c/pipeline.md`. All take paths as arguments; the two Playwright scripts read
`PAGE_URL` and have their page selectors as constants at the top (adapt them to your page's solo mode and play hook).

| Script | Does |
|---|---|
| `capture_demos.mjs` | each demo solo → timestamped CDP screencast frames (2× viewport = sharp) |
| `capture_page.mjs` | `tiles`: the page with every demo hidden + slot rectangles; `scroll`: one smooth scroll |
| `build_demos.py` | frames → constant 30 fps clips cropped to the demo |
| `demo_sheet.py` | timestamped contact sheet of one demo, to find its key moments |
| `rms_segments.py` | speech segments from a 10 ms RMS map (cut points, word anchors) |
| `anchor_words.py` | whisper words re-anchored to the RMS segments → `[[text, start, end]]` |
| `clean_voice.py` | DeepFilterNet (uncapped) → WPE dereverb → EQ / comp / expander / de-esser / air, −14 LUFS |
| `echo_tail.py`, `sibilance.py` | measure echo after phrase ends and sibilance, to compare voice versions |
| `synth_bed.py` | a bass-heavy 100 BPM bed written in code (fallback when no music model is available) |
| `assemble_stems.py` | voice + SFX + ducked music, optional intro/outro splice, one CRF 12 encode |

The 3D rig itself is `assets/style-c/lift-rig.js` (pure function of time, drop it into a HyperFrames composition).
