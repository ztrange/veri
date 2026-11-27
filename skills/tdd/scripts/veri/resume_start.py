"""resume-start.sh's computation, run in-process: RESUME.md sub-steps 1-4's fixed calls and the owed verify-plan
launch, made in one call (PRD 038.6)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import fused
import fused_step
import pr_finish
import run_dir
import run_start
import tunables

USAGE = "usage: resume-start.sh <n>"

# The $S/ scripts this call makes, in the order each is first made (git and gh aside); unit/test_resume_start.py fails
# when one is a script RESUME.md and SKILL.md do not name (FC19).
CALLS = ("next-pending-refactor.sh", "ledger-growth.sh", "next-unchecked.sh", "ledger-steps.sh", "event.sh",
         "comment.sh", "suite-red-resume.sh", "stop-requested.sh", "detach-leaf.sh", "supervise.sh", "run-verdict.sh",
         "wait-leaf.sh")


def inputs(n):
    """(preflight lines, run-start values) once every input file is readable; else None, each missing one named on
    stderr."""
    missing, lines, values = [], None, None
    try:
        with open(run_start.preflight_file(n)) as f:
            lines = f.read().splitlines()
    except OSError:
        missing.append(".tdd/issue-%s-preflight" % n)
    if lines is not None:
        wt = fused.read_lines(lines).get("worktree", "")
        if not os.path.exists(run_dir.ledger(wt, n)):
            missing.append(os.path.relpath(run_dir.ledger(".", n)))
        try:
            values = fused.read_settled(run_dir.issue_file(wt, n, "-run-start"))
        except OSError:
            missing.append(".tdd/issue-%s-run-start" % n)
        if values is not None and values.get("verify_plan") not in ("owed", "skip"):
            missing.append(".tdd/issue-%s-run-start verify_plan=owed or skip: run-start.sh on a resume" % n)
    for name in missing:
        sys.stderr.write("resume-start.sh: no %s\n" % name)
    return None if missing else (lines, values)


def main(argv):
    return fused.entry(argv, "resume-start.sh", run)


def run(n):
    given = inputs(n)
    if given is None:
        return 2
    preflight, values = given
    settled = fused.read_lines(preflight)
    wt = settled["worktree"]
    waited = fused.load_wait(wt, n, OWNER)
    if waited is not None:
        return verdict(n, wt, waited[1])
    ledger = os.path.relpath(run_dir.ledger(".", n))
    with open(os.path.join(wt, ledger)) as f:
        text = f.read()
    fused.checked("2", fused.script("next-pending-refactor.sh"), cwd=wt, stdin=text, ok=(3,))
    if not os.path.exists(os.path.join(wt, added(n))) and grown(wt, ledger):
        record_existing(n, wt, ledger)
    unserved(n, wt, text)
    step = fused.checked("3", fused.script("next-unchecked.sh"), cwd=wt, stdin=text, ok=(0, 3)).strip()
    resuming(n, wt, text, step, [line[len("stray="):] for line in preflight if line.startswith("stray=")])
    if os.path.exists(os.path.join(wt, SUITE_RED)):
        code = fused.call(fused.script("suite-red-resume.sh"), "insert", ledger, SUITE_RED, cwd=wt)[0]
        if code != 0:
            raise fused.Stop("4", "suite-red-resume.sh insert exit %d" % code, 1)
    lines = ["step=" + step, "pr_url=" + pr_url(wt)]
    if values["verify_plan"] == "owed":
        return verify_plan(n, wt, settled, ledger, lines)
    return fused.settle(wt, n, "resume-start", lines + ["verify_plan=skip"])


LEAF = "verdict-plan"
OWNER = "resume-start"


def verify_plan(n, wt, settled, ledger, lines):
    """Step 2c's verify-plan, launched as plan-publish.sh launches it; 0 posts the verify-plan comment and settles
    <lines> with verify_plan=PASS."""
    fused.launch("4", wt, LEAF, "run-verdict.sh", "--branch-base", fused_step.branch_base("4", wt, n), "plan",
                 ".tdd/issue-%s-spec.md" % n, ledger,
                 env=tunables.with_values(VERI_TEST_CMD=settled["fast_cmd"], VERI_ISSUE=n),
                 out=".tdd/verify-plan.reason", err=".tdd/verify-plan.err")
    fused.save_wait(wt, n, OWNER, "4", lines)
    return verdict(n, wt, lines)


def verdict(n, wt, lines):
    code = fused.wait(wt, n, OWNER, LEAF)
    if code != 0:
        raise fused.Stop("4", "wait-leaf.sh %s exit %d" % (LEAF, code), code)
    fused.checked("4", fused.script("comment.sh"), n, "verify-plan", cwd=wt)
    return fused.settle(wt, n, "resume-start", lines + ["verify_plan=PASS"])


NOTE = ".tdd/resume-note.md"
SUITE_RED = ".tdd/resume-suite-red"


def quiet(where, *args, wt):
    """One git call printed as its line and exit, never its output; its stdout, or a Stop at <where> with exit 2: a
    failing git call gave no answer."""
    code, out, _ = fused.run_script("git", *args, cwd=wt)
    sys.stdout.write(fused.shown("git", *args) + " exit %d\n" % code)
    if code != 0:
        raise fused.Stop(where, fused.shown("git", *args) + " exit %d" % code, 2)
    return out


def added(n):
    return os.path.relpath(run_dir.issue_file(".", n, "-added.md"))


def grown(wt, ledger):
    """Whether the ledger holds step lines its newest plan commit did not."""
    import ledger as ledger_module
    log = quiet("1", "log", "-E", "--grep=^plan: (scope|rewrite)", "--format=%H %s", wt=wt)
    sha = fused.checked("1", fused.script("ledger-growth.sh"), "plan-sha", cwd=wt, stdin=log).strip()

    def texts(text):
        return [ledger_module.body(step.text) for step in ledger_module.ledger_steps(text)]
    planned = set(texts(quiet("1", "show", "%s:%s" % (sha, ledger), wt=wt)))
    with open(os.path.join(wt, ledger)) as f:
        return any(step not in planned for step in texts(f.read()))


def record_existing(n, wt, ledger):
    """Sub-step 1's record of the steps the ledger grew before records existed, committed alone. Made only once
    sub-step 2 found no pending refactor: a commit between a step's green commit and its refactor would stop the
    refactor half (`subject chore: …`) and put the record in verify-refactor's diff."""
    fused.checked("1", fused.script("ledger-growth.sh"), "record-existing", ledger, cwd=wt)
    pr_finish.answered("1", "git", "add", added(n), cwd=wt)
    pr_finish.answered("1", "git", "commit", "-m",
                       "chore: record the steps the ledger grew before its record (#%s)" % n, cwd=wt)


def resuming(n, wt, text, step, stray):
    """Sub-step 4's mark and comment: the resume event, then the Resuming comment, its note naming the step and the
    stray work preflight's reset discarded."""
    current = fused.checked("4", fused.script("ledger-steps.sh"), "current-or-last-done", cwd=wt, stdin=text).strip()
    fused.mark("4", wt, n, current, "resume")
    note = "Resuming at: %s\n" % step if step else "Resuming: every step is checked.\n"
    if stray:
        note += ("\nThe reset discarded this stray work, seen by no verifier and now gone: %s\n"
                 % ", ".join("`%s`" % path for path in stray))
    with open(os.path.join(wt, NOTE), "w") as f:
        f.write(note)
    fused.checked("4", fused.script("comment.sh"), n, "resuming", "--note-file", NOTE, cwd=wt)


def unserved(n, wt, text):
    """Sub-step 3's judgement: an acceptance criterion unticked in the spec that no ledger step's ⟦criterion k⟧
    serves stops it, since planning it is the conductor's."""
    import issue_body
    import ledger as ledger_module
    try:
        with open(os.path.join(wt, ".tdd", "issue-%s-spec.md" % n)) as f:
            spec = f.read()
    except OSError as error:
        raise fused.Stop("3", "no .tdd/issue-%s-spec.md" % n, 2) from error
    served = {step.criterion for step in ledger_module.ledger_steps(text)}
    for k, (_, line) in enumerate(issue_body.criteria(spec), 1):
        if ledger_module.STEP_RE.fullmatch(line).group(2) == " " and str(k) not in served:
            raise fused.Stop("3", "criterion %d no ledger step serves" % k, 1)


def pr_url(wt):
    """The open PR the branch already has, read off the branch, never remembered."""
    branch = pr_finish.answered("4", "git", "branch", "--show-current", cwd=wt).strip()
    url = pr_finish.gh_answered("4", "api", "repos/{owner}/{repo}/pulls?head={owner}:%s" % branch, "-q",
                          ".[0].html_url // empty", wt=wt).strip()
    if not url:
        raise fused.Stop("4", "no open PR for " + branch, 1)
    return url


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
