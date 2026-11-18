"""resume-start.sh's computation, run in-process: RESUME.md sub-steps 1-4's fixed calls and the owed verify-plan
launch, made in one call (PRD 038.6)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import fused
import run_dir
import run_start

USAGE = "usage: resume-start.sh <n>"


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
    for name in missing:
        sys.stderr.write("resume-start.sh: no %s\n" % name)
    return None if missing else (lines, values)


def main(argv):
    return fused.entry(argv, "resume-start.sh", run)


def run(n):
    given = inputs(n)
    if given is None:
        return 2
    lines, values = given
    settled = fused.read_lines(lines)
    wt = settled["worktree"]
    ledger = os.path.relpath(run_dir.ledger(".", n))
    with open(os.path.join(wt, ledger)) as f:
        text = f.read()
    fused.checked("2", fused.script("next-pending-refactor.sh"), cwd=wt, stdin=text, ok=(3,))
    step = fused.checked("3", fused.script("next-unchecked.sh"), cwd=wt, stdin=text, ok=(0, 3)).strip()
    resuming(n, wt, text, step, [line[len("stray="):] for line in lines if line.startswith("stray=")])
    pr_url(wt)
    return 0


NOTE = ".tdd/resume-note.md"


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


def pr_url(wt):
    """The open PR the branch already has, read off the branch, never remembered."""
    branch = fused.checked("4", "git", "branch", "--show-current", cwd=wt).strip()
    import plan_publish
    return plan_publish.gh("4", "api", "repos/{owner}/{repo}/pulls?head={owner}:%s" % branch, "-q",
                           ".[0].html_url // empty", wt=wt).strip()


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
