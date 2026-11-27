"""The one reader of VERI_* tunables."""
import os
import re

import entry


def read(name, default="", unless_empty=None):
    """The raw read: the environment's string, `default` when unset (`unless_empty` also when set but empty).

    For names outside TUNABLES; a name in it is read through `get` or `resolve`."""
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


def read_bytes(name, default=b""):
    return os.environb.get(os.fsencode(name), default)


def claude_bin():
    """The model binary a leaf runs: `CLAUDE_BIN`, `claude` when unset or empty."""
    return read("CLAUDE_BIN") or "claude"


def venv_dir():
    return read("VERI_VENV") or os.path.join(os.environ.get("HOME", ""), ".veri-tools", "venv")


def tokens(raw):
    value = entry.whole_number(raw, 0)
    if value is None:
        raise ValueError
    return value


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


def queue_polls(raw):
    """A whole number of at least 2: one poll's count can never exceed itself."""
    value = entry.whole_number(raw, 2)
    if value is None:
        raise ValueError
    return value


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
gh_driver = choice("auto", "rest", "graphql")
effort_level = choice("low", "medium", "high", "xhigh", "max")


class Tunable:
    """One tunable: its `default` (a string), its `parse` (raises ValueError on a bad value) and its `refusal`.

    `refusal` is what a bad value must be, as the one-line refusal states it; `resolve` serves the entries that state
    one. None means the readers of the name refuse in their own words (or have no shape to refuse)."""

    def __init__(self, parse, default, refusal=None):
        self.parse, self.default, self.refusal = parse, default, refusal

    def __call__(self, raw):
        return self.parse(raw)


# Every tunable, stating its default once. `text` parses anything: the name has no shape to refuse.
TUNABLES = {
    "VERI_CONDUCTOR_CTX_BUDGET": Tunable(tokens, "120000", "a whole number of tokens"),
    "VERI_RESET_GROWTH_CONDUCTOR": Tunable(positive_tokens, "30000", "a whole number of tokens >= 1"),
    "VERI_KILL_POLL": Tunable(kill_poll, "0.1", "a non-negative number"),
    "REVISE_BUDGET": Tunable(tokens, "2", "a whole number"),
    "VERI_COMMENT_CHUNK": Tunable(positive_tokens, "25", "a whole number >= 1"),
    "VERI_REBASED_TIP_SUITE": Tunable(local_or_ci, "local", "local or ci"),
    "VERI_BRANCH_SUITE": Tunable(local_or_ci, "local", "local or ci"),
    "VERI_BASELINE_FULL_TIER": Tunable(baseline_full_tier, "reuse", "run or reuse"),
    "VERI_FULL_TIER_MAX_AGE_DAYS": Tunable(decimal_at_least_one, "7", "a whole number of days >= 1"),
    "VERI_CI_FLAKE_RERUNS": Tunable(tokens, "1", "a whole number"),
    "VERI_TEST_QUALITY_FIXES": Tunable(tokens, "1", "a whole number"),
    "VERI_BRANCH_REPAIRS": Tunable(tokens, "1", "a whole number"),

    "VERI_REFACTOR_BUDGET": Tunable(tokens, "5"),
    "VERI_ISSUE_REFACTOR_BUDGET": Tunable(tokens, "10"),
    "VERI_STEP_GROWTH_PERCENT": Tunable(tokens, "50"),
    "VERI_NO_VERDICT_RETRIES": Tunable(tokens, "1"),
    "VERI_SKILL_EDIT_BUDGET": Tunable(decimal_at_least_one, "3"),
    "VERI_ADJUDICATE_BUDGET": Tunable(tokens, "2"),
    "VERI_DEVIATION_BUDGET": Tunable(tokens, "1"),
    "VERI_SURROUND_MUTANTS": Tunable(positive_tokens, "5", "a whole number >= 1"),
    "VERI_STUCK_RETRIES": Tunable(tokens, "1"),
    "VERI_HEARTBEAT": Tunable(tokens, "180"),
    "VERI_TOOL_IDLE": Tunable(tokens, "600"),
    "VERI_TIMEOUT": Tunable(tokens, "900"),
    "VERI_DISPATCH_RETRY_SLEEP": Tunable(isdigit_seconds, "5"),
    "VERI_QUEUE_POLLS": Tunable(queue_polls, "3"),
    "VERI_CONDUCTOR_TEST_WORKERS": Tunable(positive_tokens, "2"),
    "VERI_TEST_BUDGET_TTL": Tunable(positive_tokens, "3600"),
    "VERI_GH_REFUSAL_RETRIES": Tunable(tokens, "3"),
    "VERI_LABEL": Tunable(text, "ready-for-agent"),
    "VERI_TOOL_RETRY_SLEEP": Tunable(text, "15"),
    "VERI_TOOL_FAST_WAIT": Tunable(text, "900"),
    "VERI_TOOL_SLOW_SLEEP": Tunable(text, "900"),
    "VERI_TOOL_WAIT": Tunable(text, "3600"),
    "VERI_GH_REFUSAL_SLEEP": Tunable(text, "60"),
    "VERI_GH_DRIVER": Tunable(gh_driver, "rest"),
    "VERI_GH_TIMEOUT": Tunable(text, "300"),
    # Set but empty or blank reads as this default too: value redaction cannot be turned off (github.redact).
    "VERI_REDACT_VARS": Tunable(text, "GH_TOKEN GITHUB_TOKEN ANTHROPIC_API_KEY CLAUDE_CODE_OAUTH_TOKEN"),
    "VERI_LEAF_ENV": Tunable(text, ""),
    "VERI_GIT_NETWORK_TIMEOUT": Tunable(text, "600"),
    "VERI_GITHUB_STATUS_URL": Tunable(text, "https://www.githubstatus.com"),
    "VERI_GITHUB_OUTAGE_MIN": Tunable(text, "30"),
    "VERI_GITHUB_STATUS_TIMEOUT": Tunable(text, "15"),
    "VERI_GITHUB_STATUS_POLL": Tunable(text, "300"),
    "VERI_MERGE_LOCK_POLL": Tunable(text, "30"),
    "VERI_MERGE_LOCK_WAIT": Tunable(tokens, "1800"),
    "VERI_FETCH_RETRY_SLEEP": Tunable(text, "1"),
    "VERI_FETCH_RETRIES": Tunable(text, "60"),
    "VERI_MERGE_SETTLE_READS": Tunable(text, "10"),
    "VERI_MERGE_SETTLE_SLEEP": Tunable(text, "3"),
    "VERI_SLICE_COMMITS": Tunable(text, "100"),
    "VERI_CI_RETRY_BACKOFF": Tunable(text, "1"),
    "VERI_CI_NO_RUN_WAIT": Tunable(text, "600"),
    "VERI_CI_HEAD_WAIT": Tunable(text, "600"),
    "VERI_CI_QUEUE_WAIT": Tunable(text, "3600"),
    "VERI_PRIORITY_LABEL": Tunable(text, "priority"),
    "VERI_RECHECK_PERMISSIONS": Tunable(choice("0", "1"), "0"),
    "VERI_AUTHOR_LABEL": Tunable(text, "author-read"),
    "VERI_PAGE_RETRIES": Tunable(text, "3"),
    "VERI_PAGE_RETRY_SLEEP": Tunable(text, "2"),
    "VERI_WORKQUEUE_LOCK_WAIT": Tunable(text, "30"),
    "VERI_MIN_FREE_GB": Tunable(text, "20"),
    "VERI_SKIP_VERIFY": Tunable(text, ""),
    "VERI_STOP_KILL_GRACE": Tunable(text, "5"),
    # Read by DRAFT-PR.md's prose only, as the bound it hands `detach-command.sh wait lint --total`.
    "VERI_LINT_TIMEOUT": Tunable(text, "1800"),
    "VERI_CALLER_DIR": Tunable(text, "."),
    "VERI_SLEEP_GAP": Tunable(text, "900"),
    "VERI_SNAPSHOT_MAX_AGE": Tunable(text, "60"),
    "VERI_WATCH_QUEUE_INTERVAL": Tunable(text, "60"),
    "VERI_WATCH_POLL": Tunable(text, "2"),
    "VERI_DISPATCH_STALL": Tunable(text, "3600"),
    "VERI_DISPATCH_OVERLAP_POLL": Tunable(text, "60"),
    "VERI_STEP_BUDGET": Tunable(text, "12"),
    "VERI_RUN_BUDGET": Tunable(text, "120"),
    "VERI_UNIT_BUDGET": Tunable(text, "10"),
    "VERI_TIME_WARN_RATIO": Tunable(text, "1.5"),
    "VERI_PROFILE_THRESHOLD": Tunable(text, "1"),
    "VERI_MODEL": Tunable(text, ""),
    "VERI_MODEL_DEVELOPER": Tunable(text, "sonnet"),
    "VERI_MODEL_VERIFIER": Tunable(text, "sonnet"),
    "VERI_MODEL_REVISE": Tunable(text, "opus"),
    "VERI_MODEL_REVISE_GREEN": Tunable(text, ""),
    "VERI_EFFORT_VERIFIER": Tunable(effort_level, ""),
    "VERI_MODEL_ADJUDICATOR": Tunable(text, "opus"),
    "VERI_MODEL_CONDUCTOR": Tunable(text, "opus"),
    "VERI_MISSING_REROUTE_BUDGET": Tunable(tokens, "3"),
    "VERI_QUALITY_REPAIRS": Tunable(tokens, "1"),
    "VERI_SETUP_THRESHOLD": Tunable(tokens, "3"),
    "VERI_PLAN_TOUCHING_CASES": Tunable(tokens, "100"),
    "VERI_TEST_LOCK": Tunable(text, ""),
    "VERI_PYTEST_WORKERS": Tunable(text, ""),
    "VERI_PYTEST_IDLE": Tunable(text, "1200"),
    "VERI_PYTEST_TERM_GRACE": Tunable(text, "5"),
    "VERI_PYTEST_LEGS": Tunable(text, ""),
    "VERI_PYTEST_WAITERS": Tunable(text, ""),
    "VERI_TEST_CEILING_FILE": Tunable(text, ""),
    "VERI_TEST_CAP_FILE": Tunable(text, ""),
    "VERI_TEST_LOAD_FILE": Tunable(text, ""),
    "VERI_TEST_TIMEOUTS_FILE": Tunable(text, ""),
    "VERI_LOAD_WINDOW": Tunable(text, "600"),
    "VERI_TEST_BUDGET_DIR": Tunable(text, ""),
    "VERI_PYCACHE": Tunable(text, ""),
    "VERI_NEW_SKILL": Tunable(text, ""),
    "VERI_PARALLEL": Tunable(text, "1"),
    "VERI_RUN_TIMEOUT": Tunable(text, "14400"),
    "VERI_MAX_ISSUES": Tunable(text, ""),
    "VERI_MACHINE_NAME": Tunable(text, ""),
    "VERI_SELF_UPDATE": Tunable(text, ""),
    "VERI_MUTATION_ADDRESS_DOMAIN": Tunable(text, ""),
    "VERI_SESSION_TRANSCRIPTS": Tunable(text, ""),
}

# Every other VERI_* name read through `read`, `read_bytes` or `pop`, and why it is not a knob: `run state` (veri sets
# it for its own child processes) or `test stand-in` (a test sets it in place of the machine's answer).
NOT_KNOBS = {
    "VERI_AWAKE_CLOCK": "test stand-in",
    "VERI_WALL_CLOCK": "test stand-in",
    "VERI_BASH_MAJOR": "test stand-in",
    "VERI_CI_ON_PR": "test stand-in",
    "VERI_EVENT_STRICT": "test stand-in",
    "VERI_GH_JSON": "test stand-in",
    "VERI_POLL": "test stand-in",
    "VERI_PYTHON_VERSION": "test stand-in",
    "VERI_SELF_UPDATE_FILE": "test stand-in",
    "VERI_ISSUE": "run state",
    "VERI_LEAF_MODEL": "run state",
    "VERI_LEAF_SKIP_PROJECT_CLAUDE_MD": "run state",
    "VERI_LEAF_TOOLS": "run state",
    "VERI_CEILING_RECORD": "run state",
    "VERI_SHIM_DEFAULT_SIGNALS": "run state",
    "VERI_SHIM_SET_COERCE": "run state",
    "VERI_SKILL_CLONE": "run state",
    "VERI_SKILL_COMMIT": "run state",
    "VERI_SKILL_REF": "run state",
    "VERI_SKILL_UNPINNED": "run state",
    "VERI_STATE_LABEL_ISSUE": "run state",
    "VERI_STEP": "run state",
    "VERI_TEST_CMD": "run state",
}

# The entries that state a refusal, which `resolve` serves (test_1313 pins their one-line refusal).
TABLE = {name: entry for name, entry in TUNABLES.items() if entry.refusal}


def default(name):
    """The one default of a tunable named in TUNABLES."""
    return TUNABLES[name].default


def parses(name, raw):
    """Whether `raw` is a value the tunable's parse accepts."""
    try:
        TUNABLES[name](raw)
    except ValueError:
        return False
    return True


def get(name, unless_empty=False):
    """The value of a tunable, its default when unset; `unless_empty` also takes the default for a set-but-empty one.

    The verb for a reader that refuses a bad value in its own words (or none)."""
    fallback = default(name)
    return read(name, fallback, unless_empty=fallback if unless_empty else None)


def get_bytes(name, unless_empty=False):
    """`get`, as the bytes of the environment (a name that is not valid UTF-8 survives); same empty rule."""
    return os.fsencode(get(name, unless_empty=unless_empty))


def is_set(name):
    """Whether `name` is in the environment at all, set-but-empty included: how a retired name is refused."""
    return name in os.environ


def resolve(name):
    """(value, None), or (None, (raw, refusal)) when the environment holds a bad value.

    The verb for a reader that refuses with the table's one line; KeyError for a name that states no refusal."""
    entry = TABLE[name]
    raw = read(name, unless_empty=entry.default)
    try:
        return entry(raw), None
    except ValueError:
        return None, (raw, entry.refusal)
