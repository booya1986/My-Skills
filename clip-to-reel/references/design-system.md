# Design system — the approved the reference build look , for any language

Measured from the reference (38.08 s, 1080×1920, −14.3 LUFS, 12 detected cuts) and tuned over 8 judge rounds.
`assets/reference-composition.html` implements all of it; copy from there rather than rewriting.

## Modes and proportions

| Mode | What it is | Target share | Rules |
|---|---|---|---|
| **Split** | beige paper top (0–954 px), face bottom (954–1920), chip on the seam | ≈25 % | Return to split several times mid-reel, not just open/close. 2–3 graphic beats inside the first split. |
| **Studio** | full-screen light radial background with Apple-like UI mocks | ≈50 % | Include one long multi-beat window (5–6 s) where things keep happening. No single shot > 6 s. |
| **Full face** | face fills 1080×1920 | ≈15 % | Only from a clean full-frame window. Max ~2.5 s per shot; push-in ≤ 3 %. |
| **Dark** | black, glowing orange mono + pixel wordmark, scanlines | one beat ≤ 2 s | Typing finishes inside the beat. |
| **Web card** | licensed stock clip in a white-framed 16:9 card + floating real-logo tiles | one beat ~1.7 s | Bright, warm grade. Icons drift so it is never static. |
| **CTA card** | full-screen paper: brand logo, huge sans "GUIDE" (quotes in rust), chip "Comment below", subline | 3–3.5 s | Word visible from its first frame (pop 0.92→1). Boosted music bed + whoosh + boom. |

Decisions baked into the approved look (they override the reference): the CTA word is **sans-serif**; the ending is a
**full-screen card**, not a face mouthing words after the voice ends; one **real web video** insert is included.

## Tokens

- Paper `#F2DFBC` + `media/paper_grain.png` overlay; studio `radial-gradient(#fff → #f2f2f0 40% → #dededa)`;
  dark `#050505`; accent orange `#E4643A`, text-safe rust `#B84A26`; ink `#1c1a17`; green check `#22C55E`.
- Fonts: Noto Sans Hebrew (`NSH`, 800–900 for chips and headlines; its latin subset covers English chips too),
  JetBrains Mono (`JB`) for UI text. Only the embedded subsets exist — no emoji, arrows or ✓ glyphs; draw them as
  inline SVG. For another script, add that language's Noto Sans subset and extend `check_glyphs.py` RANGES.
- Direction: Hebrew/Arabic → `direction:rtl` chips, dotted links and flows move right→left; otherwise LTR.

## Caption chips

```css
.capRow{position:absolute;left:0;width:1080px;height:96px;z-index:20;display:flex;justify-content:center;align-items:center}
#capSeam{top:906px}      /* centred on the seam (≈954) */
#capLow{top:1212px}      /* ≈65 % height in full-screen modes */
.cap span.c{display:inline-block;padding:8px 18px;border-radius:14px;line-height:68px;
  background:rgba(70,70,70,.85);font-size:62px;font-weight:900;color:#fff;
  text-shadow:0 3px 0 rgba(0,0,0,.85),0 3px 6px rgba(0,0,0,.6)}
```
1–3 words per chip, following the reel-time words; a chip lives in the row that matches the scene on screen.

## Motion vocabulary

- **Cut transition:** every scene's `.snap` wrapper `scale 1.12→1, y 26→0` in 0.3 s `power3.out` (and the face
  `<video>` itself), plus a whoosh 0.08 s before the cut.
- **Push-in:** every `.cam` wrapper `scale 1→1.06–1.12` across the scene, `ease:none`.
- **Reveals:** typed text via `clipPath: inset(0 100% 0 0) → inset(0)` with `steps(n)`; highlighter bars
  (`.hl` width 0→N); dotted connection lines revealed right→left (RTL forward); folder grids popping with
  `back.out(2)`; a moving selection rectangle; green check badge pops; pixel-block letters revealed row by row.
- **Hook:** frame 0 already shows the tool icon big (scale 1.7→1 in 0.3 s), wordmark types from ~0.45 s inside a
  selection box, third beat is a mini command window with highlighter.

## Structure and timing math

- Scenes are `class="clip scene top|whole"` divs; face videos live in untimed `.half` / `.full` wrappers outside
  scenes (a timed `<video>` inside a timed div fails lint).
- `data-media-start` for a face clip = `abs_time_of_reel_moment − file_start_abs`. For the bubble file cut from
  `src_<from>-<to>.mp4`: `(segment_src_from + (reel_t − segment_reel_from)) − <from>`.
- z-index: face 1–3, scenes 5, web card 6, captions 20, CTA word 22.
- One paused GSAP timeline registered on `window.__timelines["main"]`.
