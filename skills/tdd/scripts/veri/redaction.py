"""Redacting secrets from text veri hands GitHub: token shapes and the values of the variables VERI_REDACT_VARS names,
replaced by [redacted]. github passes every gh argument through `redact`, run_records every string it pushes."""
import base64
import binascii
import json
import re

import tunables

REDACTED = "[redacted]"
# Each shape at its minimum length, with the characters it may run on in: gh[pousr]_[A-Za-z0-9]{36,},
# github_pat_[A-Za-z0-9_]{22,}, sk-ant-[A-Za-z0-9_-]{20,} and AKIA[0-9A-Z]{16}.
_TOKEN_SHAPES = re.compile(r"gh[pousr]_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{22}|sk-ant-[A-Za-z0-9_-]{20}|AKIA[0-9A-Z]{16}")
_RUN_ON = ((("github_pat_",), re.compile(r"[A-Za-z0-9_]*")), (("gh",), re.compile(r"[A-Za-z0-9]*")),
           (("sk-ant-",), re.compile(r"[A-Za-z0-9_-]*")), (("AKIA",), re.compile("")))
# A line break or its JSON string escape, with the blanks before it and the next line's indent, or a zero-width
# character (ZWSP, ZWNJ, ZWJ, BOM, soft hyphen): a token split by one is still a token.
_BREAK = re.compile(r"\r\n|\r|\n|\\r\\n|\\r|\\n|[\u200b\u200c\u200d\ufeff\u00ad]")
_BLANKS = re.compile(r"[ \t]*")
_ZERO_WIDTH = "\u200b\u200c\u200d\ufeff\u00ad"
# A base64 or base64url run long enough to encode the shortest secret (an 8-character value).
_BASE64 = re.compile(r"[A-Za-z0-9+/_-]{12,}={0,2}")
_URLSAFE = str.maketrans("-_", "+/")


def _unbroken(text):
    """<text> with every _BREAK removed, and where each piece of it starts in <text>: [(joined start, text start)]."""
    pieces, starts, at, joined = [], [], 0, 0
    for found in _BREAK.finditer(text):
        start, end = found.start(), found.end()
        if found.group() not in _ZERO_WIDTH:
            # The blanks before a line break and the next line's indent go with it; each blank is read once.
            while start > at and text[start - 1] in " \t":
                start -= 1
            end = _BLANKS.match(text, end).end()
        if end <= at:
            continue
        if start > at:
            pieces.append(text[at:start])
            starts.append((joined, at))
            joined += start - at
        at = max(at, end)
    pieces.append(text[at:])
    starts.append((joined, at))
    return "".join(pieces), starts


def _in_text(starts, index):
    """Where character <index> of the unbroken text sits in the text."""
    low, high = 0, len(starts) - 1
    while low < high:
        middle = (low + high + 1) // 2
        if starts[middle][0] <= index:
            low = middle
        else:
            high = middle - 1
    return starts[low][1] + index - starts[low][0]


def _decodes_to_secret(run, values):
    """Whether the base64 (or base64url) <run>, read from each of its four alignments, decodes to text holding a token
    shape or a listed variable's value."""
    run = run.rstrip("=").translate(_URLSAFE)
    for skip in range(4):
        aligned = run[skip:]
        aligned = aligned[:-1] if len(aligned) % 4 == 1 else aligned
        aligned += "=" * (-len(aligned) % 4)
        try:
            decoded = base64.b64decode(aligned).decode("latin-1")
        except binascii.Error:
            continue
        decoded = _unbroken(decoded)[0]
        if _TOKEN_SHAPES.search(decoded) or any(value in decoded for value in values):
            return True
    return False


def _listed_values():
    """The values, 8 characters or more, of the variables VERI_REDACT_VARS names (its default when it names none: there
    is no turning value redaction off), each also as a JSON string escapes
    it."""
    names = tunables.get("VERI_REDACT_VARS").split() or tunables.default("VERI_REDACT_VARS").split()
    values = [tunables.read(name) for name in names]
    values = [value for value in values if len(value) >= 8]
    return values + [json.dumps(value)[1:-1] for value in values if json.dumps(value)[1:-1] != value]


def _secret_spans(text, values):
    """The (start, end) spans of <text> holding a token shape or one of <values>, a line break inside one included,
    and of each base64 run that decodes to one."""
    joined, starts = _unbroken(text)
    spans = [(_in_text(starts, run.start()), _in_text(starts, run.end() - 1) + 1)
             for run in _BASE64.finditer(joined) if _decodes_to_secret(run.group(), values)]
    reached = 0
    for found in _TOKEN_SHAPES.finditer(joined):
        # A shape starting inside the last one's span runs on from that span's end, never back over it: one pass.
        end = max(_in_text(starts, found.end() - 1) + 1, reached)
        run_on = next(chars for prefixes, chars in _RUN_ON if found.group().startswith(prefixes))
        reached = run_on.match(text, end).end()
        spans.append((_in_text(starts, found.start()), reached))
    for value in values:
        at = joined.find(value)
        while at != -1:
            spans.append((_in_text(starts, at), _in_text(starts, at + len(value) - 1) + 1))
            at = joined.find(value, at + len(value))
    return spans


def redact(text):
    """<text> with every token-shaped string, and every value (8 characters or more) of a variable VERI_REDACT_VARS
    names, replaced by [redacted]; a line break, or its JSON escape, inside one does not hide it, and a base64 run that
    decodes to one is replaced whole."""
    merged = []
    for start, end in sorted(_secret_spans(text, _listed_values())):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    out, at = [], 0
    for start, end in merged:
        out += [text[at:start], REDACTED]
        at = end
    out.append(text[at:])
    return "".join(out)
