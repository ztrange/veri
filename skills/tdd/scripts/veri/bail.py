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


def main(argv):
    if not _valid(argv):
        return _bad_arguments()
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    classified = subprocess.run([os.path.join(here, "classify-bail.sh"), argv[1]], capture_output=True, text=True)
    if classified.returncode != 0:
        sys.stderr.write("bail: unknown cause %s; bail by BAIL.md sub-step 1\n" % argv[1])
        return 2
    classification = classified.stdout.strip()
    step = subprocess.run([os.path.join(here, "ledger-steps.sh"), "current-or-last-done"],
                          capture_output=True, text=True).stdout.strip()
    attempt = argv[6] if len(argv) == 7 else "1"
    subprocess.run([os.path.join(here, "preserve-attempt.sh"), argv[0], step, argv[2], attempt, "bail"],
                   capture_output=True, text=True)
    subprocess.run(["git", "reset", "--hard", "HEAD"], capture_output=True, text=True)
    env = dict(os.environ, VERI_PHASE=argv[2])
    subprocess.run([os.path.join(here, "event.sh"), "bail", "cause=" + argv[1], "classification=" + classification],
                   env=env, capture_output=True, text=True)
    metrics = subprocess.run([os.path.join(here, "metrics.sh"), argv[0]], capture_output=True, text=True)
    if metrics.returncode == 0:
        path = os.path.join(".tdd", "issue-%s-metrics.md" % argv[0])
        os.makedirs(".tdd", exist_ok=True)
        with open(path, "w") as f:
            f.write(metrics.stdout)
        subprocess.run(["git", "add", "-f", path], capture_output=True, text=True)
        subprocess.run(["git", "commit", "-m", "metrics: what bailing on #%s cost (#%s)" % (argv[0], argv[0]), "--", path],
                       capture_output=True, text=True)
    subprocess.run([os.path.join(here, "push-branch.sh")], capture_output=True, text=True)
    subprocess.run([os.path.join(here, "comment.sh"), argv[0], "bailed"],
                   capture_output=True, text=True)
    subprocess.run([os.path.join(here, "comment.sh"), argv[0], "bailed", "--pr"],
                   capture_output=True, text=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
