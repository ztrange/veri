#!/usr/bin/env bash
# Unit test: no suite under skills/tdd/scripts/tests/ (or its unit/ tier) executes another
# real suite from this directory to establish something a check scoped to one call, inside
# the suite that already runs it, could establish instead. Zero-dependency plain-shell
# asserts, same idiom as no-docs-reads.test.sh — this is that suite's rule ("does it name a
# path outside a comment") asked of a *.test.sh path instead of a docs/ one.
#
# Why this exists (the pattern #331 and #332 both used): metrics-python3-
# starts.test.sh, harvest-usage-launch.test.sh and probe-suites-unchanged.test.sh each
# copied a real suite (metrics.test.sh, harvest-usage.test.sh) into a scratch tree and ran
# the WHOLE thing — sometimes several times over, against several broken variants — to pin a
# python3-start count or a case roster. Measured 2026-09-19: ~41.5s of `make test` to pin a
# ~1.5s saving. The cheaper shape already existed (supervise.test.sh case 33 counts python3
# starts for ONE supervision inside a case that already runs it) and is where all three
# rules worth keeping moved to (metrics.test.sh, harvest-usage.test.sh); the rest were
# regression pins for a one-time migration, not an ongoing product rule, and are gone with
# the suites that made them (commit body has the map).
#
# Contract under test: no suite named by the roster below both (a) names another real suite
# from this directory or its unit/ tier and (b) does so in a shape this file treats as
# launching it — outside a comment, and outside the exemptions recorded here, each with the
# reason its subject cannot be established any cheaper way.
#
# Two shapes count as "launching it", because they are the two ways a suite in this
# directory starts another one instead of $HERE/name.test.sh being that other suite's own
# business:
#
#   - the other suite's basename sits right after a `$`-prefixed path on the same line
#     ("$HERE/name.test.sh", "$copy/tests/name.test.sh", …) — this is always a launch: a
#     suite reads its OWN path through $HERE, so a *different* suite's name reached through a
#     variable is one being started, copied, or both.
#   - the other suite's basename sits bare — quoted or not, with no leading path — which is
#     how a name is put in a variable or an array element before being launched through it
#     (SUBJECT_NAME='run-conductor.test.sh', an array of `GUARDS`). A bare name is never used
#     for anything else in this tree: nothing here compares two suites' names as plain text.
#
# A bare name is read as one of those two only when it stands for the suite itself. A table
# key addressing a LINE of another suite — `[other.test.sh:66]="<reason>"`, the shape
# no-sigpipe-pipelines.test.sh's exemption table uses — is not: `other.test.sh:66` is an
# address, and no shell can launch one. So a bare name bracketed as a key and followed by
# `:<line>]` is passed over, which is why that table's own keys do not need an exemption
# here.
#
# A third shape — the other suite's FULL repo-relative path, quoted, with no `$` in front
# ("skills/tdd/scripts/tests/name.test.sh") — is common and mostly harmless on its own:
# claude-md-counts.test.sh's `present()` and `moved()` read dozens of them just to confirm a
# file is on disk or to diff a stated count, never to run anything. So that shape only counts
# when the SAME FILE also shows one of the two ways this tree launches a suite by a path
# rather than by $HERE — a `cp` (a copy, always headed somewhere to be run) or a `make …
# TESTS=`/`UNIT_TESTS=` (asking the recipe to run a named suite). Both are cheap, file-wide
# tests: neither this repo's suites nor its scripts have a reason to call `cp` or spell
# `TESTS=` for anything else that also happens to sit beside another suite's full path.
#
# What this cannot do, and does not try to: prove a suite is CHEAP, only that it does not
# launch another one. A suite that inlines a whole second suite's body, or shells out to
# `bash -c "$(cat other.test.sh)"`, would not be named here — nobody in this tree does either,
# and a check for it would be guessing at a shape nothing has used yet.
#
# Run: skills/tdd/scripts/tests/no-nested-suites.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
suites_dir="skills/tdd/scripts/tests"

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem, so
# the output says which suite and line broke the rule rather than just that one did.
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
# line stays one line. Pure parameter expansion rather than `printf … | tr`, which forks two
# processes per problem line: with dozens of them possible in one red run, that fork pair was
# most of this file's own wall time (0.65s of it, measured before this change), the same tax
# a `.test.sh` file anywhere in this tree exists to stop other suites paying.
flat() { local s="$1"; printf '%s' "${s//$'\n'/\/}"; }

# EXEMPT[<suite>]="<reason>" — a suite allowed to name another real suite outside a comment,
# each because its own subject genuinely IS that other suite's behaviour and nothing cheaper
# establishes it: a plant that has to run the real thing to prove a seam still catches a
# regression, or a runner's own verdict over a real tree. Never add a suite whose rule this
# file's own commit moved into a call-scoped check instead — a rule that can live in the
# suite it is about does not belong here.
declare -A EXEMPT=(
  # This file's own header and this table necessarily name real suites outside a comment —
  # the table's keys and the prose explaining each one. Those are policy, not a launch.
  [no-nested-suites.test.sh]="its own exemption table and header name every suite below by basename outside a comment; that is the policy this file states, not a launch of any of them"

  [hermetic-suites.test.sh]="its subject is whether a REAL suite's own output changes under an ambient VERI_* variable — solvable-issues.test.sh, supervise-retry.test.sh, leaf-model.test.sh and run-conductor.test.sh are each launched with and without one set and diffed; a copy or a fixture would be a fact about the copy, not about hermeticity"
  [claude-md-guards-green.test.sh]="its subject is whether the four suites that hold CLAUDE.md to its own rules — claude-md-counts.test.sh, lane-rule-recorded.test.sh, count-line-guard.test.sh, docs-targets-refuse.test.sh — are still green against the document as committed; there is no product script to run in their place"
  [run-conductor-argv-guard.test.sh]="pins that run-conductor.test.sh's case 4 still catches the argv-shape regression #221 fixed; the criterion is what THAT SUITE reports over a broken product, which a static read cannot establish since more than one fix satisfies it (its own header says so)"
  [docs-read-guard.test.sh]="copies no-docs-reads.test.sh (the guard #143 added) into a planted tree with a genuine documentation-tree read and asserts the guard still catches it; the guard's whole job is to catch that read, so only running it proves it still can"
  [sigpipe-guard.test.sh]="plants a suite that declares pipefail and ends a pipeline in grep -q, plus the same pipeline without pipefail, into a scratch tree and runs a copy of no-sigpipe-pipelines.test.sh (the guard #422 added) over it; after this issue's other steps the real tree holds no live site, so the guard answers the same way over it whether it still checks anything or not, and only running it over the plant says otherwise"
  [docs-read-guard-plant.test.sh]="the same plant-the-bug seam verification one level up: runs a scratch copy of docs-read-guard.test.sh against a stubbed no-docs-reads.test.sh to pin that IT still reports the guard's absence correctly"
  [verifier-launch-guard.test.sh]="plants the #297 bypass back into a copy of SKILL.md — a verifier launch line with the supervisor cut out of it — and runs skill-leaf-launch.test.sh over it to pin that its case 5 still fails and still names that line; every launch in the document is correct today, so that guard passes over this tree whether it checks anything or not, and only running it over the plant says otherwise"
  [prose-drift-red.test.sh]="its subject is the verdict \`make test\`'s own runner reaches over a tree — \`make -C \$planted test TESTS=refactor-budget.test.sh\` — not the product; only the real recipe over the real suite produces that verdict"
)

# roster: every real suite's basename under $suites_dir and its unit/ tier — not fixtures/,
# not offline/, not unit-guard/, the way `make test`'s own TESTS/UNIT_TESTS wildcards read
# only this level and that one subdirectory.
# No `basename`/`xargs` here (each is a process; `xargs -n1` is one PER name): a suite's own
# `${path##*/}` strips the directory for free, which is the whole reason this file exists.
mapfile -t SUITE_PATHS < <(cd "$ROOT" && printf '%s\n' "$suites_dir"/*.test.sh "$suites_dir"/unit/*.test.sh 2>/dev/null)
SUITES=()
for p in "${SUITE_PATHS[@]}"; do
  [[ -f "$ROOT/$p" ]] && SUITES+=("${p##*/}")
done
mapfile -t SUITES < <(printf '%s\n' "${SUITES[@]}" | sort -u)

# The full roster joined with a separator no suite name contains, and the list of files to
# scan (skipping an exempted suite's file entirely rather than reading it just to discard
# every hit) — both handed to ONE awk process below instead of one per suite. A first cut of
# this file ran one awk (and, before that, one grep) per LINE of every suite: 65s to check a
# tree awk reads in a fraction of a second, which is exactly the cost this issue exists to
# cut, just paid by the guard meant to catch it instead of by the suites it catches.
SUITE_LIST="$(IFS='|'; echo "${SUITES[*]}")"

FILES=()
for suite in "${SUITES[@]}"; do
  [[ -n "${EXEMPT[$suite]+x}" ]] && continue
  f="$ROOT/$suites_dir/$suite"
  [[ -f "$f" ]] || f="$ROOT/$suites_dir/unit/$suite"
  [[ -f "$f" ]] || continue
  FILES+=("$f")
done

problems=()

# One awk pass over every non-exempt suite file. `FNR == 1` resets the per-file state (the
# launch-verb gate and the path-form hits withheld until that file's own EOF, since the gate
# can appear after the hit) and flushes the PREVIOUS file's pending hits, so this reads as
# the same per-file logic as before with the file loop moved inside awk instead of around it.
while IFS=$'\t' read -r suite lineno other text; do
  [[ -n "$lineno" ]] || continue
  problems+=("$suite:$lineno names $other outside a comment, in a shape this file treats as launching it, with no exemption recorded: $(flat "$text")")
done < <(awk -v suites="$SUITE_LIST" -v dir="$suites_dir" '
  function flush_pending() {
    if (gate) {
      for (i = 1; i <= pending_n; i++)
        print self "\t" pending_line[i] "\t" pending_tok[i] "\t" pending_text[i]
    }
    gate = 0; pending_n = 0
  }
  BEGIN {
    n = split(suites, arr, "|")
    for (i = 1; i <= n; i++) is_suite[arr[i]] = 1
  }
  FNR == 1 {
    flush_pending()
    self = FILENAME
    sub(/^.*\//, "", self)
  }
  /^[ \t]*#/ { next }
  {
    line = $0
    if (line ~ /(^|[^A-Za-z0-9_])cp[ \t]/ || line ~ /(^|[^A-Za-z0-9_])(UNIT_)?TESTS=/) gate = 1
    rest = line
    while (match(rest, /[a-z0-9_-]+\.test\.sh/)) {
      tok = substr(rest, RSTART, RLENGTH)
      before = (RSTART > 1) ? substr(rest, RSTART - 1, 1) : ""
      rest = substr(rest, RSTART + RLENGTH)
      if (!(tok in is_suite) || tok == self) continue
      # A table key addressing a site — `[other.test.sh:66]=` — names a line of that suite,
      # which is not something any shell can launch. Never a launch, so never a problem.
      if (before == "[" && rest ~ /^:[0-9]+\]/) continue
      pathform = (index(line, dir "/" tok) > 0) || (index(line, dir "/unit/" tok) > 0)
      if (pathform) {
        pending_n++
        pending_line[pending_n] = FNR
        pending_tok[pending_n] = tok
        pending_text[pending_n] = line
      } else {
        print self "\t" FNR "\t" tok "\t" line
      }
    }
  }
  END { flush_pending() }
' "${FILES[@]}")

name="no suite under skills/tdd/scripts/tests/ (or its unit/ tier) launches another real suite outside the exemptions recorded here"

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
