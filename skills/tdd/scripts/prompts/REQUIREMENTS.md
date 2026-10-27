## skills/tdd/scripts/prompts/develop-revise.md

| ID | Requirement | Why |
|---|---|---|
| DV1 | In a `⟦suite-repair⟧` or `⟦ci-repair⟧` revise-green prompt the permission to edit a test appears once, and it covers only the failing test the full run or CI left red; every other test stays frozen (#1653, #1920). | The repair can fix the test that is actually wrong without opening every other test to edits; PR #1907's review showed a mutant reading "Any test may change" survived. |

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
