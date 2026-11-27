"""scope-check.sh's plan checks, run in-process: pytest basename collisions, multi-tag steps, plain steps naming a row
of a unit a later skill-edit step signs, skill-edit units with no Requirements heading or no path-shaped unit."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import sys

import event
import grade_prose
import ledger
import requirements
import tunables

USAGE = "usage: scope-check.sh <ledger> <repo-root>"
PY_ROOT = "skills/tdd/scripts/tests/py"
NAMED = re.compile(re.escape(PY_ROOT) + r"/(?:unit/)?test_\w+\.py")


def existing_by_basename(root):
    found = {}
    for top, dirs, files in os.walk(os.path.join(root, PY_ROOT)):
        dirs.sort()
        for name in sorted(files):
            found.setdefault(name, os.path.relpath(os.path.join(top, name), root))
    return found


def skill_edit_refused(steps, spec_text):
    skill_edits = [record[-1] for record in steps if ledger.is_skill_edit(record[-1])]
    headings = {re.sub(r" \(new\)$", "", heading)
                for heading, line in requirements.requirements_lines(spec_text.splitlines())
                if line.startswith("### ")}
    for step in skill_edits:
        unit = ledger.unit_of(step)
        if unit is None:
            print(f"scope-check.sh: no path-shaped unit for skill-edit step: {step}", file=sys.stderr)
            return True
        if unit not in headings:
            print(f"scope-check.sh: no ### heading for skill-edit unit: {unit}", file=sys.stderr)
            return True
    return False


def signed_rows(root, unit):
    """The row IDs `unit` lists in the REQUIREMENTS.md beside its file, when its GRADED file signs it; else none."""
    graded = os.path.join(root, grade_prose.graded_path(unit))
    if not any(fields[0] == unit for fields in grade_prose.graded_lines(graded)):
        return []
    listing = os.path.join(root, requirements.list_path(unit))
    if not os.path.exists(listing):
        return []
    try:
        rows = requirements.claims(listing, unit)
    except ValueError:
        return []
    return [row.split("\t")[0] for row in rows.splitlines()]


def row_move_refusal(steps, root):
    """A plain step naming a row of a signed unit a later skill-edit step regrades is red by construction (#3302):
    the unit owes a grade from that plain step until the skill-edit step signs it. So is a plain step naming a file
    not yet in the repo that a later skill-edit step names as its unit: that step creates an unsigned unit."""
    texts = [record[-1] for record in steps]
    for later, step in enumerate(texts):
        if not ledger.is_skill_edit(step):
            continue
        unit = ledger.unit_of(step)
        if unit is None:
            continue
        earlier_plain = [plain for plain in texts[:later] if not ledger.is_skill_edit(plain)]
        for row_id in signed_rows(root, unit):
            plain = first_naming(earlier_plain, r"(?<!\w)" + re.escape(row_id) + r"(?!\w)")
            if plain:
                return f"step names row {row_id} of signed unit {unit}, which a later skill-edit step signs: {plain}"
        new_file = unit.partition("#")[0]
        if os.path.exists(os.path.join(root, new_file)):
            continue
        plain = first_naming(earlier_plain, r"(?<![\w./-])" + re.escape(new_file) + r"(?![\w/-])")
        if plain:
            return f"step creates {new_file}, the unit {unit} a later skill-edit step signs: {plain}"
    return None


def first_naming(texts, pattern):
    """The first of texts in which pattern occurs, or None."""
    return next((text for text in texts if re.search(pattern, text)), None)


def main(argv):
    if len(argv) != 2:
        print(USAGE, file=sys.stderr)
        return 2
    path, root = argv
    existing = existing_by_basename(root)
    with open(path, encoding="utf-8") as lines:
        text = lines.read()
    steps = ledger.ledger_steps(text)
    refusal = ledger.multi_tag_refusal(steps) or row_move_refusal(steps, root)
    if refusal:
        print("scope-check.sh: " + refusal, file=sys.stderr)
        return 1
    issue = re.fullmatch(r"issue-(\d+)\.md", os.path.basename(path))
    if issue:
        spec = os.path.join(os.path.dirname(os.path.abspath(path)), f"issue-{issue.group(1)}-spec.md")
        if os.path.exists(spec):
            with open(spec, encoding="utf-8") as f:
                spec_text = f.read()
            if skill_edit_refused(steps, spec_text):
                return 2
    named = NAMED.findall(text)
    clashes = []
    for named_path in dict.fromkeys(named):
        taken = existing.get(os.path.basename(named_path))
        if taken and not os.path.exists(os.path.join(root, named_path)):
            clashes.append(f"{named_path} is new but its basename exists at {taken}")
    if not clashes:
        if issue:
            tdd = os.path.dirname(os.path.abspath(path))
            event.mark(os.path.dirname(tdd), event.context(tunables.with_values(VERI_ISSUE=issue.group(1))),
                       "plan", ["steps=%d" % len(steps)])
        return 0
    print("\n".join(clashes), file=sys.stderr)
    return 1


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
