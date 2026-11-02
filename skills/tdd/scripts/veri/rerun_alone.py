"""rerun-alone.sh's rerun of the test files a red run names, each alone."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import re
import subprocess
import sys

import event


def main(argv):
    if not argv:
        sys.stderr.write("usage: rerun-alone.sh <alone-cmd> <red-output-file>\n")
        return 2
    with open(argv[1], errors="replace") as red:
        files = re.findall(r"[\w./-]+\.test\.\w+", red.read())
    if not files:
        return 1
    still_red = [f for f in files if subprocess.run(["sh", "-c", argv[0], "sh", f]).returncode]
    if still_red:
        return 1
    return event.append("", {}, "suite-flake", ["files=" + ",".join(files)])


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
