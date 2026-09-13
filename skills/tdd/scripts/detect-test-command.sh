#!/usr/bin/env bash
# detect-test-command.sh — print the one command that runs the full suite of a repo.
#
# Prints the command on stdout and exits 0; prints nothing and exits 3 when it cannot
# decide, which is the conductor's cue to ask the human.
#
# Precedence is first-match-wins, and the two overrides below are the first rules on
# purpose: an issue that named its test command, or a repo that wrote .veri/test-command,
# has already answered the question in words, so no later inference gets to second-guess
# it. Which of the two answers first is argued where rule 0 sits.
#
# Usage:   detect-test-command.sh [--issue <body-file>] [repo-root]
#          (repo-root defaults to the current directory)
set -euo pipefail

# `--issue <body-file>` is optional and, when given, comes first — the conductor has
# already saved the issue body to a file, so what is passed is a path, never the text.
# `shift 2` drops both words so the repo root is read from $1 either way, and the empty
# default keeps `set -u` from aborting on the unset variable when the flag is absent.
issue=""
if [ "${1:-}" = "--issue" ]; then
  issue="${2:-}"
  shift 2
fi

root="${1:-.}"

# Every rule below ends the same way, because precedence is first-match-wins: print the
# command it decided on, and stop — a rule that answered leaves nothing for the rest to do.
# Naming that ending once keeps each rule to the question it asks, the `if` saying which
# marker was found and `answer` saying what the marker means.
answer() { printf '%s\n' "$1"; exit 0; }

# 0. The issue's own line, ahead of even the override file. `.veri/test-command` is the
# repo's answer for every run; a `Test command:` line in the issue body is this run's, and
# the narrower claim wins — a docs issue says so in its own words and the leaves obey that
# instead of the repo-wide suite.
#
# The two words themselves, named once because rule 0 asks after them three times — to
# recognise the line, to take the prefix ahead of the marker, and to take the command behind
# it — and the three have to be the same bytes: a line recognised by one spelling and cut at
# another would answer with the wrong half of itself. Every use quotes the expansion, because
# `case`, `#` and `%%` all take patterns and what is wanted here is the literal text. The name
# is introduced ahead of the paragraphs below rather than beside the code, because every one
# of them spells the marker as `"$marker"` and none of them spells out the words.
marker='Test command:'

# The first matching line answers, so a body that mentions the command again lower down —
# in a note, a quotation, a later section — cannot overrule the one that stated it. What
# follows the marker is printed verbatim but for the whitespace separating the two: the
# `#` expansion drops the marker, and `ltrim` drops what separated it from the command.
# A line with nothing after the marker names no command, so it is skipped rather than
# answered with "".
#
# The marker is looked for *anywhere* on the line, not only at its start, because that is
# where issues actually write it: mid-sentence in the Notes, with the command in a backtick
# span (#131). `*"$marker"*` matches that line, and `${line#*"$marker"}` drops the prose ahead
# of the marker as well as the marker itself — shortest match, so the first marker on the line
# is the one that answers.
#
# A marker *inside a backtick span* is being quoted, not stated: a body that writes the two
# words while describing how a leaf finds its command is talking about the line, not writing
# one. Such a marker is skipped and the scan goes on — to later markers on the same line first,
# then to later lines — because first-match-wins makes a mention
# fatal otherwise — the real line further down cannot overrule it, and what gets handed to the
# conductor is the prose that trailed the quote (#145).
#
# `quoted <prefix>` is true when that prefix — the text a line carries ahead of its marker —
# leaves a backtick span open, which is what makes the marker behind it a quotation. Backticks
# pair off, so an odd count is a span still open. `${1//[!\`]/}` deletes every character that
# is not a backtick and `${#…}` counts what is left, which is cheaper and steadier than asking
# where each span starts and ends.
quoted() {
  local ticks="${1//[!\`]/}"
  [ $(( ${#ticks} % 2 )) -eq 1 ]
}

# Two steps then turn what is left into the command, and each is named so the rule reads as
# the sentence it is: the command is what follows the marker, ltrimmed and unwrapped.
#
# `ltrim <string>` prints that string with its leading whitespace removed, and is spelled
# here exactly as `parse-verdict.sh` spells it — the operation already had a name in this
# codebase, so it keeps that one rather than growing a second hand-rolled spelling.
# `${1%%[![:space:]]*}` is the leading whitespace itself: cut the string at the first
# character that is not blank and what remains is the run of blanks in front of it. `${1#…}`
# then drops that run from the front. The inner expansion is quoted because `#` takes a
# pattern, and blanks are not the only thing a leading `*` or `[` in the string could mean.
ltrim() { printf '%s' "${1#"${1%%[![:space:]]*}"}"; }

# `unwrapped <string>` prints the backtick span the string opens with, and the string
# untouched when it opens with anything else — so a command written bare is still printed
# verbatim. `#` drops the opening backtick and `%%` cuts at the closing one, dropping the
# `. More prose.` that would otherwise be handed to a leaf as part of the command.
unwrapped() {
  case "$1" in
    '`'*)
      local s="${1#\`}"
      printf '%s\n' "${s%%\`*}"
      ;;
    *) printf '%s\n' "$1" ;;
  esac
}

if [ -n "$issue" ] && [ -f "$issue" ]; then
  while IFS= read -r line || [ -n "$line" ]; do
    # A line is walked marker by marker rather than answered from its first one, because a
    # skipped marker has somewhere else to go on the same line: an issue that quotes the
    # two words and then states them in the same sentence — which is how #145's own body
    # reads — hides the line that answers behind the one that does not. `rest` is the part
    # of the line not yet walked and `seen` is the part already walked, and each turn moves
    # one marker's worth of text from the first to the second. The `case` is the loop's only
    # exit that is not an answer: when `rest` holds no further marker the line is spent, and
    # a line that never held one is spent on the first turn.
    rest="$line"
    seen=""
    while :; do
      case "$rest" in
        *"$marker"*) ;;
        *) break ;;
      esac
      # The unwalked text cut in two at its *first* marker: `%%` takes the shortest prefix
      # and `#` the shortest match, so the two halves are cut either side of the same
      # marker rather than of two different ones. The prefix joins `seen`, which is what
      # says whether this marker is quoted — the whole of the line ahead of it, not just
      # the stretch since the previous marker, because it is the backticks opened anywhere
      # earlier that leave a span open here. The markers themselves never join `seen`, and
      # need not: the two words carry no backtick, so they cannot change the count that
      # decides it.
      seen="$seen${rest%%"$marker"*}"
      rest="${rest#*"$marker"}"
      # Two reasons a marker does not answer, and both are written as the same guard —
      # leave it behind and look for the next one — so what is left after them is the one
      # marker that does answer, rather than an `answer` buried inside a condition.
      if quoted "$seen"; then
        continue
      fi
      cmd="$(unwrapped "$(ltrim "$rest")")"
      if [ -z "$cmd" ]; then
        continue
      fi
      answer "$cmd"
    done
  done < "$issue"
fi

# 1. The override file. Its first non-empty line is the command, verbatim: `IFS=` keeps
# read from stripping leading and trailing whitespace, -r keeps it from eating
# backslashes, and `answer` re-emits exactly those bytes — the whole point of the escape
# hatch is that what the repo wrote is what the leaf runs.
#
# `|| [ -n "$line" ]` is load-bearing: read exits non-zero at end of file, which is also
# what it does after handing back a final line that had no trailing newline. Without the
# second test that last line would be read and then discarded.
override="$root/.veri/test-command"
if [ -f "$override" ]; then
  while IFS= read -r line || [ -n "$line" ]; do
    if [ -n "$line" ]; then
      answer "$line"
    fi
  done < "$override"
fi

# 2. A package.json that declares a test script names the node runner. Which runner is a
# separate question, answered by the lockfile the repo committed beside it: a lockfile is
# the repo saying which package manager actually installs here, so `pnpm test` / `yarn
# test` rather than an `npm test` that would resolve a different dependency tree.
#
# `tr -d '[:space:]'` flattens the file to one line with no whitespace, so the pattern can
# be written as if package.json were minified — formatting stops mattering. `[^}]*` then
# pins the "test": key to inside the "scripts" object, so a dependency or a config section
# that happens to be called "test" cannot answer for it. Both are inside an `if`
# condition, where grep's exit 1 for "no match" is an answer rather than a failure `set
# -e` would abort on.
pkg="$root/package.json"
if [ -f "$pkg" ] && tr -d '[:space:]' < "$pkg" | grep -q '"scripts":{[^}]*"test":'; then
  if [ -f "$root/pnpm-lock.yaml" ]; then
    answer 'pnpm test'
  elif [ -f "$root/yarn.lock" ]; then
    answer 'yarn test'
  else
    answer 'npm test'
  fi
fi

# 3. A Makefile declaring a `test:` target names `make test`, and it does so before the
# python markers are ever looked at. That ordering is deliberate and differs from the one
# SKILL.md used to describe: a repo that wrote a `test` target chose it — very often
# precisely to wrap `pytest` with whatever else the suite needs — so the target answers,
# and pytest.ini is left to speak for repos that wrote no target at all.
#
# `^test[[:space:]]*:` anchors the match to a rule at the start of a line, allowing the
# `test :` spelling make also accepts; `.PHONY: test` does not start with `test`, so it
# cannot be mistaken for the target itself.
mk="$root/Makefile"
if [ -f "$mk" ] && grep -qE '^test[[:space:]]*:' "$mk"; then
  answer 'make test'
fi

# 4. A repo that declares pytest configuration names `pytest -q` — `-q` because the
# conductor reads the exit status, not the dots. Three spellings are one rule, and they are
# asked differently on purpose. `pytest.ini` exists only to configure pytest, so the
# filename alone is the whole claim and the file may well be empty. `pyproject.toml` makes
# no such claim — it is packaging metadata for any python project — so this looks inside
# it for the section that does: `[tool.pytest`, anchored to the start of a line so a
# mention in prose or in another table's value cannot answer for it, and matched as a
# prefix because real repos write `[tool.pytest.ini_options]`. `setup.cfg` is packaging
# metadata too, so it is asked the same way, for the header pytest documents for that file:
# `[tool:pytest]`, spelled with a colon rather than the dot pyproject.toml uses.
#
# `\[` escapes the bracket that would otherwise open a character class, and `\.` keeps the
# dot literal. grep sits inside the `if` condition, where its exit 1 for "no match" is an
# answer rather than a failure `set -e` would abort on.
#
# The two look-inside spellings ask the identical question of different files, so it is named
# once: `declares <file> <pattern>` is true when the file is there and a line in it matches.
# Naming it also drops what the inline spelling needed and this does not — the path repeated
# twice per clause, and the `{ ...; }` braces that kept `&&` from binding tighter than the
# `||` separating the three markers.
declares() { [ -f "$1" ] && grep -qE "$2" "$1"; }

if [ -f "$root/pytest.ini" ] \
  || declares "$root/pyproject.toml" '^\[tool\.pytest' \
  || declares "$root/setup.cfg" '^\[tool:pytest\]'; then
  answer 'pytest -q'
fi

# 5 and 6. The two compiled stacks each name their toolchain's own runner. Both markers are
# the manifest their toolchain requires at the repo root, and neither filename belongs to
# any other kind of project, so — unlike pyproject.toml above — the name alone is the whole
# claim and nothing inside the file needs reading.
#
# `./...` is go's own spelling for "every package beneath here"; without it `go test` runs
# only the root package and quietly skips the rest of the suite. `cargo test` already walks
# the whole crate, so it needs no argument.
if [ -f "$root/go.mod" ]; then
  answer 'go test ./...'
fi

if [ -f "$root/Cargo.toml" ]; then
  answer 'cargo test'
fi

# 7. The last rule before giving up: a python repo that committed no runner configuration at
# all still has a suite if `tests/` holds files named `test_*.py`, and the stdlib runs them
# without anything installed — `python3` because a modern macOS has no `python`, `-m unittest
# discover` because there is no runner script to call, `-q` for the same reason as pytest's.
#
# Unlike every rule above, the marker is a pattern rather than a file at a known path, so the
# question is asked by letting the shell expand the pattern and testing what came back. A glob
# that matches nothing is left as its own literal text by default, and `[ -f ]` is false for
# that non-existent filename — so the loop answers on the first real match and falls through
# when there was none, with no need for the `nullglob` that bash 3.2 would handle differently.
# Only the pattern is unquoted: "$root" stays quoted so a path with spaces still resolves.
for f in "$root"/tests/test_*.py; do
  if [ -f "$f" ]; then
    answer 'python3 -m unittest discover -q'
  fi
done

# Nothing decided: say nothing, and let exit 3 — "nothing to do", not an error — send the
# question to the human.
exit 3
