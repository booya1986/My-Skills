# Style C · Live product lift

Use it when the reel promotes something that exists as a **live web page with interactive demos** (a component gallery, a
showreel, a landing page) and the creator records a **dedicated scripted take** for it. The demos are captured from the live
site, so the reel shows the real thing, sharp, and costs no generation credits.

## The look
| Element | Spec |
|---|---|
| Canvas | 1080×1920, 30 fps. The speaker in the lower part, motion on top |
| Backgrounds | bold flat colour fields that change per beat (yellow `#FFD23F`, purple `#8E9BFF`, teal `#3FD7C6`, pink `#FF5FA2`, green `#35E08A`, charcoal `#141414`); a faint 72 px grid at 16 % |
| Speaker | a matte cut-out (`npx hyperframes remove-background`) at scale ~0.82–0.86 in front of the colour field; a gradient band in the field colour (y 860→1120) keeps their half clean. A studio full frame (room blurred and dimmed) only for the CTA and one half/half beat |
| Captions | charcoal pills, weight 800, 58 px, top 1556, radius 20; the spoken word lights up as it is said, keywords in the accent colour; phrase-level, popping in with a back-out ease |
| Chips | accent chips for keywords; charcoal chips with accent numbers for item labels (`01`, `17` …) top-right |
| HUD | a running timecode top-left, a part chip ("Part 2") and the site name top-right |
| Transitions | colour wipes alternating sideways / vertical (0.18 s in, 0.26 s out); one white flash for a hard mood change; camera whips along the page |
| Font | one family for everything |
| End | the studio frame + "write / KEYWORD / in the comments" chips + a bouncing SVG arrow; after the last word the frame shrinks into a rounded card; then the creator's outro sting |

## The signature effect: lift out of the page
The page becomes a 3D plane; each demo rises out of its own slot, flies forward and plays, then drops back.
- **Capture the page once as tiles** with every demo hidden (`scripts/style-c/capture-page.mjs tiles`): ~1440 px wide at DSF 2,
  2400 px tiles (under the GPU texture limit), plus every demo's slot rectangle in page coordinates (`page.json`). Fill each slot
  with the demo's first frame so the page looks normal until a demo lifts.
- **Capture every demo on its own** (`capture-demos.mjs`): the page needs a solo mode (one demo full-window) and a play hook;
  record a CDP screencast while it plays. Solo mode scales the demo to the viewport, so a 2× viewport at scale 1 equals DSF 2
  (screencast frames come in CSS pixels whatever the DSF). Keep frames ≤ ~1500 px wide or the frame rate drops. `build-demos.py`
  turns the timestamped frames into constant-rate clips.
- **One rig, a pure function of time.** A camera pose `{cx, cy, rx, ry, rz, s, px, sc}` puts page point (px, sc) at screen
  (cx, cy). Each layer uses the same pose plus its slot offset, rises (`lz`), then interpolates `k: 0→1` to a docked screen pose.
  Two 3D containers with identical perspective — page behind, layers in front — so no depth sorting is needed. Keys are
  `[t, partial props, ease]` tracks and `render(t)` writes the transforms from the timeline time (seek-safe).
- A lift takes ~0.8 s (rise 0.3 s, fly 0.5 s); labels pop only after the layer docks; whips between slots 0.25–0.35 s; centre the
  camera on the slot (`px`) so edge-column demos don't rise half off-screen.

## Face rules (check every frame)
- **No demo ever covers the face.** Every demo layer sits *behind* the cut-out in depth. Phones dock half behind the shoulder (the
  speaker steps ~170 px aside); wide web windows and long tours go full screen as **voice-over** (cut-out and band faded out). Mix
  both and label which is which in the review stills.
- **Captions never cover the face.** Measure the chin bottom in the source (lean-in frames too) and keep
  `y + scale × chin ≤ caption_top − 26` for every captioned pose. Zooms grow upward (`transformOrigin 50% 100%`). Chips and cards
  stay above the hairline.
- A callback to part 1 (the previous post or video) can circle the speaker, always behind them, then settle above the head.

## Sound
- Music: upbeat and bass-heavy at 100 BPM, so cuts sit on a 0.3 s half-beat grid; ducked ~13 dB under the voice with a sidechain.
  Keep it a separate stem mixed at assembly, so a new track never needs a re-render.
- Every SFX maps to something on screen: whoosh on wipes / layer flights / whips, click on chips and on presses inside demos, tick
  on small state changes, typing for typed text. Leave glitch sounds and impacts out unless asked.
- Voice: `scripts/style-c/voice.py` (DeepFilterNet uncapped → WPE dereverb → EQ → 2.5:1 compression → expander → loudnorm →
  split-band de-esser → air shelf → loudnorm). Measure it (`tail.py`, `sibtest.py`) rather than trusting it.

## Mascots and logos
If the product has an official animated mascot or logo asset, use that file (often shipped inside the product's desktop app);
never redraw one. Dark-on-dark assets go on a light card.
