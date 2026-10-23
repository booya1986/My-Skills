#!/usr/bin/env python3
"""Sibilance and band balance of a voice file: the 5-9 kHz / 0.3-3 kHz ratio on loud frames (p95, p99) and the share of
energy at 5-8 kHz and 8-12 kHz. Compare versions; a de-esser that works lowers p99 without dropping 8-12k much.
usage: sibilance.py voice.wav [...]"""
import subprocess, sys
import numpy as np
def load(f, sr=48000):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32)
for path in sys.argv[1:]:
    x = load(path); n = 2048; fr = np.lib.stride_tricks.sliding_window_view(x, n)[::1024] * np.hanning(n)
    db = 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9); sp = fr[db > np.percentile(db, 97) - 30]
    S = np.abs(np.fft.rfft(sp, axis=1)) ** 2; f = np.fft.rfftfreq(n, 1 / 48000)
    sib = 10 * np.log10(S[:, (f > 5000) & (f < 9000)].sum(1) / S[:, (f > 300) & (f < 3000)].sum(1) + 1e-12)
    M = S.mean(0); tot = M[(f > 80) & (f < 16000)].sum()
    print(path, 'sib p95', round(np.percentile(sib, 95), 1), 'p99', round(np.percentile(sib, 99), 1),
          '| 5-8k', round(10 * np.log10(M[(f > 5000) & (f < 8000)].sum() / tot), 1), '8-12k', round(10 * np.log10(M[(f > 8000) & (f < 12000)].sum() / tot), 1))
