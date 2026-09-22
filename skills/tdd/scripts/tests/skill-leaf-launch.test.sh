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
#   3. Every launch that clears a leaf's completion file `.tdd/<name>.exit` clears its pid
#      file `.tdd/<name>.pid` on the same line (issue #173), so a pid file left by an
#      earlier leaf of the same name cannot end a later wait early.
#   4. The script inventory's `wait-leaf.sh` entry says a 2 also means the supervisor died
#      without recording a status, and that it takes the killed-stuck branch (issue #173).
#   5. Every launch line that names `verify.sh` names `supervise.sh` too, so a verifier is
#      launched through the supervisor the way a developer leaf is (issue #415) — the
#      invariant SKILL.md:17 states and line 322 broke.
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

# The other two scripts a launch line names, written down once for the same reason: the leaf
# **launcher** (SKILL.md:67), which case 5 requires every launch to go through, and the verify
# script, which is what makes a launch line a verifier's. Both are spelled into that case's
# failure messages as well as probed with — and into `launch_lines`, which recognises a launch
# line BY them — so a rename cannot leave a message, or a probe, naming a script the others no
# longer look for.
launcher="supervise.sh"
verifier="verify.sh"

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

# unreadable <missing> <subject> — record the problem a probe that printed NOTHING leaves
# behind, onto the same `problems` array a fault ends up in. Both cases fail closed through
# here: a probe comes back empty when the fences moved, when the launches went, or when the
# heading was renamed, and every one of those has to read as a problem saying the document
# could not be read — never as a case that passed because there was nothing left to
# contradict it. One helper so neither case can quietly stop doing it, and so the two
# messages cannot drift into different shapes.
unreadable() {
  problems+=("$skill_md has no $1 — $2 could not be read")
}

# fenced_lines <ERE> — the lines of SKILL.md INSIDE a fenced block that match <ERE>, each
# prefixed with its line number. The fence is what tells a command the conductor runs from
# prose about it, so every probe of the commands reads through here. The fence regex allows
# leading space because a phase's block is indented into its numbered step. The pattern
# goes in through the environment, not `awk -v`, because `-v` would process its backslash
# escapes and a `\.` would reach awk as a bare `.`.
fenced_lines() {
  PAT="$1" awk '
    /^[[:space:]]*```/ { fence = !fence; next }
    fence && $0 ~ ENVIRON["PAT"] { printf "%d\t%s\n", NR, $0 }
  ' "$skill_path"
}

# launch_lines — the leaf launch lines of SKILL.md, each prefixed with its line number.
#
# A launch line is a fenced line that names `$launcher` or `$verifier`: those two scripts are
# what a leaf is launched as — a developer leaf through the supervisor, a verifier through the
# `bash -c` wrapper that records the verdict. `wait-leaf.sh` and `build-develop-prompt.sh`
# share those fences and launch nothing, so they are not matched; the script inventory's
# `$S/supervise.sh <name> <cmd> [args...]` and *Bailing*'s `verify.sh exited 2` are prose, so
# they are not either.
#
# The alternation is built from those two variables rather than spelling the names a second
# time here: `${launcher//./\\.}` is a pattern substitution — every `.` in the name replaced
# by `\.` — which turns the literal script name into the ERE `fenced_lines` wants, where a
# bare `.` would match any character. Same escaping `arg_after` does in skill-leaf-env.test.sh,
# and for the same reason: a script name is text, and only this line knows it is about to
# become a regex.
launch_lines() {
  fenced_lines "${launcher//./\\.}|${verifier//./\\.}"
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
  unreadable "leaf launch line inside a fenced block" "how a leaf is launched"
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
  unreadable "*$section* section" "the reason given for the launch shape"
else
  faults=""
  [[ "$prose" == *nohup* ]] || fault "never names nohup"
  # One question, so one pattern: the three spellings a writer might reach for are the
  # signal's name and the English word with or without its hyphen, and asking them as an
  # alternation says that rather than making a reader diff three near-identical clauses to
  # find it. `=~` for the same reason the sibling suites use it — skill-identity.test.sh's
  # `claim` and skill-suite-runs.test.sh's `says` both pin "any wording that carries the
  # fact" as one regex.
  [[ "$prose" =~ (sighup|hang-?up) ]] ||
    fault "does not say nohup survives a hang-up"
  [[ "$prose" == *"process group"* ]] ||
    fault "does not say nohup leaves the leaf in the launching call's process group"
  [[ -z "$faults" ]] ||
    problems+=("$skill_md *$section* $faults")
fi

report "$name"

# clear_lines — the lines inside a fenced block that clear a completion file, each prefixed
# with its line number: every `rm -f` naming a `.tdd/<name>.exit`. Those are the first of a
# launch's three parts, and the only place the procedure resets a leaf's state before it.
clear_lines() {
  fenced_lines 'rm -f .*\.tdd/[^ ]*\.exit'
}

# 3. A pid file left by an earlier leaf of the same name cannot end a later wait early
#    (issue #173). Names are reused on every step, and `wait-leaf.sh` exits 2 when the pid
#    `.tdd/<name>.pid` records is no longer a supervisor — so the previous step's pid file,
#    naming a supervisor long gone, would end the next wait before the new supervisor has
#    written its own. The launch has to clear it together with `.tdd/<name>.exit`: the same
#    `rm -f` line, for the same name, so the two can never be reset apart.
name="$skill_md clears .tdd/<name>.pid together with .tdd/<name>.exit on every launch"
problems=()

clears="$(clear_lines)"
if [[ -z "$clears" ]]; then
  unreadable "line clearing a completion file inside a fenced block" "how a launch resets a leaf"
else
  while IFS=$'\t' read -r lineno text; do
    exitfile="$(printf '%s\n' "$text" | grep -o '\.tdd/[^ ]*\.exit' | head -n 1)"
    pidfile="${exitfile%.exit}.pid"
    [[ "$text" == *"$pidfile"* ]] ||
      problems+=("$skill_md:$lineno clears $exitfile but not $pidfile: $text")
  done <<< "$clears"
fi

report "$name"

# inventory_entry <script> — the script inventory's bullet for <script>, as one line: from
# the `- `$S/<script>` bullet up to the next bullet, heading or blank line. Prints nothing
# when no bullet names <script>, so the caller can fail closed. Case is the caller's to fold,
# as it is for `section_prose`.
inventory_entry() {
  awk -v want="- \`\$S/$1" '
    index($0, want) == 1 { inentry = 1; print; next }
    inentry && (/^- / || /^#/ || /^[[:space:]]*$/) { inentry = 0 }
    inentry
  ' "$skill_path" | tr '\n' ' '
}

# 4. A 2 from `wait-leaf.sh` also means the supervisor died without recording a status
#    (issue #173), and it takes the killed-stuck branch like any other 2. The script's
#    inventory entry is where a conductor learns what each of its codes means; an entry
#    that still reads 2 only as "the launcher's own contract" leaves a dead supervisor to
#    be read as a leaf that answered.
waiter="wait-leaf.sh"
name="$skill_md's $waiter entry says a 2 also means the supervisor died without recording a status, and takes the killed-stuck branch"
problems=()

entry="$(inventory_entry "$waiter" | tr '[:upper:]' '[:lower:]')"
if [[ -z "$entry" ]]; then
  unreadable "script inventory entry for $waiter" "what its exit codes mean"
else
  faults=""
  [[ "$entry" =~ supervisor[^.]*(died|dead|gone)[^.]*(without|never|no)[^.]*(record|status|completion) ]] ||
    fault "does not say a 2 means the supervisor died without recording a status"
  [[ "$entry" == *killed-stuck* ]] ||
    fault "does not say that 2 takes the killed-stuck branch"
  [[ -z "$faults" ]] ||
    problems+=("$skill_md $waiter entry $faults")
fi

report "$name"

# 5. A verifier is a leaf, and SKILL.md:17 says every leaf goes through the supervisor — so
#    a launch line that reaches `verify.sh` without naming `supervise.sh` contradicts the
#    document's own invariant, and the contradiction is what stalled #297 (issue #415).
#    Nothing gave that verifier a heartbeat or a timeout, so when it died before writing
#    `.tdd/verdict-<phase>.exit` the conductor waited on a file nothing would ever write.
#    Read off the same launch lines case 1 reads, narrowed to the ones that name the verify
#    script: the criterion is about how a VERIFIER is launched, and a developer launch line
#    naming only the supervisor is case 1's business, not this one's.
name="$skill_md launches every verifier through $launcher, the way it launches a developer leaf"
problems=()

verifier_launches="$(launch_lines | grep -F "$verifier" || true)"
if [[ -z "$verifier_launches" ]]; then
  unreadable "launch line naming $verifier inside a fenced block" "how a verifier is launched"
else
  while IFS=$'\t' read -r lineno text; do
    [[ "$text" == *"$launcher"* ]] ||
      problems+=("$skill_md:$lineno reaches $verifier without $launcher: $text")
  done <<< "$verifier_launches"
fi

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
