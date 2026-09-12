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
#   `plain` — with the loop it now dispatches to living in the same document.
#   A scope's selection label is `ready-for-agent` for the scope `plain` and
#   `ready-for-agent:<scope>` for any other, with `VERI_LABEL` still overriding it.
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

# frontmatter_name <file> — the value of the first `name:` inside the leading `---` block,
# empty if the block or the field is missing. The frontmatter is the leading `---` block
# and only its first `name:` counts: the exit at the closing `---` stops a later `name:`
# in the prose from answering for it. sub() edits $0 and returns how many replacements it
# made, so it doubles as the "this line is the name field" test; print then emits what is
# left, the value. Used by case 1 for the skill's own name and by case 4 for each stub's —
# the same question asked of different files, so it is asked in one place.
frontmatter_name() {
  awk 'NR == 1 && $0 == "---" { inside = 1; next }
       inside && $0 == "---" { exit }
       inside && sub(/^name:[[:space:]]*/, "") { print; exit }' "$1"
}

# 1. Both halves of the skill's identity, as one criterion: the directory it lives in and
#    the name its frontmatter declares.
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

# The skill's former home, and the scripts directory inside it that the Makefile, the docs
# build and the demo fixtures used to point at. Assembled from two pieces on purpose: the
# probe below greps the whole repository for the joined string, so spelling it out here
# would make this file its own first offender.
old_skill_dir="skills/solve-issue"
old_scripts_dir="$old_skill_dir/scripts"
# The two files the move deliberately leaves behind under the old names, each a stub whose
# body forwards to /tdd. They are allowed to name the old home; nothing else is.
stubs=("$old_skill_dir/SKILL.md" "skills/solve-issues/SKILL.md")

# stub_name <stub-path> — the old name a stub answers to, which is its own directory's name:
# Claude Code resolves a command by the directory it loads the skill from. Case 4 wants it
# bare, to compare against the stub's frontmatter, and case 5 wants it slash-led, as a user
# types it; deriving both from here keeps `stubs` the one place either old name is spelled,
# which is what lets this file sweep the repository for strings it must not itself contain.
stub_name() { basename "$(dirname "$1")"; }

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

# sweep <git-grep-flag> <pattern> — the tracked files matching <pattern>, one per line, in the
# global `swept`. Tracked, via `git grep`, because the repository's content is what ships.
# Both absence cases below want the same thing and neither should re-derive it: run the grep,
# and tell "found nothing" apart from "the probe itself broke". git grep exits 1 for no
# matches, which is the pass those cases are after, and 2+ for a real failure — collapsing
# the two would turn a broken probe into a silent green. So 1 comes back from here as an
# empty list and a zero return, while 2+ comes back as that same non-zero, for the caller to
# turn into a problem. `swept` is a newline-joined string rather than an array because a
# caller reads it with `while read`, and an empty array under `set -u` is an error on the
# bash 3.2 this repo still targets.
swept=""
sweep() {
  local code
  swept="$(cd "$ROOT" && git grep --files-with-matches "$1" -e "$2")" && code=0 || code=$?
  if [[ "$code" -gt 1 ]]; then
    swept=""
    return "$code"
  fi
  return 0
}

# 2. The plumbing moved with the skill. Stated as the absence it has to produce rather than
#    as a list of files to check, so a path constant hiding somewhere this test never heard
#    of still counts: no tracked file names the old scripts directory except the exempt ones.
name="no tracked file outside the two stubs still names $old_scripts_dir"
problems=()
sweep --fixed-strings "$old_scripts_dir" || problems+=("git grep failed with exit $?")
while IFS= read -r f; do
  [[ -n "$f" ]] || continue
  exempt "$f" || problems+=("$f still names $old_scripts_dir")
done <<< "$swept"
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
#    its frontmatter has to still declare the OLD name, since that field is what Claude Code
#    resolves the old command by, and a stub renamed to `tdd` would answer to
#    nothing; and the body has to name both `/tdd` and `$ARGUMENTS` — the destination, and
#    the harness's own spelling for "the arguments this invocation carried", used that way
#    by every SKILL.md in this repo. A body naming only `/tdd` documents a rename; one that
#    forwards is what keeps the old command working.
name='both old-name SKILL.md stubs forward $ARGUMENTS to /tdd'
problems=()
for stub in "${stubs[@]}"; do
  old_name="$(stub_name "$stub")"
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

# The two old commands as a user types them: a slash, then the name each stub answers to.
old_cmds=()
for stub in "${stubs[@]}"; do
  old_cmds+=("/$(stub_name "$stub")")
done

# The one file that names the old commands without being a source of them: docs/walkthrough.html
# is generated, never hand-edited ("Never edit it by hand" — CLAUDE.md), and its prose comes
# from docs/wt/commentary.py, which this sweep does cover. Rewording the commentary is what
# fixes the page; `make docs` is what carries the wording into it, and that rebuild is a
# separate change from the rewrite. So the subject here is the source, not the artefact.
generated_page="docs/walkthrough.html"

# 5. The prose followed the skill too. Same shape as case 2, for the same reason: stated as
#    an absence swept for across the whole repository rather than a list of files someone
#    has to remember to extend, so a stale instruction in a file this test never heard of
#    still counts. What it looks for is the COMMAND and not the path — a slash-led old name
#    whose slash does not continue a path — so that naming a stub's file, which the prose
#    describing the stubs has to do, stays legal, while telling a reader to invoke a command
#    that no longer resolves to a procedure does not.
name="no tracked file outside the two stubs names ${old_cmds[0]} or ${old_cmds[1]}"
problems=()
# The leading group is the "not part of a path" test: start of line, or a character that
# cannot be the tail of a path component. It is what keeps `skills/solve-issue/SKILL.md`
# out of this case and in case 2's, and both old names in the alternation because the
# plural is a command in its own right, not an inflection of the singular.
cmd_re="(^|[^[:alnum:]_/.-])(${old_cmds[0]}|${old_cmds[1]})"
sweep -E "$cmd_re" || problems+=("git grep failed with exit $?")
while IFS= read -r f; do
  [[ -n "$f" ]] || continue
  exempt "$f" && continue
  [[ "$f" == "$generated_page" ]] && continue
  # Quote the first offending line, trimmed: the case is about a file set, but the fix is
  # always a line, and finding it again by hand is the tedious half.
  where="$(cd "$ROOT" && git grep -nE -e "$cmd_re" -- "$f" | head -1 | cut -c1-100)"
  problems+=("$f still names an old command: $where")
done <<< "$swept"
report "$name"

# inputs_bullets <skill-md> — the `## Inputs` section of a SKILL.md, one line per bullet and
# lowercased. Two transformations, each for a reason the case below depends on. The section
# is cut out first because the words this case looks for all occur again further down, in the
# loop the move folded in, so a file-wide read would answer "yes" for a section that still
# said only "the issue number". Then each bullet — a `- ` in column one, running to the next
# such line or to a blank one — is joined onto one line, because a claim wants to ask whether
# ONE bullet carries both what the user types and where it sends them. Case is folded away
# last: the sentences are the writer's, and `Integer` must answer for `integer`.
inputs_bullets() {
  awk '/^## Inputs$/ { inside = 1; next }
       inside && /^## / { exit }
       !inside { next }
       /^- / { if (rec != "") print rec; rec = $0; next }
       /^[[:space:]]*$/ { if (rec != "") print rec; rec = ""; next }
       rec != "" { rec = rec " " $0 }
       END { if (rec != "") print rec }' "$1" | tr '[:upper:]' '[:lower:]'
}

# claim <what one bullet must say> <regex>… — assert that a single line of the global
# `bullets` matches every <regex>, recording a problem naming <what> if none does. Each claim
# below is a pair — for case 6 the argument and the procedure it selects, for case 7 the scope
# and the label it derives — and a pair split across two bullets is not a derivation: it is
# two sentences that happen to share a word. `continue 2` leaves the regex loop and takes the
# next bullet, so a bullet matching some but not all of the pair is simply not the one. The
# probe and the sentence it fails with belong together: the claims differ only in that pair
# and in the sentence, so the surrounding "…: no bullet …" is written once here rather than
# at each of the six. Both `bullets` and `bullets_from` — the part of the document those
# bullets were read out of, which names the failure — are the caller's to set, so the two
# cases differ in the globals they set and not in a helper each.
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

# 6. What the one command does with its argument. The move left a single skill where there
#    were two, so the question that used to be "which command did the user type" is now "what
#    does this one's argument say", and the answer is a three-way resolution: an integer is
#    the single-issue procedure, any other word is a scope to drain, and no argument at all
#    is the scope `plain`. It is stated in prose because prose is the whole of a SKILL.md —
#    the session reads this section before it does anything else, so an Inputs section that
#    still admits only an issue number is a `/tdd docs` that stops and asks for one.
#
#    The two structural halves of the same criterion ride along, and neither is covered
#    elsewhere: the scope branch must have somewhere to send the reader, so the loop has to
#    be a section of THIS document; and the path the loop used to reach its sibling skill's
#    scripts must be gone, since a skill with no sibling cannot resolve it. Case 2 cannot
#    see that path — it sweeps for the `skills/`-led spelling, which the `../` one does not
#    contain — so it is asked here, of the one file that ever spelled it.
name="$skill_md resolves its argument: an integer is one issue, any other word a scope, bare is plain"
problems=()
bullets="$(inputs_bullets "$ROOT/$skill_md")"
bullets_from="$skill_md Inputs"
if [[ -z "$bullets" ]]; then
  # Fail closed: no bullets means the section was renamed or emptied and not one claim below
  # was tested, which must not read as three passes.
  problems+=("$skill_md has no bullets under '## Inputs' — how the argument resolves could not be read")
else
  claim 'sends an integer argument to the single-issue procedure' \
    'integer' 'single|one issue|procedure'
  claim 'reads a non-integer argument as a scope to drain' \
    'scope' 'drain|loop'
  claim 'makes a bare invocation the scope plain' \
    'plain' 'bare|no argument|without an argument|omit|default|empty'
fi
grep -qE '^#+ .*[Ll]oop' "$ROOT/$skill_md" ||
  problems+=("$skill_md has no loop section, so a scope argument resolves to nothing")
# The sibling path assembled rather than written out, as in case 2: the probe greps this
# skill's own document for the string, and spelling it here would make the suite's subject
# and its first offender the same file.
sibling_scripts="../$(basename "$old_skill_dir")/scripts"
grep -qF "$sibling_scripts" "$ROOT/$skill_md" &&
  problems+=("$skill_md still locates its scripts at $sibling_scripts, a sibling that is no longer there")
report "$name"

# md_bullets <skill-md> — every bullet in the document, one per line and lowercased, a
# bullet being a `- ` in column one plus the indented lines continuing it up to the next
# such line or a blank one. Case 6 reads only the `## Inputs` section because the words it
# looks for recur further down; case 7 reads the whole document on purpose — its criterion
# is that the document derive the label from the scope, not that it say so under one
# heading, and each of its claims pairs the scope with the label spelling, so no unrelated
# bullet can answer for one.
md_bullets() {
  awk '/^- / { if (rec != "") print rec; rec = $0; next }
       /^[[:space:]]*$/ { if (rec != "") print rec; rec = ""; next }
       rec != "" { rec = rec " " $0 }
       END { if (rec != "") print rec }' "$1" | tr '[:upper:]' '[:lower:]'
}

# 7. Which label a scope selects on. Case 6 pins that a non-integer argument is a scope; a
#    scope is only a pool once the document says which label names it, and the mapping is
#    not the identity: the scope `plain` selects on the bare `ready-for-agent` label —
#    every issue opted in today carries that, so the default invocation must keep draining
#    it — while any other scope selects on `ready-for-agent:<scope>`, which is the
#    namespacing that lets `/tdd docs` and `/tdd scripts` draw from disjoint pools.
#    `VERI_LABEL` stays what it was, an override of whatever the scope derived, because a
#    launcher naming a pool that no scope word spells must still be able to.
#
#    Stated in prose and read here as prose, like case 6: `solvable-issues.sh` takes the
#    label from the environment and knows nothing of scopes, so the derivation exists only
#    in what this document tells the session to set. A document that names the scope and
#    the label in different breaths leaves the session to guess the colon.
name="$skill_md derives a scope's label: ready-for-agent for plain, ready-for-agent:<scope> otherwise, VERI_LABEL overriding"
problems=()
bullets="$(md_bullets "$ROOT/$skill_md")"
bullets_from="$skill_md"
if [[ -z "$bullets" ]]; then
  # Fail closed, as case 6 does: no bullets means the document's shape changed and not one
  # claim below was tested, which must not read as three passes.
  problems+=("$skill_md has no bullets at all — how a scope's label is derived could not be read")
else
  # `plain` bounded by non-alphanumerics so `explain` and `plain text` cannot answer for the
  # scope's name; the other two are distinctive enough as substrings, the colon in
  # `ready-for-agent:` being the whole of what claim two is about.
  claim 'gives the scope plain the bare ready-for-agent label' \
    '(^|[^[:alnum:]])plain([^[:alnum:]]|$)' 'ready-for-agent'
  claim 'gives any other scope the label ready-for-agent:<scope>' \
    'scope' 'ready-for-agent:'
  claim 'keeps VERI_LABEL as the override of the derived label' \
    'veri_label' 'overrid|precedence|wins'
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
