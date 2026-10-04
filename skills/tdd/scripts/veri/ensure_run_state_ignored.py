"""ensure-run-state-ignored.sh's logic, run in-process."""
import os
import subprocess
import sys

RULE = (".tdd/*", "!.tdd/issue-*.md", ".tdd/issue-*-spec.md")


def append_rule(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as f:
        f.write("".join(line + "\n" for line in RULE))


def main(argv):
    root = argv[0]
    gitignore = root + "/.gitignore"
    found = subprocess.run(["git", "-C", root, "rev-parse", "--git-common-dir"],
                           stdout=subprocess.PIPE, text=True)
    if found.returncode != 0:
        return 2
    common_dir = root + "/" + found.stdout.rstrip("\n")
    append_rule(common_dir + "/info/exclude")
    append_rule(gitignore)
    print("added")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
