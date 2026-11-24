"""pin-recheck.sh's re-run of the recorded pin mutations a range touches."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import contextlib
import dataclasses
import enum
import hashlib
import os
import shutil
import signal
import tempfile
import re
import subprocess
import sys
from pathlib import Path

import entry
import event
import mutation_record
import run_dir
from event_log import run_keeping_journal

USAGE = "usage: pin-recheck.sh --branch-base <sha> <base-sha> [--ledger <file>]"
BRANCH_BASE_REFUSAL = "pin-recheck.sh: --branch-base must name the run's branch base, a sha matching ^[0-9a-f]{7,40}$"


def current_wrapper(command):
    head, _, rest = command.partition(" ")
    if head.endswith("/timed-test-run.sh") and not Path(head).exists():
        return f"{Path(__file__).resolve().parent.parent / 'timed-test-run.sh'} {rest}"
    return command


def run_captured(command):
    return subprocess.run(command, shell=True, capture_output=True, text=True)


def control_run(path, original, command):
    path.write_bytes(b"\x00 control run: no runner can load this\n")
    control = run_captured(command)
    path.write_bytes(original)
    return control


def output_lines(run):
    """The run's lines, plus those of the output timed-test-run.sh saved in place of printing it (its `full output:` line)."""
    lines = set(run.stdout.splitlines()) | set(run.stderr.splitlines())
    for line in run.stdout.splitlines():
        saved = Path(line.removeprefix("full output: "))
        if line.startswith("full output: ") and saved.is_file():
            lines |= set(saved.read_text(errors="replace").splitlines())
    return lines


def is_go_test_failure(run):
    lines = output_lines(run)
    return any(line.startswith("--- FAIL: ") for line in lines)


def is_pytest_failure(run):
    return any(line.startswith("FAILED ") for line in output_lines(run))


def needs_a_look(looks, file, reason):
    looks[(file, reason)] = looks.get((file, reason), 0) + 1


def flush_looks(looks):
    for (file, reason), n in looks.items():
        sys.stdout.write(f"needs a look: {file} ({reason})" + (f" ×{n}" if n > 1 else "") + "\n")


def write_tail(run):
    sys.stderr.write("".join(line + "\n" for line in (run.stdout.splitlines() + run.stderr.splitlines())[-40:]))


def git_out(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def tick_commit(ledger):
    number = mutation_record.number(ledger)
    return subprocess.run(["git", "log", "-1", "--format=%H", "--", run_dir.ledger(".", number)],
                          capture_output=True, text=True).stdout.strip()


def replay_names(pin, ledger):
    green = tick_commit(ledger) or pin.get("green")
    names = git_out("diff", "--name-only", pin["before"], *([green] if green else [])).split()
    return green, [n for n in names if n != pin["keep"] and not n.startswith(".tdd/")]


def in_tree(rev, path):
    return subprocess.run(["git", "cat-file", "-e", f"{rev}:{path}"], capture_output=True).returncode == 0


def present_in_range(names, base):
    """The replay paths HEAD or <base-sha> holds: one absent at both left before the range, so the replay skips it
    rather than recreate it, perhaps in a directory that is gone too (#3696)."""
    return [n for n in names if in_tree("HEAD", n) or in_tree(base, n)]


def replay_before(pin, ledger, root=Path("."), span=None):
    green, names = span or replay_names(pin, ledger)
    if not names and green:
        sys.stderr.write(f"empty replay range: before {pin['before']} green {green}\n")
        return None
    here = os.getcwd()
    os.chdir(root)
    try:
        saved = {n: Path(n).read_bytes() for n in names if Path(n).exists()}
        modes = {n: Path(n).stat().st_mode for n in saved}
        try:
            for n in names:
                shown = subprocess.run(["git", "show", f"{pin['before']}:{n}"], capture_output=True)
                if shown.returncode == 0:
                    Path(n).write_bytes(shown.stdout)
                else:
                    Path(n).unlink(missing_ok=True)
            ran = run_captured(current_wrapper(pin["command"]))
        finally:
            for n in names:
                if n in saved:
                    Path(n).write_bytes(saved[n])
                    Path(n).chmod(modes[n])
                else:
                    Path(n).unlink(missing_ok=True)
    finally:
        os.chdir(here)
    return ran.returncode


@contextlib.contextmanager
def base_worktree(base):
    scratch = tempfile.mkdtemp()
    tree = Path(scratch) / "base"
    try:
        added = subprocess.run(["git", "worktree", "add", "--detach", str(tree), base], capture_output=True, text=True)
        if added.returncode != 0:
            sys.stderr.write(f"cannot create the base worktree at {base}: {added.stderr.strip()}\n")
            yield None
        else:
            yield tree
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(tree)], capture_output=True)
        shutil.rmtree(scratch, ignore_errors=True)


def replay_on_base(pin, ledger, branch_base, span=None):
    with base_worktree(branch_base) as tree:
        return None if tree is None else replay_before(pin, ledger, tree, span)


def mutation_green_on_base(pin, branch_base, path):
    with base_worktree(branch_base) as tree:
        if tree is None:
            return None
        target = tree / path
        if not target.exists() or pin["old"].encode() not in target.read_bytes():
            return False
        target.write_bytes(target.read_bytes().replace(pin["old"].encode(), pin["new"].encode()))
        return subprocess.run(pin["command"], shell=True, cwd=tree, capture_output=True).returncode == 0


def mutated_file_of(record):
    return record.get("file", record.get("keep"))


def declared_retirements(diff_text):
    """The `retire-pin: <ledger> <file> -- <reason>` lines a `.tdd` diff adds, as ({(ledger, file): reason}, refusal).
    The first declaration with an empty reason ends the read: its refusal message is returned with what was read
    before it dropped (the caller discards it)."""
    declared = {}
    for line in diff_text.splitlines():
        m = re.match(r"\+\s*retire-pin: (\S+) (\S+) --(.*)$", line)
        if m:
            if not m[3].strip():
                return {}, f"retire-pin for {m[1]} {m[2]} has an empty reason"
            declared[(m[1], m[2])] = m[3].strip()
    return declared, None


class Kind(enum.Enum):
    SKIP = "skip"
    RETIRE_DECLARED = "retire-declared"
    RETIRE_TESTS_GONE = "retire-tests-gone"
    RETIRE_FILE_DELETED = "retire-file-deleted"
    REPLAY_BEFORE = "replay-before"
    REPLAY_MUTATION = "replay-mutation"


@dataclasses.dataclass(frozen=True)
class Outcome:
    """How one pin sorts: `named` the test files its command still names, `gone` the ones the range deleted,
    `reason` a declaration's, `command` the pin's command without the deleted tests (None for SKIP and
    RETIRE_DECLARED, which never run it)."""
    kind: Kind
    named: tuple = ()
    gone: tuple = ()
    reason: str = ""
    command: str | None = None


def classify(ledger, pin, deleted, declared):
    """Sort one pin, from the files the range deleted and the declarations, before any file or git is consulted."""
    if "retired" in pin:
        return Outcome(Kind.SKIP)
    reason = declared.get((ledger, mutated_file_of(pin)))
    if reason:
        return Outcome(Kind.RETIRE_DECLARED, reason=reason)
    named = [n.strip("\"'") for n in re.findall(r"TESTS=(\S+)", pin["command"])]
    gone = tuple(n for n in named if n.split("::")[0] in deleted)
    named = tuple(n for n in named if n.split("::")[0] not in deleted)
    if gone and not named:
        return Outcome(Kind.RETIRE_TESTS_GONE, gone=gone, command=pin["command"])
    command = pin["command"]
    for n in gone:
        command = re.sub(r"TESTS=[\"']?" + re.escape(n) + r"[\"']*(?=\s|$)", "", command)
    if "before" in pin:
        kind = Kind.REPLAY_BEFORE
    elif pin["file"] in deleted:
        kind = Kind.RETIRE_FILE_DELETED
    else:
        kind = Kind.REPLAY_MUTATION
    return Outcome(kind, named, gone, command=command)


def replay_before_state(pin, ledger, named, base, branch_base, looks):
    """Replay a before-pin on the range, then on the base; 0 nothing to count, 1 a red status, 2 no answer."""
    green, names = replay_names(pin, ledger)
    span = (green, present_in_range(names, base))
    replayed = replay_before(pin, ledger, span=span)
    if replayed is None:
        return 2
    if replayed == 0:
        on_base = replay_on_base(pin, ledger, branch_base, span)
        if on_base is None:
            return 2
        if on_base == 0:
            sys.stdout.write(f"stale: {ledger} {(named[0].split('::')[0] if named else pin['keep'])}\n")
        else:
            needs_a_look(looks, named[0].split("::")[0] if named else pin["keep"], "pin stayed green on the before-state")
    return 0


def moved_to(pin):
    """The files holding the pin's old text: those of its directory first, else every tracked file outside .tdd/."""
    old = pin["old"].encode()
    held = [f for f in sorted(Path(pin["file"]).parent.iterdir()) if f.is_file() and old in f.read_bytes()]
    if held:
        return held
    tracked = git_out("ls-files", "-z").split("\0")
    return [f for f in map(Path, tracked) if f.parts and f.parts[0] != ".tdd" and f.is_file() and not f.is_symlink() and old in f.read_bytes()]


def gone_before_range(pin, base_sha):
    """Whether the pin's old text was already gone from its file at <base-sha> and no commit of the range added or
    removed it there (`git log -S`), so a step that added the text and refactored it away is not called stale; None
    when git could not answer."""
    if in_tree(base_sha, pin["file"]):
        shown = subprocess.run(["git", "show", f"{base_sha}:{pin['file']}"], capture_output=True)
        if shown.returncode != 0:
            sys.stderr.write(f"cannot read {pin['file']} at {base_sha}: {shown.stderr.decode(errors='replace').strip()}\n")
            return None
        if pin["old"].encode() in shown.stdout:
            return False
    touched = subprocess.run(["git", "log", "--format=%H", f"-S{pin['old']}", f"{base_sha}..HEAD", "--", pin["file"]],
                             capture_output=True, text=True)
    if touched.returncode != 0:
        sys.stderr.write(f"cannot search {base_sha}..HEAD for the old text of {pin['file']}: {touched.stderr.strip()}\n")
        return None
    return not touched.stdout.strip()


def replay(pin, ledger, looks, branch_base, base_sha):
    """Replay a mutation pin: the mutation, then a control run; 0 nothing to count, 1 a red status, 2 no answer."""
    path = Path(pin["file"])
    if not path.exists():
        sys.stdout.write(f"stale: {ledger} {mutated_file_of(pin)}\n")
        return 0
    pin["command"] = current_wrapper(pin["command"])
    original = path.read_bytes()
    if pin["old"].encode() not in original:
        moved = moved_to(pin)
        if len(moved) != 1:
            gone = gone_before_range(pin, base_sha)
            if gone is None:
                return 2
            if gone:
                sys.stdout.write(f"stale: {ledger} {pin['file']}\n")
                return 0
            where = "no file" if not moved else "more than one file"
            needs_a_look(looks, pin["file"], f"old text in {where} of the repo")
            return 0
        path = moved[0]
        original = path.read_bytes()
    if original.count(pin["old"].encode()) > 1:
        needs_a_look(looks, pin["file"], "old text occurs more than once")
        return 0
    if "context" in pin and pin["context"] not in original.decode().splitlines():
        needs_a_look(looks, pin["file"], "old text moved off its recorded line")
        return 0
    seen = Path(".tdd/pin-recheck-red") / hashlib.sha256(
        b"\0".join([git_out("rev-parse", "HEAD").encode(), original, pin["old"].encode(), pin["new"].encode(),
                    pin["command"].encode()])).hexdigest()
    if seen.exists():
        return 0
    base = run_captured(pin["command"])
    if base.returncode == 127 or "no makefile found" in base.stderr.lower():
        sys.stderr.write(f"command not found: {pin['command']} (pin file {ledger})\n")
        return 2
    if base.returncode == 2 and ("invalid option" in base.stderr or "Usage: make" in base.stderr):
        sys.stderr.write(f"command rejected by make: {pin['command']} (pin file {ledger})\n")
        return 2
    if base.returncode != 0:
        needs_a_look(looks, pin["file"], "base run failed")
        write_tail(base)
        return 0
    path.write_bytes(original.replace(pin["old"].encode(), pin["new"].encode()))
    try:
        mutated = run_keeping_journal(lambda: run_captured(pin["command"]))
    finally:
        path.write_bytes(original)
    green = mutated.returncode == 0
    base_lines = output_lines(base)
    if not green and not base_lines & output_lines(mutated) and not is_go_test_failure(mutated) and not is_pytest_failure(mutated):
        needs_a_look(looks, pin["file"], "mutation did not build")
        write_tail(mutated)
        return 1
    if green:
        control = control_run(path, original, pin["command"])
        if control.returncode == 0:
            needs_a_look(looks, pin["file"], "mutation and control green")
            return 0
        on_base = mutation_green_on_base(pin, branch_base, path)
        if on_base is None:
            return 2
        if on_base:
            sys.stdout.write(f"stale: {ledger} {pin['file']}\n")
            return 0
        needs_a_look(looks, pin["file"], "pin stayed green under its mutation")
        return 0
    seen.parent.mkdir(parents=True, exist_ok=True)
    seen.touch()
    return 0


def recheck(argv, looks):
    if argv[:1] != ["--branch-base"] or len(argv) < 2 or not re.fullmatch(r"[0-9a-f]{7,40}", argv[1]):
        return entry.refuse(BRANCH_BASE_REFUSAL, usage=USAGE)
    branch_base, argv = argv[1], argv[2:]
    if not argv or argv[1:] and (argv[1] != "--ledger" or len(argv) != 3):
        return entry.refuse(usage=USAGE)
    touched = set(git_out("diff", "--name-only", f"{argv[0]}..HEAD").split())
    found = [(f, r) for f in mutation_record.paths() for r in mutation_record.records(Path(f).read_text())]
    for f, r in found:
        if "before" not in r and "file" not in r:
            sys.stderr.write(f"unparseable mutation record in {f}: {r}\n")
            return 2
    only = argv[2] if argv[1:] else None
    pins = [(f, r) for f, r in found if mutated_file_of(r) in touched and only in (None, f)]
    if not pins:
        return 3
    deleted = set(git_out("diff", "--name-only", "--diff-filter=D", f"{argv[0]}..HEAD").split())
    declared, refusal = declared_retirements(git_out("diff", "-U0", f"{argv[0]}..HEAD", "--", ".tdd"))
    if refusal:
        sys.stderr.write(refusal + "\n")
        return 2
    held = {(f, mutated_file_of(r)) for f, r in found}
    for key in declared:
        if key not in held:
            sys.stderr.write(f"retire-pin names no pin: {key[0]} {key[1]}\n")
            return 2
    status = 0
    retired = 0
    for ledger, pin in pins:
        mutated_file = mutated_file_of(pin)
        outcome = classify(ledger, pin, deleted, declared)
        if outcome.kind is Kind.SKIP:
            retired += 1
            continue
        if outcome.kind is Kind.RETIRE_DECLARED:
            sys.stdout.write(f"retired: {ledger} {mutated_file} {outcome.reason}\n")
            retired += 1
            event.append("", {}, "pin-retired", [f"reason={outcome.reason}"])
            pin["retired"] = outcome.reason
            Path(ledger).write_text("".join(mutation_record.format_record(r.items()) for f, r in found if f == ledger))
            continue
        if outcome.kind is Kind.RETIRE_TESTS_GONE:
            for n in outcome.gone:
                sys.stdout.write(f"retired: {ledger} {mutated_file} {n}\n")
            retired += 1
            continue
        pin["command"] = outcome.command
        missing = [n for n in outcome.named if not Path(n.split("::")[0]).exists()]
        if missing:
            for n in missing:
                if subprocess.run(["git", "cat-file", "-e", f"{branch_base}:{n.split('::')[0]}"],
                                  capture_output=True).returncode == 0:
                    sys.stderr.write(f"named test missing at HEAD: {n} (pin file {ledger})\n")
                    return 2
            sys.stdout.write(f"stale: {ledger} {mutated_file}\n")
            continue
        if outcome.kind is Kind.RETIRE_FILE_DELETED:
            sys.stdout.write(f"retired: {ledger} {pin['file']} {pin['file']}\n")
            retired += 1
            continue
        if outcome.kind is Kind.REPLAY_BEFORE:
            code = replay_before_state(pin, ledger, outcome.named, argv[0], branch_base, looks)
        else:
            code = replay(pin, ledger, looks, branch_base, argv[0])
        if code == 2:
            return 2
        status = status or code
    if retired == len(pins):
        return 3
    return status


RECEIPT = Path(".tdd/pin-recheck-ok")


def main(argv):
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))
    RECEIPT.unlink(missing_ok=True)
    looks = {}
    status = recheck(argv, looks)
    flush_looks(looks)
    if status in (0, 3):
        head = git_out("rev-parse", "HEAD").strip()
        RECEIPT.write_text(head + "\n")
    return status


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
