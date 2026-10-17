#!/usr/bin/env bash
# Unit tests for the two root documents' record of the per-role model tunables — which
# variable a leaf reads, and why the developer's and the verifier's are two knobs.
#
# Contract under test:
#   SKILL.md's `supervise.sh` bullet lists all four tunables — `VERI_MODEL`,
#   `VERI_MODEL_DEVELOPER`, `VERI_MODEL_REVISE`, `VERI_MODEL_VERIFIER` — beside the tunables it already lists;
#   and CLAUDE.md names all four and says why the developer's and the verifier's are
#   separate knobs: the verdict distribution on one side, revise cycles on the other.
#   Each fact is matched by a regex, not a fixed string.
#
# Run: skills/tdd/scripts/tests/model-knobs-recorded.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

claude_md="CLAUDE.md"
claude_path="$ROOT/$claude_md"
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

source "$HERE/lib/harness.sh"

source "$HERE/record-helpers.sh"
source "$HERE/lib/claude-md-records.sh"

MODEL_ANY='veri_model([^_a-z]|$)'
MODEL_DEV='veri_model_developer'
MODEL_VER='veri_model_verifier'
MODEL_REV='veri_model_revise'

passage_text="" passage_from=""

need_supervise_bullet() {
  passage_from="$skill_md's supervise.sh bullet"
  passage_text="$(bullet '^[-*] .*supervise\.sh')"
  [[ -n "${passage_text// /}" ]] && return 0
  problems+=("$skill_md has no top-level 'supervise.sh' bullet to read, so the tunables an operator looks up beside VERI_TIMEOUT could not be found")
  return 1
}

names_all_four() {
  local what="$1"
  says "$what — it names no single passage carrying VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_REVISE and VERI_MODEL_VERIFIER" \
    "$MODEL_ANY" "$MODEL_DEV" "$MODEL_REV" "$MODEL_VER"
}

probe_skill_bullet_lists_the_tunables() {
  need_supervise_bullet || return

  names_all_four "lists the four model tunables beside the ones it already lists"
}

probe_claude_md_names_them_and_why() {
  need_claude_md_records || return

  names_all_four "names the four model tunables"

  says "why the developer's and the verifier's models are separate knobs — the two roles named, that the knobs are not one, and how each one's regression shows up: a changed verdict distribution against more revise cycles" \
    'developer' \
    'verifier' \
    'separate|two knobs|one knob|independent|its own|their own|never merged' \
    'verdict' \
    'revise'
}


finish
