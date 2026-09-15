#!/usr/bin/env bash
# Unit tests for the two root documents' record of the per-role model tunables — which
# variable a leaf reads, and why the developer's and the verifier's are two knobs and not
# one. Like lane-rule-recorded.test.sh and skill-timeout.test.sh this suite's subject is a
# document rather than a script: what an operator is told before any leaf launches.
# Zero-dependency plain-shell asserts, same idiom as lane-rule-recorded.test.sh.
#
# Why this exists (issue #171): `leaf-model.sh` resolves the model and `supervise.sh` puts
# it on the leaf's command line, so a run can already be moved onto a cheaper model — but a
# tunable nobody is told about is one nobody sets. The two places an operator looks are
# SKILL.md's `supervise.sh` bullet, which is where every other leaf tunable is listed
# (`VERI_HEARTBEAT`, `VERI_TIMEOUT`, `VERI_STUCK_RETRIES`), and CLAUDE.md, which is the
# first thing an agent reads. The `VERI_MODEL_VERIFIER` experiment that motivates the whole
# issue cannot be run by someone who cannot find the variable's name.
#
# And the *why* is not decoration. The two roles fail differently: a cheaper verifier shows
# up as a changed verdict distribution, a cheaper developer as more revise cycles and worse
# code. One knob over both would make "cheaper developer" and "weaker verifier" the same
# decision — the identical trap CLAUDE.md already records for the three budgets, whose
# entry says why they are never merged. A document that named the three variables without
# that sentence would leave the next reader free to collapse them.
#
# Contract under test:
#   SKILL.md's `supervise.sh` bullet lists all three tunables — `VERI_MODEL`,
#   `VERI_MODEL_DEVELOPER`, `VERI_MODEL_VERIFIER` — beside the tunables it already lists;
#   and CLAUDE.md names all three and says why the developer's and the verifier's are
#   separate knobs, in the terms the failure actually takes: the verdict distribution on
#   one side, revise cycles on the other.
#
# Facts are asked as the regexes any wording carrying them would match, never as fixed
# strings: what a document has to record is the claim, and how it is phrased belongs to
# whoever writes it — the protocol lane-rule-recorded.test.sh and skill-suite-runs.test.sh
# both use on these documents.
#
# Not asked here: that CLAUDE.md's script and suite counts moved when this suite landed.
# claude-md-counts.test.sh is the case that holds every count in that document to the files
# on disk, and this file arriving in the tree is what makes it answer.
#
# Run: skills/tdd/scripts/tests/model-knobs-recorded.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The two documents. Each twice — the path as a failure message spells it, and the same
# path resolved for the probes to read — so a message can never name a file the probes did
# not open. The pairing claude-md-counts.test.sh and skill-leaf-launch.test.sh both use.
claude_md="CLAUDE.md"
claude_path="$ROOT/$claude_md"
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which document is missing which sentence rather than just that one is.
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
# `VERI_MODEL` or **separate**. The normalisation lane-rule-recorded.test.sh uses on these
# same documents, for the same reason.
plain() { tr -d '*`' | tr '[:upper:]' '[:lower:]'; }

# records — markdown on stdin, one line per paragraph or bullet, normalised through
# `plain`. A record runs from a `- ` or a `* ` in column one, or from the first line after
# a blank, up to the next such line or the next blank; joining it onto one line is what
# lets a claim ask whether ONE passage carries a whole fact, rather than two sentences
# sections apart that happen to share a word. Both documents wrap mid-sentence, so this is
# also what keeps a claim split over a line break readable as one sentence. Same shape as
# skill-timeout.test.sh's `paragraphs`.
records() {
  awk '/^[-*] / { if (rec != "") print rec; rec = $0; next }
       /^[[:space:]]*$/ { if (rec != "") print rec; rec = ""; next }
       rec == "" { rec = $0; next }
       { rec = rec " " $0 }
       END { if (rec != "") print rec }' | plain
}

# bullet <regex> — the one top-level `- ` bullet of a document whose first line matches,
# as one normalised line. The tunables belong in the bullet that documents the launcher
# they are read by: a file-wide read of SKILL.md would answer "yes, it is in there" for a
# document that named `VERI_MODEL` only in the preflight step that validates it, which is
# where it is named today and is not where an operator looking up a tunable is reading.
bullet() {
  awk -v want="$1" '
    $0 ~ want { inside = 1; print; next }
    inside && /^([-*] |#)/ { exit }
    inside' "$skill_path" | plain | tr '\n' ' '
}

# The three variables, as the regexes that tell them apart. The bare `VERI_MODEL` is
# bounded on the right, because `veri_model_developer` contains it: without the bound a
# document that named only the two role variables would read as one that named all three.
MODEL_ANY='veri_model([^_a-z]|$)'
MODEL_DEV='veri_model_developer'
MODEL_VER='veri_model_verifier'

# passage_text / passage_from — the passage a probe last read and the label a failure names
# it by, filled by the two readers below and read by `names_all_three` and `says`. Globals
# because bash has no way to hand back a string; the `passage_` prefix is what marks the
# pair as one thing written by a reader and read by a claim, the convention
# lane-rule-recorded.test.sh's `section_` pair follows.
passage_text="" passage_from=""

# need_bullet <label> <regex> <problem> — one SKILL.md bullet into those globals, or the
# <problem> and a non-zero return. Fail closed: an empty string matches no regex, so every
# fact asked of a bullet that is not there would be reported missing — true, but it names
# three edits when the repair is that one bullet moved.
need_bullet() {
  passage_from="$skill_md's $1"
  passage_text="$(bullet "$2")"
  [[ -n "${passage_text// /}" ]] && return 0
  problems+=("$3")
  return 1
}

# need_records <label> <path> — a whole document's records into the same globals, for the
# claims that are about what a document says rather than about where it says it. CLAUDE.md
# is read this way on purpose: the step asks that the document name the variables and give
# the reason, not that either sit under a heading this suite picked.
need_records() {
  passage_from="$2"
  passage_text="$(records < "$1")"
  [[ -n "${passage_text// /}" ]] && return 0
  problems+=("$2 could not be read, so nothing could be asked of what it records")
  return 1
}

# says <fact> <regex>... — one fact the passage last read has to carry: some ONE record of
# it has to match every <regex>, and one problem naming the passage and the fact is
# appended if none does. A pair split across two records is not a statement — it is two
# sentences that happen to share a word — which is why the regexes are asked of a record
# and not of the passage as a whole.
says() {
  local fact="$1" line re
  shift
  while IFS= read -r line; do
    for re in "$@"; do
      [[ "$line" =~ $re ]] || continue 2
    done
    return 0
  done <<< "$passage_text"
  problems+=("$passage_from does not say $fact")
}

# names_all_three <what> — the three variables in one record of the passage last read.
# Written once because both documents owe it and a copy that drifted would leave one of
# them held to a shorter list than the other.
names_all_three() {
  says "$what — it names no single passage carrying VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER" \
    "$MODEL_ANY" "$MODEL_DEV" "$MODEL_VER"
}

# probe_skill_bullet_lists_the_tunables — the launcher's bullet is where every leaf tunable
# is listed, and a fourth axis that is not in that list is one an operator has no way to
# find: `VERI_HEARTBEAT`, `VERI_TIMEOUT` and `VERI_STUCK_RETRIES` are all read off it.
probe_skill_bullet_lists_the_tunables() {
  need_bullet 'supervise.sh bullet' '^[-*] .*supervise\.sh' \
    "$skill_md has no top-level 'supervise.sh' bullet to read, so the tunables an operator looks up beside VERI_TIMEOUT could not be found" \
    || return

  what="lists the three model tunables beside the ones it already lists"
  names_all_three
}

# probe_claude_md_names_them_and_why — the document an agent reads first, and the two facts
# it owes: the names, and the reason the developer's and the verifier's are two knobs. The
# reason is asked in the terms the failure takes — a changed verdict distribution on one
# side, more revise cycles on the other — because that is what makes the sentence load-
# bearing rather than a restatement that there happen to be two variables.
probe_claude_md_names_them_and_why() {
  need_records "$claude_path" "$claude_md" || return

  what="names the three model tunables"
  names_all_three

  says "why the developer's and the verifier's models are separate knobs — the two roles named, that the knobs are not one, and how each one's regression shows up: a changed verdict distribution against more revise cycles" \
    'developer' \
    'verifier' \
    'separate|two knobs|one knob|independent|its own|their own|never merged' \
    'verdict' \
    'revise'
}

# 1. One criterion, one case: the tunables are documented where they are looked up, with
#    the reason that keeps them apart. One case rather than three, because a reader given
#    two of the three names, or the three names without the reason, has been handed the
#    same unusable record — and the problem lines say which sentence is missing from which
#    document.
name="$skill_md's supervise.sh bullet and $claude_md name VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER, and $claude_md says why developer and verifier are separate knobs"
problems=()
what=""

probe_skill_bullet_lists_the_tunables
probe_claude_md_names_them_and_why

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
