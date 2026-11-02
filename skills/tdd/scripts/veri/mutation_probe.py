"""mutation-probe.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import shlex
import signal
import subprocess
import sys
from pathlib import Path

import tunables

USAGE = "usage: mutation-probe.sh <file> <old> <new> -- <command…>"


def before_state(argv):
    sha, keep, command = argv[1], argv[3], argv[5:]
    names = subprocess.run(["git", "diff", "--name-only", "-z", sha], capture_output=True).stdout
    saved = {}
    untracked = subprocess.run(["git", "ls-files", "--others", "--exclude-standard", "-z"], capture_output=True).stdout
    for name in names.decode().split("\0") + untracked.decode().split("\0"):
        if name and name != keep and not name.startswith(".tdd/"):
            path = Path(name)
            saved[path] = path.read_bytes()
    try:
        for path in saved:
            old = subprocess.run(["git", "show", f"{sha}:{path}"], capture_output=True)
            if old.returncode:
                path.unlink()
            else:
                path.write_bytes(old.stdout)
        returncode = subprocess.run(command).returncode
    finally:
        for path, content in saved.items():
            path.write_bytes(content)
    return 1 if returncode == 0 else 0


def main(argv):
    if argv and argv[0] == "--before":
        return before_state(argv)
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
    record = tunables.read("VERI_MUTATION_RECORD")
    if record:
        recorded = argv[7:] if argv[4] == str(Path(__file__).resolve().parent.parent / "timed-test-run.sh") else argv[4:]
        fields = (("file", argv[0]), ("old", argv[1]), ("new", argv[2]), ("command", shlex.join(recorded)))
        with open(record, "a") as f:
            for name, value in fields:
                f.write(f"{name} {len(value)}\n{value}\n")
            f.write("\n")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
