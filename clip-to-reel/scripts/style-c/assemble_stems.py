#!/usr/bin/env python3
"""Final assembly from stems, so a new music track, a voice fix or a new SFX pass never needs a re-render.

  sound:   voice + sfx + music (-9 dB, sidechain-ducked ~13 dB under the voice) on the composition timeline
  picture: main[0:cut] + intro sting + main[cut:] + outro sting  (stings optional; the hook stays first)
  encode:  once, libx264 CRF 12 slow, so UI text stays sharp; loudnorm -14 LUFS on the whole mix
usage: assemble_stems.py --voice v.m4a --music m.wav [--sfx s.wav] [--picture render.mp4] [--intro i.mp4 --outro o.mp4 --cut 4.35]
                         --out reel.mp4|mix.m4a [--secs 20]     (no --picture: the mix alone, e.g. a 20 s music sample)
Low load: niced, 4 threads. Run one heavy job at a time.
"""
import argparse, os, subprocess, tempfile
ap = argparse.ArgumentParser()
for a in ('voice', 'music', 'sfx', 'picture', 'intro', 'outro', 'out'): ap.add_argument('--' + a)
ap.add_argument('--cut', type=float); ap.add_argument('--secs', type=float); A = ap.parse_args()
run = lambda *a: subprocess.run(['nice', '-n', '10', 'ffmpeg', '-y', '-loglevel', 'error', '-threads', '4', *a], check=True)
dur = lambda f: float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f], capture_output=True, text=True).stdout)
tmp = tempfile.mkdtemp(prefix='assemble-'); mix = os.path.join(tmp, 'main.wav'); D = dur(A.picture) if A.picture else dur(A.voice)
ins = ['-i', A.music, '-i', A.voice] + (['-i', A.sfx] if A.sfx else [])
fc = ('[0:a]volume=-9dB[mu];[1:a]aresample=48000,aformat=channel_layouts=stereo,asplit=2[k][v];'
      '[mu][k]sidechaincompress=threshold=0.03:ratio=8:attack=12:release=250:makeup=1[m];'
      + (f'[v][m][2:a]amix=inputs=3' if A.sfx else '[v][m]amix=inputs=2') + f':normalize=0,apad,atrim=0:{D}[a]')
run(*ins, '-filter_complex', fc, '-map', '[a]', '-ar', '48000', mix)
st = A.intro and A.outro and A.cut is not None
full = os.path.join(tmp, 'full.m4a')
if st:
    f = lambda a, b: f'atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={b - a - 0.03:.3f}:d=0.03'
    fc = (f'[0:a]{f(0, A.cut)}[a0];[0:a]atrim={A.cut},asetpts=PTS-STARTPTS,afade=t=in:d=0.02[a1];'
          '[1:a]aresample=48000,aformat=channel_layouts=stereo,volume=-1dB[i];[2:a]aresample=48000,aformat=channel_layouts=stereo,volume=-1dB[o];'
          '[a0][i][a1][o]concat=n=4:v=0:a=1,loudnorm=I=-14:TP=-1.5:LRA=9[a]')
    run('-i', mix, '-i', A.intro, '-i', A.outro, '-filter_complex', fc, '-map', '[a]', '-ar', '48000', '-c:a', 'aac', '-b:a', '256k', full)
else:
    run('-i', mix, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=9', '-ar', '48000', '-c:a', 'aac', '-b:a', '256k', full)
if not A.picture:
    run('-i', full, *(['-t', str(A.secs)] if A.secs else []), '-c:a', 'copy', A.out); print(A.out); raise SystemExit
V = lambda i: f'[{i}:v]fps=30,scale=1080:1920:flags=lanczos,format=yuv420p'
if st:
    fc = (f'[0:v]trim=0:{A.cut},setpts=PTS-STARTPTS,fps=30,format=yuv420p[v0];[0:v]trim={A.cut},setpts=PTS-STARTPTS,fps=30,format=yuv420p[v1];'
          f'{V(1)}[vi];{V(2)}[vo];[v0][vi][v1][vo]concat=n=4:v=1:a=0[v]'); ins = ['-i', A.picture, '-i', A.intro, '-i', A.outro, '-i', full]; am = '3:a'
else:
    fc = '[0:v]fps=30,format=yuv420p[v]'; ins = ['-i', A.picture, '-i', full]; am = '1:a'
run(*ins, '-filter_complex', fc, '-map', '[v]', '-map', am, '-c:v', 'libx264', '-preset', 'slow', '-crf', '12', '-x264-params', 'threads=4',
    '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-g', '60', '-c:a', 'copy', '-movflags', '+faststart', '-shortest', A.out)
print(A.out, round(dur(A.out), 2), 's')
