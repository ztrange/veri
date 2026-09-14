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

# The two trees the counts are counts OF, each one twice for the same reason the document
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

# claimed <text> <pattern> <group> — the count <pattern> captures out of <text>, empty if
# nothing matches. The leading `.*` is greedy, so of several sentences matching in the
# same passage the last one answers; the `$BEFORE` in the patterns is what stops the
# capture starting in the middle of a count.
claimed() {
  sed -nE "s/$2/\\$3/p" <<< "$1" | head -1
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

if [[ -z "${intro// /}" ]]; then
  unreadable "$claude_md has no prose above its first '## ' heading" "the opening paragraph's script count"
else
  check "opening paragraph's script count" "$(claimed "$intro" "$intro_claim" 1)" "$n_scripts"
fi

if [[ -z "${idiom// /}" ]]; then
  unreadable "$claude_md has no '## $section_name' section" "the suite and script counts it states"
else
  check "*$section_name* suite count" "$(claimed "$idiom" "$idiom_claim" 1)" "$n_suites"
  check "*$section_name* script count" "$(claimed "$idiom" "$idiom_claim" 2)" "$n_scripts"
fi

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
