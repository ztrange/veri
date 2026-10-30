"""graded-changed.sh's entry point, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import subprocess
import sys

USAGE = "usage: graded-changed.sh <base-sha>"


def main(argv):
    if len(argv) != 1:
        print(USAGE, file=sys.stderr)
        return 2
    diff = subprocess.run(["git", "diff", "--name-only", argv[0], "HEAD"], capture_output=True, text=True)
    if diff.returncode:
        return 2
    changed = diff.stdout.split()
    listed = subprocess.run(["git", "ls-files", ":(glob)**/GRADED"], capture_output=True, text=True).stdout.split()
    hits = [line.split()[0] for g in listed for line in open(g) if line.split()[0] in changed]
    for path in hits:
        print(path)
    return 1 if hits else 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
