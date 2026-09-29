#!/usr/bin/env python3
"""Build index.html for a style-B (editorial collage) reel. Placeholder copy: replace every "caption text".

Everything time-based lives in the tables below; the HTML/CSS kit is written once.
Run: python3 build.py && npm run check
"""
import html

DUR = 81.0

# ── face windows: (start, end, media_start) on the reel clock ───────────────────────────
CARD = [(0.00, 12.60, 0.00), (12.60, 15.30, 19.00),
        (42.82, 54.54, 22.38), (54.54, 63.03, 34.10), (66.73, 78.48, 46.29)]

# ── full-bleed collage clips ─────────────────────────────────────────────────────────────
FB = [  # id, start, end, src, media_start
    ("v1", 15.30, 19.31, "media/col_stamp.mp4", 0.2),
    ("v2", 22.05, 26.56, "media/col_umbrella.mp4", 0.2),
    ("v3", 26.56, 31.40, "media/col_drawers.mp4", 0.0),
    ("v4", 63.03, 66.73, "media/col_doctor.mp4", 0.6),
    ("v5", 78.48, 81.00, "media/col_sign.mp4", 1.2),
]

# ── collage overlays above the UI scenes (face card stays on top where there is a face) ─────
OV = [  # id, start, end, src, media_start (None = still image)
    ("o1", 0.80, 2.40, "media/col_houses.png", None),
    ("o2", 10.64, 12.26, "media/col_scissors.mp4", 0.4),
    ("o3", 33.90, 35.16, "media/col_shelf.png", None),
    ("o4", 39.52, 41.09, "media/col_head.png", None),
    ("o5", 45.76, 48.00, "media/col_box.png", None),
    ("o6", 53.20, 55.09, "media/col_typewriter.mp4", 0.3),
    ("o7", 56.60, 58.45, "media/col_magnifier.mp4", 0.4),
    ("o8", 70.02, 72.23, "media/col_mechanic.png", None),
]
STILLS = ["houses", "switch", "globe", "scissors", "dollhouse", "drawers", "projector", "head", "typewriter",
          "magnifier", "mail", "box", "mechanic", "doctor"]
BURSTS = [(0.00, 8, 0.10, 0), (35.16, 13, 0.10, 3)]  # start, shots, shot length, first still

# ── captions: (start, end, text) — 1-3 words, split by meaning ─────────────────────────
CAPS = [
    (0.04, 0.98, "caption text"), (0.98, 1.77, "caption text"), (1.77, 2.77, "caption text"),
    (2.77, 3.98, "caption text"), (3.98, 4.82, "<L>Claude Explainer</L>"), (4.82, 5.88, "caption text"),
    (5.88, 6.94, "caption text"), (6.94, 7.86, "<L>CLAUDE.md</L> caption text"), (7.86, 9.07, "caption text"),
    (9.07, 10.64, "caption text"), (10.64, 11.41, "caption text"), (11.41, 12.26, "caption text"),
    (12.26, 13.48, "caption text"), (13.48, 14.72, "caption text"), (14.72, 16.09, "caption text"),
    (16.09, 16.90, "caption text"), (16.90, 17.66, "caption text"), (17.70, 18.62, "caption text"), (18.62, 19.29, "caption text"), (19.31, 20.32, "<L>CLAUDE.md</L>"),
    (20.32, 21.10, "caption text"), (21.10, 22.05, "caption text"), (22.05, 23.42, "caption text"), (23.42, 24.99, "caption text"),
    (24.99, 26.30, "caption text"), (26.56, 27.64, "caption text"), (27.64, 28.56, "caption text"),
    (28.56, 29.48, "caption text"), (29.48, 30.44, "caption text"), (30.44, 31.40, "caption text"),
    (31.40, 32.62, "caption text"), (32.62, 33.34, "caption text"), (33.34, 33.92, "caption text"), (33.92, 35.16, "caption text"),
    (35.16, 35.68, "caption text"), (35.68, 36.88, "caption text"), (36.88, 38.04, "caption text"),
    (38.04, 39.52, "caption text"), (39.52, 40.24, "caption text"), (40.24, 41.04, "caption text"),
    (41.09, 41.86, "caption text"), (41.86, 42.82, "caption text"), (42.82, 44.46, "caption text"), (44.46, 45.76, "caption text"),
    (45.76, 46.90, "caption text <L>MD</L>"), (46.90, 48.00, "caption text"), (48.00, 49.17, "caption text"), (49.17, 49.69, "caption text"), (49.69, 50.47, "caption text"), (50.47, 51.60, "caption text"),
    (51.60, 53.18, "<L>forward /</L>"), (53.18, 55.04, "<L>/init</L>"), (55.09, 55.56, "caption text"), (55.56, 56.60, "caption text"), (56.60, 57.15, "caption text"), (57.15, 58.45, "caption text"),
    (58.45, 59.79, "caption text <L>MD</L>"), (59.79, 61.54, "caption text"), (61.54, 62.98, "caption text"),
    (63.03, 64.34, "caption text"), (64.34, 65.49, "caption text"), (65.49, 66.06, "caption text"), (66.06, 67.18, "caption text"),
    (67.18, 68.42, "caption text"), (68.42, 70.02, "caption text"), (70.02, 71.12, "caption text <L>Claude Code</L>"),
    (71.13, 72.23, "caption text"), (72.23, 73.31, "caption text"), (73.31, 74.32, "caption text <L>Claude Code</L>"), (74.36, 75.26, "caption text"), (75.26, 75.88, "caption text"),
    (75.88, 76.51, "caption text"), (76.51, 77.14, "<L>forward /</L>"), (77.14, 78.48, "<L>/doctor</L>"),
]
CARD_ON = [(a, b) for a, b, _ in CARD]


def cap_html(t):
    t = html.escape(t).replace("&lt;L&gt;", '<span class="ltr">').replace("&lt;/L&gt;", "</span>")
    return t


def on_card(a):
    return any(s - 0.01 <= a < e for s, e in CARD_ON)


# scene starts get a whoosh
CUTS = [17.70, 24.17, 28.84, 65.09, 0.80, 2.40, 10.64, 12.26, 33.90, 39.52, 45.76, 53.20, 56.60, 58.45, 62.24, 70.02, 72.23, 6.31, 12.26, 15.30, 19.31, 22.05, 26.56, 31.40, 35.16, 36.48, 41.09, 48.00, 55.09, 63.03,
        66.73, 74.36, 78.48]

CSS = r"""
@font-face{font-family:'NSH';font-weight:300 900;src:url('fonts/NotoSansHebrew-hebrew.woff2') format('woff2');unicode-range:U+0590-05FF,U+FB1D-FB4F}
@font-face{font-family:'NSH';font-weight:300 900;src:url('fonts/NotoSansHebrew-latin.woff2') format('woff2');unicode-range:U+0000-00FF,U+2000-206F}
@font-face{font-family:'JB';font-weight:400;src:url('fonts/JetBrainsMono-400.woff2') format('woff2')}
@font-face{font-family:'JB';font-weight:700;src:url('fonts/JetBrainsMono-700.woff2') format('woff2')}
@font-face{font-family:'FR';src:url('fonts/FrankRuhl-hebrew.woff2') format('woff2');unicode-range:U+0590-05FF}
@font-face{font-family:'FR';src:url('fonts/FrankRuhl-latin.woff2') format('woff2');unicode-range:U+0000-00FF,U+2000-206F}
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;overflow:hidden;background:#f7f7f5}
body{font-family:'NSH',sans-serif;color:#1d1d1b}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;background:#f7f7f5}
.ltr{direction:ltr;unicode-bidi:isolate;font-family:'JB',monospace}
.bg{position:absolute;inset:0;background-color:#f7f7f5;
  background-image:radial-gradient(circle,#d6d6d2 1.6px,transparent 1.8px);background-size:26px 26px}
.scene{position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:hidden}
.cam{position:absolute;left:0;top:0;width:1080px;height:1920px}
.fb{position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover;display:block}
.still{position:absolute;left:0;top:0;width:1080px;height:1920px;background-size:cover;background-position:center}

/* face card */
#card{position:absolute;left:375px;top:1690px;width:330px;height:194px;border-radius:30px;overflow:hidden;z-index:30;
  box-shadow:0 18px 44px rgba(0,0,0,.22),0 0 0 4px #fff}
#card video{position:absolute;left:0;top:0;width:330px;height:194px;object-fit:cover;object-position:50% 20%;display:block;
  filter:contrast(1.04) saturate(1.05)}

/* captions */
.capRow{position:absolute;left:0;width:1080px;height:84px;z-index:40;display:flex;justify-content:center;align-items:center}
#capCard{top:1572px} #capFull{top:1572px}
.cap{direction:rtl;white-space:nowrap}
.cap .ltr{font-size:1.1em}
.cap span.c{display:inline-block;padding:4px 18px 6px;border-radius:2px;background:rgba(30,30,30,.92);
  font-size:42px;line-height:58px;font-weight:500;color:#fff;letter-spacing:.5px}

/* UI kit */
.win{position:absolute;background:#fff;border-radius:30px;overflow:hidden;
  box-shadow:0 28px 70px rgba(20,20,20,.14),0 0 0 1.5px rgba(0,0,0,.07)}
.dwin{position:absolute;background:rgba(28,28,30,.94);border-radius:26px;overflow:hidden;color:#e9e9e7;
  box-shadow:0 28px 70px rgba(0,0,0,.35),0 0 0 1.5px rgba(255,255,255,.06)}
.bar{height:66px;position:relative;border-bottom:1.5px solid rgba(0,0,0,.07)}
.dwin .bar{border-bottom:1.5px solid rgba(255,255,255,.08)}
.bar i{position:absolute;top:24px;width:18px;height:18px;border-radius:50%}
.bar i:nth-child(1){left:26px;background:#FF5F57}.bar i:nth-child(2){left:54px;background:#FEBC2E}.bar i:nth-child(3){left:82px;background:#28C840}
.bar b{position:absolute;left:0;right:0;top:0;line-height:66px;text-align:center;font-family:'JB',monospace;font-weight:700;font-size:26px;color:#8a8a86;direction:ltr}
.row{position:relative;height:88px;line-height:88px;padding-left:40px;font-family:'JB',monospace;font-size:42px;direction:ltr;white-space:nowrap}
.row .ic{display:inline-block;width:34px;height:26px;margin-right:18px;border-radius:5px;vertical-align:-2px;background:#6aa7ff}
.row .fi{display:inline-block;width:26px;height:32px;margin-right:22px;border-radius:4px;vertical-align:-4px;background:#bdbdb8}
.row .hlrow{position:absolute;left:14px;right:14px;top:6px;bottom:6px;border-radius:12px;background:#16a34a;opacity:0}
.row span{position:relative}
.folder{position:absolute;width:150px;height:118px}
.folder::before{content:"";position:absolute;left:0;top:0;width:62px;height:26px;border-radius:12px 12px 0 0;background:#16a34a}
.folder::after{content:"";position:absolute;left:0;top:16px;width:150px;height:102px;border-radius:14px;
  background:linear-gradient(#34d27a,#1fae55);box-shadow:0 14px 30px rgba(20,140,70,.35)}
.folder .st{position:absolute;left:47px;top:38px;width:56px;height:56px;z-index:2;background:#fff;
  -webkit-mask:url(media/logos/claude.svg) center/contain no-repeat;mask:url(media/logos/claude.svg) center/contain no-repeat}
.claude{background:#D97757;-webkit-mask:url(media/logos/claude.svg) center/contain no-repeat;mask:url(media/logos/claude.svg) center/contain no-repeat}
.md{padding:34px 44px;direction:rtl}
.md .h1{font-family:'JB',monospace;font-weight:700;font-size:46px;line-height:76px;direction:ltr;text-align:left;color:#1d1d1b}
.md .h2{font-weight:800;font-size:54px;line-height:92px;color:#1d1d1b;margin-top:10px}
.md .li{position:relative;font-size:50px;line-height:86px;color:#3a3a37}
.md .li i{position:absolute;right:-6px;top:14px;height:46px;width:0;background:rgba(34,197,94,.30);border-radius:6px;z-index:-1}
.gl{height:18px;border-radius:9px;background:#e6e6e2;margin:22px 0}
.chat{position:absolute;left:90px;width:900px;height:210px;background:#fff;border-radius:38px;
  box-shadow:0 18px 50px rgba(20,20,20,.10),0 0 0 1.5px rgba(0,0,0,.08)}
.chat .tx{position:absolute;left:40px;top:34px;font-family:'JB',monospace;font-size:48px;color:#1d1d1b;direction:ltr;white-space:nowrap;overflow:hidden}
.chat .ph{position:absolute;left:40px;top:40px;font-size:40px;color:#7c7c77}
.chat .plus{position:absolute;left:34px;bottom:30px;font-size:52px;line-height:52px;color:#8a8a86}
.chat .send{position:absolute;right:30px;bottom:26px;width:66px;height:66px;border-radius:16px;background:#16a34a}
.chat .send::after{content:"";position:absolute;left:25px;top:18px;border-left:8px solid transparent;border-right:8px solid transparent;border-bottom:14px solid #fff}
.chat .send::before{content:"";position:absolute;left:31px;top:30px;width:4px;height:20px;background:#fff}
.caret{display:inline-block;width:4px;height:52px;background:#1d1d1b;vertical-align:-8px;margin-left:4px}
.greet{position:absolute;left:0;right:0;text-align:center;font-family:'FR',serif;font-size:66px;color:#2b2b28;direction:rtl}
.greet .claude{display:inline-block;width:60px;height:60px;vertical-align:-6px;margin-left:18px}
.pill{position:absolute;height:120px;border-radius:60px;padding:0 54px 0 110px;line-height:120px;font-size:54px;font-weight:700;color:#fff;
  background:linear-gradient(90deg,#1b1b1b 0%,#1b1b1b 40%,#22C55E 60%,#1b1b1b 80%);background-size:300% 100%;white-space:nowrap;direction:ltr}
.pill::before{content:"";position:absolute;left:44px;top:34px;width:52px;height:52px;background:#fff;clip-path:polygon(50% 0,62% 38%,100% 50%,62% 62%,50% 100%,38% 62%,0 50%,38% 38%)}
.cursor{position:absolute;width:60px;height:60px;z-index:25}
.cursor svg{width:60px;height:60px;display:block}
.fcard{position:absolute;left:120px;width:840px;height:250px;background:#fff;border-radius:30px;
  box-shadow:0 20px 50px rgba(20,20,20,.10),0 0 0 1.5px rgba(0,0,0,.08);direction:rtl}
.fcard .t{position:absolute;right:44px;top:40px;font-size:56px;font-weight:800}
.fcard .p{position:absolute;right:44px;top:124px;font-family:'JB',monospace;font-size:34px;color:#8a8a86;direction:ltr}
.fcard .d{position:absolute;left:44px;top:92px;font-size:36px;color:#6a6a66}
.fcard .ring{position:absolute;inset:-6px;border-radius:36px;border:5px solid #22C55E;opacity:0}
.ok{position:absolute;width:86px;height:86px;border-radius:50%;background:#1f9d55;color:#fff;font-size:56px;line-height:86px;text-align:center;font-weight:900}
.q{position:absolute;width:86px;height:86px;border-radius:50%;background:#e9e9e5;color:#8a8a86;font-size:54px;line-height:86px;text-align:center;font-weight:900}
.ctx{position:absolute;left:110px;top:620px;width:860px;height:620px;border-radius:34px;border:4px dashed #c9c9c4;background:rgba(255,255,255,.9)}
 .ctx .lbl{position:absolute;left:200px;right:200px;top:-72px;background:#fff;border-radius:10px;text-align:center;font-family:'JB',monospace;font-size:34px;letter-spacing:8px;color:#8a8a86;direction:ltr}
.blk{position:absolute;left:40px;width:780px;height:150px;border-radius:24px;color:#fff;font-size:48px;font-weight:800;line-height:150px;text-align:center}
.flash{position:absolute;inset:0;display:flex;align-items:center;justify-content:center}
.tagline{position:absolute;left:0;right:0;text-align:center;font-family:'JB',monospace;font-size:30px;letter-spacing:10px;color:#9a9a95;direction:ltr}
.sign{position:absolute;left:0;right:0;text-align:center;direction:rtl}
"""

CURSOR = ('<svg viewBox="0 0 24 24"><path d="M4 2 L4 20 L9 15.5 L12.5 22 L15.5 20.6 L12.2 14.3 L19 14.3 Z" '
          'fill="#111" stroke="#fff" stroke-width="1.4" stroke-linejoin="round"/></svg>')


def clip(id_, a, b, track, inner, cls="scene", extra=""):
    return (f'<div id="{id_}" class="clip {cls}" data-start="{a:.2f}" data-duration="{b - a:.2f}" '
            f'data-track-index="{track}" data-layout-allow-overlap data-layout-allow-overflow{extra}>{inner}</div>')


def scenes():
    s = []
    # S2 finder (0 - 6.31): dark window + folder icon, top half only
    s.append(clip("sA", 0.00, 6.31, 5, f'''<div class="bg"></div><div class="cam" id="sACam">
      <div class="folder" id="sAFold" style="left:820px;top:470px"><div class="st"></div></div>
      <div class="dwin" id="sAWin" style="left:100px;top:660px;width:880px;height:640px">
        <div class="bar"><i></i><i></i><i></i><b>claude-explainer</b></div>
        <div style="padding-top:16px">
          <div class="row"><span class="ic"></span><span>.playwright-mcp</span></div>
          <div class="row"><span class="ic"></span><span>assets</span></div>
          <div class="row"><span class="ic"></span><span>data</span></div>
          <div class="row"><span class="ic"></span><span>web-media</span></div>
          <div class="row" id="sARow"><div class="hlrow" id="sAHl"></div><span class="fi" style="background:#22C55E"></span><span id="sAName">CLAUDE.md</span></div>
          <div class="row"><span class="fi"></span><span>index.html</span></div>
        </div></div>
      <div id="sATitle" class="greet" style="top:330px;font-size:72px"><span class="ltr" style="font-family:'FR',serif">Claude Explainer</span></div>
      <div class="cursor" id="sACur" style="left:760px;top:1290px">{CURSOR}</div></div>'''))
    # S3 doc (6.31 - 12.26)
    s.append(clip("sB", 6.31, 12.26, 5, '''<div class="bg"></div><div class="cam" id="sBCam">
      <div class="win" id="sBWin" style="left:90px;top:320px;width:900px;height:1040px">
        <div class="bar"><i></i><i></i><i></i><b>claude-explainer / CLAUDE.md</b></div>
        <div class="md">
          <div class="h1" id="sBH1">#  CLAUDE.md</div>
          <div class="gl" style="width:70%;margin-right:auto"></div><div class="gl" style="width:52%;margin-right:auto"></div>
          <div class="h2" id="sBH2">## caption text</div>
          <div class="li" id="sBL1"><i id="sBHi"></i>• caption text</div>
          <div class="li" id="sBL2">• caption text</div>
          <div class="gl" style="width:64%;margin-right:auto;margin-top:40px"></div><div class="gl" style="width:44%;margin-right:auto"></div>
        </div></div>
      <div class="tagline" id="sBTag" style="top:240px">PROJECT · CLAUDE.md</div></div>'''))
    # S4 globe still behind card (12.26 - 15.30)
    s.append(clip("sC", 12.26, 15.30, 5, '''<div class="cam" id="sCCam"><div class="still bdrop" style="background-image:url(media/col_globe.png)"></div></div>
      <div class="tagline" id="sCTag" style="top:120px;color:#6a6a66">GLOBAL · ~/.claude/CLAUDE.md</div>'''))
    # S6 chat path (19.31 - 22.05)
    s.append(clip("sD", 19.31, 22.05, 5, f'''<div class="still bdrop" style="background-image:url(media/col_globe.png);filter:blur(3px) brightness(.93)"></div><div class="still" style="background:rgba(247,247,245,.28)"></div><div class="cam" id="sDCam">
      <div class="greet" id="sDG" style="top:740px;left:200px;right:200px;background:#fff;border-radius:22px;padding:14px 0;box-shadow:0 10px 30px rgba(0,0,0,.12)"><span class="claude"></span>caption text</div>
      <div class="chat" id="sDChat" style="top:950px"><div class="tx" id="sDTx">~/.claude/CLAUDE.md</div><div class="plus">+</div><div class="send"></div></div>
      <div class="tagline" id="sDTag" style="top:1240px;left:300px;right:300px;background:#fff;border-radius:10px;color:#55554f">ALL PROJECTS</div></div>'''))
    # S9 two levels (31.40 - 35.16)
    s.append(clip("sE", 31.40, 35.16, 5, '''<div class="still bdrop" style="background-image:url(media/col_dollhouse.png);filter:blur(3px) brightness(.93)"></div><div class="still" style="background:rgba(247,247,245,.28)"></div><div class="cam" id="sECam">
      <div class="tagline" style="top:430px;left:340px;right:340px;background:#fff;border-radius:10px;color:#55554f">TWO LEVELS</div>
      <div class="fcard" id="sEG" style="top:530px"><div class="t">caption text</div><div class="p">~/.claude/CLAUDE.md</div><div class="d">caption text</div></div>
      <div class="fcard" id="sEP" style="top:870px"><div class="ring" id="sERing"></div><div class="t">caption text</div><div class="p">./CLAUDE.md</div><div class="d">caption text</div></div>
      <div class="cursor" id="sECur" style="left:760px;top:1220px">''' + CURSOR + '''</div></div>'''))
    # S11 context window (36.48 - 41.09)
    s.append(clip("sF", 36.48, 41.09, 5, '''<div class="still bdrop" style="background-image:url(media/col_projector.png);filter:blur(3px) brightness(.93)"></div><div class="still" style="background:rgba(247,247,245,.28)"></div><div class="cam" id="sFCam">
      <div class="ctx" id="sFCtx"><div class="lbl">CONTEXT WINDOW</div>
        <div class="blk" id="sFB1" style="top:60px;background:#1d1d1b">CLAUDE.md caption text</div>
        <div class="blk" id="sFB2" style="top:240px;background:#15803d">CLAUDE.md caption text</div>
        <div class="blk" id="sFB3" style="top:420px;background:#e9e9e5;color:#55554f;font-weight:500">caption text…</div></div>
      <div class="pill" id="sFPill" style="left:250px;top:1290px">every session</div></div>'''))
    # S12-13 folder without CLAUDE.md (41.09 - 48.00)
    s.append(clip("sG", 41.09, 48.00, 5, '''<div class="still bdrop" style="background-image:url(media/col_mail.png);filter:blur(3px) brightness(.93)"></div><div class="still" style="background:rgba(247,247,245,.28)"></div><div class="cam" id="sGCam">
      <div class="folder" id="sGFold" style="left:465px;top:340px"><div class="st"></div></div>
      <div class="win" id="sGWin" style="left:110px;top:560px;width:860px;height:560px">
        <div class="bar"><i></i><i></i><i></i><b>my-new-project</b></div>
        <div style="padding-top:16px">
          <div class="row"><span class="ic"></span><span>src</span></div>
          <div class="row"><span class="ic"></span><span>public</span></div>
          <div class="row"><span class="fi"></span><span>package.json</span></div>
          <div class="row" id="sGMiss" style="color:#c0392b"><span class="fi" style="background:none;border:3px dashed #c0392b"></span><span>CLAUDE.md ?</span></div>
        </div></div></div>'''))
    # S14 /init (48.00 - 55.09)
    s.append(clip("sH", 48.00, 55.09, 5, f'''<div class="still bdrop" style="background-image:url(media/col_switch.png);filter:blur(3px) brightness(.93)"></div><div class="still" style="background:rgba(247,247,245,.28)"></div><div class="cam" id="sHCam">
      <div class="greet" id="sHG" style="top:740px;left:170px;right:170px;background:#fff;border-radius:22px;padding:14px 0;box-shadow:0 10px 30px rgba(0,0,0,.12)"><span class="claude"></span>caption text?</div>
      <div class="chat" id="sHChat" style="top:950px"><div class="ph" id="sHPh">caption text…</div>
        <div class="tx" id="sHTx">/init</div><div class="plus">+</div><div class="send" id="sHSend"></div></div>
      <div class="cursor" id="sHCur" style="left:990px;top:1290px">{CURSOR}</div></div>'''))
    # S15 generating → doc (55.09 - 63.03)
    lines = "".join(f'<div class="gl" style="width:{w}%;margin-right:auto"></div>' for w in
                    (88, 72, 95, 60, 83, 70, 91, 55, 78, 86, 64, 90, 58, 80, 74, 93, 61, 85))
    s.append(clip("sI", 55.09, 63.03, 5, f'''<div class="bg"></div><div class="cam" id="sICam">
      <div class="win" id="sIWin" style="left:90px;top:200px;width:900px;height:1180px">
        <div class="bar"><i></i><i></i><i></i><b>my-new-project / CLAUDE.md</b></div>
        <div style="position:absolute;top:68px;left:0;right:0;bottom:0;overflow:hidden"><div class="md" id="sIDoc"><div class="h1">#  CLAUDE.md</div>
          <div class="h2">## caption text</div>{lines[:len(lines)//2]}
          <div class="h2">## caption text</div>{lines[len(lines)//2:]}</div></div></div>
      <div class="pill" id="sIPill" style="left:270px;top:700px;z-index:3">Generating</div></div>'''))
    # S17 check both files (66.73 - 74.36)
    s.append(clip("sJ", 66.73, 74.36, 5, '''<div class="still bdrop" style="background-image:url(media/col_drawers.png);filter:blur(3px) brightness(.93)"></div><div class="still" style="background:rgba(247,247,245,.28)"></div><div class="cam" id="sJCam">
      <div class="tagline" style="top:430px;left:330px;right:330px;background:#fff;border-radius:10px;color:#55554f">SETUP CHECK</div>
      <div class="fcard" id="sJG" style="top:530px"><div class="ring" id="sJRG"></div><div class="t">caption text</div><div class="p">~/.claude/CLAUDE.md</div><div class="q" id="sJQG" style="left:44px;top:82px">?</div></div>
      <div class="fcard" id="sJP" style="top:870px"><div class="ring" id="sJRP"></div><div class="t">caption text</div><div class="p">./CLAUDE.md</div><div class="q" id="sJQP" style="left:44px;top:82px">?</div></div></div>'''))
    # S18 /doctor (74.36 - 78.48)
    s.append(clip("sK", 74.36, 78.48, 5, f'''<div class="bg"></div><div class="cam" id="sKCam">
      <div class="greet" id="sKG" style="top:330px"><span class="claude"></span>caption text</div>
      <div class="chat" id="sKChat" style="top:470px"><div class="ph" id="sKPh">caption text…</div><div class="tx" id="sKTx">/doctor</div><div class="plus">+</div><div class="send" id="sKSend"></div></div>
      <div class="fcard" id="sKR1" style="top:780px;height:150px"><div class="t" style="top:36px;font-size:46px">CLAUDE.md caption text</div><div class="ok" id="sKO1" style="left:40px;top:32px"><svg viewBox="0 0 24 24" style="width:54px;height:54px;margin-top:16px"><path d="M5 12.5l4.2 4.2L19 7" fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/></svg></div></div>
      <div class="fcard" id="sKR2" style="top:960px;height:150px"><div class="t" style="top:36px;font-size:46px">CLAUDE.md caption text</div><div class="ok" id="sKO2" style="left:40px;top:32px"><svg viewBox="0 0 24 24" style="width:54px;height:54px;margin-top:16px"><path d="M5 12.5l4.2 4.2L19 7" fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/></svg></div></div>
      <div class="cursor" id="sKCur" style="left:900px;top:840px">{CURSOR}</div></div>'''))
    # CTA text over the sign video (78.48 - 81)
    s.append(clip("sL", 78.48, 81.00, 8, '''<div class="cam" id="sLCam">
      <div class="sign" id="sLWord" style="top:470px;font-size:190px;font-weight:900;color:#141414;line-height:200px">caption text</div></div>
      <div class="sign" id="sLSub" style="top:1560px"><span style="display:inline-block;padding:6px 24px 8px;border-radius:6px;background:#22C55E;color:#0b0b0b;font-size:48px;font-weight:800;line-height:64px">caption text</span></div>'''))
    return "\n".join(s)


def body():
    out = ['<div class="bg"></div>']
    # full-bleed collage videos
    for vid, a, b, src, ms in FB:
        out.append(f'<div class="scene" id="{vid}W" style="z-index:4"><video id="{vid}" class="clip fb" src="{src}" '
                   f'data-start="{a:.2f}" data-duration="{b - a:.2f}" data-media-start="{ms}" data-track-index="3" muted playsinline></video></div>')
    out.append('<div id="scenes" style="position:absolute;inset:0;z-index:10">' + scenes() + '</div>')
    # overlays
    for oid, a, b, src, ms in OV:
        if ms is None:
            inner = f'<div class="still" id="{oid}I" style="background-image:url({src})"></div>'
            out.append(clip(oid, a, b, 7, inner, extra=' style="z-index:12"'))
        else:
            out.append(f'<div class="scene" id="{oid}W" style="z-index:12"><video id="{oid}" class="clip fb" src="{src}" '
                       f'data-start="{a:.2f}" data-duration="{b - a:.2f}" data-media-start="{ms}" data-track-index="8" muted playsinline></video></div>')
    # bursts
    for bi, (t0, n, L, first) in enumerate(BURSTS):
        for k in range(n):
            a = t0 + k * L
            img = STILLS[(first + k) % len(STILLS)]
            sc = 1.0 + 0.35 * ((k * 7) % 5) / 4
            inner = (f'<div class="still" style="background-image:url(media/col_{img}.png);'
                     f'transform:scale({sc:.2f});transform-origin:{30 + (k * 23) % 40}% {25 + (k * 17) % 40}%"></div>')
            out.append(clip(f"b{bi}_{k}", a, (a + L + 0.03) if k == n - 1 else a + L, 9 + (k % 2), inner, extra=' style="z-index:14"'))
            out.append(f'<audio id="bt{bi}_{k}" class="clip" src="media/sfx/tick.wav" data-start="{a:.2f}" '
                       f'data-duration="0.05" data-track-index="{39 + k % 2}" data-volume="0.65"></audio>')
    # face card
    vids = "".join(
        f'<video id="face{i}" class="clip" src="media/face_up.mp4" data-start="{a:.2f}" data-duration="{b - a:.2f}" '
        f'data-media-start="{m:.2f}" data-track-index="1" muted playsinline></video>' for i, (a, b, m) in enumerate(CARD))
    out.append(f'<div id="card">{vids}</div>')
    # captions
    rc, rf = [], []
    for i, (a, b, t) in enumerate(CAPS):
        row = rc if on_card(a) else rf
        tr = 20 + (i % 2) + (0 if row is rc else 2)
        row.append(f'<div id="cap{i:02d}" class="clip cap" data-start="{a:.2f}" data-duration="{b - a:.2f}" '
                   f'data-track-index="{tr}"><span class="c">{cap_html(t)}</span></div>')
    out.append('<div class="capRow" id="capCard">' + "".join(rc) + '</div>')
    out.append('<div class="capRow" id="capFull">' + "".join(rf) + '</div>')
    # CTA chip (card row position is free at the end)
    out.append('<div class="capRow" id="capCta" style="top:1440px"><div id="capCtaC" class="clip cap" data-start="78.60" '
               'data-duration="2.40" data-track-index="26"><span class="c" style="font-size:58px">caption text</span></div></div>')
    # audio
    out.append('<audio id="aVo" class="clip" src="media/vo.wav" data-start="0" data-duration="78.48" data-track-index="30" data-volume="1"></audio>')
    out.append(f'<audio id="aMusic" class="clip" src="media/music_bed.mp3" data-start="0" data-duration="{DUR}" data-media-start="0" data-track-index="31" data-volume="0.09"></audio>')
    for i, (a, b) in enumerate([(0.0, 2.4), (15.30, 19.31), (22.05, 31.40), (35.16, 36.48), (63.03, 66.73)]):
        out.append(f'<audio id="mUp{i}" class="clip" src="media/music_bed.mp3" data-start="{a:.2f}" data-duration="{b - a:.2f}" data-media-start="{a:.2f}" data-track-index="{41 + i % 2}" data-volume="0.30"></audio>')
    out.append('<audio id="aMusicEnd" class="clip" src="media/music_bed.mp3" data-start="78.48" data-duration="2.52" data-media-start="78.48" data-track-index="32" data-volume="0.40"></audio>')
    for i, t in enumerate(sorted(set(CUTS))):
        out.append(f'<audio id="w{i}" class="clip" src="media/sfx/whoosh.wav" data-start="{max(0, t - 0.08):.2f}" data-duration="0.57" data-track-index="{33 + i % 2}" data-volume="0.70"></audio>')
    for i, t in enumerate([6.20, 11.05, 51.60, 54.90, 76.51, 77.75, 78.05, 68.90, 71.62, 32.9, 77.85, 78.15, 79.20, 75.50]):
        out.append(f'<audio id="k{i}" class="clip" src="media/sfx/click.wav" data-start="{t:.2f}" data-duration="0.09" data-track-index="{35 + i % 2}" data-volume="0.85"></audio>')
    typ = [51.6 + k * 0.58 for k in range(5)] + [76.51 + k * 0.16 for k in range(7)] + [19.7 + k * 0.05 for k in range(18)] + [6.7 + k * 0.05 for k in range(10)]
    for i, t in enumerate(typ):
        out.append(f'<audio id="ty{i}" class="clip" src="media/sfx/tick.wav" data-start="{t:.2f}" data-duration="0.05" data-track-index="{43 + i % 2}" data-volume="0.35"></audio>')
    out.append('<audio id="aBoom" class="clip" src="media/sfx/boom.wav" data-start="78.48" data-duration="2.52" data-track-index="38" data-volume="0.38"></audio>')
    return "\n".join(out)


TIMELINE = r"""
const OVS = __OVS__;
const JIT = [[0,0,0],[-6,4,-0.8],[5,-3,0.6],[-3,-5,-0.4],[6,3,0.9],[-4,6,-0.6],[3,-4,0.5],[0,5,-0.9]];
const tl = gsap.timeline({ paused: true });
const EO = "power3.out", BK = "back.out(1.8)";
const push = (sel, t, d, a = 1, b = 1.05) => tl.fromTo(sel, { scale: a }, { scale: b, duration: d, ease: "none" }, t);
const pop = (sel, t, e = BK, d = 0.34) => tl.fromTo(sel, { autoAlpha: 0, scale: 0.6 }, { autoAlpha: 1, scale: 1, duration: d, ease: e }, t);
const rise = (sel, t, y = 60) => tl.fromTo(sel, { autoAlpha: 0.6, y }, { autoAlpha: 1, y: 0, duration: 0.3, ease: EO }, t);
const type = (sel, t, d, n) => tl.fromTo(sel, { clipPath: "inset(0% 100% 0% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: d, ease: `steps(${n})` }, t);
const cut = (sel, t) => tl.fromTo(sel, { scale: 1.08 }, { scale: 1, duration: 0.28, ease: EO }, t);

/* face card: visible only on face windows; slides up at each entry */
tl.set("#card", { autoAlpha: 0 }, 0);
__SPANS__.forEach(([on, off], i) => {
  if (on < 0.05) tl.set("#card", { autoAlpha: 1 }, 0);
  else tl.fromTo("#card", { autoAlpha: 1, y: 160, scale: 0.9 }, { autoAlpha: 1, y: 0, scale: 1, duration: 0.22, ease: BK, immediateRender: false }, on);
  tl.set("#card", { autoAlpha: 0 }, off);
});
tl.set("#card", { autoAlpha: 0 }, 78.48);
push("#card video", 0, 78.48, 1.0, 1.04);

/* A · finder */
push("#sACam", 0, 6.31, 1.0, 1.06);
tl.fromTo("#sAWin", { scale: 1.1 }, { scale: 1, duration: 0.35, ease: EO }, 2.40);
tl.fromTo("#sAFold", { y: -40 }, { y: 0, duration: 0.4, ease: BK }, 2.40);
tl.fromTo("#sATitle", { autoAlpha: 0, y: 30 }, { autoAlpha: 1, y: 0, duration: 0.35, ease: EO }, 3.98);
tl.fromTo("#sACur", { x: 0, y: 0 }, { x: -380, y: -420, duration: 1.1, ease: "power2.inOut" }, 4.9);
tl.to("#sAHl", { opacity: 0.9, duration: 0.12 }, 6.05);
tl.to("#sAName", { color: "#ffffff", duration: 0.12 }, 6.05);
tl.to("#sAFold", { rotation: -6, duration: 0.5, ease: "sine.inOut", yoyo: true, repeat: 5 }, 0.4);

/* B · doc */
cut("#sBCam", 6.31); push("#sBWin", 6.31, 5.95, 1.0, 1.05);
rise("#sBWin", 6.31, 90);
type("#sBH1", 6.7, 0.5, 11);
type("#sBH2", 9.1, 0.6, 14);
type("#sBL1", 10.6, 0.5, 13);
tl.to("#sBHi", { width: 390, duration: 0.45, ease: "power2.out" }, 11.1);
tl.fromTo("#sBL2", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, 11.6);

/* C · globe behind card */
cut("#sCCam", 12.26); push("#sCCam", 12.26, 3.04, 1.0, 1.10);
rise("#sCTag", 12.5, 20);

/* full-bleed collage: slow push on every clip */
[["#v1W", 15.30, 4.01], ["#v2W", 22.05, 4.51], ["#v3W", 26.56, 4.84], ["#v4W", 63.03, 3.70], ["#v5W", 78.48, 2.52]].forEach(([s, t, d]) => {
  tl.fromTo(s, { scale: 1.10 }, { scale: 1.0, duration: 0.3, ease: EO }, t);
  tl.to(s, { scale: 1.05, duration: d - 0.3, ease: "none" }, t + 0.3);
});

[["#v1W", 17.70], ["#v2W", 24.17], ["#v3W", 28.84], ["#v4W", 65.09]].forEach(([el, t], i) => {
  tl.set(el, { transformOrigin: ["50% 30%", "50% 60%", "70% 45%", "40% 40%"][i] }, t);
  tl.fromTo(el, { scale: 1.42 }, { scale: 1.36, duration: 0.3, ease: EO, immediateRender: false }, t);
});
["#v1W", "#v2W", "#v3W", "#v4W"].forEach((el, i) => {
  const [a, b] = [[15.30, 19.31], [22.05, 26.56], [26.56, 31.40], [63.03, 66.73]][i];
  for (let t = a + 0.25, k = 1; t < b; t += 0.25, k++) { const [x, y, r] = JIT[(k + i) % JIT.length]; tl.set(el, { x: x * 0.7, y: y * 0.7, rotation: r * 0.5 }, t); }
});

document.querySelectorAll(".bdrop").forEach((el, i) => {
  const sc = el.closest(".clip"); const a = +sc.dataset.start, b = a + +sc.dataset.duration;
  tl.fromTo(el, { scale: 1.04 }, { scale: 1.12, duration: b - a, ease: "none" }, a);
  for (let t = a + 0.25, k = 1; t < b; t += 0.25, k++) { const [x, y, r] = JIT[(k + i) % JIT.length]; tl.set(el, { x: x * 1.4, y: y * 1.4, rotation: r * 0.6 }, t); }
});

/* D · global path */
cut("#sDCam", 19.31); push("#sDCam", 19.31, 2.74, 1.0, 1.05);
rise("#sDG", 19.35, 30);
rise("#sDChat", 19.45, 60);
type("#sDTx", 19.7, 0.9, 19);
rise("#sDTag", 20.8, 20);

/* E · two levels */
cut("#sECam", 31.40); push("#sECam", 31.40, 3.76, 1.0, 1.05);
rise("#sEG", 31.45, 60); rise("#sEP", 31.75, 60);
tl.to("#sEG", { opacity: 0.45, duration: 0.3 }, 32.7);
tl.to("#sERing", { opacity: 1, duration: 0.2 }, 32.9);
tl.fromTo("#sEP", { scale: 1 }, { scale: 1.06, duration: 0.3, ease: BK, immediateRender: false }, 32.9);
tl.fromTo("#sECur", { x: 0, y: 0 }, { x: -160, y: -200, duration: 0.8, ease: "power2.inOut" }, 32.1);

/* stop-motion jitter + push on overlay stills and overlay videos */
OVS.forEach(([id, a, b, still]) => {
  const el = still ? `#${id}I` : `#${id}W`;
  tl.fromTo(el, { scale: 1.12 }, { scale: 1.0, duration: 0.28, ease: EO }, a);
  tl.to(el, { scale: 1.05, duration: b - a - 0.28, ease: "none" }, a + 0.28);
  if (still) for (let t = a + 0.25, k = 1; t < b; t += 0.25, k++) {
    const [x, y, r] = JIT[k % JIT.length]; tl.set(el, { x, y, rotation: r }, t);
  }
});

/* F · context window */
cut("#sFCam", 36.48); push("#sFCam", 36.48, 4.61, 1.0, 1.05);
tl.fromTo("#sFCtx", { scale: 0.94 }, { scale: 1, duration: 0.15, ease: BK }, 36.48);
tl.fromTo("#sFB1", { autoAlpha: 1, scale: 0.92 }, { autoAlpha: 1, scale: 1, duration: 0.15, ease: BK }, 36.48);
tl.fromTo("#sFB2", { autoAlpha: 0, y: -600 }, { autoAlpha: 1, y: 0, duration: 0.4, ease: "bounce.out" }, 38.04);
tl.fromTo("#sFB3", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, 39.0);
tl.fromTo("#sFPill", { autoAlpha: 0, scale: 0.7 }, { autoAlpha: 1, scale: 1, duration: 0.35, ease: BK }, 39.5);
tl.fromTo("#sFPill", { backgroundPosition: "100% 0%" }, { backgroundPosition: "0% 0%", duration: 1.4, ease: "none", immediateRender: false }, 39.6);

tl.set("#sFCam", { autoAlpha: 0 }, 39.52);

/* G · missing file */
cut("#sGCam", 41.09); push("#sGCam", 41.09, 6.91, 1.0, 1.05);
pop("#sGFold", 41.12); rise("#sGWin", 41.2, 80);
tl.fromTo("#sGMiss", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.2 }, 45.7);
tl.fromTo("#sGMiss", { x: 0 }, { x: 14, duration: 0.07, repeat: 5, yoyo: true, ease: "none", immediateRender: false }, 45.9);

/* H · /init */
cut("#sHCam", 48.00); push("#sHCam", 48.00, 7.09, 1.0, 1.06);
rise("#sHG", 48.05, 30); rise("#sHChat", 48.2, 60);
tl.set("#sHTx", { autoAlpha: 0 }, 0);
tl.set("#sHTx", { autoAlpha: 1 }, 51.6);
tl.set("#sHPh", { autoAlpha: 0 }, 51.6);
type("#sHTx", 51.6, 2.9, 5);
tl.fromTo("#sHCur", { x: 0, y: 0 }, { x: -120, y: -260, duration: 0.9, ease: "power2.inOut" }, 53.8);
tl.fromTo("#sHSend", { scale: 1 }, { scale: 0.85, duration: 0.08, yoyo: true, repeat: 1, immediateRender: false }, 54.9);

/* I · generating */
cut("#sICam", 55.09); push("#sICam", 55.09, 7.94, 1.0, 1.04);
tl.fromTo("#sIPill", { autoAlpha: 0, scale: 0.7 }, { autoAlpha: 1, scale: 1, duration: 0.35, ease: BK }, 55.15);
tl.fromTo("#sIPill", { backgroundPosition: "100% 0%" }, { backgroundPosition: "0% 0%", duration: 1.5, ease: "none", immediateRender: false }, 55.3);
tl.to("#sIPill", { autoAlpha: 0, scale: 0.8, duration: 0.2 }, 58.3);
tl.fromTo("#sIWin", { autoAlpha: 0.35, y: 60 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: EO }, 55.09);
tl.fromTo("#sIDoc", { y: 0 }, { y: -560, duration: 5.4, ease: "power1.inOut" }, 57.6);

/* J · check */
cut("#sJCam", 66.73); push("#sJCam", 66.73, 7.63, 1.0, 1.05);
rise("#sJG", 66.8, 60); rise("#sJP", 67.1, 60);
tl.to("#sJRG", { opacity: 1, duration: 0.2 }, 68.9);
tl.to("#sJRG", { opacity: 0, duration: 0.2 }, 71.4);
tl.to("#sJRP", { opacity: 1, duration: 0.2 }, 71.62);
tl.fromTo("#sJQG", { scale: 1 }, { scale: 1.2, duration: 0.3, yoyo: true, repeat: 3, ease: "sine.inOut", immediateRender: false }, 69.0);
tl.fromTo("#sJQP", { scale: 1 }, { scale: 1.2, duration: 0.3, yoyo: true, repeat: 3, ease: "sine.inOut", immediateRender: false }, 71.7);

/* K · /doctor */
cut("#sKCam", 74.36); push("#sKCam", 74.36, 4.12, 1.0, 1.05);
rise("#sKG", 74.38, 30);
rise("#sKChat", 74.4, 60);
tl.fromTo("#sKCur", { x: -300, y: 200 }, { x: 0, y: 0, duration: 1.4, ease: "power2.inOut" }, 74.5);
tl.fromTo("#sKChat", { scale: 1 }, { scale: 1.03, duration: 0.4, yoyo: true, repeat: 3, ease: "sine.inOut", immediateRender: false }, 75.0);
tl.set("#sKTx", { autoAlpha: 0 }, 0);
tl.set("#sKTx", { autoAlpha: 1 }, 76.51);
tl.set("#sKPh", { autoAlpha: 0 }, 76.51);
type("#sKTx", 76.51, 1.1, 7);
tl.to("#sKCur", { x: -20, y: -250, duration: 0.5, ease: "power2.inOut" }, 77.1);
tl.fromTo("#sKR1", { autoAlpha: 0, y: 40 }, { autoAlpha: 1, y: 0, duration: 0.25, ease: EO }, 77.75);
tl.fromTo("#sKR2", { autoAlpha: 0, y: 40 }, { autoAlpha: 1, y: 0, duration: 0.25, ease: EO }, 78.05);
pop("#sKO1", 77.85); pop("#sKO2", 78.15);

/* L · CTA */
tl.fromTo("#sLWord", { autoAlpha: 0, scale: 1.6 }, { autoAlpha: 1, scale: 1, duration: 0.3, ease: "power4.out" }, 78.62);
tl.fromTo("#sLSub", { autoAlpha: 0, y: 30 }, { autoAlpha: 1, y: 0, duration: 0.35, ease: EO }, 79.2);
tl.to("#sLCam", { y: -24, duration: 2.0, ease: "sine.inOut" }, 78.9);
tl.fromTo("#v5W", { scale: 1.0 }, { scale: 1.07, duration: 2.2, ease: "none", immediateRender: false }, 78.8);
[[79.0, -2.2], [79.35, 1.8], [79.7, -1.6], [80.05, 2.0], [80.4, -1.2]].forEach(([t, r]) => tl.set(["#v5W", "#sLWord"], { rotation: r }, t));

window.__timelines["main"] = tl;
"""


HIDE = [(0.00, 2.40), (10.64, 15.30), (53.20, 55.09), (56.60, 58.45), ]


def card_spans():
    spans = []
    for a, b, _ in CARD:
        cur = [(a, b)]
        for h0, h1 in HIDE:
            nxt = []
            for x, y in cur:
                if h1 <= x or h0 >= y: nxt.append((x, y)); continue
                if h0 > x: nxt.append((x, h0))
                if h1 < y: nxt.append((h1, y))
            cur = nxt
        spans += [c for c in cur if c[1] - c[0] > 0.05]
    merged = []
    for x, y in sorted(spans):
        if merged and abs(merged[-1][1] - x) < 0.02: merged[-1] = (merged[-1][0], y)
        else: merged.append((x, y))
    return merged


def ovs_js():
    import json
    return json.dumps([[o[0], o[1], o[2], o[4] is None] for o in OV])


def main():
    import json
    doc = f"""<!doctype html>
<html lang="en" data-resolution="portrait">
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
<script>{TIMELINE.replace("__OVS__", ovs_js()).replace("__SPANS__", json.dumps(card_spans()))}</script>
</body>
</html>
"""
    open("index.html", "w").write(doc)
    print("wrote index.html", len(doc), "bytes")


if __name__ == "__main__":
    main()
