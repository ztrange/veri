"""ci-flake.sh's flake check of a red CI run: each test target its failed log names, rerun alone."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import re
import sys

import ci_marks
import event
import github
import rerun_alone
import tunables

USAGE = "usage: ci-flake.sh <n> <head-sha> <run-id> '<alone-cmd>' <log-file>"
# One line of `gh run view --log-failed`: job, step and timestamp before the runner's own text.
GH_LINE = re.compile(r"^[^\t]*\t[^\t]*\t\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z ?(.*)$")


def runner_text(log):
    """The runner's own output in a `--log-failed` log: each line without gh's prefix."""
    lines = []
    for line in log.splitlines():
        found = GH_LINE.match(line)
        if found:
            lines.append(found.group(1).lstrip("\ufeff"))
    return "\n".join(lines) + "\n"


def passes_alone(alone_cmd, target):
    cmd = alone_cmd if '"$1"' in alone_cmd else alone_cmd + ' "$1"'
    return github.bounded_group(["sh", "-c", cmd, "sh", target], limit_name="VERI_TIMEOUT").returncode == 0


def main(argv):
    if len(argv) != 5:
        print(USAGE, file=sys.stderr)
        return 2
    n, head, run_id, alone_cmd, log_file = argv
    with open(log_file, errors="replace") as log:
        targets = rerun_alone.named_targets(runner_text(log.read()))
    still_red = [t for t in targets if not passes_alone(alone_cmd, t)]
    if still_red or not targets:
        return 1
    github.gh_run_rerun_failed(run_id)
    ci_marks.fresh_window("", head)
    event.mark(".", event.context(tunables.with_values(VERI_ISSUE=n)), "ci-rerun",
               ["head=" + head, "run=" + run_id, "files=" + ",".join(targets)])
    print("\n".join(targets))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
