"""scope-check.sh's plan checks, run in-process: pytest basename collisions, multi-tag steps, skill-edit units with no Requirements heading."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import sys

import event
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


def main(argv):
    if len(argv) != 2:
        print(USAGE, file=sys.stderr)
        return 2
    path, root = argv
    existing = existing_by_basename(root)
    with open(path, encoding="utf-8") as lines:
        text = lines.read()
    steps = ledger.ledger_steps(text)
    refusal = ledger.multi_tag_refusal(steps)
    if refusal:
        print("scope-check.sh: " + refusal, file=sys.stderr)
        return 1
    issue = re.fullmatch(r"issue-(\d+)\.md", os.path.basename(path))
    if issue:
        spec = os.path.join(os.path.dirname(os.path.abspath(path)), f"issue-{issue.group(1)}-spec.md")
        if os.path.exists(spec):
            with open(spec, encoding="utf-8") as f:
                spec_text = f.read()
            skill_edits = [record[-1] for record in steps if ledger.carries_mark(record[-1], "skill-edit")]
            if re.search(r"^## Requirements\s*$", spec_text, re.M):
                headings = {re.sub(r" \(new\)$", "", heading)
                            for heading, line in requirements.requirements_lines(spec_text.splitlines())
                            if line.startswith("### ")}
                for step in skill_edits:
                    unit = ledger.unit_of(step)
                    if unit is None:
                        print(f"scope-check.sh: no path-shaped unit for skill-edit step: {step}", file=sys.stderr)
                        return 2
                    if unit not in headings:
                        print(f"scope-check.sh: no ### heading for skill-edit unit: {unit}", file=sys.stderr)
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
