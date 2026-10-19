"""handoff-state.sh's computation, run in-process."""
import json
import sys

from git import git

try:
    from . import status
except ImportError:
    import status


def out(*args):
    return git(*args, capture_output=True, text=True).stdout.strip()


def main(argv):
    sha = out("rev-parse", "main")
    tag = out("tag", "--sort=-v:refname").splitlines()[0]
    print("main %s %s" % (sha, tag))
    print("## Running")
    code, document = status.json_document()
    for run in (json.loads(document)["runs"] if code == 0 else []):
        if run["state"] == "running":
            print("#%s %s | step %s | %s | $%s | %ss" % (
                run["issue"], run["title"], run["step"], run["phase"], run["dollars"], run["elapsed_seconds"]))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
