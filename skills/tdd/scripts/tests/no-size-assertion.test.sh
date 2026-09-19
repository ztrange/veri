#!/usr/bin/env bash
# Unit test for the suites in this directory — none of them holds either preamble file to a
# maximum size. Like hermetic-suites.test.sh, no-docs-reads.test.sh and
# claude-md-guards-green.test.sh this suite has no script as its subject: its subject is the
# tree it is run in.
# Zero-dependency plain-shell asserts, same idiom as no-docs-reads.test.sh.
#
# Why this exists (issue #202): the two files every request is billed for — the repository's
# own agent notes, and the conductor's procedure under skills/tdd/ — are being trimmed
# because a resident token is re-read at cache-read rates on every turn. The obvious guard
# against them growing back is a byte ceiling, and #202 forbids it outright: a byte that
# stops one bad leaf pays for itself many times over, so a check that goes red when someone
# writes the sentence that prevents the next bad leaf is a check that trades a real failure
# for an accounting one. The document's brake is the four guards
# claude-md-guards-green.test.sh runs — is every rule still stated? — and never its size.
#
# So the ceiling is the thing pinned absent. Left unpinned it is the first thing the next
# author reaches for, arriving as one plausible line in an existing suite, and nothing in a
# green run would say so.
#
# Contract under test:
#   No suite under this directory measures the size of either file. A mention is not a
#   measurement — these suites quote both documents at length and must keep being able to —
#   and a comment is not one either. What is one is a size verb (`wc`, `stat`, `du`) applied
#   to one of the two, whether the line names the file itself or a variable the same suite
#   bound to it.
#
# The two shapes, because a size assertion is written in either and they are the same claim:
# `wc -c < "$ROOT/CLAUDE.md"` names its subject on the line that measures it, and
# `doc="$ROOT/CLAUDE.md"` three lines above a `wc -c < "$doc"` does not. Asking only the
# measuring line for a file name would find the first and miss the second, which is the
# distinction no-docs-reads.test.sh makes for the documentation tree: a path bound to a name
# is that path, one variable away.
#
# Asking only about the size verb, per suite rather than per line, would be simpler and
# wrong: six suites here already count something with `wc` for reasons that have nothing to
# do with either document, and a rule that fired on those would be deleted by the first
# author it blocked.
#
# Run: skills/tdd/scripts/tests/no-size-assertion.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

# The two files #202 is about, as an ERE — the repository's agent notes and the conductor's
# procedure, matched by name rather than by path so that a suite spelling either against
# $ROOT, against a fixture root or bare is asked the same question.
MD_FILES='(CLAUDE|SKILL)\.md'

# Measuring a file, as an ERE. The verb must start a word and end in whitespace, so
# `wc-of-the-plan` is not one. These three are what this tree has ever used to ask how big
# something is; `ls -l` is not among them and would be caught by the size it then compares
# against, not by the listing.
SIZE_VERB='(^|[^[:alnum:]_./-])(wc|stat|du)[[:space:]]'

# A line binding a name to one of those files: `doc="$ROOT/…"`, with or without `local`.
# The captured name is what the measuring line three lines down will spell as a variable.
BINDS="^[[:space:]]*(local[[:space:]]+)?([A-Za-z_][A-Za-z0-9_]*)=.*$MD_FILES"

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which line put a ceiling on which document rather than just that some
# line did.
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

# flat <text> — one line of it, for a failure message: newlines become slashes so a quoted
# line stays one line.
flat() { printf '%s' "$1" | tr '\n' '/'; }

# subjects <file> — the ERE matching a reference to either document in <file>: the two names
# themselves, plus every variable the file binds to one of them. Built per suite rather than
# once for the tree, because `$doc` in one suite is one of these documents and in the next
# one is the issue body.
subjects() {
  local names joined
  names="$(sed -nE "s/$BINDS.*/\2/p" "$1" | sort -u | tr '\n' '|')"
  joined="${names%|}"
  if [[ -n "$joined" ]]; then
    printf '%s' "$MD_FILES|\\\$\\{?($joined)"
  else
    printf '%s' "$MD_FILES"
  fi
}

# probe_no_suite_measures_either_file — the criterion. Every suite beside this one is asked
# for its measuring lines, and each of those for a reference to one of the two documents.
# The suites are found by globbing this directory rather than by a list, because a list is
# what the next suite would be added outside of; `make test` finds them the same way.
#
# One problem per offending line, naming the suite and the line number, because what sends
# the next author to the site is the address rather than the file.
#
# One grep across every suite first names the few that hold a size-verb line at all, so only
# those pay the per-file sed and grep below (#332).
probe_no_suite_measures_either_file() {
  local f name subj hit lineno text
  local -a suites=("$HERE"/*.test.sh) matched=()
  [[ -e "${suites[0]}" ]] || return 0
  mapfile -t matched < <(grep -lE "$SIZE_VERB" "${suites[@]}")
  for f in "${matched[@]}"; do
    name="$(basename "$f")"
    subj="$(subjects "$f")"
    while IFS= read -r hit; do
      lineno="${hit%%:*}"
      text="${hit#*:}"
      # A comment cannot assert anything, and the prose in this tree discusses both
      # documents' size at length — #202 is an issue about bytes.
      [[ "$text" =~ ^[[:space:]]*# ]] && continue
      [[ "$text" =~ $subj ]] || continue
      problems+=("$name:$lineno measures the size of one of the two files every request is billed for, which is the ceiling #202 refuses — the guard against those documents growing back is that every rule in them is still stated, never how many bytes it took: $(flat "$text")")
    done < <(grep -nE "$SIZE_VERB" "$f")
  done
  return 0
}

# 1. One criterion, one case: nothing in this directory puts a maximum size on either file.
#    One case rather than one per document, because the rule is one sentence about both —
#    and the problem lines say which document a ceiling was put on.
name="no suite under skills/tdd/scripts/tests/ asserts a maximum size for CLAUDE.md or the conductor's SKILL.md"
problems=()

probe_no_suite_measures_either_file

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
