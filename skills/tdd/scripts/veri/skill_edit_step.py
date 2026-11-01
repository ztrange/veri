"""skill-edit-step.sh's entry point, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import contextlib
import io
import os
import subprocess
import tempfile
import sys

import event
import grade_prose
import skill_edit_guard
import tunables
import requirements

try:
    from veri import leaf
except ImportError:
    import leaf

USAGE = "usage: skill-edit-step.sh [--change \"<change>\"] [--added \"<step>\"] <issue-body-file> <unit-file> [<pin-file>...]"
TABLE_HEAD = ["| ID | Requirement | Why |", "|---|---|---|"]


def _row_id(row):
    return requirements.split_cells(row)[1]


def _requirements_lines(issue):
    return requirements.requirements_lines(requirements.read_lines(issue))


def _names_unit(heading, unit):
    return heading in (unit, unit + " (new)")


def _issue_rows(issue, unit):
    rows = [line for heading, line in _requirements_lines(issue)
            if _names_unit(heading, unit) and line.startswith("|")]
    return rows[2:]


def _unknown_heading(issue):
    for heading, line in _requirements_lines(issue):
        if line.startswith("### ") and not heading.endswith(" (new)") and not os.path.exists(heading):
            return heading
    return None


def _rows_outside_requirements(issue, unit):
    inside = False
    for line in requirements.read_lines(issue):
        if line.startswith("## "):
            inside = line[3:].strip() == unit
        elif inside and line.startswith("|"):
            return True
    return False


def _refusal(issue, unit):
    unknown = _unknown_heading(issue)
    if unknown:
        return "Requirements heading names no existing unit: " + unknown
    if _rows_outside_requirements(issue, unit):
        return "rows for %s are not under ## Requirements" % unit
    if any(heading is None and line.startswith("|") for heading, line in _requirements_lines(issue)):
        return "a ## Requirements row is under no ### unit heading"
    if (any(l.strip() == "## Requirements" for l in requirements.read_lines(issue))
            and not any(_names_unit(h, unit) for h, _ in _requirements_lines(issue))):
        return "## Requirements has no ### heading for unit: " + unit
    return None


def _write(path, lines):
    with open(path, "w", encoding="utf-8", errors="surrogateescape") as f:
        f.write("\n".join(lines))


def _trimmed(lines):
    while lines and lines[-1] == "":
        lines.pop()
    return lines


def _claimed(path, unit):
    return os.path.exists(path) and requirements.claims(path, unit)


def _listed_ids(path, unit):
    return {row.split("\t")[0] for row in (_claimed(path, unit) or "").splitlines()}


def _append_section(path, unit, table):
    existing = _trimmed(requirements.read_lines(path)) if os.path.exists(path) else []
    _write(path, existing + [""] * bool(existing) + ["## " + unit, ""] + table + [""])


def _write_list(path, unit, rows):
    _append_section(path, unit, TABLE_HEAD + _numbered(rows, {_row_id(r) for r in rows}))


def _create(unit, path, rows):
    os.makedirs(os.path.dirname(unit) or ".", exist_ok=True)
    open(unit, "w").close()
    _write_list(path, unit, rows)


def _move_table(unit, path):
    lines = requirements.read_lines(unit)
    start = next((n for n, l in enumerate(lines) if l.strip() == "## Requirements"), None)
    if start is None:
        return False
    end = next((n for n in range(start + 1, len(lines)) if lines[n].startswith("## ")), len(lines))
    table = [l for l in lines[start:end] if l.startswith("|")]
    if not table:
        return False
    _append_section(path, unit, table)
    _write(unit, _trimmed(lines[:start] + lines[end:]) + [""])
    return True


def _numbered(rows, have):
    have = set(have)
    out = []
    for row in rows:
        cells = requirements.split_cells(row)
        if cells[1].endswith("<next>"):
            prefix = cells[1][:-len("<next>")]
            top = max([int(i[len(prefix):]) for i in have if i.startswith(prefix) and i[len(prefix):].isdigit()],
                      default=0)
            cells[1] = "%s%d" % (prefix, top + 1)
            row = row.replace("<next>", str(top + 1), 1)
            have.add(cells[1])
        out.append(row)
    return out


def apply(issue, unit):
    path = skill_edit_guard.list_path(unit)
    moved = not _claimed(path, unit) and os.path.exists(unit) and _move_table(unit, path)
    rows = _issue_rows(issue, unit)
    if rows and not os.path.exists(unit):
        _create(unit, path, rows)
        return True
    claimed = _claimed(path, unit)
    if not rows and not claimed:
        return moved
    if not claimed:
        _write_list(path, unit, rows)
        return moved
    have = _listed_ids(path, unit)
    rows = _numbered(rows, have | {_row_id(r) for r in rows})
    new = [r for r in rows if _row_id(r) not in have]
    reworded = {_row_id(r): r for r in rows}
    lines = requirements.read_lines(path)
    last = None
    in_unit = False
    for number, line in enumerate(lines):
        if line.startswith("## "):
            in_unit = line[3:] == unit
        elif in_unit and line.startswith("|"):
            last = number
            row = reworded.get(_row_id(line), line)
            lines[number] = None if requirements.split_cells(row)[2] == "(dropped)" else row
    lines[last + 1:last + 1] = new
    _write(path, [l for l in lines if l is not None])
    return moved


_attempt = [1]
_pins = [()]
_change = [None]


def _author(unit, path, reasons):
    rows = "".join("%s: %s\n" % tuple(r.split("\t", 1)) for r in requirements.claims(path, unit).splitlines())
    text = ("You edit the prose of %s so that it satisfies every requirement below.\n\nUnit: %s\n\n%s\n\n"
            "Requirements:\n%s\nGrader FAIL reasons:\n%s\n"
            % (unit, unit, grade_prose.unit_text(unit), rows, reasons))
    if _change[0]:
        text += "\nChange to make: %s\n" % _change[0]
    if _pins[0]:
        text += ("\nPin files: %s\nUpdate there the checksum or verbatim pin of any sentence of the unit "
                 "you change.\n" % ", ".join(_pins[0]))
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write(text)
    env = dict(os.environ)
    env["PATH"] = grade_prose.modern_python_dir() + env.get("PATH", "")
    try:
        return leaf.launch("author-skill-edit-%d" % _attempt[0], f.name,
                           "--permission-mode", "bypassPermissions", env=env).returncode
    finally:
        os.unlink(f.name)


def _captured(main, argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = main(argv)
    return code, out.getvalue()


def _grade(path, unit):
    return _captured(grade_prose.main, [path, unit])


def _guard(unit, base, issue, pins, own=()):
    code, out = _captured(skill_edit_guard.main, [unit, base, *pins])
    if code == 2:
        return 2, out
    offending = [p for p in out.splitlines() if p != issue and p not in own]
    return int(bool(offending)), "".join(p + "\n" for p in offending)


def _restore(snapshot, *names):
    for name in names:
        if name in snapshot:
            with open(name, "wb") as f:
                f.write(snapshot[name])
        elif os.path.exists(name):
            os.unlink(name)


def _read_existing(names):
    snapshot = {}
    for name in names:
        if os.path.exists(name):
            with open(name, "rb") as f:
                snapshot[name] = f.read()
    return snapshot


def _tree():
    tree = {}
    present = set()
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in (".git", ".tdd")]
        present.update(os.path.relpath(os.path.join(root, d)) for d in dirs)
        for name in files:
            path = os.path.relpath(os.path.join(root, name))
            present.add(path)
            with open(path, "rb") as f:
                tree[path] = f.read()
    return tree, present


def main(argv):
    flags = {"--added": None, "--change": None}
    while len(argv) >= 4 and argv[0] in flags:
        flags[argv[0]], argv = argv[1], argv[2:]
    added, change = flags["--added"], flags["--change"]
    if len(argv) < 2:
        print(USAGE, file=sys.stderr)
        return 2
    issue, unit, *pins = argv
    budget = tunables.read("VERI_SKILL_EDIT_BUDGET", "3")
    if not (budget.isdecimal() and int(budget) >= 1):
        print("VERI_SKILL_EDIT_BUDGET must be a whole number >= 1: " + budget, file=sys.stderr)
        return 2
    refusal = _refusal(issue, unit)
    if refusal:
        print(refusal, file=sys.stderr)
        return 2
    issue_rows = _issue_rows(issue, unit)
    for row in issue_rows:
        if not requirements.well_formed_row_id(_row_id(row)):
            print("Requirement row ID is neither <prefix><digits> nor <prefix><next>: " + _row_id(row),
                  file=sys.stderr)
            return 2
    explicit = [_row_id(r) for r in issue_rows if not _row_id(r).endswith("<next>")]
    for dup in explicit:
        if explicit.count(dup) > 1:
            print("Requirement rows resolve to the same ID twice: " + dup, file=sys.stderr)
            return 2
    base = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    path = skill_edit_guard.list_path(unit)
    graded_file = grade_prose.graded_path(unit)
    snapshot = _read_existing((path, unit, graded_file))

    def undo():
        _restore(snapshot, path, unit, graded_file)

    listed = _listed_ids(path, unit)
    fresh = any(_row_id(r) not in listed for r in issue_rows)
    moved = apply(issue, unit)
    if not _claimed(path, unit):
        if added is not None:
            print("added step names a unit no requirements list claims, so nothing would change: " + added,
                  file=sys.stderr)
            undo()
            return 2
        return 3
    if os.path.getsize(unit):
        graded, said = _grade(path, unit)
    else:
        graded, said = 1, "FAIL: unit is empty\n"
    if added is not None and graded == 0 and change is None and not fresh:
        print("added step graded PASS before any author ran, so no prose would change: " + added, file=sys.stderr)
        undo()
        return 2
    authored = graded == 1 or change is not None
    _change[0] = change
    before = _read_existing([unit, *pins])
    for attempt in range(1, int(budget) + 1):
        if graded != 1 and not (change is not None and attempt == 1):
            break
        _attempt[0] = attempt
        _pins[0] = pins
        tree, present = _tree()
        if _author(unit, path, said):
            undo()
            return 2
        graded, said = _guard(unit, base, issue, pins, [graded_file])
        if graded == 1:
            _restore(tree, *[n for n in said.splitlines()
                             if n in tree or (os.path.normpath(n) not in present
                                              and not {".git", ".tdd"} & set(os.path.normpath(n).split(os.sep)))])
        if not graded:
            graded, said = _grade(path, unit)
        if change is not None and graded == 0 and _read_existing([unit]).get(unit) == before.get(unit):
            graded, said = 1, "FAIL: the author left the prose unchanged\n"
        if graded == 1:
            _restore(before, *before)
    if graded:
        undo()
        if graded == 1:
            sys.stdout.write(said)
        return graded
    if not authored:
        event.append(".", {}, "skill-edit-no-author", ["unit=" + unit])
    files = [path, grade_prose.graded_path(unit)] + [unit] * (authored or moved) + pins * authored
    subprocess.run(["git", "add", *files], check=True)
    subprocess.run(["git", "commit", "-q", "-m", "docs: requirements for %s, graded" % unit, *files], check=True)
    return 0 if authored else 3


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
