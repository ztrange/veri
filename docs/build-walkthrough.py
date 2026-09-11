#!/usr/bin/env python3
"""build-walkthrough.py — generate docs/walkthrough.html from the real scripts.

The page shows every script's FULL source beside per-chunk commentary. The source half
is read from the scripts themselves at build time, so it cannot drift; the commentary
half lives in docs/wt/commentary.py, keyed by line range.

  docs/wt/primer.py       the bash reference — one entry per construct
  docs/wt/commentary.py   prose: stage intros, per-script chunks, upkeep
  docs/wt/style.css       inlined into the page
  docs/wt/app.js          inlined into the page (tooltip layer)

Commentary may reference the primer as {{p-id|display text}}. That becomes a real
<a href="#p-id"> — working with no JS — which app.js enhances with a hover preview.

Build:  make docs        (writes docs/walkthrough.html)
Verify: make docs-check  (regenerates and diffs against the committed file)
"""
import sys
# Never cache these modules. commentary.py is edited constantly, and a same-size
# edit inside one mtime second is enough for Python to reuse stale bytecode and
# generate a page from prose that no longer exists.
sys.dont_write_bytecode = True
import html
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
SCRIPTS_DIR = ROOT / "skills" / "solve-issue" / "scripts"
OUT = HERE / "walkthrough.html"

sys.path.insert(0, str(HERE / "wt"))
import primer as primer_mod          # noqa: E402
import commentary as com             # noqa: E402
import bashlex                       # noqa: E402
import gitmeta                       # noqa: E402

# A reference is {{p-id|display}}. Display text is nearly always bash, which is full
# of braces ("${VAR:-default}"), so a regex with a lazy or negated-class body either
# stops early and eats the closing brace, or fails to match at all — both silently.
# Scan with brace depth instead, and terminate on the first "}}" seen at depth 0.
REF_OPEN = re.compile(r"\{\{([a-z0-9-]+)\|")
# any surviving {{id| after expansion is an unexpanded reference, and a bug
REF_LEFTOVER = re.compile(r"\{\{[a-z0-9-]+\|")

# ── collected while rendering, used to build the reference section ──────────────
PRIMER_BY_ID = {i["id"]: i for g in primer_mod.PRIMER for i in g["items"]}
USED_BY = {}          # primer id -> ordered list of script files referencing it
_problems = []


def _close(text, i):
    """Index just past the '}}' that closes a reference opened before i, or -1.

    Tracks brace depth so a display containing ${...} is carried through whole.
    """
    depth = 0
    while i < len(text):
        c = text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            if depth == 0 and text.startswith("}}", i):
                return i
            depth -= 1
        i += 1
    return -1


def refs(text, origin=None):
    """Expand {{p-id|display}} into a tooltip link, recording the back-reference."""
    out, pos = [], 0
    while True:
        m = REF_OPEN.search(text, pos)
        if not m:
            out.append(text[pos:])
            break
        end = _close(text, m.end())
        if end < 0:
            _problems.append("unterminated reference {{%s|…}} in %s"
                             % (m.group(1), origin or "?"))
            out.append(text[pos:m.end()])
            pos = m.end()
            continue
        rid, disp = m.group(1), text[m.end():end]
        out.append(text[pos:m.start()])
        if rid not in PRIMER_BY_ID:
            _problems.append("unknown primer ref {{%s}} in %s" % (rid, origin or "?"))
            out.append(html.escape(disp))
        else:
            if origin:
                USED_BY.setdefault(rid, [])
                if origin not in USED_BY[rid]:
                    USED_BY[rid].append(origin)
            out.append('<a class="tt" data-ref="%s" href="#%s">%s</a>' % (rid, rid, disp))
        pos = end + 2
    return "".join(out)


def code_block(lines, start, origin="?", hunk_marks=None):
    """Render source lines verbatim, with four token classes for readability.

    Verbatim is the load-bearing word. Every line is asserted to survive the lexer
    byte for byte before it is emitted, so a lexer bug stops the build instead of
    shipping a listing that no longer matches the file it claims to quote.

    hunk_marks — {line number: (tag, description)} from gitmeta — names the first line
    of each range a later version touched. It only ever changes the wrapper <span>, so
    the verbatim check above still sees the whole line: the version layer cannot alter
    a listing, only annotate it.
    """
    out = []
    hunk_marks = hunk_marks or {}
    for i, (ln, toks) in enumerate(zip(lines, bashlex.highlight(lines))):
        if "".join(t for _, t in toks) != ln:
            _problems.append("%s: highlighting altered a line, which must never happen\n"
                             "      file: %r\n      lexer: %r"
                             % (origin, ln, "".join(t for _, t in toks)))
        parts = []
        for cls, text in toks:
            esc = html.escape(text, quote=False)
            parts.append('<span class="%s">%s</span>' % (cls, esc) if cls else esc)
        mark = hunk_marks.get(start + i)
        opening = ('<span class="l hunk" data-tag="%s" title="%s">'
                   % (html.escape(mark[0]), html.escape(mark[1]))) if mark \
            else '<span class="l">'
        out.append("%s%s</span>" % (opening, "".join(parts)))
    return ('<pre class="src" style="counter-reset: ln %d">%s</pre>'
            % (start - 1, "\n".join(out)))


def render_script(spec):
    """One script: header, contract, then the full source beside its commentary."""
    fname = spec["file"]
    path = SCRIPTS_DIR / fname
    if not path.exists():
        _problems.append("missing script %s" % fname)
        return ""
    src = path.read_text().splitlines()
    total = len(src)

    # every line must be covered exactly once, in order, with no gaps
    cursor = 1
    for ch in spec["chunks"]:
        a, b = ch["lines"]
        if a != cursor:
            _problems.append("%s: chunk starts at L%d, expected L%d" % (fname, a, cursor))
        if b < a or b > total:
            _problems.append("%s: bad range L%d-%d (file has %d lines)" % (fname, a, b, total))
        cursor = b + 1
    if cursor != total + 1:
        _problems.append("%s: chunks cover %d lines, file has %d" % (fname, cursor - 1, total))

    hunk_marks = (META["marks"].get(fname) or {}).get("hunks") or {} if META else {}

    rows = []
    for ch in spec["chunks"]:
        a, b = ch["lines"]
        note = refs(ch.get("html", ""), fname)
        cls = " quiet" if ch.get("quiet") else ""
        rows.append(
            '<div class="ann-row">'
            '<div class="ann-code">%s</div>'
            '<div class="ann-note%s">%s</div>'
            "</div>" % (code_block(src[a - 1:b], a, fname, hunk_marks), cls, note))

    contract = ""
    if spec.get("contract"):
        items = "".join("<dt>%s</dt><dd>%s</dd>" % (k, refs(v, fname))
                        for k, v in spec["contract"])
        contract = '<div class="contract"><dl>%s</dl></div>' % items

    return (
        '<h3 id="%s"><code>%s</code>%s%s</h3>\n%s\n%s\n'
        '<div class="ann">'
        '<div class="ann-head"><span class="fname">%s</span>'
        '<span class="fmeta">%d lines &middot; complete source</span></div>'
        "%s</div>\n%s"
        % (spec["id"], fname,
           (" &mdash; " + spec["tagline"]) if spec.get("tagline") else "",
           version_badge(META, fname),
           refs(spec.get("blurb", ""), fname), contract,
           fname, total, "".join(rows), refs(spec.get("after", ""), fname)))


def render_versions(meta):
    """The capability index: one row per version, newest first.

    Deliberately carries no sha and no commit count — see gitmeta's docstring; both
    would change on every commit and make `make docs-check` fail until someone re-ran
    `make docs`.
    """
    rows = []
    if meta["unreleased"]:
        rows.append(
            '<li class="ver unreleased"><p class="ver-h"><span class="vtag">Unreleased</span>'
            '<span class="ver-d">on main, past %s</span></p>'
            '<p class="ver-t">Work has landed since the last version. If it had changed a '
            'capability it would have been tagged, so this is documentation, tests or '
            'tidying &mdash; or a tag nobody cut.</p></li>' % html.escape(meta["latest"]))
    for v in reversed(meta["versions"]):
        if v["scripts"]:
            reads = " &middot; ".join(
                '<a href="#%s"><code>%s</code></a>' % (SCRIPT_ID[f], f)
                for f in v["scripts"] if f in SCRIPT_ID)
            what = '<p class="ver-s"><b>Read</b>%s</p>' % reads
        else:
            what = ('<p class="ver-s conductor">Conductor only &mdash; no script on this '
                    'page changed</p>')
        issues = ""
        if v["issues"]:
            issues = '<span class="ver-i">%s</span>' % " ".join(
                ('<a href="%s/issues/%s">#%s</a>' % (ORIGIN, n, n)) if ORIGIN else "#" + n
                for n in v["issues"])
        rows.append(
            '<li class="ver"><p class="ver-h"><span class="vtag">%s</span>'
            '<span class="ver-d">%s</span>%s</p><p class="ver-t">%s</p>%s</li>'
            % (html.escape(v["tag"]), html.escape(v["date"]), issues,
               html.escape(v["title"]), what))
    return "".join(rows)


def version_badge(meta, fname):
    """`since v0.2 · changed v0.6` for one script, or "" when there is no version layer."""
    if not meta:
        return ""
    m = meta["marks"].get(fname) or {}
    since, changed = m.get("since"), m.get("changed")
    if not since:
        return '<span class="vbadge new">unreleased</span>'
    if changed and changed != since:
        return ('<span class="vbadge">since <b>%s</b> &middot; changed <b>%s</b></span>'
                % (html.escape(since), html.escape(changed)))
    return '<span class="vbadge">since <b>%s</b></span>' % html.escape(since)


def render_reference():
    """The full reference — every construct, with computed back-links."""
    groups = []
    for g in primer_mod.PRIMER:
        cards = []
        for it in g["items"]:
            used = USED_BY.get(it["id"], [])
            used_html = ""
            if used:
                links = ", ".join(
                    '<a href="#%s"><code>%s</code></a>' % (SCRIPT_ID[u], u) for u in used)
                used_html = ('<p class="used-by"><b>Referenced from</b>%s</p>' % links)
            seen = ('<p class="seen">%s</p>' % it["seen"]) if it["seen"] else ""
            cards.append(
                '<div class="card" id="%s"><code class="card-sig">%s</code>'
                '<p class="card-name">%s</p>%s%s%s</div>'
                % (it["id"], it["sig"], it["name"], it["body"], seen, used_html))
        groups.append('<div class="primer-group"><h3 id="%s">%s</h3>'
                      '<div class="cards">%s</div></div>' % (g["id"], g["name"], "".join(cards)))
    return "".join(groups)


SCRIPT_ID = {s["file"]: s["id"] for s in com.SCRIPTS}

# The version layer, read once. None in a tree with no git or no tags — which is the
# case docs/tests/build-guards.test.sh builds in, and that build must still succeed.
META = gitmeta.read(ROOT, {s["file"]: str((SCRIPTS_DIR / s["file"]).relative_to(ROOT))
                           for s in com.SCRIPTS})
ORIGIN = gitmeta.origin_url(ROOT)


def nav_entries(meta=None):
    """The rail's contents as one ordered list, in document order.

    Three things read this: the rail markup, the scrollspy that highlights the entry
    you are currently inside, and the breadcrumb that names it at the top of the page.
    Deriving all three from one list is what stops them disagreeing about where a
    section starts or what it is called.

    "head" entries are the rail's group headings and have no anchor. Every other entry
    carries `trail`: the breadcrumb path to it, outermost first, as (label, anchor-id)
    pairs. An empty anchor is a crumb that names a grouping with no heading of its own.
    """
    flow = ("The data flow", "")
    out = []
    # only when git supplied one — an entry whose heading is not on the page would be
    # dropped by the scrollspy and caught by check-walkthrough.py as a build bug
    if meta:
        out.append({"kind": "head", "label": "Capabilities"})
        out.append({"kind": "item", "id": "capabilities", "label": "What veri gained, and when",
                    "trail": [("Capabilities", "capabilities")]})
    out.append({"kind": "head", "label": "Orientation"})
    for aid, label in com.ORIENTATION_NAV:
        out.append({"kind": "item", "id": aid, "label": label,
                    "trail": [("Orientation", ""), (label, aid)]})
    out.append({"kind": "head", "label": "The data flow"})
    for st in com.STAGES:
        crumb = ("Stage %d &middot; %s" % (st["n"], st["nav"]), st["id"])
        out.append({"kind": "stage", "id": st["id"], "label": st["nav"], "n": st["n"],
                    "trail": [flow, crumb]})
        for s in com.SCRIPTS:
            if s["stage"] == st["n"]:
                out.append({"kind": "file", "id": s["id"], "label": s["file"],
                            "trail": [flow, crumb, (s["file"], s["id"])]})
    out.append({"kind": "head", "label": "Full reference"})
    out.append({"kind": "item", "id": "reference", "label": "The bash reference",
                "trail": [("Full reference", "reference")]})
    for g in primer_mod.PRIMER:
        out.append({"kind": "item", "id": g["id"], "label": g["name"],
                    "trail": [("Full reference", "reference"), (g["name"], g["id"])]})
    out.append({"kind": "head", "label": "Upkeep"})
    out.append({"kind": "item", "id": "keeping-current", "label": "Keeping this current",
                "trail": [("Upkeep", ""), ("Keeping this current", "keeping-current")]})
    if meta:
        out.append({"kind": "item", "id": "how-versions-work",
                    "label": "Where the versions come from",
                    "trail": [("Upkeep", ""), ("Where the versions come from",
                                               "how-versions-work")]})
    return out


def render_rail(entries):
    out = ['<p class="rail-mark">veri</p><p class="rail-sub">annotated source</p>',
           '<nav aria-label="Contents">']
    for e in entries:
        if e["kind"] == "head":
            out.append("<h4>%s</h4>" % e["label"])
        elif e["kind"] == "stage":
            out.append('<a href="#%s"><span class="stage">%d</span>%s</a>'
                       % (e["id"], e["n"], e["label"]))
        elif e["kind"] == "file":
            out.append('<a href="#%s"><span class="mono">%s</span></a>'
                       % (e["id"], e["label"]))
        else:
            out.append('<a href="#%s">%s</a>' % (e["id"], e["label"]))
    out.append("</nav>")
    return "".join(out)


def render_nav_json(entries):
    """The scrollspy/breadcrumb model. Anchored entries only — headings have no id."""
    import json
    d = [{"id": e["id"], "trail": [{"t": t, "h": h} for t, h in e["trail"]]}
         for e in entries if e["kind"] != "head"]
    return json.dumps(d, ensure_ascii=False, separators=(",", ":"))


def render_tips_json():
    import json
    d = {i["id"]: {"sig": i["sig"], "name": i["name"], "gloss": i["gloss"]}
         for i in PRIMER_BY_ID.values()}
    return json.dumps(d, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def main():
    body = []
    for st in com.STAGES:
        body.append('<div class="stage-head" id="%s"><p class="stage-num">Stage <b>%d</b> &middot; %s</p>'
                    "<h2>%s</h2><p class=\"stage-lede\">%s</p></div>"
                    % (st["id"], st["n"], st["kicker"], st["title"], st["lede"]))
        body.append(refs(st.get("intro", "")))
        for s in com.SCRIPTS:
            if s["stage"] == st["n"]:
                body.append(render_script(s))
    stages_html = "\n".join(body)
    reference_html = render_reference()      # after stages, so USED_BY is populated

    totals = {s["file"]: len((SCRIPTS_DIR / s["file"]).read_text().splitlines())
              for s in com.SCRIPTS if (SCRIPTS_DIR / s["file"]).exists()}
    grand = sum(totals.values())

    entries = nav_entries(META)
    page = com.PAGE_TEMPLATE.format(
        css=(HERE / "wt" / "style.css").read_text().strip(),
        tips=render_tips_json(),
        js=(HERE / "wt" / "app.js").read_text().strip(),
        rail=render_rail(entries),
        nav=render_nav_json(entries),
        intro=refs(com.INTRO_HTML).replace("{{TOTAL}}", str(grand)),
        stages=stages_html,
        reference=reference_html,
        capabilities=(com.CAPABILITIES_HTML.replace("{{ROWS}}", render_versions(META))
                      if META else ""),
        version=('<span><b>%s</b> latest version</span>' % html.escape(META["latest"]))
                if META else "",
        upkeep=refs(com.UPKEEP_HTML).replace(
            "{{TABLE}}", com.script_table(com.SCRIPTS, totals)),
        n_scripts=len(com.SCRIPTS),
        total_lines=grand,
    )

    leftover = REF_LEFTOVER.findall(re.sub(r"<script>.*?</script>", "", page, flags=re.S))
    if leftover:
        _problems.append("unexpanded references left in the page: %s"
                         % sorted(set(leftover)))

    if _problems:
        print("BUILD PROBLEMS:", file=sys.stderr)
        for p in _problems:
            print("  - " + p, file=sys.stderr)
        return 1

    if "--stdout" in sys.argv:
        sys.stdout.write(page)
    else:
        OUT.write_text(page)
        print("wrote %s — %d scripts, %d source lines, %d reference entries"
              % (OUT.relative_to(ROOT), len(com.SCRIPTS), grand, len(PRIMER_BY_ID)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
