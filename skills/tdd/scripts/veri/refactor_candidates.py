"""refactor-candidates.sh's one candidates issue per run, filed in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import os
import re
import sys
import tempfile

try:
    from veri import github
except ImportError:
    import github

USAGE = "usage: refactor-candidates.sh <issue> <owed-file>\n"
LABELS = ("refactor", "refactor-owed")


def rows(owed):
    for line in owed.split("\n"):
        if line.startswith("- out-of-bounds | "):
            yield line
        elif line.startswith("not-done | "):
            _, reason, candidate = line.split(" | ", 2)
            yield "- %s | %s" % (reason, candidate)


def module_of(row):
    path = re.search(r"[\w.-]+/[\w./-]+", row)
    return path.group(0).split("/")[0] if path else "unsorted"


def grouped(owed):
    modules = {}
    for row in rows(owed):
        modules.setdefault(module_of(row), []).append(row)
    return "\n\n".join("## %s\n%s" % (name, "\n".join(group)) for name, group in modules.items())


def main(argv):
    if len(argv) != 2 or not re.fullmatch(r"[0-9]+", argv[0]):
        sys.stderr.write(USAGE)
        return 2
    issue, owed_file = argv
    try:
        with open(owed_file) as handle:
            owed = handle.read()
    except FileNotFoundError:
        return 3
    if not any(rows(owed)):
        return 3
    body = grouped(owed) + "\n"
    title = "Refactor candidates left by #" + issue
    found = json.loads(github.gh_issue_list("--state", "open", "--search", title + " in:title", "--json", "number,title,url"))
    existing = [row for row in found if row["title"] == title]
    if existing:
        number = str(existing[0]["number"])
        with tempfile.TemporaryDirectory() as scratch:
            body_file = os.path.join(scratch, "body.md")
            with open(body_file, "w") as handle:
                handle.write(body)
            github.gh_issue_edit(number, body_file)
        url = existing[0].get("url") or "/issues/" + number
    else:
        url = github.gh_issue_create(title, body)
        number = re.search(r"([0-9]+)\s*$", url).group(1)
        for label in LABELS:
            github.gh_issue_add_label(number, label)
    sys.stdout.write(url)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
