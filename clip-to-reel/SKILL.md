---
name: clip-to-reel
description: Turns a spoken passage from ANY existing video — a talking-head recording, a screen recording with a webcam bubble, a selfie video, a podcast or lecture — into a finished vertical 9:16 explainer reel in one of two proven styles the user picks first: A "paper split" (warm-paper split screens, Apple-like UI mocks, heavy caption chips, full-screen keyword CTA card) or B "editorial collage" (Vox-style animated paper-cut collages generated with Higgsfield, minimal white chat/doc UI, small face card, flat black chips, collage-sign CTA). Cuts only on verified silences, SFX on every cut, a music bed, and an independent judge-agent similarity loop against a reference reel. Use this whenever the user gives a video (file or path) plus a timecode range or a pasted transcript excerpt and wants a Reel / Short / TikTok out of it — "make a reel from 16:20 to 16:54", "turn this part into a short", "another clip like the last reel", "in the collage style" — even if the skill isn't named.
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

## Two styles — the user picks one (step 0)

Always start by showing `references/styles.md` (with the two preview sheets) and asking which style to use.
Then work only from that style's files:

| | A · Paper split | B · Editorial collage |
|---|---|---|
| In one line | warm-paper split screens, Apple-like UI mocks, heavy grey chips, full-screen CTA card | animated paper-cut collages (Higgsfield) + minimal white UI, small face card, flat black chips, collage-sign CTA |
| Design system | `references/design-system.md` | `references/style-b/design-system.md` |
| Starting build | `assets/reference-composition.html` (via `setup_project.sh`) | `assets/style-b/reference-build.py` → `index.html` |
| Judge | `references/judge-prompt.md` | `references/style-b/judge-prompt.md` |
| Credits | none | ≈380 Higgsfield credits — report the balance before and after every call |

**Style A:** a beige paper top half with a concrete graphic and the face below; bright studio scenes; one dark
beat ≤ 2 s; one framed web-video card with real-logo tiles; heavy grey 1–3-word chips; snap-zoom plus whoosh on
every cut; a full-screen paper CTA card with a huge bold sans keyword.

**Style B:** off-white dot-grid UI scenes (chat bar being typed, scrolling doc, "Generating" pill, cursor clicks);
full-bleed animated vintage collages in the brand accent colour; collage backdrops behind the UI; bursts of 0.1 s
shots; a small rounded face card at bottom centre; flat near-black chips; a collage sign with the keyword.

In both, don't drift into other reel templates (persistent top banner, boxed corner PIP, dark scrims over footage,
progress bar, long bottom subtitles, URL overlays). **Never show a face larger than ~1.2× its source pixels** —
with a webcam-bubble source use style B's small card; an AI upscale of a small face adds no real detail.

## Inputs to collect (ask only for what you can't infer)

| Input | Default / how to get it |
|---|---|
| **Source video** | the file the user names. Any resolution or aspect. |
| **Passage** | timecode range, or pasted text (locate it in the transcript). |
| **Language** | detect from speech. Right-to-left languages → RTL chips and right→left motion. |
| **CTA keyword + promise** | the word viewers comment and what they receive (e.g. "GUIDE" and "I'll send you the full guide"). |
| **Brand logo** | a simple-icons slug or a supplied SVG/PNG. |
| **Music** | a supplied or licensed track. Never leave the bed silent. |
| **Style** | A or B — ask (step 0). A different reference reel → see "New reference". |
| **Brand accent colour** (B) | the user's brand colour. |
| **Higgsfield OK?** (B) | confirm credits may be spent; report the balance before and after every call. |

## Workflow

Work in `_work/<slug>/` for intermediates and `reel-<slug>/` for the HyperFrames project.

Copy this checklist into your reply and tick items as you go:

```
Reel progress:
- [ ] 0 Style chosen by the user (A / B) from references/styles.md
- [ ] 1 Passage mapped (words, silences, layout sheet)
- [ ] 2 Cuts verified by transcription on both sides; voice assembled
- [ ] 3 Face clips rendered (bubble tracked / clean full-frame window)
- [ ] 4 B-roll card, logos, music bed, voice polish ready
- [ ] 5 Project set up and scenes composed to the mode table
- [ ] 6 check_glyphs NONE · hyperframes check 0 errors · check_frame_fit NONE · snapshot sheet reviewed · loudness −14 ±0.7
- [ ] 7 Judge loop run (≥90 % or plateau explained)
- [ ] 8 Full + share copy delivered with cut list and score
```

### 0 · Choose the style
Show `references/styles.md` and ask. For B also ask the accent colour and confirm Higgsfield spending.

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
- **Palette fix (style B):** `python3 scripts/recolor_accents.py in out --map blue=#22C55E red=#2B2B28`.
- **Music:** `bash scripts/make_music_bed.sh TRACK <duration> media/music_bed.mp3 [loop_from] [loop_to]`.
- **Paper grain:** `python3 scripts/make_paper_grain.py media/paper_grain.png`.
- **Voice polish:** de-ess plus light compression, then re-measure loudness to −14 ±0.7 LUFS.
- **SFX:** synthesized by `setup_project.sh` (`scripts/make_sfx.py`); swap in your own set if you prefer.

### 5 · Compose

**Style B:** run `setup_project.sh`, copy `assets/style-b/reference-build.py` to `build.py`, run it, then run
`setup_project.sh` again to fetch the fonts the new `index.html` needs. Follow `references/style-b/design-system.md`:
one collage per spoken idea, animate the strongest 5–8, keep every UI stretch under ~5 s of stillness, and run
`python3 build.py` before each check. Steps 1–4 below are style A.
1. **Set up the project:** `bash scripts/setup_project.sh reel-<slug> [font-family]` (default "Noto Sans Hebrew";
   "Noto Sans" for Latin-only). It creates the pinned HyperFrames project and brings the approved composition,
   GSAP, Google Fonts subsets, simple-icons logos, synthesized SFX and paper grain. Keep the template's CSS system,
   `snap` / `push` helpers, caption rows, web card and CTA card; replace the placeholder copy, scenes, media
   paths and timings.
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
bash scripts/check_frame_fit.sh index.html                          # NONE: no window/card leaves the frame, ever
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
2. Spawn a **fresh** subagent per round with the chosen style's judge prompt (A: `references/judge-prompt.md`, B: `references/style-b/judge-prompt.md`), blind to earlier scores.
3. Apply the ranked fixes in one batch, re-verify, re-render.

Stop at ≥ 90 %, or after ~3 rounds with no upward trend (judges disagree by ±3). Then name the real limit.
Usually that's a low-resolution face source, fixable only by a native vertical recording or an AI upscale.

### 8 · Deliver
1. Measure the render; if loudness is off by more than 0.7 LU, finish with two-pass `loudnorm` (see gotchas). Export both files. The share copy: `ffmpeg -i … -c:v libx264 -crf 21 -preset slow -c:a aac -b:a 160k -movflags +faststart`.
2. Report: the cut list (and any filler that stayed), the final judge score, and remaining weaknesses.

## Evaluations

`evals/evals.json` holds three realistic scenarios (bubble recording, full-frame talking head, new reference)
with expected behaviours. Rerun them after changing this skill.

## New reference
To copy a different creator's reel:
1. Download it with `yt-dlp` (analysis only).
2. Make 1 fps and 5 fps sheets, and detect cuts with `select='gt(scene,0.25)'`.
3. Measure seam and chip positions, plus loudness and the music floor.
4. Write the grammar into a copy of `references/design-system.md` and adapt criterion 1 of the judge prompt.
5. Compose.
