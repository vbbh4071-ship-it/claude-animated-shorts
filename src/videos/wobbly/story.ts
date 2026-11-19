// Timeline of the train short: shots timed to the voice words,
// story physics (train position, clock times, station chaos) and camera grammar
// measured in the reference study: continuous slow push-ins; symmetric ease-in-out moves ~23 f;
// big reframes are hard cuts; impacts are 7-frame kicks; no hand-held float.
export const FPS = 30;
export const TOTAL = 1800; // 60 s
export const D0 = 6.0; // station platform height (m)
export const HALF = 27; // stations at z = +-27, span 54 m
export const FILES = [-1.65, -0.55, 0.55, 1.65];
export const ROW_GAP = 1.3;
export const COUNT = 74;
export const PARK: V3 = [70, D0, -75];
export type V3 = [number, number, number];

export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const smooth = (x: number) => { const u = clamp01(x); return u * u * (3 - 2 * u); };
export const easeOut = (u: number) => 1 - (1 - clamp01(u)) ** 4;
const lin = (pts: [number, number][], x: number) => {
  if (x <= pts[0][0]) return pts[0][1];
  for (let i = 1; i < pts.length; i++) if (x <= pts[i][0]) {
    const [x0, y0] = pts[i - 1], [x1, y1] = pts[i];
    return y0 + ((y1 - y0) * (x - x0)) / (x1 - x0);
  }
  return pts[pts.length - 1][1];
};

// ---------------- story physics (tau = story time in seconds) ----------------
// The train moves along +z through stations. Each town keeps its own solar noon,
// so the train's onboard clock drifts relative to station clocks.
export const trainZ = (tau: number) => -54 + 1.6 * tau; // z of the train front, moving +z
export const front = (tau: number) => 26 - 1.6 * (tau - 4.4);
export const clockDrift = (tau: number) => (tau % 60) / 60; // fraction of a minute gained per town
export const SNAP = 22.0, CONFUSE0 = 24.0, CONFUSE1 = 26.0, CONFUSE_H = 6.6;
export const DROP0 = CONFUSE0;
export const DROP1 = CONFUSE1;
export const DROP_H = CONFUSE_H;
export const ANCHOR: V3 = [-2.7, D0 + 0.62, -37];
export const marchPhase = (tau: number) => ((tau % 1) + 1) % 1;
export const snapEnd = (snap: number): V3 => {
  const u = easeOut(snap);
  return [ANCHOR[0] - 0.6 * u, ANCHOR[1] + 5.5 * u - 2.0 * u * u, ANCHOR[2] + 4.5 * u];
};
export const amp = (tau: number) =>
  lin([[8, 0], [12, 0.05], [16, 0.11], [20, 0.22], [SNAP, 0.4], [SNAP + 0.35, 0.0]], tau);
export const stomp = (tau: number) => lin([[12, 1.0], [16, 1.3], [20, 1.5]], tau);
export const shapeZ = (z: number) => (Math.abs(z) < HALF ? Math.cos((Math.PI * z) / (2 * HALF)) : 0);
export const dropW = (z: number) => smooth((20 - z) / 26);
export const dropU = (tau: number) => (tau < CONFUSE0 ? 0 : Math.min(1, ((tau - CONFUSE0) / (CONFUSE1 - CONFUSE0)) ** 2));

export type BridgeState = { bounce: number; drop: number; snap: number; collapsed: boolean };
export const deckY = (z: number, b: BridgeState) => D0 + b.bounce * shapeZ(z) - b.drop * CONFUSE_H * dropW(z);

// ---------------- shots ----------------
export type Light = "day" | "golden";
export type Crowd = "march" | "fall" | "water" | "bank" | "tourists" | "none";
export type ShotDef = { id: number; a: number; b: number; light: Light; crowd: Crowd; tau: (t: number) => number; towns?: boolean };
export const SHOTS: ShotDef[] = [
  { id: 1, a: 0, b: 130, light: "day", crowd: "march", tau: (t) => 29.5 + t },
  { id: 2, a: 130, b: 300, light: "day", crowd: "march", tau: (t) => t, towns: true },
  { id: 3, a: 300, b: 460, light: "day", crowd: "march", tau: (t) => t },
  { id: 4, a: 460, b: 640, light: "day", crowd: "march", tau: (t) => t },
  { id: 5, a: 640, b: 820, light: "day", crowd: "march", tau: (t) => t },
  { id: 6, a: 820, b: 980, light: "day", crowd: "march", tau: (t) => t },
  { id: 7, a: 980, b: 1120, light: "day", crowd: "march", tau: (t) => t },
  { id: 8, a: 1120, b: 1280, light: "golden", crowd: "none", tau: (t) => t },
  { id: 9, a: 1280, b: 1440, light: "golden", crowd: "march", tau: (t) => t - 31 },
  { id: 10, a: 1440, b: 1620, light: "day", crowd: "bank", tau: (t) => t },
  { id: 11, a: 1620, b: TOTAL, light: "day", crowd: "tourists", tau: (t) => t, towns: true },
];
/** crossfades (frames) at place/time changes; a white 4-frame flash after the hook */
export const XFADE: Record<number, number> = { 8: 8, 9: 8, 10: 8, 11: 8 };
export const FLASH_AT = 130;

export const shotAt = (f: number) => SHOTS.find((s) => f >= s.a && f < s.b) ?? SHOTS[SHOTS.length - 1];
export const layersAt = (f: number): { id: number; alpha: number }[] => {
  for (const s of SHOTS) {
    const x = XFADE[s.id];
    if (x && f >= s.a - x / 2 && f < s.a + x / 2) return [{ id: s.id - 1, alpha: 1 }, { id: s.id, alpha: (f - (s.a - x / 2) + 1) / (x + 1) }];
  }
  return [{ id: shotAt(f).id, alpha: 1 }];
};

export const bridgeState = (id: number, t: number): BridgeState => {
  const s = SHOTS[id - 1];
  const tau = s.tau(t);
  if (id === 10) return { bounce: 0, drop: 1, snap: 1, collapsed: true };
  const bounce = -amp(tau) * Math.cos(4 * Math.PI * (tau % 1));
  if (id === 7) return { bounce, drop: dropU(tau), snap: clamp01((tau - SNAP) / 0.7), collapsed: tau >= CONFUSE1 };
  return { bounce, drop: 0, snap: 0, collapsed: false };
};

// ---------------- camera ----------------
export type Cam = { pos: V3; look: V3; fov: number; roll: number };
type Shot = Partial<Cam> & { pos: V3; look: V3 };
type Key = { f: number; dur?: number; cut?: boolean; s: (f: number) => Shot };
export const glide = (u: number) => { const x = clamp01(u); return x * x * x * (x * (6 * x - 15) + 10); };
const mix = (a: Cam, b: Cam, k: number): Cam => ({
  pos: a.pos.map((v, i) => v + (b.pos[i] - v) * k) as V3, look: a.look.map((v, i) => v + (b.look[i] - v) * k) as V3,
  fov: a.fov + (b.fov - a.fov) * k, roll: a.roll + (b.roll - a.roll) * k,
});
const full = (c: Shot): Cam => ({ fov: 40, roll: 0, ...c });
const run = (keys: Key[], f: number) => {
  let cur = full(keys[0].s(f));
  for (let i = 1; i < keys.length; i++) {
    const k = keys[i];
    if (f < k.f) break;
    cur = k.cut ? full(k.s(f)) : mix(cur, full(k.s(f)), glide((f - k.f) / (k.dur ?? 24)));
  }
  return cur;
};
const T = (f: number) => f / FPS;
const Fz = (id: number, f: number) => trainZ(SHOTS[id - 1].tau(T(f)));
const pushK = (f: number, f0: number, rate: number, punch = 0, n = 35) => {
  const x = Math.max(0, f - f0);
  let s = rate * x;
  if (punch > rate) for (let i = 0; i < Math.min(x, n); i++) s += (punch - rate) * Math.max(0, Math.min(1, (i + 0.5) / 8, (n - i - 0.5) / 8));
  return Math.exp(-s);
};
const dolly = (pos: V3, look: V3, k: number, rest: Partial<Cam> = {}): Shot =>
  ({ pos: [look[0] + (pos[0] - look[0]) * k, look[1] + (pos[1] - look[1]) * k, look[2] + (pos[2] - look[2]) * k], look, ...rest });
const zoom = (pos: V3, look: V3, fov: number, k: number, rest: Partial<Cam> = {}): Shot =>
  ({ pos, look, fov: (360 / Math.PI) * Math.atan(Math.tan((fov * Math.PI) / 360) * k), ...rest });
const rolled = (s: (f: number) => Shot, roll: number) => (f: number): Shot => ({ ...s(f), roll });

// ---- framings (f -> camera) ----
// shot 1 (hook, flash-forward): station wide -> the impossible train
const S1a = (f: number) => { const Z = Fz(1, f); return dolly([7.5, D0 + 2.6, Z - 13], [0, D0 + 2.4, Z + 5], pushK(f, 0, 0.0025), { fov: 44 }); };
const S1b = (f: number) => { const Z = Fz(1, f); return dolly([1.4, D0 + 1.4, Z - 7.2], [0, D0 + 1.7, Z + 1.5], pushK(f, 30, 0.002), { fov: 40, roll: -0.04 }); };
const S1c = (f: number) => { const Z = Fz(1, f); return dolly([-0.9, D0 + 0.4, Z - 4.2], [0, D0 + 0.55, Z + 0.8], pushK(f, 72, 0.003), { fov: 38, roll: 0.04 }); };
// shot 2: town aerial, sun clocks on town hall
const S2a = (f: number) => zoom([17, 13, -52], [0, 9, 4], 44, pushK(f, 126, 0.002));
const S2b = (f: number) => zoom([10, 10.5, -42], [0, 8, 8], 42, pushK(f, 181, 0.002));
const S2c = (f: number) => zoom([5, 10, -31], [0, 8.6, 30], 40, pushK(f, 237, 0.0015, 0.006, 35));
// shot 3: timetables CU
const S3a = (f: number) => { const Z = Fz(3, f); return dolly([1.1, D0 + 1.45, Z - 6.2], [0, D0 + 1.3, Z + 0.6], pushK(f, 283, 0.0025)); };
const S3b = (f: number) => { const Z = Fz(3, f); return dolly([0.5, D0 + 0.36, Z - 3.5], [0, D0 + 0.3, Z + 0.4], pushK(f, 333, 0.0018), { fov: 36 }); };
// shot 4: train leaves Cleveland
const S4a = (f: number) => { const Z = Fz(4, f); return dolly([13, D0 + 2.4, Z + 7], [0, D0 + 1.2, Z + 7], pushK(f, 444, 0.002)); };
const S4b = (f: number) => { const Z = Fz(4, f); return dolly([9.5, D0 + 1.2, Z + 5.5], [0, D0 + 0.95, Z + 5.5], pushK(f, 497, 0.0015, 0.006, 30), { fov: 38, roll: -0.035 }); };
// shot 5: train arrives Pittsburgh before it left
const S5a = (f: number) => { const Z = Fz(5, f); return dolly([0.3, D0 + 1.8, Z - 4.7], [0, D0 + 1.55, Z + 1.2], pushK(f, 534, 0.0025), { fov: 38 }); };
const S5b = (f: number) => { const Z = Fz(5, f); return dolly([-0.5, D0 + 1.7, Z - 3.5], [0, D0 + 1.6, Z + 0.6], pushK(f, 576, 0.002), { fov: 36, roll: 0.04 }); };
// shot 6: confused passengers, conductors with three watches
const S6a = (f: number) => { const Z = Fz(6, f); return dolly([0.8, D0 + 1.95, Z - 2.5], [0.55, D0 + 1.85, Z], pushK(f, 643, 0.003), { fov: 34 }); };
const S6b = (f: number) => { const Z = Fz(6, f); return dolly([5.5, D0 + 5.5, Z - 9], [0, D0 + 0.8, Z + 7], pushK(f, 717, 0.002), { fov: 44, roll: -0.03 }); };
// shot 7: mystery - wait how?
const S7a = (f: number) => { const Z = Fz(7, f); return zoom([-3.0, D0 + 1.4, Z - 11], [0, D0 + 1.7, Z + 3], 46, pushK(f, 823, 0.002), { roll: -0.03 }); };
const S7b = (f: number) => { const Z = Fz(7, f); return dolly([-5.4, D0 + 4.6, Z - 2.0], [-2.7, D0 + 3.4, Z + 2.5], pushK(f, 871, 0.003), { fov: 40, roll: 0.02 }); };
const S7c = (f: number) => { const Z = Fz(7, f); return dolly([0, D0 + 1.8, Z - 3.7], [0, D0 + 1.75, Z + 0.3], pushK(f, 925, 0.0025), { fov: 36 }); };
// shot 8: pivot - You see, sun moves west
const S8a = (f: number) => zoom([14, 10.5, -47], [-1, 7, -4], 40, pushK(f, 1067, 0.0016));
// shot 9: analogy - imagine on the train
const S9a = (f: number) => { const Z = Fz(9, f); return dolly([5.75, D0 + 2.45, Z + 3.1], [0, D0 + 1.5, Z + 6.5], pushK(f, 1227, 0.002), { fov: 44 }); };
const S9b = (f: number) => { const Z = Fz(9, f); return dolly([4.8, D0 + 2.45, Z + 4], [0, D0 + 1.3, Z + 4], pushK(f, 1298, 0.0025), { fov: 40 }); };
// shot 10: consequence - four time zones, bank of clocks
const S10a = (f: number) => dolly([-4.7, D0 + 1.5, -40.4], [-4.6, D0 + 0.85, -33], pushK(f, 1387, 0.002), { fov: 42 });
const S10b = (f: number) => zoom([1.3, D0 + 1.6, -36.6], [2.9, D0 + 1.3, -31.2], 42, pushK(f, 1428, 0.0025, 0.004, 24));
// shot 11: callback - tourists, train leaves after it arrives
const S11a = (f: number) => dolly([1.7, D0 + 1.75, -15.5], [0, D0 + 1.5, -9], pushK(f, 1557, 0.0025), { fov: 40 });
const S11b = (f: number) => dolly([-1.3, D0 + 1.6, -13], [0, D0 + 1.5, -7.5], pushK(f, 1590, 0.0015, 0.006, 32), { fov: 38 });
const CRANE: V3[] = [[0, 18, -16], [17, 15, -44], [0, 7, 2]];
const S11c = (f: number): Shot => {
  const a = S11b(1672), s = glide((f - 1672) / 93), r = 1 - s, [C, B, L] = CRANE;
  return { pos: [0, 1, 2].map((i) => r * r * a.pos[i] + 2 * s * r * C[i] + s * s * B[i]) as V3,
    look: [0, 1, 2].map((i) => a.look[i] + (L[i] - a.look[i]) * s) as V3, fov: (a.fov ?? 40) + (44 - (a.fov ?? 40)) * s, roll: 0 };
};

const CAMS: Record<number, Key[]> = {
  1: [
    { f: 0, s: S1a },
    { f: 30, dur: 37, s: S1b },
    { f: 72, dur: 32, s: S1c },
  ],
  2: [
    { f: 126, s: S2a },
    { f: 181, dur: 18, s: S2b },
    { f: 237, dur: 18, s: S2c },
  ],
  3: [
    { f: 283, s: S3a },
    { f: 333, dur: 40, s: S3b },
  ],
  4: [
    { f: 444, s: S4a },
    { f: 497, cut: true, s: S4b },
    { f: 497, dur: 20, s: rolled(S4b, 0.035) },
  ],
  5: [
    { f: 534, s: S5a },
    { f: 576, dur: 18, s: S5b },
    { f: 600, dur: 20, s: rolled(S5b, -0.035) },
  ],
  6: [
    { f: 643, s: S6a },
    { f: 717, cut: true, s: S6b },
  ],
  7: [
    { f: 823, s: S7a },
    { f: 871, cut: true, s: S7b },
    { f: 925, cut: true, s: S7c },
  ],
  8: [{ f: 1067, s: S8a }],
  9: [
    { f: 1227, s: S9a },
    { f: 1298, cut: true, s: S9b },
  ],
  10: [
    { f: 1387, s: S10a },
    { f: 1428, cut: true, s: S10b },
  ],
  11: [
    { f: 1557, s: S11a },
    { f: 1590, dur: 30, s: S11b },
    { f: 1672, cut: true, s: S11c },
  ],
};

// impact kicks (reference v14): the image offset flips sign every frame, decays to 0 in 7 f
const KICKS: [number, number][] = [[SNAP, 1], [CONFUSE1, 1.6], [12.0, 0.5], [13.0, 0.5], [14.5, 0.7]];
export const kickAt = (t: number) => {
  let a = 0;
  for (const [t0, g] of KICKS) {
    const n = Math.floor((t - t0) * FPS + 1e-6);
    if (n >= 0 && n < 7) a += g * (n % 2 ? -1 : 1) * (1 - n / 7) ** 1.5;
  }
  return a;
};
export const camAt = (id: number, f: number): Cam => {
  const c = run(CAMS[id], f), a = kickAt(T(f));
  if (!a) return c;
  const d: V3 = [c.look[0] - c.pos[0], c.look[1] - c.pos[1], c.look[2] - c.pos[2]];
  const L = Math.hypot(...d), h = Math.hypot(d[0], d[2]) || 1;
  const m = (3 / 640) * Math.tan((c.fov * Math.PI) / 360) * L * a;
  return { ...c, look: [c.look[0] - (d[2] / h) * m, c.look[1] + 0.6 * m, c.look[2] + (d[0] / h) * m], roll: c.roll + a * 0.004 };
};
export const keyEnd = (id: number, f: number) => {
  let e = 0;
  for (const k of CAMS[id]) if (f >= k.f) e = k.f + (k.cut ? 0 : k.dur ?? 24);
  return Math.max(f, e);
};

// ---------------- lens: depth of field + foreground framing ----------------
export type Dof = { f: number; dur?: number; cInf: number; focus?: (f: number) => V3 };
const eyes = (id: number) => (f: number): V3 => [0, D0 + 1.6, trainZ(SHOTS[id - 1].tau(f / FPS))];
const boots = (id: number) => (f: number): V3 => [0, D0 + 0.3, trainZ(SHOTS[id - 1].tau(f / FPS))];
export const DOF: Dof[] = [
  { f: 0, cInf: 15, focus: eyes(1) },
  { f: 30, dur: 37, cInf: 15, focus: eyes(1) },
  { f: 72, dur: 32, cInf: 15, focus: boots(1) },
  { f: 130, cInf: 0 },
  { f: 333, dur: 40, cInf: 14, focus: boots(3) },
  { f: 444, cInf: 0 },
  { f: 534, cInf: 10, focus: eyes(5) },
  { f: 576, dur: 18, cInf: 12, focus: eyes(5) },
  { f: 643, cInf: 14 },
  { f: 717, cInf: 0 },
  { f: 823, cInf: 12, focus: eyes(7) },
  { f: 925, cInf: 14 },
  { f: 1067, cInf: 14 },
  { f: 1227, cInf: 5 },
  { f: 1298, cInf: 7 },
  { f: 1387, cInf: 8 },
  { f: 1428, cInf: 12, focus: () => [3.35, D0 + 1.6, -31.55] },
  { f: 1557, cInf: 0 },
  { f: 1672, cInf: 0 },
];
export const dofAt = (f: number) => {
  let i = 0; while (i + 1 < DOF.length && f >= DOF[i + 1].f) i++;
  const d = DOF[i], p = DOF[Math.max(0, i - 1)];
  const k = d.dur ? Math.min(1, (f - d.f) / d.dur) : 1;
  return { cInf: p.cInf + (d.cInf - p.cInf) * k, focus: d.focus };
};
export const focusAt = (id: number, f: number): V3 => {
  const d = dofAt(f);
  return d.focus ? d.focus(f) : camAt(id, f).look;
};

export type Fg = { a: number; b: number; kit: string; pos: V3; s?: number; yaw?: number };
export const FOREGROUND: Fg[] = [
  { a: 1387, b: 1428, kit: "cart", pos: [-3.8, D0, -38.0], s: 0.85, yaw: 0.6 },
  { a: 1227, b: 1440, kit: "plant_bushDetailed", pos: [69.65, D0, -79.4], s: 1.2, yaw: 0.4 },
];
