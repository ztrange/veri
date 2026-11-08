"""tick-ledger.sh's tick, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import subprocess
import sys

import event
import ledger
import tests_frozen
from add_ledger_step import added_file
from build_verify_prompt import INTERFACE_PHASES

RETIRED_MARK = " ⟂ retired unpinnable"
USAGE = "usage: tick-ledger.sh [--refactor-pending | --phase <phase> | --phase-owed <phase> | --unpinnable <reason-file> | --already-holds <reason-file>] [--case <id>] <ledger-file> <matcher> (--unpinnable and --already-holds drop every mutation record whose named test is absent from the tree)"


def complain(message):
    print(f"tick-ledger.sh: {message}", file=sys.stderr)


def run_case(case):
    return subprocess.run(["make", "test", f"TESTS={case}"]).returncode


def changed_index(text, new):
    return next(i for i, (old, line) in enumerate(zip(text.split("\n"), new.split("\n"))) if old != line)


def changed_line(text, new):
    return new.split("\n")[changed_index(text, new)]


def tick_added(path, step_line):
    target = ledger.STEP_RE.fullmatch(step_line).group(4).split(" ⟂ ", 1)[0]
    record = added_file(path)
    try:
        with open(record, "rb") as handle:
            lines = handle.read().decode(errors="surrogateescape").split("\n")
    except FileNotFoundError:
        return
    for i, line in enumerate(lines):
        match = ledger.STEP_RE.fullmatch(line)
        if match and match.group(2) == " " and match.group(4) == target:
            lines[i] = f"{match.group(1)}[x]{line[match.end(2) + 1:]}"
            with open(record, "wb") as handle:
                handle.write("\n".join(lines).encode(errors="surrogateescape"))
            return


def drop_missing_cases(record, root):
    with open(record, encoding="utf-8") as handle:
        text = handle.read()
    kept, i = [], 0
    while i < len(text):
        start, fields = i, {}
        while i < len(text) and text[i] != "\n":
            end = text.index("\n", i)
            try:
                name, size = text[i:end].split()
                int(size)
            except ValueError:
                raise ValueError(f"{record}: malformed mutation record {text[i:end]!r}")
            fields[name] = text[end + 1:end + 1 + int(size)]
            i = end + 2 + int(size)
        while i < len(text) and text[i] == "\n":
            i += 1
        target = re.search(r"TESTS=(\S+?)::(?:\w+::)*(\w+)", fields.get("command", ""))
        if target:
            try:
                with open(os.path.join(root, target.group(1)), encoding="utf-8") as handle:
                    if not re.search(rf"def {target.group(2)}\b", handle.read()):
                        continue
            except FileNotFoundError:
                continue
        kept.append(text[start:i])
    if "".join(kept) == text:
        return
    with open(record, "w", encoding="utf-8") as handle:
        handle.write("".join(kept))


def mutations_path(ledger_path):
    return re.sub(r"\.md$", "", ledger_path) + "-mutations.md"


def main(argv):
    pending, phase, owed, reason_file, case = False, None, False, None, None
    retired_mark, event_name = RETIRED_MARK, "unpinnable-step"
    while True:
        if argv[:1] in (["--already-holds"], ["--unpinnable"]) and len(argv) > 1:
            if argv[0] == "--already-holds":
                retired_mark, event_name = " ⟂ retired already holds", "already-holds-step"
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
    reason_text = ""
    matcher = (argv[1:] or [""])[0]
    if reason_file and not case:
        complain(f"{matcher}: no case is named")
        return 1
    if reason_file:
        with open(reason_file, encoding="utf-8") as handle:
            reason_text = handle.read()
        if event_name == "unpinnable-step" and "stays green" not in reason_text:
            return 1
        if event_name == "already-holds-step" and not any(
            l.startswith("REASON:") and l[7:].strip() for l in reason_text.splitlines()
        ):
            return 1
    if case and run_case(case):
        complain(f"{matcher}: case {case} fails")
        return 1
    if pending and phase:
        complain("--phase and --refactor-pending cannot be combined")
        return 2
    if owed and phase not in ("contract-a", "contract-b"):
        complain(f"--phase-owed {phase}: only a contract phase can be owed")
        return 2
    if not argv or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        text = ledger.read_ledger(argv[0])
    except OSError as error:
        complain(f"{argv[0]}: {error.strerror}")
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
        record = mutations_path(argv[0])
        named = [before.group(1)] if before else [control.group(1), control.group(2)]
        if not os.path.exists(record) or not re.search(
                "^(?:" + "|".join(map(re.escape, named)) + ")$", open(record, encoding="utf-8").read(), re.M):
            complain(f"{record}: no mutation record for the step's go-red control")
            return 2
    if tests_frozen.is_diff_checked(step_line):
        refusal = ledger.receipt_refusal(argv[0])
        if refusal:
            complain(f"{argv[0]}: {refusal}")
            return 2
    left = ledger.rewrite_ledger(argv[0], new)
    if left is None:
        tick_added(argv[0], step_line)
    if left is None and reason_file:
        step = step_line
        reason = next((l[7:].strip() for l in reason_text.splitlines()
                       if l.startswith("REASON:") and l[7:].strip()), "")
        tdd_parent = os.path.dirname(os.path.dirname(os.path.abspath(argv[0])))
        mutations = mutations_path(os.path.abspath(argv[0]))
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
            return tests_frozen.rerecord_earlier(argv[0], ticked_line.split("] ", 1)[1])
        if pending:
            return tests_frozen.rerecord_committed(
                ticked_line.split("] ", 1)[1].removesuffix(ledger.PENDING_MARK),
                os.path.dirname(os.path.dirname(os.path.abspath(argv[0]))))
        return 0
    if left:
        complain(f"left {left} behind")
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
