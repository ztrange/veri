"""near-duplicates.sh's pairs of an added block and an older copy of it, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import re
import subprocess
import sys

import entry
from case_reader import is_test_path
import refactor_touched

USAGE = "usage: near-duplicates.sh <commit>"
MINIMUM = 3
IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
HUNK = re.compile(r"^@@ -\S+ \+(\d+)(?:,(\d+))? @@")


def git(*args):
    return subprocess.run(["git", *args], stdout=subprocess.PIPE, text=True, errors="replace").stdout


def added_lines(rev):
    """{path: the HEAD line numbers the diff from <rev>^ to HEAD added}."""
    added = {}
    path = None
    for line in git("diff", "-U0", "--no-color", "--no-renames", f"{rev}^", "HEAD").splitlines():
        if line.startswith("+++ "):
            path = line[len("+++ b/"):] if line.startswith("+++ b/") else None
        elif path is not None and (hunk := HUNK.match(line)):
            start = int(hunk[1])
            count = 1 if hunk[2] is None else int(hunk[2])
            added.setdefault(path, set()).update(range(start, start + count))
    return added


def counting_lines(text, added):
    """(HEAD line number, normalised text, added?) per line holding a letter or a digit."""
    return [(number, re.sub(r"\s", "", IDENTIFIER.sub("X", line)), number in added)
            for number, line in enumerate(text.splitlines(), 1) if re.search(r"[A-Za-z0-9]", line)]


def run_length(lines, i, others, j):
    """How many counting lines from lines[i] on are added and equal to those from others[j] on."""
    length = 0
    while (i + length < len(lines) and j + length < len(others) and lines[i + length][2]
           and lines[i + length][1] == others[j + length][1]):
        length += 1
    return length


def pairs(files):
    """The `<file>:<first>-<last> <file>:<first>-<last>` lines, over [(path, counting lines)] in touched order."""
    found = []
    for path, lines in files:
        for i, (_, text, is_added) in enumerate(lines):
            if not is_added:
                continue
            for other_path, others in files:
                for j, (_, other, _) in enumerate(others):
                    if other != text or (other_path == path and j == i):
                        continue
                    if i and j and lines[i - 1][2] and lines[i - 1][1] == others[j - 1][1]:
                        continue
                    length = run_length(lines, i, others, j)
                    if length < MINIMUM or (other_path == path and i < j + length and j < i + length):
                        continue
                    found.append(f"{path}:{lines[i][0]}-{lines[i + length - 1][0]} "
                                 f"{other_path}:{others[j][0]}-{others[j + length - 1][0]}")
    return found


def main(argv):
    rev = argv[0]
    added = added_lines(rev)
    files = [(path, counting_lines(git("show", f"HEAD:{path}"), added.get(path, set())))
             for path in refactor_touched.touched_files([f"{rev}^", rev]) if not is_test_path(path)]
    for line in pairs(files):
        print(line)
    return 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
