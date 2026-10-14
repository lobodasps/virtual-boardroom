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


def load_synonyms():
    with open(os.path.join(spec_dir(), "synonyms.json"), encoding="utf-8") as f:
        return json.load(f)["groups"]


_META = re.compile(r"[.^$*+?()\[\]{}|\\]")


def term_forms(term):
    """The term plus the simple singular or plural of its last word (mirrors termForms() in the app)."""
    t = str(term or "").lower(); m = re.match(r"^(.*?)([a-z]+)$", t)
    if not m: return [t]
    pre, w = m.group(1), m.group(2); other = None
    if len(w) > 4 and w.endswith("ies"): other = w[:-3] + "y"
    elif len(w) > 4 and re.search(r"(ss|x|z|ch|sh)es$", w): other = w[:-2]
    elif len(w) > 3 and w.endswith("s") and not re.search(r"(ss|us|is)$", w): other = w[:-1]
    elif re.search(r"(s|x|z|ch|sh)$", w): other = w + "es"
    elif re.search(r"[^aeiou]y$", w): other = w[:-1] + "ies"
    else: other = w + "s"
    return [t] if other == w else [t, pre + other]


def _matcher(q):
    ql = str(q or "").lower()
    one = lambda f: re.search(r"(^|[^a-z0-9])" + _META.sub(lambda m: "\\" + m.group(0), f) + r"(?=[^a-z0-9]|$)", ql) is not None
    return lambda t: any(one(f) for f in term_forms(t))


def matched_groups(q, groups):
    has = _matcher(q)
    return [g for g in groups if any(has(t) for t in g)]


def expand_query(q, groups, max_added):
    """Mirror of expandQuery() in the app's SPEC:SEARCH block: add the other terms of every group that the
    query mentions (whole words, case-insensitive), in group order, up to max_added. -> {added, text}"""
    has = _matcher(q)
    added, seen = [], set()
    for g in groups:
        if not any(has(t) for t in g): continue
        for t in g:
            if len(added) >= max_added: break
            if not has(t) and t.lower() not in seen: seen.add(t.lower()); added.append(t)
    return {"added": added, "text": str(q or "") + ((" " + " ".join(added)) if added else "")}


def grep_pattern(terms):
    """A ripgrep alternation for a case-insensitive Grep: every term and its singular/plural form, metacharacters
    escaped, longest first."""
    forms = dict.fromkeys(f for t in terms for f in term_forms(t))
    return "|".join(_META.sub(lambda m: "\\" + m.group(0), t) for t in sorted(forms, key=lambda x: (-len(x), x)))


def plan_for(depth, ratify, rounds=None, rules=None):
    """The session's stage list; mirrors buildPlan()/roundsFor() in the app."""
    R = rules or load_rules(); stages = R["stages"].get(depth) or R["stages"]["standard"]
    rnd = lambda k: re.fullmatch(r"(challenge|response)\d+", k)
    rounds = rounds if rounds is not None else len([k for k in stages if re.fullmatch(r"challenge\d+", k)])
    base = [k for k in stages if not rnd(k)]; out = []
    for k in base:
        if k == "redteam" or (k == "vote" and "redteam" not in base):
            for i in range(1, rounds + 1): out += [f"challenge{i}", f"response{i}"]
        if ratify and k == R["ratify"]["insert_before"]: out += R["ratify"]["stages"]
        out.append(k)
    return out


def estimate_usage(inp, R):
    """Mirror of estimateUsage() in the app's SPEC:USAGE block."""
    U, W = R["usage"], R["words"]; plan = inp.get("plan") or []; own = inp.get("own") or []; n = len(own)
    shared = inp.get("shared") or 0; evidence = inp.get("evidence"); evidence = U["default_evidence_chars"] if evidence is None else evidence
    base = U["frame_chars"] + U["context_chars"] + evidence + shared; own_sum = sum(own); own_avg = round0(own_sum / n) if n else 0
    words_of = lambda k: W.get(re.sub(r"\d+$", "", k), 0)
    calls_of = lambda k: 1 if (k in U["counsel_stages"] or k == "redteam") else n
    stages = [{"stage": "plan", "calls": 1, "chars": U["frame_chars"] + U["context_chars"], "out": U["json_output_tokens"]["plan"]}]
    tx = brief_tx = 0
    for k in plan:
        calls = calls_of(k); director = k not in U["counsel_stages"]
        before = 0 if k == "brief" else brief_tx if k == "opening" else W["draft"] * U["chars_per_word"] if k == "ratify" else tx
        own_chars = 0 if not director else own_avg if k == "redteam" else own_sum
        out = calls * U["json_output_tokens"][k] if k in U["json_output_tokens"] else calls * words_of(k) * U["output_tokens_per_word"]
        stages.append({"stage": k, "calls": calls, "chars": calls * (base + before) + own_chars, "out": out})
        if k not in U["no_transcript_stages"]:
            tx += calls * words_of(k) * U["chars_per_word"]
            if k == "brief": brief_tx = tx
    total = lambda f: sum(f(x) for x in stages)
    return {"calls": total(lambda x: x["calls"]), "input_tokens": round0(total(lambda x: x["chars"]) / U["chars_per_token"]),
            "output_tokens": round0(total(lambda x: x["out"])),
            "stages": [{"stage": x["stage"], "calls": x["calls"], "input_tokens": round0(x["chars"] / U["chars_per_token"])} for x in stages]}


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
    if isinstance(cur, bool): return "yes" if cur else "no"
    return cur if isinstance(cur, (int, float, str)) else None


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
    inc = re.compile(r"\{\{@([A-Za-z0-9_.-]+)\}\}")
    for k in prompts:  # {{@prompt.part}} includes another prompt's text at build time, one level deep
        prompts[k] = inc.sub(lambda m: prompts[m.group(1)] if m.group(1) in prompts else m.group(0), prompts[k])
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


def _yaml(v):
    if isinstance(v, bool): return "true" if v else "false"
    if isinstance(v, list): return "[" + ", ".join(_yaml(x) for x in v) + "]"
    if isinstance(v, dict): return "{" + ", ".join(f"{k}: {json.dumps(x)}" for k, x in v.items()) + "}"
    s = str(v)
    return json.dumps(s) if (not s or re.search(r"[:#\[\]{},\"']", s) or s.strip() != s) else s


def render_persona(p):
    """Write a persona (app field names, as from parse_persona or a board export) back to persona.md text."""
    fm = [("id", p["id"]), ("title", p.get("title", "")), ("mono", p.get("mono", ""))]
    if p.get("color"): fm.append(("color", p["color"]))
    fm += [("seated_by_default", p.get("active", True) is not False), ("pestle", list(p.get("pestle") or [])), ("opponents", list(p.get("opponents") or []))]
    presses = p.get("presses") or []
    if isinstance(presses, str): presses = [x for x in presses.splitlines() if x.strip()]
    sec = [("Lens", p.get("lens", "")), ("Mandate", p.get("mandate", "")), ("Always presses on", "\n".join("- " + re.sub(r"^[-*•]\s*", "", x).strip() for x in presses)),
           ("Red line", p.get("redLine", "")), ("Thresholds", p.get("thresholds", "")), ("Blind spots", p.get("blindSpots", "")), ("Voice", p.get("tone", ""))]
    return "---\n" + "".join(f"{k}: {_yaml(v)}\n" for k, v in fm) + "---\n" + "".join(f"\n## {k}\n{(v or '').strip()}\n" for k, v in sec)
