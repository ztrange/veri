"""The one reading of an issue body's `## Blocked by` section (#460), importable by any caller
rather than locked inside solvable-issues.sh's heredoc."""
import re


def blockers(body, repo):
    """The issue numbers named under the `## Blocked by` heading, spelled `#<n>` or as the full
    URL GitHub renders for `repo` (`<owner>/<name>`). An empty `repo` names no repository to
    compare against, so any github.com issue URL is read as local."""
    slug = re.escape(repo) if repo else r"[^/\s]+/[^/\s]+"
    ref = r"(?:#|https://github\.com/%s/issues/)(\d+)" % slug
    section = re.search(r"^## Blocked by$(.*?)(?=^## |\Z)", body, re.M | re.S)
    if not section:
        return []
    return [int(n) for n in re.findall(ref, section.group(1))]


def add(body, new):
    """<body> with `- #<new>` listed under its `## Blocked by` heading: replacing a `None.` line,
    after the last blocker line, or under the heading; a body with no such heading gains one at its end."""
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
