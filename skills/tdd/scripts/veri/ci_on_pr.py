"""Whether CI runs on pull requests here: the one reader of VERI_CI_ON_PR, of CLAUDE.md's `veri: ci on pr:` line,
and of the workflows in the current directory."""
import json
import os

import detect_test_command
import tunables

WORKFLOWS = ".github/workflows"
WORKFLOW_SUFFIXES = (".yml", ".yaml")
ON_KEYS = ("on:", '"on":', "'on':")


def trigger_lines(text):
    indent = None
    for line in text.splitlines():
        if not line.strip():
            continue
        depth = len(line) - len(line.lstrip(" "))
        if indent is not None and depth > indent:
            yield line
            continue
        indent = depth if line.lstrip(" ").startswith(ON_KEYS) else None
        if indent is not None:
            yield line


def pull_request_trigger(text):
    """True when a workflow's text holds a pull_request trigger, False when it was read in full and holds none (a JSON
    mapping, or a block YAML whose `on:` block was found), None when it was not read: no `on` key found, so a caller
    fails closed."""
    try:
        document = json.loads(text)
    except ValueError:
        document = None
    if isinstance(document, dict):
        return "pull_request" in json.dumps(document["on"]) if "on" in document else None
    lines = list(trigger_lines(text))
    return any("pull_request" in line for line in lines) if lines else None


def line_answer(root="."):
    try:
        detect_test_command.answer_from_file(os.path.join(root, "CLAUDE.md"), b"veri: ci on pr:")
    except FileNotFoundError:
        return ""
    except detect_test_command.Answer as found:
        return found.command.decode()
    return ""


def declared(root="."):
    """VERI_CI_ON_PR as set, else the `veri: ci on pr:` line of root's CLAUDE.md: `0`, `1`, or the empty string when
    neither says; a ValueError carrying the one-line refusal on anything else."""
    raw = tunables.read("VERI_CI_ON_PR")
    if raw not in ("", "0", "1"):
        raise ValueError("VERI_CI_ON_PR '%s' is not 0 or 1" % raw)
    if raw:
        return raw
    raw = line_answer(root)
    if raw not in ("", "0", "1"):
        raise ValueError("'veri: ci on pr: %s' in CLAUDE.md is not 0 or 1" % raw)
    return raw


def triggers_on_pull_request():
    if not os.path.isdir(WORKFLOWS):
        return False
    for name in os.listdir(WORKFLOWS):
        if not name.endswith(WORKFLOW_SUFFIXES):
            continue
        with open(os.path.join(WORKFLOWS, name)) as workflow:
            if pull_request_trigger(workflow.read()) is not False:
                return True
    return False


def runs_on_pull_requests():
    """True when declared() says 1 or, empty, a workflow of the current directory triggers on pull_request. ValueError as declared()."""
    raw = declared()
    return raw == "1" or not raw and triggers_on_pull_request()
