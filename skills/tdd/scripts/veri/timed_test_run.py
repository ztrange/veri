"""timed-test-run.sh's command run, its report in place of the raw output and its one test-run event, run in-process.

The report is a declared quiet command's own output, a foreign tree's changed run's last TAIL lines, else the bounded
report."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import subprocess
import sys
import time

import ceiling
import entry
import event
import run_line
import tunables

TIERS = ("fast", "changed", "all", "target")
USAGE = "usage: timed-test-run.sh <tier> <suites> <cmd> [args …]\n"
CASES = 10
TAIL = 20
WIDTH = 300
SUMMARY = re.compile(r"^=* ?(.*\d+ (?:passed|failed|errors?)\b.*) in [0-9.]+s\b.*$")


def report(tier, code, seconds, output, path):
    """The bounded report that stands in for the output: one counts line, the first CASES failing cases, the cut, the path."""
    lines = output.decode(errors="replace").splitlines()
    summaries = [match.group(1) for match in map(SUMMARY.match, lines) if match]
    if summaries:
        found = dict((word.rstrip("s"), number) for number, word in re.findall(r"(\d+) (passed|failed|errors?)\b",
                                                                                summaries[-1]))
        counts = ", ".join(f"{found.get(word, '0')} {word}" for word in ("passed", "failed", "error"))
    else:
        counts = "counts not found"
    failing = [line[:WIDTH] for line in lines if line.startswith(("FAILED ", "ERROR "))]
    text = [f"timed-test-run.sh: tier {tier}, exit {code}, {seconds}s, {counts}", *failing[:CASES]]
    if len(failing) > CASES:
        text.append(f"\u2026 {len(failing) - CASES} more failing cases cut")
    return "\n".join(text + [f"full output: {os.path.abspath(path)}"]) + "\n"


def tail(tier, code, seconds, output, path):
    """A foreign tree's changed run: one header line, at most the output's last TAIL lines, the path."""
    lines = output.decode(errors="replace").splitlines()[-TAIL:]
    text = [f"timed-test-run.sh: tier {tier}, exit {code}, {seconds}s", *lines]
    return "\n".join(text + [f"full output: {os.path.abspath(path)}"]) + "\n"


def main(argv):
    if len(argv) < 3 or not argv[0] or not argv[2]:
        return entry.refuse(usage=USAGE)
    tier, suites, command = argv[0], argv[1], argv[2:]
    if tier not in TIERS:
        return entry.refuse(f"timed-test-run.sh: tier {tier!r} is not one of {', '.join(TIERS)}")
    if tier == "changed" and command[:2] == ["make", "test"] and not any(a.startswith("TESTS=") for a in command[2:]):
        return entry.refuse("timed-test-run.sh: changed tier refuses 'make test' naming no TESTS= suites")
    started = int(time.time())
    top = event.toplevel()
    runs = os.path.join(top, ".tdd", "test-runs")
    os.makedirs(runs, exist_ok=True)
    path = os.path.join(runs, f"{started}-{tier}-{os.getpid()}.log")
    with open(path, "wb") as log:
        try:
            code = subprocess.call(command, stdout=log, stderr=subprocess.STDOUT)
        except FileNotFoundError:
            code = 127
        except PermissionError:
            code = 126
    if code < 0:
        code = 128 - code
    ended = int(time.time())
    quiet = run_line.quiet_prefix(top or ".")
    with open(path, "rb") as log:
        if quiet and command[:len(quiet)] == quiet:
            sys.stdout.buffer.write(log.read())
            sys.stdout.flush()
            if code == 2:
                sys.stdout.write("timed-test-run.sh: the quiet test command broke the run (exit 2): no test answer\n")
        elif tier == "changed" and not run_line.own_tree(top or "."):
            sys.stdout.write(tail(tier, code, ended - started, log.read(), path))
        else:
            sys.stdout.write(report(tier, code, ended - started, log.read(), path))
    event.mark("", event.context(tunables.environment()), "test-run", [f"tier={tier}", f"suites={suites}",
                                                           f"seconds={ended - started}", f"status={code}"], ended)
    if tier in ("fast", "all"):
        idle = ceiling.read_idle(tier)
        if idle is not None and ended - started > 2 * idle:
            event.mark("", event.context(tunables.environment()), "test-stretch",
                       [f"tier={tier}", f"seconds={ended - started}", f"idle={idle}"], ended)
    return code


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
