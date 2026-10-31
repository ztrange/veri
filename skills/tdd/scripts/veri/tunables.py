"""The one reader of VERI_* tunables."""
import math
import os
import re

STOP_TIMEOUT_MAX = 100000000


def read(name, default="", unless_empty=None):
    value = os.environ.get(name, default)
    return value if value or unless_empty is None else unless_empty


def pop(name, default=""):
    return os.environ.pop(name, default)


def environment():
    return dict(os.environ)


def with_values(**values):
    return dict(os.environ, **values)


def without(name):
    return {k: v for k, v in os.environ.items() if k != name}


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


def kill_poll(raw):
    if not re.fullmatch(r"[0-9]+(\.[0-9]+)?", raw):
        raise ValueError
    return float(raw)


class Tunable:
    def __init__(self, parse, default, must_be):
        self.parse, self.default, self.must_be = parse, default, must_be

    def __call__(self, raw):
        return self.parse(raw)


TABLE = {
    "VERI_CONDUCTOR_CTX_BUDGET": Tunable(tokens, "120000", "a whole number of tokens"),
    "VERI_CONDUCTOR_STOP_TIMEOUT": Tunable(stop_timeout, "10", "a positive number of seconds"),
    "VERI_KILL_POLL": Tunable(kill_poll, "0.1", "a non-negative number"),
}


def resolve(name):
    """(value, None), or (None, (raw, must_be)) when the environment holds a bad value."""
    entry = TABLE[name]
    raw = read(name, unless_empty=entry.default)
    try:
        return entry(raw), None
    except ValueError:
        return None, (raw, entry.must_be)
