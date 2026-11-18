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

NAME = "pr-checks"
USAGE = "usage: pr-checks.sh <n>"
LEDGER = run_dir.ledger("", "%s")
DETACH = fused.script("detach-command.sh")


def main(argv):
    return fused.entry(argv, NAME + ".sh", run)


def run(n):
    given = fused_step.inputs(NAME + ".sh", n, LEDGER)
    if given is None:
        return 2
    _, wt = given
    base = branch_base(wt)
    lint(wt, n)
    owed = ".tdd/issue-%s-refactor-owed.md" % n
    quality(wt, n, base)
    fused.call(fused.script("red-setup.sh"), "worst", n, owed, cwd=wt)
    coupling(wt, n, base, owed)
    code, said_url, _ = fused.call(fused.script("refactor-candidates.sh"), n, owed, cwd=wt)
    fused.checked("unwired", fused.script("unwired.sh"), "--accepted", ".tdd/issue-%s-unwired-accepted" % n, base,
                  ok=(0, 3), cwd=wt, out=".tdd/unwired.out")
    return fused.settle(wt, n, NAME, ["candidates=" + (said_url.strip() if code == 0 else "")])


def default_branch(wt):
    """The default branch `origin/<default>` names, read without the network."""
    import git
    return git.default_branch(cwd=wt, remote=False)


def branch_base(wt):
    """`git merge-base HEAD origin/<default>`."""
    return fused.call("git", "merge-base", "HEAD", "origin/" + default_branch(wt), cwd=wt)[1].strip()


def path(wt, name):
    return os.path.join(wt, name)


def write(wt, name, text):
    with open(path(wt, name), "w") as f:
        f.write(text)


def said(wt, name):
    with open(path(wt, name), encoding="utf-8", errors="replace") as f:
        return f.read()


def lint(wt, n):
    """The lint run: the repo's declared lint command started detached, waited on within VERI_LINT_TIMEOUT, its
    `lint` event and its `### Lint` section."""
    section = ".tdd/issue-%s-lint.md" % n
    write(wt, section, "")
    command = fused.call(fused.script("detect-test-command.sh"), "--tier", "lint", cwd=wt)[1].strip()
    fused.call(DETACH, "start", "lint", "sh", "-c", command, cwd=wt)
    waited = (DETACH, "wait", "lint", "--total", tunables.get("VERI_LINT_TIMEOUT", unless_empty=True))
    files = {"out": "/dev/null", "err": ".tdd/lint.wait.err"}
    waited_code = fused.call(*waited, cwd=wt, **files)[0]
    code = said(wt, ".tdd/lint.exit").strip()
    fused.call(fused.script("event.sh"), "lint", "exit=" + code, cwd=wt,
               env=tunables.with_values(VERI_ISSUE=n, VERI_ACTOR="conductor"))
    if code == "0":
        write(wt, section, "### Lint\n\n`%s` passed.\n" % command)
        return
    tail = "".join(line[:300] + "\n" for line in said(wt, ".tdd/lint.out").splitlines()[-20:])
    write(wt, section, "### Lint\n\n`%s` exited %s. The last 20 lines of its output:\n\n~~~text\n%s~~~\n"
          % (command, code, tail))
    raise fused.Stop("lint", fused.shown(*waited, **files) + " exit %d" % waited_code, 1)


def coupling(wt, n, base, owed):
    """coupling.sh over the range: a pair writes the `### Coupling` section and stops it with exit 1, the row and its
    commit being the conductor's; none clears an earlier entry's row."""
    section = ".tdd/issue-%s-coupling.md" % n
    write(wt, section, "")
    pairs = (fused.script("coupling.sh"), base)
    code = fused.call(*pairs, cwd=wt, out=".tdd/coupling.out")[0]
    if code == 0:
        write(wt, section, "### Coupling\n\n" + said(wt, ".tdd/coupling.out"))
        raise fused.Stop("coupling", fused.shown(*pairs, out=".tdd/coupling.out") + " exit 0", 1)
    fused.call(fused.script("refactor-owed.sh"), "clear", owed, "coupling", cwd=wt)


def quality(wt, n, base):
    """The test-quality check: the test files the range touched; none writes the record empty, and any stops it
    with exit 1 before the develop-test-quality launch, which is the conductor's."""
    files = (fused.script("test-quality.sh"), "files", base)
    code = fused.call(*files, cwd=wt, out=".tdd/test-quality-files")[0]
    if code == 0:
        raise fused.Stop("test-quality", fused.shown(*files, out=".tdd/test-quality-files") + " exit 0", 1)
    write(wt, ".tdd/issue-%s-test-quality" % n, "")


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
