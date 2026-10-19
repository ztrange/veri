"""handoff-state.sh's computation, run in-process."""
import json
import subprocess
import sys

from git import git

try:
    from . import status
except ImportError:
    import status


def out(*args):
    return git(*args, capture_output=True, text=True).stdout.strip()


def has_open_pr(branch):
    answer = subprocess.run(["gh", "pr", "list", "--head", branch, "--state", "open", "--json", "number"],
                            stdout=subprocess.PIPE, text=True)
    return answer.returncode == 0 and bool(json.loads(answer.stdout or "[]"))


def parked_reason(run):
    if run["state"] == "bailed":
        return "%s %s" % (run["bail_phase"], run["classification"])
    if run["state"] == "stopped":
        return run["stop_mode"]
    return ""


def main(argv):
    sha = out("rev-parse", "main")
    tag = out("tag", "--sort=-v:refname").splitlines()[0]
    print("main %s %s" % (sha, tag))
    print("## Running")
    code, document = status.json_document()
    runs = json.loads(document)["runs"] if code == 0 else []
    for run in runs:
        if run["state"] == "running":
            print("#%s %s | step %s | %s | $%s | %ss" % (
                run["issue"], run["title"], run["step"], run["phase"], run["dollars"], run["elapsed_seconds"]))
    print("## Parked")
    for run in runs:
        if run["state"] in ("bailed", "stopped", "stale") and has_open_pr(run.get("branch", "")):
            print(("#%s %s %s" % (run["issue"], run["state"], parked_reason(run))).rstrip())
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
