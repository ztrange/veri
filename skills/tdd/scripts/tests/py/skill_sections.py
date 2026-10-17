import pathlib

import pytest


def _level(line):
    hashes = len(line) - len(line.lstrip("#"))
    return hashes if hashes and line[hashes:hashes + 1] == " " else 0


def section(skill, heading):
    return section_of(pathlib.Path(skill).read_text(), heading, skill)


def section_of(text, heading, skill="the document"):
    lines = text.splitlines(keepends=True)
    level = _level(heading)
    start = next((i for i, line in enumerate(lines) if line.rstrip("\n") == heading), None)
    if not level or start is None:
        pytest.fail(f"no section headed {heading!r} in {skill}")
    fence = None
    end = len(lines)
    for i in range(start + 1, len(lines)):
        stripped = lines[i].lstrip()
        if fence is None and stripped.startswith(("```", "~~~")):
            fence = stripped[:3]
        elif fence is not None:
            if stripped.startswith(fence):
                fence = None
        elif min(2, level) <= _level(lines[i]) <= level:
            end = i
            break
    return "".join(lines[start:end])
