"""ci-flake.sh's flake check of a red CI run: each test target its failed log names, rerun alone."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import re
import sys

import ci_marks
import event
import event_log
import git
import github
import rerun_alone
import tunables

USAGE = "usage: ci-flake.sh <n> <head-sha> <run-id> '<alone-cmd>' <log-file>"
WHOLE = re.compile(r"[0-9]+")
# The check's overall bound: at most this many alone runs, each bounded by VERI_TIMEOUT; a log naming more is no answer.
MAX_TARGETS = 5
# An ANSI colour or style sequence, stripped from the runner's text before its targets are read.
ANSI = re.compile(r"\x1b\[[0-9;]*m")
# One line of `gh run view --log-failed`: job, step and timestamp before the runner's own text.
STAMP = re.compile(r"\t\ufeff?\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z")
GH_LINE = re.compile(r"^[^\t]*\t[^\t]*" + STAMP.pattern + " ?(.*)$")


def runner_text(log):
    """The runner's own output in a `--log-failed` log: each line without gh's prefix or colour codes.
    ValueError naming the first
    non-empty line that is not one gh line (no prefix, or two lines glued into one), so such a log is no answer."""
    lines = []
    for number, line in enumerate(log.splitlines(), 1):
        found = GH_LINE.match(line)
        if not found and not line.strip():
            continue
        if not found or STAMP.search(found.group(1)):
            raise ValueError("line %d is not one line of gh run view --log-failed" % number)
        lines.append(ANSI.sub("", found.group(1)))
    return "\n".join(lines) + "\n"


def passes_alone(alone_cmd, target):
    """True when <target> passes run alone, False when it fails, None when the run got no answer: not done within
    VERI_TIMEOUT, or killed by a signal (a negative code, or the shell's 128 and above for a killed child)."""
    cmd = alone_cmd if '"$1"' in alone_cmd else alone_cmd + ' "$1"'
    ran = github.bounded_group(["sh", "-c", cmd, "sh", target], limit_name="VERI_TIMEOUT")
    return None if isinstance(ran, github.TimedOut) or not 0 <= ran.returncode < 128 else ran.returncode == 0


def not_the_ci_head(head):
    """Why the worktree cannot stand for the CI run's tree: HEAD is not <head>, the tree is dirty, or git cannot
    answer; None when it can. A target passing alone elsewhere says nothing about the head CI ran."""
    try:
        at, dirty = git.out("rev-parse", "HEAD"), git.out("status", "--porcelain")
    except git.GitFailed as failed:
        return "git cannot read the worktree: %s" % failed
    if at != head:
        return "HEAD is %s, not the CI run's head %s" % (at, head)
    return "the worktree has uncommitted changes" if dirty else None


def no_rerun_left(n, head, budget):
    """True when issue <n> made <budget> or more re-runs since its last conductor-start, or ever re-ran <head>."""
    spent, head_rerun = 0, False
    for e in event_log.events(".", "conductor-start", "ci-rerun"):
        if str(e.get("issue")) != n:
            continue
        if e.get("event") == "conductor-start":
            spent = 0
        else:
            spent += 1
            head_rerun = head_rerun or e.get("head") == head
    return spent >= budget or head_rerun


def main(argv):
    if len(argv) != 5 or not WHOLE.fullmatch(argv[0]) or not WHOLE.fullmatch(argv[2]) \
            or not re.fullmatch(r"[0-9a-f]{40}", argv[1]):
        print(USAGE, file=sys.stderr)
        return 2
    n, head, run_id, alone_cmd, log_file = argv
    budget, bad = tunables.resolve("VERI_CI_FLAKE_RERUNS")
    if bad:
        sys.stderr.write("ci-flake: VERI_CI_FLAKE_RERUNS must be %s, got '%s'\n" % (bad[1], bad[0]))
        return 2
    if no_rerun_left(n, head, budget):
        return 3
    refusal = not_the_ci_head(head)
    if refusal:
        sys.stderr.write("ci-flake: %s\n" % refusal)
        return 2
    with open(log_file, errors="replace") as log:
        text = log.read()
    try:
        targets = rerun_alone.named_targets(runner_text(text))
    except ValueError as unread:
        sys.stderr.write("ci-flake: %s: %s\n" % (log_file, unread))
        return 2
    if len(targets) > MAX_TARGETS:
        sys.stderr.write("ci-flake: the log names %d targets, more than the %d the check runs alone\n"
                         % (len(targets), MAX_TARGETS))
        return 2
    alone = [passes_alone(alone_cmd, t) for t in targets]
    if False in alone or not targets:
        return 1
    if None in alone:
        sys.stderr.write("ci-flake: an alone run got no answer (not done within VERI_TIMEOUT, or killed by a signal)\n")
        return 2
    rerun = github.gh_run_rerun_failed(run_id)
    # The attempt is counted whatever gh answered: a refusal may come after the re-run started (a timeout), and an
    # uncounted attempt could re-run the head again.
    written = event.mark(".", event.context(tunables.with_values(VERI_ISSUE=n)), "ci-rerun",
                         ["head=" + head, "run=" + run_id, "files=" + ",".join(targets)])
    if rerun.returncode != 0:
        sys.stderr.write("ci-flake: gh run rerun %s --failed refused (exit %d): %s\n"
                         % (run_id, rerun.returncode, (rerun.stderr or "").strip()))
        return 2
    ci_marks.fresh_window("", head)
    if written:
        sys.stderr.write("ci-flake: run %s was re-run but its ci-rerun event was not written\n" % run_id)
        return 2
    print("\n".join(targets))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
