"""Every event veri emits and the keys it carries: the one table the journal page, the writers and the fixture are checked against.

`EVENTS` maps an event name to its keys, space-separated, in the order the emitter gives them. Each key is written
`name:format`: a name ending in `?` is optional, every other key is required. The format is one of `FORMATS` or a list
of values in parentheses, `(a|b|c)`; `,empty` after it marks the empty string valid too, and a key without it is
invalid when empty, whatever its format. Adding an event or a key is one line: the event's entry. The keys every line
carries from the run context (`COMMON`) are in no entry; `CONTEXT` declares the formats of its string keys, `ts` and
`awake` being numbers. It imports no veri module, so it can be read alone.

Interface:
  keys(event)       the event's keys in order, () for an event with none; KeyError for an event the table does not hold
  required(event)   the subset of those keys every line of the event carries
  format(event, key)  (format, empty allowed) for a key of `event`, or of the run context (event None or not declaring it);
                      the format is a `FORMATS` name, a tuple of values, or None when the key has none
  valid(event, key, value)  whether `value` (a str) is a valid value of that key
  stated(event, key)  that format in JOURNAL.md's words (`whole`, `one of a, b`, `, or empty` after one that may be)
  declaring(event, key)  the `EVENTS` line to write so that the table declares `key` for `event` (no key: just the event;
                         no event: the `CONTEXT` line)
"""
import json
import re

COMMON = ("ts", "awake", "issue", "actor", "phase", "step", "event", "attempt", "skill_commit")
# whole: decimal digits only; decimal: digits with at most one `.`; url: starts https:// or http://;
# sha: 7 to 40 lowercase hex digits; json: parses as JSON; text: any string.
FORMATS = ("whole", "decimal", "url", "sha", "json", "text")
CONTEXT = ("issue:whole,empty actor:text,empty phase:text,empty step:text,empty event:text attempt:whole,empty"
           " skill_commit:text,empty")

EVENTS = {
    "adjudicated": "cause:(ci-timeout|ci-conflict|pr-ready-failed|report-missing|step-add-refused"
                   "|replaces-report-failed|unreplaced-cases|reconcile-failed"
                   "|criterion-unreadable) outcome:(retry|route|bail|unparsed) reason:text,empty",
    "already-holds-step": "step:text reason:text",
    "bail": "cause:(killed-stuck|killed-external|report-missing|no-verdict|reconcile-failed|ci-timeout|ci-conflict"
            "|step-add-refused|replaces-report-failed|criterion-unreadable|setup-failed|preflight-refused|pr-ready-failed|rerecord-failed"
            "|revise-exhausted|revise-impossible|untestable-criterion|step-too-big|rebase-unresolved|uncovered|ci-red"
            "|suite-red|rebased-tip-red|unreplaced-cases|needs-user|step-added-off-route|fixture-owed"
            "|missing-reroutes-exhausted|repair-reroutes-exhausted|graded-edit-outside-skill-edit|unpinnable-missing"
            "|repin-failed|skill-edit-refused|prep-owed|no-seam|surround-owed|unwired|surround-short|tidy-first-owed) classification?:(process|system) suites?:text failed?:text",
    "case-timeout": "nodeid:text workers:whole",
    "ci-flake": "head:sha run:whole files:text",
    "ci-rerun": "head:sha run:whole files:text",
    "comment": "kind:(step-done|red|verify-red|green|verify-green|refactor|verify-refactor|revise|verify-revised|plan|verify-plan"
               "|resuming|done|bailed|stopped) url:url",
    "conductor-restart": "growth:whole knob:whole",
    "conductor-start": "pid:whole started:text,empty",
    "core-wait": "seconds:whole",
    "criterion-unticked": "matcher:text,empty",
    "diff-leaf-deviation": "leaf:text base:sha head:sha commits:whole",
    "done": "pr:url wall_seconds?:whole awake_seconds?:whole lane?:text",
    "exit": "status:whole cause?:text secs:whole name?:text",
    "grading": "unit:text verdict:(PASS|REJECT) failing:text,empty cost_usd:decimal id:text effort:text",
    "launch": "name:text cmd:text model:text,empty effort?:(low|medium|high|xhigh|max)",
    "launch-refused": "name:text reason:text",
    "lint": "exit:whole",
    "merged": "pr:url tag:text,empty message:text,empty",
    "metrics-cut": "pr:url wall_seconds?:whole awake_seconds?:whole lane?:text",
    "mutation-record-restored": "name:text file:text",
    "pin": "",
    "pin-retired": "reason:text",
    "record-refreshed": "stage:(green-half|refactor-half|reroute|revise|step-close) key:text old:text,empty new:text",
    "plan": "steps:whole",
    "prediction-diverged": "",
    "preflight-refused": "check:text cause:(preflight-refused) classification:(system) detail?:text",
    "production-file-restored": "name:text file:text",
    "prose-owed-waived": "unit:text step:text",
    "push-failed": "error:text,empty attempts:whole",
    "push-rejected": "remote_sha:sha,empty error:text,empty",
    "rebase-refresh-retry": "",
    "red-setup": "count:whole what:text,empty",
    "refactor": "transforms:whole budget:whole"
                " stopped:(nothing-left|budget|malformed|nothing-structural|structural-owed) pass:whole",
    "relaunch": "cause:(tree-change|no-verdict)",
    "report-missing": "name:text missing:(SUITE)",
    "reroute": "case?:text kind:(red|repair|supersede|supersede-diff|fixture|missing|later|prep) at?:(exhausted)",
    "resume": "",
    "resume-rebase": "from:sha rebased:sha",
    "retry": "cause:text name?:text",
    "revise": "budget:whole",
    "skill-edit-no-author": "unit:text",
    "skill-repin": "commit:sha",
    "snapshot-changed": "path:text",
    "stage-end": "stage:(preflight|baseline|push|draft-pr|full-suite|ready|ci-wait|plan|refactor-loop|structural|rebase|merge|release) status:whole secs:whole",
    "stage-start": "stage:(preflight|baseline|push|draft-pr|full-suite|ready|ci-wait|plan|refactor-loop|structural|rebase|merge|release)",
    "step-added": "anchor?:text added?:whole",
    "step-done": "",
    "step-escalated": "anchor:text at?:(over-budget)",
    "step-over-budget": "spent:decimal budget:decimal",
    "step-split": "anchor:text added:whole at?:(over-budget|exhausted)",
    "step-reworded": "from:text to:text",
    "step-start": "",
    "stop": "mode:(at-ledger|at-leaf|now) at:(unplanned|planned|green|step-done|unsettled)",
    "structural-pass": "transforms?:whole budget?:whole stopped:(candidates-done|budget-spent|nothing-structural)",
    "suite-flake": "at?:(suite-repair|resume) files:text",
    "suite-repair-retired": "",
    "test-run": "tier:(fast|changed|affected|all|target) suites:text,empty seconds:whole status:whole",
    "test-stretch": "tier:(fast|all) seconds:whole idle:whole",
    "tidy-first": "anchor:text refactoring:text",
    "tests-frozen-refused": "exit:(1|2) reason:text,empty",
    "unpinnable-missing": "step:text",
    "unpinnable-step": "step:text reason:text,empty",
    "usage": "duration_ms:whole duration_api_ms:whole num_turns:whole total_cost_usd:decimal input_tokens:whole"
             " output_tokens:whole cache_read_input_tokens:whole cache_creation_input_tokens:whole model:text,empty"
             " model_usage?:json first_turn_cache_creation_input_tokens?:whole first_turn_cache_read_input_tokens?:whole"
             " first_turn_input_tokens?:whole name?:text",
    "verdict": "verdict:(PASS|REJECT|malformed) reason:text,empty cause?:(no-verdict) check?:(1|2|3|4|5) tree?:sha name?:text",
    "verify-diff-skipped": "reason:(switched-off)",
    "verify-green-skipped": "reason:(switched-off)",
    "verify-pin-skipped": "reason:(switched-off)",
    "verify-red-skipped": "reason:(switched-off)",
    "verify-refactor-skipped": "reason:(nothing-landed|switched-off)",
}
CONTEXT_KEYS = tuple(token.partition(":")[0] for token in CONTEXT.split())


def _declared(event):
    return EVENTS[event].split()


def keys(event):
    return tuple(token.partition(":")[0].rstrip("?") for token in _declared(event))


def required(event):
    return {token.partition(":")[0] for token in _declared(event) if not token.partition(":")[0].endswith("?")}


def _parse(text):
    empty = text.endswith(",empty")
    form = text.removesuffix(",empty")
    if form.startswith("(") and form.endswith(")"):
        return tuple(form[1:-1].split("|")), empty
    return form or None, empty


def format(event, key):
    """(format, empty allowed) of `key`: the event's own declaration, else the run context's; KeyError for neither."""
    tokens = _declared(event) if event in EVENTS else []
    for token in tokens + CONTEXT.split():
        name, _, form = token.partition(":")
        if name.rstrip("?") == key:
            return _parse(form)
    raise KeyError(key)


PATTERNS = {"whole": r"[0-9]+", "decimal": r"(?=.*[0-9])[0-9]*\.?[0-9]*", "url": r"https?://.*", "sha": r"[0-9a-f]{7,40}",
            "text": r".*"}


def _matches(form, value):
    if isinstance(form, tuple):
        return value in form
    if form == "json":
        try:
            json.loads(value)
        except ValueError:
            return False
        return True
    return form in PATTERNS and re.fullmatch(PATTERNS[form], value, re.S) is not None


def valid(event, key, value):
    """Whether `value` is a valid value of `key` (see format): the empty string only where the table allows it."""
    form, empty = format(event, key)
    return empty if value == "" else _matches(form, value)


def stated(event, key):
    """The key's format in JOURNAL.md's words: `whole`, `one of a, b`, … with `, or empty` when it may be empty."""
    form, empty = format(event, key)
    return ("one of " + ", ".join(form) if isinstance(form, tuple) else str(form)) + (", or empty" if empty else "")


def declaring(event, key):
    """The one `EVENTS` line that declares `key` (optional) for `event`, the event's line grown, or a new one."""
    if event is None:
        return f'CONTEXT = "{CONTEXT}"'
    declared = _declared(event) if event in EVENTS else []
    return f'"{event}": "{" ".join(declared + [key + "?:text"] if key else declared)}",'
