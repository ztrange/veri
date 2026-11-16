"""tick-ledger.sh's tick, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import signal
import subprocess
import sys

import event
import ledger
import mutation_record
import paths
import tests_frozen

USAGE = "usage: tick-ledger.sh [--refactor-pending | --phase <phase> | --phase-owed <phase> | --unpinnable <reason-file> | --already-holds <reason-file>] [--case <id>] <ledger-file> <matcher> (--unpinnable and --already-holds drop every mutation record whose named test is absent from the tree)"


def complain(message):
    print(f"tick-ledger.sh: {message}", file=sys.stderr)


def case_env():
    return {k: v for k, v in os.environ.items() if k not in ("TESTS", "MAKEFLAGS", "MAKELEVEL")}


LAST_COMMAND = ""
LAST_CODE = 0


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


def case_code(done):
    """The case's exit code: make exits 2 for any failed recipe, so its first `*** [<target>] Error <k>` line
    (the innermost recipe's) gives `<k>` instead."""
    recipe = re.search(r"\*\*\* \[[^\]]*\] Error (\d+)", f"{done.stdout}{done.stderr}") if done.returncode == 2 else None
    return int(recipe.group(1)) if recipe else done.returncode


def run_case(case):
    global LAST_COMMAND, LAST_CODE
    detect = os.path.join(paths.resolved_scripts_of(__file__), "detect-test-command.sh")
    found = subprocess.run([detect, "--tier", "one test file"], capture_output=True, text=True)
    command = found.stdout.strip()
    path = case.split("::", 1)[0]
    if command:
        LAST_COMMAND = f"{command} {path}"
        done = subprocess.run(["sh", "-c", command, "sh", path], capture_output=True, text=True, env=case_env())
    else:
        LAST_COMMAND = f"make test TESTS={case}"
        done = subprocess.run(["make", "test", f"TESTS={case}"], capture_output=True, text=True, env=case_env())
        if "::" not in case and "/" not in path:
            path = "."
    LAST_CODE = case_code(done)
    if no_answer(LAST_CODE):
        return 2
    if LAST_CODE and (not os.path.exists(path) or re.search(r"no tests (were )?(collected|ran)|collected 0 items",
                                                            f"{done.stdout}{done.stderr}", re.I)):
        return 2
    return LAST_CODE


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


def drop_missing_cases(record, root):
    with open(record, encoding="utf-8") as handle:
        text = handle.read()
    try:
        entries = mutation_record.chunks(text)
    except mutation_record.MalformedRecord as error:
        raise ValueError(f"{record}: malformed mutation record {error.header!r}")
    kept = []
    for raw, fields in entries:
        target = re.search(r"TESTS=(\S+?)::(?:\w+::)*(\w+)", fields.get("command", ""))
        if target:
            try:
                with open(os.path.join(root, target.group(1)), encoding="utf-8") as handle:
                    if not re.search(rf"def {target.group(2)}\b", handle.read()):
                        continue
            except FileNotFoundError:
                continue
        kept.append(raw)
    if "".join(kept) == text:
        return
    with open(record, "w", encoding="utf-8") as handle:
        handle.write("".join(kept))


def mutations_path(ledger_path):
    return mutation_record.of_ledger(ledger_path)


def main(argv):
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
    `retire` ("unpinnable" or "already-holds") with a non-empty `reason_file` retires the step instead, dropping
    the mutation records whose test is gone and appending the matching `unpinnable-step` / `already-holds-step`
    event; it needs a `case`. `pending` and `phase` do not combine.
    Returns 0 ticked; 1 clean negative (the case fails; the reason does not qualify for `retire`; retire with no
    case); 2 no answer (case never ran, bad combination, unreadable ledger, no mutation record for the step's
    go-red control, missing receipt, a ledger left behind, an empty ledger_path -> usage line); 3 nothing to
    tick. Writes the ledger (and its added-steps record) and, for a retirement, events.jsonl and the mutation
    record; stderr as the script prints it.
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
    ran = run_case(case) if case else 0
    if ran == 2:
        complain(f"{matcher}: case {case} never run ({how_ended(LAST_CODE)}): no such file path, no tests ran, or the command could not run: {LAST_COMMAND}")
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
    before = re.search(r"mutation-probe\.sh --before ([0-9a-f]{7,40})", step_line)
    control = re.search(r"the go-red control is (\S+) at ([0-9a-f]+)", step_line)
    if before or control:
        record = mutations_path(ledger_path)
        named = [before.group(1)] if before else [control.group(1), control.group(2)]
        if not os.path.exists(record) or not re.search(
                "^(?:" + "|".join(map(re.escape, named)) + ")$", open(record, encoding="utf-8").read(), re.M):
            complain(f"{record}: no mutation record for the step's go-red control")
            return 2
    if tests_frozen.is_diff_checked(step_line):
        refusal = ledger.receipt_refusal(ledger_path)
        if refusal:
            complain(f"{ledger_path}: {refusal}")
            return 2
    left = ledger.rewrite_ledger(ledger_path, new)
    if left is None:
        tick_added(ledger_path, step_line)
    if left is None and reason_file:
        step = step_line
        reason = next((l[7:].strip() for l in reason_text.splitlines()
                       if l.startswith("REASON:") and l[7:].strip()), "")
        tdd_parent = os.path.dirname(os.path.dirname(os.path.abspath(ledger_path)))
        mutations = mutations_path(os.path.abspath(ledger_path))
        if os.path.exists(mutations):
            try:
                drop_missing_cases(mutations, tdd_parent)
            except ValueError as error:
                complain(str(error))
                return 2
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
