"""skill-edit-half.sh's computation, run in-process: a ⟦skill-edit⟧ step's clean path in one call (PRD 038.4, #4450)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import sys

import case_reader
import fused
import github
import ledger
import run_start

DETACH = fused.script("detach-command.sh")
STEP = fused.script("skill-edit-step.sh")
TICK = fused.script("step-tick.sh")
USAGE = 'usage: skill-edit-half.sh <n> [--change "<change>"]'


def pins(step, wt):
    unit = ledger.unit_of(step)
    spans = re.findall(r"`([^`]+)`", step[step.index("`" + unit) + len(unit) + 2:])
    return [s for s in spans if case_reader.is_test_path(s)
            and fused.call("git", "ls-files", "--error-unmatch", "--", s, cwd=wt)[0] == 0]


def graded_after_ledger(wt, n, unit):
    _, last, _ = fused.call("git", "log", "-1", "--format=%H", "--", os.path.relpath(ledger.ledger_path(wt, n), wt), cwd=wt)
    last = last.strip()
    if not last:
        return False
    _, subjects, _ = fused.call("git", "log", "--format=%s", last + "..HEAD", cwd=wt)
    return "docs: requirements for %s, graded" % unit in subjects.splitlines()


def main(argv):
    with fused.quiet():
        return run(argv)


def run(argv):
    if not argv or not argv[0].isdigit() or not (len(argv) == 1 or (len(argv) == 3 and argv[1] == "--change")):
        sys.stderr.write(USAGE + "\n")
        return 2
    n = argv[0]
    wt = fused.read_settled(run_start.preflight_file(n))["worktree"]
    with open(ledger.ledger_path(wt, n)) as f:
        step = next(line for line in f if line.startswith(ledger.OPEN_STEP + " "))[len(ledger.OPEN_STEP) + 1:]
    if not ledger.is_skill_edit(step.rstrip("\n")):
        return 2
    unit = ledger.unit_of(step)
    if unit is None:
        return 2
    waiting = fused.load_wait(wt, n, "skill-edit-half") is not None
    if not waiting and graded_after_ledger(wt, n, unit):
        return fused.call(TICK, n, cwd=wt)[0]
    if not waiting:
        read, body, _ = fused.call("gh", "api", "repos/{owner}/{repo}/issues/%s" % n, "-q", ".body", cwd=wt, run=github.bounded)
        if read != 0:
            return 2
        with open(os.path.join(wt, ".tdd", "issue-%s-body" % n), "w") as f:
            f.write(body)
        body_file = os.path.join(".tdd", "issue-%s-body" % n)
        added = ["--added", step.rstrip("\n")] if ledger.is_added(step.rstrip("\n")) else []
        change = ["--change", argv[2]] if argv[1:2] == ["--change"] else []
        fused.call(DETACH, "start", "skill-edit-" + n, STEP, *added, *change, body_file, ledger.unit_of(step), *pins(step, wt), cwd=wt)
        fused.save_wait(wt, n, "skill-edit-half", "skill-edit-" + n, {})
    waited, out, _ = fused.call(DETACH, "wait", "skill-edit-" + n, cwd=wt)
    if waited == 3:
        return 3
    os.remove(fused.wait_record(wt, n, "skill-edit-half"))
    code = author_code(waited, out)
    if code not in (0, 3):
        return 1 if code == 1 else 2
    return fused.call(TICK, n, cwd=wt)[0]


def author_code(waited, out):
    """skill-edit-step.sh's exit from detach-command.sh wait's: 0 on its 0, the printed code on its 1, else None (the
    wait obtained no answer)."""
    if waited == 0:
        return 0
    said = out.strip()
    return int(said) if waited == 1 and said.isdigit() else None


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
