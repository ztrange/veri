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

MD_FILES='(CLAUDE|SKILL)\.md'

SIZE_VERB='(^|[^[:alnum:]_./-])(wc|stat|du)[[:space:]]'

BINDS="^[[:space:]]*(local[[:space:]]+)?([A-Za-z_][A-Za-z0-9_]*)=.*$MD_FILES"

pass=0 fail=0

source "$HERE/lib/harness.sh"

flat() { printf '%s' "$1" | tr '\n' '/'; }

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
      [[ "$text" =~ ^[[:space:]]*# ]] && continue
      [[ "$text" =~ $subj ]] || continue
      problems+=("$name:$lineno measures the size of one of the two files every request is billed for, which is the ceiling #202 refuses — the guard against those documents growing back is that every rule in them is still stated, never how many bytes it took: $(flat "$text")")
    done < <(grep -nE "$SIZE_VERB" "$f")
  done
  return 0
}

name="no suite under skills/tdd/scripts/tests/ asserts a maximum size for CLAUDE.md or the conductor's SKILL.md"
problems=()

probe_no_suite_measures_either_file

report "$name"

if [[ -z "${NO_SIZE_ASSERTION_NESTED:-}" ]]; then

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

md=CLAUDE

observe() {
  local dir="$tmp/$1" suite="$2" format="$3"
  shift 3
  mkdir -p "$dir"
  cp "$HERE/no-size-assertion.test.sh" "$dir/"
  mkdir -p "$dir/lib" && cp "$HERE/lib/harness.sh" "$dir/lib/"
  printf "$format" "$@" > "$dir/$suite"
  out="$(NO_SIZE_ASSERTION_NESTED=1 "$dir/no-size-assertion.test.sh" 2>&1)"
}

name="a suite whose only size-verb line is inside a comment is not reported, even when the comment names the document"
problems=()

observe commented comment-only.test.sh \
  '#!/usr/bin/env bash\n# wc -c < "$ROOT/%s.md" the old way\necho "no ceiling here"\n' "$md"
[[ "$out" == *'1 passed, 0 failed'* ]] ||
  problems+=("want the observed suite green when the only size-verb line is a comment, got: $(flat "$out")")
[[ "$out" != *'comment-only.test.sh:'* ]] ||
  problems+=("want no problem line naming comment-only.test.sh, got: $(flat "$out")")

report "$name"

name="a suite binding a variable to the document three lines above the line measuring it is still reported, naming the suite and line"
problems=()

observe bound binds-doc.test.sh \
  '#!/usr/bin/env bash\ndoc="$ROOT/%s.md"\necho one\necho two\nbytes="$(wc -c < "$doc")"\n' "$md"
[[ "$out" == *'0 passed, 1 failed'* ]] ||
  problems+=("want the observed suite red when a suite measures a variable bound to the document, got: $(flat "$out")")
[[ "$out" == *'binds-doc.test.sh:5 measures the size'* ]] ||
  problems+=("want a problem line naming binds-doc.test.sh:5, got: $(flat "$out")")

report "$name"

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
