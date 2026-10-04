"""ensure-run-state-ignored.sh's logic, run in-process."""
import os
import subprocess
import sys

RULE = (".tdd/*", "!.tdd/issue-*.md", ".tdd/issue-*-spec.md")


def append_rule(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as f:
        f.write("".join(line + "\n" for line in RULE))


def refuses(path):
    if not os.path.isfile(path):
        return False
    with open(path, "rb") as f:
        lines = f.read().split(b"\n")
    if RULE[2].encode() in lines:
        print("ensure-run-state-ignored: %s carries veri's run-state rule only in part, or with its lines out of order"
              " — fix it by hand" % path, file=sys.stderr)
        return True
    return False


def main(argv):
    root = argv[0]
    gitignore = root + "/.gitignore"
    found = subprocess.run(["git", "-C", root, "rev-parse", "--git-common-dir"],
                           stdout=subprocess.PIPE, text=True)
    if found.returncode != 0:
        return 2
    if refuses(gitignore):
        return 2
    common_dir = root + "/" + found.stdout.rstrip("\n")
    append_rule(common_dir + "/info/exclude")
    append_rule(gitignore)
    print("added")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
