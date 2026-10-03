### 📊 Metrics — issue 727

Wall time for the issue: 9529 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 12 of 14 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/733.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 22 | 17 | 2 | 4 | 1745 | 62877 | 41642 | 0.38 |
| red | 24 | 11 | 0 | 0 | 1238 | 857 | 202 | 390 | 81602 | 10787873 | 1233023 | 13.66 |
| green | 23 | 10 | 1 | 0 | 4588 | 1160 | 254 | 498 | 100515 | 13837996 | 1140663 | 13.91 |
| refactor | 20 | 10 | 0 | 0 | 1363 | 382 | 94 | 188 | 29653 | 4179628 | 889584 | 8.55 |
| pin | 2 | 2 | 0 | 0 | 69 | 42 | 10 | 20 | 4352 | 442684 | 86746 | 0.87 |
| predicate | 2 | 0 | 0 | 0 | 45 | 36 | 6 | 12 | 2857 | 227646 | 81127 | 0.75 |
| structural | 1 | 0 | 0 | 0 | 17 | 10 | 3 | 6 | 1064 | 115293 | 41278 | 0.37 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 35 | 34 | 1 | 0 | 3749 | 1074 | 250 | 494 | 93346 | 11961275 | 1546635 | 16.63 |
| developer | claude-opus-5-5 | 38 | 0 | 0 | 0 | 3593 | 1430 | 321 | 624 | 128442 | 17692722 | 1967428 | 21.85 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 647 | 1.92 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `lib/ledger.sh`'s `ledger_steps` reports a line ending `⟦diff-checked⟧ ⟦criterion k⟧`, open or ticked, with kind `diff-checked` and criterion `k` ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 187 | 47 | 92 | 16291 | 2319239 | 276406 | 3.00 | 408 | unknown | 0/5 | nothing-left |  |  | full |
| `lib/ledger.sh`'s `ledger_steps` still reports a `⟦full-suite⟧` line as `full-suite`, a `⟦human-owed⟧` line as `human-owed`, and a plain line, a `⟦replaces-case⟧` line and a line quoting `⟦diff-checked⟧` anywhere but immediately before its closing `⟦criterion k⟧` as `step` ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 65 | 12 | 24 | 5737 | 577375 | 90758 | 0.96 | unknown | unknown | unknown | unknown |  |  | pin |
| `next-unchecked.sh` prints an open `⟦diff-checked⟧ ⟦criterion k⟧` step as the next step when it is the first unchecked one, rather than skipping it the way it skips `⟦full-suite⟧` and `⟦human-owed⟧` lines ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 132 | 37 | 72 | 11194 | 1688156 | 269220 | 2.72 | 320 | unknown | 0/5 | nothing-left |  |  | full |
| `build-verify-prompt.sh --step '<STEP>' diff <spec-file> <base-sha>` exits 0 and prints a prompt rendered from `prompts/verify-diff.md` that carries the step text and tells the verifier to judge the step's criterion against `git diff <base-sha>..HEAD` alone and to answer `VERDICT: PASS` or `VERDICT: REJECT` ⟦criterion 3⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 281 | 68 | 132 | 23718 | 3423341 | 345183 | 3.92 | 871 | 1/2 | 0/5 | nothing left to tidy; triage: structural candidates remain, a follow-up owes them |  |  | full |
| `build-verify-prompt.sh` exits 2 with nothing on stdout for a `diff` call whose `<base-sha>` does not match `^[0-9a-f]{7,40}$`, for a `diff` call with no `--step`, and for a `diff` call with a positional argument after `<base-sha>` ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 148 | 38 | 76 | 13529 | 1821767 | 274594 | 2.83 | 482 | unknown | 0/5 | nothing-left |  |  | full |
| the prompt `build-verify-prompt.sh diff` renders tells the verifier to read `git diff <base-sha>..HEAD` and not the range's commit messages, and carries nothing but the spec, the step text and the base sha | 2 | 1 | 0 | 0 | 0 | 0 | 109 | 17 | 32 | 8175 | 881976 | 104919 | 1.18 | unknown | unknown | unknown | unknown |  |  | pin |
| the rendered `diff` verifier prompt tells the verifier to REJECT when the step's commits add a test, so a criterion judged against the diff is never also pinned by a case left behind ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 143 | 34 | 68 | 11652 | 1564128 | 257512 | 2.61 | 328 | unknown | 0/5 | nothing-left |  |  | full |
| `build-develop-prompt.sh diff <spec-file> <step-text> <test-cmd>` prints a prompt rendered from `prompts/develop-diff.md` telling the developer leaf to make the change the step's criterion names and commit it, to make no commit when the criterion is that something stays unchanged, and to add no test; a missing argument exits 2 with nothing on stdout ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 182 | 50 | 98 | 18059 | 2647660 | 310270 | 3.37 | 486 | unknown | 0/5 | nothing-left |  |  | full |
| `SKILL.md`'s *Scope & plan* section defines a `- [ ] <criterion> ⟦diff-checked⟧ ⟦criterion k⟧` line for a criterion that is a property of the branch's own diff (something removed, left unchanged, or confined to named lines), says it is not planned as a Red/Green step and that its step adds no test, and names a criterion stating a rule future changes must keep as still a Red/Green step ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 222 | 53 | 102 | 18083 | 2637048 | 291381 | 3.22 | 960 | unknown | 0/5 | nothing-left |  |  | full |
| `SKILL.md` runs a `⟦diff-checked⟧` step with no Red leaf: a `develop-diff` leaf built by `build-develop-prompt.sh diff`, then the blind `diff` verifier against the run's branch point (`git merge-base HEAD origin/<default>`); PASS ticks the step and its criterion, REJECT is a revise under `REVISE_BUDGET`, exit 2 is a system bail ⟦criterion 5⟧ | 9 | 4 | 0 | 0 | 0 | 0 | 547 | 110 | 214 | 52622 | 6874570 | 543544 | 6.78 | 1354 | unknown | 0/5 | nothing-left |  |  | full |
| `verify.sh --step '<STEP>' diff <issue-spec-file> <base-sha>` (and `run-verdict.sh` with the same arguments) runs one blind diff verification, handing `build-verify-prompt.sh` exactly the spec and the base sha, and exits 0 on PASS, 1 on REJECT and 2 on a missing `--step`, a non-hex base sha or an extra argument ⟦added⟧ ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 199 | 47 | 94 | 19389 | 2513175 | 306174 | 3.34 | 1208 | unknown | 0/5 | nothing-left |  |  | full |
| the prompt `build-verify-prompt.sh plan` renders from `verify-plan.md` names the diff-property shape beside `⟦full-suite⟧` and `⟦human-owed⟧`, says a `⟦diff-checked⟧ ⟦criterion k⟧` line delivers criterion k by itself, and tells the verifier to REJECT a plan that turns a diff-property criterion into a Red/Green step or plans a test that reads another suite's source text or the git history ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 226 | 47 | 92 | 17673 | 2299746 | 280055 | 3.05 | 555 | unknown | 0/5 | structural-owed |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `lib/ledger.sh`'s `ledger_steps` reports a line ending `⟦diff-checked⟧ ⟦criterion k⟧`, open or ticked, with kind `diff-checked` and criterion `k` ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 104 | 0.82 |
| `next-unchecked.sh` prints an open `⟦diff-checked⟧ ⟦criterion k⟧` step as the next step when it is the first unchecked one, rather than skipping it the way it skips `⟦full-suite⟧` and `⟦human-owed⟧` lines ⟦criterion 5⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 67 | 0.77 |
| `build-verify-prompt.sh --step '<STEP>' diff <spec-file> <base-sha>` exits 0 and prints a prompt rendered from `prompts/verify-diff.md` that carries the step text and tells the verifier to judge the step's criterion against `git diff <base-sha>..HEAD` alone and to answer `VERDICT: PASS` or `VERDICT: REJECT` ⟦criterion 3⟧ | 1 | 0/5 | nothing left to tidy; triage: structural candidates remain, a follow-up owes them | PASS | 0 | 85 | 0.92 |
| `build-verify-prompt.sh` exits 2 with nothing on stdout for a `diff` call whose `<base-sha>` does not match `^[0-9a-f]{7,40}$`, for a `diff` call with no `--step`, and for a `diff` call with a positional argument after `<base-sha>` ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 124 | 0.88 |
| the rendered `diff` verifier prompt tells the verifier to REJECT when the step's commits add a test, so a criterion judged against the diff is never also pinned by a case left behind ⟦criterion 4⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 78 | 0.77 |
| `build-develop-prompt.sh diff <spec-file> <step-text> <test-cmd>` prints a prompt rendered from `prompts/develop-diff.md` telling the developer leaf to make the change the step's criterion names and commit it, to make no commit when the criterion is that something stays unchanged, and to add no test; a missing argument exits 2 with nothing on stdout ⟦criterion 5⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 73 | 0.88 |
| `SKILL.md`'s *Scope & plan* section defines a `- [ ] <criterion> ⟦diff-checked⟧ ⟦criterion k⟧` line for a criterion that is a property of the branch's own diff (something removed, left unchanged, or confined to named lines), says it is not planned as a Red/Green step and that its step adds no test, and names a criterion stating a rule future changes must keep as still a Red/Green step ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 279 | 0.91 |
| `verify.sh --step '<STEP>' diff <issue-spec-file> <base-sha>` (and `run-verdict.sh` with the same arguments) runs one blind diff verification, handing `build-verify-prompt.sh` exactly the spec and the base sha, and exits 0 on PASS, 1 on REJECT and 2 on a missing `--step`, a non-hex base sha or an extra argument ⟦added⟧ ⟦criterion 5⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 154 | 0.89 |
| `SKILL.md` runs a `⟦diff-checked⟧` step with no Red leaf: a `develop-diff` leaf built by `build-develop-prompt.sh diff`, then the blind `diff` verifier against the run's branch point (`git merge-base HEAD origin/<default>`); PASS ticks the step and its criterion, REJECT is a revise under `REVISE_BUDGET`, exit 2 is a system bail ⟦criterion 5⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 269 | 0.85 |
| the prompt `build-verify-prompt.sh plan` renders from `verify-plan.md` names the diff-property shape beside `⟦full-suite⟧` and `⟦human-owed⟧`, says a `⟦diff-checked⟧ ⟦criterion k⟧` line delivers criterion k by itself, and tells the verifier to REJECT a plan that turns a diff-property criterion into a Red/Green step or plans a test that reads another suite's source text or the git history ⟦criterion 6⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 130 | 0.85 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 0 | 11 | 1 | 11 | 12 | 1 | 0 | 0 | 0 | 1 | 5 | 5 | 5 | 0 | 176 | 5 | 99 | 5 | 6 | 5 | 6 | 91 | 5 | 5 | 5 | 4 | 5 | 5 | 5 | 4 | 6 | 6 | 43 | 7 | 1 | 0 | 0 | 197 | 0 | 191 | 0 | 192 | 0 | 0 | 0 | 190 | 79 | 80 | 85 | 85 | 80 | 86 | 1 | 0 | 0 | 202 | 197 | 201 | 197 | 5 | 5 | 5 | 5 | 8 | 8 | 8 | 2 |
| fast | 28 | 29 | 29 | 32 | 29 | 31 | 30 | 31 | 29 | 30 | 29 | 30 | 29 | 27 | 28 | 26 | 26 | 26 | 27 | 29 | 26 | 28 | 26 | 26 | 27 | 25 | 27 | 28 | 27 | 27 | 27 | 26 | 27 | 27 | 28 | 25 | 28 | 28 | 28 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 1 | 0 | 1 | 0 | 5 | 5 | 5 | 5 | 4 | 5 | 5 | 5 | 6 | 5 | 0 | 83 | 0 | 1 | 6 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 571 | 1118 | 221788 | 29653997 | 3514063 | 38.48 |
