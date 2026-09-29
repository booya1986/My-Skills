#!/usr/bin/env python3
"""Fail loudly on any character the embedded font subsets do not cover.
Uncovered characters render as .notdef boxes in the headless render."""
import re, sys, unicodedata

# Latin + general punctuation. Add the code-point ranges of your script's font subset.
RANGES = [(0x0000, 0x00FF), (0x2000, 0x206F)]
covered = lambda c: any(lo <= c <= hi for lo, hi in RANGES)

path = sys.argv[1] if len(sys.argv) > 1 else "index.html"
s = open(path, encoding="utf-8").read()
body = s[s.index('<div id="root"'):s.rindex('<script>')]
text = re.sub(r"<[^>]+>", "", body)
bad = sorted({c for c in text if not c.isspace() and not covered(ord(c))})
if bad:
    for c in bad:
        print(f"  U+{ord(c):04X}  {c!r}  {unicodedata.name(c, '?')}")
    sys.exit(1)
print("NONE")
