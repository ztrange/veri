#!/usr/bin/env bash
# Unit tests for no-size-assertion.test.sh itself — how many grep and sed processes its probe
# starts (issue #332). Like metrics-python3-starts.test.sh this suite's subject is another
# suite. Zero-dependency plain-shell asserts, same idiom as metrics-python3-starts.test.sh.
#
# no-size-assertion.test.sh scans every suite in its own directory. Asked per file, that is a
# `sed` (the file's subjects) and a `grep` (its size-verb lines) for each of them, although
# only a handful of files contain a size-verb line at all. Asked of the directory once, one
# `grep` names the handful and the per-file work runs on those alone. The count of processes
# started is the observable, not a timer.
#
# Contract under test, observed by running a copy of no-size-assertion.test.sh in a fixture
# directory of suites, with a PATH-first `grep` and `sed` that each append one line to a
# counter file before exec'ing the real binary:
#   the probe → still green on its one case, and its first grep-or-sed start is one `grep`
#               across every suite in the scanned directory — the only such start in the run.
#
# Run: skills/tdd/scripts/tests/no-size-assertion-forks.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
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

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

# The fixture directory: the suite under observation, whose `$HERE` is where it scans, beside
# five suites of which two carry a size-verb line — neither about the two documents, so the
# observed suite stays green and every start the shims count is the probe asking.
scanned="$tmp/tests"
mkdir -p "$scanned" "$tmp/bin"
cp "$HERE/no-size-assertion.test.sh" "$scanned/"
for i in 1 2 3; do
  printf '#!/usr/bin/env bash\necho "plain suite %s"\n' "$i" > "$scanned/plain-$i.test.sh"
done
printf '#!/usr/bin/env bash\nlines="$(wc -l < "$plan")"\n' > "$scanned/counts-plan.test.sh"
printf '#!/usr/bin/env bash\nsize="$(stat -f %%z "$log")"\n' > "$scanned/sizes-log.test.sh"
suites=6

# One line per start: the verb, then how many of the scanned directory's suites its arguments
# reach — a file named directly counts one, the directory itself counts all of them.
starts_log="$tmp/starts"
: > "$starts_log"
for verb in grep sed; do
  real="$(command -v "$verb")"
  cat > "$tmp/bin/$verb" <<SHIM
#!/bin/sh
n=0
for a in "\$@"; do
  case "\$a" in
    '$scanned'|'$scanned/') n=\$((n + $suites)) ;;
    '$scanned'/*.test.sh) [ -f "\$a" ] && n=\$((n + 1)) ;;
  esac
done
printf '%s %s\n' '$verb' "\$n" >> '$starts_log'
exec '$real' "\$@"
SHIM
  chmod +x "$tmp/bin/$verb"
done

# 1. The criterion: before any per-file work the probe makes one grep across the whole
#    scanned directory, and only one.
#      → the observed suite `1 passed, 0 failed`; the counter's first line `grep 6`, and
#        exactly one line reaching all six suites.
name="no-size-assertion.test.sh's probe makes exactly one grep across the whole scanned directory before any per-file work, counted by a PATH-first shim in front of grep and sed"
problems=()

out="$(PATH="$tmp/bin:$PATH" "$scanned/no-size-assertion.test.sh" 2>&1)"
[[ "$out" == *'1 passed, 0 failed'* ]] ||
  problems+=("setup: want the observed suite green on its one case, got: $(printf '%q' "$out")")
[[ -s "$starts_log" ]] ||
  problems+=("setup: want the counting shim to see grep or sed started at all, got nothing")

first="$(head -n 1 "$starts_log")"
[[ "$first" == "grep $suites" ]] ||
  problems+=("want the first grep-or-sed start to be one grep across all $suites suites in the scanned directory, got: '$first'")
whole="$(awk -v n="$suites" '$1 == "grep" && $2 >= n' "$starts_log" | wc -l | tr -d ' ')"
[[ "$whole" -eq 1 ]] ||
  problems+=("want exactly 1 grep across the whole scanned directory, got $whole")

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
