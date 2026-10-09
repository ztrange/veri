"""The CANDIDATES: line a refactor leaf reports, and the classes it may name."""
import re

CLASSES = ("structural", "cosmetic", "test-only", "out-of-scope")


def candidate(cls):
    return re.compile(rf"^CANDIDATES:[ \t\n\r\f\v]*{cls}[ \t\n\r\f\v]*[|][ \t\n\r\f\v]*(.*)$")
