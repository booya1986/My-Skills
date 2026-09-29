// Fail if any window / card / tile leaves the 1080x1920 frame (or its safe margin) at any moment.
//   bash scripts/check_frame_fit.sh reel-<slug>/index.html [margin=20] [step=0.05]
// Seeks the composition's GSAP timeline in headless Chromium and measures every framed element while its clip is
// on screen, so the combined scale of snap + push + punch-in + element pops is what gets checked.
import path from "node:path";
import { createRequire } from "node:module";
// playwright comes from the npx cache the wrapper provides (ESM ignores NODE_PATH)
const { chromium } = createRequire(path.join(process.env.PW_MODULES || process.cwd(), "noop.js"))("playwright");

const [file, marginArg = "20", stepArg = "0.05"] = process.argv.slice(2);
if (!file) { console.error("usage: check_frame_fit.mjs index.html [margin] [step]"); process.exit(2); }
const SEL = process.env.FIT_SELECTOR ||
  ".win,.pcard,.mcard,.tile,[class*=card],[id$=Card],[id$=CardWrap],[id$=Grid],[id$=Win],[id$=Mini]";

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
await page.addInitScript(() => { window.__timelines = {}; });
await page.goto("file://" + path.resolve(file));
await page.waitForFunction(() => window.__timelines && Object.keys(window.__timelines).length > 0, null, { timeout: 15000 });
const res = await page.evaluate(({ SEL, M, STEP }) => {
  const root = document.querySelector("[data-composition-id]");
  const W = root.offsetWidth || 1080, H = root.offsetHeight || 1920;
  const tl = window.__timelines[root.dataset.compositionId] || Object.values(window.__timelines)[0];
  const end = +root.dataset.duration || tl.duration();
  const clipOf = (e) => { for (let p = e; p && p !== root; p = p.parentElement) if (p.dataset?.start !== undefined) return p; return null; };
  const els = [...document.querySelectorAll(SEL)].filter((e) => e.offsetWidth > 4 && e.offsetHeight > 4 && clipOf(e));
  const rr = root.getBoundingClientRect(), bad = {};
  for (let t = 0; t < end; t += STEP) {
    tl.seek(t);
    for (const e of els) {
      const c = clipOf(e), s = +c.dataset.start, d = +c.dataset.duration;
      if (t < s || t >= s + d || +getComputedStyle(e).opacity < 0.05) continue;
      const r = e.getBoundingClientRect();
      const L = r.left - rr.left, R = r.right - rr.left, T = r.top - rr.top, B = r.bottom - rr.top;
      const over = Math.max(M - L, R - (W - M), M - T, B - (H - M));
      const key = e.id || `${c.id} ${e.className}`;
      if (over > 0.5 && (!bad[key] || bad[key].over < over))
        bad[key] = { over: Math.round(over), t: +t.toFixed(2), box: [L, T, R, B].map(Math.round) };
    }
  }
  return { checked: els.length, bad };
}, { SEL, M: +marginArg, STEP: +stepArg });
await browser.close();

const rows = Object.entries(res.bad);
console.log(`checked ${res.checked} framed elements, margin ${marginArg}px`);
for (const [id, b] of rows) console.log(`  OUT  ${id}  by ${b.over}px at ${b.t}s  box L,T,R,B=${b.box.join(",")}`);
console.log(rows.length ? `${rows.length} element(s) leave the frame` : "NONE");
process.exit(rows.length ? 1 : 0);
