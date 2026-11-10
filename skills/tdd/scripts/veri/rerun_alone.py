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
        text = red.read()
    files = re.findall(r"^(?:FAILED|ERROR) (\S+?\.py::\S+)", text, re.M) or re.findall(r"[\w./-]+\.test\.\w+", text) or re.findall(r"^[\w./-]*test_\w+\.py$", text, re.M)
    files = list(dict.fromkeys(files))
    if not files:
        return 1
    cmd = argv[0] if '"$1"' in argv[0] else argv[0] + ' "$1"'
    still_red = [f for f in files if subprocess.run(["sh", "-c", cmd, "sh", f]).returncode]
    if still_red:
        return 1
    return event.append("", {}, "suite-flake", ["files=" + ",".join(files)])


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
