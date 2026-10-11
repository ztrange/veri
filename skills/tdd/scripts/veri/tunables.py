"""The one reader of VERI_* tunables."""
import math
import os
import re

STOP_TIMEOUT_MAX = 2 ** 31 - 1


def read(name, default=""):
    return os.environ.get(name, default)


def environment():
    return dict(os.environ)


def with_values(**values):
    return dict(os.environ, **values)


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


TABLE = {
    "VERI_CONDUCTOR_CTX_BUDGET": tokens,
    "VERI_CONDUCTOR_STOP_TIMEOUT": stop_timeout,
    "VERI_KILL_POLL": kill_poll,
}
