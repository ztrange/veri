"""Cases for veri/blocked_by.py's blockers(body, repo), the reading other modules call."""
import os
import subprocess

from veri.blocked_by import blockers

BODY = """## Problem

Something.

## Blocked by

- #12
- https://github.com/acme/widgets/issues/34
"""

NONE_BODY = """## Problem

Something about #7.

## Blocked by

None.
"""

ABSENT_BODY = """## Problem

Something about #7.

## Acceptance criteria

1. Works.
"""

MIXED_BODY = """## Blocked by

- #1
- https://github.com/other/project/issues/56
- https://github.com/acme/widgets/issues/34
"""

LATER_BODY = """## Blocked by

- #3

## Notes

See #9.
"""


def test_blockers_reads_both_the_hash_form_and_the_full_url_of_the_given_repository():
    assert blockers(BODY, "acme/widgets") == [12, 34]


def test_blockers_returns_none_for_a_none_section_and_for_a_body_with_no_section():
    assert [blockers(NONE_BODY, "acme/widgets"), blockers(ABSENT_BODY, "acme/widgets")] == [[], []]


def test_blockers_ignores_another_repositorys_url_when_a_slug_is_given_and_reads_any_as_local_when_none_is():
    assert [blockers(MIXED_BODY, "acme/widgets"), blockers(MIXED_BODY, "")] == [[1, 34], [1, 56, 34]]


def test_blockers_stops_reading_the_section_at_the_next_heading():
    assert blockers(LATER_BODY, "acme/widgets") == [3]


def test_a_caller_gets_the_answers_with_no_gh_no_repository_and_no_child_process_started(monkeypatch, tmp_path):
    spawned = []

    def spy(name):
        def trap(*args, **kwargs):
            spawned.append(name)
            raise RuntimeError("child process started via " + name)
        return trap

    monkeypatch.setenv("PATH", "/nonexistent")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(subprocess.Popen, "__init__", spy("subprocess.Popen"))
    for name in ("system", "popen", "fork", "forkpty", "posix_spawn", "posix_spawnp", "execv", "execve",
                 "execvp", "execvpe", "spawnv", "spawnve", "spawnvp", "spawnvpe"):
        if hasattr(os, name):
            monkeypatch.setattr(os, name, spy("os." + name))

    answers = [blockers(BODY, "acme/widgets"), blockers(NONE_BODY, "acme/widgets"),
               blockers(ABSENT_BODY, "acme/widgets"), blockers(MIXED_BODY, "acme/widgets"),
               blockers(MIXED_BODY, ""), blockers(LATER_BODY, "acme/widgets")]

    assert (answers, spawned) == ([[12, 34], [], [], [1, 34], [1, 56, 34], [3]], [])
