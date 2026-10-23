// The page itself, for the lift-out-of-the-page shots.
//   tiles : the whole page as W x 2400 css tiles at DSF 2 (under the GPU texture limit) with every demo hidden,
//           plus each demo's slot rectangle in page coordinates -> OUT/tiles/tN.png + OUT/page.json
//   scroll: a real-time screencast of one smooth top-to-bottom scroll (16 s) -> OUT/scroll/ (build_demos.py scroll)
// usage: PAGE_URL=... node capture_page.mjs tiles|scroll OUT_DIR [width=1440]
// Pick the width at which the page lays the demos out the way you want them on screen (e.g. 4 phones per row).
import fs from 'node:fs';
import { chromium } from 'playwright';
const URL0 = process.env.PAGE_URL, DEMO = '.demo', FIT = '.fit', NUM = 'demo';     // demo container, its scaled child, data-* index
const [mode, OUT, w] = process.argv.slice(2); const W = +(w || 1440), TH = 2400; fs.mkdirSync(OUT, { recursive: true });
const b = await chromium.launch({ args: ['--disable-renderer-backgrounding', '--disable-background-timer-throttling'] });
const ctx = await b.newContext({ viewport: { width: W, height: mode === 'tiles' ? 1200 : 1250 }, deviceScaleFactor: mode === 'tiles' ? 2 : 1 });
const p = await ctx.newPage();
await p.goto(URL0, { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready);
const total = await p.evaluate(() => document.documentElement.scrollHeight);
if (mode === 'tiles') {
  // scroll through once so every demo has played its intro and rests in its final state
  for (let y = 0; y < total; y += 500) { await p.evaluate(y => scrollTo(0, y), y); await p.waitForTimeout(300); }
  await p.waitForTimeout(5000); await p.evaluate(() => scrollTo(0, 0)); await p.waitForTimeout(600);
  const slots = await p.evaluate(([D, F, N]) => [...document.querySelectorAll(D)].map(d => { const f = d.querySelector(F), el = f.firstElementChild || f, r = el.getBoundingClientRect(); return { n: +d.dataset[N], x: r.left, y: r.top + scrollY, w: r.width, h: r.height, br: getComputedStyle(el).borderRadius }; }), [DEMO, FIT, NUM]);
  // a strict CSP blocks injected <style> tags, so hide each node directly
  await p.evaluate(([D, F]) => document.querySelectorAll(`${D} ${F}`).forEach(e => e.style.setProperty('visibility', 'hidden', 'important')), [DEMO, FIT]);
  fs.mkdirSync(OUT + '/tiles', { recursive: true }); const tiles = [];
  for (let y = 0, i = 0; y < total; y += TH, i++) { const h = Math.min(TH, total - y); await p.screenshot({ path: `${OUT}/tiles/t${i}.png`, fullPage: true, clip: { x: 0, y, width: W, height: h } }); tiles.push({ y, h }); }
  fs.writeFileSync(OUT + '/page.json', JSON.stringify({ width: W, height: total, dsf: 2, tiles, slots }, null, 1));
  console.log('tiles', tiles.length, 'height', total, 'slots', slots.length);
} else {
  await p.waitForTimeout(1500);
  const dir = OUT + '/scroll/'; fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
  const cdp = await ctx.newCDPSession(p); const frames = []; let k = 0;
  cdp.on('Page.screencastFrame', ({ data, metadata, sessionId }) => { cdp.send('Page.screencastFrameAck', { sessionId }).catch(() => {}); const f = `f${String(k++).padStart(5, '0')}.jpg`; frames.push([f, metadata.timestamp]); fs.writeFile(dir + f, Buffer.from(data, 'base64'), () => {}); });
  await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 92, everyNthFrame: 1, maxWidth: W, maxHeight: 1250 });
  await p.waitForTimeout(500);
  await p.evaluate(() => new Promise(res => { const end = document.documentElement.scrollHeight - innerHeight, D = 16000, t0 = performance.now(); const e = k => k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2; const f = now => { const k = Math.min(1, (now - t0) / D); scrollTo(0, end * e(k)); if (k < 1) requestAnimationFrame(f); else res(); }; requestAnimationFrame(f); }));
  await p.waitForTimeout(600); await cdp.send('Page.stopScreencast'); await p.waitForTimeout(300);
  fs.writeFileSync(dir + 'frames.json', JSON.stringify({ frames, box: { x: 0, y: 0, w: W, h: 1250, br: '0px' }, playMs: 16000 }));
  console.log('scroll frames', frames.length);
}
await b.close();
