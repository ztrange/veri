#!/usr/bin/env bash
# Tests for scripts/build-develop-prompt.sh — see that script's header for why the
# developer's prompt is a versioned template rather than prose improvised each cycle.
# These tests hold it to the half of that bargain a test can observe: what the assembled
# prompt must carry.
#
# Contract under test, red phase:
#   build-develop-prompt.sh red <spec-file> <step-text> <test-cmd>
#   exits 0 and prints a prompt carrying the spec, the step criterion and the test command
#   verbatim, plus the `AGAINST_UNMODIFIED` report line — the protocol token the conductor
#   greps for to route a passing red test to verify-pin (SKILL.md, Red step). It also
#   carries the `UNTESTABLE` outcome (issue #331) and the rules a valid test holds to —
#   behaviour over mechanism (a process/fork count or a timing belongs to `make profile`,
#   never an assertion, except a call count the criterion itself names, pinned with an
#   in-process spy rather than a `PATH` shim counting real processes), lightweight
#   (~100ms, costly dependencies replaced), and self-contained (never another suite, never
#   its own again) — so a criterion only pinnable by breaking one of those is reported
#   untestable rather than forced into a costly or implementation-pinning test.
#
# Contract under test, green phase:
#   build-develop-prompt.sh green <spec-file> <step-text> <test-cmd> <test-path> <target> <fast-cmd>
#   exits 0 and prints a prompt naming the test the implementation must satisfy — its path
#   and its case name — and forbidding any edit to it, the rule that keeps "make it green"
#   from degenerating into "weaken the test".
#
# Contract under test, refactor phase:
#   build-develop-prompt.sh refactor <spec-file> <step-text> <test-cmd> <touched-files>
#   exits 0 and prints a prompt naming the files this cycle touched — the bounds of the
#   tidy-up — carrying the rule that bounds it further (no generality no test demands), and
#   requiring the `RESULT:` / `CANDIDATES:` / `NEW_STEP:` footer: the first the conductor
#   branches on, the second the backlog it lists when the loop was stopped by the budget
#   rather than by a leaf finding nothing left, the third the steps the plan gains for
#   overfit code the leaf must not generalize itself.
#
# Contract under test, the reader of that footer:
#   SKILL.md's `#### Refactor loop` section — no script assembles the `### 🛠️ Refactor`
#   comment, so the procedure's prose is the contract — tells the two stop conditions apart
#   and, when the budget ended the loop, says how many candidates were left and lists them
#   from the leaf's `CANDIDATES:` lines. Pinned here beside the prompt that asks for them.
#
# Contract under test, revise phase:
#   build-develop-prompt.sh revise <phase> <spec-file> <step-text> <test-cmd> <reason-file>
#   exits 0 and prints a prompt carrying the verifier's rejection reason verbatim — the
#   fresh leaf never saw the rejected attempt, so the reason text is the whole of what it
#   has to address — and offering `IMPOSSIBLE`, the outcome that lets it say the step
#   cannot be met rather than fake a pass.
#
# Contract under test, refusals:
#   an unknown phase, a missing positional, or a missing template, spec or reason file, exits
#   2 with a diagnostic and prints no prompt — the verifier builder's contract. Exit 2 is
#   veri's "no answer could be obtained", and a half-assembled prompt on stdout would read
#   to the conductor as a whole one.
#
# Run: scripts/tests/build-develop-prompt.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
BUILD="$HERE/../build-develop-prompt.sh"
pass=0 fail=0
ok() { pass=$((pass + 1)); }
no() { fail=$((fail + 1)); echo "FAIL - $1"; }

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

# Distinctive strings throughout, so no assertion below can match on boilerplate prose
# that the template happens to contain. The spec also carries &, \, / and {} — the
# characters a naive sed substitution would mangle.
cat > "$work/spec.md" <<'SPEC'
zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux" — see {ref}\n done.
SPEC
step_text='QWIXTLE: a seed ending in a newline gains the block and reports added'
test_cmd='make test ZORBLAT=1 -- --only "frob & nitz/quux"'

# 1. the red prompt carries its three inputs verbatim and the AGAINST_UNMODIFIED line
red="$("$BUILD" red "$work/spec.md" "$step_text" "$test_cmd" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] \
  && [[ "$red" == *'zorblat("Frob & Nitz/Quux")'* ]] \
  && [[ "$red" == *"$step_text"* ]] \
  && [[ "$red" == *"$test_cmd"* ]] \
  && [[ "$red" == *'AGAINST_UNMODIFIED'* ]] \
  && ok || no "develop-red carries spec + step + test command verbatim and the AGAINST_UNMODIFIED report line (exit $code)"

# 2. the green prompt names the test it must satisfy — path and case name — and forbids
#    editing it
test_path='tests/zorblat/test_frob & nitz.sh'
target='qwixtle seeds a newline-terminated block'
green="$("$BUILD" green "$work/spec.md" "$step_text" "$test_cmd" "$test_path" "$target" "make unit" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] \
  && [[ "$green" == *"$test_path"* ]] \
  && [[ "$green" == *"$target"* ]] \
  && grep -qiE "(do not|don't|never) (modify|change|edit|touch|weaken).{0,40}test|test.{0,40}(must not|may not) be (modified|changed|edited|touched)" <<<"$green" \
  && ok || no "develop-green names the test path + target test and forbids modifying the test (exit $code)"

# 3. the refactor prompt names the files the cycle touched, carries the rule that bounds
#    the tidy-up (no generality no test demands) and requires the RESULT: footer. The
#    footer's other two lines are cases 8 (`CANDIDATES:`) and 38 (`FLAGS:`), each of
#    which carries why it pins what it pins.
touched='scripts/zorblat.sh, tests/zorblat/test_frob & nitz.sh'
refactor="$("$BUILD" refactor "$work/spec.md" "$step_text" "$test_cmd" "$touched" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] \
  && [[ "$refactor" == *"$touched"* ]] \
  && grep -qiE '(no|not|never|without)[^.]{0,80}(generality|generali[sz]ation|abstraction)' <<<"$refactor" \
  && grep -q 'RESULT:' <<<"$refactor" \
  && ok || no "develop-refactor carries the touched-files list + the no-untested-generality rule and the RESULT: footer (exit $code)"

# 4. the revise prompt carries the verifier's rejection reason verbatim and offers the
#    IMPOSSIBLE outcome
# Spelled once, and asserted on by every case that builds a prompt from this file — case
# 35 as well as this one. A second copy of it is a copy whose backslash has to be escaped
# again for the pattern side of `==`, which is where the assertion that silently matches
# nothing hides.
reason_text='REJECT: the case asserts on zorblat()'"'"'s log line, not its return value — & {tricky}\chars.'
printf '%s\n' "$reason_text" > "$work/reason.md"
revise="$("$BUILD" revise red "$work/spec.md" "$step_text" "$test_cmd" "$work/reason.md" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] \
  && [[ "$revise" == *"$reason_text"* ]] \
  && [[ "$revise" == *'IMPOSSIBLE'* ]] \
  && ok || no "develop-revise carries the rejection reason verbatim and the IMPOSSIBLE outcome (exit $code)"

# 5. every way of not having what it takes to build a prompt is refused identically:
#    exit 2, a diagnostic on stderr, nothing on stdout. The missing-template case runs a
#    copy of the script from a directory with no prompts/ beside it — the template path is
#    derived from the phase name, so an unreadable template is not otherwise reachable.
mkdir -p "$work/no-prompts"
cp "$BUILD" "$work/no-prompts/build-develop-prompt.sh"

refusal_bad=""
refuses() {  # <label> <script> <args...> — records why, if this was not a clean refusal
  local label="$1" bin="$2"; shift 2
  local out code err="$work/err.txt"
  out="$("$bin" "$@" 2>"$err")"; code=$?
  [[ "$code" -eq 2 ]] || refusal_bad="$refusal_bad; $label exited $code, want 2"
  [[ -z "$out" ]] || refusal_bad="$refusal_bad; $label printed a prompt"
  [[ -s "$err" ]] || refusal_bad="$refusal_bad; $label gave no diagnostic"
}

refuses "unknown phase"           "$BUILD" bogus "$work/spec.md" "$step_text" "$test_cmd"
refuses "missing spec"            "$BUILD" red "$work/absent.md" "$step_text" "$test_cmd"
refuses "missing reason"          "$BUILD" revise red "$work/spec.md" "$step_text" "$test_cmd" "$work/absent.md"
refuses "missing template"        "$work/no-prompts/build-develop-prompt.sh" red "$work/spec.md" "$step_text" "$test_cmd"
# `revise` names a second phase — the one being redone — and it gets the same check the
# first one gets. Otherwise any word is accepted and interpolated into the prompt, and the
# leaf is told it is redoing a phase that does not exist. Every other argument below is
# real, so the only thing wrong with this call is that phase.
refuses "unknown phase to revise" "$BUILD" revise bogus "$work/spec.md" "$step_text" "$test_cmd" "$work/reason.md"
# A known phase short of its later positionals is a bad-arguments case too, so it is refused
# the same way. Left to itself the shell would answer this one differently: a `${N:?}`
# expansion aborts with status 1, which reads to the conductor as a leaf that ran and failed
# rather than a call it could not make sense of. `red` needs a step and a test command past
# the spec file, and neither is here.
refuses "missing positionals"     "$BUILD" red "$work/spec.md"

[[ -z "$refusal_bad" ]] \
  && ok || no "an unknown phase, a missing positional or a missing template/spec/reason file exits 2 with a diagnostic and prints no prompt (${refusal_bad#; })"

# 6. that refusal does not depend on the later positionals being supplied: a bad phase on
#    its own is still a bad-arguments case, which is exit 2. The shell's own `${N:?}` abort
#    exits 1, so a missing-argument check reached first would answer the wrong question.
bare_err="$work/bare-unknown-phase.err"
bare_out="$("$BUILD" bogus 2>"$bare_err")"; code=$?
[[ "$code" -eq 2 ]] \
  && [[ -z "$bare_out" ]] \
  && grep -q 'bogus' "$bare_err" \
  && ok || no "an unknown phase with no further arguments exits 2, names the phase on stderr and prints no prompt (exit $code, stderr: $(tr '\n' ' ' < "$bare_err"))"

# 7. called with nothing at all — the emptiest bad-arguments case there is, and the one the
#    shell answers soonest: `${1:?usage...}` aborts with status 1 before any check of ours
#    runs. A caller who passed no phase made no call the conductor can read as a negative
#    answer, so this is exit 2 like every other refusal.
none_err="$work/no-args.err"
none_out="$("$BUILD" 2>"$none_err")"; code=$?
[[ "$code" -eq 2 ]] \
  && [[ -z "$none_out" ]] \
  && [[ -s "$none_err" ]] \
  && ok || no "no arguments at all exits 2 with a usage diagnostic on stderr and prints no prompt (exit $code, stderr: $(tr '\n' ' ' < "$none_err"))"

# 8. the refactor prompt asks for one more report line than case 3 pins: the candidates the
#    leaf still sees after applying its transform (issue #106). A leaf applies one transform
#    and stops, so the loop's second stop condition — the budget — leaves work on the floor
#    with nothing saying what it was; that line is the backlog the conductor's `### 🛠️
#    Refactor` comment lists, and a later repo-wide refactor capability reads. One criterion
#    with three faces, so one case: the footer carries a `CANDIDATES:` line of its own —
#    the protocol token, at the start of a line like `RESULT:` and `NEW_STEP:`, because the
#    conductor greps for it — the candidates go **one per line**, so N of them can be
#    counted and listed rather than parsed out of a sentence, and the line says `none` when
#    the leaf sees nothing left, which is what distinguishes a clean stop from a truncated
#    one. `problems` says which face broke. The prompt it reads is case 3's: same phase,
#    same arguments, so there is one invocation and case 3 owns the exit-0 check on it.
problems=""
grep -qE '^CANDIDATES:' <<<"$refactor" || problems="$problems; no CANDIDATES: report line"
grep -qiE 'one[^.]{0,20}per line' <<<"$refactor" || problems="$problems; does not ask for one candidate per line"
grep -qiE '^CANDIDATES:.*none' <<<"$refactor" || problems="$problems; the CANDIDATES: line does not offer none"
[[ -z "$problems" ]] \
  && ok || no "develop-refactor requires a CANDIDATES: report line — the candidates still seen, one per line, or none (${problems#; })"

# 9. the consumer half of case 8's contract (issue #106). Case 8 pins that the prompt asks
#    for the `CANDIDATES:` line; a footer nothing reads is dead protocol, and the reader is
#    the conductor's procedure — so the two halves are pinned in one file, the producer above
#    and the consumer here. The narration has to do three things the loop's two stop
#    conditions make distinct: name both of them, so a step that ran dry is not reported as a
#    step that ran out of money; say HOW MANY candidates the budget left behind; and LIST
#    them, out of the leaf's `CANDIDATES:` lines, since the list is the backlog and a count
#    with no items is not one.
#
#    Read as prose because prose is all there is: no script assembles this comment — the
#    conductor writes it from what it read — so the procedure's own words are the whole of
#    the contract, the way SKILL.md's launcher prose is for wait-leaf.sh (wait-leaf.test.sh).
#    The `#### Refactor loop` section is cut out first and its newlines folded to spaces: both
#    `nothing left to tidy` and `budget` recur elsewhere in the document, so a file-wide read
#    would answer yes for a section that never mentioned either, and a claim that wraps across
#    two lines is still one sentence to the proximity probes. Fails closed — an empty cut means
#    the heading moved and nothing below was tested, which must not read as a pass.
SKILL="$HERE/../../SKILL.md"
narration="$(awk '/^#### Refactor loop/ { inside = 1; next }
                  inside && /^#{1,6} / { exit }
                  inside' "$SKILL" | tr '\n' ' ')"

# One claim, one miss: record the complaint unless the narration matches. Same shape as
# `doc_claims` in solvable-issues.test.sh, and for the same reason — what it collapses is the
# accumulator, so five probes cannot drift into reporting misses in five shapes, while the
# grep arguments stay at the call site, where the difference between a literal protocol token
# and a loosely-matched sentence is the point. `-e` because a pattern is data, not a flag.
narrates() {  # narrates <complaint> <grep argument…>
  local complaint="$1"; shift
  grep -q "$@" <<<"$narration" || problems="$problems; $complaint"
}

problems=""
if [[ -z "$narration" ]]; then
  problems="$problems; no '#### Refactor loop' section in SKILL.md — the narration could not be read"
else
  narrates "the narration never names the nothing-left-to-tidy stop" \
    -i -e 'nothing left to tidy'
  narrates "the narration never names the budget stop" \
    -i -e 'budget'
  # The protocol token, spelled as the leaf spells it, so the conductor is told where the
  # leftovers come from rather than left to summarise the transcript.
  narrates "the narration never names the leaf's CANDIDATES: line" \
    -e 'CANDIDATES:'
  # A listing verb beside the candidates, in either order, and within one sentence of them.
  narrates "the narration does not say the comment lists those candidates" \
    -iE -e '(list|lists|listing|enumerate)[^.]{0,80}candidate|candidate[^.]{0,80}(list|lists|listing|enumerate)'
  # The count — `N left`, `how many candidates`, any wording that quantifies what was left.
  # A bare `n` only counts when the next word is `candidates` or `left`, so the
  # `nothing left to tidy` already there cannot answer for it.
  narrates "the narration does not say how many candidates the budget left" \
    -iE -e '(how many|number of|count of|(^|[^[:alnum:]])n)[[:space:]]+(candidates?|left)'
fi
[[ -z "$problems" ]] \
  && ok || no "SKILL.md's Refactor narration tells nothing-left-to-tidy from stopped-by-budget and lists the N candidates from the leaf's CANDIDATES: lines (${problems#; })"

# 10. the triangulating case for case 9's `CANDIDATES:` probe (issue #106). Case 9 reads the
#     whole `#### Refactor loop` section, and `CANDIDATES:` occurs in it twice: sub-step 1 names
#     the line when it says what a leaf's report ends with, and the narration bullet names it as
#     where its list is taken from. So sub-step 1 answers case 9's probe on its own — the
#     narration could stop citing the leaf's own line, leaving the conductor to summarise the
#     transcript instead of copying `CANDIDATES:` verbatim, and case 9 would stay green. This
#     case reads the narration bullet ALONE — from its `3. ` to the end of the section, so
#     sub-steps 1 and 2 are outside the cut — and so it fails exactly where case 9 cannot: the
#     bullet stops naming `CANDIDATES:` while sub-step 1 still does. Fails closed on an empty
#     cut for case 9's reason: a moved heading or a renumbered bullet means nothing below was
#     read, which must not answer yes.
bullet="$(awk '/^#### Refactor loop/ { inside = 1; next }
               inside && /^#{1,6} / { exit }
               inside && /^3\. / { narration = 1 }
               inside && narration' "$SKILL" | tr '\n' ' ')"

problems=""
if [[ -z "$bullet" ]]; then
  problems="no '3.' bullet under '#### Refactor loop' — the narration bullet could not be read"
elif ! grep -q -e 'CANDIDATES:' <<<"$bullet"; then
  problems="the narration bullet never names CANDIDATES:, so only sub-step 1 does"
fi
[[ -z "$problems" ]] \
  && ok || no "SKILL.md's Refactor narration bullet names the leaf's CANDIDATES: line itself, not merely somewhere in the section ($problems)"

# 11. what the red leaf is told to RUN (issue #144). Case 1 pins that the prompt carries the
#     test command; this case pins that running the test command is no longer what Red asks
#     for by default. Red answers one question — does this one new case fail against
#     unmodified code — and the full suite is the most expensive way to ask it: 25 runs across
#     12 leaves, 30 of 358 leaf-minutes, in the 2026-09-13 overnight run. So the prompt names
#     the suite that holds the new case instead, says not to run the full one, and keeps the
#     test command as the fallback for a repository with no way to run a suite on its own —
#     with the leaf saying so in its report, since a fallback nobody can see is indistinguish-
#     able from a leaf that ignored the instruction. Four faces of one criterion, so one case.
#
#     The prompt read is case 1's — same phase, same arguments, so there is one invocation and
#     case 1 owns the exit-0 check on it.
#     Two shapes these probes must avoid. A branch carries at most ONE `[^.]{0,N}`: BSD grep
#     backtracks, and two bounded repeats either side of an alternation take minutes on a
#     one-line input — a hang that would only appear once the prompt matches. And the first
#     probe keys on `holds`/`contains` rather than any `suite … case` proximity, because
#     sub-step 1 already says "the existing suite the case belongs in": what changes here is
#     what the leaf is told to RUN, not that a suite is mentioned.
#
# One claim, one miss — `narrates` above, pointed at a prompt instead of the narration, and
# collapsing the accumulator for the same reason: probes cannot then drift into reporting
# their misses in as many shapes, while the patterns stay at the call site, where the comment
# above reasons about them. Which prompt is an argument, since case 12 below asks the same of
# develop-green's. The fold to one line is the helper's job rather than each caller's, and is
# there for case 9's reason: a prompt is markdown wrapped at ~85 columns, so any claim long
# enough to be worth probing for spans two lines, and grep matches within one. `-e` because a
# pattern is data, not a flag.
prompt_has() {  # prompt_has <prompt> <grep argument…> — the match itself, folded to one line
  local prompt="$1"; shift
  grep -q "$@" <<<"$(tr '\n' ' ' <<<"$prompt")"
}

prompt_says() {  # prompt_says <prompt> <complaint> <grep argument…>
  local prompt="$1" complaint="$2"; shift 2
  prompt_has "$prompt" "$@" || problems="$problems; $complaint"
}

# The same probe read the other way, for a claim a prompt must NOT make — case 36's
# negative half, where the paragraph conditional on a `## Bug` section must be absent from
# the prompt built from a spec without one. It shares `prompt_has` rather than repeating the
# fold and the grep: two copies of the probe is where the one that folds differently hides,
# and a negative assertion that quietly matches nothing because its input was never folded
# is green for the wrong reason. `return 0` because the miss is recorded in `problems`, not
# in the function's status, and a failed `grep` is this one's success.
prompt_lacks() {  # prompt_lacks <prompt> <complaint> <grep argument…> — prompt_says inverted
  local prompt="$1" complaint="$2"; shift 2
  ! prompt_has "$prompt" "$@" || problems="$problems; $complaint"
  return 0
}

# The other half of what cases 14–16 share: the roster, and the verdict reached from it. Each
# of those asks one claim of all four built prompts and reports one accumulated miss list, so
# which phases "every developer prompt" means lives here rather than once per case — a fifth
# phase is one edit, not three — and so does the shape of the answer: green when nothing
# accumulated, otherwise the case's own headline followed by every miss. The accumulator is a
# `local`, which bash's dynamic scoping still puts in reach of the `prompt_says` calls two
# frames down; a case that inherited the previous case's misses would fail naming the wrong
# claim, and now cannot see them to inherit. Cases 11–13 probe a single prompt each and keep
# their own `problems=""`. Same helper as build-verify-prompt.test.sh's, over this file's
# four phases rather than that one's.
every_phase() {  # every_phase <name of a check function taking <phase label> <prompt>> <headline>
  local check="$1" headline="$2" problems=""
  "$check" red "$red"; "$check" green "$green"; "$check" refactor "$refactor"; "$check" revise "$revise"
  [[ -z "$problems" ]] && ok || no "$headline (${problems#; })"
}

# The third thing several cases share, and the only one whose subject is a pattern rather than
# a roster. A claim about the refactor prompt usually reads as naturally backwards as forwards
# — "apply only a structural transform" against "a structural transform is the only one to
# apply" — so it has to be probed both ways round, and under the grep constraint `prompt_says`
# reasons about, one bounded `[^.]{0,N}` per alternation branch, that means spelling each half
# and the bound once per direction. Cases 16, 19 and 20 all want it, so the alternation is built
# here and each caller names only its two halves and the gap between them. Spelled out per
# probe, the only thing keeping the two copies in step is the eye that reads them: case 16
# records exactly that drift going unnoticed, a bare `comment` the forward branch accepted and
# the reversed one did not. Which prompt is an argument, since case 20 asks this of a prompt
# built with a budget in its environment rather than of case 3's.
says_both_ways() {  # says_both_ways <prompt> <complaint> <gap> <pattern> <pattern>
  local prompt="$1" complaint="$2" gap="$3" a="$4" b="$5"
  prompt_says "$prompt" "$complaint" -iE -e "$a[^.]{0,$gap}$b|$b[^.]{0,$gap}$a"
}

problems=""
prompt_says "$red" "never says to run the suite that holds the new case" \
  -iE -e 'suite (that |which )?(holds|contains|holding|containing)[^.]{0,40}case'
prompt_says "$red" "never says NOT to run the full suite" \
  -iE -e "(not|rather than|instead of|no need to|never|don't|do not)[^.]{0,40}(full|whole|entire) suite"
prompt_says "$red" "no fallback for a repository that cannot run one suite" \
  -iE -e '(cannot|can.t|no way to|unable to|has no way)[^.]{0,60}(suite|file)'
prompt_says "$red" "does not ask the leaf to say so in its report" \
  -iE -e '(say|says|saying|state|states|note|report) (so|it|this|that)[^.]{0,30}report'
[[ -z "$problems" ]] \
  && ok || no "develop-red says to run the suite holding the new case, not the full suite, falling back to the test command and saying so in the report (${problems#; })"

# 12. how often the green leaf is told to run the full suite (issue #144). Case 2 pins WHICH
#     test the green leaf must satisfy; this case pins what it spends getting there. Green is
#     where the full-suite guarantee lives — a pass bought with a broken sibling test is not a
#     pass — so unlike Red the full run cannot go away here. What can go is running it on
#     every iteration: 12 runs across 11 leaves, 13 of 358 leaf-minutes, in the 2026-09-13
#     overnight run, for a question only the last of those runs answers. So the prompt sends
#     the leaf's iterations to the suite that holds the target case, and spends the full suite
#     exactly once, immediately before the `SUITE:` line that reports it — the one place the
#     guarantee is actually read. Three faces of one criterion, so one case.
#
#     Built the way case 11 builds Red's, under the constraint reasoned about there: every
#     alternation branch carries at most ONE `[^.]{0,N}`. The prompt read is case 2's: same
#     phase, same arguments, so there is one invocation and case 2 owns the exit-0 check on it.
problems=""
prompt_says "$green" "never says to iterate on the suite that holds the target case" \
  -iE -e 'iterat[^.]{0,60}suite|suite[^.]{0,60}iterat'
prompt_says "$green" "never says the full suite is run exactly once" \
  -iE -e '(full|whole|entire) suite[^.]{0,40}once|once[^.]{0,40}(full|whole|entire) suite'
# Placed against the report line, not merely mentioned: `SUITE:` is the protocol token the
# conductor greps for, so a prompt that says "once" without saying when leaves the leaf free
# to spend it first and iterate afterwards.
prompt_says "$green" "does not put that one run immediately before the SUITE: report line" \
  -iE -e 'before[^.]{0,60}SUITE:'
[[ -z "$problems" ]] \
  && ok || no "develop-green says to iterate on the target case's suite and run the full suite exactly once, immediately before the SUITE: report line (${problems#; })"

# 13. what the refactor leaf is told to RUN after its transform (issue #144). Case 3 pins the
#     bounds of the tidy-up; this case pins what checking it costs. Refactor runs the suite more
#     than any other phase: `VERI_REFACTOR_BUDGET` defaults to 5, so one step can run the full
#     suite six times back to back — 75 runs across 55 leaves, 84 of 358 leaf-minutes in the
#     2026-09-13 overnight run, the biggest single item in it. So the transform is checked
#     against the suites covering the files it touched, and the full run is spent once, at
#     verify-refactor, on the settled result. That buys something real with something real, so
#     the prompt has to state the trade rather than bury it: a break in a suite nobody touched
#     now surfaces at verify-refactor — a REJECT the revise loop answers — instead of at the
#     transform that caused it. Three faces of one criterion, so one case.
#
#     Built the way case 11 builds Red's, under the grep constraints reasoned about there. The
#     prompt read is case 3's: same phase, same arguments, so there is one invocation and case 3
#     owns the exit-0 check on it.
problems=""
prompt_says "$refactor" "never says to run the suites covering the touched files" \
  -iE -e 'suites?[^.]{0,40}cover|cover[^.]{0,40}suites?'
prompt_says "$refactor" "never says NOT to run the full suite" \
  -iE -e "(not|rather than|instead of|no need to|never|don't|do not)[^.]{0,40}(full|whole|entire) suite"
prompt_says "$refactor" "does not name verify-refactor as where the full suite runs" \
  -iE -e 'verify-refactor[^.]{0,60}(full|whole|entire) suite|(full|whole|entire) suite[^.]{0,60}verify-refactor'
# The trade-off itself, not just the saving: what a leaf is no longer told to check is a
# regression it can no longer attribute, and a prompt that omits that reads as a free win.
prompt_says "$refactor" "does not state that a break in an untouched suite surfaces there instead" \
  -iE -e '(untouched|nobody touched|no one touched|nothing touched)[^.]{0,80}(surface|shows up|appears|caught)|(surface|shows up|appears|caught)[^.]{0,80}(untouched|nobody touched|no one touched)'
[[ -z "$problems" ]] \
  && ok || no "develop-refactor says to run the suites covering the touched files rather than the full suite, names verify-refactor as where the full suite runs and states the untouched-suite trade-off (${problems#; })"

# 14. HOW a developer leaf runs whichever suite cases 11–13 sent it to (issue #144). Those
#     cases pin which command each phase spends; this one pins that the leaf waits for it. A
#     #137 refactor leaf reported with its `make docs-test` still running in the background,
#     so the conductor read a report the suite had not answered yet and re-ran it — ~5 min
#     spent twice for one result. Backgrounding is exactly the shortcut the cheaper runs of
#     cases 11–13 make tempting, so the rule holds in **every** phase and is asked of every
#     built developer prompt: red, green, refactor and revise. Each is its own miss, so a
#     template that drops the sentence is named rather than covered for by the other three.
#
#     Built the way case 11 builds Red's, under the grep constraint reasoned about there:
#     one bounded `[^.]{0,N}` per branch. The prompts read are cases 1–4's — same phases,
#     same arguments, so there is one invocation each and those cases own the exit-0 checks.
#     `only after` rather than any report/exit proximity, because `git diff --exit-code`
#     already sits a few words from "report" in develop-red: a loose probe would answer yes
#     for a prompt that never mentions waiting.
demands_foreground() {  # demands_foreground <phase label> <prompt>
  local label="$1" prompt="$2"
  prompt_says "$prompt" "develop-$label never says to run test commands in the foreground" \
    -i -e 'foreground'
  prompt_says "$prompt" "develop-$label never says to report only after the test command has exited" \
    -iE -e '(only after|not until|never before)[^.]{0,60}(exit|exits|exited|finish)'
}

every_phase demands_foreground \
  "every built developer prompt says to run test commands in the foreground and report only after they exit"

# 15. WHICH act rule 3 forbids (issue #162). Case 14 pins that every developer prompt asks
#     for a foreground run and a report written only after it exits; this case pins that the
#     rule names **ending the turn** as the forbidden act, not only writing the report during
#     the run. The gap is not academic: #137's second refactor leaf of step 4 ended its turn
#     "waiting for the suite" with no footer at all — `c66b8e0`, the commit that landed rule
#     3, is an ancestor of that run's plan commit — so it broke nothing the old wording said
#     while costing the conductor a hand-run suite anyway. A leaf that writes no report never
#     "writes its report while the run is still going", and the conductor is left with the
#     same nothing either way. So the forbidden act has to be the one that actually ends the
#     leaf. Asked of all four built prompts for case 14's reason.
#
#     Reads the four prompts case 14 reads, and adds no invocation, for the reason given
#     there. `prompt_says` folds to one line for its own reason, which bites here in
#     particular: `end your turn` is three short words in a paragraph wrapped at ~85 columns,
#     so an unfolded probe would go red on a rewrap rather than on the rule going missing.
#     Matched tolerantly of the articles and of markdown emphasis between the words, but not
#     of the phrase itself.
forbids_ending_mid_run() {  # forbids_ending_mid_run <phase label> <prompt>
  local label="$1" prompt="$2"
  prompt_says "$prompt" "develop-$label never forbids ending the turn mid-run" \
    -iE -e 'end(ing)?[^[:alnum:]]+(your|the|its)[^[:alnum:]]+turn'
}

every_phase forbids_ending_mid_run \
  "every built developer prompt forbids ending the turn while a suite run is still going"

# 16. every built developer prompt forbids `git stash` and names a way to read the committed
#     version that touches no shared ref (issue #169). A leaf runs with
#     `--permission-mode bypassPermissions`, and `refs/stash` is ONE ref in the shared `.git`
#     that every worktree of the repository — the primary clone, every `.tdd/wt/<n>`, every
#     human session — pushes onto and pops off. So a leaf that stashes to compare against the
#     committed tree and pops afterwards pops whatever is on top *then*: another run's entry,
#     dropped from under it, restored into this branch. Two develop-refactor leaves in
#     `.tdd/wt/107` ran a bare `git stash … git stash pop -q` on 2026-09-13 to do exactly that.
#
#     The prohibition alone would leave the need unmet — wanting the tree without the change is
#     legitimate, which is why leaves keep inventing this — so the alternative is half of the
#     behaviour and gets its own miss: `git show HEAD:<path>` to read the committed version, or
#     a throwaway `git worktree add --detach` to compare against it. Asked of all four prompts
#     for case 14's reason, and each phase is its own miss, so a template that keeps one half is
#     named rather than covered for by its twin.
#
#     Reads the four prompts cases 14 and 15 read, and adds no invocation, for the reason given
#     there. `prompt_says` folds to one line for its own reason, which bites here in particular:
#     `git stash` is two short words, and a rewrap putting them across a line break is all an
#     unfolded probe needs to read them as absent.
forbids_stash() {  # forbids_stash <phase label> <prompt>
  local label="$1" prompt="$2"
  prompt_says "$prompt" "develop-$label never forbids git stash" \
    -iE -e "(never|do not|don't|no)[^.]{0,60}stash"
  prompt_says "$prompt" "develop-$label names no shared-ref-free way to see the committed version" \
    -E -e 'git show HEAD:|git worktree add'
}

every_phase forbids_stash \
  "every built developer prompt forbids git stash and names a safe alternative"

# 16. the two classes a refactor candidate falls into, and what sorts it (issue #149). Case 3
#     pins the bounds of the tidy-up and case 8 the `CANDIDATES:` backlog; both leave the leaf
#     free to count anything as a candidate. Sub-step 1 asks for "one transformation that makes
#     the code clearer" and sets no bar, so a leaf asked for one always finds one: across #105–
#     #144, at least 22 of the 127 `refactor:` commits only re-comment, re-cite or reflow, and
#     43 of 43 measured steps stopped on `VERI_REFACTOR_BUDGET` rather than on a leaf running
#     dry. Raising that budget from 2 to 5 changed how long the loop runs, not why it stops.
#     The bar is a definition, and the template's *The two classes of candidate* section is the
#     one place it is written down — a second copy here is one more thing to keep in step with
#     the prompt these probes read. What it turns on is the sorting rule: what the transform
#     CHANGES, not which file it sits in, which is why each class probe demands the class word
#     beside its effects rather than merely somewhere in the prompt. Three faces of one
#     criterion — both classes named-and-defined, and cosmetic pinned by what it leaves
#     untouched — so one case.
#
#     The prompt read is case 3's: same phase, same arguments, so there is one invocation and
#     case 3 owns the exit-0 check on it. Built with `prompt_says` for case 11's reasons, and
#     under the grep constraint reasoned about there — one bounded `[^.]{0,N}` per alternation
#     branch, so each class probe spends its budget going one way and the reversed branch gets
#     its own. Both directions because a definition reads either as `**structural**: removes
#     duplication…` or as `removing duplication is structural`, and which one a writer picks is
#     not the criterion. The class words themselves cannot be answered by what is already
#     there: no other line of the template names either class, the sub-step 1 wording
#     quoted above included.
#
#     The both-directions shape is `says_both_ways` above, shared with cases 19–20; each class
#     names only its own word and effects. Spelled out per class instead, the effects list
#     appears twice per class — once in each branch — and the one place the two copies had
#     drifted, a bare `comment` the forward cosmetic branch accepted and the reversed one did
#     not, was invisible until you diffed eight words by eye. `re-comment` alone answers the
#     bullet the template actually writes.
defines_class() {  # defines_class <class word> <alternation of that class's effects>
  local class="$1" effects="$2"
  says_both_ways "$refactor" "does not define $class by what the transform changes" \
    160 "$class" "($effects)"
}

problems=""
defines_class structural 'duplication|extract|inline|dead code|rename|scope'
defines_class cosmetic 'reword|re-word|re-cite|recite|reflow|re-flow|re-comment'
# The negative half of cosmetic's definition: rewording is cosmetic precisely because it
# removes no duplication and changes no identifier or structure. Without it the two classes
# overlap — a rename can be described as a rewording — and the sort stops being decidable.
#
# The gap is 30, not the 120 the other probes here spend, and the negation words are spelled
# with the spaces around them. Both bounds are load-bearing, and were watched: at 120 the
# probe passes with the clause deleted, matching the section's own lead-in — "never by which
# file it sits in … removes duplication" — 55 characters apart, and `no` unspaced matches the
# `no` inside `nothing`, `another` and `cannot`. What the clause has and those do not is a
# negation governing its object directly: "without removing duplication" is 10 characters
# between the two, "without changing an identifier" 13.
prompt_says "$refactor" "does not say cosmetic leaves duplication, identifiers and structure alone" \
  -iE -e ' (without|not|never|leaves) [^.]{0,30}(duplication|identifier|structure)'
[[ -z "$problems" ]] \
  && ok || no "develop-refactor defines structural and cosmetic candidates by what the transform changes (${problems#; })"

# 17. what the leaf does with the two classes case 16 defines (issue #149). A taxonomy the
#     leaf is not told to act on changes nothing: case 16 pins that the template names
#     structural and cosmetic and sorts them by what the transform changes, and sub-step 1
#     still asks for "one transformation that makes the code clearer", which a cosmetic
#     candidate answers. So the bar has to be spent twice over — on which transform the leaf
#     may apply, and on when it may stop. Both halves are needed for the loop to end early:
#     told only to prefer structural work, a leaf out of structural work applies a cosmetic
#     one and reports it, and the loop runs to `VERI_REFACTOR_BUDGET` exactly as it did for
#     43 of 43 measured steps; told only that cosmetic leftovers do not hold the loop open,
#     nothing stops the transform it just committed from having been one. Two faces of one
#     criterion, so one case.
#
#     Read, built and bounded as case 16's probes are, and for the reasons given there: case
#     3's prompt, `prompt_says`, one bounded `[^.]{0,N}` per alternation branch. Both
#     directions because either half reads as naturally forwards as backwards: "apply only a
#     structural transform" against "a structural transform is the only one to apply", "report
#     `nothing left to tidy` when only cosmetic candidates remain" against "when only cosmetic
#     candidates remain, nothing is left to tidy".
#
#     Neither probe can be answered by what is already there, which was checked against the
#     built prompt rather than the template: `structural` and `cosmetic` each occur exactly
#     once in it, in case 16's definitions, and no `only` sits within 60 characters of either,
#     nor any of the three `nothing left to tidy` occurrences within 120 of `cosmetic`.
problems=""
prompt_says "$refactor" "does not say only a structural transform may be applied" \
  -iE -e 'only[^.]{0,60}structural|structural[^.]{0,60}only'
# The stop condition, not merely the preference: a leftover cosmetic candidate must not keep
# the loop running, so the two have to be said in one breath.
prompt_says "$refactor" "does not say to report nothing left to tidy when only cosmetic candidates remain" \
  -iE -e 'nothing left to tidy[^.]{0,120}cosmetic|cosmetic[^.]{0,120}nothing left to tidy'
[[ -z "$problems" ]] \
  && ok || no "develop-refactor applies only a structural transform and reports nothing left to tidy when only cosmetic candidates remain (${problems#; })"

# 18. the class travels on the report line, not only in the leaf's head (issue #149). Cases 16
#     and 17 pin the taxonomy and what the leaf does with it; both are spent by the time the
#     leaf writes its footer, and case 8's `CANDIDATES:` line asks only for "a transform you
#     still see". So the backlog comes back unsorted, and `refactor-triage.sh` — the script
#     that reads this footer and decides whether another leaf is worth launching — has nothing
#     to sort it by: a leaf that left three cosmetic leftovers and one that left three
#     structural ones hand back the same line. Sorting them afterwards would mean re-deriving
#     from a transform's one-line description a judgement the leaf already made with the code
#     in front of it. So the class rides on each line, as the spec writes it: `CANDIDATES:
#     structural | <transform>` or `CANDIDATES: cosmetic | <transform>`. Two faces of one
#     criterion — each class offered on the line — so one case.
#
#     The prompt read is case 3's: same phase, same arguments, so there is one invocation and
#     case 3 owns the exit-0 check on it. Line-anchored greps rather than case 16's and 17's
#     `prompt_says`, and that is the point of this case rather than an accident of style:
#     `prompt_says` folds the prompt's newlines to spaces, which would throw away the `^`
#     that makes the claim "on the `CANDIDATES:` line" instead of "somewhere in the prompt" —
#     the distinction cases 16 and 17 already cover the other side of. Case 8's shape, for the
#     same reason it uses it.
#
#     `.*` before the class word and a bounded `[^|]` after it: what is pinned is that the
#     class is mechanically separable from the transform beside it, by the `|` the spec names,
#     not where on the line a writer puts the word. Spelling it `[^|]*structural` instead
#     would reject a single line offering both classes — `CANDIDATES: <structural | cosmetic>
#     | <transform>` — since the first `|` then sits between the anchor and `cosmetic`.
#     Neither probe can be answered by what is already there: the built prompt's one
#     `^CANDIDATES:` line carries no `|` at all, and `structural` and `cosmetic` occur only in
#     case 16's definitions and case 17's sub-steps, none of them on a line starting with the
#     token.
#
#     The probe is the same shape for either class, so it is written once and each caller names
#     only its own class — case 16's `defines_class` reasoning, applied to the one anchored
#     pattern this case owns: spelled out per class, the anchor, the `.*`, the `[^|]{0,40}` gap
#     and the `\|` appear twice, and a bound edited on one line and not the other is a drift no
#     diff makes loud. It is the same shape for either report TOKEN too, so the token is the
#     helper's first argument and case 38 calls it for `FLAGS:` rather than spelling a second
#     copy: the complaint names whichever token its caller passed, so nothing about the
#     sentence it records was tying the probe to this one case.
offers_class() {  # offers_class <report token> <class word>
  local token="$1" class="$2"
  grep -qE "^$token:.*$class[^|]{0,40}\|" <<<"$refactor" \
    || problems="$problems; the $token: line does not offer $class as the class"
}

problems=""
offers_class CANDIDATES structural
offers_class CANDIDATES cosmetic
[[ -z "$problems" ]] \
  && ok || no "develop-refactor requires every CANDIDATES: line to carry its class, separated from the transform (${problems#; })"

# 19. how many transforms one refactor leaf is worth, and what it owes for each (issue #150).
#     Cases 16–18 gave the leaf a bar and a vocabulary for its candidates; this one changes the
#     unit of work. ADR-0010 spends a fresh leaf per transform so that a break is attributable
#     to one change, and pays a cold `claude -p` start plus a re-read of the spec and the
#     touched files every time: refactor leaves ran 79–192 s each in #144's event log, where
#     the refactor loops and verify-refactor together took 2,147 of 3,735 leaf-seconds, and one
#     #137 step spent 49 minutes over five of them. What attribution actually needs is a commit
#     per transform and a suite run between transforms — not a leaf each. So the template asks
#     ONE leaf for the step's structural candidates up to the budget it is given, committing
#     each transform itself as `refactor:` (which is what moves that commit off the conductor,
#     whose sub-step 7 forbids it today), running the suites covering the touched files after
#     each and reverting one that turns them red, and reporting what it applied beside what it
#     left. Five faces of one criterion, so one case.
#
#     The half of the report that files the leftovers by class is case 18's and is not re-probed
#     here; what this case adds to the footer is the other half — several transforms were
#     applied now, so the leaf has to name them rather than the one RESULT: has room for.
#
#     Read, built and bounded as cases 16–17 are, and for the reasons given there: case 3's
#     prompt, so there is one invocation and case 3 owns the exit-0 check on it; `prompt_says`,
#     which folds the prompt to one line so a claim wrapped at ~85 columns is still one string;
#     and one bounded `[^.]{0,N}` per alternation branch, since BSD grep backtracks. Both
#     directions per probe, because each claim reads as naturally either way round — "commit
#     each transform as `refactor:`" against "`refactor: <what>` is what each transform is
#     committed as".
#
#     Four of the five probes cannot be answered by what is already there, which was checked
#     against the built prompt rather than the template: `budget`, `refactor:` and `after each`
#     occur nowhere in it. The revert probe is the exception and passes today — sub-step 2
#     already says to revert rather than leave a red suite behind — and is kept because the
#     criterion names it and no other case pins it, so a rewrite that dropped it while adding
#     the rest would otherwise land green.
#
#     Six probes of one shape, and that shape is `says_both_ways` above: each caller names
#     only its two halves and the gap between them, so a reversed branch that disagrees with
#     its forward half is not expressible. The bound is per probe because what the two halves
#     have to reach across differs — a sub-step's sentence for most of them, a footer line's
#     for the last.
problems=""
says_both_ways "$refactor" "does not say the structural candidates are applied up to the budget it is given" \
  80 'budget' 'structural'
# The commit moves to the leaf, and it carries the subject the conductor's checks read back:
# a prompt that says to commit without naming `refactor:` leaves the conductor counting
# commits it cannot tell apart from the green one.
says_both_ways "$refactor" "does not tell the leaf to commit its transforms itself as refactor:" \
  80 'commit' 'refactor:'
# One commit per transform is the whole of what ADR-0010's leaf-per-transform bought: batched
# into one commit, the transforms are back to being unattributable, which is the thing that
# must survive the leaf boundary going away.
says_both_ways "$refactor" "does not say one refactor: commit per transform" \
  60 '(each|every|own|per)' 'refactor:'
# After each, not once at the end: the suite run between transforms is what says WHICH
# transform turned them red, and a single run after the last one cannot.
says_both_ways "$refactor" "does not say the touched suites run after each transform" \
  80 'suites?' 'after each'
says_both_ways "$refactor" "does not say a transform that turns them red is reverted" \
  80 'revert' 'red'
# The footer's applied half: the RESULT: line named "<the transform>", singular, because there
# was only ever one. Several now, so the report has to have room for several.
says_both_ways "$refactor" "does not ask the report to name every transform it applied" \
  80 'applied' '(transforms|one per|each|every)'
[[ -z "$problems" ]] \
  && ok || no "develop-refactor applies the structural candidates up to its budget, one refactor: commit per transform, runs the touched suites after each reverting one that turns them red, and reports what it applied (${problems#; })"

# 20. where the number behind case 19's bound comes from (issue #150). Case 19 tells the leaf
#     to apply the structural candidates "up to the budget you are given", and nothing gives it
#     one: the conductor asks `refactor-budget.sh` how many transforms this step may still
#     spend and then builds a prompt that never mentions the answer. That was harmless while a
#     leaf applied exactly one transform and the count lived in the loop around it — the leaf
#     had no spending decision to make. One leaf per step moves the spending inside the leaf,
#     so either the number travels with the prompt or the bound is a phrase with nothing behind
#     it. `VERI_REFACTOR_BUDGET` is where every other reader of that number takes it from
#     (`refactor-budget.sh:20`), so the builder reads the same variable rather than growing a
#     second way to say the same thing.
#
#     Its own invocation, unlike cases 13 and 16–19, which share case 3's: what is pinned here
#     is what the environment puts in the prompt, so the environment has to be set for the
#     call, and this case owns the exit-0 check on it. Set explicitly rather than inherited,
#     for hermetic-suites.test.sh's reason — a suite's answer must be a fact about the script,
#     not about the shell that ran it.
#
#     A distinctive value, `37`, probed beside the word `budget` rather than anywhere in the
#     prompt: the template already carries digits — its sub-step numbers, `#<issue>` — so a
#     bare-number probe is answered by punctuation, and a number the leaf cannot tell is a
#     budget is not a budget. `37` occurs nowhere in the prompt built without it, checked
#     against the built prompt rather than the template. Both directions and one bounded
#     `[^.]{0,N}` per alternation branch, for case 19's reasons, so the probe is built by the
#     same `says_both_ways`, naming this call's prompt rather than case 3's.
problems=""
budgeted="$(VERI_REFACTOR_BUDGET=37 "$BUILD" refactor "$work/spec.md" "$step_text" "$test_cmd" "$touched" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] || problems="$problems; exited $code, want 0"
says_both_ways "$budgeted" "the prompt never names 37 as the budget" \
  80 'budget' '37'
[[ -z "$problems" ]] \
  && ok || no "develop-refactor carries VERI_REFACTOR_BUDGET into the prompt as the number of transforms the leaf may apply (${problems#; })"

# 21. what the red leaf is told to do BEFORE it runs anything (issue #193). Case 1 pins that
#     the prompt asks whether the new case failed, and case 11 what it runs to find out;
#     neither asks HOW it failed. A case that dies in setup on a typo'd fixture path and a case
#     whose assertion fires on the right value both report `AGAINST_UNMODIFIED: FAILS`, and both
#     reach verify-red as a red test. The dangerous member of that family is an assertion on the
#     wrong value: it stays red through Green, and the developer then contorts production code
#     to satisfy an assertion that was never a statement about the spec. So the leaf states its
#     hypothesis first — and the template has to ask for it in that order, since a prediction
#     written after the run is a transcription of it — and the footer carries the prediction
#     beside whether it held, which is what lets the conductor narrate both. Four faces of one
#     criterion, so one case.
#
#     The prompt read is case 1's — same phase, same arguments, so there is one invocation and
#     case 1 owns the exit-0 check on it. Built as cases 11 and 19 are and under the grep
#     constraints reasoned about there: `prompt_says` folds the prompt to one line, so a claim
#     wrapped at ~85 columns is still one string, and every branch carries at most ONE bounded
#     `[^.]{0,N}`. The ordering claim goes through `says_both_ways` because it reads as
#     naturally either way round — "predict before you run" against "before you run, predict".
#     Case 23 asks that same claim of the revise prompt, so the gap and both halves are spelled
#     once in `predicts_before_running` below and each caller names only its prompt and its
#     complaint — the `offers_verdict` reasoning below, across two cases rather than within one.
#     Its second half is `before you`, and the `you` is load-bearing — watched, case 16's way.
#     `before` alone is answered by the footer line another probe already pins: `PREDICTED_
#     FAILURE: <… — as predicted before running>` puts the two words adjacent, so with sub-step
#     2 deleted outright the probe still passed. What separates the instruction from that
#     placeholder is who it addresses — the leaf is told to predict before *it* acts, where the
#     placeholder only notes when the prediction was formed — so the alternation spells the
#     phrasings an instruction uses and a provenance note does not.
#     The three footer probes are literal and anchored on the token: these are protocol strings
#     a reader greps for, so a paraphrase of one is not one, and the two verdict words are
#     probed separately rather than as one alternation, which would be answered by either.
#     `predict` occurs nowhere in the prompt built today, checked against the built prompt
#     rather than the template.
#
#     Probed separately, though, the anchor, the gap and the complaint sentence are spelled
#     once per verdict — case 18's `offers_class` reasoning, applied to the one anchored
#     pattern this case owns: a bound edited on the MATCHED line and not the DIVERGED one is a
#     drift no diff makes loud, and the two would then be asking different questions under one
#     headline. So the shape is written once and each caller names only its verdict.
#
#     The gap is 20, not the 40 the other bounded probes here spend, and it is load-bearing —
#     watched, case 16's way. `prompt_says` folds the whole prompt to one line, so the footer's
#     three lines run together, and at 40 the DIVERGED branch is answered by the *next* line:
#     `PREDICTION: MATCHED PREDICTION_NOTE: <on DIVERGED` puts the word 30 characters past the
#     anchor with no `.` between, so a template offering only MATCHED on the PREDICTION: line
#     passed. What the probe means to reach across is that line's own value, `MATCHED |
#     DIVERGED` — 18 characters, 11 of them before the DIVERGED — so 20 is the value plus room
#     to reword it, and stops short of the 30 the leak needs.
#
#     Both shapes are written once and each caller names only its own prompt, label, token or
#     verdict, for the reason `offers_class` gives: the pattern is then the thing the complaint
#     names, and no two callers can disagree. `asks_for` is where `-F` lives — the whole of a
#     protocol string is the pattern, so there is nothing in it to interpret — and
#     `offers_verdict` where the bound does. Both take the prompt the way
#     `predicts_before_running` below does, because the same footer is owed by more than one
#     phase: case 29 asks these of the revise prompt.
asks_for() {  # asks_for <prompt> <report label> <footer token, colon included>
  local prompt="$1" label="$2" token="$3"
  prompt_says "$prompt" "the $label report never asks for $token" -F -e "$token"
}

offers_verdict() {  # offers_verdict <prompt> <report label> <verdict word>
  local prompt="$1" label="$2" verdict="$3"
  prompt_says "$prompt" "the $label report never offers $verdict on the PREDICTION: line" \
    -E -e "PREDICTION:[^.]{0,20}$verdict"
}

predicts_before_running() {  # predicts_before_running <prompt> <complaint>
  local prompt="$1" complaint="$2"
  says_both_ways "$prompt" "$complaint" 60 'predict' 'before (you|issuing|any command)'
}

problems=""
predicts_before_running "$red" "does not require the prediction to be stated before the run"
asks_for "$red" red 'PREDICTED_FAILURE:'
offers_verdict "$red" red MATCHED
offers_verdict "$red" red DIVERGED
asks_for "$red" red 'PREDICTION_NOTE:'
[[ -z "$problems" ]] \
  && ok || no "develop-red requires the predicted failure before the run and carries PREDICTED_FAILURE:, PREDICTION: MATCHED | DIVERGED and PREDICTION_NOTE: in its report footer (${problems#; })"

# 22. the same question asked of the OTHER branch of sub-step 5 (issue #193). Case 21 pins
#     what the leaf predicts before the run that decides FAILS or PASSES; this case pins the
#     path taken when that run says PASSES. There the leaf breaks the behaviour the case pins,
#     watches it go red and restores — and a colour is exactly as weak an answer here as it is
#     there. A temporary break that also breaks the setup, or that trips a sibling assertion,
#     turns the case red without the case having observed anything, and the leaf then reports a
#     test "capable of failing" on the strength of a red bar it never read. So the pin path
#     states what the break should make the case print, compares that against what it does
#     print, and does it BEFORE the restore: once the production code is back the output cannot
#     be reproduced, and a comparison made after it is one made against a recollection.
#     Three faces of one criterion, so one case.
#
#     The prompt read is case 1's — same phase, same arguments, so there is one invocation and
#     case 1 owns the exit-0 check on it. Built as cases 11, 19 and 21 are and under the grep
#     constraints reasoned about there: `prompt_says` folds the prompt to one line, and every
#     alternation branch carries at most ONE bounded `[^.]{0,N}`. The first two claims read as
#     naturally either way round — "predict what breaking it should print" against "what
#     breaking it should print, predicted" — so both go through `says_both_ways`.
#
#     Anchored on `break`, and that word in particular is load-bearing — watched, case 16's
#     way. `broken` is answered with sub-step 5 untouched: folded to one line, the footer puts
#     `FAIL_OUTPUT: <… from the temporarily-broken code>` a few words from case 21's
#     `PREDICTED_FAILURE: <… as predicted before running>`, so a `broken`-anchored probe reads
#     the report's two placeholders as the instruction. Anchoring the prediction on what it
#     prints fails the same way for sub-step 4's reason: `Compare what it printed against what
#     you predicted` puts `predict` beside `print` already. `break` occurs exactly once in the
#     prompt built today — sub-step 5's "temporarily break the behaviour it pins" — with
#     neither `predict` nor any of check/compare/match inside 80 characters of it, checked
#     against the built prompt rather than the template.
#
#     Two of the three probes share that anchor and that gap, so both are spelled once in
#     `pin_path_says` and each caller names only its complaint and the half it is looking for
#     — case 21's `offers_verdict` reasoning: an anchor or a bound edited on one probe and not
#     the other is a drift no diff makes loud, and the two would then be asking different
#     questions under one headline.
#
#     The ordering probe is the one claim that does NOT read both ways: "restore … before"
#     says the opposite of the criterion. So its reversed branch spells the phrasings that put
#     the restore last while leading with it — "restore only after", "do not restore until" —
#     rather than swapping the halves, and it is written out here instead of through
#     `says_both_ways`, which would build the branch that accepts the wrong order, and outside
#     `pin_path_says`, whose anchor it does not share.
pin_path_says() {  # pin_path_says <complaint> <what to find beside the break>
  local complaint="$1" pattern="$2"
  says_both_ways "$red" "$complaint" 80 'break' "$pattern"
}

problems=""
pin_path_says "the pin path never asks what the temporary break should print" 'predict'
pin_path_says "does not say what the break printed is checked against that prediction" \
  '(check|compar|match)'
prompt_says "$red" "does not put that check before the restore" \
  -iE -e 'before[^.]{0,40}restor|restor[^.]{0,40}(only after|not until)'
[[ -z "$problems" ]] \
  && ok || no "develop-red's pin path predicts what the temporary break should print and checks it before restoring (${problems#; })"

# 23. what a revise of red inherits from it (issue #193). Cases 21 and 22 pin the prediction
#     on the two paths through develop-red; this is the third way a red test reaches the
#     pipeline. A verify-red REJECT sends a fresh leaf to the revise template, and what that
#     leaf leaves on disk is a *different test* — rewritten to answer the objection, and so a
#     test whose failure nobody has predicted. The rewrite is exactly where an assertion drifts
#     onto the wrong value, since the leaf is editing to satisfy a complaint rather than to
#     state the spec, and it is the one attempt whose prediction cannot be inherited: the leaf
#     never saw the rejected attempt, so there is no old prediction for it to carry even if it
#     wanted to. So the revise prompt asks for a new prediction for the rewritten test, and
#     asks for it before the re-run — the ordering being the whole of what makes a prediction
#     one rather than a transcription. Two faces of one criterion, so one case.
#
#     The prompt read is case 4's — same phase, same arguments, so there is one invocation and
#     case 4 owns the exit-0 check on it, and it is the prompt built for `revise red`, the
#     phase the criterion names. Built as cases 11, 19, 21 and 22 are and under the grep
#     constraints reasoned about there: `prompt_says` folds the prompt to one line, so a claim
#     wrapped at ~85 columns is still one string, and every alternation branch carries at most
#     ONE bounded `[^.]{0,N}`. Both claims read as naturally either way round — "a rewritten
#     test owes a new prediction" against "predict the failure of the test you rewrote" — so
#     both go through `says_both_ways`.
#
#     `predict` occurs nowhere in the revise prompt built today, checked against the built
#     prompt rather than the template, so either probe alone is red now. They are two because
#     they fail on different wrong templates: one that says to predict before running, with
#     nothing tying it to the rewrite, answers the second and not the first — a revise of green
#     or refactor would then read it as work it owes — and one that ties a prediction to the
#     rewritten test without ordering it answers the first and not the second, which is the
#     transcription the discipline exists to rule out.
#
#     The ordering probe is case 21's `predicts_before_running`, and its `before you`
#     alternation is load-bearing here for the reason written there: the placeholder that
#     answers a bare `before`, `PREDICTED_FAILURE: <… as predicted before running>`, is one a
#     revise footer can inherit as readily as the red footer carries it.
problems=""
says_both_ways "$revise" "never says a rewritten test owes a new prediction" \
  80 '(rewrit|rewrote|new test)' 'predict'
predicts_before_running "$revise" "does not require that prediction before the re-run"
[[ -z "$problems" ]] \
  && ok || no "develop-revise asks for a new prediction for the rewritten test, before the re-run (${problems#; })"

# 24. the reconcile prompt (issue #232). A rejected push hands the branch to a leaf, and the
#     one command that leaf can get badly wrong is the force-push: a bare `--force`, or a lease
#     with no sha behind it, overwrites whatever the remote holds — someone else's commits
#     included. So the prompt carries the lease pinned to the exact sha `push-branch.sh` read
#     off the remote, spelled out literally for this branch, and the template never offers
#     the flag any other way: every `--force` in it is the start of `--force-with-lease=`.
#     A reconcile call short of its remote sha is refused like any other missing positional
#     (case 5's `refuses`), because a prompt with an empty lease is exactly the unpinned one.
#
#     Signature: reconcile <spec-file> <step-text> <test-cmd> <branch> <remote-sha>. The branch
#     carries a slash, as every run's `tdd/<n>-…` branch does, and the sha is a full 40 hex.
rc_branch='tdd/232-zorblat-frob'
rc_sha='3f9a1c0b7e2d4a6f8c1b3e5d7f9a0c2e4b6d8f01'
problems=""
reconcile="$("$BUILD" reconcile "$work/spec.md" "$step_text" "$test_cmd" "$rc_branch" "$rc_sha" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] || problems="$problems; exited $code, want 0"
[[ "$reconcile" == *"$rc_sha"* ]] || problems="$problems; no remote sha"
[[ "$reconcile" == *"$rc_branch"* ]] || problems="$problems; no branch"
[[ "$reconcile" == *"--force-with-lease=$rc_branch:$rc_sha"* ]] \
  || problems="$problems; no literal --force-with-lease=<branch>:<sha>"
rc_tpl="$HERE/../prompts/develop-reconcile.md"
if [[ ! -r "$rc_tpl" ]]; then
  problems="$problems; no template prompts/develop-reconcile.md"
elif grep -Eq -e '--force($|[^-]|-($|[^w]))' "$rc_tpl" \
  || grep -vq -e '^--force-with-lease=' < <(grep -o -e '--force-with-lease[^[:space:]`]*' "$rc_tpl"); then
  problems="$problems; template offers a --force that is not a pinned --force-with-lease="
fi
refusal_bad=""
refuses "reconcile missing remote sha" "$BUILD" reconcile "$work/spec.md" "$step_text" "$test_cmd" "$rc_branch"
[[ -z "$refusal_bad" ]] || problems="$problems${refusal_bad}"
[[ -z "$problems" ]] \
  && ok || no "develop-reconcile carries the remote sha, the branch and a pinned --force-with-lease=<branch>:<sha>, offers no bare --force, and refuses a missing argument with exit 2 (${problems#; })"

# 25. every built developer prompt forbids changing global or user-level configuration, and
#     names environment variables and throwaway directories as the way to simulate a condition
#     instead (issue #276). build-verify-prompt.test.sh's case 20 asks this of the verifier
#     prompts, after a verify-refactor leaf's `git config --global http.proxy …` outlived the
#     `trap` meant to undo it on 2026-09-17; a developer leaf runs with the same
#     `--permission-mode bypassPermissions` and the same `$HOME`, so its reach is the same and
#     so is the rule. The alternative is half of the behaviour for case 16's reason — the need to
#     simulate a condition is legitimate — and each phase is its own miss for case 14's.
#
#     Reads the four prompts cases 14–16 read and adds no invocation. The probes are that case
#     20's, word for word: the prohibition held within one sentence, and "throwaway" asked to
#     come with a directory, since the stash rule's "throwaway checkout" already carries the word.
forbids_global_config() {  # forbids_global_config <phase label> <prompt>
  local label="$1" prompt="$2"
  prompt_says "$prompt" "develop-$label never forbids changing global or user-level configuration" \
    -iE -e "(never|do not|don't|not)[^.]{0,80}(global|user-level)[^.]{0,60}config"
  prompt_says "$prompt" "develop-$label never names environment variables as the way to simulate a condition" \
    -iE -e 'environment variables?'
  prompt_says "$prompt" "develop-$label never names throwaway directories as the way to simulate a condition" \
    -iE -e '(throwaway|temporary|scratch)[^.]{0,20}director(y|ies)'
}

every_phase forbids_global_config \
  "every built developer prompt forbids changing global or user-level configuration and names environment variables and throwaway directories instead"

# 26. what a valid test is, and the escape hatch for a criterion that has none (issue #331).
#     #331's "the suite starts at most N python3" was satisfied by a leaf adding suites that
#     re-run whole suites under a counting shim (+41s of `make test`); #333's "launches
#     overlap" made a suite twice as slow. Both are criteria a developer leaf CAN satisfy —
#     just not with a test, and the pipeline had no way for it to say so. So develop-red now
#     states the rule (behaviour over mechanism, lightweight, self-contained) and the report
#     line that lets the leaf decline: `AGAINST_UNMODIFIED: UNTESTABLE` with a `WHY:`. Five
#     faces of one criterion — the mechanism ban, the process-count example, the spy carve-out
#     for a call count the criterion itself names, the lightweight rule and the escape hatch
#     itself — so one case, built the way case 11 builds its five: every alternation branch
#     carries at most ONE `[^.]{0,N}`, and `red` is case 1's prompt (same phase, same
#     arguments), so this reads it rather than building its own.
problems=""
prompt_says "$red" "never forbids pinning a process count, a fork count or a timing" \
  -iE -e '(process|fork)[^.]{0,20}count|timing'
prompt_says "$red" "never points a process/fork count or a timing at make profile instead" \
  -iE -e 'make profile'
prompt_says "$red" "never carves out a call count the criterion itself names, pinned with an in-process spy" \
  -iE -e 'in-process spy'
prompt_says "$red" "never says a PATH shim counting real processes is what the spy replaces" \
  -iE -e 'PATH[^.]{0,60}shim|shim[^.]{0,60}(count|real process)'
prompt_says "$red" "never gives the UNTESTABLE outcome as the report line for a criterion that cannot be pinned" \
  -iE -e 'UNTESTABLE'
[[ -z "$problems" ]] \
  && ok || no "develop-red states behaviour-over-mechanism (with the in-process-spy carve-out), points cost at make profile, and offers UNTESTABLE for a criterion no lightweight test can pin (${problems#; })"

# 27. the green phase takes the fast tier's command as a seventh positional (issue #341).
#     develop-green now runs the fast command plus the affected suites instead of the full
#     suite, and a leaf in a target repository has no `detect-test-command.sh` of its own to
#     ask — so the conductor passes the command in, and the prompt carries it verbatim, `&`,
#     `/` and quotes included. Without it the leaf would be told to run a command nobody
#     named, so a call short of it is a bad-arguments case: exit 2, a diagnostic, no prompt.
#     `problems` says which half broke.
fast_cmd='make unit ZORBLAT=fast -- --only "frob & nitz/quux"'
problems=""
fast_green="$("$BUILD" green "$work/spec.md" "$step_text" "$test_cmd" "$test_path" "$target" "$fast_cmd" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] || problems="$problems; with <fast-cmd> exited $code, want 0"
[[ "$fast_green" == *"$fast_cmd"* ]] || problems="$problems; the prompt does not carry <fast-cmd> verbatim"
refusal_bad=""
refuses "missing <fast-cmd>" "$BUILD" green "$work/spec.md" "$step_text" "$test_cmd" "$test_path" "$target"
[[ -z "$refusal_bad" ]] || problems="$problems${refusal_bad}"
[[ -z "$problems" ]] \
  && ok || no "develop-green takes <fast-cmd> as a seventh positional, carries it verbatim, and refuses a call without it with exit 2 (${problems#; })"

# 28. what the red leaf writes on the PREDICTED_FAILURE: line when the failure it predicts is
#     an error rather than an assertion (issue #355). Case 21 pins that the prompt asks for a
#     prediction before the run and carries the footer token; it says nothing about the one
#     family of red whose prediction has no assertion to name. In bash, Python or JS a call to
#     a name the step is about to introduce errors before any assertion runs, and verify-red
#     now accepts exactly that error — on exactly the name the step introduces — as a valid
#     red, while still rejecting a typo'd name or a wrong path. What tells the two apart is
#     whether the error names the name the step introduces, so the developer's prediction has
#     to carry that name: a prediction of "it errors" is a prediction a wrong path satisfies
#     too. So the template asks for the missing name on the PREDICTED_FAILURE: line.
#
#     The prompt read is case 1's — same phase, same arguments, so case 1 owns the exit-0
#     check on it. Probed through `says_both_ways` for case 21's reason: the claim reads as
#     naturally either way round — "PREDICTED_FAILURE: names the missing name" against "the
#     missing name goes on the PREDICTED_FAILURE: line" — and the helper spells one bounded
#     `[^.]{0,gap}` per branch, the constraint `prompt_says` reasons about. The gap is 60
#     rather than case 21's 20 because the two halves are a sentence apart at most, and the
#     footer folds to one period-free run where a looser bound would let the TARGET_TEST line's
#     "case name string" answer for the missing name this case is after. `missing name` occurs
#     nowhere in the prompt built today, checked against the built prompt rather than the
#     template.
problems=""
says_both_ways "$red" "never says the predicted missing-name error names the missing name on the PREDICTED_FAILURE: line" \
  60 'PREDICTED_FAILURE' '(missing|absent) name'
[[ -z "$problems" ]] \
  && ok || no "develop-red says a predicted missing-name error names the missing name in PREDICTED_FAILURE: (${problems#; })"

# 29. the footer a revise of red owes (issue #356). Case 23 pins that the revise prompt asks
#     for a new prediction for the rewritten test, before the re-run; it says nothing about
#     the leaf REPORTING it. The conductor's red-divergence gate reads a report's
#     `PREDICTION:` line and stops the step when it says DIVERGED — so a revise-red report
#     with no such line is a rewritten red test whose divergence nobody can see, the second
#     hole #356 names. A prediction the leaf formed and did not report is, to the conductor,
#     the same as one it never formed. So the revise footer carries the two lines the red
#     footer carries: the prediction itself, and whether it held. Two faces of one criterion,
#     so one case.
#
#     The prompt read is case 4's — same phase, same arguments, so there is one invocation and
#     case 4 owns the exit-0 check on it, and it is the prompt built for `revise red`, the
#     call the criterion names. The probes are case 21's own `asks_for` and `offers_verdict`,
#     named here with this prompt and this phase's label: the `PREDICTED_FAILURE:` one literal
#     and `-F`, since a protocol string a reader greps for has nothing in it to interpret and a
#     paraphrase of one is not one; the two verdict words anchored on `PREDICTION:` and probed
#     separately rather than as one alternation, which would be answered by either. Reused
#     rather than restated, for `offers_class`'s reason — a bound edited on one copy and not
#     the other is a drift no diff makes loud.
#
#     The gap is case 21's 20, and load-bearing for the reason written there: `prompt_says`
#     folds the prompt to one line, so at 40 the DIVERGED branch is answered by a following
#     `PREDICTION_NOTE: <on DIVERGED …>` placeholder 30 characters past the anchor with no `.`
#     between, and a footer offering only MATCHED on the PREDICTION: line would pass. The
#     probes are case-sensitive, so the lower-case `prediction` sub-step 2 already carries
#     answers neither: `PREDICTED_FAILURE` and `PREDICTION:` occur nowhere in the revise
#     prompt built today, checked against the built prompt rather than the template.
problems=""
asks_for "$revise" revise 'PREDICTED_FAILURE:'
offers_verdict "$revise" revise MATCHED
offers_verdict "$revise" revise DIVERGED
[[ -z "$problems" ]] \
  && ok || no "develop-revise ends with PREDICTED_FAILURE: and PREDICTION: MATCHED | DIVERGED report lines (${problems#; })"

# 30. the one file a transform may touch that this cycle did not (issue #358). Case 3 pins the
#     touched-files list as the bounds of the tidy-up, and the template's "Confine the transform
#     to those files" makes those bounds absolute — so duplication BETWEEN code this cycle wrote
#     and an older file can never be removed, which is the duplication Beck's refactor exists
#     for: his `Sum.plus()`/`Money.plus()` case spans two classes. So the prompt now carries one
#     exception, and only one: a transform may reach a file outside the list when it removes
#     duplication between that file and code this cycle wrote, and for no other reason. Two
#     faces of one criterion — the permission and its only-ness — so one case: a permission
#     without the bound reads as licence to tidy the whole repository, which is what case 3's
#     bounds were for.
#
#     The prompt read is case 3's: same phase, same arguments, so there is one invocation and
#     case 3 owns the exit-0 check on it. Probed through `says_both_ways` for case 16's reason —
#     "a transform outside the list only removes duplication" reads as naturally as "removing
#     duplication is the only transform outside the list" — which spells one bounded
#     `[^.]{0,gap}` per branch, the constraint `prompt_says` reasons about. The gap is 60: the
#     two halves belong to one sentence at most. `outside` occurs nowhere in the prompt built
#     today, checked against the built prompt rather than the template, so neither probe is
#     answered by prose already there.
problems=""
says_both_ways "$refactor" "never says a transform may touch a file outside the touched-files list to remove duplication" \
  60 'outside' 'duplication'
says_both_ways "$refactor" "never says removing that duplication is the only reason to leave the list" \
  60 'outside' 'only'
[[ -z "$problems" ]] \
  && ok || no "develop-refactor permits a transform outside the touched-files list only when it removes duplication with code this cycle wrote (${problems#; })"

# 31. which suites a transform owes a run of, now that it may leave the list (issue #358).
#     Case 30 lets one transform reach a file outside the touched-files list to remove
#     duplication with code this cycle wrote; case 19 pins the run that follows every
#     transform, and it is a run of "the suites affected-suites.sh prints for the files
#     refactor-touched.sh printed — the ones listed above". Those bounds were the same bounds
#     until case 30, and now are not: a transform that edits an older file runs the suites of
#     the files it did not edit, and the one suite that could catch the break it did cause is
#     the one it never runs. So the suites follow what the transform touched, the out-of-list
#     file included, rather than the list the prompt opened with.
#
#     Read and built as case 30 is, and for the reasons given there: case 3's prompt, so there
#     is one invocation and case 3 owns the exit-0 check on it; `says_both_ways`, since "run
#     the suites covering a file outside the list too" reads as naturally as "a file outside
#     the list is covered by the suites run". The gap is 80 rather than case 30's 60: the two
#     halves belong to one sub-step's sentence. Checked against the built prompt rather than the
#     template, the prompt's one `outside` sits in case 30's exception, whose sentence names
#     no suite, so the probe is not answered by prose already there — and `[^.]` cannot reach
#     sub-step 3 from it, since every script name between them carries a `.`.
problems=""
says_both_ways "$refactor" "never says the suites run after a transform cover a file it touched outside the list" \
  80 'outside' 'suites?'
[[ -z "$problems" ]] \
  && ok || no "develop-refactor tells the leaf to run the suites covering every file a transform touched, the out-of-list file included (${problems#; })"

# 32. retired by case 38 (issue #175). This case pinned what the refactor leaf reports about
#     overfit code: `NEW_STEP:`, offering `none`, and no `FLAGS:` line beside it. Case 38 moves
#     that report back onto a `FLAGS:` line carrying its class, so the two are the same
#     assertion with opposite signs — a suite holding both is unsatisfiable, and the green leaf,
#     forbidden to edit tests, could satisfy neither. So it is retired here rather than left
#     red, the way #361's own red retired case 3's `FLAGS:` clause into case 32. The number is
#     kept as this note because cases 33 and 34 cite it for the shape of an anchored report-line
#     probe; they now cite case 38, which owns that shape for this footer line.

# 33. the way out of a step too big for one green (issue #363). Case 2 pins the test the green
#     leaf must satisfy and the rule that it may not weaken it; this case pins what it may do
#     when neither is reachable — when the step needs more than one new behaviour at once, and
#     the only honest answers so far were a faked pass or a bail. Beck's Child Test is the
#     third: report the smaller steps instead of an implementation, and let the run come back
#     to this one. So the prompt offers `SPLIT:` — one to three behaviour-level criteria, one
#     per line, the conductor greps for and hands to `add-ledger-step.sh` — and says that a
#     leaf taking it changes no production code, since a split that left half an implementation
#     behind would hand the next step a tree nobody wrote a test for. Three faces of one
#     criterion, so one case.
#
#     The prompt read is case 2's: same phase, same arguments, so there is one invocation and
#     case 2 owns the exit-0 check on it. The report line is probed unfolded and anchored at
#     `^`, the way cases 8 and 38 probe `CANDIDATES:` and `FLAGS:`, because what is pinned
#     is a report LINE the conductor greps for at the start of one. The other two are claims
#     made somewhere in a sentence, so they go through `prompt_says`, and the third through
#     `says_both_ways` for case 16's reason — "report SPLIT: lines, changing no production
#     code" reads as naturally as "no production code changes when the leaf splits". The gap
#     is 80: the two halves belong to one sentence. `SPLIT` occurs nowhere in the prompt built
#     today and neither does "no production code" — the template's one "production code" is
#     the opening instruction to write the minimum of it — so no probe is answered by prose
#     already there.
problems=""
grep -qE '^SPLIT:' <<<"$green" || problems="$problems; no SPLIT: report line"
prompt_says "$green" "never bounds the split at one to three criteria" \
  -iE -e 'one to three|1 to 3|(at most|no more than) three'
says_both_ways "$green" "never says a leaf that splits changes no production code" \
  80 'SPLIT' '(no|any|without changing) production code'
[[ -z "$problems" ]] \
  && ok || no "develop-green offers one to three SPLIT: lines instead of an implementation, changing no production code (${problems#; })"

# 34. the same way out, offered to the leaf redoing that green (issue #363). Case 33 pins
#     `SPLIT:` in the green prompt; a verify-green REJECT sends a fresh leaf to the revise
#     template instead, and that leaf may only answer the verifier's objection — so a step
#     whose size is what made the attempt rejectable had, on that path, no third answer at
#     all: it could fake a pass or bail. The revise prompt therefore offers the same report,
#     and the same bound and the same no-production-code rule with it, since a split reached
#     through revise leaves the next step the same tree a split reached through green does.
#     Three faces of one criterion, so one case.
#
#     Read from its own invocation rather than case 4's `$revise`, which is built for `revise
#     red`: the criterion names the prompt built for `revise green`, and a probe answered by
#     the red one would pin nothing about green. This case therefore owns the exit-0 check on
#     that invocation. The report line is probed unfolded and anchored at `^`, the way cases
#     8, 33 and 38 probe `CANDIDATES:`, `SPLIT:` and `FLAGS:`, because what is pinned is a
#     report LINE the conductor greps for at the start of one; the other two go through
#     `prompt_says` and `says_both_ways` exactly as case 33 asks them of green, gap 80, for
#     the reason given there. `SPLIT` occurs nowhere in the revise prompt built today, so the
#     template's two existing "production code" mentions — the prediction sub-step and the
#     `AGAINST_UNMODIFIED:` footer line — answer neither probe.
revise_green="$("$BUILD" revise green "$work/spec.md" "$step_text" "$test_cmd" "$work/reason.md" 2>/dev/null)"; code=$?
problems=""
[[ "$code" -eq 0 ]] || problems="$problems; exited $code, want 0"
grep -qE '^SPLIT:' <<<"$revise_green" || problems="$problems; no SPLIT: report line"
prompt_says "$revise_green" "never bounds the split at one to three criteria" \
  -iE -e 'one to three|1 to 3|(at most|no more than) three'
says_both_ways "$revise_green" "never says a leaf that splits changes no production code" \
  80 'SPLIT' '(no|any|without changing) production code'
[[ -z "$problems" ]] \
  && ok || no "develop-revise redoing green offers the same one to three SPLIT: lines, changing no production code (${problems#; })"

# 35. the prompt for a step whose revise budget ran out (issue #408). A rejected step gets
#     `REVISE_BUDGET` attempts and then bails, losing the step's work — but a step no blind
#     verifier can be satisfied with in two attempts is usually a step carrying more than one
#     behaviour, the condition `SPLIT:` already exists for. So the budget's end sends one more
#     leaf, to a template of its own, and this case pins what that template must carry before
#     anything branches on what comes back: the step it could not satisfy, the verifier's LAST
#     rejection reason — the leaf never saw the attempt that earned it, so the reason text is
#     the whole of what it has to reason from, exactly as case 4 pins for revise — and the
#     issue spec, the criterion the step was cut from. The fourth face is the refusal: a phase
#     whose whole input is that reason file must not build a prompt without one, and a missing
#     file is exit 2, veri's "no answer could be obtained", like every other refusal in case 5.
#     Four faces of one criterion, so one case.
#
#     The reason file is case 4's: its text carries &, {} and a backslash, so a substitution
#     that mangled them would fail here too. Its own invocation, and its own exit-0 check,
#     since no other case builds this phase.
exhausted="$("$BUILD" exhausted "$work/spec.md" "$step_text" "$test_cmd" "$work/reason.md" 2>/dev/null)"; code=$?
problems=""
[[ "$code" -eq 0 ]] || problems="$problems; exited $code, want 0"
[[ "$exhausted" == *"$step_text"* ]] || problems="$problems; does not carry the step"
[[ "$exhausted" == *"$reason_text"* ]] || problems="$problems; does not carry the rejection reason verbatim"
[[ "$exhausted" == *'zorblat("Frob & Nitz/Quux")'* ]] || problems="$problems; does not carry the issue spec"
refusal_bad=""
refuses "exhausted missing reason" "$BUILD" exhausted "$work/spec.md" "$step_text" "$test_cmd" "$work/absent.md"
[[ -z "$refusal_bad" ]] || problems="$problems${refusal_bad}"
[[ -z "$problems" ]] \
  && ok || no "develop-exhausted carries the step, the verifier's last rejection reason and the issue spec, and refuses a missing reason file with exit 2 (${problems#; })"

# 36. the reproduction paragraph the red prompt gains for a bug, and only for a bug (issue
#     #112). For an issue labelled `bug`, Red is a reproduction (ADR-0015): the test encodes
#     *Expected*, is driven by *Steps to reproduce*, and must fail with the behaviour *What
#     happened* describes rather than with a missing symbol or a typo. That report reaches the
#     leaf through the one channel there is — `capture-spec.sh` puts it in the blind spec under
#     a `## Bug` heading — so the prompt's own paragraph is conditional on the spec carrying
#     that section, and a spec without one must not gain a word: a leaf told to reproduce a
#     report nobody made has nothing to reproduce. The builder's parameters do not change for
#     it, which is what the call below asserts by being case 1's call with case 1's three
#     positionals and a different spec file.
#
#     Probed through `prompt_says` under the constraint case 11 reasons about — at most one
#     bounded `[^.]{0,N}` per alternation branch — and each probe pairs the paragraph's verb
#     with the spec part it names, never a part name alone: the bug spec is interpolated into
#     the prompt verbatim, so `### Expected` is in there whatever the template says, and a
#     probe for the bare heading would pass on a template that gained nothing. The fixture's
#     four parts are nonsense carrying none of those verbs for the same reason.
#
#     The negative half reads case 1's prompt, built from the spec with no `## Bug` section,
#     and wants every one of the three probes to find nothing.
#
#     The fixture is case 1's own spec with the section appended, rather than a second copy
#     of it: the two differ in exactly the thing under test, and the positive and negative
#     halves below then read one prompt built from each, with nothing else between them that
#     could explain a difference.
cp "$work/spec.md" "$work/bug-spec.md"
cat >> "$work/bug-spec.md" <<'SPEC'

## Bug

### What happened

zorblat returned "FROB_NITZ" on the quuxed seed.

### Expected

zorblat returns "frob-nitz-quux".

### Steps to reproduce

Run zorblat --seed "Frob & Nitz/Quux".

### Environment

veri on bash 5.2, macOS 15.
SPEC

problems=""
bug_red="$("$BUILD" red "$work/bug-spec.md" "$step_text" "$test_cmd" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] || problems="$problems; with a bug spec and red's own three positionals exited $code, want 0"
[[ "$bug_red" == *'zorblat returned "FROB_NITZ" on the quuxed seed.'* ]] \
  || problems="$problems; does not carry the bug report from the spec"
writes_expected='(write|derive|encode)[^.]{0,40}expected|expected[^.]{0,40}(write|derive|encode)'
driven_by_steps='(drive|driven)[^.]{0,40}steps|steps[^.]{0,40}(drive|driven)'
fails_as_reported='(fail|fails|failure)[^.]{0,60}what happened|what happened[^.]{0,60}(fail|fails|failure)'
prompt_says "$bug_red" "never says to write the test from Expected" -iE -e "$writes_expected"
prompt_says "$bug_red" "never says to drive it with Steps to reproduce" -iE -e "$driven_by_steps"
prompt_says "$bug_red" "never says the failure must be the one What happened describes" -iE -e "$fails_as_reported"
prompt_lacks "$red" "a spec with no Bug section is still told to write the test from Expected" -iE -e "$writes_expected"
prompt_lacks "$red" "a spec with no Bug section is still told to drive it with Steps to reproduce" -iE -e "$driven_by_steps"
prompt_lacks "$red" "a spec with no Bug section is still told what the failure must be" -iE -e "$fails_as_reported"
[[ -z "$problems" ]] \
  && ok || no "develop-red tells a bug's leaf to write the test from Expected, drive it with Steps to reproduce and fail as What happened describes, and tells a leaf with no Bug section none of it (${problems#; })"

# 37. the same paragraph's last claim: a bug's case is named so it carries the issue number
#     (issue #112, criterion 3). A reproduction does not stop being useful once it is green —
#     it stays as this bug's regression test — and the only thing in the test file that says
#     which report it stands for is the number in its name. So the paragraph that tells the
#     leaf to reproduce must also tell it how to name what it wrote, in the project's own
#     test-naming idiom rather than a shape veri imposes: the leaf reads the suite it is
#     adding to, and a spelling dictated here would be wrong in most repositories.
#
#     Probed like case 36's three, under the same one-bounded-repeat constraint, and pairing
#     the verb with the thing named rather than either alone: `name` by itself matches the
#     red template's own prose about the error a test names, and `#<n>` by itself would pass
#     on a template that merely quoted the token. The negative half reads case 1's prompt for
#     the same reason case 36's does — a spec with no `## Bug` section gets no reproduction
#     and so owes no reproduction's name.
problems=""
names_with_number='(name|naming)[^.]{0,60}#<n>|#<n>[^.]{0,60}(name|naming)'
prompt_says "$bug_red" "never says to name the case so it carries #<n>" -iE -e "$names_with_number"
prompt_lacks "$red" "a spec with no Bug section is still told to name the case after the issue" -iE -e "$names_with_number"
[[ -z "$problems" ]] \
  && ok || no "develop-red tells a bug's leaf to name the case so it carries the issue's number in the project's own idiom, and tells a leaf with no Bug section nothing of it (${problems#; })"

# 38. the class a refactor flag carries, and what each class names (issue #175). Case 32 moved
#     the overfit report from `FLAGS:` to `NEW_STEP:`, so that what a leaf found could be handed
#     to `add-ledger-step.sh` as a criterion; the cost is that every flag then becomes a whole
#     ledger step — red, verify-red, green, verify-green, a refactor loop and a `### ✅ Step
#     done` — whatever it named. #175's six `plan: amend` commits are that cost paid, and
#     #107's three amendments are it feeding itself: each was flagged by a refactor leaf of the
#     step the previous amendment created. Only one of the three kinds of thing a leaf flags is
#     worth a step, so the conductor has to be able to tell them apart from the leaf's words
#     rather than its own judgement — which it can only do if the class rides on the line. So
#     the line goes back to `FLAGS:`, now carrying `overfit` (the code passes this step's test
#     without implementing the behaviour its criterion states), `uncovered-spec` (a behaviour
#     the spec requires that no ledger step covers — the only one that becomes an amendment) or
#     `beyond-spec` (an input class or edge the spec does not ask for), or `none` — and
#     `NEW_STEP:` goes with it, rather than sitting beside it, for the reason case 32 gave when
#     it took `FLAGS:` away: two footers for one answer let a leaf fill either and the conductor
#     read the other. That makes this case the exact inverse of case 32, which is retired where
#     it stood, for the reason its own note gives. What the conductor then DOES with each class
#     is `SKILL.md`'s, and the ledger's later steps.
#
#     The prompt read is case 3's: same phase, same arguments, so there is one invocation and
#     case 3 owns the exit-0 check on it. Two probe shapes, for the two halves of the criterion.
#     The line itself is probed unfolded and anchored at `^`, the way cases 8, 18 and 33 probe
#     theirs, because what is pinned is a report LINE the conductor greps for at the start of
#     one; the class-carries-a-`|` probe is case 18's own `offers_class`, called with this
#     token, since both halves of what it pins — the anchor and the `|` separating the class
#     from what follows it — are the same claim about a different footer line. What each class
#     NAMES is probed folded
#     with `says_both_ways`, the way case 16 probes the structural/cosmetic definitions — a
#     definition reads as naturally backwards as forwards, and a prompt is wrapped at ~85
#     columns, so the claim spans two lines and only the folded probe can see it. Three
#     classes, one shape, so the prompt, the gap and the complaint's `does not say <class>
#     names` frame are spelled once in `names_class` and each caller names only its class,
#     what that class names and the alternation that matches it — case 16's `defines_class`
#     reasoning, and the same drift it guards: spelled out per class the 120 appears three
#     times, and a bound widened on one and not the others is invisible in a diff. The two
#     halves cannot answer each other: a footer line carrying the word `beyond-spec` says
#     nothing about what a leaf may put on it, and a paragraph defining the three classes is
#     not a line the conductor can grep.
names_class() {  # names_class <class word> <what it names> <alternation matching that>
  local class="$1" names="$2" pattern="$3"
  says_both_ways "$refactor" "does not say $class names $names" \
    120 "$class" "$pattern"
}

problems=""
grep -qE '^FLAGS:' <<<"$refactor" || problems="$problems; no FLAGS: report line"
grep -qE '^FLAGS:.*none' <<<"$refactor" || problems="$problems; the FLAGS: line does not offer none"
grep -qE '^NEW_STEP:' <<<"$refactor" && problems="$problems; the report still carries a NEW_STEP: line"
offers_class FLAGS overfit
offers_class FLAGS uncovered-spec
offers_class FLAGS beyond-spec
names_class overfit 'code that passes the test without implementing the behaviour' \
  '(without|rather than|instead of) implementing'
names_class uncovered-spec 'a behaviour the spec requires' \
  '(spec (requires|asks)|required by the spec)'
names_class beyond-spec 'something the spec does not ask for' \
  "(does not|doesn.t|never) (ask|require)"
[[ -z "$problems" ]] \
  && ok || no "develop-refactor reports overfit code on FLAGS: lines carrying the overfit, uncovered-spec and beyond-spec classes or none, in place of NEW_STEP:, and defines what each class names (${problems#; })"

# 39. the prompt for a step that crossed its spend budget (issue #450, part of #447). The
#     parent reacts to a cost crossing the way #408 reacts to a spent revise budget — one leaf
#     asked whether the step is two behaviours — but case 35's `exhausted` phase cannot serve
#     it: that phase needs the verifier's last rejection, and a crossing often has none. So
#     `over-budget` takes the cost fact in the reason file's place: what the step has spent and
#     the budget it was given, two decimal figures. This case pins the four things the prompt
#     must carry — the step, both figures and the issue spec — and nothing else of the phase;
#     the figures are distinctive (`3.47`, `2.50`) so neither can match a number the template
#     happens to contain. Its own invocation and exit-0 check, since no other case builds it.
over_budget="$("$BUILD" over-budget "$work/spec.md" "$step_text" "$test_cmd" 3.47 2.50 2>/dev/null)"; code=$?
problems=""
[[ "$code" -eq 0 ]] || problems="$problems; exited $code, want 0"
[[ "$over_budget" == *"$step_text"* ]] || problems="$problems; does not carry the step"
[[ "$over_budget" == *'3.47'* ]] || problems="$problems; does not carry the spent figure"
[[ "$over_budget" == *'2.50'* ]] || problems="$problems; does not carry the budget figure"
[[ "$over_budget" == *'zorblat("Frob & Nitz/Quux")'* ]] || problems="$problems; does not carry the issue spec"
[[ -z "$problems" ]] \
  && ok || no "develop-over-budget carries the step, the spent figure, the budget figure and the issue spec (${problems#; })"

# 40. the over-budget prompt's report shapes (issue #450, criterion 2). Its answer is read by
#     `exhausted-outcome.sh`, unchanged by this issue, which recognises exactly two shapes: a
#     line starting `SPLIT:` (one per split criterion) and a line starting `NEEDS_USER:` (the
#     needs-user answer). A prompt that asked for anything else would get an answer that reader
#     resolves to "neither", so the case pins both labels as report lines, anchored at the start
#     of a line the way the reader's own `^SPLIT:` / `^NEEDS_USER:` patterns are. Case 39's
#     build is reused, since this asks a different question of the same prompt.
problems=""
grep -qE '^SPLIT:' <<<"$over_budget" || problems="$problems; no SPLIT: report line"
grep -qE '^NEEDS_USER:' <<<"$over_budget" || problems="$problems; no NEEDS_USER: report line"
[[ -z "$problems" ]] \
  && ok || no "develop-over-budget asks for SPLIT: lines or a NEEDS_USER: answer, the two shapes exhausted-outcome.sh reads (${problems#; })"

# 41. the over-budget prompt says a crossing is not a verdict (issue #450, criterion 3). A leaf
#     that believes it is being told off invents a split, so the prompt must say that nothing
#     has judged this work and that "one behaviour, simply expensive" is an answer the run can
#     act on. Whitespace is flattened first so a phrase the template wraps across lines still
#     reads as one; both checks ignore case. Case 39's build is reused.
over_budget_flat="$(tr -s '[:space:]' ' ' <<<"$over_budget")"
problems=""
grep -iE 'not a verdict' <<<"$over_budget_flat" > /dev/null || problems="$problems; does not say a crossing is not a verdict"
grep -iE 'one behaviour[^.]*simply expensive' <<<"$over_budget_flat" > /dev/null || problems="$problems; does not offer \"one behaviour, simply expensive\" as an answer"
[[ -z "$problems" ]] \
  && ok || no "develop-over-budget says a crossing is not a verdict and that one behaviour, simply expensive, is an available answer (${problems#; })"

# 42. the "neither" answer's own report shape (issue #450, criterion 3). Offering the answer
#     is case 41; a leaf that chooses it still has to know what to print, and `exhausted-outcome.sh`
#     reads "neither" as the absence of both labels — so the Report section itself must tell a
#     leaf answering "one behaviour, simply expensive" to print no SPLIT: and no NEEDS_USER:
#     line. Only the text from `### Report` on is searched, so case 41's sentence higher up
#     cannot satisfy this one. Case 41's flattened build is reused.
over_budget_report="${over_budget_flat#*'### Report'}"
problems=""
[[ "$over_budget_report" != "$over_budget_flat" ]] || problems="$problems; no ### Report section"
grep -iE 'simply expensive[^.]*(no|neither)[^.]*SPLIT:[^.]*NEEDS_USER:' <<<"$over_budget_report" > /dev/null \
  || problems="$problems; the report section has no shape for the one-behaviour, simply-expensive answer that says to print no SPLIT: and no NEEDS_USER: line"
[[ -z "$problems" ]] \
  && ok || no "develop-over-budget gives the \"neither — one behaviour, simply expensive\" answer its own report shape, printing no SPLIT: and no NEEDS_USER: line (${problems#; })"

# 43. the over-budget figures are numbers by regex (issue #450, criterion 4). `<spent>` and
#     `<budget>` are the only two parameters the phase adds, and they may carry a non-negative
#     decimal figure and nothing else — the same fail-closed shape as the verifier's
#     `<base-sha>`, so the phase opens no channel a rationale could reach a leaf through. Each
#     bad figure below sits beside a good one, so the call is wrong in exactly one place, and
#     each is refused the way case 5 refuses: exit 2, a diagnostic, no prompt. The last call
#     runs case 5's template-less copy: a figure validated before any template is read is
#     refused for the figure, naming it, never for the missing template or lib file.
refusal_bad=""
for bad in -1 3, qwixnum 1e3 .5 '3.47 because'; do
  refuses "spent '$bad'"  "$BUILD" over-budget "$work/spec.md" "$step_text" "$test_cmd" "$bad" 2.50
  refuses "budget '$bad'" "$BUILD" over-budget "$work/spec.md" "$step_text" "$test_cmd" 3.47 "$bad"
done
refuses "spent 'qwixnum' with no template" "$work/no-prompts/build-develop-prompt.sh" \
  over-budget "$work/spec.md" "$step_text" "$test_cmd" qwixnum 2.50
grep -F 'cannot read' "$work/err.txt" > /dev/null \
  && refusal_bad="$refusal_bad; with no template, refused for an unreadable file rather than the figure"
grep -F 'qwixnum' "$work/err.txt" > /dev/null \
  || refusal_bad="$refusal_bad; with no template, the diagnostic does not name the bad figure"
[[ -z "$refusal_bad" ]] \
  && ok || no "develop-over-budget refuses a <spent> or <budget> that is not a non-negative decimal number with exit 2, a diagnostic and no prompt, before any template is read (${refusal_bad#; })"

# 44. over-budget's arity (issue #450, criterion 5). The phase takes five arguments past its
#     own name — spec, step, test command, spent, budget — and a call short of any of them is
#     a bad-arguments case: exit 2, a diagnostic, no prompt. Every short call below passes
#     real values for what it does pass, so the only thing wrong with it is the count; the
#     four-argument call is the one a caller who dropped only `<budget>` makes.
refusal_bad=""
refuses "over-budget with no arguments"    "$BUILD" over-budget
refuses "over-budget with one argument"    "$BUILD" over-budget "$work/spec.md"
refuses "over-budget with two arguments"   "$BUILD" over-budget "$work/spec.md" "$step_text"
refuses "over-budget with three arguments" "$BUILD" over-budget "$work/spec.md" "$step_text" "$test_cmd"
refuses "over-budget with four arguments"  "$BUILD" over-budget "$work/spec.md" "$step_text" "$test_cmd" 3.47
[[ -z "$refusal_bad" ]] \
  && ok || no "develop-over-budget with fewer than five arguments after the phase exits 2, with a diagnostic and no prompt (${refusal_bad#; })"

# 45. the over-budget prompt names no rejection reason and no verdict, and takes no parameter
#     that could carry one (issue #450, criterion 6). A crossing is a cost fact, not a judgement,
#     so nothing the verifier says may reach this leaf: the prompt carries no rejection-reason
#     section and no verdict word, and a reason file handed over past the five arguments the
#     phase takes changes nothing — the prompt built with it is byte-identical to case 39's,
#     and case 4's rejection text appears nowhere in it. The figures are the only other inputs,
#     and case 43 already holds them to numbers. Case 39's build is reused.
over_budget_extra="$("$BUILD" over-budget "$work/spec.md" "$step_text" "$test_cmd" 3.47 2.50 "$work/reason.md" 2>/dev/null)"; code=$?
problems=""
[[ "$code" -eq 0 ]] || problems="$problems; with a reason file appended, exited $code, want 0"
[[ "$over_budget_extra" == "$over_budget" ]] || problems="$problems; a reason file appended past <budget> changed the prompt"
[[ "$over_budget_extra" != *"$reason_text"* ]] || problems="$problems; carries the rejection reason handed to it"
grep -iE 'rejection reason' <<<"$over_budget_flat" > /dev/null && problems="$problems; names a rejection reason"
grep -E 'REJECT|VERDICT' <<<"$over_budget" > /dev/null && problems="$problems; names a verdict"
[[ -z "$problems" ]] \
  && ok || no "develop-over-budget names no rejection reason and no verdict, and takes no parameter that could carry one (${problems#; })"

# 46. every other phase renders byte-identically to before #450 (criterion 7). `over-budget`
#     adds two positionals and two placeholders, `{{SPENT}}` and `{{BUDGET}}`, which every
#     other phase leaves empty — so none of their prompts may change by a byte. Each call below
#     is built with fixed inputs (the ones the cases above use) and reduced to a POSIX `cksum`,
#     which prints the same on BSD and GNU; the expected sums are what the builder at
#     9dffab38, the merge base #450 branched from, printed for the same calls. The scripts
#     directory is the one part of a prompt that depends on where the clone sits — the
#     `timed-test-run.sh` path is absolute — so it is replaced by a token before summing.
#     `VERI_REFACTOR_BUDGET` is pinned for the refactor call, since that phase reads it.
scripts_dir="$(cd "$HERE/.." && pwd)"
problems=""
renders_as() {  # <label> <want-cksum> <args...> — records a prompt whose sum is not <want>
  local label="$1" want="$2"; shift 2
  local out code got
  out="$(VERI_REFACTOR_BUDGET=5 "$BUILD" "$@" 2>/dev/null)"; code=$?
  [[ "$code" -eq 0 ]] || { problems="$problems; $label exited $code, want 0"; return; }
  got="$(printf '%s\n' "${out//"$scripts_dir"/@SCRIPTS@}" | cksum)"
  [[ "$got" == "$want" ]] || problems="$problems; $label renders as '$got', want '$want'"
}
renders_as red            '1517027772 9369'       red "$work/spec.md" "$step_text" "$test_cmd"
renders_as green          '577147033 6274'     green "$work/spec.md" "$step_text" "$test_cmd" "$test_path" "$target" "make unit"
renders_as refactor       '1094439882 8028'  refactor "$work/spec.md" "$step_text" "$test_cmd" "$touched"
renders_as 'revise red'   '3876022551 6477'    revise red "$work/spec.md" "$step_text" "$test_cmd" "$work/reason.md"
renders_as 'revise green' '3653834645 6479'  revise green "$work/spec.md" "$step_text" "$test_cmd" "$work/reason.md"
renders_as 'revise refactor' '3271905 6482' revise refactor "$work/spec.md" "$step_text" "$test_cmd" "$work/reason.md"
renders_as exhausted      '2209251247 3101'       exhausted "$work/spec.md" "$step_text" "$test_cmd" "$work/reason.md"
renders_as reconcile      '833555540 4704'       reconcile "$work/spec.md" "$step_text" "$test_cmd" "$rc_branch" "$rc_sha"
[[ -z "$problems" ]] \
  && ok || no "every phase other than over-budget renders byte-identically to before #450 (${problems#; })"

# 47. the rebase prompt (issue #238, criterion 3). A branch behind origin/<default> whose
#     rebase conflicted comes back from `rebase-onto-default.sh` aborted, at its pre-rebase
#     sha, with the conflicting files on stdout one per line — and is handed to a leaf. That
#     leaf has to know what to rebase onto (the onto sha, not a moving `origin/main`), where
#     it started (the pre-rebase sha), every file that conflicted, and the test command; it
#     resolves by rebasing onto the onto sha, and it leaves the ledger alone, because every
#     `[x]` tick and ` ⟂ refactor pending` mark is what a resumed run reads. Its answer is the
#     one line the conductor branches on, so the prompt ends with it. A call short of any of
#     its positionals is refused like every other (case 5's `refuses`): a prompt with no
#     conflicting files, or no sha to return to, is a leaf sent in blind.
#
#     Signature: rebase <spec-file> <step-text> <test-cmd> <onto-sha> <pre-rebase-sha>
#     <conflicting-files>, the last exactly as `rebase-onto-default.sh` printed it — one per
#     line. Both shas are full 40 hex and distinct; one file carries & and a space.
rb_onto='7c1e9a3f5b2d4e6a8c0f1b3d5e7a9c2e4f6b8d0a'
rb_pre='e2b4d6f8a0c1e3b5d7f9a1c3e5b7d9f0a2c4e6b8'
rb_files=$'skills/tdd/SKILL.md\nscripts/zorblat frob & nitz.sh'
problems=""
rebase="$("$BUILD" rebase "$work/spec.md" "$step_text" "$test_cmd" "$rb_onto" "$rb_pre" "$rb_files" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] || problems="$problems; exited $code, want 0"
[[ "$rebase" == *"$rb_onto"* ]] || problems="$problems; no onto sha"
[[ "$rebase" == *"$rb_pre"* ]] || problems="$problems; no pre-rebase sha"
while IFS= read -r rb_file; do
  [[ "$rebase" == *"$rb_file"* ]] || problems="$problems; no conflicting file '$rb_file'"
done <<< "$rb_files"
[[ "$rebase" == *"$test_cmd"* ]] || problems="$problems; no test command"
[[ "$rebase" == *"git rebase $rb_onto"* ]] || problems="$problems; no literal 'git rebase <onto-sha>'"
[[ "$rebase" == *ledger* && "$rebase" == *'[x]'* && "$rebase" == *'⟂ refactor pending'* ]] \
  || problems="$problems; does not tell the leaf to leave the ledger's [x] ticks and ⟂ refactor pending marks untouched"
rb_last="$(printf '%s\n' "$rebase" | sed '/^[[:space:]]*$/d' | tail -n 1)"
[[ "$rb_last" == 'REBASE: RESOLVED | FAILED'* ]] \
  || problems="$problems; last line is '$rb_last', want 'REBASE: RESOLVED | FAILED …'"
refusal_bad=""
refuses "rebase missing conflicting files" "$BUILD" rebase "$work/spec.md" "$step_text" "$test_cmd" "$rb_onto" "$rb_pre"
refuses "rebase missing pre-rebase sha" "$BUILD" rebase "$work/spec.md" "$step_text" "$test_cmd" "$rb_onto"
[[ -z "$refusal_bad" ]] || problems="$problems${refusal_bad}"
[[ -z "$problems" ]] \
  && ok || no "develop-rebase names the onto sha, the pre-rebase sha, every conflicting file and the test command, resolves by git rebase <onto-sha>, leaves the ledger's ticks and marks untouched, ends with REBASE: RESOLVED | FAILED, and refuses a missing argument with exit 2 and no stdout (${problems#; })"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
