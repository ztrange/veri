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

# two_issue_fixture <dir> — a gh_fixture holding two solvable issues, #7 and #8.
two_issue_fixture() {
  gh_fixture "$1" <<'JSON'
[
  {"number": 7, "title": "first", "labels": [{"name": "ready-for-agent"}], "state": "OPEN",
   "body": "## Blocked by\n\nNone.\n"},
  {"number": 8, "title": "second", "labels": [{"name": "ready-for-agent"}], "state": "OPEN",
   "body": "## Blocked by\n\nNone.\n"}
]
JSON
}

# run_launcher <gh-dir> <stub> <out> [VAR=value ...] — run the copied skill's launcher over the
# fixture <gh-dir> with <stub> as the conductor's model, the caller's selection tunables stripped
# and any VAR=value given set, its output in <out>. Sets `code` to the launcher's exit status.
run_launcher() {
  local gh="$1" stub="$2" out="$3"
  shift 3
  env -u VERI_PARALLEL -u VERI_LABEL -u VERI_PRIORITY_LABEL -u VERI_MAX_ISSUES \
    VERI_GH_JSON="$gh" CLAUDE_BIN="$stub" VERI_POLL=0.05 "$@" \
    "$skill/scripts/parallel-conductors.sh" > "$out" 2>&1 && code=0 || code=$?
}

gh2="$work/gh2"
two_issue_fixture "$gh2"

# ready_pr <gh-dir> — print the stub source a conductor ends with to answer "done": append a
# ready PR saying `Closes #$n` to <gh-dir>'s `prs.lines` and rebuild `prs.json` from it, so the
# issue leaves the solvable set the way a finished run's does.
ready_pr() {
  cat <<SH
printf '{"body": "Closes #%s", "state": "OPEN", "isDraft": false, "url": "https://example.test/pull/%s"}\n' "\$n" "\$n" >> "$1/prs.lines"
printf '[%s]\n' "\$(paste -sd, "$1/prs.lines")" > "$1/prs.json"
SH
}

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
[[ "$got_timeline" == "$want_timeline" ]] \
  && ok || no "VERI_PARALLEL unset runs two solvable issues' conductors one after another (exit=$code)
$(diff <(printf '%s\n' "$want_timeline") <(printf '%s\n' "$got_timeline"))
launcher output:
$(cat "$work/seq.out")"

# 3. With VERI_PARALLEL=2, two solvable issues' conductors run at once: both have started before
# either has ended. The same stub shape as case 2's, over a fixture and timeline of its own —
# each conductor records `start <n>`, holds until a second conductor has started (or $PATIENCE s
# pass), then records `end <n>` and opens its ready PR. A launcher that ran them one after
# another shows an `end` among the first two lines, after the first stub has waited out its hold.
gh3="$work/gh3"
two_issue_fixture "$gh3"

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
[[ "$got_order" == "$want_order" ]] \
  && ok || no "launches follow solvable-issues.sh's printed order and never an issue it did not print (exit=$code)
$(diff <(printf '%s\n' "$want_order") <(printf '%s\n' "$got_order"))
launcher output:
$(cat "$work/order.out")"

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
[[ "$got_again" == "$want_again" ]] \
  && ok || no "an issue still solvable after its conductor finished is not launched a second time (exit=$code)
$(diff <(printf '%s\n' "$want_again") <(printf '%s\n' "$got_again"))
launcher output:
$(cat "$work/again.out")"

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
[[ "$got_unblock" == "$want_unblock" ]] \
  && ok || no "an issue that became solvable while another conductor ran is launched next (exit=$code)
$(diff <(printf '%s\n' "$want_unblock") <(printf '%s\n' "$got_unblock"))
launcher output:
$(cat "$work/unblock.out")"

# 7. VERI_MAX_ISSUES caps the launches of one invocation, 0 meaning no cap. The fixture holds
# three solvable issues, #7, #8 and #9; each stub conductor records `start <n>` and answers
# "done" with a ready PR, so its issue leaves the set. With VERI_MAX_ISSUES=2 the launcher starts
# 7 and 8 and stops, with 9 still solvable; with VERI_MAX_ISSUES=0 it starts all three. Each run
# gets a fresh fixture and record; every value that misbehaves is named in the single FAIL line.
cap_fixture() {
  gh_fixture "$1" <<'JSON'
[
  {"number": 7, "title": "first", "labels": [{"name": "ready-for-agent"}], "state": "OPEN",
   "body": "## Blocked by\n\nNone.\n"},
  {"number": 8, "title": "second", "labels": [{"name": "ready-for-agent"}], "state": "OPEN",
   "body": "## Blocked by\n\nNone.\n"},
  {"number": 9, "title": "third", "labels": [{"name": "ready-for-agent"}], "state": "OPEN",
   "body": "## Blocked by\n\nNone.\n"}
]
JSON
}

bad=""
for cap in 2 0; do
  gh7="$work/gh7-$cap"
  cap_fixture "$gh7"
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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
