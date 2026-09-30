#!/usr/bin/env bash
# Unit tests for where the skill ships and what it calls itself — like
# hermetic-suites.test.sh this suite belongs to no single script: its subject is the
# skill directory that contains all of them.
# Zero-dependency plain-shell asserts, same idiom as hermetic-suites.test.sh.
#
# Why this exists (issue #105): the invocation name is the one thing every user touches,
# and it is spelled in two places that must agree — the directory Claude Code loads the
# skill from, and the `name:` field of its SKILL.md frontmatter, which is the command.
#
# Contracts under test:
#   skills/tdd/ is a directory, and skills/tdd/SKILL.md's frontmatter reads `name: tdd`.
#   No tracked file outside the two forwarding stubs still names the scripts directory
#   under the skill's old home — the build and test plumbing follows the skill when it moves.
#   Each old name still has a SKILL.md, declaring that old name and forwarding $ARGUMENTS
#   to /tdd, so a session already invoked on the old command keeps working.
#   The skill's Inputs section resolves that forwarded argument three ways — an integer is
#   the single-issue procedure, any other word is a scope, nothing at all is the scope
#   `plain` — with the loop it dispatches to reachable from that section rather than
#   resident in the document.
#   A scope's selection label is `ready-for-agent` for the scope `plain` and
#   `ready-for-agent:<scope>` for any other, with `VERI_LABEL` still overriding it, read
#   from the file the loop now lives in.
#   Only the scope branch is sent to that file — `## Inputs` is the one section of SKILL.md
#   naming it, so a single-issue run keeps the tokens the move saved — while SKILL.md still
#   holds Procedure and the loop delegates each issue back to it.
#
# Run: scripts/tests/skill-identity.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_dir="skills/tdd"
want_name="tdd"
skill_md="$skill_dir/SKILL.md"


source "$HERE/lib/harness.sh"

frontmatter_name() {
  awk 'NR == 1 && $0 == "---" { inside = 1; next }
       inside && $0 == "---" { exit }
       inside && sub(/^name:[[:space:]]*/, "") { print; exit }' "$1"
}

name="the skill ships at $skill_dir/ and its frontmatter reads name: $want_name"
problems=()
[[ -d "$ROOT/$skill_dir" ]] ||
  problems+=("want a directory at $skill_dir, found none")
if [[ -f "$ROOT/$skill_md" ]]; then
  got="$(frontmatter_name "$ROOT/$skill_md")"
  [[ "$got" == "$want_name" ]] ||
    problems+=("$skill_md frontmatter: want name '$want_name', got $(printf '%q' "$got")")
else
  problems+=("want a SKILL.md at $skill_md, found none")
fi
report "$name"

old_skill_dir="skills/solve-issue"
old_scripts_dir="$old_skill_dir/scripts"
stubs=("$old_skill_dir/SKILL.md" "skills/solve-issues/SKILL.md")

stub_name() { basename "$(dirname "$1")"; }

exempt() { [[ "$1" == .tdd/* ]]; }

swept=""
sweep() {
  local code
  swept="$(cd "$ROOT" && git grep --files-with-matches "$1" -e "$2" -- ':!docs' ':!projects/docs')" && code=0 || code=$?
  if [[ "$code" -gt 1 ]]; then
    swept=""
    return "$code"
  fi
  return 0
}

offenders() {
  local f
  while IFS= read -r f; do
    [[ -n "$f" ]] || continue
    exempt "$f" || printf '%s\n' "$f"
  done <<< "$swept"
}

name="no tracked file outside the two stubs still names $old_scripts_dir"
problems=()
sweep --fixed-strings "$old_scripts_dir" || problems+=("git grep failed with exit $?")
while IFS= read -r f; do
  [[ -n "$f" ]] || continue
  exempt "$f" || problems+=("$f still names $old_scripts_dir")
done <<< "$swept"
report "$name"



old_cmds=()
old_dirs=()
for stub in "${stubs[@]}"; do
  old_cmds+=("/$(stub_name "$stub")")
  old_dirs+=("$(dirname "$stub")")
done
old_cmd_alt="(${old_cmds[0]}|${old_cmds[1]})"
cmd_re="(^|[^[:alnum:]_/.-])$old_cmd_alt"

name="no tracked file outside the two stubs names ${old_cmds[0]} or ${old_cmds[1]}"
problems=()
sweep -E "$cmd_re" || problems+=("git grep failed with exit $?")
while IFS= read -r f; do
  [[ -n "$f" ]] || continue
  exempt "$f" && continue
  where="$(cd "$ROOT" && head -1 < <(git grep -nE -e "$cmd_re" -- "$f") | cut -c1-100)"
  problems+=("$f still names an old command: $where")
done <<< "$swept"
report "$name"

fold_bullets() {
  awk '/^- / { if (rec != "") print rec; rec = $0; next }
       /^[[:space:]]*$/ { if (rec != "") print rec; rec = ""; next }
       rec != "" { rec = rec " " $0 }
       END { if (rec != "") print rec }' | tr '[:upper:]' '[:lower:]'
}

inputs_text() {
  awk '/^## Inputs$/ { inside = 1; next }
       inside && /^## / { exit }
       inside' "$1"
}

inputs_bullets() { inputs_text "$1" | fold_bullets; }

claim() {
  local what="$1" line re
  shift
  while IFS= read -r line; do
    for re in "$@"; do
      [[ "$line" =~ $re ]] || continue 2
    done
    return 0
  done <<< "$bullets"
  problems+=("$bullets_from: no bullet $what")
}

loop_md_path() {
  local p
  p="$(head -1 < <(inputs_text "$1" | grep -oE '[A-Za-z0-9_./-]+\.md' | grep -vE '(^|/)SKILL\.md$'))"
  [[ -n "$p" ]] || return 0
  case "$p" in
    */*) printf '%s\n' "$p" ;;
    *)   printf '%s\n' "$skill_dir/$p" ;;
  esac
}

name="$skill_md resolves its argument: an integer is one issue, any other word a scope, bare is plain"
problems=()
bullets="$(inputs_bullets "$ROOT/$skill_md")"
bullets_from="$skill_md Inputs"
if [[ -z "$bullets" ]]; then
  problems+=("$skill_md has no bullets under '## Inputs' — how the argument resolves could not be read")
else
  claim 'sends an integer argument to the single-issue procedure' \
    'integer' 'single|one issue|procedure'
  claim 'reads a non-integer argument as a scope to drain' \
    'scope' 'drain|loop'
  claim 'makes a bare invocation the scope plain' \
    'plain' 'bare|no argument|without an argument|omit|default|empty'
fi
grep -qE '^#+ .*[Dd]raining a scope' "$ROOT/$skill_md" &&
  problems+=("$skill_md still holds the scope loop's own section, billed on every conductor request")
loop_subs="$(grep -cE '^#+ Loop ' "$ROOT/$skill_md")"
[[ "$loop_subs" -eq 0 ]] ||
  problems+=("$skill_md still holds $loop_subs 'Loop *' sub-sections")
loop_md="$(loop_md_path "$ROOT/$skill_md")"
if [[ -z "$loop_md" ]]; then
  problems+=("$skill_md '## Inputs' names no sibling .md file, so a scope argument resolves to nothing")
elif [[ ! -f "$ROOT/$loop_md" ]]; then
  problems+=("$skill_md Inputs points at $loop_md, which is not a file")
else
  grep -qE '^#+ .*[Dd]raining a scope' "$ROOT/$loop_md" ||
    problems+=("$loop_md has no 'Draining a scope' section, so the pointer leads nowhere")
  grep -qE '^#+ Loop ' "$ROOT/$loop_md" ||
    problems+=("$loop_md has no 'Loop *' sub-sections, so the loop's steps did not move with it")
fi
sibling_scripts="../$(basename "$old_skill_dir")/scripts"
grep -qF "$sibling_scripts" "$ROOT/$skill_md" &&
  problems+=("$skill_md still locates its scripts at $sibling_scripts, a sibling that is no longer there")
report "$name"

name="the loop file derives a scope's label: ready-for-agent for plain, ready-for-agent:<scope> otherwise, VERI_LABEL overriding"
problems=()
loop_md="$(loop_md_path "$ROOT/$skill_md")"
bullets=""
bullets_from="$skill_md"
if [[ -n "$loop_md" && -f "$ROOT/$loop_md" ]]; then
  bullets="$(fold_bullets < "$ROOT/$loop_md")"
  bullets_from="$loop_md"
fi
if [[ -z "$bullets" ]]; then
  problems+=("the loop file $skill_md Inputs points at could not be read for bullets — how a scope's label is derived was not tested")
else
  claim 'gives the scope plain the bare ready-for-agent label' \
    '(^|[^[:alnum:]])plain([^[:alnum:]]|$)' 'ready-for-agent'
  claim 'gives any other scope the label ready-for-agent:<scope>' \
    'scope' 'ready-for-agent:'
  claim 'keeps VERI_LABEL as the override of the derived label' \
    'veri_label' 'overrid|precedence|wins'
fi
report "$name"


name="only the scope branch is sent to the loop file, $skill_md keeps Procedure, and the loop delegates back to it"
problems=()
loop_md="$(loop_md_path "$ROOT/$skill_md")"
grep -qE '^#+ Procedure$' "$ROOT/$skill_md" ||
  problems+=("$skill_md no longer holds a 'Procedure' section, so the single-issue path did not stay put")
if [[ -z "$loop_md" || ! -f "$ROOT/$loop_md" ]]; then
  problems+=("$skill_md '## Inputs' points at no readable loop file — who is sent to read it could not be tested")
else
  loop_base="$(basename "$loop_md")"
  outside="$(awk -v base="$loop_base" '
    /^## Inputs$/ { inside = 1; next }
    inside && /^## / { inside = 0 }
    !inside && index($0, base) { printf "%d: %s\n", NR, substr($0, 1, 90) }' "$ROOT/$skill_md")"
  while IFS= read -r hit; do
    [[ -n "$hit" ]] || continue
    problems+=("$skill_md names $loop_base outside '## Inputs', so a single-issue run is sent to read it too — $hit")
  done <<< "$outside"
  grep -qF 'SKILL.md' < <(grep -E 'Procedure' "$ROOT/$loop_md") ||
    problems+=("$loop_md never sends an issue back to $skill_md's Procedure, so a scope run no longer reaches the procedure it used to")
fi
report "$name"

name="neither old skill directory is left in the tree"
problems=()
for old_dir in "${old_dirs[@]}"; do
  [[ ! -e "$ROOT/$old_dir" ]] ||
    problems+=("want no $old_dir/, found one")
done
report "$name"

name="a tracked file at a former stub path fails both sweeps: exempt no longer covers the stub paths"
problems=()
real_root="$ROOT"
ROOT="$(mktemp -d)"
mkdir -p "$ROOT/${old_dirs[0]}" "$ROOT/${old_dirs[1]}"
printf 'scripts live at %s/run.sh\n' "$old_scripts_dir" > "$ROOT/${stubs[0]}"
printf 'Invoke %s 12 and follow it.\n' "${old_cmds[0]}" > "$ROOT/${stubs[1]}"
if ! (cd "$ROOT" && git init -q && git add -A); then
  problems+=("could not build the scratch repository at $ROOT")
else
  sweep --fixed-strings "$old_scripts_dir" || problems+=("old-home sweep: git grep failed with exit $?")
  [[ "$(offenders)" == *"${stubs[0]}"* ]] ||
    problems+=("old-home sweep: ${stubs[0]} names $old_scripts_dir but was not reported — exempt still covers it")
  sweep -E "$cmd_re" || problems+=("old-command sweep: git grep failed with exit $?")
  [[ "$(offenders)" == *"${stubs[1]}"* ]] ||
    problems+=("old-command sweep: ${stubs[1]} invokes ${old_cmds[0]} but was not reported — exempt still covers it")
fi
rm -rf "$ROOT"
ROOT="$real_root"
report "$name"

name="a tracked file under .tdd/ naming the old home or an old command passes both sweeps"
problems=()
real_root="$ROOT"
ROOT="$(mktemp -d)"
mkdir -p "$ROOT/.tdd"
printf 'scripts live at %s/run.sh\n' "$old_scripts_dir" > "$ROOT/.tdd/issue-1-plan.md"
printf 'Invoke %s 12 and follow it.\n' "${old_cmds[0]}" > "$ROOT/.tdd/issue-2-plan.md"
if ! (cd "$ROOT" && git init -q && git add -A); then
  problems+=("could not build the scratch repository at $ROOT")
else
  sweep --fixed-strings "$old_scripts_dir" || problems+=("old-home sweep: git grep failed with exit $?")
  [[ "$swept" == *".tdd/issue-1-plan.md"* ]] ||
    problems+=("old-home sweep: .tdd/issue-1-plan.md was not matched at all, so its exemption was not tested")
  got="$(offenders)"
  [[ -z "$got" ]] ||
    problems+=("old-home sweep: want no offenders under .tdd/, got: $got")
  sweep -E "$cmd_re" || problems+=("old-command sweep: git grep failed with exit $?")
  [[ "$swept" == *".tdd/issue-2-plan.md"* ]] ||
    problems+=("old-command sweep: .tdd/issue-2-plan.md was not matched at all, so its exemption was not tested")
  got="$(offenders)"
  [[ -z "$got" ]] ||
    problems+=("old-command sweep: want no offenders under .tdd/, got: $got")
fi
rm -rf "$ROOT"
ROOT="$real_root"
report "$name"

name="ADR 0013's line 18, naming the old home as a path passes both sweeps"
problems=()
real_root="$ROOT"
ROOT="$(mktemp -d)"
adr_line="$(printf 'the user-level `~/.claude/%s` symlink into the primary clone silently' "$old_skill_dir")"
mkdir -p "$ROOT/docs/adr" && printf '%s\n' "$adr_line" > "$ROOT/docs/adr/0013-issue-branch-in-its-own-worktree.md"
if ! (cd "$ROOT" && git init -q && git add -A); then
  problems+=("could not build the scratch repository at $ROOT")
else
  sweep --fixed-strings "$old_scripts_dir" || problems+=("old-home sweep: git grep failed with exit $?")
  got="$(offenders)"
  [[ -z "$got" ]] ||
    problems+=("old-home sweep: want no offenders for ADR 0013's line 18, got: $got")
  sweep -E "$cmd_re" || problems+=("old-command sweep: git grep failed with exit $?")
  got="$(offenders)"
  [[ -z "$got" ]] ||
    problems+=("old-command sweep: want no offenders for ADR 0013's line 18, got: $got")
fi
rm -rf "$ROOT"
ROOT="$real_root"
report "$name"

name="README.md's install step symlinks $skill_dir alone and no old skill directory"
problems=()
readme="README.md"
links="$(awk '/^## Install$/ { inside = 1; next }
              inside && /^## / { exit }
              inside && /^ln -s / { print }' "$ROOT/$readme")"
[[ "$links" == *"/$skill_dir\" ~/.claude/skills/$want_name"* ]] ||
  problems+=("$readme ## Install: want an ln -s of $skill_dir to ~/.claude/skills/$want_name, got: ${links:-no ln -s line}")
for old_dir in "${old_dirs[@]}"; do
  [[ "$links" != *"/$old_dir\""* ]] ||
    problems+=("$readme ## Install still links $old_dir/: $links")
done
report "$name"

name="CLAUDE.md's opening paragraph names $skill_dir/ as the product and no old skill directory"
problems=()
claude_md="CLAUDE.md"
opening="$(awk '/^# / && !seen { seen = 1; next }
                seen && /^$/ && started { exit }
                seen && /./ { started = 1; print }' "$ROOT/$claude_md")"
[[ "$opening" == *"product is \`$skill_dir/\`"* ]] ||
  problems+=("$claude_md opening: want it to name \`$skill_dir/\` as the product, got: ${opening:-no opening paragraph}")
for old_dir in "${old_dirs[@]}"; do
  [[ "$opening" != *"$old_dir/"* ]] ||
    problems+=("$claude_md opening still names $old_dir/")
done
report "$name"

finish
