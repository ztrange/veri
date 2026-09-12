---
name: solve-issue
description: >-
  Former name of `/tdd`. Kept so a session already invoked as `/solve-issue <number>` keeps
  working: it forwards the same arguments to `/tdd`, which runs the single-issue TDD
  procedure for an integer argument. Prefer `/tdd <number>` in new invocations.
---

# solve-issue — renamed to /tdd

This skill has moved. The procedure it used to carry now lives in `skills/tdd/SKILL.md`,
invoked as `/tdd`, and an integer argument selects the same single-issue run this command
always did.

**Invoke `/tdd $ARGUMENTS` and follow that skill end to end.** Pass the arguments through
unchanged — the issue number, and any `--repo <owner/name>` alongside it. Do nothing else
here: this file exists only so an invocation on the old name is not stranded, and it holds
no procedure of its own to fall back on.
