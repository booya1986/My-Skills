#!/usr/bin/env python3
"""Swap the accent colours of a generated collage (image or video) to brand colours, frame by frame.

  python3 recolor_accents.py in.(png|mp4) out.(png|mp4) [--map blue=#22C55E red=#15803D] [--min-sat 0.35]

Only saturated pixels whose hue falls in a named band move; greys, beige paper, halftone photos and skin stay.
The target colour's hue replaces the pixel's hue and its saturation/value scale the pixel's, so paper texture
and shading survive. Bands: red 340-15, orange 15-40, yellow 40-65, green 80-165, blue 190-255, purple 255-300.
No credits: use it instead of regenerating when only the palette changes.
"""
import argparse, subprocess, sys
import numpy as np
from PIL import Image

BANDS = {"red": (340, 15), "orange": (15, 40), "yellow": (40, 65), "green": (80, 165),
         "blue": (190, 255), "purple": (255, 300)}


def hex_hsv(h):
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
    mx, mn = max(r, g, b), min(r, g, b)
    d = mx - mn
    if d == 0: hue = 0
    elif mx == r: hue = (60 * ((g - b) / d) + 360) % 360
    elif mx == g: hue = 60 * ((b - r) / d) + 120
    else: hue = 60 * ((r - g) / d) + 240
    return hue, (d / mx if mx else 0), mx


def rgb2hsv(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx, mn = a.max(-1), a.min(-1); d = mx - mn
    h = np.zeros_like(mx)
    m = d > 1e-6
    rr = m & (mx == r); gg = m & (mx == g) & ~rr; bb = m & ~rr & ~gg
    h[rr] = (60 * ((g - b)[rr] / d[rr]) + 360) % 360
    h[gg] = 60 * ((b - r)[gg] / d[gg]) + 120
    h[bb] = 60 * ((r - g)[bb] / d[bb]) + 240
    s = np.where(mx > 0, d / np.maximum(mx, 1e-6), 0)
    return h, s, mx


def hsv2rgb(h, s, v):
    c = v * s; hp = (h % 360) / 60; x = c * (1 - np.abs(hp % 2 - 1)); m = v - c
    z = np.zeros_like(h)
    conds = [(hp < 1), (hp < 2), (hp < 3), (hp < 4), (hp < 5), (hp <= 6)]
    rgbs = [(c, x, z), (x, c, z), (z, c, x), (z, x, c), (x, z, c), (c, z, x)]
    out = np.zeros(h.shape + (3,))
    done = np.zeros(h.shape, bool)
    for cond, (r, g, b) in zip(conds, rgbs):
        sel = cond & ~done
        out[sel] = np.stack([r[sel], g[sel], b[sel]], -1)
        done |= sel
    return out + m[..., None]


def recolor(frame, maps, min_sat):
    a = frame.astype(np.float32) / 255
    h, s, v = rgb2hsv(a)
    nh, ns, nv = h.copy(), s.copy(), v.copy()
    for band, target in maps:
        lo, hi = BANDS[band]
        inb = ((h >= lo) | (h < hi)) if lo > hi else ((h >= lo) & (h < hi))
        sel = inb & (s >= min_sat)
        th, ts, tv = hex_hsv(target)
        # soft edge: blend by how saturated the pixel is
        w = np.clip((s - min_sat) / 0.15, 0, 1)[sel]
        nh[sel] = th
        ns[sel] = s[sel] * (1 - w) + np.clip(ts * s[sel] / 0.85, 0, 1) * w
        nv[sel] = v[sel] * (1 - w) + np.clip(tv * v[sel] / 0.80, 0, 1) * w
    return (np.clip(hsv2rgb(nh, ns, nv), 0, 1) * 255).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("dst")
    ap.add_argument("--map", nargs="+", default=["blue=#22C55E", "red=#15803D"])
    ap.add_argument("--min-sat", type=float, default=0.35)
    a = ap.parse_args()
    maps = [tuple(m.split("=")) for m in a.map]
    if a.src.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
        Image.fromarray(recolor(np.asarray(Image.open(a.src).convert("RGB")), maps, a.min_sat)).save(a.dst)
        return
    w, h = map(int, subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                             "stream=width,height", "-of", "csv=p=0", a.src]).decode().strip().split(","))
    fps = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                   "stream=r_frame_rate", "-of", "csv=p=0", a.src]).decode().strip()
    dec = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-i", a.src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
                            "-r", fps, "-i", "-", "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p", a.dst],
                           stdin=subprocess.PIPE)
    n = 0
    while True:
        buf = dec.stdout.read(w * h * 3)
        if len(buf) < w * h * 3: break
        enc.stdin.write(recolor(np.frombuffer(buf, np.uint8).reshape(h, w, 3), maps, a.min_sat).tobytes())
        n += 1
    enc.stdin.close(); enc.wait(); dec.wait()
    print(f"recoloured {n} frames -> {a.dst}", file=sys.stderr)


if __name__ == "__main__":
    main()
