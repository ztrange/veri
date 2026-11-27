"""Redacting secrets from text veri hands GitHub: token shapes and the values of the variables VERI_REDACT_VARS names,
replaced by [redacted]. github passes every gh argument through `redact`, run_records every string it pushes."""
import base64
import binascii
import json
import re

import tunables

REDACTED = "[redacted]"
_TOKEN_SHAPES = re.compile(
    r"gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{22,}|sk-ant-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}")
# The same shapes read in two parts, so a token glued to the next one is two tokens: a prefix, then the shape at its
# minimum length, then the characters it may run on in.
_PREFIX = re.compile(r"gh[pousr]_|github_pat_|sk-ant-|AKIA")
_AT_LEAST = {"github_pat_": (re.compile(r"[A-Za-z0-9_]{22}"), re.compile(r"[A-Za-z0-9_]*")),
             "sk-ant-": (re.compile(r"[A-Za-z0-9_-]{20}"), re.compile(r"[A-Za-z0-9_-]*")),
             "AKIA": (re.compile(r"[0-9A-Z]{16}"), re.compile("")),
             **{"gh%s_" % kind: (re.compile(r"[A-Za-z0-9]{36}"), re.compile(r"[A-Za-z0-9]*")) for kind in "pousr"}}
# A token's documented length after its prefix. A run-on that crosses a split point stops there, so a token ending a
# line takes no more of the next line than that: none for a full-length one. sk-ant- keys vary in length; 101 is the
# longest documented, so a shorter one ending a line may take up to 101 minus its length of the next line with it.
_DOCUMENTED = {"github_pat_": 82, "sk-ant-": 101, "AKIA": 16, **{"gh%s_" % kind: 36 for kind in "pousr"}}
# Where a secret may be split: a line break or its JSON string escape, or a zero-width character (ZWSP, ZWNJ, ZWJ, BOM,
# soft hyphen). A line break takes with it the blanks and one backslash before it, and the next line's indent and any
# run of markdown prefixes (`> `, `>`, `- `, `* `, `+ `, `# `), so a secret wrapped into a quote or a list is still one.
_BREAK = re.compile(r"\r\n|\r|\n|\\r\\n|\\r|\\n|[\u200b\u200c\u200d\ufeff\u00ad]")
_ZERO_WIDTH = "\u200b\u200c\u200d\ufeff\u00ad"
# A continuation line may also start with a gh CI log's prefix, `<job>\t<step>\t<ISO timestamp>Z `, or a bare ISO
# timestamp and a space: a token folded across two log lines is still one.
# Each field is read at most 256 characters deep, so a break costs a bounded read and the pass stays linear.
_LINE_START = re.compile(
    r"(?:(?:[^\t\r\n]{0,256}\t[^\t\r\n]{0,256}\t)?\d{4}-\d\d-\d\dT[\d:.]{1,32}Z )?"
    r"[ \t]*(?:(?:>[ \t]?|[-*+#][ \t])[ \t]*)*")
# A base64 or base64url run long enough to encode the shortest secret (an 8-character value).
_BASE64 = re.compile(r"[A-Za-z0-9+/_-]{12,}={0,2}")
_URLSAFE = str.maketrans("-_", "+/")


def _joined(text):
    """<text> with every split point _BREAK finds removed (a line break with what goes with it), and where each piece
    of it starts in <text>: [(joined start, text start)]. One pass: each character is read a bounded number of times."""
    pieces, starts, at, joined = [], [], 0, 0
    for found in _BREAK.finditer(text):
        start, end = found.start(), found.end()
        if end <= at:
            continue
        if found.group() not in _ZERO_WIDTH:
            while start > at and text[start - 1] in " \t":
                start -= 1
            if start > at and text[start - 1] == "\\":
                start -= 1
                while start > at and text[start - 1] in " \t":
                    start -= 1
            end = _LINE_START.match(text, end).end()
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


def _piece_end(starts, index, length):
    """Where the piece of the joined text holding character <index> ends: the next piece's start, else <length>."""
    low, high = 0, len(starts) - 1
    while low < high:
        middle = (low + high + 1) // 2
        if starts[middle][0] <= index:
            low = middle
        else:
            high = middle - 1
    return starts[low + 1][0] if low + 1 < len(starts) else length


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
        decoded = _joined(decoded)[0]
        if _TOKEN_SHAPES.search(decoded) or any(value in decoded for value in values):
            return True
    return False


def listed_names():
    """The names VERI_REDACT_VARS lists (its default when it names none: there is no turning value redaction off)."""
    return tunables.get("VERI_REDACT_VARS").split() or tunables.default("VERI_REDACT_VARS").split()


def _listed_values():
    """The values, 8 characters or more, of the variables VERI_REDACT_VARS names (`listed_names`), each also as a JSON
    string escapes it."""
    values = [tunables.read(name) for name in listed_names()]
    values = [value for value in values if len(value) >= 8]
    return values + [json.dumps(value)[1:-1] for value in values if json.dumps(value)[1:-1] != value]


def _secret_spans(text, values):
    """The (start, end) spans of <text> holding a token shape or one of <values>, or a base64 run that decodes to one,
    each found in <text> joined across its split points."""
    joined, starts = _joined(text)
    found = [(run.start(), run.end()) for run in _BASE64.finditer(joined) if _decodes_to_secret(run.group(), values)]
    reached = 0
    for prefix in _PREFIX.finditer(joined):
        least, run_on = _AT_LEAST[prefix.group()]
        shape = least.match(joined, prefix.end())
        if shape:
            # A shape starting inside the last one runs on from where that one ended, never back over it: one pass.
            # A run-on reads on to the end of its own piece of the text; past a split point it reads only up to the
            # token's documented length. Both reads are bounded, so the pass stays linear.
            at = max(shape.end(), reached)
            piece_end = _piece_end(starts, at - 1, len(joined))
            reached = run_on.match(joined, at, piece_end).end()
            if reached == piece_end:
                reached = run_on.match(joined, reached, max(reached, prefix.end() + _DOCUMENTED[prefix.group()])).end()
            found.append((prefix.start(), reached))
    for value in values:
        at = joined.find(value)
        while at != -1:
            found.append((at, at + len(value)))
            at = joined.find(value, at + len(value))
    # Each match, made on the joined text only, covers the text from its first character to its last, whatever split
    # points lie between.
    return [(_in_text(starts, first), _in_text(starts, last - 1) + 1) for first, last in found]


def redact(text):
    """<text> with every token-shaped string, and every value (8 characters or more) of a variable VERI_REDACT_VARS
    names, replaced by [redacted]; no split point (_BREAK and what goes with it) inside one hides it, and a base64 run
    that decodes to one is replaced whole. What a token ending a line may take of the next: nothing at its documented
    length (gh[pousr]_ 36, github_pat_ 82, AKIA 16 after the prefix; a listed value exactly), and for an sk-ant- key,
    whose length varies, up to 101 minus its own length of the next line's first characters."""
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
