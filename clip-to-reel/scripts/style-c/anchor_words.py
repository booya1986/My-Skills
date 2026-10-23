#!/usr/bin/env python3
"""Word timings on the reel timeline: whisper words re-anchored to the RMS speech segments of the final voice.

Whisper drifts 0.1-0.3 s (more on some languages); RMS edges do not. Each word goes to the segment nearest its centre
(after a small late shift), and the words inside a segment are stretched linearly to fill it.
usage: anchor_words.py whisper.json voice.wav out.json [shift_s=0.15]
whisper.json: {"words": [{"text", "start", "end"}, ...]}   out.json: [[text, start, end], ...]
Time every scene from word indices (W[i][0]) so a new cut only regenerates this file.
"""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
wj, wav, out = sys.argv[1:4]; SHIFT = float(sys.argv[4]) if len(sys.argv) > 4 else 0.15
segs = [tuple(map(float, l.split())) for l in subprocess.run([sys.executable, os.path.join(HERE, 'rms_segments.py'), wav, '90', '0.07'],
        capture_output=True, text=True).stdout.split('\n') if l.strip()]
segs = [s for s in segs if s[1] - s[0] > 0.12]
ws = [w for w in json.load(open(wj))['words'] if w.get('type', 'word') == 'word']
def seg_of(w):
    c = (w['start'] + w['end']) / 2 + SHIFT
    return min(range(len(segs)), key=lambda i: 0 if segs[i][0] <= c <= segs[i][1] else min(abs(c - segs[i][0]), abs(c - segs[i][1])))
groups = {}
for w in ws: groups.setdefault(seg_of(w), []).append(w)
res = []
for i, (a, b) in enumerate(segs):
    inn = groups.get(i)
    if not inn: continue
    s0, s1 = inn[0]['start'], inn[-1]['end']; k = (b - a) / max(0.01, s1 - s0)
    for w in inn: res.append([w['text'], round(a + (w['start'] - s0) * k, 3), round(a + (w['end'] - s0) * k, 3)])
json.dump(res, open(out, 'w'), ensure_ascii=False)
print(len(res), 'of', len(ws), 'words anchored ->', out)
