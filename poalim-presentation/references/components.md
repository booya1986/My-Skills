# Component Catalogue — Poalim Presentation

The existing `index.html` defines 80+ component classes. This file is a quick lookup. The canonical implementation is the file itself — open it and scan when you need a working markup example.

## How to find a component

Don't trust this catalogue blindly — verify the markup by searching `index.html`:

```bash
grep -n 'class="<component-name>"' index.html | head
```

When the user describes a new visual, scan whether one of these idioms fits before designing from scratch.

## New visual idioms (from iteration)

### Playbook / designed document
When the slide shows a document or package (e.g., an onboarding guide), render it as a layered document card with a paper-stack effect — NOT as a plain md-card. Structure:

- 2-3 absolutely-offset divs behind the main card to suggest a stack of pages
- A gradient header with a document icon, title, and label
- A table-of-contents body with numbered chapters + page numbers + dotted leaders
- A footer bar with attribution and a punchy label

The paper-stack effect uses `position:absolute; top:Npx; right:-Npx; left:Npx; bottom:-Npx` on sibling divs behind the main card.

### Role / position profile card
When the slide defines a job role or position, render it as a structured role card — NOT as a markdown file mock. Structure:

- A gradient header with an avatar icon, role title, department/context
- Sections with small all-caps labels ("מה תעשי", "יעדי 90 הימים", "את לא לבד")
- A checklist with small styled checkbox squares (red-tinted, SVG check icon)
- A footer row with a team / buddy reference

### Three-zone complexity visual (green / yellow / red)
When the slide explains a spectrum from "easy" to "hard" or "safe" to "risky", use three vertically-stacked zone cards instead of a table or bullet list. Each zone has:

- A colored border + background tint (green = easy/safe, yellow = caution, red = danger/not alone)
- A circle icon appropriate to the zone (checkmark / warning triangle / info circle)
- A bold label and subtitle
- A pill badge on the right (e.g., "Vibe Coding", "בזהירות", "לא לבד")

Use `data-fx-stagger` on the parent so zones enter one after another.

### `md-card` — when to use vs when to avoid
Use `.md-card` when the slide concept is "a code/markdown file". Do NOT use it when the concept is "a real designed document" — in that case use the Playbook visual above. Do NOT use it when the concept is "a role or job description" — in that case use the Role card above.

## Frame components

### `.browser-frame`
A Mac-style window with title bar (red/yellow/green dots) wrapping any content. Used for video, dashboards, mockups, exam UI screenshots.

```html
<div class="browser-frame">
  <div class="browser-bar">
    <span class="dot red"></span><span class="dot yellow"></span><span class="dot green"></span>
    <span class="browser-url">app.example.co.il</span>
  </div>
  <div class="browser-content">
    <!-- inner content stays RTL: direction: rtl; text-align: right; -->
  </div>
</div>
```

### `.terminal-frame`
Black frame with monospace text, used for command-line demos.

### `.lms-frame`
Bank Hapoalim LMS look-alike for training mockups.

## Card families

### `.tri-card`
Glassmorphism card with a colored accent stripe. Three colors: `blue`, `purple`, `green`. Usually used in groups of 3 in a `.tri-card-grid`.

```html
<div class="tri-card-grid">
  <div class="tri-card blue">
    <div class="tri-card-icon"><!-- SVG outline icon --></div>
    <h3 class="tri-card-title">כותרת הקונספט</h3>
    <p class="tri-card-desc">תיאור קצר ומסביר</p>
  </div>
  <div class="tri-card purple">...</div>
  <div class="tri-card green">...</div>
</div>
```

### `.tc-resp-card` / `.tc-mini`
Responsibility cards used in "trinity-circles" trio (e.g., Campus / מנהלים / Trainees). The mini variant fits 3-up in a row.

### `.exam-section`
Numbered phase card with title + bullets. Used to show "phases of an exam" or "stages of a project".

```html
<div class="exam-section">
  <span class="exam-num">01</span>
  <h3 class="exam-title">שלב הראשון</h3>
  <ul class="bullet-list bullet-stacked">
    <li>...</li>
  </ul>
</div>
```

### `.md-card`
SKILL.md / YAML document mock with a file tab on top, YAML/Markdown body, and Hebrew summary at the bottom (`.md-summary`).

## Bullets & call-outs

### `.bullet-list`
Standard bullet list. Default is inline-style (title and description on one line).

### `.bullet-list.bullet-stacked`
Stacked variant — title on top, description below. The dot is `position: absolute; right: 0;` so it stays anchored regardless of title length.

```html
<ul class="bullet-list bullet-stacked">
  <li>
    <span class="b-title">כותרת הנקודה</span>
    <span class="b-desc">תיאור הנקודה, לרוב משפט אחד או שניים</span>
  </li>
</ul>
```

### `.highlight-box`
Red-bordered call-out for emphasis. RTL by default.

```html
<div class="highlight-box">
  <strong>נקודה חשובה:</strong> תוכן ההדגשה
</div>
```

## Diagrams & full-slide visuals

### `.process-flow` / `.pipeline`
4-cell horizontal flow. The last cell can be `pf-highlight` with `flex: 1.6`, red border, inner glow, and a different content tone — use it to land the takeaway.

### `.timeline`
Horizontal or vertical time-anchored events.

### `.trinity-circles`
3 SVG circles at corners + animated dashed `tc-arrow-path` arcs between them. Used for the "Holy Trinity" stakeholder pattern.

### `.hitl-stage` (Human In The Loop)
Center hub circle + 3 satellite circles + animated arrows between them.

### `.cmd-stage`
Cycle / feedback loop visualization.

### `.pyramid-stage`
SVG `<path>` polygons with `linearGradient` red→transparent, glow filter, icons aligned to each tier with dashed connector lines.

### `.funnel-stage` / `.funnel-hero`
Top dot cloud (CSS repeating `radial-gradient`) → hero number → SVG funnel with brain icon → animated bar chart.

### `.comp-table`
Comparison heatmap. Cell classes `c-30` `c-40` `c-50` `c-60` `c-70` `c-80` `c-90` provide a red→yellow→green color gradient.

```html
<table class="comp-table">
  <thead>
    <tr><th></th><th>אופציה א</th><th>אופציה ב</th><th>אופציה ג</th></tr>
  </thead>
  <tbody>
    <tr>
      <th>קריטריון 1</th>
      <td class="c-30">נמוך</td>
      <td class="c-70">בינוני</td>
      <td class="c-90">גבוה</td>
    </tr>
  </tbody>
</table>
```

### `.retro-dashboard`
3 stacked colored zones (green / yellow / red) with badge + number + icon row. Used for retrospectives.

### `.cc-pf` (floating particles)
Decorative animated dots that drift in the background. Use for hero scenes with code/data context. Keyframe: `cc-pf-drift`.

## Stat blocks

### `.day-stat` / `.pyramid-stat` / `.funnel-hero`
Big-number displays. Hero number is sized `clamp(3rem, 8vw, 5rem)` with red glow.

```html
<div class="day-stat">
  <div class="day-stat-num">120+</div>
  <div class="day-stat-label">שאלות במבחן</div>
</div>
```

## Animated mockups

### `.mock-wa` (WhatsApp)
Animated WhatsApp chat. Bubbles enter via `bubble-in` keyframe with staggered `animation-delay`.

### `.mock-cal` (Calendar)
Calendar mockup with `cal-pulse` animation on the selected date.

### `.mock-mail` (Email inbox)
Inbox mockup with shimmer animation on the highlighted row.

## Decorative & background

- Body has a faint red grid background pattern (CSS gradient).
- Each `.slide` adds a `radial-gradient` red glow.
- `.title-caret` is the animated red caret on the cover.
- `.accent-line` is a 60-80px red horizontal line under the headline.

## SVG filter library

The deck defines these reusable SVG filters in a hidden `<defs>`:

- `id="oneon"` — small neon glow
- `id="hitlGlow"` — HITL diagram glow
- `id="pyrGlow"` — pyramid glow
- `id="cmdGlow"` — command stage glow
- `id="lglow"` — large neon glow
- `id="neon"` — generic neon

Reference them in any `<svg>` via `filter="url(#oneon)"`. Don't define new Gaussian blur filters; reuse these.

## Animation keyframes

Existing keyframes near each component's CSS:

| Keyframe | Use |
|---|---|
| `cc-typing-bounce` | bounce on mascot/character images |
| `arrow-flow` | dashed line flowing along an SVG path |
| `ring-pulse` | neon glow pulse on circles |
| `bubble-in` | chat bubble entry |
| `progress-shimmer` | progress bar pulsing |
| `bar-rise` | bars rising into place |
| `cc-pf-drift` | floating decorative particles |
| `cal-pulse` | calendar selected date pulse |
| `banner-shine` | banner sweep highlight |
| `selected-pulse` | selection ring pulse |
| `timer-blink` | countdown timer blink |
| `cc-blink` | character/cursor blink |

**Always stagger `animation-delay`** so elements enter in sequence (0.3s, 1.5s, 2.7s — not all at once).

## SVG icons

Icons are inline `<svg>` outlines. Spec:
- `viewBox="0 0 24 24"` (most common)
- `fill="none"`
- `stroke="currentColor"` (inherits from `color`)
- `stroke-width="1.4"` to `1.6`
- `stroke-linecap="round"` `stroke-linejoin="round"`

Wrap them in a red-tinted square container:

```html
<div class="icon-box">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <!-- paths -->
  </svg>
</div>
```

```css
.icon-box {
  width: 32px; height: 32px;
  background: rgba(255, 32, 32, 0.12);
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
```

The existing deck has 80+ inline SVG icons. Search before drawing new ones:

```bash
grep -n '<svg' index.html | head -20
```

## Animation patterns (`data-fx`, `data-fx-stagger`)

Every slide must animate. The deck has a built-in motion library implemented in CSS + a small JS helper. Don't write custom keyframes for slide entry; use the existing system.

### `data-fx` values (entry animation on individual elements)

| Value | Effect | Use for |
|---|---|---|
| `fade-up` | fade in + translate up 18px | the workhorse. 80%+ of elements. |
| `fade` | opacity only | when you don't want positional motion (e.g., backgrounds). |
| `pop` | scale 0.92 → 1, springy easing | hero numbers, badges, stat blocks |
| `rise` | scaleY 0.4 → 1 from bottom | pyramid, funnel, full-width visuals that "grow up" |
| `tilt-in` | rotate -3° + translateY 14px | playful elements (mascots, cards) |
| `stroke` | SVG stroke-dashoffset countdown | drawing in line graphs, paths, underlines |

Combine with `data-fx-delay="N"` (in ms) to sequence. Use `data-fx-len="...path-length..."` for stroke animations (pre-compute path length in code).

### Standard cadence per slide

```html
<span class="slide-label" data-fx="fade-up" data-fx-delay="0">…</span>
<h2 class="slide-heading" data-fx="fade-up" data-fx-delay="120">…</h2>
<div class="accent-line" data-fx="fade-up" data-fx-delay="220"></div>
<p class="slide-sub" data-fx="fade-up" data-fx-delay="320">…</p>
<ul class="bullet-list" data-fx-stagger="120" data-fx-stagger-delay="500">
  <li>…</li>
</ul>
<div class="highlight-box" data-fx="fade-up" data-fx-delay="900">…</div>
```

The visual half should also animate, with delays starting around 400-700ms so it lands shortly after the heading.

### `data-fx-stagger` (auto-stagger children)

Wrap a list, grid, or row of cards in a container with:

```html
<div data-fx-stagger="120" data-fx-stagger-delay="500">
  <div>…</div>
  <div>…</div>
  <div>…</div>
</div>
```

`data-fx-stagger="STEP_MS"` is the gap between children (default 90ms). `data-fx-stagger-delay="BASE_MS"` is when the first child starts. Children fade-up in sequence.

The JS function `applyStaggerDelays()` (already in `index.html`) walks the slide on entry and sets the `transition-delay` for each child. Don't replicate this manually.

### `data-fx-mark` (mark sweep)

Place on the slide root to trigger the hand-drawn marker sweep on `<mark>` tags inside (used on `quote` slides):

```html
<div class="slide" data-layout="quote" data-fx-mark>
  <p>…<mark>91%</mark>…</p>
</div>
```

### `data-count` (animated number countup)

```html
<span data-count data-target="91" data-format="percent">0%</span>
```

Formats: `percent`, `percent-range` (with `data-base`), `number`. The countup fires on slide entry via `playCountUps(slide)`.

### Continuous animations (CSS keyframes)

For continuous (not entry) animations on visuals: use the existing keyframes (`bubble-in`, `cal-pulse`, `bar-rise`, `arrow-flow`, `ring-pulse`, `cc-pf-drift`) listed in the keyframes table above. Apply via `animation: <name> <duration> <easing> [delay] [iteration-count];` directly on the element. **Stagger via `animation-delay`** so children enter in sequence.

### Generating brand / logo SVG marks

When the brief mentions brands without supplying logos (Lovable, Claude, Cursor, v0, Bolt, etc.), generate minimal abstract SVG marks rather than skipping the visual or using text. Pattern:

```html
<div class="brand-row" data-fx-stagger="100" data-fx-stagger-delay="400" style="display:flex;gap:1.2rem;align-items:center;justify-content:center;direction:rtl;">
  <div class="brand-mark" style="display:flex;flex-direction:column;align-items:center;gap:0.4rem;">
    <div style="width:46px;height:46px;border-radius:11px;background:rgba(255,32,32,0.1);border:1px solid rgba(255,32,32,0.35);display:flex;align-items:center;justify-content:center;">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="rgba(255,180,180,0.95)" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
        <!-- brand glyph -->
      </svg>
    </div>
    <span style="font-size:0.7rem;color:rgba(255,255,255,0.7);">Brand Name</span>
  </div>
  <!-- repeat for each brand -->
</div>
```

The square container, brand mark, and label form a unit; `data-fx-stagger` on the row makes them enter one by one.

### When the visual feels empty

Audit the visual column. If it's a single icon or a flat list, **enrich it** before iterating elsewhere:

- Add a secondary element below or beside (caption, badge, small chart, mini stat)
- Add motion to existing elements (`bubble-in` on chat bubbles, `arrow-flow` on connectors)
- Increase element density (3 cards instead of 1, 5 nodes instead of 3)
- Layer a backdrop (floating particles `.cc-pf`, soft red gradient blob)

Empty space is not minimalism — it's a slide that didn't finish.

## Centering SVG icons inside circles

Use `<g transform="translate(-X,-Y)">` to center 16×16 icons over a `<circle cx="0" cy="0">`. Verify the icon visually centers — don't trust the math alone; render and look.
