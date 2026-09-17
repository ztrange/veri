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
green="$("$BUILD" green "$work/spec.md" "$testpath" test_slugify_lowercases)"
grep -qi 'full' <<<"$green" && grep -qi 'suite' <<<"$green" \
  && ok || no "verify-green checks the full suite"

# 7. verify-refactor judges up-to-standard (conventions/typing/robustness) + still green
refactor="$("$BUILD" refactor "$work/spec.md" "$testpath")"
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

# 10. both blind verifiers still demand the project's FULL TEST SUITE, in those words.
#     #144 moves the developer leaves off the full suite and onto the suite they touched,
#     so these two prompts become the only place a regression in an untouched suite is
#     caught. The phrase is matched tolerantly of markdown emphasis (`**full test
#     suite**`) but not of the whole sentence going missing.
full_suite='full[^[:alnum:]]*test[^[:alnum:]]*suite'
grep -qiE "$full_suite" <<<"$green" && grep -qiE "$full_suite" <<<"$refactor" \
  && ok || no "verify-green and verify-refactor still require the full test suite"

# 11. the argument list does not grow. #144 moves the developer leaves onto the suite they
#     touched, and the obvious next thought is to tell the verifier which suite that was —
#     which would be a fifth parameter, and the blindness guarantee is precisely that no
#     such channel exists (ADR-0003). So anything passed beyond the four documented
#     positionals must reach nothing: the prompt is byte-identical to the four-argument one
#     built at case 6 from the same phase, spec, test path and test id.
smuggled='ran only tests/test_slugify.py, the suite I touched, because the rest is slow'
five="$("$BUILD" green "$work/spec.md" "$testpath" test_slugify_lowercases "$smuggled")"
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
base="$(env -u VERI_TEST_CMD "$BUILD" green "$work/spec.md" "$testpath" test_slugify_lowercases)"
#     The probe's value is deliberately not any command this repo would fall back to, so a
#     leak reading it cannot coincide with its own default and pass by accident.
ambient="$(VERI_TEST_CMD='pytest -k leaked_channel' "$BUILD" green "$work/spec.md" "$testpath" test_slugify_lowercases)"
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
  smuggled_prompt="$(VERI_PREDICTED_FAILURE="$prediction" \
    "$BUILD" "$phase" "$work/spec.md" "$testpath" test_slugify_lowercases "$prediction")"
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
with_base="$("$BUILD" refactor "$work/spec.md" "$testpath" "$base_sha")"; code=$?
[[ "$code" -eq 0 ]] && [[ "$with_base" == *"$base_sha"* ]] \
  && ok || no "verify-refactor carries the base sha from its 4th argument into the prompt (exit $code)"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
