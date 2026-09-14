#!/usr/bin/env bash
# Unit test for how skills/tdd/SKILL.md launches a leaf. Like skill-identity.test.sh and
# skill-suite-runs.test.sh this suite belongs to no single script: its subject is the
# procedure, read as text, the way the session that follows it reads it. Zero-dependency
# plain-shell asserts, same idiom, picked up by `make test`'s glob by existing.
#
# Why this exists (issue #161): `nohup … &` is not a detach. It makes the child ignore
# SIGHUP and leaves it in the PROCESS GROUP of the Bash call that launched it, so a harness
# that signals that group when the call ends takes the leaf with it. Observed 2026-09-12
# 23:43 UTC on a conductor for #123: the call came back `Exit code 144`, the verifier's
# `.tdd/verdict-red.exit` was never written, and `verify.sh red` was gone. A leaf killed
# that way writes no completion file, so `wait-leaf.sh` returns exit 3 forever and
# SKILL.md:88-89 tells the conductor that means "still running" — the run stalls with
# nothing to say why. `detach-leaf.sh` is the fix, and it fixes nothing while the document
# ten call sites are spelled in still says `nohup`.
#
# Contract under test — the launches, then the reason a conductor is given for them:
#   1. Every developer and verifier leaf launch line in SKILL.md goes through
#      `detach-leaf.sh`, and none of them uses `nohup`.
#   2. *Launching a leaf* — the section those launches live in — says why `nohup` alone is
#      not enough: it survives a hang-up, but not a signal to the launching call's process
#      group.
#
# Case 1 is scoped to the launch LINES, not to the file, precisely so case 2 can exist:
# *Launching a leaf* has to be free to explain why `nohup` is not enough, and a suite that
# banned the word from the document would ban the explanation with it.
#
# Run: scripts/tests/skill-leaf-launch.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The document twice: the path as every failure message spells it, and the same path
# resolved for the probes to read, so a message can never name a file the probes did not
# open.
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

# The script a launch line has to name, written down once so the probe and the message it
# fails with cannot drift apart. `detacher` rather than `launcher`, because in the document's
# own vocabulary the leaf **launcher** is `supervise.sh` (SKILL.md:67) — one of the two
# scripts a launch line is recognised BY below — and `detach-leaf.sh` is "the detaching half
# of a detached launch" (SKILL.md:84). wait-leaf.test.sh case 4 names it the same way.
detacher="detach-leaf.sh"

# The section case 2 reads, written down once for the same reason: it is both an argument to
# the probe — `section_prose` matches on it as a heading prefix — and a name three failure
# messages spell. Renaming the heading in the document has to break the probe, not quietly
# leave the messages pointing at a section that is no longer called that.
section="Launching a leaf"

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output names the launch lines that are wrong rather than just saying the case is.
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

# fault <description> — record one thing wrong with the passage being read, onto the
# `faults` string the caller opens empty before reading it. Joined rather than collected
# because a line that both misses the detacher and still says `nohup` is one wrong launch,
# and reads better as one problem naming both than as two problems naming the same line.
fault() {
  faults="${faults:+$faults, and }$1"
}

# launch_lines — the leaf launch lines of SKILL.md, each prefixed with its line number.
#
# A launch line is a line INSIDE a fenced block that names `supervise.sh` or `verify.sh`:
# the fence is what tells a command the conductor runs from prose about it, and those two
# scripts are what a leaf is launched as — a developer leaf through the supervisor, a
# verifier through the `bash -c` wrapper that records the verdict. `wait-leaf.sh` and
# `build-develop-prompt.sh` share those fences and launch nothing, so they are not matched;
# the script inventory's `$S/supervise.sh <name> <cmd> [args...]` and *Bailing*'s
# `verify.sh exited 2` are prose, so they are not either. The fence regex allows leading
# space because a phase's block is indented into its numbered step.
launch_lines() {
  awk '
    /^[[:space:]]*```/ { fence = !fence; next }
    fence && /supervise\.sh|verify\.sh/ { printf "%d\t%s\n", NR, $0 }
  ' "$skill_path"
}

# section_prose <heading-prefix> — the prose of the `## ` section whose heading starts with
# <heading-prefix>, with every fenced block dropped. From that heading to the next `## `,
# so the section's own extent is read off the document rather than pinned to line numbers
# that move. Prints nothing at all when no heading matches, which is what lets the caller
# tell "the section does not explain it" from "the section is gone".
section_prose() {
  awk -v want="$1" '
    /^## / { insec = (index($0, "## " want) == 1) }
    !insec { next }
    /^[[:space:]]*```/ { fence = !fence; next }
    !fence
  ' "$skill_path"
}

# 1. One criterion — every leaf launch detaches into a session of its own — and so one
#    case. Both halves are about the same line: naming the detacher is what makes the
#    launch survive, and a leftover `nohup` in front of it is the shape the incident
#    happened in, still being copied by a conductor reading the document.
name="$skill_md launches every developer and verifier leaf through $detacher, and no launch line uses nohup"
problems=()

launches="$(launch_lines)"
if [[ -z "$launches" ]]; then
  # Fail closed: no launch line found means the fences moved or the document lost its
  # launches, and either has to read as one problem saying so — never as a case that
  # passed because there was nothing left to contradict it.
  problems+=("$skill_md has no leaf launch line inside a fenced block — how a leaf is launched could not be read")
else
  while IFS=$'\t' read -r lineno text; do
    faults=""
    [[ "$text" == *"$detacher"* ]] || fault "does not go through $detacher"
    [[ "$text" == *nohup* ]] && fault "still uses nohup"
    [[ -z "$faults" ]] ||
      problems+=("$skill_md:$lineno $faults: $text")
  done <<< "$launches"
fi

report "$name"

# 2. The same section, read as prose rather than as commands: a conductor that finds only
#    `detach-leaf.sh` in the launch shape has been told WHAT to type and not why, and the
#    next incident-driven edit to this document — or the next session improvising a launch
#    the procedure does not spell out — puts `nohup` back. The reason is two halves and
#    the case wants both: `nohup` DOES survive one thing (a hang-up, SIGHUP) and does NOT
#    survive the other (a signal to the process group of the call that launched it). Half
#    the reason is what made `nohup` look sufficient in the first place.
#
#    Read case-insensitively and with the fenced blocks dropped, because the subject is
#    the explanation, not its capitalisation, and a command inside a fence explains
#    nothing. The section runs from its own `##` heading to the next one.
name="$skill_md's *$section* says why nohup alone is not enough"
problems=()

prose="$(section_prose "$section" | tr '[:upper:]' '[:lower:]')"
if [[ -z "$prose" ]]; then
  # Fail closed, as case 1 does: a section that could not be read is never an explanation
  # that passed.
  problems+=("$skill_md has no *$section* section — the reason given for the launch shape could not be read")
else
  faults=""
  [[ "$prose" == *nohup* ]] || fault "never names nohup"
  [[ "$prose" == *sighup* || "$prose" == *hang-up* || "$prose" == *hangup* ]] ||
    fault "does not say nohup survives a hang-up"
  [[ "$prose" == *"process group"* ]] ||
    fault "does not say nohup leaves the leaf in the launching call's process group"
  [[ -z "$faults" ]] ||
    problems+=("$skill_md *$section* $faults")
fi

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
