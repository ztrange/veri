"""The CANDIDATES: line a refactor leaf reports, and the classes it may name."""
import re

CLASSES = ("structural", "cosmetic", "test-only", "out-of-scope")
KEY = "CANDIDATES:"
LINE = re.compile(rf"^{KEY}[ \t\n\r\f\v]*(.*)$")


def candidate(cls):
    return re.compile(rf"^{KEY}[ \t\n\r\f\v]*{cls}[ \t\n\r\f\v]*[|][ \t\n\r\f\v]*(.*)$")
