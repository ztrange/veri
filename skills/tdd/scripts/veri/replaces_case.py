"""The named cases and their suite, parsed from a replaces-case step."""
import re

from ledger import trailing_markers

REPLACES_MARK = "⟦replaces-case⟧"
_REPLACES = r"\breplaces "
_QUOTE = r"['\"`]"
_START = re.compile(_REPLACES + "(?=" + _QUOTE + ")")
_UNQUOTED = re.compile(_REPLACES + "(?!" + _QUOTE + r")\S")
_OTHER_SUITE = re.compile(_REPLACES + "(?=" + _QUOTE + r").*? in ([\w./-]+)")
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
    if not region.endswith(quote):
        return None
    names = re.split(re.escape(quote) + "(?:, | and )" + re.escape(quote), region[:-1])
    return names, suite.group(1)


def unreadable(step):
    start = _START.search(step)
    return start is not None and _SUITE.search(step, start.end()) is not None and parse(step) is None


def unreadable_message(step):
    return "cannot read the case names of step: " + step.replace("\n", " ")


def unquoted_clause(step):
    return _UNQUOTED.search(step) is not None


def other_suite(step):
    found = _OTHER_SUITE.search(step)
    return found.group(1) if found else None


def quote_of(step):
    return step[_START.search(step).end()]
