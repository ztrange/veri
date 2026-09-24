#!/usr/bin/env bash
# Unit test for the sizes CLAUDE.md states for this skill — like hermetic-suites.test.sh
# and skill-identity.test.sh this suite belongs to no single script: its subject is the
# inventory of `skills/tdd/scripts/` and the two sentences that count it. Zero-dependency
# plain-shell asserts, same idiom, picked up by `make test`'s glob by existing.
#
# Why this exists (issue #161): CLAUDE.md is the first thing an agent reads, and it counts
# the tree twice — once in the opening paragraph ("plus <n> bash scripts it calls") and
# once in *Testing idiom* ("<n> files for <m> scripts"). Both numbers were written by hand
# and neither has anything to hold it to the directory it describes, so every issue that
# adds a script — this one adds `detach-leaf.sh` — leaves them one further behind. A count
# that is wrong is worse than no count: an agent told there are eighteen scripts has been
# given a number it can act on, and the twenty-five on disk mean it was told the tree is
# smaller than it is before it has opened a single file.
#
# Contract under test — every count CLAUDE.md states is the number of files on disk:
#   1. The opening paragraph's script count is `skills/tdd/scripts/*.sh`.
#   2. *Testing idiom*'s suite count is `skills/tdd/scripts/tests/*.test.sh`, and the
#      script count in the same sentence is `skills/tdd/scripts/*.sh` again.
#
# One criterion — the stated counts match the files — and so one case: three numbers, but
# a document whose intro and testing section disagreed about how many scripts there are
# would be exactly as wrong as one whose single number was stale, and a reader repairing
# either repairs them the same way. The case reports one problem per number so the output
# says which of the three is off and by what.
#
# A count is accepted in either spelling a sentence like these uses: the digits, or the
# English words CLAUDE.md currently writes them in. Which one the author reaches for is
# not this suite's business — that the number is right is.
#
# Run: scripts/tests/claude-md-counts.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The document twice — the path as every failure message spells it, and the same path
# resolved for the probes to read — so a message can never name a file the probes did not
# open. The same pairing skill-leaf-launch.test.sh uses on SKILL.md.
claude_md="CLAUDE.md"
claude_path="$ROOT/$claude_md"

# The trees the counts are counts OF, each one twice for the same reason the document
# above is: repo-relative because that is how CLAUDE.md names them and how the failure
# messages have to, and resolved for `how_many` to expand, so a message can never name a
# tree the count was not taken from. Globs rather than directories: what the sentences count
# is the scripts and the suites, not everything that happens to sit beside them —
# `prompts/` and `tests/` are in the first directory, and `fixtures/` is in the second. The
# `*` survives the assignment unexpanded: bash globs a word where it is used, not where it
# is stored.
scripts_glob="skills/tdd/scripts/*.sh"
scripts_path="$ROOT/$scripts_glob"
suites_glob="skills/tdd/scripts/tests/*.test.sh"
suites_path="$ROOT/$suites_glob"
unit_glob="skills/tdd/scripts/tests/unit/*.test.sh"
unit_path="$ROOT/$unit_glob"

# The section the second and third counts live in, named once: it is both an argument to
# `section` and a name the failure messages spell, so renaming the heading in the document
# has to break the probe rather than leave the messages pointing at a section that is no
# longer called that.
section_name="Testing idiom"

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output names the count that is wrong rather than just saying one is.
report() {
  local name="$1"
  if [[ "${#problems[@]}" -eq 0 ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name"
    printf '    %s\n' "${problems[@]}"
  fi
}

# unreadable <missing> <subject> — record the problem a probe that came back with NOTHING
# leaves behind, onto the same `problems` array a mismatched count ends up in. Every
# fail-closed path in this suite goes through here: the globs matching no file, the preamble
# and the section coming back empty, a count pattern finding nothing. Each of those means an
# input this suite compares against could not be read, and every one has to say so as its own
# problem — never read as a count that agreed because there was nothing left to contradict.
# One helper so no path can quietly stop doing it, and so the five messages cannot drift into
# different shapes. Same idiom as skill-leaf-launch.test.sh's helper of the same name.
unreadable() {
  problems+=("$1 — $2 could not be read")
}

# readable <text> <missing> <subject> — true when a passage probe came back with prose to
# check. `flatten` turns line breaks into spaces, so a passage that is gone arrives here as
# spaces rather than as the empty string, and `${1// /}` — every space deleted — is what
# tells the two apart; the test is written once here rather than inline at each guard,
# because spelled out it reads as a parameter expansion and not as a question about the
# document. An unreadable passage records its own problem and returns non-zero, so the
# caller skips the checks it can no longer make instead of running them against nothing.
# Same shape as skill-suite-runs.test.sh's `need_text`: the guard reads forwards, "if the
# passage is readable, check what it claims".
readable() {
  if [[ -n "${1// /}" ]]; then return 0; fi
  unreadable "$2" "$3"
  return 1
}

# nonempty <what> <n> <glob> — fail closed on an inventory of nothing. A glob that matched
# no file means the tree moved out from under this suite, and zero must not quietly become
# the number every claim is checked against. One helper rather than the sentence once per
# tree, for the reason `unreadable` above is one helper: two copies of a message are two
# places for it to drift.
nonempty() {
  if [[ "$2" -eq 0 ]]; then
    unreadable "no $1 matched $3" "the tree the counts describe"
  fi
}

# how_many <glob> — how many files match it. The glob is left unquoted so the shell
# expands it, and every match is checked to be a file, because bash leaves a pattern that
# matched nothing standing as its own text: without the check an empty directory would
# count one.
how_many() {
  local f n=0
  for f in $1; do
    if [[ -f "$f" ]]; then n=$((n + 1)); fi
  done
  printf '%s' "$n"
}

# The English for a number below a hundred, which is the spelling CLAUDE.md writes its
# counts in ("eighteen bash scripts", "twenty-five files"). Two small tables rather than a
# map of every number the counts might reach, so the suite keeps answering as the tree
# grows. At a hundred and over the words run out and `in_words` prints nothing, which
# leaves the digits as the only spelling accepted — a document that ever counts that high
# will not be writing it out in words either.
ONES=(zero one two three four five six seven eight nine ten eleven twelve thirteen
      fourteen fifteen sixteen seventeen eighteen nineteen)
TENS=(twenty thirty forty fifty sixty seventy eighty ninety)

in_words() {
  local n="$1" t u
  if [[ "$n" -lt 20 ]]; then printf '%s' "${ONES[$n]}"; return; fi
  if [[ "$n" -ge 100 ]]; then return; fi
  t=$((n / 10 - 2))
  u=$((n % 10))
  if [[ "$u" -eq 0 ]]; then
    printf '%s' "${TENS[$t]}"
  else
    printf '%s-%s' "${TENS[$t]}" "${ONES[$u]}"
  fi
}

# preamble — the document above its first `## ` heading, which is where the opening
# paragraph's count lives. Read by structure rather than by line number so the paragraph
# is free to move as the file grows.
preamble() { awk '/^## / { exit } { print }' "$claude_path"; }

# section <heading-prefix> — the `## ` section whose heading starts with <heading-prefix>,
# from that heading to the next one. Prints nothing when no heading matches, which is what
# lets the caller tell "the section no longer states a count" from "the section is gone".
section() {
  awk -v want="$1" '/^## / { insec = (index($0, "## " want) == 1) } insec' "$claude_path"
}

# flatten — stdin as one line. CLAUDE.md is prose that wraps mid-sentence, and a claim
# split over a line break has to still read as one sentence for the patterns below to find
# it: "thirty-six files for" can sit on one line and "twenty-five scripts" on the next.
flatten() { tr '\n' ' '; }

# What a stated count looks like: the digits, or a word — hyphenated, since "twenty-five"
# is one. Written once because every pattern below embeds it — three times over the two of
# them — and a copy that drifted would leave one count read differently from the others.
NUM='([0-9]+|[A-Za-z-]+)'

# What may sit immediately before one: anything that is not itself part of a count. All
# three characters classes matter — a letter or a hyphen would let a word be captured from
# its middle ("ighteen" out of "eighteen"), and a digit would let a number be captured from
# its last digit ("7" out of "37"), which is worse than a miss: the shortened number is
# still compared against the disk, and `7` against seven suites reads as a count that
# agreed. Written beside NUM because the two are only ever used together.
BEFORE='[^0-9A-Za-z-]'

# The sentence each passage states its counts in: one pattern per passage, named after the
# passage it is matched against, because a pattern's capture groups only mean anything
# against that text — `$idiom_claim` group 1 is a suite count and group 2 a script count,
# both read out of the one sentence *Testing idiom* states them in. Beside NUM and BEFORE
# rather than at the use below, so the regex vocabulary is in one place and the checks read
# as comparisons.
intro_claim=".*$BEFORE$NUM bash scripts.*"
idiom_claim=".*$BEFORE$NUM files for $NUM scripts.*"
# The same sentence's unit-tier count, "plus <n> [words] under `unit/`" — the backticks and
# the slash matched as any character: the backticks so the pattern needs no quoting inside
# this double-quoted string, the slash because `claimed` hands the pattern to sed as
# `s/…/…/`, where a literal one ends it.
unit_claim=".*${BEFORE}plus $NUM [A-Za-z ]*under .unit..*"

# claimed <text> <pattern> <group> — the count <pattern> captures out of <text>, empty if
# nothing matches. The leading `.*` is greedy, so of several sentences matching in the
# same passage the last one answers; the `$BEFORE` in the patterns is what stops the
# capture starting in the middle of a count.
claimed() {
  head -1 < <(sed -nE "s/$2/\\$3/p" <<< "$1")
}

# check <what> <claimed> <n> — one stated count against the fact on disk. Accepts either
# spelling, case-folded because a count that opens a sentence is capitalised and that is
# not a difference about the number. An empty <claimed> fails closed through `unreadable`:
# a pattern that found nothing means the document no longer states that count where a
# reader is told to look.
check() {
  local what="$1" claimed="$2" n="$3" words
  if [[ -z "$claimed" ]]; then
    unreadable "$claude_md states no $what" "the sentence that counts them"
    return
  fi
  claimed="$(tr '[:upper:]' '[:lower:]' <<< "$claimed")"
  words="$(in_words "$n")"
  if [[ "$claimed" != "$n" ]] && [[ -z "$words" || "$claimed" != "$words" ]]; then
    problems+=("$claude_md says the $what is '$claimed'; there are $n on disk")
  fi
}

# moved <what> <claimed> <n> <added> — one stated count against the tree as it stood
# BEFORE <added> landed in it. <n> is what the glob matches now, so <n>-1 is the number the
# sentence stated before, and a sentence still stating that is one nobody edited when the
# file arrived. That is the whole failure the case below is there for and the one `check`
# above cannot see on its own: nothing recomputes a number written in prose, so a script
# can land, its suite can land, `make test` can go green, and both sentences go on counting
# the tree the script landed in. Either spelling, case-folded, for the reason `check` gives;
# an empty <claimed> fails closed through `unreadable` for the reason `check` gives too — a
# count the document no longer states cannot be shown to have moved.
moved() {
  local what="$1" claimed="$2" before="$(( $3 - 1 ))" added="$4" words
  if [[ -z "$claimed" ]]; then
    unreadable "$claude_md states no $what" "the sentence that counts them"
    return
  fi
  claimed="$(tr '[:upper:]' '[:lower:]' <<< "$claimed")"
  words="$(in_words "$before")"
  if [[ "$claimed" == "$before" ]] || [[ -n "$words" && "$claimed" == "$words" ]]; then
    problems+=("$claude_md says the $what is '$claimed' — the count of the tree without $added")
  fi
}

# present <path> — record the problem a file the counts are supposed to cover leaves behind
# by not being there. Fails closed for the same reason `nonempty` above does: with the file
# gone there is no move left to look for, and `moved` would be holding the stated count
# against a tree one file smaller than the one the sentence describes — under which a count
# that never moved reads as one that did.
present() {
  if [[ ! -f "$ROOT/$1" ]]; then
    problems+=("$1 is not in the tree whose count $claude_md states")
  fi
}

# moved_by <what> <claimed> <n> <added…> — `moved` for an issue that adds more than one
# file to the same tree. `moved` measures against <n>-1 because #149 added exactly one
# script and one suite; this issue adds one script and TWO suites, so the number nobody
# edited when it landed is <n> minus as many files as are named, and <n>-1 is a count that
# was never true of either tree. The two helpers catch different stale numbers rather than
# the same one twice — with 58 suites on disk, `moved` goes red on 57 and this goes red on
# 56 — which is why the case below is a case and not case 2 with other names. Either
# spelling, case-folded, and an empty <claimed> fails closed, all for the reasons `check`
# and `moved` give.
moved_by() {
  local what="$1" claimed="$2" n="$3" words
  shift 3
  local before="$(( n - $# ))" added
  # The files named, in one phrase, so the message says which arrivals the count slept
  # through rather than just that it did: "a.sh and b.sh", "a.sh, b.sh and c.sh".
  if [[ "$#" -eq 1 ]]; then
    added="$1"
  else
    added="$(printf '%s, ' "${@:1:$#-1}")"
    added="${added%, } and ${!#}"
  fi
  if [[ -z "$claimed" ]]; then
    unreadable "$claude_md states no $what" "the sentence that counts them"
    return
  fi
  claimed="$(tr '[:upper:]' '[:lower:]' <<< "$claimed")"
  words="$(in_words "$before")"
  if [[ "$claimed" == "$before" ]] || [[ -n "$words" && "$claimed" == "$words" ]]; then
    problems+=("$claude_md says the $what is '$claimed' — the count of the tree without $added")
  fi
}

# moved_with <script> <suite> — the question cases 2 and 5 both ask of an issue that adds
# one script and one suite: are both on disk, and did all three counts move off the number
# true of the tree without them. Written once so the two cases cannot drift into asking it
# differently. Returns non-zero when either file is missing — `present` has already recorded
# the problem, and `moved`'s <n>-1 would be measuring against the wrong tree — so a caller
# with a question of its own to add skips it the same way.
moved_with() {
  local script="$1" suite="$2"
  present "$script"
  present "$suite"
  if [[ "${#problems[@]}" -ne 0 ]]; then return 1; fi
  if readable "$intro" "$claude_md has no prose above its first '## ' heading" "the opening paragraph's script count"; then
    moved "opening paragraph's script count" "$(claimed "$intro" "$intro_claim" 1)" "$n_scripts" "$script"
  fi
  if readable "$idiom" "$claude_md has no '## $section_name' section" "the suite and script counts it states"; then
    moved "*$section_name* suite count" "$(claimed "$idiom" "$idiom_claim" 1)" "$n_suites" "$suite"
    moved "*$section_name* script count" "$(claimed "$idiom" "$idiom_claim" 2)" "$n_scripts" "$script"
  fi
}

# 1. The criterion. The counts are read off the document and the files off the disk, and
#    every one of them has to agree.
name="$claude_md's stated script and suite counts match the scripts and suites on disk"
problems=()

n_scripts="$(how_many "$scripts_path")"
n_suites="$(how_many "$suites_path")"

nonempty script "$n_scripts" "$scripts_glob"
nonempty suite "$n_suites" "$suites_glob"

intro="$(preamble | flatten)"
idiom="$(section "$section_name" | flatten)"

if readable "$intro" "$claude_md has no prose above its first '## ' heading" "the opening paragraph's script count"; then
  check "opening paragraph's script count" "$(claimed "$intro" "$intro_claim" 1)" "$n_scripts"
fi

if readable "$idiom" "$claude_md has no '## $section_name' section" "the suite and script counts it states"; then
  check "*$section_name* suite count" "$(claimed "$idiom" "$idiom_claim" 1)" "$n_suites"
  check "*$section_name* script count" "$(claimed "$idiom" "$idiom_claim" 2)" "$n_scripts"
fi

report "$name"

# 2. The counts moved with the script and the suite this issue adds. Case 1 asks whether
#    the three numbers are right; this one asks whether they are right because somebody
#    moved them when `refactor-triage.sh` and `refactor-triage.test.sh` arrived — the two
#    files whose arrival is the only thing in this issue CLAUDE.md owes an edit for. A
#    stated count is prose, so the tree can grow under it silently: the number that was
#    true of the tree without these two would still be sitting in both sentences, and
#    nothing but a case like this one goes red for it. The reads are case 1's, taken once
#    above — `n_scripts`, `n_suites`, `intro` and `idiom` — asked a narrower question here.
name="$claude_md's counts moved with refactor-triage.sh and its suite"
problems=()

moved_with "skills/tdd/scripts/refactor-triage.sh" "skills/tdd/scripts/tests/refactor-triage.test.sh"

report "$name"

# 3. The counts moved with the files THIS issue adds. Case 2 asks the same question of
#    #149's pair; this one asks it of #207's — `run-conductor.sh`, and the two suites that
#    arrive with it, `run-conductor.test.sh` and `skill-conductor-launch.test.sh`. Two
#    suites is the whole reason this is its own case: the suite count nobody edited when
#    this issue landed is two below the tree on disk, and case 2's `moved` only ever looks
#    one below, so a document still stating fifty-six suites reads to case 2 as one
#    somebody moved. The reads are case 1's, taken once above — `n_scripts`, `n_suites`,
#    `intro` and `idiom` — asked of this issue's arrivals.
name="$claude_md's counts moved with run-conductor.sh and its suites"
problems=()

conductor_script="skills/tdd/scripts/run-conductor.sh"
conductor_suites=(
  "skills/tdd/scripts/tests/run-conductor.test.sh"
  "skills/tdd/scripts/tests/skill-conductor-launch.test.sh"
)

present "$conductor_script"
for suite in "${conductor_suites[@]}"; do present "$suite"; done

# Only ask about the move when every one of them is on disk, for the reason case 2 gives:
# `present` has already recorded the problem otherwise, and the subtraction would be
# measuring against a tree that is not the one the sentences describe.
if [[ "${#problems[@]}" -eq 0 ]]; then
  if readable "$intro" "$claude_md has no prose above its first '## ' heading" "the opening paragraph's script count"; then
    moved_by "opening paragraph's script count" "$(claimed "$intro" "$intro_claim" 1)" "$n_scripts" "$conductor_script"
  fi

  if readable "$idiom" "$claude_md has no '## $section_name' section" "the suite and script counts it states"; then
    moved_by "*$section_name* suite count" "$(claimed "$idiom" "$idiom_claim" 1)" "$n_suites" "${conductor_suites[@]}"
    moved_by "*$section_name* script count" "$(claimed "$idiom" "$idiom_claim" 2)" "$n_scripts" "$conductor_script"
  fi
fi

report "$name"

# 4. The unit tier is counted too, and the count includes the suite #339 adds there. The
#    *Testing idiom* sentence that counts `tests/*.test.sh` goes on to count the suites
#    under `unit/` — "plus <n> … under `unit/`" — and case 1 never reads that number, so the
#    first unit suite written rather than moved there (`unit/push-branch.test.sh`) could land
#    with the sentence still counting the tier without it. Held to the glob the same way
#    case 1 holds the other two: the number in the prose is the number of files on disk.
name="$claude_md's unit-tier suite count matches the unit suites on disk, including push-branch.sh's"
problems=()

unit_suite="skills/tdd/scripts/tests/unit/push-branch.test.sh"

present "$unit_suite"
n_unit="$(how_many "$unit_path")"
nonempty "unit suite" "$n_unit" "$unit_glob"

if [[ "${#problems[@]}" -eq 0 ]]; then
  if readable "$idiom" "$claude_md has no '## $section_name' section" "the unit suite count it states"; then
    check "*$section_name* unit suite count" "$(claimed "$idiom" "$unit_claim" 1)" "$n_unit"
  fi
fi

report "$name"

# 5. The counts moved with `invisible-work.sh` and its suite (#197), and the prose around
#    them stays true of what was added. The opening paragraph counts "<n> bash scripts it
#    calls" — the procedure's scripts — but `invisible-work.sh` is a maintenance utility a
#    human or a loop runs; SKILL.md never calls it. A count that silently absorbed it would
#    tell a reader the procedure calls one script more than it does, so the document has
#    to name the script where it counts it: the number moves, and the sentence says which
#    of the counted scripts the procedure does not call. The reads are case 1's.
name="$claude_md's counts moved with invisible-work.sh and its suite, and its prose names the script the procedure does not call"
problems=()

# An unreadable preamble has already recorded its problem inside `moved_with`, so the name is
# only looked for in prose that is there.
if moved_with "skills/tdd/scripts/invisible-work.sh" "skills/tdd/scripts/tests/invisible-work.test.sh"; then
  if [[ -n "${intro// /}" && "$intro" != *"invisible-work.sh"* ]]; then
    problems+=("$claude_md's opening paragraph counts '<n> bash scripts it calls' without naming invisible-work.sh, a script the procedure never calls")
  fi
fi

report "$name"

# 6. The counts are unaffected by removing the two forwarding stubs (#412). The stubs were
#    `skills/solve-issue/` and `skills/solve-issues/`, neither under `skills/tdd/scripts/`,
#    so taking them out moves no number CLAUDE.md states: with both gone, the three counts
#    case 1 reads are still the files on disk. The absence is checked first and fails closed
#    — a stub still standing means the tree this case describes is not the one on disk, and
#    counts that agree with it would say nothing about the change.
name="$claude_md's stated script and suite counts are unchanged once the solve-issue stubs are gone"
problems=()

for stub in "skills/solve-issue" "skills/solve-issues"; do
  if [[ -e "$ROOT/$stub" ]]; then
    problems+=("$stub/ is still in the tree; the stubs this case counts without are not gone")
  fi
done

if [[ "${#problems[@]}" -eq 0 ]]; then
  nonempty script "$n_scripts" "$scripts_glob"
  nonempty suite "$n_suites" "$suites_glob"
  if readable "$intro" "$claude_md has no prose above its first '## ' heading" "the opening paragraph's script count"; then
    check "opening paragraph's script count" "$(claimed "$intro" "$intro_claim" 1)" "$n_scripts"
  fi
  if readable "$idiom" "$claude_md has no '## $section_name' section" "the suite and script counts it states"; then
    check "*$section_name* suite count" "$(claimed "$idiom" "$idiom_claim" 1)" "$n_suites"
    check "*$section_name* script count" "$(claimed "$idiom" "$idiom_claim" 2)" "$n_scripts"
  fi
fi

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
