#!/usr/bin/env python3
"""Move directors and their data between the browser app and a plugin workspace (<name>.board.json).

Usage:
  board_io.py export <boardroom-dir> [<out.board.json>]        default: exports/boardroom-<date>.board.json
  board_io.py import <boardroom-dir> <file.board.json> [--overwrite | --new-only]

Import matches directors by id (in boardroom/directors/ or boardroom/removed/), keeps material tags as they are
in the file, and never deletes anything that isn't in the file. Without a flag it lists what already exists and
exits with status 2 if anything would be overwritten, so the caller can ask first; --overwrite replaces those
personas and materials, --new-only adds only what is new. Format: spec/schema.md. Standard library only.
"""
import datetime, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import materials, spec

TEXT_EXT = (".txt", ".md", ".csv", ".tsv", ".json", ".html", ".htm", ".xml")


def folders(boardroom):
    """{id: (folder, archived)} for directors/ and removed/."""
    out = {}
    for sub, archived in (("directors", False), ("removed", True)):
        base = os.path.join(boardroom, sub)
        for name in sorted(os.listdir(base)) if os.path.isdir(base) else []:
            p = os.path.join(base, name, "persona.md")
            if os.path.isfile(p):
                with open(p, encoding="utf-8") as f: d = spec.parse_persona(f.read(), name)
                out.setdefault(spec.canon(d["id"]), (os.path.join(base, name), archived))
    return out


def export(boardroom, out=None):
    defaults = {d["id"] for d in spec.load_directors()}; dirs, mats = [], []
    for did, (folder, archived) in folders(boardroom).items():
        with open(os.path.join(folder, "persona.md"), encoding="utf-8") as f: p = spec.parse_persona(f.read(), os.path.basename(folder))
        dirs.append({"id": did, "title": p["title"], "mono": p["mono"], "color": p["color"] or None, "lens": p["lens"], "mandate": p["mandate"],
                     "presses": p["presses"], "redLine": p["redLine"], "thresholds": p["thresholds"], "blindSpots": p["blindSpots"], "tone": p["tone"],
                     "pestle": p["pestle"], "opponents": p["opponents"], "custom": did not in defaults, "archived": archived, "active": p["active"]})
        items = materials.load_manifest(folder) or (materials.index(folder) if os.path.isdir(os.path.join(folder, "data")) else [])
        for it in items:
            path = os.path.join(folder, "data", it.get("file", ""))
            if not os.path.isfile(path) or not path.lower().endswith(TEXT_EXT): continue
            with open(path, encoding="utf-8", errors="ignore") as f: text = f.read()
            mats.append({"director_id": did, "tag": it.get("tag"), "name": it.get("name") or os.path.basename(path), "kind": "file",
                         "shared": bool(it.get("shared")), "pinned": bool(it.get("pinned")), "as_of": it.get("as_of", ""), "added_at": it.get("added_at", ""), "text": text})
    company = ""
    cp = os.path.join(boardroom, "company.md")
    if os.path.isfile(cp):
        with open(cp, encoding="utf-8") as f: company = f.read()
    data = {"version": 1, "exported_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "company_profile": company, "directors": dirs, "materials": mats}
    out = out or os.path.join("exports", f"boardroom-{datetime.date.today().isoformat()}.board.json")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f: json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Exported {len(dirs)} directors and {len(mats)} materials to {out}")
    return out


def slug(s): return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-") or "item"


def safe_file(name):
    base, ext = os.path.splitext(os.path.basename(str(name)))
    return slug(base) + (ext.lower() if ext.lower() in TEXT_EXT else (ext.lower() + ".txt" if ext else ".txt"))


def import_board(boardroom, path, mode=None):
    with open(path, encoding="utf-8") as f: data = json.load(f)
    if not isinstance(data.get("directors"), list): raise SystemExit("Not a board export: no directors list.")
    have = folders(boardroom); dirs = [d for d in data["directors"] if d.get("id") and d.get("title")]
    monos = {}
    for did, (folder, _) in have.items():
        with open(os.path.join(folder, "persona.md"), encoding="utf-8") as f: monos[spec.parse_persona(f.read())["mono"]] = did
    skip = {d["id"] for d in dirs if d["id"] not in have and (monos.get(d.get("mono")) not in (None, d["id"]) or d.get("mono") == "SC")}
    over_dirs = [d for d in dirs if d["id"] in have]
    mats = [m for m in data.get("materials", []) if m.get("director_id") and m.get("tag") and m["director_id"] not in skip
            and (m["director_id"] in have or any(d["id"] == m["director_id"] for d in dirs))]
    tags_of = lambda did: {it.get("tag"): it for it in materials.load_manifest(have[did][0])} if did in have else {}
    over_mats = [m for m in mats if m["tag"] in tags_of(m["director_id"])]
    print(f"{len(dirs) - len(over_dirs) - len(skip)} new director(s); {len(over_dirs)} already exist: {', '.join(d['title'] for d in over_dirs) or '-'}")
    print(f"{len(mats) - len(over_mats)} new material(s); {len(over_mats)} with existing tags: {', '.join(m['tag'] for m in over_mats) or '-'}")
    for d in dirs:
        if d["id"] in skip: print(f"Skipped {d['title']}: monogram {d.get('mono')} is already used.")
    if mode is None and (over_dirs or over_mats):
        print("Rerun with --overwrite to replace those, or --new-only to add only new items."); sys.exit(2)
    overwrite = mode == "overwrite"; nd = od = nm = om = 0
    for d in dirs:
        if d["id"] in skip: continue
        if d["id"] in have:
            if not overwrite: continue
            folder = have[d["id"]][0]; od += 1
        else:
            folder = os.path.join(boardroom, "removed" if d.get("archived") else "directors", slug(d["title"]) if not os.path.exists(os.path.join(boardroom, "directors", slug(d["title"]))) else slug(d["id"]))
            nd += 1; have[d["id"]] = (folder, bool(d.get("archived")))
        os.makedirs(os.path.join(folder, "data", "shared"), exist_ok=True)
        p = dict(d); p["pestle"] = d.get("pestle") if isinstance(d.get("pestle"), list) else [x.strip() for x in str(d.get("pestle", "")).split(",") if x.strip()]
        with open(os.path.join(folder, "persona.md"), "w", encoding="utf-8") as f: f.write(spec.render_persona(p))
    for m in mats:
        did = m["director_id"]
        if did not in have: continue
        folder = have[did][0]; items = materials.load_manifest(folder); cur = next((it for it in items if it.get("tag") == m["tag"]), None)
        if cur and not overwrite: continue
        if cur: rel = cur["file"]; om += 1
        else:
            rel = ("shared/" if m.get("shared") else "") + safe_file(m.get("name") or m["tag"]); base, ext = os.path.splitext(rel); k = 2
            while os.path.exists(os.path.join(folder, "data", rel)): rel = f"{base}-{k}{ext}"; k += 1
            nm += 1
        dest = os.path.join(folder, "data", rel); os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w", encoding="utf-8") as f: f.write(str(m.get("text", "")))
        entry = {"tag": m["tag"], "file": rel, "name": m.get("name") or os.path.basename(rel), "chars": len(str(m.get("text", ""))),
                 "shared": rel.startswith("shared/"), "pinned": bool(m.get("pinned")), "as_of": m.get("as_of", ""), "added_at": m.get("added_at", "")}
        items = [it for it in items if it.get("tag") != m["tag"]] + [entry]; materials.save_manifest(folder, items)
    cp = os.path.join(boardroom, "company.md")
    if data.get("company_profile") and (not os.path.exists(cp) or overwrite):
        with open(cp, "w", encoding="utf-8") as f: f.write(data["company_profile"])
    print(f"Imported: {nd} new director(s), {od} updated; {nm} new material(s), {om} replaced.")


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) >= 2 and a[0] == "export": export(a[1], a[2] if len(a) > 2 else None)
    elif len(a) >= 3 and a[0] == "import": import_board(a[1], a[2], "overwrite" if "--overwrite" in a else "new" if "--new-only" in a else None)
    else: print(__doc__); sys.exit(1)
