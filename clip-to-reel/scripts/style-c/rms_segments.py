#!/usr/bin/env python3
"""Speech segments of a wav from a 10 ms RMS map. usage: rms_segments.py in.wav [min_gap_ms] [thr_frac]"""
import sys, subprocess, array, math
wav = sys.argv[1]; mg = float(sys.argv[2]) / 1000 if len(sys.argv) > 2 else 0.12; fr = float(sys.argv[3]) if len(sys.argv) > 3 else 0.055
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", wav, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
d = array.array("h"); d.frombytes(raw); n = 160
env = [math.sqrt(sum(x * x for x in d[i:i + n]) / n) for i in range(0, len(d) - n, n)]
thr = sorted(env)[int(len(env) * 0.97)] * fr
on = [e > thr for e in env]; segs = []; s = None; last = None
for i, v in enumerate(on):
    t = i * 0.01
    if v:
        if s is None: s = t
        elif last is not None and t - last > mg: segs.append((s, last)); s = t
        last = t + 0.01
if s is not None: segs.append((s, last))
for a, b in segs:
    if b - a >= 0.05: print(f"{a:6.2f} {b:6.2f}")
