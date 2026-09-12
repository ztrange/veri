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
#
# Run: scripts/tests/skill-identity.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root
# whichever name the skill currently carries — the path this case is about is then
# spelled out in full below rather than derived from where this file happens to live.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The two halves of the identity, each written down exactly once: the directory Claude Code
# loads the skill from, and the command name its frontmatter must declare. Neither is
# derived from the other, so a half-finished move — tree renamed, frontmatter not, or the
# reverse — still fails; and every message below quotes these rather than re-spelling them,
# so there is one place to edit if the skill is ever renamed again.
skill_dir="skills/tdd"
want_name="tdd"
# The frontmatter's file, named in the same terms as the directory: both paths in this suite
# are relative to $ROOT, and $ROOT is applied where they are used. Mixing the two bases — one
# variable relative, one already absolute — is what made the probes below read inconsistently.
skill_md="$skill_dir/SKILL.md"

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem.
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

# 1. Both halves of the skill's identity, as one criterion: the directory it lives in and
#    the name its frontmatter declares. The frontmatter is the leading `---` block, and
#    only its first `name:` counts — the awk stops at the closing `---` so a later `name:`
#    in the prose cannot answer for it.
name="the skill ships at $skill_dir/ and its frontmatter reads name: $want_name"
problems=()
[[ -d "$ROOT/$skill_dir" ]] ||
  problems+=("want a directory at $skill_dir, found none")
if [[ -f "$ROOT/$skill_md" ]]; then
  # sub() edits $0 and returns how many replacements it made, so it doubles as the
  # "this line is the name field" test; print then emits what is left, the value.
  got="$(awk 'NR == 1 && $0 == "---" { inside = 1; next }
              inside && $0 == "---" { exit }
              inside && sub(/^name:[[:space:]]*/, "") { print; exit }' "$ROOT/$skill_md")"
  [[ "$got" == "$want_name" ]] ||
    problems+=("$skill_md frontmatter: want name '$want_name', got $(printf '%q' "$got")")
else
  problems+=("want a SKILL.md at $skill_md, found none")
fi
report "$name"

# The skill's former home, and the scripts directory inside it that the Makefile, the docs
# build and the demo fixtures used to point at. Assembled from two pieces on purpose: the
# probe below greps the whole repository for the joined string, so spelling it out here
# would make this file its own first offender.
old_skill_dir="skills/solve-issue"
old_scripts_dir="$old_skill_dir/scripts"
# The two files the move deliberately leaves behind under the old names, each a stub whose
# body forwards to /tdd. They are allowed to name the old home; nothing else is.
stubs=("$old_skill_dir/SKILL.md" "skills/solve-issues/SKILL.md")

# exempt <path> — true for the files allowed to go on naming the old home: the two stubs,
# and anything under .tdd/, whose ledgers are run state quoting each issue's own words back
# verbatim, including this one's. Named as a predicate so the probe below reads as one
# condition per file rather than a loop whose exit has to be counted out in levels.
exempt() {
  case "$1" in .tdd/*) return 0 ;; esac
  local stub
  for stub in "${stubs[@]}"; do
    [[ "$1" == "$stub" ]] && return 0
  done
  return 1
}

# 2. The plumbing moved with the skill. Stated as the absence it has to produce rather than
#    as a list of files to check, so a path constant hiding somewhere this test never heard
#    of still counts: no tracked file names the old scripts directory except the exempt
#    ones. Tracked, via `git grep`, because the repository's content is what ships.
name="no tracked file outside the two stubs still names $old_scripts_dir"
problems=()
# git grep exits 1 for "no matches", which is the pass here, and 2+ for a real failure —
# collapsing the two would turn a broken probe into a silent green.
hits="$(cd "$ROOT" && git grep --files-with-matches --fixed-strings -e "$old_scripts_dir")" &&
  code=0 || code=$?
if [[ "$code" -le 1 ]]; then
  while IFS= read -r f; do
    [[ -n "$f" ]] || continue
    exempt "$f" || problems+=("$f still names $old_scripts_dir")
  done <<< "$hits"
else
  problems+=("git grep failed with exit $code")
fi
report "$name"

# 3. Where the generated page comes from. `make docs-check` builds docs/walkthrough.html
#    from the scripts and demands the committed page back byte for byte, so a build
#    pointed at a directory the skill has left fails it outright — one "missing script"
#    per listing. The condition for that gate to be green on the new path is this pair:
#    the pipeline reads $skill_dir/scripts, and every script the page documents is there.
#
#    It is a separate case from 2 because case 2 structurally cannot see it. The two
#    python files spell the directory as path COMPONENTS — `ROOT / "skills" / "tdd" /
#    "scripts"` — so the joined string case 2 sweeps for never appears in them, and one
#    left on the old home would keep that case green while `make docs` reported every
#    script missing. This is the positive half: the pipeline names the skill's own.
#
#    What this case deliberately does NOT do is rebuild the page and diff it. That is
#    `docs-fresh`, and the Makefile keeps it out of `make test` on purpose ("Neither is
#    part of `test` on purpose"): the page also encodes tags, blame and a commit count,
#    so a comparison here would turn the baseline red on a tag nobody cut in this repo
#    and on every script a green step edits — and veri refuses to start on a red
#    baseline. So this case asserts what makes the gate green and stays quiet about
#    when it was last run.
name="the walkthrough is generated from $skill_dir/scripts"
problems=()
# "skills/tdd/scripts" as python spells it — `"skills" / "tdd" / "scripts"` — derived from
# $skill_dir rather than written out again, so a future rename still has one place to edit:
# quote each path segment, then join on " / ".
py_scripts_dir="$(printf '%s/scripts' "$skill_dir" | sed 's#[^/]*#"&"#g; s#/# / #g')"
for py in docs/build-walkthrough.py docs/check-walkthrough.py; do
  if [[ -f "$ROOT/$py" ]]; then
    # -x so a line that merely mentions the components does not answer for the constant,
    # -F because the expression is a literal, quotes and slashes and all.
    grep -qxF "SCRIPTS_DIR = ROOT / $py_scripts_dir" "$ROOT/$py" ||
      problems+=("$py: want SCRIPTS_DIR = ROOT / $py_scripts_dir, got $(printf '%q' "$(grep -m1 '^SCRIPTS_DIR' "$ROOT/$py")")")
  else
    problems+=("want the page's $py, found none")
  fi
done

# The page's listings are declared in the commentary, one `file="<name>.sh"` per script;
# the build resolves each against SCRIPTS_DIR. A name with no file under the skill's
# scripts directory is exactly the "missing script" the build refuses on.
commentary="docs/wt/commentary.py"
if [[ -f "$ROOT/$commentary" ]]; then
  documented="$(sed -n 's/.*file="\([^"]*\)".*/\1/p' "$ROOT/$commentary")"
  # Fail closed: no names extracted means the declaration moved and nothing was checked,
  # which must not read as "every documented script is present".
  if [[ -z "$documented" ]]; then
    problems+=("$commentary declares no script listings — the page's set of scripts could not be read")
  else
    while IFS= read -r f; do
      [[ -n "$f" ]] || continue
      [[ -f "$ROOT/$skill_dir/scripts/$f" ]] ||
        problems+=("$commentary documents $f, which is not in $skill_dir/scripts")
    done <<< "$documented"
  fi
else
  problems+=("want the page's commentary at $commentary, found none")
fi
report "$name"

# frontmatter_name <file> — the value of the first `name:` inside the leading `---` block,
# empty if the block or the field is missing. Same scan as case 1's: sub() edits $0 and
# returns how many replacements it made, so it doubles as the "this line is the name field"
# test, and the exit at the closing `---` stops prose below from answering for it.
frontmatter_name() {
  awk 'NR == 1 && $0 == "---" { inside = 1; next }
       inside && $0 == "---" { exit }
       inside && sub(/^name:[[:space:]]*/, "") { print; exit }' "$1"
}

# skill_body <file> — everything after the frontmatter block: the instruction a session
# actually reads. The frontmatter is excluded on purpose, because a stub's `description:`
# goes on describing the old command, and it must not be able to answer for the body.
skill_body() {
  awk 'NR == 1 && $0 == "---" { inside = 1; next }
       inside && $0 == "---" { inside = 0; body = 1; next }
       body { print }' "$1"
}

# 4. What the move leaves behind. Deleting the old names would strand any session already
#    invoked on one mid-run, so both keep a SKILL.md — a stub that does the one thing a
#    stub does: send the session on with the arguments it was given. That is three
#    observable facts per file, and all three are needed. The file has to be there at all;
#    its frontmatter has to still declare the OLD name, since that field is the command
#    Claude Code resolves `/solve-issue` by, and a stub renamed to `tdd` would answer to
#    nothing; and the body has to name both `/tdd` and `$ARGUMENTS` — the destination, and
#    the harness's own spelling for "the arguments this invocation carried", used that way
#    by every SKILL.md in this repo. A body naming only `/tdd` documents a rename; one that
#    forwards is what keeps the old command working.
name='both old-name SKILL.md stubs forward $ARGUMENTS to /tdd'
problems=()
for stub in "${stubs[@]}"; do
  # The command a stub answers to is its own directory's name — derived, not written out
  # again, so the `stubs` list above stays the one place the two old names are spelled.
  old_name="$(basename "$(dirname "$stub")")"
  if [[ ! -f "$ROOT/$stub" ]]; then
    problems+=("want a stub at $stub, found none")
    continue
  fi
  got="$(frontmatter_name "$ROOT/$stub")"
  [[ "$got" == "$old_name" ]] ||
    problems+=("$stub frontmatter: want name '$old_name', got $(printf '%q' "$got")")
  body="$(skill_body "$ROOT/$stub")"
  case "$body" in
    */tdd*) ;;
    *) problems+=("$stub body never names /tdd, so it forwards nowhere") ;;
  esac
  case "$body" in
    *'$ARGUMENTS'*) ;;
    *) problems+=("$stub body never names \$ARGUMENTS, so it forwards no arguments") ;;
  esac
done
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
