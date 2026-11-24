"""pr-checks.sh's computation, run in-process: DRAFT-PR.md sub-step 1's checks after pr-prepare.sh (the lint run, the
test-quality check, red-setup.sh worst, coupling.sh, refactor-candidates.sh, unwired.sh), made in one call, stopping
at each judgement (PRD 038.8)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import fused
import fused_step
import run_dir
import tunables
from ledger import has_kind

NAME = "pr-checks"
USAGE = "usage: pr-checks.sh <n>"
LEDGER = run_dir.ledger("", "%s")
DETACH = fused.script("detach-command.sh")

# The $S/ scripts this call makes, in the order each is first made (git aside; stop-requested.sh only when the lint
# recorded no exit code); unit/test_pr_checks.py fails when one is a script DRAFT-PR.md's sub-step 1 does not name.
CALLS = ("detect-test-command.sh", "detach-command.sh", "stop-requested.sh", "event.sh", "test-quality.sh",
         "red-setup.sh", "coupling.sh", "refactor-owed.sh", "refactor-candidates.sh", "unwired.sh")


def main(argv):
    return fused.entry(argv, NAME + ".sh", run)


def run(n):
    given = fused_step.inputs(NAME + ".sh", n, LEDGER)
    if given is None:
        return 2
    _, wt = given
    base = branch_base(wt)
    owed = ".tdd/issue-%s-refactor-owed.md" % n
    lint(wt, n)
    quality(wt, n, base)
    initial = said(wt, owed, "")
    worst = (fused.script("red-setup.sh"), "worst", n, owed)
    answered("red-setup", *worst, ok=(0, 3), cwd=wt)
    coupling(wt, n, base, owed)
    if said(wt, owed, "") != initial:
        raise fused.Stop("coupling", fused.label(*worst) + " changed the owed file", 1)
    url = answered("refactor-candidates", fused.script("refactor-candidates.sh"), n, owed, ok=(0, 3), cwd=wt)
    unwired(wt, n, base)
    return fused.settle(wt, n, NAME, ["candidates=" + url.strip()])


def unwired(wt, n, base):
    """unwired.sh over the range: a finding stops it with exit 1, the pending record and the bail being the
    conductor's; any exit but 0, 1 or 3 is exit 2."""
    try:
        fused.checked("unwired", fused.script("unwired.sh"), "--accepted", ".tdd/issue-%s-unwired-accepted" % n, base,
                      ok=(0, 3), cwd=wt, out=".tdd/unwired.out")
    except fused.Stop as stop:
        raise fused.Stop(stop.where, stop.what, 1 if stop.code == 1 else 2)


def default_branch(wt):
    """The default branch `origin/<default>` names, read without the network."""
    import git
    return git.default_branch(cwd=wt, remote=False)


def branch_base(wt):
    """`git merge-base HEAD origin/<default>`; no default branch, or a failing git call, is exit 2."""
    default = default_branch(wt)
    if not default:
        raise fused.Stop("branch-base", "no default branch", 2)
    return answered("branch-base", "git", "merge-base", "HEAD", "origin/" + default, cwd=wt).strip()


def answered(where, *args, **kw):
    """fused.checked at <where>, an exit outside its <ok> stopping it with exit 2 (no answer could be obtained)."""
    try:
        return fused.checked(where, *args, **kw)
    except fused.Stop as stop:
        raise fused.Stop(stop.where, stop.what, 2)


def path(wt, name):
    return os.path.join(wt, name)


def write(wt, name, text):
    with open(path(wt, name), "w") as f:
        f.write(text)


def said(wt, name, absent=None):
    """The text of <name> under the worktree; <absent>, when given, for a file that cannot be read."""
    try:
        with open(path(wt, name), encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        if absent is None:
            raise
        return absent


def lint(wt, n):
    """The lint run: the repo's declared lint command started detached, waited on within VERI_LINT_TIMEOUT, its
    `lint` event and its `### Lint` section. No `veri: lint:` line runs nothing; a command that cannot be read, or
    that records no exit code, writes its sentence and goes on, unless a stop is `now`."""
    section = ".tdd/issue-%s-lint.md" % n
    resumed = fused.load_wait(wt, n, NAME)
    if resumed is not None:
        command = resumed[1]["lint"]
    else:
        write(wt, section, "")
        found, command, _ = fused.call(fused.script("detect-test-command.sh"), "--tier", "lint", cwd=wt)
        command = command.strip()
        if found == 3:
            return
        if found != 0:
            write(wt, section, "### Lint\n\nThe lint command could not be read: detect-test-command.sh --tier lint "
                  "exited %d.\n" % found)
            return
        answered("lint", DETACH, "start", "lint", "sh", "-c", command, cwd=wt)
        fused.save_wait(wt, n, NAME, "lint", {"lint": command})
    bound = tunables.get("VERI_LINT_TIMEOUT", unless_empty=True)
    waited = (DETACH, "wait", "lint", "--total", bound)
    files = {"out": "/dev/null", "err": ".tdd/lint.wait.err"}
    waited_code = fused.call(*waited, cwd=wt, **files)[0]
    if waited_code == 3:
        raise fused.Waiting("lint")
    os.remove(fused.wait_record(wt, n, NAME))
    if waited_code not in (0, 1):
        unrecorded(wt, section, command, bound)
        return
    code = said(wt, ".tdd/lint.exit").strip()
    answered("lint", fused.script("event.sh"), "lint", "exit=" + code, cwd=wt,
             env=tunables.with_values(VERI_ISSUE=n, VERI_ACTOR="conductor"))
    if code == "0":
        write(wt, section, "### Lint\n\n`%s` passed.\n" % command)
        return
    tail = "".join(line[:300] + "\n" for line in said(wt, ".tdd/lint.out").splitlines()[-20:])
    write(wt, section, "### Lint\n\n`%s` exited %s. The last 20 lines of its output:\n\n~~~text\n%s~~~\n"
          % (command, code, tail))
    raise fused.Stop("lint", fused.shown(*waited, **files) + " exit %d" % waited_code, 1)


def unrecorded(wt, section, command, bound):
    """A lint wait with no exit code recorded: a stop of `now` stops it at lint; else the section says the command was
    stopped past VERI_LINT_TIMEOUT or could not be run, and no event is written."""
    mode = answered("lint", fused.script("stop-requested.sh"), ok=(0, 3), cwd=wt)
    if mode.strip() == "now":
        raise fused.Stop("lint", "stop-requested.sh exit 0 now", 1)
    if "still running past --total" in said(wt, ".tdd/lint.wait.err", ""):
        why = "did not finish within VERI_LINT_TIMEOUT (%s seconds) and was stopped" % bound
    else:
        why = "could not be run: no exit code was recorded"
    write(wt, section, "### Lint\n\n`%s` %s.\n" % (command, why))


def coupling(wt, n, base, owed):
    """coupling.sh over the range: a pair writes the `### Coupling` section and stops it with exit 1, the row and its
    commit being the conductor's; none clears an earlier entry's row, and a row it drops stops it with exit 1 for the
    conductor's commit. Without a pair, run() then stops it at coupling with exit 1 when red-setup.sh changed the owed
    file, since no prose but the coupling block's commits that file."""
    section = ".tdd/issue-%s-coupling.md" % n
    write(wt, section, "")
    pairs = (fused.script("coupling.sh"), base)
    code = fused.call(*pairs, cwd=wt, out=".tdd/coupling.out")[0]
    if code not in (0, 3):
        raise fused.Stop("coupling", fused.shown(*pairs, out=".tdd/coupling.out") + " exit %d" % code, 2)
    if code == 0:
        write(wt, section, "### Coupling\n\n" + said(wt, ".tdd/coupling.out"))
        raise fused.Stop("coupling", fused.shown(*pairs, out=".tdd/coupling.out") + " exit 0", 1)
    before = said(wt, owed, "")
    cleared = (fused.script("refactor-owed.sh"), "clear", owed, "coupling")
    answered("coupling", *cleared, cwd=wt)
    if said(wt, owed, "") != before:
        raise fused.Stop("coupling", fused.label(*cleared) + " dropped a stale row", 1)


def quality(wt, n, base):
    """The test-quality check: the test files the range touched; none writes the record empty, and any stops it
    with exit 1 before the develop-test-quality launch, which is the conductor's."""
    record = ".tdd/issue-%s-test-quality" % n
    if os.path.exists(path(wt, record)):
        if owes_fix(said(wt, record), said(wt, LEDGER % n)):
            raise fused.Stop("test-quality", record + " owes a fix step", 1)
        return
    files = (fused.script("test-quality.sh"), "files", base)
    code = fused.call(*files, cwd=wt, out=".tdd/test-quality-files")[0]
    if code not in (0, 3):
        raise fused.Stop("test-quality", fused.shown(*files, out=".tdd/test-quality-files") + " exit %d" % code, 2)
    if code == 0:
        raise fused.Stop("test-quality", fused.shown(*files, out=".tdd/test-quality-files") + " exit 0", 1)
    write(wt, record, "")


def owes_fix(record, ledger):
    """Whether the recorded findings still owe a ⟦test-quality⟧ step: a weak-assertion or implementation-coupled
    finding whose <file>::<case> no such step of the ledger names, while VERI_TEST_QUALITY_FIXES exceeds the steps the
    ledger already holds."""
    steps = [line for line in ledger.splitlines() if has_kind(line, "⟦test-quality⟧")]
    unfixed = [fields[1] for fields in (line.split(" | ", 2) for line in record.splitlines())
               if len(fields) == 3 and fields[0] in ("weak-assertion", "implementation-coupled")
               and not any(fields[1] in step for step in steps)]
    return bool(unfixed) and int(tunables.get("VERI_TEST_QUALITY_FIXES", unless_empty=True)) > len(steps)


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
