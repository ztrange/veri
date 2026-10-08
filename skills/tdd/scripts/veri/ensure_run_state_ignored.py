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


def has_rule(path):
    if not os.path.isfile(path):
        return False
    with open(path, "rb") as f:
        lines = f.read().split(b"\n")
    at = [lines.index(line.encode()) if line.encode() in lines else None for line in RULE]
    if None not in at and at == sorted(at):
        return True
    if at[-1] is not None:
        print("ensure-run-state-ignored: %s carries veri's run-state rule only in part, or with its lines out of order"
              " — fix it by hand" % path, file=sys.stderr)
        return None
    return False


def restore(path, before):
    if before is None:
        os.remove(path)
    else:
        with open(path, "wb") as f:
            f.write(before)


def write_failed(error):
    print("ensure-run-state-ignored: %s" % error, file=sys.stderr)
    return 2


def inside_own_scripts(root):
    scripts = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    here = os.path.realpath(root)
    return here == scripts or here.startswith(scripts + os.sep)


def main(argv):
    root = argv[0] if argv and argv[0] else "."
    if inside_own_scripts(root):
        print("ensure-run-state-ignored: name the target repository,"
              " not the skill's own scripts directory", file=sys.stderr)
        return 2
    gitignore = root + "/.gitignore"
    found = subprocess.run(["git", "-C", root, "rev-parse", "--git-common-dir"],
                           stdout=subprocess.PIPE, text=True)
    if found.returncode != 0:
        return 2
    present = has_rule(gitignore)
    if present is None:
        return 2
    common_dir = found.stdout.rstrip("\n")
    if not common_dir.startswith("/"):
        common_dir = root + "/" + common_dir
    exclude = common_dir + "/info/exclude"
    in_exclude = has_rule(exclude)
    if in_exclude is None:
        return 2
    before = None
    if not present:
        if os.path.isfile(gitignore):
            with open(gitignore, "rb") as f:
                before = f.read()
        try:
            append_rule(gitignore)
        except OSError as error:
            return write_failed(error)
    if not in_exclude:
        try:
            append_rule(exclude)
        except OSError as error:
            if not present:
                restore(gitignore, before)
            return write_failed(error)
    print("already present" if present else "added")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
