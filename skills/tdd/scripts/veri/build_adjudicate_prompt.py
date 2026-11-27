"""build-adjudicate-prompt.sh's prompt builder, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import contextlib
import io
import os
import re
import sys

import ledger
import paths
import run_dir

USAGE = "usage: build-adjudicate-prompt.sh <n> <cause> <exit-code> <stderr-file> <command…>"


def section(doc, title):
    """doc's `### <title>` section, up to the next `###` heading; "" when it has none."""
    match = re.search(r"^### " + re.escape(title) + r"\n(.*?)(?=^### |\Z)", doc, re.M | re.S)
    return match.group(1) if match else ""


def waivable(doc, cause):
    """(rule, purpose) of the *Waivable rules* bullet naming `cause`, its wrapped lines joined; None for none."""
    for rule, named, text in re.findall(r"^- `([^`]+)`: `([^`]+)`(.*(?:\n  .*)*)",
                                        section(doc, "Waivable rules"), re.M):
        if named == cause:
            text = " ".join(text.split())
            purpose = re.search(r"Purpose: (.*?)(?= Resume action:|$)", text)
            return rule, purpose.group(1) if purpose else text
    return None


def main(argv):
    if not argv:
        print(USAGE, file=sys.stderr)
        return 2
    n, cause, exit_code, stderr_file, *command = argv
    doc = os.path.join(paths.scripts_of(__file__), "..", "ADJUDICATE.md")
    with open(doc) as f:
        text = f.read()
    eligible = dict(re.findall(r"^- `([^`]+)`:(.*)$", section(text, "Eligible causes"), re.M))
    waived = waivable(text, cause)
    if cause not in eligible and not waived:
        print(f"build-adjudicate-prompt.sh: cause not eligible: {cause}", file=sys.stderr)
        return 2
    if waived:
        routes, answers = "none", "deviate|bail"
        rule = f"Rule: {waived[0]}\nPurpose: {waived[1]}\n"
    else:
        routes = ", ".join(re.findall(r"`([^`]+)`", eligible[cause])) or eligible[cause].strip()
        answers, rule = "retry|bail|route <token>", ""
    with open(run_dir.ledger(".", n)) as f:
        steps = [line.rstrip("\n") for line in f if line.startswith((ledger.OPEN_STEP, ledger.TICKED_STEP))]
    step = next((s for s in steps if s.startswith(ledger.OPEN_STEP)), steps[-1])
    if cause == "tests-frozen-refused":
        import tests_frozen
        name = step.removeprefix(ledger.OPEN_STEP).strip()
        captured = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
        record = tests_frozen.record_path(name)
        if os.path.exists(record):
            with contextlib.redirect_stdout(captured):
                tests_frozen.diff(record, name)
            captured.flush()
            rule += captured.buffer.getvalue().decode()
    with open(stderr_file) as f:
        stderr = "".join(f.readlines()[-50:])
    print(
        f"Cause: {cause}\nCommand: {' '.join(command)}\nExit code: {exit_code}\nRoutes: {routes}\n{rule}"
        f"Stderr:\n{stderr}\nStep: {step}\n\n"
        f"End with one final line: ADJUDICATION: {answers} — <reason>"
    )
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
