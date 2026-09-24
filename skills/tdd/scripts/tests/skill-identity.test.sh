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
# left, the value. Used by case 1 for the skill's own name.
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
# Claude Code resolves a command by the directory it loads the skill from. Case 10 wants it
# bare, as the directory that must be gone, and case 5 wants it slash-led, as a user
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
#
# The generated-documentation tree is excluded by pathspec, and that exclusion is the whole
# of what either case says about it (#143). A sweep that entered it would be a development
# suite reading the page and its commentary, so a rewording there — or a page nobody had
# rebuilt yet — could fail `make test`, the command preflight reads its baseline off and
# every leaf runs (ADR 0016). Prose lagging behind code is `docs-owed.sh`'s reading and
# `docs-fresh`'s failure at a docs merge, not this suite's. `:!` is git's own spelling for
# "and not this path", so the exclusion holds for every caller of this helper.
swept=""
sweep() {
  local code
  swept="$(cd "$ROOT" && git grep --files-with-matches "$1" -e "$2" -- ':!docs')" && code=0 || code=$?
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

# 3. was "the walkthrough is generated from skills/tdd/scripts": it read the SCRIPTS_DIR
#    constant out of the page's two python entry points and the set of listings out of its
#    commentary, so that a generator left pointed at the skill's old home failed here. That
#    claim is the docs lane's (#143). Reading those three files from `make test` — the
#    command preflight reads its baseline off, that every Green leaf runs and that both
#    blind verifiers run — let an edit to the page's generator stop a TDD cycle on a red the
#    scripts did not cause, which is the coupling ADR 0016 rules out. It moved whole to
#    docs/tests/generator-inputs.test.sh (#146), which `make docs-test` globs; the numbers
#    below are left as they were, so the cases above still cite the right ones, and
#    no-docs-reads.test.sh is what keeps the read from coming back.

# 4. was "both old-name SKILL.md stubs forward $ARGUMENTS to /tdd": it read each stub's
#    frontmatter for its old name and its body for `/tdd` and `$ARGUMENTS`. The stubs were
#    never installed — Claude Code resolves a command from the directories symlinked into
#    ~/.claude/skills, and only skills/tdd is — so they forwarded nothing, and #412 deleted
#    them; case 10 pins their absence. The numbers are left as they were, as for case 3.

# The two old commands as a user types them: a slash, then the name each stub answers to.
old_cmds=()
for stub in "${stubs[@]}"; do
  old_cmds+=("/$(stub_name "$stub")")
done
# Those two names as one alternation, since every probe that looks for either wants both:
# case 5 anchors this to a "not part of a path" boundary to sweep the sources. Written once
# here so no probe re-lists the names — which is also what keeps this file out of its own
# results, the strings being assembled from `stubs` and never spelled anywhere.
old_cmd_alt="(${old_cmds[0]}|${old_cmds[1]})"
# An old name used as a COMMAND and not as a path: the alternation preceded by the "not part of
# a path" test — start of line, or a character that cannot be the tail of a path component.
# That boundary is what keeps `skills/solve-issue/SKILL.md` out of the two sweeps below and in
# case 2's, so naming a stub's file stays legal while telling a reader to invoke a command that
# no longer resolves to a procedure does not. Hoisted next to the alternation it is built from
# because case 5 matches on it, over the sources.
cmd_re="(^|[^[:alnum:]_/.-])$old_cmd_alt"

# 5. The prose followed the skill too. Same shape as case 2, for the same reason: stated as
#    an absence swept for across the whole repository rather than a list of files someone
#    has to remember to extend, so a stale instruction in a file this test never heard of
#    still counts. What it looks for is the COMMAND and not the path — a slash-led old name
#    whose slash does not continue a path — so that naming a stub's file, which the prose
#    describing the stubs has to do, stays legal, while telling a reader to invoke a command
#    that no longer resolves to a procedure does not.
name="no tracked file outside the two stubs names ${old_cmds[0]} or ${old_cmds[1]}"
problems=()
sweep -E "$cmd_re" || problems+=("git grep failed with exit $?")
while IFS= read -r f; do
  [[ -n "$f" ]] || continue
  exempt "$f" && continue
  # Quote the first offending line, trimmed: the case is about a file set, but the fix is
  # always a line, and finding it again by hand is the tedious half.
  where="$(cd "$ROOT" && head -1 < <(git grep -nE -e "$cmd_re" -- "$f") | cut -c1-100)"
  problems+=("$f still names an old command: $where")
done <<< "$swept"
report "$name"

# fold_bullets — markdown on stdin, one line per bullet and lowercased. A bullet is a `- ` in
# column one plus the indented lines continuing it, up to the next such line or a blank one;
# joining it onto one line is what lets a claim ask whether ONE bullet carries both halves of
# its pair, rather than two sentences that happen to share a word. Case is folded away last:
# the sentences are the writer's, and `Integer` must answer for `integer`. Both readers below
# want exactly this and differ only in what they feed it, so it is written once here.
fold_bullets() {
  awk '/^- / { if (rec != "") print rec; rec = $0; next }
       /^[[:space:]]*$/ { if (rec != "") print rec; rec = ""; next }
       rec != "" { rec = rec " " $0 }
       END { if (rec != "") print rec }' | tr '[:upper:]' '[:lower:]'
}

# inputs_text <skill-md> — the `## Inputs` section verbatim. The section is cut out because
# the words the cases below look for all occur again further down, so a file-wide read would
# answer "yes" for a section that still said only "the issue number".
inputs_text() {
  awk '/^## Inputs$/ { inside = 1; next }
       inside && /^## / { exit }
       inside' "$1"
}

# inputs_bullets <skill-md> — the bullets of that section alone, folded. The section is read
# both ways: as bullets, by case 6, for the three-way resolution; and unfolded, by
# `loop_md_path`, for the pointer — a filename is prose, not necessarily inside a bullet.
inputs_bullets() { inputs_text "$1" | fold_bullets; }

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

# loop_md_path <skill-md> — the repo-relative path of the sibling file `## Inputs` sends a
# scope to, empty if that section names none. Any `.md` path in the section other than a
# SKILL.md counts: the destination is what the criterion is about, not the words wrapped
# around it or what the file is called. A pointer carrying a slash is repo-relative; a bare
# filename sits beside the SKILL.md that names it — the two spellings a document can
# reasonably use for its own sibling. Asked by case 6, which pins that the pointer leads
# somewhere, and by case 7, which reads its bullets out of wherever it leads.
loop_md_path() {
  local p
  p="$(head -1 < <(inputs_text "$1" | grep -oE '[A-Za-z0-9_./-]+\.md' | grep -vE '(^|/)SKILL\.md$'))"
  [[ -n "$p" ]] || return 0
  case "$p" in
    */*) printf '%s\n' "$p" ;;
    *)   printf '%s\n' "$skill_dir/$p" ;;
  esac
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
#    elsewhere. First, the scope branch must have somewhere to send the reader, and that
#    somewhere is no longer this document: the loop is procedure only the scope branch ever
#    executes, and an integer argument takes *Procedure* and never comes back, so a loop
#    resident here bills every single-issue conductor ~1,676 tokens it will not read (#202).
#    So the pointer is pinned as the pair it has to be, since either half alone is a broken
#    skill — the loop has left $skill_md, AND `## Inputs` names a file that exists and holds
#    it. A pointer at nothing is not a destination: a scope that resolves to a failed Read is
#    a run that cannot start, so the pointer is followed here rather than merely counted, and
#    deleting it puts this case back in the red.
#
#    Second, the path the loop used to reach its sibling skill's scripts must be gone, since
#    a skill with no sibling cannot resolve it. Case 2 cannot see that path — it sweeps for
#    the `skills/`-led spelling, which the `../` one does not contain — so it is asked here,
#    of the one file that ever spelled it.
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
# The sibling path assembled rather than written out, as in case 2: the probe greps this
# skill's own document for the string, and spelling it here would make the suite's subject
# and its first offender the same file.
sibling_scripts="../$(basename "$old_skill_dir")/scripts"
grep -qF "$sibling_scripts" "$ROOT/$skill_md" &&
  problems+=("$skill_md still locates its scripts at $sibling_scripts, a sibling that is no longer there")
report "$name"

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
#    in what the skill tells the session to set. A document that names the scope and the
#    label in different breaths leaves the session to guess the colon.
#
#    Read out of the file case 6 pins the pointer to, not out of $skill_md: these three
#    bullets are the loop's own inputs, so they travel with it (#202), and asking $skill_md
#    for them after the move would be asking the one document that no longer says it. Read
#    out of the WHOLE of that file, too, with no section cut first as case 6 cuts one: the
#    criterion is that the derivation be written where the scope branch will read it, not
#    that it sit under some one heading, and each claim below pairs the scope with the label
#    spelling, so no unrelated bullet can answer for one.
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
  # Fail closed, as case 6 does: no readable loop file, or one with no bullets in it, means
  # not one claim below was tested, which must not read as three passes.
  problems+=("the loop file $skill_md Inputs points at could not be read for bullets — how a scope's label is derived was not tested")
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

# 8. was "the generated page names no old command outside the capability index": it read
#    the committed page, cut out the tag-derived index and swept the rest for either old
#    command, the way case 5 sweeps the sources, so that a rename not yet carried into the
#    page failed here — and it could not spell those names either, for the reason case 5's
#    own `old_cmd_alt` gives above. That
#    claim is the docs lane's (#143), for the reason case 3's note gives — and doubly so,
#    since what it asked for was that somebody had run `make docs`, which is the docs lane's
#    work by definition. Case 5 no longer needs its exemption as a result: its sweep does not
#    enter that tree at all.

# 9. Who pays for the loop, and what the scope branch still gets. Case 6 pins that the loop
#    left $skill_md and that `## Inputs` leads somewhere real; neither half says the move
#    saved a single-issue run anything, nor that a scope run still ends up in the same
#    procedure. Both are the criterion this case is about (#202).
#
#    The saving first: a `Read` of the loop file written anywhere a single-issue run passes
#    — a step of *Procedure*, a preamble, a "see also" — hands those ~1,676 tokens straight
#    back, and case 6 stays green while it happens, because the section it cuts is still
#    clean. So the loop file's name is pinned to `## Inputs` alone: that section is the one
#    place the argument has not yet been resolved, and every line naming it elsewhere is a
#    line an integer argument reaches. The offending line is quoted, as case 5 quotes its
#    own, because the fix is always a line.
#
#    Then what did not change: the single-issue procedure is still resident here — a move
#    that took *Procedure* with it would satisfy every probe above and leave the one command
#    unable to solve an issue — and the loop still delegates to it rather than restating it,
#    which is the whole of "a scope run reaches the same procedure it always did". A
#    restated copy would drift from this file silently, and the first symptom would be two
#    procedures disagreeing about a step.
name="only the scope branch is sent to the loop file, $skill_md keeps Procedure, and the loop delegates back to it"
problems=()
loop_md="$(loop_md_path "$ROOT/$skill_md")"
grep -qE '^#+ Procedure$' "$ROOT/$skill_md" ||
  problems+=("$skill_md no longer holds a 'Procedure' section, so the single-issue path did not stay put")
if [[ -z "$loop_md" || ! -f "$ROOT/$loop_md" ]]; then
  # Fail closed, as cases 6 and 7 do: with no readable loop file neither claim below was
  # tested, and that must not read as a pass.
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

# 10. The old names are gone, not forwarded (#412). The stubs case 4 pinned were never
#     installed — Claude Code resolves a command from the directories symlinked into
#     ~/.claude/skills, and only skills/tdd is — so they forwarded nothing. Stated as the
#     observable absence: neither old directory exists in the tree. Each is spelled through
#     `stubs` and `stub_name`, so this file still never writes an old home out in full.
name="neither old skill directory is left in the tree"
problems=()
for stub in "${stubs[@]}"; do
  old_dir="skills/$(stub_name "$stub")"
  [[ ! -e "$ROOT/$old_dir" ]] ||
    problems+=("want no $old_dir/, found one")
done
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
