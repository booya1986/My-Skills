---
name: clip-to-reel
description: Turns a spoken passage from ANY existing video (talking head, screen recording with a webcam bubble, selfie, podcast, lecture) into a finished vertical 9:16 explainer reel in one of two proven styles the user picks first: A "paper split" (warm-paper split screens, Apple-like UI mocks, heavy caption chips, full-screen keyword CTA card) or B "editorial collage" (animated paper-cut collages generated with Higgsfield, minimal white UI, face card, flat black chips, collage-sign CTA). Fast path: one question round, a ready template, parallel media work and one judge round, then a publishing gate that asks before posting anywhere (UTM-tagged links; YouTube Shorts point to the full video). Use it whenever the user gives a video plus a timecode range or a pasted transcript excerpt and wants a Reel / Short / TikTok ("make a reel from 16:20 to 16:54", "did we already make a reel from this?", "in the collage style"), or asks to publish a finished reel to their social networks.
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, Agent
---

# clip-to-reel

Turn a passage of an existing long video into a vertical reel with one specific, proven look: a creator-style
explainer that alternates beige-paper split screens, bright UI-mock scenes, full-screen face shots and a short dark
terminal beat, with heavy caption chips and a keyword CTA. The recipe was refined over eight independent judge
rounds against a top creator's reel, and `assets/reference-composition.html` is the final approved build.

**Deliverables:**
- `<slug>_9x16.mp4` full quality · `<slug>_9x16_share.mp4` under 30 MB (phones, chat apps) ·
  `<slug>_9x16_upload.mp4` under 10 MB (browser uploads) · optionally `<slug>-yt_9x16_upload.mp4`, a variant whose
  CTA points to your full video instead of a comment keyword.

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
| Starting build | `assets/reference-composition.html` (via `setup_project.sh`) | `assets/style-b/reference-build.py` + `kit.css` (via `setup_project.sh … b`) |
| Judge | `references/judge-prompt.md` | `references/style-b/judge-prompt.md` |
| Credits | none | ≈250–320 Higgsfield credits (images ≈1, animations ≈58–60 each) — report the balance before and after |

**Style A:** a beige paper top half with a concrete graphic and the face below; bright studio scenes; one dark
beat ≤ 2 s; one framed web-video card with real-logo tiles; heavy grey 1–3-word chips; snap-zoom plus whoosh on
every cut; a full-screen paper CTA card with a huge bold sans keyword.

**Style B:** off-white dot-grid UI scenes (chat bar being typed, scrolling doc, "Generating" pill, cursor clicks);
full-bleed animated vintage collages in the brand accent colour; collage backdrops behind the UI; bursts of 0.1 s
shots; a rounded face card (small for a webcam bubble, large and bottom-anchored for a sharp full-frame face);
flat near-black chips; a collage sign with the keyword.

In both, don't drift into other reel templates (persistent top banner, boxed corner PIP, dark scrims over footage,
progress bar, long bottom subtitles, URL overlays). **Never show a face larger than ~1.2× its source pixels** —
with a webcam-bubble source use style B's small card; an AI upscale of a small face adds no real detail.
**One font family for all text** (the templates use Noto Sans; swap the subset for your script).

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

## Workflow (fast path)

Work in `_work/<slug>/` for intermediates and `reel-<slug>/` for the HyperFrames project.

Copy this checklist into your reply and tick items as you go:

```
Reel progress:
- [ ] 0 Existing reel? + ONE question round (style, credits, CTA)
- [ ] 1 Passage mapped: words, silences, face windows (scene cuts)
- [ ] 2 Voice: cut on verified silences (prefer one uncut take), polished to −14 LUFS
- [ ] 3 Parallel: collage stills + animations ‖ face clip ‖ music bed ‖ project setup
- [ ] 4 Compose from the template; pre-render checklist passes
- [ ] 5 Gates: glyphs NONE · check 0 errors · frame-fit NONE · snapshot sheet read
- [ ] 6 Render → loudnorm −14 → one judge round → fix → final render
- [ ] 7 Export full / share / upload (+ full-video variant) and deliver
- [ ] 8 Publishing gate: ask; publish only after an explicit yes
```

### 0 · Before building: check, then ask once
1. **Already made?** Check the exports folder and any notes for a reel of the same passage; if one exists, say so
   and ask before building a second.
2. **One question round** covering everything not already known: style A/B (show both preview sheets,
   `assets/target-look-scenes.jpg` and `assets/style-b/target-look.jpg`), for B the OK to spend credits and the
   brand colour, and the CTA keyword + promise. Don't ask one question per step.

### 1 · Map the passage (no guessing)
- Words: `bash scripts/transcribe.sh` on the passage window only (cut the source to ~passage + 10 s first).
  Subtitle files are fine for locating a pasted excerpt, never for cutting.
- Silences: `python3 scripts/find_cuts.py voice.wav words.json FROM TO 90`.
- Face windows: `ffmpeg -i src -vf "select='gt(scene,0.2)',showinfo" -an -f null -` gives the cuts between face and
  B-roll; trim ~0.1 s off each dissolve edge. One 100 px-grid frame per window places the crop (stay clear of
  burned-in subtitles). Use `grid_crops.sh` only for unknown layouts; track an animated bubble with
  `track_bubble.py` (see `references/media-recipes.md`).

### 2 · Voice
If the user pasted a complete passage and both ends sit in clean silences, take it **uncut** and verify only the two
edges (`verify_cut_edges.sh … --rms`). Otherwise cut only on verified silences (`assemble_voice.py`), remove a
filler only with a pause on both sides, and report the ones that stayed. Polish per media-recipes, then re-measure:
−14 ±0.7 LUFS (add a `volume` step if the polish pulled it down).

### 3 · Run media in parallel (don't wait on Higgsfield)
- **Style B collages:** one image batch of ~12 stills (one concrete metaphor per spoken idea; prompt skeleton in the
  style-B design system) **plus ~8 extra stills only for the bursts** (bursts must not reuse the main plates).
  For any pop-culture reference, prompt an anonymous figure ("face not visible, not resembling any real person")
  and regenerate lookalikes. Review a contact sheet, then one video batch of 4–5 animations. Resubmit
  preset recommendations with `declined_preset_id`. Reuse an existing CTA sign animation when the keyword repeats.
- **While they render:** the face clip, the music bed (`make_music_bed.sh`) and
  `bash scripts/setup_project.sh reel-<slug> "Noto Sans" b` (one run: build.py, kit.css, index.html, GSAP, fonts, SFX).

### 4 · Compose
Style A follows `references/design-system.md`. Style B: edit only the tables, scene HTML and scene tweens of
`build.py`. Face windows = face card over a collage still; full-bleed animated collages where the source has no
face; white dot-grid UI scenes that show **the concrete things being said**; 2 bursts of 0.1 s shots (one in the
first 3 s); a CTA sign for the last 2.5 s.

**Pre-render checklist** (each item came from a judge round or a viewer):
- One font family: every `font-family` in index.html is the same (grep it).
- A whoosh only on ~8 mode changes (UI↔collage↔burst↔face↔CTA) at 0.6; burst ticks 0.45; clicks on UI actions.
- Captions never cover the mouth: with the large card, the caption row sits above the card.
- At least one continuous white-UI hold of 7–8 s with motion (cursor travel, cards rising, typing); no hold
  without motion; no letter-spaced English labels.
- Late elements rise from opacity 0. RTL pills with an icon get ≥ 120 px padding on the icon side.
- Slide-ins stay inside the frame; the face `<video>` carries `data-layout-allow-overflow` for its push-in.

### 5 · Gates before every render
```bash
python3 check_glyphs.py index.html                                        # NONE
npx --yes hyperframes@<pinned> check --samples 260 --at-transitions --tolerance 1 .   # 0 errors
bash scripts/check_frame_fit.sh index.html                                # NONE
npx --yes hyperframes@<pinned> snapshot --at <one time per scene>         # then READ the contact sheet
```
Contrast warnings on elements hidden under a full-bleed overlay are false positives; fix everything else.

### 6 · Render, loudnorm, judge once
`npm run render`, confirm the new file's mtime and duration, then always finish with a two-pass
`loudnorm=I=-14:TP=-1:LRA=7:linear=true` (video `-c copy`) and check `silencedetect` for a dead head or tail.
**One judge round by default:** a fresh subagent with the style's judge prompt and `judge_sheet.sh` sheets, told
about the deliberate client decisions (face-card size, brand colour, one font, CTA). Apply its ranked fixes in one
batch and re-render. Run another round only if the user wants more polish; judges disagree by ±3, so don't chase
noise. The usual ceiling is the face source, not the edit.

### 7 · Export and deliver
```bash
ffmpeg -i full.mp4 -c:v libx264 -crf 21 -preset slow -c:a aac -b:a 160k -movflags +faststart <slug>_9x16_share.mp4
# upload copy < 10 MB: two-pass -b:v 1200k (a 56 s reel ≈ 9.5 MB), -c:a aac -b:a 128k
```
If the user publishes Shorts that should drive to a full video, build the variant now
(`references/publishing.md` §0). Report the cut list, fillers kept, judge score, credits spent and what is still weak.

### 8 · Publishing gate
Ask which networks to publish to (or "not now"). Nothing goes public before an explicit yes. Then follow
`references/publishing.md`: draft the texts, show them for one approval, tag every link to your site with UTM
parameters, publish network by network, verify each post live, and report the URLs.

## Evaluations

`evals/evals.json` holds five realistic scenarios (bubble recording, full-frame talking head, new reference,
style B, fast path + publishing gate) with expected behaviours. Rerun them after changing this skill.

## New reference
To copy a different creator's reel:
1. Download it with `yt-dlp` (analysis only).
2. Make 1 fps and 5 fps sheets, and detect cuts with `select='gt(scene,0.25)'`.
3. Measure seam and chip positions, plus loudness and the music floor.
4. Write the grammar into a copy of `references/design-system.md` and adapt criterion 1 of the judge prompt.
5. Compose.
