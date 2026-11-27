"""bail.sh's one-call bail, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import subprocess
import sys

import entry
import git
import run_dir
import tunables

USAGE = "usage: bail.sh <n> <cause> <phase> --note-file <path> [--attempt <k>]"
NOTE_FILE_FLAG = "--note-file"
BAILED_KIND = "bailed"


def _bad_arguments():
    sys.stderr.write("%s\nbail: bad arguments; bail by BAIL.md sub-step 1\n" % USAGE)
    return 2


def _valid(argv):
    if len(argv) not in (5, 7) or entry.whole_number(argv[0]) is None or argv[3] != NOTE_FILE_FLAG:
        return False
    return len(argv) == 5 or (argv[5] == "--attempt" and entry.whole_number(argv[6]) is not None)


def _run(label, cmd, **kw):
    done = subprocess.run(cmd, capture_output=True, text=True, **kw)
    print("%s exit %d" % (label, done.returncode))
    return done


def _commit_metrics(here, issue):
    metrics = _run("metrics.sh", [os.path.join(here, "metrics.sh"), issue])
    if metrics.returncode == 0:
        path = os.path.join(".tdd", "issue-%s-metrics.md" % issue)
        os.makedirs(".tdd", exist_ok=True)
        with open(path, "w") as f:
            f.write(metrics.stdout)
        _run("git add", ["git", "add", "-f", path])
        _run("git commit",
             ["git", "commit", "-m", "metrics: what bailing on #%s cost (#%s)" % (issue, issue), "--", path])
    return metrics


def _write_note(note_file, drift, metrics):
    try:
        _append_note(note_file, drift, metrics)
    except OSError as error:
        print("note %s failed: %s" % (note_file, error.strerror or error))


def _append_note(note_file, drift, metrics):
    with open(note_file, "a") as f:
        f.write("\n" + (drift.stdout if drift.returncode == 0
                        else "Skill drift: unavailable — skill-drift.sh exited %d\n" % drift.returncode))
        f.write("\n" + (metrics.stdout if metrics.returncode == 0
                        else "metrics could not be rendered: metrics.sh exited %d\n" % metrics.returncode))


def _print_report(phase, classification):
    branch = git.git("branch", "--show-current", capture_output=True, text=True).stdout.strip()
    tree = git.git("rev-parse", "--show-toplevel", capture_output=True, text=True).stdout.strip()
    print("phase: %s\nclassification: %s\nbranch: %s\nworktree: %s" % (phase, classification, branch, tree))


def _ledger_text(issue):
    try:
        with open(run_dir.ledger(".", issue)) as f:
            return f.read()
    except OSError:
        return ""


def _snapshot_and_record(here, argv, classification):
    issue, cause, phase = argv[0], argv[1], argv[2]
    attempt = argv[6] if len(argv) == 7 else "1"
    step = _run("ledger-steps.sh", [os.path.join(here, "ledger-steps.sh"), "current-or-last-done"],
                input=_ledger_text(issue)).stdout.strip()
    _run("preserve-attempt.sh", [os.path.join(here, "preserve-attempt.sh"), issue, step, phase, attempt, "bail"])
    _run("git reset", ["git", "reset", "--hard", "HEAD"])
    env = tunables.with_values(VERI_PHASE=phase)
    _run("event.sh", [os.path.join(here, "event.sh"), "bail", "cause=" + cause, "classification=" + classification],
         env=env)


def _publish(here, issue, note_file, metrics):
    _run("push-branch.sh", [os.path.join(here, "push-branch.sh")])
    drift = _run("skill-drift.sh", [os.path.join(here, "skill-drift.sh")])
    _write_note(note_file, drift, metrics)
    _run("comment.sh", [os.path.join(here, "comment.sh"), issue, BAILED_KIND, NOTE_FILE_FLAG, note_file])
    _run("comment.sh", [os.path.join(here, "comment.sh"), issue, BAILED_KIND, "--pr", NOTE_FILE_FLAG, note_file])


def main(argv):
    if not _valid(argv):
        return _bad_arguments()
    issue, cause, phase, note_file = argv[0], argv[1], argv[2], argv[4]
    here = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    classified = _run("classify-bail.sh", [os.path.join(here, "classify-bail.sh"), cause])
    if classified.returncode != 0:
        sys.stderr.write("bail: unknown cause %s; bail by BAIL.md sub-step 1\n" % cause)
        return 2
    classification = classified.stdout.strip()
    _snapshot_and_record(here, argv, classification)
    metrics = _commit_metrics(here, issue)
    _publish(here, issue, note_file, metrics)
    _print_report(phase, classification)
    return 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
