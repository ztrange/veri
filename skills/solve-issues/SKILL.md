---
name: solve-issues
description: >-
  Former name of `/tdd`'s loop. Kept so a session already invoked as `/solve-issues` keeps
  working: it forwards the same arguments to `/tdd`, which drains a scope when its argument
  is not an integer and defaults to the bare `ready-for-agent` pool. Prefer `/tdd` or
  `/tdd <scope>` in new invocations.
---

# solve-issues — renamed to /tdd

This skill has moved. The loop it used to carry is now a branch of `skills/tdd/SKILL.md`,
invoked as `/tdd`, where an argument that is not an integer names the scope to drain and no
argument at all means the same pool this command always drained.

**Invoke `/tdd $ARGUMENTS` and follow that skill end to end.** Pass the arguments through
unchanged — `--continue-on-bail` and `--repo <owner/name>` mean there exactly what they
meant here. Do nothing else here: this file exists only so an invocation on the old name is
not stranded, and it holds no procedure of its own to fall back on.
