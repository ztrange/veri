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
#     The both-directions shape is the same for either class, so it is written once here and
#     each caller names only its own class and effects. Spelled out per class instead, the
#     effects list appears twice per class — once in each branch — and the one place the two
#     copies had drifted, a bare `comment` the forward cosmetic branch accepted and the
#     reversed one did not, was invisible until you diffed eight words by eye. `re-comment`
#     alone answers the bullet the template actually writes.
defines_class() {  # defines_class <class word> <alternation of that class's effects>
  local class="$1" effects="$2"
  prompt_says "$refactor" "does not define $class by what the transform changes" \
    -iE -e "$class[^.]{0,160}($effects)|($effects)[^.]{0,160}$class"
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
#     diff makes loud.
offers_class() {  # offers_class <class word>
  local class="$1"
  grep -qE "^CANDIDATES:.*$class[^|]{0,40}\|" <<<"$refactor" \
    || problems="$problems; the CANDIDATES: line does not offer $class as the class"
}

problems=""
offers_class structural
offers_class cosmetic
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
problems=""
prompt_says "$refactor" "does not say the structural candidates are applied up to the budget it is given" \
  -iE -e 'budget[^.]{0,80}structural|structural[^.]{0,80}budget'
# The commit moves to the leaf, and it carries the subject the conductor's checks read back:
# a prompt that says to commit without naming `refactor:` leaves the conductor counting
# commits it cannot tell apart from the green one.
prompt_says "$refactor" "does not tell the leaf to commit its transforms itself as refactor:" \
  -iE -e 'commit[^.]{0,80}refactor:|refactor:[^.]{0,80}commit'
# One commit per transform is the whole of what ADR-0010's leaf-per-transform bought: batched
# into one commit, the transforms are back to being unattributable, which is the thing that
# must survive the leaf boundary going away.
prompt_says "$refactor" "does not say one refactor: commit per transform" \
  -iE -e '(each|every|own|per)[^.]{0,60}refactor:|refactor:[^.]{0,60}(each|every|own|per)'
# After each, not once at the end: the suite run between transforms is what says WHICH
# transform turned them red, and a single run after the last one cannot.
prompt_says "$refactor" "does not say the touched suites run after each transform" \
  -iE -e 'suites?[^.]{0,80}after each|after each[^.]{0,80}suites?'
prompt_says "$refactor" "does not say a transform that turns them red is reverted" \
  -iE -e 'revert[^.]{0,80}red|red[^.]{0,80}revert'
# The footer's applied half: the RESULT: line named "<the transform>", singular, because there
# was only ever one. Several now, so the report has to have room for several.
prompt_says "$refactor" "does not ask the report to name every transform it applied" \
  -iE -e 'applied[^.]{0,80}(transforms|one per|each|every)|(transforms|one per|each|every)[^.]{0,80}applied'
[[ -z "$problems" ]] \
  && ok || no "develop-refactor applies the structural candidates up to its budget, one refactor: commit per transform, runs the touched suites after each reverting one that turns them red, and reports what it applied (${problems#; })"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
