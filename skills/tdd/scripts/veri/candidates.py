"""The CANDIDATES: line a refactor leaf reports, and the classes it may name."""
from report import report_values

CLASSES = ("structural", "cosmetic", "test-only", "out-of-scope")
KEY = "CANDIDATES:"
BLANKS = " \t\n\r\f\v"


def _typed(line, s):
    return s.encode() if isinstance(line, bytes) else s


def line(text):
    """What follows `CANDIDATES:` and any ASCII whitespace on the one line `text` (str or bytes);
    None when it is no such line."""
    value = report_values(text, KEY[:-1], occurrence="first", space="kept")
    return None if value is None else value.lstrip(_typed(text, BLANKS))


def candidate(text, cls):
    """The text after the bar of a `CANDIDATES: <cls> | <text>` line, whitespace allowed around class and bar;
    None otherwise."""
    rest = line(text)
    cls = _typed(text, cls)
    if rest is None or not rest.startswith(cls):
        return None
    rest = rest[len(cls):].lstrip(_typed(text, BLANKS))
    if not rest.startswith(_typed(text, "|")):
        return None
    return rest[1:].lstrip(_typed(text, BLANKS))
