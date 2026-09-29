# Publish: the designed HTML report (optional, user opt-in)

Offer this in one line after the note is done ("want a shareable designed version with
infographics?"). Build it only when the user says yes. It costs a repo, some image
generation credits if you add illustrations, and real iteration time; the note is the
deliverable of record, the page is a way to share it.

## What the user gets

A standalone page on GitHub Pages: editorial layout, floating table of contents,
interactive components where they explain better than prose, infographics in one
consistent style, an OG cover image for sharing, and a `DESIGN.md` that lets the next
session change the page without re-deriving the design. The link is written into the
note's frontmatter (`html_report:`) and in a callout under the note's header.

## The kit

Copy `<skill>/assets/publish-kit/` into a new project folder **outside the notes folder**
(e.g. `<projects>/<slug>-report/`). It contains:

- `build.py`: `python3 build.py "<note path or glob>" [site_url] [--lang en --dir ltr]`.
  Reads the note, strips frontmatter and an optional share callout, converts markdown
  with `npx marked --gfm` (no pip install needed), applies `components.py`, injects the
  result into `template.html`, writes `index.html`.
- `template.html`: the editorial shell (tokens, type scale, floating TOC with
  scroll-spy and no inner scrolling, progress bar, tabs, stepper, calculator, figures,
  dark mode, print). Language and direction come from `{{LANG}}` / `{{DIR}}`
  placeholders, so the same template serves LTR and RTL notes.
- `components.py`: reusable helpers (`h3_text_to_id`, `section_span`, `parse_table`,
  `illustrations`) plus small example components showing the pattern: find a heading or
  table by text, keep every word of it, re-render it as a component. The examples are to
  be replaced per report, not kept.
- `DESIGN.md`: the template of the design contract. Fill it in as decisions are made.
- `style-reference.png`: a text-free example of the illustration style (hand-drawn
  doodles, blob characters). Swap in your own reference if you prefer another style.

## Default design decisions (apply unless the user says otherwise)

- Magazine/editorial feel, **sans-serif only**, white, minimalist, modern. The template
  ships with a system font stack; set `--font` to any web font that covers the note's
  script.
- One accent color, used for meaning only (numbers to notice, active state).
- Hairlines and whitespace instead of boxes. Tables: 2px ink top rule, 1px bottom.
- Floating glass TOC that lists H2s only, so it never scrolls inside itself. The active
  item is accent-colored bold text, no bars or brackets.
- Interactive elements wherever a static table hides the point: a stage stepper, a
  calculator for ratios, tabs for options, a KPI filter by stage, a timeline, cards for
  the pre-mortem. **Nothing from the note is dropped**; components re-render the same
  content, and nothing appears only in the HTML.
- Illustrations in one consistent style with a **transparent background** and short
  labels. Image models render non-Latin scripts unreliably, so keep in-image labels
  short and in a script the model handles well, and put the real caption in HTML.
- Direction-aware arrows: "next" points right in LTR rows, left in RTL rows, and down
  when stacked on phones.

## Right-to-left reports

Run `build.py` with `--lang <code> --dir rtl` (e.g. `--lang ar --dir rtl`). The template
uses logical CSS properties (`inset-inline`, `padding-inline-start`, `text-align:start`)
so the layout mirrors on its own. Checks for RTL pages:
- `<html lang dir>` set correctly; tables inherit direction; code blocks stay LTR.
- Latin runs (product names, URLs, numbers with units) inside RTL text are isolated with
  `<bdi>` or `unicode-bidi: isolate` so punctuation does not jump to the wrong side;
  table cells use `unicode-bidi: plaintext`.
- Mirrored arrows: the stepper arrow is chosen from `dir`; any arrow you hand-write in
  content must point in reading direction.
- Mermaid flows are top-down (`flowchart TD`), never left-to-right.

## Images (optional)

Use whatever image-generation tool the user has. The pattern that works:
1. Give the model the style reference as an image reference.
2. One request per figure: high quality, ~2k resolution, transparent background (opaque
   for the OG cover), a prompt that says "match the drawing style only, no paper
   texture, replace the reference accent color with <your accent>", and the exact label
   text in quotes.
3. Wait for all jobs, download, crop the OG cover to 1200×630, resample figures to
   ~1400px wide, confirm the PNG has an alpha channel, and **look at every image and
   check its spelling** before use.
4. Register each figure in `components.ILL` (needle in heading text, filename, caption).
   Dark mode inverts line art via CSS.

## Verify in a real browser (not optional)

Serve locally on a free port (check with `lsof -ti:<port>` first; if taken by your own
old server, kill and reuse it rather than escalating ports), open the page in a real
browser (Playwright or similar), take screenshots at ~1360 and ~390 wide, look at them,
check `document.documentElement.scrollWidth === clientWidth` at phone width (no
horizontal scroll), and confirm the TOC `scrollHeight` is below `innerHeight`. Keep
screenshots in a scratch folder, delete them, and stop the server before finishing.

## Ship

`gh repo create <name> --public --source . --push`, then
`gh api -X POST repos/<owner>/<name>/pages -f source[branch]=main -f source[path]=/`.
Poll the live URL (a background `until curl -s <url> | grep -q <marker>; do sleep 10; done`
loop, not chained sleeps) and only report success once the live page shows the change.
Write the URL into the note. If the user renames the repo, update every link and
re-check with a grep for the old name.

## Iterating with the user

Expect several small design corrections in a row (palette, boxes, menu, arrows,
backgrounds). Apply each, rebuild, verify, push, and confirm the live page carries it.
Record every decision in `DESIGN.md` so the next session starts from the current state.
