"""The one reading of a GitHub issue's markdown body:
its `## <heading>` sections, its acceptance criteria and its blockers.

Interface: spans (where a section's lines sit), section (its text), criteria (its checkbox lines with their line
indexes, so the k-th can be read or ticked), blockers (the numbers under `## Blocked by`) and add_blocker.

The rules every reader shares: a heading line matches when it equals the heading once stripped (CRLF and trailing
whitespace tolerated); a heading inside a fenced code block is no heading; a section ends at the next unfenced
`# ` or `## ` line, or at the end of the body; a section named twice is read as its last occurrence unless the
caller asks for `first` or `all`; `prefix=True` also accepts a heading that only starts with the given one.
It builds on markdown_sections.fenced_lines rather than a second fence reader. Indexes count lines of
`body.split("\\n")`.
"""
import re

import markdown_sections
from ledger import STEP_RE

CRITERIA = "## Acceptance criteria"
BLOCKED_BY = "## Blocked by"
_ODD_BREAKS = re.compile("[\x0b\x0c\x1c-\x1e\x85  \r]")


def _scan(body):
    lines = body.split("\n")
    flags = markdown_sections.fenced_lines(_ODD_BREAKS.sub(" ", body))
    return lines, flags + [False] * (len(lines) - len(flags))


def _spans(lines, fenced, heading, prefix):
    found = []
    for i, line in enumerate(lines):
        text = line.strip()
        if fenced[i] or not (text == heading or prefix and text.startswith(heading)):
            continue
        end = next((j for j in range(i + 1, len(lines)) if not fenced[j] and lines[j].startswith(("# ", "## "))),
                   len(lines))
        found.append((i + 1, end))
    return found


def _chosen(found, occurrence):
    return {"first": found[:1], "last": found[-1:], "all": found}[occurrence]


def spans(body, heading, *, prefix=False):
    """(start, end) of the lines under each `heading` of body, in order:
    start the line after the heading, end exclusive."""
    lines, fenced = _scan(body)
    return _spans(lines, fenced, heading, prefix)


def section(body, heading, *, prefix=False, occurrence="last"):
    """The text under `heading` (its lines joined by newlines), or None when body has no such heading.
    `occurrence` is `first`, `last` or `all` (the matching sections' lines one after another)."""
    lines, fenced = _scan(body)
    chosen = _chosen(_spans(lines, fenced, heading, prefix), occurrence)
    if not chosen:
        return None
    return "\n".join(line for start, end in chosen for line in lines[start:end])


def criteria(body, *, prefix=False, occurrence="last"):
    """(index, line) of every unfenced checkbox line under `## Acceptance criteria`: the k-th criterion is [k - 1]."""
    lines, fenced = _scan(body)
    chosen = _chosen(_spans(lines, fenced, CRITERIA, prefix), occurrence)
    return [(i, lines[i]) for start, end in chosen for i in range(start, end)
            if not fenced[i] and STEP_RE.fullmatch(lines[i])]


def blockers(body, repo):
    """The issue numbers named under the first `## Blocked by` heading, spelled `#<n>` or as the full URL GitHub
    renders for `repo` (`<owner>/<name>`). An empty `repo` names no repository to compare against, so any
    github.com issue URL is read as local."""
    slug = re.escape(repo) if repo else r"[^/\s]+/[^/\s]+"
    ref = r"(?:#|https://github\.com/%s/issues/)(\d+)" % slug
    text = section(body, BLOCKED_BY, occurrence="first")
    return [int(n) for n in re.findall(ref, text)] if text else []


def add_blocker(body, new):
    """body with `- #<new>` (new a string of digits) listed under its `## Blocked by` heading: replacing a `None.`
    line, after the last blocker line, or under the heading; a body with no such heading gains one at its end.
    Pinned by test_coverage_blocker: it writes into EVERY section whose heading starts with `## Blocked by`
    (`## Blocked byproduct` too), replaces every line starting `None`, and adds its line again after the last
    blocker line when it also replaced a `None` line; only the exact heading line counts as a heading to create
    under. So it is not blockers()'s reading; coverage_blocker re-reads its result with blockers()."""
    blocker = "- #" + new
    lines = []
    last = None
    in_blocked = False
    heading = None
    placed = False
    for line in body.split("\n"):
        if line.startswith("## "):
            in_blocked = line.startswith("## Blocked by")
            if line == "## Blocked by" and heading is None:
                heading = len(lines)
        if in_blocked and line.startswith("None"):
            lines.append(blocker)
            placed = True
            continue
        if in_blocked and line.startswith("- #"):
            last = len(lines)
        lines.append(line)
    if last is not None:
        lines.insert(last + 1, blocker)
    elif heading is not None and not placed:
        lines.insert(heading + 1, blocker)
    if not any(line == "## Blocked by" for line in lines):
        lines = ["## Blocked by", "", blocker] if not body else lines + ["", "## Blocked by", "", blocker]
    return "\n".join(lines)
