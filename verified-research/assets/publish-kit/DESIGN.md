# <report>, design system

The living design reference for everything published from this repo. Update it when a
decision changes; the page must match this file.

## Intent
Editorial, magazine-like reading for a long research report. Calm, white, generous
whitespace, one strong accent. Not a dashboard, not a landing page.

## Language and direction
`<lang>`, `<ltr|rtl>` (set with `build.py --lang … --dir …`). Arrows for "next" point in
reading direction in rows (right in LTR, left in RTL) and down when stacked. Latin runs
inside RTL text are bidi-isolated. Sans-serif only: `<font family>` for display and body,
chosen to cover the note's script.

## Color
One accent (default red `#e5322d`, dark mode `#ff6b64`), for meaning only (numbers to
notice, active state, transitions). Ink `#111`, muted `#6f7379`, hairline `#ebebeb`,
white surfaces. Never a second accent, never colored body text.

## Type scale
H1 `clamp(2.2rem,5.4vw,4.4rem)` 900; H2 `clamp(1.7rem,3vw,2.3rem)` 900 with a 56px accent
rule above; H3 1.28rem 800; body 18px/1.8, measure 46rem; components break out to 74rem.

## Layout
Content plus a 17rem floating glass TOC (H2s only, never scrolls inside itself; active
item accent bold text). 3px accent progress bar. Hero: kicker, display H1, light lede,
optional three stat tiles, hairline meta row. Single column under 980px, the TOC becomes
an accent pill.

## Boxes are the exception
Hairlines and whitespace, not cards. Tables: 2px ink top rule, 1px bottom rule, no side
borders.

## Components
| Component | Where | Behavior |
|---|---|---|
| (fill in per report) | | |

## Illustrations
`<style>`, transparent background, short labels, one accent. Generated with
`<image tool / model>` using `style-reference.png` as reference. Registered in
`components.ILL`. OG cover 1200×630 at `assets/og.png`.

## Build
`python3 build.py "<note path or glob>" <site_url> --lang <code> --dir <ltr|rtl>`, then
commit and push; GitHub Pages serves `/`.

## Do not
No serif fonts. No second accent. No drop-shadow cards around text. No inner scrolling
in the menu. No content only in the HTML and not in the note.
