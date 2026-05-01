# Layouts (`data-layout` values) — Poalim Presentation

Each `<div class="slide">` carries a `data-layout="..."` attribute that selects layout-specific CSS. The full set of supported values exists in `index.html`. Below is a quick lookup. Reuse, don't invent.

## When to pick which

| Layout | Purpose | Typical content |
|---|---|---|
| `title` | Cover. First slide. | Slide-label, big headline (nowrap), accent line, subtitle, logo. |
| `agenda` | Optional second slide for talks > 10 min. | Numbered or bulleted topic list. |
| `divider` | Section opener — pause and reset for the speaker. | Big translucent text background ("USE CASE", "01"), slide-label, headline, accent line. |
| `split` | **Workhorse content slide.** Most slides should use this. | Text right (slide-label, heading, accent line, bullets), visual left (any of the established idioms). |
| `centered` | Single hero / break statement. Use sparingly — too many in a row feels lazy. | One headline, one supporting line. |
| `quote` | Source statistic with `<mark>` highlights and a link button. | Big stat or quote, source name, link. |
| `tri-card` | 3-column card row. | 3 parallel concepts with title + description. |
| `cards` / `cards2` | 4-6 card grid. | Catalogue-style content. |
| `team` | Speaker / team intro. | Photo cards in a row. |
| `process` | Pipeline / sequence visualization. | Process-flow stages. |
| `timeline` | Time-anchored events. | Horizontal or vertical timeline. |
| `content` | Generic content slide (less constrained than `split`). | Free composition; use only when split doesn't fit. |
| `demo` | Live demo placeholder. | Mockup or screenshot. |
| `video` | Embedded `<video>`. | Browser-frame wrapping a video element. |
| `guru` | Special "guru" character intro. | Mascot image + framing line. |
| `about` | About-the-speaker slide. | Bio card + photo. |
| `cta` | Final slide. | QR placeholder (black background, neon-red outline) + Hapoalim logo + thanks. |

## Layout structure cheatsheet

### `title` (cover)

```html
<div class="slide active" data-layout="title">
  <span class="slide-label" data-fx="fade-up" data-fx-delay="0">Meetup · Event · Year</span>
  <h1 class="slide-title" data-fx="fade-up" data-fx-delay="120">
    הכותרת הראשית של המצגת
    <span class="title-caret" aria-hidden="true"></span>
  </h1>
  <div class="accent-line" data-fx="fade-up" data-fx-delay="220"></div>
  <p class="slide-sub" data-fx="fade-up" data-fx-delay="320">תת-כותרת מסבירה</p>
  <div style="position:absolute;bottom:12%;left:0;right:0;display:flex;justify-content:center;align-items:center;" data-fx="pop" data-fx-delay="600">
    <img src="img/לוגו.png" alt="Bank Hapoalim" style="height:83px;width:auto;filter:brightness(0) invert(1);opacity:0.92;" />
  </div>
</div>
```

- `<h1 class="slide-title">` uses `white-space: nowrap`.
- The logo is the only visual on the cover. Default height 83px.
- The animated red caret (`.title-caret`) provides motion without competing with the headline.
- **Do NOT use `<div class="logo-wrap">` on the cover slide.** The `.logo-wrap` stylesheet rule is `left:50%; transform:translateX(-50%)` which conflicts with RTL and causes the animation to drift from the left. Use a plain `<div>` with fully inline positioning: `position:absolute; bottom:12%; left:0; right:0; display:flex; justify-content:center;`. Use `data-fx="pop"` (not `fade`) so the logo scales in from the element's own center with no lateral movement.

### `divider` (section opener)

```html
<div class="slide" data-layout="divider">
  <div class="part-text-bg">USE CASE</div>
  <div class="part-label">
    <span class="slide-label" data-fx="fade-up" data-fx-delay="200">מקרה בוחן</span>
    <h1 class="slide-title" data-fx="fade-up" data-fx-delay="320" style="text-align:center;text-wrap:balance;">כותרת המקטע</h1>
    <div class="accent-line" data-fx="fade-up" data-fx-delay="440"></div>
    <p class="slide-sub" data-fx="fade-up" data-fx-delay="560" style="text-align:center;text-wrap:balance;max-width:640px;">תת-כותרת המקטע</p>
  </div>
</div>
```

**Critical:** use `class="part-label"` (NOT `divider-content`). The CSS for `.part-label` provides `display:flex; flex-direction:column; align-items:center; text-align:center;`. Any other class name you invent will have no CSS, and in an RTL document the text will default to right-aligned instead of centered.

The huge translucent `part-text-bg` text sits behind the headline as a watermark. Stagger delays so the slide-label, headline, accent-line, and subtitle enter in sequence.

### `split` (workhorse — text right, visual left)

```html
<div class="slide" data-layout="split">
  <div class="split-text">
    <span class="slide-label">תווית עליון</span>
    <h2 class="slide-heading">הכותרת של השקף</h2>
    <div class="accent-line"></div>
    <ul class="bullet-list bullet-stacked">
      <li>
        <span class="b-title">כותרת הנקודה</span>
        <span class="b-desc">תיאור קצר ומסביר</span>
      </li>
      <!-- more <li> ... -->
    </ul>
    <div class="highlight-box">
      <!-- optional call-out -->
    </div>
  </div>
  <div class="split-visual">
    <!-- one of the visual idioms: trinity-circles, process-flow, browser-frame, etc. -->
  </div>
</div>
```

- Text is on the right (RTL-natural reading order).
- `flex: 1` on `.split-text`, `flex: 1.3` or `1.4` on `.split-visual` when the user asks for "more space for the visual".
- Bullets stacked, not inline (see `references/rules.md` rule 12).

### `quote` (source statistic)

```html
<div class="slide" data-layout="quote" data-fx-mark>
  <span class="slide-label">McKinsey · 2026</span>
  <blockquote>
    <p>הסטטיסטיקה החשובה כאן עם <mark>הדגשה</mark> על המספר הקריטי</p>
  </blockquote>
  <a class="quote-link" href="https://..." target="_blank">קרא עוד</a>
</div>
```

The `data-fx-mark` attribute triggers the hand-drawn marker sweep on the `<mark>` element.

### `cta` (final slide)

```html
<div class="slide" data-layout="cta" style="justify-content:center;gap:0;">
  <h1 class="slide-title" style="text-align:center;" data-fx="fade-up" data-fx-delay="0">תודה</h1>
  <div class="accent-line" style="margin-left:auto;margin-right:auto;" data-fx="fade-up" data-fx-delay="220"></div>
  <p class="slide-sub" style="max-width:30rem;text-align:center;margin-top:0.6rem;" data-fx="fade-up" data-fx-delay="320">תת-כותרת מסבירה</p>
  <div data-fx="pop" data-fx-delay="500" style="margin-top:1.4rem;width:190px;height:190px;background:#000;border:2px solid var(--accent);border-radius:14px;display:flex;align-items:center;justify-content:center;color:rgba(255,180,180,0.7);font-size:0.72rem;text-align:center;padding:0.8rem;box-shadow:0 0 32px rgba(255,32,32,0.28);">
    QR placeholder
  </div>
  <div data-fx="fade-up" data-fx-delay="800" style="margin-top:1.6rem;display:flex;justify-content:center;align-items:center;">
    <img src="img/לוגו.png" alt="Bank Hapoalim" style="height:83px;width:auto;filter:brightness(0) invert(1);opacity:0.92;" />
  </div>
</div>
```

**Critical — CTA logo**: do NOT use the `<div class="logo-wrap">` element on the CTA slide. Its CSS is `position:absolute; bottom:12%; left:50%;` which removes it from the flex flow and can conflict with flex-stacked content. Instead, wrap the `<img>` in a plain inline `<div>` with `display:flex;justify-content:center;` so it appears as a normal flex child below the QR block.

**Also critical — accent-line centering**: add `style="margin-left:auto;margin-right:auto;"` to the accent-line on the CTA slide, because the `data-layout="cta"` CSS uses `text-align:center` but the `.accent-line` has a fixed width that needs auto margins to center.

### `centered` (break statement)

```html
<div class="slide" data-layout="centered" style="overflow:hidden;justify-content:center;align-items:center;">
  <h1 class="slide-title">משפט-מפתח אחד</h1>
  <p class="slide-sub">תת-כותרת קצרה</p>
</div>
```

Use sparingly. Two `centered` slides in a row feel weak; alternate with content-rich layouts.

### `agenda`

```html
<div class="slide" data-layout="agenda">
  <h2 class="slide-heading">מה נדבר עליו</h2>
  <div class="accent-line"></div>
  <ol class="agenda-list">
    <li><span class="agenda-num">01</span> ...</li>
    <li><span class="agenda-num">02</span> ...</li>
    <!-- ... -->
  </ol>
</div>
```

Only emit an agenda slide for talks longer than ~10 min.

## Layout selection heuristics

When choosing a layout for a new slide:

1. **Is it a section opener?** → `divider`.
2. **Is it the cover or final slide?** → `title` or `cta`.
3. **Is it a one-liner break statement?** → `centered` (sparingly).
4. **Is it a sourced statistic or external quote?** → `quote`.
5. **Does it have a primary visual idea + supporting bullets?** → `split` (default).
6. **Is it a 3-way comparison?** → `tri-card`.
7. **Is it a 4-6 item catalogue?** → `cards` or `cards2`.
8. **Is it about people?** → `team`, `about`, `guru`.
9. **Is it a temporal sequence?** → `timeline` or `process`.

If none of these fit, the answer is almost certainly still `split` with a different visual on the left, not a new layout.

## Cover and CTA: bookends

Every deck opens with `title` and closes with `cta`. The slide-label register on the cover ("Meetup · Event · Year") and the QR block on the CTA establish the visual identity. Don't omit either.
