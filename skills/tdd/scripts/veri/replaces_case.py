"""The named cases and their suite, parsed from a replaces-case step."""
import re

from ledger import trailing_markers

REPLACES_MARK = "⟦replaces-case⟧"
_START = re.compile(r"\breplaces (?=['\"`])")
_SUITE = re.compile(r" in ([\w./-]+\.test\.sh)")


def is_replaces_case_step(step):
    return step.startswith(REPLACES_MARK) or REPLACES_MARK in trailing_markers(step)


def parse(step):
    start = _START.search(step)
    if start is None:
        return None
    suite = _SUITE.search(step, start.end())
    if suite is None:
        return None
    quote = step[start.end()]
    region = step[start.end() + 1:suite.start()]
    assert region.endswith(quote)
    names = re.split(re.escape(quote) + "(?:, | and )" + re.escape(quote), region[:-1])
    return names, suite.group(1)
