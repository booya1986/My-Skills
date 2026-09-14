---
name: clip-to-reel
description: Turn a spoken passage from ANY existing video — a talking-head recording, a screen recording with a webcam bubble, a selfie video, a podcast or lecture — into a finished vertical 9:16 explainer reel in a proven "paper-split" creator style — cuts only on verified silences, split / studio / full-face / dark-terminal modes, heavy 1–3-word caption chips on the seam, real logos, a licensed web b-roll card, a music bed, SFX on every cut, a full-screen keyword CTA card, and an independent judge-agent similarity loop against a reference reel. Use this whenever the user gives a video (file or path) plus a timecode range or a pasted transcript excerpt and wants a Reel / Short / TikTok out of it — "make a reel from 16:20 to 16:54", "turn this part into a short", "another clip like the last reel", "copy the style of this creator's reel" — even if the skill isn't named.
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, Agent
---

# clip-to-reel

Turn a passage of an existing long video into a vertical reel with one specific, proven look: a creator-style
explainer that alternates beige-paper split screens, bright UI-mock scenes, full-screen face shots and a short dark
terminal beat, with heavy caption chips and a keyword CTA. The recipe was refined over eight independent judge
rounds against a top creator's reel, and `assets/reference-composition.html` is the final approved build.

**Deliverables:**
- `<slug>_9x16.mp4`: full quality.
- `<slug>_9x16_share.mp4`: under 30 MB, for phones and chat apps.

Read `references/gotchas.md` before starting. Every item there cost a render or an approval round.

## Requirements

`ffmpeg`, `python3` with `numpy` + `Pillow`, [whisper.cpp](https://github.com/ggerganov/whisper.cpp) (`whisper-cli`)
with a large-v3-turbo model (set `WHISPER_MODEL`), Node + [HyperFrames](https://hyperframes.heygen.com) (`npx hyperframes`),
and optionally `yt-dlp` for analysing a reference reel.

## The target look — and only this look

Measure every decision against `references/design-system.md` and `assets/reference-composition.html`:

- **Split screen:** a beige paper top half with a concrete graphic, the face in the bottom half, and the chip on the seam.
- **Bright studio scenes:** Apple-like windows and objects, highlighter sweeps, dotted links, grids with a moving selection, check badges.
- **One dark beat** (≤ 2 s): glowing orange mono text plus pixel letters.
- **One framed web-video card**, with floating real-logo tiles.
- **Captions:** heavy grey 1–3-word chips.
- **Transitions:** a snap-zoom plus a whoosh on every cut, a slow push-in on every shot.
- **Ending:** a full-screen paper CTA card with a huge bold sans keyword.

Don't drift into other reel templates. That means no persistent top banner, no boxed PIP webcam, no dark scrims
over footage, no progress bar, no long bottom subtitles, no URL overlays. They score worse against the reference and
they are not this style.

## Inputs to collect (ask only for what you can't infer)

| Input | Default / how to get it |
|---|---|
| **Source video** | the file the user names. Any resolution or aspect. |
| **Passage** | timecode range, or pasted text (locate it in the transcript). |
| **Language** | detect from speech. Right-to-left languages → RTL chips and right→left motion. |
| **CTA keyword + promise** | the word viewers comment and what they receive (e.g. "GUIDE" and "I'll send you the full guide"). |
| **Brand logo** | a simple-icons slug or a supplied SVG/PNG. |
| **Music** | a supplied or licensed track. Never leave the bed silent. |
| **Style reference** | the look is already encoded here. A different reference reel → see "New reference". |

## Workflow

Work in `_work/<slug>/` for intermediates and `reel-<slug>/` for the HyperFrames project.

### 1 · Map the passage
1. **Words:** use an existing word-level transcript, or run `bash scripts/transcribe.sh SOURCE.mp4 _work/<slug>/words.json [lang]`.
2. **Voice:** `ffmpeg -i SOURCE -vn -ac 1 -ar 48000 _work/<slug>/voice.wav`.
3. **Silences:** `python3 scripts/find_cuts.py voice.wav words.json FROM TO 90`.
4. **Layout:** run `bash scripts/grid_crops.sh SOURCE FROM TO layout.jpg` and look at it. Classify each stretch:
   - **full-frame face**;
   - **screen share with webcam bubble**: note the anchored corner and the size changes;
   - **no face**.

   Also note burned-in subtitles, lower thirds and callouts, since crops must avoid them.

### 2 · Plan the speech (target 30–40 s)
- Cut **only** at silences, and verify every edge by transcription: `bash scripts/verify_cut_edges.sh voice.wav T1 T2 … --rms`.
  Word timestamps drift by up to a whole word, and the snippet is the truth.
- Prefer one or two long uncut blocks. Open on the start of a sentence, and end on a finished thought.
- **Fillers** ("so", "like"): remove one only with a pause on both sides. Otherwise keep it and tell the user.
- Assemble: `python3 scripts/assemble_voice.py voice.wav words.json "a-b,c-d" media/vo.wav reel_words.json`,
  then re-verify each join.

### 3 · Faces (the quality ceiling)
- **Webcam bubble:**
  1. Measure the anchored corner on the grid sheet.
  2. Run `python3 scripts/track_bubble.py src.mp4 bubble.cmd --anchor-right X --anchor-bottom Y [--hold ranges]`.
  3. Render the 9:8 lower-half crop (see `references/media-recipes.md`).
- **Full-frame face:** use only the clean window, excluding dissolves.
- **Face recipe:** `hqdn3d=1.5:1.5:3:3` → lanczos → `unsharp=5:5:0.6` → `noise=alls=3:allf=t`.
  Stronger sharpening reads as noise, and stronger denoising reads as wax.

### 4 · Other media
- **Web b-roll:** one licensed clip that matches the topic (e.g. Pexels). Grade it bright and warm, and show it as a framed 16:9 card.
- **Logos:** `https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/<slug>.svg`, used as CSS masks.
- **Music:** `bash scripts/make_music_bed.sh TRACK <duration> media/music_bed.mp3 [loop_from] [loop_to]`.
- **Paper grain:** `python3 scripts/make_paper_grain.py media/paper_grain.png`.
- **Voice polish:** de-ess plus light compression, then re-measure loudness to −14 ±0.7 LUFS.
- **SFX:** a short whoosh, click, soft impact and boom (any royalty-free or synthesized set) in `media/sfx/`.

### 5 · Compose
1. **Set up the project:**
   1. Run `npx hyperframes init reel-<slug>`.
   2. Copy `assets/reference-composition.html` to `reel-<slug>/index.html`.
   3. Put the fonts in `fonts/`: Noto Sans for your script plus JetBrains Mono (both OFL, from Google Fonts), named as in the `@font-face` rules.
   4. Keep the template's CSS system, `snap` / `push` helpers, caption rows, web card and CTA card. Replace the placeholder copy, scenes, media paths and timings.
2. **Scene list:** follow the proportions in `references/design-system.md`:
   - split ≈25 %;
   - studio ≈50 %, including one 5–6 s multi-beat window;
   - full face ≈15 %;
   - one dark beat ≤ 2 s;
   - the web card;
   - the CTA card.

   Graphics show **the concrete things being said**. If a graphic would still work for another topic, it's too generic.
   Show the instruction before the result.
3. **Captions:** 1–3 words per chip, from `reel_words.json`. A chip goes in `#capSeam` during split scenes, otherwise in `#capLow`.
4. **Audio:**
   - voice at 1.0;
   - music bed at 0.20, plus a boosted bed under the CTA card;
   - a whoosh at 0.19 on every scene start, −0.08 s;
   - clicks and impacts for on-screen actions;
   - a boom under the CTA.

### 6 · Verify before every render
```bash
python3 scripts/check_glyphs.py index.html                      # NONE (extend RANGES for your script)
npx --yes hyperframes check                                     # 0 errors, no contrast failures
npx --yes hyperframes snapshot --at <one time per scene>        # then READ the contact sheet
npm run render
```
Then check four things:
- **Loudness:** `ebur128` −14 ±0.7 LUFS.
- **No dead head or tail:** `silencedetect=noise=-45dB:d=0.15`.
- **Correct direction:** reading order in every chip.
- **Visual:** every snapshot frame fits the mode table.

### 7 · Judge loop
1. Make 1 fps sheets of your reel and the reference reel: `bash scripts/judge_sheet.sh video sheet.jpg`.
2. Spawn a **fresh** subagent per round with `references/judge-prompt.md`, blind to earlier scores.
3. Apply the ranked fixes in one batch, re-verify, re-render.

Stop at ≥ 90 %, or after ~3 rounds with no upward trend (judges disagree by ±3). Then name the real limit.
Usually that's a low-resolution face source, fixable only by a native vertical recording or an AI upscale.

### 8 · Deliver
1. Export both files. The share copy: `ffmpeg -i … -c:v libx264 -crf 21 -preset slow -c:a aac -b:a 160k -movflags +faststart`.
2. Report: the cut list (and any filler that stayed), the final judge score, and remaining weaknesses.

## New reference
To copy a different creator's reel:
1. Download it with `yt-dlp` (analysis only).
2. Make 1 fps and 5 fps sheets, and detect cuts with `select='gt(scene,0.25)'`.
3. Measure seam and chip positions, plus loudness and the music floor.
4. Write the grammar into a copy of `references/design-system.md` and adapt criterion 1 of the judge prompt.
5. Compose.
