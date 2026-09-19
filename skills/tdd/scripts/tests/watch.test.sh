#!/usr/bin/env bash
# Unit tests for `make watch` (#340) — a developer convenience that polls the tracked files
# and reruns `make unit` when one changes. Not a suite and not a gate.
# Zero-dependency plain-shell asserts, same idiom as profile.test.sh.
#
# Contract under test:
#   make -n watch  → exits 0; `watch` is a phony target of its own, neither a prerequisite
#                    of test, unit or merge-gates nor depending on any of them. Read off
#                    make's own database (`make -np`), which prints recipes without running
#                    them, so no suite and no poll loop runs.
#
# Not in tests/unit/: the cases driving the loop start real subprocesses, which the fast
# tier's admission bar excludes.
#
# Run: scripts/tests/watch.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem.
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

# prereqs <target> — the prerequisites make's database (`db`) lists on <target>'s rule line
# (the `<target>:` line followed by make's `#  Phony target` note), one per line.
prereqs() {
  awk -v t="$1:" '
    prev != "" && /^#  Phony target/ { sub(/^[^:]*:/, "", prev); print prev }
    { prev = ($1 == t) ? $0 : "" }
  ' <<< "$db" | tr ' ' '\n' | sed '/^$/d'
}

# 1. `make -np watch` exits 0, and its database marks `watch` phony, with no prerequisite
#    among test, unit and merge-gates — and none of those three lists `watch` as one.
name="make -n watch: its own .PHONY target, separate from test, unit and merge-gates"
problems=()
db="$(make --no-print-directory -np -C "$ROOT" watch 2>&1)" && code=0 || code=$?
[[ "$code" == 0 ]] ||
  problems+=("want make -n watch to exit 0, got $code: $(grep -m1 '\*\*\*' <<< "$db")")
awk '$1 == "watch:" { getline; if (/^#  Phony target/) found = 1 } END { exit !found }' \
  <<< "$db" || problems+=("no phony watch: entry in make's database")
for t in test unit merge-gates; do
  prereqs watch | grep -qx "$t" && problems+=("watch depends on $t")
  prereqs "$t" | grep -qx watch && problems+=("$t depends on watch")
done
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
