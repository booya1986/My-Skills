// Lift-out-of-the-page rig for a HyperFrames composition (style C). Pure function of time: render(t) writes every
// transform from t alone, so seeking, scrubbing and frame-parallel rendering all agree.
//
// Markup: two sibling 3D containers with the SAME perspective, page behind, layers in front (no depth sorting needed):
//   <div class="s3d"><div id="pg"> <img class="tile" ...> (page tiles, 2400 css px apart) <div id="stills"></div> </div></div>
//   <div class="s3d"> <video id="ly-05" class="layer" ...> ... </div>
//   .s3d { position:absolute; inset:0; perspective:1700px; perspective-origin:540px 520px; overflow:hidden }
//   #pg, .layer, .still { position:absolute; left:0; top:0; transform-origin:0 0; transform-style:preserve-3d }
// The cut-out of the speaker sits ABOVE both containers in z-order, so no layer can ever cover the face.
//
// Data: page.json from capture_page.mjs tiles -> SLOTS [[n, x, y, w, h], ...] in page css px.
export const EZ = {
  lin: k => k, out: k => 1 - Math.pow(1 - k, 3), in: k => k * k * k,
  io: k => k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2,
  whip: k => k < .5 ? 16 * Math.pow(k, 5) : 1 - Math.pow(-2 * k + 2, 5) / 2,
  back: k => { const c = 1.5, c3 = c + 1; return 1 + c3 * Math.pow(k - 1, 3) + c * Math.pow(k - 1, 2); },
};
// keys: [[t, {partial props}, ease]] -> a sampler t -> full props (each key inherits the props it does not set)
export const track = keys => {
  let cur = {}; const K = keys.map(([t, v, e]) => { cur = { ...cur, ...v }; return [t, cur, e || 'io']; });
  return t => {
    if (t <= K[0][0]) return K[0][1];
    for (let i = 1; i < K.length; i++) if (t <= K[i][0]) {
      const [a, va] = K[i - 1], [b, vb, e] = K[i], k = EZ[e]((t - a) / Math.max(1e-6, b - a)), o = {};
      for (const p in vb) o[p] = va[p] + (vb[p] - va[p]) * k; return o;
    }
    return K[K.length - 1][1];
  };
};
// A camera pose {cx, cy, rx, ry, rz, s, px, sc}: page point (px, sc) sits at screen (cx, cy), the page tilted around it.
export const pose = c => `translate3d(${c.cx}px,${c.cy}px,0) rotateX(${c.rx}deg) rotateY(${c.ry}deg) rotateZ(${c.rz}deg) scale(${c.s})`;
// A layer starts exactly on its slot, rises (lz, page px), then flies to its docked screen pose (k 0 -> 1).
export const lift = (t, dock = {}) => [[t, { k: 0, lz: 0, op: 1 }, 'lin'], [t + 0.3, { k: 0, lz: 230 }, 'out'], [t + 0.8, { k: 1, lz: 40, ...dock }, 'io']];
export const drop = (t, dock = {}) => [[t, { k: 1, lz: 40, ...dock }, 'lin'], [t + 0.3, { k: 0, lz: 120 }, 'io'], [t + 0.46, { k: 0, lz: 0 }, 'in']];
// Docks that respect the face: a phone half behind the speaker's shoulder (the speaker steps aside), a wide window full
// screen as voice-over (fade the cut-out out while it is up).
export const DOCK_PHONE = { dx: 300, dy: 790, ds: 1.45, drx: 0, dry: 6 }, DOCK_WIDE = { dx: 540, dy: 900, ds: 1.6, drx: 0, dry: 0 };

export function makeRender({ CAM, LY, SLOTS, pageEl, tiles, layerEl, stillEl, tileH = 2400 }) {
  const SL = Object.fromEntries(SLOTS.map(([n, x, y, w, h]) => [n, [x, y, w, h]]));
  return t => {
    const c = CAM(t);
    pageEl.style.transform = pose(c) + ` translate3d(${-c.px}px,${-c.sc}px,0)`;
    pageEl.style.opacity = c.op ?? 1;
    tiles.forEach((im, i) => { const y = i * tileH; im.style.visibility = (c.rx < -40 || (y < c.sc + 2600 && y + tileH > c.sc - 2600)) ? 'visible' : 'hidden'; });
    for (const n in LY) {
      const L = LY[n](t), el = layerEl[n], [sx, sy, w, h] = SL[n], k = L.k, m = (a, b) => a + (b - a) * k;
      const on = L.op > 0.001 && (c.op ?? 1) + k > 0.001;
      el.style.visibility = on ? 'visible' : 'hidden';
      if (stillEl[n]) stillEl[n].style.opacity = on && (k > 0 || L.lz > 0.5) ? 0 : 1;   // the slot empties as the layer rises
      if (!on) continue;
      el.style.opacity = L.op;
      el.style.transform = `translate3d(${m(c.cx, L.dx)}px,${m(c.cy, L.dy)}px,0) rotateX(${m(c.rx, L.drx)}deg) rotateY(${m(c.ry, L.dry)}deg) rotateZ(${m(c.rz, 0)}deg) scale(${m(c.s, L.ds)}) translate3d(${m(-c.px + sx, -w / 2)}px,${m(-c.sc + sy, -h / 2)}px,${L.lz}px)`;
      const sh = Math.max(L.lz, k * 60); el.style.boxShadow = `0 ${sh * 0.5}px ${sh * 1.2}px rgba(0,0,0,${0.25 + k * 0.3})`;
    }
  };
}
// Usage inside the composition (one paused GSAP timeline `tl`, W = anchored words):
//   const V = { cx: 540, cy: 470, rx: -16, ry: 12, rz: -5, s: 0.95, op: 1 };
//   const at = n => SLOT[n].y + SLOT[n].h / 2;                    // scroll value that centres demo n
//   const CAM = track([[0, { ...V, px: SLOT[5].x + SLOT[5].w / 2, sc: at(5) }], [W[12][0], { sc: at(17) }, 'whip'], ...]);
//   const LY = { 5: track([[0, { k: 0, lz: 0, op: 0, ...DOCK_PHONE }], [W[8][0] - 0.05, { op: 0 }, 'lin'], ...lift(W[8][0]), ...drop(W[11][0])]) };
//   const render = makeRender({ CAM, LY, SLOTS, pageEl, tiles, layerEl, stillEl });
//   const rig = { t: 0 }; tl.to(rig, { t: DUR, duration: DUR, ease: 'none', onUpdate: () => render(rig.t) }, 0); render(0);
