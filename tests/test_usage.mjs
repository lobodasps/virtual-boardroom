// The app's buildPlan (SPEC:PLAN) and estimateUsage (SPEC:USAGE) on tests/fixtures/data/usage.json. Plain Node, no packages.
import fs from "node:fs"; import path from "node:path"; import vm from "node:vm"; import { fileURLToPath } from "node:url";
const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const html = fs.readFileSync(path.join(root, "app", "strategy-boardroom.html"), "utf8");
const block = name => html.match(new RegExp(`/\\* SPEC:${name}:BEGIN \\*/([\\s\\S]*?)/\\* SPEC:${name}:END \\*/`))[1];
const ctx = {}; vm.createContext(ctx);
vm.runInContext(block("RULES") + block("PLAN") + block("USAGE") + ";globalThis.__=({RULES,buildPlan,roundsFor,estimateUsage});", ctx);
const { RULES } = ctx.__, J = x => JSON.stringify(x);
const F = JSON.parse(fs.readFileSync(path.join(root, "tests", "fixtures", "data", "usage.json"), "utf8"));
let n = 0, fails = 0; const check = (name, ok) => { n++; if (!ok) fails++; console.log((ok ? "ok   " : "FAIL ") + name); };
for (const c of F.plans) check(`plan ${c.depth}${c.ratify ? " + ratify" : ""}${c.rounds ? ` (${c.rounds} rounds)` : ""}`,
  J([...ctx.__.buildPlan(c.rounds ?? ctx.__.roundsFor(c.depth), c.ratify, c.depth)]) === J(c.expected));
for (const c of F.usage) { const r = JSON.parse(J(ctx.__.estimateUsage(c.input, RULES))); const got = Object.fromEntries(Object.keys(c.expected).map(k => [k, r[k]]));
  check("usage: " + c.name + (J(got) === J(c.expected) ? "" : `  got ${J(got)}`), J(got) === J(c.expected)); }
console.log(`app buildPlan/estimateUsage: ${n - fails}/${n} cases pass`); process.exit(fails ? 1 : 0);
