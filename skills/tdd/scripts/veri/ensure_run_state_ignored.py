"""ensure-run-state-ignored.sh's logic, run in-process."""
import os
import subprocess
import sys

RULE = (".tdd/*", "!.tdd/issue-*.md", ".tdd/issue-*-spec.md")


def append_rule(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "ab+") as f:
        f.seek(0, os.SEEK_END)
        if f.tell() > 0:
            f.seek(-1, os.SEEK_END)
            if f.read(1) != b"\n":
                f.write(b"\n")
        f.write("".join(line + "\n" for line in RULE).encode())


def where(line, lines):
    return lines.index(line) if line in lines else None


def has_rule(path):
    if not os.path.isfile(path):
        return False
    with open(path, "rb") as f:
        lines = f.read().split(b"\n")
    at_all, at_ledger, at_spec = (where(line.encode(), lines) for line in RULE)
    if None not in (at_all, at_ledger, at_spec) and at_all < at_ledger < at_spec:
        return True
    if at_spec is not None:
        print("ensure-run-state-ignored: %s carries veri's run-state rule only in part, or with its lines out of order"
              " — fix it by hand" % path, file=sys.stderr)
        return None
    return False


def main(argv):
    root = argv[0]
    gitignore = root + "/.gitignore"
    found = subprocess.run(["git", "-C", root, "rev-parse", "--git-common-dir"],
                           stdout=subprocess.PIPE, text=True)
    if found.returncode != 0:
        return 2
    present = has_rule(gitignore)
    if present is None:
        return 2
    common_dir = root + "/" + found.stdout.rstrip("\n")
    exclude = common_dir + "/info/exclude"
    if not has_rule(exclude):
        append_rule(exclude)
    if not present:
        append_rule(gitignore)
    print("already present" if present else "added")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
