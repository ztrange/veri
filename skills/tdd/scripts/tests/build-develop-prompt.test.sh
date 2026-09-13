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
#   greps for to route a passing red test to verify-pin (SKILL.md, Red step).
#
# Contract under test, green phase:
#   build-develop-prompt.sh green <spec-file> <step-text> <test-cmd> <test-path> <target>
#   exits 0 and prints a prompt naming the test the implementation must satisfy — its path
#   and its case name — and forbidding any edit to it, the rule that keeps "make it green"
#   from degenerating into "weaken the test".
#
# Contract under test, refactor phase:
#   build-develop-prompt.sh refactor <spec-file> <step-text> <test-cmd> <touched-files>
#   exits 0 and prints a prompt naming the files this cycle touched — the bounds of the
#   tidy-up — carrying the rule that bounds it further (no generality no test demands), and
#   requiring the `RESULT:` / `FLAGS:` / `CANDIDATES:` footer: the first two the conductor
#   branches on, the third the backlog it lists when the loop was stopped by the budget
#   rather than by a leaf finding nothing left.
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
green="$("$BUILD" green "$work/spec.md" "$step_text" "$test_cmd" "$test_path" "$target" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] \
  && [[ "$green" == *"$test_path"* ]] \
  && [[ "$green" == *"$target"* ]] \
  && grep -qiE "(do not|don't|never) (modify|change|edit|touch|weaken).{0,40}test|test.{0,40}(must not|may not) be (modified|changed|edited|touched)" <<<"$green" \
  && ok || no "develop-green names the test path + target test and forbids modifying the test (exit $code)"

# 3. the refactor prompt names the files the cycle touched, carries the rule that bounds
#    the tidy-up (no generality no test demands) and requires the RESULT:/FLAGS: footer
touched='scripts/zorblat.sh, tests/zorblat/test_frob & nitz.sh'
refactor="$("$BUILD" refactor "$work/spec.md" "$step_text" "$test_cmd" "$touched" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] \
  && [[ "$refactor" == *"$touched"* ]] \
  && grep -qiE '(no|not|never|without)[^.]{0,80}(generality|generali[sz]ation|abstraction)' <<<"$refactor" \
  && grep -q 'RESULT:' <<<"$refactor" \
  && grep -q 'FLAGS:' <<<"$refactor" \
  && ok || no "develop-refactor carries the touched-files list + the no-untested-generality rule and the RESULT:/FLAGS: footer (exit $code)"

# 4. the revise prompt carries the verifier's rejection reason verbatim and offers the
#    IMPOSSIBLE outcome
cat > "$work/reason.md" <<'REASON'
REJECT: the case asserts on zorblat()'s log line, not its return value — & {tricky}\chars.
REASON
revise="$("$BUILD" revise red "$work/spec.md" "$step_text" "$test_cmd" "$work/reason.md" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] \
  && [[ "$revise" == *"REJECT: the case asserts on zorblat()'s log line, not its return value — & {tricky}\\chars."* ]] \
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
#    the protocol token, at the start of a line like `RESULT:` and `FLAGS:`, because the
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
prompt_says() {  # prompt_says <prompt> <complaint> <grep argument…>
  local prompt="$1" complaint="$2"; shift 2
  grep -q "$@" <<<"$(tr '\n' ' ' <<<"$prompt")" || problems="$problems; $complaint"
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

problems=""
demands_foreground red "$red"
demands_foreground green "$green"
demands_foreground refactor "$refactor"
demands_foreground revise "$revise"
[[ -z "$problems" ]] \
  && ok || no "every built developer prompt says to run test commands in the foreground and report only after they exit (${problems#; })"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
