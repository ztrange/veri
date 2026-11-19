"""bail.sh's one-call bail, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import subprocess
import sys

USAGE = "usage: bail.sh <n> <cause> <phase> --note-file <path> [--attempt <k>]"


def _bad_arguments():
    sys.stderr.write("%s\nbail: bad arguments; bail by BAIL.md sub-step 1\n" % USAGE)
    return 2


def _valid(argv):
    if len(argv) not in (5, 7) or not argv[0].isdigit() or argv[3] != "--note-file":
        return False
    return len(argv) == 5 or (argv[5] == "--attempt" and argv[6].isdigit())


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
        subprocess.run(["git", "add", "-f", path], capture_output=True, text=True)
        subprocess.run(["git", "commit", "-m", "metrics: what bailing on #%s cost (#%s)" % (issue, issue), "--", path],
                       capture_output=True, text=True)
    return metrics


def _write_note(note_file, drift, metrics):
    with open(note_file, "a") as f:
        f.write("\n" + (drift.stdout if drift.returncode == 0
                        else "Skill drift: unavailable — skill-drift.sh exited %d\n" % drift.returncode))
        f.write("\n" + (metrics.stdout if metrics.returncode == 0
                        else "metrics could not be rendered: metrics.sh exited %d\n" % metrics.returncode))


def main(argv):
    if not _valid(argv):
        return _bad_arguments()
    issue, cause, phase, note_file = argv[0], argv[1], argv[2], argv[4]
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    classified = _run("classify-bail.sh", [os.path.join(here, "classify-bail.sh"), cause])
    if classified.returncode != 0:
        sys.stderr.write("bail: unknown cause %s; bail by BAIL.md sub-step 1\n" % cause)
        return 2
    classification = classified.stdout.strip()
    step = subprocess.run([os.path.join(here, "ledger-steps.sh"), "current-or-last-done"],
                          capture_output=True, text=True).stdout.strip()
    attempt = argv[6] if len(argv) == 7 else "1"
    _run("preserve-attempt.sh", [os.path.join(here, "preserve-attempt.sh"), issue, step, phase, attempt, "bail"])
    subprocess.run(["git", "reset", "--hard", "HEAD"], capture_output=True, text=True)
    env = dict(os.environ, VERI_PHASE=phase)
    subprocess.run([os.path.join(here, "event.sh"), "bail", "cause=" + cause, "classification=" + classification],
                   env=env, capture_output=True, text=True)
    metrics = _commit_metrics(here, issue)
    _run("push-branch.sh", [os.path.join(here, "push-branch.sh")])
    drift = _run("skill-drift.sh", [os.path.join(here, "skill-drift.sh")])
    _write_note(note_file, drift, metrics)
    _run("comment.sh", [os.path.join(here, "comment.sh"), issue, "bailed", "--note-file", note_file])
    _run("comment.sh", [os.path.join(here, "comment.sh"), issue, "bailed", "--pr", "--note-file", note_file])
    print("phase: %s\nclassification: %s" % (phase, classification))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
