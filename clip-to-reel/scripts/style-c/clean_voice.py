#!/usr/bin/env python3
"""Narration chain for a phone-mic take in a live room: DeepFilterNet (no attenuation cap) -> WPE dereverb -> ffmpeg chain.

  1. DeepFilterNet 3 denoise, uncapped: the room between words drops ~7 dB more than with a 32 dB cap.
  2. WPE (nara_wpe): predicts late reverberation from the past frames and subtracts it; no gating, no spectral holes.
     Running it AFTER the denoiser measured best (echo tail about -25 -> -36 dB); before it, or MossFormer-style models,
     left more noise or sibilance spikes.
  3. EQ (less box at 240/420 Hz, a little chest, presence at 3.2 kHz) -> 2.5:1 compression -> downward expander (keeps the
     make-up gain from lifting the room back) -> loudnorm -14 -> split-band de-esser (LR4 at 5 kHz, sums flat; it only
     engages after loudnorm, because its threshold assumes a -14 LUFS voice) -> air shelf from 11.5 kHz -> loudnorm -14.
usage: clean_voice.py in.(wav|mp4) out.(wav|m4a) [--skip-df] [--skip-wpe]
env:   DF_PYTHON = a python with deepfilternet installed (default: this interpreter). This interpreter needs nara_wpe,
       numpy and soundfile for step 2. Measure the result with echo_tail.py and sibilance.py; do not trust it by ear alone.
"""
import os, subprocess, sys, tempfile
args = [a for a in sys.argv[1:] if not a.startswith('--')]; src, out = args
tmp = tempfile.mkdtemp(prefix='voice-'); raw = os.path.join(tmp, 'raw48.wav')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-vn', '-ac', '1', '-ar', '48000', raw], check=True)
cur = raw
if '--skip-df' not in sys.argv:
    dst = os.path.join(tmp, 'df.wav')
    subprocess.run([os.environ.get('DF_PYTHON', sys.executable), '-c', f'''
import warnings; warnings.filterwarnings("ignore")
from df.enhance import enhance, init_df, load_audio, save_audio
model, state, _ = init_df(); a, _ = load_audio({cur!r}, sr=state.sr())
save_audio({dst!r}, enhance(model, state, a, atten_lim_db=None), state.sr())'''], check=True); cur = dst
if '--skip-wpe' not in sys.argv:
    import numpy as np, soundfile as sf
    from nara_wpe.wpe import wpe
    from nara_wpe.utils import stft, istft
    SIZE, SHIFT, TAPS, DELAY, ITER = 1536, 384, 12, 3, 3      # 32/8 ms frames; skip 3 frames so direct sound + early reflections stay
    x, sr = sf.read(cur); x = x if x.ndim == 1 else x.mean(1)
    Y = stft(x[None, :], size=SIZE, shift=SHIFT).transpose(2, 0, 1)
    z = istft(wpe(Y, taps=TAPS, delay=DELAY, iterations=ITER, statistics_mode='full').transpose(1, 2, 0), size=SIZE, shift=SHIFT)[0][:len(x)]
    z *= np.max(np.abs(x)) / (np.max(np.abs(z)) + 1e-9) * 0.98
    cur = os.path.join(tmp, 'wpe.wav'); sf.write(cur, z.astype(np.float32), sr)
CHAIN = ('highpass=f=90:poles=2,equalizer=f=130:t=q:w=1.0:g=1,equalizer=f=240:t=q:w=1.4:g=-2,equalizer=f=420:t=q:w=1.0:g=-4.5,'
         'equalizer=f=3200:t=q:w=1.0:g=2.5,acompressor=threshold=-22dB:ratio=2.5:attack=8:release=120:makeup=1.6,'
         'agate=mode=downward:threshold=0.03:ratio=3:range=0.1:attack=3:release=160:knee=4,loudnorm=I=-14:TP=-1.5:LRA=7,'
         'asplit=2[dx][dy];[dx]lowpass=f=5000,lowpass=f=5000[dl];[dy]highpass=f=5000,highpass=f=5000,'
         'acompressor=threshold=-33dB:ratio=6:attack=0.3:release=45:knee=3[dh];[dl][dh]amix=inputs=2:normalize=0,'
         'equalizer=f=11500:t=h:w=6000:g=7,loudnorm=I=-14:TP=-1.5:LRA=7')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', cur, '-filter_complex', f'[0:a]{CHAIN}[a]', '-map', '[a]', '-ar', '48000',
                *(['-c:a', 'aac', '-b:a', '256k'] if out.endswith('.m4a') else []), out], check=True)
print(out)
