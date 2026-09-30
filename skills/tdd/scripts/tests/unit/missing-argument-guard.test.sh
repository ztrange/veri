#!/usr/bin/env bash
# Unit tests for the check behind the cross-suite guard on the argument contract —
# lib/missing-argument-exit.sh, the audit that tests/unit/missing-argument-exit.test.sh
# runs over every script that requires a positional argument. Like docs-read-guard.test.sh
# is to no-docs-reads.test.sh, this suite's subject is not a script a run calls: it is what
# the guard reports about a script that answers a missing argument wrongly.
#
# Why this exists (issue #270): the guard is only worth its place in `make test` if it goes
# red, and names the culprit, when a script comes back with 1 — "a clean negative", an
# answer — where CLAUDE.md's "Exit codes are the API" says a call missing an argument owes
# 2, "no answer could be obtained". Every script in the guard's own roster refuses with 2
# today, so a case asserting over the real tree passes whether the check works or not; the
# offender is planted instead, and the audit is asked about the planted tree.
#
# Contract under test:
#   Handed a directory and the name of a script in it that exits 1 with a usage line when
#   called with no arguments, the audit prints one offender line naming that script and the
#   status it came back with, and returns 1.
#
# Admitted to the fast tier (#336) by its own usage count, which unit-tier.test.sh reads off
# one line: git 0, python3 0, server 0, sleep 0.
# The planted scripts are `#!/bin/sh` two-liners that answer before doing any work (#322), so
# the cases start one process apiece and wait on nothing.
#
# Run: scripts/tests/unit/missing-argument-guard.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LIB="$HERE/../../lib/missing-argument-exit.sh"
source "$HERE/../lib/harness.sh"
scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT
out="$scratch/out" err="$scratch/err"

show_run() {  # show_run <exit> <stdout-file> <stderr-file> — print what a failing case got
  echo "    exit $1"; echo "    stdout: $(printf '%q' "$(cat "$2")")"
  echo "    stderr: $(printf '%q' "$(cat "$3")")"
}

# judge <name> <want-stdout> <fn> [args …] — run one case and record its result. <fn> is a
# function the library defines, so it runs in a subshell that sources the library: both
# halves of the audit `return` rather than `exit`, to hand their caller an offender instead
# of tearing it down, and a subshell is what keeps a failing one from ending this suite too.
#
# Green means the audit did both things a guard is worth having for: returned 1, so the
# suite calling it goes red, and said on stdout exactly which script offended and how. Both
# cases below are judged that way, so the block lives here once rather than once per case —
# the shape tests/unit/missing-argument-exit.test.sh's own `verdict` takes.
judge() {
  local name="$1" want="$2"; shift 2
  local rc=0
  ( source "$LIB"; "$@" ) > "$out" 2> "$err" || rc=$?
  if [[ "$rc" -ne 1 || "$(cat "$out")" != "$want" ]]; then
    no "$name (want exit 1 and stdout '$want'):"
    show_run "$rc" "$out" "$err"
  else
    ok
  fi
}

# 1. the offender is a script that says how it is called and then exits 1 — the shape
#    `${1:?usage: …}` produced in all seventeen scripts #270 measured. The audit has to
#    report it: a usage line on stderr is not enough when the status is an answer the
#    conductor would branch on as a methodology failure.
name="the guard names a script that exits 1, not 2, when its required argument is missing"
plant="$scratch/scripts"
mkdir -p "$plant"
cat > "$plant/exits-one.sh" <<'STUB'
#!/bin/sh
echo "usage: exits-one.sh <n>" >&2
exit 1
STUB
chmod +x "$plant/exits-one.sh"

judge "$name" 'exits-one.sh: want exit 2, got 1' \
  missing_argument_offender "$plant" exits-one.sh

# 2. the guard's other half, and the reason it reads source as well as exit codes: a script
#    whose refusal is a bare `${N:?…}` expansion. That expansion aborts the shell with 1, and
#    it can sit on a position no roster call reaches — a `${4:?…}` guarding the fourth
#    argument of a script whose first three are checked properly. Reading the tree instead of
#    calling it also covers a script added tomorrow by existing, with no roster to edit.
name="the guard names a script guarding a required argument with a bare \${N:?…} expansion"
scan="$scratch/scan"
mkdir -p "$scan"
cat > "$scan/bare.sh" <<'STUB'
#!/usr/bin/env bash
n="${1:?usage: bare.sh <n>}"
echo "$n"
STUB
cat > "$scan/checked.sh" <<'STUB'
#!/usr/bin/env bash
[[ -n "${1:-}" ]] || { echo "usage: checked.sh <n>" >&2; exit 2; }
echo "$1"
STUB
# The prose at the head of eight scripts quotes the very shape it is telling the reader not
# to use, so a scan that read comments would make the guard red for explaining itself. A
# whole line commented out is skipped; a `${N:?…}` in a trailing comment beside code is not,
# and there is no case for that here because it is not a promise the scan makes.
cat > "$scan/explains.sh" <<'STUB'
#!/usr/bin/env bash
  # Checked rather than read through `${1:?…}`, which aborts the shell with status 1.
[[ -n "${1:-}" ]] || { echo "usage: explains.sh <n>" >&2; exit 2; }
STUB
chmod +x "$scan/bare.sh" "$scan/checked.sh" "$scan/explains.sh"

judge "$name" 'bare.sh:2: guards $1 with a bare ${N:?…} expansion, which exits 1, not 2' \
  bare_expansion_offenders "$scan"

finish
