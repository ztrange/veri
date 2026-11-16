---
name: vinstall
description: >-
  Link veri's skills into a project: `/vinstall [repo-root]`. Use when the user asks to install veri, set up a project, or repair a broken install.
---

# vinstall — link veri's skills into a project

`$S` is `skills/tdd/scripts/`, reached from this skill's base directory as `../tdd/scripts/`.

## Invocation

Invoked as `/vinstall [repo-root]`. Run `$S/install-links.sh [repo-root]`, passing the
argument through when the user gave one. Then report each skill the script linked,
repaired or removed, by name (a removed one prints as `removed <name>`).

## Stacking finished runs

During setup, after reporting the links, run `$S/stack-branch.sh [repo-root]`. When it exits 0,
report the stack branch it printed and do not ask. When it exits 2, the `CLAUDE.md` already holds a
`veri: stack branch:` line that cannot name a stack: report its stderr to the user, write nothing and
do not ask; the user fixes or removes that line. When it exits 3, ask the user whether the
repository stacks finished runs on a standing branch and, if so, under what branch name:

- On a name, write the line `veri: stack branch: <name>` into the repository's `CLAUDE.md`
  (creating the file when there is none), then run `$S/stack-branch.sh [repo-root]` again. Exit 0
  is done. Exit 2 means the name cannot be a stack (empty, a placeholder, the default branch in any
  spelling, a `refs/` or `origin/` name, or refused by `git check-ref-format --branch`, or the default
  branch cannot be told): report its stderr, take the line out again and ask once more.
- On a no, write nothing: each run then keeps one pull request against the default branch, a CI
  wait and a merge call.

## Checking readiness

Only when the script linked, repaired or removed at least one skill: run the readiness
check through a subagent, on the cheapest model that can do it (haiku). Brief the
subagent to read `<base dir>/../vready/SKILL.md` (this skill's base directory) and follow
it, and to return at most 10 lines. Never tell it to run `/vready`: vready is not linked
into projects. Report the subagent's answer. When the script changed nothing, skip this:
do not run the readiness check.

## On exit 2

Exit 2 means the script refused: it found a path veri did not create. Report the refusal
exactly as the script printed it, and stop. Never work around it: do not delete, move or
overwrite that path, and do not link by hand. The path belongs to the operator.

## Repairing an install

Re-running `/vinstall` is the way to repair an install. A missing or dangling link is
relinked by running it again; there is no separate repair command.
