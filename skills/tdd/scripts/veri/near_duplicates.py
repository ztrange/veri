"""near-duplicates.sh's pairs of an added block and an older copy of it, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import re
import subprocess
import sys

import entry
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


def pairs_within(path, lines):
    found = []
    for i, (_, text, is_added) in enumerate(lines):
        if not is_added:
            continue
        for j, (_, other, _) in enumerate(lines):
            if other != text or j == i:
                continue
            if i and j and lines[i - 1][2] and lines[i - 1][1] == lines[j - 1][1]:
                continue
            length = 0
            while (i + length < len(lines) and j + length < len(lines) and lines[i + length][2]
                   and lines[i + length][1] == lines[j + length][1]):
                length += 1
            if length < MINIMUM or (i < j + length and j < i + length):
                continue
            found.append(f"{path}:{lines[i][0]}-{lines[i + length - 1][0]} "
                         f"{path}:{lines[j][0]}-{lines[j + length - 1][0]}")
    return found


def main(argv):
    rev = argv[0]
    added = added_lines(rev)
    for path in refactor_touched.touched_files([f"{rev}^", rev]):
        text = git("show", f"HEAD:{path}")
        for line in pairs_within(path, counting_lines(text, added.get(path, set()))):
            print(line)
    return 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
