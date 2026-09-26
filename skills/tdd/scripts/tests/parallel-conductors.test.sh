#!/usr/bin/env bash
# Unit tests for scripts/parallel-conductors.sh — rung 3's selection layer. Run from a target
# repo's primary checkout, it launches up to VERI_PARALLEL supervised conductors at once over
# the issues solvable-issues.sh prints, and reports one line per issue it launched (#102).
#
# Contract under test (issue #102):
#   parallel-conductors.sh [--repo owner/name] [--continue-on-bail]
#   VERI_PARALLEL=<n>    conductors running at once, default 1. A whole number ≥ 1; anything
#                        else, set-but-empty included, is exit 2 before anything is launched,
#                        because N conductors are N concurrent `claude -p` sessions, billed as
#                        such — a value the script cannot read is never guessed into a spend.
#   VERI_GH_JSON=<dir>   passed through to solvable-issues.sh, so the solvable set is a
#                        fixture and no case reaches GitHub.
#   CLAUDE_BIN=<path>    passed through to every conductor: here a stub that records that it
#                        ran, which is what "a conductor was launched" means to these cases.
#
# Run: scripts/tests/parallel-conductors.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PARALLEL="$HERE/../parallel-conductors.sh"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
pass=0 fail=0
ok() { pass=$((pass + 1)); }
no() { fail=$((fail + 1)); echo "FAIL - $1"; }

# The target repo every case launches from: a fresh repository with one commit, standing in for
# the primary checkout of a repo that has never seen veri. The suite's cwd from here down, for
# the reason solvable-issues.test.sh gives for its own: a claim lock under THIS repository's
# `.tdd/wt/<n>` must never answer a question a case asked of its fixture.
target="$work/target"
git init -q -b main "$target" >/dev/null 2>&1
git -C "$target" -c user.name=t -c user.email=t@t commit -q --allow-empty -m init >/dev/null 2>&1
cd "$target" || exit 2

# The solvable set: one open, opted-in, unblocked, unclaimed issue, so a launcher that ignored
# a bad VERI_PARALLEL would have something to launch.
gh_json="$work/gh"
mkdir -p "$gh_json"
printf '[]\n' > "$gh_json/prs.json"
cat > "$gh_json/issues.json" <<'JSON'
[
  {
    "number": 7,
    "title": "a solvable issue",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## What to build\n\nSomething.\n\n## Blocked by\n\nNone.\n"
  }
]
JSON

# The stub conductor: any launch that got as far as the model leaves a line in $launched.
launched="$work/launched"
stub="$work/claude"
printf '#!/bin/sh\necho "$*" >> "%s"\n' "$launched" > "$stub"
chmod +x "$stub"

# 1. VERI_PARALLEL that is not a whole number ≥ 1 — zero, a word, set-but-empty — is exit 2
# and launches nothing: the stub never ran, and the launcher wrote no `.tdd/conductor-<n>.*`
# file in the target. The three values are the criterion's three shapes of "not a whole number
# ≥ 1", observed as one case; every one that misbehaves is named in the single FAIL line.
bad=""
for value in 0 two ''; do
  rm -f "$launched"
  env -u VERI_LABEL -u VERI_PRIORITY_LABEL -u VERI_MAX_ISSUES \
    VERI_PARALLEL="$value" VERI_GH_JSON="$gh_json" CLAUDE_BIN="$stub" \
    "$PARALLEL" >/dev/null 2>&1 && code=0 || code=$?
  conductor_files="$(ls -d .tdd/conductor-* 2>/dev/null)"
  if [[ "$code" != 2 || -e "$launched" || -n "$conductor_files" ]]; then
    bad+=" [VERI_PARALLEL='$value': exit=$code want 2, stub ran: $([[ -e "$launched" ]] && echo yes || echo no), conductor files: '${conductor_files}']"
  fi
done

[[ -z "$bad" ]] \
  && ok || no "VERI_PARALLEL not a whole number >= 1 (0, a word, set-but-empty) is exit 2 with no conductor launched ($bad )"

# 2. With VERI_PARALLEL unset — the default, 1 — two solvable issues' conductors run one after
# another: the second starts only after the first has ended. Observed through what each stub
# conductor writes to a shared timeline: `start <n>` when it begins, `end <n>` when it is done,
# and `overlap <n>` if another conductor was already running when it began — the running one
# holds a `mkdir` lock, which is atomic, so two at once cannot both miss it. Each stub then holds
# for up to $PATIENCE s, released early the moment another conductor starts, so a launcher that
# ran them together would be caught overlapping rather than winning a race by being slow.
#
# The launcher runs from a copy of the skill outside any git clone: from the real one,
# run-conductor.sh would fetch this repository's `origin` to pin its skill, and a suite never
# reaches a remote. Unpinned, it runs the copy as it is, which is all this case asks of it.
# Each stub answers "done" by opening a ready PR saying `Closes #<n>` in the fixture, so its
# issue leaves the solvable set the way a finished run's does.
skill="$work/skill"
mkdir -p "$skill"
cp "$HERE/../../SKILL.md" "$skill/SKILL.md"
cp -R "$HERE/.." "$skill/scripts"
rm -rf "$skill/scripts/tests"

# gh_fixture <dir> — a VERI_GH_JSON directory whose issues.json is read from stdin, and no PR
# yet. `prs.lines` is where a stub conductor appends its PR, one JSON object per line, and
# rebuilds `prs.json` from.
gh_fixture() {
  mkdir -p "$1"
  : > "$1/prs.lines"
  printf '[]\n' > "$1/prs.json"
  cat > "$1/issues.json"
}

# solvable_fixture <dir> <n>... — a gh_fixture holding one solvable issue per number given:
# open, opted in, blocked by nothing.
solvable_fixture() {
  local dir="$1" n sep="" issues="["
  shift
  for n in "$@"; do
    issues+="$sep"'{"number": '"$n"', "title": "issue '"$n"'", "labels": [{"name": "ready-for-agent"}], "state": "OPEN", "body": "## Blocked by\n\nNone.\n"}'
    sep=","
  done
  printf '%s]\n' "$issues" | gh_fixture "$dir"
}

# run_launcher <gh-dir> <stub> <out> [VAR=value ...] [-- <arg>...] — run the copied skill's
# launcher over the fixture <gh-dir> with <stub> as the conductor's model, the caller's selection
# tunables stripped, any VAR=value given set and any <arg> after `--` passed to it, its output in
# <out>. Sets `code` to the launcher's exit status.
run_launcher() {
  local gh="$1" stub="$2" out="$3" vars=()
  shift 3
  while (( $# )) && [[ "$1" != -- ]]; do vars+=("$1"); shift; done
  (( $# )) && shift
  env -u VERI_PARALLEL -u VERI_LABEL -u VERI_PRIORITY_LABEL -u VERI_MAX_ISSUES \
    VERI_GH_JSON="$gh" CLAUDE_BIN="$stub" VERI_POLL=0.05 "${vars[@]+"${vars[@]}"}" \
    "$skill/scripts/parallel-conductors.sh" "$@" > "$out" 2>&1 && code=0 || code=$?
}

# expect_lines <what> <want> <got> <out> — pass when <got> equals <want>; otherwise fail naming
# <what> with the launcher's exit status, a diff of the two, and the launcher's output in <out>.
expect_lines() {
  [[ "$3" == "$2" ]] \
    && ok || no "$1 (exit=$code)
$(diff <(printf '%s\n' "$2") <(printf '%s\n' "$3"))
launcher output:
$(cat "$4")"
}

gh2="$work/gh2"
solvable_fixture "$gh2" 7 8

# open_pr <gh-dir> <is-draft> — print the stub source that appends a PR saying `Closes #$n`,
# `isDraft` <is-draft>, to <gh-dir>'s `prs.lines` and rebuilds `prs.json` from it, so the issue
# leaves the solvable set the way a run that opened its PR does.
open_pr() {
  cat <<SH
printf '{"body": "Closes #%s", "state": "OPEN", "isDraft": $2, "url": "https://example.test/pull/%s"}\n' "\$n" "\$n" >> "$1/prs.lines"
printf '[%s]\n' "\$(paste -sd, "$1/prs.lines")" > "$1/prs.json"
SH
}

# ready_pr <gh-dir> — the stub source a conductor ends with to answer "done": a ready PR.
ready_pr() { open_pr "$1" false; }

# conductor_stub <path> — write an executable stub conductor to <path> whose body is read from
# stdin: it opens by reading the issue number the prompt names into `$n`, and closes by printing
# a successful result line and exiting 0, the way a finished `claude -p` session does.
conductor_stub() {
  {
    cat <<'HEAD'
#!/bin/sh
n="$(sed -n 's/^Solve issue #\([0-9]*\) .*/\1/p')"
HEAD
    cat
    cat <<'TAIL'
printf '%s\n' '{"type":"result","subtype":"success","is_error":false,"result":"ok"}'
exit 0
TAIL
  } > "$1"
  chmod +x "$1"
}

# record_stub <path> <record> <gh-dir> — write a stub conductor that appends `start <n>` to
# <record> and answers "done" with a ready PR in <gh-dir>, so its issue leaves the solvable set.
record_stub() {
  conductor_stub "$1" <<STUB
echo "start \$n" >> "$2"
$(ready_pr "$3")
STUB
}

# timeline_stub <path> <timeline> <gh-dir> [<lock-dir>] — write the stub conductor cases 2 and 3
# share: it records `start <n>`, holds until a second conductor has started (or $PATIENCE s
# pass), records `end <n>`, then answers "done" by opening a ready PR in <gh-dir>. Given a
# <lock-dir>, it also holds that `mkdir` lock while it runs and records `overlap <n>` first when
# another conductor already holds it.
timeline_stub() {
  local path="$1" timeline="$2" gh="$3" lock="${4:-}" lock_take="" lock_drop=""
  if [[ -n "$lock" ]]; then
    lock_take="if mkdir \"$lock\" 2>/dev/null; then held=1; else held=0; echo \"overlap \$n\" >> \"$timeline\"; fi"
    lock_drop="[ \"\$held\" = 1 ] && rmdir \"$lock\""
  fi
  conductor_stub "$path" <<STUB
$lock_take
echo "start \$n" >> "$timeline"
i=0
while [ "\$i" -lt \$(( ${PATIENCE:-1} * 50 )) ] && [ "\$(grep -c '^start' "$timeline")" -lt 2 ]; do
  sleep 0.02; i=\$((i + 1))
done
echo "end \$n" >> "$timeline"
$(ready_pr "$gh")
$lock_drop
STUB
}

timeline="$work/timeline"
seq_stub="$work/claude-seq"
timeline_stub "$seq_stub" "$timeline" "$gh2" "$work/running"

run_launcher "$gh2" "$seq_stub" "$work/seq.out"
want_timeline="$(printf 'start 7\nend 7\nstart 8\nend 8')"
got_timeline="$(cat "$timeline" 2>/dev/null)"
expect_lines "VERI_PARALLEL unset runs two solvable issues' conductors one after another" "$want_timeline" "$got_timeline" "$work/seq.out"

# 3. With VERI_PARALLEL=2, two solvable issues' conductors run at once: both have started before
# either has ended. The same stub shape as case 2's, over a fixture and timeline of its own —
# each conductor records `start <n>`, holds until a second conductor has started (or $PATIENCE s
# pass), then records `end <n>` and opens its ready PR. A launcher that ran them one after
# another shows an `end` among the first two lines, after the first stub has waited out its hold.
gh3="$work/gh3"
solvable_fixture "$gh3" 7 8

timeline3="$work/timeline3"
par_stub="$work/claude-par"
timeline_stub "$par_stub" "$timeline3" "$gh3"

run_launcher "$gh3" "$par_stub" "$work/par.out" VERI_PARALLEL=2
got_timeline="$(cat "$timeline3" 2>/dev/null)"
first_two="$(head -n 2 "$timeline3" 2>/dev/null | sort)"
all_four="$(sort "$timeline3" 2>/dev/null)"
[[ "$first_two" == "$(printf 'start 7\nstart 8')" \
   && "$all_four" == "$(printf 'end 7\nend 8\nstart 7\nstart 8')" ]] \
  && ok || no "VERI_PARALLEL=2 runs two solvable issues' conductors at once — both start before either ends (exit=$code)
timeline:
$got_timeline
launcher output:
$(cat "$work/par.out")"

# 4. Launches follow solvable-issues.sh's printed order and never include an issue it did not
# print. The fixture holds four open issues: #5 is not opted in, #6 is opted in but blocked by
# the open #9, #7 is solvable in the unlabelled band and #8 in the `priority` band — so
# solvable-issues.sh prints 8 then 7, out of numeric order, and never 5, 6 or 9. Each stub
# conductor records `start <n>` and answers "done" with a ready PR, so its issue leaves the set.
# At the default VERI_PARALLEL=1 the launch order is the whole timeline: 8, then 7, nothing else.
gh4="$work/gh4"
gh_fixture "$gh4" <<'JSON'
[
  {"number": 5, "title": "not opted in", "labels": [], "state": "OPEN",
   "body": "## Blocked by\n\nNone.\n"},
  {"number": 6, "title": "blocked", "labels": [{"name": "ready-for-agent"}], "state": "OPEN",
   "body": "## Blocked by\n\n- #9\n"},
  {"number": 7, "title": "plain", "labels": [{"name": "ready-for-agent"}], "state": "OPEN",
   "body": "## Blocked by\n\nNone.\n"},
  {"number": 8, "title": "urgent", "labels": [{"name": "ready-for-agent"}, {"name": "priority"}],
   "state": "OPEN", "body": "## Blocked by\n\nNone.\n"},
  {"number": 9, "title": "the open blocker", "labels": [], "state": "OPEN",
   "body": "## Blocked by\n\nNone.\n"}
]
JSON

order="$work/order"
order_stub="$work/claude-order"
record_stub "$order_stub" "$order" "$gh4"

run_launcher "$gh4" "$order_stub" "$work/order.out"
want_order="$(printf 'start 8\nstart 7')"
got_order="$(cat "$order" 2>/dev/null)"
expect_lines "launches follow solvable-issues.sh's printed order and never an issue it did not print" "$want_order" "$got_order" "$work/order.out"

# 5. An issue solvable-issues.sh still prints after its conductor finished is not launched a
# second time in the same invocation. The stub conductor for #7 records `start 7` and ends
# without opening a PR — a run that left no claim behind — so #7 stays in the solvable set when
# the launcher re-selects. A second launch of the same number is the failure; that stub opens
# a ready PR on it, so a launcher that relaunches still ends rather than looping.
gh5="$work/gh5"
gh_fixture "$gh5" <<'JSON'
[
  {"number": 7, "title": "stays solvable", "labels": [{"name": "ready-for-agent"}], "state": "OPEN",
   "body": "## Blocked by\n\nNone.\n"}
]
JSON

again="$work/again"
again_stub="$work/claude-again"
conductor_stub "$again_stub" <<STUB
if grep -x "start \$n" "$again" > /dev/null 2>&1; then
  $(ready_pr "$gh5")
fi
echo "start \$n" >> "$again"
STUB

run_launcher "$gh5" "$again_stub" "$work/again.out"
want_again="start 7"
got_again="$(cat "$again" 2>/dev/null)"
expect_lines "an issue still solvable after its conductor finished is not launched a second time" "$want_again" "$got_again" "$work/again.out"

# 6. The solvable set is re-asked after every completion, so an issue that became solvable while
# another conductor ran is launched next. The fixture holds #7, solvable, and #8, blocked by the
# open #9 — so the first selection prints only 7. #7's stub conductor closes #9 while it runs, the
# way a human's merge would, and answers "done" with a ready PR; #8 is solvable only from then on.
# A launcher that re-selects after #7 finishes launches #8 next; one that cached its first answer
# has nothing left to launch and ends after #7 alone.
gh6="$work/gh6"
gh_fixture "$gh6" <<'JSON'
[
  {"number": 7, "title": "runs first", "labels": [{"name": "ready-for-agent"}], "state": "OPEN",
   "body": "## Blocked by\n\nNone.\n"},
  {"number": 8, "title": "unblocked mid-run", "labels": [{"name": "ready-for-agent"}], "state": "OPEN",
   "body": "## Blocked by\n\n- #9\n"},
  {"number": 9, "title": "the blocker", "labels": [], "state": "OPEN",
   "body": "## Blocked by\n\nNone.\n"}
]
JSON

unblock="$work/unblock"
unblock_stub="$work/claude-unblock"
conductor_stub "$unblock_stub" <<STUB
echo "start \$n" >> "$unblock"
if [ "\$n" = 7 ]; then
  sed 's/"title": "the blocker", "labels": \[\], "state": "OPEN"/"title": "the blocker", "labels": [], "state": "CLOSED"/' \
    "$gh6/issues.json" > "$gh6/issues.json.new" && mv "$gh6/issues.json.new" "$gh6/issues.json"
fi
$(ready_pr "$gh6")
STUB

run_launcher "$gh6" "$unblock_stub" "$work/unblock.out"
want_unblock="$(printf 'start 7\nstart 8')"
got_unblock="$(cat "$unblock" 2>/dev/null)"
expect_lines "an issue that became solvable while another conductor ran is launched next" "$want_unblock" "$got_unblock" "$work/unblock.out"

# 7. VERI_MAX_ISSUES caps the launches of one invocation, 0 meaning no cap. The fixture holds
# three solvable issues, #7, #8 and #9; each stub conductor records `start <n>` and answers
# "done" with a ready PR, so its issue leaves the set. With VERI_MAX_ISSUES=2 the launcher starts
# 7 and 8 and stops, with 9 still solvable; with VERI_MAX_ISSUES=0 it starts all three. Each run
# gets a fresh fixture and record; every value that misbehaves is named in the single FAIL line.
bad=""
for cap in 2 0; do
  gh7="$work/gh7-$cap"
  solvable_fixture "$gh7" 7 8 9
  capped="$work/capped-$cap"
  cap_stub="$work/claude-cap-$cap"
  record_stub "$cap_stub" "$capped" "$gh7"
  run_launcher "$gh7" "$cap_stub" "$work/cap-$cap.out" VERI_MAX_ISSUES="$cap"
  case "$cap" in
    2) want_cap="$(printf 'start 7\nstart 8')" ;;
    0) want_cap="$(printf 'start 7\nstart 8\nstart 9')" ;;
  esac
  got_cap="$(cat "$capped" 2>/dev/null)"
  if [[ "$got_cap" != "$want_cap" ]]; then
    bad+=" [VERI_MAX_ISSUES=$cap: exit=$code, launched '$(printf '%s' "$got_cap" | tr '\n' ',')' want '$(printf '%s' "$want_cap" | tr '\n' ',')']"
  fi
done

[[ -z "$bad" ]] \
  && ok || no "VERI_MAX_ISSUES caps the launches of one invocation, 0 meaning no cap ($bad )"

# 8. A finished conductor's outcome is read from its PR and its run's event log, and reported one
# line per issue: #7's stub conductor opens a ready PR — done — and #8's opens a draft PR and ends
# its run's event log, `.tdd/wt/8/.tdd/events.jsonl` in the target, in a `bail` — bailed. Both
# PRs say `Closes #<n>`, so each issue leaves the solvable set. #9's stub opens a draft PR too, but
# its event log only *contains* a bail — a resumed run's `launch` follows it — so its draft is not a
# bail and #9 must not be reported bailed. At the default VERI_PARALLEL=1 the launcher runs 7, 8
# then 9, and its output carries `#7 — done <url>` and `#8 — bailed <url>`, and no bailed line for 9.
gh8="$work/gh8"
solvable_fixture "$gh8" 7 8 9

outcome_stub="$work/claude-outcome"
conductor_stub "$outcome_stub" <<STUB
if [ "\$n" = 8 ] || [ "\$n" = 9 ]; then
  mkdir -p ".tdd/wt/\$n/.tdd"
  printf '%s\n' '{"ts": 1, "issue": "'"\$n"'", "actor": "conductor", "phase": "develop-red", "step": "1", "event": "launch", "attempt": "1", "skill_commit": ""}' \
    '{"ts": 2, "issue": "'"\$n"'", "actor": "conductor", "phase": "develop-red", "step": "1", "event": "bail", "attempt": "1", "skill_commit": "", "cause": "revise-budget"}' \
    >> ".tdd/wt/\$n/.tdd/events.jsonl"
  [ "\$n" = 9 ] && printf '%s\n' '{"ts": 3, "issue": "9", "actor": "conductor", "phase": "develop-red", "step": "1", "event": "launch", "attempt": "2", "skill_commit": ""}' \
    >> ".tdd/wt/\$n/.tdd/events.jsonl"
  $(open_pr "$gh8" true)
else
  $(ready_pr "$gh8")
fi
STUB

run_launcher "$gh8" "$outcome_stub" "$work/outcome.out"
want_outcome="$(printf '#7 — done https://example.test/pull/7\n#8 — bailed https://example.test/pull/8')"
got_outcome="$(grep -E '^#[0-9]+ — ' "$work/outcome.out")"
expect_lines "a ready PR is reported '#<n> — done <pr-url>', a draft PR whose event log ends in a bail '#<n> — bailed <pr-url>', and a draft PR whose log does not end in one never bailed" "$want_outcome" "$got_outcome" "$work/outcome.out"

# 9. A conductor its supervisor killed — `supervise.sh` exit 2 — is reported `#<n> — killed after
# <VERI_RUN_TIMEOUT>s`. #7's stub conductor never answers: it holds for up to $PATIENCE s and
# opens no PR. The supervisor's awake clock is injected (VERI_AWAKE_CLOCK) as a stub that jumps
# 1000 s on every reading, so any hard timeout is exceeded at the first poll and the kill lands
# without waiting on wall time. With VERI_RUN_TIMEOUT=60 the launcher's report carries
# `#7 — killed after 60s`.
gh9="$work/gh9"
solvable_fixture "$gh9" 7

jump_clock="$work/awake-clock"
printf '#!/bin/sh\nc="$(cat "%s" 2>/dev/null || echo 0)"\nc=$((c + 1000))\necho "$c" > "%s"\necho "$c"\n' \
  "$work/awake-count" "$work/awake-count" > "$jump_clock"
chmod +x "$jump_clock"

hang_stub="$work/claude-hang"
conductor_stub "$hang_stub" <<STUB
i=0
while [ "\$i" -lt \$(( ${PATIENCE:-5} * 50 )) ]; do sleep 0.02; i=\$((i + 1)); done
STUB

run_launcher "$gh9" "$hang_stub" "$work/killed.out" VERI_RUN_TIMEOUT=60 VERI_AWAKE_CLOCK="$jump_clock" VERI_KILL_POLL=0.01
want_killed="#7 — killed after 60s"
got_killed="$(grep -E '^#[0-9]+ — ' "$work/killed.out")"
expect_lines "a conductor its supervisor killed (supervise exit 2) is reported '#<n> — killed after <VERI_RUN_TIMEOUT>s'" "$want_killed" "$got_killed" "$work/killed.out"

# 10. The first bail stops new launches while the conductors already running are waited to
# completion, and --continue-on-bail keeps launching and skips the bailed number. The fixture
# holds three solvable issues, #11, #12 and #13, at VERI_PARALLEL=2, so #11 and #12 start
# together. #11's stub conductor bails at once: a draft PR saying `Closes #11` and an event log
# at `.tdd/wt/11/.tdd/events.jsonl` ending in a `bail`. #12's is still running when it does —
# it holds until #13 has started (or $PATIENCE s pass), then records `end 12` and answers "done"
# with a ready PR — and #13's records `start 13` and answers "done". Without the flag the
# launcher never starts #13 and still waits for #12 (`end 12` recorded, `#12 — done` reported);
# with it, #13 is launched and #11 is never launched a second time. Each run gets a fresh
# fixture, record and event log; every mode that misbehaves is named in the single FAIL line.
bad=""
for mode in stop continue; do
  gh10="$work/gh10-$mode"
  solvable_fixture "$gh10" 11 12 13
  rm -rf .tdd/wt/11
  bail_record="$work/bail-$mode"
  bail_stub="$work/claude-bail-$mode"
  conductor_stub "$bail_stub" <<STUB
echo "start \$n" >> "$bail_record"
case "\$n" in
  11)
    mkdir -p ".tdd/wt/11/.tdd"
    printf '%s\n' '{"ts": 1, "issue": "11", "actor": "conductor", "phase": "develop-red", "step": "1", "event": "bail", "attempt": "1", "skill_commit": "", "cause": "revise-budget"}' \
      >> ".tdd/wt/11/.tdd/events.jsonl"
    $(open_pr "$gh10" true)
    ;;
  12)
    i=0
    while [ "\$i" -lt \$(( ${PATIENCE:-1} * 50 )) ] && ! grep -x 'start 13' "$bail_record" > /dev/null 2>&1; do
      sleep 0.02; i=\$((i + 1))
    done
    echo "end 12" >> "$bail_record"
    $(ready_pr "$gh10")
    ;;
  *)
    $(ready_pr "$gh10")
    ;;
esac
STUB
  flag=()
  [[ "$mode" == continue ]] && flag=(-- --continue-on-bail)
  run_launcher "$gh10" "$bail_stub" "$work/bail-$mode.out" VERI_PARALLEL=2 "${flag[@]+"${flag[@]}"}"
  got_bail="$(sort "$bail_record" 2>/dev/null | tr '\n' ',')"
  case "$mode" in
    stop)     want_bail="end 12,start 11,start 12," ;;
    continue) want_bail="end 12,start 11,start 12,start 13," ;;
  esac
  twelve_done="$(grep -xF '#12 — done https://example.test/pull/12' "$work/bail-$mode.out")"
  if [[ "$got_bail" != "$want_bail" || -z "$twelve_done" ]]; then
    bad+=" [$mode: exit=$code, record '$got_bail' want '$want_bail', #12 reported done: $([[ -n "$twelve_done" ]] && echo yes || echo no); output: $(tr '\n' '|' < "$work/bail-$mode.out")]"
  fi
done

[[ -z "$bad" ]] \
  && ok || no "the first bail stops new launches while running conductors finish, and --continue-on-bail keeps launching and skips the bailed number ($bad )"

# 11. The first kill stops new launches the way the first bail does. Two solvable issues, #7 and
# #8, at the default VERI_PARALLEL=1, with case 9's never-answering stub conductor and jumping
# awake clock, so every conductor's supervisor kills it at the first poll. #7 is killed, so the
# launcher never starts #8: the report holds `#7 — killed after 60s` and no line for #8, which a
# launcher that kept going would report killed too.
gh11="$work/gh11"
solvable_fixture "$gh11" 7 8
rm -f "$work/awake-count"

run_launcher "$gh11" "$hang_stub" "$work/kill-stop.out" VERI_RUN_TIMEOUT=60 VERI_AWAKE_CLOCK="$jump_clock" VERI_KILL_POLL=0.01
want_kill_stop="#7 — killed after 60s"
got_kill_stop="$(grep -E '^#[0-9]+ — ' "$work/kill-stop.out")"
expect_lines "the first kill stops new launches: #8 is never launched after #7 is killed" "$want_kill_stop" "$got_kill_stop" "$work/kill-stop.out"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
