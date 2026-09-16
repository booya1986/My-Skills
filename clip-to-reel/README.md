# clip-to-reel

Turn any spoken passage of a long video (a talking head, a screen recording with a webcam bubble, a podcast) into a
finished vertical 9:16 explainer reel in a proven creator style. The output has paper split screens, bright UI-mock scenes, heavy caption chips,
snap-zoom cuts with SFX, a music bed and a keyword CTA card. An independent judge agent scores it against a reference
reel.

**For:** creators and teams who already have long-form video and want short vertical clips that look designed, not
just cropped.

## Install

```bash
git clone https://github.com/booya1986/My-Skills.git
cp -r My-Skills/clip-to-reel ~/.claude/skills/               # global
# or: cp -r My-Skills/clip-to-reel your-project/.claude/skills/   # project scope
```

Standalone: read `SKILL.md` and follow the eight steps manually. Every script in `scripts/` runs on its own.

## Requirements

`ffmpeg`, `python3` (+ `numpy`, `Pillow`), `whisper.cpp` with a large-v3-turbo model (`WHISPER_MODEL=/path/to/model.bin`),
Node with [HyperFrames](https://hyperframes.heygen.com), and optionally `yt-dlp`.

## 5-minute quick start

1. Ask Claude: *"Make a reel from `talk.mp4`, 04:10–04:52. CTA keyword GUIDE."*
2. The skill transcribes the video, finds real silences and verifies every cut by ear (transcription). It then tracks
   the face and builds the reel from `assets/reference-composition.html`.
3. It checks, renders and runs the judge loop, then delivers `<slug>_9x16.mp4` plus a sub-30 MB share copy.

## What's inside

| Path | Purpose |
|---|---|
| `SKILL.md` | the workflow |
| `references/design-system.md` | modes, proportions, tokens, caption chips, motion vocabulary |
| `references/media-recipes.md` | ffmpeg recipes for faces, b-roll, voice polish, share copy |
| `references/judge-prompt.md` | the similarity-judge rubric |
| `references/gotchas.md` | lessons that each cost a render |
| `scripts/` | transcription, silence finding, cut verification, voice assembly, bubble tracking, paper grain, music bed, glyph check, frame-fit check, judge sheets |
| `assets/reference-composition.html` | the approved composition, with placeholder copy |
