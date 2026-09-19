#!/usr/bin/env bash
# Unit tests for scripts/detect-test-command.sh — prints the one command that runs the
# full suite of the repo at [repo-root] on stdout and exits 0; prints nothing and exits 3
# when it cannot decide (the conductor then asks the human).
#
# Contract under test (issues #39, #120):
#   detect-test-command.sh [--issue <body-file>] [repo-root]   (root default: .)
#   precedence, first match wins: the issue body's own `Test command:` line,
#   .veri/test-command override, npm/pnpm/yarn, make, pytest, go, cargo, unittest —
#   otherwise exit 3.
#
# Each case seeds a throwaway `mktemp -d` repo with only the marker files it is about:
# the script inspects files, it never runs the command, so no toolchain is needed.
# Sibling style: classify-bail.test.sh, ensure-run-state-ignored.test.sh.
#
# Run: scripts/tests/detect-test-command.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
DETECT="$HERE/../detect-test-command.sh"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
pass=0 fail=0
ok() { pass=$((pass + 1)); }
no() { fail=$((fail + 1)); echo "FAIL - $1"; }

# detect <args...> -> sets $out to stdout and $code to the exit status. Every case needs
# both halves of the contract — what was printed *and* which of 0 / 3 was returned — and
# capturing them together is fiddly enough to be worth naming once: command substitution
# would otherwise leave $? describing the assignment, so `code=$?` has to come from the
# line immediately after it. stderr is dropped because no case asserts on it.
#
# The whole argument list is forwarded rather than a single repo root, because the script
# is called two ways: with the root alone, and with `--issue <body-file>` before it.
detect() {  # detect <args...> -> runs the script, sets $out/$code
  out="$("$DETECT" "$@" 2>/dev/null)"
  code=$?
}

# matched -> true when the last detect() answered the contract: exit 0 and $want on
# stdout. Every case asserts those same two halves against those same two variables, so
# the pair is spelled out once here instead of at each call site — and a case that reads
# `matched && ok` says what it is checking, where the raw conjunction only said how.
matched() { [[ "$code" == 0 ]] && [[ "$out" == "$want" ]]; }

# note <label> -> appends one parenthesised note to $misread, saying which of a case's
# seeded repos answered wrong and what it answered instead. Three cases below seed several
# repos each and still report as one case, so each has to carry the label along with both
# halves of the mismatch; naming the wording once keeps those three notes identical, which
# is what makes them readable side by side when a case fails on more than one repo.
note() { misread="$misread ($1: exit=$code want 0, stdout='$out' want '$want')"; }

# 0. an issue that names its own test command outranks everything, the override file
# included. `--issue <body-file>` hands the script the issue body the conductor has already
# read, and the first line of it matching `Test command:` is the answer, printed verbatim.
#
# The seeded repo arms every rule below it: a `.veri/test-command`, which until now beat
# every inference; a package.json with a test script; a Makefile with a test target. So an
# answer of the issue's command can only mean the body was consulted ahead of all three —
# on a repo with no markers, any of them could have been what answered instead.
#
# Two `Test command:` lines are seeded because the claim is about the *first*: a body that
# names the command again further down — in a note, a quotation, a later section — must not
# have the last mention win. The line that must answer carries flags no rule could ever
# infer, so any normalising or re-quoting of it shows up in stdout.
#
# The body is a file rather than the issue text on stdin because that is what the conductor
# has: it saves the issue body to `.tdd/issue-<n>.md` in preflight, and every leaf is
# launched with that path.
want='bin/docs-suite --only docs --strict'
repo="$work/issue-command"
body="$work/issue-command-body.md"
mkdir -p "$repo/.veri"
printf '%s\n' 'bin/run-suite --all --strict' > "$repo/.veri/test-command"
printf '{"scripts":{"test":"jest"}}\n' > "$repo/package.json"
printf 'test:\n\techo hi\n' > "$repo/Makefile"
printf '## Notes\n\nTest command: %s\n\nTest command: make other-test\n' "$want" > "$body"

detect --issue "$body" "$repo"

matched \
  && ok || no "--issue: the body's first Test command: line beats .veri/test-command and every inference, printed verbatim (exit=$code want 0, stdout='$out' want '$want')"

# 0b. the other half of rule 0: when the issue names no command, the rule steps aside and the
# answer is exactly the one veri gave before `--issue` existed. Case 0 says the line wins when
# it is there; this says nothing else moved when it is not — which is the half a fix can
# quietly get wrong, by answering "" for a silent body, or by exiting 3 once the body has been
# read, or by consuming the `--issue <file>` words and then reading the repo root out of the
# wrong argument.
#
# Three seeded repos, one case, because "today's precedence, unchanged" is a single claim and
# the only way to observe it is at each of its three outcomes: the override file still wins
# (a `.veri/test-command` with a package.json armed beside it), an inference still fires where
# there is no override (a Makefile `test:` target over a pytest.ini), and a repo with no marker
# at all still prints nothing and exits 3. A rule 0 that swallowed the answer would pass on
# one of the three and fail on the others.
#
# Each repo is asked twice, once per spelling the step names — `--issue <body-file>` with a
# body that carries no `Test command:` line, and no `--issue` at all — so the label in
# `misread` carries the argument form as well as the repo. The bare form is the pre-`--issue`
# baseline the `--issue` form must equal, and having both side by side is what makes a
# divergence between them legible.
#
# The body mentions a command only in prose. That is the near miss worth seeding: a rule that
# looked for the *command* anywhere in the body rather than for a line opening with the marker
# would answer `make docs-test` here, on an issue that never asked for it.
#
# `note` is not reused: it spells `want 0` into its wording, and the third repo's want is exit
# 3 with empty stdout. `matched` is likewise the answering half only, so both halves are
# asserted here against a per-repo `wantcode`, the way cases 4b and 8 assert theirs directly.
misread=""
body="$work/silent-body.md"
printf '## Notes\n\nNo line here names the run command; `make docs-test` appears in prose only.\n' > "$body"

for shape in override inference none; do
  repo="$work/silent-$shape"
  case "$shape" in
    override)
      mkdir -p "$repo/.veri"
      printf '%s\n' 'bin/run-suite --all --strict' > "$repo/.veri/test-command"
      printf '{"scripts":{"test":"jest"}}\n' > "$repo/package.json"
      want='bin/run-suite --all --strict' ; wantcode=0 ;;
    inference)
      mkdir -p "$repo"
      printf 'test:\n\techo hi\n' > "$repo/Makefile"
      : > "$repo/pytest.ini"
      want='make test' ; wantcode=0 ;;
    none)
      mkdir -p "$repo/src"
      printf '# demo\n\nRun the test suite however you like.\n' > "$repo/README.md"
      printf 'int main(void) { return 0; }\n' > "$repo/src/main.c"
      want='' ; wantcode=3 ;;
  esac

  detect --issue "$body" "$repo"
  [[ "$code" == "$wantcode" ]] && [[ "$out" == "$want" ]] \
    || misread="$misread ($shape, --issue: exit=$code want $wantcode, stdout='$out' want '$want')"

  detect "$repo"
  [[ "$code" == "$wantcode" ]] && [[ "$out" == "$want" ]] \
    || misread="$misread ($shape, no --issue: exit=$code want $wantcode, stdout='$out' want '$want')"
done

[[ -z "$misread" ]] \
  && ok || no "a body with no Test command: line, and no --issue at all, both leave today's precedence untouched: override file, then inferences, exit 3 —$misread"

# 0c. the marker where veri's own issues actually write it: mid-line, in the middle of a
# sentence, with the command in a backtick span. Case 0 pins the shape #120's tests used —
# the marker at the start of the line, the command bare and running to the end of it — and
# a rule that keys on the line *opening* with the marker passes that and misses this one
# entirely. Measured on main, that is what #71, #80 and #123 hit: each names `make
# docs-test` in its Notes and each answers `make test`, so a docs issue baselines the wrong
# suite and #121 derives its leaves' timeout from it.
#
# One line carries both halves of the claim at once. `nothing before the marker` is the
# prose and the two backtick spans preceding it — a rule that answered with the whole line,
# or with the first backtick span on it, would say `docs/wt/app.js` here. `nothing after
# the closing backtick` is the trailing `. More prose.` — the shape that made #75's answer
# worse than a miss, since a command with a full stop and a sentence glued to it cannot
# run at all.
#
# The seeded repo arms the fall-through rather than leaving it bare, and arms it with the
# Makefile `test:` target specifically: `make test` is the exact wrong answer the three
# real issues get today, so a run that misses the marker reports the production bug in the
# words the issue measured it in, instead of an anonymous exit 3.
want='make docs-test'
repo="$work/issue-inline-backticks"
body="$work/issue-inline-backticks-body.md"
mkdir -p "$repo"
printf 'test:\n\techo hi\n' > "$repo/Makefile"
printf '## Notes\n\n`docs/wt/app.js`, `docs/wt/style.css`. Test command: `make docs-test`. More prose.\n' > "$body"

detect --issue "$body" "$repo"

matched \
  && ok || no "a mid-line Test command: followed by a backtick span answers the span alone, dropping the prose on either side (exit=$code want 0, stdout='$out' want '$want')"

# 0d. the marker at the *start* of the line, with the command still in a backtick span and
# prose still running past it. This is #75's shape, and it is the one measured on main as
# worse than a miss: rule 0 found the marker, printed everything after it, and answered
# '`make docs-test`. `docs/walkthrough.html` is GENERATED — never hand-edit it.' — a string
# that cannot run at all, handed to every leaf as its test command. Case 0 pins the bare
# spelling, where the rest of the line *is* the command; case 0c pins the backtick span
# found mid-sentence. Neither says what happens when the two shapes meet: the marker where
# #120's rule always looked for it, and the command wrapped the way veri's own issues write
# it. A rule that treated a line-start marker as the bare spelling and only unwrapped the
# mid-line one passes both of those and fails this.
#
# The prose after the closing backtick is seeded with a full stop, a second backtick span
# and an em dash — the bytes of #75's real Notes line — so a stdout that carried any of it
# is legible as the wrong answer rather than as a near miss on whitespace.
#
# The seeded repo arms the Makefile `test:` fall-through for the same reason case 0c does:
# a run that loses the marker entirely reports `make test`, the wrong answer the real issues
# get, instead of an anonymous exit 3.
want='make docs-test'
repo="$work/issue-linestart-backticks"
body="$work/issue-linestart-backticks-body.md"
mkdir -p "$repo"
printf 'test:\n\techo hi\n' > "$repo/Makefile"
printf '## Notes\n\nTest command: `make docs-test`. `docs/walkthrough.html` is GENERATED — never hand-edit it.\n' > "$body"

detect --issue "$body" "$repo"

matched \
  && ok || no "a line starting Test command: followed by a backtick span answers the span alone, not the rest of the line (exit=$code want 0, stdout='$out' want '$want')"

# 0e. the two shapes the backtick handling must leave exactly as they were: a marker whose
# command is written bare, and a body carrying no marker at all. Cases 0c and 0d say what a
# backtick span means; this says what everything *outside* a backtick span still means, and
# both halves are what unwrapping can quietly take away. A rule that cut every command at a
# backtick — rather than only one that opens with it — mangles `bin/run --all`, which has no
# backticks to cut at; a rule that loosened which lines count as the marker starts answering
# for bodies that never named a command, and the fall-through those bodies rely on never runs.
#
# Two seeded repos, one case, because it is one claim — "recognising the span changed nothing
# on either side of it" — observed at its two outcomes. The bare command carries a flag no
# inference could ever produce, so any trimming, re-quoting or unwrapping of it shows up in
# stdout; the silent body's repo arms the Makefile `test:` target, so falling through has a
# visible answer instead of an anonymous exit 3, and a rule 0 that answered anyway is legible
# as the wrong command rather than as exit 3.
misread=""
for shape in bare silent; do
  repo="$work/unwrap-untouched-$shape"
  body="$work/unwrap-untouched-$shape-body.md"
  mkdir -p "$repo"
  printf 'test:\n\techo hi\n' > "$repo/Makefile"
  case "$shape" in
    bare)
      printf '## Notes\n\nTest command: bin/run --all\n' > "$body"
      want='bin/run --all' ;;
    silent)
      printf '## Notes\n\nNothing here names a run command.\n' > "$body"
      want='make test' ;;
  esac

  detect --issue "$body" "$repo"

  matched || note "$shape"
done

[[ -z "$misread" ]] \
  && ok || no "a bare Test command: at line start still answers verbatim, and a body with no marker still falls through to the old precedence —$misread"

# 0f. the four bodies this issue was opened about, verbatim, as veri's own issue tracker
# holds them: #71, #75, #80 and #123, each a docs issue that names `make docs-test` in its
# Notes. Cases 0c and 0d pin the two *shapes* — marker mid-line, marker at line start, the
# command in a backtick span either way — on one hand-written line each. This case pins the
# real thing, and that is a different claim: a hand-written line is the shape as the test
# author understood it, and the whole of #131 is that what veri's issues actually write was
# not that. Measured on main, all four answered `make test`, except #75, which answered a
# string with a full stop and a sentence glued to it that no shell can run.
#
# The bodies are committed under `fixtures/detect-test-command/` rather than printf'd into
# `$work` like every case above, because they are evidence, not a seeded shape: the point is
# that nobody trimmed them into something the rule already handles. So everything a real body
# carries and a hand-written line does not is in play — thirty to fifty-odd lines of
# headings, `- [ ]` criteria, em dashes, `#70`-style cross-references, and backtick spans in
# nearly every sentence, #123's naming HTML elements (`<select>`, `<button>`) inside them.
# Each body's marker sits in its `## Notes`, three of the four with prose and several spans
# ahead of it on the line, and all four with a full stop or a whole sentence behind it.
#
# The four are not one shape repeated. #75's marker opens its line, which is the spelling
# #120's rule already looked for and the one that answered worst on main; #71, #80 and #123
# bury theirs mid-sentence behind a list of the files to touch. Between them they are both
# halves of what 0c and 0d pin, as the issues really wrote it rather than as a test author
# retyped it.
#
# `make test` specifically is what they answered before, so the seeded repo arms the Makefile
# `test:` target for the same reason cases 0c and 0d do: a run against a rule that has lost
# the marker reports the exact wrong answer the issue measured, rather than an anonymous
# exit 3.
#
# One repo, seeded once and reused across the four: the repo is only there to have a
# fall-through worth misreading, and rule 0 answers before any file in it is opened, so
# nothing a body does could carry over into the next. Four fixtures, one case, the same way
# the three node runners and the three pytest spellings are one case each — "the real bodies
# answer their own command" is one claim, observed four times, and `misread` collects every
# issue that got it wrong so a failure names all of them rather than only the first.
want='make docs-test'
misread=""
repo="$work/real-issue-bodies"
mkdir -p "$repo"
printf 'test:\n\techo hi\n' > "$repo/Makefile"

for n in 71 75 80 123; do
  detect --issue "$HERE/fixtures/detect-test-command/issue-$n.md" "$repo"

  matched || note "#$n"
done

[[ -z "$misread" ]] \
  && ok || no "the real bodies of #71, #75, #80 and #123 each answer make docs-test —$misread"

# 0g. the marker *quoted* rather than stated. #131 made the marker count anywhere on a line,
# and with it a mere mention of the marker — a body that writes the two words inside a
# backtick span, talking about the line rather than writing one — became an answer. First
# match wins, so that mention is fatal: the real line further down cannot overrule it.
#
# This is #144's own body, measured 2026-09-13: its line 3 quotes the marker while
# describing how a leaf finds its command, and its Notes state it with `make test` fifty-odd
# lines later. Rule 0 answered from line 3, printing the prose that followed the closing
# backtick — a sentence fragment, handed to the conductor as the shell command for the
# baseline and every leaf.
#
# The seeded body is that shape and only that shape: a quoted marker high up whose line
# carries prose behind it, and a stated marker in the Notes. The prose behind the quote is
# what makes this fail loudly rather than quietly — a body that quoted the marker at the very
# end of its line would name no command and be skipped already, by the `-n "$cmd"` test rule
# 0 has had since #120.
#
# The fall-through is armed with a `.veri/test-command`, not with the Makefile `test:` target
# cases 0c–0f use, and that is the half of the seeding worth reading twice: `make test` is the
# answer wanted here, so a Makefile would hand the same bytes to a rule 0 that skipped the
# body entirely, and the case would pass without the stated line ever having been consulted.
# The override gives the three outcomes three different stdouts — `make test` only if the
# stated line answered, `bin/run-suite --all --strict` if rule 0 found nothing at all, and the
# prose fragment if the quote answered — so a failure says which of the two mistakes was made.
#
# `$want` seeds the stated line as well as checking stdout, the same reason case 0 does it:
# "answers `make test`" is a claim about bytes, so the bytes written in are the bytes expected
# out.
want='make test'
repo="$work/quoted-marker"
body="$work/quoted-marker-body.md"
mkdir -p "$repo/.veri"
printf '%s\n' 'bin/run-suite --all --strict' > "$repo/.veri/test-command"
printf '# Leaves run one suite instead of the full one\n\nSince #120 a leaf takes its command from the issue body: the `Test command:` line names it, and #131 made that line count mid-sentence.\n\n## Notes\n\nTest command: %s\n' "$want" > "$body"

detect --issue "$body" "$repo"

matched \
  && ok || no "a marker quoted inside a backtick span does not answer, and the later line stating it with make test does (exit=$code want 0, stdout='$out' want '$want')"

# 0h. the body whose *only* marker is a quotation. Case 0g pins the half where a later line
# states the marker, so skipping the quote has somewhere to land; this pins the half where it
# has nowhere — rule 0 has to step aside entirely and let the next rule answer, exactly as it
# does for a body that never wrote the two words at all. A fix that skipped the quoted marker
# but then treated "rule 0 read the body" as itself an answer — exit 3, or an empty command —
# passes 0g and fails here, and that is the whole of what this case is for.
#
# "exactly as a body with no marker does" is a comparison, so both sides of it are seeded and
# asked: two bodies differing only in whether the two words appear inside that backtick span,
# one case, the way cases 0b and 0e pair a shape against its baseline. The `absent` body is the
# pre-existing behaviour the `quoted` body must now equal; having them side by side is what
# makes a divergence between them legible rather than a bare wrong answer.
#
# The quoted marker is seeded with prose running past its closing backtick, and that is
# load-bearing for the same reason it is in 0g: a marker quoted at the very end of its line
# names no command and is skipped already, by the `-n "$cmd"` test rule 0 has had since #120.
# With prose behind it, an unguarded rule 0 answers ` line names it, and #131 made that line
# count mid-sentence.` — a sentence fragment, which is what makes this fail loudly.
#
# The fall-through is armed with a `.veri/test-command` rather than the Makefile `test:` target,
# again as in 0g: its bytes are ones no inference could produce, so the three outcomes have
# three different stdouts — the override only if rule 0 stood aside, the prose fragment if the
# quote answered, and empty-with-exit-3 if rule 0 swallowed the body.
want='bin/run-suite --all --strict'
misread=""
repo="$work/only-quoted-marker"
mkdir -p "$repo/.veri"
printf '%s\n' "$want" > "$repo/.veri/test-command"

for shape in quoted absent; do
  body="$work/only-quoted-marker-$shape-body.md"
  case "$shape" in
    quoted) phrase='the `Test command:` line names it' ;;
    absent) phrase='a line in its Notes names it' ;;
  esac
  printf '# Leaves run one suite instead of the full one\n\nSince #120 a leaf takes its command from the issue body: %s, and #131 made that line count mid-sentence.\n\n## Notes\n\nFiles: `skills/tdd/scripts/detect-test-command.sh`.\n' "$phrase" > "$body"

  detect --issue "$body" "$repo"

  matched || note "$shape"
done

[[ -z "$misread" ]] \
  && ok || no "a body whose only marker sits inside a backtick span falls through to the next rule, exactly as a body with no marker does —$misread"

# 0i. both markers on the *same* line: the quotation first, the statement behind it. Cases
# 0g and 0h put the quote and the real line in different paragraphs, so skipping the quote
# only ever has to mean "read the next line". This says what skipping has to mean within one
# line — go on to the next marker on it — and a fix that treats a quoted marker as a verdict
# on the whole line passes 0g and 0h and answers `make test` here, on an issue that stated
# `make docs-test` in the same sentence.
#
# The shape is one veri's own issues write: a sentence that names the mechanism and then uses
# it, which is exactly how #145's body and this test file's own commentary read. `%%` takes
# the prefix at the *first* marker and `#` the rest at the same one, so the two halves are cut
# either side of the quotation — the stated marker is in `rest`, downstream of the guard, and
# is reachable only by scanning on.
#
# The seeded repo arms the Makefile `test:` fall-through, as cases 0c–0f do rather than 0g–0h,
# because here the three outcomes already have three different stdouts without an override:
# `make docs-test` only if the scan went on past the quote, `make test` if the quoted marker
# condemned the whole line, and ` line names it. Test command: ` — the text between the quote's
# closing backtick and the stated command's opening one — if the quote answered.
#
# The trailing `. More prose.` is the same guard 0c seeds: it keeps a stdout that carried the
# tail of the line legible as the wrong answer rather than as a near miss on whitespace.
want='make docs-test'
repo="$work/quoted-then-stated"
body="$work/quoted-then-stated-body.md"
mkdir -p "$repo"
printf 'test:\n\techo hi\n' > "$repo/Makefile"
printf '## Notes\n\nA leaf takes its command from the `Test command:` line, so: Test command: `%s`. More prose.\n' "$want" > "$body"

detect --issue "$body" "$repo"

matched \
  && ok || no "a line carrying a quoted marker and then a stated one answers the stated command (exit=$code want 0, stdout='$out' want '$want')"

# 0j. the quotation that names a *suite*: a development issue whose prose quotes a docs
# issue's marker together with `make docs-test`, and whose Notes state the marker with
# `make test`. Case 0g pins the same two-line shape with prose behind the quote, and what
# an unguarded rule 0 answers there is a sentence fragment — a command no shell can run,
# so the conductor's baseline errors and the run bails in the open. This is the failure the
# issue calls the worse one, and it is worse because it does not bail: what follows the
# quoted marker here names a real suite, so the baseline goes green on the docs tests and
# every leaf of a *development* issue then runs them, which #143 forbids outright. A wrong
# answer that runs is the one nothing downstream catches.
#
# The quotation is written the way a body actually writes it — marker and command inside one
# backtick span, describing what a docs issue says rather than saying it — and the prose
# running past the closing backtick is the same guard 0g and 0h seed: a quotation at the very
# end of its line names no command and is skipped already, by the `-n "$cmd"` test rule 0 has
# had since #120.
#
# The fall-through is armed with a `.veri/test-command` rather than the Makefile `test:`
# target, for the reason 0g spells out: `make test` is the answer wanted, so a Makefile would
# hand those same bytes to a rule 0 that never consulted the body and the case would pass
# without the stated line answering. With the override, the three outcomes have three
# stdouts — `make test` only if the stated line answered, `bin/run-suite --all --strict` if
# rule 0 found nothing at all, and a string opening `make docs-test` if the quotation
# answered, which is the docs suite legible in the failure message.
want='make test'
repo="$work/quoted-docs-command"
body="$work/quoted-docs-command-body.md"
mkdir -p "$repo/.veri"
printf '%s\n' 'bin/run-suite --all --strict' > "$repo/.veri/test-command"
printf '# Rule 0 answers a development issue with its own suite\n\nA docs issue writes `Test command: make docs-test` in its Notes, so every leaf on it runs the docs suite. This issue is not a docs issue.\n\n## Notes\n\nFiles: `skills/tdd/scripts/detect-test-command.sh`.\n\nTest command: %s\n' "$want" > "$body"

detect --issue "$body" "$repo"

matched \
  && ok || no "a development issue quoting a docs issue's marker with make docs-test answers the make test its Notes state (exit=$code want 0, stdout='$out' want '$want')"

# 0k. the body this issue was opened about, verbatim, as veri's own tracker holds it: #144,
# read on 2026-09-13. Cases 0g–0j pin the *shapes* — a quoted marker with the real line a
# paragraph below, a body whose only marker is quoted, both markers on one line, a quotation
# naming a suite — on one or two hand-written lines each. This pins the real thing, and that
# is a different claim, for the reason 0f states about #71, #75, #80 and #123: a hand-written
# line is the shape as the test author understood it, and what an issue actually writes was
# not that. It is also the only case here whose failure was *observed* rather than
# constructed — measured at 06:49 that morning, before any of this was written.
#
# The fixture is committed under `fixtures/detect-test-command/` beside those four rather than
# printf'd into `$work`, and for the same reason: it is evidence, so nobody trims it into
# something the rule already handles. Everything a real body carries is therefore in play —
# a measurements table whose cells are backtick spans, `- [x]` criteria, em dashes, `#121`-style
# cross-references, `{{TEST_CMD}}` in braces, and paths in spans in nearly every sentence.
# What the case is about sits at its two ends: line 3 quotes the marker inside a backtick
# span while naming the issues that gave a leaf its command, and line 65 states it with
# `make test` sixty-odd lines later, bare and running to the end of the line.
#
# Measured on main, rule 0 answered from line 3 with ` line). Those made a slow suite
# *survivable* for a leaf. This issue makes a leaf run the slow suite *fewer times*.` — the
# prose trailing the quote's closing backtick, handed to the conductor as the shell command
# for the baseline and every leaf of that run. The #144 conductor caught it by hand; an
# unattended one baselines on a sentence fragment and bails.
#
# The fall-through is armed with a `.veri/test-command` rather than the Makefile `test:`
# target the 0f repo uses, for the reason 0g spells out: `make test` is the answer wanted
# here, so a Makefile would hand those same bytes to a rule 0 that never consulted the body
# and the case would pass without line 65 answering. With the override the three outcomes
# have three stdouts — `make test` only if line 65 answered, `bin/run-suite --all --strict`
# if rule 0 found nothing at all, and the prose fragment above if line 3 answered.
want='make test'
repo="$work/issue-144-body"
mkdir -p "$repo/.veri"
printf '%s\n' 'bin/run-suite --all --strict' > "$repo/.veri/test-command"

detect --issue "$HERE/fixtures/detect-test-command/issue-144.md" "$repo"

matched \
  && ok || no "#144's real body, whose line 3 quotes the marker and whose line 65 states it, answers make test (exit=$code want 0, stdout='$out' want '$want')"

# 1. the .veri/test-command override wins over every inference, and its line is printed
# verbatim. The repo is seeded so that *both* of the highest-precedence inferences would
# otherwise fire (package.json with a test script → `npm test`; Makefile with a test
# target → `make test`), so a stdout of the override line can only mean the override was
# consulted first, not that inference happened to agree. The command itself is one no
# rule could ever infer — flags and all — so any normalising or re-quoting shows up.
#
# One name for the command, used to seed the file and to check stdout: "verbatim" is the
# claim, so the bytes written in and the bytes expected out must be the same bytes.
want='bin/run-suite --all --strict'
repo="$work/override"
mkdir -p "$repo/.veri"
printf '%s\n' "$want" > "$repo/.veri/test-command"
printf '{"scripts":{"test":"jest"}}\n' > "$repo/package.json"
printf 'test:\n\techo hi\n' > "$repo/Makefile"

detect "$repo"

matched \
  && ok || no ".veri/test-command beats package.json and Makefile, printed verbatim (exit=$code want 0, stdout='$out' want '$want')"

# 2. a package.json carrying a scripts.test entry names the node runner, and which runner is
# decided by the lockfile lying beside it: bare → `npm test`, pnpm-lock.yaml → `pnpm test`,
# yarn.lock → `yarn test`. Three seeded repos, one case, because the three are one rule —
# the same marker file answered three ways depending on what else the repo committed. A
# runner chosen without consulting the lockfile passes the first sub-check and fails the
# other two, which is exactly the confusion worth catching.
#
# Nothing here needs node installed: the script reads files, it never runs the command it
# prints.
#
# The runner name is the whole of what varies — it names the repo, the lockfile to seed and,
# with ` test` appended, the expected stdout — so the loop mentions each one once and the
# three sub-checks stay one case: `misread` collects whichever runners answered wrong, and
# only a run that collected nothing passes.
misread=""
for runner in npm pnpm yarn; do
  want="$runner test"
  repo="$work/node-$runner"
  mkdir -p "$repo"
  printf '{"scripts":{"test":"jest"}}\n' > "$repo/package.json"
  case "$runner" in
    pnpm) printf 'lockfileVersion: 9.0\n' > "$repo/pnpm-lock.yaml" ;;
    yarn) printf '# yarn lockfile v1\n' > "$repo/yarn.lock" ;;
  esac

  detect "$repo"

  matched || note "$runner"
done

[[ -z "$misread" ]] \
  && ok || no "package.json scripts.test: bare → npm test, pnpm-lock.yaml → pnpm test, yarn.lock → yarn test —$misread"

# 3. a Makefile declaring a `test:` target names `make test` — and it does so even when the
# repo also carries a pytest marker, which is the half of this case worth seeding. The two
# markers together are the only way to observe the precedence: on a Makefile-only repo,
# `make test` on stdout says nothing about ordering, because no other rule was in the running.
#
# This is the reordering the issue calls for. Today's SKILL.md tries npm, pytest, make,
# unittest, so this repo would answer `pytest -q`; a repo that wrote a `test` target chose
# it deliberately — very often precisely to wrap the pytest invocation with whatever else
# the suite needs — so the target wins and pytest.ini is left to answer for repos that
# wrote no target at all.
#
# The pytest marker is a bare pytest.ini: an empty file is enough, since rule 4 keys on the
# file existing, not on anything inside it. No Makefile, no pytest and no python are needed
# to run this — the script reads the two filenames and never executes what it prints.
want='make test'
repo="$work/make-over-pytest"
mkdir -p "$repo"
printf 'test:\n\techo hi\n' > "$repo/Makefile"
: > "$repo/pytest.ini"

detect "$repo"

matched \
  && ok || no "Makefile with a test: target beats pytest.ini (exit=$code want 0, stdout='$out' want '$want')"

# 4. a python repo that declares pytest configuration names `pytest -q`. The three spellings
# pytest documents are one rule — a bare `pytest.ini`, a `pyproject.toml` carrying a
# `[tool.pytest` section, or a `setup.cfg` carrying a `[tool:pytest]` one — so they are three
# seeded repos inside one case, the same way the three node runners are. Each spelling is a
# repo saying "pytest runs here", and `-q` because the conductor reads the exit status, not
# the dots.
#
# The `pytest.ini` repo seeds an empty file on purpose: the rule keys on the filename, and a
# repo whose pytest settings all live in command-line flags or tox still commits the empty
# marker. The other two need the section header and nothing else, because neither filename is
# a claim about the test runner on its own — both are packaging metadata any python project
# may carry — so the header has to be found inside the file. Each carries a second line under
# it, so the header is not also the last byte of the file. `ini_options` is the suffix real
# pyproject.toml repos write, and including it checks the rule matches the prefix rather than
# demanding the whole bare header; setup.cfg's header is pytest's own colon spelling for that
# file, `[tool:pytest]`, not the dot pyproject.toml uses.
#
# No repo here needs pytest or python installed: the script reads these three files and never
# runs the command it prints.
want='pytest -q'
misread=""
for marker in pytest.ini pyproject.toml setup.cfg; do
  repo="$work/py-$marker"
  mkdir -p "$repo"
  case "$marker" in
    pytest.ini)     : > "$repo/pytest.ini" ;;
    pyproject.toml) printf '[tool.pytest.ini_options]\naddopts = "-ra"\n' > "$repo/pyproject.toml" ;;
    setup.cfg)      printf '[tool:pytest]\naddopts = -ra\n' > "$repo/setup.cfg" ;;
  esac

  detect "$repo"

  matched || note "$marker"
done

[[ -z "$misread" ]] \
  && ok || no "pytest.ini, or pyproject.toml with a [tool.pytest section, or setup.cfg with a [tool:pytest] one, yields pytest -q —$misread"

# 4b. the other half of rule 4's setup.cfg spelling: a `setup.cfg` with no `[tool:pytest]`
# section is not a pytest marker, so the repo prints nothing and exits 3. The case above
# says the header is found; this one says the *filename* is not what answers. A rule that
# keyed on `setup.cfg` existing — the way it legitimately keys on `pytest.ini` existing —
# passes case 4 and fails here, and that is the confusion worth catching: setup.cfg is
# packaging metadata any python project may carry, whatever runs its suite.
#
# `[metadata]` is what such a repo really holds, and it is seeded with a key under it so
# the file is not merely a bare header. Nothing else is seeded: any other marker would be
# answered by another rule and the repo would never reach rule 4's verdict at all.
#
# Both halves are the opposite of `matched`'s — empty stdout, and 3 rather than 0 — so this
# asserts them directly, the same way case 8 does. 3 is "nothing to do", not an error: it
# is the conductor's cue to ask the human, which is the right outcome for a repo that never
# said pytest runs here.
repo="$work/setupcfg-no-pytest"
mkdir -p "$repo"
printf '[metadata]\nname = demo\n' > "$repo/setup.cfg"

detect "$repo"

[[ "$code" == 3 ]] && [[ -z "$out" ]] \
  && ok || no "a setup.cfg with no [tool:pytest] section prints nothing and exits 3 (exit=$code want 3, stdout='$out' want '')"

# 4c. the setup.cfg spelling sits where the rest of rule 4 sits, and the only way to observe
# that is to seed it against a neighbour on each side. Case 4 says a lone setup.cfg answers
# `pytest -q`; a lone repo says nothing about ordering, because no other rule was in the
# running. So: one repo pairs it with the rule above (a Makefile `test:` target, which must
# still win) and one pairs it with the rule below (a `go.mod`, which must still lose). Two
# seeded repos, one case, the same shape as the node runners and the three pytest spellings —
# "the new spelling changed no precedence" is a single claim about a single position.
#
# This is the half a fix can quietly get wrong: recognising setup.cfg in a rule of its own,
# placed before make or after go, passes case 4 and fails here. Both repos carry the header
# inside setup.cfg rather than the bare filename, since that is what case 4b established is
# required to make the claim at all.
#
# No Makefile, no go and no pytest are needed to run this: the script reads these filenames
# and the one header, and never executes the command it prints.
misread=""
for other in Makefile go.mod; do
  repo="$work/setupcfg-vs-$other"
  mkdir -p "$repo"
  printf '[tool:pytest]\naddopts = -ra\n' > "$repo/setup.cfg"
  case "$other" in
    Makefile) printf 'test:\n\techo hi\n' > "$repo/Makefile" ; want='make test' ;;
    go.mod)   : > "$repo/go.mod"                             ; want='pytest -q' ;;
  esac

  detect "$repo"

  matched || note "$other"
done

[[ -z "$misread" ]] \
  && ok || no "a [tool:pytest] setup.cfg loses to a Makefile test: target and beats go.mod —$misread"

# 5. the two compiled stacks each name their toolchain's own runner: a `go.mod` yields
# `go test ./...`, a `Cargo.toml` yields `cargo test`. One case, two seeded repos, the same
# shape as the node runners and the two pytest spellings — two markers answering with two
# different commands is still one rule, "the manifest file names the stack's test runner".
#
# Both markers are the manifest at the repo root that its toolchain requires, so the
# filename alone is the whole claim and an empty file is enough to make it — unlike
# pyproject.toml above, neither name belongs to any other kind of project. `./...` is go's
# own spelling for "every package beneath here", without which `go test` would run only the
# root package and quietly skip the rest of the suite; `cargo test` already walks the whole
# crate, so it needs no argument.
#
# Neither repo needs go or rust installed: the script reads the two filenames and never
# runs the command it prints.
misread=""
for marker in go.mod Cargo.toml; do
  case "$marker" in
    go.mod)     want='go test ./...' ;;
    Cargo.toml) want='cargo test' ;;
  esac
  repo="$work/compiled-$marker"
  mkdir -p "$repo"
  : > "$repo/$marker"

  detect "$repo"

  matched || note "$marker"
done

[[ -z "$misread" ]] \
  && ok || no "go.mod yields go test ./..., Cargo.toml yields cargo test —$misread"

# 7. the last rule before giving up: a repo whose only sign of a suite is a `tests/`
# directory holding `test_*.py` names `python3 -m unittest discover -q`. This is the
# stdlib fallback for a python project that committed no runner configuration at all —
# no pytest.ini, no pyproject.toml, no Makefile — which is why the seeded repo carries
# the test file and nothing else: any other marker would have been answered by a rule
# above, and the repo would never reach this one.
#
# Unlike every rule before it, the marker is not a file at a known path but a *pattern*
# inside a directory, so the file is named `test_foo.py` rather than left as an empty
# `tests/` — `discover` finds cases by that filename pattern, and a `tests/` directory of
# fixtures or helpers is no claim that a suite lives there. Its contents are irrelevant:
# the script matches the name and never imports or runs the file.
#
# `python3` and not `python`, because `python` is absent on a modern macOS and ambiguous
# where it exists; `-m unittest discover` because there is no runner script to call; `-q`
# to match the other rules, the conductor reading the exit status rather than the dots.
want='python3 -m unittest discover -q'
repo="$work/unittest-only"
mkdir -p "$repo/tests"
printf 'import unittest\n' > "$repo/tests/test_foo.py"

detect "$repo"

matched \
  && ok || no "a tests/ directory of test_*.py with no other marker yields python3 -m unittest discover -q (exit=$code want 0, stdout='$out' want '$want')"

# 8. the fall-through: a repo that matches no rule at all prints nothing and exits 3. This
# is the one case that asserts the *other* half of the contract, so it cannot use
# `matched` — that helper spells out the answering half, exit 0 with $want on stdout, and
# here both halves are the opposite: empty stdout, and 3 rather than 0. 3 is "nothing to
# do", not an error, and the conductor branches on it by asking the human, so a script
# that failed with 1 or 2 here would be read as broken plumbing instead of an honest
# "I cannot tell".
#
# The seeded repo is not an empty directory on purpose. An empty one would pass against a
# script that had no rules at all, so it says nothing about the rules having been asked and
# having declined; a repo with real content and no marker does. Both files are near misses,
# each one a thing a rule could plausibly have keyed on and must not: `README.md` mentions
# the word test in prose, and `src/main.c` is source under a directory named for source —
# neither is a runner configuration, and neither is `tests/test_*.py`.
#
# Nothing is printed because stdout is what the conductor captures as the command: a
# diagnostic written there would be run as if it were one, which is why the script keeps
# any explanation on stderr and the case checks stdout is empty rather than merely not the
# command.
repo="$work/no-markers"
mkdir -p "$repo/src"
printf '# demo\n\nRun the test suite however you like.\n' > "$repo/README.md"
printf 'int main(void) { return 0; }\n' > "$repo/src/main.c"

detect "$repo"

[[ "$code" == 3 ]] && [[ -z "$out" ]] \
  && ok || no "a repo matching nothing prints nothing and exits 3 (exit=$code want 3, stdout='$out' want '')"

# 9. no `--tier` flag means today's answer, even in a repo whose root CLAUDE.md now declares
# both tier markers (#338). The markers are new inputs a tier-aware call reads; a call that
# names no tier is every caller that existed before them, and it must go on getting the one
# command today's precedence chain picks — not the fast command, not the all command.
#
# One case over every single-command shape the chain knows, because "exactly as today" is
# one claim and it can only break shape by shape: a marker read ahead of rule 0 would take
# every repo, one read ahead of rule 3 only the ones below it. Each repo carries the same
# CLAUDE.md, stated plainly at the start of lines so that nothing but the missing flag keeps
# the markers from answering; the tier commands are spelled so that no rule could infer them.
# The `--issue` shape is asked with its body, so the issue's own line is today's winner there.
misread=""
body="$work/tier-issue-body.md"
printf '## Notes\n\nTest command: bin/issue-suite\n' > "$body"

for shape in override npm pnpm yarn make pytest.ini pyproject.toml setup.cfg go.mod Cargo.toml unittest issue; do
  repo="$work/untiered-$shape"
  mkdir -p "$repo"
  printf '# demo\n\nveri: fast tests: bin/fast-suite\nveri: all tests: bin/all-suite\n' > "$repo/CLAUDE.md"
  args=("$repo")
  case "$shape" in
    override)
      mkdir -p "$repo/.veri"
      printf '%s\n' 'bin/run-suite --all --strict' > "$repo/.veri/test-command"
      want='bin/run-suite --all --strict' ;;
    npm|pnpm|yarn)
      printf '{"scripts":{"test":"jest"}}\n' > "$repo/package.json"
      case "$shape" in
        pnpm) printf 'lockfileVersion: 9.0\n' > "$repo/pnpm-lock.yaml" ;;
        yarn) printf '# yarn lockfile v1\n' > "$repo/yarn.lock" ;;
      esac
      want="$shape test" ;;
    make)
      printf 'test:\n\techo hi\n' > "$repo/Makefile"
      want='make test' ;;
    pytest.ini)     : > "$repo/pytest.ini" ; want='pytest -q' ;;
    pyproject.toml) printf '[tool.pytest.ini_options]\naddopts = "-ra"\n' > "$repo/pyproject.toml" ; want='pytest -q' ;;
    setup.cfg)      printf '[tool:pytest]\naddopts = -ra\n' > "$repo/setup.cfg" ; want='pytest -q' ;;
    go.mod)         : > "$repo/go.mod" ; want='go test ./...' ;;
    Cargo.toml)     : > "$repo/Cargo.toml" ; want='cargo test' ;;
    unittest)
      mkdir -p "$repo/tests"
      printf 'import unittest\n' > "$repo/tests/test_foo.py"
      want='python3 -m unittest discover -q' ;;
    issue)
      printf 'test:\n\techo hi\n' > "$repo/Makefile"
      args=(--issue "$body" "$repo")
      want='bin/issue-suite' ;;
  esac

  detect "${args[@]}"

  matched || note "$shape"
done

[[ -z "$misread" ]] \
  && ok || no "no --tier: CLAUDE.md's veri: fast/all tests: lines leave every single-command answer as today —$misread"

# 9b. the other half of case 9: a repo whose root CLAUDE.md declares both tier markers and
# carries *nothing else* any rule could key on. In case 9 some rule of the chain always
# answered, so a marker read *behind* every rule would never have been reached and could not
# have shown up there; here the markers are the only thing in the repo that could answer at
# all. With no `--tier` flag they must not: the chain matches nothing, so the call says what
# case 8 says of any repo matching nothing — nothing on stdout, exit 3 — rather than handing
# back either tier's command as if it were the single one.
repo="$work/untiered-markers-only"
mkdir -p "$repo"
printf '# demo\n\nveri: fast tests: bin/fast-suite\nveri: all tests: bin/all-suite\n' > "$repo/CLAUDE.md"

detect "$repo"

[[ "$code" == 3 ]] && [[ -z "$out" ]] \
  && ok || no "no --tier: a repo whose only markers are CLAUDE.md's veri: fast/all tests: lines prints nothing and exits 3 (exit=$code want 3, stdout='$out' want '')"

# 10. with both tier markers in the root CLAUDE.md and no `--issue`, each tier answers from
# its own marker (#338): `--tier fast` prints what `veri: fast tests:` names and `--tier all`
# what `veri: all tests:` names. One repo is asked both questions, because the claim is that
# the two lines are two answers — a script that read either marker for both tiers would get
# one of the two calls wrong.
#
# The repo also carries a Makefile with a `test:` target, so the single-command chain has an
# answer of its own (`make test`) that a tier call ignoring the markers would print instead.
# Both commands carry a doubled space and a quoted argument no rule could infer, so anything
# short of the bytes after the marker — collapsed whitespace, dropped quotes, a trimmed tail
# of flags — shows up in stdout.
misread=""
repo="$work/tiered-both"
mkdir -p "$repo"
printf 'test:\n\techo hi\n' > "$repo/Makefile"
printf '# demo\n\nveri: fast tests: bin/fast-suite  --only "unit tier" -q\nveri: all tests: bin/all-suite  --every "suite there is" -v\n' > "$repo/CLAUDE.md"

for tier in fast all; do
  case "$tier" in
    fast) want='bin/fast-suite  --only "unit tier" -q' ;;
    all)  want='bin/all-suite  --every "suite there is" -v' ;;
  esac

  detect --tier "$tier" "$repo"

  matched || note "$tier"
done

[[ -z "$misread" ]] \
  && ok || no "--tier fast/all: both CLAUDE.md markers declared, each tier prints its own marker's command byte for byte —$misread"

# 11. the tier markers are found and quoted the way rule 0's `Test command:` is (#338): a
# marker is recognised anywhere on a CLAUDE.md line, not only at its start, and one inside a
# backtick span is a mention rather than a declaration, so it is skipped and the scan goes on.
# Each tier's line in the seeded CLAUDE.md is preceded by a line that *quotes* that tier's
# marker with a command of its own, and then states the marker mid-sentence with the command
# in a backtick span — the shape rule 0 already reads in issue bodies (#131, #145). A script
# that took the quoted mention would print the `bin/quoted-*` prose; one that looked only at
# a line's start would miss both lines and fall back to the Makefile's `make test`.
misread=""
repo="$work/tiered-anywhere-quoted"
mkdir -p "$repo"
printf 'test:\n\techo hi\n' > "$repo/Makefile"
{
  printf '# demo\n\n'
  printf 'Leaves never read `veri: fast tests: bin/quoted-fast` as a declaration.\n'
  printf 'In this repo the fast tier is veri: fast tests: `bin/real-fast -q`. More prose.\n'
  printf 'Nor `veri: all tests: bin/quoted-all` either.\n'
  printf 'And the full suite is veri: all tests: `bin/real-all -v`. More prose.\n'
} > "$repo/CLAUDE.md"

for tier in fast all; do
  case "$tier" in
    fast) want='bin/real-fast -q' ;;
    all)  want='bin/real-all -v' ;;
  esac

  detect --tier "$tier" "$repo"

  matched || note "$tier"
done

[[ -z "$misread" ]] \
  && ok || no "--tier fast/all: a CLAUDE.md marker is recognised mid-line and one inside a backtick span is skipped, as the issue override marker is —$misread"

# 12. with neither tier marker declared, both tiers fall back to the single command today's
# precedence chain picks (#338): a `--tier` call in a repo that never opted into tiers must get
# the same answer a call without the flag gets, not nothing and not an error. Two repos, one per
# way of declaring nothing: one whose root CLAUDE.md exists but carries no marker line — only
# prose that names the tiers without the marker's words — beside a Makefile `test:` target, and
# one with no CLAUDE.md at all, whose `.veri/test-command` override is the chain's answer.
misread=""
repo="$work/tierless-claude-md"
mkdir -p "$repo"
printf 'test:\n\techo hi\n' > "$repo/Makefile"
printf '# demo\n\nThe fast tests and all tests are the same here.\n' > "$repo/CLAUDE.md"
repo="$work/tierless-no-claude-md"
mkdir -p "$repo/.veri"
printf '%s\n' 'bin/run-suite --all --strict' > "$repo/.veri/test-command"

for shape in claude-md no-claude-md; do
  case "$shape" in
    claude-md)    repo="$work/tierless-claude-md" ;    want='make test' ;;
    no-claude-md) repo="$work/tierless-no-claude-md" ; want='bin/run-suite --all --strict' ;;
  esac
  for tier in fast all; do
    detect --tier "$tier" "$repo"

    matched || note "$shape, $tier"
  done
done

[[ -z "$misread" ]] \
  && ok || no "--tier fast/all: with neither CLAUDE.md marker declared, both tiers print the single command the precedence chain picks —$misread"

# 13. with only `veri: all tests:` declared, `--tier fast` falls back to the single command the
# precedence chain picks (#338), rather than erroring, printing nothing, or borrowing the all
# tier's line. The repo's Makefile `test:` target is that chain's answer, and the all-tier
# command is spelled so that no rule could infer it — so `make test` can only mean the fast
# tier found no marker of its own and went on down the chain.
repo="$work/tiered-all-only"
mkdir -p "$repo"
printf 'test:\n\techo hi\n' > "$repo/Makefile"
printf '# demo\n\nveri: all tests: bin/all-only-suite --every -v\n' > "$repo/CLAUDE.md"
want='make test'
detect --tier fast "$repo"
matched \
  && ok || no "--tier fast: with only CLAUDE.md's veri: all tests: declared, fast falls back to the single-command chain (exit=$code want 0, stdout='$out' want '$want')"

# 14. an issue's own `--issue <body-file>` override answers `--tier all` for that run ahead of
# CLAUDE.md's `veri: all tests:` line (#338) — the narrower, per-run claim wins, as rule 0
# already has it win over `.veri/test-command` — while `--tier fast` in the same invocation
# does not take the issue's line: it answers from `veri: fast tests:` when CLAUDE.md declares
# it, and from the single-command chain behind the override when it does not. Two repos, one
# per way the fast tier can answer: one whose CLAUDE.md declares both markers, and one that
# declares only `veri: all tests:`. Each carries a Makefile `test:` target, so the chain's own
# answer is `make test`. Both are asked with the same issue body and both tiers, so the label
# in `misread` carries the repo and the tier.
misread=""
body="$work/tiered-issue-body.md"
printf '## Notes\n\nTest command: bin/issue-suite --only "this run" -q\n' > "$body"
repo="$work/tiered-issue-both"
mkdir -p "$repo"
printf 'test:\n\techo hi\n' > "$repo/Makefile"
printf '# demo\n\nveri: fast tests: bin/fast-suite --unit -q\nveri: all tests: bin/all-suite --every -v\n' > "$repo/CLAUDE.md"
repo="$work/tiered-issue-all-only"
mkdir -p "$repo"
printf 'test:\n\techo hi\n' > "$repo/Makefile"
printf '# demo\n\nveri: all tests: bin/all-suite --every -v\n' > "$repo/CLAUDE.md"

for shape in both all-only; do
  repo="$work/tiered-issue-$shape"
  for tier in fast all; do
    case "$shape,$tier" in
      both,fast)     want='bin/fast-suite --unit -q' ;;
      all-only,fast) want='make test' ;;
      *,all)         want='bin/issue-suite --only "this run" -q' ;;
    esac

    detect --tier "$tier" --issue "$body" "$repo"

    matched || note "$shape, $tier"
  done
done

[[ -z "$misread" ]] \
  && ok || no "--tier all/fast with --issue: the issue's Test command: line answers all ahead of CLAUDE.md's veri: all tests:, while fast still answers from veri: fast tests: or the single-command chain —$misread"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
