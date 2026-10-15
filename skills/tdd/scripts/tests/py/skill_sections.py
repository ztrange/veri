import pathlib

import pytest


def _level(line):
    hashes = len(line) - len(line.lstrip("#"))
    return hashes if hashes and line[hashes:hashes + 1] == " " else 0


def section(skill, heading):
    lines = pathlib.Path(skill).read_text().splitlines(keepends=True)
    level = _level(heading)
    start = next((i for i, line in enumerate(lines) if line.rstrip("\n") == heading), None)
    if not level or start is None:
        pytest.fail(f"no section headed {heading!r} in {skill}")
    end = next((i for i in range(start + 1, len(lines)) if 0 < _level(lines[i]) <= level), len(lines))
    return "".join(lines[start:end])
