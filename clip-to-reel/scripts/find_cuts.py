#!/usr/bin/env python3
"""List safe cut points in a narration track.

Cue boundaries in subs_cues.json split on line length, not syntax, so cutting
there chops sentences mid-thought. This finds real boundaries instead: runs of
actual silence in the voice track, cross-referenced with the word-level
transcript so each candidate shows what ends before it and what starts after.

  python3 find_cuts.py <voice.wav> <transcript.json> [from] [to] [min_gap_ms]
"""
import json, math, subprocess, sys, array

def rms_map(wav, hop=0.01):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", wav, "-ac", "1",
                          "-ar", "16000", "-f", "s16le", "-"],
                         capture_output=True).stdout
    d = array.array("h"); d.frombytes(raw)
    n = int(16000 * hop)
    return [math.sqrt(sum(x * x for x in d[i:i + n]) / max(1, len(d[i:i + n])))
            for i in range(0, len(d) - n, n)], hop

def main():
    wav, tj = sys.argv[1], sys.argv[2]
    lo = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
    hi = float(sys.argv[4]) if len(sys.argv) > 4 else 1e9
    min_gap = (float(sys.argv[5]) if len(sys.argv) > 5 else 260) / 1000.0

    env, hop = rms_map(wav)
    peak = sorted(env)[int(len(env) * 0.97)]
    thr = peak * 0.055                       # silence floor relative to speech peak

    # silence runs
    runs, i = [], 0
    while i < len(env):
        if env[i] < thr:
            j = i
            while j + 1 < len(env) and env[j + 1] < thr:
                j += 1
            a, b = i * hop, (j + 1) * hop
            if b - a >= min_gap:
                runs.append((a, b))
            i = j + 1
        else:
            i += 1

    words = json.load(open(tj))["words"]
    def before(t):
        w = [x for x in words if x["end"] <= t + 0.05]
        return " ".join(x["text"] for x in w[-7:]) if w else "—"
    def after(t):
        w = [x for x in words if x["start"] >= t - 0.05]
        return " ".join(x["text"] for x in w[:7]) if w else "—"

    print(f"silence floor {thr:.0f} (speech peak {peak:.0f}) · {len(runs)} gaps >= {min_gap*1000:.0f}ms\n")
    print(f"{'cut':>8} {'gap':>6}   ...ends with  |  starts with...")
    for a, b in runs:
        mid = (a + b) / 2
        if not (lo <= mid <= hi):
            continue
        print(f"{mid:8.2f} {(b-a)*1000:5.0f}ms   {before(a)[-52:]:>52}  |  {after(b)[:52]}")

main()
