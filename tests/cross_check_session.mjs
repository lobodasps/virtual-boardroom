// Score a real plugin session with the app's scoreVotes() and compare with what scripts/score.py wrote.
// Usage: node tests/cross_check_session.mjs <session-folder>   (run score.py on the session first)
// Plain Node, no packages. Exit 0 when both front ends agree.
import fs from "node:fs"; import path from "node:path"; import vm from "node:vm"; import { fileURLToPath } from "node:url";
const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const dir = process.argv[2]; if (!dir) { console.log("Usage: node tests/cross_check_session.mjs <session-folder>"); process.exit(1); }
const html = fs.readFileSync(path.join(root, "app", "strategy-boardroom.html"), "utf8");
const block = name => html.match(new RegExp(`/\\* SPEC:${name}:BEGIN \\*/([\\s\\S]*?)/\\* SPEC:${name}:END \\*/`))[1];
const ctx = {}; vm.createContext(ctx); vm.runInContext(block("RULES") + block("SCORE") + ";globalThis.__=({RULES,scoreVotes});", ctx);
const { RULES, scoreVotes } = ctx.__, canon = id => (RULES.legacy_ids || {})[id] || id;
const load = (f, d) => { try { return JSON.parse(fs.readFileSync(path.join(dir, f), "utf8")); } catch { return d; } };
const votes = load("votes.json", {}), py = votes.scoring;
if (!py) { console.log("votes.json has no 'scoring' yet. Run scripts/score.py on this session first."); process.exit(1); }
const weights = Object.fromEntries(Object.entries(load("calibration.json", {}).weights || {}).map(([k, w]) => [canon(k), w]));
const rat = Object.fromEntries((load("ratify.json", {}).votes || []).map(r => [canon(r.director), r]));
const app = JSON.parse(JSON.stringify(scoreVotes((votes.votes || []).map(v => ({ id: canon(v.director), title: v.title, v })), weights, rat, RULES)));
const opt = s => Object.fromEntries(Object.entries(s.options || {}).map(([k, o]) => [k, o.score]));
const checks = [["recommended option", app.rec, py.rec], ["verdict", app.label, py.label], ["score", app.score, py.score], ["option scores", opt(app), opt(py)],
  ["caps", app.cap_codes, py.cap_codes || []], ["red line breached", app.redBreached, py.redBreached || []], ["red line at risk", app.redAtRisk, py.redAtRisk || []],
  ["council confidence", app.confidence, py.confidence], ["support", app.support, py.support ?? null]];
let bad = 0;
for (const [name, a, p] of checks) { const ok = JSON.stringify(a) === JSON.stringify(p); bad += !ok; console.log(`${ok ? "match   " : "DIFFERS "} ${name}: app ${JSON.stringify(a)}${ok ? "" : ` vs score.py ${JSON.stringify(p)}`}`); }
console.log(bad ? `${bad} difference(s) between the app and score.py.` : `The app and score.py agree: ${app.label} on "${app.rec}" at ${app.score}/10.`);
process.exit(bad ? 1 : 0);
