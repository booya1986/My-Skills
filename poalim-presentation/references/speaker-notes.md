# Speaker-Notes Companion — Poalim Presentation

`speaker-notes.html` is the speaker-prep companion: a mobile-first, one-slide-per-page reference the speaker uses to prep on their phone before the talk. It is a separate single HTML file served from the same directory as the deck.

## File output

Default name: `<slug>-notes.html` (matching the deck's slug). Default location: project root, same as the deck.

The existing `speaker-notes.html` is the canonical reference implementation — read it before building.

## Structure

```
<html dir="rtl">
  <head>
    <!-- same Heebo font, similar CSS tokens -->
  </head>
  <body>
    <header class="topbar">
      <button class="toc-toggle">≡</button>
      <span class="topbar-title">...</span>
    </header>
    <aside class="toc">...</aside>
    <div class="toc-back"></div>
    <main>
      <section class="slide" id="s01" data-num="1" data-title="...">...</section>
      <section class="slide" id="s02" data-num="2" data-title="...">...</section>
      <!-- one section per slide -->
    </main>
    <nav class="bottombar">
      <button class="toc-toggle">...</button>
      <button class="prev-btn">›</button>
      <button class="play-btn">▶</button>
      <button class="next-btn">‹</button>
    </nav>
    <audio id="narration" preload="metadata"></audio>
    <script>...</script>
  </body>
</html>
```

## Per-slide section structure

Each `<section class="slide">` is `100vh` with `scroll-snap-align: start`. Contents:

```html
<section class="slide" id="s05" data-num="5" data-title="הכותרת של השקף">
  <div class="slide-tag">מקרה בוחן</div>
  <div class="slide-num">05</div>
  <h2 class="slide-title">הכותרת של השקף</h2>
  <div class="accent-line"></div>
  <span class="duration-pill">2:30</span>
  <img class="thumb" src="img/slides/slide-05.png" alt="" />
  <div class="section">
    <p>פסקת קריינות ראשונה</p>
    <p>פסקת קריינות שנייה</p>
    <ul>
      <li>נקודה לתזכורת</li>
      <li>נקודה נוספת</li>
    </ul>
  </div>
</section>
```

**Important:** the existing companion was deliberately stripped of meta sections (mood, tone, anecdote, avoid). Each slide has only the **קריינות** (narration) inside `<div class="section">`. Do NOT re-introduce per-slide play buttons, `tip` / `warn` / `bad` section variants, or stage-direction sub-sections — they were explicitly removed.

If the user asks for additional context per slide (e.g., "what to remember"), fold it into the narration paragraphs themselves rather than adding a separate section type.

## Thumbnails (REQUIRED — default companion ships with them)

Each slide section references a thumbnail image at `img/slides/<slug>-NN.png` (where `NN` is zero-padded, e.g., `preboarding-01.png`, `preboarding-12.png`). Default size is 1600×900.

**Thumbnails are not optional.** The speaker reads the companion on a phone before the talk; without thumbnails, every section shows a broken-image icon and the speaker cannot quickly recall which slide is which. Always generate them as part of the companion build.

### Generating thumbnails

Use `scripts/capture-thumbnails.py` (Playwright-based, headless Chromium):

```bash
.venv-screenshot/bin/python scripts/capture-thumbnails.py <deck>.html <slide-count> <slug>
```

For example:

```bash
.venv-screenshot/bin/python scripts/capture-thumbnails.py pre-boarding-vibe-coding.html 16 preboarding
```

This produces `img/slides/preboarding-01.png` through `img/slides/preboarding-16.png`.

### How the script works

The capture script:
1. Launches headless Chromium at 1600×900.
2. Loads the deck via `file://` URL.
3. Injects a CSS override that zeroes out animation and transition durations.
4. For each slide index `i`, **directly manipulates the DOM** rather than calling `goTo()`: it removes `.active` / `.fx-play` / `.exit-*` from every slide, adds `.active` and `.fx-play` to slide `i`, and re-runs `applyStaggerDelays` and `playCountUps` on it.
5. Waits ~250ms for layout to settle.
6. Screenshots to `img/slides/<slug>-NN.png`.

The DOM-manipulation approach (vs calling `goTo(i)`) avoids a race condition where the transition machinery's `requestAnimationFrame` callbacks fight with the animation freeze and produce duplicate screenshots.

### Setting up the screenshot venv (one-time)

If `.venv-screenshot/` doesn't exist:

```bash
python3 -m venv .venv-screenshot
.venv-screenshot/bin/pip install playwright
.venv-screenshot/bin/python -m playwright install chromium
```

The venv is gitignored (it's tooling, not project code).

### When to regenerate

Regenerate thumbnails any time the deck's slide content, layout, or order changes meaningfully. Small text edits don't require a fresh capture; structural or visual changes do.

### Filename convention

Use the same kebab-case slug as the deck filename. Example: deck `pre-boarding-vibe-coding.html` → thumbnails `img/slides/preboarding-NN.png` (note the abbreviated slug for image filenames if the deck slug is long; just be consistent within a deliverable).

## TOC drawer

The TOC slides in from the left (RTL-natural):

```css
.toc { left: -100%; transition: left 0.3s; }
.toc.open { left: 0; }
.toc-back { display: none; }
.toc-back.show { display: block; }
```

The TOC lists each slide with its number and title. Clicking an entry scrolls to that slide. **Clicking a TOC entry does NOT pause or restart audio** (see "Audio decoupling" below).

## Bottom navigation

Bottom-right to bottom-left (RTL): TOC toggle, prev (`›`), title + slide-num display, **play button**, next (`‹`).

Keyboard mapping is identical to `index.html`:
- `→` = prev (RTL: right = backwards)
- `←` = next
- `Space` = next

Navigation chevrons need `direction: ltr; unicode-bidi: isolate;` so the RTL document doesn't flip the glyphs.

## Audio decoupling (critical)

This is the design decision the user explicitly requested:

- **One global `<audio>` element** loads `audio/narration.mp3` (the single concatenated file).
- **A single play button** toggles play/pause.
- **Slide navigation does NOT affect audio.** Swiping, arrow keys, prev/next buttons, and TOC clicks all change the visible slide without pausing or restarting playback.
- **Audio does NOT auto-advance slides.** Even when the audio progresses past a slide's duration, the visible slide stays put.
- While playing, the play button shows elapsed time (`m:ss`) instead of a play icon.
- A `tts-status` line in the TOC drawer reflects load state (HEAD request to `audio/narration.mp3` to check existence).

The decoupling is intentional: the speaker may want to scrub forward in audio while reading slide 3 to plan ahead, or may want to read slide 5 silently to check details — both flows must work.

## When audio is not yet generated

By default, the audio pipeline is opt-in. When generating the companion without audio:

- Leave `<audio id="narration" src="audio/narration.mp3" preload="metadata"></audio>` in the markup, but the file doesn't exist yet.
- The play button can be rendered disabled with a "no audio yet" tooltip.
- The `tts-status` text reads "אין הקלטה עדיין" or similar.
- When the user later runs the audio pipeline (see `audio-pipeline.md`), the file appears at `audio/narration.mp3` and the companion picks it up automatically on the next load.

## Mobile-first CSS hints

The companion is read on phones. Ensure:
- Each slide section is `min-height: 100vh` with `scroll-snap-align: start` on the parent.
- Body has `scroll-snap-type: y mandatory`.
- Narration text is large enough for phone reading: `font-size: clamp(0.95rem, 1.2vw, 1.05rem)`, `line-height: 1.65`.
- Bottom nav has `position: fixed; bottom: 0;` with safe-area padding.
- The TOC drawer covers the screen on mobile (full width), partial on desktop.

## Putting it together — minimal example

```html
<section class="slide" id="s01" data-num="1" data-title="פתיחה">
  <div class="slide-tag">פתיחה</div>
  <div class="slide-num">01</div>
  <h2 class="slide-title">פתיחה</h2>
  <div class="accent-line"></div>
  <span class="duration-pill">1:00</span>
  <img class="thumb" src="img/slides/slide-01.png" alt="" />
  <div class="section">
    <p>שלום לכולם, ברוכים הבאים. אני אבי לוי, ראש האקדמיה ב...</p>
    <p>היום נדבר על שלוש שאלות מרכזיות.</p>
  </div>
</section>
```

When the user asks to update narration, edit only the `<p>` and `<li>` content inside `<div class="section">` blocks. Don't touch the metadata at the top of the section (tag, num, title, accent line, duration pill, thumbnail).
