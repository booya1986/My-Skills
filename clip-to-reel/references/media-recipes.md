# Media recipes (ffmpeg / python), as used for the approved reference build

All paths relative to `_work/<slug>/`. `src.mp4` = the source cut to the passage range plus ~0.5 s margin:
`ffmpeg -ss FROM -to TO -i SOURCE -c:v libx264 -crf 14 -preset fast -c:a aac src.mp4` (times below are on src's clock).
The crop numbers are examples from a 1920×1080 screen recording — re-measure on your own grid sheet.

## Bubble face → split lower half (1080×960)

```bash
python3 SKILL/scripts/track_bubble.py src.mp4 bubble.cmd --anchor-right 1865 --anchor-bottom 1025 \
        --hold 48.4-56.6            # ranges where the bubble is absent (full-frame speaker)
first=$(head -1 bubble.cmd | sed -E 's/.*w ([0-9]+), crop h ([0-9]+), crop x ([0-9]+), crop y ([0-9]+);/\1:\2:\3:\4/')
ffmpeg -i src.mp4 -vf "sendcmd=f=bubble.cmd,crop=$first,hqdn3d=1.5:1.5:3:3,scale=1080:960:flags=lanczos,\
unsharp=5:5:0.6,eq=contrast=1.04:brightness=-0.02:saturation=1.04,vignette=PI/4.5,noise=alls=3:allf=t" \
  -an -c:v libx264 -crf 15 face_bub.mp4
```
Measure the anchor first: crop the bottom-right 640×400 at 3–4 times, draw a 40 px grid, read the corners.

## Full-frame face

Clean window: scan sharpness + two region means at 10 fps across the full-frame stretch; the dissolve shows
as a jump in the "rightTop" mean over 0.2 s. Use only the flat middle.

```bash
# full screen 1080×1920 (crop stays above the subtitle band at y≈930)
ffmpeg -ss A -to B -i src.mp4 -vf "crop=523:930:742:0,scale=1080:1920:flags=lanczos,unsharp=5:5:0.6,\
eq=contrast=1.05:saturation=1.05:brightness=-0.02,vignette=PI/4.5,noise=alls=3:allf=t" -an -crf 15 face_full.mp4
# sharp split lower half, bigger head
ffmpeg -ss A -to B -i src.mp4 -vf "crop=800:711:600:30,scale=1080:960:flags=lanczos,unsharp=5:5:0.6,\
eq=brightness=-0.03,vignette=PI/4.5,noise=alls=2:allf=t" -an -crf 15 face_split_tight.mp4
```
Adjust the crop x so the face is centred and the bottom-left callout card is excluded.

## Web b-roll card

```bash
curl -sL -A "Mozilla/5.0" -o pexels_ID.mp4 "https://www.pexels.com/download/video/ID/"
ffmpeg -ss 1.0 -t 1.9 -i pexels_ID.mp4 -vf "scale=1280:720:flags=lanczos,eq=brightness=0.22:contrast=1.15:\
saturation=1.3:gamma=1.5,colorbalance=rs=.07:gs=.02:bs=-.06" -an -crf 16 broll_card.mp4
```

## Voice polish

```bash
ffmpeg -i vo_raw.wav -af "deesser=i=0.45:m=0.5:f=0.55,equalizer=f=6800:t=q:w=1.2:g=-4,\
acompressor=threshold=-20dB:ratio=2:attack=10:release=160:makeup=1.6,volume=1.9dB,alimiter=limit=0.89:level=false" vo.wav
```
Then render and check `ebur128` — aim for −14 ±0.7 LUFS integrated, LRA ≤ 2.6.

## Share copy (< 30 MB)

```bash
ffmpeg -i reel_9x16.mp4 -c:v libx264 -crf 21 -preset slow -c:a aac -b:a 160k -movflags +faststart reel_9x16_share.mp4
```
