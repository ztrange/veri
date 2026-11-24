---
name: vinstall
description: >-
  Link veri's skills into a project: `/vinstall [repo-root]`, or prepare a repository for Claude Code cloud sessions: `/vinstall cloud [repo-root]`. Use when the user asks to install veri, set up a project, or repair a broken install.
---

# vinstall — link veri's skills into a project

`$S` is `skills/tdd/scripts/`, reached from this skill's base directory as `../tdd/scripts/`.

## Invocation

Invoked as `/vinstall [repo-root]`. Run `$S/install-links.sh [repo-root]`, passing the
argument through when the user gave one. Then report each skill the script linked,
repaired or removed, by name (a removed one prints as `removed <name>`).
When the first argument is `cloud`, follow `## Cloud sessions` instead.

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

## Recording the test commands

After `install-links.sh` exits 0, read the target repository's `CLAUDE.md`. When it holds a
`veri: fast tests:`, a `veri: all tests:`, a `veri: one test file:` and a `veri: quiet test files:`
line, ask nothing about test commands and skip the rest of this section. Otherwise:

1. **The tier commands.** When `CLAUDE.md` already holds both a `veri: fast tests:` and a
   `veri: all tests:` line, ask nothing about them: run
   `$S/detect-test-command.sh --tier fast [repo-root]` and `--tier all [repo-root]` and pass the
   two commands they print, which are those lines' commands, unchanged to step 4. When it lacks
   either line:
   - Run `$S/detect-test-command.sh --tier fast [repo-root]` and
     `$S/detect-test-command.sh --tier all [repo-root]`. Exit 0 printed the tier's proposed command;
     exit 3 means none found, and that tier is shown as none found. Show the operator both, each
     beside where it came from: the `CLAUDE.md` line, or the manifest file and key inference read
     (`package.json`'s `scripts.test`, the `Makefile`'s `test` target, the pytest section of
     `pytest.ini`, `pyproject.toml` or `setup.cfg`, `go.mod`, `Cargo.toml`, `tests/test_*.py`). Run
     no install, no test and no network command to find a command.
   - Ask the operator to confirm or replace each command. `record-test-commands.sh` runs only with
     the two commands the operator confirmed or gave. Without a confirmed command for each tier,
     nothing is written: say so and leave this section.
2. **The one-test-file command.** When `CLAUDE.md` lacks a `veri: one test file:` line, ask the
   operator for the command that runs one test file, taking the file as `"$1"`, and propose none:
   veri cannot infer it. The form recorded is one shell command, run as
   `sh -c '<command>' sh <test file>` and read by its exit code alone (0 the file passes, 1 it
   fails), a `make` command by make's last `*** Error` line. It must hold `"$1"` (anywhere in it)
   or `$1` as a word of its own, or the script refuses it; for example `pytest -q "$1"` or
   `make test TESTS="$1"`. Pass the answer with `--one-file`. With no answer, record the other
   lines without it, and say that a run's preflight stops without the line.
3. **The quiet command.** When `CLAUDE.md` lacks a `veri: quiet test files:` line, run
   `$S/detect-test-command.sh --tier "quiet test files" [repo-root]`. Exit 0 printed a proposed
   default for a recognisable runner (pytest `-q --no-header -rf` from its pytest section, jest
   `--silent` from `package.json`'s `scripts.test`): show it beside where it came from and ask the
   operator to confirm or replace it. Exit 3: ask for the command, proposing none. It takes the
   test file paths appended as arguments and prints only the failing cases (each name plus its
   first failure line) and one count line; exit 0 green, 1 a test failed, 2 the run broke. Pass
   the confirmed command with `--quiet`. With no answer, record the other lines without it, and
   say that leaves then get each run's exit code and last 20 lines. When every line to record is
   already in `CLAUDE.md`, there is nothing to record: leave this section.
4. Run `$S/record-test-commands.sh [--one-file '<one-file-cmd>'] [--quiet '<quiet-cmd>'] '<fast-cmd>' '<all-cmd>' [repo-root]`.
   Quote each command as one shell word: wrap it in single quotes and write each `'` inside it as
   `'\''`, so `echo 'hi'` is passed as `'echo '\''hi'\'''`. It pushes a `veri-install` branch whose
   one commit records the lines in `CLAUDE.md`, and opens a pull request for it.
   - Exit 0: report the pull request's URL it printed, and say that runs infer the test commands
     until that pull request merges, and that `/vinstall` never merges it: merging is the
     repository owner's.
   - Exit 2: report what the script printed, and stop.
   - Exit 3: report that there is nothing to record: the default branch already declares every
     command given, or a pull request recording them is already open.

## Checking readiness

Only when the script linked, repaired or removed at least one skill: run the readiness
check through a subagent, on the cheapest model that can do it (haiku). Brief the
subagent to read `<base dir>/../vready/SKILL.md` (this skill's base directory) and follow
it, and to return at most 10 lines. Tell it that it runs as a subagent and starts none of its
own, so no subagent starts a subagent. Never tell it to run `/vready`: vready is not linked
into projects. Report the subagent's answer. When the script changed nothing, skip this:
do not run the readiness check.

## On exit 2

Exit 2 means the script refused: it found a path veri did not create. Report the refusal
exactly as the script printed it, and stop. Never work around it: do not delete, move or
overwrite that path, and do not link by hand. The path belongs to the operator.

## Repairing an install

Re-running `/vinstall` is the way to repair an install. A missing or dangling link is
relinked by running it again; there is no separate repair command.

## Cloud sessions

Invoked as `/vinstall cloud [repo-root]`, it prepares the repository so a Claude Code cloud session can
run veri. Such a session starts with no venv and a Python below veri's floor. It supports only veri's own
repository for now: on any other repository `cloud-install.sh` exits 2 saying so and writes nothing.

1. Run `$S/cloud-install.sh [repo-root]`, passing the argument through when the user gave one. It adds
   one `SessionStart` hook to the repository's `.claude/settings.json`, creating the file when missing
   and keeping every other key and hook. The hook runs `$S/cloud-setup.sh` only when
   `CLAUDE_CODE_REMOTE=true`, so it does nothing on a local session. `cloud-setup.sh` finds or installs a
   Python at the floor, builds veri's venv once per lock and puts its `bin` on the session's PATH. On
   exit 0, report the line the script printed and tell the operator to commit `.claude/settings.json`:
   a cloud session sees only what is committed. On exit 2, report its stderr exactly and stop.
2. Print the claude.ai environment settings the operator must make by hand, in the cloud environment's
   settings on claude.ai:
   - `GH_TOKEN`, a token `gh` and `git push` can use for this repository;
   - a network level that reaches github.com and pypi.org, since setup installs from PyPI.

   Say that no CLI or API sets them: `claude` offers no command to create or configure a cloud
   environment, so they live only in the web UI.
3. Then run `/vready`'s readiness check through a subagent, briefed as `## Checking readiness` says,
   whatever `cloud-install.sh` changed, and report its answer.
