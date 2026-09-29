#!/usr/bin/env python3
"""Style-B reference build (editorial collage). Placeholder copy: replace every "caption text" and the
English on-screen strings with your own.

Copy this file to <project>/build.py and assets/style-b/kit.css to <project>/kit.css, then edit ONLY the tables
at the top (CARD face windows, FB full-bleed clips, OV overlays, STILLS/BURSTS, CAPS, CUTS), the scene HTML in
scenes(), and the per-scene tweens in TIMELINE. The defaults are the approved look: one font family, ~8 whooshes
on mode changes only, a large bottom-anchored face card with captions above it, and a collage-sign CTA.
For a small webcam-bubble face, delete the "large face card" block at the end of kit.css.
Timings below come from a real 56 s build (one uncut take, three short face windows).
Run: python3 build.py && npm run check
"""
import html
import json

DUR = 56.05
VO_END = 53.55

# ── face windows: (start, end, media_start on face_card.mp4 = source clock) ─────────────
CARD = [(0.00, 2.05, 4.85), (18.65, 20.65, 23.50), (39.70, 42.05, 44.55)]

# ── full-bleed collage clips ─────────────────────────────────────────────────────────────
FB = [  # id, start, end, src, media_start
    ("v1", 6.97, 10.90, "media/col_teach.mp4", 0.2),
    ("v2", 20.65, 23.00, "media/col_martial.mp4", 0.3),
    ("v3", 45.90, 47.40, "media/col_scroll.mp4", 1.0),
    ("v4", 47.40, 50.00, "media/col_copier.mp4", 0.3),
    ("v5", 53.55, 56.05, "media/col_sign.mp4", 1.2),
]

# ── collage overlays above the UI scenes ─────────────────────────────────────────────────
OV = [  # id, start, end, src, media_start (None = still image)
    ("o2", 38.45, 39.70, "media/col_lever.png", None),
]
STILLS = ["bulb", "recipe", "key", "reader", "stamp", "puzzle", "lab", "rocket", "gears", "cups", "head"]
BURSTS = [(2.05, 8, 0.10, 0), (32.30, 11, 0.10, 5)]  # start, shots, shot length, first still

# ── captions: (start, end, text) — 1-3 words, split by meaning ─────────────────────────
CAPS = [
    (0.02, 0.29, "caption text"), (0.29, 1.04, "caption text"), (1.04, 1.80, "caption text"), (1.80, 2.80, "caption text"),
    (2.87, 3.44, "caption text"), (3.44, 4.29, "caption text"), (4.29, 5.30, "caption text"),
    (5.37, 6.36, "caption text"), (6.36, 6.95, "caption text"),
    (6.97, 7.51, "caption text"), (7.51, 8.68, "caption text"), (8.68, 9.04, "caption text"), (9.04, 9.86, "caption text"),
    (9.86, 10.95, "caption text"),
    (11.03, 11.57, "caption text"), (11.57, 12.77, "caption text"), (12.77, 13.50, "caption text"), (13.50, 14.30, "caption text"),
    (14.35, 15.30, "caption text"), (15.30, 16.15, "caption text"),
    (16.19, 16.85, "caption text"), (16.85, 17.62, "caption text"), (17.62, 18.62, "caption text"),
    (18.87, 19.55, "caption text"), (19.55, 20.50, "caption text"),
    (20.56, 21.14, "caption text"), (21.14, 21.80, "caption text"), (21.80, 22.31, "caption text"), (22.31, 23.00, "caption text"),
    (23.09, 23.65, "caption text"), (23.65, 24.49, "caption text"), (24.49, 25.19, "caption text"), (25.19, 26.03, "caption text"),
    (26.03, 26.99, "caption text"), (26.99, 27.28, "caption text"),
    (27.31, 28.45, 'caption text <L>SKILL.md</L>'), (28.51, 29.23, "caption text"), (29.23, 30.50, 'caption text <L>Markdown</L>'),
    (30.55, 30.91, "caption text"), (30.91, 32.28, 'caption text <L>CLAUDE.md</L>'),
    (32.35, 33.13, "caption text"), (33.13, 34.01, "caption text"), (34.01, 35.20, "caption text"),
    (35.22, 36.32, "caption text"), (36.32, 37.36, "caption text"), (37.36, 38.50, "caption text"),
    (38.55, 39.41, "caption text"), (39.41, 40.25, "caption text"),
    (40.31, 41.10, "caption text"), (41.10, 42.05, "caption text"), (42.11, 43.09, "caption text"), (43.09, 43.93, "caption text"),
    (43.93, 44.50, "caption text"), (44.50, 45.53, "caption text"), (45.53, 46.54, "caption text"), (46.54, 47.45, "caption text"),
    (47.51, 48.39, "caption text"), (48.39, 49.27, "caption text"), (49.27, 49.95, "caption text"),
    (49.99, 51.18, "caption text"), (51.18, 51.69, "caption text"), (51.69, 52.78, "caption text"), (52.78, 53.50, "caption text"),
]
CARD_ON = [(a, b) for a, b, _ in CARD]

# scene starts get a whoosh
CUTS = [2.05, 6.97, 18.65, 23.00, 32.30, 39.70, 47.40, 53.55]  # whoosh only on major scene changes (one on every cut felt like too much)


def cap_html(t):
    return html.escape(t).replace("&lt;L&gt;", '<span class="ltr">').replace("&lt;/L&gt;", "</span>")


def on_card(a):
    return any(s - 0.01 <= a < e for s, e in CARD_ON)


CSS = open("kit.css", encoding="utf-8").read()

CURSOR = ('<svg viewBox="0 0 24 24"><path d="M4 2 L4 20 L9 15.5 L12.5 22 L15.5 20.6 L12.2 14.3 L19 14.3 Z" '
          'fill="#111" stroke="#fff" stroke-width="1.4" stroke-linejoin="round"/></svg>')
OK = ('<svg viewBox="0 0 24 24" style="width:54px;height:54px;margin-top:16px"><path d="M5 12.5l4.2 4.2L19 7" '
      'fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def bdrop(name, blur=True):
    if not blur:
        return f'<div class="still bdrop" style="background-image:url(media/col_{name}.png)"></div>'
    return (f'<div class="still bdrop" style="background-image:url(media/col_{name}.png);filter:blur(3px) brightness(.93)"></div>'
            '<div class="still" style="background:rgba(247,247,245,.34)"></div>')


def clip(id_, a, b, track, inner, cls="scene", extra=""):
    return (f'<div id="{id_}" class="clip {cls}" data-start="{a:.2f}" data-duration="{b - a:.2f}" '
            f'data-track-index="{track}" data-layout-allow-overlap data-layout-allow-overflow{extra}>{inner}</div>')


def lines(ws):
    return "".join(f'<div class="gl" style="width:{w}%;margin-right:auto"></div>' for w in ws)


def scenes():
    s = []
    # face backdrops (collage above the large card)
    s.append(clip("sA1", 0.00, 0.85, 5, '<div class="cam" id="sA1Cam">' + bdrop("head", False) + '</div>'))
    s.append(clip("sA2", 0.85, 2.05, 6, '<div class="cam" id="sA2Cam">' + bdrop("teach", False) + '</div>'))
    s.append(clip("sI", 18.65, 20.65, 5, '<div class="cam" id="sICam">' + bdrop("martial", False) + '</div>'))
    s.append(clip("sJ", 39.70, 42.05, 5, '<div class="cam" id="sJCam">' + bdrop("manual", False) + '</div>'))

    # B · one task, same result every time (2.85 - 6.97)
    res = "".join(f'''<div class="res" id="sBR{i}" style="left:{110 + i * 300}px;top:820px">
        {lines((90, 70, 82))}<div class="ok" id="sBO{i}">{OK}</div></div>''' for i in range(3))
    s.append(clip("sB", 2.85, 6.97, 5, '<div class="bg"></div>' + f'''<div class="cam" id="sBCam">
      <div class="fcard" id="sBTask" style="top:340px"><div class="ring" id="sBRing"></div><div class="t">Task</div>
        <div class="d" id="sBHow" style="top:132px;right:44px;left:auto;font-size:44px;color:#15803d;font-weight:700">a certain way</div></div>
      <div class="arrow" id="sBArr" style="left:535px;top:620px;height:120px"></div>
      {res}</div>'''))

    # C · the three things a skill teaches (10.90 - 18.65, gears overlay 14.35 - 16.10)
    cards = [("The way", "how to do the task"), ("The processes", "what to run"), ("The result", "what it should look like")]
    fc = "".join(f'''<div class="fcard" id="sCF{i}" style="top:{470 + i * 300}px"><div class="ring" id="sCR{i}"></div>
        <div class="t">{t}</div><div class="d" style="top:136px;right:44px;left:auto">{d}</div></div>''' for i, (t, d) in enumerate(cards))
    s.append(clip("sC", 10.90, 18.65, 5, '<div class="bg"></div>' + f'''<div class="cam" id="sCCam">
      {fc}<div class="cursor" id="sCCur" style="left:760px;top:1400px">{CURSOR}</div></div>'''))

    # D · a folder with one instructions file (23.00 - 27.20)
    s.append(clip("sD", 23.00, 27.20, 5, bdrop("folder") + f'''<div class="cam" id="sDCam">
      <div class="folder" id="sDFold" style="left:465px;top:360px"><div class="st"></div></div>
      <div class="win" id="sDWin" style="left:110px;top:590px;width:860px;height:260px">
        <div class="bar"><i></i><i></i><i></i><b>~/.claude/skills/my-skill</b></div>
        <div style="padding-top:40px">
          <div class="row" id="sDRow"><div class="hlrow" id="sDHl"></div><span class="fi" style="background:#22C55E"></span><span id="sDName">SKILL.md</span></div>
        </div></div>
      <div class="pill" id="sDPill" style="left:260px;top:960px;background:#1b1b1b;direction:rtl;padding:0 60px 0 120px">one instructions file</div>
      <div class="cursor" id="sDCur" style="left:820px;top:1180px">{CURSOR}</div></div>'''))

    # E · SKILL.md is Markdown, like CLAUDE.md (27.20 - 32.30)
    code = [('<span class="m">---</span>', 27.45), ('<span class="k">name:</span> my-skill', 27.75),
            ('<span class="k">description:</span> design + critique UI', 28.15), ('<span class="m">---</span>', 28.6),
            ('<span class="k">#</span> Instructions', 28.9), ('<span class="k">##</span> Examples', 29.25)]
    rows = "".join(f'<div class="code" id="sEc{i}">{c}</div>' for i, (c, _) in enumerate(code))
    s.append(clip("sE", 27.20, 32.30, 5, f'''<div class="bg"></div><div class="cam" id="sECam">
      <div class="win" id="sEWin" style="left:90px;top:230px;width:900px;height:640px">
        <div class="bar"><i></i><i></i><i></i><b>my-skill / SKILL.md</b></div>
        <div style="padding:40px 50px">{rows}<div id="sEMore" style="margin-top:20px">{lines((82, 64, 90, 55))}</div></div></div>
      <div class="pill" id="sEPill" style="left:300px;top:920px;z-index:3">Markdown</div>
      <div class="fcard" id="sECl" style="top:1080px;height:200px"><div class="ring" id="sERing"></div>
        <div class="t" style="top:30px;direction:ltr;font-family:'NSH',sans-serif">CLAUDE.md</div>
        <div class="d" style="top:120px;right:44px;left:auto">the same format</div></div></div>'''))

    # F · companion files (33.40 - 38.45)
    extra = [("examples/", "examples"), ("templates/", "templates"), ("scripts/", "scripts")]
    er = "".join(f'''<div class="row" id="sFR{i}"><span class="ic" style="background:#22C55E"></span><span>{n}</span><span class="he">{h}</span></div>'''
                 for i, (n, h) in enumerate(extra))
    s.append(clip("sF", 33.40, 38.45, 5, bdrop("toolbox") + f'''<div class="cam" id="sFCam">
      <div class="win" id="sFWin" style="left:110px;top:420px;width:860px;height:470px">
        <div class="bar"><i></i><i></i><i></i><b>my-skill/</b></div>
        <div style="padding-top:16px">
          <div class="row"><span class="fi" style="background:#22C55E"></span><span>SKILL.md</span></div>{er}
        </div></div></div>'''))

    # G · in practice: one big prompt (42.05 - 45.90)
    s.append(clip("sG", 42.05, 45.90, 5, f'''<div class="bg"></div><div class="cam" id="sGCam">
      <div class="win" id="sGWin" style="left:90px;top:250px;width:900px;height:1100px">
        <div class="bar"><i></i><i></i><i></i><b>my-skill / SKILL.md</b></div>
        <div style="position:absolute;top:68px;left:0;right:0;bottom:0;overflow:hidden"><div class="md" id="sGDoc">
          <div class="h2">## Instructions</div>{lines((88, 72, 95, 60, 83))}
          <div class="h2"><span class="li" style="font-size:inherit;line-height:inherit;color:inherit"><i id="sGHi1"></i>## Examples</span></div>{lines((70, 91, 55, 78))}
          <div class="h2"><span class="li" style="font-size:inherit;line-height:inherit;color:inherit"><i id="sGHi2"></i>## How to do it</span></div>{lines((86, 64, 90, 58, 80, 74, 93, 61, 85, 70, 88, 52, 79))}
        </div></div></div></div>'''))

    # H · saved once, run with a slash command (50.00 - 53.55)
    s.append(clip("sH", 50.00, VO_END, 5, '<div class="bg"></div>' + f'''<div class="cam" id="sHCam">
      <div class="fcard" id="sHSaved" style="top:330px;height:180px">
        <div class="t" style="top:30px;direction:ltr;font-family:'NSH',sans-serif">my-skill</div>
        <div class="d" style="top:112px;right:44px;left:auto">saved once</div>
        <div class="ok" id="sHOk" style="left:40px;top:46px">{OK}</div></div>
      <div class="greet" id="sHG" style="top:640px;left:170px;right:170px;background:#fff;border-radius:22px;padding:14px 0;box-shadow:0 10px 30px rgba(0,0,0,.12)"><span class="claude"></span>What shall we work on today?</div>
      <div class="chat" id="sHChat" style="top:850px"><div class="ph" id="sHPh">Write a message…</div>
        <div class="tx" id="sHTx">/my-skill</div><div class="plus">+</div><div class="send" id="sHSend"></div></div>
      <div class="pill" id="sHPill" style="left:310px;top:1110px;z-index:3">Running</div>
      <div class="cursor" id="sHCur" style="left:990px;top:1250px">{CURSOR}</div></div>'''))

    # CTA text over the sign video
    s.append(clip("sL", VO_END, DUR, 8, '''<div class="cam" id="sLCam">
      <div class="sign" id="sLWord" style="top:470px;font-size:190px;font-weight:900;color:#141414;line-height:200px">"KEYWORD"</div></div>
      <div class="sign" id="sLSub" style="top:1560px"><span style="display:inline-block;padding:6px 24px 8px;border-radius:6px;background:#22C55E;color:#0b0b0b;font-size:48px;font-weight:800;line-height:64px">and I'll send you the guide</span></div>'''))
    return "\n".join(s)


def body():
    out = ['<div class="bg"></div>']
    for vid, a, b, src, ms in FB:
        out.append(f'<div class="scene" id="{vid}W" style="z-index:4"><video id="{vid}" class="clip fb" src="{src}" '
                   f'data-start="{a:.2f}" data-duration="{b - a:.2f}" data-media-start="{ms}" data-track-index="3" muted playsinline></video></div>')
    out.append('<div id="scenes" style="position:absolute;inset:0;z-index:10">' + scenes() + '</div>')
    for oid, a, b, src, ms in OV:
        if ms is None:
            out.append(clip(oid, a, b, 7, f'<div class="still" id="{oid}I" style="background-image:url({src})"></div>',
                            extra=' style="z-index:12"'))
        else:
            out.append(f'<div class="scene" id="{oid}W" style="z-index:12"><video id="{oid}" class="clip fb" src="{src}" '
                       f'data-start="{a:.2f}" data-duration="{b - a:.2f}" data-media-start="{ms}" data-track-index="8" muted playsinline></video></div>')
    for bi, (t0, n, L, first) in enumerate(BURSTS):
        for k in range(n):
            a = t0 + k * L
            img = STILLS[(first + k) % len(STILLS)]
            sc = 1.0 + 0.35 * ((k * 7) % 5) / 4
            inner = (f'<div class="still" style="background-image:url(media/col_{img}.png);'
                     f'transform:scale({sc:.2f});transform-origin:{30 + (k * 23) % 40}% {25 + (k * 17) % 40}%"></div>')
            out.append(clip(f"b{bi}_{k}", a, (a + L + 0.034) if k == n - 1 else a + L, 9 + (k % 2), inner, extra=' style="z-index:14"'))
            out.append(f'<audio id="bt{bi}_{k}" class="clip" src="media/sfx/tick.wav" data-start="{a:.2f}" '
                       f'data-duration="0.05" data-track-index="{39 + k % 2}" data-volume="0.45"></audio>')
    vids = "".join(
        f'<video id="face{i}" class="clip" src="media/face_card.mp4" data-start="{a:.2f}" data-duration="{b - a:.2f}" '
        f'data-media-start="{m:.2f}" data-track-index="1" data-layout-allow-overflow muted playsinline></video>' for i, (a, b, m) in enumerate(CARD))
    out.append(f'<div id="card">{vids}</div>')
    rc, rf = [], []
    for i, (a, b, t) in enumerate(CAPS):
        row = rc if on_card(a) else rf
        tr = 20 + (i % 2) + (0 if row is rc else 2)
        row.append(f'<div id="cap{i:02d}" class="clip cap" data-start="{a:.2f}" data-duration="{b - a:.2f}" '
                   f'data-track-index="{tr}"><span class="c">{cap_html(t)}</span></div>')
    out.append('<div class="capRow" id="capCard">' + "".join(rc) + '</div>')
    out.append('<div class="capRow" id="capFull">' + "".join(rf) + '</div>')
    out.append(f'<div class="capRow" id="capCta" style="top:1440px"><div id="capCtaC" class="clip cap" data-start="{VO_END + 0.12:.2f}" '
               f'data-duration="{DUR - VO_END - 0.12:.2f}" data-track-index="26"><span class="c" style="font-size:58px">comment below</span></div></div>')
    # audio
    out.append(f'<audio id="aVo" class="clip" src="media/vo.wav" data-start="0" data-duration="{VO_END}" data-track-index="30" data-volume="1"></audio>')
    out.append(f'<audio id="aMusic" class="clip" src="media/music_bed.mp3" data-start="0" data-duration="{VO_END}" data-media-start="0" data-track-index="31" data-volume="0.09"></audio>')
    for i, (a, b) in enumerate([(6.97, 10.90), (20.65, 23.00), (45.90, 50.00), (31.80, 33.45), (39.20, 40.40)]):
        out.append(f'<audio id="mUp{i}" class="clip" src="media/music_bed.mp3" data-start="{a:.2f}" data-duration="{b - a:.2f}" data-media-start="{a:.2f}" data-track-index="{41 + i % 2}" data-volume="0.22"></audio>')
    out.append(f'<audio id="aMusicEnd" class="clip" src="media/music_bed.mp3" data-start="{VO_END}" data-duration="{DUR - VO_END:.2f}" data-media-start="{VO_END}" data-track-index="32" data-volume="0.40"></audio>')
    for i, t in enumerate(sorted(set(CUTS))):
        out.append(f'<audio id="w{i}" class="clip" src="media/sfx/whoosh.wav" data-start="{max(0, t - 0.08):.2f}" data-duration="0.57" data-track-index="{33 + i % 2}" data-volume="0.6"></audio>')
    for i, t in enumerate([6.36, 6.46, 6.56, 25.19, 35.55, 36.54, 37.43, 50.50, 52.85, 11.20, 17.62, 30.91, 5.37, 5.55, 5.73, 23.65, 26.03, 29.71, 52.95, 16.10, 44.50, 43.09]):
        out.append(f'<audio id="k{i}" class="clip" src="media/sfx/click.wav" data-start="{t:.2f}" data-duration="0.09" data-track-index="{35 + i % 2}" data-volume="1.0"></audio>')
    typ = [51.69 + k * 0.1 for k in range(9)] + [27.45 + k * 0.09 for k in range(20)]
    for i, t in enumerate(typ):
        out.append(f'<audio id="ty{i}" class="clip" src="media/sfx/tick.wav" data-start="{t:.2f}" data-duration="0.05" data-track-index="{43 + i % 2}" data-volume="0.55"></audio>')
    for i, t in enumerate([2.87, 33.42]):
        out.append(f'<audio id="imp{i}" class="clip" src="media/sfx/impact.wav" data-start="{t:.2f}" data-duration="0.5" data-track-index="{46 + i}" data-volume="0.5"></audio>')
    out.append(f'<audio id="aBoom" class="clip" src="media/sfx/boom.wav" data-start="{VO_END}" data-duration="{DUR - VO_END:.2f}" data-track-index="38" data-volume="0.38"></audio>')
    return "\n".join(out)


TIMELINE = r"""
const OVS = __OVS__;
const FBS = __FBS__;
const JIT = [[0,0,0],[-6,4,-0.8],[5,-3,0.6],[-3,-5,-0.4],[6,3,0.9],[-4,6,-0.6],[3,-4,0.5],[0,5,-0.9]];
const tl = gsap.timeline({ paused: true });
const EO = "power3.out", BK = "back.out(1.8)";
const push = (sel, t, d, a = 1, b = 1.05) => tl.fromTo(sel, { scale: a }, { scale: b, duration: d, ease: "none" }, t);
const pop = (sel, t, e = BK, d = 0.34) => tl.fromTo(sel, { autoAlpha: 0, scale: 0.6 }, { autoAlpha: 1, scale: 1, duration: d, ease: e }, t);
const rise = (sel, t, y = 60) => tl.fromTo(sel, { autoAlpha: 0, y }, { autoAlpha: 1, y: 0, duration: 0.3, ease: EO }, t);
const type = (sel, t, d, n) => tl.fromTo(sel, { clipPath: "inset(0% 100% 0% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: d, ease: `steps(${n})` }, t);
const cut = (sel, t) => tl.fromTo(sel, { scale: 1.08 }, { scale: 1, duration: 0.28, ease: EO }, t);
const hideUntil = (sel, t) => { tl.set(sel, { autoAlpha: 0 }, 0); };

/* face card: visible only on face windows; slides up at each entry */
tl.set("#card", { autoAlpha: 0 }, 0);
__SPANS__.forEach(([on, off]) => {
  if (on < 0.05) tl.set("#card", { autoAlpha: 1 }, 0);
  else tl.fromTo("#card", { autoAlpha: 1, y: 160, scale: 0.92 }, { autoAlpha: 1, y: 0, scale: 1, duration: 0.24, ease: BK, immediateRender: false }, on);
  tl.set("#card", { autoAlpha: 0 }, off);
});
push("#card video", 0, __VOEND__, 1.0, 1.04);

/* stills behind the card and blurred backdrops: slow push + stop-motion jitter */
document.querySelectorAll(".bdrop").forEach((el, i) => {
  const sc = el.closest(".clip"); const a = +sc.dataset.start, b = a + +sc.dataset.duration;
  tl.fromTo(el, { scale: 1.04 }, { scale: 1.12, duration: b - a, ease: "none" }, a);
  for (let t = a + 0.25, k = 1; t < b; t += 0.25, k++) { const [x, y, r] = JIT[(k + i) % JIT.length]; tl.set(el, { x: x * 1.4, y: y * 1.4, rotation: r * 0.6 }, t); }
});
cut("#sA2Cam", 0.85); cut("#sICam", 18.65); cut("#sJCam", 39.70);

/* full-bleed collage: snap + slow push, jitter */
FBS.forEach(([s, t, d], i) => {
  tl.fromTo(s, { scale: 1.12 }, { scale: 1.0, duration: 0.3, ease: EO }, t);
  tl.to(s, { scale: 1.05, duration: d - 0.3, ease: "none" }, t + 0.3);
  if (i < FBS.length - 1) for (let u = t + 0.25, k = 1; u < t + d; u += 0.25, k++) { const [x, y, r] = JIT[(k + i) % JIT.length]; tl.set(s, { x: x * 0.7, y: y * 0.7, rotation: r * 0.5 }, u); }
});
/* punch-ins inside the longer collage clips */
[["#v1W", 9.86, "50% 35%"], ["#v4W", 49.27, "45% 40%"]].forEach(([el, t, o]) => {
  tl.set(el, { transformOrigin: o }, t);
  tl.fromTo(el, { scale: 1.36 }, { scale: 1.30, duration: 0.3, ease: EO, immediateRender: false }, t);
});

/* overlays */
OVS.forEach(([id, a, b, still]) => {
  const el = still ? `#${id}I` : `#${id}W`;
  tl.fromTo(el, { scale: 1.12 }, { scale: 1.0, duration: 0.28, ease: EO }, a);
  tl.to(el, { scale: 1.05, duration: b - a - 0.28, ease: "none" }, a + 0.28);
  if (still) for (let t = a + 0.25, k = 1; t < b; t += 0.25, k++) { const [x, y, r] = JIT[k % JIT.length]; tl.set(el, { x, y, rotation: r }, t); }
});

/* B · task -> identical results */
cut("#sBCam", 2.85); push("#sBCam", 2.85, 4.12, 1.0, 1.07);
rise("#sBTask", 2.9, 60);
tl.fromTo("#sBHow", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.2 }, 4.29);
tl.to("#sBRing", { opacity: 1, duration: 0.2 }, 4.29);
tl.fromTo("#sBArr", { autoAlpha: 0, scaleY: 0, transformOrigin: "50% 0%" }, { autoAlpha: 1, scaleY: 1, duration: 0.3, ease: EO }, 5.1);
[0, 1, 2].forEach(i => { pop(`#sBR${i}`, 5.37 + i * 0.18); pop(`#sBO${i}`, 6.36 + i * 0.1); });

/* C · three things */
cut("#sCCam", 10.90); push("#sCCam", 10.90, 7.75, 1.0, 1.07);
[[0, 11.03], [1, 14.35], [2, 17.62]].forEach(([i, t]) => rise(`#sCF${i}`, t, 70));
tl.set("#sCF1", { autoAlpha: 0 }, 10.90); tl.set("#sCF2", { autoAlpha: 0 }, 10.90);
tl.to("#sCR0", { opacity: 1, duration: 0.2 }, 11.2);
tl.to("#sCR0", { opacity: 0, duration: 0.2 }, 14.3);
tl.to("#sCR1", { opacity: 1, duration: 0.2 }, 14.5);
tl.to("#sCR1", { opacity: 0, duration: 0.2 }, 17.55);
tl.to("#sCR2", { opacity: 1, duration: 0.2 }, 17.62);
tl.fromTo("#sCCur", { x: 0, y: 0 }, { x: -300, y: -820, duration: 0.9, ease: "power2.inOut" }, 11.4);
tl.to("#sCCur", { x: -260, y: -520, duration: 0.7, ease: "power2.inOut" }, 14.6);
tl.to("#sCCur", { x: -240, y: -220, duration: 0.7, ease: "power2.inOut" }, 17.7);
tl.set("#sCCam", { transformOrigin: "50% 60%" }, 16.10);
tl.fromTo("#sCCam", { scale: 1.12 }, { scale: 1.08, duration: 0.3, ease: EO, immediateRender: false }, 16.10);

/* D · folder + one file */
cut("#sDCam", 23.00); push("#sDCam", 23.00, 4.20, 1.0, 1.05);
pop("#sDFold", 23.65); rise("#sDWin", 24.49, 80);
tl.fromTo("#sDCur", { x: 0, y: 0 }, { x: -220, y: -440, duration: 0.8, ease: "power2.inOut" }, 24.35);
tl.to("#sDHl", { opacity: 0.9, duration: 0.12 }, 25.19);
tl.to("#sDName", { color: "#ffffff", duration: 0.12 }, 25.19);
tl.fromTo("#sDPill", { autoAlpha: 0, scale: 0.7 }, { autoAlpha: 1, scale: 1, duration: 0.35, ease: BK }, 26.03);
tl.to("#sDFold", { rotation: -6, duration: 0.5, ease: "sine.inOut", yoyo: true, repeat: 5 }, 23.9);

/* E · SKILL.md is Markdown */
cut("#sECam", 27.20); push("#sECam", 27.20, 5.10, 1.0, 1.07);
rise("#sEWin", 27.20, 90);
__CODE__.forEach(([i, t]) => type(`#sEc${i}`, t, 0.3, 12));
tl.fromTo("#sEPill", { autoAlpha: 0, scale: 0.7 }, { autoAlpha: 1, scale: 1, duration: 0.35, ease: BK }, 29.71);
tl.fromTo("#sEPill", { backgroundPosition: "100% 0%" }, { backgroundPosition: "0% 0%", duration: 1.4, ease: "none", immediateRender: false }, 29.8);
tl.fromTo("#sECl", { autoAlpha: 0, x: -90 }, { autoAlpha: 1, x: 0, duration: 0.4, ease: BK }, 30.91);
tl.to("#sERing", { opacity: 1, duration: 0.2 }, 31.4);
tl.fromTo("#sEMore", { clipPath: "inset(0% 0% 100% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: 2.4, ease: "steps(4)" }, 29.5);
tl.fromTo("#sEWin", { rotation: 0 }, { rotation: -1.2, duration: 0.25, yoyo: true, repeat: 1, ease: "sine.inOut", immediateRender: false }, 30.91);

/* F · companion files */
cut("#sFCam", 33.40); push("#sFCam", 33.40, 5.05, 1.0, 1.05);
rise("#sFWin", 33.42, 80);
[[0, 35.55], [1, 36.54], [2, 37.43]].forEach(([i, t]) => tl.fromTo(`#sFR${i}`, { autoAlpha: 0, x: 60 }, { autoAlpha: 1, x: 0, duration: 0.25, ease: BK }, t));

/* G · one big prompt */
cut("#sGCam", 42.05); push("#sGCam", 42.05, 3.85, 1.0, 1.04);
rise("#sGWin", 42.05, 60);
tl.fromTo("#sGDoc", { y: 0 }, { y: -240, duration: 3.3, ease: "power1.inOut" }, 42.4);
tl.to("#sGHi1", { width: 380, duration: 0.4, ease: "power2.out" }, 43.09);
tl.to("#sGHi2", { width: 440, duration: 0.4, ease: "power2.out" }, 44.5);

/* H · saved once, run with / */
cut("#sHCam", 50.00); push("#sHCam", 50.00, 3.55, 1.0, 1.07);
rise("#sHSaved", 50.02, 60); pop("#sHOk", 50.5);
rise("#sHG", 50.3, 30); rise("#sHChat", 50.45, 60);
tl.set("#sHTx", { autoAlpha: 0 }, 0);
tl.set("#sHTx", { autoAlpha: 1 }, 51.69);
tl.set("#sHPh", { autoAlpha: 0 }, 51.69);
type("#sHTx", 51.69, 0.9, 9);
tl.fromTo("#sHCur", { x: 0, y: 0 }, { x: -60, y: -300, duration: 0.6, ease: "power2.inOut" }, 52.2);
tl.fromTo("#sHSend", { scale: 1 }, { scale: 0.85, duration: 0.08, yoyo: true, repeat: 1, immediateRender: false }, 52.85);
tl.fromTo("#sHPill", { autoAlpha: 0, scale: 0.7 }, { autoAlpha: 1, scale: 1, duration: 0.3, ease: BK }, 52.95);
tl.fromTo("#sHPill", { backgroundPosition: "100% 0%" }, { backgroundPosition: "0% 0%", duration: 0.6, ease: "none", immediateRender: false }, 53.0);

/* L · CTA */
tl.fromTo("#sLWord", { autoAlpha: 0, scale: 1.6 }, { autoAlpha: 1, scale: 1, duration: 0.3, ease: "power4.out" }, __VOEND__ + 0.14);
tl.fromTo("#sLSub", { autoAlpha: 0, y: 30 }, { autoAlpha: 1, y: 0, duration: 0.35, ease: EO }, __VOEND__ + 0.7);
tl.to("#sLCam", { y: -24, duration: 2.0, ease: "sine.inOut" }, __VOEND__ + 0.4);
[[0.5, -2.2], [0.85, 1.8], [1.2, -1.6], [1.55, 2.0], [1.9, -1.2]].forEach(([t, r]) => tl.set(["#v5W", "#sLWord"], { rotation: r }, __VOEND__ + t));

tl.fromTo("#sLWord", { scale: 1 }, { scale: 1.08, duration: 0.18, yoyo: true, repeat: 3, ease: "sine.inOut", immediateRender: false }, __VOEND__ + 1.0);
window.__timelines["main"] = tl;
"""


def main():
    code_t = [[0, 27.45], [1, 27.75], [2, 28.15], [3, 28.6], [4, 28.9], [5, 29.25]]
    js = (TIMELINE.replace("__OVS__", json.dumps([[o[0], o[1], o[2], o[4] is None] for o in OV]))
          .replace("__FBS__", json.dumps([[f"#{v}W", a, b - a] for v, a, b, _, _ in FB]))
          .replace("__SPANS__", json.dumps([[a, b] for a, b, _ in CARD]))
          .replace("__CODE__", json.dumps(code_t))
          .replace("__VOEND__", str(VO_END)))
    doc = f"""<!doctype html>
<html lang="he" data-resolution="portrait">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="gsap.min.js"></script>
<style>{CSS}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
{body()}
</div>
<script>{js}</script>
</body>
</html>
"""
    open("index.html", "w", encoding="utf-8").write(doc)
    print("wrote index.html", len(doc), "bytes")


if __name__ == "__main__":
    main()
