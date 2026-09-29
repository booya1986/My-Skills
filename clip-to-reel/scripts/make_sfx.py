#!/usr/bin/env python3
"""Synthesize the reel's sound-effect kit (no samples, no licences needed).

  python3 make_sfx.py media/sfx

Writes whoosh.wav (0.57 s), click.wav (0.09 s), tick.wav (0.05 s), impact.wav (1.1 s), boom.wav (3.0 s),
48 kHz mono. Durations match the <audio data-duration> values used in the reference composition, so the
template works unchanged. Levels are normalised to -1 dBFS; balance them in the composition with data-volume.
"""
import os, sys, wave
import numpy as np

SR = 48000
rng = np.random.default_rng(7)  # fixed seed: identical sounds on every run


def write(path, x):
    x = np.clip(x / (np.abs(x).max() + 1e-9) * 0.89, -1, 1)  # 0.89 ≈ -1 dBFS
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())


def env(n, attack, decay, shape=2.0):
    e = np.ones(n)
    a, d = max(1, int(attack * SR)), max(1, int(decay * SR))
    e[:a] = np.linspace(0, 1, a) ** 0.5
    e[-d:] = np.linspace(1, 0, d) ** shape
    return e


def sweep(noise, f0, f1, q):
    """Resonant band-pass whose centre moves f0 -> f1 (block-wise biquad)."""
    out, block = np.zeros_like(noise), 256
    x1 = x2 = y1 = y2 = 0.0
    for i in range(0, len(noise), block):
        f = f0 * (f1 / f0) ** (i / len(noise))
        w0 = 2 * np.pi * f / SR; al = np.sin(w0) / (2 * q)
        b0, b2, a0, a1, a2 = al, -al, 1 + al, -2 * np.cos(w0), 1 - al
        for k, xv in enumerate(noise[i:i + block]):
            y = (b0 * xv + b2 * x2 - a1 * y1 - a2 * y2) / a0
            x2, x1, y2, y1 = x1, xv, y1, y
            out[i + k] = y
    return out


def whoosh(dur=0.57):
    n = int(dur * SR)
    return sweep(rng.standard_normal(n), 300, 3500, 1.6) * env(n, 0.08, 0.30, 2.5)


def click(dur=0.09):
    n = int(dur * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 2200 * t) * 0.6 + rng.standard_normal(n) * 0.4) * np.exp(-t * 90)


def tick(dur=0.05):
    n = int(dur * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * 3400 * t) * np.exp(-t * 160)


def impact(dur=1.1):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 95 * np.exp(-t * 9) + 45
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) + rng.standard_normal(n) * np.exp(-t * 220) * 0.35


def boom(dur=3.0):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 70 * np.exp(-t * 4) + 38
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.6) + rng.standard_normal(n) * np.exp(-t * 60) * 0.25


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "media/sfx"
    os.makedirs(out, exist_ok=True)
    for name, fn in [("whoosh", whoosh), ("click", click), ("tick", tick), ("impact", impact), ("boom", boom)]:
        write(os.path.join(out, f"{name}.wav"), fn())
        print("wrote", os.path.join(out, f"{name}.wav"))


if __name__ == "__main__":
    main()
