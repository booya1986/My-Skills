# clip-to-reel

Turn any spoken passage of a long video (a talking head, a screen recording with a webcam bubble, a podcast) into a
finished vertical 9:16 explainer reel in one of two proven creator styles you pick first:

- **A · Paper split:** paper split screens, bright UI-mock scenes, heavy caption chips, snap-zoom cuts with SFX,
  a music bed and a keyword CTA card.
- **B · Editorial collage:** Vox-style animated paper-cut collages (generated with Higgsfield) in your brand colour,
  minimal white chat/doc UI, a face card, 0.1 s bursts and a collage-sign CTA.

It runs a fast path (one question round, a ready template, parallel media work, one judge round against a reference
reel) and ends with a **publishing gate**: it asks before posting to Instagram, Facebook, LinkedIn, X, TikTok or
YouTube Shorts, tags every link with UTM, and makes Shorts drive to your full video.

**For:** creators and teams who already have long-form video and want short vertical clips that look designed, not
just cropped.

## Install

```bash
git clone https://github.com/booya1986/My-Skills.git
cp -r My-Skills/clip-to-reel ~/.claude/skills/               # global
# or: cp -r My-Skills/clip-to-reel your-project/.claude/skills/   # project scope
```

Standalone: read `SKILL.md` and follow the nine steps manually. Every script in `scripts/` runs on its own.

## Requirements

`ffmpeg`, `python3` (+ `numpy`, `Pillow`), `whisper.cpp` with a large-v3-turbo model (`WHISPER_MODEL=/path/to/model.bin`),
Node with [HyperFrames](https://hyperframes.heygen.com), optionally `yt-dlp`, and for style B a
[Higgsfield](https://higgsfield.ai) connection (image + video generation).

## 5-minute quick start

1. Ask Claude: *"Make a reel from `talk.mp4`, 04:10–04:52. CTA keyword GUIDE."*
2. The skill transcribes the video, finds real silences and verifies every cut by ear (transcription). It then tracks
   the face and builds the reel from `assets/reference-composition.html`.
3. It checks, renders, runs one judge round, then delivers `<slug>_9x16.mp4`, a sub-30 MB share copy and a
   sub-10 MB upload copy.
4. It asks whether to publish, and to which networks. Nothing is posted before you say yes.

## What's inside

| Path | Purpose |
|---|---|
| `SKILL.md` | the workflow |
| `references/design-system.md` | modes, proportions, tokens, caption chips, motion vocabulary |
| `references/media-recipes.md` | ffmpeg recipes for faces, b-roll, voice polish, share copy |
| `references/styles.md` | the A/B style picker shown to the user |
| `references/judge-prompt.md` | the similarity-judge rubric (style A) |
| `references/style-b/` | style B design system and judge rubric |
| `references/gotchas.md` | lessons that each cost a render |
| `references/publishing.md` | the publishing gate: texts, UTM tags, per-network browser notes, the Shorts setup |
| `CHANGELOG.md` | what changed and why |
| `scripts/` | transcription, silence finding, cut verification, voice assembly, bubble tracking, paper grain, music bed, glyph check, frame-fit check, accent recolouring, judge sheets |
| `assets/reference-composition.html` | the approved style-A composition, with placeholder copy |
| `assets/style-b/reference-build.py` + `kit.css` | the style-B generator (writes `index.html`) and its CSS kit, with placeholder copy |
