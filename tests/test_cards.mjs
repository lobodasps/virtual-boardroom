// The app's cardSource/validateCard/parseSynonyms (SPEC:CARDS) on tests/fixtures/data/cards.json. Plain Node, no packages.
import fs from "node:fs"; import path from "node:path"; import vm from "node:vm"; import { fileURLToPath } from "node:url";
const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const html = fs.readFileSync(path.join(root, "app", "strategy-boardroom.html"), "utf8");
const block = name => html.match(new RegExp(`/\\* SPEC:${name}:BEGIN \\*/([\\s\\S]*?)/\\* SPEC:${name}:END \\*/`))[1];
const ctx = {}; vm.createContext(ctx);
vm.runInContext(block("RULES") + block("PROMPTS") + block("CARDS") + ";globalThis.__=({RULES,PROMPTS,cardSource,validateCard,parseSynonyms,cardParts,cardCalls});", ctx);
const { RULES: R, PROMPTS } = ctx.__, J = x => JSON.parse(JSON.stringify(x));
const MARK = PROMPTS["summary-card.rest_marker"];
const F = JSON.parse(fs.readFileSync(path.join(root, "tests", "fixtures", "data", "cards.json"), "utf8"));
const build = parts => parts.map(p => p.repeat ? p.repeat.repeat(p.times) : p.text).join("");
let n = 0, fails = 0; const check = (name, ok) => { n++; if (!ok) fails++; console.log((ok ? "ok   " : "FAIL ") + name); };
for (const c of F.source) {
  const r = J(ctx.__.cardSource(build(c.parts), R, MARK)), e = c.expected;
  let ok = r.truncated === e.truncated && r.headings === e.headings;
  if ("length" in e) ok = ok && r.text.length === e.length && r.text.endsWith(e.ends_with);
  if ("heading_lines" in e) ok = ok && r.text.endsWith(MARK + "\n" + e.heading_lines.join("\n")) && r.text.startsWith("a".repeat(R.cards.source_chars) + "\n\n");
  check("source: " + c.name, ok);
}
for (const c of F.validate) {
  const r = J(ctx.__.validateCard(c.card, R)), e = c.expected;
  check("validate: " + c.name, r.ok === e.ok && ("issues" in e ? JSON.stringify(r.issues) === JSON.stringify(e.issues) : r.issues[0].startsWith(e.issues_start)));
}
for (const c of F.parts) { const txt = build(c.parts), e = c.expected, ps = [...ctx.__.cardParts(txt, R)];
  check("parts: " + c.name, JSON.stringify(ps.map(x => x.length)) === JSON.stringify(e.lengths) && ps.join("") === txt.replace(/\r/g, "")
    && ctx.__.cardCalls(txt, R, true) === e.calls_whole && ctx.__.cardCalls(txt, R, false) === e.calls_quick); }
for (const c of F.synonyms) check("synonyms: " + c.name, JSON.stringify(J(ctx.__.parseSynonyms(c.card))) === JSON.stringify(c.expected));
console.log(`app cards: ${n - fails}/${n} cases pass`); process.exit(fails ? 1 : 0);
