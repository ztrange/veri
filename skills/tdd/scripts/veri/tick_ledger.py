"""tick-ledger.sh's tick, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import signal
import subprocess
import sys

import event
import git
import ledger
import paths
import tests_frozen

USAGE = "usage: tick-ledger.sh [--refactor-pending | --phase <phase> | --phase-owed <phase> | --surround-short | --unpinnable <reason-file> | --already-holds <reason-file>] [--case <id>] <ledger-file> <matcher>"


def complain(message):
    print(f"tick-ledger.sh: {message}", file=sys.stderr)


def case_env(make=False):
    """The case command's environment: make's own variables dropped; under make, `LC_ALL=C` so its messages are
    untranslated."""
    env = {k: v for k, v in os.environ.items() if k not in ("TESTS", "MAKEFLAGS", "MAKELEVEL")}
    return {**env, "LC_ALL": "C"} if make else env


def no_answer(code):
    """Whether a case command's code says it never ran: not executable or not found (126, 127), killed by a signal
    (128 and above under a shell, negative when Python saw the signal itself)."""
    return code < 0 or code >= 126


def how_ended(code):
    """The case command's end as stderr names it: `exit <code>`, or `killed by <SIGNAME>` for a negative code."""
    if code >= 0:
        return f"exit {code}"
    try:
        return f"killed by {signal.Signals(-code).name}"
    except ValueError:
        return f"killed by signal {-code}"


MAKE_ERROR = re.compile(r"make: \*\*\* \[.*\] Error (\d+)")
# GNU make runs a simple recipe line without a shell and reports a command it could not execute as `Error 1`,
# right after its own `make: <command>: No such file or directory` (or `Permission denied`) line.
MAKE_EXEC_FAILED = re.compile(r"make: (?!\*\*\* ).+: (No such file or directory|Permission denied)")


def make_answer(stderr):
    """A failed make run's answer: 1 (the case ran and fails) only when make's last non-empty stderr line is a
    top-level `make: *** [<target>] Error 1` (make prints it after the recipe is dead), no other `make: *** [<target>]`
    text anywhere in a line (glued to recipe output, or a signal's `Killed: 9`) ends in anything but `Error 1`, and the line just before it is not make's own could-not-execute line; 2 (no answer) otherwise.
    A nested make's failure therefore reads as 2: a repository that needs one declares its one-test-file command."""
    lines = [line.rstrip() for line in stderr.splitlines() if line.strip()]
    final = MAKE_ERROR.fullmatch(lines[-1]) if lines else None
    if not final or final.group(1) != "1":
        return 2
    if any(re.search(r"make: \*\*\* \[.*\] (?!Error 1\s*$)", line) for line in lines):
        return 2
    if len(lines) > 1 and MAKE_EXEC_FAILED.fullmatch(lines[-2]):
        return 2
    return 1


def run_case(case):
    """Run the test case `case` through the repository's one-test-file command (`make test TESTS=<case>` when it
    declares none). Returns `(answer, command, code)`: the answer (0 passes, 1 fails, 2 never ran), the command line
    run, and the process exit code."""
    detect = os.path.join(paths.resolved_scripts_of(__file__), "detect-test-command.sh")
    found = subprocess.run([detect, "--tier", "one test file"], capture_output=True, text=True)
    command = found.stdout.strip()
    path = case.split("::", 1)[0]
    is_make = not command or os.path.basename((command.split() or [""])[0]) == "make"
    if command:
        ran = f"{command} {path}"
        done = subprocess.run(["sh", "-c", command, "sh", path], capture_output=True, text=True, env=case_env(is_make))
    else:
        ran = f"make test TESTS={case}"
        done = subprocess.run(["make", "test", f"TESTS={case}"], capture_output=True, text=True, env=case_env(True))
        if "::" not in case and "/" not in path:
            path = "."
    code = done.returncode
    answer = make_answer(done.stderr or "") if is_make and code > 0 else code
    if no_answer(answer) or answer == 2:
        return 2, ran, code
    if answer and (not os.path.exists(path) or re.search(r"no tests (were )?(collected|ran)|collected 0 items",
                                                         f"{done.stdout}{done.stderr}", re.I)):
        return 2, ran, code
    return answer, ran, code


def changed_index(text, new):
    return next(i for i, (old, line) in enumerate(zip(text.split("\n"), new.split("\n"))) if old != line)


def changed_line(text, new):
    return new.split("\n")[changed_index(text, new)]


def tick_added(path, step_line):
    target = ledger.body(ledger.STEP_RE.fullmatch(step_line).group(4))
    record = ledger.added_file(path)
    try:
        with open(record, "rb") as handle:
            lines = handle.read().decode(errors="surrogateescape").split("\n")
    except FileNotFoundError:
        return
    for i, line in enumerate(lines):
        match = ledger.STEP_RE.fullmatch(line)
        if match and match.group(2) == " " and match.group(4) == target:
            lines[i] = ledger.tick_line(match)
            with open(record, "wb") as handle:
                handle.write("\n".join(lines).encode(errors="surrogateescape"))
            return


def commit_resolves(root, sha):
    """Whether <sha> names a commit in the repository at <root>."""
    return git.ok("-C", root, "rev-parse", "--verify", "--quiet", sha + "^{commit}")


def go_red_receipt_refusal(ledger_path, step_line):
    """Why go-red-step.sh's receipt, `.tdd/go-red-probed` beside the ledger, does not prove step_line's probe ran:
    absent, its line 1 not the step's probe clause, or its line 2 no commit of the worktree; None when it does."""
    receipt = os.path.join(os.path.dirname(os.path.abspath(ledger_path)), "go-red-probed")
    try:
        with open(receipt, encoding="utf-8") as handle:
            lines = handle.read().split("\n")
    except (OSError, UnicodeDecodeError):
        return f"{receipt}: no go-red receipt"
    probe = ledger.GO_RED_PROBE_RE.search(step_line)
    if not probe or lines[0] != probe.group(0):
        return f"{receipt}: not the receipt of the probe the step's go-red line names"
    sha = lines[1] if len(lines) > 1 else ""
    if not re.fullmatch(r"[0-9a-f]{7,40}", sha) or not commit_resolves(os.path.dirname(os.path.dirname(receipt)), sha):
        return f"{receipt}: its sha {sha!r} names no commit"
    return None


def surround_short(ledger_path, matcher):
    """Record a legacy step's one free relaunch of develop-surround as ` ⟂ surround short` on its committed ledger
    line: 0 recorded; 1 the step already carries it (a resumed run's included), ledger untouched; 2 surround is not
    the step's next phase, or the ledger is unreadable; 3 no open step holds matcher."""
    try:
        text = ledger.read_ledger(ledger_path)
    except OSError as error:
        complain(f"{ledger_path}: {error.strerror}")
        return 2
    try:
        found, new = ledger.ledger_mark_surround_short(text, matcher)
    except ValueError as error:
        complain(str(error))
        return 2
    if found is None:
        complain(f"{matcher}: surround-short: the step's one free relaunch of develop-surround is already spent")
        return 1
    if not found:
        return 3
    left = ledger.rewrite_ledger(ledger_path, new)
    if left:
        complain(f"left {left} behind")
        return 2
    return 0


def main(argv):
    if argv[:1] == ["--surround-short"] and len(argv) == 3 and all(argv[1:]):
        return surround_short(argv[1], argv[2])
    pending, phase, owed, reason_file, case = False, None, False, None, None
    retire = None
    while True:
        if argv[:1] in (["--already-holds"], ["--unpinnable"]) and len(argv) > 1:
            if argv[0] == "--already-holds":
                retire = "already-holds"
            reason_file, argv = argv[1], argv[2:]
            continue
        if argv[:1] == ["--case"] and len(argv) > 1:
            case, argv = argv[1], argv[2:]
        elif argv[:1] == ["--refactor-pending"]:
            pending, argv = True, argv[1:]
        elif argv[:1] == ["--phase"] and len(argv) > 1:
            phase, argv = argv[1], argv[2:]
        elif argv[:1] == ["--phase-owed"] and len(argv) > 1:
            phase, owed, argv = argv[1], True, argv[2:]
        else:
            break
    if argv[:1] == ["--case"]:
        print(USAGE, file=sys.stderr)
        return 2
    return tick((argv or [""])[0], (argv[1:] or [""])[0], case=case, pending=pending, phase=phase, owed=owed,
                retire=retire, reason_file=reason_file)


def tick(ledger_path, matcher, *, case=None, pending=False, phase=None, owed=False, retire=None, reason_file=None):
    """Tick the one unchecked step of the ledger at `ledger_path` that `matcher` names: what `tick-ledger.sh`
    does once its arguments are parsed.

    `case` is a test id to run first (the tick waits for it to pass); `pending` appends the `⟂ refactor pending`
    mark; `phase` ticks one phase of a step that lists phases, `owed` marking it owed (contract phases only);
    `retire` ("unpinnable" or "already-holds") with a non-empty `reason_file` retires the step instead, appending
    the matching `unpinnable-step` / `already-holds-step`
    event; it needs a `case`. `pending` and `phase` do not combine.
    Returns 0 ticked; 1 clean negative (the case fails; the reason does not qualify for `retire`; retire with no
    case); 2 no answer (case never ran, bad combination, unreadable ledger, a ⟦go-red⟧ step with no `.tdd/go-red-probed` beside the ledger holding its probe clause and a
    commit's sha, a ledger left behind, an empty ledger_path -> usage line); 3 nothing to tick. Writes the ledger (and its added-steps record) and, for a retirement, events.jsonl; stderr as the script prints it.
    """
    retired_mark, event_name = ledger.retire_mark("unpinnable"), "unpinnable-step"
    if retire == "already-holds":
        retired_mark, event_name = ledger.retire_mark("already holds"), "already-holds-step"
    reason_text = ""
    if reason_file and not case:
        complain(f"{matcher}: no case is named")
        return 1
    if reason_file:
        with open(reason_file, encoding="utf-8") as handle:
            reason_text = handle.read()
        if event_name == "unpinnable-step" and "stays green" not in reason_text and not ledger.BEFORE_STATE_GREEN.search(
                reason_text):
            return 1
        if event_name == "already-holds-step" and not any(
            l.startswith("REASON:") and l[7:].strip() for l in reason_text.splitlines()
        ):
            return 1
    ran, ran_command, ran_code = run_case(case) if case else (0, "", 0)
    if ran == 2:
        complain(f"{matcher}: case {case} never run ({how_ended(ran_code)}): no such file path, no tests ran, or the command could not run: {ran_command}")
        return 2
    if ran:
        complain(f"{matcher}: case {case} fails")
        return 1
    if pending and phase:
        complain("--phase and --refactor-pending cannot be combined")
        return 2
    if owed and phase not in ("contract-a", "contract-b"):
        complain(f"--phase-owed {phase}: only a contract phase can be owed")
        return 2
    if not ledger_path:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        text = ledger.read_ledger(ledger_path)
    except OSError as error:
        complain(f"{ledger_path}: {error.strerror}")
        return 2
    if phase:
        try:
            ticked, new = ledger.ledger_mark_phase(text, matcher, phase, owed)
        except ValueError as error:
            complain(str(error))
            return 2
    else:
        ticked, new = ledger.ledger_tick(text, matcher, pending)
        if ticked and reason_file:
            new_lines = new.split("\n")
            new_lines[changed_index(text, new)] += retired_mark
            new = "\n".join(new_lines)
        if ticked and ledger.listed_phases(
                text.split("\n")[changed_index(text, new)]):
            complain("step lists phases; mark one with --phase <phase>")
            return 2
    if not ticked:
        return 3
    step_line = changed_line(text, new)
    # A step opening on a bare ⟦go-red⟧ that does not also trail it put the marker in the wrong place: refused rather
    # than ticked as a cycle step with no probe behind it.
    if ledger.STEP_RE.fullmatch(step_line).group(4).lstrip().startswith(ledger.GO_RED_MARK) and not ledger.is_go_red(
            step_line):
        complain(f"{matcher}: {ledger.GO_RED_MARK} must trail the step, after its text and before its criterion tag")
        return 2
    if ledger.is_go_red(step_line):
        refusal = go_red_receipt_refusal(ledger_path, step_line)
        if refusal:
            complain(refusal)
            return 2
    left = ledger.rewrite_ledger(ledger_path, new)
    if left is None:
        tick_added(ledger_path, step_line)
    if left is None and reason_file:
        step = step_line
        reason = next((l[7:].strip() for l in reason_text.splitlines()
                       if l.startswith("REASON:") and l[7:].strip()), "")
        tdd_parent = os.path.dirname(os.path.dirname(os.path.abspath(ledger_path)))
        return event.append(tdd_parent, event.context(os.environ), event_name,
                            ["step=" + step.split("] ", 1)[1], "reason=" + reason])
    if left is None:
        ticked_line = step_line
        if tests_frozen.is_diff_checked(ticked_line):
            return tests_frozen.rerecord_earlier(ledger_path, ticked_line.split("] ", 1)[1])
        if pending:
            return tests_frozen.rerecord_committed(
                ticked_line.split("] ", 1)[1].removesuffix(ledger.PENDING_MARK),
                os.path.dirname(os.path.dirname(os.path.abspath(ledger_path))))
        return 0
    if left:
        complain(f"left {left} behind")
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
