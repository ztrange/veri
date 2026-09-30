#!/usr/bin/env bash
# Unit test for what skills/tdd/SKILL.md tells an operator about launching the CONDUCTOR —
# not a leaf. Like skill-leaf-launch.test.sh and skill-timeout.test.sh this suite belongs to
# no single script: its subject is the procedure read as text, the way the person about to
# type the command reads it. Zero-dependency plain-shell asserts, same idiom as
# model-knobs-recorded.test.sh.
#
# Why this exists (issue #187): `/tdd <n>` is a skill, so it can be typed inside an
# interactive Claude Code session — and on 2026-09-14, resuming #163, that is what happened.
# What the binary then refused, and what the run had already paid for by then, are said in
# `leaf-launchable.sh`'s header (leaf-launchable.sh:4-22), once; that script now catches the
# class of fault before any of it — but a check that refuses is only half an answer. The
# operator it refuses needs to be told what to do instead, and that sentence has never been
# written down: every run to date was launched from a plain shell by habit, not because the
# document said so.
#
# The second half is a decision, not a convenience. The binary's own message offers a way
# out — unset the variable — and veri declining to take it is a choice that has to be on the
# page, because the risk it declines is the operator's: "will crash all active sessions" is
# their sessions, and a tool that quietly unset the guard would be spending that risk on
# their behalf without telling them. A document that recorded the refusal without the reason
# would leave the next reader free to "fix" it by unsetting the variable in the launcher.
#
# Contract under test (this step only — the check itself is leaf-launchable.test.sh's):
#   SKILL.md says, in one passage, how to run the conductor when the operator is already
#   inside a session — a plain shell, outside it, `claude -p "/tdd <n>"` — and says, in one
#   passage, that veri never unsets CLAUDECODE itself and why.
#
# Facts are asked as the regexes any wording carrying them would match, never as fixed
# strings: what the document has to record is the claim, and how it is phrased belongs to
# whoever writes it — the protocol lane-rule-recorded.test.sh and model-knobs-recorded.test.sh
# both use on these documents.
#
# Asked of a RECORD — one paragraph or bullet — rather than of the file, because two
# sentences sections apart that happen to share a word are not a statement. SKILL.md already
# spells `claude -p "/tdd <n>"` once, in the paragraph about print-mode leaf orphaning; that
# paragraph is not this instruction, and a file-wide read would accept it as one.
#
# Not asked here: that CLAUDE.md's script and suite counts moved when this suite landed.
# claude-md-counts.test.sh is the case that holds every count in that document to the files
# on disk, and this file arriving in the tree is what makes it answer.
#
# Run: scripts/tests/skill-conductor-launch.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"


source "$HERE/lib/harness.sh"

plain() { tr -d '*`' | tr '[:upper:]' '[:lower:]'; }

records() {
  awk '/^[-*] / { if (rec != "") print rec; rec = $0; next }
       /^[[:space:]]*$/ { if (rec != "") print rec; rec = ""; next }
       rec == "" { rec = $0; next }
       { rec = rec " " $0 }
       END { if (rec != "") print rec }' | plain
}

passage_text="" passage_from=""

need_skill_records() {
  passage_from="$skill_md"
  passage_text="$(records < "$skill_path")"
  [[ "$passage_text" =~ [^[:space:]] ]] && return 0
  problems+=("$skill_md could not be read, so nothing could be asked of what it tells an operator")
  return 1
}

matches_all() {
  local record="$1" re
  shift
  for re in "$@"; do
    [[ "$record" =~ $re ]] || return 1
  done
}

says() {
  local fact="$1" line
  shift
  while IFS= read -r line; do
    matches_all "$line" "$@" && return 0
  done <<< "$passage_text"
  problems+=("$passage_from does not say $fact")
}

never_says() {
  local claim="$1" line
  shift
  while IFS= read -r line; do
    matches_all "$line" "$@" || continue
    problems+=("$passage_from still says $claim: \"${line:0:120}...\"")
  done <<< "$passage_text"
}

NESTED='claudecode|nested|inside (another|a) claude|interactive session|own session|already in'

probe_says_the_supported_invocation() {
  says "how to launch the conductor when the operator is already inside a Claude Code session — no single passage names the nesting, the supported invocation claude -p \"/tdd <n>\", and that it is typed in a plain shell outside the session" \
    "$NESTED" \
    'claude -p' \
    '/tdd' \
    'plain shell|ordinary shell|normal shell|separate shell|own shell|a terminal|outside (the|that|this) session|outside claude code'
}

probe_says_veri_never_unsets_the_guard() {
  says "that veri never unsets CLAUDECODE itself, nor why — the guard's stated risk is the operator's to take knowingly" \
    'claudecode' \
    'unset' \
    'never|does not|will not|refus|not veri|leaves it' \
    'crash|risk|danger' \
    'operator|user|you|human|their|yours'
}

name="$skill_md says how to launch the conductor when the operator is already inside a Claude Code session, and that veri never unsets CLAUDECODE itself"
problems=()

if need_skill_records; then
  probe_says_the_supported_invocation
  probe_says_veri_never_unsets_the_guard
fi

report "$name"

INTERACTIVE='interactive|chat session|inside a session|a session you|typed into a session'
PRINT='print mode|print-mode|claude -p'

probe_says_which_launch_modes_exist() {
  says "which launch modes exist — no single passage names the interactive session, print mode, and run-conductor.sh" \
    "$INTERACTIVE" \
    "$PRINT" \
    'run-conductor'
}

CANNOT_INTERVENE='(cannot|can not|no way to|nobody can|no one can|impossible to|never|not) (be )?(asked|answered|questioned|interrupted|redirected|steered|reached|stopped)'

probe_says_print_mode_cannot_be_asked() {
  says "that a print-mode conductor cannot be asked a question or redirected mid-run" \
    "$PRINT|run-conductor|unattended" \
    "$CANNOT_INTERVENE" \
    'mid-run|mid run|while it is running|once it is running|once it has started|once running|during the run|after it start|under way|underway|in flight'
}

name="$skill_md says which launch modes exist and that a print-mode conductor cannot be asked a question mid-run"
problems=()

if need_skill_records; then
  probe_says_which_launch_modes_exist
  probe_says_print_mode_cannot_be_asked
fi

report "$name"

probe_never_says_a_pull_swaps_live_scripts() {
  never_says "that pulling the primary clone changes the scripts under a live run" \
    'pull' \
    'primary' \
    '(chang|swap|replac|mov)[a-z]* (the )?script' \
    'live|running|in flight|under (it|a run|the run)'
}

name="$skill_md no longer says pulling the primary clone changes the scripts under a live run"
problems=()

if need_skill_records; then
  probe_never_says_a_pull_swaps_live_scripts
fi

report "$name"

probe_says_the_launch_mode_is_a_trade() {
  says "that interactive and print mode are a trade picked per run — interactive can be steered and costs ~25,000 tokens a request more, print mode is that much cheaper and turns every question into a bail" \
    "$INTERACTIVE" \
    "$PRINT|run-conductor" \
    'steer|intervene|redirect' \
    '25,?000|25k' \
    'token' \
    'request' \
    'cheaper|less|saves' \
    'bail' \
    'trade|per run|each run|every run'
}

name="$skill_md presents interactive and print mode as a trade picked per run: steerable at ~25,000 tokens a request more, or that much cheaper with every question a bail"
problems=()

if need_skill_records; then
  probe_says_the_launch_mode_is_a_trade
fi

report "$name"

probe_never_says_an_interactive_run_does_not_belong() {
  never_says "that an interactive session is not where a run belongs" \
    "$INTERACTIVE" \
    'not where (a|the|your) (run|conductor) belongs|(run|conductor)s? (does|do) not belong|(is|are) not (a|the) place (for|to) (a )?(run|conductor)'
}

name="$skill_md no longer says an interactive session is not where a run belongs"
problems=()

if need_skill_records; then
  probe_never_says_an_interactive_run_does_not_belong
fi

report "$name"

PREFER_PRINT='(prefer|recommend|should|always|the (supported|right|proper|only) way)[^.]*(print mode|print-mode|claude -p|run-conductor|plain shell|outside (any|the|that|a) (claude code )?session)'

probe_says_print_mode_is_preferred_for_its_token_cost() {
  says "that print mode's advantage is ~25,000 tokens a request cheaper, #207's measurement" \
    "$PRINT|run-conductor" \
    '25,?000|25k' \
    'token' \
    'request' \
    'cheaper|less|saves'
  never_says "that print mode is preferred because of the CLAUDECODE nested-session refusal" \
    'claudecode|nested|guard' \
    "$PREFER_PRINT"
}

name="$skill_md gives the ~25,000-token per-request cost as the reason for print mode, never the CLAUDECODE nested-session refusal"
problems=()

if need_skill_records; then
  probe_says_print_mode_is_preferred_for_its_token_cost
fi

report "$name"

probe_says_what_to_do_if_a_nested_launch_guard_fires() {
  says "what to do if a nested-launch guard fires — no single passage ties the guard firing to running claude -p \"/tdd <n>\" from a plain shell outside the session" \
    'guard' \
    '(when|if|once) (one|it|the guard|a guard)[^.]*(fires|fired|does|trips|refuses)' \
    'plain shell|ordinary shell|normal shell|separate shell|outside (any|the|that|this) (claude code )?session' \
    'claude -p' \
    '/tdd'
}

name="$skill_md still says, if a nested-launch guard fires, to run the conductor from a plain shell outside the session with claude -p \"/tdd <n>\""
problems=()

if need_skill_records; then
  probe_says_what_to_do_if_a_nested_launch_guard_fires
fi

report "$name"

finish
