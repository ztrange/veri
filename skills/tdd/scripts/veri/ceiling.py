"""test-ceiling.sh's ramp, run in-process: the highest test-worker count `make test` runs at with no case timeout."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))


def commit():
    return subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()


def run_suite(workers, record):
    env = dict(os.environ, VERI_PYTEST_WORKERS=str(workers), VERI_CEILING_RECORD=record)
    return subprocess.run(["make", "--no-print-directory", "-C", ROOT, "test"], env=env,
                          stdin=subprocess.DEVNULL).returncode


def main(argv):
    top = os.cpu_count() or 1
    ceiling = None
    scratch = tempfile.mkdtemp(prefix="veri-ceiling-")
    for workers in range(2, top + 1, 2):
        run_suite(workers, os.path.join(scratch, "record-%d" % workers))
        ceiling = workers
    sys.stdout.write("ceiling: %d workers\n" % ceiling)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
