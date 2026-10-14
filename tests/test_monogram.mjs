// A director whose monogram changed (SM -> SP) with one old SM-tagged item and one new SP-tagged item, in the app:
// classifyCite/nextTag (SPEC:CITE) on the fixture, then the real app script renders the transcript and tags a new item.
import fs from "node:fs"; import path from "node:path"; import vm from "node:vm"; import { fileURLToPath } from "node:url";
const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const html = fs.readFileSync(path.join(root, "app", "strategy-boardroom.html"), "utf8");
const F = JSON.parse(fs.readFileSync(path.join(root, "tests", "fixtures", "data", "monogram.json"), "utf8")), D = F.director;
let n = 0, fails = 0; const check = (name, ok) => { n++; if (!ok) fails++; console.log((ok ? "ok   " : "FAIL ") + name); };
const block = name => html.match(new RegExp(`/\\* SPEC:${name}:BEGIN \\*/([\\s\\S]*?)/\\* SPEC:${name}:END \\*/`))[1];
const c1 = {}; vm.createContext(c1); vm.runInContext(block("CITE") + ";globalThis.__=({classifyCite,nextTag});", c1);
const tags = new Set(F.items.map(i => i.tag)), monos = new Set([D.mono, ...D.formerMonos]);
for (const [tok, want] of F.tokens) check(`classify [${tok}] -> ${want}`, c1.__.classifyCite(tok, tags, monos) === want);
check(`next tag is ${F.next_tag}`, c1.__.nextTag(D.mono, tags) === F.next_tag);
// End to end in the app script (stubbed browser, in-memory store).
const js = html.slice(html.indexOf("<script>") + 8, html.lastIndexOf("</script>"));
const el = new Proxy(function () {}, { get: (t, k) => k === "dataset" ? {} : k === "querySelectorAll" ? () => [] : k === "querySelector" ? () => null : el, set: () => true, apply: () => el });
const ctx = { console, document: el, window: { addEventListener() {} }, requestAnimationFrame: () => {}, history: { replaceState() {} }, location: { hash: "" }, setTimeout, Promise };
vm.createContext(ctx); vm.runInContext(js + ";globalThis.__t={state,md,addAttachments,loadMaterials,rebuildAttIndex,persona};", ctx); const t = ctx.__t;
await new Promise(r => setTimeout(r, 30));
check("built-in director now has SP with former SM", t.persona(D.id)?.mono === D.mono && JSON.stringify(t.persona(D.id)?.formerMonos) === JSON.stringify(D.formerMonos));
await t.addAttachments(D.id, F.items.map(i => ({ name: i.name, kind: "file", text: i.text, tag: i.tag })));
t.state.atts[D.id] = await t.loadMaterials(D.id); t.rebuildAttIndex();
const opt = { facts: { F3: { claim: "x" } }, flag: true }, h = t.md(F.transcript.replace(/ \[SM:climate-plan\.txt\]/, " [SM1]"), opt);
check("[SM1] and [SP1] render as material citations", /class="aref"[^>]*>SM1</.test(h) && /class="aref"[^>]*>SP1</.test(h));
check("[SM9] is shown as an unknown citation", /Unknown citation">SM9\?</.test(h));
check(`[CO2] stays plain text; uncited figures match the plugin (${F.expected_check.UNCITED})`, /\[CO2\]/.test(h) && opt.count === F.expected_check.UNCITED);
const made = await t.addAttachments(D.id, [{ name: "new.txt", kind: "text", text: "new" }]);
check(`a new item gets ${F.next_tag}`, made[0]?.tag === F.next_tag);
console.log(`monogram change (app): ${n - fails}/${n} cases pass`); process.exit(fails ? 1 : 0);
