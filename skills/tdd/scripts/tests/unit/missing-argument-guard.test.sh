#!/usr/bin/env bash
# Unit tests for lib/missing-argument-exit.sh, the audit tests/unit/missing-argument-exit.test.sh
# runs over every script that requires a positional argument, asked about a planted offender.
# Fast tier by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Contract under test:
#   Handed a directory and the name of a script in it that exits 1 with a usage line when
#   called with no arguments, the audit prints one offender line naming that script and the
#   status it came back with, and returns 1.
#   Handed only a directory, the audit names every script in it whose source prints a usage
#   line and that, called with no arguments, does not exit 2 with its own usage text on stderr.
#   Handed a directory with no scripts in it, the audit prints nothing and returns 0.
#
# Run: scripts/tests/unit/missing-argument-guard.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LIB="$HERE/../../lib/missing-argument-exit.sh"
source "$HERE/../lib/harness.sh"
scratch="$(scratch_dir)"
out="$scratch/out" err="$scratch/err"

show_run() {  # show_run <exit> <stdout-file> <stderr-file> — print what a failing case got
  echo "    exit $1"; echo "    stdout: $(printf '%q' "$(cat "$2")")"
  echo "    stderr: $(printf '%q' "$(cat "$3")")"
}

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
printf '%s\n' '#!/usr/bin/env bash' \
  '  # Checked rather than read through `${1:?…}`, which aborts the shell with status 1.' \
  '[[ -n "${1:-}" ]] || { echo "usage: explains.sh <n>" >&2; exit 2; }' > "$scan/explains.sh"
chmod +x "$scan/bare.sh" "$scan/checked.sh" "$scan/explains.sh"

judge "$name" 'bare.sh:2: guards $1 with a bare ${N:?…} expansion, which exits 1, not 2' \
  bare_expansion_offenders "$scan"

name="the audit finds its own subjects: every script printing a usage line that does not exit 2 with its own usage text when its required argument is missing"
found="$scratch/found"
mkdir -p "$found"
cat > "$found/needs-one.sh" <<'STUB'
#!/bin/sh
[ -n "$1" ] || { echo "usage: needs-one.sh <n>" >&2; exit 1; }
STUB
cat > "$found/borrowed.sh" <<'STUB'
#!/bin/sh
[ -n "$1" ] || { echo "usage: other.sh <n>" >&2; exit 2; }
STUB
cat > "$found/refuses.sh" <<'STUB'
#!/bin/sh
[ -n "$1" ] || { echo "usage: refuses.sh <n>" >&2; exit 2; }
STUB
cat > "$found/no-usage.sh" <<'STUB'
#!/bin/sh
exit 0
STUB
chmod +x "$found"/*.sh
rc=0
( source "$LIB"; missing_argument_audit "$found" ) > "$out" 2> "$err" || rc=$?
named="$(cut -d: -f1 < "$out" | sort | tr '\n' ' ')"
if [[ "$rc" -ne 1 || "$named" != "borrowed.sh needs-one.sh " ]]; then
  no "$name (want exit 1 naming exactly borrowed.sh and needs-one.sh):"
  show_run "$rc" "$out" "$err"
else
  ok
fi

name="the audit over a directory with no scripts prints nothing, on either stream, and returns 0"
bare="$scratch/bare"
mkdir -p "$bare"
rc=0
( source "$LIB"; missing_argument_audit "$bare" ) > "$out" 2> "$err" || rc=$?
if [[ "$rc" -ne 0 || -s "$out" || -s "$err" ]]; then
  no "$name (want exit 0 and no output):"
  show_run "$rc" "$out" "$err"
else
  ok
fi

finish
