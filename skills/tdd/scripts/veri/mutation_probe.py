"""mutation-probe.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import signal
import subprocess
import sys
from pathlib import Path

USAGE = "usage: mutation-probe.sh <file> <old> <new> -- <command…>"


def main(argv):
    if len(argv) < 5 or argv[3] != "--":
        sys.stderr.write(USAGE + "\n")
        return 2
    path = Path(argv[0])
    saved = path.read_bytes()
    mutated = saved.replace(argv[1].encode(), argv[2].encode())
    if mutated == saved:
        sys.stderr.write("mutation-probe.sh: file not mutated\n")
        return 2
    signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(128 + signum))
    path.write_bytes(mutated)
    try:
        returncode = subprocess.run(argv[4:]).returncode
    finally:
        path.write_bytes(saved)
    if returncode == 0:
        sys.stderr.write("mutation-probe.sh: suite stayed green under the mutation\n")
        return 1
    record = os.environ.get("VERI_MUTATION_RECORD")
    if record:
        fields = (("file", argv[0]), ("old", argv[1]), ("new", argv[2]), ("command", " ".join(argv[4:])))
        with open(record, "a") as f:
            for name, value in fields:
                f.write(f"{name} {len(value)}\n{value}\n")
            f.write("\n")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
