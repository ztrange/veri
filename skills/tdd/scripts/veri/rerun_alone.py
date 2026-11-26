"""rerun-alone.sh's rerun of the test targets a red run names, each alone."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import re
import subprocess
import sys

import event

USAGE = "usage: rerun-alone.sh <alone-cmd> <red-output-file>"


def named_targets(text):
    """The test targets a red run's output names, in order, each once: its `FAILED `/`ERROR ` pytest node ids, else
    its `*.test.<ext>` names, else its bare `test_*.py` lines."""
    targets = re.findall(r"^(?:FAILED|ERROR) (\S+?\.py::.+?)(?: - .*)?$", text, re.M) or re.findall(r"[\w./-]+\.test\.\w+", text) or re.findall(r"^[\w./-]*test_\w+\.py$", text, re.M)
    return list(dict.fromkeys(targets))


def rerun(alone_cmd, red_file):
    """Rerun each test target the red output at `red_file` names alone, through `alone_cmd`.

    Answers 0 after appending a suite-flake event when every target passes alone, 1 when
    none is named or one stays red, else the event append's own nonzero code. The targets'
    output goes to the inherited streams; this function prints nothing itself.
    Raises OSError when `red_file` cannot be opened.
    """
    with open(red_file, errors="replace") as red:
        text = red.read()
    targets = named_targets(text)
    if not targets:
        return 1
    cmd = alone_cmd if '"$1"' in alone_cmd else alone_cmd + ' "$1"'
    still_red = [f for f in targets if subprocess.run(["sh", "-c", cmd, "sh", f]).returncode]
    if still_red:
        return 1
    return event.append("", {}, "suite-flake", ["files=" + ",".join(targets)])


def main(argv):
    if not argv:
        sys.stderr.write("usage: rerun-alone.sh <alone-cmd> <red-output-file>\n")
        return 2
    return rerun(argv[0], argv[1])


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
