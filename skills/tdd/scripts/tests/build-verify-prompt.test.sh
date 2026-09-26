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
pass=0 fail=0
ok() { pass=$((pass + 1)); }
no() { fail=$((fail + 1)); echo "FAIL - $1"; }

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

# A spec with characters that would break naive sed substitution (&, \, /, {}).
cat > "$work/spec.md" <<'SPEC'
slugify("Hello & World/Foo") must return "hello-world-foo" — see {ref}\n done.
SPEC
testpath="tests/test_slugify.py"
# green and refactor require the fast tier's command by flag (#341, case 24); the other phases take none. fast_for <phase> sets the array `fast` to the flag its call owes.
fast_for() { fast=(); [[ "$1" == green || "$1" == refactor ]] && fast=( --fast-cmd 'make unit' ); }

red="$("$BUILD" red "$work/spec.md" "$testpath" test_slugify_lowercases)"

# 1. the issue spec is carried verbatim into the prompt (literal substitution)
[[ "$red" == *'slugify("Hello & World/Foo")'* ]] && ok || no "carries issue spec verbatim"

# 2. the test path is named so the blind verifier can read and run it itself
[[ "$red" == *"$testpath"* ]] && ok || no "names the test path"

# 3. blindness is stated explicitly: the verifier is told it has only test + spec, not
#    the author's reasoning
grep -qiE 'have not (been told|received).*(reason|rationale)|never.*(reason|rationale)' \
  <<<"$red" && ok || no "states the blindness contract"

# 4. the verdict-format contract parse-verdict.sh depends on is present
grep -q 'VERDICT:' <<<"$red" && grep -qi 'PASS' <<<"$red" && grep -qi 'REJECT' <<<"$red" \
  && ok || no "instructs the VERDICT: PASS|REJECT format"

# 5. verify-red audits right-reason failure AND test quality (trivial/coupled/complex)
grep -qi 'right reason' <<<"$red" && grep -qiE 'trivial|coupled|complex' <<<"$red" \
  && ok || no "verify-red audits right-reason + quality"

# 6. verify-green checks the FULL SUITE, not just the target test
green="$("$BUILD" --fast-cmd 'make unit' green "$work/spec.md" "$testpath" test_slugify_lowercases)"
grep -qi 'full' <<<"$green" && grep -qi 'suite' <<<"$green" \
  && ok || no "verify-green checks the full suite"

# 7. verify-refactor judges up-to-standard (conventions/typing/robustness) + still green
refactor="$("$BUILD" --fast-cmd 'make unit' refactor "$work/spec.md" "$testpath" 0123abc)"  # refactor's 4th slot is a base sha (#151)
grep -qiE 'standard|convention|typing|robust' <<<"$refactor" \
  && grep -qi 'green' <<<"$refactor" && ok || no "verify-refactor judges standard + green"

# 8. an unknown phase is rejected (exit non-zero), not silently rendered
"$BUILD" bogus "$work/spec.md" "$testpath" >/dev/null 2>&1; code=$?
[[ "$code" -ne 0 ]] && ok || no "unknown phase exits non-zero (got $code)"

# 9. verify-pin: for a criterion the code already satisfies there is nothing to make fail,
#    so the blind verifier judges the test as a regression pin instead — same two inputs
#    (spec + test path), and the three checks that a passing test is worth committing:
#    it passes now, it fails under a mutation that removes the behavior, it is
#    behavior-level rather than trivial.
pin="$("$BUILD" pin "$work/spec.md" "$testpath" test_slugify_lowercases)"; code=$?
[[ "$code" -eq 0 ]] \
  && [[ "$pin" == *'slugify("Hello & World/Foo")'* ]] \
  && [[ "$pin" == *"$testpath"* ]] \
  && grep -qiE 'pass(es)? (now|today|already|against|on the (current|unmodified))' <<<"$pin" \
  && grep -qi 'mutation' <<<"$pin" \
  && grep -qiE 'behaviou?r-level|trivial' <<<"$pin" \
  && ok || no "verify-pin carries spec + test path and the three pin checks (exit $code)"

# 10. verify-green still demands the project's FULL TEST SUITE, in those words.
#     #144 moved the developer leaves off the full suite and onto the suite they touched,
#     so the blind verifiers became the place a regression in an untouched suite is
#     caught. #341 moves verify-refactor onto the affected suites — the conductor's pre-PR
#     `--tier all` run is where the full command still runs — and prompt-test-tiers.test.sh
#     pins that half now. The phrase is matched tolerantly of markdown emphasis (`**full
#     test suite**`) but not of the whole sentence going missing.
full_suite='full[^[:alnum:]]*test[^[:alnum:]]*suite'
grep -qiE "$full_suite" <<<"$green" \
  && ok || no "verify-green still requires the full test suite"

# 11. the argument list does not grow. #144 moves the developer leaves onto the suite they
#     touched, and the obvious next thought is to tell the verifier which suite that was —
#     which would be a fifth parameter, and the blindness guarantee is precisely that no
#     such channel exists (ADR-0003). So anything passed beyond the four documented
#     positionals must reach nothing: the prompt is byte-identical to the four-argument one
#     built at case 6 from the same phase, spec, test path and test id.
smuggled='ran only tests/test_slugify.py, the suite I touched, because the rest is slow'
five="$("$BUILD" --fast-cmd 'make unit' green "$work/spec.md" "$testpath" test_slugify_lowercases "$smuggled")"
[[ "$five" == "$green" ]] && ok || no "a fifth argument reaches nothing (argument list unchanged)"

# The probe the two per-phase cases below are built from, lifted from the same helper in
# build-develop-prompt.test.sh, which carries its full reasoning. One claim, one miss: the
# pattern stays at the call site, where the comment above it reasons about that claim, while
# what every probe would otherwise repeat lives once — the fold to a single line and the
# shape of the complaint appended to `problems`. The fold is not cosmetic: a prompt is
# markdown wrapped at ~85 columns and grep only ever matches within one line, so any claim
# long enough to be worth probing for reads as absent the moment a rewrap puts it across a
# line break. `-e` because a pattern is data, not a flag.
prompt_has() {  # prompt_has <prompt> <grep argument…> — the match itself, folded to one line
  local prompt="$1"; shift
  grep -q "$@" <<<"$(tr '\n' ' ' <<<"$prompt")"
}

prompt_says() {  # prompt_says <prompt> <complaint> <grep argument…>
  local prompt="$1" complaint="$2"; shift 2
  prompt_has "$prompt" "$@" || problems="$problems; $complaint"
}

# The same probe read the other way, for a claim a prompt must NOT make — case 42's negative
# half, where the paragraph conditional on a `## Bug` section must be absent from the prompt
# built from a spec without one. It shares `prompt_has` rather than repeating the fold and the
# grep: two copies of the probe is where the one that folds differently hides, and a negative
# assertion that quietly matches nothing because its input was never folded is green for the
# wrong reason. `return 0` because the miss is recorded in `problems`, not in the function's
# status, and a failed `grep` is this one's success. Same helper as
# build-develop-prompt.test.sh's.
prompt_lacks() {  # prompt_lacks <prompt> <complaint> <grep argument…> — prompt_says inverted
  local prompt="$1" complaint="$2"; shift 2
  ! prompt_has "$prompt" "$@" || problems="$problems; $complaint"
  return 0
}

# The other half of what the two per-phase cases share: the roster, and the verdict they reach
# from it. Each asks the same claim of all four built prompts and reports one accumulated miss
# list, so which phases "every phase" means lives here rather than once per case — a fifth phase
# is one edit, not two — and so does the shape of the answer: green when nothing accumulated,
# otherwise the case's own headline followed by every miss. The accumulator is a `local`, which
# bash's dynamic scoping still puts in reach of the `prompt_says` calls two frames down; a case
# that inherited the previous case's misses would fail naming the wrong claim, and now cannot
# see them to inherit.
every_phase() {  # every_phase <name of a check function taking <phase label> <prompt>> <headline>
  local check="$1" headline="$2" problems=""
  "$check" red "$red"; "$check" green "$green"; "$check" refactor "$refactor"; "$check" pin "$pin"
  [[ -z "$problems" ]] && ok || no "$headline (${problems#; })"
}

# 12. every phase's built prompt carries the foreground rule. A verifier that puts its
#     suite run in the background can end its turn before the run returns, printing no
#     footer — so no `VERDICT:` line, so verify.sh exits 2 and the conductor must relaunch
#     or bail as a system failure (four times across #123 and #137). #144 gave the rule to
#     the developer leaves only; the verifier prompts never got it. The assertion is on
#     the built prompt for each of the four phases rather than on _shared.md, because the
#     behaviour is the rule reaching every phase, not which file holds it. Matched
#     tolerantly of markdown emphasis and of the exact sentence, but not of either half —
#     "foreground", and not ending the turn mid-run — going missing. Each half is its own
#     miss, so a rewording that keeps one and drops the other is named rather than covered
#     for by its twin.
#
#     Shaped after build-develop-prompt.test.sh case 14, which asks the same of the four
#     developer prompts: a per-phase helper feeding one accumulator. The prompts read are
#     cases 5, 6, 7 and 9's — same phases, same arguments — so this case invokes the
#     builder not at all, and those cases keep the exit-status checks on them.
#
#     `prompt_says` folds to one line for the reason given at its definition, which bites
#     here in particular: `end your turn` is three short words in a paragraph wrapped at ~85
#     columns, so an unfolded probe would go red on a rewrap rather than on the rule going
#     missing. It matches today only because the wrap happens to fall elsewhere.
demands_foreground() {  # demands_foreground <phase label> <prompt>
  local label="$1" prompt="$2"
  prompt_says "$prompt" "verify-$label never says to run test commands in the foreground" \
    -i -e 'foreground'
  prompt_says "$prompt" "verify-$label never forbids ending the turn mid-run" \
    -iE -e 'end(ing)?[^[:alnum:]]+(your|the|its)[^[:alnum:]]+turn'
}

every_phase demands_foreground "every phase's prompt carries the foreground rule"

# 13. every phase's built prompt forbids `git stash` and names a way to read the committed
#     version that touches no shared ref (issue #169). A leaf runs with
#     `--permission-mode bypassPermissions`, and `refs/stash` is ONE ref in the shared
#     `.git` that every worktree of the repository — the primary clone, every `.tdd/wt/<n>`,
#     every human session — pushes onto and pops off. So a leaf that stashes to peek at the
#     committed tree and pops afterwards pops whatever is on top *then*: another run's
#     entry, dropped from under it, restored into this branch. A verify-red leaf in
#     `.tdd/wt/70` stashed the developer's test file to see a baseline on 2026-09-11, and a
#     verifier ran a bare `git stash` on 2026-09-13 with other worktrees open.
#
#     The prohibition alone would leave the need unmet — wanting the tree without the change
#     is legitimate, which is why leaves keep inventing this — so the alternative is half of
#     the behaviour and gets its own miss: `git show HEAD:<path>` to read the committed
#     version, or a throwaway `git worktree add --detach` to compare against it. Each phase
#     is its own miss too, for case 12's reason: a template that keeps one half is named
#     rather than covered for by its twin.
#
#     Reads cases 5, 6, 7 and 9's prompts and invokes the builder not at all, as case 12
#     does, and probes through the same `prompt_says`, whose fold to one line is here for
#     the reason given at its definition: `git stash` is two short words, and a rewrap
#     putting them across a line break is all an unfolded probe needs to read them as absent.
forbids_stash() {  # forbids_stash <phase label> <prompt>
  local label="$1" prompt="$2"
  prompt_says "$prompt" "verify-$label never forbids git stash" \
    -iE -e "(never|do not|don't|no)[^.]{0,60}stash"
  prompt_says "$prompt" "verify-$label names no shared-ref-free way to see the committed version" \
    -E -e 'git show HEAD:|git worktree add'
}

every_phase forbids_stash "every phase's prompt forbids git stash and names a safe alternative"

# 14. the argument list is still the WHOLE input. #143 gives every leaf the run's test
#     command as VERI_TEST_CMD in its environment, the blind verifier's leaf included, so
#     for the first time the builder runs with a variable in scope that names the
#     developer's world. Reading it would be the fifth channel case 11 refuses in positional
#     form, arriving through the environment instead — and blindness is structural only
#     while the four documented positionals are everything the prompt can be built from
#     (ADR-0003). So the prompt built with it set is byte-identical to the one built with it
#     unset, from the same four arguments.
base="$(env -u VERI_TEST_CMD "$BUILD" --fast-cmd 'make unit' green "$work/spec.md" "$testpath" test_slugify_lowercases)"
#     The probe's value is deliberately not any command this repo would fall back to, so a
#     leak reading it cannot coincide with its own default and pass by accident.
ambient="$(VERI_TEST_CMD='pytest -k leaked_channel' "$BUILD" --fast-cmd 'make unit' green "$work/spec.md" "$testpath" test_slugify_lowercases)"
[[ "$ambient" == "$base" ]] && ok || no "VERI_TEST_CMD in the environment reaches nothing (arguments unchanged)"

# 15. no verifier prompt carries the developer's prediction, through any channel. #193 has
#     the red leaf state its predicted failure before it runs anything and report it as
#     PREDICTED_FAILURE / PREDICTION — the newest piece of developer rationale, and the one
#     most tempting to forward, since it says in advance exactly what the verifier is about to
#     go and observe. That is why it must not arrive: verify-red establishes ground truth by
#     running the test itself, and a verifier told what the developer expected is a verifier
#     primed to agree, which is the whole of what ADR-0003 buys. The two channels the
#     developer's world can reach the builder by are the ones cases 11 and 14 each close for
#     one phase and one payload — a positional past the four documented ones, and the
#     environment the conductor launches the leaf with — so the prediction is offered through
#     both at once, to all four phases, and must appear in none of them.
#
#     Two misses, not one, because they fail differently: the prediction's own text appearing
#     is a leak through a channel, while `PREDICTED_FAILURE` or `PREDICTION` appearing with no
#     prediction supplied is a template that has grown a slot asking for one — the edit that
#     would make the leak worth building. Each phase accumulates its own, for case 12's
#     reason: a template that leaks is named rather than covered for by its three siblings.
#     This case builds its own four prompts rather than reading cases 5-9's, since the payload
#     is the point, and its payload carries no form of the word "predict", so the two misses
#     stay independent.
prediction='the second assert fires: want "hello-world-foo", got "Hello & World/Foo"'
problems=""
for phase in red green refactor pin; do
  slot4=test_slugify_lowercases; [[ "$phase" == refactor ]] && slot4=0123abc  # a base sha (#151)
  fast_for "$phase"
  smuggled_prompt="$(VERI_PREDICTED_FAILURE="$prediction" \
    "$BUILD" "${fast[@]+"${fast[@]}"}" "$phase" "$work/spec.md" "$testpath" "$slot4" "$prediction")"
  [[ "$smuggled_prompt" == *"$prediction"* ]] \
    && problems="$problems; verify-$phase carries the prediction text"
  grep -qiE 'PREDICTED_FAILURE|PREDICTION' <<<"$smuggled_prompt" \
    && problems="$problems; verify-$phase asks for a prediction"
done
[[ -z "$problems" ]] && ok || no "no verifier prompt carries the prediction (${problems#; })"

# 16. verify-refactor is given a range, as a sha and nothing else (#151). It judged only the
#     settled state, so churn and improvement looked the same and a loosened test was
#     invisible. For the refactor phase the 4th positional is <base-sha>, the step's green
#     commit, and it must reach the prompt so the verifier can read the diff from it. The sha
#     is one that appears in neither the spec nor the test path, so only the argument can
#     have put it there.
base_sha='3f9a1c07e2b4'
with_base="$("$BUILD" --fast-cmd 'make unit' refactor "$work/spec.md" "$testpath" "$base_sha")"; code=$?
[[ "$code" -eq 0 ]] && [[ "$with_base" == *"$base_sha"* ]] \
  && ok || no "verify-refactor carries the base sha from its 4th argument into the prompt (exit $code)"

# 17. only a sha can arrive in that slot (#151). The argument must match ^[0-9a-f]{7,40}$;
#     anything else is exit 2 with a diagnostic on stderr, because a slot that accepted free
#     text would be exactly the rationale channel ADR-0003 refuses. Each bad value probes one
#     edge of the pattern — absent, too short, uppercase, a sha with prose after it, too long —
#     and each accumulates its own miss, for case 12's reason.
problems=""
probe_base() {  # probe_base <label> [<base-sha>]
  local label="$1"; shift
  local err="$work/base-sha.err" rc
  "$BUILD" --fast-cmd 'make unit' refactor "$work/spec.md" "$testpath" "$@" >/dev/null 2>"$err"; rc=$?
  if [[ "$rc" -ne 2 || ! -s "$err" ]]; then
    problems="$problems; $label: exit $rc, stderr $([[ -s "$err" ]] && echo present || echo empty)"
  fi
}
probe_base missing
probe_base short abc123
probe_base uppercase 3F9A1C07E2B4
probe_base with-text '3f9a1c07e2b4 because it tidies'
probe_base too-long 3f9a1c07e2b43f9a1c07e2b43f9a1c07e2b43f9a1
[[ -z "$problems" ]] && ok \
  || no "verify-refactor refuses a missing or malformed base sha with exit 2 and a stderr diagnostic (${problems#; })"

# 18. the sha is there to be diffed from, and the diff is all the range may say (#151). The
#     refactor verifier reviews `git diff <base-sha>..HEAD` with the sha case 16 passed filled
#     in, and is told not to read the range's commit messages: `git log` and `git show` on
#     the range would carry the author's rationale, the one input ADR-0003 keeps out. Each
#     half is its own miss, for case 12's reason, and both are probed through `prompt_says`,
#     whose fold keeps a rewrap from splitting `commit messages` across a line.
problems=""
prompt_says "$with_base" "never names git diff $base_sha..HEAD" -F -e "git diff $base_sha..HEAD"
prompt_says "$with_base" "never forbids reading the range's commit messages" \
  -iE -e "(never|not|don't|no)[^.]{0,80}commit messages"
[[ -z "$problems" ]] && ok \
  || no "verify-refactor reviews git diff <base-sha>..HEAD and not the range's commit messages (${problems#; })"

# 19. what the diff is read for (#151). A test assertion the range removed or weakened is a
#     REJECT that names the assertion — the suite stays green while it loosens, so the diff is
#     the only place it shows. A hunk that is only cosmetic is named in REASON: and is not a
#     REJECT by itself, since a REJECT costs a revise leaf. And an empty range, which a reset
#     of the leaf's commits leaves, is not a REJECT by itself either. Each claim is its own
#     miss, for case 12's reason, probed within one sentence (`[^.]`) through `prompt_says`.
problems=""
prompt_says "$with_base" "never makes a removed or weakened test assertion a REJECT" \
  -iE -e "(removed|weakened)[^.]{0,80}assertion[^.]{0,120}REJECT|REJECT[^.]{0,120}(removed|weakened)[^.]{0,80}assertion"
prompt_says "$with_base" "never has the REJECT name the assertion" \
  -iE -e "REJECT[^.]{0,120}nam(e|es|ing)[^.]{0,40}assertion"
prompt_says "$with_base" "never names cosmetic-only hunks in REASON:" \
  -iE -e "cosmetic[^.]{0,160}REASON:"
prompt_says "$with_base" "never says a cosmetic-only hunk is not a REJECT by itself" \
  -iE -e "cosmetic[^.]{0,200}(not|never|no)[^.]{0,60}REJECT"
prompt_says "$with_base" "never says an empty range is not a REJECT by itself" \
  -iE -e "empty (range|diff)[^.]{0,160}(not|never|no)[^.]{0,60}REJECT"
[[ -z "$problems" ]] && ok \
  || no "verify-refactor rejects a weakened assertion by name, names cosmetic hunks without rejecting, and does not reject an empty range (${problems#; })"

# 20. every verifier is told which criterion it is judging (#223). The spec is the whole issue
#     body, so a nine-step issue hands every verifier all nine criteria, and a refactor verdict
#     on step 2 once demanded step 5's behaviour (#113). An optional `--step '<STEP>'` before
#     the positionals carries the ledger's own line: every phase exits 0 with it, shows the
#     step text, and says the verdict is about that criterion only. The step text appears in
#     neither the spec nor the test path, so only the flag can have put it there. Each phase
#     accumulates its own misses, for case 12's reason.
step='frobnicate --dry-run prints the plan and writes nothing ⟦criterion 3⟧'
problems=""
for phase in red green refactor pin; do
  slot4=test_slugify_lowercases; [[ "$phase" == refactor ]] && slot4=0123abc  # a base sha (#151)
  fast_for "$phase"
  stepped="$("$BUILD" --step "$step" "${fast[@]+"${fast[@]}"}" "$phase" "$work/spec.md" "$testpath" "$slot4" 2>/dev/null)"; code=$?
  [[ "$code" -eq 0 ]] || problems="$problems; verify-$phase exits $code"
  [[ "$stepped" == *"$step"* ]] || problems="$problems; verify-$phase never shows the step"
  prompt_says "$stepped" "verify-$phase never says the verdict is about that criterion only" \
    -iE -e 'verdict[^.]{0,160}(criterion|step)[^.]{0,40}only|verdict[^.]{0,160}only[^.]{0,40}(criterion|step)'
done
[[ -z "$problems" ]] && ok \
  || no "--step shows the step in every verifier prompt and scopes the verdict to it (${problems#; })"

# 21. the step arrives by flag and by nothing else (#223). `VERI_STEP` rides on every leaf
#     launch, so from the builder's point of view the step under judgement is already in the
#     environment and reading it there would save the conductor a flag — and would hand every
#     verifier a scope no caller asked for, including a resumed run whose conductor passes
#     none. It is the same shape of leak cases 11, 14 and 15 close: a channel into the prompt
#     that the four documented positionals and the one documented flag do not account for. So
#     with `VERI_STEP` set and no `--step`, every phase builds the prompt it builds with the
#     variable unset — byte-identical, and carrying none of the variable's text.
#
#     The probe's value is a step no ledger here would write, so a leak reading it cannot
#     coincide with anything the templates already say. Two misses per phase, for case 12's
#     reason: the text appearing is a leak through the environment, while a prompt that
#     merely differs is the variable reaching the output some other way.
ambient_step='frobnicate --dry-run prints the plan and writes nothing ⟦criterion 9⟧'
problems=""
for phase in red green refactor pin; do
  slot4=test_slugify_lowercases; [[ "$phase" == refactor ]] && slot4=0123abc  # a base sha (#151)
  fast_for "$phase"
  unset_arm="$(env -u VERI_STEP "$BUILD" "${fast[@]+"${fast[@]}"}" "$phase" "$work/spec.md" "$testpath" "$slot4")"
  ambient_arm="$(VERI_STEP="$ambient_step" "$BUILD" "${fast[@]+"${fast[@]}"}" "$phase" "$work/spec.md" "$testpath" "$slot4")"
  [[ "$ambient_arm" == *"$ambient_step"* ]] \
    && problems="$problems; verify-$phase carries the ambient VERI_STEP text"
  [[ "$ambient_arm" == "$unset_arm" ]] \
    || problems="$problems; verify-$phase differs from the prompt built with VERI_STEP unset"
done
[[ -z "$problems" ]] && ok \
  || no "VERI_STEP in the environment with no --step reaches nothing (${problems#; })"

# 22. a shortfall against a criterion OUTSIDE the step under judgement is a note, not a
#     REJECT (#223). This is the half of the fix case 20 cannot reach: telling the verifier
#     which criterion is in scope leaves it free to reject for one that is not, which is the
#     chain that bailed #113 step 2 — verdict 2 demanded the spec's later guard, verdict 3
#     rejected the code that added it as new behaviour in a refactor, and no revise leaf could
#     satisfy both. So verify-refactor must route that shortfall the way case 19 routes a
#     cosmetic hunk: named in REASON:, and not a REJECT by itself. Each half is its own miss,
#     for case 12's reason — a template that mentions out-of-scope work without saying it
#     stops short of a REJECT leaves the loop exactly where it was — and both are probed
#     within one sentence (`[^.]`) through `prompt_says`, whose fold keeps a rewrap from
#     splitting `out of scope` across a line. The prompt read is the stepped one, since a
#     verifier with no step in scope has no outside to speak of; its step text carries no form
#     of the words probed for, so only the template can match.
scoped_refactor="$("$BUILD" --step "$step" --fast-cmd 'make unit' refactor "$work/spec.md" "$testpath" "$base_sha")"
problems=""
prompt_says "$scoped_refactor" "never sends a shortfall against a criterion outside the step to REASON: as out of scope" \
  -iE -e "out of scope[^.]{0,200}REASON:|REASON:[^.]{0,200}out of scope"
prompt_says "$scoped_refactor" "never says an out-of-scope shortfall is not by itself a REJECT" \
  -iE -e "outside[^.]{0,240}(not|never|no)[^.]{0,80}REJECT|out of scope[^.]{0,240}(not|never|no)[^.]{0,80}REJECT"
[[ -z "$problems" ]] && ok \
  || no "verify-refactor notes an out-of-scope shortfall in REASON: rather than rejecting for it (${problems#; })"

# 23. every phase's built prompt forbids changing global or user-level configuration, and
#     names environment variables and throwaway directories as the way to simulate a
#     condition instead (issue #276). On 2026-09-17 a verify-refactor leaf proving `make test`
#     makes no network call ran `git config --global http.proxy http://127.0.0.1:1` behind a
#     `trap` that never fired, and every network git operation on the machine failed until the
#     key was found by chance. The leaf's goal was legitimate — simulating a condition is part
#     of verifying — so the prohibition alone would leave the need unmet, and the alternative
#     is half of the behaviour, as it is in case 13: each half is its own miss, and so is each
#     phase, for case 12's reason.
#
#     Reads cases 5, 6, 7 and 9's prompts and invokes the builder not at all, as cases 12 and
#     13 do. The prohibition is probed within one sentence (`[^.]`) so a "never" elsewhere in
#     the paragraph cannot stand in for it; "throwaway" alone is not enough, since case 13's
#     "throwaway checkout" already carries the word, so the probe asks for a directory.
forbids_global_config() {  # forbids_global_config <phase label> <prompt>
  local label="$1" prompt="$2"
  prompt_says "$prompt" "verify-$label never forbids changing global or user-level configuration" \
    -iE -e "(never|do not|don't|not)[^.]{0,80}(global|user-level)[^.]{0,60}config"
  prompt_says "$prompt" "verify-$label never names environment variables as the way to simulate a condition" \
    -iE -e 'environment variables?'
  prompt_says "$prompt" "verify-$label never names throwaway directories as the way to simulate a condition" \
    -iE -e '(throwaway|temporary|scratch)[^.]{0,20}director(y|ies)'
}

every_phase forbids_global_config "every phase's prompt forbids changing global or user-level configuration and names environment variables and throwaway directories instead"

# 24. verify-red and verify-pin REJECT a test that pins mechanism instead of behaviour
#     (issue #331). #331's "at most N python3" was satisfied by a leaf adding suites that
#     re-ran whole suites under a counting shim (+41s of `make test`); #333's "launches
#     overlap" made a suite twice as slow. The blind verifier is the only backstop once the
#     developer prompt's own rule (case 26 of build-develop-prompt.test.sh) is ignored or
#     misjudged, so both verify-red and verify-pin need the same three REJECT reasons: a
#     process/fork count or a timing asserted directly, a `PATH` shim counting real
#     processes where an in-process spy on a named call would do, and a test that runs
#     another suite (or its own again) instead of the unit. Two prompts, one criterion, so
#     one case; the reads are cases 1 and 9's — same phase, same arguments — so no new
#     invocation.
problems=""
mechanism_reject() {  # mechanism_reject <phase label> <prompt>
  local label="$1" prompt="$2"
  prompt_says "$prompt" "verify-$label never rejects a test that pins a process/fork count or a timing" \
    -iE -e '(process|fork)[^.]{0,20}count|timing'
  prompt_says "$prompt" "verify-$label never carves out an in-process spy for a call count the criterion names" \
    -iE -e 'in-process spy'
  prompt_says "$prompt" "verify-$label never rejects a PATH shim counting real processes over a spy" \
    -iE -e 'PATH[^.]{0,60}shim|shim[^.]{0,60}(count|real process)'
  prompt_says "$prompt" "verify-$label never rejects a test that runs another suite or re-runs its own" \
    -iE -e '(runs?|running)[^.]{0,40}(another|other)[^.]{0,20}suite|re-runs?[^.]{0,30}suite'
}
mechanism_reject red "$red"
mechanism_reject pin "$pin"
[[ -z "$problems" ]] && ok \
  || no "verify-red and verify-pin reject mechanism-pinning tests (process/fork/timing, a PATH shim over an in-process spy, or running another suite) (${problems#; })"

# 25. verify-green takes the fast tier's command by flag, and requires it (issue #341).
#     verify-green now runs the fast command plus the affected suites instead of the full
#     suite, and a verifier in a target repository has no `detect-test-command.sh` of its own
#     to ask — so the conductor passes the command in, as `--fast-cmd '<cmd>'` before the
#     positionals the way `--step` arrives, leaving case 11's four positionals the whole of
#     the positional input. The prompt carries it verbatim, `&`, `/` and quotes included.
#     Without it the verifier would be told to run a command nobody named, so a green call
#     short of it is a bad-arguments case: exit 2, a diagnostic on stderr. `problems` says
#     which half broke.
fast_cmd='make unit ZORBLAT=fast -- --only "frob & nitz/quux"'
problems=""
fast_green="$("$BUILD" --fast-cmd "$fast_cmd" green "$work/spec.md" "$testpath" test_slugify_lowercases 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] || problems="$problems; with --fast-cmd exited $code, want 0"
[[ "$fast_green" == *"$fast_cmd"* ]] || problems="$problems; the prompt does not carry --fast-cmd's value verbatim"
"$BUILD" green "$work/spec.md" "$testpath" test_slugify_lowercases >/dev/null 2>"$work/fast-cmd.err"; code=$?
[[ "$code" -eq 2 && -s "$work/fast-cmd.err" ]] \
  || problems="$problems; without --fast-cmd: exit $code, stderr $([[ -s "$work/fast-cmd.err" ]] && echo present || echo empty), want exit 2 and a diagnostic"
[[ -z "$problems" ]] \
  && ok || no "verify-green takes --fast-cmd, carries it verbatim, and refuses a green call without it with exit 2 (${problems#; })"

# 26. verify-red accepts an error on exactly the name the step introduces as a valid red
#     (issue #355). In bash, Python or JS, calling a name that does not exist errors before
#     any assertion runs, so check 1's "must fail, not error before it reaches its
#     assertions" and check 2's "an absent function/route/field" ruled opposite ways on the
#     same test, and two verifiers spent a revise leaf on the difference. Beck counts a test
#     that does not compile as red, so the prompt must say so — and must say which names
#     qualify, since a bash step introduces a missing script or file far more often than a
#     route. The read is case 1's `$red`, so no new invocation.
problems=""
prompt_says "$red" "verify-red never says an error on exactly the name the step introduces is a valid red" \
  -iE -e "error[^.]{0,160}(exactly the name|the exact name)[^.]{0,200}(valid|legitimate) red|(valid|legitimate) red[^.]{0,200}error[^.]{0,160}(exactly the name|the exact name)"
prompt_says "$red" "verify-red never says a missing script or file is one of the names that qualify" \
  -iE -e "(missing|absent)[^.]{0,120}(script|file)[^.]{0,120}(route|field)"
[[ -z "$problems" ]] && ok \
  || no "verify-red accepts an error on exactly the name the step introduces as a valid red (${problems#; })"

# 27. and the other half of the same sentence stays put (issue #355). Widening check 1 to
#     accept an error on the name the step introduces must not widen it to accept every
#     error before an assertion: a typo'd name, a wrong path, a missing fixture and a
#     syntax error in the test are each still a REJECT, and each is a way a test reaches
#     Green looking red. Each claim is its own miss, for case 12's reason; the read is
#     case 1's `$red`, so no new invocation.
problems=""
prompt_says "$red" "verify-red never says any other error before an assertion is a REJECT" \
  -iE -e "any [^.]{0,20}other[^.]{0,20} error[^.]{0,60}before[^.]{0,40}assertion[^.]{0,80}REJECT"
prompt_says "$red" "verify-red names no typo'd name among the errors it still rejects" \
  -iE -e "typo"
prompt_says "$red" "verify-red names no wrong path among the errors it still rejects" \
  -iE -e "wrong path|incorrect path|path that does not exist"
prompt_says "$red" "verify-red names no missing fixture among the errors it still rejects" \
  -iE -e "(missing|absent) fixture"
prompt_says "$red" "verify-red names no syntax error among the errors it still rejects" \
  -iE -e "syntax error"
[[ -z "$problems" ]] && ok \
  || no "verify-red still rejects any other error before an assertion: a typo'd name, a wrong path, a missing fixture, a syntax error (${problems#; })"

# 28. and check 1 no longer requires the target test to reach its assertions (issue #355).
#     The sentence case 26 widened was one half of a contradiction; this is the other half
#     going away. While check 1 still demanded a failure that does not "error before it
#     reaches its assertions", a verifier reading it had a rule that contradicts check 2's
#     valid-red sentence outright, and the run turns on which of the two a given model reads
#     first. So the claim is an absence, and the probe is its own: `prompt_says` reports a
#     claim that is missing, and what must be named here is a claim that is present. The
#     pattern matches the requirement, not the valid-red explanation that legitimately uses
#     the same words — "a test that cannot even reach its assertions for that reason is red"
#     says the opposite and must stay. Folded to one line for `prompt_says`'s own reason: a
#     requirement rewrapped across a line break would otherwise read as already gone. The
#     read is case 1's `$red`, so no new invocation.
problems=""
one_line="$(tr '\n' ' ' <<<"$red")"
grep -qiE -e "(must|has to|should)[^.]{0,100}not error before[^.]{0,60}assertion" <<<"$one_line" \
  && problems="$problems; verify-red still forbids a failure that errors before it reaches its assertions"
grep -qiE -e "(must|has to|should)[^.]{0,100}reach(es)? its assertions" <<<"$one_line" \
  && problems="$problems; verify-red still requires the target test to reach its assertions"
[[ -z "$problems" ]] && ok \
  || no "verify-red no longer requires the target test to reach its assertions (${problems#; })"

# 29. verify-green REJECTs production code no test requires (issue #357). develop-green
#     asks for the minimum code, but verify-green's three checks — the target passes, the
#     fast command and the affected suites are green, the pass is genuine — never ask
#     whether any of the code the leaf wrote was needed. Code no test requires is caught
#     only at verify-refactor, a step later, after it has been committed as `feat:` and the
#     ledger ticked. So the green prompt names the fourth check itself: a branch, option,
#     flag or parameter whose removal leaves every test green is a REJECT, and `REASON:`
#     names that code, since a verdict that says "something is unneeded" costs the revise
#     leaf a search the verifier already did. Each claim is its own miss, for case 12's
#     reason; the read is case 6's `$green` — same phase, same arguments — so no new
#     invocation.
problems=""
prompt_says "$green" "verify-green never makes production code no test requires a REJECT" \
  -iE -e "REJECT[^.]{0,200}code[^.]{0,80}no test requires|code[^.]{0,80}no test requires[^.]{0,200}REJECT"
prompt_says "$green" "verify-green never names a branch, option, flag or parameter as the code it means" \
  -iE -e "branch[^.]{0,80}option[^.]{0,80}flag[^.]{0,80}parameter"
prompt_says "$green" "verify-green never says removing it leaves every test green" \
  -iE -e "remov(e|ed|ing|al)[^.]{0,140}(leaves?|leaving)[^.]{0,60}tests? green|remov(e|ed|ing|al)[^.]{0,140}(every|all) tests? [^.]{0,40}green"
prompt_says "$green" "verify-green never has REASON: name that code" \
  -iE -e "REASON:?[^.]{0,160}nam(e|es|ing)[^.]{0,60}code|nam(e|es|ing)[^.]{0,60}code[^.]{0,160}REASON"
[[ -z "$problems" ]] && ok \
  || no "verify-green REJECTs production code no test requires and names it in REASON: (${problems#; })"

# 30. and it tells the verifier how to establish that (issue #357). A fourth check the
#     verifier answers by reading would be a guess: "no test requires this" is a claim
#     about every test, and the only thing that settles it is removing the code and
#     watching the suite stay green. So the prompt names the procedure verify-pin already
#     names for its mutation — remove it, run the suite, put the tree back with `git
#     checkout --` and confirm with `git diff --exit-code` — and says the restore happens
#     before the verdict is reported, because a verifier that reports first leaves the
#     developer's tree mutated for the next leaf. Each claim is its own miss, for case 12's
#     reason; the read is case 6's `$green`, so no new invocation.
problems=""
prompt_says "$green" "verify-green never says to remove the code and run the suite" \
  -iE -e "remov(e|ing)[^.]{0,120}run[^.]{0,80}suite"
prompt_says "$green" "verify-green never says to restore the tree afterwards" \
  -iE -e "restor(e|ing)[^.]{0,80}(tree|code|file)"
prompt_says "$green" "verify-green never says to confirm the restore with git diff --exit-code" \
  -iE -e "git diff[[:space:]]+--exit-code"
prompt_says "$green" "verify-green never says the restore comes before reporting" \
  -iE -e "before[^.]{0,60}report"
[[ -z "$problems" ]] && ok \
  || no "verify-green tells the verifier to remove the code, run the suite, and restore the tree before reporting (${problems#; })"

# 31. the cycle's files, and the one a transform may leave them for (issue #358). Case 30 of
#     build-develop-prompt.test.sh lets a transform touch a file outside the touched-files
#     list when — and only when — it removes duplication between that file and code this
#     cycle wrote. The verifier judging that transform has no touched-files list: it is given
#     a base sha, so it derives the cycle's files itself, as `git diff --name-only
#     <base-sha>^ <base-sha>`. That is a list of paths and nothing else, so blindness holds
#     (ADR-0003) — no rationale can ride in on a file name. A changed file outside that list
#     is then a REJECT, unless its hunk removes duplication with code in the list, which is
#     the developer prompt's exception read back. Three claims, three misses, for case 12's
#     reason: the derivation without the rule leaves the verifier a list it does nothing
#     with, and the rule without its exception rejects exactly the transform #358 permits.
#     The prompt read is case 16's `$with_base` — same phase, same arguments — so no new
#     invocation, and the sha is the one case 16 established only the argument can supply.
#     The REJECT probe names the list rather than `outside` alone, because check 6's
#     out-of-scope sentence already puts `outside` within a clause of `REJECT` and would
#     answer a looser probe. `duplication` and `--name-only` appear nowhere in the prompt
#     built today, checked against the built prompt rather than the template.
problems=""
prompt_says "$with_base" "never names git diff --name-only $base_sha^ $base_sha" \
  -F -e "git diff --name-only $base_sha^ $base_sha"
prompt_says "$with_base" "never makes a changed file outside that list a REJECT" \
  -iE -e "outside[^.]{0,80}list[^.]{0,160}REJECT|REJECT[^.]{0,160}outside[^.]{0,80}list"
prompt_says "$with_base" "never spares the hunk that removes duplication with code in the list" \
  -iE -e "(unless|except)[^.]{0,160}duplication|duplication[^.]{0,160}(unless|except)"
[[ -z "$problems" ]] && ok \
  || no "verify-refactor derives the cycle's files as git diff --name-only <base-sha>^ <base-sha> and REJECTs a changed file outside that list unless its hunk removes duplication with code in it (${problems#; })"

# 32. an unhandled edge case the spec implies is a finding on a FLAGS: line, not a REJECT
#     (issues #362, #175). Check 2 asks for code that is "reasonably robust (no obvious
#     unhandled edge case the spec implies)", and handling an edge case changes behaviour —
#     so a REJECT on that ground can only be met by the untested behaviour change
#     develop-refactor forbids, and the revise leaf either fails or smuggles one in. Beck's
#     answer to a missing case is a new test. #362 wrote that finding as a `NEW_STEP:` line;
#     #175 took that token away, because every such line became a whole ledger step whatever
#     it named, so the finding now rides on the refactor leaf's own `FLAGS:` line (case 43
#     pins the line and its classes), written before the final `VERDICT:`/`REASON:` pair.
#     Classing a finding reveals no developer reasoning, so blindness holds (ADR-0003).
#
#     Three claims, three misses, for case 12's reason: the line without the edge case it
#     answers is a line the verifier fills with anything, the placement is what keeps
#     parse-verdict.sh reading the final pair, and the line arriving while the REJECT stays
#     leaves the verdict that #362 exists to remove. The prompt read is case 7's `$refactor`
#     — same phase, same arguments — so there is no new invocation, and case 7 owns the
#     build.
problems=""
prompt_says "$refactor" "verify-refactor never ties FLAGS: to an unhandled edge case the spec implies" \
  -iE -e "unhandled edge case[^.]{0,200}FLAGS|FLAGS[^.]{0,200}unhandled edge case"
prompt_says "$refactor" "verify-refactor never puts the FLAGS: line before the VERDICT: line" \
  -iE -e "FLAGS[^.]{0,120}before[^.]{0,120}VERDICT"
prompt_says "$refactor" "verify-refactor never says an unhandled edge case is not a REJECT" \
  -iE -e "(edge case|robust)[^.]{0,200}not( by itself)? a REJECT|not( by itself)? a REJECT[^.]{0,200}(edge case|robust)"
[[ -z "$problems" ]] && ok \
  || no "verify-refactor reports an unhandled edge case the spec implies as a FLAGS: line before VERDICT: rather than a REJECT (${problems#; })"

# 33. every phase's built prompt allows FLAGS: lines before the final pair (issues #362,
#     #175). The footer every verifier writes is the conductor's whole reading of the leaf,
#     and it says to end with EXACTLY the two lines and nothing after them. Case 32 has the
#     refactor verifier report an unhandled edge case on a `FLAGS:` line before that pair —
#     a line the contract as written does not admit, so the verifier is told to break the
#     contract to obey the check. The contract is what has to give: `FLAGS:` lines are
#     allowed ahead of the final two, and the final two stay last, which is what keeps
#     parse-verdict.sh reading the same verdict and reason as before. #362 made that
#     allowance for `NEW_STEP:`; #175 retired the token (case 43), and the allowance moves
#     with the finding rather than staying behind as a line no check asks for.
#
#     Asked of all four phases, not just refactor, because the contract lives in _shared.md
#     and a phase that kept the older footer would carry a rule contradicting the one the
#     run acts on — and because the refactor leaf reports on this token too, so any
#     verifier may be handed output carrying it. Assert on the built prompts rather than on
#     _shared.md, for case 12's reason: the behaviour is the rule reaching every phase, not
#     which file holds it.
#
#     Two claims, two misses per phase: a prompt naming the line without permitting it
#     still forbids the line it asks for, and permission without the placement leaves
#     parse-verdict.sh's final pair unguarded. The prompts read are cases 5, 6, 7 and 9's —
#     same phases, same arguments — so this case invokes the builder not at all, and folds
#     through `prompt_says` for the reason given at its definition.
allows_flags() {  # allows_flags <phase label> <prompt>
  local label="$1" prompt="$2"
  prompt_says "$prompt" "verify-$label's output contract never allows a FLAGS: line" \
    -iE -e "FLAGS[^.]{0,200}(may|can|allow|permit)|(may|can|allow|permit)[^.]{0,200}FLAGS"
  prompt_says "$prompt" "verify-$label never puts FLAGS: lines before the final VERDICT:/REASON: pair" \
    -iE -e "FLAGS[^.]{0,160}before[^.]{0,160}(VERDICT|(final|last)[^.]{0,40}two lines)"
}

every_phase allows_flags "every phase's prompt allows FLAGS: lines before the final VERDICT:/REASON: pair"

# 34. the builder accepts a fifth phase, `plan`, and builds its prompt from the issue spec
#     and the ledger named in the third positional (#439). The plan is the one artifact a
#     run never verifies: a planning leaf's paraphrase silently becomes the definition of
#     done, which is how #426 shipped every step ticked and its criterion unmet. The phase
#     is a verifier like the other four, so it is built here, from the same two kinds of
#     on-disk artifact — and the third slot, which for a cycle phase names the test under
#     review, for `plan` names the proposed ledger.
#
#     The assertion is that the ledger's own text reaches the prompt, not merely its path:
#     a verifier told only where the plan lives, in a target repository, judges a file it
#     was never given. Spec and ledger are both checked, because a prompt carrying one
#     without the other cannot answer the question the phase exists to ask — do the steps
#     tagged for a criterion together deliver it?
cat > "$work/ledger.md" <<'LEDGER'
# Plan for #426

- [ ] A verdict launcher script runs verify.sh with the step title as an argument ⟦criterion 1⟧
LEDGER
plan="$("$BUILD" plan "$work/spec.md" "$work/ledger.md")"; code=$?
[[ "$code" -eq 0 ]] \
  && [[ "$plan" == *'slugify("Hello & World/Foo")'* ]] \
  && [[ "$plan" == *'A verdict launcher script runs verify.sh with the step title as an argument ⟦criterion 1⟧'* ]] \
  && ok || no "verify-plan carries the issue spec and the ledger named as its third argument (exit $code)"


# 35. a plan call that names no ledger, or names one the builder cannot read, refuses with
#     exit 2 and nothing on stdout (#439). The plan phase's third positional is the one
#     input the other four phases never read off disk — for them it is a path the verifier
#     opens itself, for `plan` it is text this builder reads — so it is also the one that
#     can fail here rather than in the leaf. Exit 2 is the code for "no answer could be
#     obtained": a prompt was asked for and none exists, which is a system failure, never
#     the clean negative 1 that a verdict of REJECT is spelled with. The silent stdout is
#     the other half: a builder that printed a half-substituted prompt and exited non-zero
#     would hand run-leaf.sh a template with {{LEDGER}} still in it, and the verifier would
#     judge a plan it was shown a placeholder of.
no_ledger="$("$BUILD" plan "$work/spec.md" 2>/dev/null)"; code=$?
missing_ledger="$("$BUILD" plan "$work/spec.md" "$work/absent-ledger.md" 2>/dev/null)"; missing_code=$?
[[ "$code" -eq 2 && -z "$no_ledger" ]] \
  && [[ "$missing_code" -eq 2 && -z "$missing_ledger" ]] \
  && ok || no "verify-plan refuses a call naming no ledger or an unreadable one with exit 2 and no stdout (no ledger: exit $code, ${#no_ledger} bytes; unreadable: exit $missing_code, ${#missing_ledger} bytes)"


# 36. the plan prompt asks the question the phase exists for — do the steps tagged
#     ⟦criterion k⟧ together deliver criterion k *as written* — and binds a REJECT to name
#     both the criterion and the part of it no step covers (#439). A verifier merely handed
#     a spec and a ledger would grade the plan on whatever it thought planning meant; the
#     failure #426 shipped was a plan that restated criterion 1 as two mechanism steps, each
#     true of the delivered work while the criterion itself stayed unmet, so "together" and
#     "as written" are the two words that make the question answerable at all: one step of a
#     pair is never the unit, and the criterion's own terms are the standard rather than the
#     plan's paraphrase of them. The REJECT half is what makes the verdict actionable — the
#     scoping step rewrites the plan from that reason, and "the plan is too narrow" names
#     nothing to rewrite. Three claims, three misses, so a prompt that asks the question and
#     leaves the reason unconstrained is named for what it dropped rather than covered for
#     by what it kept. Matched over the newline-flattened prompt, tolerantly of wording and
#     of markdown emphasis, since the behaviour is the instruction reaching the verifier,
#     not the sentence it is spelled with. Every bounded repetition stays under 255: BSD
#     grep refuses a larger one outright ("maximum repetition exceeds 255"), and a refused
#     grep exits non-zero, which `prompt_says` cannot tell from a prompt that says nothing —
#     so an over-wide window is an assertion that can only ever miss.
problems=""
prompt_says "$plan" "never asks whether the steps tagged for a criterion together deliver it" \
  -iE -e 'together[^.]{0,200}deliver|deliver[^.]{0,200}together'
prompt_says "$plan" "never sets the criterion's own wording as the standard" \
  -iE -e 'as written|in its own terms|the criterion.{0,20}own (words|terms|wording)'
prompt_says "$plan" "never requires a REJECT reason to name the criterion and what no step covers" \
  -iE -e 'REJECT[^.]{0,120}(name|identif|say|state)[^.]{0,200}criterion[^.]{0,200}(no step|nothing[^.]{0,40}cover|uncovered)'
[[ -z "$problems" ]] && ok || no "verify-plan asks whether the steps tagged for a criterion together deliver it as written, and binds a REJECT reason to the criterion and the part no step covers (${problems#; })"


# 37. the plan prompt directs a PASS when every criterion is delivered by the steps tagged
#     for it (#439). The shared preamble only ever states the necessary half — "use PASS
#     only if every check below holds" — which tells a verifier when it may not pass and
#     never when it must. On this phase that gap is not academic: the subject is a plan, an
#     artifact of judgement, and a verifier with no stated sufficient condition grades it
#     against the plan it would have written itself, so a sound plan taking an approach the
#     verifier dislikes comes back REJECT and the scoping step rewrites work that was
#     already right. The plan phase is the run's cheapest verification precisely because it
#     runs once and then gets out of the way; a REJECT it cannot justify from the spec costs
#     a whole re-plan. So the prompt has to close the biconditional in the phase's own terms
#     — every criterion delivered by the steps tagged for it IS the PASS — rather than leave
#     the verifier to infer it from a rule about "checks". Matched over the newline-flattened
#     prompt, tolerantly of wording, for the reason given at `prompt_says`; the window stays
#     under 255 because BSD grep refuses a wider repetition outright and its non-zero exit
#     reads exactly like a prompt that says nothing.
problems=""
prompt_says "$plan" "never directs a PASS when every criterion is delivered by the steps tagged for it" \
  -iE -e 'PASS[^.]{0,200}every criterion[^.]{0,200}(deliver|cover)|every criterion[^.]{0,200}(deliver|cover)[^.]{0,200}PASS'
[[ -z "$problems" ]] && ok || no "verify-plan directs a PASS when every criterion is delivered by the steps tagged for it (${problems#; })"


# 38. the plan prompt makes a step too big for one Red → Green → Refactor cycle a named
#     one, under either verdict (#439). Criterion coverage and step size are two different
#     failures of the same artifact, and only the first has a verdict attached to it: a plan
#     whose steps do together deliver every criterion is a PASS by check 1, and saying so is
#     the whole of that check, so a step that quietly bundles three cycles' work into one
#     line rides out on that PASS with nothing recorded. It is not a REJECT either — the
#     plan is not wrong about what it delivers, and sending it back to be rewritten over a
#     size estimate would spend a re-plan on a judgement call. What is left is the reason
#     line, which the conductor and the human both read whichever way the verdict goes: it
#     is the only place an observation can land that neither passes nor fails a plan. So the
#     duty is on the reason and is verdict-independent — "whether PASS or REJECT" is the
#     load-bearing half, because a naming rule stated only for REJECT names nothing on the
#     runs this phase actually passes, which is most of them. Three claims — the size
#     judgement, the reason as its destination, the independence from the verdict — so three
#     misses, each named, for case 36's reason. Matched over the newline-flattened prompt,
#     tolerantly of wording, through `prompt_says`; `reason\b` rather than bare `reason`
#     because the shared preamble's blindness clause says "the author's reasoning", and a
#     probe a substring of that word satisfies would pass against a prompt that never
#     mentions a step's size at all. Every window stays well under 255, for case 36's
#     reason — a grep that refuses its own pattern exits non-zero and reads here exactly
#     like a prompt that says nothing.
problems=""
prompt_says "$plan" "never judges a step too big for one Red → Green → Refactor cycle" \
  -iE -e '(too (big|large)|too much|does not fit|not fit)[^.]{0,150}cycle'
prompt_says "$plan" "never sends that step's name to the reason" \
  -iE -e '(name|names|say so|state)[^.]{0,100}(REASON:|reason\b)'
prompt_says "$plan" "never holds the duty whether the verdict is PASS or REJECT" \
  -iE -e '(whether|either way|regardless)[^.]{0,100}(PASS|REJECT|verdict)'
[[ -z "$problems" ]] && ok || no "verify-plan requires a step too big for one Red → Green → Refactor cycle to be named in the reason under either verdict (${problems#; })"


# 39. the plan prompt states that a step carrying no ⟦criterion k⟧ tag — a gap step — is
#     never by itself a reason to REJECT (#439). `SKILL.md:612-629` asks the planning leaf
#     for exactly such a step: a behaviour `## What to build` asks for that no acceptance
#     criterion covers gets a step of its own, phrased as a criterion of the planner's own
#     and deliberately left without a tag, because `criterion-finished.sh` reads that
#     notation to decide when a criterion may be ticked and a gap step belongs to none. A
#     verifier given check 1 alone — for each criterion k, do the steps tagged ⟦criterion k⟧
#     deliver it? — meets that step with no rule at all, and the reading available to it is
#     that the step is unaccounted for: a line in the plan serving no criterion. So the
#     well-formed plan `SKILL.md` asks for is the one this phase would send back, and the
#     instruction the planner already follows becomes the thing that fails verification —
#     which is worse than silence, since a REJECT costs a re-plan and the rewrite it asks
#     for is to delete work the issue's prose needs. Two claims and a qualifier, three
#     misses: the prompt must name the untagged step at all, must say it is not a REJECT,
#     and must say so *by itself* — the last is load-bearing rather than hedging, because a
#     gap step is not exempt from the plan's other duties, and an absolute "a gap step is
#     never a REJECT" would read as a clause that immunises whatever a planner leaves
#     untagged. Matched over the newline-flattened prompt through `prompt_says`, tolerantly
#     of wording, for case 36's reason; the not-REJECT and by-itself windows each require
#     REJECT in view so neither is satisfied by a sentence about something else. Every
#     bounded repetition stays under 255, also for case 36's reason — BSD grep refuses a
#     wider one, and a refused grep is indistinguishable here from a prompt that says
#     nothing.
problems=""
gap_step='gap step|untagged|no[^.]{0,20}criterion[^.]{0,20}tag'  # the untagged step, named once for the two probes that look for it
prompt_says "$plan" "never names a step carrying no criterion tag" \
  -iE -e "$gap_step|(carries|carrying|with|without|has) no[^.]{0,40}criterion"
prompt_says "$plan" "never says such a step is not a REJECT" \
  -iE -e "($gap_step)[^.]{0,200}(not|never|no)[^.]{0,80}REJECT"
prompt_says "$plan" "never carries the by-itself qualifier on that exemption" \
  -iE -e '(by itself|on its own|alone|in itself)[^.]{0,100}REJECT|REJECT[^.]{0,100}(by itself|on its own|alone|in itself)'
[[ -z "$problems" ]] && ok || no "verify-plan states that a step carrying no criterion tag is never by itself a reason to REJECT (${problems#; })"


# 40. the plan prompt carries the issue spec and the ledger and nothing else, and none of
#     the four cycle prompts carries a ledger (#439). The blindness guarantee this builder
#     exists to make structural is per phase, not per script: the plan phase is the one
#     verifier whose subject is an artifact of judgement, and it is admissible only because
#     at scoping time there is no developer and no rationale to leak. That holds as long as
#     nothing but the spec and the ledger reaches it — so the two channels a caller could
#     push anything else through are the ones checked here, `--step` and the fourth
#     positional: both are accepted by the builder's argument loop for the cycle phases that
#     need them, and a plan call carrying either must render a prompt neither appears in.
#     Not hypothetical — `--step` carries the ledger's own line for one step, which on a
#     re-plan is text about work already judged, and the fourth slot takes free text on
#     three of the four cycle phases.
#
#     The other half is the same guarantee read backwards: the ledger is the plan phase's
#     subject and nothing else's, so a cycle phase handed that same path must name it and
#     never open it. A cycle verifier shown the plan would grade code against the intended
#     design rather than against the criterion, which is exactly the leak ADR-0003 forbids
#     and the reason this issue does not simply pass the plan to the existing four. Each
#     cycle phase is asked for both halves — the path it was given still reaches it, and the
#     file's text does not — because a prompt that dropped the path would satisfy a
#     text-absence probe by carrying nothing at all. Every miss is named rather than folded
#     into one verdict, so a leak on one phase is not covered for by the other three.
cat > "$work/rationale-ledger.md" <<'LEDGER'
# Plan for #439

- [ ] LEDGER-BODY-MARKER a plan step no cycle verifier may be shown ⟦criterion 1⟧
LEDGER
leak_step='RATIONALE-LEAK the developer chose a launcher script because bash -c broke the quoting'
problems=""
plan_only="$("$BUILD" --step "$leak_step" plan "$work/spec.md" "$work/rationale-ledger.md" test_rationale_leak)"; code=$?
[[ "$code" -eq 0 ]] || problems="$problems; the plan call exited $code"
[[ "$plan_only" == *'slugify("Hello & World/Foo")'* ]] || problems="$problems; the plan prompt drops the issue spec"
[[ "$plan_only" == *'LEDGER-BODY-MARKER'* ]] || problems="$problems; the plan prompt drops the ledger"
[[ "$plan_only" != *'RATIONALE-LEAK'* ]] || problems="$problems; the plan prompt carries the --step text"
[[ "$plan_only" != *'test_rationale_leak'* ]] || problems="$problems; the plan prompt carries the fourth positional"
for phase in red green refactor pin; do
  fast_for "$phase"
  slot=test_slugify_lowercases
  [[ "$phase" == refactor ]] && slot=0123abc  # refactor's fourth slot takes a base sha only (#151)
  cycle="$("$BUILD" "${fast[@]}" "$phase" "$work/spec.md" "$work/rationale-ledger.md" "$slot")"
  [[ "$cycle" == *"$work/rationale-ledger.md"* ]] || problems="$problems; verify-$phase drops the path it was given"
  [[ "$cycle" != *'LEDGER-BODY-MARKER'* ]] || problems="$problems; verify-$phase carries the ledger's text"
done
[[ -z "$problems" ]] && ok || no "verify-plan carries only the issue spec and the ledger, and no cycle phase's prompt carries a ledger (${problems#; })"


# 41. the plan prompt treats a step that restates a criterion as a mechanism as delivering
#     it only when that mechanism is sufficient for the criterion as written, and directs a
#     REJECT when no step establishes the criterion as written (#439). Check 1 already tells
#     the verifier that a step true of "some mechanism the criterion might be built from is
#     not the criterion being delivered", which reads as a ban on mechanism steps — and a
#     plan is entitled to name mechanism: "a verdict launcher script" was the right design on
#     #426 and the plan naming it was not wrong for naming it. What made that plan pass while
#     its criterion stayed unmet is the thing this case pins instead: a mechanism step
#     delivers the criterion exactly when the mechanism it names is **sufficient** for the
#     criterion as written, and #426's two steps were not — a launcher that quotes the title
#     for the inner shell leaves the outer one untouched, so every step was true and the
#     criterion "a step title containing an apostrophe launches its verifier successfully,
#     for every phase" was false. A verifier given the ban alone has no test to apply to a
#     mechanism step; given sufficiency, it has the same test the criterion itself states.
#
#     The second half is the verdict that judgement has to reach. Check 1's REJECT clause
#     constrains the *reason* — name the criterion and the part no step covers — and a
#     constraint on a reason is not a direction to render the verdict: the prompt can be
#     satisfied by a PASS whose reason names nothing, because nothing told the verifier that
#     an unestablished criterion IS a REJECT. Case 37 closed the sufficient half of the
#     biconditional for PASS; this closes the other end, so the two cannot both be inferred
#     away. Two claims, two misses, each named, for case 36's reason. Matched over the
#     newline-flattened prompt, tolerantly of wording and of markdown emphasis, since the
#     behaviour is the instruction reaching the verifier rather than the sentence it is spelled
#     with; every bounded repetition stays under 255, for case 36's reason — BSD grep refuses
#     a wider one outright and its non-zero exit reads exactly like a prompt that says nothing.
problems=""
prompt_says "$plan" "never makes a mechanism step deliver the criterion only when that mechanism is sufficient for it" \
  -iE -e 'mechanism[^.]{0,200}(sufficient|suffices|enough)|(sufficient|suffices|enough)[^.]{0,200}mechanism'
prompt_says "$plan" "never directs a REJECT when no step establishes the criterion as written" \
  -iE -e 'REJECT[^.]{0,200}(no step|nothing)[^.]{0,150}(establish|deliver)|(no step|nothing)[^.]{0,150}(establish|deliver)[^.]{0,200}REJECT'
[[ -z "$problems" ]] && ok || no "verify-plan makes a mechanism step deliver a criterion only when the mechanism is sufficient for it as written, and directs a REJECT when no step establishes the criterion (${problems#; })"

# 42. the reproduction paragraph verify-red gains for a bug, and only for a bug (issue #112).
#     For an issue labelled `bug`, Red is a reproduction (ADR-0015): the developer's case must
#     fail with the behaviour the report describes, not with a missing symbol or a typo. The
#     blind verifier is the only party that checks that claim by running the test, so PASS has
#     to require the failure it observes to match *What happened*. The report reaches it
#     through the one channel there is — `capture-spec.sh` puts it in the blind spec under a
#     `## Bug` heading — so the paragraph is conditional on the spec carrying that section,
#     and a spec without one must not gain a word: a verifier told to compare against a report
#     nobody made has nothing to compare with.
#
#     The four parameters do not change for it, which is what the call below asserts by being
#     case 1's call — phase, spec file, test path, test id — with a different spec file. A
#     fifth, or a flag saying "this one is a bug", would be a channel the developer's rationale
#     could travel down, which is the guarantee this whole suite exists for (ADR-0003).
#
#     Probed through `prompt_says` under case 11's constraint — at most one bounded
#     `[^.]{0,N}` per alternation branch, every bound under 255 — and the probe pairs the
#     paragraph's verb with the spec part it names rather than the part name alone: the bug
#     spec is interpolated verbatim, so `### What happened` is in the prompt whatever the
#     template says, and a probe for the bare heading would pass on a template that gained
#     nothing. The fixture's four parts carry none of those verbs for the same reason.
cp "$work/spec.md" "$work/bug-spec.md"
cat >> "$work/bug-spec.md" <<'SPEC'

## Bug

### What happened

slugify returned "HELLO_WORLD" on the ampersanded seed.

### Expected

slugify returns "hello-world-foo".

### Steps to reproduce

Call slugify("Hello & World/Foo").

### Environment

veri on bash 5.2, macOS 15.
SPEC

problems=""
bug_red="$("$BUILD" red "$work/bug-spec.md" "$testpath" test_slugify_lowercases 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] || problems="$problems; with a bug spec and red's own four positionals exited $code, want 0"
[[ "$bug_red" == *'slugify returned "HELLO_WORLD" on the ampersanded seed.'* ]] \
  || problems="$problems; does not carry the bug report from the spec"
observed_matches_reported='(match|matches|matching|same as)[^.]{0,80}what happened|what happened[^.]{0,80}(match|matches|matching|same as)'
prompt_says "$bug_red" "never requires the failure it observes to match What happened" \
  -iE -e "$observed_matches_reported"
prompt_lacks "$red" "a spec with no Bug section still requires the failure to match What happened" \
  -iE -e "$observed_matches_reported"
[[ -z "$problems" ]] \
  && ok || no "verify-red requires a bug's observed failure to match What happened, and requires nothing of the kind for a spec with no Bug section (${problems#; })"


# 43. a verify-refactor finding rides on the refactor leaf's own FLAGS: classes, never on a
#     NEW_STEP: line (issue #175). Case 32 gave the verifier `NEW_STEP:` for an unhandled edge
#     case, the token the refactor leaf then used for its overfit findings, so that the
#     conductor could hand either to `add-ledger-step.sh`. #175 took that token off the leaf:
#     every finding became a whole ledger step whatever it named, and the plan grows now only
#     from an `uncovered-spec` flag. A verifier still writing `NEW_STEP:` would be the one
#     channel left that grows the plan from a finding nobody classed — so its finding carries
#     the same three classes, `overfit`, `uncovered-spec` and `beyond-spec`, on a `FLAGS:`
#     line, and the conductor routes it by the same rule as the leaf's. Classing a finding
#     reveals no developer reasoning, so blindness holds (ADR-0003).
#
#     Cases 32 and 33 moved to the same line with it. Five claims,
#     five misses: the line, each class it may carry — a `FLAGS:` line with no class is the
#     unclassed finding again — and `NEW_STEP` absent from the prompt, since a prompt offering
#     both lets the verifier fill either. The prompt read is case 7's `$refactor`, so this case
#     invokes the builder not at all, and folds through `prompt_says`/`prompt_lacks`.
problems=""
prompt_says "$refactor" "no FLAGS: line" -F -e 'FLAGS:'
for class in overfit uncovered-spec beyond-spec; do
  prompt_says "$refactor" "does not name the $class class" -F -e "$class"
done
prompt_lacks "$refactor" "still asks for a NEW_STEP: line" -F -e 'NEW_STEP'
[[ -z "$problems" ]] && ok \
  || no "verify-refactor reports a finding on a FLAGS: line carrying the overfit, uncovered-spec or beyond-spec class, never on a NEW_STEP: line (${problems#; })"

# 44. the rebase verifier's prompt (issue #238, criterion 3). A conflicted rebase is resolved by
#     a developer leaf, and the resolution is new code no verifier has seen, so a blind
#     verify-rebase judges it before the PR is marked ready. Its builder call takes the spec
#     and the two shas alone — `rebase <spec-file> <onto-sha> <pre-rebase-sha>` — which is
#     what keeps it blind (ADR-0003): no slot for the resolving leaf's account of what it did.
#     The prompt tells the verifier to run the full test command on HEAD, and to judge that
#     both sides survived — the branch's own changes and the default branch's, since a
#     resolution that quietly drops either still merges green. Both shas get #151's guard:
#     a slot that is not ^[0-9a-f]{7,40}$ is exit 2 with nothing on stdout, whichever of the
#     two it is. One headline, every miss accumulated, for case 12's reason.
problems=""
rb_onto='8d05a4410c2e' rb_pre='278252a1b9f3'
rebase_prompt="$("$BUILD" rebase "$work/spec.md" "$rb_onto" "$rb_pre" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] || problems="$problems; exit $code, want 0"
[[ "$rebase_prompt" == *'slugify("Hello & World/Foo")'* ]] || problems="$problems; spec not carried verbatim"
[[ "$rebase_prompt" == *"$rb_onto"* ]] || problems="$problems; no onto sha"
[[ "$rebase_prompt" == *"$rb_pre"* ]] || problems="$problems; no pre-rebase sha"
[[ "$rebase_prompt" != *'{{'* ]] || problems="$problems; an unfilled {{placeholder}} left in the prompt"
prompt_says "$rebase_prompt" "does not tell the verifier to run the full test command" -iE -e 'full[^.]{0,80}(test|suite)'
prompt_says "$rebase_prompt" "does not name HEAD as what is tested" -F -e 'HEAD'
prompt_says "$rebase_prompt" "does not name the default branch's changes" -iE -e 'default branch'
prompt_says "$rebase_prompt" "does not ask that both sides' changes survive" \
  -iE -e 'both[^.]{0,200}(surviv|preserv|intact|kept)|(surviv|preserv|intact|kept)[^.]{0,200}both'
probe_rebase_sha() {  # probe_rebase_sha <label> <onto-sha> <pre-rebase-sha>
  local label="$1" out rc
  out="$("$BUILD" rebase "$work/spec.md" "$2" "$3" 2>/dev/null)"; rc=$?
  [[ "$rc" -eq 2 && -z "$out" ]] || problems="$problems; $label: exit $rc, ${#out} bytes on stdout, want exit 2 and none"
}
probe_rebase_sha "short onto" abc123 "$rb_pre"
probe_rebase_sha "uppercase onto" 8D05A4410C2E "$rb_pre"
probe_rebase_sha "onto with text" "$rb_onto because it merged" "$rb_pre"
probe_rebase_sha "short pre-rebase" "$rb_onto" abc123
probe_rebase_sha "uppercase pre-rebase" "$rb_onto" 278252A1B9F3
probe_rebase_sha "pre-rebase with text" "$rb_onto" "$rb_pre because it was green"
[[ -z "$problems" ]] && ok \
  || no "verify-rebase renders from the spec and the two shas alone, tells the verifier to run the full test command on HEAD and judge that both the branch's and the default branch's changes survive, and refuses a sha that is not 7-40 lowercase hex with exit 2 and no stdout (${problems#; })"

# 45. the plan prompt directs a REJECT for a plan that turns a criterion whose only observable
#     is the test command passing into a Red/Green step, rather than the `⟦full-suite⟧` line
#     *Scope & plan* writes for it (issue #481, criterion 3). Such a criterion has no failing
#     test to write — a case asserting "the suites pass" would have to run the suites from
#     inside itself, which no-nested-suites.test.sh forbids — so a Red leaf handed it answers
#     UNTESTABLE and the run bails `untestable-criterion`, as #451 did twice. The plan verifier
#     is the one reader who sees the plan before that leaf is paid for, and check 1 alone
#     would PASS such a step: it does deliver the criterion as written. So the prompt has to
#     name the shape, the marker that is its right spelling, and the REJECT, each in view of
#     the others. Three claims, three misses, each named, for case 36's reason; matched over
#     the newline-flattened prompt through `prompt_says`, every window under 255 for the same
#     reason.
#
#     plan_rejects_shape <marker> <shape> <shape ERE> — the three claims, for case 46 as well.
plan_rejects_shape() {
  local marker="$1" shape="$2" ere="$3"
  prompt_says "$plan" "never names the ⟦$marker⟧ marker" -F -e "⟦$marker⟧"
  prompt_says "$plan" "never directs a REJECT for a criterion $shape" \
    -iE -e "REJECT[^.]{0,200}$ere|$ere[^.]{0,200}REJECT"
  prompt_says "$plan" "never sets a Red/Green step against the ⟦$marker⟧ line it should have been" \
    -iE -e "Red[^.]{0,40}Green[^.]{0,200}$marker|$marker[^.]{0,200}Red[^.]{0,40}Green"
}
problems=""
plan_rejects_shape full-suite "whose only observable is the test command passing" \
  '(test command|suites?)[^.]{0,120}pass'
[[ -z "$problems" ]] && ok || no "verify-plan REJECTs a plan that makes a criterion whose only observable is the test command passing a Red/Green step instead of a ⟦full-suite⟧ line (#481) (${problems#; })"

# 46. case 45's other shape (issue #481, criterion 3): a criterion whose deliverable is the
#     record of a manual check — each suite broken on purpose, watched going red, the output
#     recorded, as #225 criterion 4 asked — is owed by a human, and *Scope & plan* writes it as
#     a `⟦human-owed⟧` line that no developer leaf is ever handed. Made a Red/Green step, it
#     reaches a Red leaf that can only answer UNTESTABLE, and the run bails
#     `untestable-criterion`, as #225 did twice. Check 1 alone would PASS that step, so the
#     prompt has to name the shape, the marker, and the REJECT, each in view of the others —
#     three claims, three misses, through case 45's plan_rejects_shape.
problems=""
plan_rejects_shape human-owed "whose deliverable is the record of a manual check" \
  '(manual|human)[^.]{0,120}(check|record)'
[[ -z "$problems" ]] && ok || no "verify-plan REJECTs a plan that makes a criterion whose deliverable is the record of a manual check a Red/Green step instead of a ⟦human-owed⟧ line (#481) (${problems#; })"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
