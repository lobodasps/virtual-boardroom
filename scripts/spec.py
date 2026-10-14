"""Load the Virtual Boardroom spec (spec/): directors, rules and prompts. Standard library only.

Used by build_app.py, build_plugin.py, check_sync.py and score.py. See spec/schema.md for the formats.
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def spec_dir():
    for base in (os.environ.get("CLAUDE_PLUGIN_ROOT"), ROOT):
        if base and os.path.isdir(os.path.join(base, "spec")):
            return os.path.join(base, "spec")
    raise SystemExit("spec/ not found next to the scripts or under $CLAUDE_PLUGIN_ROOT")


def load_rules():
    with open(os.path.join(spec_dir(), "rules.json"), encoding="utf-8") as f:
        return json.load(f)


def round1(x):
    """One decimal, halves up (the app's Math.round(x*10)/10)."""
    import math
    return math.floor(x * 10 + 0.5) / 10


def round0(x):
    import math
    return int(math.floor(x + 0.5))


# ───────── frontmatter / personas ─────────

def _scalar(v):
    v = v.strip()
    if v in ("true", "false"): return v == "true"
    if re.fullmatch(r"-?\d+(\.\d+)?", v): return float(v) if "." in v else int(v)
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'": return v[1:-1]
    return v


def _value(v):
    v = v.strip()
    if v.startswith("[") and v.endswith("]"):
        return [_scalar(x) for x in v[1:-1].split(",") if x.strip()]
    if v.startswith("{") and v.endswith("}"):
        out = {}
        for part in v[1:-1].split(","):
            if ":" in part:
                k, _, x = part.partition(":"); out[k.strip()] = _scalar(x)
        return out
    return _scalar(v)


def parse_frontmatter(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.S)
    if not m: return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.lstrip().startswith("#"):
            k, _, v = line.partition(":"); meta[k.strip()] = _value(v)
    return meta, text[m.end():]


SECTIONS = {"lens": "lens", "mandate": "mandate", "always presses on": "presses", "red line": "redLine",
            "thresholds": "thresholds", "blind spots": "blindSpots", "voice": "tone"}


def parse_persona(text, slug=""):
    """Return a persona in the app's field names. Unknown sections are ignored; missing ones are empty."""
    meta, body = parse_frontmatter(text)
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    sec = {}
    for m in re.finditer(r"^##\s+(.+?)\s*\n(.*?)(?=^##\s|\Z)", body, re.S | re.M):
        key = SECTIONS.get(m.group(1).strip().lower())
        if key: sec[key] = m.group(2).strip()
    presses = [re.sub(r"^[-*•]\s+", "", l).strip() for l in sec.get("presses", "").splitlines() if l.strip()]
    color = meta.get("color") or {}
    if isinstance(color, str): color = {"light": color, "dark": color}
    lst = lambda v: v if isinstance(v, list) else ([x.strip() for x in str(v).split(",") if x.strip()] if v else [])
    return {"id": str(meta.get("id") or slug), "slug": slug, "order": meta.get("order", 99), "title": meta.get("title", ""),
            "mono": meta.get("mono", ""), "color": color, "active": meta.get("seated_by_default", True) is not False,
            "nonVoting": meta.get("non_voting", False) is True, "pestle": lst(meta.get("pestle")), "opponents": lst(meta.get("opponents")),
            "lens": sec.get("lens", ""), "mandate": sec.get("mandate", ""), "presses": presses, "redLine": sec.get("redLine", ""),
            "thresholds": sec.get("thresholds", ""), "blindSpots": sec.get("blindSpots", ""), "tone": sec.get("tone", "")}


def load_directors():
    d = os.path.join(spec_dir(), "directors"); out = []
    for name in sorted(os.listdir(d)):
        if name.endswith(".md"):
            with open(os.path.join(d, name), encoding="utf-8") as f:
                out.append(parse_persona(f.read(), name[:-3]))
    return sorted(out, key=lambda p: (p["order"], p["id"]))


def director_file(slug):
    with open(os.path.join(spec_dir(), "directors", slug + ".md"), encoding="utf-8") as f:
        return f.read()


# ───────── prompts ─────────

PH = re.compile(r"\{\{([A-Za-z0-9_.]+)\}\}")


def rule_value(rules, path):
    cur = rules
    for k in path.split("."):
        if isinstance(cur, dict) and k in cur: cur = cur[k]
        else: return None
    return cur if isinstance(cur, (int, float, str)) and not isinstance(cur, bool) else None


def fill_rules(text, rules):
    def rep(m):
        v = rule_value(rules, m.group(1))
        return m.group(0) if v is None else (f"{v:g}" if isinstance(v, float) else str(v))
    return PH.sub(rep, text)


def parse_prompt(text):
    """-> (texts {key: text}, defaults {name: value}); key "" is the main text, "x" is part x."""
    defaults = {}
    m = re.search(r"<!--\s*plugin-defaults\s*\n(.*?)-->", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, _, v = line.partition(":"); defaults[k.strip()] = v.strip()
        text = text[:m.start()] + text[m.end():]
    text = re.sub(r"^<!--\s*note:.*?-->\s*\n", "", text, flags=re.M | re.S)
    texts, key, buf = {}, "", []
    for line in text.splitlines():
        pm = re.match(r"^<!--\s*part:([A-Za-z0-9_]+)\s*-->\s*$", line)
        if pm:
            texts[key] = "\n".join(buf).strip(); key, buf = pm.group(1), []
        else: buf.append(line)
    texts[key] = "\n".join(buf).strip()
    return texts, defaults


def load_prompts(rules=None):
    """-> (prompts {"name" or "name.part": text with rule placeholders filled}, defaults {"name": {...}})."""
    rules = rules or load_rules(); d = os.path.join(spec_dir(), "prompts"); prompts, defaults = {}, {}
    for f in sorted(os.listdir(d)):
        if not f.endswith(".md"): continue
        name = f[:-3]
        with open(os.path.join(d, f), encoding="utf-8") as fh:
            texts, dflt = parse_prompt(fh.read())
        defaults[name] = dflt
        for k, t in texts.items():
            prompts[name + ("." + k if k else "")] = fill_rules(t, rules)
    return prompts, defaults


def plugin_text(prompts, defaults, key):
    """A prompt as the plugin shows it: run-time placeholders become their plugin default or <readable name>."""
    dflt = defaults.get(key.split(".")[0], {})
    def rep(m):
        n = m.group(1)
        return dflt[n] if n in dflt else "<" + n.replace("_", " ") + ">"
    return PH.sub(rep, prompts[key])


# ───────── ids ─────────

def canon(did, rules=None):
    rules = rules or load_rules()
    return (rules.get("legacy_ids") or {}).get(did, did)
