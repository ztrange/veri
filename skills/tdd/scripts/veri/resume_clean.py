"""resume-clean.sh's computations, run in-process."""
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

from ledger import OPEN_STEP, PENDING_MARK, TICKED_STEP

PATHSPEC = ["--", ".", ":!.tdd"]


class GitFailed(Exception):
    pass


def git(*args, text=True):
    done = subprocess.run(["git", *args], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=text)
    if done.returncode:
        raise GitFailed("git " + " ".join(args))
    return done.stdout


TICK = TICKED_STEP + " "


def step_text(line):
    text = line[len(TICK):].rstrip("\r\n")
    return text[:-len(PENDING_MARK)] if text.endswith(PENDING_MARK) else text


def unseen_ticks(ledger):
    shown = subprocess.run(["git", "show", f"HEAD:{ledger.as_posix()}"], stdout=subprocess.PIPE,
                           stderr=subprocess.DEVNULL, text=True)
    held = {}
    for line in shown.stdout.splitlines(True):
        if line.startswith((TICK, OPEN_STEP + " ")):
            held.setdefault(step_text(line), []).append(line.startswith(TICK))
    lines = ledger.read_text(encoding="utf-8").splitlines(True)
    seen = Counter()
    for i, line in enumerate(lines):
        if line.startswith((TICK, OPEN_STEP + " ")):
            text = step_text(line)
            k = seen[text]
            seen[text] += 1
            if line.startswith(TICK) and not (k < len(held.get(text, ())) and held[text][k]):
                lines[i] = OPEN_STEP + " " + text + line[len(line.rstrip("\r\n")):]
    return "".join(lines)


def untick_ledgers():
    for ledger in sorted(Path(".tdd").glob("issue-*.md")):
        if re.fullmatch(r"issue-\d+\.md", ledger.name):
            before = ledger.read_bytes()
            after = unseen_ticks(ledger).encode("utf-8")
            if after != before:
                ledger.write_bytes(after)


def save(appends):
    kept = Path(git("rev-parse", "--git-path", "kept-tdd-appends.diff").strip())
    n = 0
    while kept.exists():
        n += 1
        kept = kept.with_name(f"kept-tdd-appends.diff.{n}")
    kept.write_bytes(appends)
    return kept


def keep(appends):
    kept = save(appends)
    files = sorted(set(re.findall(r"^diff --git a/(\S+) b/", appends.decode("utf-8", "replace"), re.M)))
    places = sorted(str(f.resolve()) for name in ("set-aside-tdd-appends.diff", "kept-tdd-appends.diff")
                    for f in kept.parent.glob(name + "*"))
    sys.stderr.write(f"resume-clean: could not re-apply appends to {' '.join(files)}; kept in {' '.join(places)}\n")
    return 2


def main(argv):
    try:
        return clean()
    except GitFailed as failed:
        sys.stderr.write(f"resume-clean: {failed} failed\n")
        return 2


def clean():
    appends = git("diff", "--binary", "HEAD", "--", ".tdd", text=False)
    stray = git("status", "--porcelain", "-uall", *PATHSPEC)
    try:
        git("reset", "--hard", "HEAD")
        git("clean", "-fd", "-e", ".tdd")
    except GitFailed:
        if appends:
            save(appends)
        raise
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
