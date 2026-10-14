// Run the app's planMaterials() (between /* SPEC:DATA:BEGIN/END */) on the budget cases from spec/schema.md.
// Plain Node, no packages.
import fs from "node:fs"; import path from "node:path"; import vm from "node:vm"; import assert from "node:assert/strict"; import { fileURLToPath } from "node:url";
const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const html = fs.readFileSync(path.join(root, "app", "strategy-boardroom.html"), "utf8");
const block = name => html.match(new RegExp(`/\\* SPEC:${name}:BEGIN \\*/([\\s\\S]*?)/\\* SPEC:${name}:END \\*/`))[1];
const ctx = {}; vm.createContext(ctx);
vm.runInContext(block("RULES") + block("DATA") + ";globalThis.__=({RULES,planMaterials});", ctx);
const { RULES } = ctx.__;
// Copy results out of the vm realm so assert.deepEqual compares plain values, not cross-realm arrays.
const planMaterials = (...a) => JSON.parse(JSON.stringify(ctx.__.planMaterials(...a)));
const item = (tag, n, extra = {}) => ({ id: tag, tag, name: tag, chars: n, text: "x".repeat(n), addedAt: 1, ...extra });
const tags = l => l.map(a => a.tag);
let n = 0; const t = (name, fn) => { fn(); n++; console.log("ok   " + name); };

const note = item("PW1", 5000, { pinned: true }), file = item("PW2", 200000);
t("tools available: pinned note in full, big file only in the index", () => {
  const p = planMaterials([note, file], RULES.OWN_BUDGET, true);
  assert.deepEqual(tags(p.full), ["PW1"]); assert.deepEqual(p.cut, []); assert.deepEqual(tags(p.indexed), ["PW2"]);
  assert.equal(p.pinnedChars, 5000); assert.equal(p.searchableChars, 200000); assert.equal(p.overPinned, false);
});
t("tools unavailable: pinned note in full, only the file is cut", () => {
  const p = planMaterials([note, file], RULES.OWN_BUDGET, false);
  assert.deepEqual(tags(p.full), ["PW1"]); assert.deepEqual(p.indexed, []);
  assert.equal(p.cut.length, 1); assert.equal(p.cut[0].item.tag, "PW2"); assert.equal(p.cut[0].keep, RULES.OWN_BUDGET - 5000);
});
t("unpinned items fill the room left, smallest first", () => {
  const p = planMaterials([item("A1", 20000), item("A2", 4000), item("A3", 9000)], RULES.OWN_BUDGET, true);
  assert.deepEqual(tags(p.full), ["A2", "A3"]); assert.deepEqual(tags(p.indexed), ["A1"]);
});
t("pinned items over budget: oldest kept, newest cut and searchable, warning raised", () => {
  const p = planMaterials([item("B1", 20000, { pinned: true, addedAt: 1 }), item("B2", 20000, { pinned: true, addedAt: 2 })], RULES.OWN_BUDGET, true);
  assert.deepEqual(tags(p.full), ["B1"]); assert.equal(p.cut[0].item.tag, "B2"); assert.equal(p.cut[0].keep, 10000);
  assert.deepEqual(tags(p.indexed), ["B2"]); assert.equal(p.overPinned, true);
});
t("shared items use SHARED_BUDGET", () => {
  const p = planMaterials([item("S1", 35000, { shared: true })], RULES.SHARED_BUDGET, true);
  assert.deepEqual(tags(p.full), ["S1"]);
});
console.log(`planMaterials: ${n}/${n} cases pass`);
