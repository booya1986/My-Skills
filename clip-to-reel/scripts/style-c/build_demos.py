#!/usr/bin/env python3
"""Screencast frames -> constant 30 fps clips cropped to the demo (phone or browser window).

Each frames.json (capture_demos.mjs / capture_page.mjs scroll) holds every frame's capture timestamp; a frame is shown
until the next one arrived, so holds stay holds and motion keeps its real speed.
usage: build_demos.py FRAMES_DIR OUT_DIR [NN ...]     FRAMES_DIR/NN/frames.json -> OUT_DIR/NN.mp4 + NN.json (size, radius)
"""
import json, os, subprocess, sys
src, dst, *want = sys.argv[1:]; os.makedirs(dst, exist_ok=True)
for n in (want or sorted(d for d in os.listdir(src) if os.path.exists(f'{src}/{d}/frames.json'))):
    n = n if not n.isdigit() else f'{int(n):02d}'; d = f'{src}/{n}/'
    meta = json.load(open(d + 'frames.json')); fr, b = meta['frames'], meta['box']
    with open(d + 'list.txt', 'w') as L:
        for (f, t), (_, t2) in zip(fr, fr[1:] + [[None, fr[-1][1] + 0.1]]): L.write(f"file '{f}'\nduration {max(0.001, t2 - t):.4f}\n")
        L.write(f"file '{fr[-1][0]}'\n")
    x, y, w, h = (int(round(v)) for v in (b['x'], b['y'], b['w'], b['h'])); w -= w % 2; h -= h % 2
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', d + 'list.txt', '-vf', f'crop={w}:{h}:{x}:{y},fps=30,format=yuv420p',
                    '-c:v', 'libx264', '-crf', '15', '-preset', 'medium', '-g', '10', '-movflags', '+faststart', '-an', f'{dst}/{n}.mp4'], check=True)
    br = float(b.get('br', '0px').split('px')[0] or 0) * float(b.get('z') or 1)
    json.dump({'w': w, 'h': h, 'radius': round(br, 1), 'playMs': round(meta.get('playMs', 0))}, open(f'{dst}/{n}.json', 'w')); print(n, w, h)
