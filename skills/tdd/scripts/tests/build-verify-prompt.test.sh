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
prompt_says() {  # prompt_says <prompt> <complaint> <grep argument…>
  local prompt="$1" complaint="$2"; shift 2
  grep -q "$@" <<<"$(tr '\n' ' ' <<<"$prompt")" || problems="$problems; $complaint"
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

# 32. an unhandled edge case the spec implies is a proposed step, not a REJECT (issue #362).
#     Check 2 asks for code that is "reasonably robust (no obvious unhandled edge case the
#     spec implies)", and handling an edge case changes behaviour — so a REJECT on that
#     ground can only be met by the untested behaviour change develop-refactor forbids, and
#     the revise leaf either fails or smuggles one in. Beck's answer to a missing case is a
#     new test, so the finding becomes a `NEW_STEP:` line, the same protocol token the
#     refactor leaf reports its overfit findings on (#361), written before the final
#     `VERDICT:`/`REASON:` pair. Proposing a criterion reveals no developer reasoning, so
#     blindness holds (ADR-0003).
#
#     Four claims, four misses, for case 12's reason: the token without the edge case it
#     answers is a line the verifier fills with anything, the placement is what keeps
#     parse-verdict.sh reading the final pair, and the token arriving while the REJECT stays
#     leaves the verdict that #362 exists to remove. The prompt read is case 7's `$refactor`
#     — same phase, same arguments — so there is no new invocation, and case 7 owns the
#     build. `NEW_STEP` and `edge case` both appear at most once in the prompt built today,
#     so no probe is answered by prose already there.
problems=""
prompt_says "$refactor" "verify-refactor never names a NEW_STEP: line" \
  -F -e 'NEW_STEP:'
prompt_says "$refactor" "verify-refactor never ties NEW_STEP: to an unhandled edge case the spec implies" \
  -iE -e "unhandled edge case[^.]{0,200}NEW_STEP|NEW_STEP[^.]{0,200}unhandled edge case"
prompt_says "$refactor" "verify-refactor never puts the NEW_STEP: line before the VERDICT: line" \
  -iE -e "NEW_STEP[^.]{0,120}before[^.]{0,120}VERDICT"
prompt_says "$refactor" "verify-refactor never says an unhandled edge case is not a REJECT" \
  -iE -e "(edge case|robust)[^.]{0,200}not( by itself)? a REJECT|not( by itself)? a REJECT[^.]{0,200}(edge case|robust)"
[[ -z "$problems" ]] && ok \
  || no "verify-refactor reports an unhandled edge case the spec implies as a NEW_STEP: line before VERDICT: rather than a REJECT (${problems#; })"

# 33. every phase's built prompt allows NEW_STEP: lines before the final pair (issue #362).
#     The footer every verifier writes is the conductor's whole reading of the leaf, and it
#     says today to end with EXACTLY the two lines and nothing after them. Case 32 has the
#     refactor verifier report an unhandled edge case on a `NEW_STEP:` line before that
#     pair — a line the contract as written does not admit, so the verifier is told to
#     break the contract to obey the check. The contract is what has to give: `NEW_STEP:`
#     lines are allowed ahead of the final two, and the final two stay last, which is what
#     keeps parse-verdict.sh reading the same verdict and reason as before.
#
#     Asked of all four phases, not just refactor, because the contract lives in _shared.md
#     and a phase that kept the older footer would carry a rule contradicting the one the
#     run acts on — and because the refactor leaf already reports on this token (#361), so
#     any verifier may be handed output carrying it. Assert on the built prompts rather
#     than on _shared.md, for case 12's reason: the behaviour is the rule reaching every
#     phase, not which file holds it.
#
#     Two claims, two misses per phase: a prompt naming the token without permitting it
#     still forbids the line it asks for, and permission without the placement leaves
#     parse-verdict.sh's final pair unguarded. The prompts read are cases 5, 6, 7 and 9's —
#     same phases, same arguments — so this case invokes the builder not at all, and folds
#     through `prompt_says` for the reason given at its definition.
allows_new_step() {  # allows_new_step <phase label> <prompt>
  local label="$1" prompt="$2"
  prompt_says "$prompt" "verify-$label's output contract never allows a NEW_STEP: line" \
    -iE -e "NEW_STEP[^.]{0,200}(may|can|allow|permit)|(may|can|allow|permit)[^.]{0,200}NEW_STEP"
  prompt_says "$prompt" "verify-$label never puts NEW_STEP: lines before the final VERDICT:/REASON: pair" \
    -iE -e "NEW_STEP[^.]{0,160}before[^.]{0,160}(VERDICT|(final|last)[^.]{0,40}two lines)"
}

every_phase allows_new_step "every phase's prompt allows NEW_STEP: lines before the final VERDICT:/REASON: pair"

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


echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
