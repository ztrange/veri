"""criterion-collisions.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import re
import subprocess
import sys

try:
    from git import git
except ImportError:
    from .git import git

USAGE = "usage: criterion-collisions.sh <spec-file> <base-sha>\n"


def criteria(text):
    section = re.search(r"^## Acceptance criteria\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return re.findall(r"^\s*- \[.\] (.*)$", section.group(1) if section else "", re.M)


def collisions(text, changed):
    return ["%s: criterion %d" % (path, k) for k, criterion in enumerate(criteria(text), 1)
            for path in changed if path in criterion]


def main(argv):
    if len(argv) != 2:
        sys.stderr.write(USAGE)
        return 2
    try:
        with open(argv[0], encoding="utf-8", errors="replace") as spec:
            text = spec.read()
    except OSError as error:
        sys.stderr.write("criterion-collisions.sh: %s\n" % error)
        return 2
    diff = git("diff", "--name-only", argv[1] + "..HEAD", text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    if diff.returncode != 0:
        sys.stderr.write("criterion-collisions.sh: git diff %s..HEAD failed\n" % argv[1])
        return 2
    found = collisions(text, diff.stdout.split())
    sys.stdout.write("".join(line + "\n" for line in found))
    return 1 if found else 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
