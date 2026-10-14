// Run the app's scoreVotes() (between /* SPEC:SCORE:BEGIN/END */ in app/strategy-boardroom.html) against
// tests/fixtures/*.json, with the app's generated RULES block. Plain Node, no packages.
import fs from "node:fs"; import path from "node:path"; import vm from "node:vm"; import { fileURLToPath } from "node:url";
const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const html = fs.readFileSync(path.join(root, "app", "strategy-boardroom.html"), "utf8");
const block = name => { const m = html.match(new RegExp(`/\\* SPEC:${name}:BEGIN \\*/([\\s\\S]*?)/\\* SPEC:${name}:END \\*/`)); if (!m) throw new Error(`SPEC:${name} block not found`); return m[1]; };
const ctx = {}; vm.createContext(ctx);
vm.runInContext(block("RULES") + block("SCORE") + ";globalThis.__=({RULES,scoreVotes});", ctx);
const { RULES, scoreVotes } = ctx.__;
const legacy = RULES.legacy_ids || {}, canon = id => legacy[id] || id;
const KEYS = ["rec", "label", "score", "options", "spread", "confidence", "cap_codes", "ruin", "redBreached", "redAtRisk", "weak", "support", "weights"];
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
let fails = 0; const dir = path.join(root, "tests", "fixtures"), files = fs.readdirSync(dir).filter(f => f.endsWith(".json")).sort();
for (const f of files) {
  const fx = JSON.parse(fs.readFileSync(path.join(dir, f), "utf8"));
  const votes = fx.votes.map(v => ({ id: canon(v.director), title: v.title, v }));
  const weights = Object.fromEntries(Object.entries(fx.weights || {}).map(([k, w]) => [canon(k), w]));
  const rat = Object.fromEntries((fx.ratify?.votes || []).map(r => [canon(r.director), r]));
  const out = JSON.parse(JSON.stringify(scoreVotes(votes, weights, rat, RULES)));
  const got = k => k === "options" ? Object.fromEntries(Object.entries(out.options).map(([o, x]) => [o, x.score])) : k === "weak" ? out.weak : out[k];
  const bad = KEYS.filter(k => k in fx.expected && !same(got(k), fx.expected[k])).map(k => `${k}: expected ${JSON.stringify(fx.expected[k])}, got ${JSON.stringify(got(k))}`);
  console.log((bad.length ? "FAIL " : "ok   ") + f); bad.forEach(b => console.log("     " + b)); if (bad.length) fails++;
}
console.log(`app scoreVotes: ${files.length - fails}/${files.length} fixtures pass`);
process.exit(fails || !files.length ? 1 : 0);
