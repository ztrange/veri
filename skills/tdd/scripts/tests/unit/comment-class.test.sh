#!/usr/bin/env bash
# Tests for scripts/comment-class.sh — prints every `#` line of the shell files it is given
# as `<file>:<line>:<class>`, class 1 a comment in code, 2 a `#` line in a heredoc written
# to a file, 3 one in any other heredoc.
# Fast tier by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/comment-class.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPTS="$HERE/../.."
CLASSIFY="$SCRIPTS/comment-class.sh"
source "$HERE/../lib/harness.sh"

work="$(scratch_dir)"

verdict() {
  if [[ -z "$problems" ]]; then
    ok
  else
    no "$1"
    printf '%s' "$problems"
  fi
}

classify() {
  out="$("$CLASSIFY" "$@" 2>"$work/stderr")" && code=0 || code=$?
  if [[ "$code" != 0 ]]; then
    problems+="    want exit 0, got $code; stderr: $(cat "$work/stderr")"$'\n'
  fi
}

want_line() {
  if ! grep -E "^$1(:|$)" <<< "$out" > /dev/null; then
    problems+="    want a line matching '$1', got:"$'\n'"$out"$'\n'
  fi
}

problems=""
f="$work/plain.sh"
printf '%s\n' 'echo one' '# a comment in code' 'echo two' > "$f"
classify "$f"
want_line "$f:2:1"
verdict "a comment in code outside any heredoc is reported as class 1 with its file and line"

problems=""
for args in "" "--sweepable"; do
  out="$("$CLASSIFY" ${args:+"$args"} 2>"$work/stderr")" && code=0 || code=$?
  if [[ "$code" != 2 ]]; then
    problems+="    with '$args': want exit 2, got $code"$'\n'
  fi
  if [[ -n "$out" ]]; then
    problems+="    with '$args': want empty stdout, got:"$'\n'"$out"$'\n'
  fi
  if [[ "$(cat "$work/stderr")" != "usage: comment-class.sh [--sweepable] <file>…" ]]; then
    problems+="    with '$args': want stderr 'usage: comment-class.sh [--sweepable] <file>…', got:"$'\n'"$(cat "$work/stderr")"$'\n'
  fi
done
verdict "comment-class.sh with no argument, and with --sweepable alone, exits 2 with empty stdout and only its usage line on stderr"

problems=""
f="$work/linked.sh"
printf '%s\n' '# a comment in code' 'cat > out.txt <<EOF' '# written' 'EOF' > "$f"
mkdir -p "$work/elsewhere"
ln -s "$(cd "$SCRIPTS/.." && pwd)" "$work/linked-skill"
in_place="$("$CLASSIFY" "$f" 2>&1)" && in_place_code=0 || in_place_code=$?
linked="$(cd "$work/elsewhere" && "$work/linked-skill/scripts/comment-class.sh" "$f" 2>&1)" && linked_code=0 || linked_code=$?
if [[ "$in_place" != "$f:1:1"$'\n'"$f:3:2" || "$in_place_code" != 0 ]]; then
  problems+="    in place: want '$f:1:1' and '$f:3:2', exit 0; got exit $in_place_code:"$'\n'"$in_place"$'\n'
fi
if [[ "$linked" != "$in_place" || "$linked_code" != "$in_place_code" ]]; then
  problems+="    through the symlink from $work/elsewhere: want exit $in_place_code and:"$'\n'"$in_place"$'\n'"    got exit $linked_code:"$'\n'"$linked"$'\n'
fi
verdict "comment-class.sh, run through a symlink to the skill directory and from another working directory, prints the same lines and exit code as when run in place"

header_walk='FNR == 1 { header = /^#!/; para = 0; fresh = 1; next }
  header && /^#$/ { fresh = 1; next }
  !(header && /^#/) { header = 0; next }'

want_no_header_citation() {
  local cited
  cited="$(awk "$header_walk"'
  /#[0-9]/ { print FILENAME ":" FNR ": " $0 }' "$@")"
  if [[ -n "$cited" ]]; then
    problems+="    want no header line citing an issue number, got:"$'\n'"$cited"$'\n'
  fi
}

want_contract_only_header() {
  local shapeless
  shapeless="$(awk "$header_walk"'
  {
    if (fresh) { para++; if (para > 1 && !/^# Contract under test/ && !/^# Run:/ && !/^#   /) print FILENAME ":" FNR ": " $0 }
    fresh = 0 }' "$@")"
  if [[ -n "$shapeless" ]]; then
    problems+="    want every header paragraph after the description to be a Contract under test block or the Run: line, got:"$'\n'"$shapeless"$'\n'
  fi
}

header_verdict() {
  local name="$1"; shift
  problems=""
  want_no_header_citation "$@"
  want_contract_only_header "$@"
  verdict "$name carries only its contract, and no line of it cites an issue number"
}

problems=""
want_no_header_citation "$SCRIPTS"/tests/[a-e]*.sh
verdict "no line of the leading header block of a top-level tests/*.sh whose name starts with a through e cites an issue number"

problems=""
want_contract_only_header "$SCRIPTS"/tests/[a-e]*.sh
verdict "the leading header block of a top-level tests/*.sh whose name starts with a through e holds only a description, its Contract under test block and its Run: line"

header_verdict "the leading header block of a top-level tests/*.sh whose name starts with f through p" "$SCRIPTS"/tests/[f-p]*.sh

files=()
for f in "$SCRIPTS"/tests/[q-z]*.sh; do
  case "${f##*/}" in skill-*) ;; *) files+=("$f") ;; esac
done
header_verdict "the leading header block of a top-level tests/*.sh whose name starts with q through z, other than the skill-* files," "${files[@]}"

header_verdict "the leading header block of every tests/skill-*.test.sh whose name after skill- starts with a through l" "$SCRIPTS"/tests/skill-[a-l]*.sh

header_verdict "the leading header block of every tests/skill-*.test.sh whose name after skill- starts with m through z" "$SCRIPTS"/tests/skill-[m-z]*.sh

header_verdict "the leading header block of every shell file under tests/unit/, tests/fixtures/, tests/unit-guard/ and tests/offline/" "$SCRIPTS"/tests/unit/*.sh "$SCRIPTS"/tests/fixtures/*/*.sh "$SCRIPTS"/tests/unit-guard/* "$SCRIPTS"/tests/offline/*

finish
