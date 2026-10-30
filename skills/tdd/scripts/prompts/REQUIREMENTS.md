## skills/tdd/scripts/prompts/develop-revise.md

| ID | Requirement | Why |
|---|---|---|
| DV1 | In a `⟦suite-repair⟧` or `⟦ci-repair⟧` revise-green prompt the permission to edit a test appears once, and it covers only the failing test the full run or CI left red; every other test stays frozen (#1653, #1920). | The repair can fix the test that is actually wrong without opening every other test to edits; PR #1907's review showed a mutant reading "Any test may change" survived. |
| DV2 | Every numbered item of the "What to do" list carries an instruction in every revise prompt the template renders, a `⟦suite-repair⟧` or `⟦ci-repair⟧` revise-green prompt included; no item renders empty. | After #1920 the repair revise-green prompt rendered item 2 as a bare `2.`, leaving the leaf to guess whether a step was dropped. |

## skills/tdd/scripts/prompts/develop-contract-a.md

| ID | Requirement | Why |
|---|---|---|
| CA1 | The prompt says this is the contract-a phase of an interface change: no product caller of the old interface remains, the tests that still exercise it move off it, tests are rewritten or deleted, and production stays frozen. (Opening paragraph.) | The leaf must know which of the four interface phases it is in and what it may touch. |
| CA2 | Step 1 tells the leaf to rewrite every test of the old interface against the new one, or to delete it where a test of the new interface already covers the same behaviour. (Numbered list, item 1.) | A test of the old interface that survives would keep the proxy alive. |
| CA3 | Step 1 tells the leaf to leave the old interface in place, because deleting its proxy is contract-b. (Numbered list, item 1, last sentence.) | The proxy's deletion belongs to the next phase. |
| CA4 | Step 3 tells the leaf to commit the change as `refactor: <what changed> (#<issue>)`, and never to modify a production file: a contract-a commit that touches one is rejected. (Numbered list, item 3.) | The commit carries the issue number, and the frozen half of the phase is enforced by rejection. |
| CA5 | The numbered list has three items in this order: rewrite or delete the tests (1), run the suites covering the touched files (2, an included fragment), commit (3). (Numbered list.) | The tests are moved before the run proves them green, and the commit follows the proof. |

## skills/tdd/scripts/prompts/develop-contract-b.md

| ID | Requirement | Why |
|---|---|---|
| CB1 | The prompt says this is the contract-b phase of an interface change: neither product code nor any test calls the old interface any more, and the old interface's proxy is deleted. (Opening paragraph, first two sentences.) | The leaf deletes the proxy only once nothing calls it. |
| CB2 | The prompt says behaviour does not change: every test that was green stays green, and test files stay frozen. (Opening paragraph, last sentence.) | The phase is a pure deletion; a changed test would hide a behaviour change. |
| CB3 | Step 1 tells the leaf to delete the old interface's proxy from production. (Numbered list, item 1.) | It is the one change this phase makes. |
| CB4 | Step 3 tells the leaf to commit the change as `refactor: <what changed> (#<issue>)`. (Numbered list, item 3, first sentence.) | The commit carries the issue number. |
| CB5 | Step 3 tells the leaf never to modify a test file: a contract-b commit that touches one is rejected. (Numbered list, item 3, second sentence.) | The frozen half of the phase is enforced by rejection. |
| CB6 | The numbered list has three items in this order: delete the proxy (1), run the suites covering the touched files (2, an included fragment), commit (3). (Numbered list.) | The deletion is proven green before it is committed. |

## skills/tdd/scripts/prompts/develop-expand.md

| ID | Requirement | Why |
|---|---|---|
| EX1 | The prompt says this is the expand phase of an interface change: production gains the new interface, and the old interface becomes a proxy that delegates to it. (Opening paragraph, first two sentences.) | The leaf must know what the phase adds and what the old interface turns into. |
| EX2 | The prompt says behaviour does not change: every test that was green stays green, and test files stay frozen. (Opening paragraph, last sentence.) | The expand is a refactor; a changed test would hide a behaviour change. |
| EX3 | Step 1 tells the leaf to add the new interface to production and turn the old one into a proxy over it, and to move no caller yet, because that is the migrate phase. (Numbered list, item 1.) | Moving callers is the next phase's work, so the diff stays one kind of change. |
| EX4 | Step 3 tells the leaf to commit the change as `refactor: <what changed> (#<issue>)`. (Numbered list, item 3, first sentence.) | The commit carries the issue number. |
| EX5 | Step 3 tells the leaf never to modify a test file: an expand commit that touches one is rejected. (Numbered list, item 3, second sentence.) | The frozen half of the phase is enforced by rejection. |
| EX6 | The numbered list has three items in this order: add the interface and proxy the old one (1), run the suites covering the touched files (2, an included fragment), commit (3). (Numbered list.) | The change is proven green before it is committed. |

## skills/tdd/scripts/prompts/develop-migrate.md

| ID | Requirement | Why |
|---|---|---|
| MG1 | The prompt says this is the migrate phase of an interface change: the new interface exists, the old one is a proxy over it, and the callers move to the new interface. (Opening paragraph, first two sentences.) | The leaf must know the state it starts from and what it moves. |
| MG2 | The prompt says behaviour does not change: every test that was green stays green, and test files stay frozen. (Opening paragraph, last sentence.) | The migrate is a refactor; a changed test would hide a behaviour change. |
| MG3 | Step 1 tells the leaf to move every product caller of the old interface to the new interface, and to leave the old interface in place, because removing it is the contract phase. (Numbered list, item 1.) | The proxy's removal is later work, so a missed caller still works through the proxy. |
| MG4 | Step 3 tells the leaf to commit the change as `refactor: <what changed> (#<issue>)`. (Numbered list, item 3, first sentence.) | The commit carries the issue number. |
| MG5 | Step 3 tells the leaf never to modify a test file: a migrate commit that touches one is rejected. (Numbered list, item 3, second sentence.) | The frozen half of the phase is enforced by rejection. |
| MG6 | The numbered list has three items in this order: move the callers (1), run the suites covering the touched files (2, an included fragment), commit (3). (Numbered list.) | The change is proven green before it is committed. |

## skills/tdd/scripts/prompts/develop-rebase.md

| ID | Requirement | Why |
|---|---|---|
| RB1 | The prompt says the run's branch is behind the default branch, that rebasing it onto `{{ONTO_SHA}}` stopped on conflicts, and that the rebase was aborted so the branch is back at `{{PRE_REBASE_SHA}}`, where it stood before. The leaf's job is to rebase the branch onto `{{ONTO_SHA}}` and resolve every conflict so that both sides' intent survives. (Opening paragraph.) | The leaf starts from a clean, aborted state and is told the goal is both sides' behaviour, not a quick merge. |
| RB2 | Under their own headings the prompt gives the leaf the files that conflicted (`{{CONFLICTING_FILES}}`), the step the run was on (`{{STEP}}`), the issue's behavior spec as context (`{{ISSUE_SPEC}}`) and the test command (`{{TEST_CMD}}`). (Sections before "What to do".) | A resolver needs to know which files, which intent and which command proves it. |
| RB3 | Step 1 tells the leaf to rebase onto that exact commit, not onto a branch name that may have moved since: `git rebase {{ONTO_SHA}}`. (What to do, item 1.) | A branch name can move between the abort and the leaf's rebase. |
| RB4 | Step 2 tells the leaf to resolve each conflict by reading both sides, with `git log --oneline {{PRE_REBASE_SHA}}..{{ONTO_SHA}}` showing what the default branch added, then to `git add` the file and run `git rebase --continue`. (What to do, item 2, first sentence.) | Resolution is by understanding both histories, one conflict at a time. |
| RB5 | Step 2 tells the leaf that, if a conflict cannot be resolved without dropping one side's behaviour, it runs `git rebase --abort`, which returns the branch to `{{PRE_REBASE_SHA}}`, and reports FAILED. (What to do, item 2, last sentence.) | Dropping one side's behaviour is a loss the leaf must not hide; a failed report leaves the branch as it was. |
| RB6 | Step 3 tells the leaf to confirm the test command is green on the rebased tip by running it through the wrapper, naming tier `all` because the whole test command is what runs, as `{{TIMED_TEST_RUN}} all '' {{TEST_CMD}}`, and the step ends with the clause (opened by the included `_exit-status-back.md` fragment) "so a red run stays red". (What to do, item 3.) | The resolution is proven on the whole test command, and a red result must not be masked by the wrapper. |
| RB7 | Step 4 tells the leaf not to push, because the conductor pushes and re-verifies the resolution. (What to do, item 4.) | The conductor owns the push and the blind re-verification. |
| RB8 | Step 5 tells the leaf not to edit the ledger `.tdd/issue-<n>.md` beyond what the rebase itself carries; the sentence runs "every" into two included fragments (`_develop-ledger-tick.md`, then `_develop-ledger-mark.md`) that name what must survive. (What to do, item 5.) | The committed ledger is the source of truth for done steps and for the refactor-pending mark. |
| RB9 | The prompt ends by asking the leaf, in its last lines, for a `REBASE:` line saying RESOLVED or FAILED and one line on which files conflicted and how they were resolved. (Report section.) | The conductor reads one fixed line to decide whether to re-verify the resolution. |
| RB10 | The prompt tells the leaf how to resolve a conflict in a `*/GRADED` file: keep the replayed branch commit's side of every conflicted row only, hunk by hunk (mid-rebase that is git's `--theirs` side of each conflict, since `--ours` is the onto side), and keep every line git merged without a conflict, so no upstream row is lost; the prompt forbids taking the branch's whole file (which drops the onto side's newer rows) and names the resolution without the literal `git checkout --` (the #1286 guard in `test_build_verify_prompt.py` forbids that text in built prompts) — edit no hash, and leave re-signing to the regrade block the conductor runs before `verify-rebase`. Resolved this way, a `GRADED` conflict drops no behaviour and is no ground for step 2's FAILED. (What to do, item 2.) | A `GRADED` row is a grade of a file's content; only the branch's row makes the conductor's selector re-sign the rebased text, and the upstream row would leave a stale grade nothing re-signs. |
| RB11 | The prompt forbids the leaf to run `grade-prose.sh` or to write or edit a `GRADED` hash by hand. (What to do, item 2.) | A grade the leaf computed or invented must never be committed; grading is the conductor's. |
| RB12 | Step 3 tells the leaf that a `prose-owed.sh` failure in the test command's run, on a unit whose `GRADED` row the rebase touched, is expected until the conductor regrades, is not the leaf's to fix, and is no ground to report `REBASE: FAILED`; any other red still is. (What to do, item 3.) | The stale row is re-signed one step later; reading its red as the resolution's failure would bail a green run `rebase-unresolved`. |

## skills/tdd/scripts/prompts/develop-reconcile.md

| ID | Requirement | Why |
|---|---|---|
| RN1 | The prompt says `push-branch.sh` could not push the run's branch because git rejected it as a non-fast-forward, that the remote branch `origin/{{BRANCH}}` is at `{{REMOTE_SHA}}`, which the local branch does not contain, and that the leaf's job is to make the push land without losing anyone's commits. (Opening paragraph.) | The leaf is told the failure and that losing others' commits is the thing to avoid. |
| RN2 | Under their own headings the prompt gives the leaf the step the run was on (`{{STEP}}`), the issue's behavior spec as context (`{{ISSUE_SPEC}}`) and the test command (`{{TEST_CMD}}`). (Sections before "What to do".) | The leaf needs the intent and the command that proves a rebase green. |
| RN3 | Step 1 tells the leaf to review the divergence in both directions: `git log --oneline {{REMOTE_SHA}}..HEAD` for what the run has that the remote does not, and `git log --oneline HEAD..{{REMOTE_SHA}}` for what the remote has that the run does not. (What to do, item 1.) | Whose commits the remote holds cannot be decided from one side. |
| RN4 | Step 2, first case: when the remote holds commits the run does not have (someone else's work, or anything that is not the run's own earlier history), the leaf rebases onto the remote with `git rebase {{REMOTE_SHA}}`, confirms the test command is still green, then pushes with `git push origin HEAD:{{BRANCH}}`. (What to do, item 2, first sub-item.) | Someone else's work is kept by building on it, and the push then fast-forwards. |
| RN5 | The green check in that first case goes through the wrapper `{{TIMED_TEST_RUN}}`, which records what the run cost and names the tier it belongs to, `all`, since the whole test command is what runs, as `{{TIMED_TEST_RUN}} all '' {{TEST_CMD}}`, and the sub-item ends with the clause (opened by the included `_exit-status-back.md` fragment) "so a red run stays red". (What to do, item 2, first sub-item, the wrapper paragraph.) | The rebased tip is proven on the whole test command, and a red result must not be masked by the wrapper. |
| RN6 | Step 2, second case: when the remote holds only the run's own pre-rebase history (the same commits, rewritten locally), the leaf pushes with the lease pinned to the sha above, and nothing looser: `git push --force-with-lease={{BRANCH}}:{{REMOTE_SHA}} origin HEAD:{{BRANCH}}`. (What to do, item 2, second sub-item.) | A pinned lease overwrites only the history the run itself rewrote. |
| RN7 | Step 3 tells the leaf never to force-push any other way: no unpinned lease, and no plain force flag. (What to do, item 3, first sentence.) | An unpinned force can erase commits pushed since the run last fetched. |
| RN8 | Step 3 tells the leaf that, if the pinned push is itself rejected, the remote moved again, and it stops and reports it. (What to do, item 3, last sentence.) | A remote that moved again holds commits the leaf has not read, so the leaf does not retry looser. |
| RN9 | Step 4 tells the leaf not to edit the ledger `.tdd/issue-<n>.md`; the sentence runs "every" into two included fragments (`_develop-ledger-tick.md`, then `_develop-ledger-mark.md`) that name what must survive. (What to do, item 4.) | The committed ledger is the source of truth for done steps and for the refactor-pending mark. |
| RN10 | The prompt ends by asking the leaf, in its last lines, for a `RECONCILE:` line saying REBASED, FORCED or FAILED and one line on what the remote held and what the leaf did. (Report section.) | The conductor reads one fixed line to see which way the push was made good. |

## skills/tdd/scripts/prompts/_develop-ledger-mark.md

| ID | Requirement | Why |
|---|---|---|
| LM1 | The fragment says a ` ⟂ refactor pending` mark must survive exactly as it is. (The whole fragment.) | A step's green tick appends the mark and only its verify-refactor PASS removes it, so a rewritten or lost mark makes a resumed run misread green as finished. |

## skills/tdd/scripts/prompts/_develop-ledger-tick.md

| ID | Requirement | Why |
|---|---|---|
| LT1 | The fragment names the `[x]` tick as the first of two ledger marks, and opens the second with "every"; the sentence it belongs to is completed by the next included fragment. (The whole fragment.) | A lost `[x]` tick re-opens a done step; the fragment is the first half of the sentence that protects it. |

## skills/tdd/scripts/prompts/develop-red.md

| ID | Requirement | Why |
|---|---|---|
| RD1 | The step's section is headed as this cycle's criterion, to be pinned and nothing else ("pin ONLY this"), and the sentence after the step tells the leaf to pin it as observable behaviour: what the code does when it is called, not how it is written inside. (The step section and the sentence after `{{STEP}}`.) | Red pins one criterion, by behaviour, so Green has one observable target. |
| RD2 | After that sentence the prompt includes `_develop-red-valid-test.md`, the "What counts as a valid test" rules that step 0 refers to as above; the issue's behavior spec section that follows is headed context only, pin only the step above. (The include line, and the spec section heading.) | The rules come before the work, and the spec informs without widening the pin. |
| RD3 | Step 0 tells the leaf to check testability first: before writing anything, hold the criterion against **What counts as a valid test**, and if no case can pin it without breaking rule 1, 2 or 3, stop and report `AGAINST_UNMODIFIED: UNTESTABLE` with `WHY:`, not proceeding to the steps below. (What to do, item 0.) | An untestable criterion is reported through a declared key instead of being forced into a bad test. |
| RD4 | Step 1 tells the leaf to read the existing suite the case belongs in and add the case in that suite's own style, leaving its other cases untouched and green, and, if no suite fits, to create one that matches the repository's testing idiom. (What to do, item 1.) | The case lands where its neighbours live, in their style. |
| RD5 | Step 2 tells the leaf to predict the failure before running anything: to write to `.tdd/red-prediction.md`, before running any suite, which assertion fires first, the observed-versus-expected values it fires on and the shape of the message, formed from the test and the code, never from the output, because a prediction written after the run is a transcription of it and answers nothing. (What to do, item 2.) | A prediction made before the run is the check that the case fails for the reason it was written for. |
| RD6 | Step 3 tells the leaf to run the suites `_affected-suites-working-tree.md` names (the included fragment), not the full suite and not one suite picked by hand, against the unmodified production code, and to record whether the new case FAILS or PASSES; it says the only question is whether that one case fails, that the suite holding the new case is among those printed, and that the others read the same files and must stay green. (What to do, item 3, first two sentences.) | The red run covers every suite the change touches without paying for the full suite. |
| RD7 | Step 3's next sentence opens "Run one suite through", runs into two included fragments (`_run-suite-lead.md`, then `_develop-run-suite-same-way.md`), and ends "the test command above and say so in your report", so a fallback to the test command is said in the report. (What to do, item 3, the sentence ending "say so in your report".) | A run that could not use the one-suite invocation is visible in the report, not hidden. |
| RD8 | Step 3 tells the leaf to make that run through the wrapper (the included `_timed-test-run.md`) naming the tier it belongs to, with the included `_timed-test-run-affected.md` line as the command, and the included `_exit-status-back.md` clause is completed "so a red run stays red — and red is the answer this phase is after". (What to do, item 3, the wrapper sentence and the line after the indented command.) | The cost is recorded, and the wrapper must not mask the red this phase is after. |
| RD9 | Step 3 tells the leaf to save that run's output to `.tdd/red-run-output.txt`, the file `red-divergence.sh` dates the prediction file against. (What to do, item 3, last sentence.) | The prediction is proven to predate the run. |
| RD10 | Step 4 tells the leaf to compare what the run printed against the prediction and report which it was: *Matched*, carry on; *Diverged*, the test is the suspect, not the prediction, and the leaf revises the **test**, predicts again and re-runs until the observed failure is the predicted one or it can say precisely why the two cannot be reconciled; it never adjusts the prediction to fit what it saw. (What to do, item 4.) | A divergence is how a typo'd fixture path or wrong assertion would otherwise reach Green looking red. |
| RD11 | Step 5 says either answer is acceptable and must be reported truthfully, since a criterion earlier work already satisfies yields a passing test with a dedicated path, and tells the leaf not to bend the test to force a failure. (What to do, item 5, first two sentences.) | A forced failure would pin nothing. |
| RD12 | Step 5 tells the leaf that, if the case PASSES, it confirms the case is capable of failing: it predicts what temporarily breaking the behaviour should make the case print, breaks it, runs the case and checks the output against that prediction, all before it restores, because after the restore that output cannot be reproduced; it then restores the production code exactly and verifies the restore with `git diff --exit-code` on the file it touched. (What to do, item 5, from "If it PASSES" to the end.) | A passing pin is only accepted once it has been seen to go red for the predicted reason. |
| RD13 | Step 6 tells the leaf to leave no change to any file other than the test file. (What to do, item 6.) | Red writes no production code. |
| RD14 | The prompt ends by asking, in its last lines, for `TEST_PATH:`, `TARGET_TEST:`, `AGAINST_UNMODIFIED: FAILS | PASSES | UNTESTABLE`, `WHY:` (UNTESTABLE only), `FAIL_OUTPUT:`, `PREDICTED_FAILURE:`, `PREDICTION: MATCHED | DIVERGED` and `PREDICTION_NOTE:` (on DIVERGED), in that order. (Report section.) | The conductor and `red-divergence.sh` read fixed lines. |
| RD15 | The `PREDICTED_FAILURE:` line asks for the missing name when the predicted failure is an error on the name the step introduces rather than an assertion, and otherwise for the assertion, the values and the message shape, as predicted before running. (Report section, the `PREDICTED_FAILURE:` line.) | A red that fails on an undefined name is predicted by that name, not by an assertion. |

## skills/tdd/scripts/prompts/develop-red-missing.md

| ID | Requirement | Why |
|---|---|---|
| RM1 | The prompt opens by telling the leaf to add exactly **ONE** new failing test case that pins the behaviour named below, to write **NO** production code, and never to edit another case. (Opening sentence after the phase heading.) | This leaf adds the one missing pin and nothing else. |
| RM2 | Under "The behaviour no test pins" the prompt says a rejection of this step's green found that no test pins a line the step needs, and gives its reason verbatim (`{{REJECTION_REASON}}`). (That section's first sentence.) | The leaf works from the verifier's own words. |
| RM3 | The prompt tells the leaf to pin the behaviour the reason's `MISSING_TEST:` line names, in one case, as observable behaviour, what the code does when called, not how it is written inside, leaving every other case and all production code untouched; the included `_develop-red-valid-test.md` rules follow. (The paragraph after `{{REJECTION_REASON}}`, and the include line.) | The pin targets exactly the line the verifier found unpinned. |
| RM4 | Step 0 tells the leaf to check testability first against **What counts as a valid test**, and if no case can pin the criterion without breaking rule 1, 2 or 3, to stop and report `AGAINST_UNMODIFIED: UNTESTABLE` with `WHY:`, not proceeding. (What to do, item 0.) | An untestable criterion is reported through a declared key. |
| RM5 | Step 1 tells the leaf to read the existing suite the case belongs in and add it in that suite's style, leaving its other cases untouched and green, or, if no suite fits, to create one matching the repository's testing idiom. (What to do, item 1.) | The case lands where its neighbours live. |
| RM6 | Step 2 tells the leaf to predict the failure before running anything, writing to `.tdd/red-prediction.md`, before any suite runs, which assertion fires first, the observed-versus-expected values and the message shape, formed from the test and the code, never from the output. (What to do, item 2.) | The prediction is the check that the case fails for its own reason. |
| RM7 | Step 3 tells the leaf to run the suites the included `_affected-suites-working-tree.md` names, not the full suite and not one suite picked by hand, against the unmodified production code, recording whether the new case FAILS or PASSES, the others staying green. (What to do, item 3, first two sentences.) | The run covers what the change touches without the full suite. |
| RM8 | Step 3's next sentence opens "Run one suite through", runs into two included fragments (`_run-suite-lead.md`, then `_develop-run-suite-same-way.md`), and ends "the test command above and say so in your report". (What to do, item 3, the sentence ending "say so in your report".) | A fallback to the test command is said in the report. |
| RM9 | Step 3 tells the leaf to run through the wrapper (included `_timed-test-run.md`) naming its tier, with the included `_timed-test-run-affected.md` line as the command, the `_exit-status-back.md` clause completed "so a red run stays red — and red is the answer this phase is after", and to save the output to `.tdd/red-run-output.txt`, the file `red-divergence.sh` dates the prediction against. (What to do, item 3, from "Make that run" to the end.) | The cost is recorded, the red is not masked, and the prediction is dated. |
| RM10 | Step 4 tells the leaf to compare the output with the prediction and report Matched or Diverged; on a divergence the test is the suspect, and the leaf revises the test, predicts again and re-runs, never adjusting the prediction to fit what it saw. (What to do, item 4.) | A divergence exposes a test that fails for the wrong reason. |
| RM11 | Step 5 says either answer is acceptable and must be reported truthfully, tells the leaf not to bend the test to force a failure, and, if the case PASSES, to predict, break, run and check the output before restoring, then restore exactly and verify with `git diff --exit-code` on the file it touched. (What to do, item 5.) | A passing pin is accepted only once seen to go red as predicted. |
| RM12 | Step 6 tells the leaf to leave no change to any file other than the test file. (What to do, item 6.) | The leaf writes no production code. |
| RM13 | The issue's behavior spec section is headed context only, pin only the step above, and the test command has its own section. (Sections before "What to do".) | The spec informs without widening the pin. |
| RM14 | The prompt ends by asking for the same report lines as Red, in order: `TEST_PATH:`, `TARGET_TEST:`, `AGAINST_UNMODIFIED: FAILS | PASSES | UNTESTABLE`, `WHY:`, `FAIL_OUTPUT:`, `PREDICTED_FAILURE:` (the missing name for a name error, otherwise assertion, values and message shape, as predicted before running), `PREDICTION: MATCHED | DIVERGED`, `PREDICTION_NOTE:`. (Report section.) | The conductor reads it as a red report. |

## skills/tdd/scripts/prompts/develop-red-supersede.md

| ID | Requirement | Why |
|---|---|---|
| SU1 | The prompt opens by telling the leaf to update the expectation of every existing test case named below to the step's criterion, and to edit those cases **only**: **NO** new test and **NO** production code. (Opening paragraph after the phase heading.) | The leaf turns the superseded pins into pins of the new criterion and nothing else. |
| SU2 | Under "The cases to update" (`{{CASES}}`) the prompt says these existing cases pin what the criterion supersedes, so a green implementing it would turn them red, and tells the leaf to change each one's expectation so it pins the criterion instead, leaving every other case and all production code untouched; the included `_develop-red-valid-test.md` rules follow. (The paragraph after `{{CASES}}`, and the include line.) | The leaf knows why these cases, and only these, change. |
| SU3 | Step 0 tells the leaf to check testability first against **What counts as a valid test**, and if no case can pin the criterion without breaking rule 1, 2 or 3, to stop and report `AGAINST_UNMODIFIED: UNTESTABLE` with `WHY:`, not proceeding. (What to do, item 0.) | An untestable criterion is reported through a declared key. |
| SU4 | Step 1 tells the leaf to read the existing suite each named case belongs in and update those cases in that suite's style, leaving its other cases untouched and green, and to create no suite and no new case. (What to do, item 1.) | The supersede edits existing cases only. |
| SU5 | Step 2 tells the leaf to predict the failure before running anything, reading the cases it just updated against the production code and writing to `.tdd/red-prediction.md`, before any suite runs, which assertion fires first, the observed-versus-expected values and the message shape, never from the output. (What to do, item 2.) | The prediction is the check that the updated cases fail for their own reason. |
| SU6 | Step 3 tells the leaf to run the suites the included `_affected-suites-working-tree.md` names, not the full suite and not one suite picked by hand, against the unmodified production code, recording whether the updated cases FAIL or PASS; the only question is whether they fail, the suites holding them are among those printed, and the others must stay green. (What to do, item 3, first two sentences.) | The run covers what the change touches without the full suite. |
| SU7 | Step 3's next sentence opens "Run one suite through", runs into two included fragments (`_run-suite-lead.md`, then `_develop-run-suite-same-way.md`), and ends "the test command above and say so in your report". (What to do, item 3, the sentence ending "say so in your report".) | A fallback to the test command is said in the report. |
| SU8 | Step 3 tells the leaf to run through the wrapper (included `_timed-test-run.md`) naming its tier, with the command line written in the template as `{{TIMED_TEST_RUN}} affected '<the suites affected-suites.sh printed>' <the command that runs them>`, the `_exit-status-back.md` clause completed "so a red run stays red — and red is the answer this phase is after". (What to do, item 3, the wrapper sentence, the indented line and the line after it.) | The cost is recorded and the red is not masked. |
| SU9 | Step 3 tells the leaf to save that run's output to `.tdd/red-run-output.txt`, the file `red-divergence.sh` dates the prediction file against. (What to do, item 3, last sentence.) | The prediction is proven to predate the run. |
| SU10 | Step 4 tells the leaf to compare the output with the prediction and report Matched or Diverged; on a divergence the test is the suspect, and the leaf revises the test, predicts again and re-runs, never adjusting the prediction to fit what it saw. (What to do, item 4.) | A divergence exposes a case that fails for the wrong reason. |
| SU11 | Step 5 says either answer is acceptable and must be reported truthfully, tells the leaf not to bend the test to force a failure, and, if the cases PASS, to predict, break, run the cases and check the output before restoring, then restore exactly and verify with `git diff --exit-code` on the file it touched. (What to do, item 5.) | A passing pin is accepted only once seen to go red as predicted. |
| SU12 | Step 6 tells the leaf to leave no change to any file other than the test files, and no change in them outside the named cases. (What to do, item 6.) | Only the named cases move. |
| SU13 | The issue's behavior spec section is headed context only, pin only the step above, and the test command has its own section. (Sections before "What to do".) | The spec informs without widening the pin. |
| SU14 | The prompt ends by asking for the red report lines in order, with `TARGET_TEST:` fixed as `NONE — the named cases are updated together, so no single case is the target`: `TEST_PATH:`, `TARGET_TEST:`, `AGAINST_UNMODIFIED: FAILS | PASSES | UNTESTABLE`, `WHY:`, `FAIL_OUTPUT:`, `PREDICTED_FAILURE:`, `PREDICTION: MATCHED | DIVERGED`, `PREDICTION_NOTE:`. (Report section.) | Several cases change together, so no single case is named as the target. |

## skills/tdd/scripts/prompts/develop-red-repair.md

| ID | Requirement | Why |
|---|---|---|
| RR1 | The prompt opens by telling the leaf to repair the one test case named below, which this step's Red wrote and which green reported wrong, and to edit that case **only**: create **NO** suite, write **NO** new case and **NO** production code. (Opening paragraph after the phase heading.) | The repair touches the one case green objected to. |
| RR2 | Under "The case to repair" (`{{CASE}}`) the prompt says "Green reported this case wrong:" and gives the reason (`{{WRONG_TEST_REASON}}{{SUPERSEDED_CASES}}`). (The case section.) | The leaf works from green's own report. |
| RR3 | The prompt tells the leaf to fix the defect that report names in this case, so that it still pins the step's criterion, leaving every other case and all production code untouched. (The paragraph after the reason.) | The repaired case still pins the same criterion. |
| RR4 | After that paragraph the prompt includes, in order, `_develop-red-valid-test.md`, `_develop-red-spec-and-testability.md` (spec, test command and What to do item 0), its own item 1, and `_develop-red-run-and-report.md` (items 2–6 and the report). (The include lines and item 1's position.) | The repair runs the same testability check, prediction and report as Red. |
| RR5 | Item 1 tells the leaf to read the suite the case belongs in and repair the case in that suite's own style, leaving its other cases untouched and green, and never to create a suite. (What to do, item 1.) | A repair edits in place. |

## skills/tdd/scripts/prompts/_develop-red-valid-test.md

| ID | Requirement | Why |
|---|---|---|
| TV1 | Under the heading "What counts as a valid test" the fragment says a case must hold all four rules that follow, or it is not a test the leaf may write. (Heading and opening sentence.) | The rules are a gate, not advice. |
| TV2 | Rule 1, **Behaviour, not mechanism**, says a case asserts the unit's output, exit code, the files or events it writes, or the error it names, never a process count, a fork count, or a timing across a suite run; those are observed with `make profile` and reported in the PR body, and a test never asserts on them. (Rule 1, first three sentences.) | A test pinned to mechanism breaks on a harmless refactor and passes a broken behaviour. |
| TV3 | Rule 1's one exception is a call count the criterion itself names as the behaviour, pinned with an **in-process spy** (the one wrapper function the code calls replaced with a same-named function that records its calls, asserted on that record), never a `PATH` shim that counts real process launches across a suite run. (Rule 1, from "The one exception" to the end.) | A spy on one call is behaviour; a shim counting processes over a suite is mechanism. |
| TV4 | Rule 2, **Lightweight**, says a case targets ~100ms and replaces a costly dependency (network, a git remote, the `claude` binary, a real sleep or wait, a server) with a stub, a same-named fake or the injected clock, unless the behaviour under test is that dependency's real use, in which case one case may exercise it for real. (Rule 2.) | The suite stays fast enough to run every cycle. |
| TV5 | Rule 3, **Self-contained**, says a case never runs another test suite, whole or sliced, and never re-runs the suite it lives in; rule 4, **On-target**, says it fails for the reason the criterion names, not an unrelated error. (Rules 3 and 4.) | A nested suite run is slow and opaque, and an off-target failure proves nothing. |
| TV6 | The paragraph after the rules says that if the criterion can only be pinned by a test breaking rules 1–3, the leaf does not write that test and skips straight to the report with `AGAINST_UNMODIFIED: UNTESTABLE` and a `WHY:` line naming which rule the only available test would break. (Paragraph after the list, first two sentences.) | An untestable criterion is reported through a declared key. |
| TV7 | The same paragraph tells the leaf not to weaken the criterion into something it does not say, and not to write the costly or implementation-pinning test anyway to force a pass. (Paragraph after the list, last sentence.) | Neither escape hatch is allowed. |
| TV8 | The last paragraph says a helper the test needs, which only the test uses, is defined in Red, inside the test file, because Green cannot write it there once Red is verified and the test file is frozen. (Last paragraph, first sentence.) | A helper left to Green could never be written. |
| TV9 | The last paragraph says a failure caused only by an undefined name in the test file (a NameError, or an ImportError of a name the test file defines nowhere) is not a red, because the case fails for a missing helper and not for the behaviour. (Last paragraph, last sentence.) | A missing helper would otherwise pass as a red. |

## skills/tdd/scripts/prompts/_develop-red-run-and-report.md

| ID | Requirement | Why |
|---|---|---|
| RP1 | The fragment begins at item 2 of the "What to do" list: predict the failure before running anything, reading the case just written against the production code and writing to `.tdd/red-prediction.md`, before any suite runs, which assertion fires first, the observed-versus-expected values and the message shape, formed from the test and the code, never from the output, because a prediction written after the run is a transcription of it. (Item 2.) | The prediction is the check that the case fails for its own reason. |
| RP2 | Item 3 tells the leaf to run the suites the included `_affected-suites-working-tree.md` names, not the full suite and not one suite picked by hand, against the unmodified production code, recording whether the new case FAILS or PASSES; the only question is whether that one case fails, the suite holding it is among those printed, and the others must stay green. (Item 3, first two sentences.) | The run covers what the change touches without the full suite. |
| RP3 | Item 3's next sentence opens "Run one suite through", runs into two included fragments (`_run-suite-lead.md`, then `_develop-run-suite-same-way.md`), and ends "the test command above and say so in your report". (Item 3, the sentence ending "say so in your report".) | A fallback to the test command is said in the report. |
| RP4 | Item 3 tells the leaf to run through the wrapper (included `_timed-test-run.md`) naming its tier, with the command line written as `{{TIMED_TEST_RUN}} affected '<the suites affected-suites.sh printed>' <the command that runs them>`, the `_exit-status-back.md` clause completed "so a red run stays red — and red is the answer this phase is after". (Item 3, the wrapper sentence, the indented line and the line after it.) | The cost is recorded and the red is not masked. |
| RP5 | Item 3 tells the leaf to save that run's output to `.tdd/red-run-output.txt`, the file `red-divergence.sh` dates the prediction file against. (Item 3, last sentence.) | The prediction is proven to predate the run. |
| RP6 | Item 4 tells the leaf to compare the output with the prediction and report Matched or Diverged; on a divergence the test is the suspect, and the leaf revises the test, predicts again and re-runs until the failure is the predicted one or it can say precisely why they cannot be reconciled, never adjusting the prediction to fit what it saw. (Item 4.) | A divergence exposes a case that fails for the wrong reason. |
| RP7 | Item 5 says either answer is acceptable and must be reported truthfully, and tells the leaf not to bend the test to force a failure. (Item 5, first two sentences.) | A forced failure would pin nothing. |
| RP8 | Item 5 tells the leaf that, if the case PASSES, it predicts what breaking the behaviour should print, breaks it, runs the case and checks the output against that prediction, all before restoring, then restores the production code exactly and verifies the restore with `git diff --exit-code` on the file it touched. (Item 5, from "If it PASSES" to the end.) | A passing pin is accepted only once seen to go red as predicted. |
| RP9 | Item 6 tells the leaf to leave no change to any file other than the test file, and no change in it outside the named case. (Item 6.) | Only the named case moves. |
| RP10 | The fragment ends by asking for the red report lines in order: `TEST_PATH:`, `TARGET_TEST:`, `AGAINST_UNMODIFIED: FAILS | PASSES | UNTESTABLE`, `WHY:` (UNTESTABLE only), `FAIL_OUTPUT:`, `PREDICTED_FAILURE:` (the missing name for a name error, otherwise assertion, values and message shape, as predicted before running), `PREDICTION: MATCHED | DIVERGED`, `PREDICTION_NOTE:` (on DIVERGED). (Report section.) | The conductor and `red-divergence.sh` read fixed lines. |

## skills/tdd/scripts/prompts/_develop-red-spec-and-testability.md

| ID | Requirement | Why |
|---|---|---|
| RT1 | The fragment gives the issue's behavior spec under a heading saying it is context only and that only the step above is pinned (`{{ISSUE_SPEC}}`), then the test command under its own heading (`{{TEST_CMD}}`), then opens the "What to do" list. (Headings and their slots.) | The spec informs without widening the pin. |
| RT2 | Item 0 tells the leaf to check testability first: before writing anything, hold the criterion against **What counts as a valid test** above, and if no case can pin it without breaking rule 1, 2 or 3, stop and report `AGAINST_UNMODIFIED: UNTESTABLE` with `WHY:`, not proceeding to the steps below; the fragment ends there. (Item 0.) | An untestable criterion is reported through a declared key, and the including prompt continues the list. |

## skills/tdd/scripts/prompts/_affected-suites-working-tree.md

| ID | Requirement | Why |
|---|---|---|
| AW1 | The fragment names `affected-suites.sh HEAD` as what prints the suites for the leaf's change, and says it reads `HEAD` to the working tree, untracked files included. (First line.) | The uncommitted change is what selects the suites. |
| AW2 | The fragment tells the leaf, for that reason, to build no commit, stash or worktree to name a range; it ends mid-sentence ("to name a range"), and the including prompt's sentence continues after it. (Last two lines.) | A commit, stash or worktree made only to name a range is wasted work, and a stash is unsafe. |

## skills/tdd/scripts/prompts/develop-green.md

| ID | Requirement | Why |
|---|---|---|
| GN1 | The prompt tells the leaf to write the **minimum** production code that makes the one failing test pass, and to keep the fast command and the affected suites green. (Opening paragraph under "## Phase: develop-green".) | Green buys only the behaviour the test demands, without breaking what already passes. |
| GN2 | Under "### The failing test" the prompt gives the test file `{{TEST_PATH}}`, the target case `{{TARGET_TEST}}` and the test command `{{TEST_CMD}}`, and the test-command line ends in the `{{FREEZE_RULE}}`, `{{REPLACES_CASE}}`, `{{SUITE_REPAIR}}` and `{{FIXTURE_REPAIR}}` slots. ("### The failing test" section.) | The leaf needs the exact test it must turn green, and the step-specific rules land beside it. |
| GN3 | The "### When the step is too big for one green" section says a step that needs more than one new behaviour at once has a third answer, and it is not a weakened test or a half-written implementation: the leaf reports `SPLIT:` lines; the sentence runs "instead of an" into the included `_develop-split.md` fragment, and closes by saying a tree left carrying part of an implementation nobody has written a test for would poison the first of them, so the leaf leaves the working tree exactly as it found it. ("When the step is too big for one green" section.) | A too-big step is answered by splitting it, never by cheating the test or leaving half an implementation behind. |
| GN4 | The behaviour-spec heading says the issue's spec is context and to build only what the failing test demands. ("### The issue's behavior spec" heading.) | The spec explains the intent but must not pull in untested code. |
| GN5 | Step 0 tells the leaf to check the step's size first: if it needs more than one new behaviour at once, stop here and report `SPLIT:` lines as the "When the step is too big for one green" section says, and not proceed to the steps below, because with no implementation written none of the runs they ask for has a question to answer. (What to do, item 0.) | The split decision comes before any code or run, and the stop names the report it ends in. |
| GN6 | Step 1 tells the leaf to make the target case pass with the smallest change that genuinely implements the behaviour, with no generality, options, flags or extra cases the test does not demand, because later steps triangulate those. (What to do, item 1.) | Untested generality is code no test pins. |
| GN7 | Step 2 tells the leaf to iterate against the suite that holds the target case, not the full suite, because that one suite answers the only question each iteration asks, in a fraction of the time. (What to do, item 2, first sentence.) | Iterating on the full suite costs time and answers nothing more. |
| GN8 | Step 2 tells the leaf to run one suite through the invocation the included `_run-suite-lead.md` fragment names; the sentence runs on through the included `_run-suite-same-way.md` fragment and ends "the test command above and say so in your report". (What to do, item 2, second sentence.) | A fallback to the whole test command must show in the report. |
| GN9 | Step 2 tells the leaf, before that run, to probe each branch, guard, default, flag, parameter, `__main__` block, flush or encoding line it added this step, naming them the usual offenders for code no test requires. (What to do, item 2, third sentence.) | Code no test requires is found by removing it, not by reading it. |
| GN10 | Step 2 tells the leaf to copy the file beside itself (`cp <file> <file>.orig`, never in a shared directory), remove that code and rerun the suite holding the target case: still green means the code was not required, so it keeps the removal and deletes the copy; red means it restores with `mv <file>.orig <file>`; and it leaves no `.orig` file behind either way. (What to do, item 2, last sentences.) | The probe is undone by a copy, never by a git command, and leaves no trace. |
| GN11 | Step 3 tells the leaf, exactly once and immediately before it writes the `SUITE:` report line, to run the fast command `{{FAST_CMD}}` (which `detect-test-command.sh --tier fast` prints), then run the suites the sentence names through the included `_affected-suites-working-tree.md` fragment, and confirm both runs are green. (What to do, item 3, first sentence.) | The fast command plus the affected suites is the green proof, taken once, right before it is reported. |
| GN12 | Step 3 tells the leaf to make each of those two runs through the wrapper (the included `_timed-test-run-tier.md` and `_timed-test-run-fast-affected.md` fragments), and the item continues after the included `_exit-status-back.md` fragment with "so a red run stays red". (What to do, item 3, wrapper sentences.) | The runs are recorded, and the wrapper must not mask a red result. |
| GN13 | Step 3 says that pair replaces the full suite and runs exactly once: the conductor runs the full command itself, before it readies the PR. (What to do, item 3, "That pair" sentence.) | The leaf does not run the full suite; the conductor does, once per PR. |
| GN14 | Step 3 says a new pass bought with a broken sibling test is not a pass, and tells the leaf to fix it or revert. (What to do, item 3, last sentence.) | A green that reddens another test is a regression. |
| GN15 | Step 4 tells the leaf to leave no change this step does not require. (What to do, item 4.) | The diff stays the step's change and nothing else. |
| GN16 | The report section asks, as the last lines of the output, for `IMPL_PATH: <comma-separated paths of the production files you created or changed>` and `SUITE: GREEN \| RED — <the final summary line of that run>`. (Report section, first two lines.) | The conductor reads which files changed and whether the run was green. |
| GN17 | The report section says that, when the step is too big for one green, those two lines are replaced by one to three `SPLIT:` lines, each a behaviour-level criterion, one per line, in the order they must be built. (Report section, the SPLIT: alternative.) | A split is reported in a fixed shape the conductor turns into steps. |
| GN18 | The report section says that, when the test itself looks wrong, those two lines are replaced by one `WRONG_TEST: <why the test looks wrong>` line, which names the existing test case the step's criterion contradicts, by its own name as its test file spells it, with no describe, class or file prefix. (Report section, the WRONG_TEST: alternative.) | The conductor routes a wrong test by the case it names, so the name must match the file. |
| GN19 | The report section says that, when older cases fail only because the step supersedes what they pin, the lines are replaced by one `SUPERSEDED:` line per such case, the older case's name written out in full as its test file spells it, without quotes; and that a case the step's change does not supersede is a `WRONG_TEST:` line, never a `SUPERSEDED:` one. (Report section, the SUPERSEDED: alternative and the sentence after it.) | A superseded case and a wrong test are routed differently, and the line must say which. |

## skills/tdd/scripts/prompts/_develop-green-freeze-rule.md

| ID | Requirement | Why |
|---|---|---|
| GF1 | The fragment opens with "**Do not modify the test.**" and says: not its assertions, not its inputs, not its name. (First two sentences.) | The test Red wrote and verify-red passed is the bar; green may not move it. |
| GF2 | The fragment says making the bar easier to clear is not clearing it: a pass bought by weakening, skipping or deleting the case is a rejected step. (Third sentence.) | A weakened test turns a failing behaviour into a false green. |
| GF3 | The fragment says that if the test itself looks wrong, the leaf says so in its report as one `WRONG_TEST: <why>` line and stops, without editing it. (Last sentence.) | A wrong test has its own route; the leaf reports it rather than fixing it. |

## skills/tdd/scripts/prompts/_develop-green-replaces-case.md

| ID | Requirement | Why |
|---|---|---|
| GC1 | The fragment completes the sentence opened by the included `_replaces-case-lead.md` fragment with "now asserts", then says the leaf is permitted, and it is required for the step to pass, to delete exactly the cases the step names, one or several. (First sentence, up to the colon.) | A replaces-case step moves cases, so the old ones must go. |
| GC2 | The fragment says deleting them is required, not optional, even when the replacement already passes on unchanged code. (First sentence, after the colon.) | A replacement that passes at once still leaves the old case to delete. |
| GC3 | The fragment tells the leaf never to modify or delete any other case, nor any case the step does not name. (Last sentence.) | The permission covers only the named cases. |

## skills/tdd/scripts/prompts/_develop-green-suite-repair.md

| ID | Requirement | Why |
|---|---|---|
| GU1 | The fragment opens with "**This step repairs the full run.**" and says the step's text lists every suite the full command left red, each with the name of its first failing case. (First two sentences.) | The leaf must know the step covers several suites, not one test. |
| GU2 | The fragment tells the leaf to make every listed suite green, not just the one named as the failing test, because a suite still red sends the run to bail. (Last sentence.) | A repair that greens one suite of several does not repair the run. |

## skills/tdd/scripts/prompts/_develop-green-fixture-repair.md

| ID | Requirement | Why |
|---|---|---|
| GX1 | The fragment opens with "**This step repairs a fixture.**" and says the script under test is correct; the defect is in the fixture, stub or helper the step names, in the fixture file it names. (First two sentences.) | The fix belongs in the test scaffolding, not in production. |
| GX2 | The fragment says the leaf may edit that fixture, only as far as the repair needs, and nothing else: not the target case, not any other case, and not any production file. (Third sentence.) | The permission to edit a test file covers the named fixture alone. |
| GX3 | The fragment says the target case must pass against the unchanged script under test. (Last sentence.) | The repair is proven by the existing production code passing. |

## skills/tdd/scripts/prompts/_develop-guard-subject-grant.md

| ID | Requirement | Why |
|---|---|---|
| GG1 | The fragment opens with "**One exception: the step's guard-subject file.**" and says the step names it in its `⟦guard-subject: <path>⟧` marker. (First line.) | The exception is tied to a file the step itself names. |
| GG2 | The fragment says the leaf may edit that file, and no other test file, and that the case Red wrote stays frozen. (Second line.) | Only the guard's subject opens; the test that pins the step stays the bar. |

## skills/tdd/scripts/prompts/_develop-repair-test-edit.md

| ID | Requirement | Why |
|---|---|---|
| TE1 | The fragment opens with "**You may edit the failing test.**" and says this step repairs a full run, the fix is often an edit to the test file that run left red, and the leaf edits that file only as far as the repair needs. (First two sentences.) | A repair step may need to fix the test that is actually wrong. |
| TE2 | The fragment says every other test stays frozen. (Third sentence.) | The permission covers the failing test alone. |
| TE3 | The fragment says making the bar easier to clear is not clearing it: a pass bought by weakening, skipping or deleting a case the repair does not require is a rejected step. (Last sentence.) | The edit permission is not a licence to weaken. |

## skills/tdd/scripts/prompts/_develop-split.md

| ID | Requirement | Why |
|---|---|---|
| SX1 | The fragment continues a sentence its including template opens with "Report `SPLIT:` lines instead of an": "implementation, changing no production code", one to three of them, each a behaviour-level criterion small enough to be one red-green cycle of its own, in the order they must be built. (First sentence.) | A split changes no code and gives the conductor steps it can run in order. |
| SX2 | The fragment says the conductor restores the tree, adds those steps ahead of this one and comes back to this step later, and ends on "so", which the including template completes. (Last sentence.) | The leaf knows its split steps run first and the current step returns after them. |

## skills/tdd/scripts/prompts/_develop-wrong-test-report.md

| ID | Requirement | Why |
|---|---|---|
| WT1 | The fragment says that, when the green being redone has a test that looks wrong, the report lines are replaced by one `WRONG_TEST: <why the test looks wrong>` line. (First paragraph and the `WRONG_TEST:` line.) | A revise of green keeps green's wrong-test route. |
| WT2 | The fragment tells the leaf to name in that line the existing test case the step's criterion contradicts, by its own name as its test file spells it, with no describe, class or file prefix. (The two sentences after the `WRONG_TEST:` line.) | The conductor routes a wrong test by the case it names. |
| WT3 | The fragment says that, when older cases fail only because the step supersedes what they pin, the lines are replaced by one `SUPERSEDED:` line per such case, the older case's name written out in full as its test file spells it, without quotes. (The `SUPERSEDED:` paragraph and line.) | A superseded case is reported in its own shape. |
| WT4 | The fragment says a case the step's change does not supersede is a `WRONG_TEST:` line, never a `SUPERSEDED:` one. (Last line.) | The two routes must not be confused. |

## skills/tdd/scripts/prompts/_develop-shared.md

| ID | Requirement | Why |
|---|---|---|
| DS1 | The fragment says the leaf is a developer agent in a strict TDD pipeline, working on ONE plan step of one issue, and that an independent verifier will check its work blind (given the spec and the code, never its reasoning), so what it leaves in the repository is the whole of its case. It then says three rules hold in every phase. (Opening paragraph.) | The developer must know its reasoning never reaches the judge, so only the repository speaks for it. |
| DS2 | Rule 1 tells the leaf to read the conventions out of the repository: where code and tests live, the test framework, the language level and the house style are facts established by reading the files already there, not preferences brought along, and it matches what it finds. (Numbered list, item 1.) | A leaf that imports its own conventions writes code the repository's tests and style do not fit. |
| DS3 | Rule 2 tells the leaf to report plainly and honestly: the conductor branches on the report lines at the end of its output, so they must say what actually happened, not what was supposed to happen. An unexpected result reported truthfully keeps the run on its rails, and a tidied-up one derails it. (Numbered list, item 2.) | The conductor acts on the report lines, so a tidied report sends the run down the wrong branch. |
| DS4 | Rule 3 opens by telling the leaf to run every test command in the foreground, and to report only after it has exited. (Numbered list, item 3, first sentence.) | A result the leaf has not waited for is not a result. |
| DS5 | Rule 3 goes on to tell the leaf never to end its turn while a suite run is still going. It gives the reason: a report written mid-run is read by the conductor as the suite's answer, a turn that ends with no report leaves it nothing to read, and either way the conductor pays for the same run twice. (Numbered list, item 3, rest of the item.) | A turn ended mid-run makes the conductor act on nothing, or pay for the run again. |
| DS6 | After the list, the fragment tells the leaf to work inside the current repository, keep its investigation tight and on-task, and change nothing the step does not require. (Paragraph after the numbered list.) | Changes outside the step widen the diff the blind verifier must judge. |
| DS7 | The fragment includes `_leaf-safety.md` on a line of its own, between that paragraph and the comment rule. (The include line.) | Every developer prompt carries the same safety rules from one source. |
| DS8 | The comment rule says a comment the leaf writes is one of two things only: a contract header (the usage line and the exit-code table, which no code expresses), or a warning where the shell itself is the hazard (bash 3.2, BSD versus GNU flags, `set -u`'s exit status, a `\|\| true` that is load-bearing under `pipefail`). Either must be succinct. (The comment rule paragraph, first two sentences.) | Comments are allowed only where they say something the code cannot. |
| DS9 | The comment rule says nothing else is written: no rationale, no issue archaeology, no restatement of the next line. (The comment rule paragraph, third sentence.) | Rationale and history in comments rot, and restating the code adds nothing. |
| DS10 | The comment rule ends by saying rationale goes to a test first (a comment claiming a line is load-bearing is a missing test), to an ADR second, and nowhere third, because blame already holds the issue numbers. (The comment rule paragraph, last sentence.) | A claim that a line matters belongs where it is checked or recorded, not in a comment. |

## skills/tdd/scripts/prompts/_leaf-safety.md

| ID | Requirement | Why |
|---|---|---|
| LS1 | The first paragraph opens with "**Never run `git stash`**" and gives the reason: the stash stack is one ref, `refs/stash`, in a `.git` shared by every worktree of the repository, so what the leaf pops may be another agent's work, and theirs is then lost. (First paragraph, first sentence.) | Concurrent runs share one stash stack, so a pop can destroy another run's work. |
| LS2 | The first paragraph gives the safe alternatives: to see the committed version of a file, read it with `git show HEAD:<path>`; to compare a whole tree against it, make a throwaway checkout with `git worktree add --detach <scratch> HEAD` and remove it afterwards. (First paragraph, second sentence.) | Forbidding the stash without an alternative would leave the leaf no way to see committed code. |
| LS3 | The first paragraph tells the leaf never to undo a probe with `git checkout -- <file>` or `git restore`, because both copy the file back from the index and so also throw away the step's uncommitted work. The paragraph ends with the included `_probe-restore.md` fragment. (First paragraph, third sentence and the include that follows it.) | Restoring from the index erases the step's own uncommitted changes along with the probe. |
| LS4 | The second paragraph tells the leaf never to change global or user-level configuration: not git's (`git config --global`, `~/.gitconfig`), not its shell's, not `~/.claude`. The reason given is that this configuration is shared with the operator and with every other run on the machine, and a cleanup that never runs (a `trap` in a killed process) leaves the change behind for all of them. (Second paragraph, first two sentences.) | A global change made by one leaf outlives it and alters every other run and the operator's own setup. |
| LS5 | The second paragraph ends by telling the leaf to simulate a condition with environment variables scoped to the one command, or with a throwaway directory made with `mktemp -d` and removed afterwards. (Second paragraph, last sentence.) | The leaf needs a scoped way to simulate the conditions it may not set globally. |
| LS6 | The fragment ends with the included `_signal-own-processes.md` fragment on a line of its own. (Last line.) | The process-signalling rule travels with the other safety rules to every prompt. |

## skills/tdd/scripts/prompts/_probe-restore.md

| ID | Requirement | Why |
|---|---|---|
| PB1 | The fragment tells the leaf to copy the file aside with `cp <file> <file>.orig` before the mutation and to put it back with `mv <file>.orig <file>` after. (The whole fragment.) | This is the restore that keeps the step's uncommitted work, in place of the index-based ones the safety rules forbid. |

## skills/tdd/scripts/prompts/_signal-own-processes.md

| ID | Requirement | Why |
|---|---|---|
| SO1 | The fragment opens with "**Signal only processes you started**", by the pid recorded when they were started. (First sentence, up to the dash.) | A leaf may only stop what it can prove is its own. |
| SO2 | The fragment says never by name or pattern, and names `pkill`, `killall` and `kill $(pgrep …)` as the forbidden forms. (First sentence, after the dash.) | These are the commands that match by pattern. |
| SO3 | The fragment gives the reason: a pattern matches every process on the machine, so it reaches another live run's supervisor and leaves. (Second sentence.) | Several runs share the machine, and a pattern kill takes theirs down too. |
| SO4 | The fragment tells the leaf to name an experiment's processes and leaves with the `exp-` prefix, which no live run uses. (Last sentence.) | A distinct prefix keeps an experiment's processes apart from live runs. |

## skills/tdd/scripts/prompts/_shared.md

| ID | Requirement | Why |
|---|---|---|
| SH1 | The fragment says the leaf is a blind independent verifier in a TDD pipeline: a different developer agent wrote the code under review, and the leaf is checking its claim. It then says two rules make the verdict trustworthy, and a third is what gets it to the conductor at all. (Opening paragraph.) | The verifier must know it judges someone else's claim, not its own work. |
| SH2 | Rule 1 says the leaf is blind: it has NOT been told the author's reasoning or rationale, only the issue's behavior spec, the test path and the repository itself. (Numbered list, item 1, first two sentences.) | The verdict is worth something only because the author's rationale cannot sway it. |
| SH3 | Rule 1 tells the leaf not to ask for the author's intent and not to assume it, and to judge only what the spec requires and what the code and test actually do. (Numbered list, item 1, last sentence.) | An assumed intent smuggles the author's rationale back in. |
| SH4 | Rule 2 says the leaf establishes ground truth itself: it trusts no reported result, runs the relevant test(s) itself with the project's test command and reads the real output. The exit status is the objective fact, and its judgement is the layer on top of it. (Numbered list, item 2, up to the last sentence.) | A reported result is the claim under review, not evidence for it. |
| SH5 | Rule 2's last sentence is built from two included fragments. It opens "Run one suite through", then comes the `_run-suite-lead.md` fragment, then "suite,", then the `_run-suite-same-way.md` fragment, and it ends "the project's own test command and say so in your report." (Numbered list, item 2, last sentence.) | The verifier runs one suite the same way as every other leaf on the step, and a fallback to the whole test command is reported, not hidden. |
| SH6 | Rule 3 opens by telling the leaf to run every test command in the foreground, and to write the two lines below only after it has exited. (Numbered list, item 3, first sentence.) | The verdict lines must follow the result they report. |
| SH7 | Rule 3 goes on to tell the leaf never to put a suite run in the background and then end its turn while that run is still going. It gives the reason: a turn that ends mid-run never writes the two lines, so there is no `VERDICT:` line for the conductor to read, and the verification counts as a system failure and is paid for again. (Numbered list, item 3, rest of the item.) | A missing verdict is a system failure that costs a whole re-verification. |
| SH8 | After the list, the fragment tells the leaf to work inside the current repository (it may read any file and run the test command) and to keep its investigation tight and on-task. It then includes `_leaf-safety.md` on a line of its own. (Paragraph after the numbered list, and the include line.) | The verifier is bounded to the repository and carries the same safety rules as the developers. |
| SH9 | The fragment tells the leaf to end its output with exactly two lines and nothing after them, with no surrounding code fence and no extra formatting: `VERDICT: PASS        (or REJECT)` and `REASON: <the objective result plus the judgement behind it, in one or two sentences — or one item per line where a check below asks for that>`. (The paragraph after the include, and the two lines it shows.) | The conductor reads exactly those last two lines. |
| SH10 | The fragment says that where a check tells the leaf to report something as a `FLAGS:` line, it may write one such line per finding immediately before the two final lines, and only there: the final two lines stay last, so nothing else follows them. (The paragraph after the two lines.) | FLAGS: lines must not displace the verdict from the last two lines. |
| SH11 | The fragment tells the leaf to use `PASS` only if every check holds, and otherwise `REJECT`, naming what fails and every item a check asks it to list. It says a `REJECT` stops the run, so the leaf must be specific enough that a human can act on it. (Last paragraph.) | A rejection stops the run, and a human then has to act on its reason. |

## skills/tdd/scripts/prompts/_exit-status-back.md

| ID | Requirement | Why |
|---|---|---|
| ES1 | The fragment says "The wrapper hands the command's own exit status straight back," and ends on that comma, so the text after its include line completes the sentence. (The whole fragment.) | The timing wrapper must not mask a red run, and the fragment is the first half of the sentence that says so. |

## skills/tdd/scripts/prompts/_run-suite-lead.md

| ID | Requirement | Why |
|---|---|---|
| UL1 | The fragment names `make test TESTS="<pytest file or node id>"` as the one invocation for a single suite. Its text stops at "the one invocation for a single", and the including text supplies the next word. (The whole fragment.) | Every leaf runs one suite with the same invocation, instead of establishing its own. |

## skills/tdd/scripts/prompts/_run-suite-same-way.md

| ID | Requirement | Why |
|---|---|---|
| SW1 | The fragment says the invocation is given so that every leaf on the step runs it the same way. If that invocation cannot run a suite in the repository, the fragment opens a fallback with "fall back to", and the including text completes it. (The whole fragment.) | Leaves on one step must agree on how a suite runs, and a repository without the invocation still needs a way to run one. |

## skills/tdd/scripts/prompts/_develop-run-suite-same-way.md

| ID | Requirement | Why |
|---|---|---|
| DW1 | The fragment says the invocation is given so that every leaf on the step runs it the same way. If that invocation cannot run a suite in the repository, the fragment opens a fallback with "fall back to", and the including text completes it. (The whole fragment.) | The developer leaves on one step must agree on how a suite runs, and a repository without the invocation still needs a way to run one. |

## skills/tdd/scripts/prompts/develop-refactor.md

| ID | Requirement | Why |
|---|---|---|
| RE1 | The prompt tells the leaf to apply behavior-preserving transformations to the code this cycle produced, or to report that nothing is left to tidy, and says the suites covering it stay green throughout. (Opening paragraph under "Phase: develop-refactor".) | The leaf must know the phase changes structure only, and that "nothing to do" is an answer. |
| RE2 | The prompt tells the leaf to confine the transform to the touched files, with one exception: a transform may touch a file outside that list only when it removes duplication between that file and code this cycle wrote; tidying code this cycle did not write is otherwise out of scope, however tempting. (Paragraph after the touched-files slot.) | The tidy-up stays bounded to this cycle's work. |
| RE3 | The prompt says a candidate's class is decided by what the transform changes, never by which file it sits in. (Section "The four classes of candidate", opening sentence.) | A file-based rule would misclassify a transform. |
| RE4 | The prompt defines a structural candidate as one that removes duplication, in code or in prose, extracts or inlines, deletes dead code, renames an identifier that misleads, narrows a scope that leaks, or moves logic to where it belongs. (Four classes list, first bullet.) | Only this class qualifies for a transform. |
| RE5 | The prompt defines a cosmetic candidate as one that rewords, re-cites, reflows or re-comments, without removing duplication and without changing an identifier or a structure. (Four classes list, second bullet.) | Cosmetic edits are never worth a transform. |
| RE6 | The prompt defines a test-only candidate as any transform that would change only files under a `tests/` directory, and tells the leaf to report it on a `CANDIDATES: test-only \| <transform>` line, never on a `CANDIDATES: structural` one. (Four classes list, third bullet.) | A tests-only change must not be counted as product refactoring. |
| RE7 | The prompt defines an out-of-scope candidate as a structural transform outside the issue's bounds or ruled out by its spec, and tells the leaf to report it on a `CANDIDATES: out-of-scope \| <transform>` line instead of a `CANDIDATES: structural` one. (Four classes list, fourth bullet, first two sentences.) | The run must not do work its issue rules out. |
| RE8 | The fourth bullet gives two exceptions decided by the files the transform changes: one that changes at least one of the touched files goes on a line kind of its own, `CANDIDATES: in-step \| <the files the transform changes, comma-separated> \| <transform>`, so the conductor can cover it; one that changes none of the touched files goes on a `CANDIDATES: out-of-bounds \| <transform>` line. (Four classes list, fourth bullet, the exceptions.) | The conductor routes an out-of-scope candidate by whether it touches this step's files. |
| RE9 | The prompt says a flag is something the leaf found and must not fix here, that its class is decided by what it names, and that the class rides on the `FLAGS:` line so the conductor routes it from the leaf's words rather than its own judgement. (Section "The three classes of flag", opening paragraph.) | Routing a flag must not depend on the conductor re-judging it. |
| RE10 | The prompt defines the three flag classes: overfit, where the code passes this step's test without implementing the behaviour the step's criterion states, hard-coding the one tested case; uncovered-spec, a behaviour the spec requires that no step of the plan covers; and beyond-spec, an input class or edge the spec does not ask for at all. (Three classes list.) | Each class leads to a different follow-up. |
| RE11 | Item 1 tells the leaf to triage the candidates in those files into the four classes, then apply the structural ones, most valuable first, up to the budget of `{{REFACTOR_BUDGET}}` transforms, and says only a structural candidate qualifies for a transform, never a cosmetic one. (What to do, item 1, first two sentences.) | The budget is spent on the best structural candidates only. |
| RE12 | Item 1 tells the leaf that of those it applies only duplication removal against code this cycle wrote, and no other structural transform here — extract a module, move behaviour, rename across files. (What to do, item 1, third sentence.) | Larger structural moves are recorded, not applied, inside a step. |
| RE13 | Item 1 tells the leaf to report every other structural candidate it sees on its own `CANDIDATES: structural` line rather than apply it, and one outside the issue's bounds on its own `CANDIDATES: out-of-scope` line (or its `CANDIDATES: in-step` or `CANDIDATES: out-of-bounds` kind). (What to do, item 1, last sentence.) | An unapplied candidate is recorded instead of lost. |
| RE14 | Item 2 tells the leaf to commit each transform on its own, as `refactor: <what changed> (#<issue>)`, never a batch, so a break stays attributable to one change. (What to do, item 2, first sentence.) | One commit per transform keeps a break attributable, and the commit carries the issue number. |
| RE15 | Item 3 tells the leaf to run the suites `affected-suites.sh` prints for the files `refactor-touched.sh` printed after each transform, not the full suite, says those suites must stay green, and tells the leaf to revert a transform that turns them red rather than leave a red suite behind, and carry on with the next candidate. (What to do, item 3, first three sentences.) | Each transform is proven on the suites it could break, and a red one is undone. |
| RE16 | Item 3's fallback sentence runs "Run one suite through" into the included `_run-suite-lead.md` fragment, continues "suite," into the included `_develop-run-suite-same-way.md` fragment, and ends "the test command above and say so in your report." (What to do, item 3, the fallback sentence.) | A fallback to the whole test command is reported, not hidden. |
| RE17 | Item 3 tells the leaf to make each of those runs through the wrapper `{{TIMED_TEST_RUN}}`, which records what the run cost and names the tier it belongs to, gives the run line as the included `_timed-test-run-affected.md` fragment, and ends the paragraph that follows with the clause (opened by the included `_exit-status-back.md` fragment) "so a suite a transform turned red still reads as red". (What to do, item 3, the wrapper paragraphs.) | Every run is costed, and a red result is not masked by the wrapper. |
| RE18 | Item 3 says that when a transform reached the one file outside the list the exception allows, its suites run too: the suites follow every file the transform touched, so the one suite that could catch the break it did cause is never the one it skipped. (What to do, item 3, last sentence.) | The exception's file is covered by its own suites. |
| RE19 | Item 4 says the full suite runs once per PR, before it is readied, and that the trade is that a break outside the affected set surfaces at that one full run, as the repair step a red result appends, rather than at the transform that caused it. (What to do, item 4.) | The leaf knows what the narrower runs give up and where it is caught. |
| RE20 | Item 5 is headed "No untested generality" and says generality is earned by triangulation — another test demanding it — never hand-written here, and tells the leaf not to add options, flags, parameters or abstraction no existing test requires. (What to do, item 5.) | Untested generality is code no test pins. |
| RE21 | Item 6 tells the leaf not to generalize overfit code itself and not to build anything the three flag classes name, and to report each finding as a `FLAGS:` line carrying its class, so the conductor can tell a triangulation this step owes from a step the plan is missing from a follow-up nobody is building in this run. (What to do, item 6.) | Findings are routed, not fixed out of turn. |
| RE22 | Item 7 tells the leaf that if no structural candidate is left under those rules, it changes nothing and reports "nothing left to tidy" — even when cosmetic candidates remain — and says that is a legitimate result, not a failure to find work. (What to do, item 7.) | An empty tidy-up must not be padded with cosmetic edits. |
| RE23 | The report's `RESULT:` line asks for "applied <the transform>, suites green", one line per transform applied, each on its own `RESULT:` line in the order applied, or "nothing left to tidy" if none was applied. (Report section, `RESULT:` line.) | The conductor counts and orders the applied transforms from these lines. |
| RE24 | The report's `CANDIDATES:` line lists the six shapes "structural \| <transform>", "cosmetic \| <transform>", "test-only \| <transform>", "out-of-scope \| <transform>", "in-step \| <files> \| <transform>" and "out-of-bounds \| <transform>", for a transform the leaf still sees left in those files, carrying its class, one per line, each on its own `CANDIDATES:` line, or "none". (Report section, `CANDIDATES:` line.) | Each candidate's class rides on its line so it can be recorded and routed. |
| RE25 | The report's `FLAGS:` line opens the overfit shape as "overfit \| <the" followed by the included `_flag-overfit.md` fragment, then gives the included `_flag-uncovered-spec.md` and `_flag-beyond-spec.md` fragments as the other two shapes, one finding per line, each on its own `FLAGS:` line, carrying the class it falls into, or "none". (Report section, `FLAGS:` line.) | The conductor routes each flag by the class on its line. |

## skills/tdd/scripts/prompts/_flag-uncovered-spec.md

| ID | Requirement | Why |
|---|---|---|
| FU1 | The fragment gives the uncovered-spec flag shape: the class `uncovered-spec`, then `<the behaviour>`, then `<the criterion or spec line requiring it>`, separated by ` \| `. (The whole fragment.) | A flag for a behaviour no step covers must name the behaviour and where the spec requires it, so the missing step can be planned. |

## skills/tdd/scripts/prompts/_flag-beyond-spec.md

| ID | Requirement | Why |
|---|---|---|
| FB1 | The fragment gives the beyond-spec flag shape: the class `beyond-spec`, then ` \| `, then `<what it names>`. (The whole fragment.) | A flag for something the spec does not ask for names it, so it becomes a follow-up rather than work in this run. |

## skills/tdd/scripts/prompts/develop-replaces-report.md

| ID | Requirement | Why |
|---|---|---|
| RX1 | The prompt says the leaf's earlier Red report is the file `{{REPORT_FILE}}`, and that it carries no `REPLACES:` line for each of the cases below, so the step cannot be checked. (Phase paragraph, first two sentences.) | The leaf is told which file is wrong and why the run cannot go on. |
| RX2 | The prompt tells the leaf to read the report and answer with a corrected one that carries a `REPLACES: <case> => <test id>` line for every one of those cases, the case name exactly as the step spells it. (Phase paragraph, third sentence.) | The conductor checks each named case against one line; a missing or respelled name leaves the step uncheckable again. |
| RX3 | The phase paragraph carries a `{{NODE_ID_RULE}}` slot right after the request for the corrected report and before the sentence on the listed case names. (Phase paragraph.) | The rule for what a test id is comes from one shared fragment, so this prompt and the Red prompt state it the same way. |
| RX4 | The phase paragraph ends by saying the listed case names are the exact strings to copy into the REPLACES: lines, and that they take precedence over anything the issue's prose says about how to spell a case name. (Phase paragraph, last sentence.) | The earlier report failed on case names; the listed strings, not the issue's wording, are what the check matches. |
| RX5 | Under their own headings the prompt gives the leaf the cases with no REPLACES: line (`{{MISSING_CASES}}`), the step (`{{STEP}}`) and the issue's behavior spec as context (`{{ISSUE_SPEC}}`). (Sections before "What to do".) | The leaf needs the exact cases to answer for and the step they come from. |
| RX6 | What to do tells the leaf to change no test and no production file, because only the report is wrong, and not to run a suite. (What to do.) | The tests already passed verification; this leaf only rewrites a report, so any file change is out of scope. |
| RX7 | The prompt ends with a report section whose last line is `REPLACES: <case> => <test id>`, and declares the format `replaces-report` with key `REPLACES:` as suite exempt, because the report is corrected and no file changed. (Report section.) | The conductor reads the declared key, and no suite line is owed when nothing ran. |

## skills/tdd/scripts/prompts/_develop-red-cases-replaces-case.md

| ID | Requirement | Why |
|---|---|---|
| RK1 | The fragment says the step replaces cases, so it is not one criterion, one case: the leaf writes one pytest replacement case for each bash case the step named, each in its own `def test_...`, with no extra cases and no generality the step does not ask for. (First sentence.) | A replaces-case step owes one replacement per named case, so the one-case rule of an ordinary Red does not apply. |
| RK2 | The fragment asks the leaf, for each of them, to report one line `REPLACES: <case name> => <pytest test id>` for each case the step named, the case name exactly as the step spells it, without the quote characters the step wraps it in. (Second sentence.) | The conductor matches each line against the step's case names; a quoted or respelled name matches none. |
| RK3 | The fragment ends with an include of `_develop-node-id-rule.md`, right after the sentence asking for the `REPLACES:` lines. (Last line, the include.) | What the test id must look like is stated once, in the shared fragment. |

## skills/tdd/scripts/prompts/_develop-red-cases.md

| ID | Requirement | Why |
|---|---|---|
| CS1 | The fragment says one criterion, one case: no extra cases, and no generality the step does not ask for. (The whole fragment.) | An ordinary Red pins one criterion with one case, so the verifier can judge it alone. |

## skills/tdd/scripts/prompts/_develop-node-id-rule.md

| ID | Requirement | Why |
|---|---|---|
| NI1 | The fragment says the test id is the pytest node id, `<path from the repository root>::<test name>`. (The whole fragment, first clause.) | The id is run and looked up as given, so it must name the case from the repository root. |
| NI2 | The fragment says the line starts at column 0 with no bullet or other prefix. (The whole fragment, second clause.) | The `REPLACES:` line is read from the start of a line; a bullet hides it. |

## skills/tdd/scripts/prompts/_develop-red-lead.md

| ID | Requirement | Why |
|---|---|---|
| RL1 | The fragment tells the leaf to add exactly **ONE** new failing test case, and to write **NO** production code, both words in bold capitals. (The whole fragment.) | An ordinary Red adds one failing case and no product code, so the Green that follows has one thing to make pass. |

## skills/tdd/scripts/prompts/_develop-red-ci-repair.md

| ID | Requirement | Why |
|---|---|---|
| RI1 | The fragment opens by saying, in bold, that this step repairs a red CI run. (First sentence.) | The leaf must know the failure it answers comes from CI, not from this machine. |
| RI2 | The fragment says the failing CI job's log quoted in the step text, with its test id and assertion diff, is this step's evidence of failure, whatever the case does on this machine. (Second sentence.) | A CI-only failure may not reproduce locally; the quoted log is what proves it. |
| RI3 | The fragment says that if the case passes locally the leaf reports `AGAINST_UNMODIFIED: PASSES` as it is, and that on this step that does not make it a pin, because the failure it answers is the CI one. (Last sentence.) | A local pass is reported honestly without turning a CI repair into a pin step. |

## skills/tdd/scripts/prompts/_develop-red-bug.md

| ID | Requirement | Why |
|---|---|---|
| UG1 | The fragment's heading says the issue is a bug, so Red is a reproduction. (Heading.) | The leaf switches from specifying new behaviour to reproducing a reported defect. |
| UG2 | The fragment says the spec below carries a `## Bug` section, the report as it was filed, which means this step's case is a reproduction rather than a fresh specification. (First paragraph, first sentence.) | It names where the reproduction's inputs come from. |
| UG3 | The fragment tells the leaf to write the test from *Expected*: that is the behaviour the code owes and the assertion the case makes. (First paragraph, second sentence.) | The assertion pins what the code should do, not what it did. |
| UG4 | The fragment tells the leaf to drive the test with *Steps to reproduce*, using *Environment* only to tell an incidental detail of the reporter's setup from a condition the behaviour depends on. (First paragraph, third sentence.) | The case reproduces the report without hard-coding the reporter's machine. |
| UG5 | The fragment tells the leaf, before it reports, to confirm the case fails with the behaviour *What happened* describes, not with a missing symbol, an import error or a typo, each of which is a red bar that says nothing about the reported defect. (First paragraph, fourth sentence.) | Only a failure of the reported shape proves the case reproduces the bug. |
| UG6 | The fragment says a failure of any other shape is the test's own bug: it is step 4's divergence, and the test is what changes. (First paragraph, last sentence.) | A wrong-shaped failure is fixed in the test, not passed on to Green. |
| UG7 | The fragment tells the leaf to name the case so it carries `#<n>`, the issue's number, in whatever the project's test-naming idiom already is, because once it is green it stays as this bug's regression test and the number says which report it stands for. (Second paragraph.) | The regression test stays traceable to the report it guards. |

## skills/tdd/scripts/prompts/develop-diff.md

| ID | Requirement | Why |
|---|---|---|
| DF1 | The prompt says this step's criterion is a property of the branch's own diff (something removed, left unchanged, or confined to named lines), that a blind verifier judges it against the diff alone, and so that no test is this step's deliverable. (Opening paragraph under "Phase: develop-diff".) | The leaf must know its deliverable is a diff, not a test. |
| DF2 | Under its own heading the prompt gives the leaf the step (`{{STEP}}`), followed by the include line of `_develop-spec-context-only.md`. (Section "The step" and the include after it.) | The leaf needs the criterion it is changing the diff for. |
| DF3 | Item 1 tells the leaf to make the change the step's criterion names, and nothing else, then commit that change as its own commit, its subject ending in `(#<issue>)`. (Numbered list, item 1.) | The diff holds one change, and its commit carries the issue number. |
| DF4 | Item 2 tells the leaf that, when the criterion is that something stays unchanged, it makes no commit and leaves the tree as it found it. (Numbered list, item 2.) | An "unchanged" criterion is satisfied by no diff at all. |
| DF5 | Item 3 tells the leaf to add no test, and says a case that pins this criterion by reading another file's text or the git history is rejected. (Numbered list, item 3.) | A test reading text or history is the substring pin a diff-checked step exists to avoid. |
| DF6 | Item 4 is the include line of `_develop-diff-run-fast-affected.md`. (Numbered list, item 4.) | The run that proves the change green comes after the change and its commit. |
| DF7 | The prompt ends by asking, in the last lines of the output, for a `DIFF:` line giving the change committed in one line, or NONE when the criterion is that something stays unchanged, and a `SUITE: GREEN \| RED` line with the final summary line of that run. (Section "Report".) | The conductor reads fixed lines to see what was committed and whether the run was green. |

## skills/tdd/scripts/prompts/develop-revise-diff.md

| ID | Requirement | Why |
|---|---|---|
| DQ1 | The prompt's phase heading names it develop-revise redoing diff, and the heading is followed by the include line of `_develop-revise-opening.md`. (Heading and the line after it.) | The leaf must know it redoes a rejected diff-checked step. |
| DQ2 | The prompt says this step's criterion is a property of the branch's own diff, judged against the diff alone, so no test is this step's deliverable. (Paragraph after the opening include.) | A redo must not answer a diff criterion with a test. |
| DQ3 | Under their own headings the prompt gives the leaf the step (`{{STEP}}`), the verifier's rejection reason (`{{REJECTION_REASON}}`, headed "address exactly this"), the issue's behavior spec as context with the criterion above as what is in scope (`{{ISSUE_SPEC}}`), and the test command (`{{TEST_CMD}}`). (Sections before "What to do".) | The redo is driven by the rejection reason, within the step's criterion. |
| DQ4 | Item 1 tells the leaf to read what this step left on disk and change it to answer that objection, and only that objection, then commit that change, its subject ending in `(#<issue>)`. (What to do, item 1.) | The redo fixes what was rejected, nothing more, and its commit carries the issue number. |
| DQ5 | Item 2 tells the leaf to add no test, and says a case that pins this criterion by reading another file's text or the git history is rejected. (What to do, item 2.) | A redo must not add the text pin the step avoids. |
| DQ6 | Item 3 is the include line of `_develop-diff-run-fast-affected.md`. (What to do, item 3.) | The redone change is proven green before the report. |
| DQ7 | Item 4 tells the leaf that, if the objection cannot be met (the criterion is already satisfied, or the reason asks for something the step cannot deliver), it reports `IMPOSSIBLE` and says why. (What to do, item 4.) | An objection that cannot be met is reported, not forced. |
| DQ8 | The prompt ends by asking, in the last lines of the output, for an `OUTCOME: REWRITTEN \| IMPOSSIBLE` line with what was changed or why the step cannot be met as stated, a `DIFF:` line with the change committed in one line or NONE, and a `SUITE: GREEN \| RED` line with the final summary line of that run. (Section "Report".) | The conductor reads fixed lines to decide whether to re-verify or bail. |

## skills/tdd/scripts/prompts/_develop-diff-run-fast-affected.md

| ID | Requirement | Why |
|---|---|---|
| DA1 | The fragment tells the leaf to run the fast command, `{{FAST_CMD}}`, then the suites that `affected-suites.sh` prints for the change, each through the wrapper; the sentence runs into the include line of `_timed-test-run-tier.md`, ends in a colon, and is followed by the include line of `_timed-test-run-fast-affected.md`. (First two lines and the include after them.) | A diff-checked change is proven on the fast tier and the affected suites, each run recorded by the wrapper. |
| DA2 | The fragment's last line tells the leaf to finish only when both runs are green. (Last line.) | A red fast or affected run means the change is not done. |
