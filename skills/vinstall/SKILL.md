---
name: vinstall
description: >-
  Link veri's skills into a project: `/vinstall [repo-root]`. Use when the user asks to install veri, set up a project, or repair a broken install.
---

# vinstall — link veri's skills into a project

`$S` is `skills/tdd/scripts/`, reached from this skill's base directory as `../tdd/scripts/`.

## Invocation

Invoked as `/vinstall [repo-root]`. Run `$S/install-links.sh [repo-root]`, passing the
argument through when the user gave one. Then report each skill the script linked or
repaired, by name.

## On exit 2

Exit 2 means the script refused: it found a path veri did not create. Report the refusal
exactly as the script printed it, and stop. Never work around it: do not delete, move or
overwrite that path, and do not link by hand. The path belongs to the operator.

## Repairing an install

Re-running `/vinstall` is the way to repair an install. A missing or dangling link is
relinked by running it again; there is no separate repair command.
