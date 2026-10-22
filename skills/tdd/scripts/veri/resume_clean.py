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


def keep(appends):
    kept = Path(git("rev-parse", "--git-path", "kept-tdd-appends.diff").strip())
    n = 0
    while kept.exists():
        n += 1
        kept = kept.with_name(f"kept-tdd-appends.diff.{n}")
    kept.write_bytes(appends)
    files = sorted(set(re.findall(r"^diff --git a/(\S+) b/", appends.decode("utf-8", "replace"), re.M)))
    places = sorted(str(f.resolve()) for name in ("set-aside-tdd-appends.diff", "kept-tdd-appends.diff")
                    for f in kept.parent.glob(name + "*"))
    sys.stderr.write(f"resume-clean: could not re-apply appends to {' '.join(files)}; kept in {' '.join(places)}\n")
    return 2


def main(argv):
    appends = subprocess.run(["git", "diff", "--binary", "HEAD", "--", ".tdd"],
                             check=True, stdout=subprocess.PIPE).stdout
    stray = git("status", "--porcelain", "-uall", *PATHSPEC)
    git("reset", "--hard", "HEAD")
    git("clean", "-fd", "-e", ".tdd")
    if appends:
        applied = subprocess.run(["git", "apply", "--unidiff-zero", "-"], input=appends,
                                 stderr=subprocess.DEVNULL)
        if applied.returncode:
            return keep(appends)
    untick_ledgers()
    sys.stdout.write(stray)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
