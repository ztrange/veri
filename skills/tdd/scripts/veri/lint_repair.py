"""lint-repair.sh's composing of a red lint's repair step, run in-process (#4123, PRD 032.10 LR1).

The step text is committed, pushed and mirrored to the issue, so the finding line goes through
run_records.redact_local (this machine's paths, host and account) and is capped by characters, never bytes. The lint
command is read here, from the repo's CLAUDE.md as detect-test-command.sh --tier lint prints it, since a conductor
Bash call shares no variable with an earlier one.
"""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import detect_test_command
import run_records

USAGE = "usage: lint-repair.sh step < <lint-output>"
FINDING_CHARS = 200
NO_OUTPUT = "the command printed nothing"


def main(argv):
    if argv != ["step"]:
        sys.stderr.write(USAGE + "\n")
        return 2
    command = detect_test_command.resolved("lint", "", ".")
    if command is None:
        return 3
    data = getattr(sys.stdin, "buffer", sys.stdin).read()
    text = data.decode("utf-8", "replace") if isinstance(data, bytes) else data
    finding = next((line.strip() for line in text.split("\n") if line.strip()), NO_OUTPUT)
    cwd = os.getcwd()
    finding = run_records.redact_local(finding, cwd)[:FINDING_CHARS]  # redacted first: a cut leaves no path fragment
    step = run_records.redact_local(f"make `{command.decode('utf-8', 'replace')}` pass: ", cwd) + finding
    sys.stdout.buffer.write((step + " ⟦diff-checked⟧ ⟦lint-repair⟧\n").encode())
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
