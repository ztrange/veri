"""preflight.sh's computation, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import subprocess
import sys

USAGE = "usage: preflight.sh <n> <slug>"


def run_script(name, *args):
    proc = subprocess.run([name, *args], capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def main(argv):
    if len(argv) != 2:
        sys.stderr.write(USAGE + "\n")
        return 2
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
