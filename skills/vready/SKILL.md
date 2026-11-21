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

The script runs the fast and full test tiers on the default branch's tip, so one call can take
up to ten minutes: give the command a 600000 ms timeout. The check also makes one paid Haiku
call, about $0.004, to prove a leaf may bypass permission prompts, including for a multi-line
command with `$'…'` quoting and a parameter expansion, the shape the dev session's subagents run.
A `subagent permissions` row checks that the dev session's subagents may run git, the repo's
test command and `$S` scripts without a permission prompt; when it fails, the script prints
the allow rules to add.

- Exit 0 or 1: that output is the answer.
- Exit 2: no answer could be obtained. Report what the script printed and stop.
- Exit 3: a test tier is still running (`waiting on ready-<tier>` is the last line). That is not
  the answer: run `ready-check.sh` again with the same argument, and keep doing so until it
  exits 0, 1 or 2.

For each failing `<tier> tier run` row, the tier's whole output is kept at
`.tdd/ready-<tier>.out` in the checked repository's main working tree. Have a subagent on the
cheapest model that can do it (haiku) read that file and return at most 10 lines on why the tier
failed, and print those lines after the table; never read the file yourself. When you run as a
subagent yourself (your brief says so, as `/vinstall`'s does), start no subagent: read the file
yourself and put why the tier failed in your answer.

## Report only

Never fix a failing row: create no label, edit no file, and run no fix command the table
printed. Granting is the human's.
