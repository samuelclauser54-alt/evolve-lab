// Arena rules. Same flyer as the Evolve Lab "gates" task (4 inputs -> 6 tanh -> 1 output), on the shrinking course:
// gate k has gap height max(2.6 * 0.965^k, 0.6). Score = gates cleared, summed over 5 courses of at most 60 gates.
export const NI = 4, HID = 6, NW = NI * HID + 2 * HID + 1, CAP = 60, COURSES = 5;
const G = -22, J = 6.5, VX = 3, SP = 4, X0 = 6, DT = 1 / 30;
export const gapH = k => Math.max(2.6 * Math.pow(0.965, k), 0.6);

export function rng(seed) {                       // mulberry32
  let a = seed >>> 0;
  return () => { a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}
export function course(seed) { const r = rng(seed); return Array.from({ length: CAP + 3 }, () => 2.2 + 5.6 * r()); }

function forward(w, o0, o1, o2, o3) {
  let o = w[NI * HID + 2 * HID];
  for (let j = 0; j < HID; j++) o += Math.tanh(w[NI * HID + j] + o0 * w[j] + o1 * w[HID + j] + o2 * w[2 * HID + j] + o3 * w[3 * HID + j]) * w[NI * HID + HID + j];
  return o;
}
export function gatesCleared(w, gaps) {
  let x = 0, y = 5, vy = 0;
  for (;;) {
    const k = Math.max(Math.ceil((x - X0 - 0.25) / SP), 0), gx = X0 + k * SP;
    if (k >= CAP) return CAP;
    const o2 = (gx - x) / SP;
    x += VX * DT;
    const inside = Math.abs(x - gx) < 0.25;
    if (forward(w, (gaps[k] - y) / 5, vy / 8, o2, (gaps[k + 1] - y) / 5) > 0) vy = J; else vy += G * DT;
    y += vy * DT;
    if (y < 0 || y > 10 || (inside && Math.abs(y - gaps[k]) > gapH(k) / 2 - 0.12)) return k;
  }
}
export function score(w, seed) { let s = 0; for (let i = 0; i < COURSES; i++) s += gatesCleared(w, course(seed + 7919 * i)); return s; }
