"""stale-rows.sh's work, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import contextlib
import hashlib
import json
import io
import os
import subprocess
import sys
import tempfile

import github
import grade_prose

MARKER = "As is: these rows describe the unit's current text."


def marked_units(body):
    units, unit, lines = {}, None, []
    for line in body.splitlines() + ["## end"]:
        if line.startswith("#"):
            if unit and lines[:1] == [MARKER]:
                units[unit] = "\n".join(lines[1:])
            unit, lines = line[4:].strip(), []
        elif line.strip() or lines:
            lines.append(line)
    return units


def default_branch_text(file):
    head = subprocess.run(["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()
    return subprocess.run(["git", "show", "%s:%s" % (head, file)],
                          capture_output=True, text=True, check=True).stdout


@contextlib.contextmanager
def reading_default_branch():
    kept = grade_prose.read
    grade_prose.read = lambda file: default_branch_text(file)
    try:
        yield
    finally:
        grade_prose.read = kept


def grade(unit, rows):
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "REQUIREMENTS.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write("## %s\n\n%s\n" % (unit, rows))
        out = io.StringIO()
        with contextlib.redirect_stdout(out), reading_default_branch():
            code = grade_prose.main([path, unit])
    return code, out.getvalue()


def cached_grade(unit, rows):
    try:
        text = default_branch_text(unit.partition("#")[0])
    except Exception:
        return grade(unit, rows)
    key = hashlib.sha256(json.dumps([unit, rows, text]).encode()).hexdigest()
    path = os.path.join(".tdd", "stale-rows-cache", key)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return tuple(json.load(f))
    code, out = grade(unit, rows)
    if code != 2:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump([code, out], f)
    return code, out


def main(argv):
    if len(argv) != 1:
        print("usage: stale-rows.sh <issue>", file=sys.stderr)
        return 2
    number, code = argv[0], 0
    units = marked_units(github.gh_issue_view(number, "body"))
    if not units:
        return 3
    for unit, rows in units.items():
        unit_code, lines = cached_grade(unit, rows)
        code = code or unit_code
        if unit_code == 2:
            print("no verdict for %s" % unit, file=sys.stderr)
        for line in filter(None, lines.splitlines()):
            print("%s\t%s\t%s\t%s" % (number, line.split(":")[0], unit, line))
    return code


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
