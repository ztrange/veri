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

# Cases 2-4 below ask three shapes of the exemption logic above that the real tree never
# happens to exercise: a comment, a variable bound three lines above its measuring line, and
# a suite that measures something else entirely with the same three verbs. Moved from
# no-size-assertion-forks.test.sh (#332), which used to observe them as a side effect of
# counting that suite's own grep/sed starts; the count is gone (a suite asserts behaviour,
# not cost — CLAUDE.md's "Testing idiom"), these three behaviours are not.
#
# Each asks its question by running a fresh COPY of this very file against a one-suite
# fixture directory, the way skill-leaf-env.test.sh relaunches a copy of itself to ask about
# a nested environment. That copy carries cases 2-4 too, and would relaunch a copy of
# itself in turn without `NO_SIZE_ASSERTION_NESTED` — set once here, checked once below —
# the same guard skill-leaf-env.test.sh's own `SKILL_LEAF_ENV_NESTED` is for. Case 1 still
# runs in a nested copy (it is the one thing being observed); only 2-4 do not recurse.
if [[ -z "${NO_SIZE_ASSERTION_NESTED:-}" ]]; then

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

# The document's name, spelled without its `.md` so no line here both measures and names it
# (the same reason no-size-assertion-forks.test.sh, where these three cases came from, split
# it the same way): this suite scans itself too, and a fixture body written out with the two
# halves already joined would be a ceiling on CLAUDE.md as far as its own probe can tell.
md=CLAUDE

# observe <dir> <suite-name> <format> [<arg>…] — a fresh copy of THIS suite, run NESTED (see
# above) in its own fixture directory beside one suite <suite-name> written by `printf
# <format> <arg>…`; the observed suite's combined output lands in `out`. Each case's own
# directory, so one case's fixture cannot be found by another's copy. The copy is of this
# file, not of a different suite: `tok == self` in no-nested-suites.test.sh's guard is
# exactly this shape, a suite proving its own exemption logic against a fixture rather than
# another suite's.
observe() {
  local dir="$tmp/$1" suite="$2" format="$3"
  shift 3
  mkdir -p "$dir"
  cp "$HERE/no-size-assertion.test.sh" "$dir/"
  printf "$format" "$@" > "$dir/$suite"
  out="$(NO_SIZE_ASSERTION_NESTED=1 "$dir/no-size-assertion.test.sh" 2>&1)"
}

# 2. The criterion: a suite whose only size-verb line is a comment is not reported, even when
#    that comment names the document — so the comment exemption, not a missing subject, is
#    what keeps it green.
#      → the observed suite `1 passed, 0 failed`, and no line naming the fixture suite.
name="a suite whose only size-verb line is inside a comment is not reported, even when the comment names the document"
problems=()

observe commented comment-only.test.sh \
  '#!/usr/bin/env bash\n# wc -c < "$ROOT/%s.md" the old way\necho "no ceiling here"\n' "$md"
[[ "$out" == *'1 passed, 0 failed'* ]] ||
  problems+=("want the observed suite green when the only size-verb line is a comment, got: $(flat "$out")")
[[ "$out" != *'comment-only.test.sh:'* ]] ||
  problems+=("want no problem line naming comment-only.test.sh, got: $(flat "$out")")

report "$name"

# 3. The criterion: a suite binding a variable to the document three lines above the line
#    that measures it is still reported — the measuring line names only `$doc`, so only the
#    binding the probe reads out of the same suite makes it a ceiling.
#      → the observed suite `0 passed, 1 failed`, naming binds-doc.test.sh:5, the `wc` line.
name="a suite binding a variable to the document three lines above the line measuring it is still reported, naming the suite and line"
problems=()

observe bound binds-doc.test.sh \
  '#!/usr/bin/env bash\ndoc="$ROOT/%s.md"\necho one\necho two\nbytes="$(wc -c < "$doc")"\n' "$md"
[[ "$out" == *'0 passed, 1 failed'* ]] ||
  problems+=("want the observed suite red when a suite measures a variable bound to the document, got: $(flat "$out")")
[[ "$out" == *'binds-doc.test.sh:5 measures the size'* ]] ||
  problems+=("want a problem line naming binds-doc.test.sh:5, got: $(flat "$out")")

report "$name"

# 4. The criterion: a suite that measures something else entirely with `wc`, `stat` and `du`
#    is not reported — even when the same suite names the document on a line that measures
#    nothing, so only the per-line subject check keeps it green.
#      → the observed suite `1 passed, 0 failed`, and no line naming the fixture suite.
name="a suite that measures something else entirely with wc, stat and du is not reported, even when it also names the document on an unrelated line"
problems=()

observe unrelated sizes-other.test.sh '#!/usr/bin/env bash
grep -q rule "$ROOT/%s.md"
lines="$(wc -l < "$plan")"
size="$(stat -f %%z "$log")"
used="$(du -k "$tmp" | cut -f1)"
' "$md"
[[ "$out" == *'1 passed, 0 failed'* ]] ||
  problems+=("want the observed suite green when a suite measures only files other than the two documents, got: $(flat "$out")")
[[ "$out" != *'sizes-other.test.sh:'* ]] ||
  problems+=("want no problem line naming sizes-other.test.sh, got: $(flat "$out")")

report "$name"

fi # NO_SIZE_ASSERTION_NESTED

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
