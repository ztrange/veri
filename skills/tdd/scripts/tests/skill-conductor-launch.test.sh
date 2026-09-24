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
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The document twice — the path as every failure message spells it, and the same path
# resolved for the probes to read — so a message can never name a file the probes did not
# open. The pairing model-knobs-recorded.test.sh and skill-leaf-launch.test.sh both use.
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which half of the instruction is missing rather than just that one is.
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

# plain — stdin with emphasis marks and backticks dropped and the case folded, so a regex
# below is written one way and still matches prose that marked the same words up as
# `CLAUDECODE` or **never**. The normalisation lane-rule-recorded.test.sh uses on these same
# documents, for the same reason.
plain() { tr -d '*`' | tr '[:upper:]' '[:lower:]'; }

# records — markdown on stdin, one line per paragraph or bullet, normalised through `plain`.
# A record runs from a `- ` or a `* ` in column one, or from the first line after a blank, up
# to the next such line or the next blank; joining it onto one line is what lets a claim ask
# whether ONE passage carries a whole fact. SKILL.md wraps mid-sentence, so this is also what
# keeps a claim split over a line break readable as one sentence. Same shape as
# model-knobs-recorded.test.sh's `records`.
records() {
  awk '/^[-*] / { if (rec != "") print rec; rec = $0; next }
       /^[[:space:]]*$/ { if (rec != "") print rec; rec = ""; next }
       rec == "" { rec = $0; next }
       { rec = rec " " $0 }
       END { if (rec != "") print rec }' | plain
}

# passage_text / passage_from — the passage a probe last read and the label a failure names
# it by, filled by the reader below and read by `says`. Globals because bash has no way to
# hand back a string; the `passage_` prefix is what marks the pair as one thing written by a
# reader and read by a claim, the convention model-knobs-recorded.test.sh follows.
passage_text="" passage_from=""

# need_skill_records — all of SKILL.md's records into those globals, or one problem and a
# non-zero return. The document is read whole on purpose: the step asks that it state the
# invocation and the decision, not that either sit under a heading this suite picked — where
# an instruction to an operator belongs is the author's call.
#
# Fail closed: an empty string matches no regex, so both facts would be reported missing —
# true, but it names two edits when the repair is that the document could not be read.
need_skill_records() {
  passage_from="$skill_md"
  passage_text="$(records < "$skill_path")"
  # Asked as a regex rather than with `${passage_text// /}`, the idiom
  # model-knobs-recorded.test.sh uses for this: that substitution is quadratic in bash 3.2
  # and SKILL.md is ~40 kB of records, which is minutes rather than the milliseconds the
  # same line costs on CLAUDE.md. One non-space character is the same question.
  [[ "$passage_text" =~ [^[:space:]] ]] && return 0
  problems+=("$skill_md could not be read, so nothing could be asked of what it tells an operator")
  return 1
}

# matches_all <record> <regex>... — whether ONE record matches every <regex>, the question
# `says` and `never_says` both ask of each record of the passage.
matches_all() {
  local record="$1" re
  shift
  for re in "$@"; do
    [[ "$record" =~ $re ]] || return 1
  done
}

# says <fact> <regex>... — one fact the passage last read has to carry: some ONE record of it
# has to match every <regex>, and one problem naming the passage and the fact is appended if
# none does.
says() {
  local fact="$1" line
  shift
  while IFS= read -r line; do
    matches_all "$line" "$@" && return 0
  done <<< "$passage_text"
  problems+=("$passage_from does not say $fact")
}

# never_says <claim> <regex>... — the converse of `says`: a claim the passage last read must NO
# LONGER carry. Every record matching all of <regex> is a problem, and the problem quotes the
# start of the record, so the failure points at the sentence to rewrite rather than at the file.
never_says() {
  local claim="$1" line
  shift
  while IFS= read -r line; do
    matches_all "$line" "$@" || continue
    problems+=("$passage_from still says $claim: \"${line:0:120}...\"")
  done <<< "$passage_text"
}

# The nesting, as the regexes any wording naming it would match: the operator's own session,
# an interactive one, the variable that once marked it, or a launch inside another session.
# Both facts name it, because both are about that situation and neither is a general note
# about how to invoke the skill.
NESTED='claudecode|nested|inside (another|a) claude|interactive session|own session|already in'

# probe_says_the_supported_invocation — the sentence the refusal sends the operator to. Four
# regexes: the situation, the binary, the command, and the place it is typed. Prose that
# named the situation and the binary without saying WHERE — a shell outside the session — is
# the instruction that was already inferable and that #187 shows nobody inferred.
probe_says_the_supported_invocation() {
  says "how to launch the conductor when the operator is already inside a Claude Code session — no single passage names the nesting, the supported invocation claude -p \"/tdd <n>\", and that it is typed in a plain shell outside the session" \
    "$NESTED" \
    'claude -p' \
    '/tdd' \
    'plain shell|ordinary shell|normal shell|separate shell|own shell|a terminal|outside (the|that|this) session|outside claude code'
}

# probe_says_veri_never_unsets_the_guard — the decision, with the reason that keeps it from
# being read as an oversight. The reason is asked in the terms the risk actually takes — a
# crash, and whose sessions it is — because a passage that said "veri does not unset it"
# without that is a note the next reader can undo in one line.
probe_says_veri_never_unsets_the_guard() {
  says "that veri never unsets CLAUDECODE itself, nor why — the guard's stated risk is the operator's to take knowingly" \
    'claudecode' \
    'unset' \
    'never|does not|will not|refus|not veri|leaves it' \
    'crash|risk|danger' \
    'operator|user|you|human|their|yours'
}

# 1. One criterion, one case: the document tells an operator inside a session what to type,
#    and what veri will not do for them. One case rather than two, because half of it is the
#    same unusable record — an operator told the tool refuses but not what to run instead is
#    as stuck as one told nothing, and the problem lines say which half is missing.
name="$skill_md says how to launch the conductor when the operator is already inside a Claude Code session, and that veri never unsets CLAUDECODE itself"
problems=()

if need_skill_records; then
  probe_says_the_supported_invocation
  probe_says_veri_never_unsets_the_guard
fi

report "$name"

# The launch modes, as the regexes any wording naming them would match. The set is the one
# the document has to enumerate once #207 lands: the skill typed into a session the operator
# is sitting in, and the two unattended shapes — `claude -p "/tdd <n>"` typed by hand, and
# `run-conductor.sh <n>`, the script that builds that command line. `run-conductor` is asked
# by name because it is the mode this issue adds: a passage listing modes that predates it
# reads as complete and is the one an operator would act on.
INTERACTIVE='interactive|chat session|inside a session|a session you|typed into a session'
PRINT='print mode|print-mode|claude -p'

# probe_says_which_launch_modes_exist — one record enumerating them. Asked of a record, not
# the file, for the reason this suite's header gives: SKILL.md already spells `claude -p
# "/tdd <n>"` and the word `interactive` in the paragraph about print-mode leaf orphaning
# (SKILL.md:292-298), which is not a list of launch modes and must not be accepted as one.
# `run-conductor` is what tells the two apart — that paragraph cannot name a script written
# after it.
probe_says_which_launch_modes_exist() {
  says "which launch modes exist — no single passage names the interactive session, print mode, and run-conductor.sh" \
    "$INTERACTIVE" \
    "$PRINT" \
    'run-conductor'
}

# probe_says_print_mode_cannot_be_asked — the trade. Three regexes: which mode, the thing
# that cannot be done to it, and when.
#
# The negation and the verb are ONE regex, not two. Asked separately they matched the
# preflight record (SKILL.md:345) — a ~200-word paragraph that happens to contain "ask the
# user to commit", "no longer" and "while it" in three unrelated sentences. A record here is
# long enough that three independent words co-occur by chance, so a fact spread over three
# probes is not a fact; requiring the negation to sit ON the verb is what makes the claim the
# sentence rather than the vocabulary.
CANNOT_INTERVENE='(cannot|can not|no way to|nobody can|no one can|impossible to|never|not) (be )?(asked|answered|questioned|interrupted|redirected|steered|reached|stopped)'

probe_says_print_mode_cannot_be_asked() {
  says "that a print-mode conductor cannot be asked a question or redirected mid-run" \
    "$PRINT|run-conductor|unattended" \
    "$CANNOT_INTERVENE" \
    'mid-run|mid run|while it is running|once it is running|once it has started|once running|during the run|after it start|under way|underway|in flight'
}

# 2. One criterion, one case: the operator choosing a mode reads what the modes are and what
#    the unattended one costs them. One case rather than two, for the same reason as case 1 —
#    a list of modes with no note of what print mode gives up is the list that makes the
#    trade invisible, which is the half #207 says an operator should read rather than
#    discover.
name="$skill_md says which launch modes exist and that a print-mode conductor cannot be asked a question mid-run"
problems=()

if need_skill_records; then
  probe_says_which_launch_modes_exist
  probe_says_print_mode_cannot_be_asked
fi

report "$name"

# probe_never_says_a_pull_swaps_live_scripts — the operating rule #251 retires. Once a run
# executes the skill pinned from origin/<default> as just fetched, the primary clone's working
# tree is not what any leaf runs, so a passage warning that pulling it changes the scripts
# under a live run is false, and it is the passage that kept the primary 50 commits behind.
# Four regexes, one record: the act (pulling), its object (the primary clone), the claimed
# effect (changing or swapping the scripts), and when (a live or running run). A record saying
# pulling the primary is now cosmetic names the act and the object but not the effect, and is
# not caught.
probe_never_says_a_pull_swaps_live_scripts() {
  never_says "that pulling the primary clone changes the scripts under a live run" \
    'pull' \
    'primary' \
    '(chang|swap|replac|mov)[a-z]* (the )?script' \
    'live|running|in flight|under (it|a run|the run)'
}

# 3. One criterion, one case (#251): SKILL.md no longer carries the "don't pull the primary
#    while a run is live" rationale, because the run no longer executes the primary's scripts.
name="$skill_md no longer says pulling the primary clone changes the scripts under a live run"
problems=()

if need_skill_records; then
  probe_never_says_a_pull_swaps_live_scripts
fi

report "$name"

# probe_says_the_launch_mode_is_a_trade — issue #213: interactive and print mode are a trade
# the operator picks per run, not one right mode and one wrong one, so ONE record has to carry
# both sides of it. Interactive: it can be steered, and it costs ~25,000 tokens a request more
# (#207's measurement, recorded at run-conductor.sh:7). Print mode: that much cheaper, and every
# question it would have put becomes a bail. Asked of one record for the reason case 2's
# CANNOT_INTERVENE gives: a paragraph naming the steering and another naming the price, sections
# apart, is two facts the reader has to put together, which is exactly how the two passages
# #213 found came to contradict each other.
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

# 4. One criterion, one case (#213): the launch section presents the two modes as a trade the
#    operator picks per run, with what each costs and what each gives up.
name="$skill_md presents interactive and print mode as a trade picked per run: steerable at ~25,000 tokens a request more, or that much cheaper with every question a bail"
problems=()

if need_skill_records; then
  probe_says_the_launch_mode_is_a_trade
fi

report "$name"

# probe_never_says_an_interactive_run_does_not_belong — issue #213's other half: once the
# launch section presents interactive as a mode to pick deliberately (case 4), a passage
# saying an interactive session is not where a run belongs is the contradiction #213 found,
# and whichever of the two a reader lands on first is the guidance they follow. Two regexes,
# one record: the interactive session, and the verdict that a run does not belong there.
# "leaves the decision where it belongs", the CLAUDECODE paragraph's closing clause, names
# neither a run nor a conductor and is not caught.
probe_never_says_an_interactive_run_does_not_belong() {
  never_says "that an interactive session is not where a run belongs" \
    "$INTERACTIVE" \
    'not where (a|the|your) (run|conductor) belongs|(run|conductor)s? (does|do) not belong|(is|are) not (a|the) place (for|to) (a )?(run|conductor)'
}

# 5. One criterion, one case (#213): no passage says an interactive run does not belong while
#    case 4's passage says to pick interactive deliberately.
name="$skill_md no longer says an interactive session is not where a run belongs"
problems=()

if need_skill_records; then
  probe_never_says_an_interactive_run_does_not_belong
fi

report "$name"

# A preference for print mode stated as a rule rather than as what to do once a guard fires:
# the verb that makes it one (prefer, recommend, should, always, the supported or right way)
# and the mode it points at, in one sentence. "If it does, run the conductor from a plain shell
# outside any Claude Code session instead", the nested-launch instruction #213 keeps, directs
# the operator only on the guard firing and carries none of those verbs, so it is not caught.
PREFER_PRINT='(prefer|recommend|should|always|the (supported|right|proper|only) way)[^.]*(print mode|print-mode|claude -p|run-conductor|plain shell|outside (any|the|that|a) (claude code )?session)'

# probe_says_print_mode_is_preferred_for_its_token_cost — issue #213: the reason SKILL.md gives
# for picking print mode is what #207 measured, ~25,000 tokens a request cheaper (recorded at
# run-conductor.sh:7), and never the CLAUDECODE nested-session refusal, which stopped firing on
# 2026-09-15 (leaf-launchable.sh:14-17) and was the reason the retired "not where a run
# belongs" sentence gave. Two halves: one record carries the cost as print mode's advantage,
# and no record ties a standing preference for print mode to the nesting guard.
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

# 6. One criterion, one case (#213): print mode's reason is its token cost, and no passage
#    gives the nested-session refusal as the reason to prefer it.
name="$skill_md gives the ~25,000-token per-request cost as the reason for print mode, never the CLAUDECODE nested-session refusal"
problems=()

if need_skill_records; then
  probe_says_print_mode_is_preferred_for_its_token_cost
fi

report "$name"

# probe_says_what_to_do_if_a_nested_launch_guard_fires — issue #213 retires the nesting guard
# as the REASON to prefer print mode (case 6), and must not retire the instruction with it: if a
# guard on nested launches does fire, the operator still has to read where to go. So ONE record
# carries the condition — a guard firing, not a standing rule — and the instruction: a plain
# shell outside the session, `claude -p "/tdd <n>"`. Case 1 asks for the invocation next to the
# nesting; this asks that it be said as what to do once a guard fires.
probe_says_what_to_do_if_a_nested_launch_guard_fires() {
  says "what to do if a nested-launch guard fires — no single passage ties the guard firing to running claude -p \"/tdd <n>\" from a plain shell outside the session" \
    'guard' \
    '(when|if|once) (one|it|the guard|a guard)[^.]*(fires|fired|does|trips|refuses)' \
    'plain shell|ordinary shell|normal shell|separate shell|outside (any|the|that|this) (claude code )?session' \
    'claude -p' \
    '/tdd'
}

# 7. One criterion, one case (#213): the nested-session instruction survives as what to do if a
#    nested-launch guard fires.
name="$skill_md still says, if a nested-launch guard fires, to run the conductor from a plain shell outside the session with claude -p \"/tdd <n>\""
problems=()

if need_skill_records; then
  probe_says_what_to_do_if_a_nested_launch_guard_fires
fi

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
