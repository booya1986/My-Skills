#!/usr/bin/env python3
"""Join verified speech segments into one voice track and map words onto the reel clock.

  python3 assemble_voice.py voice.wav words.json "130.22-137.59,147.55-155.10" vo.wav reel_words.json

Each segment gets a 12 ms fade-in and 20 ms fade-out so joins never click. Only words fully inside a segment are
kept (±0.05/0.15 s tolerance); whisper drift means you still re-read each join by ear/transcription.
"""
import json, subprocess, sys, tempfile, os

voice, words_json, spec, out_wav, out_words = sys.argv[1:6]
segs = [tuple(map(float, s.split("-"))) for s in spec.split(",")]
tmp = tempfile.mkdtemp()
files, table, off = [], [], 0.0
for i, (a, b) in enumerate(segs):
    d = b - a
    f = os.path.join(tmp, f"seg{i}.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(a), "-to", str(b), "-i", voice, "-af",
                    f"afade=t=in:d=0.012,afade=t=out:st={d-0.02:.3f}:d=0.02", "-ar", "48000", "-ac", "1", f],
                   check=True)
    files.append(f)
    table.append({"seg": i, "src_from": a, "src_to": b, "reel_from": round(off, 3), "reel_to": round(off + d, 3)})
    off += d
lst = os.path.join(tmp, "concat.txt")
open(lst, "w").write("".join(f"file '{f}'\n" for f in files))
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c:a", "pcm_s16le", out_wav],
               check=True)

words = json.load(open(words_json))["words"]
mapped = []
for s in table:
    for w in words:
        if w.get("type", "word") != "word":
            continue
        if w["start"] >= s["src_from"] - 0.05 and w["end"] <= s["src_to"] + 0.15:
            mapped.append({"t0": round(w["start"] - s["src_from"] + s["reel_from"], 2),
                           "t1": round(min(w["end"], s["src_to"]) - s["src_from"] + s["reel_from"], 2),
                           "w": w["text"], "seg": s["seg"]})
json.dump({"segments": table, "words": mapped}, open(out_words, "w"), ensure_ascii=False, indent=1)
for s in table:
    print(f"src {s['src_from']}-{s['src_to']} -> reel {s['reel_from']:.2f}-{s['reel_to']:.2f}")
print(f"total {off:.2f} s · {len(mapped)} words -> {out_words}")
