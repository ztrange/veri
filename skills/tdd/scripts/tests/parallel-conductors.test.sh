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

# two_issue_fixture <dir> — a VERI_GH_JSON directory holding two solvable issues, #7 and #8, and
# no PR yet. `prs.lines` is where a stub conductor appends its PR, one JSON object per line, and
# rebuilds `prs.json` from.
two_issue_fixture() {
  mkdir -p "$1"
  : > "$1/prs.lines"
  printf '[]\n' > "$1/prs.json"
  cat > "$1/issues.json" <<'JSON'
[
  {"number": 7, "title": "first", "labels": [{"name": "ready-for-agent"}], "state": "OPEN",
   "body": "## Blocked by\n\nNone.\n"},
  {"number": 8, "title": "second", "labels": [{"name": "ready-for-agent"}], "state": "OPEN",
   "body": "## Blocked by\n\nNone.\n"}
]
JSON
}

gh2="$work/gh2"
two_issue_fixture "$gh2"

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
  cat > "$path" <<STUB
#!/bin/sh
n="\$(sed -n 's/^Solve issue #\([0-9]*\) .*/\1/p')"
$lock_take
echo "start \$n" >> "$timeline"
i=0
while [ "\$i" -lt \$(( ${PATIENCE:-1} * 50 )) ] && [ "\$(grep -c '^start' "$timeline")" -lt 2 ]; do
  sleep 0.02; i=\$((i + 1))
done
echo "end \$n" >> "$timeline"
printf '{"body": "Closes #%s", "state": "OPEN", "isDraft": false, "url": "https://example.test/pull/%s"}\n' "\$n" "\$n" >> "$gh/prs.lines"
printf '[%s]\n' "\$(paste -sd, "$gh/prs.lines")" > "$gh/prs.json"
$lock_drop
printf '%s\n' '{"type":"result","subtype":"success","is_error":false,"result":"ok"}'
exit 0
STUB
  chmod +x "$path"
}

timeline="$work/timeline"
seq_stub="$work/claude-seq"
timeline_stub "$seq_stub" "$timeline" "$gh2" "$work/running"

env -u VERI_PARALLEL -u VERI_LABEL -u VERI_PRIORITY_LABEL -u VERI_MAX_ISSUES \
  VERI_GH_JSON="$gh2" CLAUDE_BIN="$seq_stub" VERI_POLL=0.05 \
  "$skill/scripts/parallel-conductors.sh" > "$work/seq.out" 2>&1 && code=0 || code=$?
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

env -u VERI_LABEL -u VERI_PRIORITY_LABEL -u VERI_MAX_ISSUES \
  VERI_PARALLEL=2 VERI_GH_JSON="$gh3" CLAUDE_BIN="$par_stub" VERI_POLL=0.05 \
  "$skill/scripts/parallel-conductors.sh" > "$work/par.out" 2>&1 && code=0 || code=$?
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
mkdir -p "$gh4"
: > "$gh4/prs.lines"
printf '[]\n' > "$gh4/prs.json"
cat > "$gh4/issues.json" <<'JSON'
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
cat > "$order_stub" <<STUB
#!/bin/sh
n="\$(sed -n 's/^Solve issue #\([0-9]*\) .*/\1/p')"
echo "start \$n" >> "$order"
printf '{"body": "Closes #%s", "state": "OPEN", "isDraft": false, "url": "https://example.test/pull/%s"}\n' "\$n" "\$n" >> "$gh4/prs.lines"
printf '[%s]\n' "\$(paste -sd, "$gh4/prs.lines")" > "$gh4/prs.json"
printf '%s\n' '{"type":"result","subtype":"success","is_error":false,"result":"ok"}'
exit 0
STUB
chmod +x "$order_stub"

env -u VERI_PARALLEL -u VERI_LABEL -u VERI_PRIORITY_LABEL -u VERI_MAX_ISSUES \
  VERI_GH_JSON="$gh4" CLAUDE_BIN="$order_stub" VERI_POLL=0.05 \
  "$skill/scripts/parallel-conductors.sh" > "$work/order.out" 2>&1 && code=0 || code=$?
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
mkdir -p "$gh5"
: > "$gh5/prs.lines"
printf '[]\n' > "$gh5/prs.json"
cat > "$gh5/issues.json" <<'JSON'
[
  {"number": 7, "title": "stays solvable", "labels": [{"name": "ready-for-agent"}], "state": "OPEN",
   "body": "## Blocked by\n\nNone.\n"}
]
JSON

again="$work/again"
again_stub="$work/claude-again"
cat > "$again_stub" <<STUB
#!/bin/sh
n="\$(sed -n 's/^Solve issue #\([0-9]*\) .*/\1/p')"
if grep -x "start \$n" "$again" > /dev/null 2>&1; then
  printf '{"body": "Closes #%s", "state": "OPEN", "isDraft": false, "url": "https://example.test/pull/%s"}\n' "\$n" "\$n" >> "$gh5/prs.lines"
  printf '[%s]\n' "\$(paste -sd, "$gh5/prs.lines")" > "$gh5/prs.json"
fi
echo "start \$n" >> "$again"
printf '%s\n' '{"type":"result","subtype":"success","is_error":false,"result":"ok"}'
exit 0
STUB
chmod +x "$again_stub"

env -u VERI_PARALLEL -u VERI_LABEL -u VERI_PRIORITY_LABEL -u VERI_MAX_ISSUES \
  VERI_GH_JSON="$gh5" CLAUDE_BIN="$again_stub" VERI_POLL=0.05 \
  "$skill/scripts/parallel-conductors.sh" > "$work/again.out" 2>&1 && code=0 || code=$?
want_again="start 7"
got_again="$(cat "$again" 2>/dev/null)"
[[ "$got_again" == "$want_again" ]] \
  && ok || no "an issue still solvable after its conductor finished is not launched a second time (exit=$code)
$(diff <(printf '%s\n' "$want_again") <(printf '%s\n' "$got_again"))
launcher output:
$(cat "$work/again.out")"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
