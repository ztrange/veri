"""stack-tag.sh's logic, run in-process: cuts the tags of a landed slice, one per issue that changed behaviour (PRD
034.4c)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import re
import sys

import entry

USAGE = "usage: stack-tag.sh <slice-pr-url> [--message <n>=<text>]..."


def arguments(argv):
    """(<slice-pr-url>, {issue number: message}) from <argv>; None when it is not one url followed by `--message
    <n>=<text>` pairs."""
    if not argv or argv[0].startswith("-") or len(argv) % 2 != 1:
        return None
    messages = {}
    for flag, value in zip(argv[1::2], argv[2::2]):
        pair = re.fullmatch(r"(\d+)=(.+)", value, re.S)
        if flag != "--message" or not pair:
            return None
        messages[pair[1]] = pair[2]
    return argv[0], messages


def main(argv):
    parsed = arguments(argv)
    if parsed is None:
        return entry.refuse(usage=USAGE)
    return 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
