#!/usr/bin/env python3
"""Reverb tail after phrase ends: level 50-250 ms after each phrase end that is followed by a real pause, relative to the
last 300 ms of the phrase. More negative = less echo. Phrase ends come from the first file, so compare versions of one cut.
usage: echo_tail.py voice.wav [voice2.wav ...]"""
import os, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
def load(f):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '1', '-ar', '48000', '-f', 'f32le', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32)
segs = [tuple(map(float, l.split())) for l in subprocess.run([sys.executable, os.path.join(HERE, 'rms_segments.py'), sys.argv[1], '120'],
        capture_output=True, text=True).stdout.split('\n') if l.strip()]
ends = [segs[i][1] for i in range(len(segs) - 1) if segs[i + 1][0] - segs[i][1] > 0.3]
db = lambda v: 20 * np.log10(np.sqrt((v ** 2).mean()) + 1e-9)
for f in sys.argv[1:]:
    x = load(f); r = [db(x[int((e + 0.05) * 48000):int((e + 0.25) * 48000)]) - db(x[int((e - 0.3) * 48000):int(e * 48000)]) for e in ends]
    print(f'{f}: tail {np.median(r):.1f} dB (median over {len(r)} phrase ends), worst {max(r):.1f} dB')
