---
name: vready
description: >-
  Can veri run here? `/vready [repo-root]`. Use when the user asks whether a repository is ready for veri.
---

# vready — can veri run here?

Alias: `/vready`

Obeys `operator/PRINCIPLES.md` under the veri clone root (`git -C <base dir> rev-parse --show-toplevel`); read it first.

`$S` is `skills/tdd/scripts/`, reached from this skill's base directory as `../tdd/scripts/`.

## Run

Invoked as `/vready [repo-root]`. Run `$S/ready-check.sh`, passing `repo-root` through when
given and nothing otherwise. Print the script's table and its last line as it printed them.

- Exit 0 or 1: that output is the answer.
- Exit 2: no answer could be obtained. Report what the script printed and stop.

## Report only

Never fix a failing row: create no label, edit no file, and run no fix command the table
printed. Granting is the human's.
