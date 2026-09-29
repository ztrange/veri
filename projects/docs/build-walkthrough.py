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
ROOT = HERE.parent.parent
SCRIPTS_DIR = ROOT / "skills" / "tdd" / "scripts"
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
# Runs of source no commentary chunk claims, `<script> L<a>–<b>`, one per gap. Kept apart
# from _problems because it is the opposite kind of thing: a problem stops the build, this
# is debt the build carries and reports (issue #125).
_owed = []


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


def _hunk_runs(marks):
    """{line number: (mark, does it start the hunk)} for every line INSIDE a hunk.

    hunk_marks() keys a hunk by the line it starts on and carries the line it ends on
    inside the value. A listing is rendered one line at a time and needs the question the
    other way round — "is this line in a hunk, and is it the first of it?" — so the run is
    expanded once per script here rather than searched per line.
    """
    runs = {}
    for first, mark in marks.items():
        _tag, _description, last = mark
        for lineno in range(first, last + 1):
            runs[lineno] = (mark, lineno == first)
    return runs


def _line_open(mark, starts):
    """The opening `<span>` for one source line of a listing.

    `mark` is the `(tag, description, last line)` of the hunk this line is inside, or None
    for every other line — which is most of them, hence the plain form first.

    Every line of the run carries the `hunk` class, because the left rule the stylesheet
    draws down a hunk's side is a border on each line: CSS can say "this line is in a
    hunk" and cannot say "and the next four are too", so a class on the first line alone
    would rule one line of a nine-line run. `starts` is what keeps the tag and the
    description on the first line only, so the chip drawn from them lands once per hunk
    instead of once per line; `cont` marks the rest of the run as the continuation it is.
    """
    if not mark:
        return '<span class="l">'
    if not starts:
        return '<span class="l hunk cont">'
    tag, description, _last = mark
    return ('<span class="l hunk" data-tag="%s" title="%s">'
            % (html.escape(tag), html.escape(description)))


def code_block(lines, start, origin="?", marks=None):
    """Render source lines verbatim, with four token classes for readability.

    Verbatim is the load-bearing word. Every line is asserted to survive the lexer
    byte for byte before it is emitted, so a lexer bug stops the build instead of
    shipping a listing that no longer matches the file it claims to quote.

    marks — {first line: (tag, description, last line)} from hunk_marks() below — is keyed
    by the first line of each range a later version touched. It only ever changes the
    wrapper <span> of the lines in that range, so
    the verbatim check above still sees the whole line: the version layer cannot alter
    a listing, only annotate it.
    """
    out = []
    runs = _hunk_runs(marks or {})
    for lineno, (ln, toks) in enumerate(zip(lines, bashlex.highlight(lines)), start=start):
        if "".join(t for _, t in toks) != ln:
            _problems.append("%s: highlighting altered a line, which must never happen\n"
                             "      file: %r\n      lexer: %r"
                             % (origin, ln, "".join(t for _, t in toks)))
        parts = []
        for cls, text in toks:
            esc = html.escape(text, quote=False)
            parts.append('<span class="%s">%s</span>' % (cls, esc) if cls else esc)
        mark, starts = runs.get(lineno, (None, False))
        out.append("%s%s</span>"
                   % (_line_open(mark, starts), "".join(parts)))
    return ('<pre class="src" style="counter-reset: ln %d">%s</pre>'
            % (start - 1, "\n".join(out)))


def _owed_segment(fname, first, last):
    """One run of source no chunk claims, as a segment — and a line in the owed summary.

    The build used to refuse here, which made a line added to a script unlandable until
    somebody wrote prose for it. The page's promise was never the prose, though: it is
    that the source is the file as it is today, verbatim. So the lines still render, and
    what is missing is said in the one column that can say it — and on stderr, because a
    mark only a reader of the built page ever sees is not how whoever ran the build finds
    out what the page is behind on.
    """
    _owed.append("%s L%d–%d" % (fname, first, last))
    return (first, last, com.OWED_HTML, " owed")


def segments(spec, total):
    """The script's lines 1..total split into rows, as (first, last, note html, note class).

    One segment per chunk, in the order the chunks are written, plus one per run of lines
    no chunk claims. Every line of the file lands in exactly one segment, which is what
    makes the rendered listing verbatim: the rows are the file, cut up.

    The three ways the chunks can fail to say that are no longer one thing. A chunk that
    starts LATE leaves lines nobody wrote prose for, which since #125 is debt this page
    carries rather than a build failure: the source renders as it always does, under a
    note saying what is owed. A chunk that starts EARLY claims lines another chunk already
    claimed, and one that runs past the end of the file claims lines that do not exist;
    both are still fatal, because neither describes a listing that could be rendered at all.
    """
    fname = spec["file"]
    cursor = 1
    out = []
    for ch in spec["chunks"]:
        a, b = ch["lines"]
        if a > cursor:
            out.append(_owed_segment(fname, cursor, a - 1))
        elif a < cursor:
            _problems.append("%s: chunk starts at L%d, expected L%d" % (fname, a, cursor))
        if b < a or b > total:
            _problems.append("%s: bad range L%d-%d (file has %d lines)" % (fname, a, b, total))
        out.append((a, b, refs(ch.get("html", ""), fname),
                    " quiet" if ch.get("quiet") else ""))
        cursor = b + 1
    if cursor <= total:
        out.append(_owed_segment(fname, cursor, total))
    return out


def render_script(spec):
    """One script: header, contract, then the full source beside its commentary."""
    fname = spec["file"]
    path = SCRIPTS_DIR / fname
    if not path.exists():
        _problems.append("missing script %s" % fname)
        return ""
    src = path.read_text().splitlines()
    total = len(src)

    marks = hunk_marks(META, fname)

    rows = []
    for a, b, note, cls in segments(spec, total):
        rows.append(
            '<div class="ann-row">'
            '<div class="ann-code">%s</div>'
            '<div class="ann-note%s">%s</div>'
            "</div>" % (code_block(src[a - 1:b], a, fname, marks), cls, note))

    contract = ""
    if spec.get("contract"):
        items = "".join("<dt>%s</dt><dd>%s</dd>" % (k, refs(v, fname))
                        for k, v in spec["contract"])
        contract = '<div class="contract"><dl>%s</dl></div>' % items

    # The header's own version, as an attribute rather than as the badge's prose. A script
    # that arrived whole in a later version has no hunk anywhere in it — hunks() drops every
    # run at or below a file's own `since` — so the header is the only place in the markup
    # that can be the stop since-mode owes a reader who has never seen the script. The badge
    # beside it says the same thing to a reader; this says it to the stepper, which needs a
    # ranked tag and not a sentence. Absent, not empty, where there is no version to name:
    # `h3[data-since]` is how the stepper asks for these, and an empty attribute would offer
    # it every script on the page as a stop tagged with nothing.
    since = script_since(META, fname)
    since_attr = (' data-since="%s"' % html.escape(since)) if since else ""
    return (
        '<h3 id="%s"%s><code>%s</code>%s%s</h3>\n%s\n%s\n'
        '<div class="ann">'
        '<div class="ann-head"><span class="fname">%s</span>'
        '<span class="fmeta">%d lines &middot; complete source</span></div>'
        "%s</div>\n%s"
        % (spec["id"],
           since_attr,
           fname,
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
        # The row's own version, as an attribute rather than as the prose of its `vtag`.
        # A reader's choice collapses this index onto the versions they have not read, and
        # the client does that by hiding the rows index() does not return — which means
        # matching a row against a tag. The `vtag` says the same thing to a reader; this
        # says it to the paint, which needs the tag itself and not a heading it would have
        # to scrape. Absent on the Unreleased row above, which names no version: work past
        # the last tag is news to every reader, so no choice hides it.
        tag = html.escape(v["tag"])
        rows.append(
            '<li class="ver" data-ver="%s"><p class="ver-h"><span class="vtag">%s</span>'
            '<span class="ver-d">%s</span>%s</p><p class="ver-t">%s</p>%s</li>'
            % (tag, tag, html.escape(v["date"]), issues,
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


def hunk_marks(meta, fname):
    """One script's `{line number: (tag, description)}`, or {} when there is no version layer.

    The sibling of version_badge above: both read one script's slice of gitmeta's marks,
    and both answer for a tree that has no version layer at all rather than making every
    caller re-check — the page renders with the annotation missing, not with a traceback.
    """
    if not meta:
        return {}
    return (meta["marks"].get(fname) or {}).get("hunks") or {}


def script_since(meta, fname):
    """One script's `since` — the version it arrived in — or "" with no version layer.

    The third of the same family as version_badge and hunk_marks: one script's slice of
    gitmeta's marks, answering for a tree that has no version layer instead of making the
    caller re-check. "" rather than None for the same reason version_badge returns "":
    absent and unreleased are both "no version to rank this script by", and every caller
    of the three wants the same nothing back.
    """
    if not meta:
        return ""
    return (meta["marks"].get(fname) or {}).get("since") or ""


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
# How many issues veri has solved by being run on itself. None in a tree that cannot
# count them — read separately from META because it is a property of the history, not of
# the tags: an untagged repo still knows the number, and the claim it lands in is prose
# that belongs on the page either way.
SOLVED_BY_ITSELF = gitmeta.solved_by_itself(ROOT)


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


def render_hunks_json(meta):
    """The hunk marks inverted: `{tag: [[script, first, last, description], …]}`.

    hunk_marks() answers "which hunk starts on this line of this script", which is the
    direction the listings need and the only one the markup can express: the tagged
    <span> opens on a run's first line and carries neither the script it is in nor the
    line it ends on. A reader asking the other question — "what did v0.14 touch?" —
    cannot get there by scraping the page, so the build emits the inversion it already
    has in hand, one entry per mark and therefore one per `.hunk` span.

    {} in a tree with no version layer, for the same reason hunk_marks() returns {}: the
    client reads an empty map rather than checking whether there is one.
    """
    import json
    d = {}
    for s in com.SCRIPTS:
        for first, (tag, description, last) in sorted(hunk_marks(meta, s["file"]).items()):
            d.setdefault(tag, []).append([s["file"], first, last, description])
    return json.dumps(d, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def render_scripts_json(entries):
    """The scripts in the order the page lists them — page order, as a list.

    Since-mode walks the lit hunks in the order a reader scrolls past them, and nothing
    the client already has says what that order is: the hunk map is keyed by tag, and a
    script's name is no guide, since classify-bail.sh sorts before supervise.sh as text
    and comes after it on the page. This is nav_entries()' "file" entries, which is the
    same ordered list the listings themselves are rendered from — so the walk cannot
    disagree with the page about which script comes first.
    """
    import json
    files = [e["label"] for e in entries if e["kind"] == "file"]
    return json.dumps(files, ensure_ascii=False, separators=(",", ":"))


def render_since_of_json(meta, entries):
    """Each listed script's `since` — the version it arrived in — keyed by file name.

    Named for the global it fills, `__VERI_SINCE_OF__`, the way render_hunks_json is for
    `__VERI_HUNKS__`: `render_since_json` would name `__VERI_SINCE__`, which is a
    different thing the page already has — #70's decision layer (`lit`, `index`, `walk`,
    `choose`). That map is one of its inputs, not it.

    The hunk map cannot answer this. hunks() drops every run at or below a file's own
    `since`, because the header badge already says the script is new, so a script that
    arrived whole in v0.18 has no hunk anywhere in it — and a client holding only the map
    reads that as "nothing changed here", which is what walks a reader at v0.10 straight
    past it. The badge is prose; this is the same fact in a form the client can rank a
    script by, against the tag order render_order_json emits.

    Keyed off nav_entries()' "file" entries for the same reason render_scripts_json is:
    one answer per script the page actually lists, from the list the listings are
    rendered from.

    {} in a tree with no version layer, matching the hunk map and the tag order: the
    client reads an empty map rather than checking whether there is one — which is
    script_since()'s answer there, so this loop needs no special case for it.
    """
    import json
    d = {}
    for e in entries:
        if e["kind"] == "file":
            since = script_since(meta, e["label"])
            if since:
                d[e["label"]] = since
    return json.dumps(d, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def render_order_json(meta):
    """Every tag, oldest first, in git's version sort — the page's only version order.

    "Later than X" has to be decided in the browser, and the two orders disagree exactly
    where it matters: v0.10 sorts BEFORE v0.9 as text and AFTER it as a version, so a
    client comparing the strings it was handed hides the newest capability from the
    reader who asked for it. `window.__VERI_HUNKS__` is no help — its keys are a JSON
    object's, which is to say lexical. gitmeta already sorted the tags with
    `--sort=v:refname`; this hands that order to the client as a list, where "later"
    is just a higher index.

    [] in a tree with no version layer, so the client reads an empty list rather than
    checking whether there is one.
    """
    import json
    tags = [v["tag"] for v in meta["versions"]] if meta else []
    return json.dumps(tags, ensure_ascii=False, separators=(",", ":"))


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

    # The issues-solved-by-itself aside, or nothing at all when the tree cannot count
    # them (SOLVED_BY_ITSELF is None) — the claim around it reads the same either way.
    solved_count = com.SOLVED_COUNT_HTML % SOLVED_BY_ITSELF if SOLVED_BY_ITSELF else ""

    entries = nav_entries(META)
    page = com.PAGE_TEMPLATE.format(
        css=(HERE / "wt" / "style.css").read_text().strip(),
        tips=render_tips_json(),
        js=(HERE / "wt" / "app.js").read_text().strip(),
        rail=render_rail(entries),
        nav=render_nav_json(entries),
        hunks=render_hunks_json(META),
        scripts=render_scripts_json(entries),
        since_of=render_since_of_json(META, entries),
        order=render_order_json(META),
        pitch=refs(com.PITCH_HTML).replace("{{SOLVED}}", solved_count),
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
        n_entries=len(PRIMER_BY_ID),
    )

    leftover = REF_LEFTOVER.findall(re.sub(r"<script>.*?</script>", "", page, flags=re.S))
    if leftover:
        _problems.append("unexpanded references left in the page: %s"
                         % sorted(set(leftover)))

    # Printed whether or not the build goes on to fail: the debt is a fact about the tree,
    # not a consequence of the outcome, and a run that also hit a real problem still wants
    # to say what prose the page is missing.
    if _owed:
        print("COMMENTARY OWED:", file=sys.stderr)
        for o in _owed:
            print("  owed: " + o, file=sys.stderr)

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
