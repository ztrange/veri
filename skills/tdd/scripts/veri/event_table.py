"""Every event veri emits and the keys it carries: the one table the journal page, the writers and the fixture are checked against.

`EVENTS` maps an event name to its keys, space-separated, in the order the emitter gives them; a key ending in `?` is
optional, every other key is required. Adding an event or a key is one line: the event's entry. The keys every line
carries from the run context (`COMMON`) are in no entry. It imports no veri module, so it can be read alone.

Interface:
  keys(event)       the event's keys in order, () for an event with none; KeyError for an event the table does not hold
  required(event)   the subset of those keys every line of the event carries
"""

COMMON = ("ts", "awake", "issue", "actor", "phase", "step", "event", "attempt", "skill_commit")

EVENTS = {
    "adjudicated": "cause outcome reason",
    "already-holds-step": "step reason",
    "bail": "cause classification? suites?",
    "comment": "kind url",
    "conductor-restart": "growth knob",
    "conductor-start": "pid started",
    "criterion-unticked": "matcher",
    "diff-leaf-deviation": "leaf base head commits",
    "done": "pr wall_seconds? awake_seconds? lane?",
    "exit": "status cause? secs",
    "grading": "unit verdict failing cost_usd id",
    "launch": "name cmd model",
    "launch-refused": "name reason",
    "merged": "pr tag message",
    "mutation-record-restored": "name file",
    "pin": "",
    "pin-retired": "reason",
    "plan": "steps",
    "prediction-diverged": "",
    "preflight-refused": "check cause classification detail?",
    "production-file-restored": "name file",
    "prose-owed-waived": "unit step",
    "push-failed": "error attempts",
    "push-rejected": "remote_sha error",
    "rebase-refresh-retry": "",
    "refactor": "transforms budget stopped pass",
    "relaunch": "cause",
    "report-missing": "name missing",
    "reroute": "case? kind",
    "resume": "",
    "resume-rebase": "from rebased",
    "retry": "cause",
    "revise": "budget",
    "skill-edit-no-author": "unit",
    "skill-repin": "commit",
    "step-added": "anchor added",
    "step-done": "",
    "step-escalated": "anchor at?",
    "step-over-budget": "spent budget",
    "step-split": "anchor added at?",
    "step-start": "",
    "stop": "mode at",
    "structural-pass": "transforms? budget? stopped",
    "suite-flake": "at? files",
    "suite-repair-retired": "",
    "test-run": "tier suites seconds status",
    "tests-frozen-refused": "exit reason",
    "unpinnable-missing": "step",
    "unpinnable-step": "step reason",
    "usage": "duration_ms duration_api_ms num_turns total_cost_usd input_tokens output_tokens cache_read_input_tokens cache_creation_input_tokens model model_usage?",
    "verdict": "verdict reason cause?",
    "verify-pin-skipped": "reason",
    "verify-refactor-skipped": "reason",
}


def _declared(event):
    return EVENTS[event].split()


def keys(event):
    return tuple(key.rstrip("?") for key in _declared(event))


def required(event):
    return {key for key in _declared(event) if not key.endswith("?")}
