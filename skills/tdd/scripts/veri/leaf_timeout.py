"""leaf-timeout.sh's derivation, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import pathlib
import sys

import ceiling
import entry
import paths
import run_dir
import tunables

USAGE = "usage: leaf-timeout.sh <baseline-seconds> [refactor | --full <full-seconds> [--reused]]"


def is_whole(text):
    return entry.whole_number(text, 0) is not None


def require_seconds(name, value):
    if not is_whole(value):
        return entry.refuse(f"leaf-timeout: {name} must be a whole number >= 0: {value}", usage=USAGE)
    return 0


class Malformed(Exception):
    """A run's timeout pin holds something other than a whole number of seconds >= 1.
    `path` is the pin file, `text` what it holds (trailing newlines dropped), `not_a_number` whether
    that text is non-empty yet not digits (else it is empty or below 1)."""

    def __init__(self, path, text):
        super().__init__(f"{path} holds '{text}'")
        self.path = path
        self.text = text
        self.not_a_number = bool(text) and entry.whole_number(text, 0) is None


def pin_path(root, issue):
    """The run's timeout pin: `<root>/.tdd/issue-<issue>-timeout`. str, never raises."""
    return run_dir.issue_file(root, issue, "-timeout")


def settled(root, issue):
    """The seconds the run pinned for `issue` under `root`, as the digits written (leading zeros kept),
    or None when no pin file exists. Raises Malformed for a pin that is not a whole number >= 1."""
    path = pin_path(root, issue)
    if not os.path.isfile(path):
        return None
    with open(path) as f:
        text = f.read().rstrip("\n")
    if not valid_pin(text):
        raise Malformed(path, text)
    return text


def valid_pin(text):
    """Whether <text>, trailing newlines dropped, is a timeout pin settled() accepts: a whole number of seconds >= 1."""
    return entry.whole_number(text.rstrip("\n"), 1) is not None


def record(timeout):
    issue = tunables.read("VERI_ISSUE")
    if not issue:
        return
    here = pathlib.Path.cwd()
    root = next((d for d in (here, *here.parents) if (d / ".git").exists()), here)
    os.makedirs(os.path.join(root, ".tdd"), exist_ok=True)
    try:
        with open(pin_path(root, issue), "x") as settled:
            settled.write(f"{timeout}\n")
    except FileExistsError:
        pass


def idle_full_tier():
    """The full tier's idle seconds the test-ceiling record holds, for a skipped baseline whose full-tier time was
    reused rather than run (#4835); 0, so the
    default 900 s, with one stderr line naming that fallback when the record holds none."""
    idle = ceiling.read_idle("all")
    if idle is None:
        print(f"leaf-timeout: baseline skipped and {ceiling.record_path()} records no idle full-tier duration,"
              " so the default 900 s", file=sys.stderr)
        return 0
    return idle


def main(argv):
    override = tunables.read("VERI_TIMEOUT")
    if override:
        if not is_whole(override) or int(override) < 1:
            return entry.refuse(f"leaf-timeout: VERI_TIMEOUT must be a whole number >= 1: {override}")
        print(int(override))
        return 0
    baseline = argv[0] if argv else ""
    code = require_seconds("<baseline-seconds>", baseline)
    if code:
        return code
    if argv[1:2] == ["--full"]:
        full = argv[2] if len(argv) > 2 else ""
        code = require_seconds("<full-seconds>", full)
        if code:
            return code
        reused = argv[3:4] == ["--reused"]
        baseline = idle_full_tier() if reused and int(baseline) == 0 else full
    derived = max(900, int(baseline) * 6)
    if argv[1:2] == ["refactor"]:
        budget = tunables.get("VERI_REFACTOR_BUDGET", unless_empty=True)
        if not is_whole(budget):
            return entry.refuse(f"leaf-timeout: VERI_REFACTOR_BUDGET must be a whole number >= 0: {budget}")
        derived = derived * max(1, int(budget))
    if tunables.read("VERI_ISSUE") and paths.inside_scripts(__file__):
        return entry.refuse("leaf-timeout.sh: type this from the run's worktree,"
                            " not from the skill's own scripts directory")
    record(derived)
    print(derived)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
