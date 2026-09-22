#!/usr/bin/env bash
# Unit test for the guard that keeps a verifier launch out of the shape that stalled #297 —
# case 5 of skills/tdd/scripts/tests/skill-leaf-launch.test.sh, which reads SKILL.md's
# fenced launch lines and refuses one that reaches `verify.sh` without naming
# `supervise.sh`. Like docs-read-guard.test.sh, prose-drift-red.test.sh and
# hermetic-suites.test.sh this suite has no script as its subject: its subject is what
# another suite reports about the document it is run against. Zero-dependency plain-shell
# asserts, same idiom as docs-read-guard.test.sh.
#
# Why this exists (issue #415): SKILL.md:17 states that every leaf — developer or verifier —
# is launched through the supervisor, and SKILL.md:322 launched the verifier through
# `detach-leaf.sh` alone for months. Nothing gave that verifier a heartbeat or a timeout, so
# when it died before writing `.tdd/verdict-<phase>.exit` the conductor waited on a file
# nothing would ever write — twice on #297, deterministically, with the thread sitting dead
# until a human looked. The launch lines are fixed now, and a fix to prose is exactly the
# kind that comes back: the next incident-driven edit to a launch, or the next author
# spelling one out from the shape above it, puts the bypass back as one plausible line.
#
# The guard is what stops that, and a guard that has never been watched to fail is not
# tested: every verifier launch in the document carries the supervisor today, so case 5
# passes over this tree whether it still checks anything or not. Deleting its `problems+=`
# line, or narrowing the lines it reads, would leave `make test` green and the invariant
# unguarded. So the contradiction is planted instead, and the guard is asked about the
# planted document.
#
# Contract under test:
#   Over a copy of this tree whose one `verdict-red` launch line has had the supervisor and
#   its leaf name cut out of it — the #297 shape, `detach-leaf.sh` straight to the `bash -c`
#   wrapper around `verify.sh` — skill-leaf-launch.test.sh fails, and the line it names is
#   that launch: SKILL.md with the planted line's number, saying `supervise.sh` is what is
#   missing. Over the same tree with the document unplanted it passes.
#
# Both halves are the case, and the green half is not decoration: red over a tree is worth
# nothing unless the same guard is green over the same tree before the plant. A guard broken
# so that it fails on everything would satisfy the red half alone.
#
# Naming the line, rather than merely failing, is the criterion too — and naming ONLY that
# line. A guard that listed every launch line in the document would fail over the plant and
# send the next author to nine addresses, eight of which are correct.
#
# The plant carries the document and the guard and nothing else, because those are the only
# two files the guard resolves against its own repo root. In particular the generated tree
# is not copied, and no line below names a path in it, which is what no-docs-reads.test.sh
# asks of every suite in this directory.
#
# Run: skills/tdd/scripts/tests/verifier-launch-guard.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The guard, twice, and neither name substitutes for the other: repo-relative is what a
# failure message quotes and what the plant rebuilds the path from, absolute is what copying
# it into the plant needs. Same pairing docs-read-guard.test.sh uses on its own guard.
GUARD='skills/tdd/scripts/tests/skill-leaf-launch.test.sh'
GUARD_PATH="$ROOT/$GUARD"

# The document the guard reads, the same way twice and for the same reason — and the
# repo-relative spelling is also the address the guard's own failure lines open with, which
# is what the probes below match on.
SKILL='skills/tdd/SKILL.md'
SKILL_PATH="$ROOT/$SKILL"

# What the plant cuts out of one launch line: the supervisor, with the leaf name it is given.
# A literal, matched and removed as a literal — `$S` is the document's own abbreviation for
# the scripts directory and `.` is a character in a filename, so nothing here becomes a
# regex. Cutting the pair rather than just the script name is what makes the plant the #297
# shape exactly: `detach-leaf.sh` handing the `bash -c` wrapper straight to the verifier.
FRAGMENT='$S/supervise.sh verdict-red '

# The script the planted line no longer names, and the word the guard's complaint about it
# has to carry: a red that never says which script is missing sends nobody anywhere.
MISSING='supervise.sh'

# The other script the planted line still names, asserted present by the plant's own probe:
# the guard recognises a verifier launch BY this name, so a plant that removed it would take
# the line out of the guard's scope instead of making it wrong.
VERIFIER='verify.sh'

pass=0 fail=0
scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which half of the contract broke rather than just that the case did.
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

# flat <text> — one line of it, for a failure message: newlines become slashes so a guard's
# whole output quoted inside an indented problem line stays one line.
flat() { local s="$1"; printf '%s' "${s//$'\n'/\/}"; }

# failures_in <output> — the number a suite's own count line states it failed, or '<none>'
# when it printed no count line at all. A suite's exit code alone is not trusted (#157: a
# suite that dies partway routinely comes back 0), so both probes below read the verdict the
# guard printed as well as the status it exited with — the same pair the `test` recipe reads.
failures_in() {
  local line
  line="$(grep -E '^[0-9]+ passed, [0-9]+ failed$' <<< "$1" | tail -1)"
  [[ -n "$line" ]] || { printf '%s' '<none>'; return; }
  line="${line#*, }"
  printf '%s' "${line% failed}"
}

# plant — build the scratch tree the guard is run inside, and the planted document it is run
# against. Leaves the tree's path in `tree`, the guard's copy in `guard_copy`, the rewritten
# document in `planted_skill` and the line number it rewrote in `planted_line`.
#
# The tree holds only what the guard resolves against its own repo root: itself, and the
# document. The planted document is staged OUTSIDE the tree, because the case runs the guard
# twice over the same tree — unplanted first, then planted — and `run_guard_over` is what
# puts one of the two in place.
#
# The rewrite is one literal deletion on the first line carrying it, done with awk's
# `index`/`substr` rather than sed so that neither `$` nor `.` in the fragment has to be
# escaped into a pattern. The fragment goes in through the environment for the same reason
# skill-leaf-launch.test.sh passes its patterns that way: `awk -v` would process the
# backslash escapes of anything spelled with one.
plant() {
  tree="$scratch/tree"
  mkdir -p "$tree/${SKILL%/*}" "$tree/${GUARD%/*}" || {
    problems+=("could not make a scratch tree to plant the document in, so the criterion went unasked")
    return 1
  }
  guard_copy="$tree/$GUARD"
  cp "$GUARD_PATH" "$guard_copy"

  planted_skill="$scratch/planted-SKILL.md"
  FRAG="$FRAGMENT" awk '
    !cut && (i = index($0, ENVIRON["FRAG"])) > 0 {
      $0 = substr($0, 1, i - 1) substr($0, i + length(ENVIRON["FRAG"]))
      cut = 1
    }
    { print }
  ' "$SKILL_PATH" > "$planted_skill"

  planted_line="$(grep -nF "$FRAGMENT" "$SKILL_PATH" | head -1 | cut -d: -f1)"
  # Not the status of that assignment (#183). A grep that found no launch line to plant on
  # would otherwise make `plant` return non-zero, the case skip every probe, and `report`
  # count an empty `problems` array as a pass — a guard suite saying the one thing it must
  # never be able to say. Whether the plant is what it claims is the next probe's question.
  return 0
}

# probe_guard_is_there — the premise every probe below rests on, and the one that answers
# while the guard does not exist yet: there is a suite at that path and it can be run.
# Returns non-zero so the case stops here rather than reporting on a tree it never built.
probe_guard_is_there() {
  [[ -f "$GUARD_PATH" ]] || {
    problems+=("there is no guard suite at $GUARD, so no launch line in $SKILL is checked for reaching $VERIFIER without $MISSING")
    return 1
  }
  [[ -x "$GUARD_PATH" ]] || {
    problems+=("$GUARD is not executable, so \`make test\`'s runner cannot run it")
    return 1
  }
}

# probe_plant_is_what_it_claims — the plant's premises, asserted rather than assumed. The
# fragment has to be findable, and on exactly one line, or `planted_line` is an address the
# guard was never owed. That line has to have named both scripts before the cut and only the
# verifier after it — a plant that removed the verifier's own name would take the line out of
# the guard's scope rather than make it wrong, and red would then mean nothing. And the two
# documents have to differ on that line and nowhere else, or the guard's red could be about a
# second contradiction this suite did not mean to write.
probe_plant_is_what_it_claims() {
  [[ "$planted_line" =~ ^[0-9]+$ ]] || {
    problems+=("no line of $SKILL carries '$FRAGMENT' (found '$planted_line'), so there is no supervised verifier launch to cut it out of and the criterion cannot be asked")
    return
  }
  local carriers before after changed
  carriers="$(grep -cF "$FRAGMENT" "$SKILL_PATH")"
  [[ "$carriers" == 1 ]] ||
    problems+=("$SKILL carries '$FRAGMENT' on $carriers lines, want exactly 1 — with more than one the plant's address is a guess")
  before="$(sed -n "${planted_line}p" "$SKILL_PATH")"
  after="$(sed -n "${planted_line}p" "$planted_skill")"
  [[ "$before" == *"$VERIFIER"* && "$before" == *"$MISSING"* ]] ||
    problems+=("$SKILL:$planted_line is not a supervised verifier launch to begin with, so cutting the supervisor out of it contradicts nothing: $(flat "$before")")
  [[ "$after" == *"$VERIFIER"* ]] ||
    problems+=("the planted $SKILL:$planted_line no longer reaches $VERIFIER, so the guard has no verifier launch there to judge: $(flat "$after")")
  [[ "$after" != *"$MISSING"* ]] ||
    problems+=("the planted $SKILL:$planted_line still names $MISSING, so nothing was planted: $(flat "$after")")
  changed="$(diff "$SKILL_PATH" "$planted_skill" | grep -c '^[<>]')"
  [[ "$changed" == 2 ]] ||
    problems+=("the plant rewrote $changed lines of $SKILL, want exactly one line rewritten (2 diff lines) — a red over a document changed twice is not about the launch")
}

# run_guard_over <document> — put <document> in the tree as the document the guard reads,
# run the guard there once, and leave what it said in `guard_out` and how it exited in
# `guard_code`. A step of its own because both probes below ask about one such run, and
# because the case makes two of them over the same tree.
run_guard_over() {
  cp "$1" "$tree/$SKILL"
  guard_out="$("$guard_copy" 2>&1)" && guard_code=0 || guard_code=$?
}

# probe_guard_is_green_unplanted — the half that makes the other half mean something. The
# guard is run over the tree with the document exactly as committed: it has to pass, and its
# own count line has to say nothing failed. A guard red over this tree is red over every
# tree, and the plant below would prove nothing about it.
probe_guard_is_green_unplanted() {
  local failures
  run_guard_over "$SKILL_PATH"
  failures="$(failures_in "$guard_out")"
  [[ "$guard_code" == 0 ]] ||
    problems+=("want ${GUARD##*/} to pass over $SKILL as committed — red there says nothing about the plant; it exited $guard_code and said: $(flat "$guard_out")")
  [[ "$failures" == 0 ]] ||
    problems+=("want ${GUARD##*/}'s own count line to state 0 failed over $SKILL as committed; it stated '$failures': $(flat "$guard_out")")
}

# probe_guard_names_the_planted_launch — the criterion. Not "the guard fails" — a guard
# deleted down to `exit 1` would satisfy that, and so would one whose other five cases broke
# on the copy — but a failure that carries the address of the launch the plant made wrong,
# and the name of the script it no longer goes through. Its count line as well as its status,
# for the reason `failures_in` gives.
#
# And only that address. The guard reads nine launch lines in this document and eight of them
# are still correct; a red that named them too would be a list to read rather than a line to
# go and fix.
probe_guard_names_the_planted_launch() {
  local failures named addresses
  run_guard_over "$planted_skill"
  failures="$(failures_in "$guard_out")"
  [[ "$guard_code" != 0 ]] ||
    problems+=("want ${GUARD##*/} to fail over a $SKILL whose $planted_line reaches $VERIFIER without $MISSING; it exited 0 and said: $(flat "$guard_out")")
  [[ "$failures" != 0 && "$failures" != '<none>' ]] ||
    problems+=("want ${GUARD##*/}'s own count line to state a failure over that document; it stated '$failures': $(flat "$guard_out")")
  named="$(grep -F "$SKILL:$planted_line" <<< "$guard_out")"
  if [[ -z "$named" ]]; then
    problems+=("no line of ${GUARD##*/}'s output names $SKILL:$planted_line, the launch the plant cut $MISSING out of; it said: $(flat "$guard_out")")
  else
    grep -qF "$MISSING" <<< "$named" ||
      problems+=("${GUARD##*/} named $SKILL:$planted_line without saying $MISSING is what it no longer goes through; the lines naming it were: $(flat "$named")")
  fi
  addresses="$(grep -oE "${SKILL//./\\.}:[0-9]+" <<< "$guard_out" | sort -u | tr '\n' ' ')"
  [[ "$addresses" == "$SKILL:$planted_line " ]] ||
    problems+=("${GUARD##*/} named the addresses '$addresses' over that document, want only $SKILL:$planted_line — the document's other launch lines are correct and a red naming them is a list rather than a fix")
}

# 1. One criterion — the launch guard is known to go red at the planted launch, and green
#    without it — and so one case: both runs are of the same guard over the same tree, and a
#    case that asked only about the planted one would pass over a guard that refuses
#    everything.
name="${GUARD##*/} fails over a $SKILL whose verifier launch has lost $MISSING, naming that line and nothing else, and passes over the document as committed"
problems=()
tree=""
guard_copy=""
planted_skill=""
planted_line=""
guard_out=""
guard_code=0

if probe_guard_is_there && plant; then
  probe_plant_is_what_it_claims
  probe_guard_is_green_unplanted
  probe_guard_names_the_planted_launch
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
