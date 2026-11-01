## skills/tdd/scripts/prompts/develop-revise.md

| ID | Requirement | Why |
|---|---|---|
| DV1 | In a `⟦suite-repair⟧` or `⟦ci-repair⟧` revise-green prompt the permission to edit a test appears once, and it covers only the failing test the full run or CI left red; every other test stays frozen (#1653, #1920). | The repair can fix the test that is actually wrong without opening every other test to edits; PR #1907's review showed a mutant reading "Any test may change" survived. |
| DV2 | Every numbered item of the "What to do" list carries an instruction in every revise prompt the template renders, a `⟦suite-repair⟧` or `⟦ci-repair⟧` revise-green prompt included; no item renders empty. | After #1920 the repair revise-green prompt rendered item 2 as a bare `2.`, leaving the leaf to guess whether a step was dropped. |
| DV3 | Item 0 of "What to do" tells the leaf, when the phase it is redoing is green, to check the step's size first: if it needs more than one new behaviour at once, it stops here and reports `SPLIT:` lines as **When the step is too big for one green** above says, and does not proceed to the steps below. (What to do, item 0.) | A stop must be reported through a declared key, and an oversized step answers before any run. |
| DV4 | Item 3 ends with a sentence whose single-suite invocation and its fallback come from two included fragments (`_run-suite-lead.md`, then `_run-suite-same-way.md`), and which closes with "the test command above and say so in your report". (What to do, item 3, last sentence.) | A fallback to the whole test command is reported, so a run that ran more than one suite says so. |

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

## skills/tdd/scripts/prompts/_develop-revise-freeze-test.md

| ID | Requirement | Why |
|---|---|---|
| FT1 | The fragment opens, in bold, with: redoing an interface phase freezes the test files. (First sentence.) | The redo leaf must know which half of the tree is frozen. |
| FT2 | The fragment tells the leaf never to modify a test file, and says the conductor's freeze check rejects a redone expand, migrate or contract-b that touches one. (Second sentence.) | The frozen half is enforced by rejection, so a touched test is a wasted attempt. |

## skills/tdd/scripts/prompts/_develop-revise-freeze-production.md

| ID | Requirement | Why |
|---|---|---|
| FP1 | The fragment opens, in bold, with: redoing contract-a freezes the production files. (First sentence.) | The redo leaf must know which half of the tree is frozen. |
| FP2 | The fragment tells the leaf never to modify a production file, and says the conductor's freeze check rejects a redone contract-a that touches one. (Second sentence.) | The frozen half is enforced by rejection. |

## skills/tdd/scripts/prompts/_develop-test-rewrite-grant.md

| ID | Requirement | Why |
|---|---|---|
| TG1 | The fragment opens, in bold, with: a rewritten test is a new test, and owes a new prediction. (Bold lead.) | A redo of red that rewrites the test must not reuse the rejected attempt's prediction. |
| TG2 | The fragment tells the leaf to predict the rewritten test's failure before it runs any suite, in `.tdd/red-prediction.md`: which assertion fires first against the unmodified production code, the observed-versus-expected values it fires on, and the shape of the message the suite will print. (First sentence, after the bold lead.) | A prediction written before the run is what makes the red a real red. |
| TG3 | The fragment tells the leaf to then run, saving the run's output to `.tdd/red-run-output.txt`, compare what it printed against that prediction, and never adjust the prediction to fit what it saw. (First sentence, after the dash.) | The comparison is only honest if the prediction is fixed before the output exists. |
| TG4 | The fragment says the leaf whose attempt was rejected predicted a different test, so there is nothing here to inherit. (Last sentence.) | A fresh leaf must not look for an earlier prediction to reuse. |

## skills/tdd/scripts/prompts/_develop-test-move-contract-a.md

| ID | Requirement | Why |
|---|---|---|
| TM1 | The fragment tells the leaf, in a bold lead, to move the tests off the old interface, as contract-a does, by rewriting or deleting only the tests the rejection names that still exercise it. (First sentence.) | A redo of contract-a moves exactly the tests the verifier objected to. |
| TM2 | The fragment says no new failing test is written, so no prediction is owed. (Last sentence.) | Contract-a moves tests rather than writing a red, so a prediction ask would be wrong. |

## skills/tdd/scripts/prompts/develop-cover.md

| ID | Requirement | Why |
|---|---|---|
| CO1 | The prompt says this is a refactor run: the issue's subject is structure, not behaviour, so the step names one refactoring to apply later, in the transform phase; before anything moves, the leaf establishes whether the behaviour of the code that step will move is covered, meaning whether some existing test goes red when that behaviour breaks. (Opening paragraph, all but its last sentence.) | The leaf must know it measures coverage before a transform, and what "covered" means. |
| CO2 | The opening paragraph ends by telling the leaf to write no production code and no test. (Opening paragraph, last sentence.) | The cover phase only measures; it changes nothing. |
| CO3 | Item 1 tells the leaf to read the step and find the code it will move or reshape. (Numbered list, item 1.) | The mutation has to land in the code the transform will touch. |
| CO4 | Item 2 tells the leaf to copy the file first, `cp <file> <file>.orig`, and then break its behaviour by hand with a minimal edit to that production code: remove a guard, invert a condition, drop a branch. (Numbered list, item 2.) | The copy makes an exact restore possible, and a minimal break tests whether a test watches that behaviour. |
| CO5 | Item 3 tells the leaf to run the suites that cover that code through the wrapper `{{TIMED_TEST_RUN}}` (the run line is an included fragment), to expect red, and to note the test that caught the mutation. (Numbered list, item 3.) | The test that goes red is the evidence of coverage. |
| CO6 | Item 4 tells the leaf to restore the file exactly, `mv <file>.orig <file>`, and to prove the edit is gone: `git diff` must print what it printed before the mutation, and the working tree must be exactly as the leaf found it. (Numbered list, item 4.) | A mutation left behind would ship a broken product, and comparing `git diff` with its earlier output proves the restore. |
| CO7 | Item 5 tells the leaf that if no mutation it can make turns any test red, the code is not covered and it reports `COVERED: no`; it does not write a test to cover it, because that is not this phase's work. (Numbered list, item 5.) | Writing the missing test is another phase's job; this one only reports the gap. |
| CO8 | Item 6 allows `COVERED: unreachable` only for a step that only deletes code no caller reaches, with a `PROOF:` naming every caller and why none reaches the code: none exists, every caller passes a no-op, or the value is never read. (Numbered list, item 6.) | Unreachable is a narrow escape and has to be proven caller by caller. |
| CO9 | Item 7 allows `COVERED: type-only` only for a step that changes only types, with a `PROOF:` that is the type-check command the leaf ran green: `npx tsc --noEmit`, `mypy`, or the repository's own. (Numbered list, item 7.) | A types-only change has no runtime behaviour to mutate, so a green type-check stands in for the test. |
| CO10 | Item 8 says a step that moves or reshapes runtime code is never `unreachable` or `type-only`, and that reachable code no test watches is `COVERED: no`. (Numbered list, item 8.) | The two escapes must not excuse uncovered runtime code. |
| CO11 | The numbered list has eight items in this order: find the code (1), copy then break it (2), run the covering suites (3), restore and prove the tree unchanged (4), then the answers for not covered (5), unreachable (6), type-only (7) and reshaped runtime code (8). (Numbered list.) | The copy comes before the break, and the restore after the run that watches the break. |
| CO12 | The prompt ends by asking, in its last lines, for `MUTATION:` (the edit, in one line), `COVERED: yes \| no \| unreachable \| type-only`, `CAUGHT_BY:` (the test that went red, or NONE on no) and `PROOF:` (the callers and why none reaches the code, or the type-check command run green; NONE otherwise). (Report section.) | The conductor reads fixed lines to decide whether the transform may proceed. |

## skills/tdd/scripts/prompts/develop-cover-new.md

| ID | Requirement | Why |
|---|---|---|
| CN1 | The prompt says this is the cover-new phase of an interface change: the expand phase added the new interface, and before any caller moves onto it, it gets tests of its own; cases are added and production stays frozen. (Opening paragraph.) | The leaf must know which interface phase it is in and what it may touch. |
| CN2 | Step 1 tells the leaf to add cases that call the new interface directly, each pinning a behaviour the step names, and to leave every existing case and every caller as they are. (Numbered list, item 1.) | The new interface gets its own tests before callers move, without disturbing existing ones. |
| CN3 | Step 3 tells the leaf to commit the change as `test: <what changed> (#<issue>)`. (Numbered list, item 3, first sentence.) | The commit carries the issue number. |
| CN4 | Step 3 tells the leaf never to modify a production file: a cover-new commit that touches one is rejected. (Numbered list, item 3, second sentence.) | The frozen half of the phase is enforced by rejection. |
| CN5 | The numbered list has three items in this order: add the cases (1), run the suites covering the touched files (2, an included fragment), commit (3). (Numbered list.) | The cases are proven green before they are committed. |

## skills/tdd/scripts/prompts/develop-transform.md

| ID | Requirement | Why |
|---|---|---|
| TF1 | The prompt says this is a refactor run, that the cover phase has shown the code this step moves is covered, and tells the leaf to apply the one named refactoring below and commit it. (Opening paragraph, first two sentences.) | The leaf starts from proven coverage and applies exactly one refactoring. |
| TF2 | The prompt says behaviour does not change: every test that was green stays green, and no test file is touched. (Opening paragraph, last sentence.) | A refactor that changes a test could hide a behaviour change. |
| TF3 | The prompt says the step's criterion is a shell predicate stating the smell, false before this step and true after; it is the step's red, and the transform is what makes it true. (Paragraph after "The refactoring to apply".) | The leaf's success is measured by the predicate, not by a new test. |
| TF4 | Step 1 tells the leaf to apply exactly the refactoring the step names: no other transform, no behaviour change. (Numbered list, item 1.) | One step is one transform, so the diff stays reviewable. |
| TF5 | Step 2 tells the leaf to run the step's predicate and confirm it now holds. (Numbered list, item 2.) | The predicate is the step's criterion. |
| TF6 | Step 4 tells the leaf to commit the transform as `refactor: <what changed> (#<issue>)`. (Numbered list, item 4, first sentence.) | The commit carries the issue number. |
| TF7 | Step 4 tells the leaf never to modify a test file: a transform commit that touches one is rejected. (Numbered list, item 4, second sentence.) | The frozen half of the phase is enforced by rejection. |
| TF8 | The numbered list has four items in this order: apply the refactoring (1), confirm the predicate holds (2), run the suites covering the touched files (3, an included fragment), commit (4). (Numbered list.) | The predicate and the suites are proven before the commit. |
| TF9 | After the included report fragment, the prompt asks for a `PREDICATE: HOLDS \| FAILS` line and a `SUITE: GREEN \| RED — <the final summary line of that run>` line. (Lines after the report include.) | The conductor reads fixed lines for the predicate and the suite result. |

## skills/tdd/scripts/prompts/develop-structural.md

| ID | Requirement | Why |
|---|---|---|
| ST1 | After the included structural-pass sentence, the prompt tells the leaf to apply the one candidate below and commit it, and says behaviour does not change: every test that was green stays green, and no test file is touched. (Opening paragraph, after the include.) | The pass applies one recorded candidate as a pure refactor. |
| ST2 | Under "Bounds" the prompt tells the leaf to change only the files this issue touched, listed as `{{TOUCHED_FILES}}`. (Bounds, first paragraph.) | The structural pass may not reach outside the issue's own files. |
| ST3 | The prompt says a transform that needs a file outside that list is not this pass's to apply: the leaf leaves the tree as it found it and says so in its report as one `SKIPPED: <why>` line. (Bounds, last paragraph.) | An out-of-bounds candidate is reported through a declared key, not silently dropped or half-applied. |
| ST4 | Step 1 tells the leaf to apply exactly the candidate above: no other transform, no behaviour change. (Numbered list, item 1.) | One candidate is one transform. |
| ST5 | Step 3 tells the leaf to commit this one transform as its own commit, as `refactor: <what changed> (#<issue>)`. (Numbered list, item 3, first sentence.) | Each transform is its own commit, carrying the issue number. |
| ST6 | Step 3 tells the leaf never to modify a test file: a transform commit that touches one is rejected. (Numbered list, item 3, second sentence.) | The frozen half of the pass is enforced by rejection. |
| ST7 | The numbered list has three items in this order: apply the candidate (1), run the suites covering the touched files (2, an included fragment), commit (3). (Numbered list.) | The transform is proven green before it is committed. |
| ST8 | After the included report fragment, the prompt says that if the leaf skipped the candidate for the bound above, it reports that instead, as one `SKIPPED: <why>` line. (Paragraph after the report include.) | A skip replaces the transform report with the declared `SKIPPED:` key. |

## skills/tdd/scripts/prompts/develop-predicate.md

| ID | Requirement | Why |
|---|---|---|
| PD1 | After the included structural-pass sentence, the prompt says a transform leaf needs a check its verifier can run before it applies the candidate, and tells the leaf to write one shell predicate for it: a command that fails (exits non-zero) on the current tree and succeeds (exits 0) once the candidate is applied; the leaf applies nothing itself and changes no file. (Opening paragraph, after the include.) | The predicate becomes the transform step's red, so it must be false now and true after. |
| PD2 | Under "Bounds" the prompt says the transform may change only the files this issue touched, listed as `{{TOUCHED_FILES}}`. (Bounds.) | The predicate observes only files the transform may change. |
| PD3 | Step 1 tells the leaf to read the candidate and the files it names. (Numbered list, item 1.) | The predicate is written from the candidate's own files. |
| PD4 | Step 2 tells the leaf to write one shell command, runnable from the repository root, that observes the candidate's end state in those files (a `grep`, a `test`, a count compared) and nothing else. (Numbered list, item 2.) | A predicate that observes anything else could pass or fail for unrelated reasons. |
| PD5 | Step 3 tells the leaf to run the predicate on the current tree and confirm it fails. (Numbered list, item 3, first sentence.) | A predicate already true proves nothing about the transform. |
| PD6 | Step 3 says that when the candidate is already applied on the current tree, the leaf reports the predicate that observes its end state anyway (it then succeeds) and never `PREDICATE: NONE`. (Numbered list, item 3, second sentence.) | An applied candidate is still observable; NONE would wrongly claim it is not. |
| PD7 | Step 4 tells the leaf to keep `PREDICATE: NONE` for a candidate no single command can observe, and to say why instead of writing one. (Numbered list, item 4.) | NONE is reserved for the unobservable case, with its reason. |
| PD8 | The prompt ends by asking for one last line, either `PREDICATE: <command>` or `PREDICATE: NONE — <why>`. (Report section.) | The conductor reads one fixed line to get the predicate or its absence. |

## skills/tdd/scripts/prompts/develop-exhausted.md

| ID | Requirement | Why |
|---|---|---|
| XH1 | The prompt says the step's revise budget is spent and every attempt at it was rejected by the blind verifier; the next sentence opens with an included fragment and continues "those attempts, so the last rejection reason below is the whole of what you have to reason from." (Opening paragraph, first two sentences.) | The leaf works only from the last reason, never from the attempts' reasoning. |
| XH2 | A sentence opened by a second included fragment continues "the step again", and the paragraph then tells the leaf to answer in a `STATEMENT:` line. (Opening paragraph, third and fourth sentences.) | The leaf answers a question about the step and does not retry it. |
| XH3 | The prompt tells the leaf not to modify, revert or remove anything in the working tree, because what is there is the attempts' work and the run keeps it. (Opening paragraph, the "Do not modify" sentence.) | The attempts' work is kept for the human who reads the bail. |
| XH4 | The prompt says a statement that the criterion already holds must cite a run of the test command the leaf was given, not a run of one case alone. (Opening paragraph, last sentence.) | A claim that nothing needed doing has to rest on the whole command. |
| XH5 | Under their own headings the prompt gives the leaf the step (the criterion nothing could satisfy, `{{STEP}}`) and the verifier's last rejection reason (`{{REJECTION_REASON}}`), followed by an included fragment. (Sections after the opening paragraph.) | The leaf needs the criterion and the reason it could not be met. |

## skills/tdd/scripts/prompts/develop-over-budget.md

| ID | Requirement | Why |
|---|---|---|
| OB1 | The prompt says the step has crossed the spend budget it was given; the next sentence opens with an included fragment and continues "the attempts that spent it", and a sentence opened by a second included fragment continues "the step again". (Opening paragraph.) | The leaf is fresh, judges the step, and does not retry it. |
| OB2 | The prompt says a crossing is not a verdict: nothing has rejected this work, and the step may well be correct. (Second paragraph, first two sentences.) | A budget crossing must not be read as a rejection. |
| OB3 | The prompt asks whether the step is more than one behaviour, or needs a decision this run has no authority to make, and says "neither — this step is one behaviour that is simply expensive" is an honest answer the run can act on as well. (Second paragraph, last sentence.) | "Simply expensive" is a legitimate outcome, not a failure. |
| OB4 | Under their own headings the prompt gives the step (`{{STEP}}`) and what it has spent and the budget it was given, as `Spent: {{SPENT}}` and `Budget: {{BUDGET}}`, followed by an included fragment. (Sections before the report.) | The leaf weighs the step against the actual figures. |
| OB5 | The report section says that if the step is more than one behaviour, the leaf gives one to three lines, each a behaviour-level criterion small enough to be one red-green cycle of its own, in the order they must be built, as `SPLIT:` lines. (Report section, first paragraph and its line.) | A split is fed back into the ledger in build order. |
| OB6 | The report section says that if the step needs a decision this run has no authority to make, the leaf gives one line naming that decision, as `NEEDS_USER: <the decision, stated so the user can answer it>`. (Report section, second paragraph and its line.) | The decision is put to the human in a form they can answer. |
| OB7 | The report section says that if it is neither, because the step is one behaviour that is simply expensive, the leaf prints no `SPLIT:` line and no `NEEDS_USER:` line. (Report section, last paragraph.) | The absence of both keys is the simply-expensive answer, so it has its own report shape. |

## skills/tdd/scripts/prompts/verify-red.md

| ID | Requirement | Why |
|---|---|---|
| VR1 | The template opens with the `{{SHARED}}` slot, then the heading `## Phase: verify-red`. (First lines.) | The blind verifier's shared rules come first. |
| VR2 | The opening paragraph says a developer agent has written `{{RED_WRITTEN}}` at `{{TEST_PATH}}` (the target test is `{{TARGET_TEST}}`), and asks the verifier to confirm the Red step is sound. (Opening paragraph.) | The verifier is told what was written and where, and that its subject is the Red step. |
| VR3 | After the opening, the `{{STEP}}` slot runs straight into a `### The issue's behavior spec` heading over `{{ISSUE_SPEC}}`, then the `{{BUG_REPRODUCTION}}` slot, then the `### Your checks` heading. (Sections before the checks.) | The verifier reads the step and the spec, and a bug's reproduction rule when there is one, before the checks. |
| VR4 | Check 1, "It runs and fails", tells the verifier to run the suites `affected-suites.sh` prints for the change itself, not one suite picked by hand; the target test must **fail**, and check 2 is where the way it failed is judged. (Check 1, first paragraph.) | The red is observed on the suites the change affects, not on a suite the developer chose. |
| VR5 | Check 1 asks for that run through the wrapper, the sentence completed by the included `_timed-test-run-tier.md` fragment, shows the included `_timed-test-run-affected.md` command line, and ends with the included `_exit-status-back.md` fragment completed by "so a red run stays red — and red is what this check is after." (Check 1, after its first paragraph.) | The run's cost is recorded under its tier, and the wrapper must not mask the red the check wants. |
| VR6 | Check 2, "It fails for the right reason", says the failure must be the *missing behavior from the spec*: an absent function, script, file, route or field, or a wrong returned value. (Check 2, first sentence.) | A red that fails for the missing behaviour is the only red Green can turn green. |
| VR7 | Check 2 says an error on exactly the name the step introduces is a valid red: in bash, Python or JS a name that does not exist yet errors before any assertion runs, so a test that cannot even reach its assertions for that reason is red, not broken. (Check 2, second sentence.) | Rejecting that red would reject every test of a new name. |
| VR8 | Check 2 says any *other* error before an assertion is a REJECT, and names them: a typo'd name, a wrong path, a missing fixture, a syntax error in the test, or an unrelated environment problem. (Check 2, the sentence after the valid-red one.) | Those errors are a broken test, not a red for the missing behaviour. |
| VR9 | Check 2 says a test whose only failure is a NameError, or an equivalent undefined-name error, on a name the test file references and never defines or imports is a REJECT: a helper the test needs lives in the test file and is written in Red, so production code cannot supply it. (Check 2, the NameError sentence.) | Green may not edit a test, so a missing test helper can never be supplied. |
| VR10 | Check 2 ends: a test that fails for the wrong reason is a REJECT. (Check 2, last sentence.) | The check's verdict is stated outright. |
| VR11 | Check 3, "Quality of the test", opens "REJECT if the test is:", and its first bullet, **missing a named case**, is a step whose text names a test case the step asks to be pinned (a "separate case", a second behaviour) while the change adds no case for it: REJECT naming the missing case. (Check 3, lead and first bullet.) | A Red pinning only one of two demanded behaviours leaves the second unpinned. |
| VR12 | Check 3's **trivial** bullet: the test cannot meaningfully fail once the behavior exists (asserts a constant, `assert True`, tests nothing the spec asks for). (Check 3, second bullet.) | A test that cannot fail pins nothing. |
| VR13 | Check 3's **over-coupled** bullet: the test asserts on private internals / implementation details rather than the observable behavior the spec describes. (Check 3, third bullet.) | Such a test breaks on refactoring and pins the wrong thing. |
| VR14 | Check 3's **too complex** bullet: the test pins more than this one criterion, or is so elaborate its own correctness is in doubt. (Check 3, fourth bullet.) | One cycle pins one criterion, with a test simple enough to trust. |
| VR15 | Check 3's **pins mechanism, not behaviour** bullet: the test asserts a process count, a fork count, or a timing (those belong to `make profile`, never to an assertion), or counts real process launches via a `PATH` shim over a suite run where the criterion actually names a single call: that call belongs to an in-process spy on the one wrapper function, not a shim counting real processes. (Check 3, fifth bullet.) | Counts and timings are observed with `make profile`; a suite asserts behaviour. |
| VR16 | Check 3's **not lightweight** bullet: the test exercises a costly real dependency (network, a git remote, the `claude` binary, a real sleep/wait, a server) that a stub, fake or the injected clock could stand in for, and the behavior under test is not that dependency's real use. (Check 3, sixth bullet.) | Costly dependencies make the suite slow without pinning more. |
| VR17 | Check 3's **not self-contained** bullet: the test runs another test suite, whole or sliced, or re-runs the suite it lives in, instead of exercising the unit directly; the bullet ends in the `{{RED_FAST_CHECK}}` slot. (Check 3, last bullet.) | No suite runs another suite. |
| VR18 | The closing paragraph says PASS only if the test fails for the right reason AND is a clean, behavior-level pin of the criterion. (Closing paragraph.) | Both the failure and the test's quality must hold. |
| VR19 | Check 3's REJECT list has a bullet for a test failing on an incidental error: its only observable is that something throws or exits non-zero, with no assertion on which error or on the behaviour, unless that specific error is what the criterion names. | Any exception turns such a test red, and removing the exception turns it green with the behaviour still wrong. |

## skills/tdd/scripts/prompts/verify-green.md

| ID | Requirement | Why |
|---|---|---|
| VG1 | The template opens with the `{{SHARED}}` slot, then the heading `## Phase: verify-green`. (First lines.) | The blind verifier's shared rules come first. |
| VG2 | The opening paragraph says a developer agent has written the implementation intended to make the target test `{{TARGET_TEST}}` at `{{TEST_PATH}}` pass, and asks the verifier to confirm the Green step is a genuine pass. (Opening paragraph.) | The verifier's subject is the claim that the target now passes for real. |
| VG3 | After the opening, the `{{STEP}}` slot runs straight into a `### The issue's behavior spec` heading over `{{ISSUE_SPEC}}`, then the `### Your checks` heading. (Sections before the checks.) | The verifier reads the step and the spec before the checks. |
| VG4 | Check 1, "The target test passes", tells the verifier to run `{{TARGET_TEST}}` itself, which must pass, through the wrapper (the included `_timed-test-run.md` fragment) "and names the tier it belongs to", as `{{TIMED_TEST_RUN}} target '{{TEST_PATH}}' <the command that runs the target test>`, and ends with the included `_exit-status-back.md` fragment completed by "so a red run stays red". (Check 1.) | The pass is observed by the verifier, under the target tier, with a red result left red. |
| VG5 | Check 2, "The fast command and the affected suites are green", tells the verifier to run the fast command, `{{FAST_CMD}}` (`detect-test-command.sh --tier fast` prints it), then the suites `affected-suites.sh` prints for the change itself, not just the target test. (Check 2, first sentence.) | A green bought by breaking a sibling shows only on the wider run. |
| VG6 | Check 2 says there must be **no regressions**: every test that passed before must still pass, and a new pass bought with a broken sibling test is a REJECT. (Check 2, second and third sentences.) | The step must not trade one test for another. |
| VG7 | Check 2 says this is not the project's full test suite: the conductor runs that once, before it readies the PR. (Check 2, the full-suite sentence.) | The full suite is the conductor's, paid once per PR, not once per step. |
| VG8 | Check 2 asks for each of those two runs through the same wrapper, each under its own tier, followed by the included `_timed-test-run-fast-affected.md` lines and then the included `_verify-coverage-probe.md` paragraph. (Check 2, last sentence and the lines under it.) | Each run's cost is recorded under its own tier. |
| VG9 | Check 3, "The pass is genuine", says the behavior the spec asks for is actually present: the test was not made to pass by weakening the assertion, deleting cases, skipping/xfailing the test, or hard-coding the exact expected value in a way that doesn't implement the behavior, and any of these is a REJECT. (Check 3.) | A pass faked against the test is not the behaviour. |
| VG10 | Check 3 ends in the four slots `{{REPLACES_CASE}}{{SUITE_REPAIR}}{{CI_REPAIR}}{{FIXTURE_REPAIR}}`, in that order, on its last line. (Check 3, last line.) | A marked step's extra paragraph lands inside the genuineness check. |
| VG11 | Check 4, "Only code a test requires", says to REJECT production code that no test requires (a branch, option, flag, parameter or guard whose removal leaves every test green) and to name that code in REASON:, since a verdict that only says something is unneeded costs the revise leaf the search the verifier has already done. (Check 4, first sentence.) | Code no test requires is untested; naming it saves the redo a search. |
| VG12 | Check 4 tells the verifier to probe every branch, option, flag, parameter and guard the step's diff added before it answers, and not to stop at the first one whose removal leaves every test green: it names each such item in REASON:, one per line, since the revise leaf fixes only what it is told. (Check 4, second sentence.) | A verdict naming only the first unrequired item costs a revise cycle per item. |
| VG13 | Check 4 says to establish each the way verify-pin establishes a mutation: remove the code through `{{MUTATION_PROBE}} <file> <old> <new> -- <command that runs the suites>`, which edits, runs the command and restores the file; an exit of 1 (the suites stay green) means nothing required the code, and an exit of 2 gives no verdict. (Check 4, the probe sentence.) | The probe restores the file itself, and its two non-zero exits mean different things. |
| VG14 | Check 4 ends by telling the verifier to confirm that `git diff` prints what it printed before the probe, before it reports, since a verifier that reports first leaves the developer's tree mutated for the next leaf; the check names neither `git checkout --` nor `git diff --exit-code`. (Check 4, last sentence.) | The restore is confirmed against the tree as it was, which still holds the step's uncommitted work. |
| VG15 | Check 5 is assembled from the included `_verify-comments-lead.md`, the word "change", the included `_verify-comments-allowed.md`, the word "change", and the included `_verify-comments-never-reject.md`. (Check 5.) | The comment rule is shared with verify-refactor and stated once. |
| VG16 | After the checks, a paragraph says that when a REJECT's cause is a behaviour no test pins (a line the step needs that every test leaves unchecked), the verifier puts one `MISSING_TEST: <behaviour>` line, naming that behaviour, before the `VERDICT:` line, and that a rejection for a product defect carries no such line. (The `MISSING_TEST:` paragraph.) | The conductor routes a missing test to a new Red instead of a revise of correct code. |
| VG17 | The closing paragraph says PASS only if the target test, the fast command and the affected suites are green and the pass genuinely reflects the behavior the spec requires. (Closing paragraph.) | The verdict needs both the green runs and a genuine pass. |
| VG18 | The "Only code a test requires" check: production code outside the step's criterion is rejected by asking for its removal, never by offering a test for it, and the `MISSING_TEST:` paragraph says such code is not named on that line. | verify-pin and verify-red reject a test outside the criterion, so an offered test spends the step's revise budget on a contradiction (clarion2 issue #3, step R5, `revise-exhausted`). |

## skills/tdd/scripts/prompts/verify-refactor.md

| ID | Requirement | Why |
|---|---|---|
| VF1 | The template opens with the `{{SHARED}}` slot, then the heading `## Phase: verify-refactor`. (First lines.) | The blind verifier's shared rules come first. |
| VF2 | The opening paragraph says a developer agent has finished the **refactor** pass for this cycle (the code and test around `{{TEST_PATH}}`), and that the refactor is meant to be **behavior-preserving** tidy-up. (Opening paragraph, first two sentences.) | The verifier judges a tidy-up, which may not change behaviour. |
| VF3 | The opening paragraph says the step's green commit, where the refactor started, is `{{BASE_SHA}}`; the verifier reviews what the refactor changed with `git diff {{BASE_SHA}}..HEAD` and does not read the range's commit messages, since `git log` and `git show` on the range carry the author's rationale; it renders one verdict on the settled result. (Opening paragraph, rest.) | The verifier stays blind to the author's reasons and judges the whole settled range. |
| VF4 | After the opening, the `{{STEP}}` slot runs straight into a `### The issue's behavior spec` heading over `{{ISSUE_SPEC}}`, then the `### Your checks` heading. (Sections before the checks.) | The verifier reads the step and the spec before the checks. |
| VF5 | Check 1, "Still green", tells the verifier to run the fast command, `{{FAST_CMD}}` (`detect-test-command.sh --tier fast` prints it), then the suites `affected-suites.sh` prints for the files the refactor touched itself; both must be **green**, and a refactor that changed observable behavior or broke any test is a REJECT. (Check 1, first paragraph.) | Behaviour preservation is observed on the fast tier and the affected suites. |
| VF6 | Check 1 asks for each of those two runs through the wrapper (the included `_timed-test-run-tier.md` fragment), shows the included `_timed-test-run-fast-affected.md` lines, then the included `_exit-status-back.md` fragment completed by "so a red run stays red", then the included `_verify-coverage-probe.md` paragraph. (Check 1, after its first paragraph.) | Each run's cost is recorded under its tier, and a red result is not masked. |
| VF7 | Check 2, "Up to standard", says the settled code should be code the verifier would approve: it follows the repository's **conventions**, uses sensible **typing**/structure where the project does, names things clearly, and is reasonably **robust**. (Check 2, first sentence.) | The refactor phase exists to leave code at the repository's standard. |
| VF8 | Check 2 says the code must not have smuggled in untested generality: generality is only earned through triangulation, not hand-written here. (Check 2, last sentence.) | Generality no test forced is untested code. |
| VF9 | Check 3, "A missing case is a flag, not a REJECT", says an obvious unhandled edge case the spec implies is not by itself a REJECT: handling it changes behavior, which a behavior-preserving refactor may not do, so the REJECT would demand what no revise leaf can give, since the answer to a missing case is a new test, not tidier code. (Check 3, first sentence.) | A REJECT no revise leaf can satisfy only spends the revise budget. |
| VF10 | Check 3 tells the verifier to report the unhandled edge case on a `FLAGS:` line instead, written before the final `VERDICT:`/`REASON:` pair and carrying its class: `FLAGS: overfit \| <the ` completed by the included `_flag-overfit.md` when the code passes the step's test without implementing what the step's criterion states, `FLAGS: ` with the included `_flag-uncovered-spec.md` when the spec requires a behaviour no step covers, or `FLAGS: ` with the included `_flag-beyond-spec.md` for anything the spec does not ask for; one finding per line, and no other class is offered. (Check 3, rest.) | The conductor triages each flag by its class instead of losing the finding. |
| VF11 | Check 4, "No assertion loosened", says a removed or weakened test assertion in the range is a REJECT, and the REJECT names that assertion: the suite stays green while it loosens, so the diff is the only place it shows. (Check 4.) | A loosened assertion hides from every green run. |
| VF12 | Check 5, "Cosmetic hunks", says a hunk that is only cosmetic (whitespace, reflowed prose, a rename with no other effect) is named in REASON: but is not a REJECT by itself, since a REJECT costs a revise leaf. (Check 5.) | Cosmetic noise is reported without spending a revise. |
| VF13 | Check 6, "Empty range", says an empty range, which a reset of the leaf's commits leaves, is not a REJECT by itself: the verifier judges the settled result as it stands. (Check 6.) | A refactor leaf that found nothing to tidy has not failed. |
| VF14 | Check 7, "Out of scope", says a shortfall against a criterion outside the step under judgement is named in REASON: as out of scope and is not by itself a REJECT: a behavior-preserving refactor may not add another step's work, so demanding it here is a demand no revise leaf can satisfy. (Check 7.) | Another step's work belongs to that step's cycle. |
| VF15 | Check 8, "The cycle's files", says the files this cycle touched are the ones `git diff --name-only {{BASE_SHA}}^ {{BASE_SHA}}` names and the refactor was confined to them; the verifier derives that list itself and reads it as paths and nothing else. (Check 8, first sentence.) | The bounds come from the green commit, not from the developer's account. |
| VF16 | Check 8 says a changed file outside that list is a REJECT, unless its hunk removes duplication between that file and code in the list, the one reason a transform was allowed to leave the list for. (Check 8, last sentence.) | A refactor confined to the cycle's files cannot drift into unrelated code. |
| VF17 | Check 9 is assembled from the included `_verify-comments-lead.md`, the word "range", the included `_verify-comments-allowed.md`, the word "range", and the included `_verify-comments-never-reject.md`. (Check 9.) | The comment rule is shared with verify-green and stated once. |
| VF18 | The closing paragraph says PASS if the suite is green and the code is up to standard, and REJECT, naming the specific weakness, if the tidy-up left the code below standard or altered behavior. (Closing paragraph.) | The verdict needs both behaviour preserved and the standard met. |

## skills/tdd/scripts/prompts/verify-pin.md

| ID | Requirement | Why |
|---|---|---|
| VP1 | The template opens with the `{{SHARED}}` slot, then the heading `## Phase: verify-pin`. (First lines.) | The blind verifier's shared rules come first. |
| VP2 | The opening paragraph says a developer agent has written **one new test** at `{{TEST_PATH}}` (the target test is `{{TARGET_TEST}}`) for a criterion the code **already satisfies**, so there is nothing to make fail, and asks the verifier to confirm the test is a genuine **regression pin** worth committing. (Opening paragraph.) | A pin has no red, so its value is proven another way. |
| VP3 | After the opening, the `{{STEP}}` slot runs straight into a `### The issue's behavior spec` heading over `{{ISSUE_SPEC}}`, then the `### Your checks` heading. (Sections before the checks.) | The verifier reads the step and the spec before the checks. |
| VP4 | Check 1, "It passes now", tells the verifier to run the target test itself against the current, unmodified code; it must **pass**, not error, not skip. (Check 1.) | A pin must hold on the code as it is. |
| VP5 | Check 2, "It fails under mutation", tells the verifier to identify the behavior the spec criterion describes and break the production code itself with a minimal edit (remove the guard, invert the condition, drop the branch) through `{{MUTATION_PROBE}} <file> <old> <new> -- <command that runs the target test>`, which edits, runs the command against the mutation and restores the file: the target test must **FAIL**. (Check 2, first sentence.) | A test that fails when the behaviour breaks is what makes it a pin. |
| VP6 | Check 2 says a probe exiting 2 gives no verdict, and one exiting 1 (the command still passed) is never a PASS. (Check 2, second sentence.) | The probe's two non-zero exits mean different things. |
| VP7 | Check 2 tells the verifier to confirm that `git diff` prints what it printed before the probe before it reports; the check names neither `git checkout --` nor `git diff --exit-code`. (Check 2, the restore sentence.) | The restore is confirmed against the tree as it was, which still holds the step's uncommitted work. |
| VP8 | Check 2 says a test that still passes with the behavior removed pins nothing: that is a REJECT. (Check 2, the sentence after the restore.) | The mutation is the pin's whole proof. |
| VP9 | Check 2 asks for both runs, the one in check 1 and the one after the mutation, through the wrapper `{{TIMED_TEST_RUN}}`, which records what each run cost and names the tier it belongs to, as `{{TIMED_TEST_RUN}} target '{{TEST_PATH}}' <the command that runs the target test>`, and ends with the included `_exit-status-back.md` fragment completed by "so the mutated run stays red — and red is what check 2 is after." (Check 2, last paragraph.) | Both runs are costed under the target tier, and the wrapper must not mask the mutated red. |
| VP10 | Check 3, "Quality of the test", opens "REJECT if the test is:", and its first bullet, **missing a named case**, is a step whose text names a test case the step asks to be pinned (a "separate case", a second behaviour) while the change adds no case for it: REJECT naming the missing case. (Check 3, lead and first bullet.) | A pin of only one of two demanded behaviours leaves the second unpinned. |
| VP11 | Check 3's **trivial** bullet: the test asserts a constant or something no plausible change could break. (Check 3, second bullet.) | A test no change could break pins nothing. |
| VP12 | Check 3's **over-coupled** bullet: the test asserts on private internals / implementation details rather than the observable behavior the spec describes. (Check 3, third bullet.) | Such a test breaks on refactoring and pins the wrong thing. |
| VP13 | Check 3's **too complex** bullet: the test pins more than this one criterion, or is so elaborate its own correctness is in doubt. (Check 3, fourth bullet.) | One step pins one criterion, with a test simple enough to trust. |
| VP14 | Check 3's **pins mechanism, not behaviour** bullet: the test asserts a process count, a fork count, or a timing (those belong to `make profile`, never to an assertion), or counts real process launches via a `PATH` shim over a suite run where the criterion actually names a single call: that call belongs to an in-process spy on the one wrapper function, not a shim counting real processes. (Check 3, fifth bullet.) | Counts and timings are observed with `make profile`; a suite asserts behaviour. |
| VP15 | Check 3's **not lightweight** bullet: the test exercises a costly real dependency (network, a git remote, the `claude` binary, a real sleep/wait, a server) that a stub, fake or the injected clock could stand in for, and the behavior under test is not that dependency's real use. (Check 3, sixth bullet.) | Costly dependencies make the suite slow without pinning more. |
| VP16 | Check 3's **not self-contained** bullet: the test runs another test suite, whole or sliced, or re-runs the suite it lives in, instead of exercising the unit directly. (Check 3, last bullet.) | No suite runs another suite. |
| VP17 | The closing paragraph says PASS only if all three hold: it passes now, it fails under the mutation, and it is a clean, behavior-level pin of the criterion; and it tells the verifier to leave the working tree exactly as it found it. (Closing paragraph.) | The verdict needs all three checks, and the mutation must not survive the verification. |
| VP18 | Check 3's REJECT list has a bullet for a test failing on an incidental error: its only observable is that something throws or exits non-zero, with no assertion on which error or on the behaviour, unless that specific error is what the criterion names. | A pin like this survives its mutation check today and is disarmed by any later change to the throw (#2506). |

## skills/tdd/scripts/prompts/verify-plan.md

| ID | Requirement | Why |
|---|---|---|
| VL1 | The template opens with the `{{SHARED}}` slot, then the heading `## Phase: verify-plan`. (First lines.) | The blind verifier's shared rules come first. |
| VL2 | The opening paragraph says the conductor has scoped one issue into a plan, the ledger below, and is about to run its steps; the verifier's subject is that plan, not anyone's code. (Opening paragraph.) | The plan verifier judges coverage of the issue, not an implementation. |
| VL3 | The prompt gives `### The issue's behavior spec` over `{{ISSUE_SPEC}}`, then `### The proposed plan (the ledger)` over `{{LEDGER}}`, then `### Your checks`; it has no `{{STEP}}` slot. (Sections before the checks.) | The plan is judged against the whole issue, with no step under judgement. |
| VL4 | Check 1, "Every criterion is delivered by its steps, taken together", tells the verifier, for each acceptance criterion `k` in the spec, to read the ledger steps tagged `⟦criterion k⟧` and ask one question: do those steps, together, deliver criterion k **as written**, in the criterion's own terms rather than the plan's paraphrase of it? (Check 1, first sentence.) | A plan that paraphrases a criterion can drift from it unnoticed. |
| VL5 | Check 1 says a step naming some mechanism the criterion might be built from delivers the criterion only when that mechanism is sufficient for the criterion as written: a mechanism that is necessary but not enough leaves the criterion undelivered, however true the step is of the mechanism. (Check 1, second sentence.) | A necessary part is not the whole criterion. |
| VL6 | Check 2, "Any step too big for one Red → Green → Refactor cycle", tells the verifier to read each step on its own and ask whether a developer could take it from one failing test to green and then tidy up: a step bundling two or more new behaviours is too big for one cycle. (Check 2, first sentence.) | A bundled step cannot be pinned by one failing test. |
| VL7 | Check 2 carries no verdict of its own: the verifier names every step it judges too big in its `REASON:` line, whether the verdict is PASS or REJECT, so the observation reaches the conductor either way. (Check 2, last sentence.) | The size observation informs the conductor without blocking a plan that covers its criteria. |
| VL8 | The paragraph after the checks says to use PASS when every criterion is delivered by the steps tagged for it: check 1 is the whole of what the verdict asks, so a plan meeting it passes even where the verifier would have planned the work differently. (Verdict paragraph, first sentence.) | A REJECT over planning taste would stop a correct plan. |
| VL9 | The same paragraph says to REJECT the plan when no step establishes a criterion as written: an uncovered criterion is itself the REJECT, not a PASS whose reason mentions the gap. (Verdict paragraph, second sentence.) | A gap mentioned in a PASS still ships the gap. |
| VL10 | A paragraph says two shapes of criterion have no failing test to write, so the plan carries each as one line rather than a step; its first bullet: a criterion whose only observable is that the repository's test command passes ("the suites are green") is one `⟦full-suite⟧ ⟦criterion k⟧` line, covered by the full-suite run. (The two-shapes paragraph and its first bullet.) | "The suites are green" is owed by the full run, not by a Red. |
| VL11 | Its second bullet: a criterion whose deliverable is the record of a manual check (each suite broken on purpose, watched going red, the output recorded) is owed by a human, not by code, so it is one `⟦human-owed⟧ ⟦criterion k⟧` line that no developer leaf is ever handed. (The two-shapes paragraph, second bullet.) | A leaf cannot record a human's manual check. |
| VL12 | For check 1, a `⟦full-suite⟧ ⟦criterion k⟧` or `⟦human-owed⟧ ⟦criterion k⟧` line delivers criterion k by itself: such a criterion is owed no step, and its line is never a reason to REJECT. (The paragraph after the two bullets.) | Those lines are the plan's correct answer to those shapes. |
| VL13 | The prompt says to REJECT a plan that turns either shape (the test command or the suites passing, or the record of a manual check) into a Red/Green step instead of its `⟦full-suite⟧` or `⟦human-owed⟧` line, even where check 1 alone would pass it: a Red leaf handed that step can only answer `UNTESTABLE`, and the run bails. (The paragraph after it.) | The misplanned step bails the run. |
| VL14 | A third shape has no test to leave behind: a diff-property criterion, a property of the branch's own diff (something removed, something left unchanged, a change confined to named lines), is one `⟦diff-checked⟧ ⟦criterion k⟧` line, judged against the diff by a blind verifier, and that line delivers criterion k by itself. (The third-shape paragraph, first two sentences.) | A diff property is judged on the diff, with no case left behind. |
| VL15 | The same paragraph says a criterion stating a rule every future change must keep is not this shape, and stays a Red/Green step. (The third-shape paragraph, last sentence.) | A lasting rule needs a case that keeps guarding it. |
| VL16 | The prompt says to REJECT a plan that turns a diff-property criterion into a Red/Green step instead of its `⟦diff-checked⟧` line. (The paragraph after the third shape, first clause.) | A Red cannot write a failing test for a diff property. |
| VL17 | The same paragraph says to REJECT a plan with a step whose test reads another suite's source text or the git history: such a test pins text rather than behaviour, and goes red on the next legitimate edit of what it reads. (The paragraph after the third shape, second clause.) | A suite asserts behaviour, not another suite's text or history. |
| VL18 | The prompt says to REJECT a plan that carries a Red/Green step whose criterion changes rendered prompt text, or a SKILL.md sentence that a suite pins by checksum or verbatim, instead of a `⟦diff-checked⟧` line: a Red leaf cannot compute a checksum of text that does not exist yet, so that text and every pin it moves land in one commit, judged blind against the diff. (The pinned-text paragraph.) | Such a step cannot go red first, so the run would bail. |
| VL19 | The prompt says to REJECT a plan in which a criterion that both changes rendered prompt text or a SKILL.md sentence a suite pins by checksum or verbatim, and asks for a case pinning that text, has only the `⟦diff-checked⟧` step: such a criterion needs a `⟦diff-checked⟧` step for the text and a separate step for the case, both tagged with the same `⟦criterion k⟧`, the case's step after the text's; every checksum or verbatim pin that template text moves is moved in the same commit as the text. (The pinned-text-with-a-case paragraph.) | A diff-checked step may not add a test, so the case needs its own step. |
| VL20 | The prompt says to REJECT a plan that changes text or output which existing cases outside the changing step's own Red pin (a usage string, a constant, rendered prompt text compared verbatim or by checksum) without a step that updates those older cases ahead of the step that changes the text: Green may not edit a test, so the older cases go red and the revise budget runs out; the reason names the changing step and the text its older cases pin. (The older-cases paragraph.) | Older pins must move before the text, or Green can never pass. |
| VL21 | The prompt says to REJECT a plan with a step that introduces a branch (a fallback an existing suite forces in, say) that only a later step's test requires, because that step's blind green verifier sees code none of its own tests requires and rejects correct code until the revise budget runs out; the reason names both steps, the introducing step and the later pinning step, so the plan can be reordered or the branch moved to the step that pins it. (The branch-ordering paragraph, first two sentences.) | Unrequired code is rejected by verify-green, so the branch must arrive with its pin. |
| VL22 | The same paragraph says a step bringing in code after the steps that pin its branches is not a REJECT on ordering grounds, and neither is one bringing in only the branches its own test requires, the rest arriving with the steps that pin them. (The branch-ordering paragraph, last sentence.) | The rule targets only branches that arrive before their pin. |
| VL23 | The prompt says to REJECT a plan whose only steps for a criterion delivered by an interface change that also asks for a test case are a `⟦phases: …⟧` step: the case must be its own Red/Green step tagged with the same `⟦criterion k⟧`, because a case that exists only inside the phased step is never checked by a verifier; the reason names the criterion and the test case it asks for. (The phased-step paragraph.) | No verifier checks a case written inside a phased step. |
| VL24 | The prompt says to REJECT a plan whose step drops a constraint the issue attaches to the cases that step covers (the case size it must keep, medium with a real process; "no production change"; or an end-to-end path through real processes that must stay covered); the reason names the step and the constraint it leaves out. (The dropped-constraint paragraph.) | A step that drops the issue's constraint delivers a weaker case than asked. |
| VL25 | The prompt says to REJECT a plan that plans a test-only change, one satisfiable only by editing a test, as a Red/Green step: Green may not edit a test, so the run bails on it. (The test-only paragraph, first sentence.) | The misplanned step bails the run. |
| VL26 | The same paragraph says such a change is a pin step when it adds a test case for behaviour that already holds (an ordinary step whose Red reports that the case already passes, `AGAINST_UNMODIFIED: PASSES`), and that `⟦diff-checked⟧` is reserved for steps that leave no test behind, so it is never offered for a change that adds a case. (The test-only paragraph, rest.) | A case for behaviour that holds is a pin, not a diff check. |
| VL27 | The prompt says to REJECT a plan whose `⟦diff-checked⟧` step text asks for a test to be added (a case, a pinning case, a process case): verify-diff rejects every `⟦diff-checked⟧` step whose own commits add a test, so such a step can never pass; the reason names the step and the test it asks for. (The diff-checked-asks-for-a-test paragraph.) | The step would bail on verify-diff's own rule. |
| VL28 | The exception is a well-formed `⟦fixture-repair⟧` step, for a defect in a test's own fixture, stub or harness whose script under test is correct, whose line shape is `- [ ] <criterion>: repairs the fixture '<fixture or stub name>' in <fixture file>, reproduced by a case in <test file> ⟦fixture-repair⟧ ⟦criterion k⟧`. (The fixture-repair paragraph, first two sentences.) | A broken fixture is repaired in the test file, which only this step may touch. |
| VL29 | The same paragraph says to REJECT a `⟦fixture-repair⟧` step whose spec places the defect in the script under test, one that names no fixture (a function, stub or helper, not a line range), and one whose fixture file is not a test file by `transform-touches-tests.sh`'s rule (under a `tests/` directory, or named `*.test.*`); the reason names the step and which of the three it is. (The fixture-repair paragraph, last two sentences.) | A malformed fixture-repair step would license test edits it should not. |
| VL30 | The prompt says to REJECT a plan in which a step's behaviour can only be observed once a later step is built: a step asserting that an input is ignored, guarded or without effect ("even when X is left in storage", "without dev tools") passes against unmodified code until a later step makes the code read that input, so a test for it cannot fail first. (The later-step paragraph, first sentence.) | Such a step's Red cannot go red. |
| VL31 | The same paragraph says such a step belongs after the step that makes the code read that input, a plan placing it before that step is the REJECT, and the REASON: line names both steps, the early step and the later step it waits on. (The later-step paragraph, rest.) | The fix is a reorder, and the reason must say which. |
| VL32 | The prompt says to REJECT a plan in which a step adds a script under `skills/tdd/scripts/` whose no-argument usage line and exit 2, or whose declared caller, arrives only in a later step, since the repo-wide audits go red on the adding step whatever its green does; the reason names both steps, the adding step and the later step that brings the usage or the caller. (The added-script paragraph.) | The audits fail the adding step however correct its green is. |
| VL33 | The prompt says to REJECT a plan holding a step that carries the `⟦replaces-case⟧` mark but does not name its cases in the form `replaces '<case name>', '<case name>' in <suite path>`, quoting each case name, because the guard that reads the names cannot read any other form; the reason names the step. (The replaces-case paragraph.) | The guard would read no names and pass nothing. |
| VL34 | The prompt says to REJECT a plan holding a step that carries `⟦guard-subject: P⟧` where the step text or the spec names `P` as that step's Red test file (the file its failing case is written in): `tests-frozen` records the Red's test file whole, so a Green editing `P` can never pass `tests-frozen check --step`; the reason names the step and `P`. (The guard-subject paragraph.) | The step could never pass its own frozen-tests check. |
| VL35 | The prompt says to REJECT a plan holding a step whose text names more than one observable outcome (a behaviour plus each distinct refusal, exit code or fail-closed branch): the Red adds one case, so a second outcome is a guard no case pins, and verify-green rejects it until the revise budget runs out; the reason names the step and the split it needs, one outcome per step. (The one-outcome paragraph, first three sentences.) | An unpinned second outcome is rejected as unrequired code. |
| VL36 | The same paragraph says a step naming exactly one outcome, a behaviour alone or one guard alone, is accepted: the verifier counts the named outcomes, and never refuses a step for merely mentioning a guard. (The one-outcome paragraph, last sentence.) | Over-applying the rule would split steps that need no split. |
| VL37 | The `{{REFACTOR_PLAN}}` slot stands on its own line after the one-outcome paragraph and before the paragraph on what a REJECT must name. (After the REJECT paragraphs.) | A refactor issue's extra checks land among the plan's rules. |
| VL38 | The prompt says a REJECT must name the criterion it fails on and state the part of it no step covers, in the criterion's own words, so that the plan can be rewritten from the reason alone. (Second-last paragraph.) | The planner rewrites the plan from the reason and nothing else. |
| VL39 | The last paragraph says a step carrying no `⟦criterion k⟧` tag (a gap step, which the planning leaf is asked to write for a behaviour the issue's prose needs and no acceptance criterion covers) is never by itself a reason to REJECT: it belongs to no criterion, so check 1 has no question to ask of it; it is still subject to check 2 like any other step. (Last paragraph.) | Gap steps are asked for, so rejecting them would reject the planner's instructions. |

## skills/tdd/scripts/prompts/verify-rebase.md

| ID | Requirement | Why |
|---|---|---|
| VB1 | The template opens with the `{{SHARED}}` slot, then the heading `## Phase: verify-rebase`. (First lines.) | The blind verifier's shared rules come first. |
| VB2 | The opening paragraph says this run's branch was rebased onto `{{ONTO_SHA}}`, the default branch's tip, from `{{PRE_REBASE_SHA}}`, where it stood before. (Opening paragraph, first sentence.) | The verifier knows both ends of the rebase. |
| VB3 | The opening paragraph says the rebase stopped on conflicts and a developer agent resolved them, so that resolution is new code no verifier has seen, and tells the verifier to judge the rebased branch at `HEAD`. (Opening paragraph, rest.) | A conflict resolution is unverified code and gets its own blind check. |
| VB4 | After the opening, the `{{STEP}}` slot runs straight into a `### The issue's behavior spec` heading over `{{ISSUE_SPEC}}`, then the `### Your checks` heading. (Sections before the checks.) | The verifier reads the step and the spec before the checks. |
| VB5 | Check 1, "The full test command is green on HEAD", tells the verifier to run the project's full test command (`detect-test-command.sh` prints it) itself, on `HEAD`, not the fast tier: a resolution can break a suite no single file's change would name. (Check 1, first paragraph.) | A resolution's breakage need not map to any one file's suites. |
| VB6 | Check 1 asks for that run through the wrapper (the included `_timed-test-run-tier.md` fragment), under `all`, since the whole test command is what runs, as `{{TIMED_TEST_RUN}} all '' <the full test command>`, then the included `_exit-status-back.md` fragment completed by "so a red run stays red.", and says a red run is a REJECT. (Check 1, rest.) | The full run is costed under its tier, and a red result is not masked. |
| VB7 | Check 2, "Both sides survive", says the branch's own changes (`git diff {{ONTO_SHA}}...{{PRE_REBASE_SHA}}` shows them) and the default branch's changes (`git diff {{PRE_REBASE_SHA}}...{{ONTO_SHA}}` shows them) must both be present in `HEAD`, with their behaviour intact. (Check 2, first sentence.) | A rebase that loses either side's work is not a resolution. |
| VB8 | Check 2 says a resolution that drops or weakens either side's change is a REJECT even when the suite is green, and the REJECT names the file and the change that was lost. (Check 2, last sentence.) | A green suite can miss a dropped change. |
| VB9 | The closing paragraph says PASS only if the full test command is green on HEAD and both the branch's changes and the default branch's changes survived the resolution. (Closing paragraph.) | The verdict needs both checks. |

## skills/tdd/scripts/prompts/verify-transform.md

| ID | Requirement | Why |
|---|---|---|
| VT1 | The template opens with the `{{SHARED}}` slot, then the heading `## Phase: verify-transform`. (First lines.) | The blind verifier's shared rules come first. |
| VT2 | The opening paragraph says this is a **refactor** run and that a developer agent has applied one named refactoring for this step and committed it. (Opening paragraph, first two sentences.) | The verifier judges one named transformation. |
| VT3 | The opening paragraph says the step's predicate record, the shell command stating the smell, is `{{TEST_PATH}}`, false before the step and true after, and that the step started at `{{BASE_SHA}}`; it never calls that base a green commit. (Opening paragraph, the predicate and start sentences.) | A transform's base is where the step started, not a Green's commit. |
| VT4 | The opening paragraph tells the verifier to review what the step changed with `git diff {{BASE_SHA}}..HEAD` (the whole range, not a subset of files), not to read the range's commit messages because `git log` and `git show` on the range carry the author's rationale, and to render one verdict on the settled result. (Opening paragraph, rest.) | The verifier stays blind and judges the whole range. |
| VT5 | After the opening, the `{{STEP}}` slot runs straight into a `### The issue's behavior spec` heading over `{{ISSUE_SPEC}}`, then the `### Your checks` heading. (Sections before the checks.) | The verifier reads the step and the spec before the checks. |
| VT6 | Check 1, "The predicate holds", tells the verifier to run the command in `{{TEST_PATH}}` itself; it must succeed. (Check 1.) | The smell's predicate is the step's deliverable. |
| VT7 | Check 2, "Behaviour unchanged", tells the verifier to run the suites covering the files the range touched, through the wrapper `{{TIMED_TEST_RUN}}`; they must be **green**, and the included `_timed-test-run-affected.md` command line follows, indented. (Check 2.) | A refactoring preserves behaviour, observed on the affected suites. |
| VT8 | Check 3, "One refactoring", says the range applies the refactoring the step names and nothing else. (Check 3.) | One step is one named transformation. |
| VT9 | Check 4, "No observable change", says a range that changes observable behaviour is a REJECT. (Check 4.) | A refactoring that changes behaviour is not a refactoring. |
| VT10 | The closing paragraph says PASS if the predicate holds, the suites are green, the range is that one refactoring and it changes no observable behaviour, and REJECT, naming the specific problem, otherwise. (Closing paragraph.) | The verdict restates every check. |

## skills/tdd/scripts/prompts/verify-diff.md

| ID | Requirement | Why |
|---|---|---|
| VD1 | The template opens with the `{{SHARED}}` slot, then the heading `## Phase: verify-diff`. (First lines.) | The blind verifier's shared rules come first. |
| VD2 | The opening paragraph says the step under judgement is a criterion about this branch's own diff (something removed, left unchanged, or confined to named lines), and that no test is its deliverable. (Opening paragraph, first two sentences.) | The verifier judges a diff property, not a test. |
| VD3 | The opening paragraph says the run branched at `{{BASE_SHA}}` and tells the verifier to judge the step's criterion against `git diff {{BASE_SHA}}..HEAD` alone, and not to read the range's commit messages, because `git log` and `git show` on the range carry the author's rationale. (Opening paragraph, rest.) | The verifier stays blind and judges the branch's whole diff. |
| VD4 | After the opening, the `{{STEP}}` slot runs straight into a `### The issue's behavior spec` heading over `{{ISSUE_SPEC}}`; the template has no `### Your checks` heading. (Sections.) | The verifier reads the step and the spec before the run instructions. |
| VD5 | The run paragraph tells the verifier to run the fast command, `{{FAST_CMD}}`, then the suites `affected-suites.sh` prints for the files the diff touched, each through the wrapper (the included `_timed-test-run-tier.md` fragment), shows the included `_timed-test-run-fast-affected.md` lines, then the included `_exit-status-back.md` fragment completed by "so a red run stays red.", then the included `_verify-coverage-probe.md` paragraph. (The paragraphs after the spec.) | A diff that removes code is still proven green, with each run costed under its tier. |
| VD6 | The closing paragraph says PASS if the diff satisfies the step's criterion, and REJECT, naming where the diff falls short, otherwise. (Closing paragraph, first two sentences.) | The verdict is about the criterion against the diff. |
| VD7 | The closing paragraph says REJECT, too, if the fast command or the affected suites are red. (Closing paragraph, third sentence.) | A diff that breaks a suite fails whatever the criterion says. |
| VD8 | The closing paragraph says REJECT, too, if the step's own commits add a test (those in `git diff {{STEP_BASE_SHA}}..HEAD`, never a test an earlier step of the run added): a criterion judged against the diff is never also pinned by a case left behind. (Closing paragraph, fourth sentence.) | A diff-checked step leaves no test; an earlier step's tests are not this step's. |
| VD9 | The closing paragraph ends: End with `VERDICT: PASS` or `VERDICT: REJECT`. (Closing paragraph, last sentence.) | The conductor reads one fixed verdict line. |

## skills/tdd/scripts/prompts/_verify-green-replaces-case.md

| ID | Requirement | Why |
|---|---|---|
| QR1 | The fragment opens with the `{{INCLUDE:_replaces-case-lead.md}}` line and continues that line's sentence with "is to assert instead". (First line, up to the first full stop.) | The shared lead names the step's cases; this half says the pytest case is what now asserts their behaviour. |
| QR2 | It tells the verifier to PASS only if every named case is gone from its suite and each has a pytest case asserting its behaviour, the same behaviour that bash case asserted. (Second sentence, before the semicolon.) | A replaces-case step is done only when every named case is both deleted and replaced like for like. |
| QR3 | It tells the verifier to REJECT a deletion or modification of any case the step does not name, or of any other case. (Second sentence, after the semicolon.) | The permission to delete covers the named cases only. |

## skills/tdd/scripts/prompts/_replaces-case-lead.md

| ID | Requirement | Why |
|---|---|---|
| RH1 | The fragment opens with the bold lead "This step replaces cases." (First sentence.) | The leaf sees at once that the step is a replacement, not new behaviour. |
| RH2 | It says the step's text names one suite path and one or more of that suite's bash cases, each by its exact name. (Second sentence, up to "each by its exact name".) | A step may replace several cases, and each is named exactly so it can be found and deleted. |
| RH3 | The second sentence stops unfinished after "whose behaviour a pytest case", with no verb and no full stop; the text that includes the fragment completes it. (Second sentence, its last clause.) | The develop and verify paragraphs share this lead and each finishes the sentence its own way. |

## skills/tdd/scripts/prompts/_verify-green-suite-repair.md

| ID | Requirement | Why |
|---|---|---|
| QS1 | The fragment opens with the bold lead "This step repairs the full run." and says the step's text lists every suite the full command left red, each with the name of its first failing case. (First two sentences.) | The verifier knows which suites the repair must turn green. |
| QS2 | It tells the verifier to PASS only when every listed suite is green, judged by running the full test command itself rather than the fast command. (Third sentence, before the semicolon.) | A full-run repair is proven only on the command that went red. |
| QS3 | It says a listed suite still red is a REJECT. (Third sentence, after the semicolon.) | One suite left red means the repair is not done. |

## skills/tdd/scripts/prompts/_verify-green-ci-repair.md

| ID | Requirement | Why |
|---|---|---|
| QC1 | The fragment opens with the bold lead "This step repairs a failure that reproduces only on CI." (First sentence.) | The verifier knows the usual local evidence does not exist for this step. |
| QC2 | It says the step's local suites are green both before and after the fix, so it is not judged by the local check that the target goes red when the fix is removed, and tells the verifier to skip that check. (Second sentence.) | A revert-goes-red check cannot fail locally for a CI-only failure, so demanding it would reject every such fix. |
| QC3 | It says the evidence is what exists before the push: the failing CI job's log before the fix. (Third sentence.) | The CI log is the only record of the failure. |
| QC4 | It tells the verifier to PASS when the step quotes that log, the diff touches what the failure names, and the local suites are green. (Fourth sentence.) | These are the three things checkable before the push. |
| QC5 | It tells the verifier never to require a CI run on the fix, because until after the push no CI run exists, and says that the step's latest CI run being the red one that created it is expected. (Fifth sentence.) | Requiring a green CI run before the push is unsatisfiable, and the red run is the step's origin, not a fault. |
| QC6 | It says a green CI run on the pushed fix is the verdict of `wait-ci.sh` after the verifier's PASS, where red bails `ci-red`. (Last sentence.) | The CI verdict is someone else's check, made after the push. |

## skills/tdd/scripts/prompts/_verify-green-fixture-repair.md

| ID | Requirement | Why |
|---|---|---|
| QF1 | The fragment opens with the bold lead "This step repairs a fixture." and says the script under test is correct: the defect is in the fixture, stub or helper the step names, in the fixture file it names. (First two sentences.) | The verifier judges a change to a test fixture, not to production. |
| QF2 | It tells the verifier to REJECT, naming the path or hunk, any change outside the target test's file, the named fixture file and Red's case. (Third sentence.) | A fixture repair may touch only those files; anything else is a hidden change. |
| QF3 | It tells the verifier to PASS only when the target case passes with every change confined to those. (Last sentence.) | The repair is proven by the target case, within the permitted files. |

## skills/tdd/scripts/prompts/_verify-plan-refactor.md

| ID | Requirement | Why |
|---|---|---|
| QP1 | The fragment says this issue is a refactor: its spec carries a `## Refactor` section, so each step is one Cover → Transform → Verify cycle rather than a Red → Green → Refactor one. (Opening paragraph, first sentence.) | The plan verifier judges a different cycle shape for a refactor issue. |
| QP2 | It says five more checks apply to the steps tagged with a criterion, the first three only to a step that is neither ⟦diff-checked⟧ nor a pin step, and five REJECT bullets follow. (Opening paragraph, last sentence, and the bullet list.) | A diff-checked or pin step has no Transform, so the refactoring checks would reject it wrongly. |
| QP3 | The first bullet says to REJECT a step that does not name one refactoring — the single transformation, by name, that its Transform applies, such as Extract Function or Move Function — rather than paraphrasing the issue ("tidy the helpers"). (Bullet 1.) | An unnamed transformation cannot be checked against what the Transform did. |
| QP4 | The second bullet says to REJECT a step whose smell is not stated as a runnable shell predicate in its criterion: a command that is false before the step and true after it, which the verifier can run. (Bullet 2.) | The predicate is how the refactor's effect is observed. |
| QP5 | The third bullet says to REJECT a step that leaves a no-op in place for a later step to delete — one that makes code dead by passing a no-op (`onChange={() => {}}`) while another step deletes it; the deletion belongs in the step that makes the code dead. (Bullet 3.) | A no-op left for a later step ships dead code between steps. |
| QP6 | The fourth bullet says to REJECT a refactor-kind plan that holds a ⟦phases: …⟧ step, because a rename that tests call is an interface change, filed without the `refactor` label. (Bullet 4.) | An interface change runs the phased procedure, not the refactor cycle. |
| QP7 | The fifth bullet says to REJECT a refactor-kind plan that holds a step that only edits tests, unless that step is planned as ⟦diff-checked⟧ or a pin step, because a test-only criterion has no production code to transform. (Bullet 5.) | A Transform needs production code to act on. |

## skills/tdd/scripts/prompts/_verify-comments-allowed.md

| ID | Requirement | Why |
|---|---|---|
| QA1 | The fragment opens mid-sentence with "adds is allowed only as a" and says such a comment is allowed only as a contract header (a usage line or exit-code table) or a succinct warning where the shell itself is the hazard, with bash 3.2, BSD versus GNU flags, `set -u`'s exit status and a load-bearing `|| true` as the examples. (First sentence.) | Only two kinds of comment carry information the code cannot. |
| QA2 | Its second sentence tells the verifier to REJECT any other rationale comment, and stops unfinished after "the"; the text that includes the fragment completes it. (Last sentence.) | Rationale belongs in a test or an ADR, not a comment; the verify-green and verify-refactor prompts each finish the sentence with their own noun. |

## skills/tdd/scripts/prompts/_verify-comments-never-reject.md

| ID | Requirement | Why |
|---|---|---|
| QN1 | The fragment opens by finishing a sentence begun before it, "adds, and name it in REASON:.", so the rejected comment is named in the `REASON:` line. (First sentence.) | The developer must be told which comment to remove. |
| QN2 | It says a contract header or a shell-hazard warning is never grounds for REJECT. (Last sentence.) | The two allowed kinds must not be rejected by a verifier reading the rule too broadly. |

## skills/tdd/scripts/prompts/_verify-red-bug.md

| ID | Requirement | Why |
|---|---|---|
| QB1 | The fragment has the heading "This issue is a bug, so the red bar itself is the claim". (The heading.) | The red bar is the evidence of the reported defect. |
| QB2 | It says the spec carries a `## Bug` section — the report as it was filed — so the step's case is a reproduction: the code's current, wrong behaviour is what the case has to catch. (First paragraph, first sentence.) | A bug's case pins the defect, not a new behaviour. |
| QB3 | It says the verifier is the only party who checks that by running it, because the developer's account of the run does not reach it. (First paragraph, second sentence.) | The verifier is blind to the developer's claim, so it must observe the failure itself. |
| QB4 | It says check 2 is stricter here than it reads: PASS requires the failure the verifier observes to match the behaviour *What happened* describes. (First paragraph, last sentence.) | A red for another reason does not reproduce the reported bug. |
| QB5 | It says a test that fails for any other reason is a REJECT naming that reason, including the error-on-the-name red that check 2 otherwise allows, which says nothing about the defect that was reported. (Second paragraph, first sentence.) | An undefined-name red is a valid red for a feature but not a reproduction. |
| QB6 | It tells the verifier to read *Steps to reproduce* for the conditions the case owes and *Expected* for the behaviour it asserts, and says *Environment* tells an incidental detail of the reporter's setup from a condition the behaviour depends on. (Second paragraph, last sentence.) | Each section of the bug report answers a different question about the case. |

## skills/tdd/scripts/prompts/_verify-coverage-probe.md

| ID | Requirement | Why |
|---|---|---|
| QV1 | The fragment says a judgement that a change is or is not covered by a case is made by running the fast command the verifier was given, `{{FAST_CMD}}`, and the affected suites, never one test file alone. (First sentence, up to the colon.) | A coverage claim made from one file misses cases elsewhere. |
| QV2 | It says a single file's green is not proof that no case covers the change. (First sentence, after the colon.) | It names the false inference the rule forbids. |
| QV3 | It says a REJECT on that ground names the exact command that was run. (Last sentence.) | The developer can rerun the same command and see the gap. |

## skills/tdd/scripts/prompts/_verify-red-fast.md

| ID | Requirement | Why |
|---|---|---|
| QT1 | The fragment is numbered item 4, with the bold lead "The fast command still passes." (Item 4, its lead.) | It continues verify-red's numbered checks. |
| QT2 | It tells the verifier to run `{{FAST_CMD}}` once on this tree. (Item 4, second sentence.) | One run of the fast command shows whether Red's own file breaks it. |
| QT3 | It says Green may not edit a test, so a red whose own file fails that command for any reason other than the target test's expected failure (a lint error, a type error, another case that fails) leaves a step no green can pass. (Item 4, third sentence.) | A red that breaks the fast command makes the step unsatisfiable. |
| QT4 | It tells the verifier to REJECT such a red, naming the file and the error. (Item 4, last sentence.) | The developer must know what to fix. |

## skills/tdd/scripts/prompts/verify-contract-a.md

| ID | Requirement | Why |
|---|---|---|
| VA1 | The template opens with the `{{SHARED}}` slot, then the heading `## Phase: verify-contract-a`. (First lines.) | The blind verifier's shared rules come first, and the phase heading names which interface phase is judged. |
| VA2 | The opening paragraph says this is **contract-a**: it moves the tests off the old interface onto the new one, and production stays frozen. (Opening paragraph, before the include line.) | The verifier must know which of the interface phases it judges and what may change in it. |
| VA3 | Check 2, "The tests moved", says no test calls the old interface any more. (Numbered list, item 2.) | A test still on the old interface keeps the proxy alive for contract-b. |
| VA4 | Check 3, "Production stays frozen", says a range that touches a production file is a REJECT; the item ends in the `{{LAST_PHASE_CHECK}}` slot. (Numbered list, item 3.) | The frozen half of the phase is enforced by rejection. |
| VA5 | The template's own checks are numbered 2 and 3, continuing the list the included `_verify-interface-phase-lead.md` fragment opens with check 1. (Numbered list.) | Check 1 (still green) lives in the shared lead, so the template's numbering must follow it. |
| VA6 | The closing paragraph says PASS if the suites are green, the tests moved to the new interface and no production file changed, and REJECT, naming the specific problem, otherwise. (Closing paragraph.) | The verdict rule restates every check, so a PASS needs all of them. |

## skills/tdd/scripts/prompts/verify-contract-b.md

| ID | Requirement | Why |
|---|---|---|
| VK1 | The template opens with the `{{SHARED}}` slot, then the heading `## Phase: verify-contract-b`. (First lines.) | The blind verifier's shared rules come first, and the phase heading names which interface phase is judged. |
| VK2 | The opening paragraph says this is **contract-b**: the proxy over the old interface is deleted, and test files stay frozen. (Opening paragraph, before the include line.) | The verifier must know the phase deletes the proxy and touches no test. |
| VK3 | Check 2, "The proxy is deleted", says the old interface no longer exists in production. (Numbered list, item 2.) | The deletion is the one change the phase makes. |
| VK4 | Check 3 is the included `_verify-tests-frozen.md` fragment, followed by the `{{LAST_PHASE_CHECK}}` slot. (Numbered list, item 3.) | The test-frozen rule is shared with expand and migrate, stated once. |
| VK5 | The template's own checks are numbered 2 and 3, continuing the list the included `_verify-interface-phase-lead.md` fragment opens with check 1. (Numbered list.) | Check 1 (still green) lives in the shared lead, so the template's numbering must follow it. |
| VK6 | The closing paragraph says PASS if the suites are green, the proxy is deleted and no test file changed, and REJECT, naming the specific problem, otherwise. (Closing paragraph.) | The verdict rule restates every check, so a PASS needs all of them. |

## skills/tdd/scripts/prompts/verify-expand.md

| ID | Requirement | Why |
|---|---|---|
| VE1 | The template opens with the `{{SHARED}}` slot, then the heading `## Phase: verify-expand`. (First lines.) | The blind verifier's shared rules come first, and the phase heading names which interface phase is judged. |
| VE2 | The opening paragraph says this is the **expand** phase: it adds the new interface to production, and the old interface becomes a proxy that delegates to it; test files stay frozen. (Opening paragraph, before the include line.) | The verifier must know what the phase adds, what the old interface turns into, and that no test may change. |
| VE3 | Check 2, "The new interface exists", says production gains the new interface the step names. (Numbered list, item 2.) | The new interface is what the phase delivers. |
| VE4 | Check 3, "The old interface is a proxy", says the old interface delegates to the new one, and no caller has moved yet. (Numbered list, item 3.) | Moving callers is migrate's work, so a moved caller here is a different kind of change. |
| VE5 | Check 4 is the included `_verify-tests-frozen.md` fragment, followed by the `{{LAST_PHASE_CHECK}}` slot. (Numbered list, item 4.) | The test-frozen rule is shared with migrate and contract-b, stated once. |
| VE6 | The template's own checks are numbered 2 to 4, continuing the list the included `_verify-interface-phase-lead.md` fragment opens with check 1. (Numbered list.) | Check 1 (still green) lives in the shared lead, so the template's numbering must follow it. |
| VE7 | The closing paragraph says PASS if the suites are green, the new interface exists, the old one is a proxy over it and no test file changed, and REJECT, naming the specific problem, otherwise. (Closing paragraph.) | The verdict rule restates every check, so a PASS needs all of them. |

## skills/tdd/scripts/prompts/verify-migrate.md

| ID | Requirement | Why |
|---|---|---|
| VM1 | The template opens with the `{{SHARED}}` slot, then the heading `## Phase: verify-migrate`. (First lines.) | The blind verifier's shared rules come first, and the phase heading names which interface phase is judged. |
| VM2 | The opening paragraph says this is the **migrate** phase: the product callers of the old interface move to the new interface, and the old interface stays in place; test files stay frozen. (Opening paragraph, before the include line.) | The verifier must know what moves, what stays, and that no test may change. |
| VM3 | Check 2, "The callers moved", says every product caller of the old interface now calls the new interface. (Numbered list, item 2.) | A caller left on the old interface would break when contract-b deletes the proxy. |
| VM4 | Check 3, "The old interface stays", says removing it is the contract phase's work. (Numbered list, item 3.) | Removing the old interface here would skip the contract phases. |
| VM5 | Check 4 is the included `_verify-tests-frozen.md` fragment, followed by the `{{LAST_PHASE_CHECK}}` slot. (Numbered list, item 4.) | The test-frozen rule is shared with expand and contract-b, stated once. |
| VM6 | The template's own checks are numbered 2 to 4, continuing the list the included `_verify-interface-phase-lead.md` fragment opens with check 1. (Numbered list.) | Check 1 (still green) lives in the shared lead, so the template's numbering must follow it. |
| VM7 | The closing paragraph says PASS if the suites are green, every product caller moved to the new interface and no test file changed, and REJECT, naming the specific problem, otherwise. (Closing paragraph.) | The verdict rule restates every check, so a PASS needs all of them. |
