"""mutation-probe.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import subprocess
import sys
from pathlib import Path

USAGE = "usage: mutation-probe.sh <file> <old> <new> -- <command…>"


def main(argv):
    if not argv:
        sys.stderr.write(USAGE + "\n")
        return 2
    path = Path(argv[0])
    saved = path.read_text()
    mutated = saved.replace(argv[1], argv[2])
    if mutated == saved:
        sys.stderr.write("mutation-probe.sh: file not mutated\n")
        return 2
    path.write_text(mutated)
    if subprocess.run(argv[4:]).returncode == 0:
        sys.stderr.write("mutation-probe.sh: suite stayed green under the mutation\n")
        return 1
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
