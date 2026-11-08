"""refactor-candidates.sh's one candidates issue per run, filed in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import re
import sys

try:
    from veri import github
except ImportError:
    import github

USAGE = "usage: refactor-candidates.sh <issue> <owed-file>\n"
LABELS = ("refactor", "refactor-owed")


def rows(owed):
    for line in owed.split("\n"):
        if line.startswith("- out-of-bounds | "):
            yield "- out-of-bounds | " + line[len("- out-of-bounds | "):]
        elif line.startswith("not-done | "):
            _, reason, candidate = line.split(" | ", 2)
            yield "- %s | %s" % (reason, candidate)


def main(argv):
    if len(argv) != 2:
        sys.stderr.write(USAGE)
        return 2
    issue, owed_file = argv
    with open(owed_file) as handle:
        body = "\n".join(rows(handle.read())) + "\n"
    url = github.gh_issue_create("Refactor candidates left by #" + issue, body)
    number = re.search(r"([0-9]+)\s*$", url).group(1)
    for label in LABELS:
        github.gh_issue_add_label(number, label)
    sys.stdout.write(url)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
