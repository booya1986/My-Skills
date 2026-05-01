# Hard Rules — Poalim Presentation

These rules are project invariants. Each is followed by the rationale so you can judge edge cases. None are stylistic preferences; every one was hardened after a recurring bug or a usability complaint.

## Text content

### 1. No em-dashes (—) or en-dashes (–) in user-facing text
Replace with `,`, `:`, parentheses, or split into separate phrases.

**Why:** the user reviewed the rehearsal-day deck and called every dash out by hand. They read as "AI-shaped" punctuation and break the conversational Hebrew register.

**How to apply:** when editing, audit the *entire file* with `grep -nE "—|–"`, not just the line you touched. Catch them at write time so cleanup passes are not needed.

### 2. No middle dots (·) outside `<span class="slide-label">`
The middle dot is allowed only inside the small uppercase red tag at the top of each slide.

**Why:** middle dots between Hebrew words look stylish in the slide-label ("שיחה · אסטרטגיה · ביצוע") but feel artificial inside body copy. Hebrew separates clauses with commas or colons, not dots.

**How to apply:** if you want to separate two Hebrew phrases inside body text or a card title, use a comma, a colon, or just whitespace. The dot belongs only in the label.

### 3. No emojis in `<h1>`, `<h2>`, card titles, or `<button>`
Use SVG outline icons inside red-tinted square containers instead.

**Icon spec:**
- `stroke-width: 1.4-1.6`
- `fill: none`
- `stroke-linecap: round; stroke-linejoin: round`
- Container: `background: rgba(255,32,32,0.12); border-radius: 7-8px;` 28-36px square

**Why:** emojis introduce a different visual register (color, fill, OS-specific rendering) that fights the deck's monochrome neon-red aesthetic. SVGs are crisp at any zoom and inherit `currentColor`.

**How to apply:** the existing `index.html` has 80+ inline SVG icons. Search for an analogous one before drawing a new icon.

**Tolerated exception:** decorative `.md-summary` lines (the small Hebrew summary at the bottom of `.md-card`) may use emojis sparingly.

### 4. Hard line breaks belong in CSS, not in copy
Don't insert `<br>` to fix wrapping.

**Why:** `<br>` couples the visual break to the markup, so resizing the viewport breaks the layout. CSS handles wrapping responsively.

**How to apply:** adjust `font-size` (clamp values), `max-width`, or `white-space: nowrap` instead.

## Heading & color

### 5. `<h1 class="slide-title">` and `<h2 class="slide-heading">` are white only
Do not wrap any portion in `<span style="color: var(--accent)">` or apply `text-shadow` with a red glow on the inner span.

**Why:** the user repeatedly asked for this. The accent red is reserved for: `slide-label`, `accent-line`, neon-stress on body text and `<strong>`, hero numbers, links, decorative backgrounds, and animated elements. If the heading itself is red, the rest of the visual hierarchy collapses.

**How to apply:** when the user says "שנה לבן" they mean: remove every red color reference inside the heading — inner `<span>`, inline `style="color:..."`, and `text-shadow`. Audit the whole heading, not just the visible word.

### 6. Cover/title slide title uses `white-space: nowrap`
Other slide headings may wrap.

**Why:** the cover headline anchors the visual identity of the deck. Wrapping looks weak at the moment of first impression.

**How to apply:** if a cover headline is too long to fit on one line at any viewport, edit the copy. Don't break the rule.

### 7. Slide-label is the only place red `·` separators are allowed
**Why:** see rule 2.

## RTL & alignment

### 8. Strict RTL throughout
`<html dir="rtl">`. Every card / list / panel needs `direction: rtl; text-align: right;`. Even mockups inside browser-frame, terminal, or LMS iframes stay RTL.

**Why:** the audience is Hebrew-reading. Mixing LTR and RTL within a slide creates jarring eye movement and breaks visual rhythm.

**How to apply:** when copying a card pattern from elsewhere, verify `direction` and `text-align` on the outermost container *and* on any nested list, table, or panel.

### 9. Icon-first cards: `flex-direction: row` (NOT `row-reverse`) with `direction: rtl`
This places the icon on the right edge, glued next to the title (the natural Hebrew reading order).

**Why:** `row-reverse` looks identical at first glance but breaks accessibility (screen readers traverse children in source order, not visual order) and re-flips when nested in another `direction: rtl` container. The user has called this out multiple times.

**How to apply:** when the user says "זה לא מיושר לימין", check first whether `row-reverse` is being used. Switch to `row` and verify.

### 10. Card titles always sit beside their icon on the right side
Never floating in a corner, never centered, never separated by a wide gap.

**How to apply:** the icon's container should have `flex-shrink: 0`, the title should sit immediately to its left in source order (which is right in RTL visually), and the gap should be `0.5-0.75rem`.

### 11. Navigation arrow direction is the RTL trap
- `prev-btn` (right side) shows `›` (right-pointing chevron — backwards in Hebrew).
- `next-btn` (left side) shows `‹` (left-pointing chevron — forwards in Hebrew).
- Both buttons need `direction: ltr; unicode-bidi: isolate;` so the RTL document doesn't flip the chevron itself.
- **Keyboard mapping is the inverse of intuition:** `→` = prev, `←` = next.

**Why:** in RTL the right side is "backwards in time". Without `unicode-bidi: isolate;` on the buttons, the document's RTL inverts the chevron glyph, producing the correct visual but with broken keyboard semantics.

## Bullets & lists

### 12. Bullets with title + description go stacked, not inline
Use `.bullet-list.bullet-stacked` with `<span class="b-title">` + `<span class="b-desc">`.

**Why:** inline bullets (`<strong>foo:</strong> bar`) crash visually when the title and description have different lengths. The stacked form lets each line breathe.

**How to apply:** the bullet dot is `position: absolute; right: 0;` — it stays anchored to the right edge regardless of title length. Inline bullets are only acceptable for short, single-line items.

## Logo, layout & sizing

### 13. Logo path and styling
Path: `img/לוגו.png`. Filter: `filter: brightness(0) invert(1);` to render it white. Default `height: 83px` (it lives in `.logo-wrap`). Same logo appears on the title slide and the CTA slide.

### 14. Default workhorse layout is `split` with text on the right and the visual on the left
When the user asks for "more space for the visual", weight via `flex: 1.3` / `flex: 1.4` on the visual column rather than inline `max-width`.

### 15. Relative resizing applies consistently to all related properties
When the user asks for "20% bigger" or "make it half", apply the change to `max-width`, `font-size` (both base and clamp values), `padding`, `gap`, and icon size. Don't scale only one and leave the others.

**Why:** scaling only one property creates visual incoherence (a card with bigger text but the same padding looks cramped; bigger padding with the same text looks empty).

### 16. Match the existing typography scale
New components inherit the typography scale:
- Body text: `clamp(0.78rem, 1.15vw, 0.9rem)`
- Card titles: `clamp(0.85rem, 1.2vw, 1rem)`
- Card descriptions: `clamp(0.7rem, 1vw, 0.85rem)`

Don't introduce arbitrary `font-size: 12px`.

## Animation, visuals, and UX

### 17. Projection text size: inject CSS overrides
The default `index.html` typography scale caps `b-title` at 0.98rem and `b-desc` at 0.88rem — too small for a projected screen viewed from several meters. Always inject a CSS override block via the build script:

```css
.bullet-stacked .b-title { font-size: clamp(1.02rem, 1.55vw, 1.18rem) !important; line-height: 1.35 !important; }
.bullet-stacked .b-desc  { font-size: clamp(0.88rem, 1.28vw, 1.0rem)  !important; line-height: 1.55 !important; }
.split-col > .slide-sub  { font-size: clamp(0.96rem, 1.4vw, 1.08rem)  !important; }
```

Add this to `_build-deck.py` as a string injected just before `</style>` in the output file.

### 18. Orphan prevention: `text-wrap: balance` globally
Single words left alone on the last line of any heading or paragraph look unprofessional on a projected slide. Add these rules to the CSS override block:

```css
h1.slide-title, h2.slide-heading { text-wrap: balance; }
.slide-sub { text-wrap: balance; }
.bullet-stacked .b-title, .bullet-stacked .b-desc { text-wrap: pretty; }
```

For specific troublesome phrases with English brand names that `text-wrap` can't rebalance (e.g. "Vibe Coding"), use `&nbsp;` between the words to prevent line breaks within a brand name, and `&#8209;` (non-breaking hyphen) for hyphenated English terms.

### 19. Every slide must animate
Every visible element on every slide carries a `data-fx` attribute with a staggered `data-fx-delay`. A static slide is a defect, not a stylistic choice.

**Why:** the deck has a built-in motion library (`data-fx="fade-up"`, `pop`, `fade`, `rise`, `tilt-in`, `stroke`) and a `.fx-play` class added on slide entry. Without `data-fx`, elements appear instantly and the slide feels dead. The motion is what makes the deck feel alive when projected.

**How to apply:** standard cadence per slide:

| Element | data-fx-delay |
|---|---|
| `slide-label` | `0` |
| `slide-title` / `slide-heading` | `120` |
| `accent-line` | `220` |
| Intro paragraph (`slide-sub`) | `320` |
| Bullet list / primary visual | `440-700` |
| Secondary blocks (highlight-box, link, footer) | `700-1500` |

For lists or grids, prefer `data-fx-stagger="120" data-fx-stagger-delay="500"` on the parent — the JS auto-applies sequential delays to the children. See `references/components.md` (Animation patterns) for snippets.

### 18. Generate visuals when source material doesn't supply them
If the brief lacks a screenshot, photo, or external diagram, **build the visual yourself in SVG, HTML, or via the existing component library**. Don't fall back to a flat text panel "because the user didn't provide media".

**Why:** the deck's visual coherence depends on every slide pulling its weight. A slide that says "Lovable, Claude, Cursor, v0, Bolt" in plain text reads as a list. A slide with five inline SVG brand marks animated in sequence reads as a story. The reader experience is defined by what you choose to draw, not by what was in the brief.

**How to apply:**
- Brands → inline SVG marks (a stylized C for Claude, a lightning bolt for Bolt, a heart for Lovable, etc.). Position them in a row with `data-fx-stagger`.
- Mockups → `.browser-frame`, `.mock-wa`, `.md-card`, or compose a custom one using inline styles.
- Diagrams → SVG with the existing filter library (`#oneon`, `#pyrGlow`, `#lglow`, `#hitlGlow`) and red gradient defs.
- Process / cycle / hierarchy → reuse `.process-flow`, `.trinity-circles`, `.pyramid-stage`, `.hitl-stage`, `.funnel-stage` from `index.html`.

When a brief is text-heavy, the slide split is still text-right + visual-left. The visual side is your responsibility to fill.

### 19. UX sizing: visual carries the message
The visual half of a `split` slide should carry the slide's emotional weight. The text supports it.

**Why:** when the visual feels empty (a single icon, a flat list), the audience reads only the text and the slide collapses to "a paragraph projected on a wall". When the visual is rich (animated mockup, custom diagram, multi-element composition), the slide feels designed.

**How to apply:**
- If the visual feels sparse, **enrich the visual** (more SVG detail, more cards, more motion, more layered components) before tightening the text.
- If the text feels cramped, weight the visual column with `flex: 1.3` to `flex: 1.4` so the text gets more breathing room.
- Typography stays on the established scale (see Design tokens). **Don't shrink fonts to fit content** — restructure layout instead.
- Visuals on the left column should fill ~80-90% of the column width with `max-width` clamps; never leave them as a postage-stamp icon in a sea of empty space.

## Quick lookup: what the user usually means

| User says | Almost always means |
|---|---|
| "תגדיל ב-20%" | scale `max-width`, font-size, padding, gap, icon size — all of them |
| "זה לא מיושר לימין" | `flex-direction: row-reverse` should be `row` with `direction: rtl` |
| "תוריד את האימוג'י" | replace with SVG outline icon in a red-tinted square |
| "תוריד את ה-em-dash" | audit the whole file, not just the line they pointed at |
| "שנה לבן" | strip every red reference inside the heading: span, inline style, text-shadow |
| "תעלה למעלה" / "במרכז" / "למטה" | adjust `justify-content` and `padding-top/bottom` on the slide |
| "תוסיף שקף" | insert before the CTA slide; verify dot-nav and keyboard hint still align |
| "consistency" (implicit) | apply the change to peer cards in the same slide and similar cards in sibling slides |
| "זה סטטי" / "תוסיף אנימציה" | add `data-fx="fade-up"` with staggered `data-fx-delay` to every visible element on the slide |
| "הגרפיקה דלה" / "תוסיף משהו ויזואלי" | enrich the visual side: more SVG elements, more motion, more detail. Don't add more text. |
| "אם אין לך, צור בעצמך" | when source brief doesn't provide media, generate the visual inline (SVG marks, custom diagrams, mockups) — don't degrade to flat text |
| "טקסט גדול / קטן מדי" | rebalance layout (flex weights, padding, max-width). Don't shrink fonts off-scale. |
