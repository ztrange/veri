"""The named cases and their suite, parsed from a replaces-case step."""
import re

_START = re.compile(r"\breplaces (?=['\"`])")
_SUITE = re.compile(r" in ([\w./-]+\.test\.sh)")


def parse(step):
    start = _START.search(step)
    suite = _SUITE.search(step, start.end())
    quote = step[start.end()]
    region = step[start.end() + 1:suite.start()]
    assert region.endswith(quote)
    names = region[:-1].split(quote + ", " + quote)
    return names, suite.group(1)
