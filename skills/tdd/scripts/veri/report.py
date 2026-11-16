"""The reader of KEY: value lines off a leaf report.

Each reader keeps its own rule (PRD 017.2): which occurrence wins, whether a space must follow
the colon, whether a `- ` or `* ` bullet may precede the key, how the text splits into lines and
whether a line is stripped first. The text may be str or bytes; a key is always str.
"""

_SPACES = ("required", "optional", "kept")
_OCCURRENCES = ("first", "last", "every")


def _typed(text, s):
    return s.encode() if isinstance(text, bytes) else s


def _value(line, key, space, bullet):
    """The value of `line` as a `key:` line under the rule, or None when it is not one.

    space: "required" — one space must follow the colon and is removed; "optional" — at most one is
    removed; "kept" — anything may follow and nothing is removed.
    """
    if bullet:
        for mark in ("- ", "* "):
            mark = _typed(line, mark)
            if line.startswith(mark):
                line = line[len(mark):]
                break
    prefix = _typed(line, key + ":")
    if not line.startswith(prefix):
        return None
    value = line[len(prefix):]
    if space == "kept":
        return value
    if value.startswith(_typed(line, " ")):
        return value[1:]
    return value if space == "optional" else None


def report_values(text, key, *, occurrence="every", space="required", bullet=False, splitlines=False, strip=False):
    """The values of the `key:` lines of `text`: a list for "every", else the first or last value or None.

    Lines split on "\\n" only unless `splitlines`; `strip` strips each line's surrounding whitespace first.
    """
    if occurrence not in _OCCURRENCES or space not in _SPACES:
        raise ValueError(f"occurrence {occurrence!r}, space {space!r}")
    lines = text.splitlines() if splitlines else text.split(_typed(text, "\n"))
    values = []
    for line in lines:
        value = _value(line.strip() if strip else line, key, space, bullet)
        if value is None:
            continue
        if occurrence == "first":
            return value
        values.append(value)
    if occurrence == "every":
        return values
    return values[-1] if values else None


def report_read(text, keys, *, optional_space=False, terminated_only=False):
    fields = {}
    lines = text.replace("\0", "").split("\n")
    if terminated_only:
        lines.pop()
    space = "optional" if optional_space else "required"
    for line in lines:
        for key in keys:
            value = _value(line, key, space, False)
            if value is not None:
                fields[key] = value
                break
    return fields
