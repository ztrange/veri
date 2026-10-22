"""resume-clean.sh's computations, run in-process."""
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

PATHSPEC = ["--", ".", ":!.tdd"]


def git(*args):
    return subprocess.run(["git", *args], check=True, stdout=subprocess.PIPE, text=True).stdout


TICK = "- [x] "
PENDING = " ⟂ refactor pending"


def step_text(line):
    text = line[len(TICK):].rstrip("\r\n")
    return text[:-len(PENDING)] if text.endswith(PENDING) else text


def unseen_ticks(ledger):
    shown = subprocess.run(["git", "show", f"HEAD:{ledger.as_posix()}"], stdout=subprocess.PIPE,
                           stderr=subprocess.DEVNULL, text=True)
    held = Counter(step_text(line) for line in shown.stdout.splitlines(True) if line.startswith(TICK))
    lines = ledger.read_text(encoding="utf-8").splitlines(True)
    for i, line in enumerate(lines):
        if line.startswith(TICK):
            text = step_text(line)
            if held[text] > 0:
                held[text] -= 1
            else:
                lines[i] = "- [ ] " + text + line[len(line.rstrip("\r\n")):]
    return "".join(lines)


def untick_ledgers():
    for ledger in sorted(Path(".tdd").glob("issue-*.md")):
        if re.fullmatch(r"issue-\d+\.md", ledger.name):
            before = ledger.read_bytes()
            after = unseen_ticks(ledger).encode("utf-8")
            if after != before:
                ledger.write_bytes(after)


def main(argv):
    appends = subprocess.run(["git", "diff", "--binary", "HEAD", "--", ".tdd"],
                             check=True, stdout=subprocess.PIPE).stdout
    stray = git("status", "--porcelain", "-uall", *PATHSPEC)
    git("reset", "--hard", "HEAD")
    git("clean", "-fd", "-e", ".tdd")
    if appends:
        subprocess.run(["git", "apply", "-"], input=appends, check=True)
    untick_ledgers()
    sys.stdout.write(stray)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
