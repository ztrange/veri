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
