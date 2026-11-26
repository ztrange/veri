"""resume-clean.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

import entry
import git
from ledger import OPEN_STEP, PENDING_MARK, TICKED_STEP

PATHSPEC = ["--", ".", ":!.tdd"]


TICK = TICKED_STEP + " "


def step_text(line):
    text = line[len(TICK):].rstrip("\r\n")
    return text[:-len(PENDING_MARK)] if text.endswith(PENDING_MARK) else text


def unseen_ticks(ledger):
    shown = git.git("show", f"HEAD:{ledger.as_posix()}", stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    held = {}
    for line in shown.stdout.splitlines(True):
        if line.startswith((TICK, OPEN_STEP + " ")):
            held.setdefault(step_text(line), []).append(line.startswith(TICK))
    lines = ledger.read_bytes().decode("utf-8").splitlines(True)
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
    kept = Path(git.out("rev-parse", "--git-path", "kept-tdd-appends.diff").strip())
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


USAGE = "usage: resume-clean.sh"


def main(argv):
    refused = entry.no_arguments(argv, USAGE)
    if refused is not None:
        return refused
    try:
        return clean()
    except git.GitFailed as failed:
        sys.stderr.write(f"resume-clean: {named(failed)} failed\n")
        return 2


def named(failed):
    return "git " + " ".join(failed.args_)


def clean():
    diff = ("diff", "--binary", "HEAD", "--", ".tdd")
    done = git.git(*diff, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    if done.returncode:
        raise git.GitFailed(diff, done.returncode, "")
    appends = done.stdout
    stray = git.out("status", "--porcelain", "-uall", *PATHSPEC)
    stray += "\n" if stray else ""
    try:
        git.out("reset", "--hard", "HEAD")
        git.out("clean", "-fd", "-e", ".tdd")
    except git.GitFailed as failed:
        if not appends:
            raise
        kept = save(appends)
        paths = " ".join(line[3:] for line in stray.splitlines())
        sys.stderr.write(f"resume-clean: {named(failed)} failed; appends saved in {kept.resolve()}; stray: {paths}\n")
        return 2
    if appends:
        applied = git.git("apply", "--unidiff-zero", "-", input=appends, stderr=subprocess.DEVNULL)
        if applied.returncode:
            return keep(appends)
    untick_ledgers()
    sys.stdout.write(stray)
    return 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
