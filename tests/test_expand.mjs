// The app's expandQuery (SPEC:SEARCH) with the generated SYNONYMS on tests/fixtures/data/expand.json. Plain Node, no packages.
import fs from "node:fs"; import path from "node:path"; import vm from "node:vm"; import { fileURLToPath } from "node:url";
const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const html = fs.readFileSync(path.join(root, "app", "strategy-boardroom.html"), "utf8");
const block = name => html.match(new RegExp(`/\\* SPEC:${name}:BEGIN \\*/([\\s\\S]*?)/\\* SPEC:${name}:END \\*/`))[1];
const ctx = {}; vm.createContext(ctx);
vm.runInContext(block("RULES") + block("SEARCH") + ";globalThis.__=({SYNONYMS,expandQuery,termForms});", ctx);
const { SYNONYMS } = ctx.__;
const { cases, forms } = JSON.parse(fs.readFileSync(path.join(root, "tests", "fixtures", "data", "expand.json"), "utf8"));
let fails = 0;
for (const c of cases) {
  const r = JSON.parse(JSON.stringify(ctx.__.expandQuery(c.query, [...SYNONYMS, ...(c.extra_groups || [])], c.max)));
  const ok = JSON.stringify(r.added) === JSON.stringify(c.expected) && r.text === c.query + (c.expected.length ? " " + c.expected.join(" ") : "");
  if (!ok) fails++; console.log((ok ? "ok   " : "FAIL ") + c.name + (ok ? "" : `  got ${JSON.stringify(r.added)}`));
}
for (const c of forms) { const got = [...ctx.__.termForms(c.term)], ok = JSON.stringify(got) === JSON.stringify(c.expected); if (!ok) fails++;
  console.log((ok ? "ok   " : "FAIL ") + `forms of ${JSON.stringify(c.term)}` + (ok ? "" : `  got ${JSON.stringify(got)}`)); }
console.log(`app expandQuery/termForms: ${cases.length + forms.length - fails}/${cases.length + forms.length} cases pass`); process.exit(fails ? 1 : 0);
