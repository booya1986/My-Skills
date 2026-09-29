# Style B · Editorial collage — design system

Measured from the reference reel (50 s, 1080×1920, −14.4 LUFS, 30 cuts at scene>0.25) and refined on
a real 81 s build. The reference build is `assets/style-b/reference-build.py` (a Python generator that writes
`index.html`): copy it into the project, then edit only its tables (face windows, collage clips, overlays,
bursts, captions, cuts) and the scene HTML.

## Modes

| Mode | What is on screen | Share | Notes |
|---|---|---|---|
| **UI** | off-white `#f7f7f5` with a 26 px dot grid; one minimal object: chat bar being typed in, file window, markdown doc, two stacked cards, "Generating" pill; a cursor that moves and clicks | ≈40 % | content lives in y 200–1400; the face card sits below |
| **Collage + card** | full-bleed collage (still with stop-motion jitter, or animated video) and the face card on top | ≈20 % | the way to keep lip-sync while cutting away |
| **Full-bleed collage** | animated collage, no face | ≈25 % | only where the source has no face, or for a strong beat |
| **Burst** | 6–12 shots of 0.10–0.11 s, each a different collage at a different zoom/origin, a tick on each | 2–3 per reel | one in the first 3 s |
| **CTA** | animated collage sign with the keyword on it + green sub-chip + music swell + boom | last 2.5 s | |

Rules: no UI stretch longer than ~5 s without an overlay or burst; first cut by ~0.9 s; frame 0 fully drawn
(no fade from empty); every collage gets a 1.12→1.0 snap and a slow push to 1.05.

## Face card
- Small: 330×194, radius 30, 4 px white ring, soft shadow, `left:375 top:1690` (bottom centre). Use it when the
  face source is a webcam bubble — never display a face larger than ~1.2× its source pixels (the user sees
  pixelation immediately; an AI upscale of a 60 px face adds no real detail).
- Large (reference look): 964 px wide, top 1355, radius 64 — only with a sharp native face source.
- Visible only on lip-synced windows; re-enters with y 160→0 and scale 0.9→1 (`back.out`).

## Captions
Single row at `top:1572` (just above the small card). Chip: `rgba(30,30,30,.92)`, radius 6, padding 4/20,
Noto Sans Hebrew 500, 46 px, white. 1–3 words by meaning. Latin/commands in JetBrains Mono inside `.ltr`.

## Collage generation (Higgsfield)
- Image: `gpt_image_2_5`, 9:16, 1 credit. Prompt skeleton: "Vintage editorial paper-cut collage, Vox explainer
  style: <one concrete metaphor for the sentence>. Halftone black-and-white photo cutouts, torn cream paper
  background with graph-paper scraps, accents only in flat <brand colour> and charcoal black paper shapes, visible
  cut edges and soft shadows. No text, no letters. Vertical 9:16, subject in upper two thirds."
  Keep the subject in the upper two thirds — the caption and face card cover the bottom.
- Animation: `seedance_2_5`, `mode: omni_reference`, `start_image` = the image job id, 5 s, 1080p,
  `generate_audio: false`, 45 credits. Prompt: "Paper cut-out stop-motion animation. <one physical action>.
  Slight stop-motion jitter. Static camera, slow push in. Keep the collage style, no text."
  `upscale_video` has no cost preflight — read `balance` before and after.
- Wrong palette? `scripts/recolor_accents.py in out --map blue=#22C55E red=#2B2B28` recolours images and videos
  for free. Map only one band to the brand colour and the rest to charcoal — all-green loses contrast.
- One metaphor per spoken idea (rulebook + stamp = global rules; umbrella over a town = all projects;
  two-drawer cabinet = two levels; scissors on a scroll = short answers; typewriter = typing a command;
  magnifier on a blueprint = scanning the project; doctor = /doctor).

## UI kit (in the reference build)
`.win` white window (radius 30, traffic lights, mono title), `.dwin` dark window, `.chat` bar (typed text with
`steps()` clip-path, brand-colour send button that presses), `.greet` serif line (Frank Ruhl Libre) with the
Claude logo, `.md` doc (headings, highlighted bullet, grey line placeholders, scrolls inside a clipped body under
the title bar), `.fcard` label cards with a brand ring, `.pill` "Generating" with a moving gradient, `.cursor`,
`.folder` in brand colour with the logo in white, `.ok` green check (SVG, not a ✓ glyph).

## Audio
Voice 1.0, bed 0.16 (0.40 under the CTA), whoosh 0.32 on every cut, click 0.55 on UI actions, tick 0.45 on every
burst shot, boom under the CTA. Integrated −14 ±0.7 LUFS.
