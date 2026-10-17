#!/usr/bin/env bash
# Tests for scripts/build-verify-prompt.sh — assembles a BLIND verifier leaf's prompt
# from on-disk artifacts only: the issue's behavior spec and the test's path. It has no
# parameter for the developer leaf's rationale, so rationale structurally cannot enter
# the verifier's context (ADR-0003). This is the seam that makes blindness enforceable
# rather than left to the conductor's discretion.
#
# Run: scripts/tests/build-verify-prompt.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
BUILD="$HERE/../build-verify-prompt.sh"
source "$HERE/lib/harness.sh"
source "$HERE/lib/probe-order.sh"

work="$(scratch_dir)"

cat > "$work/spec.md" <<'SPEC'
slugify("Hello & World/Foo") must return "hello-world-foo" — see {ref}\n done.
SPEC
testpath="tests/test_slugify.py"
fast_for() { fast=(); [[ "$1" == green || "$1" == refactor ]] && fast=( --fast-cmd 'make unit' ); }

red="$("$BUILD" red "$work/spec.md" "$testpath" test_slugify_lowercases)"

prompt_has() {  # prompt_has <prompt> <grep argument…> — the match itself, folded to one line
  local prompt="$1"; shift
  grep -q "$@" <<<"$(tr '\n' ' ' <<<"$prompt")"
}

# hazard: BSD grep refuses a bounded repetition over 255 and exits non-zero, which reads as a miss.
prompt_says() {  # prompt_says <prompt> <complaint> <grep argument…>
  local prompt="$1" complaint="$2"; shift 2
  prompt_has "$prompt" "$@" || problems="$problems; $complaint"
}

prompt_lacks() {  # prompt_lacks <prompt> <complaint> <grep argument…> — prompt_says inverted
  local prompt="$1" complaint="$2"; shift 2
  ! prompt_has "$prompt" "$@" || problems="$problems; $complaint"
  return 0
}

finish
