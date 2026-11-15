"""The one reader of VERI_* tunables."""
import math
import os
import re

STOP_TIMEOUT_MAX = 100000000


def read(name, default="", unless_empty=None):
    value = os.environ.get(name, default)
    return value if value or unless_empty is None else unless_empty


def lane_of(opt_in):
    """The lane an opt-in label names (`ready-for-agent:mu` -> `mu`), None for a plain one."""
    return opt_in.rpartition(":")[2] if ":" in opt_in else None


def taken_label(opt_in):
    return "taken:" + (lane_of(opt_in) or "main")


def pop(name, default=""):
    return os.environ.pop(name, default)


def environment():
    return dict(os.environ)


def with_values(**values):
    return dict(os.environ, **values)


def without(name):
    env = with_values()
    env.pop(name, None)
    return env


def read_bytes(name, default=b""):
    return os.environb.get(os.fsencode(name), default)


def venv_dir():
    return read("VERI_VENV") or os.path.join(os.environ.get("HOME", ""), ".veri-tools", "venv")


def stop_timeout(raw):
    value = float(raw)
    if not math.isfinite(value) or value <= 0 or value > STOP_TIMEOUT_MAX:
        raise ValueError
    return value


def tokens(raw):
    if not re.fullmatch(r"[0-9]+", raw):
        raise ValueError
    return int(raw)


def positive_tokens(raw):
    if tokens(raw) < 1:
        raise ValueError
    return int(raw)


def kill_poll(raw):
    if not re.fullmatch(r"[0-9]+(\.[0-9]+)?", raw):
        raise ValueError
    return float(raw)


def text(raw):
    return raw


def isdigit_seconds(raw):
    """str.isdigit, which accepts what int() refuses ('²'); returns the string so no int() runs here."""
    if not raw.isdigit():
        raise ValueError
    return raw


def decimal_at_least_one(raw):
    if not (raw.isdecimal() and int(raw) >= 1):
        raise ValueError
    return int(raw)


def choice(*allowed):
    def parse(raw):
        if raw not in allowed:
            raise ValueError
        return raw

    return parse


local_or_ci = choice("local", "ci")
baseline_full_tier = choice("run", "reuse")


class Tunable:
    def __init__(self, parse, default, must_be):
        self.parse, self.default, self.must_be = parse, default, must_be

    def __call__(self, raw):
        return self.parse(raw)


TABLE = {
    "VERI_CONDUCTOR_CTX_BUDGET": Tunable(tokens, "120000", "a whole number of tokens"),
    "VERI_RESET_GROWTH_CONDUCTOR": Tunable(positive_tokens, "70000", "a whole number of tokens >= 1"),
    "VERI_CONDUCTOR_STOP_TIMEOUT": Tunable(stop_timeout, "10", "a positive number of seconds"),
    "VERI_KILL_POLL": Tunable(kill_poll, "0.1", "a non-negative number"),
    "REVISE_BUDGET": Tunable(tokens, "2", "a whole number"),
    "VERI_COMMENT_CHUNK": Tunable(positive_tokens, "25", "a whole number >= 1"),
    "VERI_REBASED_TIP_SUITE": Tunable(local_or_ci, "local", "local or ci"),
    "VERI_BRANCH_SUITE": Tunable(local_or_ci, "local", "local or ci"),
    "VERI_BASELINE_FULL_TIER": Tunable(baseline_full_tier, "reuse", "run or reuse"),
}


# Tunables whose readers keep their own refusal text, so they are not in TABLE (test_1313 pins
# TABLE's one-line refusal). A reader asks `get`/`default`/`parses` and carries no literal default.
# `text` parses anything: the name has no shape to refuse, or its readers disagree on one (see
# VERI_NO_VERDICT_RETRIES, which verify.py and grade_prose.py parse differently).
DEFAULTED = {
    "VERI_REFACTOR_BUDGET": Tunable(tokens, "5", "a whole number >= 0"),
    "VERI_ISSUE_REFACTOR_BUDGET": Tunable(tokens, "10", "a whole number >= 0"),
    "VERI_STEP_GROWTH": Tunable(tokens, "5", "a whole number >= 0"),
    "VERI_NO_VERDICT_RETRIES": Tunable(text, "1", "a non-negative integer"),
    "VERI_SKILL_EDIT_BUDGET": Tunable(decimal_at_least_one, "3", "a whole number >= 1"),
    "VERI_ADJUDICATE_BUDGET": Tunable(tokens, "2", "a non-negative whole number"),
    "VERI_STUCK_RETRIES": Tunable(tokens, "1", "a number"),
    "VERI_HEARTBEAT": Tunable(tokens, "180", "a number"),
    "VERI_TOOL_IDLE": Tunable(tokens, "600", "a number"),
    "VERI_TIMEOUT": Tunable(tokens, "900", "a number"),
    "VERI_DISPATCH_RETRY_SLEEP": Tunable(isdigit_seconds, "5", "a whole number of seconds"),
    "VERI_GH_REFUSAL_RETRIES": Tunable(tokens, "3", "a whole number"),
    "VERI_LABEL": Tunable(text, "ready-for-agent", "a label"),
    "VERI_MODEL": Tunable(text, "", "a model id or alias"),
    "VERI_MODEL_DEVELOPER": Tunable(text, "sonnet", "a model id or alias"),
    "VERI_MODEL_VERIFIER": Tunable(text, "sonnet", "a model id or alias"),
    "VERI_MODEL_REVISE": Tunable(text, "opus", "a model id or alias"),
    "VERI_MODEL_ADJUDICATOR": Tunable(text, "opus", "a model id or alias"),
    "VERI_MODEL_CONDUCTOR": Tunable(text, "opus", "a model id or alias"),
}


def entry_of(name):
    return TABLE[name] if name in TABLE else DEFAULTED[name]


def default(name):
    """The one default of a tunable named in TABLE or DEFAULTED."""
    return entry_of(name).default


def parses(name, raw):
    """Whether `raw` is a value the tunable's parse accepts."""
    try:
        entry_of(name)(raw)
    except ValueError:
        return False
    return True


def get(name, unless_empty=False):
    """The value of a tunable, its default when unset; `unless_empty` also takes the default for a set-but-empty one."""
    fallback = default(name)
    return read(name, fallback, unless_empty=fallback if unless_empty else None)


def set_but_empty(name):
    return name in os.environ and not os.environ[name]


def resolve(name):
    """(value, None), or (None, (raw, must_be)) when the environment holds a bad value."""
    entry = TABLE[name]
    raw = read(name, unless_empty=entry.default)
    try:
        return entry(raw), None
    except ValueError:
        return None, (raw, entry.must_be)
