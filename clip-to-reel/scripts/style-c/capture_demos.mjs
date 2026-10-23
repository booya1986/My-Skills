// Records each demo of a live page on its own, one play-through each, sharp. The demos run on real timers and CSS
// transitions, so this is a real-time CDP screencast; frames keep their timestamps and build_demos.py makes them CFR.
// The page needs (a) a solo mode that shows one demo scaled to the window and (b) a hook that plays it and resolves
// when done. Adapt the four constants below to your page.
// usage: PAGE_URL=https://example.com/demos/ node capture_demos.mjs OUT_DIR 1 2 3 ...   (run where playwright resolves)
import fs from 'node:fs';
import { chromium } from 'playwright';
const URL0 = process.env.PAGE_URL;
const SOLO = n => `${URL0}?solo=${n}&still&once`;                    // solo mode URL
const FIT = '.demo.is-solo .fit';                                    // the element that holds the scaled demo
const PLAY = 'window.__demo.play({ loop: false })';                  // resolves when the demo has played once
const WIDE = new Set((process.env.WIDE || '').split(',').filter(Boolean).map(Number));   // browser-window demos (not phones)
const [OUT, ...ns] = process.argv.slice(2);
const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required', '--disable-renderer-backgrounding', '--disable-background-timer-throttling'] });
for (const n of ns.map(Number)) {
  // Screencast frames arrive in CSS pixels whatever the deviceScaleFactor, so render big instead: solo mode scales the
  // demo to the viewport, and a 2x viewport at DSF 1 looks like DSF 2. Keep frames <= ~1500 px wide or the fps drops.
  const vp = WIDE.has(n) ? { width: 1500, height: 1030 } : { width: 1240, height: 2000 };
  const ctx = await b.newContext({ viewport: vp, deviceScaleFactor: 1 });
  const p = await ctx.newPage();
  await p.goto(SOLO(n), { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(800);
  const box = await p.evaluate(sel => { const f = document.querySelector(sel); const el = f.firstElementChild || f; const r = el.getBoundingClientRect(); return { x: r.left, y: r.top, w: r.width, h: r.height, br: getComputedStyle(el).borderRadius, z: getComputedStyle(f).zoom }; }, FIT);
  const dir = `${OUT}/${String(n).padStart(2, '0')}/`; fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
  const cdp = await ctx.newCDPSession(p); const frames = []; let k = 0;
  cdp.on('Page.screencastFrame', ({ data, metadata, sessionId }) => {
    cdp.send('Page.screencastFrameAck', { sessionId }).catch(() => {});
    const f = `f${String(k++).padStart(5, '0')}.jpg`; frames.push([f, metadata.timestamp]); fs.writeFile(dir + f, Buffer.from(data, 'base64'), () => {});
  });
  await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 93, everyNthFrame: 1, maxWidth: vp.width, maxHeight: vp.height });
  await p.waitForTimeout(400);
  const dur = await p.evaluate(async js => { const a = performance.now(); await eval(js); return performance.now() - a; }, PLAY);
  await p.waitForTimeout(700); await cdp.send('Page.stopScreencast'); await p.waitForTimeout(300);
  fs.writeFileSync(dir + 'frames.json', JSON.stringify({ n, vp, box, playMs: dur, frames }));
  const ts = frames.map(f => f[1]); console.log(n, frames.length, 'frames', (dur / 1000).toFixed(2) + 's', 'fps', (frames.length / (ts.at(-1) - ts[0])).toFixed(1));
  await ctx.close();
}
await b.close();
