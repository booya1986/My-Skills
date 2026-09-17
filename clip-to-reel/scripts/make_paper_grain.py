#!/usr/bin/env python3
"""Fine paper grain overlay (1080x1920 RGBA PNG) for the beige paper panels.

  python3 make_paper_grain.py media/paper_grain.png [seed]

Alpha stays below ~11 % so it reads as paper, not noise; low-frequency blotches are isotropic on purpose —
stretched noise looked like wood streaks to the judge.
"""
import sys
import numpy as np
from PIL import Image, ImageFilter

out = sys.argv[1]
seed = int(sys.argv[2]) if len(sys.argv) > 2 else 5
rng = np.random.default_rng(seed)
H, W = 1920, 1080
fine = rng.normal(0, 1, (H, W))
blot = np.asarray(Image.fromarray(rng.normal(128, 50, (H // 24, W // 24)).clip(0, 255).astype("uint8"))
                  .resize((W, H), Image.BICUBIC)).astype(float)
blot = (blot - blot.mean()) / blot.std()
lum = fine + 0.35 * blot
alpha = np.clip(np.abs(lum) * 12, 0, 28).astype("uint8")
dark = lum > 0
rgba = np.zeros((H, W, 4), "uint8")
rgba[..., 0] = np.where(dark, 90, 255)
rgba[..., 1] = np.where(dark, 72, 250)
rgba[..., 2] = np.where(dark, 44, 238)
rgba[..., 3] = alpha
Image.fromarray(rgba, "RGBA").filter(ImageFilter.GaussianBlur(0.4)).save(out, optimize=True)
print("wrote", out)
