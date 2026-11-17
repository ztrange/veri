"""pr-finish.sh's computation, run in-process: DRAFT-PR.md sub-step 2's second block up to the refactor-owed render on
its clean path, after the first wait-ci.sh exited 0, made in one call (PRD 027.11). The PR's title and body stay the
conductor's."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import sys

import fused
import fused_step
import ledger
import plan_publish
import pr_ready_wait
import run_dir
import tunables

NAME = "pr-finish"
LEDGER = run_dir.ledger("", "%s")
WHERE = "2"
FULL_SUITE = "⟦full-suite⟧"
REFACTOR_OWED = ".tdd/issue-%s-refactor-owed.md"
RENDER = ".tdd/issue-%s-refactor-owed-render"


def main(argv):
    return fused.entry(argv, NAME + ".sh", run)


def run(n):
    given = fused_step.inputs(NAME + ".sh", n, LEDGER)
    if given is None:
        return 2
    _, wt = given
    url = pr_ready_wait.pr_url(wt)
    tick_full_suite(wt, n)
    values = {"pr_url": url, "metrics": record(wt, n, url)}
    if fused.changed_paths(WHERE, wt):
        raise fused.Stop(WHERE, "tree-check", 1)
    fused.checked(WHERE, fused.script("push-branch.sh"), cwd=wt)
    fused.save_wait(wt, n, NAME, pr_ready_wait.WAIT, values)
    pr_ready_wait.ci_wait(wt, n, NAME, url)
    render(wt, n)
    lines = ["pr_url=" + url] + (["metrics=%d" % values["metrics"]] if values["metrics"] else [])
    return fused.settle(wt, n, NAME, lines + ["refactor_owed_render=" + RENDER % n])


def record(wt, n, url):
    """MC2, MC3: the `done` mark, then metrics.sh into .tdd/issue-<n>-metrics.md, committed as `metrics:` on exit 0;
    metrics.sh's exit code, which any other exit carries rather than stops on."""
    fused.checked(WHERE, fused.script("event.sh"), "done", "pr=" + url, cwd=wt,
                  env=tunables.with_values(VERI_ISSUE=n, VERI_ACTOR="conductor"))
    metrics = ".tdd/issue-%s-metrics.md" % n
    code = fused.call(fused.script("metrics.sh"), n, cwd=wt, out=metrics)[0]
    if code == 0:
        fused.checked(WHERE, "git", "add", metrics, cwd=wt)
        fused.checked(WHERE, "git", "commit", "-m", "metrics: what solving #%s cost (#%s)" % (n, n), cwd=wt)
    return code


def render(wt, n):
    """MC6: refactor-owed.sh render's output written to .tdd/issue-<n>-refactor-owed-render; exit 3 an empty file."""
    code, out, _ = fused.call(fused.script("refactor-owed.sh"), "render", REFACTOR_OWED % n, cwd=wt)
    if code not in (0, 3):
        raise fused.Stop(WHERE, fused.label("refactor-owed.sh", "render", REFACTOR_OWED % n) + " exit %d" % code, code)
    with open(os.path.join(wt, RENDER % n), "w") as f:
        f.write(out if code == 0 else "")


def tick_full_suite(wt, n):
    """MC1: under `ci`, with an unchecked ⟦full-suite⟧ line and a first wait that did not say `has no checks`, each
    such line ticked with tick-ledger.sh until it exits 3, each line's issue criterion ticked, and the ledger
    committed as `plan: the full suite is green on CI`; nothing otherwise."""
    if fused.checked(WHERE, fused.script("branch-suite.sh"), cwd=wt).strip() != "ci":
        return
    lines = [r.text for r in ledger.ledger_steps(ledger.read_ledger(run_dir.ledger(wt, n)))
             if r.state == "open" and FULL_SUITE in r.text]
    if not lines or pr_ready_wait.NO_CHECKS in pr_ready_wait.said(wt, ".tdd/wait-ci.err"):
        return
    tick = (fused.script("tick-ledger.sh"), LEDGER % n, FULL_SUITE)
    while (code := fused.call(*tick, cwd=wt)[0]) != 3:
        if code != 0:
            raise fused.Stop(WHERE, fused.shown(*tick) + " exit %d" % code, code)
    for k in [k for line in lines for k in re.findall(r"⟦criterion (\d+)⟧", line)]:
        body = plan_publish.gh(WHERE, "api", "repos/{owner}/{repo}/issues/%s" % n, "-q", ".body", wt=wt)
        criterion = fused.checked(WHERE, fused.script("ledger-steps.sh"), "criterion", k, cwd=wt, stdin=body).strip()
        fused.checked(WHERE, fused.script("tick-issue-criterion.sh"), n, criterion, cwd=wt, ok=(0, 3))
    fused.checked(WHERE, "git", "add", LEDGER % n, cwd=wt)
    fused.checked(WHERE, "git", "commit", "-m", "plan: the full suite is green on CI (#%s)" % n, cwd=wt)


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
