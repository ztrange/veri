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


_STOP_WORDS = re.compile(r"\b(stop|skip|skipped|give up|say so)\b", re.IGNORECASE)


EXEMPT = {
    "develop-green.md:36": "the SPLIT: format is named in the paragraph that follows",
    "develop-green.md:49": "the fallback to the test command is reported inside SUITE:",
    "develop-reconcile.md:43": "a remote that moved again is reported through the declared keys",
    "develop-red-contradicted.md:89": "the fallback to the test command is reported inside SUITE:",
    "develop-red-missing.md:90": "the fallback to the test command is reported inside SUITE:",
    "develop-red-repair.md:91": "the fallback to the test command is reported inside SUITE:",
    "develop-red-supersede.md:88": "the fallback to the test command is reported inside SUITE:",
    "develop-red.md:84": "the fallback to the test command is reported inside SUITE:",
    "develop-refactor.md:76": "the fallback to the test command is reported inside SUITE:",
    "develop-refactor.md:87": "a skipped transform is listed in the declared report",
    "develop-revise.md:67": "the fallback to the test command is reported inside SUITE:",
}


def stop_prose_offenders(prompt, text, exempt=EXEMPT):
    """`<prompt>:<line>` for each line that tells the leaf to stop, skip, give up or say so without naming a declared format."""
    names = [name for fmt in parse(text) for name in [fmt["name"], *fmt["keys"]]]
    offenders = []
    for number, line in enumerate(text.splitlines(), 1):
        where = f"{prompt}:{number}"
        if line.startswith("REPORT-FORMAT ") or where in exempt:
            continue
        if _STOP_WORDS.search(line) and not any(name in line for name in names):
            offenders.append(where)
    return offenders
