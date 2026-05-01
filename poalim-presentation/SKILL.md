---
name: poalim-presentation
description: Use this skill ONLY when the user explicitly asks for a slideshow / deck / presentation for Bank Hapoalim, Hapoalim L&D, or "Poalim" — i.e. the request must mention "Poalim", "Hapoalim", "Bank Hapoalim", "פועלים", "בנק הפועלים", or "the bank" (when context makes Hapoalim clear). DO NOT invoke this skill for generic slideshow / presentation / deck requests, blog-related slides, or any other branded deck — the user maintains a separate design system for their personal blog and other contexts. Produces two single-file vanilla deliverables for Poalim only: an `index.html`-style deck (Hebrew RTL, neon-red on dark, Heebo font, animated CSS/JS, no build, no framework) and a `speaker-notes.html` companion with auto-generated slide thumbnails.
---

# Poalim Presentation

Builds a single-file HTML slideshow deck and an optional speaker-prep companion in the Bank Hapoalim L&D visual language: Hebrew RTL, neon red `#FF2020` on near-black `#111111`, Heebo font, vanilla HTML/CSS/JS, no build pipeline. The user opens the file in a browser and that is the entire dev loop.

## When to invoke

**Trigger only when the request explicitly references Bank Hapoalim, Hapoalim L&D, "Poalim", "פועלים", or "the bank" (when context makes Hapoalim clear).** Phrases like "make me a deck for Poalim about X", "I need slides for the bank meetup", "build a presentation for Hapoalim training", or "מצגת לפועלים" all qualify. If the user has a brief, transcript, or topic they want turned into a Hapoalim-branded talk, that qualifies too.

**Do NOT invoke for generic deck / slideshow requests** — e.g. "make me a slideshow for my blog post", "build a presentation about X" with no Hapoalim mention, or any non-Poalim branded deliverable. The user maintains separate design systems for their personal blog and for other contexts; this skill is Hapoalim-specific. When in doubt, ask which design system they want before invoking.

If the user asks to *edit* the existing `index.html` (the L&D meetup deck) rather than produce a new one, you can still consult this skill for the rules and component catalogue, but the project-level `CLAUDE.md` is the primary spec for that file.

## Canonical implementation reference

The existing `index.html` and `speaker-notes.html` at the project root are the **authoritative reference implementation**. Open them and read structurally before building anything new. When you need a component, animation, or layout, **always scan `index.html` first** for an analogous existing element. The deck has 80+ component classes; introducing parallel new ones fragments the visual language.

The project-level `CLAUDE.md` documents the same conventions from the maintenance angle. Treat its rules as project invariants. This skill adds the **creation workflow** (interview → outline → implement → companion) on top.

## Workflow

The user gives you a topic, a brief, or sometimes a long transcript. Your job is to break it down into slides, choose appropriate layouts, and emit two HTML files. Follow these four steps in order; do not skip the interview or the outline approval.

### Step 1: Interview (concise — 4-5 questions, not a survey)

Before drafting slides, gather:

1. **Topic / framing** — what is the talk about, in one sentence?
2. **Audience** — engineers, leadership, mixed, training participants, external?
3. **Duration** — target talk length. Use this to size the deck:
   - 5 min → 5-7 slides
   - 10-15 min → 10-15 slides
   - 20-30 min → 20-30 slides (the example deck)
   - 45-60 min → 35-45 slides
4. **3-5 key takeaways** — what should the audience remember the next morning?
5. **Materials** — case studies, anecdotes, stats, quotes, screenshots, the user wants included. Ask explicitly whether they have media to drop into `img/`, `vid/`, or `sound/`.

Also confirm:
- **File name.** Default: `<slug>.html` in project root, where `<slug>` is a kebab-case version of the topic. Do **not** overwrite the existing `index.html` (it is the L&D meetup deck) unless the user explicitly asks.
- **Companion?** Default: yes, produce `<slug>-notes.html` alongside.
- **Audio?** Default: no. Audio pipeline is opt-in (see `references/audio-pipeline.md`).

If the user dropped a long brief or transcript, do not pepper them with all five questions; extract what you can from the brief and ask only about the gaps.

### Step 2: Propose the outline

Draft a slide-by-slide outline before writing any HTML. Show it to the user in this format:

```
1. Cover (layout: title) — "Headline + speaker name"
2. Agenda (layout: agenda) — 4-5 bullets
3. Divider 01 — "Section 1: X"
4. The hook (split) — body bullets ; visual: trinity-circles
5. ...
N-1. Q&A divider
N. CTA (layout: cta) — QR + thanks
```

For each slide give: layout choice, headline / hook, key visual idea, body bullets in shorthand. **Get the user's sign-off before implementing.** Outline density should match the duration heuristics above.

Open and close the deck with established patterns:
- First slide: `title` (cover with logo).
- Optional second slide: `agenda` (only for talks longer than ~10 min).
- Section dividers (`divider`) at every major topic shift — they let the speaker breathe and reset.
- Last slide: `cta` (QR placeholder + Hapoalim logo + thanks).
- For a 20-min+ talk, slot in at least one `quote` slide for a stat or external authority and one `divider` per ~5-7 content slides.

### Step 3: Implement the deck

1. **Clone the structural skeleton** from `index.html`: copy `<head>` (Heebo font, meta, CSS tokens, all `<style>` blocks), the body wrapper (`#progress-bar`, `#nav`, `#slide-container`, `#dot-nav`, `#kbd-hint`, footer), and the `<script>` tag (navigation handlers, video pause logic, fullscreen toggle, clicker support, swipe). Replace only the `#slide-container` contents with your new slides.

2. **Build slides one at a time**, choosing a `data-layout` value per slide (see `references/layouts.md`). Default to `split` (text right, visual left) for content-heavy slides. Use `centered` only for true break statements. Use `divider` for section transitions.

3. **For visuals, reuse one of the established idioms** (see `references/components.md`):
   - Hierarchy / 3-way relationship → trinity-circles or pyramid
   - Process / linear flow → process-flow or pipeline
   - Funnel / convergence → funnel-stage with hero number on top
   - Cycle / feedback loop → HITL-style center hub + satellites
   - Comparison / matrix → comp-table heatmap (red→yellow→green)
   - Retrospective → retro-dashboard 3-zone
   - Code / data context with motion → floating particles `.cc-pf`
   - Mockup → `.browser-frame`, `.mock-wa`, `.mock-cal`, `.mock-mail`

4. **Apply all hard rules** as you write — do not write violations and clean up later. See `references/rules.md` for the full list with rationale. The big six:
   - No em-dashes (—) or en-dashes (–) anywhere in user-facing text.
   - No middle dots (·) outside `<span class="slide-label">`.
   - No emojis in `<h1>`, `<h2>`, card titles, or `<button>`. Use SVG outline icons instead.
   - `<h1 class="slide-title">` and `<h2 class="slide-heading">` are white only.
   - Strict RTL: every card / list / panel needs `direction: rtl; text-align: right;`.
   - Icon-first cards use `flex-direction: row` (NOT `row-reverse`) with `direction: rtl`.

5. **Animate every slide.** Every visible element on every slide must have entry animation via `data-fx` attributes. A static slide is a defect, not a stylistic choice. The deck has a built-in motion library (`data-fx="fade-up"` is the workhorse; also `pop`, `fade`, `rise`, `tilt-in`, `stroke`). Combine with `data-fx-delay="N"` (ms) for sequencing, or wrap children in `data-fx-stagger="STEP" data-fx-stagger-delay="BASE"` for auto-staggered groups. Standard cadence per slide: slide-label at 0ms, heading at 120ms, accent-line at 220ms, body / intro at 320ms, lists or visuals at 440ms+, secondary blocks at 700ms+. See `references/components.md` (Animation patterns).

6. **When source material doesn't provide visuals, generate them yourself.** Don't fall back to plain text panels or sparse layouts because the user "didn't supply a screenshot". If a slide needs a brand row, produce SVG marks for the brands. If it needs a mockup, build it inline using `.browser-frame` / `.mock-wa` / `.md-card`. If it needs an architecture diagram, draw it in SVG with the existing filter library (`#oneon`, `#pyrGlow`, `#lglow`). The deck's visual coherence depends on every slide carrying its weight visually.

7. **UX sizing rule.** The visual should carry the slide's emotional weight, not the text. When the visual side feels empty, enrich it (more elements, more motion, more SVG detail) before tightening the text. When the text side feels cramped, weight the visual column with `flex: 1.3-1.4` to give the text breathing room. Typography stays on scale (see Design tokens) — solve density problems with layout, not by shrinking fonts.

8. **After each slide is added**, mentally check that the dot indicators still align and the keyboard hint remains visible.

### Step 4: Speaker-notes companion (default on)

Build `<slug>-notes.html` mirroring the existing `speaker-notes.html` structure. See `references/speaker-notes.md`.

**Two parts to ship by default:**

1. **The HTML companion** — one section per slide with tag, title, accent line, duration pill, narration body. Audio decoupled from navigation.

2. **Slide thumbnails** — run `scripts/capture-thumbnails.py` after the deck is built. It launches headless Chromium, freezes animations, walks each slide, and saves a 1600×900 PNG to `img/slides/<slug>-NN.png`. The companion `<img class="thumb">` tags reference these images. **Do NOT skip this step** — the speaker uses the thumbnails to navigate the talk on their phone, and broken-image icons make the companion unusable on stage.

   ```bash
   .venv-screenshot/bin/python scripts/capture-thumbnails.py <deck>.html <slide-count> <slug>
   ```

   If the venv doesn't exist, create it first: `python3 -m venv .venv-screenshot && .venv-screenshot/bin/pip install playwright && .venv-screenshot/bin/python -m playwright install chromium`. The capture script bypasses `goTo()` and toggles `.active` directly, so transitions don't race with screenshots.

**Default for audio: NO.** Audio pipeline is opt-in (Step 5). The play button reads "אין הקלטה עדיין" or is hidden.

### Build pipeline (always use)

The assembly script `_build-deck.py` combines `index.html` skeleton + `_new-slides.html` into the final deck. It also patches JS constants (VIDEO/GURU_SLIDE, SLIDE_TITLES, BONUS_SLIDES) and injects a `<style>` override block for projection-readable text and orphan prevention. **Always use the build pipeline** — editing the output HTML directly means changes get lost on the next rebuild.

After any change to `_new-slides.html`:
1. `python3 _build-deck.py`
2. `.venv-screenshot/bin/python scripts/capture-thumbnails.py <deck>.html <N> <slug>`
3. Read each thumbnail to verify before declaring done.

### Step 5: Audio pipeline (opt-in only)

Run only when the user explicitly says "generate the narration", "make the audio", "run TTS", or similar. See `references/audio-pipeline.md`. Requires `ELEVENLABS_API_KEY`.

## Hard rules (project invariants, non-negotiable)

These rules have been hardened over many iterations of the example deck. Apply them to every new deck. Full list with rationale in `references/rules.md`. Top rules:

1. **No em-dashes or en-dashes** in user-facing copy. Use commas, colons, parentheses, or split the sentence.
2. **No middle dots (·)** outside `<span class="slide-label">`.
3. **No emojis in headings or buttons.** Use SVG outline icons (stroke 1.4-1.6, no fill, round caps) inside red-tinted square containers (`background: rgba(255,32,32,0.12)`, `border-radius: 7-8px`).
4. **`slide-title` and `slide-heading` are white only.** Do not wrap any portion in red `<span>`. Red is reserved for `slide-label`, accent lines, body neon-stress, hero numbers, links, and decorative backgrounds.
5. **Strict RTL throughout.** `<html dir="rtl">`. Every card / list / panel / mockup needs `direction: rtl; text-align: right;`.
6. **Nav arrow direction.** `prev-btn` (right side) shows `›`, `next-btn` (left side) shows `‹`. Both buttons need `direction: ltr; unicode-bidi: isolate;`. Keyboard mapping is the inverse: `→` = prev, `←` = next.

7. **Every slide animates.** Every visible element gets a `data-fx` attribute (typically `fade-up`) with a staggered `data-fx-delay`. Static slides feel dead. Use `data-fx-stagger` on lists and grids so children enter sequentially.

8. **Generate visuals when not supplied.** If the source brief lacks media, build the visual yourself in SVG / HTML rather than degrade to plain text. The deck's visual coherence depends on every slide carrying weight.

## Design tokens (do not redefine)

CSS custom properties already live at the top of `<style>` in `index.html`:

| Token | Value | Use |
|---|---|---|
| `--bg` | `#111111` | dark background |
| `--accent` | `#FF2020` | neon red, primary |
| `--accent-light` | `#FF6060` | brighter red |
| `--accent-glow` / `--accent-glow2` | red rgba layers | text-shadow / box-shadow neon |
| `--text-1/2/3` | white → light gray → mid gray | typography hierarchy |
| `--border` / `--border-h` | subtle / red hover | card borders |

Font: **Heebo** (300-800) loaded from Google Fonts. Body has a faint red grid background; each slide layers a radial-gradient red glow. Reuse, do not redefine.

Typography scale (clamp values inherit from the existing deck):
- Body text: `clamp(0.78rem, 1.15vw, 0.9rem)`
- Card titles: `clamp(0.85rem, 1.2vw, 1rem)`
- Card descriptions: `clamp(0.7rem, 1vw, 0.85rem)`

Don't introduce arbitrary `font-size: 12px`.

## Layouts (`data-layout` values)

Brief summary; full guidance in `references/layouts.md`.

| Layout | When to use |
|---|---|
| `title` | Cover. Logo bottom-center. `nowrap` headline. |
| `centered` | Single hero / break statement. Use sparingly. |
| `split` | **Workhorse.** Text right, visual left. |
| `divider` | Section opener with big translucent text background. |
| `quote` | Source statistic with `<mark>` highlights and a link button. |
| `cta` | Final QR + logo. |
| `agenda` `cards` `cards2` `tri-card` `timeline` `process` `team` `content` `demo` `video` `about` `guru` | Already defined; reuse rather than invent new layouts. |

## Component catalogue (high level)

The deck has 80+ component classes. Always check `index.html` first. Common ones (full list in `references/components.md`):

- `.browser-frame` (Mac-style window for screenshots, dashboards, mockups)
- `.tri-card` (glassmorphism with `blue|purple|green` accent stripe)
- `.bullet-list.bullet-stacked` (title-on-top bullets, dot anchored to right edge)
- `.highlight-box` (red-bordered call-out, RTL)
- `.process-flow` `.pipeline` `.timeline` `.trinity-circles` `.hitl-stage` `.cmd-stage` `.pyramid-stage` `.funnel-stage`
- `.comp-table` with `.c-30 ... .c-90` heatmap cells
- `.retro-dashboard` (3-zone retrospective, green/yellow/red)
- `.mock-wa` `.mock-cal` `.mock-mail` (animated mockups)
- `.tc-resp-card` `.tc-mini` (responsibility cards)
- `.md-card` (SKILL.md / YAML mock with file tab + body + Hebrew summary)
- `.day-stat` `.pyramid-stat` `.funnel-hero` (stat blocks)

## Navigation contract

Already implemented in the `<script>` block of `index.html` — copy as-is for new decks. Key bindings and behaviours:

- Right-side button + `→` + `PageUp` + `Backspace` → `goPrev()` (RTL: right = backwards).
- Left-side button + `←` + `Space` + `PageDown` + `Enter` → `goNext()`.
- Touch swipe with 60px threshold.
- Dot indicators: active dot widens and shows the slide number.
- Top progress bar (`#progress-bar`) animates with the red gradient.
- `#kbd-hint` bottom-right shows `← → Space` keys faintly.
- Disable `prev` on slide 0, `next` on the last slide.
- Fullscreen toggle (F key + bottom-left button).
- Presentation clicker support.
- For `<video>` and sound elements: pause + reset on slide leave at the **top of `goTo()`**, before the 520ms animation timeout. Audio bleeding into the next slide is the bug to avoid.

## Media handling

If a slide includes `<video>` or sound:
- Set a `userHasInteracted` flag on the first document `click` so autoplay-with-sound is allowed afterwards.
- On entering the video slide: `slideVideo.currentTime = 0; slideVideo.play().catch(() => {})`.
- On leaving (in `goTo()`, **before** the 520ms timeout): pause + reset `currentTime` to 0.
- Same hook is wired for `guruSound`. Any new sound effect needs the same hook.

## Asset paths

- Hebrew filenames are fine: `img/לוגו.png`, `img/גורו.png`, etc.
- Logo path is `img/לוגו.png` with `filter: brightness(0) invert(1);`. Default height 83px on cover and CTA.
- HEIC → JPG conversion (the user often drops `.heic` from iPhone Photos):
  ```bash
  sips -s format jpeg "img/<name>.heic" --out "img/<slug>.jpg" --resampleWidth 600
  ```
  Resample large PNGs (Gemini-generated 2048×2048) to ~800px width.
- White background → transparent: convert via Python Pillow (replace near-white pixels with alpha 0). `mix-blend-mode` does not fully erase white on a near-black page.

## Pre-deploy QA checklist

Before declaring a deck done, run through this list:

- [ ] Click through every slide — no overlap, clipping, or horizontal scrollbar.
- [ ] Progress bar reaches 100% on the final slide.
- [ ] Every `<video>` / `<audio>` pauses immediately on slide leave (no audio bleed).
- [ ] `grep -nE "—|–" <deck>.html` returns 0 user-facing matches.
- [ ] Middle dots `·` exist only inside `<span class="slide-label">`.
- [ ] No emojis in any `<h1>`, `<h2>`, or `<button>`.
- [ ] `slide-title` and `slide-heading` contain no inner red `<span>`.
- [ ] All cards have `direction: rtl; text-align: right;`.
- [ ] Keyboard navigation works: `→` `←` `Space`.
- [ ] Logo on cover and CTA renders white at `height: 83px`.
- [ ] Media files referenced exist in `img/` / `vid/` / `sound/`.

## File outputs

- `<slug>.html` — single file, all CSS + JS inline. Default to a kebab-case slug of the topic; do not overwrite the existing `index.html` unless asked.
- `<slug>-notes.html` — companion, single file, references shared `audio/narration.mp3` only if the user has opted into the audio pipeline.

Do not introduce a build step, `package.json`, or external CSS files. The "open file in browser" simplicity is a hard project constraint.

## When in doubt

If the user describes a new diagram, scan whether one of the established idioms fits before designing from scratch. If they ask for a relative resize ("20% bigger"), apply the change consistently to all related properties (`max-width`, `font-size` clamp values, `padding`, `gap`) — not just one. If they say "תוריד את האימוג'י", replace the emoji with an SVG outline icon in a red-tinted square. If they say "שנה לבן", remove every red color reference inside that heading (inner `<span>`, inline `style`, `text-shadow`).

Consistency over locality: if the user changes one card, apply the same change to peer cards in the same slide and similar cards in sibling slides where it makes sense.
