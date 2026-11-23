"""go-red-step.sh's computation, run in-process: a ⟦go-red⟧ step's one stage, a mutation probe on the case the step
names, recorded in the run's mutation record, then step-tick.sh (#4443)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import sys

import fused
import fused_step
import ledger
import run_dir
import tunables
from ledger import handed_out

NAME = "go-red-step"
USAGE = "usage: go-red-step.sh <n>"
LEDGER = run_dir.ledger("", "%s")
RECORD = ".tdd/issue-%s-mutations.md"

# The $S/ scripts this call makes, in the order each is first made.
CALLS = ("detect-test-command.sh", "mutation-probe.sh", "step-tick.sh")


def main(argv):
    return fused.entry(argv, NAME + ".sh", run)


def run(n):
    given = fused_step.inputs(NAME + ".sh", n, LEDGER)
    if given is None:
        return 2
    _, wt = given
    step = fused_step.first_step(wt, n, handed_out)
    if step is None or not ledger.is_go_red(step):
        sys.stderr.write("go-red-step.sh: no open %s step in %s\n" % (ledger.GO_RED_MARK, LEDGER % n))
        return 2
    probe = ledger.go_red_probe(step)
    if probe is None:
        sys.stderr.write("go-red-step.sh: the open %s step names no probe `<file>` `<old>` → `<new>` on `<case>`\n"
                         % ledger.GO_RED_MARK)
        return 2
    path, old, new, case = probe
    before = read_bytes(wt, path)
    if before is not None and old.encode() not in before:
        raise fused.Stop("probe", "%s no longer holds `%s`" % (path, old), 1)
    code = fused.call(fused.script("mutation-probe.sh"), path, old, new, "--", *command(wt, committed_case(wt, case)), cwd=wt,
                      env=tunables.with_values(VERI_MUTATION_RECORD=RECORD % n), out=".tdd/go-red-probe.out")[0]
    if code == 1:
        raise fused.Stop("probe", "%s stayed green with %s→%s in %s" % (case, old, new, path), 1)
    if code != 0:
        raise fused.Stop("probe", "mutation-probe.sh exit %d" % code, 2)
    if read_bytes(wt, path) != before:
        raise fused.Stop("restore", "%s differs from its bytes before the probe" % path, 2)
    # Exit 1 is the case staying green, the one real answer this stage gives; a tick that fails is no answer (2).
    code = fused.call(fused.script("step-tick.sh"), n, cwd=wt)[0]
    if code != 0:
        raise fused.Stop("tick", "step-tick.sh %s exit %d" % (n, code), 2)
    return 0


def read_bytes(wt, path):
    """<path>'s bytes under the worktree; None when it cannot be read."""
    try:
        with open(os.path.join(wt, path), "rb") as f:
            return f.read()
    except OSError:
        return None


def committed_case(wt, case):
    """<case>, or the `test_<digits>_x` case its file defines for `test_x` (the red leaf's issue-number prefix)."""
    file, _, name = case.partition("::")
    body = read_bytes(wt, file)
    if body is None:
        return case
    text = body.decode("utf-8", "replace")
    if re.search(r"^def %s\b" % re.escape(name), text, re.M):
        return case
    found = re.findall(r"^def (test_\d+_%s)\b" % re.escape(name[5:]), text, re.M)
    return "%s::%s" % (file, found[0]) if len(found) == 1 else case


def defining_file(wt, case):
    """The repo-relative path of the first file under the worktree defining `func <case>`, else stops at probe (exit 2)."""
    if os.path.exists(os.path.join(wt, case)):
        return case
    pattern = re.compile(r"func\s+" + case)
    found = []
    for root, dirs, files in os.walk(wt):
        dirs[:] = [d for d in dirs if d not in (".git", ".tdd")]
        for name in files:
            full = os.path.join(root, name)
            with open(full, encoding="utf-8") as f:
                if pattern.search(f.read()):
                    found.append(os.path.relpath(full, wt))
    if len(found) == 1:
        return found[0]
    if found:
        sys.stderr.write("go-red-step.sh: the case %s is defined by more than one test file: %s\n" % (case, ", ".join(found)))
        raise fused.Stop("probe", "%d test files define %s" % (len(found), case), 2)
    if not re.fullmatch(r"\w+", case):
        return case
    sys.stderr.write("go-red-step.sh: no test file under the worktree defines the case %s\n" % case)
    raise fused.Stop("probe", "no test file defines %s" % case, 2)


def command(wt, case):
    """The probe's command: the `veri: one test file:` command on <case>. Its absence (detect-test-command.sh exit 3)
    stops with exit 2, as does any other exit but 0: the all-tier command would probe every case, not the named one."""
    code, alone, _ = fused.call(fused.script("detect-test-command.sh"), "--tier", "one test file", cwd=wt)
    if code == 0:
        return ("sh", "-c", alone.strip(), "sh", defining_file(wt, case))
    if code == 3:
        sys.stderr.write("go-red-step.sh: no `veri: one test file:` line, so the case %s cannot be probed alone\n" % case)
    raise fused.Stop("probe", "detect-test-command.sh --tier one test file exit %d" % code, 2)


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
