"""pin-recheck.sh's re-run of the recorded pin mutations a range touches."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import glob
import subprocess
import sys
from pathlib import Path


def records(text):
    out, i = [], 0
    while i < len(text):
        if text[i] == "\n":
            i += 1
            continue
        record = {}
        while i < len(text) and text[i] != "\n":
            end = text.index("\n", i)
            name, size = text[i:end].split()
            record[name] = text[end + 1:end + 1 + int(size)]
            i = end + 2 + int(size)
        out.append(record)
    return out


def main(argv):
    if not argv:
        sys.stderr.write("usage: pin-recheck.sh <base-sha>\n")
        return 2
    touched = set(subprocess.run(["git", "diff", "--name-only", f"{argv[0]}..HEAD"], capture_output=True, text=True,
                                 check=True).stdout.split())
    pins = [r for f in sorted(glob.glob(".tdd/issue-*-mutations.md")) for r in records(Path(f).read_text())
            if r["file"] in touched]
    return 0 if pins else 3


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
