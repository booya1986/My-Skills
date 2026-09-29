#!/usr/bin/env python3
"""Render a verified-research note into index.html using template.html + components.py.

Usage:
    python3 build.py "<note path or glob>" [site_url] [--lang en] [--dir ltr]
                     [--kicker "Verified research"] [--toc-label Contents]
                     [--footer "..."] [--drop-callout "Share version."]

- The note path is required (no default). A glob must match exactly one file; locate the
  note by glob because users rename notes mid-run.
- site_url is the public base URL (e.g. https://<owner>.github.io/<repo>/), used for
  Open Graph tags. Optional.
- For right-to-left notes pass --dir rtl and the right --lang (e.g. --lang ar --dir rtl).
Needs Node.js for `npx marked` (no pip install required). Run it from the kit folder.
"""
import argparse
import glob
import html
import pathlib
import re
import subprocess
import sys

import components

DEFAULT_FOOTER = ("Built with the verified-research pipeline. Every source that survived "
                  "fact-checking is listed at the end with a link, a date and a confidence level.")


def main():
    ap = argparse.ArgumentParser(description="Build index.html from a research note.")
    ap.add_argument("note", help="path or glob of the markdown note (must match exactly one file)")
    ap.add_argument("site_url", nargs="?", default="", help="public base URL for Open Graph tags")
    ap.add_argument("--lang", default="en", help="BCP 47 language code of the note (default: en)")
    ap.add_argument("--dir", default="ltr", choices=["ltr", "rtl"], help="text direction (default: ltr)")
    ap.add_argument("--kicker", default="Verified research", help="small label above the title")
    ap.add_argument("--toc-label", default="Contents", help="label of the table of contents")
    ap.add_argument("--footer", default=DEFAULT_FOOTER, help="footer text")
    ap.add_argument("--drop-callout", action="append", default=[],
                    help="drop a one-line blockquote that starts with this bold text (repeatable), "
                         "e.g. a notes-only 'Share version.' callout")
    args = ap.parse_args()

    matches = sorted(glob.glob(args.note))
    if len(matches) != 1:
        sys.exit(f"note glob must match exactly one file, matched {len(matches)}: {matches[:5]}")
    src = matches[0]
    s = open(src, encoding="utf-8").read()

    m = re.match(r"^---\n(.*?)\n---\n", s, re.S)
    fm = m.group(1) if m else ""
    body = s[m.end():] if m else s

    # the page header carries the title, so drop the note's H1
    body = re.sub(r"^# .*?\n", "", body.lstrip(), count=1)
    for lead in args.drop_callout:
        body = re.sub(r"\n> \*\*" + re.escape(lead) + r"\*\*[^\n]*\n", "\n", body)

    pathlib.Path("body.md").write_text(body, encoding="utf-8")
    subprocess.run(["npx", "--yes", "marked", "--gfm", "-i", "body.md", "-o", "body.html"], check=True)
    h = open("body.html", encoding="utf-8").read()

    # mermaid code blocks -> live diagrams
    h = re.sub(r'<pre><code class="language-mermaid">(.*?)</code></pre>',
               lambda mm: '<pre class="mermaid">' + html.unescape(mm.group(1)) + "</pre>", h, flags=re.S)

    # heading ids + toc
    toc = []
    counter = [0]

    def hid(mm):
        lvl, txt = mm.group(1), mm.group(2)
        counter[0] += 1
        i = f"s{counter[0]}"
        toc.append((int(lvl), i, re.sub(r"<.*?>", "", txt)))
        return f'<h{lvl} id="{i}">{txt}</h{lvl}>'

    h = re.sub(r"<h([23])>(.*?)</h\1>", hid, h)
    # tables scroll horizontally instead of widening the page
    h = h.replace("<table>", '<div class="tbl"><table>').replace("</table>", "</table></div>")
    h = h.replace("<blockquote>", '<blockquote class="callout">')
    toc_html = "".join(f'<a class="l{l}" href="#{i}">{t}</a>' for l, i, t in toc if l == 2)

    h = components.apply(h)

    def fmv(k):
        mm = re.search(r"^" + k + r':\s*"?(.*?)"?\s*$', fm, re.M)
        return mm.group(1) if mm else ""

    kicker = args.kicker + (" · " + fmv("created") if fmv("created") else "")
    stats = components.STATS  # optional hero stat tiles, see components.py
    meta = components.META
    tpl = open("template.html", encoding="utf-8").read()
    out = (tpl.replace("{{BODY}}", h).replace("{{TOC}}", toc_html)
              .replace("{{LANG}}", html.escape(args.lang)).replace("{{DIR}}", args.dir)
              .replace("{{TITLE}}", html.escape(fmv("title"))).replace("{{DESCRIPTION}}", html.escape(fmv("description")))
              .replace("{{SITE_URL}}", args.site_url).replace("{{KICKER}}", html.escape(kicker))
              .replace("{{TOC_LABEL}}", html.escape(args.toc_label)).replace("{{FOOTER}}", html.escape(args.footer))
              .replace("{{STATS}}", stats).replace("{{META}}", meta))
    pathlib.Path("index.html").write_text(out, encoding="utf-8")
    print("index.html", len(out), "bytes; toc", len(toc), "; source", src)


if __name__ == "__main__":
    main()
