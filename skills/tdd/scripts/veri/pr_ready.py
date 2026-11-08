"""pr-ready.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

try:
    from veri import github, tunables
except ImportError:
    import github
    import tunables


def main(argv):
    if len(argv) != 2:
        print("usage: pr-ready.sh <pr-number> <sha>", file=sys.stderr)
        return 2
    try:
        github.gh_pr_ready(argv[0], argv[1])
    except github.NoAnswer:
        return 2
    issue = tunables.read("VERI_STATE_LABEL_ISSUE")
    if issue:
        try:
            github.gh_issue_add_label(issue, "pr-ready")
        except github.NoAnswer:
            print("pr-ready.sh: no answer from gh labelling #%s pr-ready" % issue, file=sys.stderr)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
