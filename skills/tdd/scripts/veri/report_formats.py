"""The terminal report formats a develop prompt declares, parsed from its text."""
import re

_DECLARATION = re.compile(
    r"^REPORT-FORMAT (\S+) \| keys (.+?) \| suite (required|exempt)(?:: (.*))?$"
)


def parse(text):
    """The declared formats in order; ValueError for none or a required format without SUITE:."""
    formats = []
    for line in text.splitlines():
        match = _DECLARATION.match(line)
        if not match:
            continue
        name, keys, suite, reason = match.groups()
        keys = keys.split()
        if suite == "required" and "SUITE:" not in keys:
            raise ValueError(f"format {name} requires SUITE but its keys omit SUITE:")
        formats.append({"name": name, "keys": keys, "suite": suite, "reason": reason or ""})
    if not formats:
        raise ValueError("no REPORT-FORMAT declaration")
    return formats
