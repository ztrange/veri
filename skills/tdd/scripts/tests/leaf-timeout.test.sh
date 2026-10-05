#!/usr/bin/env bash
# Unit tests for scripts/leaf-timeout.sh — sizes the run's hard timeout from the wall time
# preflight measured on the green-baseline run.
#
# Contract under test:
#   leaf-timeout.sh <baseline-seconds>  with VERI_TIMEOUT unset
#                              → prints the larger of 900 and 6 × <baseline-seconds>,
#                                as a whole number of seconds, and exits 0.
#   a baseline that is not a whole number ≥ 0 (`abc`, `-1`, `1.5`, or no argument at all)
#                              → exit 2, a diagnostic on stderr, nothing on stdout.
#
# Run: scripts/tests/leaf-timeout.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LEAF_TIMEOUT="$HERE/../leaf-timeout.sh"

source "$HERE/lib/harness.sh"

capture() {
  probe_out="$(mktemp)" probe_err="$(mktemp)"
  "$@" >"$probe_out" 2>"$probe_err" && probe_code=0 || probe_code=$?
}

capture_done() {
  rm -f "$probe_out" "$probe_err"
}

good_probe() {
  local baseline="$1" want="$2"
  capture env -u VERI_TIMEOUT "$LEAF_TIMEOUT" "$baseline"
  assert_answer "baseline $baseline" "$want"
  capture_done
}

assert_answer() {
  local label="$1" want="$2"
  [[ "$probe_code" == 0 ]] ||
    problems+=("$label: want exit 0, got $probe_code")
  [[ "$(cat "$probe_out")" == "$want" ]] ||
    problems+=("$label: want $want on stdout, got: $(printf '%q' "$(cat "$probe_out")")")
  [[ ! -s "$probe_err" ]] ||
    problems+=("$label: want nothing on stderr, got: $(printf '%q' "$(cat "$probe_err")")")
}

assert_fail_closed() {
  local label="$1"
  [[ "$probe_code" == 2 ]] ||
    problems+=("$label: want exit 2, got $probe_code")
  [[ ! -s "$probe_out" ]] ||
    problems+=("$label: want nothing on stdout, got: $(printf '%q' "$(cat "$probe_out")")")
  [[ -s "$probe_err" ]] ||
    problems+=("$label: want a diagnostic on stderr, got nothing")
}

bad_probe() {
  local label="$1"; shift
  capture env -u VERI_TIMEOUT "$LEAF_TIMEOUT" "$@"
  assert_fail_closed "$label"
  capture_done
}

name="VERI_TIMEOUT unset: the baseline derives max(900, 6 × baseline) on stdout; a baseline that is not a whole number >= 0 exits 2 with a diagnostic on stderr and nothing on stdout"
problems=()
good_probe 0 900
good_probe 5 900
good_probe 150 900
good_probe 151 906
good_probe 200 1200
bad_probe "baseline abc" abc
bad_probe "baseline -1" -1
bad_probe "baseline 1.5" 1.5
bad_probe "no argument"
report "$name"

name="leaf-timeout.sh ten, with VERI_TIMEOUT unset, exits 2 with nothing on stdout and exactly the diagnostic and the usage line on stderr"
problems=()
capture env -u VERI_TIMEOUT "$LEAF_TIMEOUT" ten
want_err="leaf-timeout: <baseline-seconds> must be a whole number >= 0: ten
usage: leaf-timeout.sh <baseline-seconds> [refactor | --full <full-seconds>]"
[[ "$probe_code" == 2 ]] ||
  problems+=("want exit 2, got $probe_code")
[[ ! -s "$probe_out" ]] ||
  problems+=("want nothing on stdout, got: $(printf '%q' "$(cat "$probe_out")")")
[[ "$(cat "$probe_err")" == "$want_err" ]] ||
  problems+=("want stderr $(printf '%q' "$want_err"), got: $(printf '%q' "$(cat "$probe_err")")")
capture_done
report "$name"



name="leaf-timeout.sh, run through a symlink to the skill directory and from another working directory, prints the same stdout, stderr and exit code as when run in place, for a good baseline and for a bad one"
problems=()
work="$(scratch_dir)"
ln -s "$(cd "$HERE/../.." && pwd)" "$work/linked-skill"
mkdir -p "$work/elsewhere"
for baseline in 200 ten; do
  in_out="$(cd "$HERE/.." && env -u VERI_TIMEOUT ./leaf-timeout.sh "$baseline" 2>"$work/in.err")" && in_code=0 || in_code=$?
  ln_out="$(cd "$work/elsewhere" && env -u VERI_TIMEOUT "$work/linked-skill/scripts/leaf-timeout.sh" "$baseline" 2>"$work/ln.err")" && ln_code=0 || ln_code=$?
  in_err="$(cat "$work/in.err")" ln_err="$(cat "$work/ln.err")"
  case "$baseline" in
    200) [[ "$in_code" == 0 && "$in_out" == 1200 ]] ||
           problems+=("baseline 200 in place: want 1200 and exit 0, got $(printf '%q' "$in_out") and exit $in_code") ;;
    ten) [[ "$in_code" == 2 && -n "$in_err" ]] ||
           problems+=("baseline ten in place: want exit 2 and a diagnostic, got exit $in_code and stderr $(printf '%q' "$in_err")") ;;
  esac
  [[ "$ln_out" == "$in_out" ]] ||
    problems+=("baseline $baseline: stdout through the symlink $(printf '%q' "$ln_out"), in place $(printf '%q' "$in_out")")
  [[ "$ln_err" == "$in_err" ]] ||
    problems+=("baseline $baseline: stderr through the symlink $(printf '%q' "$ln_err"), in place $(printf '%q' "$in_err")")
  [[ "$ln_code" == "$in_code" ]] ||
    problems+=("baseline $baseline: exit through the symlink $ln_code, in place $in_code")
done
report "$name"

name="#954: VERI_ISSUE=954 leaf-timeout.sh 10 --full 200 records its settled 1200 in the run worktree's .tdd/issue-954-timeout, and a second settling for the same issue (--full 300, a resumed session) leaves that 1200 in place"
problems=()
work="$(scratch_dir)"
new_repo -b main "$work" >/dev/null 2>&1
mkdir -p "$work/.tdd"
( cd "$work" && env -u VERI_TIMEOUT VERI_ISSUE=954 "$LEAF_TIMEOUT" 10 --full 200 ) >/dev/null 2>"$work/first.err"
first_record="$(cat "$work/.tdd/issue-954-timeout" 2>/dev/null || echo '<no record>')"
[[ "$first_record" == 1200 ]] ||
  problems+=("first settling: want .tdd/issue-954-timeout holding 1200, got $(printf '%q' "$first_record") (stderr: $(cat "$work/first.err"))")
( cd "$work" && env -u VERI_TIMEOUT VERI_ISSUE=954 "$LEAF_TIMEOUT" 10 --full 300 ) >/dev/null 2>"$work/second.err"
second_record="$(cat "$work/.tdd/issue-954-timeout" 2>/dev/null || echo '<no record>')"
[[ "$second_record" == 1200 ]] ||
  problems+=("second settling: want .tdd/issue-954-timeout still holding the first session's 1200, got $(printf '%q' "$second_record") (stderr: $(cat "$work/second.err"))")
report "$name"

name="#954: with VERI_ISSUE unset, leaf-timeout.sh 10 --full 200 still prints 1200 and records no settled timeout under .tdd"
problems=()
work="$(scratch_dir)"
new_repo -b main "$work" >/dev/null 2>&1
( cd "$work" && env -u VERI_TIMEOUT -u VERI_ISSUE "$LEAF_TIMEOUT" 10 --full 200 ) >"$work/out" 2>"$work/err"
[[ "$(cat "$work/out")" == 1200 ]] ||
  problems+=("want stdout 1200, got $(printf '%q' "$(cat "$work/out")") (stderr: $(cat "$work/err"))")
recorded=("$work"/.tdd/issue-*timeout)
[[ ! -e "${recorded[0]}" ]] ||
  problems+=("want no .tdd/issue-*timeout record, found: ${recorded[*]#"$work"/}")
report "$name"

name="#954: VERI_ISSUE=954 leaf-timeout.sh 10 --full 200, run from a subdirectory of the run worktree, records its settled 1200 at the worktree root's .tdd/issue-954-timeout, where supervise.sh reads it"
problems=()
work="$(scratch_dir)"
new_repo -b main "$work" >/dev/null 2>&1
mkdir -p "$work/sub/dir"
( cd "$work/sub/dir" && env -u VERI_TIMEOUT VERI_ISSUE=954 "$LEAF_TIMEOUT" 10 --full 200 ) >/dev/null 2>"$work/err"
root_record="$(cat "$work/.tdd/issue-954-timeout" 2>/dev/null || echo '<no record>')"
[[ "$root_record" == 1200 ]] ||
  problems+=("want the worktree root's .tdd/issue-954-timeout holding 1200, got $(printf '%q' "$root_record") (stderr: $(cat "$work/err"))")
report "$name"

finish
