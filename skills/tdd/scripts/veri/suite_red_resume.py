"""suite-red-resume.sh's check, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import errno
import os
import re
import subprocess
import sys

try:
    from . import add_ledger_step, event, prose_owed
    from .ledger import STEP_RE, read_ledger
except ImportError:
    import add_ledger_step
    import event
    import prose_owed
    from ledger import STEP_RE, read_ledger

CASE_RE = re.compile(r"([-+])\s*def (test\w*)")

USAGE = (
    "usage: suite-red-resume.sh check <ledger-file> <branch-red-file> <default-red-file>\n"
    "       suite-red-resume.sh insert <ledger-file> <branch-red-file>\n"
    "       suite-red-resume.sh rebased-tip <ledger-file> <red-file> <pre-rebase-sha>\n"
    "       suite-red-resume.sh flake <at> <red-file> <alone-red-file>\n"
    "       suite-red-resume.sh test-only <base-sha> <alone-cmd> <suite>..."
)
SEPARATOR = " — "
GRADE_SUITES = {"test_prd_015_prose_signed.py", "test_prd_016_short_names.py"}


def complain(message):
    print(f"suite-red-resume.sh: {message}", file=sys.stderr)


def read_text(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def read_nonempty(path):
    text = read_text(path)
    if not text.strip():
        raise OSError(errno.ENODATA, "empty", path)
    return text


def attempt(read):
    try:
        return read(), None
    except OSError as error:
        complain(f"{error.filename}: {error.strerror}")
        return None, 2


def suites(text):
    return [line.split(SEPARATOR)[0] for line in text.splitlines()]


def insert(ledger, branch_file):
    text, failed = attempt(lambda: read_nonempty(branch_file))
    if failed:
        return failed
    reds = text.splitlines()
    steps = [line for line in read_ledger(ledger).split("\n") if STEP_RE.fullmatch(line)]
    ticks = [STEP_RE.fullmatch(line).group(2) for line in steps]
    unchecked = [line for line, tick in zip(steps, ticks) if tick == " "]
    if any("fix the full-suite failure by editing" in line for line, tick in zip(steps, ticks) if tick != " "):
        return 1
    graded_only = set(suites(text)) <= GRADE_SUITES
    owed = prose_owed.owed_listed()[0] if graded_only else []
    if unchecked and "⟦skill-edit⟧" in unchecked[0]:
        if graded_only and any(unit in unchecked[0] for _, unit in owed):
            return 0
    where, anchor = ("before", unchecked[0]) if unchecked else ("after", steps[-1])
    step = "fix the full-suite failure: " + "; ".join(reds) + " ⟦suite-repair⟧"
    if graded_only:
        pinned = [unit for _, unit in owed if all(unit in red for red in reds)]
        if pinned:
            step = f"fix the full-suite failure by editing `{pinned[0]}`: " + "; ".join(reds) + " ⟦skill-edit⟧"
    return add_ledger_step.main([ledger, where, anchor, step])


def flake(at, red_file, alone_file):
    text, failed = attempt(lambda: suites(read_text(red_file)))
    if failed:
        return failed
    alone, failed = attempt(lambda: suites(read_text(alone_file)))
    if failed:
        return failed
    still_red = [name for name in alone if name != "none"]
    if still_red:
        for name in still_red:
            complain(f"{name} is still red alone")
        return 1
    if not text:
        return 1
    return event.append("", {}, "suite-flake", ["at=" + at, "files=" + ",".join(text)])


def test_only(base, alone_cmd, named):
    red = [name for name in named if subprocess.run(["sh", "-c", alone_cmd, "sh", name]).returncode]
    for name in red:
        complain(f"{name} is still red alone")
    diff = subprocess.run(["git", "diff", base], capture_output=True, text=True).stdout.splitlines()
    cases = [m.groups() for m in map(CASE_RE.match, diff) if m]
    gone = {name for sign, name in cases if sign == "-"} - {name for sign, name in cases if sign == "+"}
    for name in sorted(gone):
        complain(f"{name} is deleted")
    return 1 if red or gone else 0


def main(argv):
    if len(argv) >= 4 and argv[0] == "test-only":
        return test_only(argv[1], argv[2], argv[3:])
    if len(argv) == 4 and argv[0] == "flake":
        return flake(argv[1], argv[2], argv[3])
    if len(argv) == 4 and argv[0] == "rebased-tip":
        code = insert(argv[1], argv[2])
        if code == 1:
            subprocess.run(["git", "reset", "--hard", argv[3]])
        elif code == 0:
            lease = os.path.join(os.path.dirname(os.path.abspath(argv[1])), "rebase-lease")
            with open(lease, "w") as handle:
                handle.write(argv[3] + "\n")
        return code
    if len(argv) == 3 and argv[0] == "insert":
        return insert(argv[1], argv[2])
    if len(argv) != 4 or argv[0] != "check":
        print(USAGE, file=sys.stderr)
        return 2
    _, ledger, branch_file, default_file = argv
    inputs, failed = attempt(lambda: (read_nonempty(branch_file), read_nonempty(default_file)))
    if failed:
        return failed
    branch, default = inputs
    red_on_default = set(suites(default))
    shared = [suite for suite in suites(branch) if suite in red_on_default]
    if shared:
        for suite in shared:
            complain(f"{suite} is red on the default branch too")
        return 1
    sys.stdout.write(branch)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
