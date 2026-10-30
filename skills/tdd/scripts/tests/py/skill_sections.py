import pathlib
import re

import pytest

from veri.markdown_sections import fenced_lines

LOWER = {c: c + 32 for c in range(ord("A"), ord("Z") + 1)}


def plain(text):
    return text.replace("*", "").replace("`", "").translate(LOWER)


def plain_lower(text):
    return text.replace("*", "").replace("`", "").lower()


def has_match(pattern, lines):
    return any(re.search(pattern, line) for line in lines)


def plain_lines(lines):
    return " ".join(line.replace("*", "").replace("`", "").lower() for line in lines) + " "


def plain_bytes(raw):
    return raw.translate(None, b"*`").lower()


def plain_folded(raw):
    return plain_bytes(raw).replace(b"\n", b" ")


def has(text, pattern):
    return any(re.search(pattern.encode(), line) for line in text.split(b"\n"))


def windows(text, pattern, radius=250):
    found = []
    for line in text.split(b"\n"):
        for match in re.finditer(pattern.encode(), line):
            found.append(line[max(match.start() - radius, 0):match.end() + radius])
    return found


def window(text, pattern, radius=250):
    return next(iter(windows(text, pattern, radius)), b"")


def heading_window(doc, heading, start):
    lines = section(doc, heading).splitlines()[1:]
    for i, line in enumerate(lines):
        if line.startswith("#"):
            lines = lines[:i]
            break
    for i, line in enumerate(lines):
        if re.search(start, line):
            return plain_lines(lines[i:])
    raise AssertionError(f"{heading!r} in {doc} has no line matching {start!r}")


def lines_of(path):
    lines = pathlib.Path(path).read_text().split("\n")
    return lines[:-1] if lines and lines[-1] == "" else lines


def _level(line):
    hashes = len(line) - len(line.lstrip("#"))
    return hashes if hashes and line[hashes:hashes + 1] == " " else 0


def section(skill, heading):
    return section_of(pathlib.Path(skill).read_text(), heading, skill)


def section_of(text, heading, skill="the document"):
    lines = text.splitlines(keepends=True)
    fenced = fenced_lines(text)
    level = _level(heading)
    start = None
    for i, line in enumerate(lines):
        if not fenced[i] and line.rstrip("\n") == heading:
            start = i
            break
    if not level or start is None:
        pytest.fail(f"no section headed {heading!r} in {skill}")
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if not fenced[i] and min(2, level) <= _level(lines[i]) <= level:
            end = i
            break
    return "".join(lines[start:end])
