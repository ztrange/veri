"""Whether CI runs on pull requests here: the one reader of VERI_CI_ON_PR, and of the workflows in the current directory."""
import os

import tunables

WORKFLOWS = ".github/workflows"


def trigger_lines(text):
    indent = None
    for line in text.splitlines():
        if not line.strip():
            continue
        depth = len(line) - len(line.lstrip(" "))
        if indent is not None and depth > indent:
            yield line
            continue
        indent = depth if line.lstrip(" ").startswith("on:") else None
        if indent is not None:
            yield line


def declared():
    """VERI_CI_ON_PR as set: `0`, `1`, or the empty string when unset or empty; a ValueError carrying the one-line refusal on anything else."""
    raw = tunables.read("VERI_CI_ON_PR")
    if raw not in ("", "0", "1"):
        raise ValueError("VERI_CI_ON_PR '%s' is not 0 or 1" % raw)
    return raw


def triggers_on_pull_request():
    if not os.path.isdir(WORKFLOWS):
        return False
    for name in os.listdir(WORKFLOWS):
        with open(os.path.join(WORKFLOWS, name)) as workflow:
            if any("pull_request" in line for line in trigger_lines(workflow.read())):
                return True
    return False


def runs_on_pull_requests():
    """True when the variable says 1 or, unset, a workflow of the current directory triggers on pull_request. ValueError as declared()."""
    raw = declared()
    return raw == "1" or not raw and triggers_on_pull_request()
