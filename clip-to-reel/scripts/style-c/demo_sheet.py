#!/usr/bin/env python3
"""Timestamped contact sheet of one captured demo, to read its key moments (saved, error, green, menu back) and place
them on the spoken words. usage: demo_sheet.py FRAMES_DIR/NN out.jpg [every_s=0.25] [cols=10]"""
import json, sys
from PIL import Image, ImageDraw
d, out = sys.argv[1].rstrip('/') + '/', sys.argv[2]; step = float(sys.argv[3]) if len(sys.argv) > 3 else 0.25; cols = int(sys.argv[4]) if len(sys.argv) > 4 else 10
m = json.load(open(d + 'frames.json')); fr = m['frames']; t0 = fr[0][1]; b = m['box']; picks, t = [], 0.0
while t <= fr[-1][1] - t0:
    i = max(j for j, f in enumerate(fr) if f[1] - t0 <= t); picks.append((t, fr[i][0])); t += step
W = 240 if b['w'] < b['h'] else 360; H = int(W * b['h'] / b['w'])
sheet = Image.new('RGB', (cols * W, -(-len(picks) // cols) * (H + 22)), (20, 20, 20)); dr = ImageDraw.Draw(sheet)
for k, (t, f) in enumerate(picks):
    im = Image.open(d + f).crop((int(b['x']), int(b['y']), int(b['x'] + b['w']), int(b['y'] + b['h']))).resize((W, H))
    x, y = (k % cols) * W, (k // cols) * (H + 22); sheet.paste(im, (x, y + 22)); dr.text((x + 4, y + 4), f'{t:.2f}', fill=(255, 210, 63))
sheet.save(out, quality=80); print(out, len(picks))
