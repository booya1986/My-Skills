#!/usr/bin/env python3
"""Track an animated webcam bubble and write an ffmpeg `sendcmd` crop file.

Some screen recorders scale the bubble between sizes while keeping one corner anchored, so a fixed crop catches half a
face. This finds the bubble's top edge every 1/fps s in a narrow strip next to the anchored side, smooths it,
and emits a 9:8 crop (for the 1080x960 lower half of a split) centred on the face.

  python3 track_bubble.py src.mp4 out.cmd --anchor-right 1865 --anchor-bottom 1025 \
      [--strip 1700-1860] [--search 700-880] [--hold 48.4-56.6,...] [--fps 10] [--aspect 1.7778]

--anchor-right/--anchor-bottom : the fixed corner of the bubble in the source frame (measure on a gridded crop)
--strip   : x-range of the vertical strip used to find the top edge (inside the bubble in every size)
--search  : y-range where the top edge can be
--hold    : time ranges (src clock) with no bubble (full-frame speaker); the last good value is held there
Prints the first crop as w:h:x:y for the initial `crop=` filter.
"""
import argparse, json, statistics, subprocess
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("out")
ap.add_argument("--anchor-right", type=int, required=True)
ap.add_argument("--anchor-bottom", type=int, required=True)
ap.add_argument("--strip", default=None)
ap.add_argument("--search", default=None)
ap.add_argument("--hold", default="")
ap.add_argument("--fps", type=int, default=10)
ap.add_argument("--aspect", type=float, default=16 / 9, help="bubble width/height")
ap.add_argument("--crop-height", type=float, default=0.80, help="fraction of bubble height kept")
ap.add_argument("--face-x", type=float, default=0.53, help="face centre as fraction of bubble width")
a = ap.parse_args()

R, B = a.anchor_right, a.anchor_bottom
x0, x1 = map(int, (a.strip or f"{R-165}-{R-5}").split("-"))
s0, s1 = map(int, (a.search or f"{B-325}-{B-145}").split("-"))
y0 = s0 - 20
w, h = x1 - x0, B - y0
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", a.src, "-vf",
                      f"fps={a.fps},crop={w}:{h}:{x0}:{y0},format=gray", "-f", "rawvideo", "-"],
                     capture_output=True).stdout
n = len(raw) // (w * h)
frames = np.frombuffer(raw, np.uint8)[: n * w * h].reshape(n, h, w).astype(np.float32)

tops = []
for f in frames:
    g = np.abs(np.diff(f.mean(axis=1)))
    lo, hi = s0 - y0, s1 - y0
    tops.append(y0 + int(np.argmax(g[lo:hi])) + lo)
smooth = [statistics.median(tops[max(0, i - 2): i + 3]) for i in range(len(tops))]

holds = []
for r in filter(None, a.hold.split(",")):
    lo, hi = map(float, r.split("-")); holds.append((lo, hi))

cmds, last = [], smooth[0] if smooth else s0
for i, y in enumerate(smooth):
    t = i / a.fps
    if any(lo <= t <= hi for lo, hi in holds):
        y = last
    last = y
    bh = B - y; bw = bh * a.aspect; left = R - bw
    ch = int(bh * a.crop_height) // 2 * 2; cw = int(ch * 9 / 8) // 2 * 2
    x = int(left + bw * a.face_x - cw / 2); yy = int(y + bh * 0.05)
    cmds.append(f"{t:.1f} crop w {cw}, crop h {ch}, crop x {x}, crop y {yy};")

open(a.out, "w").write("\n".join(cmds) + "\n")
json.dump([[i / a.fps, t] for i, t in enumerate(tops)], open(a.out + ".tops.json", "w"))
print(f"frames {n} · top y range {min(tops)}-{max(tops)} · wrote {a.out}")
if cmds:
    import re
    m = re.search(r"w (\d+), crop h (\d+), crop x (\d+), crop y (\d+)", cmds[0])
    print("first crop:", ":".join(m.groups()))
