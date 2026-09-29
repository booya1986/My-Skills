"""Component post-processor for build.py.

The helpers at the top are reusable. The components below them are EXAMPLES of one
pattern: find a heading or table in the rendered note by its text, keep every word of
its content, and re-render it as an interactive component. Nothing from the note may be
dropped; components only change how the same content is shown.

Every example is driven by a config at the bottom of this file and is a no-op when its
config is empty or its heading is not found, so the kit builds any note out of the box.
Fill the configs (or write new components) per report, and record them in DESIGN.md.
"""
import html
import os
import re


# ---------------------------------------------------------------- helpers

def h3_text_to_id(h, needle):
    """id of the first h2/h3 whose text contains needle, or None."""
    m = re.search(r'<h[23] id="(s\d+)">([^<]*' + re.escape(needle) + r'[^<]*)</h[23]>', h)
    return m.group(1) if m else None


def section_span(h, hid):
    """(start, end) of the heading with id hid up to the next h2/h3."""
    m = re.search(r'<h[23] id="' + hid + r'">', h)
    start = m.start()
    nxt = re.search(r'<h[23] id="', h[m.end():])
    end = m.end() + nxt.start() if nxt else len(h)
    return start, end


def parse_table(tbl_html):
    """(header_cells, body_rows) from a rendered table."""
    rows = re.findall(r"<tr>(.*?)</tr>", tbl_html, flags=re.S)
    out = [[c.strip() for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", r, flags=re.S)] for r in rows]
    return out[0], out[1:]


# ---------------------------------------------------------------- example components

def stepper(h):
    """Replace the first mermaid diagram under STEPPER['heading'] with clickable stage cards.
    Each step can open the matching option tab (data-go = opt1, opt2, ...)."""
    cfg = STEPPER
    if not cfg.get("steps"):
        return h
    hid = h3_text_to_id(h, cfg["heading"])
    if not hid:
        return h
    s, e = section_span(h, hid)
    sec = h[s:e]
    parts = []
    for k, (label, title, sub) in enumerate(cfg["steps"]):
        parts.append(f'<button class="step" data-go="opt{k + 1}" role="listitem"><span class="n">{label}</span>'
                     f'<b>{title}</b><small>{sub}</small></button>')
        if k < len(cfg.get("conditions", [])):
            parts.append(f'<div class="cond">{cfg["conditions"][k]}</div>')
    block = '<div class="stepper" role="list">' + "".join(parts) + "</div>"
    sec2 = re.sub(r'<pre class="mermaid">.*?</pre>', block, sec, count=1, flags=re.S)
    if sec2 == sec:  # no diagram to replace: insert after the heading
        i = sec.find("</h") + 5
        sec2 = sec[:i] + block + sec[i:]
    return h[:s] + sec2 + h[e:]


def calculator(h):
    """Insert a ratio calculator before the first table under CALCULATOR['heading'].
    Each output shows round(value / per)."""
    cfg = CALCULATOR
    if not cfg.get("outputs"):
        return h
    hid = h3_text_to_id(h, cfg["heading"])
    if not hid:
        return h
    s, e = section_span(h, hid)
    sec = h[s:e]
    outs = "".join(f'<div><small>{label}</small><b data-per="{per}">-</b></div>' for label, per in cfg["outputs"])
    calc = (f'<div class="calc"><div class="calc-h"><b>{cfg["title"]}</b><span>{cfg.get("hint", "")}</span></div>'
            f'<div class="calc-row"><label for="calc-in">{cfg["label"]}</label>'
            f'<input id="calc-in" type="range" min="{cfg["min"]}" max="{cfg["max"]}" step="{cfg["step"]}" value="{cfg["value"]}">'
            f'<output>{cfg["value"]}</output></div><div class="calc-out">{outs}</div>'
            f'<p class="calc-note">{cfg.get("note", "")}</p></div>')
    i = sec.find('<div class="tbl">')
    i = i if i > -1 else len(sec)
    return h[:s] + sec[:i] + calc + sec[i:] + h[e:]


def option_tabs(h):
    """Turn consecutive sections (one per OPTION_TABS needle) into a tab set."""
    needles = OPTION_TABS.get("needles", [])
    ids = [h3_text_to_id(h, n) for n in needles]
    if not ids or None in ids:
        return h
    spans = [section_span(h, i) for i in ids]
    labels = OPTION_TABS.get("labels") or [("", n, "") for n in needles]
    first = OPTION_TABS.get("selected", 0)
    bar = '<div class="tabbar" role="tablist">' + "".join(
        f'<button role="tab" class="tab{" on" if k == first else ""}" data-tab="opt{k + 1}" '
        f'aria-selected="{"true" if k == first else "false"}"><span>{a}</span><b>{b}</b><small>{c}</small></button>'
        for k, (a, b, c) in enumerate(labels)) + "</div>"
    panels = "".join(f'<section class="panel{" on" if k == first else ""}" id="opt{k + 1}" role="tabpanel">{h[s:e]}</section>'
                     for k, (s, e) in enumerate(spans))
    return h[:spans[0][0]] + f'<div class="opts">{bar}{panels}</div>' + h[spans[-1][1]:]


def premortem(h):
    """Paragraphs that start with bold 'Story N. <title>' under PREMORTEM['heading'] become cards."""
    cfg = PREMORTEM
    if not cfg.get("heading"):
        return h
    hid = h3_text_to_id(h, cfg["heading"])
    if not hid:
        return h
    s, e = section_span(h, hid)
    sec = h[s:e]
    pat = re.compile(r"<p><strong>" + re.escape(cfg.get("lead", "Story")) + r" (\d)\. (.*?)</strong>(.*?)</p>", re.S)
    ms = list(pat.finditer(sec))
    if not ms:
        return h
    cards = '<div class="pm">' + "".join(
        f'<div class="pmcard"><span class="n">0{m.group(1)}</span><b>{m.group(2)}</b><p>{m.group(3).strip()}</p></div>'
        for m in ms) + "</div>"
    sec = sec[:ms[0].start()] + cards + sec[ms[-1].end():]
    return h[:s] + sec + h[e:]


def timeline(h):
    """The first two-column table under TIMELINE['heading'] (period | outcome) becomes a timeline."""
    cfg = TIMELINE
    if not cfg.get("heading"):
        return h
    hid = h3_text_to_id(h, cfg["heading"])
    if not hid:
        return h
    s, e = section_span(h, hid)
    sec = h[s:e]
    m = re.search(r'<div class="tbl"><table>.*?</table></div>', sec, flags=re.S)
    if not m:
        return h
    _, rows = parse_table(m.group(0))
    tl = '<div class="timeline">' + "".join(
        f'<div class="tcard"><span class="dot"></span><b>{r[0]}</b><p>{r[1] if len(r) > 1 else ""}</p></div>'
        for r in rows) + "</div>"
    return h[:s] + sec[:m.start()] + tl + sec[m.end():] + h[e:]


def illustrations(h):
    """Insert each registered figure right after the heading whose text contains its needle."""
    for needle, fn, cap in ILL:
        if not os.path.exists(os.path.join("assets", fn)):
            continue
        m = re.search(r'(<h[23] id="s\d+">[^<]*' + re.escape(needle) + r"[^<]*</h[23]>)", h)
        if not m:
            continue
        fig = (f'<figure class="ill"><img src="assets/{fn}" alt="{html.escape(cap)}" loading="lazy">'
               f"<figcaption>{cap}</figcaption></figure>")
        h = h[:m.end()] + fig + h[m.end():]
    return h


def apply(h):
    for f in (stepper, calculator, option_tabs, timeline, premortem, illustrations):
        h = f(h)
    return h


# ---------------------------------------------------------------- per-report config
# Everything below is empty by default. Example values are in the comments.

STEPPER = {}
# STEPPER = {
#     "heading": "Three ways to set it up",
#     "steps": [("Stage 1", "Core team", "3 to 5 people"),
#               ("Stage 2", "Core + analytics", "6 to 10 people"),
#               ("Stage 3", "Full product team", "10 or more")],
#     "conditions": ["Move on when the data is clean", "Move on when value is proven"],
# }

CALCULATOR = {}
# CALCULATOR = {
#     "heading": "How many people",
#     "title": "Team size calculator", "hint": "Drag to your organization's size",
#     "label": "Employees", "min": 1000, "max": 100000, "step": 500, "value": 10000,
#     "outputs": [("First year (1 per 4,800)", 4800), ("Mature (1 per 2,700)", 2700)],
#     "note": "Ratios from <source>; see the table below.",
# }

OPTION_TABS = {}
# OPTION_TABS = {"needles": ["Option 1.", "Option 2.", "Option 3."],
#                "labels": [("Stage 1", "Core team", "3 to 5"), ("Stage 2", "Core + analytics", "6 to 10"),
#                           ("Stage 3", "Full product team", "10+")],
#                "selected": 1}

TIMELINE = {}
# TIMELINE = {"heading": "How we know it worked, by year"}

PREMORTEM = {}
# PREMORTEM = {"heading": "Pre-mortem", "lead": "Story"}

ILL = [
    # (needle in h2/h3 text, file in assets/, caption)
    # ("Three ways to set it up", "stages.png", "The three stages. Each builds on the one before."),
]

STATS = ""  # optional hero tiles: '<div class="stat"><b>13%</b><span>caption</span></div>' x3
META = ""   # optional hero meta row: '<span>…</span>' items
