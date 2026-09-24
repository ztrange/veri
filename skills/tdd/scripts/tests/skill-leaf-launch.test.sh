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
#   5. Every launch line that reaches the verifier — by naming `verify.sh` or the verdict
#      launcher `run-verdict.sh` that execs it — names `supervise.sh` too, so a verifier is
#      launched through the supervisor the way a developer leaf is (issue #415) — the
#      invariant SKILL.md:17 states and line 322 broke.
#   6. Every supervised verifier launch passes the blind parameter list and nothing else —
#      the phase, the spec file, the test path and the test id, or the base sha for
#      `refactor`, behind verify.sh's own `--step` and `--fast-cmd` flags — so nothing the
#      supervisor put in front of that call can carry the developer's rationale to a
#      verifier that is blind by construction (issue #415). Read at the verdict launcher,
#      which since #426 is where that list is typed: it passes its argv to `verify.sh`
#      untouched, so an argument added to the launch is an argument the verifier gets.
#   7. Every verifier launch invokes the verdict launcher `run-verdict.sh` and inlines no
#      `bash -c` command string, so the step's own title reaches the verifier as one argv
#      element rather than as shell text a second shell has to parse (issue #426).
#   8. The document states in ONE place how the step's title reaches a command line — in
#      double quotes, because the title is the planning leaf's own English and an
#      apostrophe in it closes a single-quoted one early — and every fenced command
#      carrying `<STEP>` follows that rule (issue #431).
#   9. Every documented command line that passes a FRAGMENT of the step's title follows that
#      same rule — the `tick-ledger.sh`, `clear-refactor-pending.sh` and
#      `tick-issue-criterion.sh` calls handed a distinctive substring of STEP to find the
#      checkbox they tick — read over the whole document, prose included, since three of
#      those calls are written inline in a sentence rather than in a fenced block (#431).
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
# script, which a launch may still reach a verifier by. Both are spelled into that case's
# failure messages as well as probed with — and into `launch_lines`, which recognises a launch
# line BY them — so a rename cannot leave a message, or a probe, naming a script the others no
# longer look for.
launcher="supervise.sh"
verifier="verify.sh"

# The script case 7 requires every verifier launch to invoke, and the leaf name that case
# recognises one BY. Both written down once, for the reason the three above are: the leaf
# name is what a failure message quotes as well as what the probe narrows on, and the
# launcher's name is spelled into the message that says a line does not invoke it.
#
# `verdict-` rather than `verify.sh` is what a verifier launch is recognised by here,
# because the criterion is precisely that `verify.sh` stops being the name on that line:
# narrowing on it would make a fixed launch invisible to the case that asked for the fix.
# For the same reason the launcher's name joins `launch_lines`' alternation and is what
# cases 5 and 6 narrow on: once a launch reaches the verifier through it, a probe still
# looking only for `verify.sh` reads a fixed document as one with no verifier launch at all.
verdict_launcher="run-verdict.sh"
verdict_leaf="verdict-"

# The section case 2 reads, written down once for the same reason: it is both an argument to
# the probe — `section_prose` matches on it as a heading prefix — and a name three failure
# messages spell. Renaming the heading in the document has to break the probe, not quietly
# leave the messages pointing at a section that is no longer called that.
section="Launching a leaf"

# The placeholder every command spells the step's title as, and the two shapes case 8 tells
# apart: `$double_quoted_step`, the rule SKILL.md states, and `$single_quoted_step`, the shape
# the incident happened in. Written down once for the reason the script names above are: the
# placeholder is what four probes narrow on AND what their failure messages quote, and the
# two quoted shapes are built from it here rather than retyped, so a document that renames
# the placeholder cannot leave one probe reading a shape no other looks for.
step_ph="<STEP>"
double_quoted_step="\"$step_ph\""
single_quoted_step="'$step_ph'"

# The spec file a verifier launch names, as one ERE alternation: the concrete path the
# conductor's own launches spell and the `<spec-file>` placeholder the shapes they are copied
# from use. Written down once for the same reason the placeholders above are — case 6 narrows
# the launch lines on it and then judges their whole argument list against it, so a document
# that renames the placeholder must fail the case rather than quietly leave the two probes
# looking for different files.
spec_re="(\.tdd/issue-<n>-spec\.md|<spec-file>)"

# The same three shapes for a FRAGMENT of the title — the substring `tick-ledger.sh`,
# `clear-refactor-pending.sh` and `tick-issue-criterion.sh` are handed to find the step they
# act on. A fragment of the planning leaf's English is the planning leaf's English, so it
# carries an apostrophe exactly as readily as the whole title does and is bound by the same
# rule; the document spells it several ways — `<substring>`, `<distinctive substring of
# STEP>`, `<anchor substring>` — so the placeholder is an ERE matching any of them rather
# than the one literal `$step_ph` is, and `[^<>]` is what keeps a match inside one
# placeholder rather than letting it span from one to the next. ERE is the one dialect both
# readers speak: `grep -E` selects the lines and `read_quoted_lines` reads them with `=~` and
# `sed -E`, never with a glob — `[^<>]*` means "one non-bracket character, then anything at
# all" to `[[ … == … ]]`, which is not this pattern and does not match `'<substring>'` or
# `'<anchor substring>'`. Written down here beside the whole title's three shapes, for the
# reason those are: the probe narrows on them and its failure messages quote them, and a
# document that renames the placeholder must not leave one reading a shape no other looks
# for.
fragment_ph="<[^<>]*substring[^<>]*>"
double_quoted_fragment="\"$fragment_ph\""
single_quoted_fragment="'$fragment_ph'"

# EXEMPT[<file>:<line>]="<reason>" — a documented line allowed to carry the step's title in
# the broken shape, each with the sentence that says why that line has to keep it. The reason
# is what makes an entry an exemption; a bare key is a line someone once wanted quiet, and the
# next reader cannot tell the two apart, so an entry with no reason excuses nothing and the
# line is reported as it would have been. The key is the repository-relative path and the
# line, because that is the address the report itself quotes — an exemption answers a report,
# so it is written in the same words. Empty today, and the declaration stays so that a line
# that must keep the shape can be answered by name rather than by deleting the check. Same
# reader no-job-spec-kills.test.sh and no-sigpipe-pipelines.test.sh keep their tables behind.
declare -A EXEMPT=(
)

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

# faulted <lineno> <text> — close one document line's reading, on the `faults` string the
# caller opened empty before it: nothing wrong is nothing recorded, and otherwise one
# problem naming the line, what is wrong with it and the line itself. Cases 1 and 7 end a
# launch line through here directly and cases 8 and 9 through the reader below, so the shape
# lives here rather than being retyped at each of them, where one could stop quoting the
# offending line while the others went on doing it.
faulted() {
  [[ -z "$faults" ]] ||
    problems+=("$skill_md:$1 $faults: $2")
}

# read_quoted_lines <lines> <noun> <ph> <single> <double> — hold every numbered document line
# in <lines> to the step-title rule, where <noun> names what the line carries, <ph> is the
# placeholder it spells it as and <single>/<double> are that placeholder's two quoted shapes.
# One fault per line, and the single-quoted shape names itself: it is the one the incident
# happened in, and a line carrying it is not also worth being told that what it carries is
# therefore not double-quoted. The second reading is what catches the other ways the text can
# reach a command line bare — unquoted, or quoted with something else. Every occurrence, not
# just the first: a launch spells the title twice — once into the environment and once as the
# verdict launcher's `--step` — so the double-quoted ones are struck out and what is left is
# asked whether it still carries it bare.
#
# Cases 8 and 9 are the same reading over two texts — the whole title, and a fragment of it —
# because it is one rule and the fragment fails it one argument over. So the reading lives
# here rather than being retyped at each, where one could go on being tightened while the
# other read the document the old way and called it a pass. The three patterns go in as EREs,
# and are read as EREs — `=~` for the first reading, `sed -E` for the strike-out the second
# needs — because the fragment's placeholder is a character class matching the several ways
# the document spells it, and a class means something else to a glob. The whole title's
# placeholder is its own literal and reads the same either way, so ERE for both is the choice
# that lets one reading serve two texts without one of them being read wrong.
read_quoted_lines() {
  local lines="$1" noun="$2" ph="$3" single="$4" double="$5"
  local lineno text
  while IFS=$'\t' read -r lineno text; do
    # The table first, so an exempted line is never read: a report an entry has answered by
    # name is a report the author already acted on.
    [[ -n "${EXEMPT[$skill_md:$lineno]:-}" ]] && continue
    faults=""
    if [[ "$text" =~ $single ]]; then
      fault "single-quotes $noun"
    elif [[ "$(sed -E "s|$double||g" <<< "$text")" =~ $ph ]]; then
      fault "carries $noun outside double quotes"
    fi
    faulted "$lineno" "$text"
  done <<< "$lines"
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

# lowered — stdin, case-folded. Three cases read a passage of the document for what it says
# rather than for how it is capitalised — the launch section's prose, `wait-leaf.sh`'s
# inventory entry, the step-title rule's paragraph — and each of them folded the case with
# its own `tr`. One name for it, so the folding a probe is written against is the folding it
# gets.
lowered() {
  tr '[:upper:]' '[:lower:]'
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

# name_re <script>... — the script names as one ERE alternation, ready to match the literal
# names inside SKILL.md.
#
# Every `.` in a name is replaced by `\.` — `${n//./\\.}` is a pattern substitution — because
# a script name is text and a bare `.` in an ERE matches any character. Same escaping
# `arg_after` does in skill-leaf-env.test.sh. It is a function rather than the idiom written
# out at each probe because the probes narrow on different subsets of the same three names,
# and an escape spelled once per subset is an escape that can be got wrong in one of them
# while the others go on passing.
name_re() {
  local out="" n
  for n in "$@"; do out+="|${n//./\\.}"; done
  printf '%s' "${out#|}"
}

# launch_lines — the leaf launch lines of SKILL.md, each prefixed with its line number.
#
# A launch line is a fenced line that names `$launcher`, `$verifier` or `$verdict_launcher`:
# those three scripts are what a leaf is launched as — a developer leaf through the
# supervisor, a verifier through the verdict launcher that execs the verify verb.
# `wait-leaf.sh` and `build-develop-prompt.sh` share those fences and launch nothing, so they
# are not matched; the script inventory's `$S/supervise.sh <name> <cmd> [args...]` and
# *Bailing*'s `verify.sh exited 2` are prose, so they are not either.
launch_lines() {
  fenced_lines "$(name_re "$launcher" "$verifier" "$verdict_launcher")"
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
    faulted "$lineno" "$text"
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

prose="$(section_prose "$section" | lowered)"
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
    exitfile="$(head -n 1 < <(grep -o '\.tdd/[^ ]*\.exit' <<< "$text"))"
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

entry="$(inventory_entry "$waiter" | lowered)"
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

verifier_launches="$(launch_lines | grep -E -- "$(name_re "$verifier" "$verdict_launcher")" || true)"
if [[ -z "$verifier_launches" ]]; then
  unreadable "launch line naming $verifier or $verdict_launcher inside a fenced block" "how a verifier is launched"
else
  while IFS=$'\t' read -r lineno text; do
    [[ "$text" == *"$launcher"* ]] ||
      problems+=("$skill_md:$lineno reaches $verifier without $launcher: $text")
  done <<< "$verifier_launches"
fi

report "$name"

# blind_args <launch-line> — what one supervised verifier launch passes `verify.sh`: the
# text between the script's own name and the redirect that captures its verdict. That
# redirect ends the argument list — everything after it is the wrapper's business, not the
# verifier's — so a line whose redirect is missing yields the rest of itself and fails the
# case below, which is the fail-closed answer for a launch whose parameters cannot be read.
blind_args() {
  local tail="${1#*"$verdict_launcher" }"
  printf '%s' "${tail%% > .tdd/verify-*}"
}

# The whole argument list a supervised verifier launch is allowed to pass, as one anchored
# pattern: verify.sh's own two flags — the step the verdict is scoped to (#223) and, for a
# call that can judge green, the fast tier's command (#341) — then the phase, the spec file,
# the test path, and the target, which is the test id in every phase but `refactor`, where it
# is the step's green commit. Anchored at BOTH ends because the criterion is *only these*:
# an unanchored pattern would pass a line that carries all of them and something else after.
# The `plan` phase (#439) is the second alternative and is spelled out in full rather than
# folded into the first: it carries no `--step` (the plan is verified before the first step,
# so there is no step to scope a verdict to), its third positional is the proposed ledger
# where a cycle phase names a test path, and it takes no target. Written as its own anchored
# alternative, an argument added to either shape still fails this case.
blind_re="^(--step $double_quoted_step( --fast-cmd '<fast-cmd>')? (red|green|refactor|pin|<phase>) $spec_re <test-path> (<target-test-id>|<green-sha>|<base-sha>|\[target\])|plan $spec_re \.tdd/issue-<n>\.md)$"

# 6. The verifier is blind **by construction**: `build-verify-prompt.sh` has no parameter for
#    the developer's rationale, so it cannot leak one, and a launch that passes verify.sh
#    only the phase, the spec file, the test path and the test id — or the base sha, for
#    refactor — keeps that guarantee end to end. Routing the launch through the supervisor
#    (case 5) put a leaf name, a `bash -c` and a quoted wrapper in front of that call, and
#    none of it may reach the verifier (issue #415). Read off the same launch lines case 5
#    reads: their argument list whole, not a prefix of it, so an argument ADDED to one fails
#    here rather than being judged on whether it looks harmless.
name="$skill_md passes $verifier only the blind parameters on every supervised verifier launch"
problems=()

# A supervised verifier launch is a launch line naming both scripts AND the spec file — the
# mark skill-verify-step.test.sh uses to tell a call a conductor copies as it stands from the
# shape it is copied FROM. *Launching a leaf*'s template (SKILL.md:322) names both scripts and
# abbreviates the parameters as `<phase> …`, so it is a launch shape, not a launch: its
# ellipsis is what the concrete launches below fill in, and reading it as a call would fail
# this case on the document's own way of introducing it.
supervised_launches="$(launch_lines | grep -F "$verdict_launcher" | grep -F "$launcher" |
  grep -E "$spec_re" || true)"
if [[ -z "$supervised_launches" ]]; then
  unreadable "launch line naming $verdict_launcher, $launcher and a spec file inside a fenced block" "what a supervised verifier launch passes"
else
  while IFS=$'\t' read -r lineno text; do
    args="$(blind_args "$text")"
    [[ "$args" =~ $blind_re ]] ||
      problems+=("$skill_md:$lineno passes $verifier more than the blind parameters: $args")
  done <<< "$supervised_launches"
fi

report "$name"

# 7. The step's title is the conductor's own English, written by the planning leaf, and the
#    launch above wrapped `verify.sh` in a `bash -c "…"` that inlined it into a `'<STEP>'`
#    inside a `"…"`. A title carrying an apostrophe — `that shell's stderr` — closed that
#    quote early and the launch died with `bash: -c: unexpected EOF while looking for
#    matching `\''` (issue #426), observed on the #424 run. Passing the call through
#    `run-verdict.sh` instead puts the title in argv, where no second shell parses it.
#
#    Both halves are one launch: naming the launcher is what makes the title an argument,
#    and a `bash -c` left in front of it is the shape the incident happened in, still there
#    for a conductor to copy. Read off the launch lines narrowed by the leaf name every
#    verifier launch is given, so the shape at *Launching a leaf* is judged with the five
#    concrete launches that fill it in.
name="$skill_md invokes $verdict_launcher on every verifier launch, with no inlined bash -c command string"
problems=()

verdict_launches="$(launch_lines | grep -F "$launcher $verdict_leaf" || true)"
if [[ -z "$verdict_launches" ]]; then
  unreadable "launch line naming $launcher and a ${verdict_leaf}<phase> leaf inside a fenced block" "how a verdict is launched"
else
  while IFS=$'\t' read -r lineno text; do
    faults=""
    [[ "$text" == *"$verdict_launcher"* ]] || fault "does not invoke $verdict_launcher"
    [[ "$text" == *"bash -c"* ]] && fault "still inlines the verifier call in a bash -c command string"
    faulted "$lineno" "$text"
  done <<< "$verdict_launches"
fi

report "$name"

# prose_paragraphs — every blank-line-separated paragraph of SKILL.md that is OUTSIDE a
# fenced block, one per output line with its internal newlines folded to spaces, prefixed
# with the line the paragraph starts on. The document's commands are read by
# `fenced_lines`; this is the other half — what a conductor is TOLD, as opposed to what it
# types — and it is a paragraph rather than a line because a rule stated over three wrapped
# lines is one statement, and counting the places a rule is stated is what case 8 does.
#
# `section_prose` above reads one section and drops its line numbers; this reads the whole
# document and keeps them, because case 8's question is *where else* the rule is stated, and
# an answer that cannot name the other place is not one a writer can act on.
prose_paragraphs() {
  awk '
    /^[[:space:]]*```/ { flush(); fence = !fence; next }
    fence { next }
    /^[[:space:]]*$/ { flush(); next }
    { if (para == "") start = NR; para = para (para == "" ? "" : " ") $0 }
    END { flush() }
    function flush() { if (para != "") printf "%d\t%s\n", start, para; para = "" }
  ' "$skill_path"
}

# step_lines — the fenced lines that carry the step's title, each prefixed with its line
# number: every command the document hands a conductor with `<STEP>` in it. Not narrowed to
# the leaf launches, because the title reaches a command line on more than those — the
# prompt builder, `event.sh`, `add-ledger-step.sh`, `preserve-attempt.sh` — and one rule for
# all of them is what the criterion asks for.
step_lines() {
  fenced_lines "$step_ph"
}

# 8. The step's title is the planning leaf's own English, and the document's every command
#    still spells it `'<STEP>'` — a single-quoted literal in the shell the conductor types
#    the line into. A title carrying an apostrophe closes that quote early and the line dies
#    before anything is launched (issue #431):
#
#        bash: -c: line 1: unexpected EOF while looking for matching `''
#
#    #426 fixed the INNER half of this — the `bash -c "…"` a verifier call was nested in, so
#    that no second shell parses the title — and left the outer one, which is on every
#    command here and not only the verifier's. The rule is the one the develop-red launch
#    already follows since this issue's first step: the title is carried in DOUBLE quotes,
#    where an apostrophe is an ordinary character.
#
#    Two halves, one criterion, because a rule the commands do not follow is not a rule and
#    a command shape with no rule behind it is the next edit's to get wrong:
#
#      - the rule is stated, and stated ONCE. A paragraph that says how the title is quoted
#        is what a conductor improvising a command it does not find here reads; two of them
#        are two rules the moment one is edited. The reason is required with it for the
#        reason case 2 requires nohup's: a rule whose cost is invisible is a rule the next
#        incident-driven edit undoes.
#      - every fenced command carrying the title follows it: `"<STEP>"` everywhere, and
#        `'<STEP>'` nowhere.
#
#    Both halves are read where case 1 reads its launches — the fenced blocks, and the prose
#    with the fences dropped — and for the same reason case 1 gives: *Launching a leaf* has
#    to stay free to quote the broken shape `'<STEP>'` while explaining it, and a case that
#    banned that text from the document would ban its own explanation with it.
name="$skill_md states the step-title rule in one place, and every fenced command carrying the title follows it"
problems=()

# The rule's paragraph, recognised by what it is about rather than by its wording: it names
# the step title — as the English words, or as the placeholder every command spells — and it
# says something about quoting. Anything that does both is a statement of this rule, which is
# what makes "in one place" answerable at all.
rules="$(prose_paragraphs | grep -i -E 'quot' | grep -F -e 'step title' -e "$step_ph" || true)"
rule_count="$(grep -c . <<< "$rules")"
if [[ "$rule_count" -eq 0 ]]; then
  problems+=("$skill_md states no rule for how a step title reaches a command line — no paragraph outside a fenced block says how the title is quoted")
elif [[ "$rule_count" -gt 1 ]]; then
  problems+=("$skill_md states the step-title rule in $rule_count places, at lines $(cut -f1 <<< "$rules" | paste -sd, -) — one rule, or the next edit moves one of them")
else
  ruleno="$(cut -f1 <<< "$rules")"
  ruletext="$(cut -f2- <<< "$rules")"
  ruletext_lc="$(lowered <<< "$ruletext")"
  faults=""
  [[ "$ruletext" == *"$double_quoted_step"* || "$ruletext_lc" == *"double quote"* ]] ||
    fault "does not say the title is carried in double quotes"
  [[ "$ruletext_lc" == *apostrophe* ]] ||
    fault "does not say why: a title carrying an apostrophe closes a single-quoted one early"
  [[ -z "$faults" ]] ||
    problems+=("$skill_md:$ruleno states the step-title rule but $faults")
fi

steps="$(step_lines)"
if [[ -z "$steps" ]]; then
  unreadable "line carrying $step_ph inside a fenced block" "how the step's title reaches a command line"
else
  read_quoted_lines "$steps" "the step title" \
    "$step_ph" "$single_quoted_step" "$double_quoted_step"
fi

report "$name"

# document_lines <ERE> — every line of SKILL.md matching <ERE>, prefixed with its line
# number, fenced or not. `fenced_lines` above reads only the commands set off in a block,
# which is the right scope for a launch; this is the wider one, because a command the
# document hands a conductor is as often written inline in a sentence — the script inventory
# is entirely inline code, and the `tick-issue-criterion.sh` call at the end of Green is a
# command wrapped across two prose lines. A conductor types what it reads either way.
document_lines() {
  PAT="$1" awk '$0 ~ ENVIRON["PAT"] { printf "%d\t%s\n", NR, $0 }' "$skill_path"
}

# fragment_lines — every documented command line that passes a FRAGMENT of the step's title,
# each prefixed with its line number, in whichever way it is quoted, so that the case below
# reads the lines that carry one rather than only the lines that carry one wrongly — a probe
# narrowed to the broken shape would go quiet the moment the document had none left, and a
# case with nothing to read is a case that cannot fail.
#
# A line carries a fragment if it holds the placeholder; it is a *command* line if it names a
# script or quotes that placeholder as an argument. The second half of that test is what
# keeps the prose mention at *Scoping the plan* — the `<substring>` for ticking, named in a
# sentence and passed to nothing — out of a case about how arguments are quoted, and the
# first is what still catches a line that names a script and passes the fragment bare.
fragment_lines() {
  document_lines "$fragment_ph" | grep -E "\\\$S/|$single_quoted_fragment|$double_quoted_fragment" || true
}

# 9. The step-title rule is about the planning leaf's English reaching a command line, and a
#    fragment of that English is still that English: `tick-ledger.sh`,
#    `clear-refactor-pending.sh` and `tick-issue-criterion.sh` are each handed a distinctive
#    substring of STEP to find the checkbox they tick, and every one of those calls still
#    spells it `'<substring>'`. A step titled *that shell's stderr* gives the conductor
#    `'that shell'` followed by junk the shell never accepts — the same unterminated quote
#    case 8 is about, one argument over (issue #431).
#
#    So the rule case 8 requires the document to state once is required here to hold of every
#    line that carries text taken from the title, not only of the lines that carry the whole
#    of it. Read over the whole document rather than over the fenced blocks alone, because
#    three of these calls are written inline in prose — the script inventory's entries, and
#    the issue-mirroring call Green ends with — and a conductor copies those as readily as it
#    copies a fenced one.
name="$skill_md double-quotes every documented command line that passes a fragment of the step's title"
problems=()

fragments="$(fragment_lines)"
if [[ -z "$fragments" ]]; then
  unreadable "command line passing a fragment of the step's title" "how a fragment of the step's title reaches a command line"
else
  read_quoted_lines "$fragments" "a fragment of the step title" \
    "$fragment_ph" "$single_quoted_fragment" "$double_quoted_fragment"
fi

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
