#!/usr/bin/env python3
"""A bass-heavy 100 BPM beat synthesized in code (fallback when no music model is available).

808 kick with a pitch drop and a long sub tail, a sub bass that follows the chords (Am - F - C - G), claps on 2 and 4,
swung 8th hats with an open hat every other bar, a filtered saw stab on the off-beats, and a short riser into each 8-bar
section. Beat 0 is at t = 0, so every half beat sits on the 0.3 s grid the composition cuts on.
usage: synth_bed.py out.wav [seconds=56]
"""
import sys, os, wave
import numpy as np
OUT = sys.argv[1]
SR = 48000; BPM = 100; B = 60 / BPM; DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 56.0
N = int(DUR * SR); L = np.zeros(N); Rr = np.zeros(N)
rng = np.random.default_rng(17)
def add(sig, t, g=1.0, pan=0.0):
    i = int(t * SR); j = min(N, i + len(sig))
    if i >= N: return
    L[i:j] += sig[:j - i] * g * (1 - max(0, pan)); Rr[i:j] += sig[:j - i] * g * (1 + min(0, pan))
def env(n, a, d):
    t = np.arange(n) / SR; e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d); return e
def kick():
    n = int(0.9 * SR); t = np.arange(n) / SR
    f = 48 + 110 * np.exp(-t * 28); ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t * 3.2); s += 0.35 * np.tanh(4 * np.sin(ph)) * np.exp(-t * 18)
    s[:200] += rng.normal(0, 0.4, 200) * np.linspace(1, 0, 200); return np.tanh(1.6 * s)
def clap():
    n = int(0.35 * SR); t = np.arange(n) / SR; nz = rng.normal(0, 1, n)
    e = sum(np.exp(-np.maximum(0, t - o) * 60) * (t >= o) for o in (0, 0.011, 0.022)) * 0.5 + np.exp(-t * 14) * 0.6
    b = np.convolve(nz, np.ones(6) / 6, 'same') - np.convolve(nz, np.ones(40) / 40, 'same'); return b * e * 0.8
def hat(open_=False):
    n = int((0.32 if open_ else 0.06) * SR); nz = rng.normal(0, 1, n); hp = nz - np.convolve(nz, np.ones(4) / 4, 'same')
    return hp * env(n, 0.001, 0.09 if open_ else 0.018) * 0.5
def sub(freq, dur, glide_from=None):
    n = int(dur * SR); t = np.arange(n) / SR
    f = np.full(n, freq) if glide_from is None else freq + (glide_from - freq) * np.exp(-t * 18)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR); s = np.tanh(2.2 * s) * 0.8
    e = np.minimum(1, t / 0.01) * np.minimum(1, (dur - t) / 0.04).clip(0); return s * e
def stab(freqs, dur=0.22, cutoff=1800):
    n = int(dur * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for f in freqs:
        for det in (-0.12, 0.0, 0.12):
            s += 2 * ((t * f * 2 ** (det / 12)) % 1) - 1
    s /= len(freqs) * 3
    a = np.exp(-2 * np.pi * cutoff / SR); y = np.zeros(n); y[0] = s[0]
    for i in range(1, n): y[i] = (1 - a) * s[i] + a * y[i - 1]
    return y * env(n, 0.003, 0.12) * 0.9
def pluck(f, dur=0.28):
    n = int(dur * SR); t = np.arange(n) / SR; ph = (t * f) % 1
    s = (4 * np.abs(ph - 0.5) - 1) * 0.7 + 0.3 * np.sin(2 * np.pi * 2 * f * t)
    return s * env(n, 0.002, 0.09)
NOTE = lambda m: 440 * 2 ** ((m - 69) / 12)
CH = [(45, [57, 60, 64]), (41, [57, 60, 65]), (48, [55, 60, 64]), (43, [55, 59, 62])]   # Am F C G (bass midi, stab midi)
beats = int(DUR / B) + 1
K = kick(); C = clap()
for b in range(beats):
    t = b * B; bar, bb = divmod(b, 4); sec = bar // 8
    intro = bar < 2
    root, notes = CH[bar % 4]
    if not intro or bb in (0,):
        add(K, t, 0.95)
    if not intro and bb == 2 and bar % 2 == 1: add(K, t + B * 0.75, 0.6)        # pickup kick
    if bb in (1, 3) and bar >= 1: add(C, t, 0.9)
    for e8 in range(2):
        sw = 0.0 if e8 == 0 else B * 0.06
        add(hat(), t + e8 * B / 2 + sw, 0.7 if e8 else 0.5, pan=0.2)
        if not intro and bar >= 4: add(hat(), t + e8 * B / 2 + B / 4 + sw, 0.3, pan=-0.2)
    if bb == 3 and bar % 2 == 1: add(hat(True), t + B / 2, 0.5, pan=-0.15)
    if not intro:
        add(sub(NOTE(root - 12), B * (0.95 if bb < 3 else 0.45), glide_from=NOTE(root - 12) * (1.5 if bb == 0 else 1.0)), t, 0.55)
        if bb == 3: add(sub(NOTE(root - 5), B * 0.45), t + B / 2, 0.45)
        add(stab([NOTE(m) for m in notes], cutoff=2600 + 1600 * (bar % 8) / 7), t + B / 2, 0.75, pan=0.25 if bb % 2 else -0.25)
        if bar >= 4:   # the hook: a plucked arp an octave up, one note per 8th
            for e8 in range(2): add(pluck(NOTE(notes[(bb * 2 + e8) % 3] + 12)), t + e8 * B / 2, 0.42, pan=-0.3 if e8 else 0.3)
    if bar % 8 == 7 and bb == 0:                                                 # riser into the next section
        n = int(4 * B * SR); tt = np.arange(n) / SR; nz = rng.normal(0, 1, n) * (tt / (4 * B)) ** 2 * 0.25
        add(nz - np.convolve(nz, np.ones(3) / 3, 'same'), t, 0.5)
mix = np.stack([L, Rr], 1); mix /= np.max(np.abs(mix)) + 1e-9; mix = np.tanh(mix * 1.3) * 0.89
os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
with wave.open(OUT, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype('<i2').tobytes())
print(OUT, round(DUR, 1), 's')
