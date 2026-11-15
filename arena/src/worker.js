import { NW, CAP, COURSES, score } from "./sim.js";

const ORIGINS = ["https://samuelclauser54-alt.github.io", "http://localhost:8765", "http://127.0.0.1:8765"];
const BAD = /fuck|shit|bitch|nigg|fag|cunt|rape|nazi|hitler|porn|sex|dick|cock|pussy|whore|slut|kill|kys|retard|penis|vagin|anal|cum/i;
const DAILY_PER_IP = 20, MAX_ROWS = 300000;

const day = () => new Date().toISOString().slice(0, 10);
async function sha(s) { const b = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s)); return [...new Uint8Array(b)].slice(0, 12).map(x => x.toString(16).padStart(2, "0")).join(""); }
function cors(req) { const o = req.headers.get("Origin"); return { "Access-Control-Allow-Origin": ORIGINS.includes(o) ? o : ORIGINS[0], "Access-Control-Allow-Methods": "GET,POST,OPTIONS", "Access-Control-Allow-Headers": "Content-Type", "Vary": "Origin" }; }
const json = (req, obj, status = 200) => new Response(JSON.stringify(obj), { status, headers: { "Content-Type": "application/json", "Cache-Control": "no-store", ...cors(req) } });
const bump = (env, col, n = 1) => env.DB.prepare(`INSERT INTO counts (day, ${col}) VALUES (?1, ?2) ON CONFLICT(day) DO UPDATE SET ${col} = ${col} + ?2`).bind(day(), n).run();

async function board(env) {
  const top = await env.DB.prepare("SELECT name, score, gen FROM subs WHERE hidden = 0 ORDER BY score DESC, id LIMIT 20").all();
  const tot = await env.DB.prepare("SELECT COUNT(*) AS n FROM subs WHERE hidden = 0").first();
  const c = await env.DB.prepare("SELECT COALESCE(SUM(loads),0) AS loads, COALESCE(SUM(gens),0) AS gens FROM counts").first();
  return { total: tot.n, max: CAP * COURSES, top: top.results, loads: c.loads, gens: c.gens };
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url), admin = env.ADMIN_KEY && url.searchParams.get("key") === env.ADMIN_KEY;
    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: cors(req) });
    try {
      if (req.method === "GET" && url.pathname === "/top") return json(req, await board(env));

      if (req.method === "POST" && url.pathname === "/hit") {          // anonymous counters: one page load, N generations trained
        const b = await req.json().catch(() => ({})), g = Math.min(Math.max(parseInt(b.gens) || 0, 0), 5000);
        if (g) await bump(env, "gens", g); else await bump(env, "loads");
        return json(req, { ok: true });
      }

      if (req.method === "POST" && url.pathname === "/submit") {
        const b = await req.json().catch(() => null);
        if (!b || !Array.isArray(b.w) || b.w.length !== NW || !b.w.every(v => typeof v === "number" && Number.isFinite(v) && Math.abs(v) < 1e4)) return json(req, { error: "That does not look like a network from the lab." }, 400);
        const name = String(b.name || "").trim().replace(/\s+/g, " ");
        if (!/^[A-Za-z0-9_.\- ]{2,16}$/.test(name) || BAD.test(name.replace(/[^A-Za-z]/g, ""))) return json(req, { error: "Pick a nickname of 2 to 16 letters or digits." }, 400);
        const gen = Math.min(Math.max(parseInt(b.gen) || 1, 1), 1e6), w = b.w.map(v => Math.round(v * 1e4) / 1e4);
        const iph = await sha((req.headers.get("CF-Connecting-IP") || "") + day() + (env.SEED || "")), whash = await sha(JSON.stringify(w));
        const used = await env.DB.prepare("SELECT COUNT(*) AS n FROM subs WHERE iph = ?1 AND day = ?2").bind(iph, day()).first();
        if (used.n >= DAILY_PER_IP) return json(req, { error: "That is 20 entries today. Come back tomorrow." }, 429);
        const tot = await env.DB.prepare("SELECT COUNT(*) AS n FROM subs").first();
        if (tot.n >= MAX_ROWS) return json(req, { error: "The arena is full for now." }, 503);
        const s = score(w, parseInt(env.SEED || "12345") | 0);
        const ins = await env.DB.prepare("INSERT OR IGNORE INTO subs (name, w, whash, gen, score, day, iph) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7)").bind(name, JSON.stringify(w), whash, gen, s, day(), iph).run();
        if (!ins.meta.changes) return json(req, { error: "That exact network is already entered. Train it further and try again." }, 409);
        await bump(env, "subs");
        const better = await env.DB.prepare("SELECT COUNT(*) AS n FROM subs WHERE hidden = 0 AND score > ?1").bind(s).first();
        return json(req, { score: s, rank: better.n + 1, ...(await board(env)) });
      }

      if (admin && url.pathname === "/export") {
        const r = await env.DB.prepare("SELECT id, name, w, gen, score, day, hidden FROM subs ORDER BY score DESC, id LIMIT ?1").bind(parseInt(url.searchParams.get("n")) || 1000).all();
        const c = await env.DB.prepare("SELECT * FROM counts ORDER BY day").all();
        return json(req, { subs: r.results, counts: c.results });
      }
      if (admin && url.pathname === "/hide") {
        await env.DB.prepare("UPDATE subs SET hidden = ?2 WHERE id = ?1").bind(parseInt(url.searchParams.get("id")), url.searchParams.get("show") ? 0 : 1).run();
        return json(req, { ok: true });
      }
      return json(req, { error: "not found" }, 404);
    } catch (e) {
      return json(req, { error: "Something went wrong. Try again." }, 500);
    }
  }
};
